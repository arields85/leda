"""La tabla de los apodos (migración 0055; ADR 0020, decisiones 6 y 8).

La capa de garantías de `apodo`, no la conversación: el apodo es del espacio y nunca de otro
(RLS forzado, la persona del apodo del mismo espacio), nace vigente, lo aprendido no cambia, se
deja de usar una vez y nunca se borra, y quien lo enseñó, cuándo y por qué canal son obligatorios.
"""

from __future__ import annotations

from datetime import datetime, timezone

import psycopg
import pytest

from leda.db import admin, espacio

AHORA = datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc)


def _apodo(cur, w: dict, *, de: str = "Sam North", ensena: str = "Taylor Quinn",
           apodo: str = "el tano", canal: str = "chat", ws: str | None = None) -> str:
    cur.execute(
        """insert into apodo (workspace_id, membership_id, apodo, ensenado_por_app_user_id,
                              canal, at)
           values (%s, %s, %s, %s, %s, %s) returning id""",
        (ws or w["id"], w["people"][de]["membership_id"], apodo,
         w["people"][ensena]["app_user_id"], canal, AHORA))
    return str(cur.fetchone()["id"])


def _cuantos(cur) -> int:
    cur.execute("select count(*) n from apodo")
    return cur.fetchone()["n"]


def test_la_tabla_tiene_espacio_obligatorio_rls_forzado_y_nada_del_transporte(conn):
    with admin(conn) as cur:
        cur.execute("""select relrowsecurity, relforcerowsecurity from pg_class
                        where oid = to_regclass('leda.apodo')""")
        fila = cur.fetchone()
        assert fila["relrowsecurity"] and fila["relforcerowsecurity"]
        cur.execute("select polname from pg_policy where polrelid = to_regclass('leda.apodo')")
        assert [p["polname"] for p in cur.fetchall()] == ["aislamiento_espacio"]
        cur.execute("""select column_name, is_nullable, data_type, column_default
                         from information_schema.columns
                        where table_schema = 'leda' and table_name = 'apodo'""")
        columnas = {c["column_name"]: c for c in cur.fetchall()}
    assert columnas["workspace_id"]["is_nullable"] == "NO"
    for obligatoria in ("membership_id", "apodo", "ensenado_por_app_user_id", "canal", "at"):
        assert columnas[obligatoria]["is_nullable"] == "NO", obligatoria
    assert not {"chat_id", "callback_data"} & set(columnas)
    for nombre, c in columnas.items():
        if c["data_type"].startswith("timestamp"):
            assert c["column_default"] is None, nombre


def test_un_espacio_no_ve_ni_escribe_los_apodos_de_otro(conn, intake_world):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    with admin(conn) as cur:
        _apodo(cur, oeste)
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        assert _cuantos(cur) == 0
        cur.execute("""select count(*) n from apodo a
                         join integrante i on i.membership_id = a.membership_id""")
        assert cur.fetchone()["n"] == 0
    with espacio(conn, norte["id"]) as cur:
        # Lo rechaza la política o, antes, la referencia a una persona que para este espacio
        # no existe.
        with pytest.raises((psycopg.errors.InsufficientPrivilege,
                            psycopg.errors.ForeignKeyViolation)), conn.transaction():
            _apodo(cur, oeste, apodo="el chino")
        cur.execute("update apodo set borrado_en = %s", (AHORA,))
        assert cur.rowcount == 0
    with espacio(conn, oeste["id"]) as cur:
        assert _cuantos(cur) == 1


def test_la_persona_del_apodo_es_del_mismo_espacio(conn, intake_world):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _apodo(cur, oeste, ws=norte["id"])


def test_leda_app_lo_aprende_y_lo_deja_de_usar_pero_no_lo_borra(conn, intake_world):
    norte = intake_world["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        apodo = _apodo(cur, norte)
    conn.commit()
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("delete from apodo where id = %s", (apodo,))
        cur.execute("""update apodo set borrado_en = %s, borrado_por_app_user_id = %s
                        where id = %s""",
                    (AHORA, norte["people"]["Morgan Hale"]["app_user_id"], apodo))
        assert cur.rowcount == 1
    conn.commit()


def test_lo_aprendido_no_cambia_y_se_deja_de_usar_una_sola_vez(conn, intake_world):
    norte = intake_world["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        apodo = _apodo(cur, norte)
    conn.commit()
    with espacio(conn, norte["id"]) as cur:
        for cambio in ("apodo = 'el chino'", "canal = 'plataforma'",
                       f"membership_id = '{norte['people']['Sam Noble']['membership_id']}'"):
            with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
                cur.execute(f"update apodo set {cambio} where id = %s", (apodo,))
        # Dejarlo de usar pide quién y cuándo, las dos cosas.
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("update apodo set borrado_en = %s where id = %s", (AHORA, apodo))
        cur.execute("""update apodo set borrado_en = %s, borrado_por_app_user_id = %s
                        where id = %s""",
                    (AHORA, norte["people"]["Morgan Hale"]["app_user_id"], apodo))
    conn.commit()
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("update apodo set borrado_en = null, borrado_por_app_user_id = null "
                        "where id = %s", (apodo,))


def test_nace_vigente_con_su_canal_y_uno_vigente_por_persona_y_apodo(conn, intake_world):
    norte = intake_world["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _apodo(cur, norte, canal="telegram")
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _apodo(cur, norte, apodo=" el  tano ")
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute(
                """insert into apodo (workspace_id, membership_id, apodo,
                                      ensenado_por_app_user_id, canal, at, borrado_en,
                                      borrado_por_app_user_id)
                   values (%s, %s, 'el tano', %s, 'chat', %s, %s, %s)""",
                (norte["id"], norte["people"]["Sam North"]["membership_id"],
                 norte["people"]["Taylor Quinn"]["app_user_id"], AHORA, AHORA,
                 norte["people"]["Taylor Quinn"]["app_user_id"]))
        _apodo(cur, norte)
        with pytest.raises(psycopg.errors.UniqueViolation), conn.transaction():
            _apodo(cur, norte, ensena="Morgan Hale", canal="plataforma")
        # El mismo apodo puede ser de otra persona.
        _apodo(cur, norte, de="Sam Noble")
        assert _cuantos(cur) == 2
    conn.commit()
