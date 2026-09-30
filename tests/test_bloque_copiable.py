"""Un mensaje con un bloque que se copia con un toque (T9-R1c-3, ADR 0005
decisión 1, precisión del 2026-09-29: Modificar en el borrador del alta).

Telegram no deja que un bot escriba texto editable en la caja de la persona: lo
que se puede hacer es mostrar lo que ella había escrito en un bloque (entidad
`pre`) que se copia con un toque y, si entra en 256 caracteres, con el botón de
copiar (`copy_text`). El bloque es siempre el final del mensaje: el transporte
calcula su posición sobre el texto que de verdad manda (con el saludo diario ya
antepuesto, si lo hubo), así que nada guarda un desplazamiento que el saludo
pueda mover.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prisma import saludo
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.despachador import Boton, TransporteDePrueba, TransporteTelegram, despachar
from prisma.salida import (COPY_TEXT_LIMIT, ETIQUETA_COPIAR, PayloadValidationError,
                           enqueue_outbox, entidad_de_bloque, prepare_buttons,
                           telegram_utf16_units)

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)   # lunes, en horario


class _Respuesta:
    def raise_for_status(self):
        pass

    def json(self):
        return {"result": {"message_id": 1}}


class _Http:
    def __init__(self):
        self.cuerpos = []

    def post(self, url, json=None, **kwargs):
        self.cuerpos.append(json)
        return _Respuesta()


def _enviar_por_telegram(texto, botones=None, bloque=None):
    http = _Http()
    transporte = TransporteTelegram("unused", cliente=http)
    if bloque is None:
        transporte.enviar(1, texto, botones)
    else:
        transporte.enviar(1, texto, botones, bloque=bloque)
    return http.cuerpos[0]


# ------------------------------------------------------------- transporte

def test_el_bloque_sale_como_una_entidad_pre_al_final_del_mensaje():
    texto = "Este es el título actual:\n\nCablear tablero norte"

    cuerpo = _enviar_por_telegram(texto, bloque="Cablear tablero norte")

    assert cuerpo["text"] == texto
    assert cuerpo["entities"] == [
        {"type": "pre", "offset": len("Este es el título actual:\n\n"),
         "length": len("Cablear tablero norte")}]


def test_la_entidad_cuenta_en_unidades_utf16_no_en_caracteres():
    # El emoji del principio y el del bloque ocupan dos unidades cada uno.
    antes = "👋 Título:\n\n"
    bloque = "Revisar 🔧 la válvula"
    cuerpo = _enviar_por_telegram(antes + bloque, bloque=bloque)

    assert cuerpo["entities"] == [
        {"type": "pre", "offset": telegram_utf16_units(antes),
         "length": telegram_utf16_units(bloque)}]
    assert telegram_utf16_units(antes) != len(antes)


def test_sin_bloque_no_hay_entidades():
    assert "entities" not in _enviar_por_telegram("hola")


def test_un_bloque_que_no_es_el_final_del_texto_no_sale():
    with pytest.raises(PayloadValidationError):
        entidad_de_bloque("Título: A\n\nresto", "A")


def test_un_bloque_vacio_no_sale():
    with pytest.raises(PayloadValidationError):
        entidad_de_bloque("Título:", "")


def test_el_boton_de_copiar_sale_con_copy_text():
    boton = Boton(ETIQUETA_COPIAR, "", copiar="Cablear tablero norte")

    cuerpo = _enviar_por_telegram("Título:\n\nCablear tablero norte", [boton],
                                  bloque="Cablear tablero norte")

    assert cuerpo["reply_markup"]["inline_keyboard"] == [[
        {"text": ETIQUETA_COPIAR, "copy_text": {"text": "Cablear tablero norte"}}]]


def test_un_boton_de_copiar_y_uno_de_callback_conviven():
    botones = [Boton(ETIQUETA_COPIAR, "", copiar="abc"), Boton("Otra", "p:tok")]

    cuerpo = _enviar_por_telegram("x\n\nabc", botones, bloque="abc")

    assert cuerpo["reply_markup"]["inline_keyboard"] == [
        [{"text": ETIQUETA_COPIAR, "copy_text": {"text": "abc"}}],
        [{"text": "Otra", "callback_data": "p:tok"}]]


@pytest.mark.parametrize("largo, entra", [(COPY_TEXT_LIMIT, True),
                                          (COPY_TEXT_LIMIT + 1, False)])
def test_el_boton_de_copiar_respeta_el_limite_de_256(largo, entra):
    boton = Boton(ETIQUETA_COPIAR, "", copiar="a" * largo)

    if entra:
        assert prepare_buttons([boton]) == [(ETIQUETA_COPIAR, "", "a" * largo)]
    else:
        with pytest.raises(PayloadValidationError):
            prepare_buttons([boton])


def test_el_limite_de_copiar_se_mide_en_unidades_utf16():
    # 129 emojis son 129 caracteres pero 258 unidades: no entra en el botón.
    with pytest.raises(PayloadValidationError):
        prepare_buttons([Boton(ETIQUETA_COPIAR, "", copiar="🔧" * 129)])
    assert prepare_buttons([Boton(ETIQUETA_COPIAR, "", copiar="🔧" * 128)])


def test_un_boton_de_copiar_vacio_no_sale():
    with pytest.raises(PayloadValidationError):
        prepare_buttons([Boton(ETIQUETA_COPIAR, "", copiar="")])


def test_un_boton_de_callback_sigue_necesitando_su_callback():
    with pytest.raises(PayloadValidationError):
        prepare_buttons([Boton("Otra", "")])


# ------------------------------------------------------------ cola y salida

def _encolar(cur, ws, texto, bloque, **kw):
    return enqueue_outbox(
        cur, workspace_id=ws, chat_id=500, text=texto, scheduled_for=AHORA,
        dedupe_key=kw.pop("clave", "bc1"), is_response=True,
        bloque_copiable=bloque, **kw)


def test_el_mensaje_con_bloque_sale_con_su_bloque_y_su_boton_de_copiar(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, "Título actual:\n\nCablear tablero norte",
                 "Cablear tablero norte")
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), AHORA)

    enviado = transporte.enviados[0]
    assert enviado.bloque == "Cablear tablero norte"
    assert enviado.botones == [Boton(ETIQUETA_COPIAR, "", "Cablear tablero norte")]


@pytest.mark.parametrize("largo, con_boton", [(COPY_TEXT_LIMIT, True),
                                              (COPY_TEXT_LIMIT + 1, False)])
def test_el_boton_de_copiar_aparece_hasta_256_y_el_bloque_siempre(
        largo, con_boton, corework, conn):
    ws = corework.workspace_id
    bloque = "b" * largo
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, f"Descripción actual:\n\n{bloque}", bloque)
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), AHORA)

    enviado = transporte.enviados[0]
    assert enviado.bloque == bloque                   # el bloque sale siempre
    assert bool(enviado.botones) is con_boton         # el botón, sólo si entra


def test_un_mensaje_sin_bloque_sale_como_siempre(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, "buen día", None)
        transporte = TransporteDePrueba()
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), AHORA)

    assert transporte.enviados[0].bloque is None
    assert transporte.enviados[0].botones == []


def test_encolar_un_bloque_que_no_es_el_final_del_texto_falla(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        with pytest.raises(PayloadValidationError):
            _encolar(cur, ws, "Título: A y algo más", "A")


def test_encolar_un_bloque_no_se_parte_en_varios_mensajes(corework, conn):
    ws = corework.workspace_id
    largo = "palabra " * 700                      # más de 4096 unidades
    with espacio(conn, ws) as cur:
        with pytest.raises(PayloadValidationError):
            _encolar(cur, ws, f"Descripción:\n\n{largo.strip()}", largo.strip(),
                     allow_split=True)


def test_el_saludo_diario_no_mueve_el_bloque(corework, conn):
    """El transporte ubica el bloque en el texto final: si el despachador le
    antepone el saludo, la entidad sigue sobre el bloque."""
    ws = corework.workspace_id
    texto = "Título actual:\n\nCablear tablero norte"
    with admin(conn) as cur:
        cur.execute(
            """select m.id from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and u.nombre = %s""",
            (ws, "Marcos Tarquini"))
        persona = str(cur.fetchone()["id"])
        cur.execute("delete from greeting_state where membership_id = %s", (persona,))
    with espacio(conn, ws) as cur:
        _encolar(cur, ws, texto, "Cablear tablero norte",
                 recipient_membership_id=persona)
        http = _Http()
        transporte = TransporteTelegram("unused", cliente=http)
        despachar(cur, ws, transporte, Calendario.desde_base(cur, ws), AHORA)

    cuerpo = http.cuerpos[0]
    assert cuerpo["text"] != texto and cuerpo["text"].endswith(texto)   # con saludo
    entidad = cuerpo["entities"][0]
    unidades = cuerpo["text"].encode("utf-16-le")
    trozo = unidades[entidad["offset"] * 2:(entidad["offset"] + entidad["length"]) * 2]
    assert trozo.decode("utf-16-le") == "Cablear tablero norte"


# ------------------------------------------------- arranque: la migración 0020

def test_verificar_migraciones_sin_bloque_copiable_nombra_la_0020():
    class _Cursor:
        def __init__(self, respuestas):
            self._respuestas = list(respuestas)
            self._actual = None

        def execute(self, *a, **k):
            self._actual = self._respuestas.pop(0)

        def fetchone(self):
            return self._actual

    cur = _Cursor([{"ok": True}, {"ok": True}, {"ok": False}])
    assert saludo.verificar_migraciones(cur) == "0020_bloque_copiable.sql"


def test_verificar_migraciones_al_dia_devuelve_none(corework, conn):
    with admin(conn) as cur:
        assert saludo.verificar_migraciones(cur) is None


# ----------------------- la base: Modificar nunca convierte el borrador (0020)

def test_el_token_de_modificar_no_llega_a_convertir_el_borrador(
        corework, conn, authority_conn):
    """`confirmar_borrador_tarea` sólo distingue `false` (cancelar) de todo lo
    demás: un token cuya opción valga "modificar" que llegara hasta ella
    convertiría el borrador. La envoltura `resolver_ingreso_borrador` lo trata
    como inexistente (migración 0020); el botón Confirmar sigue funcionando."""
    from prisma import pendientes as P
    from prisma.db import autoridad
    from tests.test_task_drafts import (_confirmar, _crear_preview, _telegram,
                                        _token)

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        preview = _crear_preview(cur, ws)
        pid = preview["pending_action_id"]
        modificar = P._crear_opcion(cur, ws, pid, "Modificar", "modificar", 2).token
        confirmar = _token(cur, pid)
        aprobador = _telegram(cur, "Marcos Tarquini")
    conn.commit()

    with autoridad(authority_conn) as cur:
        assert P.resolver_borrador(cur, ws, modificar, aprobador, aprobador) is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "esperando"

    resuelta = _confirmar(authority_conn, ws, confirmar, aprobador)
    assert resuelta is not None and resuelta.task_id


def test_el_token_de_enviar_no_llega_a_convertir_el_borrador(
        corework, conn, authority_conn):
    """Enviar a aprobación (T9-R1c-4) es del gateway, que lo intercepta: nunca
    llega a la autoridad. Si llegara, `confirmar_borrador_tarea` (que sólo
    distingue `false` de todo lo demás) convertiría el borrador. La envoltura
    `resolver_ingreso_borrador` lo trata como inexistente, igual que a Modificar
    (migración 0023): defensa en profundidad."""
    from prisma import pendientes as P
    from prisma.db import autoridad
    from tests.test_task_drafts import _crear_preview, _telegram

    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        preview = _crear_preview(cur, ws)
        pid = preview["pending_action_id"]
        enviar = P._crear_opcion(cur, ws, pid, "Enviar a aprobación", "enviar", 2).token
        aprobador = _telegram(cur, "Marcos Tarquini")
    conn.commit()

    with autoridad(authority_conn) as cur:
        assert P.resolver_borrador(cur, ws, enviar, aprobador, aprobador) is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 0
        cur.execute("select estado from pending_action where id = %s", (pid,))
        assert cur.fetchone()["estado"] == "esperando"
