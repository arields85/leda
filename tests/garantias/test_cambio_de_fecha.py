"""El cambio de fecha de una tarea, en la base (migración 0077; ADR 0025, decisión 6; J5, porción S2).

La capa de garantías del cambio de fecha, no la conversación ni la web: la fecha de una tarea cambia
sólo al agregarse una fila en `cambio_de_fecha` (con el molde de `cambio_de_responsable`), que no se
edita ni se borra; el cambio dice la fecha que tenía la tarea (uno viejo se rechaza), lleva su
motivo, quién lo hizo y quién lo decidió; la fecha nueva es un día hábil del espacio, de hoy en
adelante; una tarea de otro espacio no se encuentra, igual que un id inventado; y la marca con la
que el disparador escribe la fecha no abre ningún otro campo de la tarea. Quién puede cambiar una
fecha es de las porciones siguientes (S6), no de ésta.

El mundo es el de las conversaciones (`tests.conversaciones.carga`): Marcos, encargado de OT, con
"Revisar comunicaciones", que vence el viernes 6/11.
"""

from __future__ import annotations

from datetime import datetime, timezone

import psycopg
import pytest

from leda.db import admin, espacio

from tests.conversaciones.carga import cargar, fin_del_dia

AT = datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc)   # martes 20/10
VENCE = fin_del_dia("2026-11-06")                           # viernes
NUEVA = fin_del_dia("2026-11-13")                           # viernes siguiente


@pytest.fixture
def equipo(conn):
    return cargar(conn, {"tareas": {
        "COM": {"titulo": "Revisar comunicaciones", "responsable": "Marcos",
                "vence": "2026-11-06"},
    }})


def _fecha(conn, tarea: str):
    with admin(conn) as cur:
        cur.execute("select fecha_objetivo from task where id = %s", (tarea,))
        fecha = cur.fetchone()["fecha_objetivo"]
    conn.commit()
    return fecha


def _cambios(conn, tarea: str) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select * from cambio_de_fecha where task_id = %s order by at", (tarea,))
        filas = cur.fetchall()
    conn.commit()
    return filas


def _insertar(cur, mundo, *, tarea: str | None = None, workspace_id: str | None = None,
              anterior=VENCE, nueva=NUEVA, motivo: str | None = "Primero va el tablero",
              clase: str = "cambio_directo", at=AT):
    marcos = mundo.personas["Marcos"]
    cur.execute(
        """insert into cambio_de_fecha (workspace_id, task_id, fecha_anterior, fecha_nueva,
                                        motivo, clase, cambiada_por_app_user_id,
                                        decidida_por_membership_id, at)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (workspace_id or mundo.workspace_id, tarea or mundo.tareas["COM"], anterior, nueva,
         motivo, clase, marcos["app_user_id"], marcos["membership_id"], at))


def _rechazo(conn, mundo, error, **kw) -> str:
    """Intenta el cambio como `leda_app` en el espacio del mundo y devuelve el mensaje."""
    with espacio(conn, mundo.workspace_id) as cur:
        with pytest.raises(error) as e:
            with conn.transaction():
                _insertar(cur, mundo, **kw)
    conn.rollback()
    return e.value.diag.message_primary


# --- La fecha cambia sólo así ----------------------------------------------------------------------

def test_la_fecha_de_una_tarea_no_se_escribe_directamente(conn, equipo):
    tarea = equipo.tareas["COM"]
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute("update task set fecha_objetivo = %s where id = %s", (NUEVA, tarea))
    conn.rollback()
    with espacio(conn, equipo.workspace_id) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with conn.transaction():
                cur.execute("update task set fecha_objetivo = %s where id = %s", (NUEVA, tarea))
    conn.rollback()
    assert _fecha(conn, tarea) == VENCE


def test_un_cambio_de_fecha_aplica_la_fecha_nueva_y_queda_escrito(conn, equipo):
    tarea = equipo.tareas["COM"]
    with espacio(conn, equipo.workspace_id) as cur:
        _insertar(cur, equipo)
    conn.commit()
    assert _fecha(conn, tarea) == NUEVA
    (cambio,) = _cambios(conn, tarea)
    marcos = equipo.personas["Marcos"]
    assert str(cambio["workspace_id"]) == equipo.workspace_id
    assert cambio["fecha_anterior"] == VENCE and cambio["fecha_nueva"] == NUEVA
    assert cambio["motivo"] == "Primero va el tablero"
    assert cambio["clase"] == "cambio_directo"
    assert str(cambio["cambiada_por_app_user_id"]) == marcos["app_user_id"]
    assert str(cambio["decidida_por_membership_id"]) == marcos["membership_id"]
    assert cambio["at"] == AT
    with admin(conn) as cur:
        cur.execute("select actualizado_en from task where id = %s", (tarea,))
        assert cur.fetchone()["actualizado_en"] == AT
    conn.commit()


def test_dos_cambios_seguidos_encadenan_sus_fechas(conn, equipo):
    tarea = equipo.tareas["COM"]
    otra = fin_del_dia("2026-11-20")
    with espacio(conn, equipo.workspace_id) as cur:
        _insertar(cur, equipo)
        _insertar(cur, equipo, anterior=NUEVA, nueva=otra, motivo="Se sumó la auditoría")
    conn.commit()
    assert _fecha(conn, tarea) == otra
    assert [(c["fecha_anterior"], c["fecha_nueva"]) for c in _cambios(conn, tarea)] == [
        (VENCE, NUEVA), (NUEVA, otra)]


# --- Lo que se rechaza -----------------------------------------------------------------------------

def test_un_cambio_con_una_fecha_anterior_vieja_se_rechaza(conn, equipo):
    tarea = equipo.tareas["COM"]
    mensaje = _rechazo(conn, equipo, psycopg.errors.RaiseException,
                       anterior=fin_del_dia("2026-11-05"))
    assert "ya cambió" in mensaje
    assert _fecha(conn, tarea) == VENCE and _cambios(conn, tarea) == []


@pytest.mark.parametrize("motivo,error", [
    ("", psycopg.errors.CheckViolation),
    ("   ", psycopg.errors.CheckViolation),
    (None, psycopg.errors.NotNullViolation),
])
def test_un_cambio_sin_motivo_se_rechaza(conn, equipo, motivo, error):
    _rechazo(conn, equipo, error, motivo=motivo)
    assert _fecha(conn, equipo.tareas["COM"]) == VENCE


def test_un_cambio_a_la_misma_fecha_o_de_otra_clase_se_rechaza(conn, equipo):
    _rechazo(conn, equipo, psycopg.errors.CheckViolation, nueva=VENCE)
    _rechazo(conn, equipo, psycopg.errors.CheckViolation, clase="mas_tiempo")
    assert _fecha(conn, equipo.tareas["COM"]) == VENCE


def test_la_fecha_nueva_es_un_dia_habil_de_hoy_en_adelante(conn, equipo):
    # Un sábado no (decisión 56; `es_dia_habil`, la misma regla de la carga)...
    mensaje = _rechazo(conn, equipo, psycopg.errors.RaiseException,
                       nueva=fin_del_dia("2026-11-14"))
    assert "día hábil" in mensaje
    # ...ni un día que ya pasó en el espacio.
    mensaje = _rechazo(conn, equipo, psycopg.errors.RaiseException,
                       nueva=fin_del_dia("2026-10-19"))
    assert "ya pasó" in mensaje
    assert _fecha(conn, equipo.tareas["COM"]) == VENCE


# --- El aislamiento --------------------------------------------------------------------------------

def _tarea_de_otro_espacio(conn) -> tuple[str, str]:
    with admin(conn) as cur:
        cur.execute("""insert into workspace (slug, nombre, activo)
                       values ('west-studio', 'West Studio', true) returning id""")
        oeste = str(cur.fetchone()["id"])
        cur.execute("""insert into work_calendar (workspace_id, dias, hora_inicio, hora_fin)
                       values (%s, array['lunes','martes','miercoles','jueves','viernes'],
                               '09:00', '17:00')""", (oeste,))
        cur.execute("insert into area (workspace_id, slug, nombre) values (%s, 'diseno', "
                    "'Diseño') returning id", (oeste,))
        area = cur.fetchone()["id"]
        cur.execute("insert into objective (workspace_id, tipo, titulo, estado) "
                    "values (%s, 'operativo', 'Lanzar el sitio', 'activo') returning id",
                    (oeste,))
        objetivo = cur.fetchone()["id"]
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id, estado,
                                         fecha_objetivo)
                       values (%s, %s, 'Una de West Studio', %s, 'asignada', %s)
                       returning id""", (oeste, objetivo, area, VENCE))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return oeste, tarea


def test_una_tarea_de_otro_espacio_no_se_encuentra_como_un_id_inventado(conn, equipo):
    oeste, ajena = _tarea_de_otro_espacio(conn)
    inventado = "00000000-0000-4000-8000-000000000000"
    de_otro = _rechazo(conn, equipo, psycopg.errors.RaiseException, tarea=ajena)
    sin_tarea = _rechazo(conn, equipo, psycopg.errors.RaiseException, tarea=inventado)
    assert de_otro == sin_tarea
    # Diciendo el espacio de la tarea ajena, tampoco: la sesión es la de CoreWork.
    with espacio(conn, equipo.workspace_id) as cur:
        with pytest.raises(psycopg.Error):
            with conn.transaction():
                _insertar(cur, equipo, tarea=ajena, workspace_id=oeste)
    conn.rollback()
    assert _fecha(conn, ajena) == VENCE and _cambios(conn, ajena) == []


# --- Nadie edita ni borra un cambio, y la marca no abre otros campos -------------------------------

def test_la_aplicacion_no_edita_ni_borra_un_cambio_de_fecha(conn, equipo):
    with espacio(conn, equipo.workspace_id) as cur:
        _insertar(cur, equipo)
    conn.commit()
    with espacio(conn, equipo.workspace_id) as cur:
        for sql in ("update cambio_de_fecha set motivo = 'otro'",
                    "update cambio_de_fecha set fecha_nueva = fecha_anterior",
                    "delete from cambio_de_fecha"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with conn.transaction():
                    cur.execute(sql)
        # Ni con la marca del disparador puesta a mano: `leda_app` no escribe la tarea.
        cur.execute("select set_config('leda.aplicando_cambio_de_fecha', '1', true)")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with conn.transaction():
                cur.execute("update task set fecha_objetivo = %s where id = %s",
                            (VENCE, equipo.tareas["COM"]))
    conn.rollback()
    assert len(_cambios(conn, equipo.tareas["COM"])) == 1


@pytest.mark.parametrize("sql", [
    "update task set titulo = 'Otro título' where id = %s",
    "update task set criterio_aceptacion = 'otro' where id = %s",
    "update task set estado = 'terminada' where id = %s",
    "update task set responsable_membership_id = null where id = %s",
])
def test_la_marca_del_cambio_de_fecha_no_abre_otros_campos(conn, equipo, sql):
    with admin(conn) as cur:
        cur.execute("select set_config('leda.aplicando_cambio_de_fecha', '1', true)")
        with pytest.raises(psycopg.errors.RaiseException):
            with conn.transaction():
                cur.execute(sql, (equipo.tareas["COM"],))
    conn.rollback()
