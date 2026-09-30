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


# ---------------------------------------------------------------------------
# Revisión review-167e3c98261bbc91: la evidencia puede venir en el mismo mensaje
# ---------------------------------------------------------------------------

def _entregar_con(tid, evidencia):
    return Respuesta(llamadas=[Llamada("c2", "actualizar_estado", {
        "tarea_id": tid, "estado": "en_revision", "evidencia_texto": evidencia})])


def _hay_pendiente(conn, ws, herramienta: str, tg: int) -> bool:
    with admin(conn) as cur:
        cur.execute("select 1 from pending_action where workspace_id = %s and "
                    "herramienta = %s and chat_id = %s and estado = 'esperando'",
                    (ws, herramienta, tg))
        return cur.fetchone() is not None


def test_con_un_enlace_en_el_mensaje_el_modelo_puede_reintentar_con_la_evidencia(
        cliente, conn, corework, monkeypatch):
    """El mensaje trae un enlace (entidad `url`) y el modelo, en su primera llamada,
    la omitió: el rechazo no corta el turno, el modelo reintenta con la evidencia y
    la persona llega a la vista previa sin que se le pida reenviarla."""
    from tests.test_evidencia_con_enlace_va_a_la_vista_previa import _con_entidades

    ws = corework.workspace_id
    tid, tg = _escenario(conn, ws)
    proveedor = _guion(
        monkeypatch, _entregar(tid),
        _entregar_con(tid, "https://ejemplo.test/tablero"),
        Respuesta(texto="Listo, mirá la vista previa."))
    texto = "entrego la tarea: https://ejemplo.test/tablero"

    assert _con_entidades(cliente, tg, texto, [
        {"type": "url", "offset": 20, "length": 28}]).status_code == 200

    assert len(proveedor.recibidos) >= 2
    assert _hay_pendiente(conn, ws, "actualizar_estado", tg)
    assert not _hay_pendiente(conn, ws, P.SENTINEL_DATO_MENU_TAREA, tg)
    salidas = _salidas(conn, ws, tg)
    assert not any(gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in s["cuerpo"]
                   for s in salidas), [s["cuerpo"] for s in salidas]


def test_con_un_enlace_si_el_modelo_no_reintenta_igual_se_pide_la_evidencia(
        cliente, conn, corework, monkeypatch):
    """Si al final del turno el único resultado sigue siendo el rechazo por falta de
    evidencia, se abre la pregunta de siempre."""
    from tests.test_evidencia_con_enlace_va_a_la_vista_previa import _con_entidades

    ws = corework.workspace_id
    tid, tg = _escenario(conn, ws)
    _guion(monkeypatch, _entregar(tid), Respuesta(texto="Falta la evidencia."))

    assert _con_entidades(cliente, tg, "entrego la tarea, mirá https://x.test", [
        {"type": "url", "offset": 26, "length": 14}]).status_code == 200

    salidas = _salidas(conn, ws, tg)
    assert len(salidas) == 1, [s["cuerpo"] for s in salidas]
    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in salidas[0]["cuerpo"]
    assert _hay_pendiente(conn, ws, P.SENTINEL_DATO_MENU_TAREA, tg)


def test_sin_enlace_se_corta_en_la_primera_vuelta(
        cliente, conn, corework, monkeypatch):
    """Sin la señal estructural se conserva el corte temprano: una sola vuelta del
    modelo y la pregunta de evidencia."""
    ws = corework.workspace_id
    tid, tg = _escenario(conn, ws)
    proveedor = _guion(monkeypatch, _entregar(tid),
                       _entregar_con(tid, "algo"), Respuesta(texto="Listo."))

    assert _mensaje(cliente, tg, "quiero entregar la tarea").status_code == 200

    assert len(proveedor.recibidos) == 1
    assert _hay_pendiente(conn, ws, P.SENTINEL_DATO_MENU_TAREA, tg)
    assert not _hay_pendiente(conn, ws, "actualizar_estado", tg)


def test_un_rechazo_por_evidencia_mezclado_con_otro_no_se_convierte_en_la_pregunta(
        cliente, conn, corework, monkeypatch):
    """Si otra llamada `actualizar_estado` del mismo turno se rechazó por otro motivo
    (una tarea que no es de la persona), esa causa no puede quedar sin decirse: el
    turno sigue el camino de siempre, que informa que no se aplicó nada."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        propia = _tarea(cur, ws)
        ajena = _tarea(cur, ws, titulo="Reporte semanal", persona="Marcos Tarquini")
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _guion(monkeypatch,
           Respuesta(llamadas=[
               Llamada("c1", "actualizar_estado",
                       {"tarea_id": propia, "estado": "en_revision"}),
               Llamada("c2", "actualizar_estado",
                       {"tarea_id": ajena, "estado": "en_revision"})]),
           Respuesta(texto="No pude entregar ninguna."),
           Respuesta(texto="No pude entregar ninguna."))

    assert _mensaje(cliente, tg, "entrego las dos").status_code == 200

    assert not _hay_pendiente(conn, ws, P.SENTINEL_DATO_MENU_TAREA, tg)
    salidas = _salidas(conn, ws, tg)
    assert len(salidas) == 1, [s["cuerpo"] for s in salidas]
    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA not in salidas[0]["cuerpo"]
