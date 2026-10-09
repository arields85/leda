"""Con qué bloqueo suyo está trabado quien destraba (migración 0044; C-5, porción 4; decisión 6
del usuario, bloqueos encadenados).

La capa de garantías de la columna nueva de `dicho_de_quien_destraba`, no la conversación: quien
destraba puede decir que no puede porque está trabado con algo suyo; el bloqueo que nombra es del
mismo espacio, eso alcanza solo como algo dicho, y la tabla sigue siendo sólo para agregar.
"""

from __future__ import annotations

import psycopg
import pytest

from leda.db import admin, espacio

from tests.garantias.test_motor_tablas import (AHORA, Espacio, _quien_destraba,  # noqa: F401
                                               espacios)


def _dicho(cur, e: Espacio, destraba: str, bloqueo: str | None, **valores) -> None:
    cur.execute(
        """insert into dicho_de_quien_destraba
             (workspace_id, blocker_unblocker_id, dicho_por_membership_id, lo_que_dice,
              espera_su_bloqueo_id, at)
           values (%s, %s, %s, %s, %s, %s)""",
        (e.id, destraba, e.referente, valores.get("lo_que_dice"), bloqueo, AHORA))


def test_la_columna_existe_y_puede_quedar_vacia(conn):
    with admin(conn) as cur:
        cur.execute("""select is_nullable, data_type from information_schema.columns
                        where table_schema = 'leda' and table_name = 'dicho_de_quien_destraba'
                          and column_name = 'espera_su_bloqueo_id'""")
        columna = cur.fetchone()
    assert columna == {"is_nullable": "YES", "data_type": "uuid"}


def test_el_bloqueo_que_nombra_alcanza_solo_y_es_del_mismo_espacio(conn, espacios):
    norte, sur = espacios["north-lab"], espacios["west-studio"]
    with admin(conn) as cur:
        destraba = _quien_destraba(cur, norte, integrante=norte.referente)
    conn.commit()
    with espacio(conn, norte.id) as cur:
        _dicho(cur, norte, destraba, norte.bloqueo)
        # Sin nada dicho no hay fila (la restricción de la 0042 sigue).
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            _dicho(cur, norte, destraba, None)
        # Un bloqueo de otro espacio no se puede nombrar.
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            _dicho(cur, norte, destraba, sur.bloqueo)
        cur.execute("select count(*) as n from dicho_de_quien_destraba")
        assert cur.fetchone()["n"] == 1
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            cur.execute("update dicho_de_quien_destraba set espera_su_bloqueo_id = null")
