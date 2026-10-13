"""La entrada a la web por chat (ADR 0022, decisión 4; migración 0066; tarea A-3 de
`odd/tasks/acceso-por-chat.md`): la capa de garantías.

Lo que se prueba acá es la base, no la conversación:

- **Lo que la cocina pregunta sin leer las tablas:** si la persona entró alguna vez a la web
  (`entro_a_la_web`) y si tiene un enlace sin usar (`tiene_un_enlace_sin_usar`), en el espacio de
  quien llama.
- **El corte siempre deja su auditoría** (decisión técnica 3), también sin sesiones abiertas.
- **Aislamiento:** las dos tablas nuevas con `workspace_id` obligatorio y `row level security`
  forzado; desde un espacio no se ve nada de otro.
"""

from __future__ import annotations

import re
import secrets
from pathlib import Path

import psycopg
import pytest

from leda import web_app
from leda.db import admin, espacio, sin_espacio
from leda.salida import enqueue_outbox

TABLAS = ("message_outbox_entrada_web", "ofrecimiento_web")
FUNCIONES = ("entro_a_la_web", "tiene_un_enlace_sin_usar", "cortar_sesiones_de_membresia")


# --- Ayudas ---------------------------------------------------------------------------------

def _persona(mundo: dict, nombre: str = "Sam Noble", slug: str = "north-lab") -> str:
    return mundo[slug]["people"][nombre]["membership_id"]


def _filas(conn, sql: str, *args) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(sql, args)
        filas = cur.fetchall()
    conn.commit()
    return filas


def _auditoria(conn, accion: str) -> list[dict]:
    return _filas(conn, "select * from audit_log where accion = %s order by at, id", accion)


def _emitir(conn, mundo: dict, nombre: str = "Sam Noble", slug: str = "north-lab") -> str:
    with espacio(conn, mundo[slug]["id"]) as cur:
        token = web_app.emitir_enlace(cur, _persona(mundo, nombre, slug))
    conn.commit()
    assert token
    return token


def _canjear(conn, token: str) -> str | None:
    with sin_espacio(conn) as cur:
        cur.execute("select canjear_enlace_de_entrada(%s, %s) as id",
                    (web_app._hash(token), web_app._hash(secrets.token_urlsafe(32))))
        sesion = cur.fetchone()["id"]
    conn.commit()
    return str(sesion) if sesion else None


def _pregunta(conn, mundo: dict, funcion: str, nombre: str = "Sam Noble",
              slug: str = "north-lab", en: str | None = None) -> bool:
    with espacio(conn, mundo[en or slug]["id"]) as cur:
        cur.execute(f"select {funcion}(%s) as si", (_persona(mundo, nombre, slug),))
        si = cur.fetchone()["si"]
    conn.commit()
    return si


def _cortar(conn, mundo: dict, nombre: str = "Sam Noble", slug: str = "north-lab",
            en: str | None = None, **como) -> int:
    with espacio(conn, mundo[en or slug]["id"]) as cur:
        cortadas = web_app.cortar_sesiones(cur, _persona(mundo, nombre, slug), **como)
    conn.commit()
    return cortadas


# --- Las tablas y las funciones -------------------------------------------------------------

def test_las_tablas_tienen_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in TABLAS:
            cur.execute("""select relrowsecurity, relforcerowsecurity
                             from pg_class where oid = to_regclass(%s)""", (f"leda.{tabla}",))
            fila = cur.fetchone()
            assert fila is not None, f"{tabla} no existe"
            assert fila["relrowsecurity"] and fila["relforcerowsecurity"], tabla
            cur.execute("""select is_nullable from information_schema.columns
                            where table_schema = 'leda' and table_name = %s
                              and column_name = 'workspace_id'""", (tabla,))
            assert cur.fetchone()["is_nullable"] == "NO", tabla
            cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                        (f"leda.{tabla}",))
            assert {p["polname"] for p in cur.fetchall()} == {"aislamiento_espacio"}, tabla


def test_la_aplicacion_agrega_y_lee_la_marca_y_maneja_el_ofrecimiento(conn):
    """La marca sólo se agrega y se lee (como la del enlace de una tarea); el ofrecimiento se
    reserva, se marca ofrecido y se libera. Nada para `public` ni para la autoridad."""
    esperado = {"message_outbox_entrada_web": {"select", "insert"},
                "ofrecimiento_web": {"select", "insert", "update", "delete"}}
    with admin(conn) as cur:
        for tabla, privilegios in esperado.items():
            for rol, deberia in (("leda_app", privilegios), ("leda_gateway", set()),
                                 ("public", set())):
                tiene = set()
                for privilegio in ("select", "insert", "update", "delete"):
                    cur.execute("select has_table_privilege(%s, %s, %s) as si",
                                (rol, f"leda.{tabla}", privilegio))
                    if cur.fetchone()["si"]:
                        tiene.add(privilegio)
                assert tiene == deberia, (tabla, rol, tiene)
            cur.execute("select has_table_privilege('leda_admin', %s, 'insert') as si",
                        (f"leda.{tabla}",))
            assert cur.fetchone()["si"], f"{tabla}: la bienvenida se escribe como leda_admin"


def test_las_funciones_son_elevadas_de_leda_owner_y_solo_las_ejecuta_la_aplicacion(conn):
    with admin(conn) as cur:
        for funcion in FUNCIONES:
            cur.execute("""select p.prosecdef, r.rolname dueno,
                                  has_function_privilege('leda_app', p.oid, 'execute') app,
                                  has_function_privilege('public', p.oid, 'execute') pub
                             from pg_proc p join pg_roles r on r.oid = p.proowner
                             join pg_namespace n on n.oid = p.pronamespace
                            where n.nspname = 'leda' and p.proname = %s""", (funcion,))
            fila = cur.fetchone()
            assert fila is not None, f"{funcion} no existe"
            assert fila["prosecdef"] and fila["dueno"] == "leda_owner", funcion
            assert fila["app"] and not fila["pub"], funcion


# --- Si entró alguna vez y si tiene un enlace sin usar --------------------------------------

def test_entro_a_la_web_solo_cuando_canjeo_un_enlace(conn, intake_world):
    assert _pregunta(conn, intake_world, "entro_a_la_web") is False
    token = _emitir(conn, intake_world)
    assert _pregunta(conn, intake_world, "entro_a_la_web") is False, "emitido no es entrar"
    assert _canjear(conn, token)
    assert _pregunta(conn, intake_world, "entro_a_la_web") is True
    # Y sigue habiendo entrado aunque después se le corte el acceso.
    _cortar(conn, intake_world)
    assert _pregunta(conn, intake_world, "entro_a_la_web") is True


def test_tiene_un_enlace_sin_usar_hasta_que_lo_canjea_o_se_anula(conn, intake_world):
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is False
    token = _emitir(conn, intake_world)
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is True
    assert _canjear(conn, token)
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is False
    _emitir(conn, intake_world)
    _cortar(conn, intake_world)
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is False


def test_un_enlace_vencido_sin_usar_todavia_cuenta_como_sin_usar(conn, intake_world):
    """El que un enlace nuevo deja sin servir, vencido o no (la 0065 no lo marca)."""
    _emitir(conn, intake_world)
    with admin(conn) as cur:
        cur.execute("update enlace_de_entrada set emitido_en = now() - interval '25 hours'")
    conn.commit()
    assert _pregunta(conn, intake_world, "tiene_un_enlace_sin_usar") is True


def test_desde_otro_espacio_las_preguntas_dan_que_no(conn, intake_world):
    """Una membresía de West Studio, vista desde North Lab, es igual a una que no existe."""
    token = _emitir(conn, intake_world, slug="west-studio")
    _emitir(conn, intake_world, nombre="Sam North", slug="west-studio")
    assert _canjear(conn, token)
    for funcion, nombre in (("entro_a_la_web", "Sam Noble"),
                            ("tiene_un_enlace_sin_usar", "Sam North")):
        assert _pregunta(conn, intake_world, funcion, nombre, slug="west-studio") is True
        assert _pregunta(conn, intake_world, funcion, nombre, slug="west-studio",
                         en="north-lab") is False, funcion


# --- El corte siempre deja su auditoría -----------------------------------------------------

def test_el_corte_sin_sesiones_deja_su_auditoria_con_el_motivo_y_quien(conn, intake_world):
    _emitir(conn, intake_world)                         # un enlace sin usar, ninguna sesión
    quien = intake_world["north-lab"]["people"]["Sam Noble"]["app_user_id"]
    assert _cortar(conn, intake_world, motivo="perdio_el_celular",
                   actor_app_user_id=quien) == 0
    [corte] = _auditoria(conn, "cortar_acceso_web")
    assert str(corte["workspace_id"]) == intake_world["north-lab"]["id"]
    assert (corte["sujeto_tipo"], str(corte["sujeto_id"])) == (
        "membership", _persona(intake_world))
    assert corte["actor_kind"] == "persona" and str(corte["actor_app_user_id"]) == quien
    assert corte["detalle"] == {"motivo": "perdio_el_celular", "sesiones_cortadas": 0,
                                "enlace_anulado": True}
    assert corte["pack_hash"] == "hash-0" and corte["nucleo_hash"]
    assert _auditoria(conn, "cortar_sesion_web") == []


def test_el_corte_sin_nada_que_cortar_tambien_queda(conn, intake_world):
    assert _cortar(conn, intake_world) == 0
    [corte] = _auditoria(conn, "cortar_acceso_web")
    assert corte["detalle"] == {"motivo": "administrador", "sesiones_cortadas": 0,
                                "enlace_anulado": False}
    assert corte["actor_kind"] == "leda" and corte["actor_app_user_id"] is None


def test_el_corte_con_sesiones_deja_cada_sesion_y_el_corte(conn, intake_world):
    for _ in range(2):
        assert _canjear(conn, _emitir(conn, intake_world))
    assert _cortar(conn, intake_world, motivo="perdio_el_celular") == 2
    sesiones = _auditoria(conn, "cortar_sesion_web")
    assert [s["detalle"]["motivo"] for s in sesiones] == ["perdio_el_celular"] * 2
    [corte] = _auditoria(conn, "cortar_acceso_web")
    assert corte["detalle"] == {"motivo": "perdio_el_celular", "sesiones_cortadas": 2,
                                "enlace_anulado": False}


def test_un_espacio_no_corta_ni_audita_a_alguien_de_otro(conn, intake_world):
    sesion = _canjear(conn, _emitir(conn, intake_world, slug="west-studio"))
    assert _cortar(conn, intake_world, slug="west-studio", en="north-lab") == 0
    assert _auditoria(conn, "cortar_acceso_web") == []
    [fila] = _filas(conn, "select cortada_en from sesion_web where id = %s", sesion)
    assert fila["cortada_en"] is None


def test_un_motivo_desconocido_no_corta_ni_audita(conn, intake_world):
    with pytest.raises(psycopg.errors.RaiseException, match="motivo desconocido"):
        _cortar(conn, intake_world, motivo="porque_si")
    conn.rollback()
    assert _auditoria(conn, "cortar_acceso_web") == []


# --- Aislamiento ----------------------------------------------------------------------------

def test_desde_un_espacio_no_se_ven_las_marcas_ni_los_ofrecimientos_de_otro(conn, intake_world):
    oeste = intake_world["west-studio"]
    persona = _persona(intake_world, slug="west-studio")
    with espacio(conn, oeste["id"]) as cur:
        enqueue_outbox(cur, workspace_id=oeste["id"], chat_id=71103, text="Hola.",
                       recipient_membership_id=persona, dedupe_key="oeste")
        cur.execute("""insert into message_outbox_entrada_web (workspace_id, outbox_id,
                                                             membership_id)
                       select workspace_id, id, %s from message_outbox
                        where dedupe_key = 'oeste'""", (persona,))
        cur.execute("insert into ofrecimiento_web (workspace_id, membership_id) values (%s, %s)",
                    (oeste["id"], persona))
    conn.commit()
    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        for tabla in TABLAS:
            cur.execute(f"select count(*) n from {tabla}")
            assert cur.fetchone()["n"] == 0, f"{tabla}: se ven filas de otro espacio"
        # Ni se puede escribir una del otro espacio.
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("""insert into ofrecimiento_web (workspace_id, membership_id)
                           values (%s, %s)""",
                        (oeste["id"], _persona(intake_world, "Sam North", "west-studio")))
    conn.rollback()


# --- La vuelta atrás ------------------------------------------------------------------------

def test_el_rollback_de_la_0066_se_niega_si_hay_marcas_u_ofrecimientos(conn, intake_world):
    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0066_la_entrada_a_la_web_por_chat.sql").read_text("utf-8")
    guarda = re.findall(r"do \$\$.*?end \$\$;", script, re.S)[-1]
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        cur.execute("insert into ofrecimiento_web (workspace_id, membership_id) values (%s, %s)",
                    (ws, _persona(intake_world)))
    conn.commit()
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0066 rollback refused"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
        cur.execute("select count(*) n from ofrecimiento_web")
        assert cur.fetchone()["n"] == 1
