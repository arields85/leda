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


# Las tablas con `workspace_id` que quedan sin `row level security`, cada una con su motivo. La
# regla de `AGENTS.md` ("Invariantes vigentes") es que ninguna tabla con alcance de espacio queda
# sin RLS forzada; una excepción sólo vale si ni `leda_app` ni `leda_gateway` tienen privilegio
# sobre la tabla, de modo que sólo se llega a ella por la conexión administrativa o por una
# función acotada. Una tabla nueva con `workspace_id` falla acá hasta que tenga su política o
# figure en esta lista con su motivo.
EXCEPCIONES_SIN_RLS = {
    "acceso_tablero": (
        "los enlaces del tablero: sólo se llega por las funciones que los emiten y resuelven "
        "(security definer, dueño leda_owner); leda_app no tiene privilegio sobre la tabla"),
    "activation_token": (
        "los enlaces de activación: los emite y los canjea la conexión administrativa (alta "
        "de integrantes), nunca la aplicación"),
    "admin_notice": (
        "la cola del bot de administración: no tiene un único espacio dueño (workspace_id "
        "admite nulo y queda en nulo si se borra el espacio); la escribe "
        "avisar_incidente_admin() y la despacha leda_admin"),
    "conversation_access_log": (
        "el registro de accesos del administrador a conversaciones (constitución §12): lo "
        "escribe y lo lee sólo la administración de plataforma"),
    "learning": (
        "el aprendizaje persistente, reservado (ADR 0018, decisión 3): no lo lee ni lo escribe "
        "nadie de la aplicación hasta su propio ADR"),
}

# Las cinco tablas con `workspace_id` que `leda_app` lee directamente (sólo `select`): el
# calendario laboral y los feriados, el tono del pack, la versión del pack y el modelo de la IA.
TABLAS_LEIDAS_POR_LA_APLICACION = (
    "holiday", "work_calendar", "persona_config", "workspace_version", "model_config")


def test_toda_tabla_con_espacio_tiene_rls_forzada_salvo_las_excepciones_declaradas(conn):
    """Ninguna tabla con alcance de espacio queda sin `row level security` forzada.

    Se lee el catálogo efectivo: toda tabla común del esquema `leda` con una columna
    `workspace_id`. Las que no tienen política sólo pueden ser las de `EXCEPCIONES_SIN_RLS`, y
    para esas ni la aplicación ni la conexión de autoridad pueden leer ni escribir la tabla:
    una excepción con privilegios sería un agujero sin política que lo tape.
    """
    with admin(conn) as cur:
        cur.execute(
            """select c.relname, c.relrowsecurity, c.relforcerowsecurity
                 from pg_class c
                 join pg_namespace n on n.oid = c.relnamespace
                 join pg_attribute a on a.attrelid = c.oid
                where n.nspname = 'leda' and c.relkind = 'r'
                  and a.attname = 'workspace_id' and not a.attisdropped
                order by c.relname""")
        tablas = cur.fetchall()

        assert tablas, "no se encontró ninguna tabla con workspace_id"
        nombres = {t["relname"] for t in tablas}
        sobrantes = sorted(set(EXCEPCIONES_SIN_RLS) - nombres)
        assert not sobrantes, ("excepciones que ya no son tablas con workspace_id: "
                               + ", ".join(sobrantes))

        sin_rls = [t["relname"] for t in tablas
                   if t["relname"] not in EXCEPCIONES_SIN_RLS
                   and not (t["relrowsecurity"] and t["relforcerowsecurity"])]
        assert not sin_rls, ("tablas con workspace_id sin row level security forzada: "
                             + ", ".join(sin_rls))

        cur.execute(
            """select t.tabla, r.rol, p.privilegio
                 from unnest(%s::text[]) t(tabla)
                 cross join unnest(array['leda_app', 'leda_gateway']) r(rol)
                 cross join unnest(array['select', 'insert', 'update', 'delete']) p(privilegio)
                where has_table_privilege(r.rol, 'leda.' || t.tabla, p.privilegio)
                order by 1, 2, 3""",
            (sorted(EXCEPCIONES_SIN_RLS),))
        con_privilegio = cur.fetchall()
    assert not con_privilegio, (
        "excepciones sin RLS a las que llega la aplicación: "
        + ", ".join(f"{f['tabla']} ({f['rol']}: {f['privilegio']})" for f in con_privilegio))


def test_lo_que_la_aplicacion_lee_de_un_espacio_no_muestra_filas_de_otro(intake_world, conn):
    """El calendario, los feriados, el tono, la versión del pack y el modelo de la IA de un
    espacio no se ven desde otro.

    `leda_app` lee estas cinco tablas directamente. Sin política, su aislamiento dependía del
    `where workspace_id = %s` de cada lector; con ella, una consulta sin filtro dentro de
    `espacio()` devuelve sólo las filas del espacio activo. El modelo global (`ambito =
    'global'`, sin espacio) sigue visible para todos: es la configuración por omisión.
    """
    north = intake_world["north-lab"]
    west = intake_world["west-studio"]

    with admin(conn) as cur:
        for ws in (north["id"], west["id"]):
            cur.execute("insert into holiday (workspace_id, fecha) values (%s, '2026-12-25')",
                        (ws,))
            cur.execute(
                """insert into model_config (ambito, workspace_id, proveedor, modelo)
                   values ('espacio', %s, 'openai', %s)""",
                (ws, f"modelo-{ws}"))
        cur.execute("update model_config set activo = false where ambito = 'global'")
        cur.execute(
            """insert into model_config (ambito, proveedor, modelo)
               values ('global', 'openai', 'modelo-global')""")
    conn.commit()

    with espacio(conn, north["id"]) as cur:
        for tabla in TABLAS_LEIDAS_POR_LA_APLICACION:
            cur.execute(f"select count(*) n from {tabla} where workspace_id = %s",
                        (west["id"],))
            assert cur.fetchone()["n"] == 0, f"{tabla}: se ven filas de otro espacio"
            cur.execute(f"select count(*) n from {tabla} where workspace_id = %s",
                        (north["id"],))
            assert cur.fetchone()["n"] >= 1, f"{tabla}: no se ven las filas del propio espacio"
        cur.execute(
            """select modelo from model_config where workspace_id is null and ambito = 'global'
                  and activo""")
        assert [f["modelo"] for f in cur.fetchall()] == ["modelo-global"]

    with espacio(conn, west["id"]) as cur:
        cur.execute("select pack_hash from workspace_version")
        assert [f["pack_hash"] for f in cur.fetchall()] == ["hash-1"]

    # Sin espacio fijado no se ve ninguna fila de un espacio; el modelo global, sí.
    from leda.db import sin_espacio

    with sin_espacio(conn) as cur:
        for tabla in TABLAS_LEIDAS_POR_LA_APLICACION:
            cur.execute(f"select count(*) n from {tabla} where workspace_id is not null")
            assert cur.fetchone()["n"] == 0, f"{tabla}: se ven filas sin espacio fijado"
        cur.execute("select count(*) n from model_config where ambito = 'global'")
        assert cur.fetchone()["n"] >= 1
