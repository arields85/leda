"""El bloqueo viejo (`leda.motor.bloqueo_viejo`; C-5, porción 5; decisión 7 del usuario,
2026-10-08, opción A; mecánica §8; conversación 36).

Un bloqueo que sigue abierto a los días hábiles del espacio (`bloqueos.escala_solo_a_los_dias`;
5 si no está) se le informa al referente de la tarea, una sola vez, aunque la cadena se mueva,
con la historia y las fechas que dio cada uno; si el referente es la persona trabada, a quien
aprueba su trabajo. No le pide nada. Queda registrado a quién y cuándo. Uno que se cerró antes,
no; y al salir se vuelve a mirar.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from leda.db import admin
from leda.motor import hechos as hechos_mod
from leda.motor.avisos import TIPOS
from leda.motor.ia import Jugada

from tests.motor.ayudantes import (AHORA, administrador, avisos_guardados, cuantas, octubre,
                                   todos, uno)
from tests.motor.test_aprobacion import Turnos
from tests.motor.test_cadena_del_bloqueo import _integrante, _membresia, _referente

CAUSA = "me falta la ip del servidor"
VIEJO = "bloqueo_que_sigue_abierto"
ARIEL, LUCAS = "Ariel De Simone", "Lucas Natuche"


def _dias_del_espacio(conn, mundo, valor) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'bloqueos', %s)""", (mundo["id"], json.dumps(valor)))
    conn.commit()


@pytest.fixture
def equipo(conn, espacio_con_escalera) -> Turnos:
    """Ariel y Lucas; Lucas es el referente del área de la tarea de Marcos."""
    mundo = espacio_con_escalera
    _integrante(conn, mundo, "Ariel", ARIEL, 81_040)
    _integrante(conn, mundo, "Lucas", LUCAS, 81_041)
    _referente(conn, mundo["area"], _membresia(mundo, "Lucas"))
    return Turnos(conn, mundo)


def _marcos_trabado(t: Turnos) -> None:
    """Marcos se traba el lunes 5, dice que lo destraba Ariel, y Ariel da una fecha."""
    t.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    t.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "ariel"}))
    t.dice("Ariel", Jugada("decir_cuando_destraba",
                           {"tarea": "T1", "para_cuando": "2026-10-08",
                            "lo_que_dice": "te la paso el jueves"}))


def _viejos(conn) -> list[dict]:
    return avisos_guardados(conn, VIEJO)


def _para(dias, nombre: str) -> list[dict]:
    return [h for p in dias.ia.pedidos_de_redaccion if p["persona"] == nombre
            for h in p["hechos"] if h.get("aviso") == VIEJO]


def test_el_aviso_esta_declarado_con_su_significado():
    tipo = TIPOS[VIEJO]
    assert tipo.tipo_de_mensaje == "informativo" and not tipo.es_coordinacion
    for codigo in (VIEJO, "trabada_desde", "dias_habiles_trabada", "historia"):
        assert hechos_mod.significado(codigo), codigo


def test_a_los_dias_del_espacio_se_le_informa_una_vez_al_referente(conn, mundo, equipo, dias):
    _dias_del_espacio(conn, mundo, {"escala_solo_a_los_dias": 5})
    _marcos_trabado(equipo)

    # El viernes 9 lleva cuatro días hábiles (el lunes 12 es feriado): nada.
    dias.ciclo(octubre(9, 10))
    dias.ciclo(octubre(12, 10))
    assert _viejos(conn) == []

    # El martes 13, cinco: al referente del área, una vez, con la historia.
    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Lucas")
    assert aviso["estado"] == "enviado"
    [hechos] = _para(dias, LUCAS)
    assert hechos["necesita_respuesta"] is False
    assert (hechos["tarea"], hechos["responsable"], hechos["causa"]) == (
        "Revisar el tablero", "Marcos", CAUSA)
    assert hechos["trabada_desde"] == "2026-10-05"
    assert hechos["dias_habiles_trabada"] == 5
    assert hechos["historia"] == [
        {"el": "2026-10-05", "de": "Marcos", "le_toca_a": ARIEL},
        {"el": "2026-10-05", "de": ARIEL, "para_cuando": "2026-10-08",
         "lo_que_dice": "te la paso el jueves"}]
    # Queda registrado a quién y cuándo se informó, con su auditoría.
    bloqueo = uno(conn, "select escalado_a::text a, escalado_en from blocker")
    assert bloqueo == {"a": _membresia(mundo, "Lucas"), "escalado_en": octubre(13, 10)}
    assert cuantas(conn, "audit_log", "accion = 'informar_bloqueo_que_sigue_abierto'") == 1
    # Nada a Marcos por esto, y no se repite.
    assert _para(dias, "Marcos") == []
    dias.ciclo(octubre(14, 10))
    dias.ciclo(octubre(15, 10))
    assert len(_viejos(conn)) == 1


def test_aunque_la_cadena_se_mueva_se_informa(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-14",
                                 "lo_que_dice": "se me complico"}),
                at=octubre(12, 15))

    dias.ciclo(octubre(13, 10))

    [hechos] = _para(dias, LUCAS)
    assert hechos["historia"][-1] == {"el": "2026-10-12", "de": ARIEL,
                                      "para_cuando": "2026-10-14", "lo_que_dice": "se me complico"}


def test_si_el_referente_es_la_persona_trabada_va_a_quien_aprueba_su_trabajo(conn, mundo, equipo,
                                                                             dias):
    _referente(conn, mundo["area"], _membresia(mundo, "Marcos"))
    _marcos_trabado(equipo)

    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ismael")


def test_un_bloqueo_que_se_cerro_antes_no_se_informa(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), texto="ya la tengo",
                at=octubre(8, 11))

    dias.ciclo(octubre(13, 10))

    assert _viejos(conn) == []


@pytest.mark.parametrize("valor", [None, {"escala_solo_a_los_dias": 0},
                                   {"escala_solo_a_los_dias": "cinco"},
                                   {"escala_solo_a_los_dias": True}, ["5"]])
def test_sin_un_valor_valido_del_espacio_vale_el_del_producto(conn, mundo, equipo, dias, valor):
    if valor is not None:
        _dias_del_espacio(conn, mundo, valor)
    _marcos_trabado(equipo)

    dias.ciclo(octubre(9, 10))
    assert _viejos(conn) == []
    dias.ciclo(octubre(13, 10))
    assert len(_viejos(conn)) == 1


def test_los_dias_son_los_del_espacio(conn, mundo, equipo, dias):
    _dias_del_espacio(conn, mundo, {"escala_solo_a_los_dias": 2})
    _marcos_trabado(equipo)

    dias.ciclo(octubre(6, 10))
    assert _viejos(conn) == []
    dias.ciclo(octubre(7, 10))
    assert len(_viejos(conn)) == 1


def test_al_salir_se_vuelve_a_mirar(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    # Antes del horario se guarda para las 10:00; Marcos se destraba antes de que salga.
    dias.ciclo(octubre(13, 8))
    [aviso] = _viejos(conn)
    assert aviso["estado"] == "guardado"
    assert aviso["programado_para"] == octubre(13, 10)
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), texto="ya la tengo",
                at=octubre(13, 8, 30))

    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_se_destrabo")
    assert uno(conn, "select escalado_en from blocker")["escalado_en"] is None
    assert _para(dias, LUCAS) == []


def test_va_a_quien_es_referente_al_salir(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    dias.ciclo(octubre(13, 8))
    _integrante(conn, mundo, "Nico", "Nico Sanchez", 81_042)
    _referente(conn, mundo["area"], _membresia(mundo, "Nico"))

    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Nico")
    assert uno(conn, "select escalado_a::text a from blocker")["a"] == _membresia(mundo, "Nico")


def test_nunca_va_a_alguien_de_la_cadena(conn, mundo, equipo, dias):
    """Decisión 24 (C-5d): el referente de la tarea es Ariel, quien la destraba: va a quien
    aprueba el trabajo de Marcos (Ismael)."""
    _referente(conn, mundo["area"], _membresia(mundo, "Ariel"))
    _marcos_trabado(equipo)

    dias.ciclo(octubre(13, 10))

    [aviso] = _viejos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Ismael")
    [hechos] = _asentado_para(dias, "Marcos")
    assert hechos["queda_asentado"]["a"] == "Ismael"


# --- Se le cuenta a la persona trabada (decisión 34) y con la forma de la 35 ----------------------

A_LA_PERSONA = "asentado_que_sigue_trabada"


def _a_marcos(conn) -> list[dict]:
    return avisos_guardados(conn, A_LA_PERSONA)


def _asentado_para(dias, nombre: str) -> list[dict]:
    return [h for p in dias.ia.pedidos_de_redaccion if p["persona"] == nombre
            for h in p["hechos"] if h.get("aviso") == A_LA_PERSONA]


def test_el_aviso_a_la_persona_trabada_esta_declarado_con_su_significado():
    tipo = TIPOS[A_LA_PERSONA]
    # Seguimiento que Leda hace por su cuenta sobre el bloqueo de la persona: dentro del tope.
    assert tipo.tipo_de_mensaje == "informativo" and not tipo.es_coordinacion
    for codigo in (A_LA_PERSONA, "la_vez_anterior", "desde_la_vez_anterior"):
        assert hechos_mod.significado(codigo), codigo


def test_a_la_persona_trabada_se_le_dice_que_quedo_asentado(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)

    dias.ciclo(octubre(13, 10))

    [aviso] = _a_marcos(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["estado"] == "enviado"
    [hechos] = _asentado_para(dias, "Marcos")
    assert hechos["necesita_respuesta"] is False
    assert (hechos["tarea"], hechos["causa"]) == ("Revisar el tablero", CAUSA)
    assert hechos["trabada_desde"] == "2026-10-05"
    assert hechos["dias_habiles_trabada"] == 5
    # Quedó asentado; a quién le llegó, sólo si pregunta; sin informe al grupo, nada del equipo.
    assert hechos["queda_asentado"] == {"figura_en_el_informe_al_grupo": False, "a": LUCAS}
    redactado = hechos_mod.para_redactar(hechos)
    assert redactado["queda_asentado"] == {"figura_en_el_informe_al_grupo": False,
                                           "solo_si_pregunta": {"a": LUCAS}}
    assert LUCAS not in json.dumps({k: v for k, v in redactado["queda_asentado"].items()
                                    if k != "solo_si_pregunta"}, ensure_ascii=False)
    assert "historia" not in hechos         # un mensaje corto


def test_con_informe_al_grupo_el_equipo_esta_al_tanto(conn, mundo, equipo, dias):
    from tests.motor.test_asentado import informe_al_grupo
    informe_al_grupo(conn, mundo)
    _marcos_trabado(equipo)

    dias.ciclo(octubre(13, 10))

    [hechos] = _asentado_para(dias, "Marcos")
    assert hechos["queda_asentado"]["figura_en_el_informe_al_grupo"] is True


def test_a_la_persona_trabada_no_le_llega_si_se_destrabo_antes_de_salir(conn, mundo, equipo,
                                                                        dias):
    _marcos_trabado(equipo)
    dias.ciclo(octubre(13, 8))
    [aviso] = _a_marcos(conn)
    assert aviso["estado"] == "guardado"
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), texto="ya la tengo",
                at=octubre(13, 8, 30))

    dias.ciclo(octubre(13, 10))

    [aviso] = _a_marcos(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_se_destrabo")
    assert _asentado_para(dias, "Marcos") == []


def _sin_referente(conn, mundo) -> None:
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = null where id = %s",
                    (mundo["area"],))
        cur.execute("update membership set aprobador_membership_id = null")
    conn.commit()


def test_sin_nadie_a_quien_informar_queda_asentado_igual(conn, mundo, equipo, dias):
    """Sin a quién informar (decisión 49: dejar asentado es la historia de la tarea, quien
    decide, el informe al grupo y la persona trabada; "nunca fallar en silencio"): queda en la
    historia (su auditoría), a la persona trabada se le dice que quedó asentado, sin que le
    llegue a nadie, y queda un incidente para el administrador. Antes no pasaba nada."""
    administrador(conn)
    _marcos_trabado(equipo)
    _sin_referente(conn, mundo)

    dias.ciclo(octubre(13, 10))

    # A nadie le sale el aviso del referente; la vez queda contada, con su motivo.
    [viejo] = _viejos(conn)
    assert (viejo["estado"], viejo["motivo_omision"]) == ("omitido", "sin_a_quien_informar")
    assert uno(conn, "select escalado_a from blocker")["escalado_a"] is None
    [fila] = todos(conn, """select detalle from audit_log
                             where accion = 'asentar_bloqueo_que_sigue_abierto'""")
    assert fila["detalle"]["sin_a_quien_informar"] == "sin_referente"
    assert fila["detalle"]["vez"] == 1
    [incidente] = todos(conn, "select etapa, resumen_sanitizado from incident")
    assert incidente["etapa"] == "motor_sin_a_quien_informar"
    assert "Revisar el tablero" in incidente["resumen_sanitizado"]
    [aviso] = _a_marcos(conn)
    assert aviso["estado"] == "enviado"
    [hechos] = _asentado_para(dias, "Marcos")
    assert hechos["queda_asentado"] == {"figura_en_el_informe_al_grupo": False,
                                        "solo_si_pregunta": {"no_le_llega_a_nadie": True}}
    # Y no otra vez hasta los días del espacio desde esta vez.
    dias.ciclo(octubre(14, 10))
    assert len(_viejos(conn)) == 1 and len(_a_marcos(conn)) == 1


def test_si_el_referente_no_tiene_leda_conectada_queda_asentado_igual(conn, mundo, equipo, dias):
    administrador(conn)
    _marcos_trabado(equipo)
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (mundo["personas"]["Lucas"]["app_user_id"],))
    conn.commit()

    dias.ciclo(octubre(13, 10))

    [viejo] = _viejos(conn)
    assert (viejo["estado"], viejo["motivo_omision"]) == ("omitido", "sin_a_quien_informar")
    [fila] = todos(conn, """select detalle from audit_log
                             where accion = 'asentar_bloqueo_que_sigue_abierto'""")
    assert fila["detalle"]["sin_a_quien_informar"] == "destinatario_sin_telegram"
    assert cuantas(conn, "incident", "etapa = 'motor_sin_a_quien_informar'") == 1
    [hechos] = _asentado_para(dias, "Marcos")
    assert hechos["queda_asentado"]["solo_si_pregunta"] == {"no_le_llega_a_nadie": True}


def test_lo_que_se_le_dice_a_la_persona_trabada_ya_quedo_asentado(conn, mundo, equipo, dias):
    """Lo asentado queda en la historia al guardarse, no cuando le llega al referente: si Lucas
    está ausente y su aviso espera, a Marcos se le dice algo que ya es cierto (revisión
    `review-1db0e16dfeacfc4f`, `bloqueo_viejo.py:279-281`)."""
    _marcos_trabado(equipo)
    with admin(conn) as cur:
        cur.execute("""insert into absence (workspace_id, membership_id, desde, hasta)
                       values (%s, %s, '2026-10-13', '2026-10-14')""",
                    (mundo["id"], _membresia(mundo, "Lucas")))
    conn.commit()

    dias.ciclo(octubre(13, 10))

    [viejo] = _viejos(conn)
    assert viejo["estado"] == "guardado"            # Lucas está ausente: su aviso espera
    [aviso] = _a_marcos(conn)
    assert aviso["estado"] == "enviado"
    [fila] = todos(conn, """select detalle from audit_log
                             where accion = 'asentar_bloqueo_que_sigue_abierto'""")
    assert fila["detalle"]["a_membership_id"] == _membresia(mundo, "Lucas")
    assert "sin_a_quien_informar" not in fila["detalle"]


def test_si_el_aviso_al_referente_no_salio_no_se_dice_que_le_llega(conn, mundo, equipo, dias):
    """Constitución §4: el aviso a Lucas quedó `fallido` (la IA no lo redactó tras sus
    intentos) antes de que saliera el de Marcos. Si Marcos pregunta a quién le llegó, la verdad
    es que a nadie: no se nombra a Lucas (revisión `review-8d6e96daab3e588b`,
    `bloqueo_viejo.py:324-328`)."""
    _marcos_trabado(equipo)
    dias.ciclo(octubre(13, 8))                  # fuera del horario: los dos, guardados
    [viejo] = _viejos(conn)
    with admin(conn) as cur:
        cur.execute("""update scheduled_notice set estado = 'fallido', resuelto_en = %s
                        where id = %s""", (octubre(13, 8, 30), str(viejo["id"])))
    conn.commit()

    dias.ciclo(octubre(13, 10))

    [hechos] = _asentado_para(dias, "Marcos")
    assert hechos["queda_asentado"] == {"figura_en_el_informe_al_grupo": False,
                                        "solo_si_pregunta": {"no_le_llega_a_nadie": True}}


# --- Se vuelve a asentar mientras siga (decisión 36) ---------------------------------------------

def test_mientras_siga_trabada_se_vuelve_a_asentar_con_lo_que_paso_desde_la_vez_anterior(
        conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    dias.ciclo(octubre(13, 10))                 # la primera vez, a los cinco días hábiles
    equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-19",
                                 "lo_que_dice": "el lunes sin falta"}),
                at=octubre(15, 11))

    # Del martes 13 al lunes 19 van cuatro días hábiles: nada.
    for dia in (14, 15, 16, 19):
        dias.ciclo(octubre(dia, 10))
    assert len(_viejos(conn)) == 1 and len(_a_marcos(conn)) == 1

    # El martes 20, cinco desde la vez anterior: otra vez, al referente y a la persona trabada.
    dias.ciclo(octubre(20, 10))

    primera, segunda = _viejos(conn)
    assert segunda["estado"] == "enviado" and segunda["dedupe_key"] != primera["dedupe_key"]
    [_, hechos] = _para(dias, LUCAS)
    assert hechos["dias_habiles_trabada"] == 10
    assert hechos["la_vez_anterior"] == "2026-10-13"
    assert hechos["desde_la_vez_anterior"] == [
        {"el": "2026-10-15", "de": ARIEL, "para_cuando": "2026-10-19",
         "lo_que_dice": "el lunes sin falta"}]
    assert "historia" not in hechos
    assert len(_a_marcos(conn)) == 2
    [_, a_marcos] = _asentado_para(dias, "Marcos")
    assert a_marcos["dias_habiles_trabada"] == 10
    assert a_marcos["queda_asentado"]["figura_en_el_informe_al_grupo"] is False
    # Cada vez con su auditoría; el bloqueo guarda la primera vez que se informó.
    assert cuantas(conn, "audit_log", "accion = 'informar_bloqueo_que_sigue_abierto'") == 2
    assert uno(conn, "select escalado_en from blocker")["escalado_en"] == octubre(13, 10)
    # Y no antes de otros cinco.
    dias.ciclo(octubre(21, 10))
    assert len(_viejos(conn)) == 2


def test_sin_novedades_desde_la_vez_anterior_va_vacio(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)
    dias.ciclo(octubre(13, 10))

    dias.ciclo(octubre(20, 10))

    [_, hechos] = _para(dias, LUCAS)
    assert hechos["desde_la_vez_anterior"] == []


def test_si_la_vez_anterior_no_salio_no_se_guarda_otra(conn, mundo, equipo, dias):
    """Una vez guardada que todavía no salió (Lucas estaba ausente, el ciclo parado) sale con
    los hechos de su momento: no se guarda otra encima."""
    _marcos_trabado(equipo)
    from leda.motor.escalera import correr_escalera
    from leda.motor.tiempo import RelojFijo
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(13, 10)))
    conn.commit()
    correr_escalera(conn, mundo["id"], RelojFijo(octubre(20, 10)))
    conn.commit()

    [aviso] = _viejos(conn)
    assert aviso["estado"] == "guardado"


# --- Lo da por destrabado quien está trabado (decisión 41; C-5d) --------------------------------

YA_NO_HACE_FALTA = "ya_no_hace_falta_que_destrabe"
LO_QUE_DIJO = "lo_que_dijo_quien_destraba"


def _se_le_informo_a_lucas(equipo, dias) -> None:
    _marcos_trabado(equipo)
    dias.ciclo(octubre(13, 10))


def test_quien_recibio_el_bloqueo_viejo_lo_ve_en_su_lista(conn, mundo, equipo, dias):
    _se_le_informo_a_lucas(equipo, dias)

    equipo.dice("Lucas", at=octubre(13, 11))

    [tarea] = equipo.situacion["tareas"]
    assert tarea["se_le_informo_que_sigue_trabada"] is True
    assert "espera_que_la_destrabe" not in tarea
    assert (tarea["responsable"], tarea["causa"]) == ("Marcos", CAUSA)


def test_ya_esta_de_quien_recibio_el_bloqueo_viejo_se_anota_y_no_lo_cierra(conn, mundo, equipo,
                                                                           dias):
    _se_le_informo_a_lucas(equipo, dias)

    r = equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                    {"tarea": "T1", "ya_esta": True, "para_cuando": "2026-10-14",
                                     "lo_que_dice": "ya esta, llega mañana"}),
                    at=octubre(13, 11))

    # Queda anotado, dicho por Lucas, y Marcos se entera.
    dicho = uno(conn, """select ya_esta, para_cuando::text para_cuando,
                                dicho_por_membership_id::text de
                           from dicho_de_quien_destraba where dicho_por_membership_id = %s""",
                _membresia(mundo, "Lucas"))
    assert dicho == {"ya_esta": True, "para_cuando": "2026-10-14",
                     "de": _membresia(mundo, "Lucas")}
    aviso = avisos_guardados(conn, LO_QUE_DIJO)[-1]
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["hechos"]["quien_destraba"] == LUCAS
    assert aviso["hechos"]["dice_quien_destraba"]["ya_esta"] is True
    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["aviso_a_quien_esta_trabado"]["a"] == "Marcos"
    # El bloqueo sigue abierto hasta que Marcos diga que pudo seguir.
    assert cuantas(conn, "blocker", "resuelto_en is null") == 1
    assert uno(conn, "select estado::text e from task where titulo = 'Revisar el tablero'")[
        "e"] == "bloqueada"


def test_cuando_quien_esta_trabado_lo_destraba_se_enteran_los_que_dijeron_que_ya_esta(
        conn, mundo, equipo, dias):
    """Derivado de la regla 39: quien ya dijo "ya está" (Lucas) y quien había dado un día
    (Ariel) se enteran de que el bloqueo, por fin, se cerró."""
    _se_le_informo_a_lucas(equipo, dias)
    equipo.dice("Lucas", Jugada("decir_cuando_destraba", {"tarea": "T1", "ya_esta": True}),
                at=octubre(13, 11))

    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), texto="ya la tengo",
                at=octubre(14, 11))

    avisos = avisos_guardados(conn, YA_NO_HACE_FALTA)
    assert {str(a["destinatario_membership_id"]) for a in avisos} == {
        _membresia(mundo, "Lucas"), _membresia(mundo, "Ariel")}
    de_lucas = next(a for a in avisos
                    if str(a["destinatario_membership_id"]) == _membresia(mundo, "Lucas"))
    assert de_lucas["hechos"]["como_se_cerro"] == "ya_se_destrabo"
    assert de_lucas["hechos"]["habia_dicho"] == {"ya_esta": True}


def test_sin_nadie_que_lo_destrabe_lo_que_dice_queda_como_suyo(conn, mundo, equipo, dias):
    """Marcos nunca dijo quién lo destraba: lo que dice Lucas queda anotado igual, como que lo
    destraba él (dicho por él)."""
    equipo.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    dias.ciclo(octubre(13, 10))

    equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-14"}),
                at=octubre(13, 11))

    fila = uno(conn, """select destraba_membership_id::text destraba,
                               dicho_por_membership_id::text de from blocker_unblocker""")
    assert fila == {"destraba": _membresia(mundo, "Lucas"), "de": _membresia(mundo, "Lucas")}
    assert cuantas(conn, "dicho_de_quien_destraba") == 1
    assert avisos_guardados(conn, LO_QUE_DIJO)[-1]["hechos"]["quien_destraba"] == LUCAS
    assert cuantas(conn, "blocker", "resuelto_en is null") == 1


def test_quien_no_recibio_el_bloqueo_viejo_no_puede_decirlo(conn, mundo, equipo, dias):
    _marcos_trabado(equipo)

    r = equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                    {"tarea": "T1", "ya_esta": True}),
                    at=octubre(6, 11))

    assert r.hechos[0]["resultado"] in ("no_se_puede", "falta_dato")
    assert cuantas(conn, "dicho_de_quien_destraba", "dicho_por_membership_id = %s",
                   _membresia(mundo, "Lucas")) == 0
