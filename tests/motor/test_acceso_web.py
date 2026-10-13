"""La entrada a la web por chat: las jugadas `pedir_acceso_web` y `perdi_el_celular` (ADR 0022,
decisión 4; decisiones 1 y 3 del usuario del 2026-10-12; conversación 50, pasos 4 a 6; tarea A-3
de `odd/tasks/acceso-por-chat.md`).

- `pedir_acceso_web`: la respuesta lleva la marca del enlace de entrada de la persona
  (`message_outbox_entrada_web`); el despachador lo emite al mandar y anula el que tenía sin
  usar. Los hechos dicen que va el enlace, que sirve una vez, que vence a las 24 horas y si el
  anterior deja de servir. La IA nunca ve ni escribe una dirección. Un mensaje lleva un solo
  enlace (decisión técnica 2): con el de una tarea, el otro no se promete.
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
ENLACE_WEB = re.compile(r"\nhttps://leda\.invalid/app/entrar/([A-Za-z0-9_-]{43})$")

ENLACE_NUEVO = {"jugada": "pedir_acceso_web", "resultado": "enlace_nuevo",
                "lleva_el_enlace_de_entrada_a_la_web": True, "sirve_una_sola_vez": True,
                "vence_a_las_24_horas": True}


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
    return todos(conn, """select w.membership_id::text persona, w.es_ofrecimiento
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
        assert ficha.necesita == () and ficha.opcional == ()
        assert ficha.es and ficha.para_que in lo_que_puede_hacer(JUGADAS)
        # La redacción las recibe por lo que hacen.
        assert hechos_mod.es_un_concepto_de_la_cocina(nombre)
        assert nombre in hechos_mod.PARA_LA_REDACCION


def test_lo_que_es_cada_jugada_no_trae_frases_de_ejemplo():
    """Describe la jugada, nunca un caso ni una frase (la regla del mozo): sin comillas."""
    for nombre in ("pedir_acceso_web", "perdi_el_celular"):
        assert not re.search(r"[\"“”«»]", FICHAS[nombre].es), nombre


def test_cada_clave_y_codigo_de_sus_hechos_tiene_significado():
    for codigo in ("enlace_nuevo", "lleva_el_enlace_de_entrada_a_la_web", "sirve_una_sola_vez",
                   "vence_a_las_24_horas", "el_anterior_ya_no_sirve", "acceso_cortado",
                   "sesiones_cortadas", "recuerda_cerrar_telegram_en_ese_celular",
                   "puede_pedir_otro_enlace", "ya_lleva_otro_enlace"):
        assert hechos_mod.significado(codigo), codigo
    # El significado dice que la dirección la agrega el código: la IA no escribe ninguna.
    assert "no lo ve ni lo escribe" in hechos_mod.significado(
        "lleva_el_enlace_de_entrada_a_la_web")


# --- Pedir el acceso ------------------------------------------------------------------------

def test_pedir_el_acceso_lleva_la_marca_y_el_enlace_se_emite_al_mandar(conn, mundo, escribe,
                                                                       direccion):
    [hecho], pedido = _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    assert hecho == {**ENLACE_NUEVO, "el_anterior_ya_no_sirve": False}
    assert _marcas(conn) == [{"persona": _membresia(mundo), "es_ofrecimiento": False}]
    assert todos(conn, "select 1 from enlace_de_entrada") == []    # todavía no se emitió
    # La IA nunca ve una dirección ni un nombre de la base.
    assert "http" not in repr(pedido) and "leda.invalid" not in repr(pedido)
    assert "entro_a_la_web" not in repr(pedido) and "tiene_un_enlace" not in repr(pedido)
    [mensaje] = _despachar(conn, mundo).enviados
    encontrado = ENLACE_WEB.search(mensaje.texto)
    assert encontrado and mensaje.sin_vista_previa
    assert _canjear(conn, encontrado.group(1)) is not None


def test_con_un_enlace_sin_usar_el_anterior_deja_de_servir(conn, mundo, escribe, direccion):
    anterior = _emitir(conn, mundo)
    [hecho], _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    assert hecho == {**ENLACE_NUEVO, "el_anterior_ya_no_sirve": True}
    _despachar(conn, mundo)
    assert _canjear(conn, anterior) is None


def test_un_enlace_ya_usado_no_es_uno_que_deja_de_servir(conn, mundo, escribe, direccion):
    """La sesión que abrió sigue abierta: pedir otro no la corta."""
    assert _canjear(conn, _emitir(conn, mundo)) is not None
    [hecho], _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    assert hecho["el_anterior_ya_no_sirve"] is False


def test_sin_la_direccion_publica_no_se_promete_ningun_enlace(conn, mundo, escribe):
    [hecho], _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}))
    assert hecho == {"jugada": "pedir_acceso_web", "resultado": "no_se_puede",
                     "motivo": "la_pagina_no_esta_disponible"}
    assert _marcas(conn) == []


def test_pedirlo_dos_veces_en_un_mensaje_lleva_un_solo_enlace(conn, mundo, escribe, direccion):
    hechos, _ = _dice(conn, escribe, Jugada("pedir_acceso_web", {}),
                      Jugada("pedir_acceso_web", {}))
    assert [h["resultado"] for h in hechos] == ["enlace_nuevo", "enlace_nuevo"]
    assert len(_marcas(conn)) == 1


def test_con_el_enlace_de_una_tarea_el_de_entrada_no_se_promete(conn, mundo, escribe,
                                                                  direccion):
    """Un enlace por mensaje (decisión técnica 2): el de la tarea, pedido primero, sale; el de
    entrada se puede pedir aparte."""
    tarea, web = _dice(conn, escribe, Jugada("pedir_enlace", {"tarea": "T1"}),
                       Jugada("pedir_acceso_web", {}))[0]
    assert tarea[LLEVA_EL_ENLACE] is True
    assert web == {"jugada": "pedir_acceso_web", "resultado": "no_se_puede",
                   "motivo": "ya_lleva_otro_enlace"}
    assert _marcas(conn) == []
    assert len(todos(conn, "select 1 from message_outbox_enlace")) == 1


def test_con_el_de_entrada_el_enlace_de_una_tarea_no_se_promete(conn, mundo, escribe,
                                                                  direccion):
    web, tarea = _dice(conn, escribe, Jugada("pedir_acceso_web", {}),
                       Jugada("pedir_enlace", {"tarea": "T1"}))[0]
    assert web["resultado"] == "enlace_nuevo"
    assert (tarea["resultado"], tarea["motivo"]) == ("no_se_puede",
                                                     "ya_lleva_el_enlace_de_otra_tarea")
    assert LLEVA_EL_ENLACE not in tarea
    assert todos(conn, "select 1 from message_outbox_enlace") == []
    assert len(_marcas(conn)) == 1
    # El significado del código dice la verdad también acá: lleva otro enlace.
    assert "entrada a la web" in hechos_mod.significado("ya_lleva_el_enlace_de_otra_tarea")


def test_si_la_ia_no_redacta_no_sale_ningun_enlace(conn, mundo, escribe, direccion):
    """El texto fijo no lleva lo que hicieron las jugadas: se deshizo."""
    from leda.motor.ia import IAGuionada as Guionada

    class NoRedacta(Guionada):
        def redactar(self, pedido):
            raise RuntimeError("caída")

    quien, entrante = escribe("Marcos", "-")
    procesar_turno(conn, quien, entrante,
                   NoRedacta(jugadas=[[Jugada("pedir_acceso_web", {})]] * 2),
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
                     "puede_pedir_otro_enlace": True}
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
