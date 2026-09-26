"""Listas de tareas como botones (T3, `prisma-orienta`; ADR 0007 punto 3).

El servidor, no el modelo, garantiza que una lista de tareas salga como
botones: cuando en un turno el modelo usa `consultar_tareas` y responde, el
servidor le agrega un botón a cada tarea que devolvió esa consulta -- tocarlo
abre el menú de acciones de T2 (`accion: "menu"`), igual que una opción de
tarea de `ofrecer_opciones` (T1). Con más de cuatro tareas, la primera página
trae cuatro más "Ver más"; tocar "Ver más" pagina en el servidor, sin volver a
llamar al modelo, a Jev ni a `route_intent` -- y revalida los ids restantes
contra PostgreSQL, igual que T1 valida las tareas que ofrece el modelo.

Reusa el mismo mecanismo que T1/T2
(`pendientes.SENTINEL_OPCIONES_MODELO`): los toques se simulan con
`gateway.procesar_update` y un `callback_query`, igual que
`tests/test_opciones_modelo.py` y `tests/test_menu_tarea.py`.
"""

from __future__ import annotations

import uuid
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from prisma import gateway
from prisma import pendientes as P
from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta
from prisma.salida import BUTTON_TEXT_LIMIT, telegram_utf16_units

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _telegram_id(cur, nombre) -> int:
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return cur.fetchone()["t"]


def _tarea(cur, ws, *, titulo, area="ot", persona="Marcos Tarquini",
          estado="asignada", dias_para_vencer=None):
    """Crea una tarea con `estado` escrito directo en la fila (como
    `tests/test_lectura.py::_tarea`), no por `task_state_event`: pasar acá
    `estado="terminada"` dispararía `trg_exigir_condiciones_de_cierre`
    (evidencia requerida, aprobación) sin venir al caso para estas pruebas,
    que sólo necesitan una tarea que YA ESTÁ en un estado dado, no la
    transición en sí."""
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Objetivo de prueba') returning id""", (ws,))
    obj = cur.fetchone()["id"]
    vence = (datetime.now(timezone.utc) + timedelta(days=dias_para_vencer)
             if dias_para_vencer is not None else None)
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida, fecha_objetivo, estado)
           values (%s, %s, %s,
                   (select id from area where workspace_id = %s and slug = %s),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = %s),
                    'Criterio de prueba', array['explicacion'], %s, %s)
           returning id""",
        (ws, obj, titulo, ws, area, ws, persona, vence, estado))
    return str(cur.fetchone()["id"])


def _tareas_en_orden(cur, ws, cantidad, *, persona="Marcos Tarquini"):
    """Crea `cantidad` tareas con `fecha_objetivo` creciente -- para que
    `consultar_tareas` (ordena por `fecha_objetivo`) las devuelva siempre en
    este mismo orden -- y devuelve sus ids en ese orden."""
    return [_tarea(cur, ws, titulo=f"Tarea {n}", persona=persona,
                   dias_para_vencer=n)
            for n in range(1, cantidad + 1)]


def _con_proveedor(monkeypatch, guion):
    proveedor = ProveedorGuionado(guion=list(guion))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


@pytest.fixture
def cliente(conn, monkeypatch):
    """Como en `test_opciones_modelo.py`/`test_menu_tarea.py`: sin esto, cada
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


def _pendiente(cur, ws, herramienta) -> str:
    cur.execute(
        """select id from pending_action
            where workspace_id = %s and herramienta = %s and estado = 'esperando'
            order by creado_en desc limit 1""",
        (ws, herramienta))
    return str(cur.fetchone()["id"])


def _outbox(cur, ws, chat_id):
    cur.execute(
        """select cuerpo, pending_action_id, programado_para
             from message_outbox
            where workspace_id = %s and chat_id = %s
            order by programado_para""",
        (ws, chat_id))
    return cur.fetchall()


# ---------------------------------------------------------------------------
# Hasta cuatro tareas: botones + salida; tocar una abre el menú de T2
# ---------------------------------------------------------------------------

def test_lista_de_hasta_cuatro_tareas_arma_botones_y_tocar_una_abre_el_menu(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = _tareas_en_orden(cur, ws, 3)
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés 3 tareas abiertas.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.texto == "Tenés 3 tareas abiertas."
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas = _opciones(cur, pid)
        tg = _telegram_id(cur, "Marcos Tarquini")

    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Tarea 1", "Tarea 2", "Tarea 3", P.ETIQUETA_SALIR_OPCIONES]
    for n, (f, tid) in enumerate(zip(filas[:3], ids), start=1):
        assert f["valor"] == {"tipo": "tarea", "tarea_id": tid,
                              "titulo": f"Tarea {n}", "accion": "menu"}

    primera = filas[0]
    assert _tocar(cliente, primera["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid_menu = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA)
        menu_filas = _opciones(cur, pid_menu)
    etiquetas_menu = [f["etiqueta"] for f in menu_filas]
    # Responsable, "asignada": el menú de §4.6 -- prueba que de verdad se
    # abrió el menú de T2, no que se retomó la conversación con el modelo.
    assert "Ver detalle" in etiquetas_menu
    assert "Empezar" in etiquetas_menu


# ---------------------------------------------------------------------------
# Más de cuatro tareas: 4 + "Ver más" + salida; "Ver más" pagina sin modelo
# ---------------------------------------------------------------------------

def test_mas_de_cuatro_tareas_pagina_con_ver_mas_sin_llamar_al_modelo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = _tareas_en_orden(cur, ws, 6)
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés varias tareas abiertas.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas = _opciones(cur, pid)
        tg = _telegram_id(cur, "Marcos Tarquini")

    etiquetas = [f["etiqueta"] for f in filas]
    assert etiquetas == ["Tarea 1", "Tarea 2", "Tarea 3", "Tarea 4",
                        P.ETIQUETA_VER_MAS, P.ETIQUETA_SALIR_OPCIONES]
    ver_mas = next(f for f in filas if f["etiqueta"] == P.ETIQUETA_VER_MAS)
    assert ver_mas["valor"] == {"tipo": "ver_mas", "tarea_ids": ids[4:]}

    llamadas_antes = len(proveedor.recibidos)
    assert _tocar(cliente, ver_mas["token"], tg).status_code == 200
    # No llamó al modelo: sigue con los mismos "recibidos" de antes.
    assert len(proveedor.recibidos) == llamadas_antes

    with admin(conn) as cur:
        pid2 = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas2 = _opciones(cur, pid2)
    etiquetas2 = [f["etiqueta"] for f in filas2]
    assert etiquetas2 == ["Tarea 5", "Tarea 6", P.ETIQUETA_SALIR_OPCIONES]


def test_ver_mas_de_tareas_terminadas_no_dice_que_ya_no_estan_disponibles(
        cliente, conn, corework, monkeypatch):
    """Revisión del orquestador sobre T3: la primera página de esta lista ya
    sale tal cual la devuelve `consultar_tareas`, que acepta `estado`
    "terminada" y no filtra nada -- así que alguien que pide sus tareas
    terminadas, ve más de cuatro y toca "Ver más" tiene que seguir viendo
    tareas terminadas, nunca "Esas tareas ya no están disponibles" (eso sería
    falso: nunca dejaron de existir, siguen siendo exactamente lo que pidió
    ver)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = [_tarea(cur, ws, titulo=f"Tarea terminada {n}", estado="terminada",
                      dias_para_vencer=n)
              for n in range(1, 7)]
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas",
                                        {"estado": "terminada"})]),
            Respuesta(texto="Tenés 6 tareas terminadas.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "qué terminé", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        ver_mas = next(f for f in _opciones(cur, pid)
                      if f["etiqueta"] == P.ETIQUETA_VER_MAS)
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert _tocar(cliente, ver_mas["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid2 = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas2 = _opciones(cur, pid2)
    etiquetas2 = [f["etiqueta"] for f in filas2]
    assert etiquetas2 == ["Tarea terminada 5", "Tarea terminada 6",
                          P.ETIQUETA_SALIR_OPCIONES]


def test_ver_mas_tarea_que_se_cierra_mientras_tanto_se_queda_en_la_pagina(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = _tareas_en_orden(cur, ws, 6)
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés varias tareas abiertas.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        ver_mas = next(f for f in _opciones(cur, pid)
                      if f["etiqueta"] == P.ETIQUETA_VER_MAS)
        tg = _telegram_id(cur, "Marcos Tarquini")

    # "Tarea 5" se cancela antes de que la persona toque "Ver más" -- una
    # transición real por `task_state_event`, no la escritura directa que usa
    # `_tarea` para crearlas: cerrar por "cancelada" no dispara
    # `trg_exigir_condiciones_de_cierre` (ese chequeo es sólo para
    # "terminada"), así que no hace falta simular evidencia ni aprobación
    # para esta prueba -- lo que importa es que la tarea deje de estar activa.
    with admin(conn) as cur:
        cur.execute(
            "insert into task_state_event (task_id, estado_anterior, estado_nuevo, "
            "actor_kind, motivo) values (%s, 'asignada', 'cancelada', 'prisma', "
            "'prueba')", (ids[4],))
    conn.commit()

    assert _tocar(cliente, ver_mas["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid2 = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas2 = _opciones(cur, pid2)
    etiquetas2 = [f["etiqueta"] for f in filas2]
    # "Tarea 5" se QUEDA en la página siguiente: se cerró, no dejó de
    # existir. La primera página de esta misma lista ya podía traer tareas
    # cerradas (si el modelo hubiera pedido terminadas), así que la segunda
    # tiene que ser consistente con la primera.
    assert etiquetas2 == ["Tarea 5", "Tarea 6", P.ETIQUETA_SALIR_OPCIONES]

    fila5 = next(f for f in filas2 if f["etiqueta"] == "Tarea 5")
    assert _tocar(cliente, fila5["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid_menu = _pendiente(cur, ws, P.SENTINEL_MENU_TAREA)
        etiquetas_menu = [f["etiqueta"] for f in _opciones(cur, pid_menu)]
    # El menú, al abrirse, recalcula por el estado ACTUAL de la tarea: para
    # una "cancelada" (responsable) sólo ofrece "Ver detalle" -- no hace
    # falta que "Ver más" filtre por estado, el menú ya lo hace.
    assert etiquetas_menu == ["Ver detalle", P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# Lista vacía: no se arma ningún botón
# ---------------------------------------------------------------------------

def test_consultar_tareas_vacio_no_arma_botones(corework, conn, monkeypatch):
    ws = corework.workspace_id
    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="No tenés tareas pendientes.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.texto == "No tenés tareas pendientes."
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        assert cur.fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# Nunca dos juegos de botones en el mismo turno
# ---------------------------------------------------------------------------

def test_turno_con_otras_opciones_no_agrega_botones_de_lista(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tareas_en_orden(cur, ws, 2)
    conn.commit()

    guion = [Respuesta(llamadas=[
        Llamada("c1", "consultar_tareas", {}),
        Llamada("c2", "ofrecer_opciones", {
            "pregunta": "¿Cuál preferís?",
            "opciones": [{"texto": "A"}, {"texto": "B"}]})])]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "algo", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert r.elecciones == ["ofrecer_opciones"]

        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        # Un solo juego de botones -- el de `ofrecer_opciones` --, nunca dos.
        assert cur.fetchone()["n"] == 1

        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]
    assert etiquetas == ["A", "B", P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# Varias llamadas a consultar_tareas en el mismo turno: gana la última con filas
# ---------------------------------------------------------------------------

def test_ultima_llamada_con_filas_gana(corework, conn, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Tarea asignada A", estado="asignada",
              dias_para_vencer=1)
        _tarea(cur, ws, titulo="Tarea asignada B", estado="asignada",
              dias_para_vencer=2)
        _tarea(cur, ws, titulo="Tarea terminada C", estado="terminada",
              dias_para_vencer=3)
    conn.commit()

    guion = [Respuesta(llamadas=[
        Llamada("c1", "consultar_tareas", {"estado": "asignada"}),
        Llamada("c2", "consultar_tareas", {"estado": "terminada"}),
        # Ninguna bloqueada: esta última llamada vuelve vacía y no debe pisar
        # la de "terminada", que sí trajo filas.
        Llamada("c3", "consultar_tareas", {"estado": "bloqueada"})]),
        Respuesta(texto="Listo.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "resumime", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    assert etiquetas == ["Tarea terminada C", P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# Aislamiento entre espacios: "Ver más" nunca muestra una tarea de otro
# ---------------------------------------------------------------------------

def _tarea_admin(cur, ws, objetivo, area_id, membership_id, titulo):
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, criterio_aceptacion,
                             evidencia_requerida)
           values (%s, %s, %s, %s, %s, 'Criterio', array['explicacion'])
           returning id""",
        (ws, objetivo, titulo, area_id, membership_id))
    tid = str(cur.fetchone()["id"])
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, 'asignada', 'prisma')", (tid,))
    return tid


def test_ver_mas_nunca_muestra_una_tarea_de_otro_espacio(intake_world, conn):
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]
    with admin(conn) as cur:
        propia = _tarea_admin(cur, norte["id"], norte["objectives"][0],
                              norte["areas"]["field"],
                              norte["people"]["Taylor Quinn"]["membership_id"],
                              "Tarea del norte")
        ajena = _tarea_admin(cur, oeste["id"], oeste["objectives"][0],
                             oeste["areas"]["field"],
                             oeste["people"]["Taylor Quinn"]["membership_id"],
                             "Tarea del oeste")
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        quien = identificar(cur, norte["people"]["Taylor Quinn"]["telegram"],
                            Canal.ESPACIO, norte["id"])
        # "Ver más" nunca confía en los ids del botón: acá se simula un
        # payload con una tarea propia y una de otro espacio, como si viniera
        # manipulado o de un cruce raro entre listas.
        gateway._mostrar_mas_tareas(cur, quien, norte["id"], 1, [propia, ajena],
                                    datetime.now(timezone.utc))
        pid = _pendiente(cur, norte["id"], P.SENTINEL_OPCIONES_MODELO)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    assert etiquetas == ["Tarea del norte", P.ETIQUETA_SALIR_OPCIONES]


# ---------------------------------------------------------------------------
# T3a -- una respuesta larga no puede perder sus botones (revisión del
# orquestador sobre T3: `salida.prepare_payload` nunca parte un mensaje con
# botones y lo rechaza por encima de BUTTON_TEXT_LIMIT).
# ---------------------------------------------------------------------------

def test_lista_con_respuesta_larga_se_parte_y_los_botones_van_aparte(
        conn, corework, monkeypatch):
    """Antes de esta corrección, `_encolar_respuesta_con_tareas` mandaba el
    texto del modelo JUNTO con los botones sin mirar su longitud: una
    respuesta más larga que `BUTTON_TEXT_LIMIT` levantaba
    `PayloadValidationError` (un mensaje con botones nunca se parte) y la
    persona se quedaba con el aviso neutro de incidente en vez de su lista.
    Antes de T3, esa misma respuesta iba por `_encolar_respuesta`, que sí
    parte -- este es el comportamiento al que hay que volver cuando el texto
    no entra con los botones."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = _tareas_en_orden(cur, ws, 6)  # > 4: la página también trae "Ver más"
    conn.commit()

    oracion = "Resumen largo de las tareas pendientes para revisar con calma. "
    texto_largo = oracion * 70
    assert telegram_utf16_units(texto_largo) > BUTTON_TEXT_LIMIT

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto=texto_largo)]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                     ahora=datetime.now(timezone.utc))
        assert not r.incidente

        filas = _outbox(cur, ws, 1)
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        etiquetas = [f["etiqueta"] for f in _opciones(cur, pid)]

    partes_texto = [f for f in filas if f["pending_action_id"] is None]
    mensajes_botones = [f for f in filas if f["pending_action_id"] is not None]

    # El texto sale partido, nunca junto con los botones.
    assert len(partes_texto) >= 2
    # Orden explícito por `programado_para`, no un supuesto sobre el `order
    # by` de `_outbox`: antes de la corrección del orquestador del
    # 2026-09-26, `enqueue_outbox` mandaba todas las partes con la MISMA
    # marca (`scheduled_for`) y `despachador.despachar` sólo ordena `by
    # programado_para` (`despachador.py:299`) -- el `id` de `message_outbox`
    # es un uuid al azar que no desempata, así que el orden entre filas
    # empatadas quedaba librado al orden físico con el que Postgres las
    # devolviera. Esta prueba era la intermitente que lo mostraba. Ahora
    # cada parte tiene una marca estrictamente creciente
    # (`salida.enqueue_outbox`): se comprueba acá mismo, sin depender de que
    # `filas` haya llegado en ese orden por casualidad.
    partes_texto = sorted(partes_texto, key=lambda f: f["programado_para"])
    marcas = [f["programado_para"] for f in partes_texto]
    assert marcas == sorted(marcas)
    assert len(set(marcas)) == len(marcas)  # sin empates
    for indice, fila in enumerate(partes_texto, start=1):
        assert fila["cuerpo"].startswith(f"({indice}/{len(partes_texto)})\n")
        assert telegram_utf16_units(fila["cuerpo"]) <= 4096  # TELEGRAM_TEXT_LIMIT

    # Un solo mensaje de botones, corto, después de TODAS las partes del
    # texto (después de la última, no sólo de la primera).
    assert len(mensajes_botones) == 1
    assert mensajes_botones[0]["cuerpo"] == "Elegí una tarea:"
    assert (max(f["programado_para"] for f in partes_texto)
           < mensajes_botones[0]["programado_para"])

    assert etiquetas == ["Tarea 1", "Tarea 2", "Tarea 3", "Tarea 4",
                        P.ETIQUETA_VER_MAS, P.ETIQUETA_SALIR_OPCIONES]


def test_lista_con_respuesta_corta_sigue_yendo_junto_con_los_botones(
        conn, corework, monkeypatch):
    """Que el texto largo se mande aparte no puede romper el caso de siempre:
    una respuesta que entra en `BUTTON_TEXT_LIMIT` sigue en el mismo mensaje
    que los botones, un solo renglón en `message_outbox`."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tareas_en_orden(cur, ws, 2)
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés 2 tareas abiertas.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        filas = _outbox(cur, ws, 1)

    assert len(filas) == 1
    assert filas[0]["pending_action_id"] is not None
    assert filas[0]["cuerpo"] == "Tenés 2 tareas abiertas."


# ---------------------------------------------------------------------------
# T3a -- cobertura de las dos ramas sin prueba de `_mostrar_mas_tareas`
# (observación del orquestador sobre T3, no un defecto nuevo)
# ---------------------------------------------------------------------------

def test_mostrar_mas_tareas_sin_sobrevivientes_dice_que_ya_no_estan_disponibles(
        conn, corework):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        # Ninguno de estos ids existe: ni son de otro espacio, directamente no
        # están en `task`.
        gateway._mostrar_mas_tareas(cur, quien, ws, 1,
                                    [str(uuid.uuid4()), str(uuid.uuid4())],
                                    datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas = _opciones(cur, pid)

    assert [f["etiqueta"] for f in filas] == [P.ETIQUETA_SALIR_OPCIONES]
    assert filas[0]["valor"] == {"tipo": "salida"}


def test_ver_mas_de_mas_de_ocho_tareas_arma_una_tercera_pagina(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        ids = _tareas_en_orden(cur, ws, 10)
    conn.commit()

    guion = [Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés varias tareas abiertas.")]
    proveedor = _con_proveedor(monkeypatch, guion)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "qué tengo pendiente", proveedor, cal, chat_id=1,
                 ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        ver_mas1 = next(f for f in _opciones(cur, pid)
                       if f["etiqueta"] == P.ETIQUETA_VER_MAS)
        tg = _telegram_id(cur, "Marcos Tarquini")

    assert ver_mas1["valor"] == {"tipo": "ver_mas", "tarea_ids": ids[4:]}
    assert _tocar(cliente, ver_mas1["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid2 = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas2 = _opciones(cur, pid2)
    etiquetas2 = [f["etiqueta"] for f in filas2]
    assert etiquetas2 == ["Tarea 5", "Tarea 6", "Tarea 7", "Tarea 8",
                          P.ETIQUETA_VER_MAS, P.ETIQUETA_SALIR_OPCIONES]
    ver_mas2 = next(f for f in filas2 if f["etiqueta"] == P.ETIQUETA_VER_MAS)
    assert ver_mas2["valor"] == {"tipo": "ver_mas", "tarea_ids": ids[8:]}

    assert _tocar(cliente, ver_mas2["token"], tg).status_code == 200

    with admin(conn) as cur:
        pid3 = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO)
        filas3 = _opciones(cur, pid3)
    etiquetas3 = [f["etiqueta"] for f in filas3]
    assert etiquetas3 == ["Tarea 9", "Tarea 10", P.ETIQUETA_SALIR_OPCIONES]
