"""La carga de una tarea desde la puerta de administración (ADR 0022, decisiones 9, 11 y 12; ADR
0017, decisión 2; porción 2, tarea P2-2 de `odd/tasks/plataforma-p2.md`; migración 0062): la
capa de garantías, en la base y en la entrada HTTP.

- **El día hábil del espacio, en SQL** (`es_dia_habil`): el mismo que `Calendario.es_habil`.
- **La carga la hace una función de la base** (`cargar_tarea`, `security definer` de
  `leda_owner`, sólo para `leda_app`): comprueba la sesión de administración (el rol de
  plataforma vigente) en cada llamada y que el espacio exista, y fija ella misma ese espacio, así
  que la RLS no le deja encontrar un objetivo ni una persona de otro espacio. Nunca confía en un
  id sin esa comprobación (riesgo 4 de `docs/STATUS.md`).
- **Lo que no se carga** (decisión 9), devuelto todo junto: sin objetivo, título, responsable,
  fecha, criterio o evidencia; un objetivo de otro espacio o que no está abierto; un día no hábil
  o pasado; alguien que no es integrante activo; nadie que pueda revisarla (tampoco la autoridad
  final sin aprobador, que se revisaría a sí misma); quien la decidió, si no es integrante
  activo; un tipo de evidencia que la política del área no conoce.
- **Lo que se avisa y no bloquea:** un responsable sin Leda conectada.
- **Una tarea no vence después que su objetivo** (decisión 6 del usuario, 2026-10-14; migración
  0070): si el objetivo tiene fecha, una tarea que vence después se rechaza, con el día hasta el
  que puede vencer. Antes era un aviso que no bloqueaba.
- **Lo que deja:** la tarea, su evento `asignada` (el estado sigue siendo la proyección) y una
  fila de auditoría en el espacio de la tarea con quién la cargó y quién la decidió (declarado
  por quien la carga, nunca una aprobación hecha en Leda), y las versiones del paquete y del
  núcleo.
- **Una sola vez por clave:** la misma clave con los mismos datos devuelve la misma tarea; con
  otros datos, se rechaza.
"""

from __future__ import annotations

import contextlib
import hashlib
import re
import secrets
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
import pytest

from leda.calendario import Calendario
from leda.db import admin, espacio

# Miércoles 14/10/2026 al mediodía en Buenos Aires.
AHORA = datetime(2026, 10, 14, 15, 0, tzinfo=timezone.utc)
HOY = date(2026, 10, 14)
VIERNES = date(2026, 10, 16)
SABADO = date(2026, 10, 17)
FERIADO = date(2026, 10, 19)
AYER = date(2026, 10, 13)

FUNCIONES_DE_LA_WEB = ("cargar_tarea", "opciones_de_la_carga")

BASE = "https://testserver"


# --- Ayudas ---------------------------------------------------------------------------------

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@contextlib.contextmanager
def sin_espacio(conn):
    """La web antes de saber de qué espacio es el pedido."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_app")
            yield cur


def _otorgar(conn, app_user_id: str) -> None:
    with admin(conn) as cur:
        cur.execute("insert into platform_role (app_user_id, rol) values (%s, 'administrador')",
                    (app_user_id,))
    conn.commit()


def _revocar(conn, app_user_id: str) -> None:
    with admin(conn) as cur:
        cur.execute("delete from platform_role where app_user_id = %s", (app_user_id,))
    conn.commit()


def _entrar(conn, app_user_id: str) -> str:
    """Abre una sesión de administración y devuelve su token en claro."""
    enlace, sesion = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with admin(conn) as cur:
        cur.execute("select emitir_enlace_de_administracion(%s, %s, null)",
                    (app_user_id, _hash(enlace)))
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_administracion(%s, %s) as id",
                    (_hash(enlace), _hash(sesion)))
        assert cur.fetchone()["id"]
    conn.commit()
    return sesion


@pytest.fixture
def administradora(conn, intake_world) -> str:
    """Morgan Hale, de North Lab: administradora de plataforma y autoridad final de su equipo."""
    quien = intake_world["north-lab"]["people"]["Morgan Hale"]["app_user_id"]
    _otorgar(conn, quien)
    return quien


@pytest.fixture
def sesion(conn, administradora) -> str:
    return _entrar(conn, administradora)


def _norte(mundo: dict) -> dict:
    return mundo["north-lab"]


def _persona(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _datos(mundo: dict, **cambios) -> dict:
    """Una carga válida en North Lab para Sam North (la revisa Taylor Quinn)."""
    datos = {
        "espacio": _norte(mundo)["id"],
        "objetivo": _norte(mundo)["objectives"][0],
        "titulo": "Instalar el switch de la planta",
        "descripcion": None,
        "responsable": _persona(mundo, "Sam North"),
        "fecha": VIERNES,
        "criterio": "El switch responde desde la sala de control",
        "evidencia": ["test record"],
        "decidio": _persona(mundo, "Morgan Hale"),
        "clave": secrets.token_urlsafe(18),
        "ahora": AHORA,
    }
    datos.update(cambios)
    return datos


def _llamar(cur, sesion: str, d: dict) -> dict:
    cur.execute(
        """select cargar_tarea(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) as r""",
        (_hash(sesion), d["espacio"], d["objetivo"], d["titulo"], d["descripcion"],
         d["responsable"], d["fecha"], d["criterio"], d["evidencia"], d["decidio"],
         d["clave"], d["ahora"]))
    return cur.fetchone()["r"]


def _cargar(conn, sesion: str, mundo: dict, **cambios) -> dict:
    with sin_espacio(conn) as cur:
        resultado = _llamar(cur, sesion, _datos(mundo, **cambios))
    conn.commit()
    return resultado


def _errores(resultado: dict) -> set[tuple[str, str]]:
    assert resultado["ok"] is False, resultado
    return {(e["campo"], e["motivo"]) for e in resultado["errores"]}


def _avisos(resultado: dict) -> set[tuple[str, str]]:
    assert resultado["ok"] is True, resultado
    return {(a["campo"], a["motivo"]) for a in resultado["avisos"]}


def _contar(conn, tabla: str, donde: str = "true", *args) -> int:
    with admin(conn) as cur:
        cur.execute(f"select count(*) n from {tabla} where {donde}", args)
        n = cur.fetchone()["n"]
    conn.commit()
    return n


def _fila(conn, consulta: str, *args) -> dict | None:
    with admin(conn) as cur:
        cur.execute(consulta, args)
        fila = cur.fetchone()
    conn.commit()
    return fila


def _nada_cargado(conn) -> None:
    assert _contar(conn, "task") == 0
    assert _contar(conn, "task_state_event") == 0
    assert _contar(conn, "carga_de_tarea") == 0
    assert _contar(conn, "audit_log", "accion = 'cargar_tarea'") == 0


# --- Las funciones ----------------------------------------------------------------------------

def test_las_funciones_son_elevadas_y_las_ejecuta_solo_la_web(conn):
    with admin(conn) as cur:
        cur.execute(
            """select p.proname, r.rolname, p.prosecdef, p.proconfig,
                      has_function_privilege('public', p.oid, 'execute') as de_public,
                      has_function_privilege('leda_app', p.oid, 'execute') as de_app,
                      has_function_privilege('leda_gateway', p.oid, 'execute') as de_gateway
                 from pg_proc p join pg_roles r on r.oid = p.proowner
                 join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'leda' and p.proname = any(%s)""",
            (list(FUNCIONES_DE_LA_WEB) + ["es_dia_habil"],))
        filas = {f["proname"]: f for f in cur.fetchall()}
    conn.commit()
    assert set(filas) == set(FUNCIONES_DE_LA_WEB) | {"es_dia_habil"}
    for nombre, f in filas.items():
        assert f["rolname"] == "leda_owner", nombre
        assert any(c.startswith("search_path=") and c.endswith("pg_temp")
                   for c in f["proconfig"] or []), nombre
        assert not f["de_public"] and not f["de_gateway"], nombre
    for nombre in FUNCIONES_DE_LA_WEB:
        assert filas[nombre]["prosecdef"] and filas[nombre]["de_app"], nombre
    # El día hábil corre con la RLS de quien llama: no es elevada ni la necesita la web.
    assert not filas["es_dia_habil"]["prosecdef"] and not filas["es_dia_habil"]["de_app"]


def test_la_aplicacion_no_escribe_tareas_ni_claves_directo(conn, intake_world):
    norte = _norte(intake_world)
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute(
                """insert into task (workspace_id, objective_id, titulo, area_id)
                   values (%s, %s, 'x', %s)""",
                (norte["id"], norte["objectives"][0], norte["areas"]["field"]))
        for orden in ("select * from carga_de_tarea", "delete from carga_de_tarea",
                      "insert into carga_de_tarea (workspace_id, clave, huella, task_id) "
                      "values (gen_random_uuid(), 'x', 'x', gen_random_uuid())"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(orden)
    conn.commit()


# --- El día hábil del espacio ---------------------------------------------------------------

def test_el_dia_habil_en_sql_es_el_del_calendario(conn, intake_world):
    norte, oeste = intake_world["north-lab"]["id"], intake_world["west-studio"]["id"]
    with admin(conn) as cur:
        cur.execute("insert into holiday (workspace_id, fecha, nombre) values (%s, %s, 'feriado')",
                    (norte, FERIADO))
        # Otro calendario, con un sábado y un feriado en martes.
        cur.execute("update work_calendar set dias = array['martes', 'sabado'] "
                    "where workspace_id = %s", (oeste,))
        cur.execute("insert into holiday (workspace_id, fecha) values (%s, %s)",
                    (oeste, date(2026, 10, 20)))
        for ws in (norte, oeste):
            calendario = Calendario.desde_base(cur, ws)
            for i in range(45):
                dia = date(2026, 10, 1) + timedelta(days=i)
                cur.execute("select es_dia_habil(%s, %s) as h", (ws, dia))
                assert cur.fetchone()["h"] is calendario.es_habil(dia), (ws, dia)
        cur.execute("select es_dia_habil(%s, %s) as h", (norte, FERIADO))
        assert cur.fetchone()["h"] is False
        cur.execute("select es_dia_habil(%s, %s) as h", (norte, SABADO))
        assert cur.fetchone()["h"] is False
        # Sin calendario no hay días hábiles: falla cerrado.
        cur.execute("select es_dia_habil(gen_random_uuid(), %s) as h", (VIERNES,))
        assert cur.fetchone()["h"] is False
    conn.commit()


# --- Una carga válida -------------------------------------------------------------------------

def test_una_carga_valida_deja_la_tarea_su_evento_y_su_auditoria(conn, intake_world, sesion,
                                                                 administradora):
    with admin(conn) as cur:
        cur.execute("select set_config('leda.nucleo_hash', 'nucleo-de-prueba', false)")
    conn.commit()
    norte = _norte(intake_world)
    r = _cargar(conn, sesion, intake_world, descripcion="Con el cable que llegó el lunes")
    assert r["ok"] is True and r["repetida"] is False and r["avisos"] == []
    tarea = _fila(conn, "select * from task where id = %s", r["task_id"])
    assert str(tarea["workspace_id"]) == norte["id"]
    assert str(tarea["area_id"]) == norte["areas"]["field"], "el área sale del responsable"
    assert str(tarea["responsable_membership_id"]) == _persona(intake_world, "Sam North")
    assert tarea["estado"] == "asignada"
    assert tarea["titulo"] == "Instalar el switch de la planta"
    assert tarea["descripcion"] == "Con el cable que llegó el lunes"
    assert tarea["evidencia_requerida"] == ["test record"]
    assert tarea["evidencia_policy_version"] == 1
    # La fecha elegida, al cierre de la jornada del espacio, en su zona.
    local = tarea["fecha_objetivo"].astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
    assert local.date() == VIERNES and local.time() == time(18, 0)

    eventos = _fila(conn, "select count(*) n, min(estado_nuevo::text) e, "
                          "min(actor_kind::text) k, min(actor_app_user_id::text) a "
                          "from task_state_event where task_id = %s", r["task_id"])
    assert (eventos["n"], eventos["e"], eventos["k"], eventos["a"]) == (
        1, "asignada", "persona", administradora)

    auditoria = _fila(conn, "select * from audit_log where accion = 'cargar_tarea'")
    assert str(auditoria["workspace_id"]) == norte["id"]
    assert str(auditoria["sujeto_id"]) == r["task_id"] and auditoria["sujeto_tipo"] == "task"
    assert str(auditoria["actor_app_user_id"]) == administradora
    assert auditoria["pack_hash"] == "hash-0"
    assert auditoria["nucleo_hash"] == "nucleo-de-prueba"
    detalle = auditoria["detalle"]
    assert detalle["cargada_por_app_user_id"] == administradora
    assert detalle["decidida_por_membership_id"] == _persona(intake_world, "Morgan Hale")
    assert detalle["decision_declarada_al_cargar"] is True
    assert detalle["origen"] == "web"
    assert sesion not in str(detalle) and _hash(sesion) not in str(detalle)
    assert _contar(conn, "audit_log", "accion = 'cargar_tarea'") == 1


def test_la_tarea_cargada_aparece_en_tus_tareas_de_su_responsable(conn, intake_world, sesion):
    r = _cargar(conn, sesion, intake_world)
    norte = _norte(intake_world)
    enlace, equipo = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with espacio(conn, norte["id"]) as cur:
        cur.execute("select emitir_enlace_de_entrada(%s, %s, null)",
                    (_persona(intake_world, "Sam North"), _hash(enlace)))
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s)", (_hash(enlace), _hash(equipo)))
        cur.execute("select * from tareas_de_la_sesion(%s, 'tus', %s)", (_hash(equipo), AHORA))
        filas = cur.fetchall()
    conn.commit()
    assert [(str(f["task_id"]), f["papel"], f["estado"]) for f in filas] == [
        (r["task_id"], "mia", "asignada")]


def test_hoy_vale_si_es_un_dia_habil(conn, intake_world, sesion):
    assert _cargar(conn, sesion, intake_world, fecha=HOY)["ok"] is True


def test_hoy_ya_no_vale_cuando_cerro_la_jornada_del_espacio(conn, intake_world, sesion):
    """Revisión RDD `review-40c4b218bf40f1fa` (migración 0064): la tarea vence al cierre de la
    jornada (18:00 en North Lab); cargarla para hoy después de esa hora la dejaría vencida al
    nacer."""
    al_cierre = datetime(2026, 10, 14, 18, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    assert _errores(_cargar(conn, sesion, intake_world, fecha=HOY, ahora=al_cierre)) == {
        ("fecha", "ya_cerro_el_dia")}
    _nada_cargado(conn)
    assert _cargar(conn, sesion, intake_world, fecha=VIERNES, ahora=al_cierre)["ok"] is True
    antes = al_cierre - timedelta(minutes=1)
    assert _cargar(conn, sesion, intake_world, fecha=HOY, ahora=antes)["ok"] is True


def test_las_opciones_no_ofrecen_hoy_cuando_cerro_la_jornada(conn, intake_world, sesion):
    norte = _norte(intake_world)
    al_cierre = datetime(2026, 10, 14, 18, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    habiles = _opciones(conn, sesion, norte["id"], al_cierre)["calendario"]["dias_habiles"]
    assert habiles[0] == (HOY + timedelta(days=1)).isoformat()
    antes = _opciones(conn, sesion, norte["id"], al_cierre - timedelta(minutes=1))
    assert antes["calendario"]["dias_habiles"][0] == HOY.isoformat()


# --- Lo que no se carga ---------------------------------------------------------------------

def test_sin_los_datos_obligatorios_se_rechaza_todo_junto(conn, intake_world, sesion):
    r = _cargar(conn, sesion, intake_world, objetivo=None, titulo="  ", responsable=None,
                fecha=None, criterio="", evidencia=None, decidio=None, clave=None)
    assert _errores(r) == {("objetivo", "falta"), ("titulo", "falta"), ("responsable", "falta"),
                           ("fecha", "falta"), ("criterio", "falta"), ("evidencia", "falta"),
                           ("decidio", "falta"), ("clave", "falta")}
    _nada_cargado(conn)


def test_sin_evidencia_pedida_no_se_carga_salvo_que_el_area_no_pida(conn, intake_world, sesion):
    assert _errores(_cargar(conn, sesion, intake_world, evidencia=[])) == {
        ("evidencia", "falta")}
    # Una política vacía es la decisión explícita de no pedir evidencia (`task_evidence_policy`).
    with admin(conn) as cur:
        cur.execute("""update task_evidence_policy set evidencia_requerida = '{}', version = 2
                        where area_id = %s""", (_norte(intake_world)["areas"]["quality"],))
    conn.commit()
    r = _cargar(conn, sesion, intake_world, responsable=_persona(intake_world, "Sam Noble"),
                evidencia=[])
    assert r["ok"] is True
    assert _fila(conn, "select evidencia_policy_version v from task where id = %s",
                 r["task_id"])["v"] == 2


def test_un_tipo_de_evidencia_que_la_politica_no_conoce_no_se_carga(conn, intake_world, sesion):
    """Un tipo que la política del área no conoce no lo cubriría ninguna pieza: la tarea no se
    podría cerrar nunca."""
    r = _cargar(conn, sesion, intake_world, evidencia=["test record", "una foto del tablero"])
    assert _errores(r) == {("evidencia", "tipo_no_es_de_la_politica")}
    with admin(conn) as cur:
        cur.execute("""update task_evidence_policy
                          set tipos = '{"captura": {"clases": ["imagen"],
                                                     "en_palabras": "una captura"}}'
                        where area_id = %s""", (_norte(intake_world)["areas"]["field"],))
    conn.commit()
    assert _cargar(conn, sesion, intake_world, evidencia=["captura"])["ok"] is True


def test_un_area_sin_politica_de_evidencia_no_carga(conn, intake_world, sesion):
    with admin(conn) as cur:
        cur.execute("delete from task_evidence_policy where area_id = %s",
                    (_norte(intake_world)["areas"]["field"],))
    conn.commit()
    assert _errores(_cargar(conn, sesion, intake_world)) == {
        ("evidencia", "sin_politica_del_area")}


def test_textos_demasiado_largos_no_se_cargan(conn, intake_world, sesion):
    r = _cargar(conn, sesion, intake_world, titulo="x" * 201, descripcion="y" * 801,
                criterio="z" * 501)
    assert _errores(r) == {("titulo", "demasiado_largo"), ("descripcion", "demasiado_largo"),
                           ("criterio", "demasiado_largo")}
    _nada_cargado(conn)


def test_el_objetivo_tiene_que_ser_del_espacio_y_estar_abierto(conn, intake_world, sesion):
    ajeno = intake_world["west-studio"]["objectives"][0]
    assert _errores(_cargar(conn, sesion, intake_world, objetivo=ajeno)) == {
        ("objetivo", "no_existe")}
    with admin(conn) as cur:
        cur.execute("""insert into objective (workspace_id, tipo, titulo, estado)
                       values (%s, 'operativo', 'Suspendido', 'suspendido') returning id""",
                    (_norte(intake_world)["id"],))
        suspendido = str(cur.fetchone()["id"])
    conn.commit()
    assert _errores(_cargar(conn, sesion, intake_world, objetivo=suspendido)) == {
        ("objetivo", "no_esta_abierto")}
    _nada_cargado(conn)


def test_la_fecha_tiene_que_ser_un_dia_habil_y_no_pasado(conn, intake_world, sesion):
    with admin(conn) as cur:
        cur.execute("insert into holiday (workspace_id, fecha) values (%s, %s)",
                    (_norte(intake_world)["id"], FERIADO))
    conn.commit()
    for dia, motivo in ((SABADO, "no_es_dia_habil"), (FERIADO, "no_es_dia_habil"),
                        (AYER, "en_el_pasado")):
        assert _errores(_cargar(conn, sesion, intake_world, fecha=dia)) == {("fecha", motivo)}
    _nada_cargado(conn)


def test_el_responsable_tiene_que_ser_integrante_activo_del_espacio(conn, intake_world, sesion):
    de_otro = _persona(intake_world, "Sam North", "west-studio")
    assert _errores(_cargar(conn, sesion, intake_world, responsable=de_otro)) == {
        ("responsable", "no_es_integrante_activo")}
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam North"),))
    conn.commit()
    assert _errores(_cargar(conn, sesion, intake_world)) == {
        ("responsable", "no_es_integrante_activo")}
    _nada_cargado(conn)


def test_quien_la_hace_no_puede_ser_quien_la_revisa(conn, intake_world, sesion):
    """Morgan es la autoridad final y nadie aprueba su trabajo: se revisaría a sí misma."""
    r = _cargar(conn, sesion, intake_world, responsable=_persona(intake_world, "Morgan Hale"))
    assert _errores(r) == {("responsable", "la_hace_y_la_revisa")}
    _nada_cargado(conn)


def test_sin_nadie_activo_que_la_revise_no_se_carga(conn, intake_world, sesion):
    with admin(conn) as cur:
        # Taylor deja el equipo: nadie revisa el trabajo de Sam North ni de Sam Noble.
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Taylor Quinn"),))
    conn.commit()
    assert _errores(_cargar(conn, sesion, intake_world)) == {
        ("responsable", "sin_quien_la_revise")}
    with admin(conn) as cur:
        cur.execute("update membership set activo = true where id = %s",
                    (_persona(intake_world, "Taylor Quinn"),))
        cur.execute("update membership set aprobador_membership_id = null where id = %s",
                    (_persona(intake_world, "Taylor Quinn"),))
    conn.commit()
    r = _cargar(conn, sesion, intake_world, responsable=_persona(intake_world, "Taylor Quinn"))
    assert _errores(r) == {("responsable", "sin_quien_la_revise")}
    _nada_cargado(conn)


def test_quien_la_decidio_tiene_que_ser_integrante_activo_del_espacio(conn, intake_world,
                                                                      sesion):
    de_otro = _persona(intake_world, "Morgan Hale", "west-studio")
    assert _errores(_cargar(conn, sesion, intake_world, decidio=de_otro)) == {
        ("decidio", "no_es_integrante_activo")}
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(intake_world, "Sam Noble"),))
    conn.commit()
    r = _cargar(conn, sesion, intake_world, decidio=_persona(intake_world, "Sam Noble"))
    assert _errores(r) == {("decidio", "no_es_integrante_activo")}
    _nada_cargado(conn)


def test_un_espacio_que_no_existe_no_carga(conn, intake_world, sesion):
    r = _cargar(conn, sesion, intake_world, espacio="00000000-0000-0000-0000-000000000000")
    assert _errores(r) == {("espacio", "no_existe")}
    _nada_cargado(conn)


# --- Una tarea no vence después que su objetivo (decisión 6; migración 0070) ------------------

def _fecha_del_objetivo(conn, objetivo: str, fecha: date | None) -> None:
    with admin(conn) as cur:
        cur.execute("update objective set fecha_objetivo = %s where id = %s", (fecha, objetivo))
    conn.commit()


def test_una_tarea_que_vence_despues_que_su_objetivo_no_se_carga(conn, intake_world, sesion):
    """Decisión 6 del usuario (2026-10-14): "leda tiene que frenar esas cosas". El objetivo se
    demoraría; la base lo rechaza y dice hasta qué día puede vencer."""
    norte = _norte(intake_world)
    _fecha_del_objetivo(conn, norte["objectives"][0], date(2026, 10, 15))
    r = _cargar(conn, sesion, intake_world, fecha=VIERNES)
    assert _errores(r) == {("fecha", "vence_despues_del_objetivo")}
    (error,) = r["errores"]
    assert error["hasta"] == "2026-10-15"
    _nada_cargado(conn)


def test_una_tarea_que_vence_el_dia_de_su_objetivo_se_carga(conn, intake_world, sesion):
    norte = _norte(intake_world)
    _fecha_del_objetivo(conn, norte["objectives"][0], VIERNES)
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (norte["people"]["Sam North"]["app_user_id"],))
    conn.commit()
    # El mismo día que el objetivo vale, y alguien sin Leda conectada se sigue avisando.
    r = _cargar(conn, sesion, intake_world, fecha=VIERNES)
    assert _avisos(r) == {("responsable", "sin_conectar")}
    r = _cargar(conn, sesion, intake_world, fecha=HOY,
                responsable=_persona(intake_world, "Sam Noble"))
    assert _avisos(r) == set()
    assert _contar(conn, "task") == 2


def test_un_objetivo_sin_fecha_no_pone_limite(conn, intake_world, sesion):
    """Los objetivos iniciales del pack no tienen fecha: no limitan a sus tareas."""
    norte = _norte(intake_world)
    _fecha_del_objetivo(conn, norte["objectives"][0], None)
    assert _cargar(conn, sesion, intake_world, fecha=date(2027, 3, 16))["ok"] is True


# --- Una sola vez por clave -----------------------------------------------------------------

def test_la_misma_clave_con_los_mismos_datos_devuelve_la_misma_tarea(conn, intake_world, sesion):
    datos = _datos(intake_world)
    with sin_espacio(conn) as cur:
        primera = _llamar(cur, sesion, datos)
    conn.commit()
    with sin_espacio(conn) as cur:
        segunda = _llamar(cur, sesion, datos)
    conn.commit()
    assert primera["ok"] and segunda["ok"]
    assert segunda["task_id"] == primera["task_id"]
    assert (primera["repetida"], segunda["repetida"]) == (False, True)
    assert _contar(conn, "task") == 1
    assert _contar(conn, "task_state_event") == 1
    assert _contar(conn, "audit_log", "accion = 'cargar_tarea'") == 1


def test_la_misma_clave_con_otros_datos_se_rechaza(conn, intake_world, sesion):
    clave = secrets.token_urlsafe(18)
    assert _cargar(conn, sesion, intake_world, clave=clave)["ok"] is True
    r = _cargar(conn, sesion, intake_world, clave=clave, titulo="Otra cosa")
    assert _errores(r) == {("clave", "usada_con_otros_datos")}
    assert _contar(conn, "task") == 1
    assert _errores(_cargar(conn, sesion, intake_world, clave="corta")) == {
        ("clave", "mal_formada")}


def test_la_misma_clave_en_otro_espacio_es_otra_carga(conn, intake_world, sesion):
    clave = secrets.token_urlsafe(18)
    assert _cargar(conn, sesion, intake_world, clave=clave)["ok"] is True
    oeste = intake_world["west-studio"]
    r = _cargar(conn, sesion, intake_world, clave=clave, espacio=oeste["id"],
                objetivo=oeste["objectives"][0],
                responsable=_persona(intake_world, "Sam North", "west-studio"),
                decidio=_persona(intake_world, "Morgan Hale", "west-studio"))
    assert r["ok"] is True and r["repetida"] is False
    assert _contar(conn, "task") == 2


# --- La sesión y el aislamiento ------------------------------------------------------------

def test_sin_una_sesion_de_administracion_vigente_no_carga(conn, intake_world, administradora):
    assert _errores(_cargar(conn, secrets.token_urlsafe(32), intake_world)) == {
        ("sesion", "sin_sesion")}
    # La sesión del equipo de Morgan (autoridad final de North Lab) no carga tareas.
    enlace, equipo = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with espacio(conn, _norte(intake_world)["id"]) as cur:
        cur.execute("select emitir_enlace_de_entrada(%s, %s, null)",
                    (_persona(intake_world, "Morgan Hale"), _hash(enlace)))
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s)", (_hash(enlace), _hash(equipo)))
    conn.commit()
    assert _errores(_cargar(conn, equipo, intake_world)) == {("sesion", "sin_sesion")}
    # Con el rol revocado, la sesión de administración se corta en la llamada.
    sesion = _entrar(conn, administradora)
    _revocar(conn, administradora)
    assert _errores(_cargar(conn, sesion, intake_world)) == {("sesion", "sin_sesion")}
    _nada_cargado(conn)


def test_la_tarea_y_su_auditoria_van_al_espacio_elegido_aunque_haya_otro_fijado(
        conn, intake_world, sesion):
    norte, oeste = _norte(intake_world), intake_world["west-studio"]
    with espacio(conn, oeste["id"]) as cur:
        r = _llamar(cur, sesion, _datos(intake_world))
        cur.execute("select current_setting('leda.workspace_id', true) ws")
        assert cur.fetchone()["ws"] == oeste["id"], "la función no devolvió el espacio previo"
    conn.commit()
    assert r["ok"] is True
    assert str(_fila(conn, "select workspace_id w from task where id = %s",
                     r["task_id"])["w"]) == norte["id"]
    assert str(_fila(conn, "select workspace_id w from audit_log where accion = 'cargar_tarea'"
                     )["w"]) == norte["id"]
    assert str(_fila(conn, "select workspace_id w from carga_de_tarea")["w"]) == norte["id"]


def test_ningun_dato_de_otro_espacio_entra_en_una_carga(conn, intake_world, sesion):
    oeste = intake_world["west-studio"]
    r = _cargar(conn, sesion, intake_world, objetivo=oeste["objectives"][0],
                responsable=_persona(intake_world, "Sam North", "west-studio"),
                decidio=_persona(intake_world, "Morgan Hale", "west-studio"))
    assert _errores(r) == {("objetivo", "no_existe"), ("responsable", "no_es_integrante_activo"),
                           ("decidio", "no_es_integrante_activo")}
    _nada_cargado(conn)


# --- Las opciones del formulario ------------------------------------------------------------

def _opciones(conn, sesion: str, espacio_id: str, ahora: datetime = AHORA) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select opciones_de_la_carga(%s, %s, %s) as r",
                    (_hash(sesion), espacio_id, ahora))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def test_las_opciones_dicen_lo_que_el_formulario_necesita(conn, intake_world, sesion):
    norte = _norte(intake_world)
    with admin(conn) as cur:
        cur.execute("insert into holiday (workspace_id, fecha, nombre) values (%s, %s, 'Feriado')",
                    (norte["id"], FERIADO))
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (norte["people"]["Sam Noble"]["app_user_id"],))
        cur.execute("""insert into objective (workspace_id, tipo, titulo, estado)
                       values (%s, 'hito', 'Cerrado', 'terminado')""", (norte["id"],))
    conn.commit()
    r = _opciones(conn, sesion, norte["id"])
    assert r["ok"] is True
    assert r["hoy"] == HOY.isoformat()
    assert {o["id"] for o in r["objetivos"]} == set(norte["objectives"])
    personas = {p["nombre"]: p for p in r["integrantes"]}
    assert set(personas) == {"Morgan Hale 1", "Taylor Quinn 1", "Sam North 1", "Sam Noble 1"}
    assert personas["Sam North 1"]["revisa"]["nombre"] == "Taylor Quinn 1"
    assert personas["Sam North 1"]["area_id"] == norte["areas"]["field"]
    assert personas["Morgan Hale 1"]["revisa"] is None
    assert personas["Sam Noble 1"]["conectado"] is False
    assert personas["Sam North 1"]["conectado"] is True
    politicas = {p["area_id"]: p for p in r["politicas"]}
    assert politicas[norte["areas"]["field"]]["evidencia_requerida"] == ["test record"]
    assert politicas[norte["areas"]["field"]]["version"] == 1
    habiles = r["calendario"]["dias_habiles"]
    assert habiles[0] == HOY.isoformat() and VIERNES.isoformat() in habiles
    assert SABADO.isoformat() not in habiles and FERIADO.isoformat() not in habiles
    assert date.fromisoformat(habiles[-1]) >= HOY + timedelta(days=170)
    assert {"fecha": FERIADO.isoformat(), "nombre": "Feriado"} in r["calendario"]["feriados"]
    # Nada de otro espacio.
    texto = str(r)
    for nombre in ("Morgan Hale 2", "Sam North 2"):
        assert nombre not in texto
    for objetivo in intake_world["west-studio"]["objectives"]:
        assert objetivo not in texto


def test_las_opciones_piden_una_sesion_y_un_espacio_que_exista(conn, intake_world,
                                                               administradora):
    assert _errores(_opciones(conn, secrets.token_urlsafe(32), _norte(intake_world)["id"])) == {
        ("sesion", "sin_sesion")}
    sesion = _entrar(conn, administradora)
    assert _errores(_opciones(conn, sesion, "00000000-0000-0000-0000-000000000000")) == {
        ("espacio", "no_existe")}


# --- La vuelta atrás ------------------------------------------------------------------------

def test_el_rollback_de_la_0062_se_niega_si_hay_cargas(conn, intake_world, sesion):
    rollbacks = Path(__file__).resolve().parents[2] / "db" / "rollbacks"
    (archivo,) = rollbacks.glob("0062_*.sql")
    guarda = re.findall(r"do \$\$.*?end \$\$;", archivo.read_text("utf-8"), re.S)[-1]
    assert _cargar(conn, sesion, intake_world)["ok"] is True
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0062 rollback refused"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
    conn.commit()
    assert _contar(conn, "carga_de_tarea") == 1


# --- La entrada HTTP ------------------------------------------------------------------------

@pytest.fixture
def web(conn, monkeypatch):
    """Un navegador nuevo por llamada, con la conexión de la prueba. El juicio del criterio al
    cargar (J2-9) usa una IA de mentira que lo da por comprobable: nunca la real (las pruebas
    del juicio, en `test_criterio_verificable.py`, ponen la suya)."""
    from fastapi.testclient import TestClient

    from leda import entrada, web_app
    from tests.test_ayuda_al_cargar import IAQueCopiaElCriterio

    monkeypatch.setattr(web_app, "_conn_de_la_web", lambda: conn)
    monkeypatch.setattr(web_app, "_ia_del_criterio",
                        lambda conn, espacio: IAQueCopiaElCriterio())

    def nuevo():
        return TestClient(entrada.app, base_url=BASE, follow_redirects=False)
    return nuevo


def _navegador_de_administracion(web, conn, app_user_id: str):
    from leda import web_app

    with admin(conn) as cur:
        token = web_app.emitir_enlace_de_administracion(cur, app_user_id)
    conn.commit()
    navegador = web()
    assert navegador.post(f"/app/admin/entrar/{token}").status_code == 303
    return navegador


def _navegador_del_equipo(web, conn, mundo: dict, nombre: str):
    from leda import web_app

    with espacio(conn, mundo["north-lab"]["id"]) as cur:
        token = web_app.emitir_enlace(cur, _persona(mundo, nombre))
    conn.commit()
    navegador = web()
    assert navegador.post(f"/app/entrar/{token}").status_code == 303
    return navegador


def _proximo_habil_real(dias: int = 7) -> date:
    """Un día hábil de North Lab (de lunes a viernes, sin feriados) más adelante que hoy: la web
    mira el reloj de verdad."""
    dia = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date() + timedelta(days=dias)
    while dia.weekday() >= 5:
        dia += timedelta(days=1)
    return dia


def _cuerpo(mundo: dict, **cambios) -> dict:
    norte = _norte(mundo)
    cuerpo = {
        "objetivo_id": norte["objectives"][0],
        "titulo": "Instalar el switch de la planta",
        "responsable_id": _persona(mundo, "Sam North"),
        "fecha": _proximo_habil_real().isoformat(),
        "criterio": "El switch responde desde la sala de control",
        "evidencia": ["test record"],
        "decidio_id": _persona(mundo, "Morgan Hale"),
        "clave": secrets.token_urlsafe(18),
    }
    cuerpo.update(cambios)
    return cuerpo


def test_las_opciones_por_la_api_piden_la_cookie_de_administracion(web, conn, intake_world,
                                                                   administradora):
    norte = _norte(intake_world)
    camino = f"/app/admin/api/espacios/{norte['id']}/opciones"
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.get(camino)
    assert r.status_code == 200, r.text
    assert r.headers["cache-control"] == "no-store"
    datos = r.json()
    assert {o["id"] for o in datos["objetivos"]} == set(norte["objectives"])
    assert "ok" not in datos
    assert web().get(camino).status_code == 401
    assert _navegador_del_equipo(web, conn, intake_world, "Morgan Hale").get(
        camino).status_code == 401
    assert navegador.get("/app/admin/api/espacios/no-es-un-id/opciones").status_code == 404
    assert navegador.get(
        "/app/admin/api/espacios/00000000-0000-0000-0000-000000000000/opciones"
    ).status_code == 404


def test_cargar_por_la_api_crea_la_tarea_una_sola_vez(web, conn, intake_world, administradora):
    norte = _norte(intake_world)
    camino = f"/app/admin/api/espacios/{norte['id']}/tareas"
    navegador = _navegador_de_administracion(web, conn, administradora)
    cuerpo = _cuerpo(intake_world)
    r = navegador.post(camino, json=cuerpo)
    assert r.status_code == 201, r.text
    assert r.headers["cache-control"] == "no-store"
    task_id = r.json()["task_id"]
    assert r.json()["avisos"] == [] and r.json()["repetida"] is False
    otra = navegador.post(camino, json=cuerpo)
    assert otra.status_code == 200 and otra.json()["task_id"] == task_id
    assert otra.json()["repetida"] is True
    assert _contar(conn, "task") == 1


def test_cargar_por_la_api_devuelve_todo_lo_que_falta_y_los_avisos(web, conn, intake_world,
                                                                   administradora):
    norte = _norte(intake_world)
    camino = f"/app/admin/api/espacios/{norte['id']}/tareas"
    navegador = _navegador_de_administracion(web, conn, administradora)
    r = navegador.post(camino, json=_cuerpo(intake_world, objetivo_id="no-es-un-id",
                                            fecha="31/12/2026", criterio="",
                                            evidencia="test record"))
    assert r.status_code == 422, r.text
    errores = {(e["campo"], e["motivo"]) for e in r.json()["errores"]}
    assert errores == {("objetivo", "mal_formado"), ("fecha", "mal_formada"),
                       ("criterio", "falta"), ("evidencia", "mal_formada")}
    for error in r.json()["errores"]:
        assert error["texto"]
        for de_la_cocina in ("traceback", "psycopg", "cargar_tarea", "sql"):
            assert de_la_cocina not in error["texto"].lower()
    assert _contar(conn, "task") == 0
    with admin(conn) as cur:
        cur.execute("update app_user set telegram_user_id = null where id = %s",
                    (norte["people"]["Sam North"]["app_user_id"],))
    conn.commit()
    r = navegador.post(camino, json=_cuerpo(intake_world))
    assert r.status_code == 201
    (aviso,) = r.json()["avisos"]
    assert (aviso["campo"], aviso["motivo"]) == ("responsable", "sin_conectar")
    assert "no va a recibir avisos ni seguimiento" in aviso["texto"]


TEXTO_VENCE_DESPUES_DEL_OBJETIVO = (
    "Esta tarea vence después que su objetivo: el objetivo se demoraría. Para cargarla ahora, "
    "elegí una fecha hasta la del objetivo.")


def test_cargar_y_revisar_por_la_api_rechazan_una_tarea_que_vence_despues_que_su_objetivo(
        web, conn, intake_world, administradora):
    """Decisión 6: la carga y la revisión previa (J2-21) rechazan igual, con palabras y con el
    día del objetivo, para que la web diga hasta cuándo puede vencer."""
    norte = _norte(intake_world)
    objetivo_hasta = _proximo_habil_real()
    _fecha_del_objetivo(conn, norte["objectives"][0], objetivo_hasta)
    camino = f"/app/admin/api/espacios/{norte['id']}/tareas"
    navegador = _navegador_de_administracion(web, conn, administradora)
    tarde = _proximo_habil_real(14).isoformat()
    for ruta in (camino, f"{camino}/revisar"):
        r = navegador.post(ruta, json=_cuerpo(intake_world, fecha=tarde))
        assert r.status_code == 422, (ruta, r.text)
        (error,) = r.json()["errores"]
        assert error == {"campo": "fecha", "motivo": "vence_despues_del_objetivo",
                         "texto": TEXTO_VENCE_DESPUES_DEL_OBJETIVO,
                         "hasta": objetivo_hasta.isoformat()}, ruta
    assert _contar(conn, "task") == 0
    # Ese mismo día, sí.
    r = navegador.post(camino, json=_cuerpo(intake_world, fecha=objetivo_hasta.isoformat()))
    assert r.status_code == 201, r.text


def test_un_cuerpo_anidado_hasta_el_fondo_es_un_pedido_mal_formado_y_no_un_error(
        web, conn, intake_world, administradora):
    """Revisión RDD `review-40c4b218bf40f1fa`: `json.loads` de un cuerpo muy anidado (por debajo
    del tope de tamaño) no tira `ValueError` sino `RecursionError`; antes daba 500."""
    norte = _norte(intake_world)
    camino = f"/app/admin/api/espacios/{norte['id']}/tareas"
    navegador = _navegador_de_administracion(web, conn, administradora)
    for cuerpo in ("[" * 30000 + "]" * 30000, '{"a":' * 5000 + "1" + "}" * 5000):
        assert len(cuerpo.encode()) < 64 * 1024
        r = navegador.post(camino, content=cuerpo, headers={"content-type": "application/json"})
        assert r.status_code == 422, r.text
        assert ("clave", "falta") in {(e["campo"], e["motivo"]) for e in r.json()["errores"]}
    assert _contar(conn, "task") == 0


def test_cargar_por_la_api_se_protege_de_otros_sitios_y_de_la_cookie_del_equipo(
        web, conn, intake_world, administradora):
    norte = _norte(intake_world)
    camino = f"/app/admin/api/espacios/{norte['id']}/tareas"
    navegador = _navegador_de_administracion(web, conn, administradora)
    for origen in ("https://otro.example", "null"):
        r = navegador.post(camino, json=_cuerpo(intake_world), headers={"origin": origen})
        assert r.status_code == 403
    r = navegador.post(camino, content="titulo=x", headers={
        "content-type": "application/x-www-form-urlencoded"})
    assert r.status_code == 415
    assert web().post(camino, json=_cuerpo(intake_world)).status_code == 401
    equipo = _navegador_del_equipo(web, conn, intake_world, "Morgan Hale")
    assert equipo.post(camino, json=_cuerpo(intake_world)).status_code == 401
    token = equipo.cookies.get("leda_sesion")
    impostor = web()
    impostor.cookies.set("leda_admin", token, domain="testserver", path="/app/admin")
    assert impostor.post(camino, json=_cuerpo(intake_world)).status_code == 401
    _revocar(conn, administradora)
    assert navegador.post(camino, json=_cuerpo(intake_world)).status_code == 401
    assert _contar(conn, "task") == 0
    assert navegador.post("/app/admin/api/espacios/no-es-un-id/tareas",
                          json=_cuerpo(intake_world)).status_code in (401, 404)
