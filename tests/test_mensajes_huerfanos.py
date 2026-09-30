"""Un mensaje cuyo turno murió nunca queda sin respuesta (T9-H19e, ADR 0013 regla 2).

T9-H19d recupera un mensaje muerto cuando Telegram lo reentrega pasada la ventana.
Si la reentrega no llega (Telegram dejó de reintentar, o el proceso murió y nadie
reintenta), el recibo de la fase 1 queda sin respuesta para siempre: el barrido de
`huerfanos.barrer` -- parte de cada pasada de fondo -- le encola el aviso neutro
aprobado y deja el incidente. No vuelve a correr el turno con contenido viejo.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from prisma import ciclo, gateway, huerfanos
from prisma.db import admin, espacio
from prisma.despachador import TransporteDePrueba
from prisma.incidentes import (EXPLICACION_POR_ETAPA, NOTICIA_NEUTRA_INCIDENTE)

from tests.test_una_respuesta import _tg

AHORA = datetime(2026, 9, 30, 15, 0, tzinfo=timezone.utc)
EN_CURSO = gateway.VENTANA_TURNO_EN_CURSO
COTA = gateway.COTA_REENTREGA


def _recibo(conn, ws, app_user_id, chat, *, hace, message_id=41, texto="hola",
            boton=None):
    """Una fila de `inbound_message` de hace `hace` (timedelta)."""
    with admin(conn) as cur:
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto,
                  boton_callback, at)
               values (%s, %s, %s, %s, %s, %s, %s) returning id""",
            (ws, message_id, chat, app_user_id, texto, boton, AHORA - hace))
        fila = cur.fetchone()
    conn.commit()
    return str(fila["id"])


def _persona(conn, nombre="Nahuel Gimenez"):
    with admin(conn) as cur:
        cur.execute(
            "select id, telegram_user_id from app_user where nombre = %s", (nombre,))
        f = cur.fetchone()
    return str(f["id"]), f["telegram_user_id"]


def _responder(conn, ws, chat, entrante_id, *, estado="listo"):
    with admin(conn) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, tipo, cuerpo, estado, es_respuesta,
                  entrante_id, dedupe_key)
               values (%s, %s, 'normal', 'ok', %s, true, %s, %s)""",
            (ws, chat, estado, entrante_id, f"test:{entrante_id}"))
    conn.commit()


def _barrer(conn, ws, ahora=AHORA):
    with espacio(conn, ws) as cur:
        n = huerfanos.barrer(cur, ws, ahora)
    conn.commit()
    return n


def _avisos(conn, chat):
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo, es_respuesta, entrante_id, dedupe_key,
                      destinatario_membership_id
                 from message_outbox where chat_id = %s""", (chat,))
        return cur.fetchall()


def _incidentes(conn, ws):
    with admin(conn) as cur:
        cur.execute(
            """select referencia_tipo, referencia_id, severidad, chat_id
                 from incident where workspace_id = %s and etapa = %s""",
            (ws, huerfanos.ETAPA_MENSAJE_HUERFANO))
        return cur.fetchall()


def test_un_huerfano_viejo_recibe_un_aviso_neutro_y_un_incidente(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))

    assert _barrer(conn, ws) == 1

    (aviso,) = _avisos(conn, tg)
    assert aviso["cuerpo"] == NOTICIA_NEUTRA_INCIDENTE
    assert aviso["es_respuesta"] and str(aviso["entrante_id"]) == recibo
    assert aviso["destinatario_membership_id"] is not None
    (incidente,) = _incidentes(conn, ws)
    assert incidente["referencia_tipo"] == "inbound_message"
    assert str(incidente["referencia_id"]) == recibo
    assert incidente["chat_id"] == tg


def test_barrer_dos_veces_no_manda_nada_nuevo(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))

    assert _barrer(conn, ws) == 1
    assert _barrer(conn, ws) == 0

    assert len(_avisos(conn, tg)) == 1
    assert len(_incidentes(conn, ws)) == 1


def test_el_aviso_no_deja_el_entrante_atado_a_lo_que_sigue_en_la_transaccion(
        corework, conn):
    """La atadura al recibo es sólo del aviso: lo que se encole después, en la
    misma transacción (cadencias, escalera), no responde a ese mensaje."""
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))

    with espacio(conn, ws) as cur:
        huerfanos.barrer(cur, ws, AHORA)
        cur.execute("select nullif(current_setting('prisma.entrante_id', true), '') e")
        assert cur.fetchone()["e"] is None


def test_un_recibo_reciente_sin_respuesta_no_se_toca(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO - timedelta(minutes=1))

    assert _barrer(conn, ws) == 0
    assert _avisos(conn, tg) == [] and _incidentes(conn, ws) == []


def test_un_recibo_con_respuesta_no_se_toca(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    _responder(conn, ws, tg, recibo)

    assert _barrer(conn, ws) == 0
    assert len(_avisos(conn, tg)) == 1 and _incidentes(conn, ws) == []


def test_una_respuesta_descartada_no_cuenta_como_respuesta(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    _responder(conn, ws, tg, recibo, estado="descartado")

    assert _barrer(conn, ws) == 1


def test_un_toque_absorbido_no_es_un_mensaje_sin_respuesta(corework, conn):
    """`_registrar_toque(..., None)`: ni texto, ni id de Telegram, ni botón."""
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1),
            message_id=None, texto=None, boton=None)

    assert _barrer(conn, ws) == 0
    assert _avisos(conn, tg) == [] and _incidentes(conn, ws) == []


def test_un_toque_que_murio_sin_respuesta_tambien_recibe_el_aviso(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1),
            message_id=None, texto=None, boton="pa:abc")

    assert _barrer(conn, ws) == 1


def test_un_mensaje_recuperado_no_se_avisa_ni_el_recibo_muerto_ni_el_nuevo(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30))   # el muerto
    nuevo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=5))
    _responder(conn, ws, tg, nuevo)                    # la recuperación respondió

    assert _barrer(conn, ws) == 0
    assert len(_avisos(conn, tg)) == 1 and _incidentes(conn, ws) == []


def test_de_un_mismo_mensaje_muerto_dos_veces_se_avisa_una_sola(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30))
    ultimo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=5))

    assert _barrer(conn, ws) == 1

    (aviso,) = _avisos(conn, tg)
    assert str(aviso["entrante_id"]) == ultimo


def test_un_recibo_mas_viejo_que_la_cota_no_se_avisa(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=COTA + timedelta(minutes=1))

    assert _barrer(conn, ws) == 0
    assert _avisos(conn, tg) == [] and _incidentes(conn, ws) == []


def test_el_barrido_de_un_espacio_no_toca_los_recibos_de_otro(intake_world, conn):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    p_norte = norte["people"]["Morgan Hale"]
    p_oeste = oeste["people"]["Morgan Hale"]
    r_norte = _recibo(conn, norte["id"], p_norte["app_user_id"], p_norte["telegram"],
                      hace=EN_CURSO + timedelta(minutes=1))
    r_oeste = _recibo(conn, oeste["id"], p_oeste["app_user_id"], p_oeste["telegram"],
                      hace=EN_CURSO + timedelta(minutes=1))

    assert _barrer(conn, norte["id"]) == 1

    assert [str(a["entrante_id"]) for a in _avisos(conn, p_norte["telegram"])] == [
        r_norte]
    assert _avisos(conn, p_oeste["telegram"]) == []
    assert _incidentes(conn, oeste["id"]) == []
    assert _barrer(conn, oeste["id"]) == 1
    assert [str(a["entrante_id"]) for a in _avisos(conn, p_oeste["telegram"])] == [
        r_oeste]


def test_el_lote_acota_cuantos_se_avisan_por_pasada(corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    for i in range(3):
        _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1),
                message_id=100 + i)

    with espacio(conn, ws) as cur:
        assert huerfanos.barrer(cur, ws, AHORA, lote=2) == 2
    conn.commit()
    assert _barrer(conn, ws) == 1
    assert _barrer(conn, ws) == 0


def test_sin_membresia_activa_el_aviso_sale_sin_destinatario_y_lo_dice_el_incidente(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where app_user_id = %s",
                    (uid,))
    conn.commit()

    assert _barrer(conn, ws) == 1
    assert _barrer(conn, ws) == 0                     # y no se repite

    (aviso,) = _avisos(conn, tg)
    assert aviso["destinatario_membership_id"] is None
    assert len(_incidentes(conn, ws)) == 1


def test_el_ciclo_de_fondo_barre_y_despacha_el_aviso_en_la_misma_pasada(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    transporte = TransporteDePrueba()

    with espacio(conn, ws) as cur:
        resumen = ciclo.ejecutar_ciclo_espacio(
            cur, ws, transporte, AHORA, AHORA - timedelta(hours=1),
            con_cadencias=False)
    conn.commit()

    assert resumen["huerfanos_avisados"] == 1
    assert [e for e in transporte.enviados if NOTICIA_NEUTRA_INCIDENTE in str(e)]


def test_una_falla_del_barrido_no_frena_el_despacho_y_se_reporta(
        corework, conn, monkeypatch):
    ws = corework.workspace_id

    def _revienta(*a, **k):
        raise RuntimeError("falla del barrido")

    monkeypatch.setattr(huerfanos, "barrer", _revienta)
    with espacio(conn, ws) as cur:
        resumen = ciclo.ejecutar_ciclo_espacio(
            cur, ws, TransporteDePrueba(), AHORA, AHORA - timedelta(hours=1),
            con_cadencias=False)
    conn.commit()

    assert resumen["huerfanos_avisados"] == 0
    assert isinstance(resumen["huerfanos_fallo"], RuntimeError)


def test_la_etapa_del_huerfano_tiene_su_explicacion():
    assert huerfanos.ETAPA_MENSAJE_HUERFANO == "mensaje_huerfano_sin_respuesta"
    assert huerfanos.ETAPA_MENSAJE_HUERFANO in EXPLICACION_POR_ETAPA
    assert huerfanos.VENTANA is gateway.VENTANA_TURNO_EN_CURSO
    assert huerfanos.COTA is gateway.COTA_REENTREGA
