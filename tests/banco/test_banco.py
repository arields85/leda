"""El banco conversacional contra un modelo real.

Fuera de la suite por defecto (marcador `modelo_real`, `pyproject.toml`
`addopts`). Se corre explícitamente:

    .venv/Scripts/python.exe -m pytest -m modelo_real tests/banco \\
        --banco-n 3 --banco-proveedor nan --banco-modelo deepseek-v4-flash

Cada (escenario, corrida) empieza de una base limpia: `corework` y `conn` son
fixtures por test, y la parametrización de `escenario_y_corrida`
(`conftest.py`) genera un test por corrida.

Criterio de aprobación (revisión, `odd/tasks/banco-conversacional.md`,
Progreso): el protocolo dice "sin umbrales inventados" para latencia y
costo, pero exige `cumple` para corrección y completitud conversacional
(`docs/validation/README.md`, "Criterios de aprobación y baseline"). Un
`falla` de cualquier comprobador -- herramienta, acción inventada, estado o
efecto incorrecto -- corta la corrida con `pytest.fail` (y guarda el
candidato de replay). Un `bloqueado` también corta -- es un fallo de
mecanismo, no de calidad del modelo. Un `no_concluyente` (nombre ajeno al
equipo que la detección sobre texto libre no puede confirmar ni descartar)
no corta la corrida -- el protocolo lo trata como "no verificable", no como
fallo -- pero se emite como warning y queda igual en el reporte de sesión.
"""

from __future__ import annotations

import warnings

import pytest

from prisma.db import admin

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
from tests.banco.conftest import guardar_candidato_replay, registrar_entrada_sesion
from tests.banco.corrida import (
    conteos_delta,
    ejecutar_escenario,
    recolectar_efectos,
    sembrar_precondiciones,
)
from tests.banco.reporte import EntradaReporte

pytestmark = pytest.mark.modelo_real


def _roster_y_titulos(conn, ws: str) -> tuple[list[str], list[str]]:
    with admin(conn) as cur:
        cur.execute(
            """select u.nombre from membership m join app_user u on u.id = m.app_user_id
                where m.workspace_id = %s and m.activo""", (ws,))
        integrantes = [f["nombre"] for f in cur.fetchall()]
        cur.execute("select titulo from task where workspace_id = %s", (ws,))
        titulos = [f["titulo"] for f in cur.fetchall()]
    return integrantes, titulos


def test_escenario_contra_modelo_real(
        escenario_y_corrida, corework, conn, proveedor_real, cliente_jev_real):
    escenario, indice = escenario_y_corrida
    ws = corework.workspace_id

    # Un borrador de alta cuyos botones el escenario toca se siembra dentro de la
    # corrida: los toques sólo ven lo creado durante ella (`corrida`).
    borrador_en_la_corrida = bool(
        escenario.toques and escenario.precondiciones.get("borrador_de_alta"))
    ids_semilla: dict[str, str] = {}
    if escenario.precondiciones:
        with admin(conn) as cur:
            ids_semilla = sembrar_precondiciones(
                cur, ws, escenario.precondiciones,
                sin_borrador_de_alta=borrador_en_la_corrida)

    resultado = ejecutar_escenario(
        conn, ws, "corework", escenario.actor, escenario.mensajes, proveedor_real,
        escenario_id=escenario.id, indice=indice, cliente_jev=cliente_jev_real,
        aclaracion_esperada=escenario.aclaracion_esperada or None,
        toques=list(escenario.toques) or None,
        mensajes_tras_toques=list(escenario.mensajes_tras_toques) or None,
        toques_tras_mensajes=list(escenario.toques_tras_mensajes) or None,
        confirmar=escenario.confirmar or None,
        preguntas_sembradas={
            c: escenario.precondiciones[c]
            for c in ("vista_previa", "aclaracion", "borrador_de_alta")
            if escenario.precondiciones.get(c)
            and (c != "borrador_de_alta" or borrador_en_la_corrida)} or None)

    if resultado.bloqueado:
        entrada = EntradaReporte(
            escenario_id=escenario.id, indice=indice, resultado="bloqueado",
            comprobaciones=[], latencia_total_s=resultado.latencia_total_s,
            grabacion=resultado.grabacion, motivo_bloqueo=resultado.motivo_bloqueo)
        registrar_entrada_sesion(entrada)
        guardar_candidato_replay(entrada, escenario.id)
        pytest.fail(f"corrida bloqueada: {resultado.motivo_bloqueo}")

    integrantes, titulos = _roster_y_titulos(conn, ws)
    evidencia = Evidencia(respuesta_texto=resultado.respuesta_texto,
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
    # ADR 0007 ("Prisma orienta, no charla"), T4: activa por defecto para
    # todo escenario -- `permite_pregunta_sin_opciones` es el opt-out
    # explícito de un escenario legado que necesite seguir pasando con una
    # pregunta en texto abierto sin botones
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

    entrada = EntradaReporte(
        escenario_id=escenario.id, indice=indice, resultado=veredicto,
        comprobaciones=[{"nombre": c.nombre, "resultado": c.resultado,
                        "diferencia": c.diferencia} for c in comprobaciones],
        latencia_total_s=resultado.latencia_total_s, grabacion=resultado.grabacion)
    registrar_entrada_sesion(entrada)

    if veredicto == "aprobado":
        return

    detalle = "; ".join(f"{c.nombre}={c.resultado} ({c.diferencia})"
                        for c in comprobaciones if c.resultado != "aprobado")

    if veredicto == "no_concluyente":
        # No verificable, no es un fallo (protocolo, "Verificación de
        # resultado"): no corta la corrida, pero no se pierde en silencio.
        warnings.warn(f"{escenario.id}[{indice}] no_concluyente: {detalle}", stacklevel=1)
        return

    ruta = guardar_candidato_replay(entrada, escenario.id)
    pytest.fail(f"{veredicto}: {detalle} -- candidato de replay guardado en {ruta}")
