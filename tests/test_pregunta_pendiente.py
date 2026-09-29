"""Una pregunta pendiente es contexto, no una trampa (T9-R1a, ADR 0013
regla 1, primera etapa: el dato pedido desde el menú de una tarea).

Con una pregunta abierta ("Ya la terminé" pide la evidencia, "Informar un
bloqueo" pide la causa), el mensaje siguiente pasa por el ruteo tipado, que
sólo devuelve un comando de una lista cerrada; el código ejecuta un manejo
determinista por comando. Regresión del hallazgo R3-H17: un "hola" quedó como
"Evidencia: hola" en la vista previa de la entrega.

Los ruteos se guionan con `ProveedorGuionado`; ninguna prueba toca la red ni
el modelo real.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from prisma import gateway
from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
                         RespectoPendiente, Respuesta, RouteEnvelope)

from tests.test_menu_tarea import (_abrir_menu, _mensaje, _quien,  # noqa: F401
                                   _tarea, _tocar_accion, cliente)

TITULO = "Programar HMI línea 2"


def _ruta(comando: RespectoPendiente | None) -> IntentRoute:
    return IntentRoute(IntentAction.NORMAL_CONVERSATION,
                       respecto_pendiente=comando)


def _con_rutas(monkeypatch, rutas, guion=()) -> ProveedorGuionado:
    proveedor = ProveedorGuionado(guion=list(guion), rutas=list(rutas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _abiertas(conn) -> int:
    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from pending_action
                where herramienta = %s and modificar_pedido_en is not null
                  and modificacion_consumida_en is null""",
            (P.SENTINEL_DATO_MENU_TAREA,))
        return cur.fetchone()["n"]


def _salidas(conn, chat_id) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox where chat_id = %s",
                    (chat_id,))
        return cur.fetchone()["n"]


def _ultimo_cuerpo(conn, chat_id) -> str:
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo from message_outbox where chat_id = %s
                order by programado_para desc limit 1""", (chat_id,))
        return cur.fetchone()["cuerpo"]


def _vista_previa(conn, herramienta: str):
    with admin(conn) as cur:
        cur.execute(
            """select resumen from pending_action
                where herramienta = %s and estado = 'esperando'""",
            (herramienta,))
        return cur.fetchone()


def _incidentes(conn, ws) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s",
                    (ws,))
        return cur.fetchone()["n"]


def _abrir_pregunta(cliente, conn, ws, monkeypatch, accion: str):
    """Deja abierta la pregunta del dato para `accion` del menú y devuelve
    (tarea_id, telegram_id)."""
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="asignada")
    conn.commit()
    _pid, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                  "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, accion, tg)
    assert _abiertas(conn) == 1
    return tid, tg


def test_r3_h17_un_saludo_no_es_la_evidencia(cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(monkeypatch, [
        _ruta(RespectoPendiente.CHARLA), _ruta(RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, tg)

    assert _mensaje(cliente, tg, "hola").status_code == 200

    assert _vista_previa(conn, "actualizar_estado") is None   # sin vista previa
    assert _abiertas(conn) == 1                               # sigue abierta
    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in _ultimo_cuerpo(conn, tg)
    with admin(conn) as cur:
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0

    assert _mensaje(cliente, tg, "https://ejemplo.com/pr/12").status_code == 200

    fila = _vista_previa(conn, "actualizar_estado")
    assert fila is not None
    assert "https://ejemplo.com/pr/12" in fila["resumen"]
    assert "en revisión" in fila["resumen"].lower()
    assert _abiertas(conn) == 0                               # se consumió
    assert len(proveedor.pendientes) == 2                     # ruteó cada uno


def test_el_ruteo_recibe_la_descripcion_de_la_pregunta_pendiente(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje(cliente, tg, "hola")

    assert proveedor.ruteados == ["hola"]
    assert proveedor.pendientes == [
        f"la evidencia de la entrega de «{TITULO}»"]


@pytest.mark.parametrize("accion, estado, descripcion", [
    ("Informar un bloqueo", "asignada", f"la causa del bloqueo de «{TITULO}»"),
    ("Adjuntar evidencia", "en_revision", f"la evidencia de «{TITULO}»"),
])
def test_la_descripcion_sigue_a_la_accion_del_menu(
        cliente, conn, corework, monkeypatch, accion, estado, descripcion):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado=estado)
    conn.commit()
    _pid, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                  "Nahuel Gimenez")
    _tocar_accion(cliente, conn, ws, filas, accion, tg)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje(cliente, tg, "hola")

    assert proveedor.pendientes == [descripcion]


def test_cancela_cierra_sin_efecto_y_el_siguiente_mensaje_rutea_normal(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.CANCELA), _ruta(None)],
        guion=[Respuesta(texto="Tenés dos tareas abiertas.")])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "mejor dejalo")

    assert _abiertas(conn) == 0
    assert _salidas(conn, tg) == antes + 1
    assert "dejé de lado" in _ultimo_cuerpo(conn, tg)
    assert TITULO in _ultimo_cuerpo(conn, tg)
    assert _vista_previa(conn, "actualizar_estado") is None
    with admin(conn) as cur:
        cur.execute("select estado from task where id = %s", (tid,))
        assert cur.fetchone()["estado"] == "asignada"

    _mensaje(cliente, tg, "¿qué tengo pendiente?")

    assert proveedor.pendientes == [
        f"la evidencia de la entrega de «{TITULO}»", None]
    assert "dos tareas abiertas" in _ultimo_cuerpo(conn, tg)


def test_otro_tema_atiende_el_mensaje_con_una_sola_llamada_de_ruteo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
        guion=[Respuesta(texto="Tenés dos tareas abiertas.")])

    _mensaje(cliente, tg, "¿qué tengo pendiente?")

    assert len(proveedor.ruteados) == 1          # sin segundo ruteo
    assert len(proveedor.recibidos) == 1         # el agente respondió una vez
    assert "dos tareas abiertas" in _ultimo_cuerpo(conn, tg)
    assert _abiertas(conn) == 1                  # la pregunta sigue abierta


def test_no_puedo_avisa_repite_la_pregunta_y_no_consume(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.NO_PUEDO)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "mandá este archivo al cliente")

    cuerpo = _ultimo_cuerpo(conn, tg)
    assert gateway.AVISO_NO_PUEDO_DATO_PENDIENTE in cuerpo
    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in cuerpo
    assert _salidas(conn, tg) == antes + 1
    assert _abiertas(conn) == 1


@pytest.mark.parametrize("comando", [
    RespectoPendiente.CORRIGE, RespectoPendiente.DUDOSO])
def test_corrige_y_dudoso_repiten_la_pregunta_en_esta_etapa(
        cliente, conn, corework, monkeypatch, comando):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    _con_rutas(monkeypatch, [_ruta(comando)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "no sé si era eso")

    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in _ultimo_cuerpo(conn, tg)
    assert _salidas(conn, tg) == antes + 1
    assert _abiertas(conn) == 1
    assert _vista_previa(conn, "actualizar_estado") is None


def test_falla_del_ruteo_registra_incidente_y_no_consume(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    malo = RouteEnvelope(calls=())
    _con_rutas(monkeypatch, [malo, malo])
    incidentes = _incidentes(conn, ws)
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "hola")

    assert _incidentes(conn, ws) == incidentes + 1
    assert _salidas(conn, tg) == antes + 1
    assert _abiertas(conn) == 1
    assert _vista_previa(conn, "actualizar_estado") is None


def test_falla_del_primer_intento_reintenta_y_sigue_el_comando(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(monkeypatch, [
        RouteEnvelope(calls=()), _ruta(RespectoPendiente.RESPONDE)])

    _mensaje(cliente, tg, "lo probé en producción")

    assert len(proveedor.pendientes) == 2
    assert _vista_previa(conn, "actualizar_estado") is not None
    assert _abiertas(conn) == 0


def test_causa_de_bloqueo_charla_no_consume_y_responde_si_arma_la_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch,
                               "Informar un bloqueo")
    _con_rutas(monkeypatch, [
        _ruta(RespectoPendiente.CHARLA), _ruta(RespectoPendiente.RESPONDE)])

    _mensaje(cliente, tg, "buen día")

    assert _vista_previa(conn, "registrar_bloqueo") is None
    assert _abiertas(conn) == 1
    assert f"¿Cuál es la causa del bloqueo de «{TITULO}»?" in _ultimo_cuerpo(conn, tg)

    _mensaje(cliente, tg, "Falta un repuesto que no llegó")

    fila = _vista_previa(conn, "registrar_bloqueo")
    assert fila is not None
    assert "falta un repuesto" in fila["resumen"].lower()
    assert _abiertas(conn) == 0


def test_pedir_cambios_responde_arma_la_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=TITULO, estado="en_revision")
    conn.commit()
    _pid, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid,
                                  "Marcos Tarquini")
    _tocar_accion(cliente, conn, ws, filas, "Pedir cambios", tg)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])

    _mensaje(cliente, tg, "Falta el manual del operador")

    assert proveedor.pendientes == [f"qué hay que corregir en «{TITULO}»"]
    fila = _vista_previa(conn, "pedir_cambios_tarea")
    assert fila is not None
    assert "manual del operador" in fila["resumen"].lower()


# ---------------------------------------------------------------------------
# Peek y consumo de un solo uso (pendientes)
# ---------------------------------------------------------------------------


def test_ver_no_consume_y_consumir_es_de_un_solo_uso(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    ahora = datetime.now(timezone.utc)

    with espacio(conn, ws) as cur:
        quien = _quien(cur, "Nahuel Gimenez", ws)
        primera = P.ver_modificacion_abierta(cur, quien, tg, ahora)
        segunda = P.ver_modificacion_abierta(cur, quien, tg, ahora)
        assert primera is not None and segunda is not None
        assert primera.pending_action_id == segunda.pending_action_id
        assert primera.herramienta == P.SENTINEL_DATO_MENU_TAREA
        assert primera.args["accion"] == "terminar"
        assert _abiertas(conn) == 1                      # mirar no consume

        assert P.consumir_modificacion(
            cur, primera.pending_action_id, ahora) is True
        assert P.consumir_modificacion(
            cur, primera.pending_action_id, ahora) is False
        assert P.ver_modificacion_abierta(cur, quien, tg, ahora) is None
    assert _abiertas(conn) == 0
