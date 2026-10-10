"""Las migraciones: rollbacks ejercitados, paridad entre una instalación limpia y una base
migrada, funciones que llegan por la cadena con su dueño, preflight antes de tocar el
esquema, y el arranque que se niega a correr sin las migraciones.

Movidas desde `tests/test_task_intake.py`, `tests/test_una_respuesta.py`,
`tests/test_saludo.py` y `tests/test_bloque_copiable.py` (E3-1).
"""

from __future__ import annotations

import os
import subprocess
import threading
import time
import uuid
from pathlib import Path

import psycopg
import pytest
from psycopg.types.json import Jsonb

from leda import saludo
from leda.db import admin
from tests.historia_previa_a_leda import a_nombres_actuales


ROOT = Path(__file__).resolve().parents[2]

# Las pruebas de migración necesitan el esquema anterior a 0002. No puede ser
# HEAD: desde que 0002 y el esquema que produce se versionaron en el mismo
# commit, HEAD ya la incluye y la migración se rechaza a sí misma.
BASELINE_REF = "efa8ee2"


def esquema_base() -> str:
    """`db/esquema.sql` en `BASELINE_REF`, con los nombres actuales (ADR 0015): ese
    commit es anterior al renombre y las migraciones que se le aplican ya no lo son."""
    texto = subprocess.run(
        ["git", "show", f"{BASELINE_REF}:db/esquema.sql"], cwd=ROOT,
        check=True, capture_output=True).stdout.decode("utf-8")
    return a_nombres_actuales(texto)


def _migraciones_posteriores_a(prefijo: str) -> list[Path]:
    """Las migraciones que siguen a la indicada, descubiertas del directorio.

    Nombrarlas a mano deja cada migración nueva fuera de las comparaciones de
    paridad hasta que alguien se acuerda de agregarla, y el fallo aparece lejos
    de la causa.
    """
    return [p for p in sorted((ROOT / "db" / "migrations").glob("0*.sql"))
            if p.name[:4] > prefijo]


def _sql_script(path: Path) -> str:
    lines = path.read_text("utf-8").splitlines()
    while lines and lines[0].startswith("\\"):
        lines.pop(0)
    return "\n".join(lines)


# El Motor (migraciones 0030 y 0031): las tablas nuevas y las existentes que esas
# migraciones tocan (restricciones únicas, el mínimo del aviso previo). Los archivos
# recibidos (migración 0033; ADR 0019): sus dos tablas y el rango del tamaño máximo en
# `workspace_setting`. La evidencia de la entrega (migración 0034): las columnas nuevas de
# `evidence` y de `task_evidence_policy`, y sus dos tablas nuevas. La salida con adjuntos
# (migración 0035): su tabla. La página de la tarea (migración 0036): sus tres tablas y el
# referente de `area`. Lo que dice quien destraba (migración 0042): su tabla, y la restricción
# única de `blocker_unblocker`; que no le corresponde (migración 0043), su columna y sus dos
# restricciones; con qué bloqueo suyo está trabado (migración 0044), su columna, su referencia
# del mismo espacio y la restricción de que dice algo. Delegar (migración 0045): sus dos tablas
# y quién revisa el trabajo de `task`; de quién era la tarea y el pase sin respuesta (0046).
TABLAS_DEL_MOTOR = ("conversation_state", "conversation_turn",
                    "conversation_question", "conversation_option",
                    "scheduled_notice", "task_forecast", "blocker_unblocker",
                    "task", "blocker", "workspace_setting",
                    "archivo", "archivo_de_mensaje",
                    "evidence", "task_evidence_policy", "evidencia_retirada",
                    "archivo_de_tarea", "message_outbox_adjunto",
                    "area", "acceso_tarea", "vista_de_tarea", "message_outbox_enlace",
                    "dicho_de_quien_destraba", "pase_de_tarea", "cambio_de_responsable",
                    # El detalle de una tarea (migración 0050; decisión 33): el pedido y lo
                    # compartido.
                    "pedido_de_detalle", "tarea_compartida")

# La configuración de cada espacio (migración 0041): `leda_app` la lee directamente y tiene su
# política. `model_config` admite espacio nulo para el modelo global.
TABLAS_DE_CONFIGURACION = ("work_calendar", "holiday", "persona_config",
                           "workspace_version", "model_config")

# Las políticas de más de una tabla, además de la de aislamiento: `acceso_tarea` (migración
# 0036) se encuentra por el hash del token antes de saber su espacio, sólo desde las funciones
# de `leda_owner`.
POLITICAS_DE_MAS = {"acceso_tarea": ["resolver_por_token"]}


def _retrato_de_aislamiento(url, tablas):
    """Cómo quedó el aislamiento de unas tablas, leído del catálogo real.

    `column_default` entra a propósito (T6j, migración 0016): una migración
    puede cambiar sólo el `default` de una columna que ya existe -- ni el
    tipo, ni la nulabilidad, ni ningún privilegio -- y sin este campo
    `test_los_rollbacks_devuelven_la_base_al_estado_anterior` la daría por
    "no cambió nada observable", igual que si el rollback fuera vacío.

    `to_regclass(%s)` en vez de `%s::regclass` (pack 06, migración 0018,
    `greeting_state`): la primera migración que crea una tabla nueva y
    todavía no existe en instantáneas anteriores de la cadena -- necesario
    para que `test_los_rollbacks_devuelven_la_base_al_estado_anterior` pueda
    seguir esa misma tabla desde ANTES de que exista (0002-0017) sin que el
    cast reviente por relación inexistente; `to_regclass` devuelve `null` en
    vez de fallar, y las tres consultas de abajo devuelven cero filas para
    una tabla que todavía no está.
    """
    import psycopg
    from psycopg.rows import dict_row

    retrato = {}
    with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
        for tabla in tablas:
            columnas = db.execute(
                """select column_name, data_type, is_nullable, column_default
                     from information_schema.columns
                    where table_schema = 'leda' and table_name = %s
                    order by column_name""", (tabla,)).fetchall()
            seguridad = db.execute(
                """select relrowsecurity, relforcerowsecurity
                     from pg_class where oid = to_regclass(%s)""",
                (f"leda.{tabla}",)).fetchone()
            politicas = db.execute(
                """select polname, pg_get_expr(polqual, polrelid) as expresion
                     from pg_policy where polrelid = to_regclass(%s)
                    order by polname""", (f"leda.{tabla}",)).fetchall()
            disparadores = db.execute(
                """select tgname from pg_trigger
                    where tgrelid = to_regclass(%s) and not tgisinternal
                    order by tgname""", (f"leda.{tabla}",)).fetchall()
            permisos = db.execute(
                """select privilege_type from information_schema.role_table_grants
                    where grantee = 'leda_app' and table_schema = 'leda'
                      and table_name = %s
                    order by privilege_type""", (tabla,)).fetchall()
            # Restricciones e índices (El Motor, migraciones 0030 y 0031): una
            # migración puede agregar sólo una restricción o un índice único -- el
            # mínimo del aviso previo, la ejecución única de un mensaje -- y sin
            # esto ni la paridad ni el rollback lo verían.
            restricciones = db.execute(
                """select conname, pg_get_constraintdef(oid) as definicion
                     from pg_constraint where conrelid = to_regclass(%s)
                    order by conname""", (f"leda.{tabla}",)).fetchall()
            indices = db.execute(
                """select indexname, indexdef from pg_indexes
                    where schemaname = 'leda' and tablename = %s
                    order by indexname""", (tabla,)).fetchall()
            retrato[tabla] = {
                "columnas": columnas, "seguridad": seguridad,
                "politicas": politicas, "disparadores": disparadores,
                "permisos": permisos, "restricciones": restricciones,
                "indices": indices,
            }
    return retrato


def _retrato_de_funciones(url):
    """Definición, dueño y ACL de las funciones del esquema.

    No se filtra por `p.prosecdef` (ADR 0009, migración 0012): una migración
    puede cambiar el cuerpo de una función ordinaria -- `evidencia_pendiente`
    y la nueva rama de `motivo_no_cierra_tarea` no son `security definer`,
    no necesitan privilegios elevados -- y esa migración es igual de
    observable que una que toque una función elevada. Filtrar por
    `prosecdef` dejaba pasar como "no cambió nada" una migración que sí
    cambió una función real, sólo porque no era security definer."""
    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
        return db.execute(
            """select p.proname, pg_get_functiondef(p.oid) definicion,
                      r.rolname dueno, p.proacl::text acl
                 from pg_proc p
                 join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda'
                order by p.proname""").fetchall()


def _seguridad_de_las_funciones_elevadas(url):
    """Dueño, camino fijado y privilegios de cada función `security definer` (migración 0037):
    una instalación limpia y una base migrada tienen que darles lo mismo."""
    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
        return db.execute(
            """select p.oid::regprocedure::text firma, r.rolname dueno,
                      p.proconfig configuracion, p.proacl::text acl
                 from pg_proc p
                 join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.prosecdef
                order by 1""").fetchall()


def _retrato_migratorio(url, tablas):
    return {"tablas": _retrato_de_aislamiento(url, tablas),
            "funciones": _retrato_de_funciones(url)}


def test_los_rollbacks_devuelven_la_base_al_estado_anterior():
    """Un rollback sin ejercitar es una promesa, no un control.

    Se compara el catálogo efectivo antes y después de cada par
    migración/rollback. Se exige además que la migración haya cambiado algo:
    sin eso, la comparación pasaría igual con dos rollbacks vacíos.
    """
    maintenance = os.environ.get("LEDA_TEST_DB_URL")
    if not maintenance:
        pytest.skip("Migration rehearsal requires the pytest-authorized test server.")

    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.sql import SQL, Identifier

    tablas = ("task_state_event", "objective_state_event",
              "absence", "audit_log", "incident", "greeting_state",
              "message_outbox", "inbound_message") + TABLAS_DEL_MOTOR
    tablas += TABLAS_DE_CONFIGURACION
    nombre = f"leda_rollback_{uuid.uuid4().hex[:10]}"
    with psycopg.connect(maintenance, autocommit=True) as control:
        control.execute(SQL("create database {}").format(Identifier(nombre)))
    url = make_conninfo(**{**conninfo_to_dict(maintenance), "dbname": nombre})

    def correr(carpeta, archivo):
        with psycopg.connect(url, autocommit=True) as db:
            db.execute(_sql_script(ROOT / "db" / carpeta / archivo))

    try:
        base = esquema_base()
        with psycopg.connect(url, autocommit=True) as db:
            db.execute(base)
        correr("migrations", "0002_general_task_intake.sql")

        # Recorre la cadena descubriéndola del directorio. Nombrar las
        # migraciones a mano dejaba cada una nueva sin rollback ejercitado.
        for migracion in _migraciones_posteriores_a("0002"):
            rollback = ROOT / "db" / "rollbacks" / migracion.name
            assert rollback.is_file(), f"{migracion.name} no tiene rollback"

            antes = _retrato_migratorio(url, tablas)
            correr("migrations", migracion.name)
            despues = _retrato_migratorio(url, tablas)
            assert despues != antes, (
                f"{migracion.name} no cambió nada observable: la comparación "
                f"de abajo pasaría igual con un rollback vacío")

            correr("rollbacks", migracion.name)
            assert _retrato_migratorio(url, tablas) == antes, (
                f"el rollback de {migracion.name} no devolvió la base a su "
                f"estado anterior")

            # Se vuelve a aplicar para que la siguiente encuentre su premisa.
            correr("migrations", migracion.name)
    finally:
        with psycopg.connect(maintenance, autocommit=True) as control:
            control.execute(SQL("drop database if exists {} with (force)")
                            .format(Identifier(nombre)))


def test_instalacion_limpia_y_base_migrada_convergen_en_el_aislamiento():
    """Paridad comprobada contra dos bases reales, no comparando texto.

    La prueba textual de más abajo sólo busca cadenas en los archivos. Acá se
    instala el esquema limpio en una base, se migra otra desde el esquema
    anterior a 0002, y se comparan los catálogos efectivos: columnas, RLS,
    políticas, disparadores y privilegios. Si divergen, una instalación nueva y
    una migrada no quedan igual de aisladas.
    """
    maintenance = os.environ.get("LEDA_TEST_DB_URL")
    if not maintenance:
        pytest.skip("Migration rehearsal requires the pytest-authorized test server.")

    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.sql import SQL, Identifier

    # Todas se comparan entre limpia y migrada. `acceso_tablero` no lleva
    # política a propósito —el token se busca antes de saber el espacio— pero
    # sus privilegios sí tienen que converger: divergían, y nada lo veía
    # porque las bases de prueba se construyen desde el esquema limpio.
    tablas = ("task_state_event", "objective_state_event",
              "absence", "audit_log", "incident", "acceso_tablero",
              "greeting_state", "message_outbox", "inbound_message"
              ) + TABLAS_DEL_MOTOR + TABLAS_DE_CONFIGURACION
    con_politica = set(tablas) - {"acceso_tablero"}
    sufijo = uuid.uuid4().hex[:10]
    nombres = {"limpia": f"leda_limpia_{sufijo}",
               "migrada": f"leda_migrada_{sufijo}"}
    urls = {}
    try:
        for clave, nombre in nombres.items():
            with psycopg.connect(maintenance, autocommit=True) as control:
                control.execute(SQL("create database {}").format(Identifier(nombre)))
            urls[clave] = make_conninfo(
                **{**conninfo_to_dict(maintenance), "dbname": nombre})

        with psycopg.connect(urls["limpia"], autocommit=True) as db:
            db.execute((ROOT / "db" / "esquema.sql").read_text("utf-8"))

        base = esquema_base()
        with psycopg.connect(urls["migrada"], autocommit=True) as db:
            db.execute(base)
            for migracion in _migraciones_posteriores_a("0001"):
                db.execute(_sql_script(migracion))

        limpia = _retrato_de_aislamiento(urls["limpia"], tablas)
        migrada = _retrato_de_aislamiento(urls["migrada"], tablas)

        elevadas = {clave: _seguridad_de_las_funciones_elevadas(url)
                    for clave, url in urls.items()}
        assert elevadas["limpia"] == elevadas["migrada"], (
            "las funciones elevadas no quedan igual en la instalación limpia y en la migrada"
            f"\nlimpia:  {elevadas['limpia']}\nmigrada: {elevadas['migrada']}")

        for tabla in tablas:
            assert limpia[tabla] == migrada[tabla], (
                f"{tabla}: la instalación limpia y la base migrada no "
                f"convergen.\nlimpia:  {limpia[tabla]}\nmigrada: {migrada[tabla]}")

        for tabla in con_politica:
            assert limpia[tabla]["seguridad"]["relrowsecurity"]
            assert limpia[tabla]["seguridad"]["relforcerowsecurity"]
            assert [p["polname"] for p in limpia[tabla]["politicas"]] == sorted(
                ["aislamiento_espacio"] + POLITICAS_DE_MAS.get(tabla, []))

        # `audit_log` e `incident` admiten espacio nulo para los hechos de
        # alcance global, y `model_config` para el modelo global; el resto no
        # tiene esa excepción.
        for tabla in con_politica - {"audit_log", "incident", "model_config"}:
            assert any(c["column_name"] == "workspace_id"
                       and c["is_nullable"] == "NO"
                       for c in limpia[tabla]["columnas"]), (
                f"{tabla}: workspace_id debería ser obligatorio")
    finally:
        for nombre in nombres.values():
            with psycopg.connect(maintenance, autocommit=True) as control:
                control.execute(SQL("drop database if exists {} with (force)")
                                .format(Identifier(nombre)))


def test_0007_estado_previo_a_bloqueo_llega_por_migracion_con_dueno_correcto():
    """Corrección tras revisión: la función vivía sólo en `esquema.sql`.

    `db/migrations/README.md` dice que `esquema.sql` es la fuente para bases
    limpias de prueba nada más: una base existente (CoreWork) avanza con los
    scripts de `db/migrations/`. Sin uno para `estado_previo_a_bloqueo`,
    `resolver_bloqueo` fallaría contra ella con "function does not exist".
    """
    maintenance = os.environ.get("LEDA_TEST_DB_URL")
    if not maintenance:
        pytest.skip("Migration rehearsal requires the pytest-authorized test server.")

    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.rows import dict_row
    from psycopg.sql import SQL, Identifier

    database = f"leda_0007_migration_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(maintenance, autocommit=True) as control:
        control.execute(SQL("create database {}").format(Identifier(database)))
    url = make_conninfo(**{**conninfo_to_dict(maintenance), "dbname": database})
    try:
        baseline = esquema_base()
        with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
            db.execute(baseline)
            # Cadena completa desde el directorio, no a mano: nombrarlas dejó
            # una migración nueva fuera de esta comparación cuatro veces.
            for migracion in _migraciones_posteriores_a("0001"):
                db.execute(_sql_script(migracion))

            existe = db.execute(
                "select to_regprocedure("
                "'leda.estado_previo_a_bloqueo(uuid)') as f"
            ).fetchone()["f"]
            assert existe is not None, (
                "estado_previo_a_bloqueo no llegó por la cadena de migraciones")

            fila = db.execute(
                """select r.rolname dueno,
                          has_function_privilege('public',
                            'leda.estado_previo_a_bloqueo(uuid)', 'execute') publico,
                          has_function_privilege('leda_app',
                            'leda.estado_previo_a_bloqueo(uuid)', 'execute') app
                     from pg_proc p join pg_roles r on r.oid = p.proowner
                    where p.oid = 'leda.estado_previo_a_bloqueo(uuid)'::regprocedure"""
            ).fetchone()
            assert fila["dueno"] == "leda_owner"
            assert fila["publico"] is False
            assert fila["app"] is True
    finally:
        with psycopg.connect(maintenance, autocommit=True) as control:
            control.execute(SQL("drop database if exists {} with (force)").format(
                Identifier(database)))


def test_0008_motivo_no_arranca_tarea_llega_por_migracion():
    """El freno de `en_curso` (mecánica §4) vive en un disparador que llama a
    `motivo_no_arranca_tarea`. Sin una migración para esa función y ese
    disparador, una base existente (CoreWork) los tendría en `esquema.sql`
    nada más -- que `db/migrations/README.md` reserva para bases limpias de
    prueba -- y `actualizar_estado` podría mover una tarea a `en_curso` con
    su bloqueante sin terminar.
    """
    maintenance = os.environ.get("LEDA_TEST_DB_URL")
    if not maintenance:
        pytest.skip("Migration rehearsal requires the pytest-authorized test server.")

    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.rows import dict_row
    from psycopg.sql import SQL, Identifier

    database = f"leda_0008_migration_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(maintenance, autocommit=True) as control:
        control.execute(SQL("create database {}").format(Identifier(database)))
    url = make_conninfo(**{**conninfo_to_dict(maintenance), "dbname": database})
    try:
        baseline = esquema_base()
        with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
            db.execute(baseline)
            for migracion in _migraciones_posteriores_a("0001"):
                db.execute(_sql_script(migracion))

            existe = db.execute(
                "select to_regprocedure("
                "'leda.motivo_no_arranca_tarea(uuid)') as f"
            ).fetchone()["f"]
            assert existe is not None, (
                "motivo_no_arranca_tarea no llegó por la cadena de migraciones")

            disparador = db.execute(
                """select tgenabled from pg_trigger
                    where tgname = 'trg_exigir_dependencias_resueltas'
                      and tgrelid = 'leda.task_state_event'::regclass"""
            ).fetchone()
            assert disparador is not None, (
                "trg_exigir_dependencias_resueltas no llegó por la cadena de migraciones")
    finally:
        with psycopg.connect(maintenance, autocommit=True) as control:
            control.execute(SQL("drop database if exists {} with (force)").format(
                Identifier(database)))


def test_migration_rejects_mojibake_then_accepts_zero_unit1a_rows():
    maintenance = os.environ.get("LEDA_TEST_DB_URL")
    if not maintenance:
        pytest.skip("Migration rehearsal requires the pytest-authorized test server.")

    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.rows import dict_row
    from psycopg.sql import SQL, Identifier

    database = f"leda_empty_migration_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(maintenance, autocommit=True) as control:
        control.execute(SQL("create database {}").format(Identifier(database)))
    url = make_conninfo(**{**conninfo_to_dict(maintenance), "dbname": database})
    try:
        baseline = esquema_base()
        migration = _sql_script(
            ROOT / "db" / "migrations" / "0002_general_task_intake.sql")
        with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
            db.execute(baseline)
            mojibake = migration.encode("utf-8").decode("latin-1")
            with pytest.raises(psycopg.errors.RaiseException,
                               match="unmodified UTF-8 input stream"):
                db.execute(mojibake)
            db.execute("rollback")
            assert db.execute(
                "select to_regclass('leda.task_intake_request') table_name"
            ).fetchone()["table_name"] is None
            db.execute(migration)
            assert db.execute(
                "select to_regclass('leda.task_intake_request') table_name"
            ).fetchone()["table_name"] in {
                "task_intake_request", "leda.task_intake_request"}
            assert db.execute(
                "select count(*) n from leda.task_draft"
            ).fetchone()["n"] == 0
    finally:
        with psycopg.connect(maintenance, autocommit=True) as control:
            control.execute(SQL("drop database if exists {} with (force)").format(
                Identifier(database)))


def test_migration_reconciles_legacy_and_guarded_rollback_restores_it(conn):
    maintenance = os.environ.get("LEDA_TEST_DB_URL")
    if not maintenance:
        pytest.skip("Migration rehearsal requires the pytest-authorized test server.")

    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.rows import dict_row
    from psycopg.sql import SQL, Identifier

    database = f"leda_migration_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(maintenance, autocommit=True) as control:
        control.execute(SQL("create database {}").format(Identifier(database)))
    url = make_conninfo(**{**conninfo_to_dict(maintenance), "dbname": database})
    try:
        baseline = esquema_base()
        migration = _sql_script(
            ROOT / "db" / "migrations" / "0002_general_task_intake.sql")
        rollback = _sql_script(
            ROOT / "db" / "rollbacks" / "0002_general_task_intake.sql")

        with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
            db.execute(baseline)
            db.execute("set search_path = leda, public")
            ws = db.execute(
                """insert into workspace (slug, nombre, activo)
                   values ('migration-lab', 'Migration Lab', true) returning id"""
            ).fetchone()["id"]
            area = db.execute(
                """insert into area (workspace_id, slug, nombre)
                   values (%s, 'ops', 'Operations') returning id""", (ws,)
            ).fetchone()["id"]
            role = db.execute(
                """insert into rol (workspace_id, slug, nombre, autoridad_final)
                   values (%s, 'owner', 'Owner', true) returning id""", (ws,)
            ).fetchone()["id"]
            user = db.execute(
                """insert into app_user (telegram_user_id, nombre)
                   values (990001, 'Migration User') returning id"""
            ).fetchone()["id"]
            member = db.execute(
                """insert into membership
                     (workspace_id, app_user_id, area_id, rol_id)
                   values (%s, %s, %s, %s) returning id""",
                (ws, user, area, role),
            ).fetchone()["id"]
            objective = db.execute(
                """insert into objective (workspace_id, tipo, titulo, estado)
                   values (%s, 'operativo', 'Migration objective', 'activo')
                   returning id""", (ws,),
            ).fetchone()["id"]
            db.execute(
                """insert into task_evidence_policy
                     (workspace_id, area_id, evidencia_requerida, version)
                   values (%s, %s, array['migration proof'], 1)""",
                (ws, area),
            )

            legacy_drafts = {}
            legacy_pending = {}
            for index, pending_state in enumerate(("esperando", "cancelada", "resuelta")):
                draft = db.execute(
                    """insert into task_draft
                         (workspace_id, creado_por_membership_id, objective_id,
                          objective_snapshot, titulo, descripcion, area_id,
                          responsable_membership_id, fecha_objetivo,
                          criterio_aceptacion, evidencia_requerida,
                          evidencia_policy_version)
                       values (%s, %s, %s,
                          jsonb_build_object('id', %s::uuid,
                                             'titulo', 'Migration objective',
                                             'estado', 'activo'),
                          %s, %s, %s, %s, '2028-03-01', 'Migration accepted',
                          array['migration proof'], 1)
                       returning id, version""",
                    (ws, member, objective, objective,
                     f"Legacy {pending_state}", f"Description {pending_state}",
                     area, member),
                ).fetchone()
                preview = db.execute(
                    """select jsonb_build_object(
                         'draft_id', id::text, 'version', version,
                         'titulo', titulo, 'objetivo', objective_snapshot,
                         'area_id', area_id::text,
                         'responsable_membership_id', responsable_membership_id::text,
                         'fecha_objetivo', fecha_objetivo::text,
                         'criterio_aceptacion', criterio_aceptacion,
                         'evidencia_requerida', to_jsonb(evidencia_requerida),
                         'evidencia_policy_version', evidencia_policy_version) preview
                         from task_draft where id = %s""",
                    (draft["id"],),
                ).fetchone()["preview"]
                pending_row = db.execute(
                    """insert into pending_action
                         (workspace_id, membership_id, herramienta, args, resumen,
                          estado, vence_en, chat_id, draft_id, draft_version, preview)
                       values (%s, %s, 'confirmar_borrador_tarea', '{}', 'legacy preview',
                               %s, now() + interval '1 hour', 990001, %s, %s, %s)
                       returning id""",
                    (ws, member, pending_state, draft["id"], draft["version"],
                     Jsonb(preview)),
                ).fetchone()["id"]
                db.execute(
                    """insert into pending_action_option
                         (workspace_id, pending_action_id, token, etiqueta, valor)
                       values (%s, %s, %s, 'Confirmar', 'true')""",
                    (ws, pending_row, f"legacy-unit1a-{index:02d}"),
                )
                legacy_drafts[pending_state] = draft["id"]
                legacy_pending[pending_state] = pending_row

            converted_task = db.execute(
                """insert into task
                     (workspace_id, objective_id, titulo, descripcion, area_id,
                      responsable_membership_id, fecha_objetivo,
                      criterio_aceptacion, evidencia_requerida,
                      evidencia_policy_version, source_draft_id)
                   values (%s, %s, 'Legacy converted', 'Description resuelta', %s,
                           %s, '2028-03-01', 'Migration accepted',
                           array['migration proof'], 1, %s)
                   returning id""",
                (ws, objective, area, member, legacy_drafts["resuelta"]),
            ).fetchone()["id"]
            db.execute("update task_draft set converted_task_id = %s where id = %s",
                       (converted_task, legacy_drafts["resuelta"]))
            pending = db.execute(
                """insert into pending_action
                     (workspace_id, membership_id, herramienta, args, resumen,
                      vence_en, chat_id)
                   values (%s, %s, 'crear_tarea', '{}', 'legacy',
                           now() + interval '1 hour', 990001) returning id""",
                (ws, member),
            ).fetchone()["id"]
            db.execute(
                """insert into pending_action_option
                     (workspace_id, pending_action_id, token, etiqueta, valor)
                   values (%s, %s, 'legacy-token-001', 'Confirmar', 'true')""",
                (ws, pending),
            )
            outbox = db.execute(
                """insert into message_outbox
                     (workspace_id, chat_id, cuerpo, estado, dedupe_key,
                      pending_action_id)
                   values (%s, 990001, 'legacy', 'listo', 'legacy-outbox', %s)
                   returning id""",
                (ws, pending),
            ).fetchone()["id"]

            db.execute(migration)
            migrated_states = db.execute(
                """select id, estado from task_draft where id = any(%s)
                   order by estado""",
                (list(legacy_drafts.values()),),
            ).fetchall()
            assert {str(row["id"]): row["estado"] for row in migrated_states} == {
                str(legacy_drafts["esperando"]): "open",
                str(legacy_drafts["cancelada"]): "cancelled",
                str(legacy_drafts["resuelta"]): "converted",
            }
            for state, pending_id in legacy_pending.items():
                migrated_preview = db.execute(
                    "select preview, resultado from pending_action where id = %s",
                    (pending_id,),
                ).fetchone()
                assert migrated_preview["preview"]["descripcion"] == f"Description {state}"
                assert migrated_preview["resultado"]["preview_description_backfilled"]
            row = db.execute(
                "select estado, resultado from pending_action where id = %s",
                (pending,),
            ).fetchone()
            assert row["estado"] == "cancelada"
            assert row["resultado"]["migration"] == "0002"
            assert db.execute(
                "select activa from pending_action_option where pending_action_id = %s",
                (pending,),
            ).fetchone()["activa"] is False
            assert db.execute(
                "select estado from message_outbox where id = %s", (outbox,),
            ).fetchone()["estado"] == "descartado"

            db.execute("begin")
            converted = db.execute(
                "select * from confirmar_borrador_tarea(%s, %s, 990001, 990001)",
                (ws, "legacy-unit1a-00"),
            ).fetchone()
            assert converted["resultado"] == "ok"
            terminal_body = db.execute(
                """select cuerpo from message_outbox
                    where dedupe_key = %s""",
                (f"{ws}:intake-terminal:{legacy_pending['esperando']}:converted",),
            ).fetchone()["cuerpo"]
            assert terminal_body == "Hecho. La tarea quedó comprometida."
            db.execute("rollback")

            signatures = db.execute(
                """select p.proname, pg_get_function_identity_arguments(p.oid) args
                     from pg_proc p join pg_namespace n on n.oid = p.pronamespace
                    where n.nspname = 'leda'
                      and p.proname in ('confirmar_borrador_tarea',
                                        'resolver_ingreso_borrador')
                    order by p.proname, args"""
            ).fetchall()
            assert signatures == [
                {"proname": "confirmar_borrador_tarea",
                 "args": "p_workspace_id uuid, p_token text, p_telegram_user_id bigint, p_chat_id bigint"},
                {"proname": "resolver_ingreso_borrador",
                 "args": "p_workspace_id uuid, p_token text, p_telegram_user_id bigint, p_chat_id bigint"},
            ]
            for function in ("confirmar_borrador_tarea", "resolver_ingreso_borrador"):
                signature = f"leda.{function}(uuid,text,bigint,bigint)"
                assert db.execute(
                    "select has_function_privilege('leda_gateway', %s, 'execute') ok",
                    (signature,),
                ).fetchone()["ok"]
                assert not db.execute(
                    "select has_function_privilege('leda_app', %s, 'execute') ok",
                    (signature,),
                ).fetchone()["ok"]
                assert not db.execute(
                    """select exists (
                         select 1
                           from pg_proc p,
                                aclexplode(coalesce(p.proacl,
                                  acldefault('f', p.proowner))) acl
                          where p.oid = %s::regprocedure and acl.grantee = 0
                            and acl.privilege_type = 'EXECUTE') ok""",
                    (signature,),
                ).fetchone()["ok"]

            inbound = db.execute(
                """insert into inbound_message
                     (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
                   values (%s, 1300, 990001, %s, 'terminal migration') returning id""",
                (ws, user),
            ).fetchone()["id"]
            draft = db.execute(
                """insert into task_draft (workspace_id, creado_por_membership_id)
                   values (%s, %s) returning id""",
                (ws, member),
            ).fetchone()["id"]
            request = db.execute(
                """insert into task_intake_request
                     (workspace_id, membership_id, chat_id, task_draft_id,
                      source_inbound_id, source_raw_text)
                   values (%s, %s, 990001, %s, %s, 'terminal migration') returning id""",
                (ws, member, draft, inbound),
            ).fetchone()["id"]
            terminal_pending = db.execute(
                """insert into pending_action
                     (workspace_id, membership_id, herramienta, args, resumen,
                      vence_en, chat_id, draft_id, draft_version, preview)
                   values (%s, %s, 'confirmar_borrador_tarea', '{}', 'preview',
                           now() + interval '1 hour', 990001, %s, 1, '{}') returning id""",
                (ws, member, draft),
            ).fetchone()["id"]
            terminal_token = "migration-terminal-token"
            db.execute(
                """insert into pending_action_option
                     (workspace_id, pending_action_id, token, etiqueta, valor)
                   values (%s, %s, %s, 'Cancelar', 'false')""",
                (ws, terminal_pending, terminal_token),
            )
            terminal = db.execute(
                "select * from confirmar_borrador_tarea(%s, %s, 990001, 990001)",
                (ws, terminal_token),
            ).fetchone()
            assert terminal["resultado"] == "cancelada"
            assert db.execute(
                "select estado from task_intake_request where id = %s", (request,),
            ).fetchone()["estado"] == "cancelled"
            assert db.execute(
                "select count(*) n from message_outbox where dedupe_key = %s",
                (f"{ws}:intake-terminal:{terminal_pending}:cancelled",),
            ).fetchone()["n"] == 1

            # Hasta acá la base migrada sólo tiene 0002, que es lo que este
            # caso ejercita. La comparación de abajo exige la cadena completa:
            # sin ella diverge por cada migración posterior, y el fallo culpa
            # a la instalación limpia en vez de a la cadena incompleta. La 0032
            # se niega a borrar solicitudes del alta guiada: la de este caso ya
            # cumplió su papel y se borra antes.
            db.execute("delete from task_intake_request where id = %s", (request,))
            for posterior in _migraciones_posteriores_a("0002"):
                db.execute(_sql_script(posterior))

            clean_functions = {}
            with admin(conn) as clean:
                for function in ("confirmar_borrador_tarea", "resolver_ingreso_borrador"):
                    clean.execute(
                        """select pg_get_functiondef(%s::regprocedure) definition,
                                  p.proacl, r.rolname owner
                             from pg_proc p join pg_roles r on r.oid = p.proowner
                            where p.oid = %s::regprocedure""",
                        (f"leda.{function}(uuid,text,bigint,bigint)",
                         f"leda.{function}(uuid,text,bigint,bigint)"),
                    )
                    clean_functions[function] = clean.fetchone()
            for function in ("confirmar_borrador_tarea", "resolver_ingreso_borrador"):
                migrated_function = db.execute(
                    """select pg_get_functiondef(%s::regprocedure) definition,
                              p.proacl, r.rolname owner
                         from pg_proc p join pg_roles r on r.oid = p.proowner
                        where p.oid = %s::regprocedure""",
                    (f"leda.{function}(uuid,text,bigint,bigint)",
                     f"leda.{function}(uuid,text,bigint,bigint)"),
                ).fetchone()
                assert migrated_function == clean_functions[function]
            with admin(conn) as clean:
                clean.execute(
                    """select pg_get_functiondef('leda.telegram_utf16_units(text)'::regprocedure)
                       definition"""
                )
                clean_utf16 = clean.fetchone()["definition"]
            migrated_utf16 = db.execute(
                """select pg_get_functiondef(
                     'leda.telegram_utf16_units(text)'::regprocedure) definition"""
            ).fetchone()["definition"]
            assert migrated_utf16 == clean_utf16

            # Lo que sigue ejercita la vuelta atrás de la 0002, que necesita las
            # tablas del alta guiada: se deshace la 0032 (las recrea vacías) y la
            # base queda donde esa vuelta atrás espera encontrarla. Antes, la 0045 y la 0036,
            # cuyas claves compuestas por espacio apuntan a la restricción única de
            # `membership` que la vuelta atrás de la 0002 borra (la 0045 primero: vuelve a
            # dejar las funciones de la página como las dejó la 0036), y antes de la 0045, la
            # 0046, que deja la tarea y el pase como los espera aquélla. Antes de todas, la 0050,
            # cuyas claves también apuntan ahí (el detalle de una tarea, decisión 33), y antes
            # de ella la 0051, que suma otra (quién decidió el pedido).
            db.execute(_sql_script(
                ROOT / "db" / "rollbacks" / "0051_las_revisiones_de_la_c5d_y_del_detalle.sql"))
            db.execute(_sql_script(
                ROOT / "db" / "rollbacks" / "0050_el_detalle_de_una_tarea.sql"))
            db.execute(_sql_script(
                ROOT / "db" / "rollbacks" / "0046_la_revision_sigue_a_quien_era_la_tarea.sql"))
            db.execute(_sql_script(
                ROOT / "db" / "rollbacks" / "0045_pase_de_tarea.sql"))
            db.execute(_sql_script(
                ROOT / "db" / "rollbacks" / "0036_pagina_de_la_tarea.sql"))
            db.execute(_sql_script(
                ROOT / "db" / "rollbacks" / "0032_borrar_el_alta_guiada.sql"))

            db.execute("delete from message_outbox where pending_action_id = %s",
                       (terminal_pending,))
            db.execute("delete from audit_log where sujeto_id = %s", (draft,))
            db.execute("delete from pending_action where id = %s", (terminal_pending,))
            db.execute("delete from task_draft where id = %s", (draft,))
            db.execute("delete from inbound_message where id = %s", (inbound,))
            db.execute("update task_draft set converted_task_id = null where id = %s",
                       (legacy_drafts["resuelta"],))
            db.execute("delete from task where id = %s", (converted_task,))
            db.execute("delete from pending_action where id = %s",
                       (legacy_pending["resuelta"],))
            db.execute("delete from task_draft where id = %s",
                       (legacy_drafts["resuelta"],))

        writer = psycopg.connect(url, row_factory=dict_row)
        writer.execute("set search_path = leda, public")
        draft = writer.execute(
            """insert into task_draft (workspace_id, creado_por_membership_id)
               values (%s, %s) returning id""",
            (ws, member),
        ).fetchone()["id"]
        inbound = writer.execute(
            """insert into inbound_message
                 (workspace_id, telegram_message_id, chat_id, app_user_id, texto)
               values (%s, 1400, 990001, %s, 'rollback race') returning id""",
            (ws, user),
        ).fetchone()["id"]
        writer.execute(
            """insert into task_intake_request
                 (workspace_id, membership_id, chat_id, task_draft_id,
                  source_inbound_id, source_raw_text)
               values (%s, %s, 990001, %s, %s, 'rollback race')""",
            (ws, member, draft, inbound),
        )
        rollback_failure = []

        def attempt_rollback():
            try:
                with psycopg.connect(url, autocommit=True, row_factory=dict_row) as other:
                    other.execute(rollback)
            except Exception as exc:
                rollback_failure.append(exc)

        rollback_thread = threading.Thread(target=attempt_rollback)
        rollback_thread.start()
        time.sleep(0.2)
        assert rollback_thread.is_alive()
        writer.commit()
        writer.close()
        rollback_thread.join(timeout=5)
        assert rollback_failure

        with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
            assert db.execute(
                "select to_regclass('leda.task_intake_request') table_name"
            ).fetchone()["table_name"] == "leda.task_intake_request"
            db.execute("set search_path = leda, public")
            db.execute("delete from task_intake_request")
            db.execute("delete from task_draft where id = %s", (draft,))
            db.execute("delete from inbound_message where id = %s", (inbound,))

            db.execute(rollback)
            assert db.execute(
                "select estado from pending_action where id = %s", (pending,),
            ).fetchone()["estado"] == "esperando"
            assert db.execute(
                "select estado from message_outbox where id = %s", (outbox,),
            ).fetchone()["estado"] == "listo"
            assert db.execute(
                "select to_regclass('leda.task_intake_request') as table_name"
            ).fetchone()["table_name"] is None
            for state in ("esperando", "cancelada"):
                restored = db.execute(
                    "select estado, preview from pending_action where id = %s",
                    (legacy_pending[state],),
                ).fetchone()
                assert restored["estado"] == state
                assert "descripcion" not in restored["preview"]
    finally:
        with psycopg.connect(maintenance, autocommit=True) as control:
            control.execute(SQL("drop database if exists {} with (force)").format(
                Identifier(database)))


@pytest.mark.parametrize("shape", ("wrong_preview", "converted_waiting",
                                   "resolved_without_conversion"))
def test_migration_preflight_fails_before_ddl_for_incompatible_unit1a_rows(
        shape):
    maintenance = os.environ.get("LEDA_TEST_DB_URL")
    if not maintenance:
        pytest.skip("Migration rehearsal requires the pytest-authorized test server.")

    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg.rows import dict_row
    from psycopg.sql import SQL, Identifier

    database = f"leda_preflight_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(maintenance, autocommit=True) as control:
        control.execute(SQL("create database {}").format(Identifier(database)))
    url = make_conninfo(**{**conninfo_to_dict(maintenance), "dbname": database})
    try:
        baseline = esquema_base()
        migration = _sql_script(
            ROOT / "db" / "migrations" / "0002_general_task_intake.sql")
        with psycopg.connect(url, autocommit=True, row_factory=dict_row) as db:
            db.execute(baseline)
            db.execute("set search_path = leda, public")
            ws = db.execute(
                "insert into workspace (slug, nombre) values ('preflight', 'Preflight') returning id"
            ).fetchone()["id"]
            area = db.execute(
                "insert into area (workspace_id, slug, nombre) values (%s, 'ops', 'Ops') returning id",
                (ws,),
            ).fetchone()["id"]
            role = db.execute(
                """insert into rol (workspace_id, slug, nombre, autoridad_final)
                   values (%s, 'owner', 'Owner', true) returning id""", (ws,),
            ).fetchone()["id"]
            user = db.execute(
                "insert into app_user (telegram_user_id, nombre) values (991001, 'Owner') returning id"
            ).fetchone()["id"]
            member = db.execute(
                """insert into membership (workspace_id, app_user_id, area_id, rol_id)
                   values (%s, %s, %s, %s) returning id""",
                (ws, user, area, role),
            ).fetchone()["id"]
            objective = db.execute(
                """insert into objective (workspace_id, tipo, titulo, estado)
                   values (%s, 'operativo', 'Objective', 'activo') returning id""", (ws,),
            ).fetchone()["id"]
            db.execute(
                """insert into task_evidence_policy
                     (workspace_id, area_id, evidencia_requerida, version)
                   values (%s, %s, array['proof'], 1)""", (ws, area),
            )
            draft = db.execute(
                """insert into task_draft
                     (workspace_id, creado_por_membership_id, objective_id,
                      objective_snapshot, titulo, descripcion, area_id,
                      responsable_membership_id, fecha_objetivo,
                      criterio_aceptacion, evidencia_requerida,
                      evidencia_policy_version)
                   values (%s, %s, %s,
                           jsonb_build_object('id', %s::uuid, 'titulo', 'Objective',
                                              'estado', 'activo'),
                           'Legacy', 'Description', %s, %s, '2028-03-01',
                           'Accepted', array['proof'], 1)
                   returning id, version""",
                (ws, member, objective, objective, area, member),
            ).fetchone()
            preview = db.execute(
                """select jsonb_build_object(
                     'draft_id', id::text, 'version', version, 'titulo', titulo,
                     'objetivo', objective_snapshot, 'area_id', area_id::text,
                     'responsable_membership_id', responsable_membership_id::text,
                     'fecha_objetivo', fecha_objetivo::text,
                     'criterio_aceptacion', criterio_aceptacion,
                     'evidencia_requerida', to_jsonb(evidencia_requerida),
                     'evidencia_policy_version', evidencia_policy_version) preview
                     from task_draft where id = %s""", (draft["id"],),
            ).fetchone()["preview"]
            pending_state = "resuelta" if shape == "resolved_without_conversion" else "esperando"
            if shape == "wrong_preview":
                preview = {"wrong": True}
            db.execute(
                """insert into pending_action
                     (workspace_id, membership_id, herramienta, args, resumen, estado,
                      vence_en, chat_id, draft_id, draft_version, preview)
                   values (%s, %s, 'confirmar_borrador_tarea', '{}', 'legacy', %s,
                           now() + interval '1 hour', 991001, %s, %s, %s)""",
                (ws, member, pending_state, draft["id"], draft["version"], Jsonb(preview)),
            )
            if shape == "converted_waiting":
                task = db.execute(
                    """insert into task
                         (workspace_id, objective_id, titulo, descripcion, area_id,
                          responsable_membership_id, fecha_objetivo,
                          criterio_aceptacion, evidencia_requerida,
                          evidencia_policy_version, source_draft_id)
                       values (%s, %s, 'Legacy', 'Description', %s, %s, '2028-03-01',
                               'Accepted', array['proof'], 1, %s) returning id""",
                    (ws, objective, area, member, draft["id"]),
                ).fetchone()["id"]
                db.execute("update task_draft set converted_task_id = %s where id = %s",
                           (task, draft["id"]))

            with pytest.raises(psycopg.errors.RaiseException,
                               match="0002 preflight failed"):
                db.execute(migration)
            db.execute("rollback")
            assert db.execute(
                """select count(*) n from information_schema.columns
                    where table_schema = 'leda' and table_name = 'task_draft'
                      and column_name = 'estado'"""
            ).fetchone()["n"] == 0
            assert db.execute(
                "select to_regclass('leda.task_intake_request') table_name"
            ).fetchone()["table_name"] is None
    finally:
        with psycopg.connect(maintenance, autocommit=True) as control:
            control.execute(SQL("drop database if exists {} with (force)").format(
                Identifier(database)))


# ---------------------------------------------------------------------------
# El arranque se niega sin las migraciones (R4-003, revisión 2026-09-28+3): sin
# ellas, cualquier despacho o encolado de un mensaje personal rompe con
# UndefinedTable/UndefinedColumn. `verificar_migraciones` es el chequeo que
# `cli.py` corre antes de `escuchar`/`servir`. Cursor falso: no hace falta tocar el
# esquema real de la sesión de pruebas para simular "falta algo".
# ---------------------------------------------------------------------------

class _CursorFalso:
    """Devuelve, en orden, cada uno de `resultados` -- un por `execute`. Sin
    tocar ninguna base real: `verificar_migraciones` hace como mucho dos
    consultas, siempre de sólo lectura sobre el catálogo."""

    def __init__(self, resultados: list[dict]):
        self._resultados = list(resultados)
        self._actual = None

    def execute(self, *a, **k):
        self._actual = self._resultados.pop(0)

    def fetchone(self):
        return self._actual


def test_verificar_migraciones_todo_al_dia_devuelve_none(corework, conn):
    with admin(conn) as cur:
        assert saludo.verificar_migraciones(cur) is None


def test_verificar_migraciones_sin_greeting_state_nombra_la_0018():
    cur = _CursorFalso([{"ok": False}])
    assert saludo.verificar_migraciones(cur) == "0018_saludo_diario.sql"


def test_verificar_migraciones_sin_es_bienvenida_nombra_la_0019():
    cur = _CursorFalso([{"ok": True}, {"ok": False}])
    assert saludo.verificar_migraciones(cur) == "0019_marca_de_bienvenida.sql"


def test_verificar_migraciones_sin_bloque_copiable_nombra_la_0020():
    class _Cursor:
        def __init__(self, respuestas):
            self._respuestas = list(respuestas)
            self._actual = None

        def execute(self, *a, **k):
            self._actual = self._respuestas.pop(0)

        def fetchone(self):
            return self._actual

    cur = _Cursor([{"ok": True}, {"ok": True}, {"ok": False}])
    assert saludo.verificar_migraciones(cur) == "0020_bloque_copiable.sql"


def test_verificar_migraciones_al_dia_devuelve_none(corework, conn):
    with admin(conn) as cur:
        assert saludo.verificar_migraciones(cur) is None


def test_el_arranque_avisa_que_falta_la_migracion_0021():
    from leda import saludo

    class _Cursor:
        def __init__(self, respuestas):
            self._respuestas = list(respuestas)
            self._actual = None

        def execute(self, *a, **k):
            self._actual = self._respuestas.pop(0)

        def fetchone(self):
            return self._actual

    cur = _Cursor([{"ok": True}, {"ok": True}, {"ok": True}, {"ok": False}])
    assert saludo.verificar_migraciones(cur) == "0021_respuesta_atada_al_mensaje.sql"


def test_con_el_esquema_al_dia_el_arranque_no_pide_migraciones(corework, conn):
    from leda import saludo

    with admin(conn) as cur:
        assert saludo.verificar_migraciones(cur) is None
