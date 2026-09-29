"""El modelo ofrece opciones en vez de preguntar en texto abierto (T1,
`prisma-orienta`; ADR 0007 "Prisma orienta, no charla").

`ofrecer_opciones` es una herramienta más: el modelo la llama con una
pregunta y sus opciones (texto corto o tarea existente por id), el servidor
valida cada tarea contra PostgreSQL, arma los botones con "Quiero consultar
otra cosa" y termina el turno -- el modelo no puede seguir escribiendo
después. Tocar una opción NO vuelve a llamar a la herramienta (a diferencia
de `NecesitaElegir`): retoma la conversación con el modelo, con la elección
como si fuera lo que escribió la persona -- para una tarea, ya resuelta, sin
pasar por Jev.

Los toques se simulan con `gateway.procesar_update` y un `callback_query`,
igual que `tests/test_aclaracion_botones.py`.
"""

from __future__ import annotations

import json
from contextlib import nullcontext
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import agente
from prisma import gateway
from prisma import herramientas as H
from prisma import jev as jev_modulo
from prisma import pendientes as P
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.contexto import PREAMBULO, construir
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta
from prisma.salida import (BUTTON_TEXT_LIMIT, ICONO_TAREA,
                             OBJETIVO_ETIQUETA_BOTON, etiqueta_sin_icono,
                             normalize_visible_text, telegram_utf16_units)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


def _tarea(cur, ws, *, titulo="Cablear tablero máq. 3", area="electricidad",
          persona="Mariano Naim", estado="asignada"):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    'Criterio de prueba', array['explicacion'])
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, %s, 'prisma')", (t, estado))
    return str(t)


def _con_proveedor(monkeypatch, guion):
    proveedor = ProveedorGuionado(guion=list(guion))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _jev_no_debe_llamarse(monkeypatch):
    """Falla la prueba si algo intenta resolver con Jev: el toque de una
    opción de tarea ya trae la tarea resuelta, no tiene que consultarlo."""
    def _explota(api_key):
        raise AssertionError("No debería consultarse a Jev al retomar una opción.")
    monkeypatch.setattr(jev_modulo, "desde_base", _explota)


@pytest.fixture
def cliente(conn, monkeypatch):
    """Como en `test_botones.py`/`test_aclaracion_botones.py`: sin esto, cada
    toque de verdad intenta hablar con `api.telegram.org`."""
    monkeypatch.setattr(gateway, "acusar_toque", lambda *a, **k: None)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    import dataclasses
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, webhook_secret="s3cr3t"))
    return TestClient(gateway.app)


def _tocar(cliente, token, user_id):
    return cliente.post(
        "/telegram/corework",
        json={"callback_query": {
            "id": "cb1", "from": {"id": user_id}, "data": f"p:{token}",
            "message": {"message_id": 7, "chat": {"id": user_id}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _opciones(cur, pid):
    cur.execute(
        """select token, etiqueta, valor from pending_action_option
            where pending_action_id = %s order by orden""", (pid,))
    return cur.fetchall()


def _pendiente_opciones(cur, ws) -> str:
    cur.execute(
        """select id from pending_action
            where workspace_id = %s and herramienta = %s and estado = 'esperando'
            order by creado_en desc limit 1""",
        (ws, P.SENTINEL_OPCIONES_MODELO))
    return str(cur.fetchone()["id"])


# ---------------------------------------------------------------------------
# La herramienta arma botones con la salida, hasta el tope
# ---------------------------------------------------------------------------

def test_opciones_de_texto_arman_botones_con_la_salida(corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál preferís?",
        "opciones": [{"texto": "El Dashboard de lotes"},
                    {"texto": "La Integración de datos"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "no sé qué mirar", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.elecciones == ["ofrecer_opciones"]
        assert r.texto == ""            # nada de texto extra después de ofrecer

        pid = _pendiente_opciones(cur, ws)
        filas = _opciones(cur, pid)

    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["El Dashboard de lotes", "La Integración de datos",
                        "💬 Quiero consultar otra cosa"]


# ---------------------------------------------------------------------------
# El texto del modelo acompaña la pregunta, no se descarta (hallazgo del
# orquestador, evidencia real de banco b-0001-a, ADR 0007 punto 2: "el texto
# da el contexto; la elección se hace tocando").
# ---------------------------------------------------------------------------

def test_texto_del_modelo_acompana_la_pregunta_de_opciones(corework, conn, monkeypatch):
    ws = corework.workspace_id
    texto_modelo = ("Tenés dos tareas abiertas: «Programar PLC» y «Revisar "
                    "comunicaciones», sin fecha.")
    guion = [Respuesta(texto=texto_modelo, llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿De cuál te referís?",
        "opciones": [{"texto": "Programar PLC"}, {"texto": "Revisar comunicaciones"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "lo del dashboard", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.elecciones == ["ofrecer_opciones"]
        assert r.texto == texto_modelo           # antes se descartaba entero (r.texto == "")

        pid = _pendiente_opciones(cur, ws)
        cur.execute(
            "select cuerpo from message_outbox where pending_action_id = %s", (pid,))
        cuerpo = cur.fetchone()["cuerpo"]

    assert texto_modelo in cuerpo
    assert "¿De cuál te referís?" in cuerpo
    assert cuerpo.index(texto_modelo) < cuerpo.index("¿De cuál te referís?")


def test_no_duplica_la_pregunta_si_el_texto_del_modelo_ya_pregunta(
        corework, conn, monkeypatch):
    """Hallazgo 6 (sesión 2 por Telegram, 2026-09-27, confirmado por el
    usuario): "Hola Ismael. ¿Con qué te ayudo?\n\n¿Qué querés hacer?" -- el
    texto del modelo ya preguntaba, y encima se le agregaba la `pregunta` de
    `ofrecer_opciones` -- dos preguntas seguidas en el mismo mensaje. Si el
    texto ya pregunta (`deteccion_pregunta.hace_pregunta`), sólo él sale: la
    `pregunta` de las opciones no se repite aparte."""
    ws = corework.workspace_id
    texto_modelo = "Hola Ismael. ¿Con qué te ayudo?"
    guion = [Respuesta(texto=texto_modelo, llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Qué querés hacer?",
        "opciones": [{"texto": "Es una tarea nueva"},
                    {"texto": "Es sobre una tarea existente"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "hola", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.elecciones == ["ofrecer_opciones"]
        assert r.texto == texto_modelo

        pid = _pendiente_opciones(cur, ws)
        cur.execute(
            "select cuerpo from message_outbox where pending_action_id = %s", (pid,))
        cuerpo = cur.fetchone()["cuerpo"]

    assert cuerpo == texto_modelo
    assert cuerpo.count("?") == 1
    assert "¿Qué querés hacer?" not in cuerpo


def test_no_repite_la_pregunta_en_los_botones_si_el_texto_largo_ya_pregunto(
        corework, conn, monkeypatch):
    """Seguimiento de review-149a33fa ("pregunta suprimida") al hallazgo 6:
    la supresión de arriba sólo tapaba el mensaje único -- si el texto del
    modelo ya pregunta pero es tan largo que no entra en `BUTTON_TEXT_LIMIT`,
    `_encolar_texto_con_opciones` lo parte aparte y manda los botones con
    `texto_corto` como resumen DESPUÉS; pasarle ahí `e.pregunta` de todos
    modos reintroducía la segunda pregunta, exactamente en el caso que el
    hallazgo 6 quería evitar. El resumen de los botones pasa a ser el mismo
    genérico que ya usa el cierre de T4b (`agente._TEXTO_BOTONES_GENERICO`)
    cuando la pregunta ya se dijo."""
    ws = corework.workspace_id
    texto_modelo = "Avance registrado. " * 250 + "¿Seguimos con la siguiente?"
    assert telegram_utf16_units(normalize_visible_text(texto_modelo)) > BUTTON_TEXT_LIMIT
    guion = [Respuesta(texto=texto_modelo, llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Qué querés hacer?",
        "opciones": [{"texto": "Es una tarea nueva"},
                    {"texto": "Es sobre una tarea existente"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "hola", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        cur.execute(
            "select cuerpo from message_outbox where pending_action_id = %s", (pid,))
        resumen_botones = cur.fetchone()["cuerpo"]

    assert resumen_botones == agente._TEXTO_BOTONES_GENERICO
    assert "¿Qué querés hacer?" not in resumen_botones


def test_texto_de_una_vuelta_posterior_a_ofrecer_opciones_se_descarta(
        corework, conn, monkeypatch):
    """El texto que acompaña la pregunta es el de la vuelta que LLAMÓ a
    `ofrecer_opciones` -- no el de una vuelta posterior del mismo turno. El
    modelo suele repetir un cierre ("Listo, ahí tenés las opciones") después
    de ver el resultado de la herramienta; ese texto no describe nada nuevo
    y se descarta, aunque sea el último `salida` del turno."""
    ws = corework.workspace_id
    texto_primera_vuelta = ("Tenés dos tareas abiertas: «Programar PLC» y "
                            "«Revisar comunicaciones», sin fecha.")
    guion = [
        Respuesta(texto=texto_primera_vuelta, llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿De cuál te referís?",
            "opciones": [{"texto": "Programar PLC"}, {"texto": "Revisar comunicaciones"}]})]),
        # Vuelta posterior, sin llamadas: cierra el turno, pero su texto no
        # tiene que viajar -- el modelo ya no puede agregar nada después de
        # `ofrecer_opciones` (T1, "el turno termina acá").
        Respuesta(texto="Listo, ahí tenés las opciones."),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "lo del dashboard", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.elecciones == ["ofrecer_opciones"]
        assert r.texto == texto_primera_vuelta

        pid = _pendiente_opciones(cur, ws)
        cur.execute(
            "select cuerpo from message_outbox where pending_action_id = %s", (pid,))
        cuerpo = cur.fetchone()["cuerpo"]

    assert texto_primera_vuelta in cuerpo
    assert "Listo, ahí tenés las opciones" not in cuerpo


def test_texto_se_descarta_si_ademas_queda_una_confirmacion_pendiente(
        corework, conn, monkeypatch):
    """Evitar anunciar como hecho algo que no se hizo (ADR 0005) sigue
    ganando: si en el mismo turno además queda una confirmación esperando,
    el texto no viaja -- sólo la pregunta con sus botones."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, persona="Marcos Tarquini")

    guion = [Respuesta(
        texto="Ya casi termino, sólo falta elegir con cuál seguimos.",
        llamadas=[
            Llamada("c1", "actualizar_estado", {"tarea_id": tid, "estado": "en_curso"}),
            Llamada("c2", "ofrecer_opciones", {
                "pregunta": "¿Seguimos con ésta?",
                "opciones": [{"texto": "Sí"}, {"texto": "No"}]}),
        ])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "arranco", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.confirmaciones == ["actualizar_estado"]
        assert r.texto == ""

        pid = _pendiente_opciones(cur, ws)
        cur.execute(
            "select cuerpo from message_outbox where pending_action_id = %s", (pid,))
        cuerpo = cur.fetchone()["cuerpo"]

    assert cuerpo == "¿Seguimos con ésta?"
    assert "Ya casi termino" not in cuerpo


def test_texto_largo_con_opciones_se_parte_y_los_botones_van_aparte(
        corework, conn, monkeypatch):
    oracion = "Repasé las tareas abiertas y ninguna tiene fecha asignada. "
    texto_largo = oracion * 70
    assert telegram_utf16_units(texto_largo) > BUTTON_TEXT_LIMIT

    ws = corework.workspace_id
    guion = [Respuesta(texto=texto_largo, llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál priorizamos?",
        "opciones": [{"texto": "A"}, {"texto": "B"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "estado general", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))

        cur.execute(
            """select cuerpo, pending_action_id, programado_para
                 from message_outbox where workspace_id = %s and chat_id = %s
                order by programado_para""", (ws, 1))
        filas = cur.fetchall()

    partes_texto = [f for f in filas if f["pending_action_id"] is None]
    mensajes_botones = [f for f in filas if f["pending_action_id"] is not None]

    assert len(partes_texto) >= 2
    assert len(mensajes_botones) == 1
    assert mensajes_botones[0]["cuerpo"] == "¿Cuál priorizamos?"
    assert (max(f["programado_para"] for f in partes_texto)
           < mensajes_botones[0]["programado_para"])


def test_mas_de_cuatro_opciones_se_rechaza_al_modelo(corework, conn, monkeypatch):
    ws = corework.workspace_id
    opciones = [{"texto": f"Opción {n}"} for n in range(H.MAX_OPCIONES_MODELO + 1)]
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál?", "opciones": opciones})]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "elegí algo", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        # El rechazo vuelve al modelo como error de la herramienta, no se
        # arma ninguna acción pendiente.
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 0
    assert r.elecciones == []
    assert "ofrecer_opciones" not in r.acciones


# ---------------------------------------------------------------------------
# Un solo juego de botones por turno (ADR 0007): una segunda llamada a
# `ofrecer_opciones` en el mismo turno no se muestra, y se le dice la verdad
# al modelo en vez de contarle que sí (hallazgo del orquestador).
# ---------------------------------------------------------------------------

def test_segunda_llamada_a_ofrecer_opciones_en_el_mismo_turno_no_se_muestra(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [
        Respuesta(llamadas=[
            Llamada("c1", "ofrecer_opciones", {
                "pregunta": "¿A o B?",
                "opciones": [{"texto": "A"}, {"texto": "B"}]}),
            Llamada("c2", "ofrecer_opciones", {
                "pregunta": "¿C o D?",
                "opciones": [{"texto": "C"}, {"texto": "D"}]}),
        ]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)
    # El turno cierra tras esa vuelta (T8c-1) y el modelo ya no vuelve a
    # leer los resultados: se capturan al salir de `_ejecutar_una`.
    resultados_vistos: list[dict] = []
    original = agente._ejecutar_una

    def _capturando(*args, **kwargs):
        bloque = original(*args, **kwargs)
        resultados_vistos.append(bloque)
        return bloque
    monkeypatch.setattr(agente, "_ejecutar_una", _capturando)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "dos preguntas de una", proveedor, cal,
                     chat_id=1, ahora=datetime.now(timezone.utc))
        # Sólo la primera cuenta como mostrada -- ni duplicada en
        # `elecciones` ni una segunda `pending_action`.
        assert r.elecciones == ["ofrecer_opciones"]
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 1

        pid = _pendiente_opciones(cur, ws)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]
    assert etiquetas[:2] == ["A", "B"]           # la primera llamada ganó

    # El resultado de la segunda llamada dice la verdad, no el mismo texto de
    # éxito que la primera.
    r1 = next(b for b in resultados_vistos if b["tool_use_id"] == "c1")
    r2 = next(b for b in resultados_vistos if b["tool_use_id"] == "c2")
    assert r1["is_error"] is False
    assert r2["is_error"] is True
    contenido_2 = json.loads(r2["content"])
    assert "ya ofreciste opciones" in contenido_2["explicacion"]


# ---------------------------------------------------------------------------
# Dos opciones no pueden mostrar la misma etiqueta (seguimiento de
# review-149a33fa, "etiquetas repetidas del modelo"): la persona no podría
# distinguir a cuál de las dos tocó.
# ---------------------------------------------------------------------------

def test_dos_opciones_de_texto_con_la_misma_etiqueta_se_rechazan_al_modelo(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál?",
            "opciones": [{"texto": "Sí"}, {"texto": "Sí"}]})]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "elegí algo", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 0
    assert r.elecciones == []


def test_dos_tareas_con_la_misma_etiqueta_corta_del_modelo_se_rechazan(
        corework, conn, monkeypatch):
    """Las dos etiquetas son `fija` (el modelo dio una corta para cada una):
    `salida.etiquetas_boton_distinguibles` nunca numera una fija (hallazgo 7,
    seguimiento b), así que sin este rechazo quedarían dos botones
    idénticos apuntando a tareas distintas."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        a = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
        b = _tarea(cur, ws, titulo="Cablear tablero máq. 4", persona="Marcos Tarquini")
    conn.commit()

    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál tarea?",
            "opciones": [{"tarea_id": a, "etiqueta": "Cablear máquina"},
                        {"tarea_id": b, "etiqueta": "Cablear máquina"}]})]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "elegí una tarea", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 0
    assert r.elecciones == []


# ---------------------------------------------------------------------------
# Una tarea inexistente o de otro espacio se rechaza al modelo, no se inventa
# ---------------------------------------------------------------------------

def test_tarea_id_inexistente_se_rechaza_al_modelo(corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál tarea?",
            "opciones": [{"tarea_id": "00000000-0000-0000-0000-000000000000"}]})]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "elegí una tarea", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 0

    sistema, mensajes = proveedor.recibidos[-1]
    ultimo = mensajes[-1]
    assert ultimo["role"] == "user"
    contenido = str(ultimo["content"])
    assert "no existe" in contenido or "permitido" in contenido.lower()


def test_tarea_de_otro_espacio_se_rechaza_al_modelo(intake_world, conn, monkeypatch):
    """`intake_world` arma dos espacios independientes: la tarea de uno no
    puede ofrecerse en el otro (T1: "valida... bajo RLS")."""
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, criterio_aceptacion,
                                 evidencia_requerida)
               values (%s, %s, 'Tarea de otro equipo', %s, %s, 'Criterio',
                       array['explicacion']) returning id""",
            (oeste["id"], oeste["objectives"][0], oeste["areas"]["field"],
             oeste["people"]["Taylor Quinn"]["membership_id"]))
        tarea_ajena = str(cur.fetchone()["id"])
        cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                    "values (%s, 'asignada', 'prisma')", (tarea_ajena,))
    conn.commit()

    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál tarea?", "opciones": [{"tarea_id": tarea_ajena}]})]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, norte["id"]) as cur:
        quien = identificar(cur, norte["people"]["Taylor Quinn"]["telegram"],
                            Canal.ESPACIO, norte["id"])
        cal = Calendario.desde_base(cur, norte["id"])
        responder(cur, quien, "elegí una tarea", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# Etiqueta de una opción de tarea (seguimiento d a la revisión de la sesión
# de etiquetas, review-af418dd9): a través de la herramienta, no llamando
# directo a `herramientas._ofrecer_opciones`.
# ---------------------------------------------------------------------------

def test_etiqueta_del_modelo_corta_se_respeta_tal_cual(corework, conn, monkeypatch):
    ws = corework.workspace_id
    etiqueta_modelo = "Cablear máq. 3"
    assert len(etiqueta_modelo) <= OBJETIVO_ETIQUETA_BOTON
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero eléctrico de la máquina 3",
                    persona="Marcos Tarquini")
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál tarea?",
        "opciones": [{"tarea_id": tid, "etiqueta": etiqueta_modelo}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "elegí una tarea", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        etiqueta = _opciones(cur, pid)[0]["etiqueta"]

    # Ícono de tarea aparte (T1 vía `ofrecer_opciones`, íconos): el texto
    # elegido por el modelo sigue exacto, ni cortado ni con "…".
    assert etiqueta.startswith(f"{ICONO_TAREA} ")
    assert etiqueta_sin_icono(etiqueta) == etiqueta_modelo


def test_etiqueta_del_modelo_larga_se_acorta_en_limite_de_palabra(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    etiqueta_modelo = "Cablear el tablero eléctrico completo de la máquina número tres"
    assert len(etiqueta_modelo) > OBJETIVO_ETIQUETA_BOTON
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero", persona="Marcos Tarquini")
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál tarea?",
        "opciones": [{"tarea_id": tid, "etiqueta": etiqueta_modelo}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "elegí una tarea", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        etiqueta = _opciones(cur, pid)[0]["etiqueta"]

    assert etiqueta.startswith(f"{ICONO_TAREA} ")
    sin_icono = etiqueta_sin_icono(etiqueta)
    assert sin_icono.endswith("…")
    sin_elipsis = sin_icono[:-1].rstrip()
    assert etiqueta_modelo.startswith(sin_elipsis)
    assert sin_elipsis in [
        " ".join(etiqueta_modelo.split(" ")[:n])
        for n in range(len(etiqueta_modelo.split(" ")) + 1)]


def test_etiqueta_de_tarea_sin_etiqueta_propia_sale_del_titulo(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    titulo = "Revisar comunicaciones industriales de la compresora principal"
    assert len(titulo) > OBJETIVO_ETIQUETA_BOTON
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=titulo, persona="Marcos Tarquini")
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál tarea?", "opciones": [{"tarea_id": tid}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "elegí una tarea", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        etiqueta = _opciones(cur, pid)[0]["etiqueta"]

    assert etiqueta.startswith(f"{ICONO_TAREA} ")
    sin_icono = etiqueta_sin_icono(etiqueta)
    assert sin_icono.endswith("…")
    assert titulo.startswith(sin_icono[:-1].rstrip())


# ---------------------------------------------------------------------------
# Tocar una tarea retoma con la tarea resuelta, sin pasar por Jev
# ---------------------------------------------------------------------------

def test_tocar_una_tarea_retoma_resuelta_sin_jev(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
    conn.commit()

    _jev_no_debe_llamarse(monkeypatch)
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿De cuál tarea hablamos?",
            "opciones": [{"tarea_id": tid}]})]),
        Respuesta(texto="Va bien, sin novedades."),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "¿cómo va?", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "resuelta"

    sistema, mensajes = proveedor.recibidos[-1]
    assert f"«Cablear tablero máq. 3» ({tid})" in sistema
    assert "no la vuelvas a resolver" in sistema
    assert mensajes[-1]["role"] == "user"


# ---------------------------------------------------------------------------
# Tocar una opción de texto retoma con ese texto
# ---------------------------------------------------------------------------

def test_tocar_texto_retoma_con_ese_texto(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Terminaste la tarea?",
            "opciones": [{"texto": "Sí"}, {"texto": "Todavía no"}]})]),
        Respuesta(texto="Perfecto, la paso a revisión."),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "avisame", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        si = next(o for o in _opciones(cur, pid) if o["etiqueta"] == "Sí")
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, si["token"], tg).status_code == 200

    sistema, mensajes = proveedor.recibidos[-1]
    assert mensajes[-1] == {"role": "user", "content": "Sí"}
    assert "¿Terminaste la tarea?" in sistema
    assert "tocó «Sí»" in sistema


# ---------------------------------------------------------------------------
# "Quiero consultar otra cosa": cierra sin efecto, invita a escribir
# ---------------------------------------------------------------------------

def test_salida_cierra_sin_efecto_y_no_llama_al_modelo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál?", "opciones": [{"texto": "A"}, {"texto": "B"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        salir = next(o for o in _opciones(cur, pid)
                    if o["etiqueta"] == P.ETIQUETA_SALIR_OPCIONES)
        tg = _telegram_id(cur, "Marcos Tarquini")

    llamadas_antes = len(proveedor.recibidos)
    assert _tocar(cliente, salir["token"], tg).status_code == 200

    # No retoma la conversación con el modelo: cierra e invita a escribir.
    assert len(proveedor.recibidos) == llamadas_antes

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "resuelta"
        cur.execute(
            "select cuerpo from message_outbox where chat_id = %s order by id desc limit 1",
            (tg,))
        assert "escrib" in cur.fetchone()["cuerpo"].lower()


# ---------------------------------------------------------------------------
# Hallazgo 10 (sesión 2 por Telegram, 2026-09-27): Prisma no puede volver a
# preguntar sola lo que la persona ya descartó con "Quiero consultar otra
# cosa". Evidencia real: Marcos tocó la salida sobre "¿Sobre cuál de tus
# tareas avanzaste?", escribió "hols" (un saludo) y Prisma repitió la misma
# pregunta -- el cierre salía con un texto fijo ("Dale, escribime qué
# necesitás.") que no nombraba qué se había cerrado; `contexto.historial`
# guarda literalmente lo que salió por `message_outbox`, así que el turno
# siguiente veía la pregunta y el cierre como dos mensajes de Prisma
# seguidos, sin ninguna marca de que la persona la había descartado.
# ---------------------------------------------------------------------------

def test_salida_nombra_la_pregunta_cerrada_en_vez_de_un_texto_fijo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    pregunta = "¿Sobre cuál de tus tareas avanzaste?"
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": pregunta,
        "opciones": [{"texto": "Cablear tablero"}, {"texto": "Programar PLC"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "avancé con algo", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        salir = next(o for o in _opciones(cur, pid)
                    if o["etiqueta"] == P.ETIQUETA_SALIR_OPCIONES)
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, salir["token"], tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select cuerpo from message_outbox where chat_id = %s order by id desc limit 1",
            (tg,))
        cierre = cur.fetchone()["cuerpo"]

    # Nombra qué pregunta quedó cerrada -- no el texto fijo de siempre --
    # para que quede como un hecho en el propio `message_outbox`, que es lo
    # único que lee `contexto.historial` (`tests/test_memoria.py` prueba que
    # ese hecho llega al historial).
    assert pregunta in cierre
    assert "escrib" in cierre.lower()


def test_traer_el_tema_de_nuevo_reabre_la_pregunta_normalmente(
        cliente, conn, corework, monkeypatch):
    """La regla nueva es "no la retomes sola", no "no se puede volver a
    preguntar nunca": si la persona trae el tema de nuevo, el modelo puede
    volver a ofrecer la misma pregunta sin que nada del servidor lo bloquee."""
    ws = corework.workspace_id
    pregunta = "¿Sobre cuál de tus tareas avanzaste?"
    opciones = [{"texto": "Cablear tablero"}, {"texto": "Programar PLC"}]
    # Dos proveedores, uno por turno -- el bucle de `responder` consume el
    # guion hasta que una vuelta llega sin llamadas (`ProveedorGuionado`
    # devuelve texto vacío cuando se queda sin guion), así que un segundo
    # `ofrecer_opciones` en el MISMO guion se consumiría dentro del primer
    # turno (y se rechazaría por el tope de un juego de botones por turno,
    # ADR 0007), no en el segundo.
    proveedor1 = _con_proveedor(monkeypatch, [Respuesta(llamadas=[Llamada(
        "c1", "ofrecer_opciones", {"pregunta": pregunta, "opciones": opciones})])])

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "avancé con algo", proveedor1, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        salir = next(o for o in _opciones(cur, pid)
                    if o["etiqueta"] == P.ETIQUETA_SALIR_OPCIONES)
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, salir["token"], tg).status_code == 200

    proveedor2 = ProveedorGuionado(guion=[Respuesta(llamadas=[Llamada(
        "c2", "ofrecer_opciones", {"pregunta": pregunta, "opciones": opciones})])])
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien,
                     "che, sobre lo de la tarea: avancé con el tablero",
                     proveedor2, cal, chat_id=1, ahora=datetime.now(timezone.utc))
        assert r.elecciones == ["ofrecer_opciones"]
        pid2 = _pendiente_opciones(cur, ws)
        assert pid2 != pid


# ---------------------------------------------------------------------------
# Nada se aplica sin la vista previa de siempre
# ---------------------------------------------------------------------------

def test_retomar_con_un_cambio_sigue_pidiendo_confirmar(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3", persona="Marcos Tarquini")
    conn.commit()

    _jev_no_debe_llamarse(monkeypatch)
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál pasamos a revisión?",
            "opciones": [{"tarea_id": tid}]})]),
        Respuesta(llamadas=[Llamada(
            "c2", "actualizar_estado",
            {"tarea_id": tid, "estado": "en_revision",
             "evidencia_texto": "Ya está."})]),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "ya terminé", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"      # sin tocar: sólo hay preview
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = 'actualizar_estado' and estado = 'esperando'""")
        assert cur.fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# Garantías existentes reusadas: otro integrante, vencida, doble toque
# ---------------------------------------------------------------------------

def test_toque_de_otro_integrante_no_resuelve(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál?", "opciones": [{"texto": "A"}, {"texto": "B"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        ajeno = _telegram_id(cur, "Ariel De Simone")

    assert _tocar(cliente, token, ajeno).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "esperando"


def test_toque_vencido_no_aplica(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
        "pregunta": "¿Cuál?", "opciones": [{"texto": "A"}, {"texto": "B"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")
        cur.execute(
            "update pending_action set vence_en = now() - interval '1 hour' where id = %s",
            (pid,))
    conn.commit()

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "vencida"


def test_toque_repetido_no_aplica_dos_veces(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál?", "opciones": [{"texto": "A"}, {"texto": "B"}]})]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, token, tg).status_code == 200
    assert _tocar(cliente, token, tg).status_code == 200   # de nuevo, no rompe

    with admin(conn) as cur:
        cur.execute(
            "select count(*) n from audit_log where accion = 'eleccion_opciones_modelo'")
        assert cur.fetchone()["n"] == 1, "el segundo toque no vuelve a auditar nada"


# ---------------------------------------------------------------------------
# Auditoría de la elección, nunca el texto
# ---------------------------------------------------------------------------

def test_auditoria_sin_texto(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Cablear tablero máq. 3 (secreto)",
                    persona="Marcos Tarquini")
    conn.commit()

    _jev_no_debe_llamarse(monkeypatch)
    guion = [
        Respuesta(llamadas=[Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿Cuál tarea, secreto de más?",
            "opciones": [{"tarea_id": tid}]})]),
        Respuesta(texto="listo"),
    ]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente_opciones(cur, ws)
        token = _opciones(cur, pid)[0]["token"]
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, token, tg).status_code == 200

    with admin(conn) as cur:
        cur.execute(
            "select detalle from audit_log where accion = 'eleccion_opciones_modelo'")
        fila = cur.fetchone()
        assert fila["detalle"] == {"tipo": "tarea", "tarea_id": tid}
        crudo = str(fila["detalle"])
        assert "secreto" not in crudo.lower()


# ---------------------------------------------------------------------------
# Reglas del contexto (ADR 0007)
# ---------------------------------------------------------------------------

def test_reglas_del_contexto_piden_ofrecer_opciones(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        ctx = construir(cur, quien)

    assert "ofrecer_opciones" in PREAMBULO
    assert "ofrecer_opciones" in ctx.sistema
    assert "no la presentes como un hecho" in PREAMBULO.lower() or \
           "no presentes" in PREAMBULO.lower()
    # Hallazgo 1 (sesión 2 por Telegram, 2026-09-27): una respuesta real
    # hizo dos preguntas seguidas ("¿En qué te ayudo? ¿Por dónde
    # arrancamos?"). Nunca más de una por turno.
    assert "más de una pregunta" in PREAMBULO.lower()
    # Hallazgo 4 (misma sesión): con la lista de tareas en botones (T3), el
    # texto no puede volver a enumerar cada tarea -- eso es lo que hacía la
    # respuesta real ("- Backup de servidores... (simulado)" x 12).
    assert "no las enumeres" in PREAMBULO.lower()
