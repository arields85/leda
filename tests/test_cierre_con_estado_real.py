"""Un cambio rechazado cierra con el estado real de la tarea (T10-7, decisión del
usuario, 2026-09-30).

Cuando Leda no hace algo sobre una tarea porque el cambio se rechazó, el mensaje
no cierra con "Estado: sin cambios." -- que no dice de qué tarea ni cómo está --,
sino con lo que es cierto de ella ahora: "«Programar PLC» sigue en revisión.". Es
una garantía del servidor, con la misma técnica que las demás guardas de
`agente.py`: el dato sale de la base, no de las palabras del modelo.

- Con UNA tarea clara en el turno, esa línea reemplaza al aviso de "sin cambios".
- Sin una única tarea clara, el aviso sigue como siempre.
- Una consulta o un cambio ejecutado no llevan la línea.
"""

from __future__ import annotations

from datetime import datetime, timezone

from leda.agente import responder
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.llm import Llamada, ProveedorGuionado, Respuesta
from leda.salida import NO_EFFECT_STATUS

from tests.banco.corrida import sembrar_precondiciones
from tests.test_menu_tarea import _quien

TITULO = "Programar PLC"
LINEA = f"«{TITULO}» sigue en revisión."


def _sembrar(conn, ws, *, estado="en_revision", dos=False):
    with admin(conn) as cur:
        tareas = [{"id": "t1", "titulo": TITULO, "area": "ot",
                   "responsable": "Marcos Tarquini", "estado": estado}]
        if dos:
            tareas.append({"id": "t2", "titulo": "Reporte semanal", "area": "ot",
                           "responsable": "Marcos Tarquini",
                           "estado": "en_curso"})
        ids = sembrar_precondiciones(cur, ws, {"tareas": tareas})
    conn.commit()
    return ids


def _turno(conn, ws, guion, claras, *, persona="Nahuel Gimenez",
           texto="aprobá el trabajo de Programar PLC"):
    proveedor = ProveedorGuionado(guion=list(guion))
    with espacio(conn, ws) as cur:
        quien = _quien(cur, persona, ws)
        cal = Calendario.desde_base(cur, ws)
        resultado = responder(cur, quien, texto, proveedor, cal, chat_id=9010,
                              ahora=datetime.now(timezone.utc),
                              tareas_resueltas_claras=claras)
    conn.commit()
    return resultado


def _aprobar_ajena(tid):
    return Respuesta(llamadas=[Llamada("c1", "aprobar_tarea", {"tarea_id": tid})])


# ---------------------------------------------------------------------------
# Lo que no lleva la línea
# ---------------------------------------------------------------------------

def test_una_consulta_sobre_la_tarea_no_lleva_la_linea(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    r = _turno(conn, ws, [Respuesta(texto="Vence el viernes.")],
               {ids["t1"]: TITULO})

    assert "sigue" not in r.texto


def test_un_cambio_ejecutado_no_lleva_la_linea(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws, estado="asignada")
    guion = [Respuesta(llamadas=[Llamada(
                "c1", "actualizar_estado",
                {"tarea_id": ids["t1"], "estado": "en_curso"})]),
             Respuesta(texto="Listo, la empezaste.")]

    r = _turno(conn, ws, guion, {ids["t1"]: TITULO}, persona="Marcos Tarquini",
               texto="empecé Programar PLC")

    assert "sigue" not in r.texto


# ---------------------------------------------------------------------------
# Un cambio intentado que se rechazó: la línea reemplaza a "Estado: sin cambios."
# ---------------------------------------------------------------------------

def test_un_rechazo_con_una_tarea_clara_cierra_con_su_estado_en_vez_de_sin_cambios(
        corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    r = _turno(conn, ws, [_aprobar_ajena(ids["t1"]),
                          Respuesta(texto="No pude aprobarla."),
                          Respuesta(texto="No pude aprobarla, no es tu tarea.")],
               {ids["t1"]: TITULO})

    assert r.acciones == []
    assert r.texto.endswith(LINEA)
    assert NO_EFFECT_STATUS not in r.texto


def test_un_rechazo_sin_tarea_clara_conserva_estado_sin_cambios(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws)

    r = _turno(conn, ws, [_aprobar_ajena(ids["t1"]),
                          Respuesta(texto="No pude aprobarla."),
                          Respuesta(texto="No pude aprobarla, no es tu tarea.")],
               None)

    assert r.texto.endswith(NO_EFFECT_STATUS)


def test_un_rechazo_con_dos_tareas_claras_conserva_estado_sin_cambios(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws, dos=True)

    r = _turno(conn, ws, [_aprobar_ajena(ids["t1"]),
                          Respuesta(texto="No pude aprobarla."),
                          Respuesta(texto="No pude aprobarla, no es tu tarea.")],
               {ids["t1"]: TITULO, ids["t2"]: "Reporte semanal"})

    assert r.texto.endswith(NO_EFFECT_STATUS)


def test_el_estado_sale_de_la_base_no_de_lo_que_dijo_el_modelo(corework, conn):
    ws = corework.workspace_id
    ids = _sembrar(conn, ws, estado="en_curso")

    r = _turno(conn, ws, [_aprobar_ajena(ids["t1"]),
                          Respuesta(texto="No pude aprobarla."),
                          Respuesta(texto=f"«{TITULO}» está en revisión, esperá.")],
               {ids["t1"]: TITULO})

    assert r.texto.endswith(f"«{TITULO}» sigue en curso.")
    assert NO_EFFECT_STATUS not in r.texto
