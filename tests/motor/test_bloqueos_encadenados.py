"""Los bloqueos encadenados y los avisos hacia abajo (`leda.motor.encadenados`; C-5, porción 4;
decisión 6 del usuario, 2026-10-08; conversación 35).

Marcos está trabado esperando algo de Ariel. Si Ariel se traba con la tarea que es lo que le falta
a Marcos (su tarea es la previa de la de Marcos, cargada por la plataforma, o Ariel lo dice al
contestar), los dos bloqueos quedan enlazados: la pregunta a Ariel por lo de Marcos ya tiene
respuesta, y Marcos, más abajo, se entera de cada avance del medio con avisos informativos (que
Ariel se trabó, lo que dice quien lo destraba, que pudo seguir, un día nuevo, que la entregó, que
quedó terminada). Sin el enlace, nada. Nunca se da por destrabada la tarea de Marcos.
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

from tests.motor.ayudantes import (AHORA, VIERNES_16, avisos_guardados, cuantas, estado_de,
                                   todos, uno)
from tests.motor.test_aprobacion import Turnos
from tests.motor.test_cadena_del_bloqueo import _integrante, _membresia, _salir, _su_pregunta

CAUSA = "me falta la ip del servidor"
SWITCH = "falta el switch nuevo"
SERVIDOR = "Configurar el servidor"
TABLERO = "Revisar el tablero"
NOVEDAD = "novedad_de_lo_que_espera"
LO_QUE_DIJO = "lo_que_dijo_quien_destraba"
PREGUNTA_A_QUIEN_DESTRABA = "pregunta_a_quien_destraba"
ARIEL, LUCAS, JUAN = "Ariel De Simone", "Lucas Natuche", "Juan Perez"


def _tarea_de(conn, mundo, quien: str, titulo: str, *, depende: str | None = None) -> str:
    """Una tarea en curso de otra persona, con su criterio; con `depende`, la tarea que espera a
    ésta (la dependencia que carga la plataforma)."""
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado, fecha_objetivo,
                                 criterio_aceptacion)
               values (%s, %s, %s, %s, %s, 'asignada', %s, %s) returning id""",
            (mundo["id"], mundo["objetivo"], titulo, mundo["area"], _membresia(mundo, quien),
             VIERNES_16, f"{titulo}: hecho y probado"))
        tarea = str(cur.fetchone()["id"])
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind, motivo, at)
                       values (%s, 'asignada', 'en_curso', 'persona', 'prueba', %s)""",
                    (tarea, AHORA - timedelta(days=3)))
        if depende is not None:
            cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id,
                                                   tipo)
                           values (%s, %s, %s, 'bloqueante')""", (mundo["id"], tarea, depende))
    conn.commit()
    return tarea


@pytest.fixture
def equipo(conn, mundo) -> Turnos:
    """Ariel, Lucas y Juan, con un chat con Leda; su trabajo lo aprueba Ismael."""
    _integrante(conn, mundo, "Ariel", ARIEL, 81_030)
    _integrante(conn, mundo, "Lucas", LUCAS, 81_031)
    _integrante(conn, mundo, "Juan", JUAN, 81_032)
    return Turnos(conn, mundo)


@pytest.fixture
def servidor(conn, mundo, equipo) -> str:
    """La tarea de Ariel, previa de la de Marcos (Marcos no puede seguir sin ella)."""
    return _tarea_de(conn, mundo, "Ariel", SERVIDOR, depende=mundo["tarea"])


def _marcos_espera_a_ariel(conn, mundo, t: Turnos) -> None:
    """Marcos se traba, dice que lo destraba Ariel y a Ariel le llega la pregunta."""
    t.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    t.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "ariel"}))
    _salir(conn, mundo, AHORA + timedelta(minutes=12))
    t.minuto = 30


def _ariel_se_traba(t: Turnos):
    """Ariel se traba con su tarea (la T1 de su lista) y dice que lo destraba Lucas."""
    r = t.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))
    t.dice("Ariel", Jugada("anotar_quien_destraba", {"quien": "lucas"}))
    return r


def _novedades(conn, persona: str | None = None) -> list[dict]:
    return [a for a in avisos_guardados(conn, NOVEDAD)
            if persona is None or str(a["destinatario_membership_id"]) == persona]


def _pedidos_para(ia, nombre: str, aviso: str) -> list[dict]:
    return [h for p in ia.pedidos_de_redaccion if p["persona"] == nombre
            for h in p["hechos"] if h.get("aviso") == aviso]


# --- La lista cerrada y el vocabulario --------------------------------------------------------

def test_el_aviso_y_el_dato_nuevos_estan_declarados_con_su_significado():
    assert TIPOS[NOVEDAD].es_coordinacion and TIPOS[NOVEDAD].tipo_de_mensaje == "informativo"
    assert "su_tarea_trabada" in FICHAS["decir_cuando_destraba"].opcional
    assert DATOS["su_tarea_trabada"][0] == "string"
    for codigo in (NOVEDAD, "esperando_a", "novedad", "se_trabo", "lo_destraba", "se_destrabo",
                   "la_entrego", "avisos_a_quienes_esperan", "aviso_a_quien_espera",
                   "su_tarea_trabada", "su_tarea_no_esta_trabada", "ya_no_espera_esa_tarea",
                   "no_se_entero_que_se_trabo"):
        assert hechos_mod.significado(codigo), codigo


# --- El enlace por la tarea previa ------------------------------------------------------------

def test_quien_destraba_se_traba_con_la_tarea_previa_y_quien_espera_se_entera(conn, mundo,
                                                                              servidor, equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)
    assert _su_pregunta(conn, mundo, "Ariel")["tipo"] == "cuando_se_destraba"

    r = equipo.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    [item] = hecho["avisos_a_quienes_esperan"]
    assert item["aviso_a_quien_espera"]["a"] == "Marcos"
    assert item["aviso_a_quien_espera"]["tarea"] == TABLERO
    # A Marcos, terminado el margen para corregir, que Ariel se trabó: información.
    [aviso] = _novedades(conn)
    assert str(aviso["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert aviso["programado_para"] == AHORA + timedelta(minutes=31 + 10)
    assert aviso["hechos"]["necesita_respuesta"] is False
    assert aviso["hechos"]["tarea"] == TABLERO and aviso["hechos"]["causa"] == CAUSA
    assert aviso["hechos"]["esperando_a"] == [{"de": ARIEL, "tarea": SERVIDOR}]
    assert aviso["hechos"]["novedad"] == {"de": ARIEL, "tarea": SERVIDOR,
                                          "se_trabo": {"causa": SWITCH}}
    # La pregunta a Ariel por lo de Marcos ya tiene respuesta: se cierra con su espera, y la que
    # sigue es quién lo destraba a él.
    assert _su_pregunta(conn, mundo, "Ariel")["tipo"] == "quien_destraba"
    assert cuantas(conn, "pending_reply", "membership_id = %s and tipo = 'cuando_se_destraba' "
                   "and satisfecho_en is null", _membresia(mundo, "Ariel")) == 0
    # La tarea de Marcos sigue trabada.
    assert estado_de(conn, mundo["tarea"]) == "bloqueada"


def test_al_salir_dice_quien_destraba_lo_de_ariel(conn, mundo, servidor, equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)
    _ariel_se_traba(equipo)

    ia = _salir(conn, mundo, AHORA + timedelta(minutes=70))

    [novedad] = _pedidos_para(ia, "Marcos", NOVEDAD)
    assert novedad["novedad"]["se_trabo"] == {"causa": SWITCH, "lo_destraba": LUCAS}
    [aviso] = _novedades(conn)
    assert aviso["estado"] == "enviado"


def test_sin_la_tarea_previa_no_se_enlazan(conn, mundo, equipo):
    _tarea_de(conn, mundo, "Ariel", SERVIDOR)
    _marcos_espera_a_ariel(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))

    assert "avisos_a_quienes_esperan" not in r.hechos[0]
    assert _novedades(conn) == []
    # La pregunta por lo de Marcos sigue sin contestar, con su espera: nada la contestó.
    assert cuantas(conn, "conversation_question", "membership_id = %s and tipo = "
                   "'cuando_se_destraba' and cerrada_en is null", _membresia(mundo, "Ariel")) == 1
    assert cuantas(conn, "pending_reply", "membership_id = %s and tipo = 'cuando_se_destraba' "
                   "and satisfecho_en is null", _membresia(mundo, "Ariel")) == 1


def test_si_la_destraba_otra_persona_no_se_enlazan(conn, mundo, servidor, equipo):
    equipo.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "lucas"}))

    equipo.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))

    assert _novedades(conn) == []


def test_si_se_traba_antes_de_que_le_llegue_la_pregunta_la_pregunta_no_sale(conn, mundo,
                                                                             servidor, equipo):
    equipo.dice("Marcos", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": CAUSA}))
    equipo.dice("Marcos", Jugada("anotar_quien_destraba", {"quien": "ariel"}))

    equipo.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))

    [pregunta] = avisos_guardados(conn, PREGUNTA_A_QUIEN_DESTRABA)
    assert (pregunta["estado"], pregunta["motivo_omision"]) == ("omitido", "ya_respondio")
    assert len(_novedades(conn)) == 1


# --- Los avances del medio --------------------------------------------------------------------

def test_lo_que_dice_quien_destraba_lo_de_ariel_le_llega_tambien_a_marcos(conn, mundo, servidor,
                                                                         equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)
    _ariel_se_traba(equipo)

    r = equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                    {"tarea": "T1", "para_cuando": "2026-10-08"}))

    # A Ariel, lo de siempre; a Marcos, el avance del medio.
    [a_ariel] = avisos_guardados(conn, LO_QUE_DIJO)
    assert str(a_ariel["destinatario_membership_id"]) == _membresia(mundo, "Ariel")
    _se_trabo, avance = _novedades(conn)
    assert str(avance["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert avance["hechos"]["novedad"] == {
        "de": ARIEL, "tarea": SERVIDOR, "quien_destraba": LUCAS,
        "dice_quien_destraba": {"para_cuando": "2026-10-08"}}
    [hecho] = r.hechos
    assert hecho["aviso_a_quien_esta_trabado"]["a"] == ARIEL
    [item] = hecho["avisos_a_quienes_esperan"]
    assert item["aviso_a_quien_espera"]["a"] == "Marcos"


def test_que_ariel_pudo_seguir_le_llega_a_marcos_y_su_tarea_sigue_trabada(conn, mundo, servidor,
                                                                         equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)
    _ariel_se_traba(equipo)

    r = equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}), texto="llego el switch")

    _se_trabo, destrabada = _novedades(conn)
    assert destrabada["hechos"]["novedad"] == {"de": ARIEL, "tarea": SERVIDOR,
                                               "se_destrabo": True}
    assert r.hechos[0]["avisos_a_quienes_esperan"][0]["aviso_a_quien_espera"]["a"] == "Marcos"
    assert estado_de(conn, mundo["tarea"]) == "bloqueada"
    assert cuantas(conn, "blocker", "task_id = %s and resuelto_en is null", mundo["tarea"]) == 1


def test_un_dia_nuevo_de_ariel_le_llega_a_marcos(conn, mundo, servidor, equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)
    _ariel_se_traba(equipo)
    equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}), texto="llego el switch")

    equipo.dice("Ariel", Jugada("anotar_prevision", {"tarea": "T1", "fecha": "2026-10-20",
                                                     "motivo": "se demoro el switch"}))

    dia = _novedades(conn)[-1]
    assert dia["hechos"]["novedad"] == {"de": ARIEL, "tarea": SERVIDOR,
                                        "prevision": "2026-10-20"}


def test_que_ariel_la_entrego_y_quedo_terminada_le_llega_a_marcos(conn, mundo, servidor,
                                                                  equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)

    equipo.dice("Ariel", Jugada("entregar", {"tarea": "T1", "lo_descrito_cubre": ["C1"]}),
                texto="termine, quedo configurado y probado")
    equipo.dice("Ariel", Jugada("confirmar", {}), texto="dale")

    assert estado_de(conn, servidor) == "en_revision"
    [entregada] = _novedades(conn)
    assert entregada["hechos"]["novedad"] == {"de": ARIEL, "tarea": SERVIDOR, "la_entrego": True}

    at = AHORA + timedelta(hours=2)
    equipo.dice("Ismael", Jugada("aprobar", {"tarea": "T1"}), texto="aprobado", at=at)

    assert estado_de(conn, servidor) == "terminada"
    terminada = _novedades(conn)[-1]
    assert terminada["hechos"]["novedad"] == {"de": ARIEL, "tarea": SERVIDOR,
                                              "quedo_terminada": True}
    # Una decisión no se corrige por chat: sale enseguida, sin el margen (decisión 19).
    assert terminada["programado_para"] == at
    assert estado_de(conn, mundo["tarea"]) == "bloqueada"


# --- La cadena entera ------------------------------------------------------------------------

def test_quien_esta_mas_lejos_se_entera_de_cada_avance_del_medio(conn, mundo, equipo):
    # Juan espera a Marcos, Marcos a Ariel, Ariel a Lucas.
    juan = _tarea_de(conn, mundo, "Juan", "Montar el gabinete")
    with admin(conn) as cur:
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id,
                                               tipo)
                       values (%s, %s, %s, 'bloqueante')""", (mundo["id"], mundo["tarea"], juan))
    conn.commit()
    _tarea_de(conn, mundo, "Ariel", SERVIDOR, depende=mundo["tarea"])
    equipo.dice("Juan", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el tablero"}))
    equipo.dice("Juan", Jugada("anotar_quien_destraba", {"quien": "marcos"}))
    _marcos_espera_a_ariel(conn, mundo, equipo)
    _ariel_se_traba(equipo)

    equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-08"}))

    a_marcos = _novedades(conn, _membresia(mundo, "Marcos"))[-1]
    a_juan = _novedades(conn, _membresia(mundo, "Juan"))[-1]
    assert a_marcos["hechos"]["esperando_a"] == [{"de": ARIEL, "tarea": SERVIDOR}]
    assert a_juan["hechos"]["esperando_a"] == [{"de": "Marcos", "tarea": TABLERO},
                                              {"de": ARIEL, "tarea": SERVIDOR}]
    assert a_juan["hechos"]["novedad"]["quien_destraba"] == LUCAS
    assert a_juan["hechos"]["tarea"] == "Montar el gabinete"
    # A Lucas, que lo dijo, nada de esto.
    assert _novedades(conn, _membresia(mundo, "Lucas")) == []


def test_a_quien_hizo_el_avance_no_le_llega_su_propio_avance(conn, mundo, servidor, equipo):
    # Lucas espera a Ariel (la tarea de Ariel es la previa de la suya) y destraba a Ariel.
    lucas = _tarea_de(conn, mundo, "Lucas", "Instalar el rack")
    with admin(conn) as cur:
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id,
                                               tipo)
                       values (%s, %s, %s, 'bloqueante')""", (mundo["id"], servidor, lucas))
    conn.commit()
    equipo.dice("Lucas", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": "falta el servidor"}))
    equipo.dice("Lucas", Jugada("anotar_quien_destraba", {"quien": "ariel"}))
    _ariel_se_traba(equipo)
    antes = len(_novedades(conn, _membresia(mundo, "Lucas")))

    r = equipo.dice("Lucas", Jugada("decir_cuando_destraba", {"tarea": "T2", "ya_esta": True}))

    assert r.hechos[0]["resultado"] == "anotado"
    assert len(_novedades(conn, _membresia(mundo, "Lucas"))) == antes


# --- El enlace dicho por quien destraba -------------------------------------------------------

def test_quien_destraba_dice_que_esta_trabado_con_una_tarea_suya_y_los_enlaza(conn, mundo,
                                                                             equipo):
    _tarea_de(conn, mundo, "Ariel", SERVIDOR)          # sin la dependencia
    _ariel_se_traba(equipo)
    _marcos_espera_a_ariel(conn, mundo, equipo)
    equipo.minuto = 60

    # En la lista de Ariel: su tarea (T1) y la de Marcos, que destraba (T2).
    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"tarea": "T2", "su_tarea_trabada": "T1",
                                     "lo_que_dice": "sigo parado con el servidor"}))

    [hecho] = r.hechos
    assert hecho["resultado"] == "anotado"
    assert hecho["dice_quien_destraba"]["su_tarea_trabada"] == {
        "tarea": SERVIDOR, "causa": SWITCH, "lo_destraba": LUCAS}
    dicho = uno(conn, """select d.espera_su_bloqueo_id::text bloqueo, b.task_id::text tarea
                           from dicho_de_quien_destraba d
                           join blocker b on b.id = d.espera_su_bloqueo_id""")
    assert dicho["tarea"] != mundo["tarea"]
    [a_marcos] = avisos_guardados(conn, LO_QUE_DIJO)
    assert a_marcos["hechos"]["dice_quien_destraba"]["su_tarea_trabada"]["lo_destraba"] == LUCAS
    assert cuantas(conn, "audit_log", "accion = 'anotar_lo_que_dice_quien_destraba'") == 1

    # Lo que dice Lucas de lo de Ariel ahora le llega también a Marcos.
    equipo.dice("Lucas", Jugada("decir_cuando_destraba",
                                {"tarea": "T1", "para_cuando": "2026-10-08"}))
    [avance] = _novedades(conn)
    assert str(avance["destinatario_membership_id"]) == _membresia(mundo, "Marcos")
    assert avance["hechos"]["esperando_a"] == [{"de": ARIEL, "tarea": SERVIDOR}]


def test_una_tarea_suya_que_no_esta_trabada_no_se_anota_asi(conn, mundo, equipo):
    _tarea_de(conn, mundo, "Ariel", SERVIDOR)
    _marcos_espera_a_ariel(conn, mundo, equipo)

    r = equipo.dice("Ariel", Jugada("decir_cuando_destraba",
                                    {"tarea": "T2", "su_tarea_trabada": "T1"}))

    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "su_tarea_no_esta_trabada")
    assert hecho["su_tarea_trabada"]["titulo"] == SERVIDOR
    assert cuantas(conn, "dicho_de_quien_destraba") == 0
    assert avisos_guardados(conn, LO_QUE_DIJO) == []


# --- Al salir se vuelve a mirar ---------------------------------------------------------------

def test_si_marcos_ya_no_espera_el_aviso_no_sale(conn, mundo, servidor, equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))
    equipo.dice("Marcos", Jugada("destrabar", {"tarea": "T1"}), texto="ya consegui la ip")

    _salir(conn, mundo, AHORA + timedelta(minutes=80))

    [aviso] = _novedades(conn)
    assert (aviso["estado"], aviso["motivo_omision"]) == ("omitido", "ya_no_espera_esa_tarea")


def test_trabado_y_destrabado_dentro_del_margen_no_le_llega_nada(conn, mundo, servidor, equipo):
    _marcos_espera_a_ariel(conn, mundo, equipo)
    equipo.dice("Ariel", Jugada("anotar_bloqueo", {"tarea": "T1", "causa": SWITCH}))
    equipo.dice("Ariel", Jugada("destrabar", {"tarea": "T1"}), texto="no, ya llego")

    _salir(conn, mundo, AHORA + timedelta(minutes=80))

    se_trabo, se_destrabo = _novedades(conn)
    assert (se_trabo["estado"], se_trabo["motivo_omision"]) == ("omitido", "ya_se_destrabo")
    assert (se_destrabo["estado"], se_destrabo["motivo_omision"]) == (
        "omitido", "no_se_entero_que_se_trabo")
    assert todos(conn, """select 1 from message_outbox
                           where chat_id = %s and not es_respuesta""",
                 mundo["personas"]["Marcos"]["telegram"]) == []
