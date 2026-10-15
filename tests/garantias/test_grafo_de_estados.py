"""El grafo de transiciones de estado, en la base (migración 0079; parte 1: sólo lo que dice la
mecánica, `nucleo/mecanica-pm.md` §3).

La capa de garantías, no la conversación: el estado de una tarea o de un objetivo es la
proyección de sus eventos, y desde la 0079 un evento sólo se agrega si encadena con el estado
vigente:

1. el evento dice de qué estado sale (`estado_anterior`) y ése es el estado de la fila ahora;
   sólo el evento que la crea (sin `estado_anterior`) puede no decirlo, y sólo si la fila todavía
   no tiene ningún evento;
2. `cancelada` y `cancelado` son terminales: ningún evento sale de ellos;
3. salir de `bloqueada` devuelve la tarea al estado que tenía antes de bloquearse, o la cancela.

El resto del grafo (quién cancela, qué otros saltos valen, la máquina de estados de un objetivo)
espera decisiones del usuario y no se restringe acá. Los caminos que usa el producto siguen
pasando.

El mundo es el de las conversaciones (`tests.conversaciones.carga`): Marcos, encargado de OT.
"""

from __future__ import annotations

import psycopg
import pytest

from leda.db import admin, espacio

from tests.conversaciones.carga import cargar


@pytest.fixture
def equipo(conn):
    return cargar(conn, {"tareas": {
        "COM": {"titulo": "Revisar comunicaciones", "responsable": "Marcos",
                "vence": "2026-11-06"},
    }})


def _estado(conn, tarea: str) -> str:
    with admin(conn) as cur:
        cur.execute("select estado::text e from task where id = %s", (tarea,))
        estado = cur.fetchone()["e"]
    conn.commit()
    return estado


def _evento(cur, tarea: str, anterior: str | None, nuevo: str) -> None:
    cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                 actor_kind, motivo)
                   values (%s, %s, %s, 'sistema', 'prueba del grafo')""",
                (tarea, anterior, nuevo))


def _pasa(conn, mundo, tarea: str, anterior: str | None, nuevo: str) -> None:
    """Agrega el evento como `leda_app`, en el espacio del mundo, y comprueba la proyección."""
    with espacio(conn, mundo.workspace_id) as cur:
        _evento(cur, tarea, anterior, nuevo)
    conn.commit()
    assert _estado(conn, tarea) == nuevo


def _rechazo(conn, mundo, tarea: str, anterior: str | None, nuevo: str) -> str:
    """Intenta el evento como `leda_app` y devuelve el mensaje; la tarea no cambia."""
    antes = _estado(conn, tarea)
    with espacio(conn, mundo.workspace_id) as cur:
        with pytest.raises(psycopg.errors.RaiseException) as e:
            with conn.transaction():
                _evento(cur, tarea, anterior, nuevo)
    conn.rollback()
    assert _estado(conn, tarea) == antes
    return e.value.diag.message_primary


def _bloquear(conn, mundo, tarea: str, causa: str = "Falta el cable") -> None:
    with admin(conn) as cur:
        cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_por)
                       values (%s, %s, %s, %s)""",
                    (mundo.workspace_id, tarea, causa,
                     mundo.personas["Marcos"]["membership_id"]))
    conn.commit()
    _pasa(conn, mundo, tarea, _estado(conn, tarea), "bloqueada")


def _aprobar(conn, mundo, tarea: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                             aprobador_membership_id, decision)
                       select %s, 'tarea', %s, aprobador_membership_id, 'aprobado'
                         from membership where id = %s""",
                    (mundo.workspace_id, tarea, mundo.personas["Marcos"]["membership_id"]))
    conn.commit()


def _tarea_nueva(conn, mundo, titulo: str = "Ordenar el tablero") -> str:
    """Una tarea recién insertada, sin ningún evento todavía (como la deja quien la crea)."""
    with admin(conn) as cur:
        cur.execute("select objective_id, area_id, responsable_membership_id from task "
                    "where id = %s", (mundo.tareas["COM"],))
        base = cur.fetchone()
        cur.execute("""insert into task (workspace_id, objective_id, titulo, area_id,
                                         responsable_membership_id)
                       values (%s, %s, %s, %s, %s) returning id""",
                    (mundo.workspace_id, base["objective_id"], titulo, base["area_id"],
                     base["responsable_membership_id"]))
        tarea = str(cur.fetchone()["id"])
    conn.commit()
    return tarea


# --- 1. El evento sale del estado vigente ---------------------------------------------------------

def test_un_evento_que_sale_de_otro_estado_se_rechaza(conn, equipo):
    tarea = equipo.tareas["COM"]
    assert _estado(conn, tarea) == "asignada"
    mensaje = _rechazo(conn, equipo, tarea, "en_curso", "en_revision")
    assert mensaje.startswith("transicion_invalida")


def test_un_evento_viejo_se_rechaza_despues_de_otro(conn, equipo):
    """Dos actos pensados sobre el mismo estado: el segundo llega tarde y no se aplica."""
    tarea = equipo.tareas["COM"]
    _pasa(conn, equipo, tarea, "asignada", "en_curso")
    mensaje = _rechazo(conn, equipo, tarea, "asignada", "en_curso")
    assert mensaje.startswith("transicion_invalida")


def test_el_evento_que_crea_la_tarea_pasa_si_no_tiene_ninguno(conn, equipo):
    tarea = _tarea_nueva(conn, equipo)
    _pasa(conn, equipo, tarea, None, "asignada")


def test_un_evento_sin_estado_anterior_se_rechaza_si_ya_tiene_historia(conn, equipo):
    tarea = _tarea_nueva(conn, equipo)
    _pasa(conn, equipo, tarea, None, "asignada")
    mensaje = _rechazo(conn, equipo, tarea, None, "en_curso")
    assert mensaje.startswith("transicion_invalida")


def test_la_regla_vale_tambien_para_la_administracion(conn, equipo):
    """El importador y la siembra escriben con `leda_admin`: la cadena no depende del rol."""
    tarea = equipo.tareas["COM"]
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException) as e:
            with conn.transaction():
                _evento(cur, tarea, "en_revision", "terminada")
    conn.rollback()
    assert e.value.diag.message_primary.startswith("transicion_invalida")
    with admin(conn) as cur:
        _evento(cur, tarea, "asignada", "en_curso")
    conn.commit()
    assert _estado(conn, tarea) == "en_curso"


# --- 2. Cancelada es terminal ---------------------------------------------------------------------

def test_de_cancelada_no_se_sale(conn, equipo):
    tarea = equipo.tareas["COM"]
    _pasa(conn, equipo, tarea, "asignada", "cancelada")
    for destino in ("asignada", "en_curso", "en_revision", "terminada"):
        mensaje = _rechazo(conn, equipo, tarea, "cancelada", destino)
        assert mensaje.startswith("transicion_invalida"), destino


def test_una_tarea_bloqueada_se_puede_cancelar(conn, equipo):
    tarea = equipo.tareas["COM"]
    _pasa(conn, equipo, tarea, "asignada", "en_curso")
    _bloquear(conn, equipo, tarea)
    _pasa(conn, equipo, tarea, "bloqueada", "cancelada")


# --- 3. Salir de bloqueada vuelve al estado previo --------------------------------------------------

def test_salir_de_bloqueada_vuelve_al_estado_que_tenia(conn, equipo):
    tarea = equipo.tareas["COM"]
    _pasa(conn, equipo, tarea, "asignada", "en_curso")
    _bloquear(conn, equipo, tarea)
    for destino in ("asignada", "en_revision", "terminada"):
        mensaje = _rechazo(conn, equipo, tarea, "bloqueada", destino)
        assert mensaje.startswith("transicion_invalida"), destino
    _pasa(conn, equipo, tarea, "bloqueada", "en_curso")


def test_una_tarea_que_nunca_arranco_vuelve_a_asignada(conn, equipo):
    """Bloqueada sin haber arrancado: no sale a `en_curso` (mecánica §3 y §4)."""
    tarea = equipo.tareas["COM"]
    _bloquear(conn, equipo, tarea)
    mensaje = _rechazo(conn, equipo, tarea, "bloqueada", "en_curso")
    assert mensaje.startswith("transicion_invalida")
    _pasa(conn, equipo, tarea, "bloqueada", "asignada")


# --- Los caminos del producto siguen pasando --------------------------------------------------------

def test_el_camino_completo_de_una_tarea(conn, equipo):
    tarea = equipo.tareas["COM"]
    _pasa(conn, equipo, tarea, "asignada", "en_curso")
    _pasa(conn, equipo, tarea, "en_curso", "en_revision")
    # Pedir cambios: vuelve al estado que tenía antes de entregarla.
    _pasa(conn, equipo, tarea, "en_revision", "en_curso")
    _pasa(conn, equipo, tarea, "en_curso", "en_revision")
    _aprobar(conn, equipo, tarea)
    _pasa(conn, equipo, tarea, "en_revision", "terminada")
    # Reabrirla quien la pidió (migración 0071).
    _pasa(conn, equipo, tarea, "terminada", "asignada")


def test_deshacer_un_inicio_anotado_por_error(conn, equipo):
    tarea = equipo.tareas["COM"]
    _pasa(conn, equipo, tarea, "asignada", "en_curso")
    _pasa(conn, equipo, tarea, "en_curso", "asignada")


# --- Objetivos: la cadena y cancelado terminal ----------------------------------------------------

def _objetivo(conn, mundo) -> str:
    with admin(conn) as cur:
        cur.execute("select objective_id from task where id = %s", (mundo.tareas["COM"],))
        padre = cur.fetchone()["objective_id"]
        cur.execute("""insert into objective (workspace_id, parent_id, tipo, titulo)
                       values (%s, %s, 'operativo', 'Ordenar la planta') returning id""",
                    (mundo.workspace_id, padre))
        objetivo = str(cur.fetchone()["id"])
    conn.commit()
    return objetivo


def _evento_objetivo(conn, objetivo: str, anterior: str | None, nuevo: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into objective_state_event (objective_id, estado_anterior,
                                                          estado_nuevo, actor_kind)
                       values (%s, %s, %s, 'sistema')""", (objetivo, anterior, nuevo))
    conn.commit()


def _rechazo_objetivo(conn, objetivo: str, anterior: str | None, nuevo: str) -> str:
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException) as e:
            with conn.transaction():
                cur.execute("""insert into objective_state_event (objective_id, estado_anterior,
                                                                  estado_nuevo, actor_kind)
                               values (%s, %s, %s, 'sistema')""", (objetivo, anterior, nuevo))
    conn.rollback()
    return e.value.diag.message_primary


def _estado_objetivo(conn, objetivo: str) -> str:
    with admin(conn) as cur:
        cur.execute("select estado::text e from objective where id = %s", (objetivo,))
        estado = cur.fetchone()["e"]
    conn.commit()
    return estado


def test_el_objetivo_encadena_sus_eventos(conn, equipo):
    objetivo = _objetivo(conn, equipo)
    _evento_objetivo(conn, objetivo, None, "activo")
    assert _rechazo_objetivo(conn, objetivo, None, "suspendido").startswith(
        "transicion_invalida")
    assert _rechazo_objetivo(conn, objetivo, "propuesto", "suspendido").startswith(
        "transicion_invalida")
    _evento_objetivo(conn, objetivo, "activo", "suspendido")
    _evento_objetivo(conn, objetivo, "suspendido", "activo")
    assert _estado_objetivo(conn, objetivo) == "activo"


def test_de_un_objetivo_cancelado_no_se_sale(conn, equipo):
    objetivo = _objetivo(conn, equipo)
    _evento_objetivo(conn, objetivo, None, "activo")
    _evento_objetivo(conn, objetivo, "activo", "cancelado")
    for destino in ("activo", "propuesto", "suspendido"):
        assert _rechazo_objetivo(conn, objetivo, "cancelado", destino).startswith(
            "transicion_invalida"), destino
    assert _estado_objetivo(conn, objetivo) == "cancelado"
