"""Pruebas de `herramientas.ejecutar` y de las descripciones del registro.

Venían de `tests/test_agente.py`, que se retiró con los flujos A y B (E3-4): un
argumento que la herramienta no conoce, o uno requerido que falta, se rechaza con
`Denegado` y no tira abajo el turno.
"""

from __future__ import annotations

import pytest

from leda import herramientas as H
from leda.autoridad import Canal, identificar
from leda.db import espacio


def _quien(cur, nombre, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s", (nombre,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def test_argumento_desconocido_se_rechaza_con_h_ejecutar(corework, conn):
    """`consultar_tareas` no tiene `tarea_id` -- b-0002: el modelo lo llamó
    así y un `TypeError` sin atrapar tiraba abajo el turno entero."""
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        with pytest.raises(H.Denegado) as exc:
            H.ejecutar(cur, quien, "consultar_tareas", {"tarea_id": "algo"})
    mensaje = str(exc.value)
    assert "argumentos no válidos" in mensaje
    assert "tarea_id" in mensaje
    assert "responsable" in mensaje and "estado" in mensaje and "vencidas" in mensaje


def test_argumento_requerido_faltante_se_rechaza_con_h_ejecutar(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        with pytest.raises(H.Denegado) as exc:
            H.ejecutar(cur, quien, "registrar_bloqueo", {"tarea_id": "algo"})
    mensaje = str(exc.value)
    assert "argumentos no válidos" in mensaje
    assert "causa" in mensaje


def test_argumentos_correctos_no_se_ven_afectados(corework, conn):
    ws = corework.workspace_id
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        resultado = H.ejecutar(cur, quien, "consultar_tareas", {})
    assert resultado == []                       # sin tareas propias sembradas


def test_descripcion_de_bloqueo_distingue_causa_externa_de_otra_tarea():
    descripcion = H.REGISTRO["registrar_bloqueo"].descripcion
    assert "causa externa" in descripcion or "externa al equipo" in descripcion
    assert "crear_dependencia" in descripcion


def test_descripcion_de_dependencia_distingue_otra_tarea_de_causa_externa():
    descripcion = H.REGISTRO["crear_dependencia"].descripcion
    assert "otra tarea" in descripcion
    assert "registrar_bloqueo" in descripcion
