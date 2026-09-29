"""Una pregunta pendiente es contexto, no una trampa (T9-R1c-1, ADR 0013 regla
1): el campo de texto libre del alta guiada de una tarea.

Con el alta esperando un campo (título, descripción, fecha objetivo...), el
mensaje siguiente pasa por el ruteo tipado, que sólo devuelve un comando de una
lista cerrada; el código ejecuta un manejo determinista por comando, el mismo
manejo (`gateway._atender_pregunta_pendiente`) que ya usan el dato del menú,
Modificar y "Ninguna, lo escribo". Hasta ahora `procesar_update` le daba el
mensaje al alta antes de `_turno` y el campo lo tomaba sin mirarlo: un "hola"
quedaba como título de la tarea.

Los ruteos y el modelo se guionan con `ProveedorGuionado`; ninguna prueba toca
la red ni el modelo real.
"""

from __future__ import annotations

import itertools
from datetime import datetime, timezone

import pytest
from psycopg.types.json import Jsonb

from prisma import gateway
from prisma import ingreso_tareas as I
from prisma.db import admin, espacio
from prisma.llm import RespectoPendiente, Respuesta, RouteEnvelope

from tests.test_menu_tarea import (_quien, _tarea as _tarea_menu,  # noqa: F401
                                   _telegram_id, _tocar, cliente)
from tests.test_pregunta_pendiente_otras import (_con_rutas, _filas_del_chat,
                                                 _incidentes, _ruta, _salidas)

PERSONA = "Marcos Tarquini"
TITULO_ALTA = "Cablear tablero norte"
PREGUNTA_TITULO = "Escribí el título exacto de la tarea"
PREGUNTA_FECHA = "Escribí la fecha objetivo exacta"

_ids_de_mensaje = itertools.count(700)


def _mensaje_privado(cliente, tg, texto):
    """Un mensaje de un chat privado, como lo manda Telegram (`type` incluido),
    con un `message_id` propio por mensaje."""
    return cliente.post(
        "/telegram/corework",
        json={"message": {"message_id": next(_ids_de_mensaje), "text": texto,
                          "chat": {"id": tg, "type": "private"},
                          "from": {"id": tg}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "s3cr3t"})


def _abrir_alta(conn, ws, *, campo: str = "title") -> tuple[int, str]:
    """Deja el alta esperando el texto libre de `campo` y devuelve (chat,
    request_id). `title`: el alta recién empezada, sin nada propuesto.
    `due_date`: con el título y las entidades ya confirmadas."""
    with admin(conn) as cur:
        _tarea_menu(cur, ws)              # deja un objetivo, así hay candidatos
    conn.commit()
    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        cur.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
               values (%s, %s, %s, %s, 'armame una tarea') returning id""",
            (ws, next(_ids_de_mensaje), tg, quien.app_user_id))
        inbound_id = str(cur.fetchone()["id"])
        outcome = I.start(cur, quien, chat_id=tg, source_inbound_id=inbound_id,
                          source_raw_text="armame una tarea", proposals={},
                          now=ahora)
        if campo == "due_date":
            for nombre, valor in (
                    ("title", TITULO_ALTA), ("objective", {"id": "x"}),
                    ("responsible", {"id": "x"}), ("area", {"id": "x"})):
                cur.execute(
                    """update task_intake_field
                          set estado = 'confirmed', valor = %s
                        where request_id = %s and campo = %s""",
                    (Jsonb(valor), outcome.request_id, nombre))
            I._advance(cur, I._request(cur, outcome.request_id), quien, ahora)
    conn.commit()
    assert _campo_del_slot(conn) == campo
    return tg, outcome.request_id


def _campo_del_slot(conn) -> str | None:
    with admin(conn) as cur:
        cur.execute("""select campo from task_intake_free_text_slot
                        where estado = 'active'""")
        fila = cur.fetchone()
    return fila["campo"] if fila else None


def _request(conn, request_id: str) -> dict:
    with admin(conn) as cur:
        cur.execute("""select r.estado, d.estado draft_estado
                         from task_intake_request r
                         join task_draft d on d.id = r.task_draft_id
                        where r.id = %s""", (request_id,))
        return cur.fetchone()


def _campo(conn, request_id: str, campo: str) -> dict:
    with admin(conn) as cur:
        cur.execute("""select estado, valor from task_intake_field
                        where request_id = %s and campo = %s""",
                    (request_id, campo))
        return cur.fetchone()


def _boton(conn, etiqueta: str) -> str:
    """El token del botón `etiqueta` de la última pregunta con botones."""
    with admin(conn) as cur:
        cur.execute(
            """select o.token from pending_action_option o
                 join pending_action p on p.id = o.pending_action_id
                where p.herramienta = %s and o.etiqueta like %s
                order by p.creado_en desc limit 1""",
            ("_respuesta_dato_menu", f"%{etiqueta}%"))
        return cur.fetchone()["token"]


# ---------------------------------------------------------------------------
# Cada comando
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("texto", [
    TITULO_ALTA, "revisión del variador de la línea 2", "ok, poné: Mantener HMI"])
def test_responde_toma_el_campo_y_sigue_como_siempre(
        cliente, conn, corework, monkeypatch, texto):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, tg)

    assert _mensaje_privado(cliente, tg, texto).status_code == 200

    campo = _campo(conn, rid, "title")
    assert campo["estado"] == "confirmed" and campo["valor"] == texto
    assert _campo_del_slot(conn) != "title"                   # se consumió
    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    assert _request(conn, rid)["estado"] == "active"
    assert proveedor.recibidos == []                          # el agente no habló
    # El ruteo recibió la pregunta abierta, no sólo el mensaje.
    assert len(proveedor.pendientes) == 1
    assert PREGUNTA_TITULO in proveedor.pendientes[0]


@pytest.mark.parametrize("texto", ["hola", "gracias", "buen día"])
def test_charla_repite_la_pregunta_y_no_consume(
        cliente, conn, corework, monkeypatch, texto):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, texto)

    assert _campo(conn, rid, "title")["estado"] == "missing"  # no es el título
    assert _campo_del_slot(conn) == "title"                   # sigue abierta
    assert _salidas(conn, tg) == antes + 1
    assert PREGUNTA_TITULO in _filas_del_chat(conn, tg)[-1]["cuerpo"]
    assert proveedor.recibidos == []


def test_no_puedo_lo_dice_una_vez_y_deja_la_pregunta_abierta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.NO_PUEDO)])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "adjuntame el plano de la máquina")

    assert _campo_del_slot(conn) == "title"
    assert _salidas(conn, tg) == antes + 1
    cuerpo = _filas_del_chat(conn, tg)[-1]["cuerpo"]
    assert gateway.AVISO_NO_PUEDO_DATO_PENDIENTE in cuerpo
    assert PREGUNTA_TITULO in cuerpo


@pytest.mark.parametrize("texto", [
    "mejor dejalo", "no, cancelá todo", "olvidate, no quiero crear nada"])
def test_cancela_cancela_el_borrador_y_dice_que_lo_dejo(
        cliente, conn, corework, monkeypatch, texto):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CANCELA)])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, texto)

    estados = _request(conn, rid)
    assert estados["estado"] == "cancelled"
    assert estados["draft_estado"] == "cancelled"
    assert _campo_del_slot(conn) is None
    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    cuerpo = _filas_del_chat(conn, tg)[-1]["cuerpo"]
    assert "dejé de lado" in cuerpo and "borrador" in cuerpo
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log "
                    "where accion = 'cancelar_ingreso_tarea'")
        assert cur.fetchone()["n"] == 1


def test_cancela_nombra_la_tarea_si_ya_tiene_titulo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws, campo="due_date")
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CANCELA)])

    _mensaje_privado(cliente, tg, "dejalo así")

    assert _request(conn, rid)["estado"] == "cancelled"
    assert TITULO_ALTA in _filas_del_chat(conn, tg)[-1]["cuerpo"]


def test_otro_tema_atiende_el_mensaje_y_retoma_la_pregunta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
        guion=[Respuesta(texto="Un bloqueo es algo que frena una tarea.")])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "¿qué es un bloqueo?")

    assert _campo_del_slot(conn) == "title"                   # sigue abierta
    assert _campo(conn, rid, "title")["estado"] == "missing"
    assert _salidas(conn, tg) == antes + 2                    # texto + retome
    filas = _filas_del_chat(conn, tg)
    assert filas[-2]["cuerpo"].startswith("Un bloqueo es")
    assert filas[-1]["cuerpo"].startswith("¿Seguimos con")
    assert PREGUNTA_TITULO in filas[-1]["cuerpo"]
    assert filas[-1]["pending_action_id"] is not None         # con su botón
    # El responder sabe que hay una pregunta abierta y no la propone de nuevo.
    assert gateway.MARCA_PREGUNTA_PENDIENTE in proveedor.recibidos[-1][0]


def test_dejarlo_del_retome_cancela_el_borrador_y_el_segundo_toque_se_avisa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
               guion=[Respuesta(texto="Un bloqueo frena una tarea.")])
    _mensaje_privado(cliente, tg, "¿qué es un bloqueo?")
    token = _boton(conn, "Dejarlo")
    antes = _salidas(conn, tg)

    assert _tocar(cliente, token, tg).status_code == 200

    assert _request(conn, rid)["estado"] == "cancelled"
    assert _salidas(conn, tg) == antes + 1
    assert "dejé de lado" in _filas_del_chat(conn, tg)[-1]["cuerpo"]

    assert _tocar(cliente, token, tg).status_code == 200      # toque tardío
    assert _request(conn, rid)["estado"] == "cancelled"


def test_dudoso_pregunta_con_botones_y_si_es_eso_toma_el_campo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO)])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "mmm, algo del tablero")

    assert _salidas(conn, tg) == antes + 1
    assert _campo_del_slot(conn) == "title"                   # no se consumió
    assert _campo(conn, rid, "title")["estado"] == "missing"
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"].startswith("¿Esto es")
    token = _boton(conn, "Sí, es eso")
    antes = _salidas(conn, tg)

    assert _tocar(cliente, token, tg).status_code == 200

    campo = _campo(conn, rid, "title")
    assert campo["estado"] == "confirmed"
    assert campo["valor"] == "mmm, algo del tablero"
    assert _salidas(conn, tg) == antes + 1

    # Un segundo toque, con el campo ya tomado, no lo vuelve a tomar.
    antes = _salidas(conn, tg)
    assert _tocar(cliente, token, tg).status_code == 200
    assert _campo(conn, rid, "title")["valor"] == "mmm, algo del tablero"
    assert _salidas(conn, tg) <= antes + 1


def test_dudoso_no_es_otra_cosa_sigue_el_camino_normal_y_deja_abierta_la_pregunta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
        guion=[Respuesta(texto="Tenés que decirme el título.")])
    _mensaje_privado(cliente, tg, "puede ser")
    token = _boton(conn, "No, es otra cosa")

    assert _tocar(cliente, token, tg).status_code == 200

    assert _campo_del_slot(conn) == "title"
    assert _campo(conn, rid, "title")["estado"] == "missing"
    assert gateway.MARCA_PREGUNTA_PENDIENTE in proveedor.recibidos[-1][0]


def test_corrige_todavia_no_tiene_camino_en_el_alta_y_se_trata_como_dudoso(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CORRIGE)])

    _mensaje_privado(cliente, tg, "no, en realidad ponele otro nombre")

    assert _campo(conn, rid, "title")["estado"] == "missing"
    assert _campo_del_slot(conn) == "title"
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"].startswith("¿Esto es")


def test_con_el_ruteo_caido_la_pregunta_queda_abierta_y_hay_una_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    malo = RouteEnvelope(calls=())
    _con_rutas(monkeypatch, [malo, malo])
    incidentes = _incidentes(conn, ws)
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, TITULO_ALTA)

    assert _incidentes(conn, ws) == incidentes + 1
    assert _salidas(conn, tg) == antes + 1
    assert _campo_del_slot(conn) == "title"                   # no se perdió
    assert _campo(conn, rid, "title")["estado"] == "missing"


# ---------------------------------------------------------------------------
# Lo que no cambia
# ---------------------------------------------------------------------------


def test_otras_preguntas_de_texto_libre_del_alta_tambien_pasan_por_el_ruteo(
        cliente, conn, corework, monkeypatch):
    # La fecha objetivo: un "hola" no es una fecha.
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws, campo="due_date")
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje_privado(cliente, tg, "hola")

    assert _campo_del_slot(conn) == "due_date"
    assert PREGUNTA_FECHA in _filas_del_chat(conn, tg)[-1]["cuerpo"]
    assert "la fecha objetivo" in proveedor.pendientes[0]


def test_sin_un_campo_de_texto_libre_abierto_el_alta_sigue_como_antes(
        cliente, conn, corework, monkeypatch):
    # T9-R1c-2 cubre las opciones con botones: hoy el mensaje se atiende con el
    # recordatorio de siempre, sin ruteo.
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    with espacio(conn, ws) as cur:
        cur.execute("""update task_intake_free_text_slot
                          set estado = 'invalidated' where request_id = %s""",
                    (rid,))
    conn.commit()
    proveedor = _con_rutas(monkeypatch, [])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "hola")

    assert proveedor.ruteados == []
    assert _salidas(conn, tg) == antes + 1


def test_fuera_de_un_chat_privado_el_alta_no_lee_el_mensaje(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(None)],
                           guion=[Respuesta(texto="Hola.")])

    # El helper de `test_menu_tarea` manda el mensaje sin `type: private`.
    from tests.test_menu_tarea import _mensaje
    _mensaje(cliente, tg, TITULO_ALTA)

    assert _campo_del_slot(conn) == "title"
    assert _campo(conn, rid, "title")["estado"] == "missing"
    assert proveedor.pendientes == [None]


def test_un_campo_demasiado_largo_se_rechaza_y_la_pregunta_sigue_abierta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "x" * 300)

    assert _campo(conn, rid, "title")["estado"] == "missing"
    assert _campo_del_slot(conn) == "title"
    assert _salidas(conn, tg) == antes + 1
    assert "Acortá" in _filas_del_chat(conn, tg)[-1]["cuerpo"]


def test_un_toque_tardio_sobre_un_campo_ya_cancelado_se_avisa_sin_tomarlo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO)])
    _mensaje_privado(cliente, tg, "mmm, algo del tablero")
    token = _boton(conn, "Sí, es eso")
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        cur.execute("select * from task_intake_request where id = %s", (rid,))
        I._cancel(cur, cur.fetchone(), quien, datetime.now(timezone.utc))
    conn.commit()
    antes = _salidas(conn, tg)

    assert _tocar(cliente, token, tg).status_code == 200

    assert _campo(conn, rid, "title")["estado"] == "missing"
    assert _salidas(conn, tg) == antes + 1
    assert (gateway.AVISO_DATO_YA_NO_PENDIENTE
            in _filas_del_chat(conn, tg)[-1]["cuerpo"])


def test_con_el_alta_y_otra_pregunta_abiertas_el_alta_tiene_precedencia(
        cliente, conn, corework, monkeypatch):
    # Como antes de T9-R1c-1: el alta leía el mensaje antes que `_turno`. La
    # pregunta de Modificar queda abierta, sin consumirse.
    from tests.test_pregunta_pendiente_otras import _abiertas, _abrir_modificar

    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _abrir_modificar(cliente, conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje_privado(cliente, tg, "hola")

    assert PREGUNTA_TITULO in proveedor.pendientes[0]
    assert _campo_del_slot(conn) == "title"
    assert _abiertas(conn) == 1                               # Modificar sigue
