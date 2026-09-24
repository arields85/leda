"""Regresión de replay: cada archivo en `tests/banco/replays/` graba una
corrida ya evaluada (una grabación de proveedor + el resultado esperado de
los comprobadores) y este test la repite con `ProveedorGuionado` sobre el
circuito real, sin red y sin modelo. Corre en la suite por defecto -- no
lleva el marcador `modelo_real` (`odd/tasks/banco-conversacional.md`, T4).
"""

from __future__ import annotations

import json

from prisma.db import admin

from tests.banco.comprobadores import (
    Evidencia,
    comprobar_accion_sin_herramienta,
    comprobar_aclaracion,
    comprobar_contenido,
    comprobar_efectos,
    comprobar_herramientas,
    comprobar_personas_mencionadas,
    comprobar_pregunta,
    comprobar_sin_efectos_antes_de_confirmar,
    resultado_general,
)
from tests.banco.conftest import DIR_ESCENARIOS
from tests.banco.corrida import (
    conteos_delta,
    ejecutar_escenario,
    guionado_desde_grabacion,
    jev_guionado_desde_grabacion,
    recolectar_efectos,
    sembrar_precondiciones,
)
from tests.banco.escenario import cargar_escenario


def _roster_y_titulos(conn, ws: str) -> tuple[list[str], list[str]]:
    with admin(conn) as cur:
        cur.execute(
            """select u.nombre from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and m.activo""", (ws,))
        integrantes = [f["nombre"] for f in cur.fetchall()]
        cur.execute("select titulo from task where workspace_id = %s", (ws,))
        titulos = [f["titulo"] for f in cur.fetchall()]
    return integrantes, titulos


def test_replay_reproduce_el_resultado_esperado(archivo_replay, corework, conn):
    datos = json.loads(archivo_replay.read_text("utf-8"))
    escenario = cargar_escenario(DIR_ESCENARIOS / f"{datos['escenario_id']}.yaml")
    ws = corework.workspace_id

    ids_semilla: dict[str, str] = {}
    if escenario.precondiciones:
        with admin(conn) as cur:
            ids_semilla = sembrar_precondiciones(cur, ws, escenario.precondiciones)

    guionado = guionado_desde_grabacion(datos["grabacion"])
    jev_guionado = jev_guionado_desde_grabacion(datos["grabacion"])
    resultado = ejecutar_escenario(
        conn, ws, "corework", escenario.actor, escenario.mensajes, guionado,
        escenario_id=escenario.id, indice=0, cliente_jev=jev_guionado,
        aclaracion_esperada=escenario.aclaracion_esperada or None)

    assert not resultado.bloqueado, resultado.motivo_bloqueo

    integrantes, titulos = _roster_y_titulos(conn, ws)
    evidencia = Evidencia(
        respuesta_texto=resultado.respuesta_texto,
        herramientas_ejecutadas=tuple(resultado.herramientas_ejecutadas),
        ofrecio_opciones=resultado.ofrecio_opciones)

    with admin(conn) as cur:
        efectos_observados = recolectar_efectos(cur, ids_semilla)
    efectos_observados["conteos_delta"] = conteos_delta(
        resultado.conteos_antes, resultado.conteos_despues)

    comprobaciones = [
        comprobar_herramientas(evidencia, esperadas=escenario.herramientas_esperadas,
                               prohibidas=escenario.herramientas_prohibidas),
        comprobar_accion_sin_herramienta(evidencia),
        comprobar_personas_mencionadas(
            evidencia, integrantes, titulos_tareas=titulos,
            nombres_permitidos=escenario.nombres_permitidos),
        comprobar_efectos(efectos_observados, escenario.efectos),
        comprobar_contenido(
            evidencia, menciona=escenario.respuesta_menciona,
            no_contiene_patron=escenario.respuesta_no_contiene_patron),
        comprobar_sin_efectos_antes_de_confirmar(
            resultado.conteos_antes, resultado.conteos_antes_del_toque,
            resultado.conteos_despues,
            herramientas_antes_del_toque=resultado.herramientas_antes_del_toque),
    ]
    if escenario.debe_preguntar:
        comprobaciones.append(comprobar_pregunta(
            evidencia, task_draft_delta=efectos_observados["conteos_delta"].get("task_draft", 0),
            permite_borrador_de_tarea=escenario.permite_borrador_de_tarea))
    if escenario.aclaracion_esperada:
        comprobaciones.append(comprobar_aclaracion(
            resultado.etiquetas_aclaracion_ofrecidas,
            candidatas_esperadas=escenario.aclaracion_esperada["candidatas"]))
    veredicto = resultado_general(comprobaciones)

    assert veredicto == datos["resultado_esperado"], (
        f"esperado {datos['resultado_esperado']!r}, obtuve {veredicto!r} -- "
        f"comprobaciones: {[(c.nombre, c.resultado, c.diferencia) for c in comprobaciones]}")
