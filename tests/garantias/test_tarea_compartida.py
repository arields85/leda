"""Compartir el detalle de una tarea con alguien que no la ve (decisión 33 del usuario, 2026-10-09;
migración 0050): la capa de garantías.

El resumen de una tarea lo ve cualquiera del equipo; el detalle (la página: fotos, archivos,
correcciones pedidas) sólo quienes tienen que ver con ella (ADR 0019, 7b, igual). Compartirlo con
otra persona es nuevo y lo decide el encargado del sector de la tarea (el referente de su área).
Lo que se prueba acá es la base:

- **Aislamiento.** `pedido_de_detalle` y `tarea_compartida` tienen el espacio obligatorio y `row
  level security` forzado, y sus referencias van con el espacio: una tarea de un espacio no se
  comparte con alguien de otro, y lo compartido en un espacio no da nada en otro.
- **Quién comparte.** Sólo el encargado del sector de la tarea; nadie más, tampoco la autoridad
  final (no es quien decide el detalle de un área).
- **Lo compartido cuenta para ver** (`puede_ver_tarea`): la página y su enlace la honran, y cada
  vista queda registrada como cualquier otra (7e).
- **Revocable, nunca borrado.** Dejar de compartirla es lo único que cambia de la fila, una sola
  vez, por el encargado o por quien la compartió; desde ese momento deja de valer, también el
  enlace ya emitido. `leda_app` no borra nada.
"""

from __future__ import annotations

from datetime import datetime, timezone

import psycopg
import pytest

from leda.db import admin, espacio

from tests.garantias.test_pagina_de_la_tarea import (_emitir, _leer, _persona,  # noqa: F401
                                                     mundo)

AHORA = datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc)
NUEVAS = ("pedido_de_detalle", "tarea_compartida")
# Una referencia a otro espacio no se escribe: la frena la clave del mismo espacio o, antes,
# la regla de quién comparte, que busca la tarea en el espacio de la fila.
NO_SE_ESCRIBE = (psycopg.errors.ForeignKeyViolation, psycopg.errors.RaiseException)


@pytest.fixture
def con_encargado(conn, mundo):  # noqa: F811 -- la fixture de la página de la tarea
    """Taylor Quinn es el encargado de quality, el sector de la tarea de Sam Noble, en los dos
    espacios."""
    with admin(conn) as cur:
        for slug in ("north-lab", "west-studio"):
            cur.execute("update area set referente_membership_id = %s where id = %s",
                        (_persona(mundo, "Taylor Quinn", slug),
                         mundo[slug]["areas"]["quality"]))
    conn.commit()
    return mundo


def _compartir(conn, mundo, *, con: str = "Sam North", por: str = "Taylor Quinn",
               tarea: dict | None = None, slug: str = "north-lab") -> str:
    """La aplicación escribe que la tarea queda compartida, dentro del espacio."""
    tarea = tarea or mundo["norte"]
    with espacio(conn, mundo[slug]["id"]) as cur:
        cur.execute(
            """insert into tarea_compartida (workspace_id, task_id, membership_id,
                                             compartida_por_membership_id, at)
               values (%s, %s, %s, %s, %s) returning id""",
            (mundo[slug]["id"], tarea["id"], _persona(mundo, con, slug),
             _persona(mundo, por, slug), AHORA))
        compartida = str(cur.fetchone()["id"])
    conn.commit()
    return compartida


def _ve(conn, mundo, nombre: str, tarea: dict | None = None, slug: str = "north-lab") -> bool:
    tarea = tarea or mundo["norte"]
    with espacio(conn, mundo[slug]["id"]) as cur:
        cur.execute("select puede_ver_tarea(%s, %s) ve", (_persona(mundo, nombre, slug),
                                                          tarea["id"]))
        ve = cur.fetchone()["ve"]
    conn.commit()
    return ve


# --- Las tablas -----------------------------------------------------------------------------

def test_las_tablas_nuevas_tienen_espacio_obligatorio_y_rls_forzado(conn):
    with admin(conn) as cur:
        for tabla in NUEVAS:
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


def test_la_aplicacion_no_borra_lo_compartido_ni_los_pedidos(conn, con_encargado):
    _compartir(conn, con_encargado)
    with espacio(conn, con_encargado["north-lab"]["id"]) as cur:
        for tabla in NUEVAS:
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                cur.execute(f"delete from {tabla}")
    conn.commit()


def test_dentro_de_un_espacio_no_se_ve_lo_compartido_en_otro(conn, con_encargado):
    _compartir(conn, con_encargado)
    with espacio(conn, con_encargado["west-studio"]["id"]) as cur:
        cur.execute("select count(*) n from tarea_compartida")
        assert cur.fetchone()["n"] == 0
    conn.commit()


# --- Lo compartido cuenta para ver ------------------------------------------------------------

def test_compartida_por_el_encargado_la_ve_y_su_enlace_lee_la_pagina(conn, con_encargado):
    """Sam North es del equipo y no tiene nada que ver con la tarea: no la ve hasta que el
    encargado de quality se la comparte. Desde entonces su enlace lee la página, y la vista queda
    registrada como cualquier otra (7e)."""
    assert not _ve(conn, con_encargado, "Sam North")
    assert _emitir(conn, con_encargado, "Sam North") is None

    _compartir(conn, con_encargado)

    assert _ve(conn, con_encargado, "Sam North")
    token = _emitir(conn, con_encargado, "Sam North")
    datos = _leer(conn, token)
    assert datos is not None and datos["tarea"]["titulo"] == "Calibrar la balanza"
    with admin(conn) as cur:
        cur.execute("""select v.que from vista_de_tarea v
                         join acceso_tarea a on a.id = v.acceso_tarea_id
                        where a.membership_id = %s""",
                    (_persona(con_encargado, "Sam North"),))
        assert [v["que"] for v in cur.fetchall()] == ["pagina"]
    conn.commit()


def test_lo_compartido_en_un_espacio_no_da_nada_en_otro(conn, con_encargado):
    """La misma persona por nombre en el otro espacio es otra membresía: no ve la tarea de su
    espacio por lo compartido en éste."""
    _compartir(conn, con_encargado)
    assert not _ve(conn, con_encargado, "Sam North", con_encargado["oeste"], "west-studio")
    assert _emitir(conn, con_encargado, "Sam North", con_encargado["oeste"],
                   "west-studio") is None


def test_no_se_comparte_con_alguien_de_otro_espacio(conn, con_encargado):
    """Las referencias van con el espacio: la tarea de North Lab con una membresía de West
    Studio, o al revés, no se escriben."""
    norte, oeste = con_encargado["north-lab"], con_encargado["west-studio"]
    with admin(conn) as cur:
        with pytest.raises(NO_SE_ESCRIBE), conn.transaction():
            cur.execute(
                """insert into tarea_compartida (workspace_id, task_id, membership_id,
                                                 compartida_por_membership_id, at)
                   values (%s, %s, %s, %s, %s)""",
                (norte["id"], con_encargado["norte"]["id"],
                 _persona(con_encargado, "Sam North", "west-studio"),
                 _persona(con_encargado, "Taylor Quinn"), AHORA))
        with pytest.raises(NO_SE_ESCRIBE), conn.transaction():
            cur.execute(
                """insert into tarea_compartida (workspace_id, task_id, membership_id,
                                                 compartida_por_membership_id, at)
                   values (%s, %s, %s, %s, %s)""",
                (oeste["id"], con_encargado["norte"]["id"],
                 _persona(con_encargado, "Sam North", "west-studio"),
                 _persona(con_encargado, "Taylor Quinn", "west-studio"), AHORA))
    conn.commit()


# --- Quién comparte -------------------------------------------------------------------------

@pytest.mark.parametrize("por", ["Morgan Hale", "Sam Noble"])
def test_solo_la_comparte_el_encargado_del_sector_de_la_tarea(conn, con_encargado, por):
    """Ni la autoridad final ni quien la tiene: el detalle lo comparte el encargado del sector
    de la tarea (decisión 33)."""
    with pytest.raises(psycopg.errors.RaiseException):
        _compartir(conn, con_encargado, por=por)
    conn.rollback()
    assert not _ve(conn, con_encargado, "Sam North")


def test_sin_encargado_del_sector_nadie_la_comparte(conn, mundo):  # noqa: F811
    with pytest.raises(psycopg.errors.RaiseException):
        _compartir(conn, mundo)
    conn.rollback()


def test_compartida_una_sola_vez_mientras_vale(conn, con_encargado):
    _compartir(conn, con_encargado)
    with pytest.raises(psycopg.errors.UniqueViolation):
        _compartir(conn, con_encargado)
    conn.rollback()


def test_un_pedido_del_detalle_lo_decide_el_encargado_y_solo_avanza(conn, con_encargado):
    norte = con_encargado["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute(
                """insert into pedido_de_detalle (workspace_id, task_id, pedido_por_membership_id,
                                                  decide_membership_id, estado, pedido_en)
                   values (%s, %s, %s, %s, 'esperando_decision', %s)""",
                (norte["id"], con_encargado["norte"]["id"],
                 _persona(con_encargado, "Sam North"), _persona(con_encargado, "Morgan Hale"),
                 AHORA))
        cur.execute(
            """insert into pedido_de_detalle (workspace_id, task_id, pedido_por_membership_id,
                                              decide_membership_id, estado, pedido_en)
               values (%s, %s, %s, %s, 'esperando_decision', %s) returning id""",
            (norte["id"], con_encargado["norte"]["id"], _persona(con_encargado, "Sam North"),
             _persona(con_encargado, "Taylor Quinn"), AHORA))
        pedido = cur.fetchone()["id"]
        cur.execute("""update pedido_de_detalle set estado = 'no_compartida', decidido_en = %s,
                              decidido_por_membership_id = %s
                        where id = %s""", (AHORA, _persona(con_encargado, "Taylor Quinn"), pedido))
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("""update pedido_de_detalle set estado = 'compartida' where id = %s""",
                        (pedido,))
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("""update pedido_de_detalle set pedido_por_membership_id = %s
                            where id = %s""", (_persona(con_encargado, "Sam Noble"), pedido))
    conn.commit()


def _pedido(conn, mundo) -> str:
    norte = mundo["north-lab"]
    with espacio(conn, norte["id"]) as cur:
        cur.execute(
            """insert into pedido_de_detalle (workspace_id, task_id, pedido_por_membership_id,
                                              decide_membership_id, estado, pedido_en)
               values (%s, %s, %s, %s, 'esperando_decision', %s) returning id""",
            (norte["id"], mundo["norte"]["id"], _persona(mundo, "Sam North"),
             _persona(mundo, "Taylor Quinn"), AHORA))
        pedido = str(cur.fetchone()["id"])
    conn.commit()
    return pedido


def _otro_encargado(conn, mundo, nombre: str = "Morgan Hale") -> None:
    with admin(conn) as cur:
        cur.execute("update area set referente_membership_id = %s where id = %s",
                    (_persona(mundo, nombre), mundo["north-lab"]["areas"]["quality"]))
    conn.commit()


@pytest.mark.parametrize("estado", ["compartida", "no_compartida"])
def test_un_encargado_anterior_no_decide_el_pedido_ni_que_si_ni_que_no(conn, con_encargado,
                                                                       estado):
    """El pedido sigue al encargado de ahora (migración 0051; decisión 33 con la 43): si cambió
    el encargado del sector, quien lo era ya no decide, y el de ahora sí."""
    pedido = _pedido(conn, con_encargado)
    _otro_encargado(conn, con_encargado)
    with espacio(conn, con_encargado["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="encargado de ahora"), \
                conn.transaction():
            cur.execute("""update pedido_de_detalle set estado = %s, decidido_en = %s,
                                  decidido_por_membership_id = %s where id = %s""",
                        (estado, AHORA, _persona(con_encargado, "Taylor Quinn"), pedido))
        cur.execute("""update pedido_de_detalle set estado = %s, decidido_en = %s,
                              decidido_por_membership_id = %s where id = %s""",
                    (estado, AHORA, _persona(con_encargado, "Morgan Hale"), pedido))
    conn.commit()


def test_un_pedido_decidido_dice_quien_lo_decidio_y_uno_sin_respuesta_no(conn, con_encargado):
    pedido = _pedido(conn, con_encargado)
    with espacio(conn, con_encargado["north-lab"]["id"]) as cur:
        # Sin quién lo decidió no hay decisión: la frena la base (el disparador, antes que la
        # restricción).
        with pytest.raises((psycopg.errors.CheckViolation, psycopg.errors.RaiseException)),                 conn.transaction():
            cur.execute("""update pedido_de_detalle set estado = 'no_compartida',
                                  decidido_en = %s where id = %s""", (AHORA, pedido))
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            cur.execute("""update pedido_de_detalle set estado = 'sin_respuesta', decidido_en = %s,
                                  decidido_por_membership_id = %s where id = %s""",
                        (AHORA, _persona(con_encargado, "Taylor Quinn"), pedido))
        cur.execute("""update pedido_de_detalle set estado = 'sin_respuesta', decidido_en = %s
                        where id = %s""", (AHORA, pedido))
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("""update pedido_de_detalle set estado = 'esperando_decision',
                                  decidido_en = null where id = %s""", (pedido,))
    conn.commit()


def test_el_rollback_de_la_0051_se_niega_con_un_pedido_sin_respuesta(conn, con_encargado):
    """Deshacerla perdería cómo terminó un pedido (constitución §12). Se ejercita la guarda tal
    como está escrita en el archivo."""
    import re
    from pathlib import Path

    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0051_las_revisiones_de_la_c5d_y_del_detalle.sql").read_text("utf-8")
    guarda = re.findall(r"do \$\$.*?end \$\$;", script, re.S)[1]
    pedido = _pedido(conn, con_encargado)
    with espacio(conn, con_encargado["north-lab"]["id"]) as cur:
        cur.execute("""update pedido_de_detalle set estado = 'sin_respuesta', decidido_en = %s
                        where id = %s""", (AHORA, pedido))
    conn.commit()
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0051 se niega"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
    conn.rollback()


# --- Revocable, nunca borrado -----------------------------------------------------------------

def test_dejar_de_compartirla_corta_el_acceso_y_el_enlace_ya_emitido(conn, con_encargado):
    compartida = _compartir(conn, con_encargado)
    token = _emitir(conn, con_encargado, "Sam North")
    assert _leer(conn, token) is not None

    with espacio(conn, con_encargado["north-lab"]["id"]) as cur:
        cur.execute("""update tarea_compartida set revocada_en = %s,
                              revocada_por_membership_id = %s
                        where id = %s""",
                    (AHORA, _persona(con_encargado, "Taylor Quinn"), compartida))
    conn.commit()

    assert not _ve(conn, con_encargado, "Sam North")
    assert _leer(conn, token) is None
    assert _emitir(conn, con_encargado, "Sam North") is None
    # Se puede volver a compartir: otra fila, con su propia fecha.
    _compartir(conn, con_encargado)
    assert _ve(conn, con_encargado, "Sam North")


def test_lo_compartido_solo_cambia_para_revocarse_una_vez(conn, con_encargado):
    compartida = _compartir(conn, con_encargado)
    taylor = _persona(con_encargado, "Taylor Quinn")
    with espacio(conn, con_encargado["north-lab"]["id"]) as cur:
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("update tarea_compartida set membership_id = %s where id = %s",
                        (_persona(con_encargado, "Sam Noble"), compartida))
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            # Revocarla no es de cualquiera: ni de la autoridad final.
            cur.execute("""update tarea_compartida set revocada_en = %s,
                                  revocada_por_membership_id = %s where id = %s""",
                        (AHORA, _persona(con_encargado, "Morgan Hale"), compartida))
        cur.execute("""update tarea_compartida set revocada_en = %s,
                              revocada_por_membership_id = %s where id = %s""",
                    (AHORA, taylor, compartida))
        with pytest.raises(psycopg.errors.RaiseException), conn.transaction():
            cur.execute("""update tarea_compartida set revocada_en = null,
                                  revocada_por_membership_id = null where id = %s""",
                        (compartida,))
    conn.commit()


def test_el_rollback_de_la_0050_se_niega_con_algo_compartido(conn, con_encargado):
    """Deshacerla borraría quién compartió qué con quién, que es auditoría (constitución §12).
    Se ejercita la guarda tal como está escrita en el archivo."""
    import re
    from pathlib import Path

    script = (Path(__file__).resolve().parents[2] / "db" / "rollbacks"
              / "0050_el_detalle_de_una_tarea.sql").read_text("utf-8")
    guarda = re.search(r"do \$\$.*?end \$\$;", script, re.S).group(0)
    _compartir(conn, con_encargado)
    with admin(conn) as cur:
        with pytest.raises(psycopg.errors.RaiseException, match="0050 se niega"), \
                conn.transaction():
            cur.execute("set local search_path = leda, public")
            cur.execute(guarda)
    conn.rollback()
