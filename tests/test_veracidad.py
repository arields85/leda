"""Pruebas de que Prisma no diga que hizo algo que no hizo.

El resto del sistema ya impide que el modelo *haga* lo que no debe: la
autoridad se verifica en el servidor y las reglas de cierre viven en la base.
Lo que queda sin cubrir es lo que *dice*. Una acción puede quedar esperando
correctamente y el modelo contestar "listo, ya está" en la misma vuelta.

La defensa no es pedirle al modelo que no lo haga —eso ya está escrito en el
preámbulo y un modelo se distrae— sino no darle el lugar. Cuando hay algo
esperando a la persona, el texto que sale lo pone el sistema.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from prisma.agente import responder
from prisma.autoridad import Canal, identificar
from prisma.calendario import Calendario
from prisma.db import admin, espacio
from prisma.llm import Llamada, ProveedorGuionado, Respuesta
from prisma.salida import NO_EFFECT_STATUS

BA = ZoneInfo("America/Argentina/Buenos_Aires")
AHORA = datetime(2026, 7, 27, 10, 0, tzinfo=BA)


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _tarea(cur, ws):
    cur.execute(
        """insert into objective (workspace_id, tipo, titulo)
           values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
        (ws,))
    obj = cur.fetchone()["id"]
    cur.execute("set local role prisma_admin")
    # Por `membership`/`app_user` directo y no por la vista `integrante`: esa
    # vista filtra por `prisma.workspace_id` (`db/esquema.sql`), que sólo
    # pone `db.espacio` -- bajo `admin` queda sin definir, la vista no
    # devuelve nada y la subconsulta original resolvía en null. Con el
    # chequeo de autoridad de T2b (`herramientas._preparar_actualizar_estado`)
    # eso dejó de ser invisible: `responsable_membership_id` null nunca
    # coincide con quien llama, así que la corrección es necesaria, no sólo
    # prolija (revisión del orquestador sobre `0814fa3`).
    cur.execute(
        """insert into task (workspace_id, objective_id, titulo, area_id,
                             responsable_membership_id, fecha_objetivo,
                             criterio_aceptacion, evidencia_requerida)
           values (%s, %s, 'Programar PLC',
                   (select id from area where workspace_id = %s and slug = 'ot'),
                   (select m.id from membership m join app_user u on u.id = m.app_user_id
                     where m.workspace_id = %s and u.nombre = 'Marcos Tarquini'),
                    '2026-08-14', 'Resultado verificado',
                    array['resultado_de_prueba'])
           returning id""", (ws, obj, ws, ws))
    t = cur.fetchone()["id"]
    cur.execute("insert into task_state_event (task_id, estado_nuevo, actor_kind) "
                "values (%s, 'asignada', 'prisma')", (t,))
    cur.execute("set local role prisma_app")
    return str(t)


def _cuerpos(cur) -> list[str]:
    cur.execute("select cuerpo from message_outbox order by id")
    return [f["cuerpo"] for f in cur.fetchall()]


# ---------------------------------------------------------------------------

def test_no_anuncia_como_hecho_lo_que_quedo_esperando_confirmacion(corework, conn):
    """El caso que da vergüenza: "listo" cuando no hizo nada.

    Desde ADR 0005 (decisión 1), `actualizar_estado` siempre pide
    confirmación: no hace falta forzar `REQUIEREN_CONFIRMACION` a mano.
    """
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)

    guion = [
        Respuesta(llamadas=[Llamada("c1", "actualizar_estado",
                                    {"tarea_id": tid, "estado": "en_curso"})]),
        Respuesta(texto="Listo, ya la puse en curso."),
    ]
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        responder(cur, quien, "arranco con esto", ProveedorGuionado(guion),
                  cal, chat_id=9004, ahora=AHORA)

        cuerpos = _cuerpos(cur)
        assert not any("Listo" in c for c in cuerpos), cuerpos
        assert any("Todavía no se aplicó ningún cambio." in c for c in cuerpos)


def test_legacy_crear_tarea_no_produce_eleccion_ni_efecto(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Ismael Soschinski", ws)
        cur.execute(
            """insert into objective (workspace_id, tipo, titulo)
               values (%s, 'operativo', 'Integrar comprimidora 3') returning id""",
            (ws,))
        obj = str(cur.fetchone()["id"])
        cal = Calendario.desde_base(cur, ws)

        guion = [
            Respuesta(llamadas=[Llamada("c1", "crear_tarea", {
                "titulo": "Relevar tablero", "objetivo_id": obj,
                "area_slug": "ot", "responsable": "Mar"})]),
            Respuesta(texto="Hecho, se la asigné a Marcos."),
        ]
        responder(cur, quien, "creá una tarea para Mar",
                  ProveedorGuionado(guion), cal, chat_id=9000, ahora=AHORA)

        cuerpos = _cuerpos(cur)
        assert any(NO_EFFECT_STATUS in c for c in cuerpos), cuerpos
        cur.execute("select count(*) n from pending_action")
        assert cur.fetchone()["n"] == 0
        cur.execute("select count(*) n from task_draft")
        assert cur.fetchone()["n"] == 0


def test_no_arrastra_el_texto_de_una_vuelta_anterior(corework, conn):
    """"Voy a crear la tarea" no es una respuesta final."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        tid = _tarea(cur, ws)

        guion = [
            Respuesta(texto="Voy a ponerla en curso.",
                      llamadas=[Llamada("c1", "actualizar_estado",
                                        {"tarea_id": tid, "estado": "en_curso"})]),
            Respuesta(texto=""),      # el modelo no cierra
        ]
        r = responder(cur, quien, "arranco", ProveedorGuionado(guion), cal,
                      chat_id=9004, ahora=AHORA)

        assert "Voy a ponerla" not in r.texto
        assert not any("Voy a ponerla" in c for c in _cuerpos(cur))


def test_si_se_agotan_las_vueltas_no_inventa_un_cierre(corework, conn):
    """Quedó a mitad de camino: no puede sonar a terminado."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        tid = _tarea(cur, ws)

        # Siempre pide otra herramienta: nunca cierra.
        guion = [Respuesta(texto="Ya está todo hecho.",
                           llamadas=[Llamada(f"c{i}", "consultar_tareas", {})])
                 for i in range(10)]
        r = responder(cur, quien, "cómo venimos", ProveedorGuionado(guion), cal,
                      chat_id=9004, ahora=AHORA)

        assert "Ya está todo hecho" not in r.texto
        assert not any("Ya está todo hecho" in c for c in _cuerpos(cur))

    # Los incidentes se leen con rol de administración: el agente los escribe
    # y no los lee, que es justamente lo que dice el esquema.
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident")
        assert cur.fetchone()["n"] == 1


def test_una_respuesta_normal_sale_tal_cual(corework, conn):
    """La red de seguridad no puede volverse una mordaza."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)

        guion = [Respuesta(texto="Tenés dos tareas abiertas esta semana.")]
        r = responder(cur, quien, "qué tengo", ProveedorGuionado(guion), cal,
                      chat_id=9004, ahora=AHORA)

        assert r.texto == "Tenés dos tareas abiertas esta semana."
        assert _cuerpos(cur) == [r.texto]


def test_lo_que_si_ejecuto_lo_puede_contar(corework, conn):
    """Si la acción corrió, el texto del modelo sale sin recortes.

    Las 8 herramientas que escriben ya no ejecutan directo (ADR 0005): la
    que se ejecuta sola en un turno es una de consulta.
    """
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        cal = Calendario.desde_base(cur, ws)
        _tarea(cur, ws)

        guion = [
            Respuesta(llamadas=[Llamada("c1", "consultar_tareas", {})]),
            Respuesta(texto="Tenés una tarea abierta."),
        ]
        r = responder(cur, quien, "qué tengo", ProveedorGuionado(guion), cal,
                      chat_id=9004, ahora=AHORA)

        # T10-5 (H7): la única tarea listada se nombra; el texto del modelo sale entero.
        assert r.texto.endswith("Tenés una tarea abierta.")
        assert r.acciones == ["consultar_tareas"]
