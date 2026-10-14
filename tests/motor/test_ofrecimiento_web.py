"""El ofrecimiento de la web, una sola vez (decisión 2 del usuario del 2026-10-12; ADR 0022,
decisión 4; conversación 50, pasos 1 a 3 y 7; tarea A-4 de `odd/tasks/acceso-por-chat.md`).

A cada integrante activo que nunca entró a la web ni se le ofreció, Leda le ofrece la entrada al
final de su próxima respuesta a lo que escribió: un segundo hecho (`ofrecimiento`) y la marca del
enlace de entrada (`es_ofrecimiento`), que el despachador emite al mandar. El ofrecimiento se
reserva al armar el turno (`ofrecimiento_web.reservado_en`, decisión técnica 1), queda ofrecido al
mandar (`ofrecido_en`) y se libera si el envío falla sin reintento. No va en un toque (decisión
técnica 4), ni con el enlace de una tarea (espera al turno siguiente, decisión técnica 2), ni en la
respuesta a "perdí el celular", ni en lo que Leda manda por su cuenta (eso no pasa por el turno).
También va en la bienvenida al conectarse.

Y el corte del acceso (`web_app.cortar_sesiones`) anula los enlaces de entrada que todavía no
salieron: el despachador no emite uno después del corte (la advertencia de la revisión de la A-3).
"""

from __future__ import annotations

import dataclasses
import re
import secrets

import pytest

from leda import config as config_mod
from leda import web_app
from leda.calendario import Calendario
from leda.db import admin, espacio, sin_espacio
from leda.despachador import MAX_INTENTOS, TransporteDePrueba, despachar
from leda.motor import hechos as hechos_mod
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import (AHORA, TelegramFalso, mensaje_de_telegram,
                                   todos, toca, uno)

DIRECCION = "https://leda.invalid/"
ENLACE_WEB = re.compile(r"\nhttps://leda\.invalid/app/entrar/([A-Za-z0-9_-]{43})$")

OFRECIMIENTO = {"ofrecimiento": "acceso_a_la_web", "lleva_el_boton": "Ver mis tareas"}
MINI_APP = "https://leda.invalid/app/e/prueba/"


def _boton_de_la_web(mensaje):
    """El botón que abre la web como Mini App (ADR 0024), o `None`."""
    return next((b for b in mensaje.botones if b.web_app), None)


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))


def _membresia(mundo, nombre: str = "Marcos") -> str:
    return mundo["personas"][nombre]["membership_id"]


def _emitir(conn, mundo, nombre: str = "Marcos") -> str:
    """Un enlace emitido antes, como lo emite la consola."""
    with espacio(conn, mundo["id"]) as cur:
        token = web_app.emitir_enlace(cur, _membresia(mundo, nombre))
    conn.commit()
    return token


def _canjear(conn, token: str) -> str | None:
    """El botón "Entrar" de la página del enlace."""
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (web_app._hash(token), web_app._hash(secrets.token_urlsafe(32))))
        sesion = cur.fetchone()["id"]
    conn.commit()
    return sesion


def _sin_ofrecer(conn, mundo, nombre: str = "Marcos") -> None:
    """La persona nunca recibió el ofrecimiento: el mundo de las pruebas da por ofrecido a todos
    (como el saludo del día), así que se le borra su fila."""
    with admin(conn) as cur:
        cur.execute("delete from ofrecimiento_web where membership_id = %s",
                    (_membresia(mundo, nombre),))
    conn.commit()


@pytest.fixture
def nunca(conn, mundo, direccion):
    """Marcos nunca entró a la web ni se le ofreció, y la página está disponible."""
    _sin_ofrecer(conn, mundo)


def _dice(conn, escribe, *jugadas: Jugada, nombre: str = "Marcos", texto: str = "-",
          entrante: str | None = None):
    quien, nuevo = escribe(nombre, texto)
    ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
    resultado = procesar_turno(conn, quien, entrante or nuevo, ia, RelojFijo(AHORA))
    conn.commit()
    assert resultado.error is None
    return resultado.hechos, ia


def _ofrecimiento(conn, mundo, nombre: str = "Marcos") -> dict | None:
    filas = todos(conn, """select reservado_en, ofrecido_en from ofrecimiento_web
                            where membership_id = %s""", _membresia(mundo, nombre))
    return filas[0] if filas else None


def _marcas(conn) -> list[dict]:
    return todos(conn, """select w.membership_id::text persona, w.es_ofrecimiento, o.estado::text
                            from message_outbox_entrada_web w
                            join message_outbox o on o.id = w.outbox_id
                           order by o.programado_para, o.cuerpo, o.id""")


def _despachar(conn, mundo, transporte: TransporteDePrueba | None = None) -> TransporteDePrueba:
    transporte = transporte or TransporteDePrueba()
    with espacio(conn, mundo["id"]) as cur:
        despachar(cur, mundo["id"], transporte, Calendario.desde_base(cur, mundo["id"]), AHORA)
    conn.commit()
    return transporte


def _telegram(mundo, nombre: str = "Marcos") -> int:
    return mundo["personas"][nombre]["telegram"]


# --- El hecho ---------------------------------------------------------------------------------

def test_cada_clave_y_codigo_del_ofrecimiento_tiene_significado():
    for codigo in ("ofrecimiento", "acceso_a_la_web"):
        assert hechos_mod.significado(codigo), codigo
    assert not hechos_mod.sin_significado(OFRECIMIENTO)


# --- Una sola vez, al final de una respuesta a lo que escribió ---------------------------------

def test_la_primera_respuesta_a_lo_que_escribe_lleva_el_ofrecimiento_al_final(conn, mundo,
                                                                              escribe, nunca):
    hechos, ia = _dice(conn, escribe, Jugada("consultar_pendientes", {}))
    assert [h.get("jugada") for h in hechos] == ["consultar_pendientes", None]
    assert hechos[-1] == OFRECIMIENTO
    # La IA lo recibe para redactar, sin ninguna dirección.
    pedido = ia.pedidos_de_redaccion[-1]
    assert "http" not in repr(pedido) and "leda.invalid" not in repr(pedido)
    # Reservado al armar el turno, con la marca del ofrecimiento.
    reserva = _ofrecimiento(conn, mundo)
    assert reserva["reservado_en"] is not None and reserva["ofrecido_en"] is None
    assert _marcas(conn) == [{"persona": _membresia(mundo), "es_ofrecimiento": True,
                              "estado": "listo"}]
    [mensaje] = _despachar(conn, mundo).enviados
    boton = _boton_de_la_web(mensaje)
    assert (boton.etiqueta, boton.web_app) == ("Ver mis tareas", MINI_APP)
    assert not ENLACE_WEB.search(mensaje.texto)
    assert _ofrecimiento(conn, mundo)["ofrecido_en"] is not None
    assert todos(conn, "select 1 from enlace_de_entrada") == []


def test_no_se_ofrece_dos_veces(conn, mundo, escribe, nunca):
    _dice(conn, escribe, Jugada("consultar_pendientes", {}))
    # Aunque todavía no salió: la reserva alcanza.
    hechos, _ = _dice(conn, escribe, Jugada("consultar_pendientes", {}))
    assert all("ofrecimiento" not in h for h in hechos)
    _despachar(conn, mundo)
    hechos, _ = _dice(conn, escribe)
    assert hechos == []
    assert [m["es_ofrecimiento"] for m in _marcas(conn)] == [True]


def test_ni_aunque_la_misma_respuesta_se_despache_dos_veces(conn, mundo, escribe, nunca):
    """El mismo mensaje que vuelve a llegar no tiene otro turno, y una segunda pasada del
    despachador no lo vuelve a mandar: un solo botón."""
    quien, entrante = escribe("Marcos", "que tengo pendiente?")
    for _ in range(2):
        procesar_turno(conn, quien, entrante,
                       IAGuionada(jugadas=[[Jugada("consultar_pendientes", {})]],
                                  redacciones=["Listo."]), RelojFijo(AHORA))
        conn.commit()
    assert len(_despachar(conn, mundo).enviados) == 1
    assert _despachar(conn, mundo).enviados == []
    assert len(_marcas(conn)) == 1


def test_a_quien_ya_entro_a_la_web_no_se_le_ofrece(conn, mundo, escribe, nunca):
    assert _canjear(conn, _emitir(conn, mundo)) is not None
    hechos, _ = _dice(conn, escribe, Jugada("consultar_pendientes", {}))
    assert all("ofrecimiento" not in h for h in hechos)
    assert _marcas(conn) == [] and _ofrecimiento(conn, mundo) is None


def test_sin_la_direccion_publica_no_se_ofrece(conn, mundo, escribe):
    _sin_ofrecer(conn, mundo)
    hechos, _ = _dice(conn, escribe, Jugada("consultar_pendientes", {}))
    assert all("ofrecimiento" not in h for h in hechos)
    assert _ofrecimiento(conn, mundo) is None


def test_un_toque_no_lo_lleva_y_sale_en_el_proximo_mensaje_escrito(conn, mundo, duda,
                                                                    escribe, direccion):
    _sin_ofrecer(conn, mundo)
    resultado, _ = toca(conn, mundo, duda["O1"])
    assert resultado.error is None
    assert all("ofrecimiento" not in h for h in resultado.hechos)
    assert _marcas(conn) == [] and _ofrecimiento(conn, mundo) is None
    hechos, _ = _dice(conn, escribe)
    assert hechos == [OFRECIMIENTO]


def test_con_el_enlace_de_una_tarea_espera_al_turno_siguiente(conn, mundo, escribe, nunca):
    """Un enlace por mensaje (decisión técnica 2)."""
    hechos, _ = _dice(conn, escribe, Jugada("pedir_enlace", {"tarea": "T1"}))
    assert all("ofrecimiento" not in h for h in hechos)
    assert _ofrecimiento(conn, mundo) is None
    hechos, _ = _dice(conn, escribe)
    assert hechos == [OFRECIMIENTO]


def test_quien_pide_el_enlace_ya_lo_recibio_y_no_se_le_ofrece_despues(conn, mundo, escribe,
                                                                       nunca):
    """Ya tiene el botón: el ofrecimiento sería repetirlo."""
    hechos, _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    assert [h["resultado"] for h in hechos] == ["boton_para_abrir_la_web"]
    # Mientras su botón no salió, tampoco.
    hechos, _ = _dice(conn, escribe)
    assert hechos == []
    _despachar(conn, mundo)
    assert _ofrecimiento(conn, mundo)["ofrecido_en"] is not None
    hechos, _ = _dice(conn, escribe)
    assert hechos == []


def test_no_en_la_respuesta_a_perdi_el_celular(conn, mundo, escribe, nunca):
    hechos, _ = _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert [h.get("jugada") for h in hechos] == ["perdi_el_celular"]
    assert _marcas(conn) == [] and _ofrecimiento(conn, mundo) is None


def test_si_la_ia_no_redacta_no_hay_ofrecimiento_ni_reserva(conn, mundo, escribe, nunca):
    """Sale el texto fijo: lo del turno se deshizo, también la reserva."""
    quien, entrante = escribe("Marcos", "-")
    resultado = procesar_turno(
        conn, quien, entrante,
        IAGuionada(jugadas=[[Jugada("consultar_pendientes", {})]],
                   redacciones=[RuntimeError("caída"), RuntimeError("caída")]),
        RelojFijo(AHORA))
    conn.commit()
    assert resultado.error is not None
    assert _marcas(conn) == [] and _ofrecimiento(conn, mundo) is None
    hechos, _ = _dice(conn, escribe)
    assert hechos == [OFRECIMIENTO]


# --- El envío ---------------------------------------------------------------------------------

def test_un_envio_que_se_reintenta_guarda_la_reserva(conn, mundo, escribe, nunca):
    _dice(conn, escribe)
    _despachar(conn, mundo, TransporteDePrueba(falla_en={_telegram(mundo)}))
    reserva = _ofrecimiento(conn, mundo)
    assert reserva["reservado_en"] is not None and reserva["ofrecido_en"] is None
    hechos, _ = _dice(conn, escribe)
    assert hechos == []


def test_un_envio_que_falla_sin_reintento_libera_la_reserva(conn, mundo, escribe, nunca):
    _dice(conn, escribe)
    with admin(conn) as cur:
        cur.execute("update message_outbox set intentos = %s", (MAX_INTENTOS - 1,))
    conn.commit()
    _despachar(conn, mundo, TransporteDePrueba(falla_en={_telegram(mundo)}))
    assert [m["estado"] for m in _marcas(conn)] == ["fallido"]
    assert _ofrecimiento(conn, mundo) is None
    hechos, _ = _dice(conn, escribe)
    assert hechos == [OFRECIMIENTO]


# --- El corte anula lo que todavía no salió ----------------------------------------------------

def test_perdi_el_celular_anula_un_enlace_que_todavia_no_salio(conn, mundo, escribe, direccion):
    """La advertencia de la revisión de la A-3: la respuesta anterior, con el enlace, sigue en la
    salida (por ejemplo, esperando su reintento); después del corte no sale, ni se emite su
    enlace, y queda el incidente."""
    _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert [m["estado"] for m in _marcas(conn)] == ["descartado"]
    enviados = _despachar(conn, mundo).enviados
    assert len(enviados) == 1 and not ENLACE_WEB.search(enviados[0].texto)
    assert todos(conn, "select 1 from enlace_de_entrada") == []
    [incidente] = todos(conn, """select etapa, severidad::text, referencia_tipo from incident
                                  where etapa = 'enlace_de_entrada_web'""")
    assert incidente["referencia_tipo"] == "message_outbox"


def test_el_corte_libera_un_ofrecimiento_que_no_salio(conn, mundo, escribe, nunca):
    _dice(conn, escribe)
    _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert [m["estado"] for m in _marcas(conn)] == ["descartado"]
    assert _ofrecimiento(conn, mundo) is None


def test_pedir_otro_enlace_en_el_mismo_mensaje_del_corte_no_lo_manda(conn, mundo, escribe,
                                                                      direccion):
    """En el mismo mensaje, en cualquier orden: después del corte no sale ningún enlace."""
    for orden in ((Jugada("pedir_acceso_web", {}), Jugada("perdi_el_celular", {})),
                  (Jugada("perdi_el_celular", {}), Jugada("pedir_acceso_web", {}))):
        hechos, _ = _dice(conn, escribe, *orden)
        web = next(h for h in hechos if h["jugada"] == "pedir_acceso_web")
        assert "lleva_el_enlace_de_entrada_a_la_web" not in web
        assert web["motivo"] == "corta_el_acceso_en_este_mensaje"
    assert _marcas(conn) == []
    assert hechos_mod.significado("corta_el_acceso_en_este_mensaje")


def test_el_corte_por_la_consola_tambien_anula_lo_que_no_salio(conn, mundo, escribe, direccion):
    from leda import web_app

    _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    with espacio(conn, mundo["id"]) as cur:
        web_app.cortar_sesiones(cur, _membresia(mundo))
    conn.commit()
    assert [m["estado"] for m in _marcas(conn)] == ["descartado"]
    assert _despachar(conn, mundo).enviados == []


def test_el_corte_no_toca_lo_que_no_lleva_el_enlace_ni_lo_de_otra_persona(conn, mundo, escribe,
                                                                         direccion):
    _dice(conn, escribe, Jugada("pedir_acceso_web", {}), nombre="Ismael")
    _dice(conn, escribe, Jugada("consultar_pendientes", {}))
    _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert [m["estado"] for m in _marcas(conn)] == ["listo"]
    assert uno(conn, """select count(*) n from message_outbox
                         where estado = 'descartado'""")["n"] == 0


# --- Lo que Leda manda por su cuenta no lo lleva -----------------------------------------------

def test_un_aviso_que_leda_manda_por_su_cuenta_no_lo_lleva(conn, mundo, dias, direccion):
    """El aviso previo de la escalera (la 50, paso 7): no pasa por el turno."""
    from tests.motor.ayudantes import octubre

    _sin_ofrecer(conn, mundo)
    [pedido] = dias.ciclo(octubre(6, 10))
    assert "ofrecimiento" not in repr(pedido)
    assert _marcas(conn) == [] and _ofrecimiento(conn, mundo) is None


# --- La bienvenida ----------------------------------------------------------------------------

def _bienvenida(conn, mundo, update_id: int = 901):
    """Marcos escribe /start al bot del equipo: el escuchador le da la bienvenida."""
    from leda.motor.escucha import BotTelegram, Escucha

    telegram, telegram_admin = TelegramFalso(), TelegramFalso()
    salida = TransporteDePrueba()
    escucha = Escucha(conn, mundo["id"], IAGuionada(), RelojFijo(AHORA),
                      bot=BotTelegram("token-falso", telegram.cliente()), transporte=salida,
                      bot_admin=BotTelegram("token-admin-falso", telegram_admin.cliente()),
                      transporte_admin=TransporteDePrueba(), imprimir=lambda *_: None)
    escucha.preparar()
    telegram.lotes = [[mensaje_de_telegram(update_id, "/start", _telegram(mundo), update_id,
                                           "private")]]
    escucha.una_vuelta(espera=0)
    return salida.enviados


def test_la_bienvenida_de_quien_nunca_entro_lleva_el_ofrecimiento(conn, mundo, direccion):
    _sin_ofrecer(conn, mundo)
    [bienvenida] = _bienvenida(conn, mundo)
    assert bienvenida.texto.startswith("Listo, Marcos.")
    boton = _boton_de_la_web(bienvenida)
    assert (boton.etiqueta, boton.web_app) == ("Ver mis tareas", MINI_APP)
    assert not ENLACE_WEB.search(bienvenida.texto)
    ofrecimiento = bienvenida.texto.rsplit("\n\n", 1)[-1]
    assert "web" in ofrecimiento and "«Ver mis tareas»" in ofrecimiento
    # Leda nunca sugiere pedir un enlace (ADR 0024, decisión 1).
    assert "enlace" not in ofrecimiento and "pedime" not in ofrecimiento
    assert _ofrecimiento(conn, mundo)["ofrecido_en"] is not None
    assert [m["es_ofrecimiento"] for m in _marcas(conn)] == [True]


def test_la_bienvenida_no_lo_repite(conn, mundo, direccion):
    _sin_ofrecer(conn, mundo)
    _bienvenida(conn, mundo, 901)
    [otra] = _bienvenida(conn, mundo, 902)
    assert not ENLACE_WEB.search(otra.texto) and "web" not in otra.texto
    assert len(_marcas(conn)) == 1


def test_la_bienvenida_de_quien_ya_entro_no_lo_lleva(conn, mundo, direccion):
    _sin_ofrecer(conn, mundo)
    assert _canjear(conn, _emitir(conn, mundo)) is not None
    [bienvenida] = _bienvenida(conn, mundo)
    assert not ENLACE_WEB.search(bienvenida.texto) and "web" not in bienvenida.texto
    assert _ofrecimiento(conn, mundo) is None


def test_la_bienvenida_sin_la_direccion_publica_no_lo_lleva(conn, mundo):
    _sin_ofrecer(conn, mundo)
    [bienvenida] = _bienvenida(conn, mundo)
    assert "web" not in bienvenida.texto and _marcas(conn) == []
