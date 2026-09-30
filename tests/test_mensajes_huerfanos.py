"""Un mensaje cuyo turno murió nunca queda sin respuesta (T9-H19e, ADR 0013 regla 2).

T9-H19d recupera un mensaje muerto cuando Telegram lo reentrega pasada la ventana.
Si la reentrega no llega (Telegram dejó de reintentar, o el proceso murió y nadie
reintenta), el recibo de la fase 1 queda sin respuesta para siempre: el barrido de
`huerfanos.barrer` -- parte de cada pasada de fondo -- le encola el aviso neutro
aprobado y deja el incidente. No vuelve a correr el turno con contenido viejo.
"""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from psycopg import Rollback

from prisma import ciclo, gateway, huerfanos
from prisma.db import admin, conectar, espacio
from prisma.despachador import TransporteDePrueba
from prisma.incidentes import (EXPLICACION_POR_ETAPA, NOTICIA_NEUTRA_INCIDENTE)
from prisma.salida import enqueue_outbox

from tests.test_una_respuesta import (_ADJUNTOS, _con_adjunto,
                                      _con_respuesta_del_modelo, _tg)
from tests.test_mensaje_repetido import _enviar, _update
from tests.test_menu_tarea import _mensaje, _tocar, cliente  # noqa: F401
from tests.test_toque_idempotente import _confirmar_en_curso, _tocar_boton



def _ahora():
    """El reloj de la aplicación. Los recibos se siembran con el reloj de la base
    (`now()`), que es el que manda para la ventana (T9-H19g): en las pruebas los dos
    coinciden salvo que una prueba desalinee este a propósito."""
    return datetime.now(timezone.utc)

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
               values (%s, %s, %s, %s, %s, %s,
                       now() - make_interval(secs => %s)) returning id""",
            (ws, message_id, chat, app_user_id, texto, boton,
             hace.total_seconds()))
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


def _barrer(conn, ws, ahora=None):
    return huerfanos.barrer(conn, ws, ahora or _ahora())


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

    huerfanos.barrer(conn, ws, _ahora())
    with espacio(conn, ws) as cur:
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


def test_una_respuesta_descartada_a_proposito_sigue_siendo_una_respuesta(
        corework, conn):
    """Lo que el código descarta antes de enviar (un juego de opciones reemplazado, una
    vista previa que ya no es vigente al despachar, el duplicado que `controlar`
    suprime) es la respuesta de ese turno: el turno no murió, la persona ya tiene
    una respuesta posterior o la decisión ya no corresponde. Un aviso de "tuve un
    problema" sería falso."""
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    _responder(conn, ws, tg, recibo, estado="descartado")

    assert _barrer(conn, ws) == 0
    assert len(_avisos(conn, tg)) == 1 and _incidentes(conn, ws) == []


def test_una_vista_previa_descartada_al_despachar_no_se_avisa_como_huerfana(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    _responder(conn, ws, tg, recibo, estado="listo")
    with admin(conn) as cur:
        cur.execute("update message_outbox set estado = 'descartado' "
                    "where entrante_id = %s", (recibo,))
    conn.commit()

    assert _barrer(conn, ws) == 0
    assert _incidentes(conn, ws) == []


def test_una_respuesta_fallida_no_se_avisa_como_huerfana(corework, conn):
    """Una falla de entrega tiene su propio camino de incidente."""
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    _responder(conn, ws, tg, recibo, estado="fallido")

    assert _barrer(conn, ws) == 0
    assert len(_avisos(conn, tg)) == 1 and _incidentes(conn, ws) == []


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

    assert huerfanos.barrer(conn, ws, _ahora(), lote=2) == 2
    assert _barrer(conn, ws) == 1
    assert _barrer(conn, ws) == 0


def test_sin_membresia_activa_no_sale_ningun_mensaje_y_queda_un_incidente(
        corework, conn):
    """Quien ya no es integrante no recibe mensajes de Prisma: queda el incidente
    (sin contenido) y una marca descartada atada al recibo, que hace idempotente el
    barrido."""
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where app_user_id = %s",
                    (uid,))
    conn.commit()

    assert _barrer(conn, ws) == 1
    assert _barrer(conn, ws) == 0                     # y no se repite

    (marca,) = _avisos(conn, tg)
    assert str(marca["entrante_id"]) == recibo
    assert marca["destinatario_membership_id"] is None
    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where chat_id = %s", (tg,))
        assert [f["estado"] for f in cur.fetchall()] == ["descartado"]
    (incidente,) = _incidentes(conn, ws)
    assert str(incidente["referencia_id"]) == recibo
    transporte = TransporteDePrueba()
    ciclo.ejecutar_pasada(conn, ws, transporte, _ahora(),
                          _ahora() - timedelta(hours=1), con_cadencias=False)
    conn.commit()
    assert not [e for e in transporte.enviados if NOTICIA_NEUTRA_INCIDENTE in str(e)]


def test_el_ciclo_de_fondo_barre_y_despacha_el_aviso_en_la_misma_pasada(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    transporte = TransporteDePrueba()

    resumen = ciclo.ejecutar_pasada(
        conn, ws, transporte, _ahora(), _ahora() - timedelta(hours=1),
        con_cadencias=False)
    conn.commit()

    assert resumen["huerfanos_avisados"] == 1
    assert [e for e in transporte.enviados if NOTICIA_NEUTRA_INCIDENTE in str(e)]


def test_la_etapa_del_huerfano_tiene_su_explicacion():
    assert huerfanos.ETAPA_MENSAJE_HUERFANO == "mensaje_huerfano_sin_respuesta"
    assert huerfanos.ETAPA_MENSAJE_HUERFANO in EXPLICACION_POR_ETAPA
    assert huerfanos.VENTANA is gateway.VENTANA_TURNO_EN_CURSO
    assert huerfanos.COTA is gateway.COTA_REENTREGA


# --- T9-H19g: lo que dejó la revisión de T9-H19e/f ----------------------------------

def _incidentes_de_etapa(conn, ws, etapa):
    with admin(conn) as cur:
        cur.execute("select referencia_id from incident where workspace_id = %s "
                    "and etapa = %s", (ws, etapa))
        return [str(f["referencia_id"]) for f in cur.fetchall()]


def _envenenar(monkeypatch, veneno):
    """`registrar_incidente` revienta, DESPUÉS de que el aviso ya se encoló (una
    escritura parcial), sólo para el incidente del huérfano `veneno`."""
    real = huerfanos.registrar_incidente

    def selectivo(cur, workspace_id, resumen, **kw):
        if (kw.get("etapa") == huerfanos.ETAPA_MENSAJE_HUERFANO
                and kw.get("referencia_id") == veneno):
            raise RuntimeError("recibo envenenado")
        return real(cur, workspace_id, resumen, **kw)

    monkeypatch.setattr(huerfanos, "registrar_incidente", selectivo)


def test_un_recibo_envenenado_no_frena_el_aviso_de_los_demas(
        corework, conn, monkeypatch):
    """Un recibo cuyo aviso falla (aun después de escribir algo) se reporta y se
    saltea: no revierte el lote ni encabeza para siempre todas las pasadas."""
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    veneno = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30),
                     message_id=1)
    sano = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1),
                   message_id=2)
    _envenenar(monkeypatch, veneno)

    assert _barrer(conn, ws) == 1

    assert [str(a["entrante_id"]) for a in _avisos(conn, tg)] == [sano]
    assert [str(i["referencia_id"]) for i in _incidentes(conn, ws)] == [sano]
    assert _incidentes_de_etapa(
        conn, ws, huerfanos.ETAPA_MENSAJE_HUERFANO_FALLO) == [veneno]


def test_el_fallo_de_un_recibo_se_reporta_una_sola_vez_y_se_sigue_reintentando(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    veneno = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30),
                     message_id=1)
    _envenenar(monkeypatch, veneno)

    assert _barrer(conn, ws) == 0
    assert _barrer(conn, ws) == 0
    assert len(_incidentes_de_etapa(
        conn, ws, huerfanos.ETAPA_MENSAJE_HUERFANO_FALLO)) == 1

    monkeypatch.undo()                               # la causa desaparece
    assert _barrer(conn, ws) == 1                    # y el recibo se avisa
    assert [str(a["entrante_id"]) for a in _avisos(conn, tg)] == [veneno]


def test_un_recibo_envenenado_no_ocupa_el_lugar_de_los_sanos_en_el_lote(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    veneno = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30),
                     message_id=1)
    sano = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1),
                   message_id=2)
    _envenenar(monkeypatch, veneno)

    # lote de uno: el veneno es el primero, y falla; ya reportado, pasa al final
    assert huerfanos.barrer(conn, ws, _ahora(), lote=1) == 0
    assert huerfanos.barrer(conn, ws, _ahora(), lote=1) == 1
    assert [str(a["entrante_id"]) for a in _avisos(conn, tg)] == [sano]


def test_si_ni_el_incidente_del_fallo_se_puede_escribir_no_se_pierde_el_resto(
        corework, conn, monkeypatch, capsys):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    veneno = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30),
                     message_id=1)
    sano = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1),
                   message_id=2)
    real = huerfanos.registrar_incidente

    def roto(cur, workspace_id, resumen, **kw):
        if kw.get("referencia_id") == veneno:
            raise RuntimeError("tampoco se puede escribir")
        return real(cur, workspace_id, resumen, **kw)

    monkeypatch.setattr(huerfanos, "registrar_incidente", roto)

    assert _barrer(conn, ws) == 1
    assert [str(a["entrante_id"]) for a in _avisos(conn, tg)] == [sano]
    assert "RuntimeError" in capsys.readouterr().out      # nunca en silencio


# El barrido y la reentrega comparten el candado del mensaje.

class _CursorConGancho:
    """Un cursor que dispara `gancho` justo antes de tomar el candado por mensaje:
    el hueco entre elegir el candidato y escribir, donde puede colarse la reentrega."""

    def __init__(self, cur, gancho):
        self._cur, self._gancho, self._disparado = cur, gancho, False

    def execute(self, consulta, params=None):
        if (not self._disparado and params
                and any(str(p).startswith("mensaje:") for p in params)):
            self._disparado = True
            self._gancho()
        return self._cur.execute(consulta, params)

    def __getattr__(self, nombre):
        return getattr(self._cur, nombre)


def _barrer_con_gancho(conn, ws, gancho):
    """`barrer` con el cursor de cada transacción de recibo envuelto: dispara `gancho`
    justo antes de que tome el candado del mensaje."""
    real = huerfanos.espacio

    @contextmanager
    def con_gancho(c, workspace_id):
        with real(c, workspace_id) as cur:
            yield _CursorConGancho(cur, gancho)

    huerfanos.espacio = con_gancho
    try:
        return huerfanos.barrer(conn, ws, _ahora())
    finally:
        huerfanos.espacio = real


def test_una_respuesta_que_llega_entre_elegir_y_escribir_evita_el_aviso(
        corework, conn, uri):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    recibo = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))
    otra = conectar(uri)

    try:
        assert _barrer_con_gancho(
            conn, ws, lambda: _responder(otra, ws, tg, recibo)) == 0
    finally:
        otra.close()

    assert [a["cuerpo"] for a in _avisos(conn, tg)] == ["ok"]      # sólo la real
    assert _incidentes(conn, ws) == []


def test_un_recibo_nuevo_del_mismo_mensaje_entre_elegir_y_escribir_evita_el_aviso(
        corework, conn, uri):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30))
    otra = conectar(uri)

    try:
        assert _barrer_con_gancho(
            conn, ws,
            lambda: _recibo(otra, ws, uid, tg, hace=timedelta(seconds=1))) == 0
    finally:
        otra.close()

    assert _avisos(conn, tg) == [] and _incidentes(conn, ws) == []


def test_si_la_reentrega_tiene_el_candado_del_mensaje_el_barrido_lo_deja_para_despues(
        corework, conn, uri):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1), message_id=41)
    otra = conectar(uri)
    try:
        otra.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                     (f"mensaje:{ws}:{tg}:41",))    # la reentrega, en su fase 1
        assert _barrer(conn, ws) == 0
        assert _avisos(conn, tg) == []
    finally:
        otra.close()

    assert _barrer(conn, ws) == 1                   # liberado: ahora sí


def test_una_reentrega_durante_el_aviso_de_su_recibo_espera_y_se_absorbe(
        cliente, corework, conn, uri, monkeypatch):
    """Mientras la transacción del aviso de un recibo sigue abierta (el aviso ya
    encolado, sin commit), la reentrega del mismo mensaje espera el candado, ve el
    aviso como la respuesta y se absorbe: nunca el aviso neutro Y la respuesta real."""
    ws = corework.workspace_id
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1), message_id=41)
    errores, estado = [], {}

    def entregar():
        c = conectar(uri)
        try:
            gateway.procesar_update(c, "corework", _update(tg))
        except Exception as e:  # noqa: BLE001
            errores.append(e)
        finally:
            c.close()

    hilo = threading.Thread(target=entregar)
    real = huerfanos.registrar_incidente

    def incidente_con_reentrega(*a, **k):
        hilo.start()                                # el aviso ya está encolado
        time.sleep(1.0)
        estado["espero"] = hilo.is_alive()          # espera el candado del mensaje
        return real(*a, **k)

    monkeypatch.setattr(huerfanos, "registrar_incidente", incidente_con_reentrega)
    assert huerfanos.barrer(conn, ws, _ahora()) == 1
    hilo.join(timeout=60)

    assert estado["espero"] is True
    assert not hilo.is_alive() and errores == []
    assert [a["cuerpo"] for a in _avisos(conn, tg)] == [NOTICIA_NEUTRA_INCIDENTE]
    assert proveedor.ruteados == []                 # y no corrió un turno de más


# --- Ningún turno real queda marcado como huérfano ----------------------------------

def _nada_huerfano(conn, ws):
    """Envejece todo recibo más allá de la ventana y barre: nada se marca."""
    with admin(conn) as cur:
        cur.execute("update inbound_message set at = at - make_interval(secs => %s)",
                    ((EN_CURSO + timedelta(minutes=2)).total_seconds(),))
    conn.commit()
    assert _barrer(conn, ws) == 0
    assert _incidentes(conn, ws) == []


def test_un_mensaje_escrito_y_respondido_nunca_se_marca(
        cliente, corework, conn, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _mensaje(cliente, tg, "hola")
    _nada_huerfano(conn, corework.workspace_id)


def test_un_toque_de_un_menu_respondido_nunca_se_marca(cliente, corework, conn):
    tg, token, _tarea = _confirmar_en_curso(conn, corework.workspace_id)
    _tocar_boton(cliente, token, tg, callback_id="a")
    _nada_huerfano(conn, corework.workspace_id)


def test_un_toque_repetido_absorbido_nunca_se_marca(cliente, corework, conn):
    tg, token, _tarea = _confirmar_en_curso(conn, corework.workspace_id)
    _tocar_boton(cliente, token, tg, callback_id="a")
    _tocar_boton(cliente, token, tg, callback_id="b")
    _nada_huerfano(conn, corework.workspace_id)


def test_un_toque_de_un_boton_desconocido_nunca_se_marca(
        cliente, corework, conn, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _tocar(cliente, "token-inexistente", tg)
    _nada_huerfano(conn, corework.workspace_id)


def test_un_mensaje_editado_nunca_se_marca(cliente, corework, conn, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _enviar(cliente, _update(tg, message_id=41))
    _enviar(cliente, _update(tg, texto="hola, editado", message_id=41,
                             clave="edited_message"))
    _nada_huerfano(conn, corework.workspace_id)


def test_un_mensaje_repetido_absorbido_nunca_se_marca(
        cliente, corework, conn, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _enviar(cliente, _update(tg))
    _enviar(cliente, _update(tg))
    _nada_huerfano(conn, corework.workspace_id)


def test_un_mensaje_con_adjunto_nunca_se_marca(
        cliente, corework, conn, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    for i, tipo in enumerate(sorted(_ADJUNTOS)):
        _con_adjunto(cliente, tg, tipo, message_id=10 + i)
    _con_adjunto(cliente, tg, "photo", "¿qué tengo pendiente?", message_id=30)
    _nada_huerfano(conn, corework.workspace_id)


def test_un_mensaje_que_termino_en_el_aviso_neutro_por_incidente_nunca_se_marca(
        cliente, corework, conn, monkeypatch):
    def turno_roto(*a, **k):
        raise RuntimeError("falló algo interno")

    monkeypatch.setattr(gateway, "_turno", turno_roto)
    tg = _tg(conn)
    _mensaje(cliente, tg, "hola")
    _nada_huerfano(conn, corework.workspace_id)


def test_un_mensaje_sin_respuesta_que_termino_en_el_aviso_neutro_nunca_se_marca(
        cliente, corework, conn, monkeypatch):
    monkeypatch.setattr(gateway, "_turno", lambda *a, **k: None)
    tg = _tg(conn)
    _mensaje(cliente, tg, "hola")
    _nada_huerfano(conn, corework.workspace_id)


def test_un_mensaje_recuperado_por_la_reentrega_nunca_se_marca(
        cliente, corework, conn, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    uid, _ = _persona(conn)
    _recibo(conn, corework.workspace_id, uid, tg,
            hace=EN_CURSO + timedelta(minutes=1), message_id=41)
    _enviar(cliente, _update(tg, message_id=41))
    _nada_huerfano(conn, corework.workspace_id)


# --- La membresía se busca en ESTE espacio ------------------------------------------

def test_una_persona_en_dos_espacios_se_decide_por_su_membresia_de_cada_uno(
        intake_world, conn):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    yo = norte["people"]["Morgan Hale"]
    with admin(conn) as cur:                          # inactiva en el otro espacio
        cur.execute("select id from rol where workspace_id = %s limit 1",
                    (oeste["id"],))
        rol = cur.fetchone()["id"]
        cur.execute(
            """insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                       activo)
               values (%s, %s, %s, %s, false)""",
            (oeste["id"], yo["app_user_id"], next(iter(oeste["areas"].values())), rol))
    conn.commit()
    r_norte = _recibo(conn, norte["id"], yo["app_user_id"], yo["telegram"],
                      hace=EN_CURSO + timedelta(minutes=1), message_id=1)
    r_oeste = _recibo(conn, oeste["id"], yo["app_user_id"], yo["telegram"],
                      hace=EN_CURSO + timedelta(minutes=1), message_id=2)

    assert _barrer(conn, norte["id"]) == 1
    assert _barrer(conn, oeste["id"]) == 1

    por_recibo = {str(a["entrante_id"]): a for a in _avisos(conn, yo["telegram"])}
    assert len(por_recibo) == 2
    assert str(por_recibo[r_norte]["destinatario_membership_id"]) == \
        yo["membership_id"]
    assert por_recibo[r_oeste]["destinatario_membership_id"] is None
    assert len(_incidentes(conn, norte["id"])) == 1
    assert len(_incidentes(conn, oeste["id"])) == 1
    assert _barrer(conn, norte["id"]) == 0 and _barrer(conn, oeste["id"]) == 0


# --- El reloj de la base manda, no el de la aplicación ------------------------------

def test_el_barrido_usa_el_reloj_de_la_base_y_no_avisa_un_turno_vivo(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO - timedelta(minutes=1))

    assert _barrer(conn, ws, _ahora() + timedelta(minutes=15)) == 0   # app adelantada
    assert _avisos(conn, tg) == [] and _incidentes(conn, ws) == []


def test_el_barrido_usa_el_reloj_de_la_base_y_no_deja_pasar_un_huerfano(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1))

    assert _barrer(conn, ws, _ahora() - timedelta(minutes=15)) == 1   # app atrasada


def test_el_barrido_usa_el_reloj_de_la_base_para_la_cota_de_24_horas(
        corework, conn):
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=COTA + timedelta(minutes=1))

    assert _barrer(conn, ws, _ahora() - timedelta(hours=12)) == 0   # app atrasada


def _reloj_de_la_aplicacion_desalineado(monkeypatch, delta):
    """El `datetime.now` que ve el gateway, corrido `delta`."""
    real = gateway.datetime

    class _Desalineado(real):
        @classmethod
        def now(cls, tz=None):
            return real.now(tz) + delta

    monkeypatch.setattr(gateway, "datetime", _Desalineado)


def test_la_recuperacion_del_gateway_usa_el_reloj_de_la_base_con_la_app_adelantada(
        cliente, corework, conn, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO - timedelta(minutes=1), message_id=41)
    _reloj_de_la_aplicacion_desalineado(monkeypatch, timedelta(days=30))

    _enviar(cliente, _update(tg, message_id=41))

    assert proveedor.ruteados == []                  # su turno puede seguir vivo


def test_la_recuperacion_del_gateway_usa_el_reloj_de_la_base_con_la_app_atrasada(
        cliente, corework, conn, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1), message_id=41)
    _reloj_de_la_aplicacion_desalineado(monkeypatch, timedelta(days=-30))

    _enviar(cliente, _update(tg, message_id=41))

    assert len(proveedor.ruteados) == 1              # el turno murió: se recupera


# --- El reporte de la falla del barrido y el despacho que sigue ---------------------

def test_el_reporte_de_una_falla_del_barrido_es_deduplicado_y_no_deja_la_excepcion(
        corework, conn):
    ws = corework.workspace_id
    supresor = ciclo.SupresorDeRepetidos()
    impreso = []

    def resumen():
        r = ciclo._resumen_vacio()
        r["huerfanos_fallo"] = RuntimeError("falla del barrido")
        return r

    primero = resumen()
    ciclo.reportar_cadencias_rotas(conn, supresor, ws, "corework", primero,
                                   imprimir=impreso.append)
    ciclo.reportar_cadencias_rotas(conn, supresor, ws, "corework", resumen(),
                                   imprimir=impreso.append)

    assert "huerfanos_fallo" not in primero
    assert not any(isinstance(v, BaseException) for v in primero.values())
    assert len(impreso) == 1 and "RuntimeError" in impreso[0]
    assert len(_incidentes_de_etapa(conn, ws, "ciclo_de_fondo")) == 1
    assert supresor.activa((ws, "barrido_huerfanos"))


def test_un_barrido_que_se_recupera_limpia_la_marca_y_una_falla_nueva_se_reporta(
        corework, conn):
    ws = corework.workspace_id
    supresor = ciclo.SupresorDeRepetidos()
    impreso = []
    con_fallo = ciclo._resumen_vacio()
    con_fallo["huerfanos_fallo"] = RuntimeError("x")
    ciclo.reportar_cadencias_rotas(conn, supresor, ws, "corework", con_fallo,
                                   imprimir=impreso.append)

    sano = ciclo._resumen_vacio()
    ciclo.reportar_cadencias_rotas(conn, supresor, ws, "corework", sano,
                                   imprimir=impreso.append)
    assert not supresor.activa((ws, "barrido_huerfanos"))
    assert "huerfanos_fallo" not in sano

    otra = ciclo._resumen_vacio()
    otra["huerfanos_fallo"] = RuntimeError("y")
    ciclo.reportar_cadencias_rotas(conn, supresor, ws, "corework", otra,
                                   imprimir=impreso.append)
    assert len(impreso) == 2
    assert len(_incidentes_de_etapa(conn, ws, "ciclo_de_fondo")) == 2


def test_una_falla_del_barrido_no_frena_el_despacho_y_se_reporta(
        corework, conn, monkeypatch):
    """El barrido falla DESPUÉS de una escritura parcial: esa escritura se revierte
    (su savepoint) y lo que ya estaba listo en la salida igual llega al transporte."""
    ws = corework.workspace_id
    _uid, tg = _persona(conn)
    with espacio(conn, ws) as cur:
        cur.execute("select membership_id from integrante where telegram_user_id = %s",
                    (tg,))
        membership = str(cur.fetchone()["membership_id"])
        enqueue_outbox(cur, workspace_id=ws, chat_id=tg, text="Listo para salir",
                       dedupe_key="test:listo", recipient_membership_id=membership,
                       is_response=True,
                       scheduled_for=_ahora() - timedelta(minutes=1))
    conn.commit()

    def _revienta(c, workspace_id, ahora, *a, **k):
        with espacio(c, workspace_id) as cur:
            enqueue_outbox(cur, workspace_id=workspace_id, chat_id=tg,
                           text="Parcial que se revierte", dedupe_key="test:parcial",
                           recipient_membership_id=membership, scheduled_for=ahora,
                           is_response=True)
            raise RuntimeError("falla del barrido")

    monkeypatch.setattr(huerfanos, "barrer", _revienta)
    transporte = TransporteDePrueba()
    resumen = ciclo.ejecutar_pasada(
        conn, ws, transporte, _ahora(), _ahora() - timedelta(hours=1),
        con_cadencias=False)
    conn.commit()

    assert resumen["huerfanos_avisados"] == 0
    assert isinstance(resumen["huerfanos_fallo"], RuntimeError)
    enviados = [str(e) for e in transporte.enviados]
    assert any("Listo para salir" in e for e in enviados)
    assert not any("Parcial que se revierte" in e for e in enviados)
    assert [a["cuerpo"] for a in _avisos(conn, tg)] == ["Listo para salir"]


def test_la_etapa_del_fallo_de_un_huerfano_tiene_su_explicacion():
    assert huerfanos.ETAPA_MENSAJE_HUERFANO_FALLO in EXPLICACION_POR_ETAPA


# --- T9-H19h: lo que dejó la revisión de T9-H19g -------------------------------------

def _cerca_de_ahora_de_la_base(conn, consulta_de_at: str) -> bool:
    with admin(conn) as cur:
        cur.execute(f"select abs(extract(epoch from now() - ({consulta_de_at}))) < 30 "
                    "as cerca")
        return cur.fetchone()["cerca"]


def test_la_marca_de_fallo_no_se_pone_si_el_incidente_no_se_confirmo(
        corework, conn, monkeypatch, capsys):
    """La marca en memoria sólo vale si el incidente del fallo quedó confirmado: si
    la transacción que lo llevaba se pierde, el recibo se reporta de nuevo."""
    ws = corework.workspace_id
    uid, tg = _persona(conn)
    veneno = _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=30),
                     message_id=1)
    _envenenar(monkeypatch, veneno)
    real_espacio, real_incidente = huerfanos.espacio, huerfanos.registrar_incidente
    estado = {"perder": True, "escribio": False}

    def incidente(cur, workspace_id, resumen, **kw):
        if kw.get("etapa") == huerfanos.ETAPA_MENSAJE_HUERFANO_FALLO:
            estado["escribio"] = True
        return real_incidente(cur, workspace_id, resumen, **kw)

    @contextmanager
    def espacio_que_pierde_el_commit(c, workspace_id):
        estado["escribio"] = False
        with real_espacio(c, workspace_id) as cur:
            yield cur
            if estado["perder"] and estado["escribio"]:
                raise RuntimeError("falló el commit")     # se revierte todo

    monkeypatch.setattr(huerfanos, "registrar_incidente", incidente)
    monkeypatch.setattr(huerfanos, "espacio", espacio_que_pierde_el_commit)

    assert huerfanos.barrer(conn, ws, _ahora()) == 0

    assert veneno not in huerfanos._FALLIDOS
    assert "RuntimeError" in capsys.readouterr().out       # nunca en silencio
    estado["perder"] = False
    assert huerfanos.barrer(conn, ws, _ahora()) == 0       # se reporta de nuevo
    assert veneno in huerfanos._FALLIDOS
    assert _incidentes_de_etapa(
        conn, ws, huerfanos.ETAPA_MENSAJE_HUERFANO_FALLO) == [veneno]


def test_una_reentrega_durante_el_resto_del_ciclo_no_espera_a_que_termine(
        cliente, corework, conn, uri, monkeypatch):
    """El candado del mensaje sólo dura lo que dura el aviso de ese recibo: una
    reentrega que llega mientras el ciclo sigue (despacho) no espera a su commit."""
    ws = corework.workspace_id
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    uid, tg = _persona(conn)
    _recibo(conn, ws, uid, tg, hace=EN_CURSO + timedelta(minutes=1), message_id=41)
    espera = {}

    def entregar():
        c = conectar(uri)
        try:
            gateway.procesar_update(c, "corework", _update(tg))
        finally:
            c.close()

    real = ciclo.despachar

    def despachar_con_reentrega(*a, **k):
        hilo = threading.Thread(target=entregar)
        hilo.start()
        hilo.join(timeout=10)                # el ciclo sigue: no puede esperarlo
        espera["viva"] = hilo.is_alive()
        return real(*a, **k)

    monkeypatch.setattr(ciclo, "despachar", despachar_con_reentrega)
    ciclo.ejecutar_pasada(conn, ws, TransporteDePrueba(), _ahora(),
                          _ahora() - timedelta(hours=1), con_cadencias=False)
    conn.commit()

    assert espera["viva"] is False
    assert proveedor.ruteados == []                 # se absorbió: ya tenía su aviso


def test_olvidar_fallidos_viejos_descarta_lo_reportado_hace_mas_que_la_cota():
    viejo = time.monotonic() - COTA.total_seconds() - 1
    huerfanos._FALLIDOS["viejo"] = viejo
    huerfanos._FALLIDOS["reciente"] = time.monotonic()

    huerfanos._olvidar_fallidos_viejos()

    assert list(huerfanos._FALLIDOS) == ["reciente"]


def test_un_mensaje_escrito_se_fecha_con_el_reloj_de_la_base_aunque_la_app_este_desalineada(
        cliente, corework, conn, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _reloj_de_la_aplicacion_desalineado(monkeypatch, timedelta(days=-2))

    _enviar(cliente, _update(tg, message_id=77))

    assert _cerca_de_ahora_de_la_base(
        conn, "select at from inbound_message where telegram_message_id = 77")
