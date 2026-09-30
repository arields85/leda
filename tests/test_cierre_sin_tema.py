"""Dejar de lado una pregunta que no es un tema (R4-H2; ADR 0013).

Cuarta ronda por Telegram: después de tocar "Quiero consultar otra cosa" sobre los
botones del saludo, Prisma dijo "Dale, dejamos de lado «Hola Ariel, ¿en qué te
ayudo?». Escribime qué necesitás." Regla del usuario (2026-09-30): "Dale, escribime
qué necesitás." Lo que se deja de lado se nombra sólo cuando es un tema real (una
tarea, una propuesta, un alta); el saludo no lo es. Se decide por la marca
estructural que guarda la pregunta (`args.saludo`), nunca por su texto.
"""

from __future__ import annotations

from prisma import pendientes as P
from prisma.db import admin
from prisma.llm import IntentAction, IntentRoute, ProveedorGuionado

from tests.test_pedir_cambios_extremo_a_extremo import (  # noqa: F401
    _mensaje, _opciones, _pendiente, _tg, _tocar, cliente)

CIERRE_SIN_TEMA = "Dale, escribime qué necesitás."


def _guion(monkeypatch, *rutas):
    proveedor = ProveedorGuionado(guion=[], rutas=list(rutas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _tocar_salida(cliente, conn, ws, tg: int) -> None:
    with admin(conn) as cur:
        pid = _pendiente(cur, ws, P.SENTINEL_OPCIONES_MODELO, chat_id=tg)
        token = next(f["token"] for f in _opciones(cur, pid)
                     if "consultar otra cosa" in f["etiqueta"])
    assert _tocar(cliente, token, tg).status_code == 200


def _ultimo_cuerpo(conn, ws, tg: int) -> str:
    with admin(conn) as cur:
        cur.execute("select cuerpo from message_outbox where workspace_id = %s and "
                    "chat_id = %s order by programado_para desc, dedupe_key desc "
                    "limit 1", (ws, tg))
        return cur.fetchone()["cuerpo"]


def _abrir_generica(conn, ws, tg: int, pregunta: str, **marcas) -> None:
    from datetime import datetime, timedelta, timezone

    from prisma.db import espacio

    from tests.test_pedir_cambios_extremo_a_extremo import _quien

    ahora = datetime.now(timezone.utc)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        P.registrar(cur, quien, herramienta=P.SENTINEL_OPCIONES_MODELO,
                    args={"pregunta": pregunta, "cierre_generico": True, **marcas},
                    resumen=pregunta, vence_en=ahora + timedelta(hours=8),
                    campo="eleccion",
                    opciones=[("Otra", {"tipo": "salida"}),
                              (P.ETIQUETA_SALIR_OPCIONES, {"tipo": "salida"})],
                    chat_id=tg)
    conn.commit()


def test_dejar_de_lado_el_saludo_no_lo_nombra(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()
    _guion(monkeypatch, IntentRoute(IntentAction.GREETING))
    assert _mensaje(cliente, tg, "hola").status_code == 200

    _tocar_salida(cliente, conn, ws, tg)

    assert _ultimo_cuerpo(conn, ws, tg) == CIERRE_SIN_TEMA


def test_se_decide_por_la_marca_y_no_por_el_texto(cliente, conn, corework,
                                                  monkeypatch):
    """Una pregunta con la marca del saludo no se nombra aunque su texto sea
    cualquiera (la prueba de abajo cubre la inversa)."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()

    _abrir_generica(conn, ws, tg, "¿Cuál de tus tareas querés mirar?", saludo=True)
    _tocar_salida(cliente, conn, ws, tg)
    assert _ultimo_cuerpo(conn, ws, tg) == CIERRE_SIN_TEMA


def test_una_pregunta_sobre_un_tema_sigue_nombrandose(cliente, conn, corework,
                                                      monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tg = _tg(cur, "Nahuel Gimenez")
    conn.commit()

    _abrir_generica(conn, ws, tg, "Hola Nahuel, ¿en qué te ayudo?")
    _tocar_salida(cliente, conn, ws, tg)

    assert _ultimo_cuerpo(conn, ws, tg) == (
        "Dale, dejamos de lado «Hola Nahuel, ¿en qué te ayudo?». "
        "Escribime qué necesitás.")
