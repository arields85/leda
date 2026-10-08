"""El aislamiento entre espacios, la garantía número uno del producto.

Ninguna vía autorizada de cambio (los eventos de estado de una tarea, la auditoría) cruza
de un espacio a otro, y ninguna función `security definer` tiene un dueño que ignore la RLS.

Movidas desde `tests/test_task_intake.py` (E3-1).
"""

from __future__ import annotations

import uuid

import psycopg
import pytest

from leda.db import admin, espacio


def test_un_espacio_no_puede_mover_el_estado_de_una_tarea_de_otro(
        intake_world, conn):
    """El aislamiento entre clientes es la garantía número uno del producto.

    `task_state_event` es la única vía autorizada para cambiar el estado de una
    tarea: `task.estado` es su proyección. Si esa vía no está acotada por
    espacio, un cliente le mueve el trabajo a otro.
    """
    north = intake_world["north-lab"]
    west = intake_world["west-studio"]

    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, estado)
               values (%s, %s, 'Trabajo de West', %s, %s, 'asignada')
               returning id""",
            (west["id"], west["objectives"][0], west["areas"]["field"],
             west["people"]["Taylor Quinn"]["membership_id"]))
        tarea_ajena = cur.fetchone()["id"]
    conn.commit()

    inexistente = uuid.uuid4()
    errores = {}
    for etiqueta, objetivo in (("ajena", tarea_ajena),
                               ("inexistente", inexistente)):
        with espacio(conn, north["id"]) as cur:
            with pytest.raises(psycopg.Error) as excinfo, conn.transaction():
                cur.execute(
                    """insert into task_state_event
                         (task_id, estado_anterior, estado_nuevo, actor_kind,
                          actor_app_user_id, motivo)
                       values (%s, 'asignada', 'en_curso', 'persona', %s,
                               'cruce de espacios')""",
                    (objetivo,
                     north["people"]["Taylor Quinn"]["app_user_id"]))
            errores[etiqueta] = excinfo.value

    # Sin oráculo de enumeración: una tarea de otro espacio y una que no existe
    # tienen que ser indistinguibles. Si difieren, el error revela cuáles de los
    # identificadores probados son reales.
    assert type(errores["ajena"]) is type(errores["inexistente"])
    assert str(errores["ajena"]) == str(errores["inexistente"])

    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tarea_ajena,))
        assert cur.fetchone()["estado"] == "asignada"
        cur.execute(
            "select count(*) n from task_state_event where task_id = %s",
            (tarea_ajena,))
        assert cur.fetchone()["n"] == 0


def test_un_espacio_no_puede_fabricar_auditoria_en_otro(intake_world, conn):
    """La auditoría autoritativa es la prueba que se le muestra a un cliente.

    Si otro cliente puede escribir en ella, deja de ser evidencia. `audit_log`
    tiene `workspace_id` pero ninguna política, y `leda_app` tiene `insert`:
    nada impide declarar el espacio ajeno.
    """
    north = intake_world["north-lab"]
    west = intake_world["west-studio"]

    with espacio(conn, north["id"]) as cur:
        cur.execute(
            """insert into audit_log (workspace_id, actor_kind, accion)
               values (%s, 'sistema', 'auditoria-forjada')""",
            (west["id"],))

    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from audit_log
                where workspace_id = %s and accion = 'auditoria-forjada'""",
            (west["id"],))
        assert cur.fetchone()["n"] == 0, (
            "un espacio escribió auditoría atribuida a otro")


def test_ninguna_funcion_elevada_pertenece_a_un_rol_que_ignora_la_rls(conn):
    """Una función `security definer` corre con los privilegios de su dueño.

    Si ese dueño es superusuario o tiene `bypassrls`, la función ignora la
    política de aislamiento por completo: adentro de ella, la RLS que protege
    al resto del esquema no existe. Y el esquema no fija ningún propietario,
    así que hoy queda a nombre de quien haya corrido el script.

    Se lee el catálogo efectivo, no el texto del archivo: lo que importa es
    quién resultó dueño en la instalación, no qué dice el SQL.
    """
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, r.rolname, r.rolsuper, r.rolbypassrls
                 from pg_proc p
                 join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.prosecdef
                order by p.proname""")
        elevadas = cur.fetchall()

    assert elevadas, "no se encontró ninguna función security definer"
    ciegas = [f for f in elevadas if f["rolsuper"] or f["rolbypassrls"]]
    assert not ciegas, (
        "funciones elevadas cuyo dueño ignora la RLS: "
        + ", ".join(f"{f['proname']} (dueño {f['rolname']}"
                    f"{', superusuario' if f['rolsuper'] else ''}"
                    f"{', bypassrls' if f['rolbypassrls'] else ''})"
                    for f in ciegas))


def test_ninguna_funcion_elevada_tiene_el_camino_abierto_ni_la_ejecuta_cualquiera(conn):
    """Una función `security definer` fija su `search_path`, con `pg_temp` al final, y no la
    ejecuta `public`.

    Sin un `search_path` fijado, la función resuelve los nombres sin esquema con el camino de
    quien la llama: `leda_app` puede crear tablas temporales, y una tabla temporal con el nombre
    de una que la función usa la reemplazaría adentro, con los privilegios del dueño. Fijarlo no
    alcanza si `pg_temp` no está nombrado: Postgres busca las tablas temporales antes que todo lo
    que el camino nombra, salvo que se lo ponga explícitamente (al final). Y `execute` para
    `public` (lo que da Postgres por omisión al crear una función) deja llamarla a cualquier rol
    de la base, no sólo a los que la usan.

    Es una regla de todas las funciones elevadas del esquema, no de una en particular: se lee el
    catálogo efectivo.
    """
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, p.proconfig,
                      has_function_privilege('public', p.oid, 'execute') as de_public
                 from pg_proc p
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.prosecdef
                order by p.proname""")
        elevadas = cur.fetchall()

    assert elevadas, "no se encontró ninguna función security definer"

    def camino(f) -> list[str]:
        for c in f["proconfig"] or []:
            if c.startswith("search_path="):
                return [e.strip().strip('"') for e in c.removeprefix("search_path=").split(",")]
        return []

    sin_camino = [f["proname"] for f in elevadas if camino(f)[-1:] != ["pg_temp"]]
    assert not sin_camino, ("funciones elevadas sin search_path fijado con pg_temp al final: "
                            + ", ".join(sin_camino))
    de_public = [f["proname"] for f in elevadas if f["de_public"]]
    assert not de_public, ("funciones elevadas que puede ejecutar public: "
                           + ", ".join(de_public))
