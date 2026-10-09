"""Pasarle una tarea a otra persona (migraciones 0045 y 0046; C-7; ADR 0017, enmienda a la
decisión 2; decisiones 26, 27, 28 y 43 del usuario).

La capa de garantías del pase, no la conversación: quién puede pedirlo (el encargado de un sector, a
cualquiera, una tarea suya o de alguien de su sector; un integrante, una suya, sólo dentro de su
sector), quién lo decide (el encargado del sector de quien recibe; si es quien pide, su pedido es la
decisión; si es quien recibe, decide con su respuesta), qué tareas se pasan (asignadas, en curso o
trabadas), que ningún responsable cambia sin la confirmación de quien pide, la decisión de quien
decide y la de quien recibe (la base lo hace cumplir: el responsable cambia sólo al agregarse un
`cambio_de_responsable` de un pase que espera que lo tome esa persona), que la revisión sigue a
quien era la tarea (aunque la haga quien la revisa, que al entregarla la deja aprobada y
terminada), que un pase sin respuesta termina sin cambiar nada, la auditoría con quién pidió,
quién decidió, quién aceptó y quién la tenía, y el aislamiento entre espacios.

El mundo es el de las conversaciones (`tests.conversaciones.carga`): Marcos, encargado de OT, y
Nahuel; Martín, encargado de IT, y Lucas; Ismael, Dirección, que aprueba el trabajo de Marcos y de
Martín. Se suma Pedro, otro integrante de OT, para el pase entre dos integrantes de un sector.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from leda.autoridad import Denegado, identificar_en_espacio
from leda.db import admin, espacio
from leda.herramientas import NecesitaConfirmacion, ejecutar

from tests.conversaciones.carga import cargar

AT = datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc)


def _conversacion(tareas: dict) -> dict:
    return {"tareas": tareas}


@pytest.fixture
def equipo(conn):
    """CoreWork en chico, con una tarea de cada uno y Pedro, otro integrante de OT."""
    return _equipo(conn)


def _equipo(conn):
    mundo = cargar(conn, _conversacion({
        "COM": {"titulo": "Revisar comunicaciones", "responsable": "Marcos",
                "vence": "2026-11-06"},
        "PLC": {"titulo": "Programar el PLC", "responsable": "Marcos", "vence": "2026-11-06",
                "estado": "en_curso", "desde": "2026-10-19"},
        "HMI": {"titulo": "Instalar el panel HMI", "responsable": "Marcos",
                "vence": "2026-11-06", "estado": "en_revision", "desde": "2026-10-19"},
        "SRV": {"titulo": "Instalar el servidor", "responsable": "Martin",
                "vence": "2026-11-06", "estado": "en_curso", "desde": "2026-10-19"},
        "SEN": {"titulo": "Calibrar los sensores", "responsable": "Nahuel",
                "vence": "2026-11-06"},
    }))
    with admin(conn) as cur:
        cur.execute("insert into app_user (telegram_user_id, nombre) values (70100, 'Pedro Paz') "
                    "returning id")
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
        mundo.personas["Pedro"] = {"nombre": "Pedro Paz", "app_user_id": usuario,
                                   "membership_id": str(cur.fetchone()["id"]),
                                   "telegram": 70100, "area_id": nahuel["area_id"],
                                   "area": "ot"}
    conn.commit()
    return mundo


def _quien(conn, mundo, corto: str):
    with espacio(conn, mundo.workspace_id) as cur:
        quien = identificar_en_espacio(cur, mundo.personas[corto]["telegram"], mundo.workspace_id)
    conn.commit()
    return quien


def _hacer(conn, mundo, corto: str, nombre: str, args: dict, *, confirmada: bool = True):
    quien = _quien(conn, mundo, corto)
    with espacio(conn, mundo.workspace_id) as cur:
        con_momento = {"at": AT.isoformat(), **args} if nombre.endswith("pase_de_tarea") else args
        r = ejecutar(cur, quien, nombre, con_momento, ya_confirmada=confirmada)
    conn.commit()
    return r


def _pedir(conn, mundo, corto: str, tarea: str, a: str, **kw):
    return _hacer(conn, mundo, corto, "pedir_pase_de_tarea",
                  {"tarea_id": mundo.tareas[tarea],
                   "a_membership_id": mundo.personas[a]["membership_id"]}, **kw)


def _decidir(conn, mundo, corto: str, pase: str, aprueba: bool):
    return _hacer(conn, mundo, corto, "decidir_pase_de_tarea",
                  {"pase_id": pase, "aprueba": aprueba})


def _contestar(conn, mundo, corto: str, pase: str, acepta: bool, motivo: str | None = None):
    return _hacer(conn, mundo, corto, "contestar_pase_de_tarea",
                  {"pase_id": pase, "acepta": acepta,
                   **({"motivo": motivo} if motivo else {})})


def _quien_la_tiene(conn, mundo, tarea: str) -> str:
    with admin(conn) as cur:
        cur.execute("select responsable_membership_id from task where id = %s",
                    (mundo.tareas[tarea],))
        r = str(cur.fetchone()["responsable_membership_id"])
    conn.commit()
    return mundo.persona_de_membresia(r)


def _pase(conn, pase: str) -> dict:
    with admin(conn) as cur:
        cur.execute("select * from pase_de_tarea where id = %s", (pase,))
        fila = cur.fetchone()
    conn.commit()
    return fila


def _id(mundo, corto: str) -> str:
    return mundo.personas[corto]["membership_id"]


# --- Quién puede pedirlo y quién decide ------------------------------------------------------------

def test_el_encargado_le_pasa_una_tarea_a_su_sector_y_su_pedido_es_la_decision(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    assert r["estado"] == "esperando_que_la_tome"
    assert r["decide_membership_id"] == _id(equipo, "Marcos")
    pase = _pase(conn, r["pase_id"])
    assert pase["decidido_en"] is not None
    assert str(pase["pedido_por_membership_id"]) == _id(equipo, "Marcos")
    assert str(pase["de_membership_id"]) == _id(equipo, "Marcos")
    # Pedirlo no cambia quién la tiene.
    assert _quien_la_tiene(conn, equipo, "COM") == "Marcos"


def test_el_encargado_le_pasa_una_tarea_a_otro_sector_y_decide_el_encargado_de_ese(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    assert (r["estado"], r["decide_membership_id"]) == ("esperando_decision", _id(equipo, "Martin"))
    assert _pase(conn, r["pase_id"])["decidido_en"] is None


def test_un_integrante_se_la_pasa_a_otro_de_su_sector_y_decide_su_encargado(conn, equipo):
    r = _pedir(conn, equipo, "Nahuel", "SEN", "Pedro")
    assert (r["estado"], r["decide_membership_id"]) == ("esperando_decision", _id(equipo, "Marcos"))


def test_un_integrante_no_se_la_pasa_a_otro_sector_y_dice_quien_lo_decide(conn, equipo):
    r = _pedir(conn, equipo, "Nahuel", "SEN", "Lucas")
    assert r == {"error": "otro_sector", "lo_decide": _id(equipo, "Marcos")}
    with admin(conn) as cur:
        cur.execute("select count(*) n from pase_de_tarea")
        assert cur.fetchone()["n"] == 0
        cur.execute("""select count(*) n from audit_log
                        where accion = 'herramienta_rechazada:pedir_pase_de_tarea'""")
        assert cur.fetchone()["n"] == 1
    conn.commit()


def test_cuando_recibe_un_encargado_decide_el_mismo(conn, equipo):
    r = _pedir(conn, equipo, "Martin", "SRV", "Marcos")
    assert (r["estado"], r["decide_membership_id"]) == ("esperando_decision", _id(equipo, "Marcos"))


def test_sin_confirmar_no_se_pide_nada(conn, equipo):
    with pytest.raises(NecesitaConfirmacion):
        _pedir(conn, equipo, "Marcos", "COM", "Nahuel", confirmada=False)
    conn.rollback()
    assert _pase_abierto(conn, equipo, "COM") is None


def _pase_abierto(conn, mundo, tarea: str):
    with admin(conn) as cur:
        cur.execute("""select * from pase_de_tarea where task_id = %s
                        and estado in ('esperando_decision', 'esperando_que_la_tome')""",
                    (mundo.tareas[tarea],))
        fila = cur.fetchone()
    conn.commit()
    return fila


# --- Qué tareas se pasan ----------------------------------------------------------------------------

def test_una_tarea_en_revision_no_se_pasa(conn, equipo):
    assert _pedir(conn, equipo, "Marcos", "HMI", "Nahuel") == {"error": "estado",
                                                              "estado": "en_revision"}


def test_sólo_se_pasa_una_tarea_propia_o_de_alguien_de_su_sector_si_es_el_encargado(conn,
                                                                                   equipo):
    # La de los sensores es de Nahuel (OT): ni el encargado de otro sector, ni otro integrante de
    # OT, ni Dirección la pasan (decisión 27: sólo el encargado del sector de quien la tiene).
    for otro in ("Martin", "Pedro", "Ismael"):
        with pytest.raises(Denegado):
            _pedir(conn, equipo, otro, "SEN", "Lucas")
        conn.rollback()
    assert _pase_abierto(conn, equipo, "SEN") is None


# --- El encargado pasa una tarea de su gente (decisión 27) ----------------------------------------

def test_el_encargado_pasa_una_tarea_de_alguien_de_su_sector(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "SEN", "Pedro")
    # Las mismas reglas: Pedro es de OT, así que decide Marcos, con su pedido.
    assert (r["estado"], r["decide_membership_id"]) == ("esperando_que_la_tome",
                                                        _id(equipo, "Marcos"))
    pase = _pase(conn, r["pase_id"])
    assert str(pase["de_membership_id"]) == _id(equipo, "Nahuel")
    assert str(pase["pedido_por_membership_id"]) == _id(equipo, "Marcos")
    assert _quien_la_tiene(conn, equipo, "SEN") == "Nahuel"
    _contestar(conn, equipo, "Pedro", r["pase_id"], True)
    assert _quien_la_tiene(conn, equipo, "SEN") == "Pedro"
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where accion = 'cambiar_responsable'")
        d = cur.fetchone()["detalle"]
    conn.commit()
    assert (d["pedido_por"], d["responsable_anterior"], d["responsable_nuevo"]) == (
        _id(equipo, "Marcos"), _id(equipo, "Nahuel"), _id(equipo, "Pedro"))


def test_el_encargado_pasa_una_de_su_gente_a_otro_sector_y_decide_ese_encargado(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "SEN", "Lucas")
    assert (r["estado"], r["decide_membership_id"]) == ("esperando_decision",
                                                        _id(equipo, "Martin"))


def test_el_encargado_no_la_pasa_a_quien_ya_la_tiene(conn, equipo):
    assert _pedir(conn, equipo, "Marcos", "SEN", "Nahuel") == {"error": "ya_la_tiene"}


# --- El encargado se queda él mismo con una tarea de su gente (decisión 53) ---------------------

def test_el_encargado_se_queda_con_una_tarea_de_su_gente_al_confirmar(conn, equipo):
    # "La de los sensores de Nahuel la hago yo": como cuando se la pasa a Pedro (decisión 27),
    # pero quien pide, quien decide y quien la toma son la misma persona, así que su confirmación
    # de la vista previa vale por las tres.
    with pytest.raises(NecesitaConfirmacion):
        _pedir(conn, equipo, "Marcos", "SEN", "Marcos", confirmada=False)
    conn.rollback()
    assert _quien_la_tiene(conn, equipo, "SEN") == "Nahuel"
    r = _pedir(conn, equipo, "Marcos", "SEN", "Marcos")
    assert (r["estado"], r["tomada"]) == ("la_tomo", True)
    assert _quien_la_tiene(conn, equipo, "SEN") == "Marcos"
    pase = _pase(conn, r["pase_id"])
    assert pase["estado"] == "la_tomo" and pase["decidido_en"] is not None
    assert {str(pase[k]) for k in ("pedido_por_membership_id", "decide_membership_id",
                                   "a_membership_id")} == {_id(equipo, "Marcos")}
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where accion = 'cambiar_responsable'")
        [d] = [f["detalle"] for f in cur.fetchall()]
    conn.commit()
    assert (d["pedido_por"], d["decidio"], d["acepto"], d["responsable_anterior"],
            d["era_de"]) == (_id(equipo, "Marcos"), _id(equipo, "Marcos"), _id(equipo, "Marcos"),
                             _id(equipo, "Nahuel"), _id(equipo, "Nahuel"))
    # Sigue siendo trabajo del sector (decisión 28): la revisa Marcos y, al entregarla, se cierra.
    assert _quien_revisa(conn, equipo, "SEN") == "Marcos"
    assert _entregar(conn, equipo, "Marcos", "SEN")["estado"] == "terminada"


def test_solo_el_encargado_se_queda_con_la_tarea_de_otro(conn, equipo):
    # Una tarea propia no se pasa a uno mismo, y nadie más que el encargado de su sector se queda
    # con la de otra persona.
    assert _pedir(conn, equipo, "Nahuel", "SEN", "Nahuel") == {"error": "es_la_misma_persona"}
    for otro in ("Pedro", "Martin", "Ismael"):
        with pytest.raises(Denegado):
            _pedir(conn, equipo, otro, "SEN", otro)
        conn.rollback()
    assert _quien_la_tiene(conn, equipo, "SEN") == "Nahuel"


def test_no_se_pasa_a_la_misma_persona_ni_dos_veces(conn, equipo):
    assert _pedir(conn, equipo, "Marcos", "COM", "Marcos") == {"error": "es_la_misma_persona"}
    primero = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    assert _pedir(conn, equipo, "Marcos", "COM", "Pedro") == {
        "error": "ya_hay_un_pase", "pase_id": primero["pase_id"]}


def test_la_base_no_acepta_un_pase_de_una_tarea_en_revision_ni_de_otra_persona(conn, equipo):
    with espacio(conn, equipo.workspace_id) as cur:
        for tarea, de in (("HMI", "Marcos"), ("COM", "Nahuel")):
            with pytest.raises(psycopg.errors.RaiseException):
                with conn.transaction():
                    cur.execute(
                        """insert into pase_de_tarea (workspace_id, task_id, de_membership_id,
                               a_membership_id, pedido_por_membership_id, decide_membership_id,
                               estado, pedido_en)
                           values (%s, %s, %s, %s, %s, %s, 'esperando_decision', %s)""",
                        (equipo.workspace_id, equipo.tareas[tarea], _id(equipo, de),
                         _id(equipo, "Pedro"), _id(equipo, de), _id(equipo, "Marcos"), AT))
    conn.rollback()


# --- Ningún cambio sin las tres confirmaciones -------------------------------------------------------

def test_quien_recibe_no_la_toma_antes_de_que_decida_el_encargado(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    with pytest.raises(Denegado):
        _contestar(conn, equipo, "Lucas", r["pase_id"], True)
    conn.rollback()
    assert _quien_la_tiene(conn, equipo, "PLC") == "Marcos"


def test_sólo_decide_el_encargado_del_sector_de_quien_recibe(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    for otro in ("Ismael", "Lucas", "Marcos"):
        with pytest.raises(Denegado):
            _decidir(conn, equipo, otro, r["pase_id"], True)
        conn.rollback()
    assert _pase(conn, r["pase_id"])["estado"] == "esperando_decision"


def test_sólo_la_toma_quien_la_recibe(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    for otro in ("Marcos", "Pedro", "Ismael"):
        with pytest.raises(Denegado):
            _contestar(conn, equipo, otro, r["pase_id"], True)
        conn.rollback()
    assert _quien_la_tiene(conn, equipo, "COM") == "Marcos"


def test_con_las_tres_confirmaciones_cambia_quien_la_tiene(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    assert _decidir(conn, equipo, "Martin", r["pase_id"], True)["estado"] == \
        "esperando_que_la_tome"
    assert _quien_la_tiene(conn, equipo, "PLC") == "Marcos"
    hecho = _contestar(conn, equipo, "Lucas", r["pase_id"], True)
    assert hecho["tomada"] is True
    assert _quien_la_tiene(conn, equipo, "PLC") == "Lucas"
    assert _pase(conn, r["pase_id"])["estado"] == "la_tomo"
    # La fecha, el criterio y el estado no cambian.
    with admin(conn) as cur:
        cur.execute("select estado::text e, fecha_objetivo, criterio_aceptacion from task "
                    "where id = %s", (equipo.tareas["PLC"],))
        fila = cur.fetchone()
    conn.commit()
    assert fila["e"] == "en_curso"
    assert fila["fecha_objetivo"].date().isoformat() == "2026-11-06"


def test_el_si_del_encargado_que_recibe_vale_como_decision_y_como_confirmacion(conn, equipo):
    r = _pedir(conn, equipo, "Martin", "SRV", "Marcos")
    _contestar(conn, equipo, "Marcos", r["pase_id"], True)
    assert _quien_la_tiene(conn, equipo, "SRV") == "Marcos"
    pase = _pase(conn, r["pase_id"])
    assert pase["estado"] == "la_tomo" and pase["decidido_en"] is not None


def test_un_no_deja_la_tarea_con_quien_la_tenia(conn, equipo):
    a = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    assert _decidir(conn, equipo, "Martin", a["pase_id"], False)["estado"] == "no_lo_aprobo"
    b = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    assert _contestar(conn, equipo, "Nahuel", b["pase_id"], False,
                      "estoy con otra cosa")["estado"] == "no_la_tomo"
    assert (_quien_la_tiene(conn, equipo, "PLC"), _quien_la_tiene(conn, equipo, "COM")) == (
        "Marcos", "Marcos")
    assert _pase(conn, b["pase_id"])["motivo"] == "estoy con otra cosa"
    # Un pase terminado no se contesta otra vez.
    with pytest.raises(Denegado):
        _contestar(conn, equipo, "Nahuel", b["pase_id"], True)
    conn.rollback()


def test_la_base_no_cambia_el_responsable_por_fuera_del_pase(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    with admin(conn) as cur:
        # Ni una escritura directa en la tarea...
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute("update task set responsable_membership_id = %s where id = %s",
                            (_id(equipo, "Lucas"), equipo.tareas["PLC"]))
        # ...ni dar el pase por tomado sin el cambio...
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute("update pase_de_tarea set estado = 'la_tomo', decidido_en = %s "
                            "where id = %s", (AT, r["pase_id"]))
        # ...ni un cambio de un pase que todavía espera la decisión de Martín.
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute(
                    """insert into cambio_de_responsable (workspace_id, task_id, pase_id,
                           anterior_membership_id, nuevo_membership_id,
                           aceptado_por_membership_id, at)
                       values (%s, %s, %s, %s, %s, %s, %s)""",
                    (equipo.workspace_id, equipo.tareas["PLC"], r["pase_id"],
                     _id(equipo, "Marcos"), _id(equipo, "Lucas"), _id(equipo, "Lucas"), AT))
    conn.rollback()
    assert _quien_la_tiene(conn, equipo, "PLC") == "Marcos"


def test_la_aplicacion_no_borra_un_pase_ni_toca_un_cambio(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    _contestar(conn, equipo, "Nahuel", r["pase_id"], True)
    with espacio(conn, equipo.workspace_id) as cur:
        for sql in ("delete from pase_de_tarea", "delete from cambio_de_responsable",
                    "update cambio_de_responsable set at = at"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with conn.transaction():
                    cur.execute(sql)
    conn.rollback()


# --- Una trabada se mueve con su bloqueo -----------------------------------------------------------

def test_una_tarea_trabada_se_pasa_con_su_bloqueo_abierto(conn, equipo):
    marcos = _quien(conn, equipo, "Marcos")
    with espacio(conn, equipo.workspace_id) as cur:
        ejecutar(cur, marcos, "registrar_bloqueo",
                 {"tarea_id": equipo.tareas["PLC"], "causa": "falta el cable"}, ya_confirmada=True)
    conn.commit()
    r = _pedir(conn, equipo, "Marcos", "PLC", "Nahuel")
    _contestar(conn, equipo, "Nahuel", r["pase_id"], True)
    with admin(conn) as cur:
        cur.execute("select estado::text e from task where id = %s", (equipo.tareas["PLC"],))
        assert cur.fetchone()["e"] == "bloqueada"
        cur.execute("select count(*) n from blocker where task_id = %s and resuelto_en is null",
                    (equipo.tareas["PLC"],))
        assert cur.fetchone()["n"] == 1
    conn.commit()
    assert _quien_la_tiene(conn, equipo, "PLC") == "Nahuel"


# --- El trabajo lo sigue revisando quien lo revisaba ------------------------------------------------

def _quien_revisa(conn, mundo, tarea: str) -> str:
    with espacio(conn, mundo.workspace_id) as cur:
        cur.execute("select quien_revisa_la_tarea(%s) q", (mundo.tareas[tarea],))
        q = str(cur.fetchone()["q"])
    conn.commit()
    return mundo.persona_de_membresia(q)


def test_el_trabajo_lo_sigue_revisando_quien_lo_revisaba(conn, equipo):
    assert _quien_revisa(conn, equipo, "COM") == "Ismael"
    r = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    _contestar(conn, equipo, "Nahuel", r["pase_id"], True)
    # A Nahuel lo aprueba Marcos, pero esta tarea la revisaba Ismael: la sigue revisando él.
    assert _quien_revisa(conn, equipo, "COM") == "Ismael"
    with espacio(conn, equipo.workspace_id) as cur:
        cur.execute("select puede_ver_tarea(%s, %s) v", (_id(equipo, "Ismael"),
                                                          equipo.tareas["COM"]))
        assert cur.fetchone()["v"] is True
    conn.commit()


def test_la_revision_sigue_a_quien_era_la_tarea_aunque_la_tome_quien_la_revisaba(conn, equipo):
    # Decisión 28: la de los sensores era de Nahuel y la revisa Marcos; si la toma Marcos, la
    # sigue revisando él (es trabajo del sector), y a Ismael no le llega.
    assert _quien_revisa(conn, equipo, "SEN") == "Marcos"
    r = _pedir(conn, equipo, "Nahuel", "SEN", "Marcos")
    _contestar(conn, equipo, "Marcos", r["pase_id"], True)
    assert _quien_revisa(conn, equipo, "SEN") == "Marcos"


def test_con_dos_pases_la_revision_sigue_a_quien_era_la_tarea_al_principio(conn, equipo):
    # La de comunicaciones era de Marcos (la revisa Ismael): pasa a Nahuel y de Nahuel a Pedro, y
    # la sigue revisando Ismael, no Marcos (que aprueba el trabajo de Nahuel y de Pedro).
    r = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    _contestar(conn, equipo, "Nahuel", r["pase_id"], True)
    r = _pedir(conn, equipo, "Nahuel", "COM", "Pedro")
    _decidir(conn, equipo, "Marcos", r["pase_id"], True)
    _contestar(conn, equipo, "Pedro", r["pase_id"], True)
    assert _quien_la_tiene(conn, equipo, "COM") == "Pedro"
    assert _quien_revisa(conn, equipo, "COM") == "Ismael"


def test_si_cambia_quien_aprueba_a_quien_era_la_tarea_la_revision_sigue_el_cambio(conn, equipo):
    # Decisión 43, derivada de la 28: la plataforma cambia quién aprueba el trabajo de Marcos
    # después de que su tarea pasó a Nahuel; la revisión sigue a ese cambio.
    r = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    _contestar(conn, equipo, "Nahuel", r["pase_id"], True)
    with admin(conn) as cur:
        cur.execute("update membership set aprobador_membership_id = %s where id = %s",
                    (_id(equipo, "Martin"), _id(equipo, "Marcos")))
    conn.commit()
    assert _quien_revisa(conn, equipo, "COM") == "Martin"


def _entregar(conn, mundo, corto: str, tarea: str) -> dict:
    quien = _quien(conn, mundo, corto)
    with espacio(conn, mundo.workspace_id) as cur:
        r = ejecutar(cur, quien, "entregar_tarea",
                     {"tarea_id": mundo.tareas[tarea],
                      "piezas": [{"clase": "texto", "texto": "listo, calibrados y probados"}]},
                     ya_confirmada=True)
    conn.commit()
    return r


def test_si_la_entrega_quien_la_revisa_queda_aprobada_por_el_y_terminada(conn, equipo):
    # Decisión 28: Marcos toma la de Nahuel y, al entregarla, se cierra ahí: la hizo y la aprobó
    # Marcos, con la auditoría de las dos cosas; a Ismael no le llega nada.
    r = _pedir(conn, equipo, "Nahuel", "SEN", "Marcos")
    _contestar(conn, equipo, "Marcos", r["pase_id"], True)
    hecho = _entregar(conn, equipo, "Marcos", "SEN")
    assert hecho["estado"] == "terminada"
    assert hecho["aprobada_por_quien_la_entrego"] is True and hecho["cerrada"] is True
    with admin(conn) as cur:
        cur.execute("select estado::text e from task where id = %s", (equipo.tareas["SEN"],))
        assert cur.fetchone()["e"] == "terminada"
        cur.execute("""select aprobador_membership_id a, decision from approval
                        where sujeto_id = %s""", (equipo.tareas["SEN"],))
        assert [(str(f["a"]), f["decision"]) for f in cur.fetchall()] == [
            (_id(equipo, "Marcos"), "aprobado")]
        cur.execute("""select estado_nuevo::text e, actor_app_user_id from task_state_event
                        where task_id = %s order by at""", (equipo.tareas["SEN"],))
        eventos = cur.fetchall()
        cur.execute("""select detalle from audit_log where accion = 'aprobar_tarea'
                        and sujeto_id = %s""", (equipo.tareas["SEN"],))
        auditoria = cur.fetchone()
    conn.commit()
    assert [e["e"] for e in eventos][-2:] == ["en_revision", "terminada"]
    assert {str(e["actor_app_user_id"]) for e in eventos[-2:]} == {
        equipo.personas["Marcos"]["app_user_id"]}
    assert auditoria is not None
    assert auditoria["detalle"]["la_entrego_quien_la_revisa"] is True


def test_si_la_entrega_otra_persona_queda_en_revision_para_quien_la_revisa(conn, equipo):
    # Tarea de Nahuel que hace Pedro: la revisa Marcos; no se aprueba sola.
    r = _pedir(conn, equipo, "Marcos", "SEN", "Pedro")
    _contestar(conn, equipo, "Pedro", r["pase_id"], True)
    hecho = _entregar(conn, equipo, "Pedro", "SEN")
    assert hecho["estado"] == "en_revision"
    assert "aprobada_por_quien_la_entrego" not in hecho
    assert _quien_revisa(conn, equipo, "SEN") == "Marcos"


# --- Un pase que nadie contesta (decisión 26) --------------------------------------------------

def _terminar(conn, mundo, pase: str, *, vencido: bool):
    from leda.herramientas import terminar_pase
    with espacio(conn, mundo.workspace_id) as cur:
        r = terminar_pase(cur, pase, AT, vencido=vencido)
    conn.commit()
    return r


def _sin_respuesta(conn, mundo, pase: str):
    return _terminar(conn, mundo, pase, vencido=True)


def test_un_pase_que_todavia_espera_no_lo_termina_el_sistema(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    assert _terminar(conn, equipo, r["pase_id"], vencido=False) is None
    assert _pase(conn, r["pase_id"])["estado"] == "esperando_decision"


def test_el_pase_de_una_tarea_que_ya_no_se_puede_pasar_termina_sin_efecto(conn, equipo):
    # Mientras Martín no decide, Marcos entrega el PLC: el pase ya no espera nada, aunque no se
    # haya cumplido el plazo (decisión 39: el tema se cierra para todos, y Leda deja de preguntar).
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    marcos = _quien(conn, equipo, "Marcos")
    with espacio(conn, equipo.workspace_id) as cur:
        ejecutar(cur, marcos, "entregar_tarea",
                 {"tarea_id": equipo.tareas["PLC"],
                  "piezas": [{"clase": "texto", "texto": "probado, 20 ciclos sin fallas"}]},
                 ya_confirmada=True)
    conn.commit()
    assert _terminar(conn, equipo, r["pase_id"], vencido=False) == {
        "pase_id": r["pase_id"], "estado": "sin_efecto"}
    assert _pase(conn, r["pase_id"])["estado"] == "sin_efecto"
    assert _quien_la_tiene(conn, equipo, "PLC") == "Marcos"
    assert _terminar(conn, equipo, r["pase_id"], vencido=True) is None
    with admin(conn) as cur:
        cur.execute("""select actor_kind, detalle, pack_hash, nucleo_hash from audit_log
                        where accion = 'pase_sin_efecto'""")
        [fila] = cur.fetchall()
    conn.commit()
    assert fila["actor_kind"] == "sistema" and fila["detalle"]["pase_id"] == r["pase_id"]
    assert fila["pack_hash"] and fila["nucleo_hash"]


def test_un_pase_sin_respuesta_termina_y_la_tarea_sigue_con_quien_la_tenia(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    assert _sin_respuesta(conn, equipo, r["pase_id"]) == {"pase_id": r["pase_id"],
                                                          "estado": "sin_respuesta"}
    pase = _pase(conn, r["pase_id"])
    assert pase["estado"] == "sin_respuesta" and pase["contestado_en"] == AT
    assert _quien_la_tiene(conn, equipo, "PLC") == "Marcos"
    # Ya no espera nada: Martín no lo decide tarde, y otra vez no hace nada.
    with pytest.raises(Denegado):
        _decidir(conn, equipo, "Martin", r["pase_id"], True)
    conn.rollback()
    assert _sin_respuesta(conn, equipo, r["pase_id"]) is None
    # Quien lo pidió puede pedírselo a otra persona.
    assert _pedir(conn, equipo, "Marcos", "PLC", "Nahuel")["estado"] == "esperando_que_la_tome"
    with admin(conn) as cur:
        cur.execute("""select actor_kind, detalle, pack_hash, nucleo_hash from audit_log
                        where accion = 'pase_sin_respuesta'""")
        [fila] = cur.fetchall()
    conn.commit()
    assert fila["actor_kind"] == "sistema"
    assert fila["detalle"]["pase_id"] == r["pase_id"]
    assert fila["pack_hash"] and fila["nucleo_hash"]


def test_la_base_no_reabre_un_pase_sin_respuesta(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    _sin_respuesta(conn, equipo, r["pase_id"])
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute("update pase_de_tarea set estado = 'esperando_decision' "
                            "where id = %s", (r["pase_id"],))
    conn.rollback()


def test_aprueba_la_entrega_quien_revisa_la_tarea_no_quien_aprueba_a_la_persona(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Nahuel")
    _contestar(conn, equipo, "Nahuel", r["pase_id"], True)
    nahuel = _quien(conn, equipo, "Nahuel")
    with espacio(conn, equipo.workspace_id) as cur:
        ejecutar(cur, nahuel, "entregar_tarea",
                 {"tarea_id": equipo.tareas["PLC"],
                  "piezas": [{"clase": "texto", "texto": "probado, 20 ciclos sin fallas"}]},
                 ya_confirmada=True)
    conn.commit()
    with pytest.raises(Denegado):
        _hacer(conn, equipo, "Marcos", "aprobar_tarea", {"tarea_id": equipo.tareas["PLC"]})
    conn.rollback()
    r = _hacer(conn, equipo, "Ismael", "aprobar_tarea", {"tarea_id": equipo.tareas["PLC"]})
    assert r["aprobada"] is True


# --- La auditoría -------------------------------------------------------------------------------------

def test_la_auditoria_guarda_quien_pidio_quien_decidio_quien_acepto_y_quien_la_tenia(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "PLC", "Lucas")
    _decidir(conn, equipo, "Martin", r["pase_id"], True)
    _contestar(conn, equipo, "Lucas", r["pase_id"], True)
    with admin(conn) as cur:
        cur.execute("""select accion, actor_kind, actor_app_user_id, detalle, pack_hash,
                              nucleo_hash
                         from audit_log where accion like '%%pase_de_tarea'
                            or accion = 'cambiar_responsable' order by at, accion""")
        filas = cur.fetchall()
    conn.commit()
    acciones = [f["accion"] for f in filas]
    assert acciones.count("herramienta:pedir_pase_de_tarea") == 1
    assert acciones.count("herramienta:decidir_pase_de_tarea") == 1
    assert acciones.count("herramienta:contestar_pase_de_tarea") == 1
    [cambio] = [f for f in filas if f["accion"] == "cambiar_responsable"]
    d = cambio["detalle"]
    assert (d["pedido_por"], d["decidio"], d["acepto"], d["responsable_anterior"],
            d["responsable_nuevo"], d["revisa"]) == (
        _id(equipo, "Marcos"), _id(equipo, "Martin"), _id(equipo, "Lucas"),
        _id(equipo, "Marcos"), _id(equipo, "Lucas"), _id(equipo, "Ismael"))
    assert d["pase_id"] == r["pase_id"]
    assert cambio["actor_kind"] == "persona"
    assert str(cambio["actor_app_user_id"]) == equipo.personas["Lucas"]["app_user_id"]
    assert all(f["pack_hash"] and f["nucleo_hash"] for f in filas)


# --- El aislamiento -------------------------------------------------------------------------------------

def test_tablas_con_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in ("pase_de_tarea", "cambio_de_responsable"):
            cur.execute("select relrowsecurity, relforcerowsecurity from pg_class "
                        "where oid = to_regclass(%s)", (f"leda.{tabla}",))
            fila = cur.fetchone()
            assert fila["relrowsecurity"] and fila["relforcerowsecurity"], tabla
            cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                        (f"leda.{tabla}",))
            assert [p["polname"] for p in cur.fetchall()] == ["aislamiento_espacio"], tabla
            cur.execute("""select is_nullable from information_schema.columns
                            where table_schema = 'leda' and table_name = %s
                              and column_name = 'workspace_id'""", (tabla,))
            assert cur.fetchone()["is_nullable"] == "NO", tabla
    conn.commit()


def test_un_pase_de_otro_espacio_no_se_ve_ni_se_contesta(conn, equipo):
    r = _pedir(conn, equipo, "Marcos", "COM", "Nahuel")
    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, zona_horaria, activo)
                       values ('otro', 'Otro', 'America/Argentina/Buenos_Aires', true)
                       returning id""")
        otro = str(cur.fetchone()["id"])
    conn.commit()
    with espacio(conn, otro) as cur:
        cur.execute("select count(*) n from pase_de_tarea")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from cambio_de_responsable")
        assert cur.fetchone()["n"] == 0
    conn.commit()
    # Contestarlo desde su espacio, con un id que no es de un pase de ese espacio, no hace nada.
    with pytest.raises(Denegado):
        _contestar(conn, equipo, "Nahuel", "00000000-0000-0000-0000-000000000000", True)
    conn.rollback()
    assert _pase(conn, r["pase_id"])["estado"] == "esperando_que_la_tome"


# --- La migración 0046 con datos: el relleno y su vuelta atrás ------------------------------------

@pytest.fixture
def base_aparte():
    """Una base propia, con el esquema de hoy (el de la 0046), para correr su vuelta atrás y volver
    a aplicarla sin tocar la base que comparten las demás pruebas."""
    import os
    from leda.db import conectar
    from tests.conftest import _con_base_efimera

    mantenimiento = os.environ.get("LEDA_TEST_DB_URL")
    if not mantenimiento:
        pytest.skip("La migración con datos necesita el servidor de pruebas (LEDA_TEST_DB_URL).")
    base = _con_base_efimera(mantenimiento)
    url = next(base)
    c = conectar(url)
    try:
        yield url, c
    finally:
        c.close()
        base.close()


def _correr_0046(url, carpeta: str) -> None:
    from tests.garantias.test_migraciones import ROOT, _sql_script
    with psycopg.connect(str(url), autocommit=True) as db:
        db.execute(_sql_script(
            ROOT / "db" / carpeta / "0046_la_revision_sigue_a_quien_era_la_tarea.sql"))


def test_la_0046_rellena_de_quien_era_y_su_vuelta_atras_no_deja_a_nadie_revisando_lo_suyo(
        base_aparte):
    url, c = base_aparte
    equipo = _equipo(c)
    # Marcos toma la de los sensores de Nahuel (decisión 28: la revisa él); la de comunicaciones,
    # de Marcos, pasa a Nahuel y de Nahuel a Pedro.
    r = _pedir(c, equipo, "Nahuel", "SEN", "Marcos")
    _contestar(c, equipo, "Marcos", r["pase_id"], True)
    r = _pedir(c, equipo, "Marcos", "COM", "Nahuel")
    _contestar(c, equipo, "Nahuel", r["pase_id"], True)
    # El segundo, una hora después: el relleno toma el primero por su momento.
    despues = (AT + timedelta(hours=1)).isoformat()
    r = _hacer(c, equipo, "Nahuel", "pedir_pase_de_tarea",
               {"tarea_id": equipo.tareas["COM"], "a_membership_id": _id(equipo, "Pedro"),
                "at": despues})
    _hacer(c, equipo, "Marcos", "decidir_pase_de_tarea",
           {"pase_id": r["pase_id"], "aprueba": True, "at": despues})
    _hacer(c, equipo, "Pedro", "contestar_pase_de_tarea",
           {"pase_id": r["pase_id"], "acepta": True, "at": despues})
    c.commit()

    def leer(columna: str) -> dict[str, tuple[str, str]]:
        with admin(c) as cur:
            cur.execute(f"""select id::text id, {columna}::text col,
                                   quien_revisa_la_tarea(id)::text revisa
                              from task where id = any(%s::uuid[])""",
                        ([equipo.tareas["SEN"], equipo.tareas["COM"]],))
            filas = {f["id"]: (equipo.persona_de_membresia(f["col"]),
                               equipo.persona_de_membresia(f["revisa"]))
                     for f in cur.fetchall()}
        c.commit()
        return {k: filas[equipo.tareas[k]] for k in ("SEN", "COM")}

    # La vuelta atrás deja la regla de la 0045, en la que nadie revisa lo suyo: la de los sensores,
    # que ahora hace Marcos, la revisa quien aprueba su trabajo.
    _correr_0046(url, "rollbacks")
    assert {k: v[1] for k, v in leer("revisa_membership_id").items()} == {
        "SEN": "Ismael", "COM": "Ismael"}
    # Al volver a aplicarla, el relleno: de quién era cada tarea antes de su primer pase.
    _correr_0046(url, "migrations")
    assert leer("era_de_membership_id") == {"SEN": ("Nahuel", "Marcos"),
                                            "COM": ("Marcos", "Ismael")}
