"""Lo que la persona acaba de dejar no se vuelve a proponer al atender lo otro
(T9-R1d-1a-fix, ADR 0013 regla 1 y su enmienda "una sola rama abierta").

Con "Dejarlo y ver lo otro" (o "No, es otra cosa" de `dudoso`) el mensaje
guardado se atiende por el camino normal, y el modelo ve en el historial la
propuesta que se acaba de dejar (banco b-0020-f, 0/3: volvió a llamar a
`registrar_bloqueo` sobre la misma tarea). La guarda es de código, sobre
(herramienta, id): un prompt no lo garantiza. Nunca mira el texto.

Los ruteos y el modelo se guionan con `ProveedorGuionado`; nada toca la red.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest

from leda import gateway
from leda import jev as jev_modulo
from leda import pendientes as P
from leda.agente import NoProponer, repite_lo_pendiente
from leda.db import admin, espacio
from leda.jev import ClienteJevGuionado
from leda.llm import (IntentAction, IntentRoute, Llamada, RespectoPendiente,
                        Respuesta)

from tests.test_menu_tarea import (_abrir_menu, _bloquear, _mensaje, _opciones,
                                   _pendiente, _quien,  # noqa: F401
                                   _tarea as _tarea_menu, _telegram_id,
                                   _tocar, _tocar_accion, cliente)
from tests.test_modificar import _proponer, _tarea as _tarea_modificar
from tests.test_pregunta_pendiente_otras import (_abiertas, _con_rutas, _ruta,
                                                 _tocar_boton)

PERSONA = "Marcos Tarquini"
CAUSA = "falta el switch"
TITULO_MENU = "Programar HMI línea 2"
OTRO_MENSAJE = "¿qué tareas tengo abiertas?"
FRAGMENTO_RECHAZO = "ya está pendiente con la persona"


def _vistas_previas(conn, herramienta: str, valor: str,
                    campo: str = "tarea_id") -> int:
    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from pending_action
                where estado = 'esperando' and herramienta = %s
                  and args->>%s = %s""", (herramienta, campo, valor))
        return cur.fetchone()["n"]


def _resultados_de_herramientas(proveedor) -> list[dict]:
    """Los `tool_result` que el modelo recibió, en orden y sin repetir."""
    vistos, unicos = set(), []
    for _sistema, mensajes in proveedor.recibidos:
        for m in mensajes:
            if m["role"] == "user" and isinstance(m["content"], list):
                for b in m["content"]:
                    if (b.get("type") == "tool_result"
                            and b["tool_use_id"] not in vistos):
                        vistos.add(b["tool_use_id"])
                        unicos.append(b)
    return unicos


def _rechazos(proveedor) -> list[dict]:
    return [r for r in _resultados_de_herramientas(proveedor)
            if FRAGMENTO_RECHAZO in r["content"]]


def _abrir_modificar(cliente, conn, ws) -> tuple[int, str, str]:
    """Una vista previa de `registrar_bloqueo` sobre la tarea A, el toque en
    "Modificar", y una tarea B distinta. Devuelve (chat, A, B)."""
    with admin(conn) as cur:
        a = _tarea_modificar(cur, ws)
        b = _tarea_modificar(cur, ws, titulo="Revisar variador línea 2")
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": a, "causa": CAUSA}, chat_id=tg,
                        ahora=datetime.now(timezone.utc))
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
    conn.commit()
    assert _tocar(cliente, modificar.token, tg).status_code == 200
    assert _abiertas(conn) == 1
    return tg, a, b


def _abrir_dato_menu(cliente, conn, ws, monkeypatch) -> tuple[int, str, str]:
    """"Ya la terminé" sobre la tarea A (pide la evidencia) y una tarea B."""
    with admin(conn) as cur:
        a = _tarea_menu(cur, ws, titulo=TITULO_MENU, estado="asignada")
        b = _tarea_menu(cur, ws, titulo="Revisar variador línea 2",
                        estado="asignada")
    conn.commit()
    _pid, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, a,
                                  "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, "Ya la terminé", tg)
    assert _abiertas(conn) == 1
    return tg, a, b


def _guion(herramienta: str, args: dict) -> list[Respuesta]:
    """El modelo consulta las tareas, vuelve a llamar a `herramienta` y cierra
    con un texto: lo que hizo en el banco real."""
    return [Respuesta(llamadas=[Llamada("q1", "consultar_tareas", {})]),
            Respuesta(llamadas=[Llamada("q2", herramienta, args)]),
            Respuesta(texto="Tenés dos tareas abiertas.")]


def _dejar_y_ver_lo_otro(cliente, conn, ws, tg, monkeypatch, guion, *,
                         escribir=_mensaje):
    """`otro_tema` con la pregunta abierta, y el toque en "Dejarlo y ver lo
    otro": el mensaje guardado se atiende con el modelo guionado. `escribir`
    es cómo se manda el mensaje (el alta sólo se lee en un chat privado)."""
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=guion)
    escribir(cliente, tg, OTRO_MENSAJE)
    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)
    return proveedor


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_dejar_un_modificar_no_vuelve_a_proponer_la_misma_herramienta_en_la_misma_tarea(
        cliente, conn, corework, monkeypatch, es_la_misma):
    ws = corework.workspace_id
    tg, a, b = _abrir_modificar(cliente, conn, ws)
    destino = a if es_la_misma else b
    previas_a = _vistas_previas(conn, "registrar_bloqueo", a)

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("registrar_bloqueo", {"tarea_id": destino, "causa": CAUSA}))

    assert bool(_rechazos(proveedor)) is es_la_misma
    assert _vistas_previas(conn, "registrar_bloqueo", a) == previas_a
    if es_la_misma:
        rechazo = _rechazos(proveedor)[0]
        assert rechazo["tool_use_id"] == "q2" and rechazo["is_error"] is True
    else:
        # Aserción positiva: sobre otra tarea la propuesta sí se arma.
        assert _vistas_previas(conn, "registrar_bloqueo", b) == 1


def test_dejar_un_modificar_permite_otra_herramienta_sobre_la_misma_tarea(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("actualizar_estado", {"tarea_id": a, "estado": "en_revision",
                                     "evidencia_texto": "quedó probada"}))

    assert _rechazos(proveedor) == []
    assert _vistas_previas(conn, "actualizar_estado", a) == 1


def test_la_llamada_rechazada_se_audita_sin_el_texto_de_la_persona(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)

    _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("registrar_bloqueo", {"tarea_id": a, "causa": CAUSA}))

    with admin(conn) as cur:
        cur.execute(
            """select detalle from audit_log
                where accion = 'herramienta_rechazada:registrar_bloqueo'""")
        (fila,) = cur.fetchall()
    assert fila["detalle"]["args"]["tarea_id"] == a
    assert "qué tareas tengo abiertas" not in str(fila["detalle"])


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_dejar_un_dato_del_menu_guarda_la_herramienta_de_la_accion(
        cliente, conn, corework, monkeypatch, es_la_misma):
    ws = corework.workspace_id
    tg, a, b = _abrir_dato_menu(cliente, conn, ws, monkeypatch)
    destino = a if es_la_misma else b

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("actualizar_estado", {"tarea_id": destino, "estado": "en_revision",
                                     "evidencia_texto": "quedó probada"}))

    assert bool(_rechazos(proveedor)) is es_la_misma
    assert _vistas_previas(conn, "actualizar_estado", a) == 0
    if not es_la_misma:
        assert _vistas_previas(conn, "actualizar_estado", b) == 1


def test_dudoso_no_es_otra_cosa_tambien_tiene_la_guarda(
        cliente, conn, corework, monkeypatch):
    # Es la misma salida que "Dejarlo y ver lo otro": misma guarda.
    ws = corework.workspace_id
    tg, a, _b = _abrir_modificar(cliente, conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
        guion=_guion("registrar_bloqueo", {"tarea_id": a, "causa": CAUSA}))
    _mensaje(cliente, tg, "puede ser")
    previas = _vistas_previas(conn, "registrar_bloqueo", a)

    _tocar_boton(cliente, conn, ws, "No, es otra cosa", tg)

    assert _vistas_previas(conn, "registrar_bloqueo", a) == previas
    assert _rechazos(proveedor)


def test_sin_pregunta_pendiente_registrar_bloqueo_funciona_como_siempre(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        a = _tarea_modificar(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, PERSONA)
    conn.commit()
    proveedor = _con_rutas(
        monkeypatch, [_ruta(None)],
        guion=[Respuesta(llamadas=[Llamada("q2", "registrar_bloqueo", {
                   "tarea_id": a, "causa": CAUSA})]),
               Respuesta(texto="listo")])

    _mensaje(cliente, tg, "anotá un bloqueo")

    assert _vistas_previas(conn, "registrar_bloqueo", a) == 1
    assert _rechazos(proveedor) == []


def _bloqueo_de(conn, tarea_id: str) -> str:
    with admin(conn) as cur:
        cur.execute("select id from blocker where task_id = %s", (tarea_id,))
        return str(cur.fetchone()["id"])


@pytest.mark.parametrize("es_el_mismo", [True, False],
                         ids=["mismo_bloqueo_rechaza", "otro_bloqueo_permite"])
def test_dejar_un_modificar_de_resolver_bloqueo_guarda_por_bloqueo_id(
        cliente, conn, corework, monkeypatch, es_el_mismo):
    ws = corework.workspace_id
    with admin(conn) as cur:
        a = _tarea_modificar(cur, ws)
        b = _tarea_modificar(cur, ws, titulo="Revisar variador línea 2")
        _bloquear(cur, ws, a)
        _bloquear(cur, ws, b, causa="Falta un cable")
    conn.commit()
    bloqueo_a, bloqueo_b = _bloqueo_de(conn, a), _bloqueo_de(conn, b)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        pid = _proponer(cur, ws, quien, "resolver_bloqueo",
                        {"bloqueo_id": bloqueo_a, "resolucion": "llegó el switch"},
                        chat_id=tg, ahora=datetime.now(timezone.utc))
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
    conn.commit()
    assert _tocar(cliente, modificar.token, tg).status_code == 200
    previas_a = _vistas_previas(conn, "resolver_bloqueo", bloqueo_a, "bloqueo_id")
    destino = bloqueo_a if es_el_mismo else bloqueo_b

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion("resolver_bloqueo",
               {"bloqueo_id": destino, "resolucion": "llegó el switch"}))

    assert bool(_rechazos(proveedor)) is es_el_mismo
    assert _vistas_previas(conn, "resolver_bloqueo", bloqueo_a,
                           "bloqueo_id") == previas_a
    if not es_el_mismo:
        assert _vistas_previas(conn, "resolver_bloqueo", bloqueo_b,
                               "bloqueo_id") == 1


# ---------------------------------------------------------------------------
# La guarda de cada acción del menú que pide un dato (review-ed284b3aec853536):
# `gateway._HERRAMIENTA_DE_DATO_MENU` nombra la herramienta y el campo de id
# que la guarda compara, y los `args` de la pregunta tienen que traerlo.
# ---------------------------------------------------------------------------

_EVIDENCIA_DE_PRUEBA = "ya está probado"

_ACCIONES_DEL_MENU = {
    "informar_bloqueo": dict(
        persona="Nahuel Gimenez", estado="asignada", etiqueta="Informar un bloqueo",
        herramienta="registrar_bloqueo", campo="tarea_id", clave="tarea",
        args=lambda d: {"tarea_id": d["tarea"], "causa": CAUSA}),
    "destrabar": dict(
        persona="Nahuel Gimenez", estado="asignada", etiqueta="Ya se destrabó",
        herramienta="resolver_bloqueo", campo="bloqueo_id", clave="bloqueo",
        bloquear=True,
        args=lambda d: {"bloqueo_id": d["bloqueo"],
                        "resolucion": "llegó el switch"}),
    "adjuntar_evidencia": dict(
        persona="Nahuel Gimenez", estado="en_revision",
        etiqueta="Adjuntar evidencia", herramienta="adjuntar_evidencia",
        campo="tarea_id", clave="tarea",
        args=lambda d: {"tarea_id": d["tarea"], "tipo": "texto",
                        "descripcion": _EVIDENCIA_DE_PRUEBA}),
    "pedir_cambios": dict(
        persona="Marcos Tarquini", estado="en_revision",
        etiqueta="Pedir cambios", herramienta="pedir_cambios_tarea",
        campo="tarea_id", clave="tarea",
        args=lambda d: {"tarea_id": d["tarea"], "comentario": "falta la foto"}),
}


def _abrir_accion_del_menu(cliente, conn, ws, monkeypatch, caso: dict):
    """Abre, desde el menú de la tarea A, la pregunta del dato de `caso`.
    Devuelve (chat, ids de A, ids de B): tarea y, si hay, bloqueo."""
    with admin(conn) as cur:
        a = _tarea_menu(cur, ws, titulo=TITULO_MENU, estado=caso["estado"])
        b = _tarea_menu(cur, ws, titulo="Revisar variador línea 2",
                        estado=caso["estado"])
        if caso.get("bloquear"):
            _bloquear(cur, ws, a)
            _bloquear(cur, ws, b, causa="Falta un cable")
    conn.commit()
    ids_a, ids_b = {"tarea": a}, {"tarea": b}
    if caso.get("bloquear"):
        ids_a["bloqueo"], ids_b["bloqueo"] = _bloqueo_de(conn, a), _bloqueo_de(conn, b)
    _pid, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, a,
                                  caso["persona"])
    _tocar_accion(cliente, conn, ws, filas, caso["etiqueta"], tg)
    assert _abiertas(conn) == 1
    return tg, ids_a, ids_b


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_rechaza", "otra_permite"])
@pytest.mark.parametrize("accion", list(_ACCIONES_DEL_MENU))
def test_dejar_un_dato_del_menu_guarda_por_el_id_de_cada_accion(
        cliente, conn, corework, monkeypatch, accion, es_la_misma):
    ws = corework.workspace_id
    caso = _ACCIONES_DEL_MENU[accion]
    tg, ids_a, ids_b = _abrir_accion_del_menu(cliente, conn, ws, monkeypatch, caso)
    destino = ids_a if es_la_misma else ids_b

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion(caso["herramienta"], caso["args"](destino)))

    assert bool(_rechazos(proveedor)) is es_la_misma
    campo, herramienta = caso["campo"], caso["herramienta"]
    assert _vistas_previas(conn, herramienta, ids_a[caso["clave"]], campo) == 0
    if not es_la_misma:
        # Aserción positiva: sobre otro objetivo la propuesta sí se arma.
        assert _vistas_previas(conn, herramienta, ids_b[caso["clave"]], campo) == 1


# ---------------------------------------------------------------------------
# La guarda sobrevive a la aclaración con botones: "Dejarlo y ver lo otro" se
# detiene a preguntar a qué tarea se refiere el mensaje guardado y sigue al
# tocar una candidata (`_avanzar_aclaracion`).
# ---------------------------------------------------------------------------

REFERENCIA_DEL_OTRO_MENSAJE = "lo del tablero"


@pytest.fixture
def cliente_con_credencial(cliente, monkeypatch):
    """Con la credencial de Jev configurada, una referencia ambigua se
    resuelve con botones en vez de quedar sin resolver."""
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, openrouter_api_key="sk-test-fake"))
    return cliente


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_la_guarda_sigue_vigente_al_retomar_tras_botones_de_aclaracion(
        cliente_con_credencial, conn, corework, monkeypatch, es_la_misma):
    cliente = cliente_con_credencial
    ws = corework.workspace_id
    tg, a, b = _abrir_modificar(cliente, conn, ws)
    destino = a if es_la_misma else b
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: ClienteJevGuionado(
        guion=[{"alcance": {"probabilities": {"una_tarea": 0.8,
                                              "varias_tareas": 0.0,
                                              "ninguna": 0.0}},
                "tarea": {"probabilities": {"T1": 0.5, "T2": 0.3}}}]))
    con_referencia = IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                 trabajos=(REFERENCIA_DEL_OTRO_MENSAJE,))
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), con_referencia],
        guion=_guion("registrar_bloqueo", {"tarea_id": destino, "causa": CAUSA}))
    _mensaje(cliente, tg, f"¿cómo va {REFERENCIA_DEL_OTRO_MENSAJE}?")
    previas_a = _vistas_previas(conn, "registrar_bloqueo", a)

    # "Dejarlo" cierra el Modificar y se detiene en la pregunta de la
    # aclaración: el modelo todavía no habló.
    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)
    assert proveedor.recibidos == []
    with admin(conn) as cur:
        pid = _pendiente(cur, ws, gateway._SENTINEL_ACLARACION)
        candidata = _opciones(cur, pid)[0]

    # Tocar una candidata retoma el mensaje guardado, con la guarda puesta.
    assert _tocar(cliente, candidata["token"], tg).status_code == 200

    assert bool(_rechazos(proveedor)) is es_la_misma
    assert _vistas_previas(conn, "registrar_bloqueo", a) == previas_a
    if not es_la_misma:
        assert _vistas_previas(conn, "registrar_bloqueo", b) == 1


# ---------------------------------------------------------------------------
# Lo que se dejó de lado incluye el alta (T9-R2b, banco real b-0021-i 2/3):
# tras "Dejarlo y ver lo otro" sobre una pregunta del alta, el responder atendió
# el otro mensaje y siguió con "para armar la tarea nueva, necesito saber dónde
# cuelga" (`ofrecer_opciones`), reabriendo lo que la persona acababa de soltar.
# Causa general: en ese turno el modelo no ve que se dejó algo de lado (el
# aviso "dejé de lado" todavía no salió y el historial sólo cuenta lo enviado) y
# la guarda de código no tenía caso para el alta (no hay herramienta ni id).
# Los dos arreglos son un solo mecanismo: el responder recibe, como contexto de
# confianza, qué se dejó de lado; y la guarda rechaza reabrirlo.
# ---------------------------------------------------------------------------

FRAGMENTO_RECHAZO_ALTA = "dejar de lado el armado de una tarea nueva"
PREGUNTA_ALTA_REPROPUESTA = "¿A qué objetivo contribuye la tarea nueva?"
NOMBRE_DEL_TITULO_DEL_ALTA = "el título de la tarea nueva"


def _abrir_alta_de_la_persona(conn, ws) -> tuple[int, str]:
    """El alta esperando el título, con una tarea del equipo ya existente."""
    from tests.test_alta_pregunta_pendiente import _abrir_alta

    tg, _request_id = _abrir_alta(conn, ws)
    with admin(conn) as cur:
        cur.execute("select id from task limit 1")
        return tg, str(cur.fetchone()["id"])


TEXTO_RECHAZADO = ("Tenés una tarea abierta.\n\nPara armar la tarea nueva, "
                   "necesito saber dónde cuelga.")


def _guion_ofrecer(opciones: list[dict]) -> list[Respuesta]:
    """El modelo consulta las tareas, vuelve a ofrecer opciones y cierra: lo que
    hizo en el banco real."""
    return [Respuesta(llamadas=[Llamada("q1", "consultar_tareas", {})]),
            Respuesta(texto=TEXTO_RECHAZADO,
                      llamadas=[Llamada("q2", "ofrecer_opciones", {
                          "pregunta": PREGUNTA_ALTA_REPROPUESTA,
                          "opciones": opciones})]),
            Respuesta(texto="Tenés una tarea abierta.")]


def _rechazos_del_alta(proveedor) -> list[dict]:
    return [r for r in _resultados_de_herramientas(proveedor)
            if FRAGMENTO_RECHAZO_ALTA in r["content"]]


def _opciones_ofrecidas(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (P.SENTINEL_OPCIONES_MODELO,))
        return cur.fetchone()["n"]


def _dejar_el_alta_y_ver_lo_otro(cliente, conn, ws, monkeypatch, guion):
    from tests.test_alta_pregunta_pendiente import _mensaje_privado

    tg, tarea_id = _abrir_alta_de_la_persona(conn, ws)
    proveedor = _dejar_y_ver_lo_otro(cliente, conn, ws, tg, monkeypatch, guion,
                                     escribir=_mensaje_privado)
    return proveedor, tg, tarea_id


def test_dejar_el_alta_no_vuelve_a_ofrecer_opciones_sobre_la_tarea_nueva(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    proveedor, tg, _tarea = _dejar_el_alta_y_ver_lo_otro(
        cliente, conn, ws, monkeypatch,
        _guion_ofrecer([{"texto": "Conectar y automatizar equipos"},
                        {"texto": "Planos eléctricos correctos"}]))

    (rechazo,) = _rechazos_del_alta(proveedor)
    assert rechazo["tool_use_id"] == "q2" and rechazo["is_error"] is True
    assert _opciones_ofrecidas(conn) == 0                # nada quedó esperando
    # La persona recibe, en una sola respuesta, lo que dejó y lo que pidió.
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para, dedupe_key""", (tg,))
        cuerpos = [f["cuerpo"] for f in cur.fetchall()]
    assert PREGUNTA_ALTA_REPROPUESTA not in "".join(cuerpos)
    # El texto que acompañaba a la llamada rechazada ("Para armar la tarea nueva,
    # necesito saber dónde cuelga", banco b-0021-i) nunca llega al outbox, ni
    # descartado: la persona no lo lee y la salida no lo guarda.
    assert TEXTO_RECHAZADO not in "".join(cuerpos)
    assert "Para armar la tarea nueva" not in "".join(cuerpos)
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox "
                    "where cuerpo like '%%Para armar la tarea nueva%%'")
        assert cur.fetchone()["n"] == 0
    assert cuerpos[-1] == "Tenés una tarea abierta."


def test_el_rechazo_del_alta_se_audita_sin_el_texto_de_la_persona(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _dejar_el_alta_y_ver_lo_otro(
        cliente, conn, ws, monkeypatch,
        _guion_ofrecer([{"texto": "Conectar y automatizar equipos"}]))

    with admin(conn) as cur:
        cur.execute(
            """select detalle from audit_log
                where accion = 'herramienta_rechazada:ofrecer_opciones'""")
        (fila,) = cur.fetchall()
    assert "opciones" in fila["detalle"]["args"]
    assert "qué tareas tengo abiertas" not in str(fila["detalle"])


def test_el_responder_sabe_que_la_persona_dejo_el_alta_de_lado(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    proveedor, _tg, _tarea = _dejar_el_alta_y_ver_lo_otro(
        cliente, conn, ws, monkeypatch, [Respuesta(texto="Tenés dos tareas.")])

    sistema = proveedor.recibidos[0][0]
    assert "acaba de dejar de lado" in sistema
    assert NOMBRE_DEL_TITULO_DEL_ALTA in sistema
    assert "no lo propongas" in sistema.lower()


def test_el_responder_sabe_que_la_persona_dejo_un_modificar_de_lado(
        cliente, conn, corework, monkeypatch):
    # El contexto es general: cualquier pregunta que se deja, no sólo el alta.
    ws = corework.workspace_id
    tg, _a, _b = _abrir_modificar(cliente, conn, ws)

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch, [Respuesta(texto="Tenés dos tareas.")])

    sistema = proveedor.recibidos[0][0]
    assert "acaba de dejar de lado" in sistema
    assert "la corrección de la propuesta" in sistema


def test_sin_nada_dejado_de_lado_el_responder_no_recibe_ese_contexto(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea_modificar(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        tg = _telegram_id(cur, PERSONA)
    conn.commit()
    proveedor = _con_rutas(monkeypatch, [_ruta(None)],
                           guion=[Respuesta(texto="Tenés una tarea.")])

    _mensaje(cliente, tg, OTRO_MENSAJE)

    assert "acaba de dejar de lado" not in proveedor.recibidos[0][0]


def test_dejar_el_alta_permite_ofrecer_tareas_existentes_como_opciones(
        cliente, conn, corework, monkeypatch):
    # Una opción de tarea existente no puede ser sobre la tarea nueva (todavía
    # no tiene id): es una elección sobre lo otro que la persona pidió.
    ws = corework.workspace_id
    from tests.test_alta_pregunta_pendiente import _mensaje_privado

    tg, tarea_id = _abrir_alta_de_la_persona(conn, ws)
    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion_ofrecer([{"tarea_id": tarea_id}]), escribir=_mensaje_privado)

    assert _rechazos_del_alta(proveedor) == []
    assert _opciones_ofrecidas(conn) == 1


def test_dejar_un_modificar_no_bloquea_ofrecer_opciones_de_texto(
        cliente, conn, corework, monkeypatch):
    # La regla del alta no se extiende a lo que no es el alta.
    ws = corework.workspace_id
    tg, _a, _b = _abrir_modificar(cliente, conn, ws)

    proveedor = _dejar_y_ver_lo_otro(
        cliente, conn, ws, tg, monkeypatch,
        _guion_ofrecer([{"texto": "Ver mis tareas"}]))

    assert _rechazos_del_alta(proveedor) == []
    assert _opciones_ofrecidas(conn) == 1


def test_dudoso_no_es_otra_cosa_sobre_el_alta_tambien_tiene_la_guarda(
        cliente, conn, corework, monkeypatch):
    from tests.test_alta_pregunta_pendiente import _mensaje_privado

    ws = corework.workspace_id
    tg, _tarea = _abrir_alta_de_la_persona(conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
        guion=_guion_ofrecer([{"texto": "Conectar y automatizar equipos"}]))
    assert _mensaje_privado(cliente, tg, "puede ser").status_code == 200

    _tocar_boton(cliente, conn, ws, "No, es otra cosa", tg)

    assert len(_rechazos_del_alta(proveedor)) == 1
    assert _opciones_ofrecidas(conn) == 0


def _llamada(nombre: str, args: dict) -> Llamada:
    return Llamada("x", nombre, args)


def _alta_dejada() -> NoProponer:
    return NoProponer(None, None, None, dejado=NOMBRE_DEL_TITULO_DEL_ALTA,
                      alta=True)


@pytest.mark.parametrize("llamada, se_rechaza", [
    # Empezar el alta o preguntar por ella: no se puede.
    (_llamada("crear_tarea", {}), True),
    (_llamada("ofrecer_opciones", {"pregunta": "¿Qué objetivo?",
                                   "opciones": [{"texto": "A"}]}), True),
    (_llamada("ofrecer_opciones", {"pregunta": "¿Y esta?",
                                   "opciones": [{"tarea_id": "t1"},
                                                {"texto": "Otra"}]}), True),
    (_llamada("ofrecer_opciones", {"pregunta": "¿?", "opciones": []}), True),
    (_llamada("ofrecer_opciones", {"pregunta": "¿?"}), True),
    (_llamada("ofrecer_opciones", {"pregunta": "¿?", "opciones": "A"}), True),
    (_llamada("ofrecer_opciones", {"pregunta": "¿?",
                                   "opciones": [{"tarea_id": ""}]}), True),
    # Lo que es de una tarea que ya existe, o no es una pregunta: sí.
    (_llamada("ofrecer_opciones", {"pregunta": "¿Cuál?",
                                   "opciones": [{"tarea_id": "t1"},
                                                {"tarea_id": "t2",
                                                 "accion": "menu"}]}), False),
    (_llamada("consultar_tareas", {}), False),
    (_llamada("registrar_bloqueo", {"tarea_id": "t1", "causa": "x"}), False),
])
def test_la_guarda_del_alta_distingue_lo_que_reabre_el_alta(llamada, se_rechaza):
    assert repite_lo_pendiente(llamada, _alta_dejada()) is se_rechaza


# ---------------------------------------------------------------------------
# T9-R3 (seguimientos de review-467d41b3f96573d5). La guarda del alta y lo que
# se dejó de lado viajan en el estado de la aclaración y siguen vigentes al
# retomar el mensaje tras los botones; y una pregunta legítima con opciones de
# texto sobre lo otro, que la guarda del alta rechaza, termina bien para la
# persona.
# ---------------------------------------------------------------------------

def test_la_guarda_del_alta_y_lo_dejado_sobreviven_a_los_botones_de_aclaracion(
        cliente_con_credencial, conn, corework, monkeypatch):
    from tests.test_alta_pregunta_pendiente import _mensaje_privado

    cliente = cliente_con_credencial
    ws = corework.workspace_id
    tg, _tarea_existente = _abrir_alta_de_la_persona(conn, ws)
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: ClienteJevGuionado(
        guion=[{"alcance": {"probabilities": {"una_tarea": 0.8,
                                              "varias_tareas": 0.0,
                                              "ninguna": 0.0}},
                "tarea": {"probabilities": {"T1": 0.5, "T2": 0.3}}}]))
    con_referencia = IntentRoute(IntentAction.NORMAL_CONVERSATION,
                                 trabajos=(REFERENCIA_DEL_OTRO_MENSAJE,))
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), con_referencia],
        guion=_guion_ofrecer([{"texto": "Conectar y automatizar equipos"}]))
    assert _mensaje_privado(
        cliente, tg, f"¿cómo va {REFERENCIA_DEL_OTRO_MENSAJE}?").status_code == 200

    # "Dejarlo" cierra el alta y se detiene en la aclaración: el modelo todavía no
    # habló, y lo dejado de lado ya viaja en el estado guardado de esa pregunta.
    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)
    assert proveedor.recibidos == []
    with admin(conn) as cur:
        pid = _pendiente(cur, ws, gateway._SENTINEL_ACLARACION)
        cur.execute("select args from pending_action where id = %s", (pid,))
        guardado = cur.fetchone()["args"]["no_proponer"]
        candidata = _opciones(cur, pid)[0]
    assert guardado["alta"] is True
    assert guardado["dejado"] == NOMBRE_DEL_TITULO_DEL_ALTA

    # Al tocar una candidata se retoma con la guarda puesta y el modelo lo sabe.
    assert _tocar(cliente, candidata["token"], tg).status_code == 200

    assert len(_rechazos_del_alta(proveedor)) == 1
    assert _opciones_ofrecidas(conn) == 0
    sistema = proveedor.recibidos[0][0]
    assert "acaba de dejar de lado" in sistema
    assert NOMBRE_DEL_TITULO_DEL_ALTA in sistema


def test_una_pregunta_de_texto_sobre_lo_otro_rechazada_por_el_alta_termina_bien(
        cliente, conn, corework, monkeypatch):
    """La persona deja el alta y pregunta otra cosa; el modelo quiere elegir con
    opciones de texto (la guarda del alta las rechaza: no se puede distinguir de un
    campo del alta) y termina preguntando. Lo que ve: lo que dejó de lado y una sola
    pregunta con botones que el sistema puede cumplir -- sin volver a ofrecerle
    armar la tarea nueva que acaba de soltar, y sin decir que se hizo algo."""
    ws = corework.workspace_id
    guion = [Respuesta(llamadas=[Llamada("q1", "ofrecer_opciones", {
                 "pregunta": "¿Cuál querés ver?",
                 "opciones": [{"texto": "Las mías"}, {"texto": "Las del equipo"}]})]),
             Respuesta(texto="¿Querés ver tus tareas o las del equipo?")]

    proveedor, tg, _tarea = _dejar_el_alta_y_ver_lo_otro(
        cliente, conn, ws, monkeypatch, guion)

    assert len(_rechazos_del_alta(proveedor)) == 1
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo, pending_action_id from message_outbox
                where chat_id = %s order by programado_para, dedupe_key""", (tg,))
        filas = cur.fetchall()
        # La pregunta de la rama ya había salido con sus botones; la última es
        # la del cierre de este turno.
        botones = [f for f in filas if f["pending_action_id"]][-1]
        cur.execute("select etiqueta from pending_action_option "
                    "where pending_action_id = %s order by orden",
                    (botones["pending_action_id"],))
        etiquetas = [f["etiqueta"] for f in cur.fetchall()]
    cuerpos = [f["cuerpo"] for f in filas]
    assert "¿Querés ver tus tareas o las del equipo?" in botones["cuerpo"]
    assert "Estado: sin cambios" not in "".join(cuerpos)     # nada se intentó cambiar
    assert not any("tarea nueva" in e for e in etiquetas)    # lo soltó
    assert any("tarea existente" in e for e in etiquetas)
    assert P.ETIQUETA_SALIR_OPCIONES in etiquetas
