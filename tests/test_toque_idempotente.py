"""Todo toque tiene señal inmediata y es idempotente (T9-R4, ADR 0013 regla 4).

Mecanismo, en el orden en que corre `gateway._toque`:

- El acuse del toque (`acusar_toque`) sale antes de cualquier trabajo y para
  TODO toque, aunque no sea de un botón de Prisma o vaya a absorberse.
- El procesamiento del toque va envuelto en el indicador de actividad (ADR 0011):
  no aparece nada si termina antes del umbral.
- "El mismo botón" es el mismo `callback_data` (lleva el token de la opción, único
  por botón), de la misma persona, en el mismo chat. Se guarda en
  `inbound_message.boton_callback`. El segundo toque dentro de
  `gateway.VENTANA_TOQUE_REPETIDO` (10 s) se absorbe: sólo el acuse, ni efecto ni
  error ni "ya no está vigente". Fuera de la ventana, o de otra persona, se
  contesta como siempre.
- Cada toque que no se absorbe recibe exactamente una respuesta visible
  (`respuesta_unica.controlar`, con la fila del toque como el mensaje entrante).
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from prisma import gateway
from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.respuesta_unica import (ETAPA_RESPUESTA_DUPLICADA,
                                    ETAPA_SIN_RESPUESTA)

from tests.test_botones import _quien, _tarea, _telegram_id, cliente  # noqa: F401
from tests.toques import (FUERA_DE_LA_VENTANA, MITAD_DE_LA_VENTANA_MAS_UNO,
                          envejecer_toques)
from tests.test_una_respuesta import _filas_de_salida, _incidentes, _tg

PERSONA = "Marcos Tarquini"
OTRA = "Nahuel Gimenez"


def _tocar_boton(cliente, token, user_id, *, callback_id="cb1", chat=None):
    return cliente.post(
        "/telegram/corework",
        json={"callback_query": {
            "id": callback_id, "from": {"id": user_id}, "data": f"p:{token}",
            "message": {"message_id": 7, "chat": {"id": chat or user_id,
                                                  "type": "private"}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _confirmar_en_curso(conn, ws):
    """Una acción pendiente de poner la tarea en curso, con su Confirmar. Devuelve
    (chat, token_de_confirmar, tarea)."""
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tarea = _tarea(cur, ws)
        tg = _telegram_id(cur, PERSONA)
        p = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": tarea, "estado": "en_curso"},
            resumen="poner Programar PLC en curso",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1), chat_id=tg)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
    conn.commit()
    return tg, token, tarea


def _pasos_a_en_curso(conn, tarea) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from task_state_event "
                    "where task_id = %s and estado_nuevo = 'en_curso'", (tarea,))
        return cur.fetchone()["n"]


def _respuestas(conn, tg) -> list[dict]:
    return [f for f in _filas_de_salida(conn, tg)
            if f["es_respuesta"] and f["estado"] != "descartado"]


# ---------------------------------------------------------------------------
# H13: el segundo toque del mismo botón se absorbe
# ---------------------------------------------------------------------------


def test_la_ventana_de_toque_repetido_es_de_10_segundos():
    assert gateway.VENTANA_TOQUE_REPETIDO == timedelta(seconds=10)


def test_doble_toque_en_la_ventana_un_efecto_y_una_respuesta(
        cliente, conn, corework):
    ws = corework.workspace_id
    tg, token, tarea = _confirmar_en_curso(conn, ws)

    assert _tocar_boton(cliente, token, tg, callback_id="a").status_code == 200
    assert _tocar_boton(cliente, token, tg, callback_id="b").status_code == 200

    assert _pasos_a_en_curso(conn, tarea) == 1
    (respuesta,) = _respuestas(conn, tg)
    assert "pasó a" in respuesta["cuerpo"]
    assert not any("no está vigente" in f["cuerpo"] for f in _filas_de_salida(conn, tg))
    for etapa in (ETAPA_SIN_RESPUESTA, ETAPA_RESPUESTA_DUPLICADA):
        assert _incidentes(conn, ws, etapa) == []


def test_el_toque_absorbido_se_acusa_y_queda_auditado(
        cliente, conn, corework, monkeypatch):
    acusados = []
    monkeypatch.setattr(
        gateway, "acusar_toque",
        lambda token, callback_id, cliente=None: acusados.append(callback_id))
    ws = corework.workspace_id
    tg, token, _tarea_id = _confirmar_en_curso(conn, ws)

    _tocar_boton(cliente, token, tg, callback_id="a")
    _tocar_boton(cliente, token, tg, callback_id="b")

    assert acusados == ["a", "b"]
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where accion = "
                    "'toque_repetido_absorbido'")
        assert cur.fetchone()["n"] == 1


def test_fuera_de_la_ventana_el_segundo_toque_se_contesta_como_siempre(
        cliente, conn, corework):
    ws = corework.workspace_id
    tg, token, tarea = _confirmar_en_curso(conn, ws)
    _tocar_boton(cliente, token, tg, callback_id="a")
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)

    _tocar_boton(cliente, token, tg, callback_id="b")

    assert _pasos_a_en_curso(conn, tarea) == 1
    cuerpos = [f["cuerpo"] for f in _respuestas(conn, tg)]
    assert len(cuerpos) == 2 and gateway.AVISO_PEDIDO_NO_VIGENTE in cuerpos[-1]


def test_un_toque_absorbido_no_prolonga_la_ventana(cliente, conn, corework):
    ws = corework.workspace_id
    tg, token, _tarea_id = _confirmar_en_curso(conn, ws)
    _tocar_boton(cliente, token, tg, callback_id="a")
    envejecer_toques(conn, MITAD_DE_LA_VENTANA_MAS_UNO)
    _tocar_boton(cliente, token, tg, callback_id="b")        # absorbido, a mitad de la ventana
    envejecer_toques(conn, MITAD_DE_LA_VENTANA_MAS_UNO)     # el primero, fuera de la ventana

    _tocar_boton(cliente, token, tg, callback_id="c")

    assert gateway.AVISO_PEDIDO_NO_VIGENTE in _respuestas(conn, tg)[-1]["cuerpo"]


def test_el_toque_de_otra_persona_no_se_absorbe(cliente, conn, corework):
    ws = corework.workspace_id
    tg, token, tarea = _confirmar_en_curso(conn, ws)
    otra = _tg(conn, OTRA)

    _tocar_boton(cliente, token, tg, callback_id="a")
    _tocar_boton(cliente, token, otra, callback_id="b", chat=tg)

    assert _pasos_a_en_curso(conn, tarea) == 1
    respuestas = _respuestas(conn, tg)
    assert len(respuestas) == 2                     # a ella se le contesta
    assert "pasó a" in respuestas[0]["cuerpo"]


def test_otro_boton_de_la_misma_persona_no_se_absorbe(cliente, conn, corework):
    ws = corework.workspace_id
    tg, token, tarea = _confirmar_en_curso(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        segunda = P.registrar(
            cur, quien, herramienta="actualizar_estado",
            args={"tarea_id": tarea, "estado": "en_curso"},
            resumen="otra", chat_id=tg,
            vence_en=datetime.now(timezone.utc) + timedelta(days=1))
        otro_token = P.opcion_por_etiqueta(cur, segunda.id, "Cancelar").token
    conn.commit()

    _tocar_boton(cliente, token, tg, callback_id="a")
    _tocar_boton(cliente, otro_token, tg, callback_id="b")

    assert len(_respuestas(conn, tg)) == 2


# ---------------------------------------------------------------------------
# H5: señal inmediata en cada toque
# ---------------------------------------------------------------------------


def test_todo_toque_se_acusa_aunque_no_sea_de_un_boton_de_prisma(
        cliente, conn, corework, monkeypatch):
    acusados = []
    monkeypatch.setattr(
        gateway, "acusar_toque",
        lambda token, callback_id, cliente=None: acusados.append(callback_id))

    r = cliente.post(
        "/telegram/corework",
        json={"callback_query": {
            "id": "ajeno", "from": {"id": 1}, "data": "otra-cosa",
            "message": {"message_id": 7, "chat": {"id": 1}}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})

    assert r.status_code == 200 and acusados == ["ajeno"]


def test_el_toque_se_procesa_con_el_indicador_de_actividad(
        cliente, conn, corework, monkeypatch):
    eventos = []

    @contextmanager
    def activo(token, chat_id, **kwargs):
        eventos.append(("inicio", chat_id, kwargs.get("chat_type")))
        try:
            yield
        finally:
            eventos.append(("fin", chat_id))

    monkeypatch.setattr(gateway, "mantener_chat_activo", activo)
    monkeypatch.setattr(
        gateway, "acusar_toque",
        lambda token, callback_id, cliente=None: eventos.append(("acuse", None)))
    ws = corework.workspace_id
    tg, token, _tarea_id = _confirmar_en_curso(conn, ws)

    _tocar_boton(cliente, token, tg)

    # El acuse sale primero; el indicador envuelve todo el procesamiento y se
    # retira cuando ya está encolada la respuesta.
    assert eventos == [("acuse", None), ("inicio", tg, "private"), ("fin", tg)]


# ---------------------------------------------------------------------------
# Una respuesta visible por toque
# ---------------------------------------------------------------------------


def test_un_toque_que_no_encola_nada_deja_el_aviso_neutro_y_un_incidente(
        cliente, conn, corework, monkeypatch):
    monkeypatch.setattr(gateway, "_seguir_resuelta", lambda *a, **k: None)
    ws = corework.workspace_id
    tg, token, _tarea_id = _confirmar_en_curso(conn, ws)

    _tocar_boton(cliente, token, tg)

    (respuesta,) = _respuestas(conn, tg)
    assert respuesta["cuerpo"] == gateway.NOTICIA_NEUTRA_INCIDENTE
    (incidente,) = _incidentes(conn, ws, ETAPA_SIN_RESPUESTA)
    assert incidente["referencia_tipo"] == "inbound_message"


def test_un_toque_con_dos_respuestas_independientes_deja_una(
        cliente, conn, corework, monkeypatch):
    def dos(cur, quien, workspace_id, chat_id, token, resuelta, pid, ahora):
        gateway._responder(cur, workspace_id, chat_id, quien, "Primera.", ahora)
        gateway._responder(cur, workspace_id, chat_id, quien, "Segunda.",
                           ahora + timedelta(seconds=1))

    monkeypatch.setattr(gateway, "_seguir_resuelta", dos)
    ws = corework.workspace_id
    tg, token, _tarea_id = _confirmar_en_curso(conn, ws)

    _tocar_boton(cliente, token, tg)

    assert [f["cuerpo"] for f in _respuestas(conn, tg)] == ["Primera."]
    assert len(_incidentes(conn, ws, ETAPA_RESPUESTA_DUPLICADA)) == 1


def test_la_respuesta_del_toque_queda_atada_a_la_fila_del_toque(
        cliente, conn, corework):
    ws = corework.workspace_id
    tg, token, _tarea_id = _confirmar_en_curso(conn, ws)

    _tocar_boton(cliente, token, tg)

    with admin(conn) as cur:
        cur.execute("select id, boton_callback from inbound_message "
                    "where chat_id = %s and boton_callback is not null", (tg,))
        (toque,) = cur.fetchall()
    assert toque["boton_callback"] == f"p:{token}"
    (respuesta,) = _respuestas(conn, tg)
    assert str(respuesta["entrante_id"]) == str(toque["id"])


# ---------------------------------------------------------------------------
# "Dejarlo y ver lo otro": el aviso de lo que se dejó y lo que contesta el camino
# normal son UNA respuesta
# ---------------------------------------------------------------------------


def test_dejarlo_y_ver_lo_otro_es_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    from prisma.llm import Respuesta
    from prisma.respuesta_unica import grupo_de

    from tests.test_rama_abierta_guarda import (_abrir_modificar,
                                                _dejar_y_ver_lo_otro)

    ws = corework.workspace_id
    tg, _a, _b = _abrir_modificar(cliente, conn, ws)

    _dejar_y_ver_lo_otro(cliente, conn, ws, tg, monkeypatch,
                         [Respuesta(texto="Tenés dos tareas abiertas.")])

    with admin(conn) as cur:
        cur.execute("select id from inbound_message where chat_id = %s "
                    "and boton_callback is not null order by at desc limit 1",
                    (tg,))
        toque = str(cur.fetchone()["id"])
    filas = [f for f in _filas_de_salida(conn, tg)
             if str(f["entrante_id"]) == toque]
    assert [f["cuerpo"] for f in filas][-1] == "Tenés dos tareas abiertas."
    assert len(filas) == 2                            # lo dejado y lo atendido
    assert filas[0]["cuerpo"] != filas[1]["cuerpo"]
    assert all(f["estado"] != "descartado" and f["es_respuesta"] for f in filas)
    assert len({grupo_de(f) for f in filas}) == 1     # una sola respuesta
    for etapa in (ETAPA_SIN_RESPUESTA, ETAPA_RESPUESTA_DUPLICADA):
        assert _incidentes(conn, ws, etapa) == []
