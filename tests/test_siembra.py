"""Siembra reproducible de datos ficticios (T7, `odd/tasks/prisma-orienta.md`).

`prisma.siembra.sembrar` carga un archivo YAML de semilla en un espacio recién
importado, para que la próxima base de prueba no dependa de tareas cargadas a
mano -- eso fue lo que dejó las 12 tareas ficticias de las sesiones 1 y 2 con
" (simulado)" en el título, un campo de compromiso inmutable que después no se
pudo renombrar.

Cubre:
  1. Sembrar `espacios/corework.semilla-ficticia.yaml` de punta a punta: crea
     exactamente las tareas de la semilla, ninguna con "(simulado)", con los
     estados declarados alcanzados por eventos reales, la dependencia
     declarada, y nada preaprobado ni en revisión.
  2. Las dos guardas: espacio con tareas ya cargadas, espacio inexistente.
  3. La semilla es idempotente por rechazo: una segunda corrida no agrega ni
     modifica nada.
  4. Invariantes del comprobador diario del experimento (Experimento 1,
     `odd/tasks/prisma-orienta.md`): `task.estado` es el último evento;
     ninguna tarea `en_curso` tiene una dependencia bloqueante abierta salvo
     la diseñada a propósito, y esa dependencia se cargó en un orden legal
     (la tarea ya estaba en curso antes de que la dependencia existiera).
  5. Auditoría: una sola fila en `audit_log` por siembra exitosa, con sólo
     conteos y el nombre del archivo -- nunca títulos ni personas -- y
     ninguna fila cuando la siembra se rechaza.
  6. `evidencia_policy_version` queda igual que si la tarea hubiera pasado
     por `confirmar_borrador_tarea`: la versión vigente de
     `task_evidence_policy` para el área de esa tarea, nunca `null`.
  7. Seguimientos T7b (`odd/tasks/prisma-orienta.md`): toda la validación
     corre antes del primer insert -- título repetido, `estado_inicial`
     fuera del allow-list `asignada`/`en_curso`, clave requerida faltante,
     objetivo ambiguo, archivo de semilla inexistente o YAML roto o vacío --
     y ninguna deja una fila escrita. La CLI (`cli.py`, rama `sembrar`)
     nunca deja pasar una traza cruda ni el DETAIL de la base, y revierte la
     conexión en cualquier rechazo.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import psycopg
import pytest
import yaml

from prisma.db import admin
from prisma.siembra import ResultadoSiembra, SiembraInvalida, sembrar

RAIZ = Path(__file__).resolve().parents[1]
SEMILLA_COREWORK = RAIZ / "espacios" / "corework.semilla-ficticia.yaml"


def _semilla_minima(tmp_path, *, tareas=None, dependencias=None) -> Path:
    contenido = {
        "version": 1,
        "tareas": tareas if tareas is not None else [
            {
                "titulo": "Tarea de prueba A",
                "area": "ot",
                "objetivo": "Conectar y automatizar equipos para que produzcan y entreguen datos",
                "responsable": "Nahuel Gimenez",
                "criterio_aceptacion": "Criterio de prueba",
                "evidencia_requerida": ["explicacion"],
                "fecha_objetivo": {"dias": 5},
                "estado_inicial": "asignada",
            },
        ],
        "dependencias": dependencias or [],
    }
    ruta = tmp_path / "semilla.yaml"
    ruta.write_text(yaml.safe_dump(contenido, allow_unicode=True), encoding="utf-8")
    return ruta


# ---------------------------------------------------------------------------
# 1. La semilla real de corework, de punta a punta
# ---------------------------------------------------------------------------

def test_sembrar_corework_crea_las_12_tareas_sin_simulado(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        r = sembrar(cur, ws, SEMILLA_COREWORK)

    assert isinstance(r, ResultadoSiembra)
    assert r.tareas == 12
    assert r.dependencias == 1

    with admin(conn) as cur:
        cur.execute("select titulo, estado from task where workspace_id = %s", (ws,))
        tareas = cur.fetchall()

    assert len(tareas) == 12
    for t in tareas:
        assert "(simulado)" not in t["titulo"]


def test_sembrar_corework_seis_en_curso_y_seis_asignada(corework, conn):
    """Estados iniciales documentados en el YAML y en T7
    (`odd/tasks/prisma-orienta.md`): seis `en_curso` -- una por responsable
    con aprobador -- y seis `asignada`, ninguna en otro estado."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        r = sembrar(cur, ws, SEMILLA_COREWORK)

        cur.execute(
            """select estado, count(*) as n from task
                where workspace_id = %s group by estado""", (ws,))
        por_estado = {f["estado"]: f["n"] for f in cur.fetchall()}

    assert r.estados == {"en_curso": 6, "asignada": 6}
    assert por_estado == {"en_curso": 6, "asignada": 6}


def test_sembrar_corework_no_preaprueba_ni_deja_nada_en_revision(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar(cur, ws, SEMILLA_COREWORK)

        cur.execute(
            "select count(*) as n from task where workspace_id = %s and estado = 'en_revision'",
            (ws,))
        assert cur.fetchone()["n"] == 0

        cur.execute(
            """select count(*) as n from approval a
                join task t on t.id = a.sujeto_id and a.sujeto_tipo = 'tarea'
               where t.workspace_id = %s""", (ws,))
        assert cur.fetchone()["n"] == 0


def test_sembrar_corework_estado_es_siempre_el_ultimo_evento(corework, conn):
    """Invariante del comprobador del Experimento 1: `task.estado` es una
    proyección -- tiene que coincidir con el último `task_state_event`."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar(cur, ws, SEMILLA_COREWORK)

        cur.execute(
            """select t.id, t.estado,
                      (select e.estado_nuevo from task_state_event e
                        where e.task_id = t.id order by e.at desc limit 1) as ultimo
                 from task t where t.workspace_id = %s""", (ws,))
        filas = cur.fetchall()

    assert len(filas) == 12
    for f in filas:
        assert f["estado"] == f["ultimo"]


def test_sembrar_corework_una_sola_dependencia_bloqueante_abierta_en_orden_legal(corework, conn):
    """Sólo la tarea diseñada a propósito (T6c, `odd/tasks/prisma-orienta.md`)
    tiene una dependencia bloqueante abierta mientras está `en_curso`, y la
    dependencia se cargó después de que la tarea ya estuviera en curso -- no
    la movió retroactivamente, igual que
    `test_crear_dependencia_bloqueante_sobre_destino_ya_en_curso_lo_menciona`
    en `tests/test_dependencias.py`."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar(cur, ws, SEMILLA_COREWORK)

        cur.execute(
            """select dt.id as destino_id, dt.titulo as destino, dt.estado,
                      ot.estado as estado_origen
                 from dependency d
                 join task dt on dt.id = d.destino_task_id
                 join task ot on ot.id = d.origen_task_id
                where d.workspace_id = %s and d.tipo = 'bloqueante'""", (ws,))
        deps = cur.fetchall()

        cur.execute(
            """select count(*) as n from task
                where workspace_id = %s and estado = 'en_curso'""", (ws,))
        n_en_curso = cur.fetchone()["n"]

    assert len(deps) == 1
    dep = deps[0]
    assert dep["destino"] == "Revisar comunicaciones industriales de la comprimidora"
    assert dep["estado"] == "en_curso"
    assert dep["estado_origen"] not in ("terminada", "cancelada")

    # De las tareas en_curso, sólo la destino de esa dependencia tiene una
    # bloqueante abierta: el resto arrancó limpio.
    with admin(conn) as cur:
        cur.execute(
            """select t.id from task t where t.workspace_id = %s and t.estado = 'en_curso'
                and exists (
                  select 1 from dependency d join task o on o.id = d.origen_task_id
                   where d.destino_task_id = t.id and d.tipo = 'bloqueante'
                     and o.estado not in ('terminada', 'cancelada'))""", (ws,))
        con_bloqueo_abierto = cur.fetchall()

    assert len(con_bloqueo_abierto) == 1
    assert str(con_bloqueo_abierto[0]["id"]) == str(dep["destino_id"])
    assert n_en_curso >= 1

    # `dependency` no tiene ninguna columna de fecha (`db/esquema.sql`): no
    # se puede comparar por timestamp contra `task_state_event.at`, como sí
    # se podría entre `task_state_event` y `evidence`/`approval` desde T6j.
    # `cmin` -- el contador de comandos de PostgreSQL dentro de esta misma
    # transacción -- es la prueba honesta que sí existe: `sembrar` inserta
    # todos los `task_state_event` iniciales antes de insertar ninguna
    # `dependency` (docstring del módulo), así que el evento que puso en
    # curso a la tarea destino tiene que haberse escrito en un comando
    # anterior al de la dependencia que la señala.
    with admin(conn) as cur:
        cur.execute(
            """select cmin::text::bigint as cmin from task_state_event
                where task_id = %s and estado_nuevo = 'en_curso'""",
            (dep["destino_id"],))
        cmin_evento = cur.fetchone()["cmin"]

        cur.execute(
            """select cmin::text::bigint as cmin from dependency
                where workspace_id = %s and destino_task_id = %s
                  and tipo = 'bloqueante'""",
            (ws, dep["destino_id"]))
        cmin_dependencia = cur.fetchone()["cmin"]

    assert cmin_dependencia > cmin_evento


def test_sembrar_corework_evidencia_requerida_coherente_con_la_politica_del_pack(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar(cur, ws, SEMILLA_COREWORK)

        cur.execute(
            """select t.evidencia_requerida, a.slug as area, p.evidencia_requerida as admitida
                 from task t
                 join area a on a.id = t.area_id
                 join task_evidence_policy p on p.area_id = a.id
                where t.workspace_id = %s""", (ws,))
        filas = cur.fetchall()

    assert len(filas) == 12
    for f in filas:
        assert set(f["evidencia_requerida"]) <= set(f["admitida"])
        assert f["evidencia_requerida"]  # ninguna vacía: todas piden evidencia


def test_sembrar_corework_evidencia_policy_version_igual_a_la_politica_vigente(corework, conn):
    """`task.evidencia_policy_version` tiene que quedar igual que si la tarea
    hubiera pasado por `confirmar_borrador_tarea`: la versión vigente de
    `task_evidence_policy` para su área (nunca `null`, que es como habían
    quedado las 12 tareas cargadas a mano en las sesiones 1 y 2 -- hallazgo
    lateral del Experimento 1 de invariantes)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        sembrar(cur, ws, SEMILLA_COREWORK)

        cur.execute(
            """select t.evidencia_policy_version as version_tarea,
                      p.version as version_politica
                 from task t
                 join task_evidence_policy p on p.area_id = t.area_id
                     and p.workspace_id = t.workspace_id
                where t.workspace_id = %s""", (ws,))
        filas = cur.fetchall()

    assert len(filas) == 12
    for f in filas:
        assert f["version_tarea"] is not None
        assert f["version_tarea"] == f["version_politica"]


def test_sembrar_rechaza_area_sin_politica_de_evidencia(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path)

    with admin(conn) as cur:
        cur.execute(
            """delete from task_evidence_policy
                where workspace_id = %s
                  and area_id = (select id from area where workspace_id = %s and slug = 'ot')""",
            (ws, ws))

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="política de evidencia"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# 5. Auditoría
# ---------------------------------------------------------------------------

def test_sembrar_corework_audita_una_fila_con_solo_conteos(corework, conn):
    ws = corework.workspace_id
    with admin(conn) as cur:
        r = sembrar(cur, ws, SEMILLA_COREWORK)

        cur.execute(
            """select actor_kind, actor_app_user_id, sujeto_tipo, sujeto_id, detalle
                 from audit_log
                where workspace_id = %s and accion = 'siembra_ficticia'""", (ws,))
        filas = cur.fetchall()

    assert len(filas) == 1
    fila = filas[0]
    assert fila["actor_kind"] == "sistema"
    assert fila["actor_app_user_id"] is None
    assert fila["sujeto_tipo"] == "workspace"
    assert str(fila["sujeto_id"]) == str(ws)

    detalle = fila["detalle"]
    assert detalle == {
        "archivo": SEMILLA_COREWORK.name,
        "tareas": r.tareas,
        "dependencias": r.dependencias,
        "estados": r.estados,
    }

    # Nunca títulos de tarea ni nombres de personas en el detalle auditado.
    volcado = json.dumps(detalle, ensure_ascii=False)
    for dato_privado in (
        "Mariano", "Marcos", "Nahuel", "Lucas", "Martín", "Ariel",
        "Cablear", "comprimidora", "(simulado)",
    ):
        assert dato_privado not in volcado


# ---------------------------------------------------------------------------
# 2. Guardas
# ---------------------------------------------------------------------------

def test_sembrar_rechaza_si_el_espacio_ya_tiene_tareas(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path)

    with admin(conn) as cur:
        # Una tarea "real", ajena a la semilla, ya cargada en el espacio.
        cur.execute("select id from objective where workspace_id = %s limit 1", (ws,))
        obj = cur.fetchone()["id"]
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 criterio_aceptacion)
               values (%s, %s, 'Tarea real previa',
                       (select id from area where workspace_id = %s and slug = 'ot'),
                       'criterio')
               returning id""", (ws, obj, ws))
        tarea_previa = cur.fetchone()["id"]
        cur.execute(
            "insert into task_state_event (task_id, estado_nuevo, actor_kind) "
            "values (%s, 'asignada', 'sistema')", (tarea_previa,))

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="ya tiene tareas"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 1  # nada de la semilla se coló

        cur.execute(
            """select count(*) as n from audit_log
                where workspace_id = %s and accion = 'siembra_ficticia'""", (ws,))
        assert cur.fetchone()["n"] == 0  # rechazada: ningún efecto que auditar


def test_sembrar_rechaza_si_el_espacio_no_existe(conn, tmp_path):
    ruta = _semilla_minima(tmp_path)
    ws_inexistente = str(uuid.uuid4())

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="no existe"):
            sembrar(cur, ws_inexistente, ruta)


def test_sembrar_rechaza_responsable_fuera_del_pack(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path, tareas=[{
        "titulo": "Tarea de nadie",
        "area": "ot",
        "objetivo": "Conectar y automatizar equipos para que produzcan y entreguen datos",
        "responsable": "Persona Que No Existe",
        "criterio_aceptacion": "Criterio",
        "evidencia_requerida": ["explicacion"],
        "estado_inicial": "asignada",
    }])

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="Persona Que No Existe"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0  # nada a medio cargar


def test_sembrar_rechaza_objetivo_que_no_existe(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path, tareas=[{
        "titulo": "Tarea sin objetivo válido",
        "area": "ot",
        "objetivo": "Este frente no está en el pack",
        "responsable": "Nahuel Gimenez",
        "criterio_aceptacion": "Criterio",
        "evidencia_requerida": ["explicacion"],
        "estado_inicial": "asignada",
    }])

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="no existe en este espacio"):
            sembrar(cur, ws, ruta)


def test_sembrar_rechaza_dependencia_con_titulo_fuera_de_la_semilla(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path, dependencias=[
        {"origen": "Tarea de prueba A", "destino": "Tarea que no está", "tipo": "bloqueante"},
    ])

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="no está en esta misma semilla"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0  # la tarea válida tampoco se coló


def test_sembrar_rechaza_titulo_repetido_en_la_semilla(corework, conn, tmp_path):
    ws = corework.workspace_id
    tarea = {
        "titulo": "Tarea repetida",
        "area": "ot",
        "objetivo": "Conectar y automatizar equipos para que produzcan y entreguen datos",
        "responsable": "Nahuel Gimenez",
        "criterio_aceptacion": "Criterio",
        "evidencia_requerida": ["explicacion"],
        "estado_inicial": "asignada",
    }
    ruta = _semilla_minima(tmp_path, tareas=[tarea, dict(tarea)])

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="Título repetido"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0  # ni siquiera la primera se escribió


@pytest.mark.parametrize("estado_inicial", [
    "propuesta", "pendiente_aprobacion", "en_revision", "terminada",
    "bloqueada", "cancelada",
])
def test_sembrar_rechaza_estado_inicial_no_permitido(corework, conn, tmp_path, estado_inicial):
    """Sólo `asignada`/`en_curso` -- "nada preaprobado, nada en revisión"
    (ADR 0009) en código, no sólo en la semilla."""
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path, tareas=[{
        "titulo": "Tarea con estado prohibido",
        "area": "ot",
        "objetivo": "Conectar y automatizar equipos para que produzcan y entreguen datos",
        "responsable": "Nahuel Gimenez",
        "criterio_aceptacion": "Criterio",
        "evidencia_requerida": ["explicacion"],
        "estado_inicial": estado_inicial,
    }])

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="no permitido"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


@pytest.mark.parametrize("clave", ["titulo", "area", "objetivo", "responsable"])
def test_sembrar_rechaza_tarea_sin_clave_requerida(corework, conn, tmp_path, clave):
    ws = corework.workspace_id
    tarea = {
        "titulo": "Tarea incompleta",
        "area": "ot",
        "objetivo": "Conectar y automatizar equipos para que produzcan y entreguen datos",
        "responsable": "Nahuel Gimenez",
        "criterio_aceptacion": "Criterio",
        "evidencia_requerida": ["explicacion"],
        "estado_inicial": "asignada",
    }
    del tarea[clave]
    ruta = _semilla_minima(tmp_path, tareas=[tarea])

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match=f"clave.*'{clave}'"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


def test_sembrar_rechaza_objetivo_ambiguo(corework, conn, tmp_path):
    """`objective.titulo` no tiene `unique` en `db/esquema.sql`: un segundo
    objetivo con el mismo título en el mismo espacio tiene que rechazar la
    siembra, nunca elegir uno de los dos en silencio (T7b)."""
    ws = corework.workspace_id
    titulo = "Conectar y automatizar equipos para que produzcan y entreguen datos"

    with admin(conn) as cur:
        cur.execute(
            "select tipo from objective where workspace_id = %s and titulo = %s",
            (ws, titulo))
        tipo = cur.fetchone()["tipo"]
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo, estado)
               values (%s, %s, %s, 'activo')""",
            (ws, tipo, titulo))

    ruta = _semilla_minima(tmp_path, tareas=[{
        "titulo": "Tarea contra un objetivo ambiguo",
        "area": "ot",
        "objetivo": titulo,
        "responsable": "Nahuel Gimenez",
        "criterio_aceptacion": "Criterio",
        "evidencia_requerida": ["explicacion"],
        "estado_inicial": "asignada",
    }])

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="ambiguo"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


def test_sembrar_rechaza_archivo_de_semilla_inexistente(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = tmp_path / "no-existe.yaml"

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="No se pudo leer"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


def test_sembrar_rechaza_yaml_vacio(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = tmp_path / "vacia.yaml"
    ruta.write_text("", encoding="utf-8")

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="vacío"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


def test_sembrar_rechaza_yaml_malformado(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = tmp_path / "rota.yaml"
    ruta.write_text("tareas: [a, b\n  - esto no cierra", encoding="utf-8")

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="no es un YAML válido"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


def test_sembrar_deja_que_la_base_rechace_una_autodependencia_y_no_escribe_nada(
        corework, conn, tmp_path):
    """`sembrar` no valida `origen != destino` en Python -- ya la rechaza el
    disparador `trg_evitar_ciclo_dependencia` (`db/esquema.sql`, una
    dependencia de una tarea hacia sí misma es un ciclo de largo uno) -- así
    que esto llega a la base como un rechazo real. `sembrar` no abre su
    propio SAVEPOINT (docstring del módulo): sin la transacción de
    `admin(conn)` revirtiendo alrededor, la tarea ya insertada quedaría
    escrita."""
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path, dependencias=[
        {"origen": "Tarea de prueba A", "destino": "Tarea de prueba A", "tipo": "bloqueante"},
    ])

    with pytest.raises(psycopg.Error):
        with admin(conn) as cur:
            sembrar(cur, ws, ruta)

    with admin(conn) as cur:
        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# 3. Idempotente por rechazo
# ---------------------------------------------------------------------------

def test_sembrar_es_idempotente_por_rechazo(corework, conn, tmp_path):
    ws = corework.workspace_id
    ruta = _semilla_minima(tmp_path)

    with admin(conn) as cur:
        r1 = sembrar(cur, ws, ruta)
    assert r1.tareas == 1

    with admin(conn) as cur:
        with pytest.raises(SiembraInvalida, match="ya tiene tareas"):
            sembrar(cur, ws, ruta)

        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 1  # la segunda corrida no duplicó nada


# ---------------------------------------------------------------------------
# 7. La CLI (`cli.py`, rama `sembrar`): nunca una traza cruda ni el DETAIL de
#    la base, siempre rollback en el rechazo (T7b, `odd/tasks/prisma-orienta.md`)
# ---------------------------------------------------------------------------

def test_cli_sembrar_ok_imprime_solo_conteos_y_commitea(corework, conn, monkeypatch, capsys):
    import prisma.cli as cli

    monkeypatch.setattr(cli, "conectar", lambda: conn)
    codigo = cli.main(["sembrar", "corework", "--semilla", str(SEMILLA_COREWORK)])

    assert codigo == 0
    salida = capsys.readouterr().out
    assert "12 tareas y 1 dependencias sembradas." in salida
    assert "asignada: 6" in salida
    assert "en_curso: 6" in salida
    # nunca títulos de tarea ni nombres de personas en la salida de éxito
    for dato_privado in ("comprimidora", "Marcos", "Mariano"):
        assert dato_privado not in salida

    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 12


def test_cli_sembrar_rechazo_de_validacion_sin_traza_y_sin_escribir_nada(
        corework, conn, tmp_path, monkeypatch, capsys):
    import prisma.cli as cli

    monkeypatch.setattr(cli, "conectar", lambda: conn)
    ruta_inexistente = tmp_path / "no-existe.yaml"

    codigo = cli.main(["sembrar", "corework", "--semilla", str(ruta_inexistente)])

    assert codigo == 1
    salida = capsys.readouterr().out
    assert "Traceback" not in salida
    assert "no se pudo leer" in salida.lower()

    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0


def test_cli_sembrar_rechazo_de_la_base_no_muestra_detalle_ni_escribe_nada(
        corework, conn, tmp_path, monkeypatch, capsys):
    import prisma.cli as cli

    monkeypatch.setattr(cli, "conectar", lambda: conn)
    ruta = _semilla_minima(tmp_path, dependencias=[
        {"origen": "Tarea de prueba A", "destino": "Tarea de prueba A", "tipo": "bloqueante"},
    ])

    codigo = cli.main(["sembrar", "corework", "--semilla", str(ruta)])

    assert codigo == 1
    salida = capsys.readouterr().out
    assert "Traceback" not in salida
    assert "La base rechazó la siembra" in salida
    assert "DETAIL" not in salida.upper()
    assert "constraint" not in salida.lower()
    assert "Tarea de prueba A" not in salida

    ws = corework.workspace_id
    with admin(conn) as cur:
        cur.execute("select count(*) as n from task where workspace_id = %s", (ws,))
        assert cur.fetchone()["n"] == 0
