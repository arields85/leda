"""Vista previa en filas y recibo corto (T10-4, R3-H11, H14 y H9).

La vista previa de una herramienta que escribe pone un dato por línea, armada
en un solo lugar (`herramientas._filas`); el recibo al confirmar cuenta lo que
pasó en una oración, no repite la vista previa; y el estado se nombra de una
forma que se lee bien con cualquiera ("y vuelve a estar en curso", nunca "vuelve
a en curso").
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from prisma import herramientas as H
from prisma import pendientes as P
from prisma.db import admin, espacio
from tests.test_botones import _quien, _tarea, _telegram_id, _tocar, cliente  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]


def test_filas_pone_un_dato_por_linea():
    assert H._filas(("Tarea", "Programar PLC"), ("Estado actual", "Asignada")) == (
        "Tarea: Programar PLC\nEstado actual: Asignada")


def test_filas_admite_una_frase_suelta_y_saltea_lo_que_no_hay():
    assert H._filas(("Tarea", "X"), ("Impacto", None), (None, "La tarea sigue bloqueada.")) == (
        "Tarea: X\nLa tarea sigue bloqueada.")


def test_ninguna_preparacion_junta_datos_con_puntos_medios():
    """Un dato por línea sale de `_filas`, no de cada llamada: ningún texto de
    `herramientas.py` vuelve a juntar campos con " · "."""
    lineas = [
        f"{n}: {linea.strip()}"
        for n, linea in enumerate(
            (ROOT / "src" / "prisma" / "herramientas.py").read_text(encoding="utf-8").splitlines(), 1)
        if "·" in linea and not linea.lstrip().startswith("#")]
    assert lineas == []


@pytest.mark.parametrize("estado", sorted(H.ESTADOS_LEGIBLES))
def test_el_estado_se_nombra_bien_con_cualquiera(estado):
    frase = f"La tarea vuelve a {H._estar(estado)}."
    assert frase == f"La tarea vuelve a estar {H.ESTADOS_LEGIBLES[estado].lower()}."
    assert "vuelve a en " not in frase


def test_el_recibo_de_una_entrega_agradece_y_no_nombra_estado_en_mayuscula():
    recibo = H.recibo_de_estado("Programar HMI línea 2", "en_revision")
    assert recibo == "Gracias. La tarea «Programar HMI línea 2» pasó a revisión."


@pytest.mark.parametrize("estado", ["asignada", "en_curso", "bloqueada", "terminada"])
def test_el_recibo_de_otro_estado_no_lleva_el_estado_en_mayuscula(estado):
    recibo = H.recibo_de_estado("Programar PLC", estado)
    assert recibo == (
        f"La tarea «Programar PLC» pasó a estar {H.ESTADOS_LEGIBLES[estado].lower()}.")


def _vista_previa_de_bloqueo(conn, ws):
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tarea = _tarea(cur, ws)
        try:
            H.ejecutar(cur, quien, "registrar_bloqueo",
                       {"tarea_id": tarea, "causa": "falta el switch",
                        "impacto": "la línea 2 no arranca"})
        except H.NecesitaConfirmacion as e:
            return e.resumen
    raise AssertionError("tenía que pedir confirmación")


def test_la_vista_previa_de_un_bloqueo_sale_en_filas(corework, conn):
    assert _vista_previa_de_bloqueo(conn, corework.workspace_id).split("\n") == [
        "Tarea: Programar PLC",
        "Causa del bloqueo: falta el switch",
        "Impacto: la línea 2 no arranca",
        "Estado actual: Asignada",
        "Nuevo estado: Bloqueada",
        "",
        "Todavía no se aplicó ningún cambio."]


def _confirmar(cliente, conn, ws, herramienta, args_de_tarea):
    """Registra la acción pendiente, la confirma por botón y devuelve el último
    mensaje que le llegó a la persona."""
    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Marcos Tarquini", ws)
        tarea = _tarea(cur, ws)
        p = P.registrar(
            cur, quien, herramienta=herramienta, args=args_de_tarea(tarea),
            resumen="vista previa",
            vence_en=datetime.now(timezone.utc) + timedelta(days=1), chat_id=500)
        token = P.opcion_por_etiqueta(cur, p.id, "Confirmar").token
        tg = _telegram_id(cur, "Marcos Tarquini")
    conn.commit()
    assert _tocar(cliente, token, tg).status_code == 200
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox
                where workspace_id = %s and chat_id = %s
               order by programado_para desc limit 1""", (ws, tg))
        return cur.fetchone()["cuerpo"]


def test_el_recibo_de_un_bloqueo_cuenta_lo_que_paso_sin_repetir_la_vista_previa(
        cliente, conn, corework):
    cuerpo = _confirmar(
        cliente, conn, corework.workspace_id, "registrar_bloqueo",
        lambda t: {"tarea_id": t, "causa": "falta el switch"})
    assert cuerpo == "Registré el bloqueo en «Programar PLC»: la tarea quedó bloqueada."
    assert "Causa del bloqueo" not in cuerpo and "Hecho" not in cuerpo


def test_el_recibo_de_pasar_a_en_curso_lee_bien(cliente, conn, corework):
    cuerpo = _confirmar(
        cliente, conn, corework.workspace_id, "actualizar_estado",
        lambda t: {"tarea_id": t, "estado": "en_curso"})
    assert cuerpo == "La tarea «Programar PLC» pasó a estar en curso."
