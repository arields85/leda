"""Cada mensaje recibe exactamente una respuesta visible (T9-R2, ADR 0013 regla 2).

Al terminar de procesar un mensaje entrante, un control estructural mira lo
encolado para ese mensaje (`message_outbox.entrante_id`, migración 0021): sin
respuesta, sale el aviso neutro y queda el incidente; con más de una respuesta
independiente, queda una sola y el incidente dice qué se suprimió. Una
respuesta puede tener varias partes y un juego de botones. Los toques no
entran (regla 4, T9-R4).

Ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from leda import gateway
from leda.db import admin
from leda.llm import ProveedorGuionado, Respuesta
from leda.respuesta_unica import grupo_de

from tests.test_menu_tarea import _mensaje, cliente  # noqa: F401


def _tg(conn, nombre="Nahuel Gimenez") -> int:
    with admin(conn) as cur:
        cur.execute("select telegram_user_id t from app_user where nombre = %s",
                    (nombre,))
        return cur.fetchone()["t"]


def _con_respuesta_del_modelo(monkeypatch, texto="Anotado.") -> ProveedorGuionado:
    proveedor = ProveedorGuionado([Respuesta(texto=texto)] * 4)
    monkeypatch.setattr("leda.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _filas_de_salida(conn, chat_id) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            """select id, cuerpo, estado, es_respuesta, entrante_id,
                      respuesta_grupo, dedupe_key, pending_action_id
                 from message_outbox where chat_id = %s
                order by programado_para, dedupe_key""", (chat_id,))
        return cur.fetchall()


def _incidentes(conn, ws, etapa=None) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            """select etapa, severidad, resumen_sanitizado, referencia_tipo,
                      referencia_id, chat_id
                 from incident where workspace_id = %s
                  and (%s::text is null or etapa = %s) order by at""",
            (ws, etapa, etapa))
        return cur.fetchall()


def _entrantes(conn, chat_id) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select id, texto from inbound_message where chat_id = %s "
                    "order by at", (chat_id,))
        return cur.fetchall()


def test_la_respuesta_queda_atada_al_mensaje_que_contesta(
        cliente, conn, corework, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    assert _mensaje(cliente, tg, "hola").status_code == 200

    (entrante,) = _entrantes(conn, tg)
    filas = _filas_de_salida(conn, tg)
    assert filas and all(f["es_respuesta"] for f in filas)
    assert {str(f["entrante_id"]) for f in filas} == {str(entrante["id"])}


def _sin_respuesta(monkeypatch):
    monkeypatch.setattr(gateway, "_turno", lambda *a, **k: None)


def _turno_que_encola(monkeypatch, *responder):
    """Un turno que encola lo que diga cada `responder(cur, ws, chat, quien,
    ahora)`: reemplaza el camino de interpretación, no el control."""
    def turno(cur, quien, texto, workspace_id, chat_id, entrante_id=None, **_k):
        ahora = datetime.now(timezone.utc)
        for i, accion in enumerate(responder):
            accion(cur, workspace_id, chat_id, quien, ahora + timedelta(seconds=i))

    monkeypatch.setattr(gateway, "_turno", turno)


def _texto(cuerpo, **kw):
    def accion(cur, ws, chat, quien, ahora):
        gateway._responder(cur, ws, chat, quien, cuerpo, ahora, **kw)
    return accion


def test_sin_ninguna_respuesta_sale_el_aviso_neutro_y_queda_el_incidente(
        cliente, conn, corework, monkeypatch):
    _sin_respuesta(monkeypatch)
    tg = _tg(conn)

    assert _mensaje(cliente, tg, "hola").status_code == 200

    (fila,) = _filas_de_salida(conn, tg)
    assert fila["cuerpo"] == gateway.NOTICIA_NEUTRA_INCIDENTE
    (entrante,) = _entrantes(conn, tg)
    assert str(fila["entrante_id"]) == str(entrante["id"])
    (inc,) = _incidentes(conn, corework.workspace_id, "sin_respuesta")
    assert inc["referencia_tipo"] == "inbound_message"
    assert str(inc["referencia_id"]) == str(entrante["id"])
    assert inc["chat_id"] == tg


def test_dos_respuestas_independientes_dejan_una_y_el_incidente_dice_cual_se_suprimio(
        cliente, conn, corework, monkeypatch):
    _turno_que_encola(monkeypatch, _texto("Primera respuesta."),
                      _texto("Segunda respuesta."))
    tg = _tg(conn)

    _mensaje(cliente, tg, "hola")

    filas = _filas_de_salida(conn, tg)
    visibles = [f for f in filas if f["estado"] != "descartado"]
    assert [f["cuerpo"] for f in visibles] == ["Primera respuesta."]
    assert [f["cuerpo"] for f in filas if f["estado"] == "descartado"] == [
        "Segunda respuesta."]
    (inc,) = _incidentes(conn, corework.workspace_id, "respuesta_duplicada")
    assert "2 respuestas independientes" in inc["resumen_sanitizado"]
    assert "se suprimieron 1" in inc["resumen_sanitizado"]
    assert "Segunda respuesta" not in inc["resumen_sanitizado"]   # sin cuerpos


def test_la_respuesta_con_botones_se_conserva_aunque_no_sea_la_primera(
        cliente, conn, corework, monkeypatch):
    from leda import pendientes as P

    def con_botones(cur, ws, chat, quien, ahora):
        p = P.registrar(cur, quien, herramienta="actualizar_estado", args={},
                        resumen="¿Confirmás?", vence_en=ahora + timedelta(hours=1),
                        chat_id=chat, opciones=[("Sí", True), ("No", False)])
        gateway.enqueue_outbox(
            cur, workspace_id=ws, chat_id=chat, text="¿Confirmás?",
            recipient_membership_id=quien.membership_id, scheduled_for=ahora,
            dedupe_key=f"{ws}:prueba:botones", is_response=True,
            pending_action_id=p.id)

    _turno_que_encola(monkeypatch, _texto("Charla suelta."), con_botones)
    tg = _tg(conn)

    _mensaje(cliente, tg, "hola")

    visibles = [f for f in _filas_de_salida(conn, tg) if f["estado"] != "descartado"]
    assert [f["cuerpo"] for f in visibles] == ["¿Confirmás?"]
    (inc,) = _incidentes(conn, corework.workspace_id, "respuesta_duplicada")
    assert "la que ofrece botones" in inc["resumen_sanitizado"]


def test_las_partes_de_una_misma_respuesta_no_son_dos_respuestas(
        cliente, conn, corework, monkeypatch):
    largo = "\n\n".join(f"Párrafo {i}. " + "palabra " * 60 for i in range(20))
    _turno_que_encola(monkeypatch, _texto(largo))    # `_responder` parte el texto
    tg = _tg(conn)

    _mensaje(cliente, tg, "hola")

    filas = _filas_de_salida(conn, tg)
    assert len(filas) > 1 and all(f["estado"] != "descartado" for f in filas)
    assert _incidentes(conn, corework.workspace_id) == []


def test_las_llamadas_de_un_mismo_grupo_son_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    def parte(cuerpo, clave):
        def accion(cur, ws, chat, quien, ahora):
            gateway.enqueue_outbox(
                cur, workspace_id=ws, chat_id=chat, text=cuerpo,
                recipient_membership_id=quien.membership_id, scheduled_for=ahora,
                dedupe_key=f"{ws}:prueba:{clave}", is_response=True,
                grupo_respuesta=f"{ws}:prueba")
        return accion

    _turno_que_encola(monkeypatch, parte("Texto.", "texto"), parte("Botones.", "b"))
    tg = _tg(conn)

    _mensaje(cliente, tg, "hola")

    filas = _filas_de_salida(conn, tg)
    assert [f["cuerpo"] for f in filas] == ["Texto.", "Botones."]
    assert _incidentes(conn, corework.workspace_id) == []


# ---------------------------------------------------------------------------
# Mensajes sin texto (H15): foto, archivo, audio, nota de voz, video, sticker
# ---------------------------------------------------------------------------

from tests.test_pregunta_pendiente import _abiertas, _abrir_pregunta  # noqa: E402,F401

_ADJUNTOS = {
    "photo": [{"file_id": "f1", "width": 90, "height": 90}],
    "document": {"file_id": "f2", "file_name": "informe.pdf"},
    "audio": {"file_id": "f3", "duration": 9},
    "voice": {"file_id": "f4", "duration": 3},
    "video": {"file_id": "f5", "duration": 4},
    "sticker": {"file_id": "f6", "emoji": "x"},
}


def _con_adjunto(cliente, tg, tipo, epigrafe=None, message_id=5):
    mensaje = {"message_id": message_id, "chat": {"id": tg}, "from": {"id": tg},
               tipo: _ADJUNTOS[tipo]}
    if epigrafe is not None:
        mensaje["caption"] = epigrafe
    return cliente.post("/telegram/corework", json={"message": mensaje},
                        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _visibles(conn, chat_id) -> list[dict]:
    return [f for f in _filas_de_salida(conn, chat_id) if f["estado"] != "descartado"]


@pytest.mark.parametrize("tipo", sorted(_ADJUNTOS))
def test_un_adjunto_sin_epigrafe_recibe_una_sola_respuesta_que_pide_texto_o_link(
        tipo, cliente, conn, corework, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    assert _con_adjunto(cliente, tg, tipo).status_code == 200

    (fila,) = _visibles(conn, tg)
    assert fila["cuerpo"] == gateway.AVISO_SIN_ADJUNTOS
    assert "fotos, archivos ni audios" in fila["cuerpo"]
    assert "texto o un link" in fila["cuerpo"]
    assert proveedor.ruteados == []                 # sin texto no hay qué interpretar
    assert _incidentes(conn, corework.workspace_id) == []
    (entrante,) = _entrantes(conn, tg)
    assert entrante["texto"] == ""
    assert str(fila["entrante_id"]) == str(entrante["id"])


@pytest.mark.parametrize("tipo", ["photo", "document", "video", "audio"])
def test_el_epigrafe_se_procesa_como_texto_y_avisa_que_el_adjunto_no_se_guarda(
        tipo, cliente, conn, corework, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    assert _con_adjunto(cliente, tg, tipo, "¿qué tengo pendiente?").status_code == 200

    assert proveedor.ruteados == ["¿qué tengo pendiente?"]     # el epígrafe es el texto
    filas = _visibles(conn, tg)
    assert [f["cuerpo"] for f in filas] == [gateway.NOTA_ADJUNTO_NO_GUARDADO,
                                            "Anotado."]
    # La nota y la respuesta son partes de UNA respuesta: comparten el grupo
    # (`respuesta_unica.grupo_de`), la fila de la nota incluida.
    assert len({grupo_de(f) for f in filas}) == 1
    assert _incidentes(conn, corework.workspace_id) == []      # una sola respuesta
    (entrante,) = _entrantes(conn, tg)
    assert entrante["texto"] == "¿qué tengo pendiente?"


def test_un_adjunto_sin_epigrafe_con_una_pregunta_abierta_la_vuelve_a_hacer_en_la_misma_respuesta(
        cliente, conn, corework, monkeypatch):
    tid, tg = _abrir_pregunta(cliente, conn, corework.workspace_id, monkeypatch,
                              "Ya la terminé")
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    antes = len(_filas_de_salida(conn, tg))

    assert _con_adjunto(cliente, tg, "photo").status_code == 200

    nuevas = _filas_de_salida(conn, tg)[antes:]
    (fila,) = nuevas
    assert fila["cuerpo"].startswith(gateway.AVISO_SIN_ADJUNTOS)
    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in fila["cuerpo"]
    assert _abiertas(conn) == 1                       # la pregunta sigue abierta
    assert proveedor.ruteados == []
    assert _incidentes(conn, corework.workspace_id) == []


def test_un_mensaje_sin_contenido_de_persona_no_se_responde_ni_falla(
        cliente, conn, corework, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    r = cliente.post(
        "/telegram/corework",
        json={"message": {"message_id": 8, "chat": {"id": tg}, "from": {"id": tg},
                          "new_chat_title": "Equipo"}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})

    assert r.status_code == 200
    assert _filas_de_salida(conn, tg) == []
    assert _incidentes(conn, corework.workspace_id) == []


def test_un_error_no_manejado_deja_su_aviso_como_la_unica_respuesta_atada_al_mensaje(
        cliente, conn, corework, monkeypatch):
    def turno_roto(*a, **k):
        raise RuntimeError("falló algo interno")

    monkeypatch.setattr(gateway, "_turno", turno_roto)
    tg = _tg(conn)

    _mensaje(cliente, tg, "hola")

    (fila,) = _filas_de_salida(conn, tg)
    assert fila["cuerpo"] == gateway.NOTICIA_NEUTRA_INCIDENTE
    (entrante,) = _entrantes(conn, tg)
    assert str(fila["entrante_id"]) == str(entrante["id"])
    (inc,) = _incidentes(conn, corework.workspace_id)
    assert inc["etapa"] == "turno_texto"        # sólo el de la red de contención


def test_un_toque_no_es_un_mensaje_ni_queda_como_mensaje_sin_respuesta(
        cliente, conn, corework, monkeypatch):
    from tests.test_menu_tarea import _tocar

    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    _tocar(cliente, "token-inexistente", tg)      # una fila de actividad, sin texto

    with admin(conn) as cur:
        cur.execute("select texto from inbound_message where chat_id = %s", (tg,))
        assert [f["texto"] for f in cur.fetchall()] == [None]
    assert _incidentes(conn, corework.workspace_id, "sin_respuesta") == []
    # T9-R4: el toque se controla como un mensaje, con su propia fila como el
    # entrante (la de actividad, sin texto): una sola respuesta atada a ella.
    with admin(conn) as cur:
        cur.execute("select id from inbound_message where chat_id = %s", (tg,))
        (toque,) = cur.fetchall()
    assert [str(f["entrante_id"]) for f in _filas_de_salida(conn, tg)] == [
        str(toque["id"])]
