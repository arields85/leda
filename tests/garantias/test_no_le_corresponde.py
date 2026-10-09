"""Que no le corresponde, dicho por quien destraba (migración 0043; C-5, porción 3; decisión 5 del
usuario).

La capa de garantías de la columna nueva de `dicho_de_quien_destraba`, no la conversación: "no me
corresponde" es algo que se dice (alcanza solo, sin fecha ni palabras), nunca junto con para
cuándo lo resuelve ni con que ya está, y la tabla sigue siendo sólo para agregar.
"""

from __future__ import annotations

from datetime import date

import psycopg
import pytest

from leda.db import admin, espacio

from tests.garantias.test_motor_tablas import (AHORA, Espacio, _quien_destraba,  # noqa: F401
                                               espacios)


def _dicho(cur, e: Espacio, destraba: str, **valores) -> None:
    fila = {"para_cuando": None, "ya_esta": False, "lo_que_dice": None,
            "no_le_corresponde": False, **valores}
    cur.execute(
        """insert into dicho_de_quien_destraba
             (workspace_id, blocker_unblocker_id, dicho_por_membership_id, para_cuando, ya_esta,
              lo_que_dice, no_le_corresponde, at)
           values (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (e.id, destraba, e.referente, fila["para_cuando"], fila["ya_esta"], fila["lo_que_dice"],
         fila["no_le_corresponde"], AHORA))


def test_la_columna_existe_no_es_nula_y_vale_falso_por_omision(conn):
    with admin(conn) as cur:
        cur.execute("""select is_nullable, column_default from information_schema.columns
                        where table_schema = 'leda' and table_name = 'dicho_de_quien_destraba'
                          and column_name = 'no_le_corresponde'""")
        columna = cur.fetchone()
    assert columna == {"is_nullable": "NO", "column_default": "false"}


def test_no_le_corresponde_alcanza_solo_y_nunca_va_con_una_fecha_ni_con_ya_esta(conn,
                                                                                espacios):
    norte = espacios["north-lab"]
    with admin(conn) as cur:
        destraba = _quien_destraba(cur, norte, integrante=norte.referente)
    conn.commit()
    with espacio(conn, norte.id) as cur:
        _dicho(cur, norte, destraba, no_le_corresponde=True)
        _dicho(cur, norte, destraba, no_le_corresponde=True, lo_que_dice="eso es de pedro")
        for valores in ({"no_le_corresponde": True, "para_cuando": date(2026, 10, 6)},
                        {"no_le_corresponde": True, "ya_esta": True},
                        {}):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                _dicho(cur, norte, destraba, **valores)
        cur.execute("select count(*) as n from dicho_de_quien_destraba")
        assert cur.fetchone()["n"] == 2
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("update dicho_de_quien_destraba set no_le_corresponde = false")
