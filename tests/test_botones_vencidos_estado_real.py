"""Un botón vencido contesta con el estado real y un próximo paso (C0-5).

Ronda C0-C (2026-10-02, 12:50:48, hallazgo H4): con el borrador ya confirmado y la
tarea creada, Marcos tocó Modificar en el resumen viejo y Leda contestó "Ese pedido
ya no está vigente. Si sigue haciendo falta, escribime y lo vemos de nuevo.": no dice
qué pasó con lo que el botón tocaba (la tarea ya existe) ni qué se puede hacer ahora.
Es la misma clase que C-3 de `main` (tocar "Aprobar" en un aviso viejo de una tarea
ya terminada). Constitución §8 (ningún mensaje deja a la persona sin un próximo paso)
y ADR 0013, regla 3 (estado real y sólo opciones posibles).

Un solo mecanismo para todo botón vencido (`gateway._contestar_boton_vencido`): el
estado real sale de lo que el botón tocaba (el borrador, la tarea, la pregunta) y el
próximo paso es lo que se puede hacer ahora con eso: con una tarea, su menú con los
botones que correspondan; con un borrador cancelado, armarla de nuevo; si no se puede
leer a qué correspondía, se dice y se ofrece un paso general.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from leda import gateway
from leda import pendientes as P
from leda.db import admin, autoridad, espacio
from leda.salida import etiqueta_sin_icono

from tests.test_alta_eleccion_confirmacion import (
    _actor, _alta_en_confirmacion, _nuevas, _salidas, _tocar_boton, _usuario)
from tests.test_task_intake import _callback_client
from tests.toques import FUERA_DE_LA_VENTANA, envejecer_toques

CALLEJON_SIN_SALIDA = ("Ese pedido ya no está vigente. Si sigue haciendo falta, "
                       "escribime y lo vemos de nuevo.")


# ----------------------------------------------------------------- ayudas

def _token(conn, pid, etiqueta) -> str:
    """El token del botón aunque su acción ya esté cerrada: un toque tardío usa el
    mismo botón de siempre."""
    with admin(conn) as cur:
        cur.execute("select token from pending_action_option "
                    "where pending_action_id = %s and etiqueta like %s",
                    (pid, f"%{etiqueta}"))
        return cur.fetchone()["token"]


def _tocar(client, conn, user, pid, etiqueta) -> list[dict]:
    antes = _salidas(conn, user)
    assert _tocar_boton(client, conn, _token(conn, pid, etiqueta),
                        user).status_code == 200
    return _nuevas(conn, user, antes)


def _botones(conn, fila) -> list[str]:
    """Las etiquetas (sin ícono) de los botones que lleva una respuesta."""
    assert fila["pending_action_id"] is not None, fila["cuerpo"]
    with admin(conn) as cur:
        return [etiqueta_sin_icono(o.etiqueta)
                for o in P.opciones(cur, fila["pending_action_id"])]


def _tarea(conn) -> dict:
    with admin(conn) as cur:
        cur.execute("select id, titulo, estado from task")
        (tarea,) = cur.fetchall()
        return tarea


def _cliente(conn, monkeypatch, authority_conn):
    """El webhook real, con la autoridad del borrador en su propia conexión."""
    client = _callback_client(conn, monkeypatch)
    monkeypatch.setattr(gateway, "_authority_conn", lambda: authority_conn)
    return client


def _tarea_creada(intake_world, conn, monkeypatch, authority_conn):
    """Taylor Quinn pide una tarea para Sam North, que aprueba ella misma, y la
    confirma con el botón: el borrador queda convertido y la tarea creada."""
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    user = _usuario(intake_world)
    client = _cliente(conn, monkeypatch, authority_conn)
    respuesta = _tocar(client, conn, user, pid, "Confirmar")
    assert any("quedó comprometida" in f["cuerpo"] for f in respuesta)
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)
    return rid, pid, client, user


def _sin_callejon(respuesta: list[dict]) -> dict:
    """Una sola respuesta visible, y no la del callejón sin salida."""
    (fila,) = respuesta
    assert CALLEJON_SIN_SALIDA not in fila["cuerpo"]
    return fila


# ------------------------------------- (a) el resumen de un borrador ya convertido

def test_modificar_en_el_resumen_ya_confirmado_dice_que_la_tarea_existe_y_ofrece_su_menu(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid, client, user = _tarea_creada(intake_world, conn, monkeypatch,
                                           authority_conn)
    tarea = _tarea(conn)

    fila = _sin_callejon(_tocar(client, conn, user, pid, "Modificar"))

    assert "ya quedó creada" in fila["cuerpo"]
    assert f"«{tarea['titulo']}»" in fila["cuerpo"]
    # Lo que se puede hacer ahora con la tarea: su menú, calculado por el código.
    assert "Ver detalle" in _botones(conn, fila)
    assert _tarea(conn)["estado"] == tarea["estado"]               # nada cambió


def test_confirmar_otra_vez_fuera_de_la_ventana_tambien_da_el_estado_real(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid, client, user = _tarea_creada(intake_world, conn, monkeypatch,
                                           authority_conn)

    fila = _sin_callejon(_tocar(client, conn, user, pid, "Confirmar"))

    assert "ya quedó creada" in fila["cuerpo"]
    assert "Ver detalle" in _botones(conn, fila)
    with admin(conn) as cur:
        cur.execute("select count(*) n from task")
        assert cur.fetchone()["n"] == 1                              # una sola tarea


# --------------------------------------------- (b) otras clases de botón vencido

def test_aprobar_en_un_aviso_viejo_dice_el_estado_de_la_tarea_y_ofrece_su_menu(
        intake_world, conn, monkeypatch, authority_conn):
    """C-3 de `main`: el aviso de entrega con Aprobar y Pedir cambios, ya vencido."""
    rid, pid, client, user = _tarea_creada(intake_world, conn, monkeypatch,
                                           authority_conn)
    tarea = _tarea(conn)
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        aviso = P.registrar(
            cur, _actor(cur, intake_world), herramienta=P.SENTINEL_MENU_TAREA,
            args={"tarea_id": str(tarea["id"]), "titulo": tarea["titulo"],
                  "aviso": P.AVISO_ENTREGA},
            resumen=f"Sam North entregó «{tarea['titulo']}»",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=8),
            campo="eleccion",
            opciones=[("Aprobar", {"accion": "aprobar"}),
                      ("Pedir cambios", {"accion": "pedir_cambios"})],
            chat_id=user)
        cur.execute("update pending_action set estado = 'vencida' where id = %s",
                    (aviso.id,))
    conn.commit()

    fila = _sin_callejon(_tocar(client, conn, user, aviso.id, "Aprobar"))

    assert f"«{tarea['titulo']}»" in fila["cuerpo"]
    assert "Asignada" in fila["cuerpo"]                              # su estado real
    assert "Aprobar" not in _botones(conn, fila)                     # sólo lo posible
    assert "Ver detalle" in _botones(conn, fila)
    assert _tarea(conn)["estado"] == tarea["estado"]


def test_modificar_en_un_borrador_cancelado_lo_dice_y_ofrece_armarla_de_nuevo(
        intake_world, conn, monkeypatch, authority_conn):
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    user = _usuario(intake_world)
    ws = intake_world["north-lab"]["id"]
    client = _cliente(conn, monkeypatch, authority_conn)
    with autoridad(authority_conn) as cur:
        assert P.resolver_borrador(cur, ws, _token(conn, pid, "Cancelar"),
                                   user, user).cancelada

    fila = _sin_callejon(_tocar(client, conn, user, pid, "Modificar"))

    assert "se canceló" in fila["cuerpo"]
    assert "no se creó" in fila["cuerpo"]
    assert "armamos de nuevo" in fila["cuerpo"]                      # el próximo paso


def test_un_boton_cuyo_destino_no_se_puede_leer_lo_dice_y_ofrece_un_paso_general(
        intake_world, conn, monkeypatch, authority_conn):
    """Un botón de algo que ya no existe (la acción se borró): se dice que no se
    puede ver a qué correspondía, sin inventar, y se ofrece seguir por escrito."""
    user = _usuario(intake_world)
    client = _cliente(conn, monkeypatch, authority_conn)
    antes = _salidas(conn, user)

    assert _tocar_boton(client, conn, "token-que-no-existe", user).status_code == 200

    fila = _sin_callejon(_nuevas(conn, user, antes))
    assert fila["cuerpo"] == gateway.AVISO_PEDIDO_NO_VIGENTE
    assert "no puedo ver a qué correspondía" in fila["cuerpo"]


def test_en_un_chat_privado_un_boton_viejo_del_borrador_vuelve_a_hacer_la_pregunta_abierta(
        intake_world, conn, monkeypatch, authority_conn):
    """El borrador sigue abierto y la persona tiene una pregunta abierta (el selector
    de Modificar): el próximo paso es esa pregunta de nuevo, con sus botones, en el
    mismo mensaje (una sola rama, ADR 0013 regla 1)."""
    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")
    user = _usuario(intake_world)
    client = _cliente(conn, monkeypatch, authority_conn)

    def tocar_modificar_en_privado() -> list[dict]:
        antes = _salidas(conn, user)
        respuesta = client.post(
            "/telegram/north-lab",
            json={"callback_query": {
                "id": f"cb-privado-{len(antes)}", "from": {"id": user},
                "data": P.CALLBACK_PREFIJO + _token(conn, pid, "Modificar"),
                "message": {"message_id": 7,
                            "chat": {"id": user, "type": "private"}}}},
            headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"})
        assert respuesta.status_code == 200
        return _nuevas(conn, user, antes)

    (selector,) = tocar_modificar_en_privado()
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)

    fila = _sin_callejon(tocar_modificar_en_privado())

    assert fila["cuerpo"].startswith("Ese botón ya no está vigente; el borrador")
    assert "sigue abierto" in fila["cuerpo"]
    assert fila["cuerpo"].endswith(selector["cuerpo"])              # la pregunta abierta
    assert fila["intake_choice_set_id"] == selector["intake_choice_set_id"]
