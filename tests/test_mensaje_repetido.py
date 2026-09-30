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
from prisma.incidentes import EXPLICACION_POR_ETAPA

from tests.test_una_respuesta import (_con_respuesta_del_modelo, _filas_de_salida,
                                      _tg)
from tests.test_menu_tarea import cliente  # noqa: F401


def _update(tg, texto="hola", message_id=41, clave="message"):
    return {clave: {"message_id": message_id, "text": texto,
                    "chat": {"id": tg, "type": "private"},
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
    real = gateway._estado_de_entrega
    primera = threading.Event()

    def demorada(*args, **kwargs):
        resultado = real(*args, **kwargs)
        if not primera.is_set():
            primera.set()
            time.sleep(1.0)
        return resultado

    monkeypatch.setattr(gateway, "_estado_de_entrega", demorada)
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

    assert not any(h.is_alive() for h in hilos)     # ninguna quedó colgada
    assert errores == []
    assert len(_entrantes(conn, tg)) == 1
    assert len(_visibles(conn, tg)) == 1
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 1


# --- T9-H19d: absorber sólo lo que se atendió o puede estar atendiéndose -------------
# El recibo de la fase 1 significa "recibido", no "respondido": si el turno del primer
# envío murió después de confirmarlo (reinicio, OOM), la reentrega es la recuperación.

EN_CURSO = int(gateway.VENTANA_TURNO_EN_CURSO.total_seconds())
COTA = int(gateway.COTA_REENTREGA.total_seconds())


def _recibo_sin_respuesta(conn, tg, message_id, hace_s):
    """Un recibo de la fase 1 cuyo turno nunca encoló nada, de hace `hace_s`."""
    with admin(conn) as cur:
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto, at)
               select m.workspace_id, %s, %s, u.id, 'hola',
                      now() - make_interval(secs => %s)
                 from app_user u join membership m on m.app_user_id = u.id
                where u.telegram_user_id = %s limit 1 returning id""",
            (message_id, tg, hace_s, tg))
        fila = cur.fetchone()
    conn.commit()
    return str(fila["id"])


def _envejecer(conn, message_id, segundos):
    with admin(conn) as cur:
        cur.execute("""update inbound_message set at = at - make_interval(secs => %s)
                        where telegram_message_id = %s""", (segundos, message_id))
    conn.commit()


def _detalles(conn, accion):
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where accion = %s", (accion,))
        return [f["detalle"] for f in cur.fetchall()]


def _incidentes_de(conn, etapa):
    with admin(conn) as cur:
        cur.execute("select referencia_id from incident where etapa = %s", (etapa,))
        return cur.fetchall()


def test_la_reentrega_de_un_turno_muerto_se_recupera_una_sola_vez(
        cliente, conn, corework, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    previo = _recibo_sin_respuesta(conn, tg, 41, EN_CURSO + 60)

    _enviar(cliente, _update(tg))
    _enviar(cliente, _update(tg))             # y la siguiente reentrega ya se absorbe

    assert len(_visibles(conn, tg)) == 1
    assert len(proveedor.ruteados) == 1
    assert len(_entrantes(conn, tg, 41)) == 2       # el recibo muerto y el nuevo
    incidentes = _incidentes_de(conn, gateway.ETAPA_MENSAJE_RECUPERADO)
    assert len(incidentes) == 1
    assert str(incidentes[0]["referencia_id"]) != previo
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 1


def test_la_reentrega_de_un_turno_cuya_respuesta_se_descarto_a_proposito_se_absorbe(
        cliente, conn, corework, monkeypatch):
    """Una respuesta que el código descartó antes de enviar (opciones reemplazadas,
    vista previa ya no vigente) sigue siendo la respuesta de ese turno: el turno no
    murió, así que la reentrega no lo vuelve a correr."""
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    previo = _recibo_sin_respuesta(conn, tg, 41, EN_CURSO + 60)
    with admin(conn) as cur:
        cur.execute(
            """insert into message_outbox
                 (workspace_id, chat_id, tipo, cuerpo, estado, es_respuesta,
                  entrante_id, dedupe_key)
               select workspace_id, chat_id, 'normal', 'ok', 'descartado', true,
                      id, 'test:' || id::text
                 from inbound_message where id = %s""", (previo,))
    conn.commit()

    _enviar(cliente, _update(tg))

    assert len(_entrantes(conn, tg, 41)) == 1
    assert proveedor.ruteados == []
    assert _incidentes_de(conn, gateway.ETAPA_MENSAJE_RECUPERADO) == []


def test_la_reentrega_dentro_de_la_ventana_sin_respuesta_todavia_se_absorbe(
        cliente, conn, corework, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _recibo_sin_respuesta(conn, tg, 41, EN_CURSO - 60)   # su turno puede seguir

    _enviar(cliente, _update(tg))

    assert len(_entrantes(conn, tg, 41)) == 1
    assert _visibles(conn, tg) == []
    assert proveedor.ruteados == []
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 1
    assert _incidentes_de(conn, gateway.ETAPA_MENSAJE_RECUPERADO) == []


def test_la_reentrega_de_un_mensaje_ya_respondido_se_absorbe_aunque_sea_vieja(
        cliente, conn, corework, monkeypatch):
    proveedor = _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _enviar(cliente, _update(tg))
    _envejecer(conn, 41, EN_CURSO + 60)

    _enviar(cliente, _update(tg))

    assert len(_entrantes(conn, tg, 41)) == 1
    assert len(_visibles(conn, tg)) == 1
    assert len(proveedor.ruteados) == 1
    assert _incidentes_de(conn, gateway.ETAPA_MENSAJE_RECUPERADO) == []


def test_un_recibo_mas_viejo_que_la_cota_nunca_absorbe(
        cliente, conn, corework, monkeypatch):
    """Si Telegram reinicia la numeración (cambió el token del bot), un mensaje
    nuevo puede chocar con un id viejo: pasado lo que Telegram reentrega, es nuevo."""
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _enviar(cliente, _update(tg))
    _envejecer(conn, 41, COTA + 60)

    _enviar(cliente, _update(tg))

    assert len(_entrantes(conn, tg, 41)) == 2
    assert len(_visibles(conn, tg)) == 2
    assert _auditorias(conn, "mensaje_repetido_absorbido") == 0
    assert _incidentes_de(conn, gateway.ETAPA_MENSAJE_RECUPERADO) == []


def test_la_auditoria_de_lo_absorbido_dice_cual_mensaje_y_cual_recibo(
        cliente, conn, corework, monkeypatch):
    _con_respuesta_del_modelo(monkeypatch)
    tg = _tg(conn)
    _enviar(cliente, _update(tg, message_id=77))
    previo = str(_entrantes(conn, tg, 77)[0]["id"])

    _enviar(cliente, _update(tg, message_id=77))

    (detalle,) = _detalles(conn, "mensaje_repetido_absorbido")
    assert detalle["telegram_message_id"] == 77
    assert detalle["entrante_previo_id"] == previo


def test_la_etapa_de_recuperacion_tiene_su_explicacion():
    assert gateway.ETAPA_MENSAJE_RECUPERADO == "mensaje_recuperado_sin_respuesta"
    assert gateway.ETAPA_MENSAJE_RECUPERADO in EXPLICACION_POR_ETAPA


def test_las_ventanas_son_coherentes():
    assert (gateway.VENTANA_TOQUE_REPETIDO < gateway.VENTANA_TURNO_EN_CURSO
            < gateway.COTA_REENTREGA)
