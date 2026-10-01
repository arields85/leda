"""El camino general ve el borrador pausado (diseño B, 2026-10-01).

Un borrador pausado (`terminal_result.pausado`) no es una rama abierta, así que
los mensajes siguientes van al camino general, que sólo conocía las tareas de la
tabla `task`: "¿qué tarea dejaste para el lunes?" abría una aclaración con
botones de tareas ajenas, y esa aclaración quedaba como rama abierta. Ahora el
servidor le da al ruteo (y al modelo que responde) el HECHO de que la persona
tiene un borrador guardado (`ingreso_tareas.borrador_pausado`), y el ruteo puede
devolver el comando cerrado `paused_draft` (ADR 0013 regla 1): el código ejecuta
un manejo determinista, el menú que ya existe (Continuar / Cancelar / Empezar
otro), en UNA respuesta y sin pasar por Jev.

El ruteo se guiona: el doble hace de modelo que decide. Ninguna prueba toca la
red ni el modelo real.
"""

from __future__ import annotations

import dataclasses

import pytest

from prisma import gateway
from prisma import ingreso_tareas as I
from prisma import jev as jev_modulo
from prisma.db import admin, espacio
from prisma.jev import ClienteJevGuionado
from prisma.salida import etiqueta_sin_icono
from prisma.llm import (IntentAction, IntentRoute, ProveedorGuionado,
                        Respuesta)

from tests.test_alta_eleccion_confirmacion import (
    TITULO, _alta_con_eleccion, _escribir, _nuevas, _RoutingProvider, _salidas,
    _usuario)
from tests.test_task_intake import NOW, _actor

HECHO = f"La persona tiene guardado, en pausa, el borrador de la tarea «{TITULO}»."
HECHO_SIN_TITULO = ("La persona tiene guardado, en pausa, un borrador de tarea "
                    "que estaba armando.")
MENU = f"Quedó guardado el borrador de la tarea «{TITULO}». Elegí cómo seguir."
MENU_SIN_TITULO = ("Quedó guardado un borrador de tarea que estabas armando. "
                   "Elegí cómo seguir.")
MENU_DE_SIEMPRE = "Ya hay un borrador de tarea en curso. Elegí cómo seguir."
ETIQUETAS = ["Continuar borrador", "Cancelar borrador", "Empezar otro"]

BORRADOR = IntentRoute(IntentAction.PAUSED_DRAFT)


class _Proveedor(_RoutingProvider):
    """Registra el hecho que recibe cada ruteo y el sistema de cada respuesta."""

    def __init__(self, routes, answer="Natural answer"):
        super().__init__(routes, answer)
        self.hechos: list[str | None] = []
        self.sistemas: list[str] = []

    def route_intent(self, text, pendiente=None, valor_esperado=None,
                     historial=None, borrador_pausado=None):
        self.hechos.append(borrador_pausado)
        return super().route_intent(text, pendiente, valor_esperado, historial)

    def responder(self, sistema, *args):
        self.sistemas.append(sistema)
        return super().responder(sistema, *args)


def _pausar(conn, world, rid, *, sin_titulo=False) -> None:
    ws = world["north-lab"]["id"]
    if sin_titulo:
        with admin(conn) as cur:
            cur.execute(
                "update task_intake_field set estado = 'missing', valor = null "
                "where request_id = %s and campo = 'title'", (rid,))
    with espacio(conn, ws) as cur:
        actor = _actor(cur, world)
        cur.execute("select * from task_intake_request where id = %s", (rid,))
        I.pause_request(cur, actor, cur.fetchone(), NOW)
    conn.commit()


def _aclaraciones(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (gateway._SENTINEL_ACLARACION,))
        return cur.fetchone()["n"]


def _etiquetas(conn, salida) -> list[str]:
    with admin(conn) as cur:
        cur.execute("""select etiqueta from task_intake_choice
                        where choice_set_id = %s order by orden""",
                    (salida["intake_choice_set_id"],))
        return [etiqueta_sin_icono(f["etiqueta"]) for f in cur.fetchall()]


@pytest.mark.parametrize("texto", [
    "¿qué tarea dejaste para el lunes?",
    "¿dónde quedó lo que estaba armando?",
    "quiero seguir con eso",
    "mostrame ese borrador",
])
def test_preguntar_por_el_borrador_pausado_da_el_menu_en_una_respuesta(
        texto, intake_world, conn, monkeypatch):
    """El ruteo decide `paused_draft` (aunque separe una referencia que parece de
    una tarea): una sola respuesta, la del menú de siempre, sin Jev y sin abrir
    ninguna aclaración."""
    rid = _alta_con_eleccion(conn, intake_world)
    _pausar(conn, intake_world, rid)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _Proveedor([dataclasses.replace(
        BORRADOR, trabajos=("la tarea que quedó para el lunes",))])

    _escribir(conn, monkeypatch, intake_world, provider, texto)

    nuevas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in nuevas] == [MENU]
    assert _etiquetas(conn, nuevas[0]) == ETIQUETAS
    assert _aclaraciones(conn) == 0
    assert provider.main_calls == 0
    assert provider.hechos == [HECHO]


def test_pedir_una_tarea_con_un_borrador_pausado_da_el_menu_de_siempre(
        intake_world, conn, monkeypatch):
    """Regresión: crear una tarea sigue por `start_task_intake` y su menú."""
    rid = _alta_con_eleccion(conn, intake_world)
    _pausar(conn, intake_world, rid)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _Proveedor([IntentRoute(IntentAction.START_TASK_INTAKE)])

    _escribir(conn, monkeypatch, intake_world, provider, "quiero crear una tarea")

    nuevas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in nuevas] == [MENU_DE_SIEMPRE]
    assert _etiquetas(conn, nuevas[0]) == ETIQUETAS
    assert _aclaraciones(conn) == 0
    assert provider.hechos == [HECHO]


def test_sin_titulo_confirmado_el_hecho_y_el_menu_son_genericos(
        intake_world, conn, monkeypatch):
    rid = _alta_con_eleccion(conn, intake_world)
    _pausar(conn, intake_world, rid, sin_titulo=True)
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _Proveedor([BORRADOR])

    _escribir(conn, monkeypatch, intake_world, provider,
              "¿qué tarea dejaste para el lunes?")

    nuevas = _nuevas(conn, user, antes)
    assert [f["cuerpo"] for f in nuevas] == [MENU_SIN_TITULO]
    assert _etiquetas(conn, nuevas[0]) == ETIQUETAS
    assert provider.hechos == [HECHO_SIN_TITULO]


def test_el_menu_del_borrador_pausado_sigue_su_camino(
        intake_world, conn, monkeypatch):
    """Es el menú de siempre: Continuar quita la pausa y retoma el borrador."""
    from tests.test_task_intake import _choose

    rid = _alta_con_eleccion(conn, intake_world)
    _pausar(conn, intake_world, rid)
    user = _usuario(intake_world)
    _escribir(conn, monkeypatch, intake_world, _Proveedor([BORRADOR]),
              "¿qué tarea dejaste para el lunes?")

    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        _choose(cur, _actor(cur, intake_world), rid, "Continuar borrador",
                chat_id=user)
    conn.commit()

    with admin(conn) as cur:
        cur.execute("select estado, terminal_result from task_intake_request "
                    "where id = %s", (rid,))
        fila = cur.fetchone()
    assert fila["estado"] == "active"
    assert not (fila["terminal_result"] or {}).get("pausado")


def test_sin_borrador_pausado_el_camino_general_no_cambia(
        intake_world, conn, monkeypatch):
    """Sin borrador pausado no hay hecho (ni en el ruteo ni en la respuesta), y
    un `paused_draft` que no corresponde se atiende como conversación normal."""
    user = _usuario(intake_world)
    antes = _salidas(conn, user)
    provider = _Proveedor([IntentRoute(IntentAction.NORMAL_CONVERSATION), BORRADOR],
                          answer="Hay dos tareas abiertas.")

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué tengo pendiente?")
    _escribir(conn, monkeypatch, intake_world, provider,
              "¿qué tarea dejaste para el lunes?")

    assert provider.hechos == [None, None]
    assert provider.main_calls == 2
    assert all("en pausa" not in s for s in provider.sistemas)
    assert [f["cuerpo"] for f in _nuevas(conn, user, antes)] == [
        "Hay dos tareas abiertas."] * 2


def test_el_modelo_que_responde_recibe_el_hecho_del_borrador_pausado(
        intake_world, conn, monkeypatch):
    """Si el ruteo no lo toma como el borrador, la respuesta igual sabe que existe."""
    rid = _alta_con_eleccion(conn, intake_world)
    _pausar(conn, intake_world, rid)
    provider = _Proveedor([IntentRoute(IntentAction.NORMAL_CONVERSATION)],
                          answer="Hay dos tareas abiertas.")

    _escribir(conn, monkeypatch, intake_world, provider, "¿qué tengo pendiente?")

    assert provider.hechos == [HECHO]
    assert provider.main_calls == 1
    assert HECHO in provider.sistemas[0]


def test_una_tarea_existente_se_resuelve_aunque_haya_un_borrador_pausado(
        intake_world, conn, monkeypatch):
    """El hecho del borrador no secuestra las referencias reales: una pregunta
    por una tarea que existe sigue por Jev y se resuelve a esa tarea."""
    rid = _alta_con_eleccion(conn, intake_world)
    _pausar(conn, intake_world, rid)
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        cur.execute("""insert into objective (workspace_id, tipo, titulo)
                       values (%s, 'operativo', 'Objetivo de prueba')
                       returning id""", (ws,))
        objetivo = cur.fetchone()["id"]
        cur.execute(
            """insert into task (workspace_id, objective_id, titulo, area_id,
                                 responsable_membership_id, criterio_aceptacion,
                                 evidencia_requerida)
               values (%s, %s, 'Cablear tablero máq. 3',
                       (select id from area where workspace_id = %s
                           and slug = 'field'),
                       (select m.id from membership m
                          join app_user u on u.id = m.app_user_id
                         where m.workspace_id = %s and u.nombre = 'Sam North'),
                       'Criterio de prueba', array['explicacion'])
               returning id""", (ws, objetivo, ws, ws))
        tarea_id = str(cur.fetchone()["id"])
        cur.execute("insert into task_state_event (task_id, estado_nuevo, "
                    "actor_kind) values (%s, 'asignada', 'prisma')", (tarea_id,))
    conn.commit()
    monkeypatch.setattr(
        gateway, "config",
        dataclasses.replace(gateway.config, openrouter_api_key="sk-test-fake"))
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: ClienteJevGuionado(
        guion=[{"alcance": {"probabilities": {"una_tarea": 0.95,
                                              "varias_tareas": 0.0,
                                              "ninguna": 0.0}},
                "tarea": {"probabilities": {"T1": 0.9}}},
               {"misma": {"noul": 0.8}}]))
    proveedor = ProveedorGuionado(
        guion=[Respuesta(texto="Va bien.")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION,
                           trabajos=("lo del tablero",))])
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)

    with espacio(conn, ws) as cur:
        gateway._turno(cur, _actor(cur, intake_world), "¿cómo va lo del tablero?",
                       ws, _usuario(intake_world))

    assert proveedor.borradores_pausados == [HECHO]
    sistema, _ = proveedor.recibidos[-1]
    assert f"«lo del tablero» es la tarea «Cablear tablero máq. 3» ({tarea_id})" in sistema
    assert _aclaraciones(conn) == 0


def test_el_ruteo_ofrece_paused_draft_y_el_hecho_sólo_con_un_borrador_guardado():
    from prisma import llm

    def acciones(con):
        return llm._herramienta_del_ruteo(None, None, con)[
            "input_schema"]["properties"]["action"]["enum"]

    assert "paused_draft" not in acciones(False)
    assert "paused_draft" in acciones(True)
    assert "paused_draft" not in llm.ROUTER_TOOL[
        "input_schema"]["properties"]["action"]["enum"]   # el global no muta
    assert HECHO not in llm._sistema_del_ruteo(None)
    assert HECHO in llm._sistema_del_ruteo(None, None, None, HECHO)


def test_el_contexto_de_la_respuesta_mira_el_mismo_chat_que_el_ruteo(
        intake_world, conn):
    """Quien responde no puede saber de un borrador sobre el que el código de este
    turno no va a actuar: el hecho sale sólo en el chat del borrador (revisión RDD
    `review-9b9e456cc4c197c1`, R2/R3)."""
    from prisma.contexto import construir

    rid = _alta_con_eleccion(conn, intake_world)
    _pausar(conn, intake_world, rid)
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        quien = _actor(cur, intake_world)
        assert HECHO in construir(cur, quien, "hola", ahora=NOW, chat_id=user).sistema
        assert "en pausa" not in construir(cur, quien, "hola", ahora=NOW,
                                           chat_id=user + 1).sistema
        assert "en pausa" not in construir(cur, quien, "hola", ahora=NOW).sistema
