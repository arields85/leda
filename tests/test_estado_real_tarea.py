"""Decir el estado real de la tarea y no esconder lo que falta (T9-R3, ADR 0013
regla 3; hallazgos R3-H20 y R3-H16).

- H20: evidencia registrada sobre una tarea que sigue en curso. La respuesta dice
  que la evidencia quedó registrada, que la tarea sigue en curso (nadie la puede
  revisar todavía) y ofrece la entrega como botón, sólo si el menú de la tarea
  la ofrece hoy. La entrega sigue siendo explícita.
- H16: el motivo de "Pedir cambios" se ve en toda lectura de la tarea (encabezado
  del menú y detalle) hasta la nueva entrega, no sólo en un aviso.

Nada toca la red ni el modelo real.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from leda import agente
from leda import herramientas as H
from leda import menu_tarea as M
from leda import pendientes as P
from leda.calendario import Calendario
from leda.db import admin, espacio
from leda.salida import etiquetas_coinciden

from tests.test_menu_tarea import (_abrir_menu, _opciones, _pendiente, _quien,
                                   _resumen_menu, _tarea, _telegram_id, _tocar,
                                   cliente)  # noqa: F401

RESPONSABLE = "Nahuel Gimenez"
APROBADOR = "Marcos Tarquini"        # aprueba a Nahuel en el pack de prueba
TITULO = "Programar HMI línea 2"
MOTIVO = "falta la captura del tablero con la hora visible"


def _ultima_salida(conn, chat_id) -> dict:
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo, pending_action_id from message_outbox
                where chat_id = %s order by programado_para desc, id desc limit 1""",
            (chat_id,))
        return cur.fetchone()


def _etiquetas(conn, pid) -> list[str]:
    with admin(conn) as cur:
        return [o["etiqueta"] for o in _opciones(cur, pid)]


# ------------------------------------------------- H20: evidencia sobre lo no entregado

def _confirmar_evidencia(cliente, conn, ws, tid, persona=RESPONSABLE):
    """La vista previa de `adjuntar_evidencia` y el toque en Confirmar. Devuelve
    el chat de quien la adjuntó."""
    with espacio(conn, ws) as cur:
        quien = _quien(cur, persona, ws)
        tg = _telegram_id(cur, persona)
        try:
            H.ejecutar(cur, quien, "adjuntar_evidencia", {
                "tarea_id": tid, "tipo": "texto", "descripcion": "acá está el link"},
                chat_id=tg)
        except H.NecesitaConfirmacion as e:
            agente._encolar_confirmacion(
                cur, quien, tg, e, Calendario.desde_base(cur, ws),
                datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, "adjuntar_evidencia")
        token = P.opcion_por_etiqueta(cur, pid, "Confirmar").token
    conn.commit()
    assert _tocar(cliente, token, tg).status_code == 200
    return tg


@pytest.mark.parametrize("estado, dice", [("en_curso", "sigue en curso"),
                                          ("asignada", "sigue asignada")])
def test_evidencia_sobre_una_tarea_no_entregada_dice_que_sigue_y_ofrece_entregarla(
        cliente, conn, corework, estado, dice):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado=estado)
    conn.commit()

    tg = _confirmar_evidencia(cliente, conn, ws, tid)

    salida = _ultima_salida(conn, tg)
    assert "quedó registrada" in salida["cuerpo"]
    assert dice in salida["cuerpo"]
    assert TITULO in salida["cuerpo"]
    assert "no la entregaste" in salida["cuerpo"]
    # La entrega, como opción real: el mismo botón que ofrece el menú de la tarea.
    assert salida["pending_action_id"]
    (etiqueta,) = _etiquetas(conn, salida["pending_action_id"])
    assert etiquetas_coinciden(etiqueta, "Ya la terminé")


def test_el_boton_de_entrega_abre_la_vista_previa_y_no_entrega_solo(
        cliente, conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_curso")
    conn.commit()
    tg = _confirmar_evidencia(cliente, conn, ws, tid)
    boton = _ultima_salida(conn, tg)["pending_action_id"]
    with admin(conn) as cur:
        (fila,) = _opciones(cur, boton)

    assert _tocar(cliente, fila["token"], tg).status_code == 200

    # Sigue sin entregarse: queda una vista previa esperando su Confirmar.
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "en_curso"
    salida = _ultima_salida(conn, tg)
    assert "Confirmar" in " ".join(_etiquetas(conn, salida["pending_action_id"]))


def test_evidencia_sobre_una_tarea_en_revision_dice_que_sigue_en_revision_sin_boton(
        cliente, conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    conn.commit()

    tg = _confirmar_evidencia(cliente, conn, ws, tid)

    salida = _ultima_salida(conn, tg)
    assert "quedó registrada" in salida["cuerpo"] and "sigue en revisión" in salida["cuerpo"]
    assert salida["pending_action_id"] is None       # nada que entregar


def test_no_se_ofrece_entregar_una_tarea_bloqueada(cliente, conn, corework):
    """Las opciones salen de lo que el menú permite hoy: una tarea bloqueada no se
    entrega."""
    from tests.test_menu_tarea import _bloquear

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="asignada")
        _bloquear(cur, ws, tid)
    conn.commit()

    tg = _confirmar_evidencia(cliente, conn, ws, tid)

    salida = _ultima_salida(conn, tg)
    assert "quedó registrada" in salida["cuerpo"] and "bloqueada" in salida["cuerpo"]
    assert salida["pending_action_id"] is None


# ------------------------------------------------- H16: el motivo de Pedir cambios

def _pedir_cambios(conn, ws, tid, comentario=MOTIVO):
    """"Pedir cambios" por el camino real de la herramienta, como el aprobador y
    con la vista previa ya confirmada: la aprobación `rechazado` con su comentario
    y la tarea de vuelta en curso."""
    with espacio(conn, ws) as cur:
        quien = _quien(cur, APROBADOR, ws)
        H.ejecutar(cur, quien, "pedir_cambios_tarea",
                   {"tarea_id": tid, "comentario": comentario},
                   ya_confirmada=True, chat_id=_telegram_id(cur, APROBADOR))
    conn.commit()


def _entregar_de_nuevo(conn, ws, tid):
    with espacio(conn, ws) as cur:
        quien = _quien(cur, RESPONSABLE, ws)
        H.ejecutar(cur, quien, "actualizar_estado", {
            "tarea_id": tid, "estado": "en_revision",
            "evidencia_texto": "corregido"},
            ya_confirmada=True, chat_id=_telegram_id(cur, RESPONSABLE))
    conn.commit()


@pytest.mark.parametrize("quien", [RESPONSABLE, APROBADOR, "Mariano Naim"],
                         ids=["responsable", "aprobador", "otra_persona"])
def test_el_motivo_esta_en_el_encabezado_del_menu_para_cualquiera(
        quien, cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    _pedir_cambios(conn, ws, tid)

    _abrir_menu(cliente, conn, ws, monkeypatch, tid, quien)
    resumen = _resumen_menu(conn, ws)

    assert MOTIVO in resumen
    assert "Cambios pedidos" in resumen
    assert resumen.count("?") == 1          # sigue siendo una sola pregunta


def test_el_encabezado_nombra_a_quien_pidio_los_cambios(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    _pedir_cambios(conn, ws, tid)

    _abrir_menu(cliente, conn, ws, monkeypatch, tid, RESPONSABLE)

    assert APROBADOR in _resumen_menu(conn, ws)


def test_el_motivo_esta_en_el_detalle(conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    _pedir_cambios(conn, ws, tid)

    with espacio(conn, ws) as cur:
        detalle = M.detalle_tarea(cur, tid)

    assert MOTIVO in detalle and "Cambios pedidos" in detalle


def test_el_motivo_deja_de_verse_con_la_nueva_entrega(conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    _pedir_cambios(conn, ws, tid)
    _entregar_de_nuevo(conn, ws, tid)

    with espacio(conn, ws) as cur:
        assert MOTIVO not in M.detalle_tarea(cur, tid)
        menu = M.calcular_menu(cur, _quien(cur, RESPONSABLE, ws), tid)
        assert MOTIVO not in M.encabezado_menu(menu)


def test_se_ve_el_pedido_mas_reciente(conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    _pedir_cambios(conn, ws, tid, "primer motivo")
    _entregar_de_nuevo(conn, ws, tid)
    _pedir_cambios(conn, ws, tid, "segundo motivo")

    with espacio(conn, ws) as cur:
        detalle = M.detalle_tarea(cur, tid)

    assert "segundo motivo" in detalle and "primer motivo" not in detalle


def test_sin_pedido_de_cambios_no_hay_linea_de_cambios(conn, corework):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_curso")
    conn.commit()

    with espacio(conn, ws) as cur:
        assert "Cambios pedidos" not in M.detalle_tarea(cur, tid)
        menu = M.calcular_menu(cur, _quien(cur, RESPONSABLE, ws), tid)
        assert "Cambios pedidos" not in M.encabezado_menu(menu)


def test_un_motivo_largo_no_rompe_el_mensaje_del_menu(
        cliente, conn, corework, monkeypatch):
    """El encabezado comparte el mensaje con los botones (límite de Telegram): el
    motivo se acorta, nunca deja el menú sin salir."""
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    _pedir_cambios(conn, ws, tid, "x" * 1500)

    _abrir_menu(cliente, conn, ws, monkeypatch, tid, RESPONSABLE)

    resumen = _resumen_menu(conn, ws)
    assert "Cambios pedidos" in resumen and len(resumen) < 1000
