"""La entrada a la web por chat: las jugadas `pedir_acceso_web` y `perdi_el_celular` (ADR 0024,
decisiones 1, 2 y 4, que enmiendan la decisión 4 del ADR 0022; decisión 3 del usuario del
2026-10-12; conversación 50).

- `pedir_acceso_web`: la respuesta no lleva ningún botón (decisión del usuario del 2026-10-14,
  noche, MA-5): los hechos dicen que la persona abre su espacio con el botón fijo del menú del
  chat, "Mi espacio", y ya no se le ofrece la web después. No se emite ningún enlace; la IA nunca
  ve ni escribe una dirección. Pedida la dirección para la computadora, la dirección sola (no da
  acceso: ahí se entra con el QR). Los botones de un destino ("Cargar la tarea", "Crear el
  objetivo") siguen siendo uno por mensaje (decisión técnica 2).
- `perdi_el_celular`: corta enseguida, sin confirmación, todas las sesiones de la persona y su
  enlace sin usar, con el motivo `perdio_el_celular` y la persona como actor; el corte queda en la
  auditoría también sin sesiones (decisión técnica 3).
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
from leda.despachador import TransporteDePrueba, despachar
from leda.motor import hechos as hechos_mod
from leda.motor.avisos import LLEVA_EL_ENLACE
from leda.motor.fichas import FICHAS, JUGADAS, lo_que_puede_hacer
from leda.motor.ia import IAGuionada, Jugada
from leda.motor.tiempo import RelojFijo
from leda.motor.turno import procesar_turno

from tests.motor.ayudantes import AHORA, todos

DIRECCION = "https://leda.invalid/"
# Los botones abren el lanzador (MA-2); la dirección para la computadora es la de la web.
MINI_APP = "https://leda.invalid/app/abrir/e/prueba/"
WEB = "https://leda.invalid/app/e/prueba/"

MENU = {"jugada": "pedir_acceso_web", "resultado": "se_abre_con_el_boton_del_menu",
        "boton_del_menu": "Mi espacio"}


@pytest.fixture
def direccion(monkeypatch):
    monkeypatch.setattr(config_mod, "config",
                        dataclasses.replace(config_mod.config, base_url=DIRECCION))


def _dice(conn, escribe, *jugadas: Jugada, nombre: str = "Marcos", texto: str = "-"):
    """Un mensaje de `nombre` con las jugadas que elige la IA guionada: sus hechos y lo que la
    IA recibió para redactar."""
    quien, entrante = escribe(nombre, texto)
    ia = IAGuionada(jugadas=[list(jugadas)], redacciones=["Listo."])
    resultado = procesar_turno(conn, quien, entrante, ia, RelojFijo(AHORA))
    conn.commit()
    assert resultado.error is None
    return resultado.hechos, ia.pedidos_de_redaccion[-1]


def _membresia(mundo, nombre: str = "Marcos") -> str:
    return mundo["personas"][nombre]["membership_id"]


def _emitir(conn, mundo, nombre: str = "Marcos") -> str:
    """Un enlace emitido antes, como lo emite la consola."""
    with espacio(conn, mundo["id"]) as cur:
        token = web_app.emitir_enlace(cur, _membresia(mundo, nombre))
    conn.commit()
    return token


def _canjear(conn, token: str) -> str | None:
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (web_app._hash(token), web_app._hash(secrets.token_urlsafe(32))))
        sesion = cur.fetchone()["id"]
    conn.commit()
    return sesion


def _marcas(conn) -> list[dict]:
    return todos(conn, """select w.membership_id::text persona, w.es_ofrecimiento, w.destino
                            from message_outbox_entrada_web w
                            join message_outbox o on o.id = w.outbox_id
                           where o.es_respuesta""")


def _despachar(conn, mundo) -> TransporteDePrueba:
    transporte = TransporteDePrueba()
    with espacio(conn, mundo["id"]) as cur:
        despachar(cur, mundo["id"], transporte, Calendario.desde_base(cur, mundo["id"]), AHORA)
    conn.commit()
    return transporte


def _auditoria(conn, accion: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select * from audit_log where accion = %s order by at, id", (accion,))
        filas = cur.fetchall()
    conn.commit()
    return filas


# --- Las fichas -----------------------------------------------------------------------------

def test_las_dos_jugadas_son_de_la_lista_cerrada_y_sin_tarea():
    for nombre in ("pedir_acceso_web", "perdi_el_celular"):
        ficha = FICHAS[nombre]
        assert nombre in JUGADAS
        assert ficha.se_ofrece and not ficha.del_responsable
        assert ficha.necesita == ()
        assert ficha.es and ficha.para_que in lo_que_puede_hacer(JUGADAS)
        # La redacción las recibe por lo que hacen.
        assert hechos_mod.es_un_concepto_de_la_cocina(nombre)
        assert nombre in hechos_mod.PARA_LA_REDACCION
    assert FICHAS["pedir_acceso_web"].opcional == ("para_la_compu",)
    assert FICHAS["perdi_el_celular"].opcional == ()


def test_lo_que_es_cada_jugada_no_trae_frases_de_ejemplo():
    """Describe la jugada, nunca un caso ni una frase (la regla del mozo): sin comillas."""
    for nombre in ("pedir_acceso_web", "perdi_el_celular"):
        assert not re.search(r"[\"“”«»]", FICHAS[nombre].es), nombre


def test_cada_clave_y_codigo_de_sus_hechos_tiene_significado():
    for codigo in ("se_abre_con_el_boton_del_menu", "boton_del_menu", "lleva_el_boton",
                   "direccion_para_la_compu",
                   "acceso_cortado", "sesiones_cortadas",
                   "recuerda_cerrar_telegram_en_ese_celular", "vuelve_a_entrar_desde_telegram",
                   "ya_lleva_otro_enlace"):
        assert hechos_mod.significado(codigo), codigo
    # Leda nunca sugiere pedir un enlace (ADR 0024, decisión 1).
    for codigo, texto in hechos_mod.SIGNIFICADOS.items():
        assert "pedir otro enlace" not in texto and "le pide otro" not in texto, codigo
    # El significado dice que el botón lo pone el código: la IA no escribe ninguna dirección.
    assert "la IA no escribe ninguna" in hechos_mod.significado("lleva_el_boton")


# --- Pedir el acceso ------------------------------------------------------------------------

def test_pedir_el_acceso_dice_el_boton_del_menu_y_el_mensaje_no_lleva_ninguno(conn, mundo,
                                                                              escribe, direccion):
    """MA-5 (decisión del usuario, 2026-10-14, noche): a pedido, ningún botón en el mensaje; la
    persona abre su espacio con el botón fijo del menú, el mismo texto que fija `menu_del_bot`."""
    from leda.menu_del_bot import TEXTO_DEL_EQUIPO

    [hecho], pedido = _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    assert hecho == MENU and hecho["boton_del_menu"] == TEXTO_DEL_EQUIPO
    assert _marcas(conn) == []
    # La IA nunca ve una dirección ni un nombre de la base.
    assert "http" not in repr(pedido) and "leda.invalid" not in repr(pedido)
    [mensaje] = _despachar(conn, mundo).enviados
    assert mensaje.texto == "Listo."
    assert mensaje.botones == []
    # Ningún enlace de entrada se emitió.
    assert todos(conn, "select 1 from enlace_de_entrada") == []


def test_a_direccion_tambien_le_dice_el_boton_del_menu(conn, mundo, escribe, direccion):
    [hecho], _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}), nombre="Ismael")
    assert hecho == MENU
    [mensaje] = _despachar(conn, mundo).enviados
    assert mensaje.botones == []


def test_la_direccion_para_la_compu_va_sola_y_sin_boton(conn, mundo, escribe, direccion):
    [hecho], pedido = _dice(conn, escribe, Jugada("pedir_acceso_web", {"para_la_compu": True}))
    assert hecho == {"jugada": "pedir_acceso_web", "resultado": "direccion_para_la_compu",
                     "direccion_para_la_compu": WEB}
    assert _marcas(conn) == []
    [mensaje] = _despachar(conn, mundo).enviados
    assert mensaje.botones == []


def test_sin_la_direccion_publica_no_se_promete_ningun_boton(conn, mundo, escribe):
    [hecho], _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    assert hecho == {"jugada": "pedir_acceso_web", "resultado": "no_se_puede",
                     "motivo": "la_pagina_no_esta_disponible"}
    assert _marcas(conn) == []


def test_pedirlo_dos_veces_en_un_mensaje_no_lleva_ningun_boton(conn, mundo, escribe, direccion):
    hechos, _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}),
                      Jugada("pedir_acceso_web", {}))
    assert hechos == [MENU, MENU]
    assert _marcas(conn) == []


@pytest.mark.parametrize("primero", ["pedir_enlace", "pedir_acceso_web"])
def test_el_boton_del_menu_no_le_quita_el_enlace_a_una_tarea(conn, mundo, escribe, direccion,
                                                              primero):
    """Sin botón en el mensaje, el enlace de la tarea sale en cualquier orden."""
    jugadas = [Jugada("pedir_enlace", {"tarea": "T1"}), Jugada("pedir_acceso_web", {})]
    hechos, _ = _dice(conn, escribe, *(jugadas if primero == "pedir_enlace" else jugadas[::-1]))
    tarea = next(h for h in hechos if h["jugada"] == "pedir_enlace")
    web = next(h for h in hechos if h["jugada"] == "pedir_acceso_web")
    assert tarea[LLEVA_EL_ENLACE] is True and web == MENU
    assert _marcas(conn) == []
    assert len(todos(conn, "select 1 from message_outbox_enlace")) == 1
    assert "botón" in hechos_mod.significado("ya_lleva_el_enlace_de_otra_tarea")


def test_si_la_ia_no_redacta_no_sale_ningun_boton(conn, mundo, escribe, direccion):
    """El texto fijo no lleva lo que hicieron las jugadas: se deshizo."""
    from leda.motor.ia import IAGuionada as Guionada

    class NoRedacta(Guionada):
        def redactar(self, pedido):
            raise RuntimeError("caída")

    quien, entrante = escribe("Marcos", "-")
    procesar_turno(conn, quien, entrante,
                   NoRedacta(jugadas=[[Jugada("pedir_crear", {"que_quiere_crear": "tarea"})]] * 2),
                   RelojFijo(AHORA))
    conn.commit()
    assert _marcas(conn) == []


# --- Perdí el celular -----------------------------------------------------------------------

def test_perdi_el_celular_corta_enseguida_todas_sus_sesiones_y_su_enlace(conn, mundo, escribe):
    celular = _canjear(conn, _emitir(conn, mundo))
    computadora = _canjear(conn, _emitir(conn, mundo))
    pendiente = _emitir(conn, mundo)
    de_ismael = _canjear(conn, _emitir(conn, mundo, "Ismael"))
    assert celular and computadora and de_ismael
    [hecho], pedido = _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert hecho == {"jugada": "perdi_el_celular", "resultado": "acceso_cortado",
                     "sesiones_cortadas": 2, "recuerda_cerrar_telegram_en_ese_celular": True,
                     "vuelve_a_entrar_desde_telegram": True}
    # Sin confirmación: ninguna pregunta ni botón.
    assert todos(conn, "select 1 from conversation_question") == []
    assert _canjear(conn, pendiente) is None
    abiertas = todos(conn, """select membership_id::text persona from sesion_web
                               where cortada_en is null""")
    assert abiertas == [{"persona": _membresia(mundo, "Ismael")}]
    assert "perdio_el_celular" not in repr(pedido)


def test_el_corte_queda_en_la_auditoria_con_su_motivo_y_la_persona(conn, mundo, escribe):
    _emitir(conn, mundo)                                  # sin sesiones, un enlace sin usar
    [hecho], _ = _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert hecho["sesiones_cortadas"] == 0
    [corte] = _auditoria(conn, "cortar_acceso_web")
    assert corte["detalle"] == {"motivo": "perdio_el_celular", "sesiones_cortadas": 0,
                                "enlace_anulado": True}
    assert corte["actor_kind"] == "persona"
    assert str(corte["actor_app_user_id"]) == mundo["personas"]["Marcos"]["app_user_id"]
    assert corte["pack_hash"] == "hash-prueba" and corte["nucleo_hash"]


def test_sin_nada_que_cortar_igual_corta_y_lo_dice(conn, mundo, escribe):
    [hecho], _ = _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert (hecho["resultado"], hecho["sesiones_cortadas"]) == ("acceso_cortado", 0)
    assert len(_auditoria(conn, "cortar_acceso_web")) == 1


def test_perdi_el_celular_de_un_espacio_no_toca_otro(conn, mundo, escribe):
    """Marcos también está en otro espacio: su sesión de allá sigue abierta."""
    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, zona_horaria, activo)
                       values ('otro', 'Otro', 'America/Argentina/Buenos_Aires', true)
                       returning id""")
        otro = str(cur.fetchone()["id"])
        cur.execute("""insert into workspace_version (workspace_id, version, pack_hash)
                       values (%s, 1, 'hash-otro')""", (otro,))
        cur.execute("""insert into area (workspace_id, slug, nombre)
                       values (%s, 'campo', 'Campo') returning id""", (otro,))
        area = str(cur.fetchone()["id"])
        cur.execute("""insert into rol (workspace_id, slug, nombre, autoridad_final)
                       values (%s, 'lider', 'lider', true) returning id""", (otro,))
        rol = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id)
                       values (%s, %s, %s, %s) returning id""",
                    (otro, mundo["personas"]["Marcos"]["app_user_id"], area, rol))
        de_alla = str(cur.fetchone()["id"])
    conn.commit()
    with espacio(conn, otro) as cur:
        token = web_app.emitir_enlace(cur, de_alla)
    conn.commit()
    assert _canjear(conn, token) is not None
    _dice(conn, escribe, Jugada("perdi_el_celular", {}))
    assert len(todos(conn, "select 1 from sesion_web where cortada_en is null")) == 1


# --- Abrir la app y un pedido con la pregunta abierta (prueba de la Mini App, 2026-10-14) ------

def test_la_jugada_describe_abrir_la_aplicacion_sin_frases_de_ejemplo():
    """"abrí la app" no eligió ninguna jugada: la definición hablaba de un enlace. Ahora describe
    el trabajo (abrir la aplicación de Leda, que se abre dentro de Telegram), sin frases."""
    ficha = FICHAS["pedir_acceso_web"]
    assert "aplicación" in ficha.es and "Telegram" in ficha.es and "enlace de entrada" not in ficha.es
    assert "aplicación" in ficha.para_que
    assert not re.search(r"[\"“”«»]", ficha.es)


def test_la_jugada_dice_donde_se_abre_la_aplicacion_en_cada_dispositivo():
    """MA-5 (b): la definición decía que la aplicación es "la que se abre dentro de Telegram", y
    la IA le contestó a quien la quería abrir en el navegador que no se abre ahí. El hecho: se
    abre con el botón fijo del menú; en el celular, dentro de Telegram; en Telegram de la
    computadora, en el navegador. La dirección (para_la_compu) es para una computadora sin
    Telegram."""
    ficha = FICHAS["pedir_acceso_web"]
    es = " ".join(ficha.es.split())
    assert "que también es una web" not in es
    assert all(p in es for p in ("menú", "celular", "computadora", "navegador"))
    oracion = next(o for o in es.split(". ") if "para_la_compu" in o)
    assert "computadora sin Telegram" in oracion
    assert "ningún botón" in " ".join(ficha.despues.split())


def test_un_pedido_que_ninguna_jugada_hace_nunca_va_como_ninguna_jugada():
    """La regla general de ADR 0018 (decisión 1), dicha también en la definición de lo que no
    está en la lista: un pedido va ahí, también con una pregunta abierta; y la redacción, con una
    pregunta que vuelve, contesta antes lo que el mensaje dijo o pidió."""
    from leda.motor.ia_real import FUERA_DE_LA_LISTA_ES
    from leda.motor.instrucciones import INSTRUCCIONES_REDACCION

    assert "nunca como ninguna jugada" in FUERA_DE_LA_LISTA_ES
    assert "también con una pregunta abierta" in FUERA_DE_LA_LISTA_ES
    assert "antes le contestás a lo que dijo o pidió" in " ".join(INSTRUCCIONES_REDACCION.split())



def test_un_boton_por_mensaje_el_primero_decide_y_cada_hecho_dice_ese(conn, mundo, escribe,
                                                                     direccion):
    """R3-destino-overwrite: con dos jugadas que marcan el botón, el primero decide a dónde lleva
    y los dos hechos dicen el botón que de verdad sale. Pedir abrir la app no marca ninguno."""
    hechos, _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}),
                      Jugada("pedir_crear", {"que_quiere_crear": "tarea"}),
                      Jugada("pedir_crear", {"que_quiere_crear": "objetivo"}), nombre="Ismael")
    assert hechos[0] == MENU
    assert [h.get("lleva_el_boton") for h in hechos[1:]] == ["Cargar la tarea"] * 2
    [marca] = _marcas(conn)
    assert marca["destino"] == "cargar_tarea"
    [mensaje] = _despachar(conn, mundo).enviados
    assert mensaje.botones[-1].etiqueta == "Cargar la tarea"


def test_el_dato_para_la_compu_es_un_booleano_de_la_jugada():
    """R3-para-la-compu-no-consumer-or-test: el esquema que recibe la IA lo ofrece como un
    verdadero o falso, y la jugada lo usa (`test_la_direccion_para_la_compu_va_sola_y_sin_boton`)."""
    from leda.motor.ia_real import DATOS

    tipo, descripcion = DATOS["para_la_compu"]
    assert tipo == "boolean" and "computadora sin Telegram" in descripcion
    # Un hecho, sin frases de ejemplo (MA-5).
    assert not re.search(r"[\"“”«»]", descripcion)
    assert "para_la_compu" in FICHAS["pedir_acceso_web"].opcional
