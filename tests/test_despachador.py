"""El despachador como transporte: entrega cada fila una sola vez, aun si falla a mitad de
un lote, y nunca deja el token del bot en un error.

Movidas desde `tests/test_ciclo.py` (E3-7), cuando se retiró el ciclo viejo de `leda`
(`ciclo.py`, con sus cadencias y su escalera): estas pruebas son del despachador, que sigue.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import pytest

from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.despachador import TransporteDePrueba

BA = ZoneInfo("America/Argentina/Buenos_Aires")

# Token de bot falso, sólo para probar que un error de Telegram no lo
# filtra -- nunca se compara contra `os.environ` (regla de seguridad del
# proyecto: no afirmar directo contra variables de entorno).
TOKEN_FALSO = "123456789:AAAA-SECRETO-DE-PRUEBA-FALSO"



# ---------------------------------------------------------------------------
# R4-001: un mensaje ya entregado y marcado no se reenvía porque OTRO
# mensaje del mismo lote falló después
# ---------------------------------------------------------------------------

def test_despachar_no_reenvia_el_primero_si_el_segundo_falla_al_marcarse(
        corework, conn, monkeypatch):
    """Antes, sólo el ENVÍO estaba protegido: si la marca de 'enviado' (el
    UPDATE posterior) fallaba, la excepción escapaba de `despachar` sin
    contenerse y el `rollback` de la transacción entera -- compartida con la
    escalera -- devolvía a 'listo' TAMBIÉN los mensajes anteriores del mismo
    lote, que se reenviaban en la próxima pasada."""
    from leda import despachador as desp

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)  # lunes, en horario

    with espacio(conn, ws) as cur:
        for i in range(2):
            cur.execute(
                """insert into message_outbox
                     (workspace_id, chat_id, cuerpo, estado, programado_para,
                      dedupe_key)
                   values (%s, %s, %s, 'listo', %s, %s)""",
                (ws, 5000 + i, f"mensaje de prueba {i}",
                 ahora - timedelta(microseconds=2 - i), f"prueba-r4-001-{i}"))
    conn.commit()

    llamadas = {"n": 0}
    original = desp._marcar_enviado

    def _falla_en_el_segundo(cur, ahora, outbox_id):
        llamadas["n"] += 1
        if llamadas["n"] == 2:
            raise RuntimeError("falla simulada al marcar 'enviado'")
        return original(cur, ahora, outbox_id)

    monkeypatch.setattr(desp, "_marcar_enviado", _falla_en_el_segundo)

    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r1 = desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    assert r1["enviados"] == 1   # el primero se entregó y quedó marcado
    assert r1["fallidos"] == 1   # el segundo falló al marcarse

    # "próxima pasada": si el primero hubiera vuelto a 'listo' por un
    # rollback de todo el lote, se reenviaría acá.
    monkeypatch.setattr(desp, "_marcar_enviado", original)
    transporte2 = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r2 = desp.despachar(cur, ws, transporte2, cal, ahora)
    conn.commit()

    assert len(transporte2.enviados) == 1   # sólo el segundo (reintento)
    assert r2["enviados"] == 1


# ---------------------------------------------------------------------------
# R3-001 (revisión 2026-09-28): marcar 'enviado' va ANTES de enviar, no
# después -- si el envío ya salió y la marca falla, se reenvía seguro.
# ---------------------------------------------------------------------------

def test_intentar_envio_no_envia_si_falla_la_marca_de_enviado(
        corework, conn, monkeypatch):
    """Si el UPDATE que marca 'enviado' falla, el mensaje NUNCA se manda:
    la marca -- el cambio de estado durable -- va antes del envío, no
    después."""
    from leda import despachador as desp

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)  # lunes, en horario

    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, programado_para,
                  dedupe_key)
               values (%s, 6000, 'mensaje de prueba', 'listo', %s, %s)""",
            (ws, ahora, "prueba-r3-001-marca"))
    conn.commit()

    def _marca_rota(cur, ahora, outbox_id):
        raise RuntimeError("falla simulada al marcar 'enviado'")

    monkeypatch.setattr(desp, "_marcar_enviado", _marca_rota)

    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r = desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    assert transporte.enviados == []   # nunca se llegó a llamar a enviar
    assert r["fallidos"] == 1

    with admin(conn) as cur:
        cur.execute("select estado from message_outbox where dedupe_key = %s",
                    ("prueba-r3-001-marca",))
        fila = cur.fetchone()
    conn.commit()
    assert fila["estado"] == "listo"   # sigue pendiente, nunca quedó 'enviado'


def test_intentar_envio_conserva_la_marca_si_falla_guardar_el_id_de_telegram(
        corework, conn, monkeypatch, capsys):
    """El mensaje YA se entregó cuando se intenta guardar el id de
    Telegram: si ese UPDATE falla, la marca 'enviado' tiene que quedar en
    pie -- no se reenvía en la próxima pasada -- y el fallo se reporta sin
    el texto crudo de la excepción."""
    from leda import despachador as desp

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)

    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, programado_para,
                  dedupe_key)
               values (%s, 6001, 'mensaje de prueba', 'listo', %s, %s)""",
            (ws, ahora, "prueba-r3-001-id"))
    conn.commit()

    original_guardar = desp._guardar_id_telegram
    texto_secreto = "falla simulada al guardar el id de Telegram"

    def _id_roto(cur, tg_id, outbox_id):
        raise RuntimeError(texto_secreto)

    monkeypatch.setattr(desp, "_guardar_id_telegram", _id_roto)

    transporte = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r = desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    assert len(transporte.enviados) == 1   # sí se entregó
    assert r["enviados"] == 1              # cuenta como éxito: ya se entregó

    salida = capsys.readouterr().out
    assert texto_secreto not in salida     # nunca el texto crudo de la excepción
    assert "RuntimeError" in salida

    with admin(conn) as cur:
        cur.execute(
            """select estado, telegram_message_id from message_outbox
                where dedupe_key = %s""",
            ("prueba-r3-001-id",))
        fila = cur.fetchone()
    conn.commit()
    assert fila["estado"] == "enviado"          # la marca queda en pie
    assert fila["telegram_message_id"] is None  # el id no se pudo guardar

    # "próxima pasada": si la marca se hubiera deshecho, se reenviaría acá.
    monkeypatch.setattr(desp, "_guardar_id_telegram", original_guardar)
    transporte2 = TransporteDePrueba()
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        r2 = desp.despachar(cur, ws, transporte2, cal, ahora)
    conn.commit()

    assert transporte2.enviados == []   # no se reenvía: ya estaba 'enviado'
    assert r2["enviados"] == 0


# ---------------------------------------------------------------------------
# Fix E: nunca un cliente HTTP nuevo por pasada -- se cachea por token
# ---------------------------------------------------------------------------

def test_transporte_telegram_cerrar_cierra_el_cliente_http():
    from leda.despachador import TransporteTelegram

    class _ClienteFalso:
        def __init__(self) -> None:
            self.cerrado = False

        def close(self) -> None:
            self.cerrado = True

    cliente = _ClienteFalso()
    transporte = TransporteTelegram("tok", cliente=cliente)
    transporte.cerrar()
    assert cliente.cerrado


# ---------------------------------------------------------------------------
# R1-001 (revisión 2026-09-28): un error de la API de Telegram nunca lleva
# la URL del pedido -- la URL de la API de Telegram lleva el token del bot.
# ---------------------------------------------------------------------------

def test_pedido_telegram_traduce_un_401_con_descripcion_sin_token():
    from leda import despachador as desp

    pedido = httpx.Request(
        "POST", f"https://api.telegram.org/bot{TOKEN_FALSO}/sendMessage")
    respuesta = httpx.Response(
        401, request=pedido,
        json={"ok": False, "error_code": 401, "description": "Unauthorized"})

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(respuesta.raise_for_status)

    error = info.value
    filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
    assert not filtra, "el error traducido filtra el token del bot"
    assert str(error) == "HTTPStatusError HTTP 401: Unauthorized"


def test_pedido_telegram_traduce_un_500_sin_descripcion_sin_token():
    from leda import despachador as desp

    pedido = httpx.Request(
        "POST", f"https://api.telegram.org/bot{TOKEN_FALSO}/sendMessage")
    respuesta = httpx.Response(500, request=pedido)  # sin cuerpo JSON

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(respuesta.raise_for_status)

    error = info.value
    filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
    assert not filtra, "el error traducido filtra el token del bot"
    assert str(error) == "HTTPStatusError HTTP 500"


def test_pedido_telegram_traduce_un_error_de_conexion_que_lleva_la_url():
    """Un error de red puede traer la URL en su propio mensaje -- no sólo un
    `HTTPStatusError` -- y se traduce igual, sin mirar `str(e)` del original."""
    from leda import despachador as desp

    url = f"https://api.telegram.org/bot{TOKEN_FALSO}/getUpdates"
    pedido = httpx.Request("GET", url)
    error_original = httpx.ConnectError(f"sin red para {url}", request=pedido)

    def _falla():
        raise error_original

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(_falla)

    error = info.value
    filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
    assert not filtra, "el error traducido filtra el token del bot"
    assert str(error) == "ConnectError"


def test_pedido_telegram_corta_la_cadena_de_excepciones():
    """`from None`: ni `__cause__` ni el traceback del error ya traducido
    arrastran el original -- que sí llevaba el token."""
    from leda import despachador as desp

    def _falla():
        raise RuntimeError(f"secreto en bot{TOKEN_FALSO}")

    with pytest.raises(desp.ErrorTelegram) as info:
        desp.pedido_telegram(_falla)

    error = info.value
    assert error.__cause__ is None
    assert error.__suppress_context__ is True


def test_texto_error_seguro_no_retraduce_un_error_ya_traducido():
    from leda import despachador as desp

    ya_traducido = desp.ErrorTelegram("HTTPStatusError HTTP 401: Unauthorized")
    assert desp.texto_error_seguro(ya_traducido) == str(ya_traducido)


def test_mantener_chat_activo_traduce_el_error_del_ping_de_typing(monkeypatch):
    """El `sendChatAction` de fondo hoy descarta su error entero (es
    cosmético) -- pero pasa por el mismo traductor que el resto de las
    llamadas a Telegram, así que si algún día deja de descartarse, ya no
    puede filtrar el token."""
    from leda import despachador as desp

    capturados: list[Exception] = []
    original = desp.pedido_telegram

    def _pedido_que_registra(fn, *a, **k):
        try:
            return original(fn, *a, **k)
        except desp.ErrorTelegram as e:
            capturados.append(e)
            raise

    monkeypatch.setattr(desp, "pedido_telegram", _pedido_que_registra)

    class _ClienteQueFalla:
        def post(self, url, json=None):
            pedido = httpx.Request("POST", url)
            raise httpx.HTTPStatusError(
                "fallo", request=pedido, response=httpx.Response(401, request=pedido))

    with desp.mantener_chat_activo(
            TOKEN_FALSO, 123, cliente=_ClienteQueFalla(), intervalo=0.01,
            espera_cierre=0.5, umbral=0):
        time.sleep(0.1)

    assert capturados, "el ping de typing nunca intentó llamar a Telegram"
    for error in capturados:
        filtra = TOKEN_FALSO in str(error) or TOKEN_FALSO in repr(error)
        assert not filtra, "el ping de typing filtra el token del bot"


def test_despachar_no_guarda_el_token_en_ultimo_error_si_telegram_falla(
        corework, conn):
    """`message_outbox.ultimo_error` -- lo que queda tras `_fallo` -- nunca
    lleva el token del bot, ni siquiera cuando el transporte real de
    Telegram es el que fallò (R1-001, revisión 2026-09-28): antes,
    `TransporteTelegram.enviar` dejaba escapar el `HTTPStatusError` de
    httpx tal cual, y su `str()` lleva la URL completa con el token."""
    from leda import despachador as desp

    class _ClienteQueFalla:
        def post(self, url, json=None):
            pedido = httpx.Request("POST", url)
            raise httpx.HTTPStatusError(
                "fallo", request=pedido,
                response=httpx.Response(
                    401, request=pedido,
                    json={"ok": False, "description": "Unauthorized"}))

    ws = corework.workspace_id
    ahora = datetime(2026, 7, 27, 10, 0, tzinfo=BA)

    with espacio(conn, ws) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, cuerpo, estado, programado_para,
                  dedupe_key)
               values (%s, 6002, 'mensaje de prueba', 'listo', %s, %s)""",
            (ws, ahora, "prueba-r1-001-ultimo-error"))
    conn.commit()

    transporte = desp.TransporteTelegram(TOKEN_FALSO, cliente=_ClienteQueFalla())
    with espacio(conn, ws) as cur:
        cal = Calendario.desde_base(cur, ws)
        desp.despachar(cur, ws, transporte, cal, ahora)
    conn.commit()

    with admin(conn) as cur:
        cur.execute(
            "select ultimo_error from message_outbox where dedupe_key = %s",
            ("prueba-r1-001-ultimo-error",))
        ultimo_error = cur.fetchone()["ultimo_error"]
    conn.commit()

    filtra = TOKEN_FALSO in (ultimo_error or "")
    assert not filtra, "message_outbox.ultimo_error guarda el token del bot"
    assert "401" in ultimo_error
