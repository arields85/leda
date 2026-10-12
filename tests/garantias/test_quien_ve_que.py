"""Quién ve qué en las listas de la puerta del equipo (ADR 0022, decisiones 3, 5, 11 y 13;
migración 0058): la capa de garantías.

Lo que se prueba acá es la regla en la base, no la API ni la web:

- **Una sola regla** (decisión 13): la lista de cada vista extiende `puede_ver_tarea` de una
  tarea a la lista, en SQL (`tareas_que_ve`). La web la lee con la sesión
  (`tareas_de_la_sesion`, `vistas_de_la_sesion`): la persona sale del hash del token de la
  sesión, que revalida `sesion_vigente` (0057), nunca de un dato del pedido (decisión 11).
- **Integrante, "Tus tareas"** (decisión 3): las suyas, las que espera de otros y las que otros
  esperan de él. De una tarea ajena ve lo mismo que el informe al grupo (decisiones del usuario
  del 2026-10-12, 1, 5 y 7; migración 0060): su estado y si está trabada; su atraso, recién
  cuando ya se habló en privado con quien la tiene (constitución §8): una previsión vigente
  posterior al vencimiento, que también ve, o el escalamiento de ese vencimiento ya salido.
  Una tarea de otra área que no lo toca no aparece.
- **Referente, "Tu sector":** todas las tareas de su área, con fechas, atrasos y bloqueos; las de
  otra área, no.
- **Autoridad final, "El equipo":** todo su espacio y nada de otro, sin rankings ni cuentas por
  persona (constitución §15, principio 14).
- **Qué vistas tiene cada persona:** integrante, "tus"; referente, además "sector"; autoridad
  final, además "equipo".
- **Las terminadas de los últimos 30 días** (decisión 3 del usuario, 2026-10-12; migración
  0060), cada vista en su alcance, con quién las hizo; las canceladas, no.
"""

from __future__ import annotations

import contextlib
import hashlib
import secrets
from datetime import date, datetime, timedelta, timezone

import psycopg
import pytest

from leda.db import admin, espacio

AHORA = datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc)   # jueves
ANTES = datetime(2026, 10, 19, 20, 0, tzinfo=timezone.utc)   # lunes: ya venció
DESPUES = datetime(2026, 10, 30, 20, 0, tzinfo=timezone.utc)  # viernes de la otra semana

DE_LA_SESION = ("tareas_de_la_sesion", "vistas_de_la_sesion", "terminadas_de_la_sesion")
INTERNAS = ("tareas_que_ve", "vistas_de", "terminadas_que_ve")
COLUMNAS = {"task_id", "titulo", "estado", "fecha_objetivo", "asignada_en", "responsable",
            "area", "papel", "vencida", "bloqueo_abierto", "ve_la_pagina", "prevision"}


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


def _terminadas(conn, sesion: str, vista: str) -> dict[str, dict]:
    """Las terminadas de los últimos 30 días que ve la sesión en una vista, por título."""
    with sin_espacio(conn) as cur:
        cur.execute("select * from terminadas_de_la_sesion(%s, %s, %s)",
                    (_hash(sesion), vista, AHORA))
        filas = cur.fetchall()
    conn.commit()
    return {f["titulo"]: f for f in filas}


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


def _prevision(cur, mundo: dict, tarea: str, de: str, prevista: date, at: datetime,
               reemplaza: str | None = None) -> str:
    """Una previsión que dio `de` para `tarea` (`task_forecast`, como la guarda el motor)."""
    cur.execute("select fecha_objetivo from task where id = %s", (tarea,))
    comprometida = cur.fetchone()["fecha_objetivo"]
    cur.execute(
        """insert into task_forecast (workspace_id, task_id, fecha_prevista, motivo,
                                      fecha_comprometida, atraso_dias_habiles, reemplaza_id,
                                      dicho_por_membership_id, at)
           values (%s, %s, %s, 'falta el cable', %s, 2, %s, %s, %s) returning id""",
        (mundo["id"], tarea, prevista, comprometida, reemplaza,
         mundo["people"][de]["membership_id"], at))
    return str(cur.fetchone()["id"])


def _escalamiento(cur, mundo: dict, tarea: str, vence: str, estado: str = "enviado") -> None:
    """El escalamiento por falta de respuesta de ese vencimiento (`scheduled_notice`), a la
    autoridad del espacio."""
    cur.execute(
        """insert into scheduled_notice (workspace_id, tipo, task_id,
                                         destinatario_membership_id, hechos, programado_para,
                                         estado, dedupe_key, creado_en, resuelto_en)
           values (%s, 'escalamiento', %s, %s, jsonb_build_object('vence', %s::text), %s, %s,
                   %s, %s, %s)""",
        (mundo["id"], tarea, mundo["people"]["Morgan Hale"]["membership_id"], vence, ANTES,
         estado,
         f"prueba:escalamiento:{tarea}:{vence}:{estado}", ANTES,
         ANTES if estado == "enviado" else None))


def _trabada_y_vencida(conn, mundo: dict) -> str:
    """"Afinar el motor" (Sam North, field): venció el lunes y está trabada; la destraba Sam
    Noble."""
    norte = mundo["north-lab"]
    with admin(conn) as cur:
        afinar = _tarea(cur, norte, "Afinar el motor", "Sam North", "field", "asignada", ANTES)
        _bloqueo(cur, norte, afinar, "Sam North", "Sam Noble")
        cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                     actor_kind)
                       values (%s, 'asignada', 'bloqueada', 'persona')""", (afinar,))
    conn.commit()
    return afinar


def _terminada(cur, mundo: dict, titulo: str, persona: str, area: str,
               cuando: datetime) -> str:
    """Una tarea de `persona` terminada en `cuando`, con la aprobación que su cierre exige."""
    tarea = _tarea(cur, mundo, titulo, persona, area, "asignada", ANTES)
    cur.execute("""insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                         aprobador_membership_id, decision)
                   values (%s, 'tarea', %s,
                           coalesce(quien_revisa_la_tarea(%s), %s), 'aprobado')""",
                (mundo["id"], tarea, tarea, mundo["people"]["Morgan Hale"]["membership_id"]))
    cur.execute("""insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                                 actor_kind, motivo, at)
                   values (%s, 'asignada', 'terminada', 'sistema', 'prueba', %s)""",
                (tarea, cuando))
    return tarea


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


def test_lo_suyo_con_su_atraso_y_su_bloqueo_como_hasta_ahora(conn, mundo):
    norte = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")
    assert norte["Pintar el galpón"]["vencida"] is True
    assert norte["Montar la línea"]["vencida"] is False
    assert norte["Medir el ruido"]["bloqueo_abierto"] is True
    assert norte["Pintar el galpón"]["bloqueo_abierto"] is False
    assert norte["Pintar el galpón"]["prevision"] is None


def test_lo_ajeno_trae_su_estado_y_si_esta_trabada(conn, mundo):
    """Decisión 7: quien espera una tarea ajena ve que está trabada; quien la destraba, también
    (como en el informe al grupo)."""
    noble = _lista(conn, _entrar(conn, mundo, "Sam Noble"), "tus")
    assert noble["Medir el ruido"]["papel"] == "me_esperan"
    assert noble["Medir el ruido"]["estado"] == "bloqueada"
    assert noble["Medir el ruido"]["bloqueo_abierto"] is True
    norte = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")
    assert norte["Calibrar la balanza"]["bloqueo_abierto"] is False
    assert norte["Calibrar la balanza"]["fecha_objetivo"] == ANTES


def test_el_atraso_ajeno_no_se_marca_antes_de_hablarse(conn, mundo):
    """"Calibrar la balanza" (Sam Noble) venció el lunes, pero nadie lo habló con él: Sam North,
    que la espera, ve la fecha sola (constitución §8)."""
    calibrar = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")["Calibrar la balanza"]
    assert calibrar["vencida"] is False
    assert calibrar["prevision"] is None


def test_una_prevision_posterior_es_un_atraso_ya_hablado(conn, mundo):
    """Regla a: Sam Noble le dio a Leda un día posterior al vencimiento; Sam North ve la marca
    (ya venció) y la previsión."""
    with admin(conn) as cur:
        _prevision(cur, mundo["north-lab"], mundo["t"]["calibrar"], "Sam Noble",
                   date(2026, 10, 28), ANTES)
    conn.commit()
    calibrar = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")["Calibrar la balanza"]
    assert calibrar["vencida"] is True
    assert calibrar["prevision"] == date(2026, 10, 28)


def test_una_prevision_posterior_antes_del_vencimiento_no_marca_vencida(conn, mundo):
    """"Soldar el soporte" (Sam Noble) vence el viernes que viene y "Montar la línea" depende
    de ella: Sam Noble ya dijo que la termina después; Sam North ve la previsión, sin la marca."""
    norte = mundo["north-lab"]
    with admin(conn) as cur:
        soldar = _tarea(cur, norte, "Soldar el soporte", "Sam Noble", "quality", "asignada",
                        DESPUES)
        cur.execute("""insert into dependency (workspace_id, origen_task_id, destino_task_id)
                       values (%s, %s, %s)""", (norte["id"], soldar, mundo["t"]["montar"]))
        _prevision(cur, norte, soldar, "Sam Noble", date(2026, 11, 3), ANTES)
    conn.commit()
    fila = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")["Soldar el soporte"]
    assert fila["papel"] == "espero"
    assert fila["vencida"] is False
    assert fila["prevision"] == date(2026, 11, 3)


def test_solo_cuenta_la_prevision_vigente(conn, mundo):
    """Una previsión reemplazada por otra que ya no es posterior al vencimiento no es un atraso
    hablado: se mira la vigente, como el motor (`prevision_vigente`)."""
    with admin(conn) as cur:
        vieja = _prevision(cur, mundo["north-lab"], mundo["t"]["calibrar"], "Sam Noble",
                           date(2026, 10, 28), ANTES)
        _prevision(cur, mundo["north-lab"], mundo["t"]["calibrar"], "Sam Noble",
                   date(2026, 10, 19), AHORA, reemplaza=vieja)
    conn.commit()
    calibrar = _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")["Calibrar la balanza"]
    assert calibrar["vencida"] is False
    assert calibrar["prevision"] is None


def test_el_escalamiento_de_ese_vencimiento_es_un_atraso_asentado(conn, mundo):
    """Regla b: salió el escalamiento por falta de respuesta de ese vencimiento; uno guardado
    sin salir, o de otro vencimiento, no cuenta."""
    t = mundo["t"]
    with admin(conn) as cur:
        _escalamiento(cur, mundo["north-lab"], t["calibrar"], "2026-10-19", estado="guardado")
        _escalamiento(cur, mundo["north-lab"], t["calibrar"], "2026-10-12")
    conn.commit()
    sesion = _entrar(conn, mundo, "Sam North")
    assert _lista(conn, sesion, "tus")["Calibrar la balanza"]["vencida"] is False
    with admin(conn) as cur:
        _escalamiento(cur, mundo["north-lab"], t["calibrar"], "2026-10-19")
    conn.commit()
    calibrar = _lista(conn, sesion, "tus")["Calibrar la balanza"]
    assert calibrar["vencida"] is True
    assert calibrar["prevision"] is None


def test_trabada_y_vencida_a_la_vez(conn, mundo):
    """Decisión 5: "Afinar el motor" (Sam North) trabada y vencida; Sam Noble, que la destraba,
    ve las dos cosas sólo cuando el atraso ya se habló."""
    afinar = _trabada_y_vencida(conn, mundo)
    sesion = _entrar(conn, mundo, "Sam Noble")
    fila = _lista(conn, sesion, "tus")["Afinar el motor"]
    assert fila["bloqueo_abierto"] is True and fila["vencida"] is False
    with admin(conn) as cur:
        _escalamiento(cur, mundo["north-lab"], afinar, "2026-10-19")
    conn.commit()
    fila = _lista(conn, sesion, "tus")["Afinar el motor"]
    assert fila["bloqueo_abierto"] is True and fila["vencida"] is True


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
    # Entregada: ya no es un atraso que siga (informe al grupo, `_sin_entregar`).
    assert taylor["Auditar proveedores"]["vencida"] is False
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
    # Vencida, pero nadie lo habló con Sam Noble: la fecha sola; trabada, sí.
    assert norte["Auditar proveedores"]["vencida"] is False
    assert norte["Auditar proveedores"]["bloqueo_abierto"] is True


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


def test_hablar_un_atraso_no_amplia_quien_ve_la_tarea(conn, mundo):
    """"Auditar proveedores" no toca a Sam North: con su atraso hablado, sigue fuera de su
    lista."""
    with admin(conn) as cur:
        _escalamiento(cur, mundo["north-lab"], mundo["t"]["auditar"], "2026-10-19")
        _prevision(cur, mundo["north-lab"], mundo["t"]["auditar"], "Sam Noble",
                   date(2026, 10, 28), ANTES)
    conn.commit()
    assert "Auditar proveedores" not in _lista(conn, _entrar(conn, mundo, "Sam North"), "tus")


# --- Las terminadas de los últimos 30 días --------------------------------------------------

@pytest.fixture
def terminadas(conn, mundo) -> dict:
    """North Lab: "Cerrar el tablero" (Sam North, field, hace 2 días), "Pesar la carga" (Sam
    Noble, quality, hace 29 días), "Lo del mes pasado" (Sam North, field, hace 31 días); West
    Studio: "Terminada del oeste" (Sam North, hace 2 días)."""
    norte, oeste = mundo["north-lab"], mundo["west-studio"]
    with admin(conn) as cur:
        _terminada(cur, norte, "Cerrar el tablero", "Sam North", "field",
                   AHORA - timedelta(days=2))
        _terminada(cur, norte, "Pesar la carga", "Sam Noble", "quality",
                   AHORA - timedelta(days=29))
        _terminada(cur, norte, "Lo del mes pasado", "Sam North", "field",
                   AHORA - timedelta(days=31))
        _terminada(cur, oeste, "Terminada del oeste", "Sam North", "field",
                   AHORA - timedelta(days=2))
    conn.commit()
    return mundo


def test_las_terminadas_de_cada_vista_en_su_alcance(conn, terminadas):
    mundo = terminadas
    assert set(_terminadas(conn, _entrar(conn, mundo, "Sam North"), "tus")) == {
        "Cerrar el tablero"}
    assert set(_terminadas(conn, _entrar(conn, mundo, "Sam Noble"), "tus")) == {
        "Pesar la carga"}
    assert set(_terminadas(conn, _entrar(conn, mundo, "Taylor Quinn"), "sector")) == {
        "Cerrar el tablero"}
    equipo = _terminadas(conn, _entrar(conn, mundo, "Morgan Hale"), "equipo")
    assert set(equipo) == {"Cerrar el tablero", "Pesar la carga"}
    fila = equipo["Pesar la carga"]
    assert set(fila) == {"task_id", "titulo", "responsable", "area", "terminada_en"}
    assert fila["responsable"] == "Sam Noble 1" and fila["area"] == "Quality Guild"
    assert fila["terminada_en"] == AHORA - timedelta(days=29)


def test_una_terminada_de_hace_31_dias_o_una_cancelada_no_estan(conn, terminadas):
    for nombre, vista in (("Sam North", "tus"), ("Taylor Quinn", "sector"),
                          ("Morgan Hale", "equipo")):
        vistas = _terminadas(conn, _entrar(conn, terminadas, nombre), vista)
        assert "Lo del mes pasado" not in vistas
        assert "Lo de antes" not in vistas
        assert vistas, nombre


def test_las_terminadas_no_cruzan_espacios_ni_vistas_ajenas(conn, terminadas):
    mundo = terminadas
    sesion = _entrar(conn, mundo, "Sam North")
    assert _terminadas(conn, sesion, "sector") == {}
    assert _terminadas(conn, sesion, "equipo") == {}
    oeste = _terminadas(conn, _entrar(conn, mundo, "Morgan Hale", "west-studio"), "equipo")
    assert set(oeste) == {"Terminada del oeste"}
    assert _terminadas(conn, secrets.token_urlsafe(32), "tus") == {}
    with pytest.raises(psycopg.errors.RaiseException, match="vista desconocida"):
        _terminadas(conn, sesion, "todo")
    conn.rollback()
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("set local role leda_owner")
        cur.execute("select set_config('leda.workspace_id', %s, true)",
                    (mundo["north-lab"]["id"],))
        cur.execute("select * from terminadas_que_ve(%s, 'equipo', %s)",
                    (_persona(mundo, "Morgan Hale", "west-studio"), AHORA))
        assert cur.fetchall() == []
    conn.commit()
