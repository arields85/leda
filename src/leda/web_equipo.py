"""Ver el equipo desde la web (J7-3 de `odd/tasks/plataforma-jerarquias.md`; ADR 0023, decisiones 4
y 5; migración 0082).

Dos puertas con la misma forma: la del equipo, sólo para Dirección (el rol con la autoridad final),
que ve el suyo (`GET /app/api/equipo`); y la de administración, el administrador de plataforma, que
ve el de cualquier espacio (`GET /app/admin/api/espacios/{id}/equipo`). Lo decide la base
(`equipo_de` y `cambios_del_equipo`): la sesión de la puerta en cada llamada y el espacio fijado por
ella. Un referente o un integrante reciben 403, aunque la web les esconda la vista.

Devuelve las áreas, las personas, los roles, los problemas del equipo y la historia de sus cambios,
lo más nuevo primero. Nada de esto cambia el equipo: crear, dar de alta y los demás cambios son de
las porciones que siguen de la J7, y cada uno va a vivir en este módulo.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import Response

from .db import sin_espacio
from .web_app import (PUERTA_DE_ADMINISTRACION, PUERTA_DEL_EQUIPO, con_la_version_del_nucleo,
                      hash_del_token, json_de_la_web, leer_por_la_puerta, rechazo_de_la_base)

router = APIRouter(prefix="/app")

TEXTO_SIN_AUTORIDAD = "Organizar el equipo le corresponde a Dirección."


def _el_equipo(conn, puerta: str, token: str, espacio: str | None) -> Response:
    """El equipo y sus cambios, en una sola transacción; o lo que la base rechaza."""
    with sin_espacio(conn) as cur:
        con_la_version_del_nucleo(cur)
        cur.execute("select equipo_de(%s, %s, %s) as r", (puerta, hash_del_token(token), espacio))
        equipo: dict[str, Any] = cur.fetchone()["r"]
        rechazo = rechazo_de_la_base(equipo, puerta, TEXTO_SIN_AUTORIDAD)
        if rechazo is not None:
            return rechazo
        cur.execute("select cambios_del_equipo(%s, %s, %s) as r",
                    (puerta, hash_del_token(token), espacio))
        cambios: dict[str, Any] = cur.fetchone()["r"]
    rechazo = rechazo_de_la_base(cambios, puerta, TEXTO_SIN_AUTORIDAD)
    if rechazo is not None:
        return rechazo
    return json_de_la_web({**{k: v for k, v in equipo.items() if k != "ok"},
                           "cambios": cambios["cambios"]})


@router.get("/api/equipo")
def el_equipo_de_direccion(request: Request):
    """El equipo de la sesión, sólo para Dirección (403 a los demás)."""
    return leer_por_la_puerta(
        request, PUERTA_DEL_EQUIPO, None,
        lambda conn, token, espacio: _el_equipo(conn, PUERTA_DEL_EQUIPO, token, espacio))


@router.get("/admin/api/espacios/{espacio_id}/equipo")
def el_equipo_en_la_administracion(espacio_id: str, request: Request):
    """El equipo de un espacio, por la puerta de administración (ADR 0023, decisión 5)."""
    return leer_por_la_puerta(
        request, PUERTA_DE_ADMINISTRACION, espacio_id,
        lambda conn, token, espacio: _el_equipo(conn, PUERTA_DE_ADMINISTRACION, token, espacio))
