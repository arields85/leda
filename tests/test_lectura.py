"""El puerto de lectura: que no cruce de espacio y que además acierte.

Las dos caras importan por igual. Seis funciones que devolvieran siempre lista
vacía pasarían una prueba de aislamiento perfecta, así que cada consulta se
comprueba también contra datos conocidos.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from prisma.db import admin, espacio
from prisma.lectura import (avance_de_objetivos, bloqueos_abiertos,
                            carga_por_persona, tareas_por_estado,
                            tareas_vencidas, trabajo_esperando_aprobacion)

AHORA = datetime(2028, 3, 15, 12, 0, tzinfo=timezone.utc)


def _tarea(cur, mundo, slug, *, titulo, estado, persona="Taylor Quinn",
           objetivo=0, vence=None):
    espacio_ = mundo[slug]
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, estado, fecha_objetivo)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (espacio_["id"], espacio_["objectives"][objetivo], titulo,
         espacio_["areas"]["field"], espacio_["people"][persona]["membership_id"],
         estado, vence))
    return cur.fetchone()["id"]


def _bloqueo(cur, mundo, slug, task_id, causa, *, abierto, resuelto=None):
    espacio_ = mundo[slug]
    cur.execute(
        """insert into blocker (workspace_id, task_id, causa, abierto_en,
                                resuelto_en, abierto_por)
           values (%s, %s, %s, %s, %s, %s)""",
        (espacio_["id"], task_id, causa, abierto, resuelto,
         espacio_["people"]["Taylor Quinn"]["membership_id"]))


def _sembrar_ambos(conn, mundo):
    """Datos distintos y reconocibles en cada espacio."""
    with admin(conn) as cur:
        norte = _tarea(cur, mundo, "north-lab", titulo="Norte en curso",
                       estado="en_curso")
        _tarea(cur, mundo, "north-lab", titulo="Norte terminada",
               estado="terminada")
        _tarea(cur, mundo, "north-lab", titulo="Norte vencida",
               estado="asignada", vence=AHORA - timedelta(days=4))
        _tarea(cur, mundo, "north-lab", titulo="Norte en revisión",
               estado="en_revision", persona="Morgan Hale")
        _bloqueo(cur, mundo, "north-lab", norte, "Norte trabada",
                 abierto=AHORA - timedelta(days=3))
        _bloqueo(cur, mundo, "north-lab", norte, "Norte ya resuelta",
                 abierto=AHORA - timedelta(days=9),
                 resuelto=AHORA - timedelta(days=1))

        oeste = _tarea(cur, mundo, "west-studio", titulo="Oeste en curso",
                       estado="en_curso")
        _tarea(cur, mundo, "west-studio", titulo="Oeste vencida",
               estado="asignada", vence=AHORA - timedelta(days=30))
        _tarea(cur, mundo, "west-studio", titulo="Oeste en revisión",
               estado="en_revision")
        _bloqueo(cur, mundo, "west-studio", oeste, "Oeste trabada",
                 abierto=AHORA - timedelta(days=2))
    conn.commit()


def test_ninguna_consulta_devuelve_datos_de_otro_espacio(intake_world, conn):
    _sembrar_ambos(conn, intake_world)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        leido = {
            "objetivos": avance_de_objetivos(cur),
            "estados": tareas_por_estado(cur),
            "carga": carga_por_persona(cur),
            "vencidas": tareas_vencidas(cur, AHORA),
            "bloqueos": bloqueos_abiertos(cur, AHORA),
            "aprobacion": trabajo_esperando_aprobacion(cur),
        }

    texto = repr(leido)
    assert "Oeste" not in texto, (
        f"una consulta devolvió tareas del otro espacio:\n{texto}")
    # Los nombres también: `carga_por_persona` cruza la vista `integrante`,
    # que es otra vía por la que se podría escapar gente ajena.
    for quien in intake_world["west-studio"]["people"].values():
        assert quien["name"] not in texto, (
            f"apareció {quien['name']}, que es del otro espacio")

    # Y no por estar todo vacío: el espacio propio sí aparece.
    assert "Norte" in texto
    assert sum(f["tareas"] for f in leido["estados"]) == 4


def test_avance_de_objetivos_cuenta_terminadas_e_incluye_los_vacios(
        intake_world, conn):
    _sembrar_ambos(conn, intake_world)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        por_id = {str(f["id"]): f for f in avance_de_objetivos(cur)}

    objetivos = intake_world["north-lab"]["objectives"]
    assert len(por_id) == len(objetivos), "faltan objetivos del espacio"

    con_trabajo = por_id[str(objetivos[0])]
    assert con_trabajo["tareas"] == 4
    assert con_trabajo["terminadas"] == 1

    # Un objetivo sin tareas es información, no una fila que se omite.
    vacio = por_id[str(objetivos[1])]
    assert vacio["tareas"] == 0
    assert vacio["terminadas"] == 0


def test_tareas_por_estado_cuenta_exacto(intake_world, conn):
    _sembrar_ambos(conn, intake_world)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        conteo = {f["estado"]: f["tareas"] for f in tareas_por_estado(cur)}

    assert conteo == {"en_curso": 1, "terminada": 1, "asignada": 1,
                      "en_revision": 1}


def test_carga_por_persona_solo_cuenta_trabajo_activo(intake_world, conn):
    _sembrar_ambos(conn, intake_world)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        carga = {f["nombre"]: f["activas"] for f in carga_por_persona(cur)}

    gente = intake_world["north-lab"]["people"]
    # Taylor tiene tres tareas, pero una está terminada y no pesa.
    assert carga[gente["Taylor Quinn"]["name"]] == 2
    assert carga[gente["Morgan Hale"]["name"]] == 1
    # Quien no tiene trabajo aparece en cero, no desaparece del tablero.
    assert all(cantidad >= 0 for cantidad in carga.values())
    assert min(carga.values()) == 0


def test_tareas_vencidas_solo_las_abiertas_con_fecha_pasada(intake_world, conn):
    _sembrar_ambos(conn, intake_world)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        vencidas = tareas_vencidas(cur, AHORA)

    assert [f["titulo"] for f in vencidas] == ["Norte vencida"]
    assert vencidas[0]["dias_vencida"] == 4
    assert vencidas[0]["nombre"] == (
        intake_world["north-lab"]["people"]["Taylor Quinn"]["name"])


def test_bloqueos_abiertos_excluye_los_resueltos_y_mide_antiguedad(
        intake_world, conn):
    _sembrar_ambos(conn, intake_world)

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        bloqueos = bloqueos_abiertos(cur, AHORA)

    assert [f["causa"] for f in bloqueos] == ["Norte trabada"]
    assert bloqueos[0]["dias"] == 3
    assert bloqueos[0]["titulo"] == "Norte en curso"


def test_trabajo_esperando_aprobacion_toma_tareas_y_objetivos(
        intake_world, conn):
    _sembrar_ambos(conn, intake_world)
    objetivo = intake_world["north-lab"]["objectives"][2]
    with admin(conn) as cur:
        cur.execute(
            """insert into objective_state_event
                 (objective_id, estado_anterior, estado_nuevo, actor_kind)
               values (%s, 'activo', 'completo_pendiente_aprobacion',
                       'sistema')""",
            (objetivo,))
    conn.commit()

    with espacio(conn, intake_world["north-lab"]["id"]) as cur:
        esperando = trabajo_esperando_aprobacion(cur)

    porsujeto = {f["sujeto_tipo"]: f for f in esperando}
    assert set(porsujeto) == {"tarea", "objetivo"}
    assert porsujeto["tarea"]["titulo"] == "Norte en revisión"
    assert porsujeto["tarea"]["responsable"] == (
        intake_world["north-lab"]["people"]["Morgan Hale"]["name"])
    assert str(porsujeto["objetivo"]["sujeto_id"]) == str(objetivo)
