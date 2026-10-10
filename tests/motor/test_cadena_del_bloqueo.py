"""Quien destraba dice que no le corresponde (`leda.motor.persecucion`; C-5, porción 3; decisión 5
del usuario, 2026-10-08, opción A con límite; ADR 0017, decisión 3a, paso 4; ADR 0018, 9c, con la
precisión del 2026-10-09; conversación 34). Con las decisiones 24, 49 y 51 del usuario
(2026-10-09; C-5d).

A quien Leda le pregunta por un bloqueo dice que no le toca. Si no dice de quién es, Leda le
pregunta una vez quién se encarga. Si nombra a otro integrante, Leda le escribe a esa persona como
le escribió a la primera, y la persona trabada se entera, como información. **La cadena llega
hasta tres personas preguntadas** (decisión 51): si la tercera tampoco lo toma (no le corresponde,
no sabe o nombra a otra), Leda no sigue. **Antes de asentar un "ni idea", Leda le pregunta a la
persona trabada** si se le ocurre otra persona (decisión 49): si nombra a alguien, sigue con esa
persona, en la misma cadena; si no, queda asentado. Al cortarse, la cadena entera le llega a quien
decide quién lo resuelve, sin pedirle nada: **nunca a alguien de la cadena** (decisión 24), al
referente de la tarea trabada o, si ése es la persona trabada o alguien de la cadena, a quien
aprueba el trabajo de la persona trabada. A la persona trabada se le dice que quedó asentado, sin
nombrar a nadie por su cuenta (decisiones 11 y 35).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor.avisos import TIPOS
from leda.motor.fichas import FICHAS
from leda.motor.ia import Jugada
from leda.motor.ia_real import DATOS
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import (AHORA, IAQueRedacta, administrador, avisos_guardados, cuantas,
                                   todos, uno)
from tests.motor.test_aprobacion import Turnos

CAUSA = "me falta la ip del servidor"
PREGUNTA_A_QUIEN_DESTRABA = "pregunta_a_quien_destraba"
LO_QUE_DIJO = "lo_que_dijo_quien_destraba"
CADENA = "cadena_del_bloqueo"
QUIEN_MAS = "quien_mas_puede_destrabar"
ARIEL, MARIANO, JUAN, PEDRO = "Ariel De Simone", "Mariano Naim", "Juan Perez", "Pedro Gomez"


def _area(conn, mundo, slug: str) -> str:
    with admin(conn) as cur:
        cur.execute("insert into area (workspace_id, slug, nombre) values (%s, %s, %s) "
                    "returning id", (mundo["id"], slug, slug.capitalize()))
        area = str(cur.fetchone()["id"])
    conn.commit()
    return area


def _referente(conn, area: str, membership_id: str) -> None:
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (membership_id, area))
    conn.commit()


def _integrante(conn, mundo, corto: str, nombre: str, telegram: int | None,
                area: str | None = None) -> None:
    """Otra persona del espacio, cuyo trabajo aprueba Ismael."""
    with admin(conn) as cur:
        cur.execute("select rol_id from membership where id = %s",
                    (mundo["personas"]["Marcos"]["membership_id"],))
        rol = cur.fetchone()["rol_id"]
        cur.execute("insert into app_user (telegram_user_id, nombre) values (%s, %s) "
                    "returning id", (telegram, nombre))
        usuario = str(cur.fetchone()["id"])
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (mundo["id"], usuario, area or mundo["area"], rol,
                     mundo["personas"]["Ismael"]["membership_id"]))
        mundo["personas"][corto] = {"app_user_id": usuario, "telegram": telegram,
                                    "membership_id": str(cur.fetchone()["id"])}
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""",
                    (mundo["personas"][corto]["membership_id"], mundo["id"]))
    conn.commit()


@pytest.fixture
def equipo(conn, mundo) -> Turnos:
    """Ariel, Mariano y Pedro, del área de la tarea (su referente es Ismael); Juan y Lucas, del
    taller, cuyo referente es Lucas. Todos con un chat con Leda."""
    _integrante(conn, mundo, "Ariel", ARIEL, 81_020)
    _integrante(conn, mundo, "Mariano", MARIANO, 81_021)
    taller = _area(conn, mundo, "taller")
    _integrante(conn, mundo, "Juan", JUAN, 81_022, area=taller)
    _integrante(conn, mundo, "Lucas", "Lucas Natuche", 81_023, area=taller)
    _integrante(conn, mundo, "Pedro", PEDRO, 81_024)
    _referente(conn, mundo["area"], _membresia(mundo, "Ismael"))
    _referente(conn, taller, _membresia(mundo, "Lucas"))
    mundo["taller"] = taller
    return Turnos(conn, mundo)


def _membresia(mundo, corto: str) -> str:
    return mundo["personas"][corto]["membership_id"]


def _salir(conn, mundo, at) -> IAQueRedacta:
    from leda.motor.avisos import enviar_avisos
    ia = IAQueRedacta()
    enviar_avisos(conn, mundo["id"], ia, RelojFijo(at))
    conn.commit()
    return ia


def _le_pregunto_a_ariel(conn, mundo, t: Turnos) -> None:
    """Marcos se traba, dice que lo destraba Ariel y a Ariel le llega la pregunta."""
    t.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    t.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "ariel"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=12))
    t.minuto = 30


def _le_pregunto_a_mariano(conn, mundo, t: Turnos) -> None:
    """Ariel dijo que lo maneja Mariano, y a Mariano le llegó la pregunta."""
    _le_pregunto_a_ariel(conn, mundo, t)
    t.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "mariano"}))
    # Pasada la media hora en que Ariel estuvo conversando: a Mariano no lo demora.
    _salir(conn, mundo, AHORA + timedelta(minutes=45))
    t.minuto = 60


def _le_pregunto_a_juan(conn, mundo, t: Turnos) -> None:
    """Mariano dijo que es de Juan, y a Juan le llegó la pregunta: la tercera persona
    preguntada."""
    _le_pregunto_a_mariano(conn, mundo, t)
    t.dice("Mariano", Jugada("decir_que_no_le_toca", {"quien": "juan"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=75))
    t.minuto = 90


def _ariel_no_sabe_y_se_lo_pregunto_a_marcos(conn, mundo, t: Turnos) -> None:
    """Ariel no sabe de quién es, y a Marcos le llegó la pregunta de si se le ocurre otra
    persona."""
    _le_pregunto_a_ariel(conn, mundo, t)
    t.dice("Ariel", Jugada("decir_que_no_le_toca", {"no_sabe": True, "lo_que_dice": "ni idea"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=45))
    t.minuto = 60


def _su_pregunta(conn, mundo, corto: str) -> dict | None:
    return uno(conn, """select q.tipo, q.task_id::text tarea, q.jugada
                          from conversation_state s
                          join conversation_question q on q.id = s.pregunta_abierta_id
                         where s.membership_id = %s and q.cerrada_en is null""",
               _membresia(mundo, corto))


def _destraban(conn) -> list[dict]:
    return todos(conn, """select destraba_membership_id::text destraba, destraba_externo,
                                 no_sabe, dicho_por_membership_id::text dicho_por
                            from blocker_unblocker order by at, id""")


def _a_quienes_les_pregunto(conn) -> list[str]:
    return [str(a["destinatario_membership_id"])
            for a in avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)]


# --- "No me corresponde", sin decir de quién ------------------------------------------------------

def test_sin_decir_de_quien_es_pregunta_quien_se_encarga(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca",
                                    {"lo_que_dice": "no me corresponde eso"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "falta_dato"
    assert hecho["falta"] == ["quien_se_encarga"]
    assert hecho["pregunta"] == "cuando_se_destraba"
    # Nada queda anotado todavía: ni lo que dijo ni quién destraba.
    assert cuantas(conn, "dicho_de_quien_destraba") == 0
    assert len(_destraban(conn)) == 1
    assert avisos_guardados(conn, LO_QUE_DIJO) == []
    pregunta = _su_pregunta(conn, mundo, "Ariel")
    assert pregunta["tipo"] == "cuando_se_destraba"
    assert pregunta["jugada"]["datos"]["no_le_corresponde"] is True
    assert cuantas(conn, "pending_reply", "membership_id = %s and satisfecho_en is null",
                   _membresia(mundo, "Ariel")) == 1


def test_el_segundo_sin_decir_de_quien_es_tambien_pregunta_quien_se_encarga(conn, mundo,
                                                                           equipo):
    """Con lugar en la cadena (decisión 51), el segundo que no dice de quién es recibe la misma
    pregunta que el primero, una vez."""
    _le_pregunto_a_mariano(conn, mundo, equipo)

    r = equipo.dice("Mariano", Jugada("decir_que_no_le_toca", {}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "falta_dato"
    assert hecho["falta"] == ["quien_se_encarga"]
    assert avisos_guardados(conn, CADENA) == []
    assert _su_pregunta(conn, mundo, "Mariano")["tipo"] == "cuando_se_destraba"


# --- Nombra a otro: Leda sigue con esa persona -------------------------------------------------

def test_nombra_a_otro_y_leda_le_escribe_a_esa_persona(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"lo_que_dice": "no me corresponde"}))

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "mariano"}))

    # Lo que dijo Ariel queda anotado, atribuido y auditado; quién destraba ahora es Mariano,
    # dicho por Ariel.
    dicho = uno(conn, """select no_le_corresponde, lo_que_dice, para_cuando, ya_esta,
                                dicho_por_membership_id::text quien
                           from dicho_de_quien_destraba""")
    assert dicho == {"no_le_corresponde": True, "lo_que_dice": "no me corresponde",
                     "para_cuando": None, "ya_esta": False, "quien": _membresia(mundo, "Ariel")}
    assert _destraban(conn)[-1] == {"destraba": _membresia(mundo, "Mariano"),
                                    "destraba_externo": None, "no_sabe": False,
                                    "dicho_por": _membresia(mundo, "Ariel")}
    assert cuantas(conn, "audit_log", "accion = 'anotar_que_no_le_toca'") == 1
    assert cuantas(conn, "audit_log", "accion = 'anotar_quien_destraba'") == 2
    # A Mariano, la pregunta, como Leda, diciendo quién está trabado y quién lo nombró.
    _primera, pregunta = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert str(pregunta["destinatario_membership_id"]) == _membresia(mundo, "Mariano")
    assert pregunta["programado_para"] == AHORA + timedelta(minutes=32 + 10)
    assert pregunta["hechos"]["responsable"] == "Marcos"
    assert pregunta["hechos"]["nombrado_por"] == ARIEL
    assert pregunta["hechos"]["causa"] == CAUSA
    # A Marcos, lo que dijo Ariel, como información.
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["hechos"]["dice_quien_destraba"] == {
        "no_le_corresponde": True, "le_toca_a": MARIANO, "lo_que_dice": "no me corresponde"}
    assert aviso["hechos"]["se_le_pregunta_a"] == {"a": MARIANO}
    assert aviso["hechos"]["necesita_respuesta"] is False
    # Nada al referente: la cadena sigue.
    assert avisos_guardados(conn, CADENA) == []
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["se_le_pregunta_a"]["a"] == MARIANO
    assert hecho["aviso_a_quien_esta_trabado"]["a"] == "Marcos"
    assert "aviso_de_la_cadena" not in hecho
    # Su pregunta y su espera se cierran, y la tarea ya no está en su lista.
    assert _su_pregunta(conn, mundo, "Ariel") is None
    assert cuantas(conn, "pending_reply", "membership_id = %s and satisfecho_en is null",
                   _membresia(mundo, "Ariel")) == 0
    assert equipo.situacion["tareas"][0]["alias"] == "T1"
    equipo.dice("Ariel", Jugada("decir_cuando_destraba", {"tarea": "T1", "ya_esta": True}))
    assert equipo.situacion["tareas"] == []


def test_lo_que_dice_el_segundo_le_llega_a_quien_esta_trabado(conn, mundo, equipo):
    _le_pregunto_a_mariano(conn, mundo, equipo)
    assert _su_pregunta(conn, mundo, "Mariano")["tipo"] == "cuando_se_destraba"

    equipo.dice("Mariano", Jugada("decir_cuando_destraba",
                                  {"tarea": "T1", "para_cuando": "2026-10-07"}))

    _de_ariel, de_mariano = avisos_guardados(conn, LO_QUE_DIJO)
    assert de_mariano["hechos"]["quien_destraba"] == MARIANO
    assert de_mariano["hechos"]["dice_quien_destraba"] == {"para_cuando": "2026-10-07"}


# --- Hasta tres personas preguntadas (decisión 51) -----------------------------------------------

def test_el_segundo_que_nombra_a_otro_y_leda_le_escribe_al_tercero(conn, mundo, equipo):
    _le_pregunto_a_mariano(conn, mundo, equipo)

    r = equipo.dice("Mariano", Jugada("decir_que_no_le_toca", {"quien": "juan"}))

    assert _a_quienes_les_pregunto(conn) == [_membresia(mundo, p)
                                             for p in ("Ariel", "Mariano", "Juan")]
    tercera = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)[-1]
    assert tercera["hechos"]["nombrado_por"] == MARIANO
    assert tercera["hechos"]["responsable"] == "Marcos"
    assert avisos_guardados(conn, CADENA) == []
    _de_ariel, de_mariano = avisos_guardados(conn, LO_QUE_DIJO)
    assert de_mariano["hechos"]["se_le_pregunta_a"] == {"a": JUAN}
    [hecho] = r.hechos
    assert hecho["se_le_pregunta_a"]["a"] == JUAN
    assert "aviso_de_la_cadena" not in hecho


def test_si_el_tercero_se_hace_cargo_se_resolvio(conn, mundo, equipo):
    _le_pregunto_a_juan(conn, mundo, equipo)

    equipo.dice("Juan", Jugada("decir_cuando_destraba",
                               {"tarea": "T1", "para_cuando": "2026-10-07"}))

    assert avisos_guardados(conn, CADENA) == []
    assert avisos_guardados(conn, QUIEN_MAS) == []
    assert avisos_guardados(conn, LO_QUE_DIJO)[-1]["hechos"]["dice_quien_destraba"] == {
        "para_cuando": "2026-10-07"}


def test_el_tercero_que_nombra_a_otro_corta_la_cadena(conn, mundo, equipo):
    _le_pregunto_a_juan(conn, mundo, equipo)

    r = equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"quien": "pedro"}))

    # A Pedro no le escribe: la cadena llega hasta tres personas preguntadas.
    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 3
    assert _destraban(conn)[-1]["destraba"] == _membresia(mundo, "Pedro")
    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert cadena["hechos"]["cadena"] == [
        {"de": "Marcos", "le_toca_a": ARIEL},
        {"de": ARIEL, "no_le_corresponde": True, "le_toca_a": MARIANO},
        {"de": MARIANO, "no_le_corresponde": True, "le_toca_a": JUAN},
        {"de": JUAN, "no_le_corresponde": True, "le_toca_a": PEDRO}]
    [hecho] = r.hechos
    assert hecho["aviso_de_la_cadena"]["a"] == "Ismael"
    assert "se_le_pregunta_a" not in hecho


def test_el_tercero_que_no_sabe_corta_sin_preguntarle_a_quien_esta_trabado(conn, mundo, equipo):
    """Con las tres personas ya preguntadas, el "ni idea" del tercero queda asentado: no hay
    lugar para otra persona (decisiones 49 y 51)."""
    _le_pregunto_a_juan(conn, mundo, equipo)

    equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"no_sabe": True}))

    assert avisos_guardados(conn, QUIEN_MAS) == []
    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["hechos"]["cadena"][-1] == {"de": JUAN, "no_le_corresponde": True,
                                              "no_sabe": True}
    # A Marcos, lo que dijo Juan y que quedó asentado.
    aviso = avisos_guardados(conn, LO_QUE_DIJO)[-1]
    assert aviso["hechos"]["queda_asentado"] == {"figura_en_el_informe_al_grupo": False,
                                                 "a": "Ismael"}


def test_el_tercero_que_solo_dice_que_no_le_corresponde_corta_sin_preguntar(conn, mundo, equipo):
    _le_pregunto_a_juan(conn, mundo, equipo)

    r = equipo.dice("Juan", Jugada("decir_que_no_le_toca", {}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["hechos"]["cadena"][-1] == {"de": JUAN, "no_le_corresponde": True}
    # Quién destraba no cambia: Juan no dijo de quién es.
    assert _destraban(conn)[-1]["destraba"] == _membresia(mundo, "Juan")


def test_el_primero_que_nombra_a_alguien_de_afuera_corta_la_cadena(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 1
    assert _destraban(conn)[-1]["destraba_externo"] == "el proveedor"
    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert cadena["hechos"]["cadena"][-1] == {"de": ARIEL, "no_le_corresponde": True,
                                              "le_toca_a": "el proveedor"}


# --- "Ni idea": antes de asentarlo, a la persona trabada (decisión 49) ---------------------------

def test_el_primero_que_no_sabe_le_pregunta_a_quien_esta_trabado(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca",
                                    {"no_sabe": True, "lo_que_dice": "ni idea"}))

    # Nada se asienta todavía: a Marcos, lo que dijo Ariel y si se le ocurre otra persona.
    assert avisos_guardados(conn, CADENA) == []
    assert avisos_guardados(conn, LO_QUE_DIJO) == []
    [aviso] = avisos_guardados(conn, QUIEN_MAS)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["programado_para"] == AHORA + timedelta(minutes=31 + 10)
    hechos = aviso["hechos"]
    assert hechos["necesita_respuesta"] is True
    assert hechos["pregunta"] == "quien_destraba"
    assert (hechos["tarea"], hechos["causa"], hechos["quien_destraba"]) == (
        "Revisar el tablero", CAUSA, ARIEL)
    assert hechos["dice_quien_destraba"] == {"no_le_corresponde": True, "no_sabe": True,
                                             "lo_que_dice": "ni idea"}
    # Lo que dijo Ariel queda anotado igual.
    assert _destraban(conn)[-1] == {"destraba": None, "destraba_externo": None, "no_sabe": True,
                                    "dicho_por": _membresia(mundo, "Ariel")}
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["aviso_a_quien_esta_trabado"]["a"] == "Marcos"
    assert "aviso_de_la_cadena" not in hecho
    assert _su_pregunta(conn, mundo, "Ariel") is None


def test_la_pregunta_a_quien_esta_trabado_le_abre_la_de_quien_destraba(conn, mundo, equipo):
    _ariel_no_sabe_y_se_lo_pregunto_a_marcos(conn, mundo, equipo)

    [aviso] = avisos_guardados(conn, QUIEN_MAS)
    assert aviso["estado"] == "enviado"
    pregunta = _su_pregunta(conn, mundo, "Marcos")
    assert (pregunta["tipo"], pregunta["jugada"]["nombre"]) == ("quien_destraba",
                                                               "anotar_quien_destraba")
    assert cuantas(conn, "pending_reply", "membership_id = %s and satisfecho_en is null "
                   "and tipo = 'quien_destraba'", _membresia(mundo, "Marcos")) == 1


def test_no_me_corresponde_dos_veces_sin_decir_de_quien_le_pregunta_a_quien_esta_trabado(
        conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {}))

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["dice_quien_destraba"] == {"no_le_corresponde": True, "no_sabe": True}
    assert avisos_guardados(conn, CADENA) == []
    [aviso] = avisos_guardados(conn, QUIEN_MAS)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")


def test_el_segundo_que_no_sabe_tambien_le_pregunta_a_quien_esta_trabado(conn, mundo, equipo):
    _le_pregunto_a_mariano(conn, mundo, equipo)

    equipo.dice("Mariano", Jugada("decir_que_no_le_toca",
                                  {"no_sabe": True, "lo_que_dice": "ni idea"}))

    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 2
    assert avisos_guardados(conn, CADENA) == []
    [aviso] = avisos_guardados(conn, QUIEN_MAS)
    assert aviso["hechos"]["quien_destraba"] == MARIANO


def test_si_se_le_ocurre_otra_persona_leda_le_escribe(conn, mundo, equipo):
    _ariel_no_sabe_y_se_lo_pregunto_a_marcos(conn, mundo, equipo)

    r = equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "mariano"}))

    assert _a_quienes_les_pregunto(conn)[-1] == _membresia(mundo, "Mariano")
    assert avisos_guardados(conn, CADENA) == []
    [hecho] = r.hechos
    assert hecho["se_le_pregunta_a"]["a"] == MARIANO
    assert "salidas" not in hecho
    assert _su_pregunta(conn, mundo, "Marcos") is None


def test_lo_que_nombra_quien_esta_trabado_sigue_en_la_misma_cadena(conn, mundo, equipo):
    """Ariel (1) no sabe; Marcos nombra a Mariano (2); Mariano nombra a Juan (3); Juan nombra a
    Pedro: la cadena se corta ahí, con todo lo que dijo cada uno desde que Marcos nombró a
    Ariel."""
    _ariel_no_sabe_y_se_lo_pregunto_a_marcos(conn, mundo, equipo)
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "mariano"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=75))
    equipo.minuto = 90
    equipo.dice("Mariano", Jugada("decir_que_no_le_toca", {"quien": "juan"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=105))
    equipo.minuto = 120

    equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"quien": "pedro"}))

    assert _a_quienes_les_pregunto(conn) == [_membresia(mundo, p)
                                             for p in ("Ariel", "Mariano", "Juan")]
    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["hechos"]["cadena"] == [
        {"de": "Marcos", "le_toca_a": ARIEL},
        {"de": ARIEL, "no_le_corresponde": True, "no_sabe": True, "lo_que_dice": "ni idea"},
        {"de": "Marcos", "le_toca_a": MARIANO},
        {"de": MARIANO, "no_le_corresponde": True, "le_toca_a": JUAN},
        {"de": JUAN, "no_le_corresponde": True, "le_toca_a": PEDRO}]


def test_si_no_se_le_ocurre_nadie_queda_asentado(conn, mundo, equipo):
    """Qué es dejar asentado (decisión 49): en la historia de la tarea, le llega a quien decide
    quién lo resuelve (decisión 24) y a la persona trabada se le dice con la forma de la decisión
    35, sin nombrar a nadie por su cuenta."""
    _ariel_no_sabe_y_se_lo_pregunto_a_marcos(conn, mundo, equipo)

    r = equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"no_sabe": True}))

    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert cadena["hechos"]["cadena"] == [
        {"de": "Marcos", "le_toca_a": ARIEL},
        {"de": ARIEL, "no_le_corresponde": True, "no_sabe": True, "lo_que_dice": "ni idea"},
        {"de": "Marcos", "no_sabe": True}]
    assert cuantas(conn, "audit_log", "accion = 'informar_la_cadena_del_bloqueo'") == 1
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["queda_asentado"] == {"figura_en_el_informe_al_grupo": False, "a": "Ismael"}
    redactado = hechos_mod.para_redactar(dict(hecho))
    assert "a" not in redactado["queda_asentado"]
    # El tema se cierra así: no le propone salidas ni le vuelve a preguntar.
    assert "salidas" not in hecho
    assert _su_pregunta(conn, mundo, "Marcos") is None
    assert cuantas(conn, "blocker", "resuelto_en is null") == 1


def test_si_contesta_antes_de_que_le_llegue_la_pregunta_no_sale(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"no_sabe": True}))
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "mariano"}))

    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    [aviso] = avisos_guardados(conn, QUIEN_MAS)
    assert aviso["estado"] == "omitido"


def test_despues_de_cortarse_lo_que_nombra_quien_esta_trabado_empieza_otra_cadena(conn, mundo,
                                                                                 equipo):
    """La cadena cortada quedó asentada; si después Marcos nombra a otra persona por su cuenta,
    es otra vuelta: Leda vuelve a seguir hasta tres."""
    _le_pregunto_a_juan(conn, mundo, equipo)
    equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"quien": "pedro"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=105))
    equipo.minuto = 120
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"tarea": "T1", "quien": "pedro"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=135))
    equipo.minuto = 150

    equipo.dice("Pedro", Jugada("decir_que_no_le_toca", {"quien": "lucas"}))

    assert _a_quienes_les_pregunto(conn)[-1] == _membresia(mundo, "Lucas")


# --- A quién va: nunca a alguien de la cadena (decisión 24) -------------------------------------

def test_va_al_referente_de_la_tarea_y_no_al_sector_de_quien_quedo_nombrado(conn, mundo,
                                                                            equipo):
    """Juan es del taller, cuyo referente es Lucas: lo que falta no cambia a quién va. Va al
    referente de la tarea trabada (Ismael)."""
    _le_pregunto_a_mariano(conn, mundo, equipo)
    equipo.dice("Mariano", Jugada("decir_que_no_le_toca", {"quien": "pedro"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=75))
    equipo.minuto = 90

    equipo.dice("Pedro", Jugada("decir_que_no_le_toca", {"quien": "juan"}))

    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")


def test_nunca_va_a_alguien_de_la_cadena(conn, mundo, equipo):
    """El referente de la tarea es Mariano, que dijo que no es suyo: va a quien aprueba el
    trabajo de Marcos (Ismael)."""
    _referente(conn, mundo["area"], _membresia(mundo, "Mariano"))
    _le_pregunto_a_juan(conn, mundo, equipo)

    r = equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert r.hechos[0]["aviso_de_la_cadena"]["a"] == "Ismael"


def test_si_quien_aprueba_tambien_es_de_la_cadena_queda_asentado_sin_a_quien(conn, mundo,
                                                                            equipo):
    """El referente de la tarea (Ariel) y quien aprueba el trabajo de Marcos (Mariano) son de la
    cadena: no le llega a nadie, y queda asentado igual, con un incidente para el administrador."""
    administrador(conn)
    _referente(conn, mundo["area"], _membresia(mundo, "Ariel"))
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (_membresia(mundo, "Mariano"), _membresia(mundo, "Marcos")))
    conn.commit()
    _le_pregunto_a_juan(conn, mundo, equipo)

    r = equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    assert avisos_guardados(conn, CADENA) == []
    assert r.hechos[0]["aviso_de_la_cadena"] == {"llega": "no_le_va_a_llegar",
                                                 "motivo": "sin_referente"}
    assert cuantas(conn, "audit_log", "accion = 'asentar_la_cadena_del_bloqueo'") == 1
    [incidente] = todos(conn, "select etapa from incident")
    assert incidente["etapa"] == "motor_sin_a_quien_informar"


def test_si_el_referente_es_quien_esta_trabado_va_a_quien_aprueba_su_trabajo(conn, mundo,
                                                                              equipo):
    _referente(conn, mundo["area"], _membresia(mundo, "Marcos"))
    _le_pregunto_a_ariel(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")


def test_sin_referente_no_promete_que_se_informa(conn, mundo, equipo):
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = null where id = %s",
                    (mundo["area"],))
        cur.execute("update membership set aprobador_membership_id = null where id = %s",
                    (_membresia(mundo, "Marcos"),))
    conn.commit()
    _le_pregunto_a_ariel(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    assert avisos_guardados(conn, CADENA) == []
    [hecho] = r.hechos
    assert hecho["aviso_de_la_cadena"] == {"llega": "no_le_va_a_llegar",
                                           "motivo": "sin_referente"}


def test_sin_referente_la_cadena_queda_asentada_igual(conn, mundo, equipo):
    """Sin nadie a quien informar (decisión 49, qué es dejar asentado; "nunca fallar en
    silencio"): queda en la historia de la tarea (su auditoría), a la persona trabada se le dice
    que quedó asentado, sin que le llegue a nadie, y queda un incidente para el administrador
    (revisión `review-1db0e16dfeacfc4f`, `persecucion.py:550-559`)."""
    administrador(conn)
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = null where id = %s",
                    (mundo["area"],))
        cur.execute("update membership set aprobador_membership_id = null where id = %s",
                    (_membresia(mundo, "Marcos"),))
    conn.commit()
    _le_pregunto_a_ariel(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    [fila] = todos(conn, """select sujeto_tipo, detalle from audit_log
                             where accion = 'asentar_la_cadena_del_bloqueo'""")
    assert fila["sujeto_tipo"] == "blocker"
    assert fila["detalle"]["sin_a_quien_informar"] == "sin_referente"
    assert fila["detalle"]["cadena"][-1]["le_toca_a"] == "el proveedor"
    [incidente] = todos(conn, "select etapa, resumen_sanitizado from incident")
    assert incidente["etapa"] == "motor_sin_a_quien_informar"
    assert "Revisar el tablero" in incidente["resumen_sanitizado"]
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert "aviso_de_la_cadena" not in aviso["hechos"]
    assert aviso["hechos"]["queda_asentado"] == {
        "figura_en_el_informe_al_grupo": False,
        "solo_si_pregunta": {"no_le_llega_a_nadie": True}}


# --- Una sola vez, y sólo mientras siga trabada -------------------------------------------------

def test_el_aviso_al_referente_no_sale_si_ya_se_destrabo(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    [cadena] = avisos_guardados(conn, CADENA)
    assert (cadena["estado"], cadena["motivo_omision"]) == ("omitido", "ya_se_destrabo")


def test_la_cadena_le_llega_al_referente_una_sola_vez(conn, mundo, equipo):
    """El tercero que vuelve a decir que no le toca, después de que la cadena salió: la cadena no
    se le manda otra vez al referente, y los hechos dicen que ya le llegó (revisión del
    2026-10-09)."""
    _le_pregunto_a_juan(conn, mundo, equipo)
    equipo.dice("Juan", Jugada("decir_que_no_le_toca", {}))
    _salir(conn, mundo, AHORA + timedelta(minutes=130))
    equipo.minuto = 140

    r = equipo.dice("Juan", Jugada("decir_que_no_le_toca",
                                   {"lo_que_dice": "ya te dije que no es mio"}))

    # Lo que dijo queda anotado (sólo se agrega), pero la cadena no vuelve a salir.
    assert cuantas(conn, "dicho_de_quien_destraba", "dicho_por_membership_id = %s",
                   _membresia(mundo, "Juan")) == 2
    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["estado"] == "enviado"
    [hecho] = r.hechos
    assert hecho["aviso_de_la_cadena"]["a"] == "Ismael"
    assert hecho["aviso_de_la_cadena"]["llega"] == "ya_le_llego"
    assert cuantas(conn, "audit_log", "accion = 'informar_la_cadena_del_bloqueo'") == 1


def test_la_cadena_que_todavia_no_salio_sale_una_vez_con_lo_ultimo(conn, mundo, equipo):
    """Si el tercero vuelve a hablar antes de que la cadena salga, sale una sola, con lo último
    que dijo; la anterior queda omitida (nunca se borra)."""
    _le_pregunto_a_juan(conn, mundo, equipo)
    equipo.dice("Juan", Jugada("decir_que_no_le_toca", {}))

    equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"no_sabe": True,
                                                         "lo_que_dice": "ni idea"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=130))

    vieja, nueva = avisos_guardados(conn, CADENA)
    assert (vieja["estado"], vieja["motivo_omision"]) == ("omitido", "dijo_algo_mas_nuevo")
    assert nueva["estado"] == "enviado"
    assert nueva["hechos"]["cadena"][-1] == {"de": JUAN, "no_le_corresponde": True,
                                             "no_sabe": True, "lo_que_dice": "ni idea"}


def test_quien_quedo_nombrado_al_cortarse_no_manda_la_cadena_otra_vez(conn, mundo, equipo):
    """Pedro, nombrado por Juan cuando la cadena ya se cortó, ve la tarea en su lista; si dice
    que tampoco es suyo, la cadena no se le manda otra vez al referente."""
    _le_pregunto_a_juan(conn, mundo, equipo)
    equipo.dice("Juan", Jugada("decir_que_no_le_toca", {"quien": "pedro"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=130))
    equipo.minuto = 140

    equipo.dice("Pedro", Jugada("decir_que_no_le_toca", {"tarea": "T1"}))

    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["estado"] == "enviado"


def test_si_al_segundo_no_se_le_puede_escribir_la_cadena_va_al_referente(conn, mundo, equipo):
    """La primera nombra a alguien del equipo sin un chat con Leda: Leda no puede seguir con esa
    persona, así que la cadena se corta y le llega al referente, diciendo que a esa persona no
    se le puede escribir; nunca queda en silencio (revisión del 2026-10-09)."""
    _integrante(conn, mundo, "Nico", "Nico Sanchez", None)
    _le_pregunto_a_ariel(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "nico"}))

    # A Nico no se le guarda nada; quién destraba ahora es Nico, dicho por Ariel.
    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 1
    assert _destraban(conn)[-1]["destraba"] == _membresia(mundo, "Nico")
    # Al referente de la tarea (Ismael), la cadena y que a Nico no se le puede escribir.
    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert cadena["hechos"]["cadena"][-1] == {"de": ARIEL, "no_le_corresponde": True,
                                              "le_toca_a": "Nico Sanchez"}
    assert cadena["hechos"]["no_se_le_puede_escribir_a"] == {
        "a": "Nico Sanchez", "motivo": "destinatario_sin_telegram"}
    [hecho] = r.hechos
    assert hecho["no_se_le_puede_escribir_a"]["a"] == "Nico Sanchez"
    assert hecho["aviso_de_la_cadena"]["a"] == "Ismael"
    # A Marcos, que a Nico no se le puede escribir y que quedó asentado (decisión 35).
    [aviso] = avisos_guardados(conn, LO_QUE_DIJO)
    assert aviso["hechos"]["no_se_le_puede_escribir_a"]["a"] == "Nico Sanchez"
    assert aviso["hechos"]["queda_asentado"] == {"figura_en_el_informe_al_grupo": False,
                                                 "a": "Ismael"}


def test_el_aviso_al_referente_sale_como_informacion(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    ia = _salir(conn, mundo, AHORA + timedelta(minutes=45))

    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["estado"] == "enviado"
    [pedido] = [p for p in ia.pedidos_de_redaccion if p["persona"] == "Ismael"]
    assert pedido.get("pregunta") is None
    # Ismael no queda debiendo nada.
    assert cuantas(conn, "pending_reply", "membership_id = %s",
                   _membresia(mundo, "Ismael")) == 0


# --- Quién lo puede decir -----------------------------------------------------------------------

def test_quien_no_destraba_esa_tarea_no_puede_decir_que_no_le_toca(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)

    r = equipo.dice("Mariano", Jugada("decir_que_no_le_toca", {"quien": "juan"}))

    [hecho] = r.hechos
    assert hecho["resultado"] in ("no_se_puede", "falta_dato")
    assert cuantas(conn, "dicho_de_quien_destraba") == 0
    assert len(_destraban(conn)) == 1


# --- Nada de lo que dice se pierde ----------------------------------------------------------------

def test_lo_que_dijo_antes_de_nombrar_a_otro_no_se_pierde(conn, mundo, equipo):
    """Ariel dice algo al no tomarlo y algo más al nombrar a Mariano: quedan las dos cosas."""
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca",
                                {"lo_que_dice": "no me corresponde, yo no toco servidores"}))

    equipo.dice("Ariel", Jugada("decir_que_no_le_toca",
                                {"quien": "mariano", "lo_que_dice": "lo maneja mariano"}))

    dicho = uno(conn, "select lo_que_dice from dicho_de_quien_destraba")
    assert "no me corresponde, yo no toco servidores" in dicho["lo_que_dice"]
    assert "lo maneja mariano" in dicho["lo_que_dice"]


# --- El contrato con la IA ------------------------------------------------------------------

def test_la_jugada_nueva_tiene_sus_datos_y_sus_significados():
    ficha = FICHAS["decir_que_no_le_toca"]
    assert ficha.es and not ficha.se_ofrece
    assert set(ficha.opcional) == {"tarea", "quien", "no_sabe", "lo_que_dice"}
    for dato in ficha.opcional:
        assert dato in DATOS, dato
    assert "decir_que_no_le_toca" in hechos_mod.PARA_LA_REDACCION
    for codigo in (CADENA, "cadena", "no_le_corresponde", "le_toca_a", "quien_se_encarga",
                   "aviso_de_la_cadena", "nombrado_por", "sin_referente", QUIEN_MAS):
        assert hechos_mod.significado(codigo), codigo
    assert hechos_mod.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO["aviso_de_la_cadena"] == "a"


def test_la_pregunta_a_quien_esta_trabado_es_de_coordinacion_y_abre_su_pregunta():
    tipo = TIPOS[QUIEN_MAS]
    assert tipo.es_coordinacion and tipo.abre is not None
    assert tipo.tipo_de_mensaje == "normal"


# --- Las advertencias de la revisión de la C-5d ----------------------------------------------------

def test_si_nombra_a_alguien_de_afuera_la_cadena_queda_asentada(conn, mundo, equipo):
    """A la pregunta de si se le ocurre otra persona, Marcos nombra a alguien de afuera del equipo:
    Leda no le puede escribir, así que la cadena se corta y queda asentada (decisión 49), con lo
    que dijo, y Marcos se entera de que quedó asentado: nunca silencio (revisión de la C-5d,
    `fichas.py:895-898`)."""
    _ariel_no_sabe_y_se_lo_pregunto_a_marcos(conn, mundo, equipo)

    r = equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "el proveedor"}))

    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert cadena["hechos"]["cadena"] == [
        {"de": "Marcos", "le_toca_a": ARIEL},
        {"de": ARIEL, "no_le_corresponde": True, "no_sabe": True, "lo_que_dice": "ni idea"},
        {"de": "Marcos", "le_toca_a": "el proveedor"}]
    [hecho] = r.hechos
    assert hecho["quien_destraba"] == {"externo": "el proveedor"}
    assert hecho["queda_asentado"] == {"figura_en_el_informe_al_grupo": False, "a": "Ismael"}
    assert _su_pregunta(conn, mundo, "Marcos") is None


def test_quien_recibio_la_cadena_la_ve_en_su_lista(conn, mundo, equipo):
    """A quien le llegó la cadena (`para_destrabar`, revisión de la C-5d,
    `persecucion.py:509-516`) la ve como una tarea que se le informó que sigue trabada; no como
    una que espera que la destrabe."""
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=45))

    equipo.dice("Ismael", at=AHORA + timedelta(hours=2))

    [tarea] = [t for t in equipo.situacion["tareas"] if t.get("responsable") == "Marcos"]
    assert tarea["se_le_informo_que_sigue_trabada"] is True
    assert "espera_que_la_destrabe" not in tarea
    assert tarea["causa"] == CAUSA


def test_la_cadena_que_todavia_no_salio_no_la_pone_en_su_lista(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    equipo.dice("Ismael")

    assert not [t for t in equipo.situacion["tareas"] if t.get("responsable") == "Marcos"]


def test_la_cadena_no_pone_la_tarea_en_la_lista_de_otra_persona(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=45))

    equipo.dice("Pedro", at=AHORA + timedelta(hours=2))

    assert not [t for t in equipo.situacion["tareas"] if t.get("responsable") == "Marcos"]


def test_destrabada_la_tarea_sale_de_la_lista_de_quien_recibio_la_cadena(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=45))
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), at=AHORA + timedelta(hours=1))

    equipo.dice("Ismael", at=AHORA + timedelta(hours=2))

    assert not [t for t in equipo.situacion["tareas"]
                if t.get("responsable") == "Marcos" and t.get("se_le_informo_que_sigue_trabada")]
