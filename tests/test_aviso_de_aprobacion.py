"""Quien confirma el borrador de otra persona le avisa a quien lo pidió que la tarea
quedó creada (hallazgo (c) de la prueba real del 2026-10-01; mecánica §10: es el
mismo tipo de aviso de coordinación que el rechazo).

Antes, al confirmar, sólo quien confirmaba se enteraba ("Hecho. La tarea quedó
comprometida."); quien la pidió no sabía que su tarea existía. Ahora recibe un aviso
de coordinación, fuera del tope diario, una sola vez y auditado; si quien pidió es
quien confirma (su propio resumen) no se manda nada de más. Texto de código, sin
modelo, por el mismo camino de salida que el aviso del rechazo.

Todo por el webhook real.
"""

from __future__ import annotations

from datetime import timedelta

from leda import gateway
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba, despachar

from tests.test_alta_eleccion_confirmacion import (_alta_en_confirmacion,
                                                   _alta_enviada, _nuevas,
                                                   _salidas, _usuario)
from tests.test_alta_enviar_a_aprobacion import _tg_aprobador, _tocar
from tests.test_alta_modificar import _tareas
from tests.test_rechazar_borrador import _nombre, _titulo
from tests.test_task_intake import NOW, _callback_client


def _cliente(conn, monkeypatch, authority_conn):
    """El webhook real; la autoridad (que convierte el borrador) es la de la base de
    prueba."""
    monkeypatch.setattr(gateway, "_authority_conn", lambda: authority_conn)
    return _callback_client(conn, monkeypatch)


def _avisos(conn, chat_id) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select id, cuerpo, es_respuesta, es_coordinacion "
                    "from message_outbox where chat_id = %s "
                    "and cuerpo like %s", (chat_id, "%confirmó%"))
        return cur.fetchall()


def test_al_confirmar_a_quien_lo_pidio_le_llega_un_aviso_de_coordinacion(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_enviada(conn, intake_world)
    client = _cliente(conn, monkeypatch, authority_conn)
    aprobador = _tg_aprobador(intake_world)
    pide = _usuario(intake_world)
    de_quien_pide = _salidas(conn, pide)

    _tocar(client, conn, aprobador, pid, "Confirmar")

    assert _tareas(conn) == 1
    (aviso,) = _nuevas(conn, pide, de_quien_pide)
    assert aviso["cuerpo"] == (
        f"{_nombre(conn, aprobador)} confirmó el borrador de la tarea "
        f"«{_titulo(conn, rid)}»: la tarea quedó creada.")
    (fila,) = _avisos(conn, pide)
    assert fila["es_respuesta"] is False and fila["es_coordinacion"] is True


def test_el_toque_repetido_de_confirmar_no_avisa_dos_veces(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_enviada(conn, intake_world)
    client = _cliente(conn, monkeypatch, authority_conn)
    aprobador = _tg_aprobador(intake_world)
    pide = _usuario(intake_world)
    _tocar(client, conn, aprobador, pid, "Confirmar")
    despues = _salidas(conn, pide)

    _tocar(client, conn, aprobador, pid, "Confirmar")

    assert _salidas(conn, pide) == despues
    assert len(_avisos(conn, pide)) == 1


def test_el_aviso_de_aprobacion_sale_por_el_despachador_fuera_del_tope(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_enviada(conn, intake_world)
    client = _cliente(conn, monkeypatch, authority_conn)
    _tocar(client, conn, _tg_aprobador(intake_world), pid, "Confirmar")
    ws = intake_world["north-lab"]["id"]
    transporte = TransporteDePrueba()

    with espacio(conn, ws) as cur:
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws),
                  ahora=NOW + timedelta(minutes=1))

    a_quien_pide = [e.texto for e in transporte.enviados
                    if e.chat_id == _usuario(intake_world)]
    assert any("confirmó el borrador" in t and "quedó creada" in t
               for t in a_quien_pide)


def test_el_aviso_de_aprobacion_queda_en_la_auditoria(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_enviada(conn, intake_world)
    client = _cliente(conn, monkeypatch, authority_conn)
    _tocar(client, conn, _tg_aprobador(intake_world), pid, "Confirmar")
    _tocar(client, conn, _tg_aprobador(intake_world), pid, "Confirmar")

    with admin(conn) as cur:
        cur.execute("select detalle from audit_log "
                    "where accion = 'avisar_aprobacion_ingreso_tarea'")
        filas = cur.fetchall()
    assert len(filas) == 1 and filas[0]["detalle"]["request_id"] == rid


def test_si_quien_pidio_es_quien_confirma_no_se_manda_ningun_aviso_de_mas(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    client = _cliente(conn, monkeypatch, authority_conn)
    pide = _usuario(intake_world)

    _tocar(client, conn, pide, pid, "Confirmar")

    assert _tareas(conn) == 1
    assert _avisos(conn, pide) == []
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log "
                    "where accion = 'avisar_aprobacion_ingreso_tarea'")
        assert cur.fetchone()["n"] == 0
