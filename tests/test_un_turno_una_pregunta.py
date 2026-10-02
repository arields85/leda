"""Un turno nunca abre dos cosas (T9-R1d-1c, ADR 0013 regla 1 y regla 2).

Cuando una llamada a herramienta deja algo esperando a la persona -- una vista
previa con Confirmar, una elección con botones, `ofrecer_opciones` -- el turno
termina ahí: las llamadas que siguen en la misma vuelta que escriben o abren
otra pregunta se rechazan antes de ejecutarse (el modelo recibe el rechazo y
queda su auditoría), y lo que se ve es una sola pregunta con un solo juego de
botones. Las lecturas no se ven afectadas.

Evidencia: banco real `b-0023` (2026-09-29), donde el responder abrió dos
cosas seguidas en el mismo turno.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from leda import agente
from leda import pendientes as P
from leda.agente import responder
from leda.autoridad import Canal, identificar
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import Llamada, ProveedorGuionado, Respuesta

from tests.test_modificar import _tarea

PERSONA = "Marcos Tarquini"
CHAT = 4242


def _quien(cur, ws):
    cur.execute("select telegram_user_id t from integrante where nombre = %s",
                (PERSONA,))
    return identificar(cur, cur.fetchone()["t"], Canal.ESPACIO, ws)


def _dos_tareas(conn, ws) -> tuple[str, str]:
    with admin(conn) as cur:
        a = _tarea(cur, ws, titulo="Programar PLC")
        b = _tarea(cur, ws, titulo="Revisar variador")
    conn.commit()
    return a, b


def _bloqueo(llamada_id: str, tarea_id: str) -> Llamada:
    return Llamada(llamada_id, "registrar_bloqueo",
                   {"tarea_id": tarea_id, "causa": "falta el switch"})


def _turno(conn, ws, monkeypatch, llamadas: list[Llamada]):
    """Corre un turno cuyo modelo pide todas `llamadas` en una sola vuelta.
    Devuelve (resultado, resultados de herramienta que vio el modelo)."""
    vistos: list[dict] = []

    def _capturar(nombre: str) -> None:
        original = getattr(agente, nombre)

        def _capturando(*args, **kwargs):
            bloque = original(*args, **kwargs)
            vistos.append(bloque)
            return bloque

        monkeypatch.setattr(agente, nombre, _capturando)

    # El turno cierra tras esa vuelta y el modelo ya no vuelve a leer los
    # resultados: se capturan al salir, en el orden de las llamadas.
    _capturar("_ejecutar_una")
    _capturar("_rechazar_segunda_pregunta")
    proveedor = ProveedorGuionado(guion=[Respuesta(llamadas=llamadas),
                                         Respuesta(texto="listo")])
    with espacio(conn, ws) as cur:
        quien = _quien(cur, ws)
        cal = Calendario.desde_base(cur, ws)
        r = responder(cur, quien, "quedé trabado", proveedor, cal, chat_id=CHAT,
                      ahora=datetime.now(timezone.utc))
    conn.commit()
    return r, vistos


def _pendientes(conn, herramienta: str | None = None) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            "select id, herramienta from pending_action where estado = 'esperando'"
            + (" and herramienta = %s" if herramienta else ""),
            (herramienta,) if herramienta else ())
        return cur.fetchall()


def _mensajes_con_botones(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox where chat_id = %s "
                    "and pending_action_id is not null", (CHAT,))
        return cur.fetchone()["n"]


def _rechazos(conn, herramienta: str) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from audit_log where accion = %s",
                    (f"herramienta_rechazada:{herramienta}",))
        return cur.fetchone()["n"]


def test_dos_escrituras_en_la_misma_vuelta_abren_una_sola_vista_previa(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    a, b = _dos_tareas(conn, ws)

    r, vistos = _turno(conn, ws, monkeypatch,
                       [_bloqueo("c1", a), _bloqueo("c2", b)])

    (unica,) = _pendientes(conn, "registrar_bloqueo")           # una sola abierta
    assert r.confirmaciones == ["registrar_bloqueo"]
    assert _mensajes_con_botones(conn) == 1                     # un juego de botones
    primera, segunda = vistos
    assert primera["is_error"] is False
    assert segunda["is_error"] is True                          # se rechazó la segunda
    assert json.loads(segunda["content"])["ejecutado"] is False
    assert _rechazos(conn, "registrar_bloqueo") == 1            # y quedó auditada
    with admin(conn) as cur:
        cur.execute("select args from pending_action where id = %s", (unica["id"],))
        assert cur.fetchone()["args"]["tarea_id"] == a          # ganó la primera


def test_una_escritura_despues_de_ofrecer_opciones_se_rechaza(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    a, _b = _dos_tareas(conn, ws)

    r, vistos = _turno(conn, ws, monkeypatch, [
        Llamada("c1", "ofrecer_opciones", {
            "pregunta": "¿A o B?", "opciones": [{"texto": "A"}, {"texto": "B"}]}),
        _bloqueo("c2", a)])

    assert _pendientes(conn, "registrar_bloqueo") == []         # no abrió la vista previa
    assert len(_pendientes(conn, P.SENTINEL_OPCIONES_MODELO)) == 1
    assert r.elecciones == ["ofrecer_opciones"] and r.confirmaciones == []
    assert vistos[1]["is_error"] is True
    assert _mensajes_con_botones(conn) == 1


def test_ofrecer_opciones_despues_de_una_vista_previa_se_rechaza(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    a, _b = _dos_tareas(conn, ws)

    r, vistos = _turno(conn, ws, monkeypatch, [
        _bloqueo("c1", a),
        Llamada("c2", "ofrecer_opciones", {
            "pregunta": "¿A o B?", "opciones": [{"texto": "A"}, {"texto": "B"}]})])

    assert len(_pendientes(conn, "registrar_bloqueo")) == 1
    assert _pendientes(conn, P.SENTINEL_OPCIONES_MODELO) == []
    assert r.confirmaciones == ["registrar_bloqueo"] and r.elecciones == []
    assert vistos[1]["is_error"] is True
    assert _mensajes_con_botones(conn) == 1


def test_una_lectura_despues_de_la_pregunta_abierta_si_se_ejecuta(
        corework, conn, monkeypatch):
    ws = corework.workspace_id
    a, _b = _dos_tareas(conn, ws)

    r, vistos = _turno(conn, ws, monkeypatch,
                       [_bloqueo("c1", a), Llamada("c2", "consultar_tareas", {})])

    assert len(_pendientes(conn, "registrar_bloqueo")) == 1
    assert vistos[1]["is_error"] is False                       # la lectura corrió
    assert _rechazos(conn, "consultar_tareas") == 0
    assert "consultar_tareas" in r.acciones


def test_una_escritura_rechazada_por_negocio_no_cierra_el_turno_a_las_siguientes(
        corework, conn, monkeypatch):
    # Sólo lo que deja esperando a la persona cierra el turno: una tarea que no
    # existe se rechaza como siempre y la llamada siguiente sigue su camino.
    ws = corework.workspace_id
    a, _b = _dos_tareas(conn, ws)

    r, vistos = _turno(conn, ws, monkeypatch, [
        _bloqueo("c1", "00000000-0000-0000-0000-000000000000"), _bloqueo("c2", a)])

    assert len(_pendientes(conn, "registrar_bloqueo")) == 1
    assert r.confirmaciones == ["registrar_bloqueo"]
    assert vistos[0]["is_error"] is True and vistos[1]["is_error"] is False
    assert _rechazos(conn, "registrar_bloqueo") == 1            # la de negocio, no la del turno


@pytest.mark.parametrize("orden", ["antes", "despues"])
def test_lo_que_abrio_una_vuelta_no_se_repite_en_la_siguiente(
        corework, conn, monkeypatch, orden):
    # La vuelta que deja algo esperando ya cierra el turno (`break`): el modelo
    # no llega a pedir una segunda. Queda como red: una sola pregunta abierta.
    ws = corework.workspace_id
    a, b = _dos_tareas(conn, ws)
    llamadas = ([_bloqueo("c1", a)] if orden == "antes" else
                [Llamada("c0", "consultar_tareas", {}), _bloqueo("c1", a)])

    _turno(conn, ws, monkeypatch, llamadas)

    assert len(_pendientes(conn)) == 1


def test_una_escritura_despues_de_una_eleccion_de_herramienta_se_rechaza(
        corework, conn, monkeypatch):
    """La elección que pide una herramienta (`NecesitaElegir`) también termina
    el turno: una escritura que la sigue en la misma vuelta se rechaza antes de
    ejecutarse (review-faccc0e9d83561b3)."""
    from leda import herramientas as H

    ws = corework.workspace_id
    a, _b = _dos_tareas(conn, ws)
    ejecutadas: list[str] = []

    def _ambiguo(cur, quien, nombre, args, **kw):
        ejecutadas.append(nombre)
        e = H.NecesitaElegir("¿En cuál tarea?", "tarea_id",
                             [("Programar PLC", a), ("Revisar variador", _b)])
        e.herramienta = nombre
        raise e

    monkeypatch.setattr(H, "ejecutar", _ambiguo)

    r, vistos = _turno(conn, ws, monkeypatch, [
        Llamada("c1", "actualizar_estado", {"causa": "x"}),
        _bloqueo("c2", a)])

    assert ejecutadas == ["actualizar_estado"]                  # la segunda no corrió
    assert r.elecciones == ["actualizar_estado"] and r.confirmaciones == []
    assert len(_pendientes(conn, "actualizar_estado")) == 1     # una sola elección
    assert _pendientes(conn, "registrar_bloqueo") == []
    assert _mensajes_con_botones(conn) == 1                     # un juego de botones
    assert vistos[-1]["is_error"] is True                       # rechazo, con la verdad
    assert _rechazos(conn, "registrar_bloqueo") == 1            # y auditado
