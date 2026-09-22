"""La credencial del tablero: las cinco propiedades del modelo de amenaza.

Un enlace que abre los datos de un cliente es una credencial, y se prueba como
tal. Cada prueba de acá abajo corresponde a una fila de la tabla de amenazas de
`odd/tasks/acceso-al-tablero.md`.
"""

from __future__ import annotations

import contextlib
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from prisma import tablero
from prisma.db import admin, espacio
from prisma.lectura import tareas_por_estado

AHORA = datetime(2028, 3, 15, 12, 0, tzinfo=timezone.utc)


@contextlib.contextmanager
def sin_espacio(conn):
    """La aplicación antes de saber a qué espacio pertenece el pedido.

    Es la situación real de una petición HTTP: llega un token y todavía no hay
    ningún espacio fijado. Resolverlo es justamente lo que lo averigua.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("set local role prisma_app")
            yield cur


def _emitir(conn, mundo, slug, persona="Taylor Quinn", ahora=AHORA):
    with espacio(conn, mundo[slug]["id"]) as cur:
        token = tablero.emitir(
            cur, mundo[slug]["people"][persona]["membership_id"], ahora)
    conn.commit()
    return token


def test_un_token_recien_emitido_resuelve_a_su_espacio_y_su_membresia(
        intake_world, conn):
    norte = intake_world["north-lab"]
    token = _emitir(conn, intake_world, "north-lab")

    with sin_espacio(conn) as cur:
        resuelto = tablero.resolver(cur, token)

    assert resuelto is not None
    assert resuelto["workspace_id"] == str(norte["id"])
    assert resuelto["membership_id"] == str(
        norte["people"]["Taylor Quinn"]["membership_id"])


def test_un_token_vencido_no_resuelve(intake_world, conn):
    """Vence: la ventana acota el reenvío, no lo evita."""
    hace_rato = datetime.now(timezone.utc) - timedelta(hours=2)
    token = _emitir(conn, intake_world, "north-lab", ahora=hace_rato)

    with sin_espacio(conn) as cur:
        assert tablero.resolver(cur, token) is None


def test_el_token_en_claro_no_queda_en_la_base(intake_world, conn):
    """Si se filtrara la base, los enlaces emitidos no tendrían que servir."""
    token = _emitir(conn, intake_world, "north-lab")

    with admin(conn) as cur:
        cur.execute("select * from acceso_tablero")
        filas = cur.fetchall()

    assert filas, "no se guardó ningún acceso"
    for fila in filas:
        for columna, valor in fila.items():
            assert token not in str(valor), (
                f"el token en claro apareció en la columna {columna}")


def test_una_membresia_dada_de_baja_pierde_el_acceso(intake_world, conn):
    """La autoridad se revalida en cada pedido, no sólo al emitir."""
    norte = intake_world["north-lab"]
    token = _emitir(conn, intake_world, "north-lab")

    with sin_espacio(conn) as cur:
        assert tablero.resolver(cur, token) is not None

    with admin(conn) as cur:
        cur.execute("update membership set activo = false where id = %s",
                    (norte["people"]["Taylor Quinn"]["membership_id"],))
    conn.commit()

    with sin_espacio(conn) as cur:
        assert tablero.resolver(cur, token) is None


def test_un_token_no_alcanza_los_datos_de_otro_espacio(intake_world, conn):
    """El espacio sale del token, así que no hay nada que cambiar en la URL."""
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]

    with admin(conn) as cur:
        for slug, titulo in (("north-lab", "Trabajo del norte"),
                             ("west-studio", "Trabajo del oeste")):
            mundo = intake_world[slug]
            cur.execute(
                """insert into task (workspace_id, objective_id, titulo,
                                     area_id, responsable_membership_id, estado)
                   values (%s, %s, %s, %s, %s, 'asignada')""",
                (mundo["id"], mundo["objectives"][0], titulo,
                 mundo["areas"]["field"],
                 mundo["people"]["Taylor Quinn"]["membership_id"]))
    conn.commit()

    token = _emitir(conn, intake_world, "north-lab")
    with sin_espacio(conn) as cur:
        resuelto = tablero.resolver(cur, token)
    assert resuelto["workspace_id"] == str(norte["id"])
    assert resuelto["workspace_id"] != str(oeste["id"])

    # Leer con ese espacio trae lo propio y nada de lo ajeno.
    with espacio(conn, resuelto["workspace_id"]) as cur:
        cur.execute("select titulo from task")
        titulos = {fila["titulo"] for fila in cur.fetchall()}
        assert titulos == {"Trabajo del norte"}
        assert sum(f["tareas"] for f in tareas_por_estado(cur)) == 1


def test_la_aplicacion_no_puede_leer_la_tabla_ni_emitir_para_otro_espacio(
        intake_world, conn):
    """La tabla no tiene política: lo que la protege es que nadie la consulta."""
    norte = intake_world["north-lab"]
    oeste = intake_world["west-studio"]

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), \
                conn.transaction():
            cur.execute("select * from acceso_tablero")

    with espacio(conn, norte["id"]) as cur:
        with pytest.raises(psycopg.Error), conn.transaction():
            tablero.emitir(
                cur, oeste["people"]["Taylor Quinn"]["membership_id"], AHORA)


def test_la_vigencia_es_configuracion_del_cliente(intake_world, conn):
    """Un administrador la cambia sin tocar código ni migrar nada."""
    norte = intake_world["north-lab"]

    with espacio(conn, norte["id"]) as cur:
        assert tablero.minutos_de_vigencia(cur) == tablero.MINUTOS_POR_DEFECTO

    with admin(conn) as cur:
        cur.execute(
            """insert into workspace_setting (workspace_id, clave, valor)
               values (%s, %s, %s)""",
            (norte["id"], tablero.CLAVE_VIGENCIA, "120"))
    conn.commit()

    with espacio(conn, norte["id"]) as cur:
        assert tablero.minutos_de_vigencia(cur) == 120
