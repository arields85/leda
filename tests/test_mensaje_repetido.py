"""Un reenvío de Telegram no es un mensaje nuevo (T9-H19b, ADR 0013 regla 2).

Telegram reintenta el webhook si tarda (un turno con modelo tarda 10-30 s): la
segunda entrega trae el mismo `message_id` en el mismo chat. Se absorbe: ni turno,
ni respuesta, ni efecto, ni recibo nuevo -- sólo su auditoría. Es el mismo
mecanismo de los toques (T9-R4): un candado de asesor por
(espacio, chat, `message_id`) y luego la consulta, en la fase 1, que confirma
antes de la fase 2 larga; la segunda entrega espera ese commit y ve la fila.

`edited_message` NO entra: hoy se trata como un mensaje nuevo y esa decisión es del
usuario (T9-H19c); estas pruebas fijan el comportamiento actual.
"""

from __future__ import annotations

import threading
import time

from prisma import gateway
from prisma.db import admin, conectar

from tests.test_una_respuesta import (_con_respuesta_del_modelo, _filas_de_salida,
                                      _tg)
from tests.test_menu_tarea import cliente  # noqa: F401


def _update(tg, texto="hola", message_id=41, chat=None, clave="message"):
    return {clave: {"message_id": message_id, "text": texto,
                    "chat": {"id": chat or tg, "type": "private"},
                    "from": {"id": tg}}}


def _enviar(cliente, update):
    r = cliente.post("/telegram/corework", json=update,
                     headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})
    assert r.status_code == 200
    return r


def _entrantes(conn, tg, message_id=None):
    with admin(conn) as cur:
        cur.execute(
            """select id from inbound_message where chat_id = %s
                  and boton_callback is null
                  and (%s::bigint is null or telegram_message_id = %s)""",
            (tg, message_id, message_id))
        return cur.fetchall()


def _auditorias(conn, accion):
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where accion = %s", (accion,))
        return cur.fetchone()["n"]


def _visibles(conn, tg):
    return [f for f in _filas_de_salida(conn, tg)
            if f["es_respuesta"] and f["estado"] != "descartado"]


def test_el_mismo_mensaje_entregado_dos_veces_se_atiende_una_sola_vez(
        cliente, conn, corework, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    _enviar(cliente, _update(tg))
    _enviar(cliente, _update(tg))

    assert len(_entrantes(conn, tg)) == 1
    assert len(_visibles(conn, tg)) == 1
    assert len(proveedor.ruteados) == 1              # un solo turno
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 1
    assert _auditorias(conn, "mensaje_recibido") == 1


def test_otro_message_id_en_el_mismo_chat_se_atiende(
        cliente, conn, corework, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    _enviar(cliente, _update(tg, message_id=41))
    _enviar(cliente, _update(tg, message_id=42))

    assert len(_entrantes(conn, tg)) == 2
    assert len(_visibles(conn, tg)) == 2
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 0


def test_el_mismo_message_id_en_otro_chat_se_atiende(
        cliente, conn, corework, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    otra = _tg(conn, "Marcos Tarquini")

    _enviar(cliente, _update(tg, message_id=41))
    _enviar(cliente, _update(otra, message_id=41))

    assert len(_entrantes(conn, tg)) == 1
    assert len(_entrantes(conn, otra)) == 1
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 0


def test_un_mensaje_sin_message_id_se_atiende_como_siempre(
        cliente, conn, corework, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    update = _update(tg)
    del update["message"]["message_id"]

    _enviar(cliente, update)
    _enviar(cliente, update)

    assert len(_entrantes(conn, tg)) == 2
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 0


def test_un_mensaje_editado_se_sigue_tratando_como_nuevo(
        cliente, conn, corework, monkeypatch):
    """Fija el comportamiento de hoy (T9-H19c es una decisión del usuario): la
    edición de un mensaje ya atendido, con el mismo `message_id`, recibe su turno."""
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)

    _enviar(cliente, _update(tg, message_id=41))
    _enviar(cliente, _update(tg, texto="hola, editado", message_id=41,
                             clave="edited_message"))

    assert len(_entrantes(conn, tg, 41)) == 2
    assert len(_visibles(conn, tg)) == 2
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 0


def test_dos_entregas_simultaneas_se_atienden_una_sola_vez(
        cliente, uri, conn, corework, monkeypatch):
    """La segunda espera el commit de la primera (candado de asesor) y ve su fila.
    La primera se demora a propósito DESPUÉS de consultar y ANTES de insertar: sin
    el candado, la segunda la alcanzaría en esa ventana y las dos insertarían."""
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    real = gateway._es_mensaje_repetido
    primera = threading.Event()

    def demorada(*args, **kwargs):
        resultado = real(*args, **kwargs)
        if not primera.is_set():
            primera.set()
            time.sleep(1.0)
        return resultado

    monkeypatch.setattr(gateway, "_es_mensaje_repetido", demorada)
    errores = []

    def entregar(espera):
        time.sleep(espera)
        c = conectar(uri)
        try:
            gateway.procesar_update(c, "corework", _update(tg))
        except Exception as e:  # noqa: BLE001
            errores.append(e)
        finally:
            c.close()

    hilos = [threading.Thread(target=entregar, args=(0.0,)),
             threading.Thread(target=entregar, args=(0.3,))]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=60)

    assert errores == []
    assert len(_entrantes(conn, tg)) == 1
    assert len(_visibles(conn, tg)) == 1
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 1
