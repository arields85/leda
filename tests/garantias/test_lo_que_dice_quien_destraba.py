"""Lo que dice quien destraba (migración 0042; C-5, porción 1; decisión 4 del usuario).

La capa de garantías de `dicho_de_quien_destraba`, no la conversación: aislamiento entre espacios
(RLS forzado con su política, la fila de quién destraba y quien lo dijo, del mismo espacio), que
sólo se agrega y que siempre dice algo (para cuándo, que ya está o sus palabras).
"""

from __future__ import annotations

from datetime import date

import psycopg
import pytest

from leda.db import admin, espacio

from tests.garantias.test_motor_tablas import (AHORA, Espacio, _quien_destraba,  # noqa: F401
                                               espacios)

TABLA = "dicho_de_quien_destraba"


def _dicho(cur, e: Espacio, destraba: str, *, ws: str | None = None, quien: str | None = None,
           para_cuando: date | None = date(2026, 10, 6), ya_esta: bool = False,
           lo_que_dice: str | None = None) -> str:
    cur.execute(
        """insert into dicho_de_quien_destraba
             (workspace_id, blocker_unblocker_id, dicho_por_membership_id, para_cuando, ya_esta,
              lo_que_dice, at)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (ws or e.id, destraba, quien or e.referente, para_cuando, ya_esta, lo_que_dice, AHORA))
    return str(cur.fetchone()["id"])


def _cuantas(cur) -> int:
    cur.execute(f"select count(*) as n from {TABLA}")
    return cur.fetchone()["n"]


def test_tiene_espacio_obligatorio_y_rls_forzado_con_su_politica(conn):
    with admin(conn) as cur:
        cur.execute("""select relrowsecurity, relforcerowsecurity
                         from pg_class where oid = to_regclass(%s)""", (f"leda.{TABLA}",))
        fila = cur.fetchone()
        assert fila["relrowsecurity"] and fila["relforcerowsecurity"]
        cur.execute("select polname from pg_policy where polrelid = to_regclass(%s)",
                    (f"leda.{TABLA}",))
        assert [p["polname"] for p in cur.fetchall()] == ["aislamiento_espacio"]
        cur.execute("""select column_name, is_nullable, data_type, column_default
                         from information_schema.columns
                        where table_schema = 'leda' and table_name = %s""", (TABLA,))
        columnas = {c["column_name"]: c for c in cur.fetchall()}
    assert columnas["workspace_id"]["is_nullable"] == "NO"
    # Nada propio del transporte, y los momentos los pone el motor con su reloj.
    assert not {"chat_id", "callback_data"} & set(columnas)
    for nombre, c in columnas.items():
        if c["data_type"].startswith("timestamp") or c["data_type"] == "date":
            assert c["column_default"] is None, nombre


def test_un_espacio_no_ve_ni_escribe_lo_del_otro(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        destraba_oeste = _quien_destraba(cur, oeste, integrante=oeste.referente)
        _dicho(cur, oeste, destraba_oeste)
    conn.commit()

    with espacio(conn, norte.id) as cur:
        assert _cuantas(cur) == 0
        with pytest.raises((psycopg.errors.InsufficientPrivilege,
                            psycopg.errors.ForeignKeyViolation)), conn.transaction():
            _dicho(cur, oeste, destraba_oeste)
    with espacio(conn, oeste.id) as cur:
        assert _cuantas(cur) == 1


def test_las_referencias_tienen_que_ser_del_mismo_espacio(conn, espacios):
    norte, oeste = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        destraba_norte = _quien_destraba(cur, norte, integrante=norte.referente)
        destraba_oeste = _quien_destraba(cur, oeste, integrante=oeste.referente)
        # La fila de quién destraba de otro espacio, y quien lo dijo de otro espacio.
        for intento in (lambda: _dicho(cur, norte, destraba_oeste),
                        lambda: _dicho(cur, norte, destraba_norte, quien=oeste.referente)):
            with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
                intento()


def test_solo_se_agrega_y_siempre_dice_algo(conn, espacios):
    norte = espacios["north-lab"]
    with admin(conn) as cur:
        destraba = _quien_destraba(cur, norte, integrante=norte.referente)
    conn.commit()
    with espacio(conn, norte.id) as cur:
        _dicho(cur, norte, destraba)
        _dicho(cur, norte, destraba, para_cuando=None, ya_esta=True)
        _dicho(cur, norte, destraba, para_cuando=None, lo_que_dice="depende del proveedor")
        for valores in ({"para_cuando": None},
                        {"para_cuando": None, "lo_que_dice": "   "}):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                _dicho(cur, norte, destraba, **valores)
        assert _cuantas(cur) == 3
        for sql in (f"update {TABLA} set ya_esta = true", f"delete from {TABLA}"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(sql)
