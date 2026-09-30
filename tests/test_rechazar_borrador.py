"""Quien confirma el borrador de otra persona lo RECHAZA, con un motivo, y a quien
lo pidió se le avisa (decisión del usuario, 2026-09-30; ADR 0013 reglas 1, 2 y 4).

Antes, quien confirmaba lo de otra persona veía Confirmar y Cancelar: "Cancelar"
cancelaba el borrador y sólo él se enteraba. Ahora el botón es Rechazar: pide el
motivo con la misma pregunta de texto libre que "Pedir cambios", y con el motivo el
borrador se cancela, quien confirma recibe un recibo corto y quien lo pidió recibe
un aviso de coordinación que dice quién lo rechazó y por qué. Cancelar su propio
borrador no cambia (sigue siendo "Cancelar", sin aviso a nadie).

Todo por el webhook real; los ruteos se guionan y ninguna prueba toca el modelo.
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import timedelta
from types import SimpleNamespace

from fastapi.testclient import TestClient

from prisma import gateway
from prisma import pendientes as P
from prisma.calendario import Calendario
from prisma.db import admin, autoridad, espacio
from prisma.despachador import TransporteDePrueba, despachar
from prisma.llm import RespectoPendiente

from tests.test_alta_eleccion_confirmacion import (_alta_en_confirmacion,
                                                   _alta_enviada, _nuevas, _ruta,
                                                   _salidas, _solicitud,
                                                   _tocar_boton, _usuario)
from tests.test_alta_enviar_a_aprobacion import (_acciones, _etiquetas, _tg_aprobador,
                                                 _token)
from tests.test_alta_modificar import _tareas
from tests.test_task_intake import NOW, _RoutingProvider, _callback_client

MOTIVO = "Falta definir bien el alcance"


def _titulo(conn, rid) -> str:
    with admin(conn) as cur:
        cur.execute("select d.titulo from task_draft d join task_intake_request r "
                    "on r.task_draft_id = d.id where r.id = %s", (rid,))
        return cur.fetchone()["titulo"]


def _nombre(conn, telegram_id) -> str:
    with admin(conn) as cur:
        cur.execute("select nombre from app_user where telegram_user_id = %s",
                    (telegram_id,))
        return cur.fetchone()["nombre"]


def _tocar(client, conn, user, pid, etiqueta):
    response = _tocar_boton(client, conn, _token(conn, pid, etiqueta), user)
    assert response.status_code == 200


def _escribir_como(conn, monkeypatch, provider, user, texto, message_id):
    monkeypatch.setattr(gateway, "_conn", lambda: conn)
    monkeypatch.setattr(gateway, "mantener_chat_activo",
                        lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(gateway, "config", SimpleNamespace(
        webhook_secret="test-secret", llm_api_key="unused",
        token_bot=lambda slug: "unused-token"))
    monkeypatch.setattr("prisma.llm.desde_base", lambda *args: provider)
    response = TestClient(gateway.app).post(
        "/telegram/north-lab",
        json={"message": {"message_id": message_id, "text": texto,
                          "chat": {"id": user, "type": "private"},
                          "from": {"id": user}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"})
    assert response.status_code == 200


def _rechazo_pedido(conn, monkeypatch, world):
    """El borrador enviado a quien confirma, con Rechazar ya tocado: la pregunta del
    motivo abierta."""
    rid, pid = _alta_enviada(conn, world)
    client = _callback_client(conn, monkeypatch)
    aprobador = _tg_aprobador(world)
    _tocar(client, conn, aprobador, pid, "Rechazar")
    return rid, pid, client, aprobador


def _dar_el_motivo(conn, monkeypatch, aprobador, motivo=MOTIVO, message_id=7001):
    provider = _RoutingProvider([_ruta(RespectoPendiente.RESPONDE)])
    _escribir_como(conn, monkeypatch, provider, aprobador, motivo, message_id)
    return provider


def test_quien_confirma_lo_de_otra_persona_ve_confirmar_y_rechazar(
        intake_world, conn):
    rid, pid = _alta_enviada(conn, intake_world)

    assert _etiquetas(conn, pid) == ["Confirmar", "Rechazar"]


def test_rechazar_pide_el_motivo_y_no_cancela_nada_todavia(
        intake_world, conn, monkeypatch):
    rid, pid = _alta_enviada(conn, intake_world)
    client = _callback_client(conn, monkeypatch)
    aprobador = _tg_aprobador(intake_world)
    del_aprobador = _salidas(conn, aprobador)
    de_quien_pide = _salidas(conn, _usuario(intake_world))

    _tocar(client, conn, aprobador, pid, "Rechazar")

    nuevas = _nuevas(conn, aprobador, del_aprobador)
    assert len(nuevas) == 1 and _titulo(conn, rid) in nuevas[0]["cuerpo"]
    assert nuevas[0]["cuerpo"].endswith("?")
    assert _solicitud(conn, rid) == "active" and _tareas(conn) == 0
    assert _salidas(conn, _usuario(intake_world)) == de_quien_pide


def test_el_toque_repetido_de_rechazar_no_pregunta_dos_veces(
        intake_world, conn, monkeypatch):
    rid, pid, client, aprobador = _rechazo_pedido(conn, monkeypatch, intake_world)
    despues = _salidas(conn, aprobador)

    _tocar(client, conn, aprobador, pid, "Rechazar")         # dentro de la ventana

    assert _salidas(conn, aprobador) == despues


def test_con_el_motivo_el_borrador_se_cancela_y_cada_uno_recibe_un_solo_mensaje(
        intake_world, conn, monkeypatch):
    rid, pid, client, aprobador = _rechazo_pedido(conn, monkeypatch, intake_world)
    pide = _usuario(intake_world)
    del_aprobador = _salidas(conn, aprobador)
    de_quien_pide = _salidas(conn, pide)

    _dar_el_motivo(conn, monkeypatch, aprobador)

    assert _solicitud(conn, rid) == "cancelled" and _tareas(conn) == 0
    assert [a["estado"] for a in _acciones(conn, rid)].count("esperando") == 0
    # Quien confirma: un recibo corto y verdadero.
    (recibo,) = _nuevas(conn, aprobador, del_aprobador)
    assert "rechacé" in recibo["cuerpo"] and _titulo(conn, rid) in recibo["cuerpo"]
    # Quien lo pidió: el aviso con quién, cuál y por qué.
    (aviso,) = _nuevas(conn, pide, de_quien_pide)
    assert aviso["cuerpo"] == (
        f"{_nombre(conn, aprobador)} rechazó el borrador de la tarea "
        f"«{_titulo(conn, rid)}»: {MOTIVO}")
    with admin(conn) as cur:
        cur.execute("select es_respuesta, es_coordinacion from message_outbox "
                    "where id = %s", (aviso["id"],))
        fila = cur.fetchone()
    assert fila["es_respuesta"] is False and fila["es_coordinacion"] is True


def test_el_aviso_del_rechazo_sale_por_el_despachador_a_quien_lo_pidio(
        intake_world, conn, monkeypatch):
    rid, pid, client, aprobador = _rechazo_pedido(conn, monkeypatch, intake_world)
    _dar_el_motivo(conn, monkeypatch, aprobador)
    ws = intake_world["north-lab"]["id"]
    transporte = TransporteDePrueba()

    with espacio(conn, ws) as cur:
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws),
                  ahora=NOW + timedelta(minutes=1))

    a_quien_pide = [e.texto for e in transporte.enviados
                    if e.chat_id == _usuario(intake_world)]
    assert any("rechazó el borrador" in t and MOTIVO in t for t in a_quien_pide)


def test_el_motivo_queda_en_la_auditoria(intake_world, conn, monkeypatch):
    rid, pid, client, aprobador = _rechazo_pedido(conn, monkeypatch, intake_world)
    _dar_el_motivo(conn, monkeypatch, aprobador)

    with admin(conn) as cur:
        cur.execute("select detalle from audit_log "
                    "where accion = 'rechazar_ingreso_tarea'")
        filas = cur.fetchall()
    assert len(filas) == 1 and filas[0]["detalle"]["motivo"] == MOTIVO


def test_un_segundo_mensaje_despues_del_rechazo_no_lo_repite(
        intake_world, conn, monkeypatch):
    rid, pid, client, aprobador = _rechazo_pedido(conn, monkeypatch, intake_world)
    _dar_el_motivo(conn, monkeypatch, aprobador)
    pide = _usuario(intake_world)
    avisos = _salidas(conn, pide)

    provider = _RoutingProvider([_ruta(None)])
    _escribir_como(conn, monkeypatch, provider, aprobador, "gracias", 7002)

    assert _salidas(conn, pide) == avisos


def test_si_el_borrador_se_confirmo_antes_del_motivo_no_se_avisa_ni_se_rechaza(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid, client, aprobador = _rechazo_pedido(conn, monkeypatch, intake_world)
    ws = intake_world["north-lab"]["id"]
    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(
            cur, ws, _token(conn, pid, "Confirmar"), aprobador, aprobador)
    assert resuelta is not None and resuelta.task_id
    pide = _usuario(intake_world)
    de_quien_pide = _salidas(conn, pide)
    del_aprobador = _salidas(conn, aprobador)

    _dar_el_motivo(conn, monkeypatch, aprobador)

    assert _solicitud(conn, rid) == "converted" and _tareas(conn) == 1
    assert _salidas(conn, pide) == de_quien_pide
    assert len(_nuevas(conn, aprobador, del_aprobador)) == 1   # la verdad, una vez


def test_rechazar_lo_toca_solo_quien_confirma(intake_world, conn, monkeypatch):
    rid, pid = _alta_enviada(conn, intake_world)
    ajena = intake_world["north-lab"]["people"]["Sam Noble"]["telegram"]
    client = _callback_client(conn, monkeypatch)

    _tocar(client, conn, ajena, pid, "Rechazar")

    assert _solicitud(conn, rid) == "active"
    assert [f["cuerpo"] for f in _salidas(conn, ajena)][-1:] == [
        "Eso se lo pregunté a otra persona del equipo."]


def test_el_token_de_rechazar_nunca_convierte_el_borrador_en_la_autoridad(
        intake_world, conn, authority_conn):
    """Defensa en profundidad (como 0023 con "enviar"): la autoridad sólo distingue
    `false` de todo lo demás; un token de "rechazar" que llegara hasta ella
    convertiría el borrador."""
    rid, pid = _alta_enviada(conn, intake_world)
    ws = intake_world["north-lab"]["id"]
    aprobador = _tg_aprobador(intake_world)

    with autoridad(authority_conn) as cur:
        resuelta = P.resolver_borrador(
            cur, ws, _token(conn, pid, "Rechazar"), aprobador, aprobador)

    assert resuelta is None and _tareas(conn) == 0 and _solicitud(conn, rid) == "active"


def test_quien_pide_y_confirma_lo_suyo_sigue_viendo_cancelar(intake_world, conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")

    assert _etiquetas(conn, pid) == ["Confirmar", "Modificar", "Cancelar"]
