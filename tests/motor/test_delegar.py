"""Delegar por chat (`leda.motor.pase`; C-7; ADR 0017, enmienda a la decisión 2; conversación 38).

Pasarle una tarea a otra persona, por chat, con las garantías de siempre: quien pide ve una vista
previa y la confirma (con el botón o escribiéndolo, con la guarda de la decisión 2); si decide otra
persona, Leda se lo pregunta; quien recibe confirma que la toma; recién entonces cambia el
responsable, y Leda le avisa a quien pidió y, si es otra persona, a quien decidió. Un "no" deja la
tarea donde estaba y se le dice a quien pidió. A Dirección no le llega nada. Lo que hace cumplir la
regla (quién pide, quién decide, qué tareas, las tres confirmaciones) es la cocina
(`tests/garantias/test_pase_de_tarea.py`); acá, la conversación del motor.

El mundo es el de las conversaciones (`tests.conversaciones.carga`), con Pedro, otro integrante
de OT, para el pase entre dos integrantes de un sector.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from leda.db import admin
from leda.motor import hechos, preguntas
from leda.motor.avisos import enviar_avisos
from leda.motor.ia import Jugada
from leda.motor.tiempo import RelojFijo

from tests.conversaciones.carga import cargar
from tests.motor.ayudantes import AHORA, IAQueRedacta, avisos_guardados, todos, uno
from tests.motor.test_aprobacion import Turnos

PASE_PARA_DECIDIR, PASE_PARA_TOMAR = "pase_para_decidir", "pase_para_tomar"
COMO_TERMINO = "como_termino_el_pase"
MARCOS, NAHUEL, LUCAS, MARTIN, PEDRO = ("Marcos Tarquini", "Nahuel Gimenez", "Lucas Natuche",
                                        "Martín Forte", "Pedro Paz")


@pytest.fixture
def equipo(conn) -> Turnos:
    """CoreWork en chico con una tarea de cada uno, y Pedro, otro integrante de OT."""
    mundo = cargar(conn, {"tareas": {
        "COM": {"titulo": "Revisar comunicaciones", "responsable": "Marcos",
                "vence": "2026-11-06"},
        "PLC": {"titulo": "Programar el PLC", "responsable": "Marcos", "vence": "2026-11-06",
                "estado": "en_curso", "desde": "2026-10-01"},
        "HMI": {"titulo": "Instalar el panel HMI", "responsable": "Marcos",
                "vence": "2026-11-06", "estado": "en_revision", "desde": "2026-10-01"},
        "SRV": {"titulo": "Instalar el servidor", "responsable": "Martin",
                "vence": "2026-11-06", "estado": "en_curso", "desde": "2026-10-01"},
        "SEN": {"titulo": "Calibrar los sensores", "responsable": "Nahuel",
                "vence": "2026-11-06"},
    }})
    with admin(conn) as cur:
        cur.execute("insert into app_user (telegram_user_id, nombre) values (70100, %s) "
                    "returning id", (PEDRO,))
        usuario = str(cur.fetchone()["id"])
        nahuel = mundo.personas["Nahuel"]
        cur.execute("select rol_id, aprobador_membership_id from membership where id = %s",
                    (nahuel["membership_id"],))
        fila = cur.fetchone()
        cur.execute("""insert into membership (workspace_id, app_user_id, area_id, rol_id,
                                               aprobador_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (mundo.workspace_id, usuario, nahuel["area_id"], fila["rol_id"],
                     fila["aprobador_membership_id"]))
        pedro = str(cur.fetchone()["id"])
        cur.execute("""insert into greeting_state (membership_id, workspace_id, ultima_fecha_local)
                       values (%s, %s, date '9999-12-31')""", (pedro, mundo.workspace_id))
    conn.commit()
    mundo.personas["Pedro"] = {"nombre": PEDRO, "app_user_id": usuario, "membership_id": pedro,
                               "telegram": 70100, "area_id": nahuel["area_id"], "area": "ot"}
    t = Turnos(conn, {"id": mundo.workspace_id, "personas": mundo.personas})
    t.carga = mundo
    return t


def _alias(t: Turnos, nombre: str, clave: str) -> str:
    """El alias de una tarea en la lista de esa persona (sus tareas y las que esperan algo de
    ella), leído de lo que recibiría la IA."""
    t.dice(nombre)
    titulo = t.carga.titulos[clave]
    return next(x["alias"] for x in t.situacion["tareas"] if x["titulo"] == titulo)


def _pedir(t: Turnos, nombre: str, clave: str, a: str):
    alias = _alias(t, nombre, clave)
    return t.dice(nombre, Jugada("pedir_reasignacion", {"tarea": alias, "a": a}))


def _quien_la_tiene(conn, t: Turnos, clave: str) -> str:
    fila = uno(conn, """select i.nombre from task t
                          join membership m on m.id = t.responsable_membership_id
                          join app_user i on i.id = m.app_user_id
                         where t.id = %s""", t.carga.tareas[clave])
    return fila["nombre"]


def _pases(conn) -> list[dict]:
    return todos(conn, "select * from pase_de_tarea order by pedido_en")


def _boton(conn, t: Turnos, nombre: str, etiqueta: str) -> str:
    fila = uno(conn, """select o.token from conversation_option o
                          join conversation_question q on q.id = o.question_id
                         where q.membership_id = %s and o.etiqueta = %s
                         order by q.abierta_en desc limit 1""",
               t.mundo["personas"][nombre]["membership_id"], etiqueta)
    return fila["token"]


def _salir(conn, t: Turnos, at) -> IAQueRedacta:
    ia = IAQueRedacta()
    enviar_avisos(conn, t.carga.workspace_id, ia, RelojFijo(at))
    conn.commit()
    return ia


# --- La vista previa y la confirmación de quien pide -------------------------------------------

def test_pedir_un_pase_muestra_la_vista_previa_y_no_cambia_nada(conn, equipo):
    r = _pedir(equipo, "Marcos", "COM", "nahuel")
    [hecho] = r.hechos
    assert hecho["resultado"] == "pase_para_confirmar"
    assert hecho["pase"] == {"la_tiene": MARCOS, "pasaria_a": NAHUEL}
    # Marcos es el encargado de OT: su pedido es la decisión; falta que Nahuel la tome.
    assert hecho["al_confirmar_el_pase"] == {"la_tiene_que_tomar": NAHUEL}
    assert hecho["pregunta"] == preguntas.CONFIRMAR_EL_PASE
    assert r.pregunta["tipo"] == preguntas.CONFIRMAR_EL_PASE
    assert [o["etiqueta"] for o in r.pregunta["opciones"]] == ["Confirmar"]
    assert _pases(conn) == []
    assert _quien_la_tiene(conn, equipo, "COM") == MARCOS
    # Un pase es una jugada de la lista: no se le avisa a la administración.
    assert todos(conn, "select * from incident") == []


def test_confirmarlo_escrito_en_otro_mensaje_pide_el_pase_y_le_pregunta_a_quien_recibe(conn,
                                                                                       equipo):
    _pedir(equipo, "Marcos", "COM", "nahuel")
    r = equipo.dice("Marcos", Jugada("confirmar", {}))
    [hecho] = r.hechos
    assert hecho["resultado"] == "pase_pedido"
    assert hecho["le_pregunta_a"]["a"] == NAHUEL
    [pase] = _pases(conn)
    assert pase["estado"] == "esperando_que_la_tome"
    [aviso] = avisos_guardados(conn, PASE_PARA_TOMAR)
    assert str(aviso["destinatario_membership_id"]) == equipo.mundo["personas"]["Nahuel"][
        "membership_id"]
    # Le llega terminado el margen para corregir (es por lo que pidió Marcos), y el hecho lo dice.
    assert aviso["programado_para"] > AHORA
    assert hecho["le_pregunta_a"]["llega"].startswith(
        aviso["programado_para"].astimezone(equipo_zona()).isoformat()[:16])
    assert aviso["hechos"]["pidio"] == MARCOS
    assert aviso["hechos"]["necesita_respuesta"] is True
    assert "tambien_lo_decide" not in aviso["hechos"]
    # Hasta que Nahuel la tome, sigue con Marcos.
    assert _quien_la_tiene(conn, equipo, "COM") == MARCOS


def equipo_zona():
    from zoneinfo import ZoneInfo
    return ZoneInfo("America/Argentina/Buenos_Aires")


def test_confirmar_en_el_mismo_mensaje_que_la_vista_previa_no_vale(conn, equipo):
    alias = _alias(equipo, "Marcos", "COM")
    r = equipo.dice("Marcos", Jugada("pedir_reasignacion", {"tarea": alias, "a": "nahuel"}),
                    Jugada("confirmar", {}))
    assert r.hechos[1]["resultado"] == "no_vale_la_confirmacion"
    assert _pases(conn) == []


def test_confirmarlo_con_el_boton_pide_el_pase(conn, equipo):
    _pedir(equipo, "Marcos", "COM", "nahuel")
    r = equipo.toca("Marcos", _boton(conn, equipo, "Marcos", "Confirmar"))
    assert r.hechos[0]["jugada"] == "confirmar"
    assert r.hechos[0]["resultado"] == "pase_pedido"
    assert len(_pases(conn)) == 1


def test_si_la_tarea_cambio_desde_la_vista_previa_la_confirmacion_no_vale(conn, equipo):
    _pedir(equipo, "Marcos", "COM", "nahuel")
    alias = _alias(equipo, "Marcos", "COM")
    equipo.dice("Marcos", Jugada("anotar_inicio", {"tarea": alias}))
    r = equipo.dice("Marcos", Jugada("confirmar", {}))
    assert r.hechos[0]["resultado"] == "no_vale_la_confirmacion"
    assert _pases(conn) == []


def test_dejar_la_vista_previa_sin_efecto_no_pide_nada(conn, equipo):
    _pedir(equipo, "Marcos", "COM", "nahuel")
    r = equipo.dice("Marcos", Jugada("cancelar", {}))
    assert r.hechos[0]["resultado"] == "cancelado"
    assert _pases(conn) == []


# --- Lo que no se puede ---------------------------------------------------------------------

def test_una_tarea_en_revision_no_se_pasa(conn, equipo):
    r = _pedir(equipo, "Marcos", "HMI", "nahuel")
    assert r.hechos[0]["resultado"] == "no_se_puede"
    assert r.hechos[0]["motivo"] == "estado"
    assert r.pregunta is None


def test_un_integrante_no_se_la_pasa_a_otro_sector_y_lo_decide_su_encargado(conn, equipo):
    r = _pedir(equipo, "Nahuel", "SEN", "lucas")
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"], hecho["quien_decide"]) == (
        "no_se_puede", "otro_sector", MARCOS)
    assert _pases(conn) == [] and avisos_guardados(conn) == []
    assert todos(conn, "select * from incident") == []


def test_alguien_que_no_es_del_equipo_o_la_misma_persona_no(conn, equipo):
    r = _pedir(equipo, "Marcos", "COM", "roberto")
    assert (r.hechos[0]["resultado"], r.hechos[0]["motivo"]) == ("no_se_puede",
                                                                 "persona_desconocida")
    r = _pedir(equipo, "Marcos", "COM", "marcos")
    assert r.hechos[0]["motivo"] == "es_la_misma_persona"


def test_sin_decir_a_quien_lo_pregunta(conn, equipo):
    alias = _alias(equipo, "Marcos", "COM")
    r = equipo.dice("Marcos", Jugada("pedir_reasignacion", {"tarea": alias}))
    assert (r.hechos[0]["resultado"], r.hechos[0]["falta"]) == ("falta_dato", ["a"])


def test_dos_pedidos_de_la_misma_tarea_no(conn, equipo):
    _pedir(equipo, "Marcos", "COM", "nahuel")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    r = _pedir(equipo, "Marcos", "COM", "pedro")
    assert r.hechos[0]["motivo"] == "ya_hay_un_pase"
    assert r.hechos[0]["pase"]["pasaria_a"] == NAHUEL


# --- Quien decide y quien recibe ------------------------------------------------------------

def test_entre_dos_integrantes_decide_su_encargado_y_despues_confirma_quien_recibe(conn,
                                                                                    equipo):
    _pedir(equipo, "Nahuel", "SEN", "pedro")
    r = equipo.dice("Nahuel", Jugada("confirmar", {}))
    assert r.hechos[0]["le_pregunta_a"]["a"] == MARCOS
    [aviso] = avisos_guardados(conn, PASE_PARA_DECIDIR)
    assert aviso["hechos"]["pasaria_a"] == PEDRO
    # Marcos ve la tarea en su lista, como un pase que espera su decisión.
    alias = _alias(equipo, "Marcos", "SEN")
    vista = next(x for x in equipo.situacion["tareas"] if x["alias"] == alias)
    assert vista["espera_su_decision_del_pase"] is True and vista["pidio"] == NAHUEL
    r = equipo.dice("Marcos", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}))
    assert r.hechos[0]["aprobo_el_pase"] is True
    assert r.hechos[0]["le_pregunta_a"]["a"] == PEDRO
    [aviso] = avisos_guardados(conn, PASE_PARA_TOMAR)
    assert aviso["hechos"]["lo_aprobo"] == MARCOS
    assert _quien_la_tiene(conn, equipo, "SEN") == NAHUEL
    alias = _alias(equipo, "Pedro", "SEN")
    r = equipo.dice("Pedro", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}))
    assert r.hechos[0]["la_toma"] is True
    assert _quien_la_tiene(conn, equipo, "SEN") == PEDRO
    # Le llega a quien pidió y a quien decidió, que son otras personas.
    assert {a["hechos"]["la_tomo"] for a in avisos_guardados(conn, COMO_TERMINO)} == {True}
    destinatarios = sorted(str(a["destinatario_membership_id"])
                           for a in avisos_guardados(conn, COMO_TERMINO))
    assert destinatarios == sorted([equipo.mundo["personas"]["Nahuel"]["membership_id"],
                                    equipo.mundo["personas"]["Marcos"]["membership_id"]])
    assert set(r.hechos[0]) >= {"aviso_a_quien_pidio", "aviso_a_quien_decidio"}


def test_si_quien_decide_dice_que_no_la_tarea_sigue_y_se_le_dice_a_quien_pidio(conn, equipo):
    _pedir(equipo, "Marcos", "PLC", "lucas")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    alias = _alias(equipo, "Martin", "PLC")
    r = equipo.dice("Martin", Jugada("contestar_el_pase", {"tarea": alias, "acepta": False,
                                                          "por_que": "lucas esta tapado"}))
    assert r.hechos[0]["aprobo_el_pase"] is False
    assert r.hechos[0]["sigue_con"] == MARCOS
    [aviso] = avisos_guardados(conn, COMO_TERMINO)
    assert aviso["hechos"]["no_lo_aprobo"] is True
    assert aviso["hechos"]["por_que"] == "lucas esta tapado"
    assert str(aviso["destinatario_membership_id"]) == equipo.mundo["personas"]["Marcos"][
        "membership_id"]
    assert avisos_guardados(conn, PASE_PARA_TOMAR) == []
    assert _quien_la_tiene(conn, equipo, "PLC") == MARCOS


def test_el_si_del_encargado_que_recibe_vale_por_las_dos_y_a_ismael_no_le_llega_nada(conn,
                                                                                      equipo):
    _pedir(equipo, "Martin", "SRV", "marcos")
    r = equipo.dice("Martin", Jugada("confirmar", {}))
    assert r.hechos[0]["le_pregunta_a"]["a"] == MARCOS
    [aviso] = avisos_guardados(conn, PASE_PARA_TOMAR)
    assert aviso["hechos"]["tambien_lo_decide"] is True
    alias = _alias(equipo, "Marcos", "SRV")
    r = equipo.dice("Marcos", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}))
    assert r.hechos[0]["la_toma"] is True and r.hechos[0]["tambien_lo_decidia"] is True
    assert "aviso_a_quien_decidio" not in r.hechos[0]
    assert _quien_la_tiene(conn, equipo, "SRV") == MARCOS
    ismael = equipo.mundo["personas"]["Ismael"]["membership_id"]
    assert [a for a in avisos_guardados(conn)
            if str(a["destinatario_membership_id"]) == ismael] == []


def test_quien_no_espera_nada_no_contesta_un_pase(conn, equipo):
    _pedir(equipo, "Marcos", "PLC", "lucas")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    # Lucas todavía no: lo decide Martín primero. Sin nada que contestar, lo dice.
    r = equipo.dice("Lucas", Jugada("contestar_el_pase", {"acepta": True}))
    assert (r.hechos[0]["resultado"], r.hechos[0]["motivo"]) == ("no_se_puede",
                                                                 "no_hay_un_pase")
    assert _quien_la_tiene(conn, equipo, "PLC") == MARCOS


# --- Lo que Leda manda: la pregunta, con sus botones, y cómo terminó -------------------------

def test_la_pregunta_a_quien_recibe_sale_con_dos_botones_y_tocar_la_tomo_la_pasa(conn, equipo):
    _pedir(equipo, "Marcos", "COM", "nahuel")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    [aviso] = avisos_guardados(conn, PASE_PARA_TOMAR)
    ia = _salir(conn, equipo, aviso["programado_para"] + timedelta(minutes=1))
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["pregunta"]["tipo"] == preguntas.TOMAR_LA_TAREA
    assert [o["etiqueta"] for o in pedido["pregunta"]["opciones"]] == ["La tomo", "No la tomo"]
    assert hechos.sin_significado(pedido) == set()
    r = equipo.toca("Nahuel", _boton(conn, equipo, "Nahuel", "La tomo"),
                    at=aviso["programado_para"] + timedelta(minutes=20))
    assert r.hechos[0]["la_toma"] is True
    assert _quien_la_tiene(conn, equipo, "COM") == NAHUEL
    [termino] = avisos_guardados(conn, COMO_TERMINO)
    ia = _salir(conn, equipo, termino["programado_para"] + timedelta(minutes=40))
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["pregunta"] is None
    assert hechos.sin_significado(pedido) == set()


def test_la_pregunta_a_quien_decide_ya_no_sale_si_el_pase_termino(conn, equipo):
    _pedir(equipo, "Marcos", "PLC", "lucas")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    alias = _alias(equipo, "Martin", "PLC")
    equipo.dice("Martin", Jugada("contestar_el_pase", {"tarea": alias, "acepta": False}))
    [aviso] = avisos_guardados(conn, PASE_PARA_DECIDIR)
    _salir(conn, equipo, aviso["programado_para"] + timedelta(minutes=40))
    fila = uno(conn, "select estado, motivo_omision from scheduled_notice where id = %s",
               aviso["id"])
    assert fila["estado"] == "omitido"


# --- Al cambiar de manos ------------------------------------------------------------------

def test_al_cambiar_de_manos_lo_que_esperaba_de_quien_la_tenia_pasa_a_quien_la_tiene(conn,
                                                                                    equipo):
    marcos = equipo.mundo["personas"]["Marcos"]["membership_id"]
    nahuel = equipo.mundo["personas"]["Nahuel"]["membership_id"]
    with admin(conn) as cur:
        # Un pedido de estado de la escalera, guardado para Marcos, que todavía no salió.
        cur.execute("""insert into scheduled_notice (workspace_id, tipo, task_id,
                                                     destinatario_membership_id, hechos,
                                                     programado_para, dedupe_key, creado_en)
                       values (%s, 'pedido_de_estado', %s, %s, '{}', %s, 'prueba:pedido', %s)""",
                    (equipo.carga.workspace_id, equipo.carga.tareas["COM"], marcos,
                     AHORA + timedelta(days=3), AHORA))
    conn.commit()
    _pedir(equipo, "Marcos", "COM", "nahuel")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    alias = _alias(equipo, "Nahuel", "COM")
    equipo.dice("Nahuel", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}))
    fila = uno(conn, "select destinatario_membership_id d from scheduled_notice "
                     "where dedupe_key = 'prueba:pedido'")
    assert str(fila["d"]) == nahuel
    # Lo que Leda le preguntaba a Marcos sobre esa tarea ya no espera nada de él.
    assert todos(conn, """select * from conversation_question
                           where membership_id = %s and task_id = %s and cerrada_en is null""",
                 marcos, equipo.carga.tareas["COM"]) == []
