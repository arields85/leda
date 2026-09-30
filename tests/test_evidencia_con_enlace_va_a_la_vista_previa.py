"""Con la pregunta de evidencia abierta, un enlace ES la respuesta (R4-H9; ADR
0005, ADR 0013 regla 1).

Cuarta ronda por Telegram: con "Contame brevemente qué hiciste o pasame un link."
abierta, mandar `google.com` disparó "¿Esto es la evidencia de la entrega de «X»?"
[Sí, es eso] [No, es otra cosa] y sólo después la vista previa con Confirmar: dos
confirmaciones para un dato que se acababa de pedir. Esa pregunta intermedia existe
por R3-H17 (un "hola" no es evidencia) y se conserva para lo que no tiene forma de
evidencia. Cuando el mensaje trae una señal estructural -- una entidad `url` o
`text_link` de Telegram, nunca patrones de texto --, la duda del ruteo se resuelve
sola: es la respuesta y sigue directo la vista previa.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
                        RespectoPendiente, Respuesta)

from tests.toques import id_de_mensaje
from tests.test_pedir_cambios_extremo_a_extremo import (  # noqa: F401
    _mensaje, _pendiente, _quien, _tarea, _tg, cliente)


def _ruta(respecto: RespectoPendiente) -> IntentRoute:
    return IntentRoute(IntentAction.NORMAL_CONVERSATION,
                       respecto_pendiente=respecto)


def _guion(monkeypatch, *respuestas, rutas=()) -> ProveedorGuionado:
    proveedor = ProveedorGuionado(guion=list(respuestas), rutas=list(rutas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _con_entidades(cliente, user_id, texto, entidades):
    return cliente.post(
        "/telegram/corework",
        json={"message": {"message_id": id_de_mensaje(), "text": texto,
                          "chat": {"id": user_id}, "from": {"id": user_id},
                          "entities": entidades}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _abrir_pregunta_de_evidencia(cliente, conn, ws, monkeypatch):
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _guion(monkeypatch, Respuesta(llamadas=[Llamada("c1", "actualizar_estado", {
        "tarea_id": tid, "estado": "en_revision"})]))
    assert _mensaje(cliente, tg, "quiero entregar la tarea").status_code == 200
    return tid, tg


def _ids(conn, ws, tg: int) -> set:
    with admin(conn) as cur:
        cur.execute("select id from message_outbox where workspace_id = %s and "
                    "chat_id = %s", (ws, tg))
        return {f["id"] for f in cur.fetchall()}


def _salidas_tras(conn, ws, tg: int, antes: set) -> list[str]:
    with admin(conn) as cur:
        cur.execute("select id, cuerpo from message_outbox where workspace_id = %s "
                    "and chat_id = %s order by programado_para, dedupe_key",
                    (ws, tg))
        return [f["cuerpo"] for f in cur.fetchall() if f["id"] not in antes]


def _hay(conn, ws, herramienta: str, tg: int) -> bool:
    with admin(conn) as cur:
        cur.execute("select 1 from pending_action where workspace_id = %s and "
                    "herramienta = %s and chat_id = %s and estado = 'esperando'",
                    (ws, herramienta, tg))
        return cur.fetchone() is not None


def test_un_enlace_con_la_pregunta_de_evidencia_abierta_va_directo_a_la_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tid, tg = _abrir_pregunta_de_evidencia(cliente, conn, ws, monkeypatch)
    antes = _ids(conn, ws, tg)
    _guion(monkeypatch, rutas=[_ruta(RespectoPendiente.DUDOSO)])

    resp = _con_entidades(cliente, tg, "google.com",
                          [{"type": "url", "offset": 0, "length": 10}])
    assert resp.status_code == 200

    salidas = _salidas_tras(conn, ws, tg, antes)
    assert len(salidas) == 1, salidas
    assert "google.com" in salidas[0]
    assert "¿Esto es" not in salidas[0]
    assert _hay(conn, ws, "actualizar_estado", tg)
    assert not _hay(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU, tg)


def test_un_enlace_con_texto_visible_tambien_es_la_respuesta_y_conserva_la_url(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tid, tg = _abrir_pregunta_de_evidencia(cliente, conn, ws, monkeypatch)
    _guion(monkeypatch, rutas=[_ruta(RespectoPendiente.DUDOSO)])

    resp = _con_entidades(cliente, tg, "el tablero", [
        {"type": "text_link", "offset": 3, "length": 7,
         "url": "https://ejemplo.test/tablero"}])
    assert resp.status_code == 200

    assert _hay(conn, ws, "actualizar_estado", tg)
    with admin(conn) as cur:
        cur.execute("select resumen from pending_action where workspace_id = %s "
                    "and herramienta = 'actualizar_estado' and chat_id = %s "
                    "and estado = 'esperando'", (ws, tg))
        assert "https://ejemplo.test/tablero" in cur.fetchone()["resumen"]


def test_sin_senal_de_enlace_la_duda_sigue_preguntando(
        cliente, conn, corework, monkeypatch):
    """R3-H17: un mensaje sin forma de evidencia que el ruteo duda sigue con la
    pregunta "¿Esto es...?", aunque tenga otras entidades (negrita, mención)."""
    ws = corework.workspace_id
    tid, tg = _abrir_pregunta_de_evidencia(cliente, conn, ws, monkeypatch)
    _guion(monkeypatch, rutas=[_ruta(RespectoPendiente.DUDOSO)])

    resp = _con_entidades(cliente, tg, "hola", [
        {"type": "bold", "offset": 0, "length": 4}])
    assert resp.status_code == 200

    assert _hay(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU, tg)
    assert not _hay(conn, ws, "actualizar_estado", tg)


def test_un_enlace_no_cambia_lo_que_decidio_el_ruteo_si_no_era_duda(
        cliente, conn, corework, monkeypatch):
    """La señal sólo resuelve la duda: si el ruteo entendió que la persona deja
    lo pendiente, se respeta."""
    ws = corework.workspace_id
    tid, tg = _abrir_pregunta_de_evidencia(cliente, conn, ws, monkeypatch)
    _guion(monkeypatch, rutas=[_ruta(RespectoPendiente.CANCELA)])

    resp = _con_entidades(cliente, tg, "dejalo, ya lo hago en https://x.test",
                          [{"type": "url", "offset": 22, "length": 14}])
    assert resp.status_code == 200

    assert not _hay(conn, ws, "actualizar_estado", tg)
    assert not _hay(conn, ws, P.SENTINEL_DATO_MENU_TAREA, tg)


def test_un_enlace_en_otra_pregunta_de_dato_no_la_responde_solo(
        cliente, conn, corework, monkeypatch):
    """La señal es de la pregunta de evidencia: el motivo de "Pedir cambios" con un
    enlace adentro sigue por la duda del ruteo."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        p = P.registrar(cur, quien, herramienta=P.SENTINEL_DATO_MENU_TAREA,
                        args={"accion": "pedir_cambios", "tarea_id": "t",
                              "titulo": "X"},
                        resumen="¿Qué falta corregir en «X»?",
                        vence_en=ahora + timedelta(hours=8), chat_id=tg,
                        opciones=[])
        P.marcar_para_corregir(cur, quien, p.id, tg, ahora)
    conn.commit()
    _guion(monkeypatch, rutas=[_ruta(RespectoPendiente.DUDOSO)])

    resp = _con_entidades(cliente, tg, "mirá https://x.test", [
        {"type": "url", "offset": 5, "length": 14}])
    assert resp.status_code == 200

    assert _hay(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU, tg)
