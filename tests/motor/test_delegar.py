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

def test_a_quien_no_tiene_leda_conectada_no_se_le_pasa_y_se_avisa_al_administrador(conn, equipo):
    """Un pase a alguien sin Leda conectada sigue la decisión 37 (derivada en la 50): a quien
    pide se le dice, el administrador recibe el aviso para conectarlo (de verdad, por su canal) y
    Leda ofrece pasársela a otra persona. Nada cambia."""
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (equipo.mundo["personas"]["Nahuel"]["app_user_id"],))
    conn.commit()

    r = _pedir(equipo, "Marcos", "COM", "nahuel")

    [hecho] = r.hechos
    assert hecho["resultado"] == "no_se_puede"
    assert hecho["no_se_le_puede_escribir_a"] == {"a": NAHUEL,
                                                  "motivo": "destinatario_sin_telegram"}
    assert hecho["se_le_aviso_al_administrador"]["para_que_conecte"] == NAHUEL
    assert hecho["se_le_aviso_al_administrador"]["llega"] != "no_le_va_a_llegar"
    assert hecho["en_cambio_puede"] == ["pasarsela_a_otra_persona"]
    assert hechos.significado("pasarsela_a_otra_persona")
    [incidente] = todos(conn, "select etapa, resumen_sanitizado from incident")
    assert incidente["etapa"] == "motor_sin_leda_conectada"
    assert NAHUEL in incidente["resumen_sanitizado"]
    assert uno(conn, "select count(*) n from admin_notice")["n"] == 1
    assert _pases(conn) == []
    assert _quien_la_tiene(conn, equipo, "COM") == MARCOS


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


def _aprobado_por_marcos(conn, equipo) -> None:
    """Nahuel pide pasarle los sensores a Pedro y Marcos, que decide, lo aprueba."""
    _pedir(equipo, "Nahuel", "SEN", "pedro")
    equipo.dice("Nahuel", Jugada("confirmar", {}))
    alias = _alias(equipo, "Marcos", "SEN")
    equipo.dice("Marcos", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}))


def _a_quienes_les_llega_como_termino(conn, equipo) -> dict[str, dict]:
    personas = {p["membership_id"]: corto for corto, p in equipo.mundo["personas"].items()}
    return {personas[str(a["destinatario_membership_id"])]: a["hechos"]
            for a in avisos_guardados(conn, COMO_TERMINO)}


def test_si_quien_recibe_no_la_toma_tambien_se_entera_quien_lo_aprobo(conn, equipo):
    """Decisión 39: quien autorizó el pase también sabe cómo terminó, no sólo cuando la tomaron."""
    _aprobado_por_marcos(conn, equipo)
    alias = _alias(equipo, "Pedro", "SEN")

    r = equipo.dice("Pedro", Jugada("contestar_el_pase", {"tarea": alias, "acepta": False}))

    avisos = _a_quienes_les_llega_como_termino(conn, equipo)
    assert set(avisos) == {"Nahuel", "Marcos"}
    assert avisos["Marcos"]["la_tomo"] is False and avisos["Marcos"]["la_tiene"] == NAHUEL
    assert set(r.hechos[0]) >= {"aviso_a_quien_pidio", "aviso_a_quien_decidio"}


def test_si_quien_recibe_no_contesta_tambien_se_entera_quien_lo_aprobo(conn, equipo):
    _aprobado_por_marcos(conn, equipo)
    [pregunta] = avisos_guardados(conn, PASE_PARA_TOMAR)
    _salir(conn, equipo, pregunta["programado_para"] + timedelta(minutes=1))
    _escalera(conn, equipo, AHORA + timedelta(days=1))
    _salir(conn, equipo, AHORA + timedelta(days=1, minutes=5))

    _escalera(conn, equipo, AHORA + timedelta(days=2))

    assert _pases(conn)[0]["estado"] == "sin_respuesta"
    avisos = _a_quienes_les_llega_como_termino(conn, equipo)
    assert set(avisos) == {"Nahuel", "Marcos", "Pedro"}
    assert avisos["Marcos"]["sin_respuesta"] is True
    assert "no_contesto" not in avisos["Marcos"]
    assert avisos["Pedro"]["ya_no_espera_su_respuesta"] is True


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


# --- Un pase que nadie contesta (decisión 26) ------------------------------------------------

RECORDATORIO_DEL_PASE = "recordatorio_del_pase"


def _escalera(conn, t: Turnos, at) -> dict:
    from leda.motor.escalera import correr_escalera
    resumen = correr_escalera(conn, t.carga.workspace_id, RelojFijo(at))
    conn.commit()
    return resumen


def test_un_pase_que_nadie_contesta_se_repite_una_vez_y_despues_termina(conn, equipo):
    # Marcos le pasa el PLC a Lucas; decide Martín, que no contesta.
    _pedir(equipo, "Marcos", "PLC", "lucas")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    [pregunta] = avisos_guardados(conn, PASE_PARA_DECIDIR)
    _salir(conn, equipo, pregunta["programado_para"] + timedelta(minutes=1))
    # El mismo día no se repite.
    _escalera(conn, equipo, AHORA + timedelta(hours=6))
    assert avisos_guardados(conn, RECORDATORIO_DEL_PASE) == []
    # El día hábil siguiente (martes 6), una sola vez, a Martín.
    martes = AHORA + timedelta(days=1)
    _escalera(conn, equipo, martes)
    _escalera(conn, equipo, martes + timedelta(hours=1))
    [repite] = avisos_guardados(conn, RECORDATORIO_DEL_PASE)
    assert str(repite["destinatario_membership_id"]) == equipo.mundo["personas"]["Martin"][
        "membership_id"]
    assert repite["hechos"]["pregunta"] == preguntas.DECIDIR_EL_PASE
    assert repite["hechos"]["pasaria_a"] == LUCAS
    assert repite["hechos"]["si_sigue_sin_contestar"] == {"sigue_con": MARCOS,
                                                          "fecha": "2026-10-07"}
    ia = _salir(conn, equipo, martes + timedelta(minutes=5))
    [pedido] = ia.pedidos_de_redaccion
    assert pedido["pregunta"]["tipo"] == preguntas.DECIDIR_EL_PASE
    assert pedido["pregunta"]["desde_antes"] is True
    assert hechos.sin_significado(pedido) == set()
    assert _pases(conn)[0]["estado"] == "esperando_decision"
    # Sigue sin contestar: al día hábil siguiente (miércoles 7) el pase termina, la tarea sigue
    # con Marcos y Leda se lo dice.
    miercoles = martes + timedelta(days=1)
    _escalera(conn, equipo, miercoles - timedelta(hours=4))
    assert _pases(conn)[0]["estado"] == "esperando_decision"
    _escalera(conn, equipo, miercoles)
    assert _pases(conn)[0]["estado"] == "sin_respuesta"
    assert _quien_la_tiene(conn, equipo, "PLC") == MARCOS
    personas = equipo.mundo["personas"]
    avisos = {str(a["destinatario_membership_id"]): a["hechos"]
              for a in avisos_guardados(conn, COMO_TERMINO)}
    assert set(avisos) == {personas["Marcos"]["membership_id"],
                           personas["Martin"]["membership_id"]}
    a_marcos = avisos[personas["Marcos"]["membership_id"]]
    assert a_marcos["sin_respuesta"] is True
    assert a_marcos["no_contesto"] == MARTIN
    assert a_marcos["la_tiene"] == MARCOS
    assert a_marcos["puede_pedirselo_a_otra_persona"] is True
    # Decisión 39: Martín, a quien Leda le preguntaba, también se entera de que terminó y de que ya
    # no hace falta que conteste, sin un reproche; y Leda deja de preguntarle (sus botones, también).
    a_martin = avisos[personas["Martin"]["membership_id"]]
    assert a_martin["sin_respuesta"] is True and a_martin["ya_no_espera_su_respuesta"] is True
    assert a_martin["pidio"] == MARCOS and a_martin["la_tiene"] == MARCOS
    assert "no_contesto" not in a_martin and "puede_pedirselo_a_otra_persona" not in a_martin
    assert _preguntas_del_pase_abiertas(conn, equipo, "Martin") == []
    ia = _salir(conn, equipo, miercoles + timedelta(minutes=5))
    assert len(ia.pedidos_de_redaccion) == 2
    assert all(hechos.sin_significado(p) == set() for p in ia.pedidos_de_redaccion)
    # Nada más: ni otra repetición ni otro aviso.
    _escalera(conn, equipo, miercoles + timedelta(days=1))
    assert len(avisos_guardados(conn, RECORDATORIO_DEL_PASE)) == 1
    assert len(avisos_guardados(conn, COMO_TERMINO)) == 2
    # Si Martín contesta tarde, no hay nada que contestar.
    r = equipo.dice("Martin", Jugada("contestar_el_pase", {"acepta": True}),
                    at=miercoles + timedelta(hours=1))
    assert (r.hechos[0]["resultado"], r.hechos[0]["motivo"]) == ("no_se_puede",
                                                                 "no_hay_un_pase")


def test_la_repeticion_de_un_pase_es_a_quien_tiene_que_tomarla(conn, equipo):
    _pedir(equipo, "Marcos", "COM", "nahuel")
    equipo.dice("Marcos", Jugada("confirmar", {}))
    [pregunta] = avisos_guardados(conn, PASE_PARA_TOMAR)
    _salir(conn, equipo, pregunta["programado_para"] + timedelta(minutes=1))
    _escalera(conn, equipo, AHORA + timedelta(days=1, hours=-1))
    [repite] = avisos_guardados(conn, RECORDATORIO_DEL_PASE)
    assert str(repite["destinatario_membership_id"]) == equipo.mundo["personas"]["Nahuel"][
        "membership_id"]
    assert repite["hechos"]["pregunta"] == preguntas.TOMAR_LA_TAREA
    # Nahuel la toma antes de que salga: la repetición ya no sale.
    alias = _alias(equipo, "Nahuel", "COM")
    equipo.dice("Nahuel", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}),
                at=AHORA + timedelta(days=1, minutes=-10))
    _salir(conn, equipo, AHORA + timedelta(days=1, minutes=40))
    fila = uno(conn, "select estado from scheduled_notice where id = %s", repite["id"])
    assert fila["estado"] == "omitido"


# --- El encargado pasa una tarea de su gente (decisión 27) -----------------------------------

def test_el_encargado_pasa_la_de_alguien_de_su_sector_nombrandola(conn, equipo):
    r = equipo.dice("Marcos", Jugada("pedir_reasignacion",
                                     {"como_la_nombra": "sensores de Nahuel", "a": "pedro"}))
    [hecho] = r.hechos
    assert hecho["resultado"] == "pase_para_confirmar"
    assert hecho["pase"] == {"la_tiene": NAHUEL, "pasaria_a": PEDRO}
    assert hecho["tarea"]["titulo"] == "Calibrar los sensores"
    assert hecho["al_confirmar_el_pase"] == {"la_tiene_que_tomar": PEDRO}
    assert _pases(conn) == []
    r = equipo.dice("Marcos", Jugada("confirmar", {}))
    assert r.hechos[0]["resultado"] == "pase_pedido"
    assert r.hechos[0]["le_pregunta_a"]["a"] == PEDRO
    [pase] = _pases(conn)
    assert str(pase["de_membership_id"]) == equipo.mundo["personas"]["Nahuel"]["membership_id"]
    [aviso] = avisos_guardados(conn, PASE_PARA_TOMAR)
    assert aviso["hechos"]["la_tiene"] == NAHUEL and aviso["hechos"]["pidio"] == MARCOS
    alias = _alias(equipo, "Pedro", "SEN")
    equipo.dice("Pedro", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}))
    assert _quien_la_tiene(conn, equipo, "SEN") == PEDRO
    # A Marcos, que lo pidió, y a Nahuel, que la tenía: su tarea pasó a Pedro.
    avisos = {str(a["destinatario_membership_id"]): a["hechos"]
              for a in avisos_guardados(conn, COMO_TERMINO)}
    personas = equipo.mundo["personas"]
    assert set(avisos) == {personas["Marcos"]["membership_id"],
                           personas["Nahuel"]["membership_id"]}
    a_nahuel = avisos[personas["Nahuel"]["membership_id"]]
    assert a_nahuel["la_tomo"] is True and a_nahuel["era_suya"] is True
    assert a_nahuel["la_tiene"] == PEDRO and a_nahuel["pidio"] == MARCOS
    ia = _salir(conn, equipo, AHORA + timedelta(hours=2))
    assert ia.pedidos_de_redaccion
    assert all(hechos.sin_significado(p) == set() for p in ia.pedidos_de_redaccion)


def test_el_encargado_de_otro_sector_no_pasa_la_de_nahuel(conn, equipo):
    r = equipo.dice("Martin", Jugada("pedir_reasignacion",
                                     {"como_la_nombra": "sensores", "a": "lucas"}))
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "no_es_de_su_sector")
    assert hecho["la_tiene"] == NAHUEL
    assert _pases(conn) == []


def test_sin_tarea_en_la_lista_ni_nombrada_pregunta_cual(conn, equipo):
    r = equipo.dice("Marcos", Jugada("pedir_reasignacion", {"a": "nahuel"}))
    assert (r.hechos[0]["resultado"], r.hechos[0]["falta"]) == ("falta_dato", ["tarea"])


# --- La revisión sigue a quien era la tarea (decisión 28) ------------------------------------

def test_la_de_nahuel_que_toma_marcos_se_cierra_cuando_marcos_la_entrega(conn, equipo):
    _pedir(equipo, "Nahuel", "SEN", "marcos")
    equipo.dice("Nahuel", Jugada("confirmar", {}))
    alias = _alias(equipo, "Marcos", "SEN")
    equipo.dice("Marcos", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}))
    alias = _alias(equipo, "Marcos", "SEN")
    r = equipo.dice("Marcos", Jugada("entregar", {"tarea": alias, "lo_descrito_cubre": ["C1"]}),
                    texto="listo, calibrados y probados, dan dentro de la tolerancia")
    assert r.hechos[0]["al_confirmar"]["la_aprueba_al_entregarla"] is True
    assert "queda_esperando_la_aprobacion_de" not in r.hechos[0]["al_confirmar"]
    r = equipo.dice("Marcos", Jugada("confirmar", {}), texto="dale")
    [hecho] = r.hechos
    assert hecho["estado"] == "terminada"
    assert hecho["la_aprobo_al_entregarla"] is True
    assert "aviso_a_quien_aprueba" not in hecho
    assert "queda_esperando_la_aprobacion_de" not in hecho
    assert hechos.sin_significado(equipo.redaccion) == set()
    fila = uno(conn, "select estado::text e from task where id = %s", equipo.carga.tareas["SEN"])
    assert fila["e"] == "terminada"
    # A Ismael no le llega nada; tampoco el aviso de la entrega a nadie.
    ismael = equipo.mundo["personas"]["Ismael"]["membership_id"]
    assert [a for a in avisos_guardados(conn)
            if str(a["destinatario_membership_id"]) == ismael] == []
    assert avisos_guardados(conn, "entrega_para_aprobar") == []


# --- El encargado se queda él mismo con una tarea de su gente (decisión 53) ------------------

def test_el_encargado_se_queda_con_la_de_nahuel_al_confirmar(conn, equipo):
    r = equipo.dice("Marcos", Jugada("pedir_reasignacion",
                                     {"como_la_nombra": "sensores de Nahuel", "a": "marcos"}))
    [hecho] = r.hechos
    assert hecho["resultado"] == "pase_para_confirmar"
    assert hecho["pase"] == {"la_tiene": NAHUEL, "pasaria_a": MARCOS}
    # Pide, decide y la toma él: al confirmar, la tarea pasa a ser suya.
    assert hecho["al_confirmar_el_pase"] == {"la_toma_al_confirmar": True}
    assert hechos.sin_significado(equipo.redaccion) == set()
    assert _pases(conn) == [] and _quien_la_tiene(conn, equipo, "SEN") == NAHUEL
    r = equipo.dice("Marcos", Jugada("confirmar", {}))
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["la_toma"]) == ("anotado", True)
    assert hecho["aviso_a_quien_la_tenia"]["a"] == NAHUEL
    assert hechos.sin_significado(equipo.redaccion) == set()
    assert _quien_la_tiene(conn, equipo, "SEN") == MARCOS
    # Nadie más tiene que decidir ni tomarla; a Nahuel, que su tarea pasó a Marcos.
    assert avisos_guardados(conn, PASE_PARA_TOMAR) == []
    assert avisos_guardados(conn, PASE_PARA_DECIDIR) == []
    [aviso] = avisos_guardados(conn, COMO_TERMINO)
    assert str(aviso["destinatario_membership_id"]) == equipo.mundo["personas"]["Nahuel"][
        "membership_id"]
    assert (aviso["hechos"]["la_tomo"], aviso["hechos"]["era_suya"], aviso["hechos"]["pidio"],
            aviso["hechos"]["la_tiene"]) == (True, True, MARCOS, MARCOS)
    ia = _salir(conn, equipo, aviso["programado_para"] + timedelta(minutes=1))
    assert all(hechos.sin_significado(p) == set() for p in ia.pedidos_de_redaccion)
    # Sigue siendo trabajo del sector (decisión 28): cuando Marcos dice "listo", se cierra ahí.
    alias = _alias(equipo, "Marcos", "SEN")
    r = equipo.dice("Marcos", Jugada("entregar", {"tarea": alias, "lo_descrito_cubre": ["C1"]}),
                    texto="listo, calibrados y probados, dan dentro de la tolerancia")
    assert r.hechos[0]["al_confirmar"]["la_aprueba_al_entregarla"] is True
    ismael = equipo.mundo["personas"]["Ismael"]["membership_id"]
    assert [a for a in avisos_guardados(conn)
            if str(a["destinatario_membership_id"]) == ismael] == []


# --- Nunca un pase abierto sin que todos sepan cómo terminó (decisión 39) ---------------------

def _preguntas_del_pase_abiertas(conn, t: Turnos, nombre: str) -> list[dict]:
    """Las preguntas de un pase, con sus botones, que esperan algo de esa persona."""
    return todos(conn, """select * from conversation_question
                           where membership_id = %s and tipo = any(%s) and cerrada_en is null""",
                 t.mundo["personas"][nombre]["membership_id"],
                 [preguntas.DECIDIR_EL_PASE, preguntas.TOMAR_LA_TAREA])


def _entregar_por_la_cocina(conn, t: Turnos, nombre: str, clave: str) -> None:
    from leda.db import espacio
    from leda.herramientas import ejecutar
    quien = t._quien(nombre)
    with espacio(conn, t.carga.workspace_id) as cur:
        r = ejecutar(cur, quien, "entregar_tarea",
                     {"tarea_id": t.carga.tareas[clave],
                      "piezas": [{"clase": "texto", "texto": "probado, 20 ciclos sin fallas"}]},
                     ya_confirmada=True)
    conn.commit()
    assert r["estado"] == "en_revision"


def _plc_a_lucas_con_la_pregunta_a_martin(conn, t: Turnos) -> dict:
    _pedir(t, "Marcos", "PLC", "lucas")
    t.dice("Marcos", Jugada("confirmar", {}))
    [pregunta] = avisos_guardados(conn, PASE_PARA_DECIDIR)
    _salir(conn, t, pregunta["programado_para"] + timedelta(minutes=1))
    assert len(_preguntas_del_pase_abiertas(conn, t, "Martin")) == 1
    return pregunta


def test_si_la_tarea_ya_no_se_puede_pasar_el_pase_termina_y_todos_se_enteran(conn, equipo):
    _plc_a_lucas_con_la_pregunta_a_martin(conn, equipo)
    # Mientras Martín no decide, Marcos entrega el PLC: el pase ya no espera nada. Leda no espera
    # el plazo del pase sin respuesta.
    _entregar_por_la_cocina(conn, equipo, "Marcos", "PLC")
    _escalera(conn, equipo, AHORA + timedelta(hours=2))
    assert _pases(conn)[0]["estado"] == "sin_efecto"
    personas = equipo.mundo["personas"]
    avisos = {str(a["destinatario_membership_id"]): a["hechos"]
              for a in avisos_guardados(conn, COMO_TERMINO)}
    # A Marcos, que lo pidió, y a Martín, a quien se le preguntaba; a Lucas todavía no se le había
    # preguntado nada.
    assert set(avisos) == {personas["Marcos"]["membership_id"],
                           personas["Martin"]["membership_id"]}
    assert avisos[personas["Marcos"]["membership_id"]]["la_tarea_cambio"] is True
    a_martin = avisos[personas["Martin"]["membership_id"]]
    assert a_martin["la_tarea_cambio"] is True and a_martin["ya_no_espera_su_respuesta"] is True
    assert _preguntas_del_pase_abiertas(conn, equipo, "Martin") == []
    ia = _salir(conn, equipo, AHORA + timedelta(hours=3))
    assert len(ia.pedidos_de_redaccion) == 2
    assert all(hechos.sin_significado(p) == set() for p in ia.pedidos_de_redaccion)
    # Una vuelta más de la escalera no repite nada.
    _escalera(conn, equipo, AHORA + timedelta(days=1))
    assert len(avisos_guardados(conn, COMO_TERMINO)) == 2
    assert avisos_guardados(conn, RECORDATORIO_DEL_PASE) == []


def test_si_quien_decide_contesta_cuando_la_tarea_ya_cambio_se_entera_quien_lo_pidio(conn,
                                                                                     equipo):
    pregunta = _plc_a_lucas_con_la_pregunta_a_martin(conn, equipo)
    _entregar_por_la_cocina(conn, equipo, "Marcos", "PLC")
    alias = _alias(equipo, "Martin", "PLC")
    r = equipo.dice("Martin", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}),
                    at=pregunta["programado_para"] + timedelta(minutes=20))
    [hecho] = r.hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "la_tarea_cambio")
    assert hecho["aviso_a_quien_pidio"]["a"] == MARCOS
    assert hechos.sin_significado(equipo.redaccion) == set()
    [aviso] = avisos_guardados(conn, COMO_TERMINO)
    assert str(aviso["destinatario_membership_id"]) == equipo.mundo["personas"]["Marcos"][
        "membership_id"]
    assert aviso["hechos"]["la_tarea_cambio"] is True
    assert _preguntas_del_pase_abiertas(conn, equipo, "Martin") == []


def test_contestado_escrito_la_pregunta_con_botones_deja_de_esperar(conn, equipo):
    pregunta = _plc_a_lucas_con_la_pregunta_a_martin(conn, equipo)
    alias = _alias(equipo, "Martin", "PLC")
    equipo.dice("Martin", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}),
                at=pregunta["programado_para"] + timedelta(minutes=20))
    assert _preguntas_del_pase_abiertas(conn, equipo, "Martin") == []


def test_si_el_sistema_termina_el_pase_mientras_quien_decide_contesta_no_falla(conn, equipo,
                                                                              uri):
    # La escalera termina el pase (y no confirma todavía) justo cuando Martín contesta: el turno
    # espera a la escalera y dice que ya no hay nada que contestar, en lugar de fallar.
    import threading
    import time

    from leda.db import conectar
    from leda.herramientas import terminar_pase
    from leda.motor.ancla import candado

    pregunta = _plc_a_lucas_con_la_pregunta_a_martin(conn, equipo)
    alias = _alias(equipo, "Martin", "PLC")
    [pase] = _pases(conn)
    escalera = conectar(uri)
    resultado: dict = {}
    try:
        cur = escalera.cursor()
        cur.execute("set local role leda_app")
        cur.execute("select set_config('leda.workspace_id', %s, true)",
                    (equipo.carga.workspace_id,))
        assert candado(cur, equipo.carga.tareas["PLC"], esperar=False)
        assert terminar_pase(cur, str(pase["id"]), AHORA + timedelta(days=2),
                             vencido=True)["estado"] == "sin_respuesta"

        def contestar() -> None:
            try:
                resultado["r"] = equipo.dice(
                    "Martin", Jugada("contestar_el_pase", {"tarea": alias, "acepta": True}),
                    at=pregunta["programado_para"] + timedelta(minutes=20))
            except BaseException as e:      # noqa: BLE001 -- se mira en el hilo principal
                resultado["error"] = e

        hilo = threading.Thread(target=contestar)
        hilo.start()
        time.sleep(1.5)
        escalera.commit()
        hilo.join(60)
    finally:
        escalera.close()
    assert "error" not in resultado, resultado.get("error")
    [hecho] = resultado["r"].hechos
    assert (hecho["resultado"], hecho["motivo"]) == ("no_se_puede", "no_hay_un_pase")
