"""Regresión de replay: cada archivo en `tests/banco/replays/` graba una
corrida ya evaluada (una grabación de proveedor + el resultado esperado de
los comprobadores) y este test la repite con `ProveedorGuionado` sobre el
circuito real, sin red y sin modelo. Corre en la suite por defecto -- no
lleva el marcador `modelo_real` (`odd/tasks/banco-conversacional.md`, T4).
"""

from __future__ import annotations

import json

from prisma.db import admin
from prisma.llm import IntentAction, IntentRoute, ProveedorGuionado, Respuesta

from tests.banco.comprobadores import (
    Evidencia,
    comprobaciones_pregunta_con_opciones,
    comprobar_accion_sin_herramienta,
    comprobar_aclaracion,
    comprobar_contenido,
    comprobar_efectos,
    comprobar_herramientas,
    comprobar_personas_mencionadas,
    comprobar_pregunta,
    comprobar_sin_efectos_antes_de_confirmar,
    comprobar_una_respuesta_por_entrada,
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
        aclaracion_esperada=escenario.aclaracion_esperada or None,
        toques=list(escenario.toques) or None,
        mensajes_tras_toques=list(escenario.mensajes_tras_toques) or None,
        confirmar=escenario.confirmar or None)

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
        # ADR 0013 regla 2 (T9-R2): cada mensaje, exactamente una respuesta
        # visible -- en todo escenario, sin opt-out.
        comprobar_una_respuesta_por_entrada(
            resultado.respuestas_por_mensaje,
            incidentes=resultado.incidentes_de_respuesta,
            respuestas_por_toque=resultado.respuestas_por_toque),
    ]
    # ADR 0007 ("Prisma orienta, no charla"), T4: mismo criterio que
    # `test_banco.py` -- activa por defecto, opt-out explícito por escenario
    # (`comprobaciones_pregunta_con_opciones`, una sola implementación de la
    # puerta para los dos llamadores reales).
    comprobaciones.extend(comprobaciones_pregunta_con_opciones(
        evidencia, permite_pregunta_sin_opciones=escenario.permite_pregunta_sin_opciones))
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


# ---------------------------------------------------------------------------
# Puerta de opt-out de `comprobar_pregunta_con_opciones` (T4, ADR 0007),
# de punta a punta (revisión del orquestador, 2026-09-26): antes de esto,
# `permite_pregunta_sin_opciones` sólo tenía prueba de que se parsea bien
# (`test_escenario.py`) y de que `comprobar_pregunta_con_opciones` funciona
# sola (`test_comprobadores.py`) -- nada ejercitaba la puerta en sí, sobre
# una corrida real de `ejecutar_escenario`, con los dos valores del campo.
# No se fabrica un replay "real" para esto (mismo criterio que T4 con
# `b-0016`-`b-0018`: un replay representa una corrida ya evaluada de verdad);
# en cambio, corre un `ProveedorGuionado` directo -- sin red, en la suite por
# defecto -- contra `comprobaciones_pregunta_con_opciones`, la función que
# este archivo y `test_banco.py` llaman de verdad.
# ---------------------------------------------------------------------------


def _corrida_pregunta_en_texto_abierto(conn, ws: str, escenario_id: str):
    """Un guión que hace que el modelo cierre el turno preguntando en texto
    abierto, sin llamar a `ofrecer_opciones` ni a ninguna otra herramienta.

    Hasta T4b (`prisma-orienta`), este era el caso que
    `comprobar_pregunta_con_opciones` marcaba `falla` cuando la puerta está
    activa -- nada del lado del servidor evitaba que esa pregunta abierta
    llegara tal cual. Desde T4b, `agente.responder` agrega un cierre
    genérico de botones cada vez que el turno termina así (ADR 0007, "Prisma
    orienta, no charla", sin excepción), así que esta misma corrida ya
    ofrece opciones -- ver `test_pregunta_con_opciones_activa_ahora_aprueba_
    porque_el_servidor_ya_cierra_con_botones`, más abajo."""
    interno = ProveedorGuionado(
        guion=[Respuesta(texto="Tenés dos pendientes. ¿Cuál mirás primero?")],
        rutas=[IntentRoute(IntentAction.NORMAL_CONVERSATION)],
    )
    resultado = ejecutar_escenario(
        conn, ws, "corework", "Marcos Tarquini",
        ["tengo dos cosas pendientes, no se por cual arrancar"], interno,
        escenario_id=escenario_id, indice=0)
    assert resultado.bloqueado is False, resultado.motivo_bloqueo
    return Evidencia(
        respuesta_texto=resultado.respuesta_texto,
        herramientas_ejecutadas=tuple(resultado.herramientas_ejecutadas),
        ofrecio_opciones=resultado.ofrecio_opciones)


def test_permite_pregunta_sin_opciones_deja_pasar_una_pregunta_en_texto_abierto(
        corework, conn):
    evidencia = _corrida_pregunta_en_texto_abierto(
        conn, corework.workspace_id, "b-test-gate-permitida")
    comprobaciones = comprobaciones_pregunta_con_opciones(
        evidencia, permite_pregunta_sin_opciones=True)
    assert comprobaciones == []
    assert resultado_general(comprobaciones) == "aprobado"


def test_pregunta_con_opciones_activa_ahora_aprueba_porque_el_servidor_ya_cierra_con_botones(
        corework, conn):
    """Regresión detectada al implementar T4b (`prisma-orienta`): antes de
    esa unidad, esta misma corrida (una pregunta en texto abierto, sin
    `ofrecer_opciones`) daba `falla` con la puerta activa -- era el caso que
    `comprobar_pregunta_con_opciones` existía para atrapar. Desde T4b,
    `agente.responder` agrega el cierre genérico de tres botones al mismo
    turno (nunca deja pasar una pregunta sin opciones), así que la corrida
    real ya trae `ofrecio_opciones=True` y la comprobación aprueba -- no
    porque la comprobación se haya debilitado, sino porque el defecto que
    medía ya no existe en el servidor. El comprobador sigue fallando ante
    una `Evidencia` sin opciones armada a mano
    (`test_comprobadores.py::test_pregunta_con_opciones_signo_de_pregunta_
    sin_botones_falla`), que no depende de este camino."""
    evidencia = _corrida_pregunta_en_texto_abierto(
        conn, corework.workspace_id, "b-test-gate-activada")
    comprobaciones = comprobaciones_pregunta_con_opciones(
        evidencia, permite_pregunta_sin_opciones=False)
    assert [c.nombre for c in comprobaciones] == ["pregunta_con_opciones"]
    assert resultado_general(comprobaciones) == "aprobado"
