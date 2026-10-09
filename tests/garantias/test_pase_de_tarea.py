"""Pasarle una tarea a otra persona (migración 0045; C-7; ADR 0017, enmienda a la decisión 2).

La capa de garantías del pase, no la conversación: quién puede pedirlo (el encargado de un sector, a
cualquiera; un integrante, sólo dentro de su sector), quién lo decide (el encargado del sector de
quien recibe; si es quien pide, su pedido es la decisión; si es quien recibe, decide con su
respuesta), qué tareas se pasan (asignadas, en curso o trabadas), que ningún responsable cambia sin
la confirmación de quien pide, la decisión de quien decide y la de quien recibe (la base lo hace
cumplir: el responsable cambia sólo al agregarse un `cambio_de_responsable` de un pase que espera
que lo tome esa persona), que el trabajo lo sigue revisando quien lo revisaba, la auditoría con
quién pidió, quién decidió, quién aceptó y quién la tenía, y el aislamiento entre espacios.

El mundo es el de las conversaciones (`tests.conversaciones.carga`): Marcos, encargado de OT, y
Nahuel; Martín, encargado de IT, y Lucas; Ismael, Dirección, que aprueba el trabajo de Marcos y de
Martín. Se suma Pedro, otro integrante de OT, para el pase entre dos integrantes de un sector.
"""

from __future__ import annotations

from datetime import datetime, timezone

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
        con_momento = {**args, "at": AT.isoformat()} if nombre.endswith("pase_de_tarea") else args
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


def test_sólo_se_pasa_una_tarea_propia(conn, equipo):
    with pytest.raises(Denegado):
        _pedir(conn, equipo, "Marcos", "SEN", "Pedro")
    conn.rollback()


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


def test_nadie_revisa_su_propio_trabajo_despues_de_un_pase(conn, equipo):
    # La de los sensores la revisaba Marcos; si la toma Marcos, la revisa quien revisa a Marcos.
    assert _quien_revisa(conn, equipo, "SEN") == "Marcos"
    r = _pedir(conn, equipo, "Nahuel", "SEN", "Marcos")
    _contestar(conn, equipo, "Marcos", r["pase_id"], True)
    assert _quien_revisa(conn, equipo, "SEN") == "Ismael"


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
