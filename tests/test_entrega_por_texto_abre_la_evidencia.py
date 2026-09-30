"""Pedir entregar por texto sin evidencia abre la pregunta de evidencia de verdad
(R4-H3; ADR 0013 reglas 1 y 2, ADR 0005).

Cuarta ronda por Telegram: "quiero entregar el dash de lotes" -> el modelo llamó
`actualizar_estado(en_revision)`, la guarda lo rechazó por falta de evidencia y la
respuesta salió con los tres botones genéricos y una pregunta abierta guardada como
`_opciones_modelo`: la persona no supo dónde poner el link. Ahora, si el único
rechazo del turno es "falta la evidencia de la entrega" de UNA tarea de la persona,
el servidor abre la misma pregunta que abre "Ya la terminé" (`_dato_menu_tarea`,
acción `terminar`) y nada más: sin botones genéricos, sin texto libre del modelo y
con una sola respuesta. Se decide por el motivo tipado del rechazo de la herramienta,
nunca por lo que el modelo escriba.
"""

from __future__ import annotations

from prisma import gateway
from prisma import herramientas as H
from prisma import pendientes as P
from prisma.db import admin
from prisma.llm import Llamada, ProveedorGuionado, Respuesta

from tests.test_pedir_cambios_extremo_a_extremo import (  # noqa: F401
    _mensaje, _pendiente, _tarea, _tg, cliente)


def _guion(monkeypatch, *respuestas) -> ProveedorGuionado:
    proveedor = ProveedorGuionado(guion=list(respuestas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _entregar(tid):
    return Respuesta(llamadas=[Llamada("c1", "actualizar_estado", {
        "tarea_id": tid, "estado": "en_revision"})])


def _salidas(conn, ws, tg: int):
    with admin(conn) as cur:
        cur.execute("select cuerpo, pending_action_id from message_outbox "
                    "where workspace_id = %s and chat_id = %s "
                    "order by programado_para, dedupe_key", (ws, tg))
        return cur.fetchall()


def _escenario(conn, ws):
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    return tid, tg


def test_el_rechazo_por_falta_de_evidencia_lleva_un_motivo_tipado(corework, conn):
    from prisma.autoridad import Canal, identificar
    from prisma.db import espacio

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = identificar(cur, tg, Canal.ESPACIO, ws)
        rechazo = H._preparar_actualizar_estado(cur, quien, tid, "en_revision")

    assert rechazo["falta_tipo"] == H.FALTA_EVIDENCIA_DE_ENTREGA
    assert rechazo["en_revision"] is False


def test_entregar_por_texto_sin_evidencia_abre_la_pregunta_de_evidencia(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tid, tg = _escenario(conn, ws)
    proveedor = _guion(
        monkeypatch, _entregar(tid),
        # Lo que hoy se reescribe tras el rechazo: no tiene que llegar a la persona.
        Respuesta(texto="Para entregarla necesito la evidencia. ¿Me pasás el link?"),
        Respuesta(texto="¿Me pasás el link?"))

    assert _mensaje(cliente, tg, "quiero entregar la tarea").status_code == 200

    salidas = _salidas(conn, ws, tg)
    assert len(salidas) == 1, [s["cuerpo"] for s in salidas]
    cuerpo = salidas[0]["cuerpo"]
    assert "Programar HMI línea 2" in cuerpo
    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in cuerpo
    assert salidas[0]["pending_action_id"] is None       # sin botones
    # El texto no salió del modelo: la llamada a la herramienta fue la única.
    assert len(proveedor.recibidos) == 1
    with admin(conn) as cur:
        pid = _pendiente(cur, ws, P.SENTINEL_DATO_MENU_TAREA, chat_id=tg)
        cur.execute("select args from pending_action where id = %s", (pid,))
        args = cur.fetchone()["args"]
        cur.execute("select count(*) n from pending_action where workspace_id = %s "
                    "and herramienta = %s", (ws, P.SENTINEL_OPCIONES_MODELO))
        assert cur.fetchone()["n"] == 0
    assert args["accion"] == "terminar" and args["tarea_id"] == tid


def test_el_mensaje_siguiente_es_la_evidencia_y_va_a_la_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tid, tg = _escenario(conn, ws)
    _guion(monkeypatch, _entregar(tid))
    assert _mensaje(cliente, tg, "quiero entregar la tarea").status_code == 200

    _guion(monkeypatch)
    assert _mensaje(cliente, tg, "https://ejemplo.test/tablero").status_code == 200

    with admin(conn) as cur:
        pid = _pendiente(cur, ws, "actualizar_estado", chat_id=tg)
        cur.execute("select resumen from pending_action where id = %s", (pid,))
        resumen = cur.fetchone()["resumen"]
    assert "https://ejemplo.test/tablero" in resumen
    assert "Programar HMI línea 2" in resumen


def test_otro_rechazo_no_abre_la_pregunta_de_evidencia(
        cliente, conn, corework, monkeypatch):
    """Sólo el motivo tipado de "falta la evidencia de la entrega" la abre: una
    tarea que no es de la persona, por ejemplo, sigue el camino de siempre."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        ajena = _tarea(cur, ws, persona="Marcos Tarquini")
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _guion(monkeypatch, _entregar(ajena),
           Respuesta(texto="Esa tarea no es tuya."),
           Respuesta(texto="Esa tarea no es tuya."))

    assert _mensaje(cliente, tg, "quiero entregar la tarea").status_code == 200

    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action where workspace_id = %s "
                    "and herramienta = %s", (ws, P.SENTINEL_DATO_MENU_TAREA))
        assert cur.fetchone()["n"] == 0
