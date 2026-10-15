"""El equipo cuadra, en la base (migración 0081; J7-1 de `odd/tasks/plataforma-jerarquias.md`).

La capa de garantías de la J7, no la web: las reglas del equipo (ADR 0023, decisión 4; mecánica §7)
no se pueden exigir en las tablas, porque las pruebas y el importador pasan por estados intermedios.
Las comprueba `problemas_del_equipo`, que cada función de la J7 vuelve a correr dentro de su
transacción: una sola persona activa con la autoridad final; cada otra persona activa, con un
aprobador activo; sin vueltas en la cadena de quién aprueba a quién; y cada área sin archivar, con
un referente activo, la autoaprobación declarada o sin referente (la decide Dirección, J6-D6).
Además: un área se archiva (`area.archivada_en`), no se borra; cada cambio del equipo queda en
`cambio_del_equipo`, que sólo se agrega; y `leda_app` ya no escribe las tablas del equipo.

El mundo es el de las conversaciones (`tests.conversaciones.carga`): Ismael (Dirección), los
referentes Ariel, Martín, Marcos y Mariano, Nahuel (OT, lo aprueba Marcos) y Lucas (IT, lo aprueba
Martín).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import psycopg
import pytest
from psycopg.types.json import Jsonb

from leda.db import admin, espacio

from tests.conversaciones.carga import cargar

AT = datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc)
TABLAS_DEL_EQUIPO = ("area", "rol", "membership", "approval_policy", "escalation_route")


@pytest.fixture
def equipo(conn):
    return cargar(conn, {})


def _problemas(conn, ws: str, *, consultado: str | None = None) -> list[dict]:
    """Los problemas del equipo `consultado` (por omisión, el mismo `ws`), como `leda_app` en el
    espacio `ws`."""
    with espacio(conn, ws) as cur:
        cur.execute("select problemas_del_equipo(%s) as p", (consultado or ws,))
        problemas = cur.fetchone()["p"]
    conn.commit()
    return problemas


def _codigos(problemas: list[dict]) -> list[str]:
    return sorted(p["codigo"] for p in problemas)


def _admin(conn, sql: str, params=()) -> None:
    with admin(conn) as cur:
        cur.execute(sql, params)
    conn.commit()


def _mid(equipo, corto: str) -> str:
    return equipo.personas[corto]["membership_id"]


# --- Las reglas ----------------------------------------------------------------------------------

def test_un_equipo_que_cuadra_no_tiene_problemas(conn, equipo):
    assert _problemas(conn, equipo.workspace_id) == []


def test_dos_personas_con_la_autoridad_final_es_un_problema(conn, equipo):
    _admin(conn, """update membership set rol_id = (select rol_id from membership where id = %s)
                     where id = %s""", (_mid(equipo, "Ismael"), _mid(equipo, "Martin")))
    (problema,) = _problemas(conn, equipo.workspace_id)
    assert problema["codigo"] == "mas_de_una_autoridad_final"
    assert "Ismael Soschinski" in problema["mensaje"]
    assert "Martín Forte" in problema["mensaje"]


def test_sin_nadie_con_la_autoridad_final_es_un_problema(conn, equipo):
    _admin(conn, """update membership set rol_id = (select rol_id from membership where id = %s)
                     where id = %s""", (_mid(equipo, "Martin"), _mid(equipo, "Ismael")))
    problemas = _problemas(conn, equipo.workspace_id)
    # Ismael deja de ser Dirección y queda sin quién lo apruebe: también se dice.
    assert _codigos(problemas) == ["sin_aprobador", "sin_autoridad_final"]


def test_una_persona_sin_aprobador_es_un_problema(conn, equipo):
    _admin(conn, "update membership set aprobador_membership_id = null where id = %s",
           (_mid(equipo, "Lucas"),))
    (problema,) = _problemas(conn, equipo.workspace_id)
    assert problema["codigo"] == "sin_aprobador"
    assert problema["membership_id"] == _mid(equipo, "Lucas")
    assert "Lucas Natuche" in problema["mensaje"]


def test_un_aprobador_o_un_referente_que_ya_no_esta_es_un_problema(conn, equipo):
    _admin(conn, "update membership set activo = false where id = %s", (_mid(equipo, "Martin"),))
    problemas = _problemas(conn, equipo.workspace_id)
    assert _codigos(problemas) == ["aprobador_inactivo", "referente_inactivo"]
    aprobador = next(p for p in problemas if p["codigo"] == "aprobador_inactivo")
    assert aprobador["membership_id"] == _mid(equipo, "Lucas")
    assert "Martín Forte" in aprobador["mensaje"]
    referente = next(p for p in problemas if p["codigo"] == "referente_inactivo")
    assert referente["area_id"] == equipo.areas["it"]


def test_una_vuelta_en_la_cadena_de_aprobacion_se_dice_una_vez(conn, equipo):
    # Marcos aprueba a Ismael, e Ismael a Marcos; Nahuel (lo aprueba Marcos) llega a la misma vuelta.
    _admin(conn, "update membership set aprobador_membership_id = %s where id = %s",
           (_mid(equipo, "Marcos"), _mid(equipo, "Ismael")))
    (problema,) = _problemas(conn, equipo.workspace_id)
    assert problema["codigo"] == "ciclo_de_aprobacion"
    assert "Ismael Soschinski" in problema["mensaje"]
    assert "Marcos Tarquini" in problema["mensaje"]
    assert "Nahuel" not in problema["mensaje"]


def test_nadie_se_aprueba_a_si_mismo(conn, equipo):
    # Lo impide la tabla misma, aun a la administración.
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            with conn.transaction():
                cur.execute("update membership set aprobador_membership_id = id where id = %s",
                            (_mid(equipo, "Lucas"),))
    conn.rollback()
    assert _problemas(conn, equipo.workspace_id) == []


def test_un_area_con_referente_inactivo_cuadra_si_declara_que_se_autoaprueba(conn, equipo):
    _admin(conn, "update membership set activo = false where id = %s",
           (_mid(equipo, "Mariano"),))
    (problema,) = _problemas(conn, equipo.workspace_id)
    assert problema["codigo"] == "referente_inactivo"
    assert problema["area_id"] == equipo.areas["electricidad"]
    _admin(conn, """insert into approval_policy (workspace_id, sujeto, area_id,
                                                 autoaprobacion_declarada, motivo)
                    values (%s, 'tarea', %s, true, 'El área revisa su propio trabajo')""",
           (equipo.workspace_id, equipo.areas["electricidad"]))
    assert _problemas(conn, equipo.workspace_id) == []


def test_un_area_sin_referente_cuadra_porque_la_decide_direccion(conn, equipo):
    _admin(conn, "update area set referente_membership_id = null where id = %s",
           (equipo.areas["corelabs"],))
    assert _problemas(conn, equipo.workspace_id) == []


def test_un_area_archivada_no_cuenta_pero_nadie_activo_queda_en_ella(conn, equipo):
    # Electricidad se archiva y Mariano, su referente y única persona, se va: cuadra.
    _admin(conn, "update membership set activo = false where id = %s",
           (_mid(equipo, "Mariano"),))
    _admin(conn, "update area set archivada_en = %s where id = %s",
           (AT, equipo.areas["electricidad"]))
    assert _problemas(conn, equipo.workspace_id) == []
    # IT se archiva con Martín y Lucas adentro: no cuadra (ADR 0023, decisión 4).
    _admin(conn, "update area set archivada_en = %s where id = %s", (AT, equipo.areas["it"]))
    problemas = _problemas(conn, equipo.workspace_id)
    assert _codigos(problemas) == ["integrante_en_area_archivada"] * 2
    assert {p["membership_id"] for p in problemas} == {_mid(equipo, "Martin"),
                                                        _mid(equipo, "Lucas")}


def test_un_area_se_crea_sin_archivar(conn, equipo):
    with admin(conn) as cur:
        cur.execute("select archivada_en from area where id = %s", (equipo.areas["ot"],))
        assert cur.fetchone()["archivada_en"] is None
    conn.commit()


# --- El aislamiento ------------------------------------------------------------------------------

def _otro_espacio(conn) -> str:
    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, activo)
                       values ('mantenimiento', 'Mantenimiento', true) returning id""")
        ws = str(cur.fetchone()["id"])
    conn.commit()
    return ws


def test_otro_espacio_no_ve_los_problemas_ni_las_personas_de_este(conn, equipo):
    otro = _otro_espacio(conn)
    # Desde el otro espacio, el equipo de CoreWork no se puede consultar.
    with espacio(conn, otro) as cur:
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute("select problemas_del_equipo(%s)", (equipo.workspace_id,))
    conn.rollback()
    # Y el suyo no trae a nadie de CoreWork: está vacío, sin autoridad final.
    (problema,) = _problemas(conn, otro)
    assert problema["codigo"] == "sin_autoridad_final"
    assert _problemas(conn, equipo.workspace_id) == []


def test_sin_espacio_fijado_no_se_consulta_nada(conn, equipo):
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute("select problemas_del_equipo(%s)", (equipo.workspace_id,))
    conn.rollback()


# --- Los cambios del equipo ----------------------------------------------------------------------

def _cambio(equipo, **kw) -> dict:
    fila = {"workspace_id": equipo.workspace_id, "clase": "cambio_de_aprobador",
            "puerta": "equipo", "hecho_por_app_user_id": equipo.personas["Ismael"]["app_user_id"],
            "hecho_por_membership_id": _mid(equipo, "Ismael"),
            "antes": Jsonb({"aprobador": _mid(equipo, "Martin")}),
            "despues": Jsonb({"aprobador": _mid(equipo, "Ismael")}),
            "clave": "clave-del-cambio-0001",
            "huella": hashlib.sha256(b"equipo").hexdigest(), "at": AT}
    fila.update(kw)
    return fila


def _insertar_cambio(cur, fila: dict) -> str:
    columnas = ", ".join(fila)
    cur.execute(f"insert into cambio_del_equipo ({columnas}) values "
                f"({', '.join(['%s'] * len(fila))}) returning id", tuple(fila.values()))
    return str(cur.fetchone()["id"])


def test_un_cambio_del_equipo_solo_se_agrega(conn, equipo):
    with admin(conn) as cur:
        cambio = _insertar_cambio(cur, _cambio(equipo))
    conn.commit()
    for sql in ("update cambio_del_equipo set clase = 'alta' where id = %s",
                "delete from cambio_del_equipo where id = %s"):
        with admin(conn) as cur:
            with pytest.raises(psycopg.errors.RaiseException):
                with conn.transaction():
                    cur.execute(sql, (cambio,))
        conn.rollback()
    with admin(conn) as cur:
        cur.execute("select count(*) as n from cambio_del_equipo")
        assert cur.fetchone()["n"] == 1
    conn.commit()


def test_la_misma_clave_no_se_agrega_dos_veces(conn, equipo):
    with admin(conn) as cur:
        _insertar_cambio(cur, _cambio(equipo))
    conn.commit()
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.UniqueViolation):
            with conn.transaction():
                _insertar_cambio(cur, _cambio(equipo))
    conn.rollback()


@pytest.mark.parametrize("cambios", [
    {"puerta": "equipo", "hecho_por_membership_id": None},   # por el equipo, sin la persona
    {"puerta": "administracion"},                            # por administración, con una
    {"puerta": "otra"},
    {"clase": "inventada"},
    {"antes": None, "despues": None},
    {"clave": "corta"},
    {"huella": "no-es-una-huella"},
])
def test_un_cambio_del_equipo_mal_formado_se_rechaza(conn, equipo, cambios):
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            with conn.transaction():
                _insertar_cambio(cur, _cambio(equipo, **cambios))
    conn.rollback()


def test_el_administrador_de_plataforma_cambia_sin_ser_del_equipo(conn, equipo):
    with admin(conn) as cur:
        cur.execute("select app_user_id from platform_role limit 1")
        administrador = str(cur.fetchone()["app_user_id"])
        _insertar_cambio(cur, _cambio(equipo, puerta="administracion",
                                      hecho_por_app_user_id=administrador,
                                      hecho_por_membership_id=None))
    conn.commit()


def test_los_cambios_del_equipo_no_los_toca_leda_app_y_no_se_ven_desde_otro_espacio(conn, equipo):
    with admin(conn) as cur:
        _insertar_cambio(cur, _cambio(equipo))
    conn.commit()
    with espacio(conn, equipo.workspace_id) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with conn.transaction():
                cur.execute("select count(*) from cambio_del_equipo")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with conn.transaction():
                _insertar_cambio(cur, _cambio(equipo, clave="clave-del-cambio-0002"))
    conn.rollback()
    # `leda_owner`, el dueño de las funciones de la J7, no saltea la RLS: desde otro espacio no ve
    # el cambio, desde el suyo sí.
    otro = _otro_espacio(conn)
    for ws, cuantos in ((otro, 0), (equipo.workspace_id, 1)):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("set local role leda_owner")
                cur.execute("select set_config('leda.workspace_id', %s, true)", (ws,))
                cur.execute("select count(*) as n from cambio_del_equipo")
                assert cur.fetchone()["n"] == cuantos
    conn.commit()


# --- leda_app ya no escribe el equipo -------------------------------------------------------------

@pytest.mark.parametrize("tabla", TABLAS_DEL_EQUIPO)
def test_leda_app_ya_no_escribe_las_tablas_del_equipo(conn, equipo, tabla):
    with espacio(conn, equipo.workspace_id) as cur:
        for sql in (f"insert into {tabla} (workspace_id) values (%s)",
                    f"update {tabla} set workspace_id = workspace_id where workspace_id = %s",
                    f"delete from {tabla} where workspace_id = %s"):
            if tabla == "membership" and sql.startswith("update"):
                continue        # la columna del espacio: ver la prueba de abajo
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with conn.transaction():
                    cur.execute(sql, (equipo.workspace_id,))
    conn.rollback()


def test_leda_app_toma_una_membresia_para_leerla_pero_no_la_cambia(conn, equipo):
    """El despachador lee a la persona y a quien la aprueba `for share` (vista previa vigente),
    que pide un privilegio de `update`: `leda_app` lo tiene sólo sobre `workspace_id`, que la
    política del espacio no deja cambiar."""
    lucas = _mid(equipo, "Lucas")
    with espacio(conn, equipo.workspace_id) as cur:
        cur.execute("select aprobador_membership_id from membership where id = %s for share",
                    (lucas,))
        assert str(cur.fetchone()["aprobador_membership_id"]) == _mid(equipo, "Martin")
        for sql in ("update membership set activo = false where id = %s",
                    "update membership set aprobador_membership_id = null where id = %s",
                    "update membership set area_id = area_id where id = %s"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with conn.transaction():
                    cur.execute(sql, (lucas,))
        otro_id = "00000000-0000-0000-0000-000000000001"
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with conn.transaction():
                cur.execute("update membership set workspace_id = %s where id = %s",
                            (otro_id, lucas))
    conn.rollback()
