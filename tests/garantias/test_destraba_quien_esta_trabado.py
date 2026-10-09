"""El bloqueo lo da por destrabado quien está trabado (decisión 41 del usuario, 2026-10-09; C-5d).

La capa de garantías de `resolver_bloqueo`, no la conversación: un bloqueo lo cierra la persona
trabada (quien tiene la tarea, o quien lo anotó), nunca a quien se le informó que seguía abierto
(`blocker.escalado_a`, el bloqueo viejo). Si esa persona dice "ya está, llega mañana", Leda lo
anota y se lo cuenta a la persona trabada (`tests/motor/test_bloqueo_viejo.py`), pero el bloqueo
sigue abierto hasta que la persona trabada diga que pudo seguir. Ni la vista previa ni la
ejecución lo dejan pasar.
"""

from __future__ import annotations

import pytest

from leda import herramientas as H
from leda.autoridad import Denegado
from leda.db import admin, espacio

from tests.garantias.test_vista_previa_confirmacion import _bloquear, _quien, _tarea


def _membership(cur, ws, nombre):
    cur.execute(
        """select m.id from membership m join app_user u on u.id = m.app_user_id
            where m.workspace_id = %s and u.nombre = %s""", (ws, nombre))
    return cur.fetchone()["id"]


def _bloqueo_informado_a_ismael(conn, ws) -> tuple[str, str]:
    """La tarea de Marcos, trabada, con el bloqueo viejo ya informado a Ismael."""
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
        bid = _bloquear(cur, ws, tid)
        cur.execute("update blocker set escalado_a = %s, escalado_en = now() where id = %s",
                    (_membership(cur, ws, "Ismael Soschinski"), bid))
    conn.commit()
    return tid, bid


@pytest.mark.parametrize("ya_confirmada", [False, True])
def test_a_quien_se_le_informo_el_bloqueo_no_lo_puede_cerrar(corework, conn, ya_confirmada):
    ws = corework.workspace_id
    _tid, bid = _bloqueo_informado_a_ismael(conn, ws)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        with pytest.raises(Denegado):
            H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "ya está, llega mañana"},
                       ya_confirmada=ya_confirmada)
    conn.rollback()

    with admin(conn) as cur:
        cur.execute("select resuelto_en from blocker where id = %s", (bid,))
        assert cur.fetchone()["resuelto_en"] is None


def test_la_persona_trabada_si_lo_puede_cerrar_aunque_se_haya_informado(corework, conn):
    ws = corework.workspace_id
    tid, bid = _bloqueo_informado_a_ismael(conn, ws)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        r = H.ejecutar(cur, quien, "resolver_bloqueo",
                       {"bloqueo_id": bid, "resolucion": "llegó, sigo"}, ya_confirmada=True)
    conn.commit()

    assert r["resuelto"] is True
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"
