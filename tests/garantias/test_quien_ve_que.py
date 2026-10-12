"""Quién ve qué en las listas de la puerta del equipo (ADR 0022, decisiones 3, 5, 11 y 13;
migración 0058): la capa de garantías.

Lo que se prueba acá es la regla en la base, no la API ni la web:

- **Una sola regla** (decisión 13): la lista de cada vista extiende `puede_ver_tarea` de una
  tarea a la lista, en SQL (`tareas_que_ve`). La web la lee con la sesión
  (`tareas_de_la_sesion`, `vistas_de_la_sesion`): la persona sale del hash del token de la
  sesión, que revalida `sesion_vigente` (0057), nunca de un dato del pedido (decisión 11).
- **Integrante, "Tus tareas"** (decisión 3): las suyas, las que espera de otros y las que otros
  esperan de él; no ve los atrasos ni los bloqueos de los demás (constitución §8: los atrasos se
  tratan primero en privado). Una tarea de otra área que no lo toca no aparece.
- **Referente, "Tu sector":** todas las tareas de su área, con fechas, atrasos y bloqueos; las de
  otra área, no.
- **Autoridad final, "El equipo":** todo su espacio y nada de otro, sin rankings ni cuentas por
  persona (constitución §15, principio 14).
- **Qué vistas tiene cada persona:** integrante, "tus"; referente, además "sector"; autoridad
  final, además "equipo".
"""

from __future__ import annotations

import contextlib
import hashlib
import secrets
from datetime import datetime, timezone

import psycopg
import pytest

from leda.db import admin, espacio

AHORA = datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc)   # jueves
ANTES = datetime(2026, 10, 19, 20, 0, tzinfo=timezone.utc)   # lunes: ya venció
DESPUES = datetime(2026, 10, 30, 20, 0, tzinfo=timezone.utc)  # viernes de la otra semana

DE_LA_SESION = ("tareas_de_la_sesion", "vistas_de_la_sesion")
INTERNAS = ("tareas_que_ve", "vistas_de")
COLUMNAS = {"task_id", "titulo", "estado", "fecha_objetivo", "asignada_en", "responsable",
            "area", "papel", "vencida", "bloqueo_abierto", "ve_la_pagina"}


# --- Ayudas ---------------------------------------------------------------------------------

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@contextlib.contextmanager
def sin_espacio(conn):
    """La aplicación antes de saber de qué espacio es el pedido (cada pedido de la web)."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role leda_app")
            yield cur


def _persona(mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _entrar(conn, mundo: dict, nombre: str, slug: str = "north-lab") -> str:
    """Emite el enlace de una persona, lo canjea y devuelve el token de su sesión."""
    enlace, sesion = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with espacio(conn, mundo[slug]["id"]) as cur:
        cur.execute("select emitir_enlace_de_entrada(%s, %s, null) as id",
                    (_persona(mundo, nombre, slug), _hash(enlace)))
        assert cur.fetchone()["id"]
    conn.commit()
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (_hash(enlace), _hash(sesion)))
        assert cur.fetchone()["id"]
    conn.commit()
    return sesion


def _lista(conn, sesion: str, vista: str) -> dict[str, dict]:
    """Lo que ve la sesión en una vista, por título."""
    with sin_espacio(conn) as cur:
        cur.execute("select * from tareas_de_la_sesion(%s, %s, %s)",
                    (_hash(sesion), vista, AHORA))
        filas = cur.fetchall()
    conn.commit()
    por_titulo = {f["titulo"]: f for f in filas}
    assert len(por_titulo) == len(filas), "una tarea aparece dos veces"
    return por_titulo


def _vistas(conn, sesion: str) -> list[str] | None:
    with sin_espacio(conn) as cur:
        cur.execute("select * from vistas_de_la_sesion(%s)", (_hash(sesion),))
        fila = cur.fetchone()
    conn.commit()
    return None if fila is None else list(fila["vistas"])


def _tarea(cur, mundo: dict, titulo: str, persona: str, area: str, estado: str,
           vence: datetime | None) -> str:
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, %s, %s, %s, %s, 'Que ande', '{}') returning id""",
        (mundo["id"], mundo["objectives"][0], titulo, mundo["areas"][area],
         mundo["people"][persona]["membership_id"], vence))
    tarea = str(cur.fetchone()["id"])
    cur.execute("""insert into task_state_event (task_id, estado_nuevo, actor_kind, at)
                   values (%s, 'asignada', 'leda', %s)""",
                (tarea, datetime(2026, 10, 12, 13, 0, tzinfo=timezone.utc)))
    if estado != "asignada":
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'asignada', %s, 'persona')""", (tarea, estado))
    return tarea


def _bloqueo(cur, mundo: dict, tarea: str, de: str, destraba: str) -> tuple[str, str]:
    """Un bloqueo abierto de `de` sobre `tarea`, que destraba `destraba`: el bloqueo y la fila
    de quién lo destraba."""
    ws = mundo["id"]
    cur.execute("""insert into blocker (workspace_id, task_id, causa, abierto_por)
                   values (%s, %s, 'falta una pieza', %s) returning id""",
                (ws, tarea, mundo["people"][de]["membership_id"]))
    bloqueo = str(cur.fetchone()["id"])
    cur.execute("""insert into blocker_unblocker (workspace_id, blocker_id,
                                                  destraba_membership_id,
                                                  dicho_por_membership_id, at)
                   values (%s, %s, %s, %s, %s) returning id""",
                (ws, bloqueo, mundo["people"][destraba]["membership_id"],
                 mundo["people"][de]["membership_id"], ANTES))
    return bloqueo, str(cur.fetchone()["id"])


@pytest.fixture
def mundo(conn, intake_world) -> dict:
    """North Lab. Morgan Hale es la autoridad final; Taylor Quinn, el referente del área field;
    Sam North (field) y Sam Noble (quality), integrantes.

    - "Pintar el galpón" (Sam North): en curso, vencida.
    - "Medir el ruido" (Sam North): trabada; la destraba Sam Noble.
    - "Montar la línea" (Sam North): asignada; espera "Calibrar la balanza" (dependencia).
    - "Calibrar la balanza" (Sam Noble, quality): en curso, vencida.
    - "Auditar proveedores" (Sam Noble, quality): asignada, vencida; no toca a Sam North.
    - "Ordenar el depósito" (Taylor Quinn, field): asignada.
    - "Lo de antes" (Sam North): cancelada.

    West Studio: "Secreto del oeste" (Sam Noble) y "Galpón del oeste" (Sam North)."""
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    t = {}
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (norte["people"]["Taylor Quinn"]["membership_id"], norte["areas"]["field"]))
        t["pintar"] = _tarea(cur, norte, "Pintar el galpón", "Sam North", "field",
                             "en_curso", ANTES)
        t["medir"] = _tarea(cur, norte, "Medir el ruido", "Sam North", "field",
                            "asignada", DESPUES)
        t["bloqueo_medir"], t["destraba_medir"] = _bloqueo(cur, norte, t["medir"],
                                                           "Sam North", "Sam Noble")
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'asignada', 'bloqueada', 'persona')""", (t["medir"],))
        t["montar"] = _tarea(cur, norte, "Montar la línea", "Sam North", "field",
                             "asignada", DESPUES)
        t["calibrar"] = _tarea(cur, norte, "Calibrar la balanza", "Sam Noble", "quality",
                               "en_curso", ANTES)
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id)
                       values (%s, %s, %s)""", (norte["id"], t["calibrar"], t["montar"]))
        t["auditar"] = _tarea(cur, norte, "Auditar proveedores", "Sam Noble", "quality",
                              "asignada", ANTES)
        t["ordenar"] = _tarea(cur, norte, "Ordenar el depósito", "Taylor Quinn", "field",
                              "asignada", DESPUES)
        t["antes"] = _tarea(cur, norte, "Lo de antes", "Sam North", "field", "cancelada",
                            ANTES)
        _tarea(cur, oeste, "Secreto del oeste", "Sam Noble", "quality", "en_curso", ANTES)
        _tarea(cur, oeste, "Galpón del oeste", "Sam North", "field", "asignada", DESPUES)
    conn.commit()
    return {**intake_world, "t": t}


ABIERTAS_DEL_NORTE = {"Pintar el galpón", "Medir el ruido", "Montar la línea",
                      "Calibrar la balanza", "Auditar proveedores", "Ordenar el depósito"}


# --- Las funciones --------------------------------------------------------------------------

def test_las_de_la_sesion_son_elevadas_con_camino_fijo_y_sin_public(conn):
    with admin(conn) as cur:
        for funcion in DE_LA_SESION + INTERNAS:
            cur.execute(
                """select p.prosecdef, r.rolname dueno, p.proconfig,
                          has_function_privilege('leda_app', p.oid, 'execute') app,
                          exists (select 1 from aclexplode(coalesce(p.proacl,
                                    acldefault('f', p.proowner))) a
                                   where a.grantee = 0 and a.privilege_type = 'EXECUTE') publico
                     from pg_proc p
                     join pg_roles r on r.oid = p.proowner
                     join pg_namespace n on n.oid = p.pronamespace
                    where n.nspname = 'leda' and p.proname = %s""", (funcion,))
            filas = cur.fetchall()
            assert len(filas) == 1, f"{funcion}: tiene que existir una sola"
            f = filas[0]
            assert f["dueno"] == "leda_owner", funcion
            assert not f["publico"], funcion
            assert "search_path=leda, public, pg_temp" in (f["proconfig"] or []), funcion
            if funcion in DE_LA_SESION:
                # La web las llama: elevadas, y sólo `leda_app` las ejecuta.
                assert f["prosecdef"] and f["app"], funcion
            else:
                # La regla: la corren las de la sesión, con su dueño; `leda_app` no la llama
                # con una persona que elija.
                assert not f["prosecdef"] and not f["app"], funcion


# --- Qué vistas tiene cada persona ----------------------------------------------------------

def test_las_vistas_de_cada_puesto(conn, mundo):
    assert _vistas(conn, _entrar(conn, mundo, "Sam North")) == ["tus"]
    assert _vistas(conn, _entrar(conn, mundo, "Taylor Quinn")) == ["tus", "sector"]
    assert _vistas(conn, _entrar(conn, mundo, "Morgan Hale")) == ["tus", "equipo"]


def test_la_autoridad_que_tambien_es_referente_tiene_las_tres(conn, mundo):
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (_persona(mundo, "Morgan Hale"), mundo["north-lab"]["areas"]["quality"]))
    conn.commit()
    assert _vistas(conn, _entrar(conn, mundo, "Morgan Hale")) == ["tus", "sector", "equipo"]


def test_una_sesion_que_no_entra_no_tiene_vistas_ni_tareas(conn, mundo):
    sesion = _entrar(conn, mundo, "Sam North")
    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (_persona(mundo, "Sam North"),))
    conn.commit()
    assert _vistas(conn, sesion) is None
    assert _lista(conn, sesion, "tus") == {}
    assert _vistas(conn, secrets.token_urlsafe(32)) is None
    assert _lista(conn, secrets.token_urlsafe(32), "tus") == {}
    assert _lista(conn, "no es un token", "equipo") == {}


def test_una_vista_desconocida_se_rechaza(conn, mundo):
    sesion = _entrar(conn, mundo, "Morgan Hale")
    with pytest.raises(psycopg.errors.RaiseException, match="vista desconocida"):
        _lista(conn, sesion, "todo")
    conn.rollback()


# --- Integrante: "Tus tareas" ---------------------------------------------------------------

def test_el_integrante_ve_las_suyas_las_que_espera_y_las_que_lo_esperan(conn, mundo):
    norte = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")
    assert {t: f["papel"] for t, f in norte.items()} == {
        "Pintar el galpón": "mia", "Medir el ruido": "mia", "Montar la línea": "mia",
        "Calibrar la balanza": "espero"}
    noble = _lista(conn, _entrar(conn, mundo, "Sam Noble"), "tus")
    assert {t: f["papel"] for t, f in noble.items()} == {
        "Calibrar la balanza": "mia", "Auditar proveedores": "mia",
        "Montar la línea": "me_esperan", "Medir el ruido": "me_esperan"}
    fila = norte["Calibrar la balanza"]
    assert set(fila) == COLUMNAS
    assert fila["responsable"] == "Sam Noble 1" and fila["area"] == "Quality Guild"
    assert fila["estado"] == "en_curso" and fila["fecha_objetivo"] == ANTES
    assert fila["asignada_en"] == datetime(2026, 10, 12, 13, 0, tzinfo=timezone.utc)


def test_el_integrante_no_ve_una_tarea_de_otra_area_que_no_lo_toca(conn, mundo):
    sesion = _entrar(conn, mundo, "Sam North")
    assert "Auditar proveedores" not in _lista(conn, sesion, "tus")
    # Ni pidiendo una vista que no es la suya.
    assert _lista(conn, sesion, "sector") == {}
    assert _lista(conn, sesion, "equipo") == {}


def test_el_integrante_no_ve_el_atraso_ni_el_bloqueo_ajeno(conn, mundo):
    norte = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")
    # Lo suyo, con su atraso y su bloqueo.
    assert norte["Pintar el galpón"]["vencida"] is True
    assert norte["Montar la línea"]["vencida"] is False
    assert norte["Medir el ruido"]["bloqueo_abierto"] is True
    assert norte["Pintar el galpón"]["bloqueo_abierto"] is False
    # La de Sam Noble que espera está vencida, pero no es su atraso: no lo ve.
    assert norte["Calibrar la balanza"]["vencida"] is None
    assert norte["Calibrar la balanza"]["bloqueo_abierto"] is None
    noble = _lista(conn, _entrar(conn, mundo, "Sam Noble"), "tus")
    assert noble["Medir el ruido"]["vencida"] is None
    assert noble["Medir el ruido"]["bloqueo_abierto"] is None


def test_lo_terminado_o_cancelado_no_esta_en_la_lista(conn, mundo):
    for nombre, vista in (("Sam North", "tus"), ("Taylor Quinn", "sector"),
                          ("Morgan Hale", "equipo")):
        assert "Lo de antes" not in _lista(conn, _entrar(conn, mundo, nombre), vista)


def test_a_quien_revisa_lo_espera_la_revision(conn, mundo):
    """Una entrega espera a quien la revisa (Taylor Quinn aprueba a Sam Noble): le aparece en
    "Tus tareas" aunque sea de otra área, sin su atraso."""
    with admin(conn) as cur:
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'asignada', 'en_revision', 'persona')""",
                    (mundo["t"]["auditar"],))
    conn.commit()
    taylor = _lista(conn, _entrar(conn, mundo, "Taylor Quinn"), "tus")
    assert taylor["Auditar proveedores"]["papel"] == "me_esperan"
    assert taylor["Auditar proveedores"]["vencida"] is None
    assert taylor["Ordenar el depósito"]["papel"] == "mia"


def test_la_cadena_que_dice_quien_destraba_tambien_es_una_espera(conn, mundo):
    """Sam Noble, que destraba "Medir el ruido", dice que está trabada con su bloqueo de
    "Auditar proveedores": Sam North espera esa tarea."""
    ws = mundo["north-lab"]["id"]
    with admin(conn) as cur:
        suyo, _ = _bloqueo(cur, mundo["north-lab"], mundo["t"]["auditar"],
                           "Sam Noble", "Morgan Hale")
        cur.execute("""insert into dicho_de_quien_destraba (workspace_id, blocker_unblocker_id,
                                                            dicho_por_membership_id,
                                                            espera_su_bloqueo_id, at)
                       values (%s, %s, %s, %s, %s)""",
                    (ws, mundo["t"]["destraba_medir"], _persona(mundo, "Sam Noble"), suyo,
                     AHORA))
    conn.commit()
    norte = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")
    assert norte["Auditar proveedores"]["papel"] == "espero"
    assert norte["Auditar proveedores"]["vencida"] is None


def test_la_pagina_de_la_tarea_sigue_su_propia_regla(conn, mundo):
    """La lista no amplía quién abre la página: la tarea que espera de otra área la ve en la
    lista, y la página sólo si `puede_ver_tarea` lo dice."""
    norte = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")
    assert norte["Pintar el galpón"]["ve_la_pagina"] is True
    assert norte["Calibrar la balanza"]["ve_la_pagina"] is False


# --- Referente: "Tu sector" -----------------------------------------------------------------

def test_el_referente_ve_todo_su_sector_con_atrasos_y_bloqueos_y_no_otro(conn, mundo):
    sector = _lista(conn, _entrar(conn, mundo, "Taylor Quinn"), "sector")
    assert set(sector) == {"Pintar el galpón", "Medir el ruido", "Montar la línea",
                           "Ordenar el depósito"}
    assert sector["Pintar el galpón"]["vencida"] is True
    assert sector["Medir el ruido"]["bloqueo_abierto"] is True
    assert sector["Montar la línea"]["vencida"] is False


# --- Autoridad final: "El equipo" -----------------------------------------------------------

def test_la_autoridad_ve_todo_su_espacio_y_nada_de_otro(conn, mundo):
    equipo = _lista(conn, _entrar(conn, mundo, "Morgan Hale"), "equipo")
    assert set(equipo) == ABIERTAS_DEL_NORTE
    assert equipo["Calibrar la balanza"]["vencida"] is True
    assert equipo["Auditar proveedores"]["vencida"] is True
    assert equipo["Medir el ruido"]["bloqueo_abierto"] is True
    # Cada fila es una tarea: ninguna cuenta ni orden por persona.
    assert all(set(f) == COLUMNAS for f in equipo.values())
    oeste = _lista(conn, _entrar(conn, mundo, "Morgan Hale", "west-studio"), "equipo")
    assert set(oeste) == {"Secreto del oeste", "Galpón del oeste"}


def test_la_regla_no_cruza_espacios_aunque_se_la_llame_con_otra_persona(conn, mundo):
    """La regla corre con la RLS de quien la llama: con el espacio del norte fijado, una
    persona del oeste no encuentra nada."""
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("set local role leda_owner")
        cur.execute("select set_config('leda.workspace_id', %s, true)",
                    (mundo["north-lab"]["id"],))
        cur.execute("select * from tareas_que_ve(%s, 'equipo', %s)",
                    (_persona(mundo, "Morgan Hale", "west-studio"), AHORA))
        assert cur.fetchall() == []
        cur.execute("select * from tareas_que_ve(%s, 'equipo', %s)",
                    (_persona(mundo, "Morgan Hale"), AHORA))
        assert {f["titulo"] for f in cur.fetchall()} == ABIERTAS_DEL_NORTE
    conn.commit()
