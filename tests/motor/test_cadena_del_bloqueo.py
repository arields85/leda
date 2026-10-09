"""Quien destraba dice que no le corresponde (`leda.motor.persecucion`; C-5, porción 3; decisión 5
del usuario, 2026-10-08, opción A con límite; ADR 0017, decisión 3a, paso 4; ADR 0018, 9c, con la
precisión del 2026-10-09; conversación 34).

A quien Leda le pregunta por un bloqueo dice que no le toca. Si no dice de quién es, Leda le
pregunta una vez quién se encarga. Si nombra a otro integrante, Leda le escribe a esa persona como
le escribió a la primera, y la persona trabada se entera, como información. Si la segunda tampoco
lo toma (no le corresponde, no sabe o nombra a otra), o si la primera no sabe de quién es, Leda no
sigue: le informa la cadena entera al referente, sin pedirle nada (al del sector de lo que falta,
si se sabe; si no, al de la tarea trabada), y a la persona trabada le dice que lo informa, sin
nombrarlo por su cuenta (decisión 11).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor.fichas import FICHAS
from leda.motor.ia import Jugada
from leda.motor.ia_real import DATOS
from leda.motor.tiempo import RelojFijo

from tests.motor.ayudantes import AHORA, IAQueRedacta, avisos_guardados, cuantas, todos, uno
from tests.motor.test_aprobacion import Turnos

CAUSA = "me falta la ip del servidor"
PREGUNTA_A_QUIEN_DESTRABA = "pregunta_a_quien_destraba"
LO_QUE_DIJO = "lo_que_dijo_quien_destraba"
CADENA = "cadena_del_bloqueo"
ARIEL, MARIANO, JUAN = "Ariel De Simone", "Mariano Naim", "Juan Perez"


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
    """Ariel y Mariano, del área de la tarea (su referente es Ismael); Juan y Lucas, del taller,
    cuyo referente es Lucas. Todos con un chat con Leda."""
    _integrante(conn, mundo, "Ariel", ARIEL, 81_020)
    _integrante(conn, mundo, "Mariano", MARIANO, 81_021)
    taller = _area(conn, mundo, "taller")
    _integrante(conn, mundo, "Juan", JUAN, 81_022, area=taller)
    _integrante(conn, mundo, "Lucas", "Lucas Natuche", 81_023, area=taller)
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


def test_no_me_corresponde_dos_veces_sin_decir_de_quien_corta_la_cadena(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {}))

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["dice_quien_destraba"] == {"no_le_corresponde": True, "no_sabe": True}
    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")


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


# --- La cadena se corta: al referente ----------------------------------------------------------

def test_el_segundo_que_no_sabe_corta_la_cadena_y_va_al_referente_de_la_tarea(conn, mundo,
                                                                              equipo):
    _le_pregunto_a_mariano(conn, mundo, equipo)

    r = equipo.dice("Mariano", Jugada("decir_que_no_le_toca",
                                      {"no_sabe": True, "lo_que_dice": "ni idea"}))

    # No le escribe a nadie más.
    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 2
    assert _destraban(conn)[-1] == {"destraba": None, "destraba_externo": None, "no_sabe": True,
                                    "dicho_por": _membresia(mundo, "Mariano")}
    # Al referente del área de la tarea (Ismael), la cadena entera, como información.
    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert cadena["programado_para"] == AHORA + timedelta(minutes=61 + 10)
    hechos = cadena["hechos"]
    assert hechos["necesita_respuesta"] is False
    assert (hechos["tarea"], hechos["responsable"], hechos["causa"]) == (
        "Revisar el tablero", "Marcos", CAUSA)
    assert hechos["cadena"] == [
        {"de": "Marcos", "le_toca_a": ARIEL},
        {"de": ARIEL, "no_le_corresponde": True, "le_toca_a": MARIANO},
        {"de": MARIANO, "no_le_corresponde": True, "no_sabe": True, "lo_que_dice": "ni idea"}]
    assert cuantas(conn, "audit_log", "accion = 'informar_la_cadena_del_bloqueo'") == 1
    # A Marcos, que se informa, sin nombrar a quién por su cuenta.
    _de_ariel, aviso = avisos_guardados(conn, LO_QUE_DIJO)
    assert aviso["hechos"]["aviso_de_la_cadena"] == {"a": "Ismael"}
    redactado = hechos_mod.para_redactar(dict(aviso["hechos"]))
    assert "a" not in redactado["aviso_de_la_cadena"]
    assert redactado["aviso_de_la_cadena"]["solo_si_pregunta"]["a"] == "Ismael"
    [hecho] = r.hechos
    assert hecho["aviso_de_la_cadena"]["a"] == "Ismael"
    assert "se_le_pregunta_a" not in hecho
    # Nada se cierra ni se destraba.
    assert cuantas(conn, "blocker", "resuelto_en is null") == 1
    assert _su_pregunta(conn, mundo, "Mariano") is None


def test_el_segundo_que_nombra_a_otro_va_al_referente_del_sector_de_esa_persona(conn, mundo,
                                                                                 equipo):
    _le_pregunto_a_mariano(conn, mundo, equipo)

    equipo.dice("Mariano", Jugada("decir_que_no_le_toca", {"quien": "juan"}))

    # A Juan no le escribe: Leda no da más vueltas.
    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 2
    assert _destraban(conn)[-1]["destraba"] == _membresia(mundo, "Juan")
    # Va al referente del taller, el sector de quien quedó nombrado.
    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Lucas")
    assert cadena["hechos"]["cadena"][-1] == {"de": MARIANO, "no_le_corresponde": True,
                                              "le_toca_a": JUAN}


def test_el_segundo_que_solo_dice_que_no_le_corresponde_corta_la_cadena(conn, mundo, equipo):
    _le_pregunto_a_mariano(conn, mundo, equipo)

    r = equipo.dice("Mariano", Jugada("decir_que_no_le_toca", {}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["hechos"]["cadena"][-1] == {"de": MARIANO, "no_le_corresponde": True}
    # Quién destraba no cambia: Mariano no dijo de quién es.
    assert _destraban(conn)[-1]["destraba"] == _membresia(mundo, "Mariano")


def test_el_primero_que_no_sabe_de_quien_es_va_al_referente(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"no_sabe": True}))

    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 1
    [cadena] = avisos_guardados(conn, CADENA)
    assert str(cadena["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    assert cadena["hechos"]["cadena"] == [
        {"de": "Marcos", "le_toca_a": ARIEL},
        {"de": ARIEL, "no_le_corresponde": True, "no_sabe": True}]


def test_el_primero_que_nombra_a_alguien_de_afuera_va_al_referente(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"quien": "el proveedor"}))

    assert len(avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)) == 1
    assert _destraban(conn)[-1]["destraba_externo"] == "el proveedor"
    [cadena] = avisos_guardados(conn, CADENA)
    assert cadena["hechos"]["cadena"][-1] == {"de": ARIEL, "no_le_corresponde": True,
                                              "le_toca_a": "el proveedor"}


def test_si_el_referente_es_quien_esta_trabado_va_a_quien_aprueba_su_trabajo(conn, mundo,
                                                                              equipo):
    _referente(conn, mundo["area"], _membresia(mundo, "Marcos"))
    _le_pregunto_a_ariel(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"no_sabe": True}))

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

    r = equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"no_sabe": True}))

    assert avisos_guardados(conn, CADENA) == []
    [hecho] = r.hechos
    assert hecho["aviso_de_la_cadena"] == {"llega": "no_le_va_a_llegar",
                                           "motivo": "sin_referente"}


def test_el_aviso_al_referente_no_sale_si_ya_se_destrabo(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"no_sabe": True}))
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}))

    _salir(conn, mundo, AHORA + timedelta(minutes=90))

    [cadena] = avisos_guardados(conn, CADENA)
    assert (cadena["estado"], cadena["motivo_omision"]) == ("omitido", "ya_se_destrabo")


def test_el_aviso_al_referente_sale_como_informacion(conn, mundo, equipo):
    _le_pregunto_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("decir_que_no_le_toca", {"no_sabe": True}))

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


# --- El contrato con la IA ------------------------------------------------------------------

def test_la_jugada_nueva_tiene_sus_datos_y_sus_significados():
    ficha = FICHAS["decir_que_no_le_toca"]
    assert ficha.es and not ficha.se_ofrece
    assert set(ficha.opcional) == {"tarea", "quien", "no_sabe", "lo_que_dice"}
    for dato in ficha.opcional:
        assert dato in DATOS, dato
    assert "decir_que_no_le_toca" in hechos_mod.PARA_LA_REDACCION
    for codigo in (CADENA, "cadena", "no_le_corresponde", "le_toca_a", "quien_se_encarga",
                   "aviso_de_la_cadena", "nombrado_por", "sin_referente"):
        assert hechos_mod.significado(codigo), codigo
    assert hechos_mod.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO["aviso_de_la_cadena"] == "a"
