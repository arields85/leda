"""Un saludo suelto se contesta en UNA línea (R4-H1, R3-H8; ADR 0013).

Cuarta ronda por Telegram: a "hola", primer mensaje del día, Prisma mandó "👋 Buen
día", una línea en blanco y "Hola Ariel, ¿en qué te ayudo?", con los tres botones
genéricos. Regla del usuario (2026-09-30): una sola línea, "👋 Buen día Ariel, ¿en
qué te ayudo?"; y (R3-H8) un saludo sin rama abierta se contesta con un saludo y una
pregunta abierta, nunca repitiendo la lista de tareas.

Es un comando de la lista cerrada del ruteo (`IntentAction.GREETING`): el modelo sólo
clasifica; el texto lo arma el código, sin texto libre del modelo. Cuando el saludo
del día le corresponde a la persona, la línea lleva el saludo del día (`saludo.py`) y
el despachador no lo antepone otra vez; si ya lo recibió hoy, "Hola {nombre}, ...".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest

from prisma import pendientes as P
from prisma import saludo as S
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
                        Respuesta, RouteEnvelope, RoutingError, ROUTER_TOOL,
                        ROUTER_SYSTEM)

from tests.test_pedir_cambios_extremo_a_extremo import (  # noqa: F401
    _mensaje, _opciones, _pendiente, _tarea, _tg, cliente)

UNA_LINEA_DEL_DIA = re.compile(
    r"^👋 (Buen día|Buenas tardes|Buenas noches) Nahuel, ¿en qué te ayudo\?$")
UNA_LINEA_SIN_SALUDO_DEL_DIA = "Hola Nahuel, ¿en qué te ayudo?"


def _guion(monkeypatch, *rutas, respuestas=()):
    proveedor = ProveedorGuionado(guion=list(respuestas), rutas=list(rutas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _saludo_pendiente(conn, ws, nombre: str) -> None:
    """La persona todavía no recibió el saludo del día (la fixture compartida
    la marca como ya saludada)."""
    with admin(conn) as cur:
        cur.execute(
            """delete from greeting_state where membership_id in (
                 select m.id from membership m join app_user u on u.id = m.app_user_id
                  where m.workspace_id = %s and u.nombre = %s)""", (ws, nombre))
    conn.commit()


def _cuerpos(conn, ws, tg: int) -> list[str]:
    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox where workspace_id = %s and "
                    "chat_id = %s order by programado_para, dedupe_key", (ws, tg))
        return [f["cuerpo"] for f in cur.fetchall()]


def _despachar(conn, ws):
    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        despachar(cur, ws, transporte, cal, datetime.now(timezone.utc))
    conn.commit()
    return transporte


def _ultima_fecha_saludo(conn, ws, nombre: str):
    with admin(conn) as cur:
        cur.execute(
            """select g.ultima_fecha_local from greeting_state g
                 join membership m on m.id = g.membership_id
                 join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
        fila = cur.fetchone()
    return fila["ultima_fecha_local"] if fila else None


# ---------------------------------------------------------------------------
# El comando cerrado del ruteo
# ---------------------------------------------------------------------------

def test_el_saludo_suelto_es_un_comando_de_la_lista_cerrada_del_ruteo():
    assert IntentAction.GREETING.value in ROUTER_TOOL["input_schema"][
        "properties"]["action"]["enum"]
    ruta = RouteEnvelope(calls=(Llamada(
        "r", "route_intent", {"action": IntentAction.GREETING.value}),)).validate()
    assert ruta.action is IntentAction.GREETING
    assert IntentAction.GREETING.value in ROUTER_SYSTEM


def test_un_saludo_con_propuestas_de_tarea_sigue_siendo_invalido():
    sobre = RouteEnvelope(calls=(Llamada("r", "route_intent", {
        "action": IntentAction.GREETING.value, "task": {"title": "X"}}),))
    with pytest.raises(RoutingError, match="Only task creation can contain task "
                                           "proposals"):
        sobre.validate()


# ---------------------------------------------------------------------------
# La respuesta, de punta a punta por el webhook
# ---------------------------------------------------------------------------

def test_hola_con_el_saludo_del_dia_pendiente_sale_en_una_sola_linea(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _saludo_pendiente(conn, ws, "Nahuel Gimenez")
    proveedor = _guion(monkeypatch, IntentRoute(IntentAction.GREETING))

    assert _mensaje(cliente, tg, "hola").status_code == 200

    # El texto no sale del modelo: el guion de respuestas está vacío.
    assert proveedor.recibidos == []
    transporte = _despachar(conn, ws)
    enviados = [e for e in transporte.enviados if e.chat_id == tg]
    assert len(enviados) == 1
    assert UNA_LINEA_DEL_DIA.match(enviados[0].texto), enviados[0].texto
    assert "\n" not in enviados[0].texto
    assert _ultima_fecha_saludo(conn, ws, "Nahuel Gimenez") is not None
    # Los tres botones genéricos siguen, sobre una pregunta abierta marcada.
    assert [b.etiqueta for b in enviados[0].botones] == [
        "Es una tarea nueva", "Es sobre una tarea existente",
        P.ETIQUETA_SALIR_OPCIONES]


def test_hola_con_el_saludo_del_dia_ya_dado_sale_sin_saludo_del_dia(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()  # la fixture ya dejó a la persona como saludada hoy
    _guion(monkeypatch, IntentRoute(IntentAction.GREETING))

    assert _mensaje(cliente, tg, "hola").status_code == 200

    transporte = _despachar(conn, ws)
    enviados = [e.texto for e in transporte.enviados if e.chat_id == tg]
    assert enviados == [UNA_LINEA_SIN_SALUDO_DEL_DIA]


def test_hola_deja_la_pregunta_abierta_marcada_como_cierre_generico(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _guion(monkeypatch, IntentRoute(IntentAction.GREETING))

    assert _mensaje(cliente, tg, "hola").status_code == 200

    with admin(conn) as cur:
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO, chat_id=tg)
        cur.execute("select args from pending_action where id = %s", (pid,))
        args = cur.fetchone()["args"]
    assert args["cierre_generico"] is True
    assert args["pregunta"] == UNA_LINEA_SIN_SALUDO_DEL_DIA


def test_el_saludo_del_dia_no_se_duplica_con_el_del_despachador_ni_se_repite(
        cliente, conn, corework, monkeypatch):
    """Dos "hola" seguidos el mismo día: el primero lleva el saludo del día en su
    línea; el segundo, ya sin saludo del día, dice "Hola Nahuel, ..."."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _saludo_pendiente(conn, ws, "Nahuel Gimenez")
    _guion(monkeypatch, IntentRoute(IntentAction.GREETING),
           IntentRoute(IntentAction.GREETING))

    assert _mensaje(cliente, tg, "hola").status_code == 200
    primero = [e.texto for e in _despachar(conn, ws).enviados if e.chat_id == tg]
    assert _mensaje(cliente, tg, "hola de nuevo").status_code == 200
    segundo = [e.texto for e in _despachar(conn, ws).enviados if e.chat_id == tg]

    assert len(primero) == 1 and UNA_LINEA_DEL_DIA.match(primero[0])
    assert segundo == [UNA_LINEA_SIN_SALUDO_DEL_DIA]


def test_dos_saludos_antes_de_un_despacho_solo_el_primero_lleva_el_saludo_del_dia(
        cliente, conn, corework, monkeypatch):
    """Dos "hola" encolados antes de que el despachador corra: los dos se armarían
    con el saludo del día pendiente, y como cada uno se marca como su propio saludo
    (`es_bienvenida`) el despachador no antepone nada a ninguno. Sólo el primero lo
    lleva; el segundo es el "Hola {nombre}" de siempre."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _saludo_pendiente(conn, ws, "Nahuel Gimenez")
    _guion(monkeypatch, IntentRoute(IntentAction.GREETING),
           IntentRoute(IntentAction.GREETING))

    assert _mensaje(cliente, tg, "hola").status_code == 200
    assert _mensaje(cliente, tg, "buenas").status_code == 200

    enviados = [e.texto for e in _despachar(conn, ws).enviados if e.chat_id == tg]
    assert len(enviados) == 2, enviados
    assert UNA_LINEA_DEL_DIA.match(enviados[0]), enviados[0]
    assert enviados[1] == UNA_LINEA_SIN_SALUDO_DEL_DIA


def test_un_saludo_seguido_de_un_pedido_se_contesta_sobre_la_tarea_no_con_la_linea_fija(
        cliente, conn, corework, monkeypatch):
    """Banco b-0035: "hola, ¿cómo va el PLC?" no es un saludo suelto -- el ruteo lo
    deja como conversación normal --, así que responde el modelo sobre la tarea y
    nunca sale la línea fija del saludo."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws, titulo="Programar PLC de la comprimidora (simulado)")
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _saludo_pendiente(conn, ws, "Nahuel Gimenez")
    proveedor = _guion(
        monkeypatch, IntentRoute(IntentAction.NORMAL_CONVERSATION),
        respuestas=[
            Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="«Programar PLC de la comprimidora (simulado)» sigue "
                            "en curso.")])

    assert _mensaje(cliente, tg, "hola, ¿cómo va el PLC?").status_code == 200

    assert proveedor.recibidos, "el modelo tenía que contestar el pedido"
    enviados = [e.texto for e in _despachar(conn, ws).enviados if e.chat_id == tg]
    assert enviados and "PLC" in enviados[0], enviados
    assert not any("¿en qué te ayudo?" in t for t in enviados), enviados


def test_una_persona_sin_nombre_no_lo_inventa():
    assert S.linea_de_saludo(None, None) == "Hola, ¿en qué te ayudo?"
    assert S.linea_de_saludo("Ariel De Simone", None) == (
        "Hola Ariel, ¿en qué te ayudo?")
    assert S.linea_de_saludo("Ariel De Simone", S.SALUDO_MANANA) == (
        "👋 Buen día Ariel, ¿en qué te ayudo?")
    assert S.linea_de_saludo(None, S.SALUDO_TARDE) == (
        "👋 Buenas tardes, ¿en qué te ayudo?")
