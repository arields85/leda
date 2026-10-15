"""Cada espacio ve su propio nombre para una persona (J7-5b, migración 0085).

Lucas es «Lucas Pérez» en West Studio. Dirección de North Lab lo da de alta como «Lucas P.» y él
abre el enlace con el mismo Telegram: la membresía nueva queda unida a su cuenta (J7-5). El
nombre que se ve en un espacio es el de su membresía, nunca el de la cuenta (`app_user.nombre`,
uno por persona en toda Leda): North Lab ve «Lucas P.», West Studio sigue viendo «Lucas Pérez», y
nada de lo que ve North Lab dice «Lucas Pérez» (constitución §13).
"""

from __future__ import annotations

import contextlib
import json
from datetime import datetime, timedelta, timezone

import pytest

from leda import lectura
from leda.autoridad import identificar_en_espacio
from leda.db import admin, espacio
from leda.onboarding import activar, bienvenida, pendientes_de_activar
from tests.garantias.test_alta_del_equipo import (  # noqa: F401 -- `direccion` es fixture
    _alta,
    _bot,
    _emitir,
    _filas,
    _rol,
    direccion,
)
from tests.garantias.test_carga_de_tareas import _hash, sin_espacio
from tests.garantias.test_ver_el_equipo import (  # noqa: F401 -- `_referente_de_field` es autouse
    _referente_de_field,
    _sesion_del_equipo,
)

TELEGRAM_DE_LUCAS = 990555
AHORA = datetime(2026, 10, 14, 15, 0, tzinfo=timezone.utc)


def _dar_de_alta_y_conectar(conn, mundo: dict, slug: str, token: str, nombre: str) -> str:
    ws = mundo[slug]
    r = _alta(conn, "equipo", token, None, nombre=nombre, area_id=ws["areas"]["field"],
              rol_id=_rol(conn, ws["id"], "member"))
    assert r["ok"] is True, r
    membresia = str(r["membership_id"])
    _, enlace = _emitir(conn, "equipo", token, None, membresia)
    with admin(conn) as cur:
        nombre_canjeado = activar(cur, ws["id"], enlace, TELEGRAM_DE_LUCAS)
    conn.commit()
    assert nombre_canjeado == nombre
    return membresia


@pytest.fixture
def lucas(conn, intake_world, direccion) -> dict:
    """Lucas Pérez en West Studio y, unido a la misma cuenta, Lucas P. en North Lab."""
    oeste = intake_world["west-studio"]
    _bot(conn, oeste["id"])
    direccion_oeste = _sesion_del_equipo(conn, intake_world, "Morgan Hale", "west-studio")
    en_oeste = _dar_de_alta_y_conectar(conn, intake_world, "west-studio", direccion_oeste,
                                       "Lucas Pérez")
    en_norte = _dar_de_alta_y_conectar(conn, intake_world, "north-lab", direccion, "Lucas P.")
    return {"oeste": en_oeste, "norte": en_norte, "direccion_oeste": direccion_oeste}


@contextlib.contextmanager
def _como_la_web(conn, ws: str):
    """Como las funciones que la web llama dentro de otra elevada: con el dueño y el espacio
    de la transacción fijado (`test_quien_ve_que`)."""
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("set local role leda_owner")
        cur.execute("select set_config('leda.workspace_id', %s, true)", (ws,))
        yield cur


def _equipo(conn, token: str) -> dict:
    with sin_espacio(conn) as cur:
        cur.execute("select equipo_de('equipo', %s, null) as r", (_hash(token),))
        r = cur.fetchone()["r"]
    conn.commit()
    return r


def _nombre_en(equipo: dict, membership_id: str) -> str:
    (persona,) = [p for p in equipo["personas"] if p["membership_id"] == membership_id]
    return persona["nombre"]


def test_la_cuenta_es_una_y_cada_espacio_la_nombra_a_su_manera(conn, intake_world, direccion,
                                                               lucas):
    (uno, otro) = _filas(conn, """select app_user_id from membership where id in (%s, %s)""",
                         lucas["oeste"], lucas["norte"])
    assert uno["app_user_id"] == otro["app_user_id"]
    # Unirse no pisa el nombre de la cuenta ni le trae a North Lab el de West Studio.
    (cuenta,) = _filas(conn, "select nombre from app_user where telegram_user_id = %s",
                       TELEGRAM_DE_LUCAS)
    assert cuenta["nombre"] == "Lucas Pérez"
    (norte,) = _filas(conn, "select nombre from membership where id = %s", lucas["norte"])
    assert norte["nombre"] == "Lucas P."


def test_el_equipo_de_cada_espacio_muestra_su_nombre(conn, intake_world, direccion, lucas):
    norte = _equipo(conn, direccion)
    assert _nombre_en(norte, lucas["norte"]) == "Lucas P."
    assert "Lucas Pérez" not in json.dumps(norte, ensure_ascii=False)
    oeste = _equipo(conn, lucas["direccion_oeste"])
    assert _nombre_en(oeste, lucas["oeste"]) == "Lucas Pérez"
    assert "Lucas P.\"" not in json.dumps(oeste, ensure_ascii=False)


def test_la_cocina_del_motor_lo_nombra_como_su_espacio(conn, intake_world, direccion, lucas):
    norte, oeste = intake_world["north-lab"], intake_world["west-studio"]
    with espacio(conn, norte["id"]) as cur:
        quien = identificar_en_espacio(cur, TELEGRAM_DE_LUCAS, norte["id"])
        cur.execute("select nombre from integrante where membership_id = %s", (lucas["norte"],))
        vista = cur.fetchone()["nombre"]
        carga = lectura.carga_por_persona(cur)
    conn.commit()
    assert quien.nombre == "Lucas P." and vista == "Lucas P."
    assert "Lucas Pérez" not in {f["nombre"] for f in carga}
    assert "Lucas P." in {f["nombre"] for f in carga}
    with espacio(conn, oeste["id"]) as cur:
        assert identificar_en_espacio(cur, TELEGRAM_DE_LUCAS, oeste["id"]).nombre == (
            "Lucas Pérez")
    conn.commit()
    with admin(conn) as cur:
        assert bienvenida(cur, norte["id"], "Lucas P.").startswith("Listo, Lucas.")
    conn.commit()


def test_las_tareas_de_cada_espacio_lo_nombran_como_su_espacio(conn, intake_world, direccion,
                                                               lucas):
    norte = intake_world["north-lab"]
    with admin(conn) as cur:
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, fecha_objetivo,
                                 criterio_aceptacion, evidencia_requerida,
                                 pedida_por_membership_id)
               values (%s, %s, 'Calibrar el sensor', %s, %s, %s, 'Que ande', '{}', %s)
               returning id""",
            (norte["id"], norte["objectives"][0], norte["areas"]["field"], lucas["norte"],
             AHORA + timedelta(days=3), norte["people"]["Morgan Hale"]["membership_id"]))
        tarea = str(cur.fetchone()["id"])
        cur.execute("""insert into task_state_event (task_id, estado_nuevo, actor_kind, at)
                       values (%s, 'asignada', 'leda', %s)""", (tarea, AHORA))
    conn.commit()
    direccion_norte = norte["people"]["Morgan Hale"]["membership_id"]
    with _como_la_web(conn, norte["id"]) as cur:
        cur.execute("select * from tareas_que_ve(%s, 'equipo', %s)", (direccion_norte, AHORA))
        tareas = cur.fetchall()
        cur.execute("select * from pedidas_que_ve(%s, %s)", (direccion_norte, AHORA))
        pedidas = cur.fetchall()
    conn.commit()
    with espacio(conn, norte["id"]) as cur:
        vencidas = lectura.tareas_vencidas(cur, AHORA + timedelta(days=10))
    conn.commit()
    (fila,) = [t for t in tareas if str(t["task_id"]) == tarea]
    assert fila["responsable"] == "Lucas P."
    (pedida,) = [t for t in pedidas if str(t["task_id"]) == tarea]
    assert pedida["responsable"] == "Lucas P."
    (vencida,) = [t for t in vencidas if str(t["id"]) == tarea]
    assert vencida["nombre"] == "Lucas P."


def test_nada_de_lo_que_ve_el_otro_espacio_dice_el_nombre_de_este(conn, intake_world,
                                                                    direccion, lucas):
    norte = intake_world["north-lab"]
    vistos = []
    with sin_espacio(conn) as cur:
        for consulta, args in (
                ("select equipo_de('equipo', %s, null) as r", (_hash(direccion),)),
                ("select cambios_del_equipo('equipo', %s, null) as r", (_hash(direccion),)),
                ("select opciones_de_la_carga_del_equipo(%s, %s) as r", (_hash(direccion), AHORA)),
                ("select opciones_del_objetivo('equipo', %s, null, %s) as r",
                 (_hash(direccion), AHORA))):
            cur.execute(consulta, args)
            vistos.append(cur.fetchone()["r"])
    conn.commit()
    with _como_la_web(conn, norte["id"]) as cur:
        cur.execute("select problemas_del_equipo(%s) as r", (norte["id"],))
        vistos.append(cur.fetchone()["r"])
        cur.execute("select opciones_de_la_carga_en(%s, %s) as r", (norte["id"], AHORA))
        vistos.append(cur.fetchone()["r"])
    conn.commit()
    with admin(conn) as cur:
        vistos.append(pendientes_de_activar(cur, norte["id"]))
    conn.commit()
    texto = json.dumps(vistos, ensure_ascii=False, default=str)
    assert "Lucas Pérez" not in texto
    assert "Lucas P." in texto
