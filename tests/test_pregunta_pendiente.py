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
from prisma import jev as jev_modulo
from prisma import pendientes as P
from prisma.jev import ClienteJevGuionado
from prisma.db import admin, espacio
from prisma.llm import (IntentAction, IntentRoute, ProveedorGuionado,
                         RespectoPendiente, Respuesta, RouteEnvelope)

from tests.toques import envejecer_toques
from tests.test_menu_tarea import (_abrir_menu, _mensaje, _opciones,  # noqa: F401
                                   _pendiente, _quien, _tarea, _tocar,
                                   _tocar_accion, cliente)

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
    (pendiente,) = proveedor.pendientes
    assert pendiente.startswith(f"la evidencia de la entrega de «{TITULO}»")


def test_el_ruteo_recibe_tambien_la_pregunta_literal(
        cliente, conn, corework, monkeypatch):
    # Banco real b-0019-d (2026-09-29): con sólo la descripción ("la evidencia
    # de la entrega de «…»") el modelo marcó un link suelto como `dudoso` en
    # 3 de 3 corridas, porque no veía que se había pedido un link. El ruteo
    # interpreta contra la pregunta tal como se le hizo a la persona.
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje(cliente, tg, "https://ejemplo.com/pr/12")

    (pendiente,) = proveedor.pendientes
    assert pendiente.startswith(f"la evidencia de la entrega de «{TITULO}»")
    assert gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA in pendiente


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

    (pendiente,) = proveedor.pendientes
    assert pendiente.startswith(descripcion)


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

    assert proveedor.pendientes[0].startswith(f"la evidencia de la entrega de «{TITULO}»")
    assert proveedor.pendientes[1] is None
    assert "dos tareas abiertas" in _ultimo_cuerpo(conn, tg)


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

    (pendiente,) = proveedor.pendientes
    assert pendiente.startswith(f"qué hay que corregir en «{TITULO}»")
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
        assert primera.pregunta_id == segunda.pregunta_id
        assert primera.herramienta == P.SENTINEL_DATO_MENU_TAREA
        assert primera.args["accion"] == "terminar"
        assert _abiertas(conn) == 1                      # mirar no consume

        assert P.consumir_modificacion(
            cur, primera.pregunta_id, ahora) is True
        assert P.consumir_modificacion(
            cur, primera.pregunta_id, ahora) is False
        assert P.ver_modificacion_abierta(cur, quien, tg, ahora) is None
    assert _abiertas(conn) == 0


# ---------------------------------------------------------------------------
# T9-R1a-2: dudoso y corrige con botones, seguimientos
# ---------------------------------------------------------------------------

DESCRIPCION = f"la evidencia de la entrega de «{TITULO}»"
LINK = "https://ejemplo.com/pr/12"


def _filas_del_chat(conn, chat_id) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo, pending_action_id from message_outbox
                where chat_id = %s order by programado_para""", (chat_id,))
        return cur.fetchall()


def _botones_de(conn, ws, herramienta: str) -> list[dict]:
    """Las opciones de la acción pendiente más reciente de esa herramienta."""
    with admin(conn) as cur:
        pid = _pendiente(cur, ws, herramienta)
        return _opciones(cur, pid)


def _tocar_boton(cliente, conn, ws, herramienta: str, etiqueta: str, tg):
    fila = next(o for o in _botones_de(conn, ws, herramienta)
                if etiqueta in o["etiqueta"])
    assert _tocar(cliente, fila["token"], tg).status_code == 200


def _preguntar_si_es_el_dato(cliente, conn, ws, monkeypatch, comando, texto):
    """Deja abierta la pregunta de evidencia y manda `texto`, que el ruteo
    (guionado) clasifica como `comando`. Devuelve (proveedor, tg, tid)."""
    tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(monkeypatch, [_ruta(comando)])
    _mensaje(cliente, tg, texto)
    return proveedor, tg, tid


@pytest.mark.parametrize("comando", [
    RespectoPendiente.DUDOSO, RespectoPendiente.CORRIGE])
def test_dudoso_y_corrige_preguntan_con_dos_botones_sin_consumir(
        cliente, conn, corework, monkeypatch, comando):
    # `corrige` no tiene una propuesta anterior que corregir en una pregunta
    # de dato del menú: se maneja igual que `dudoso`.
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    _con_rutas(monkeypatch, [_ruta(comando)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "ya casi está")

    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    ultima = _filas_del_chat(conn, tg)[-1]
    assert ultima["cuerpo"] == gateway.PREGUNTA_ES_EL_DATO.format(
        descripcion=DESCRIPCION)
    assert ultima["pending_action_id"] is not None            # con botones
    etiquetas = [o["etiqueta"]
                 for o in _botones_de(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU)]
    assert etiquetas == [gateway.ETIQUETA_ES_EL_DATO,
                         gateway.ETIQUETA_NO_ES_EL_DATO]
    assert _abiertas(conn) == 1                               # no se consumió
    assert _vista_previa(conn, "actualizar_estado") is None


def test_dudoso_si_arma_la_vista_previa_con_el_texto_original(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _proveedor, tg, _tid = _preguntar_si_es_el_dato(
        cliente, conn, ws, monkeypatch, RespectoPendiente.DUDOSO,
        f"esto {LINK}")
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU, "Sí", tg)

    fila = _vista_previa(conn, "actualizar_estado")
    assert fila is not None
    assert LINK in fila["resumen"]
    assert "en revisión" in fila["resumen"].lower()
    assert _abiertas(conn) == 0                               # se consumió
    assert _salidas(conn, tg) == antes + 1                    # una respuesta


def test_dudoso_si_con_la_pregunta_ya_consumida_lo_dice_y_no_hace_nada(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _proveedor, tg, tid = _preguntar_si_es_el_dato(
        cliente, conn, ws, monkeypatch, RespectoPendiente.DUDOSO, "ya casi está")
    with admin(conn) as cur:                       # otro camino la consumió
        cur.execute(
            """update pending_action set modificacion_consumida_en = now()
                where herramienta = %s""", (P.SENTINEL_DATO_MENU_TAREA,))
    conn.commit()
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU, "Sí", tg)

    assert _salidas(conn, tg) == antes + 1
    assert _ultimo_cuerpo(conn, tg) == gateway.AVISO_DATO_YA_NO_PENDIENTE
    assert _vista_previa(conn, "actualizar_estado") is None
    with admin(conn) as cur:
        cur.execute("select count(*) n from evidence where task_id = %s", (tid,))
        assert cur.fetchone()["n"] == 0


def test_dudoso_tocado_dos_veces_no_repite_el_efecto(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _proveedor, tg, _tid = _preguntar_si_es_el_dato(
        cliente, conn, ws, monkeypatch, RespectoPendiente.DUDOSO, LINK)
    fila = next(o for o in _botones_de(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU)
                if "Sí" in o["etiqueta"])
    _tocar(cliente, fila["token"], tg)
    envejecer_toques(conn, 11)                  # fuera de la ventana (T9-R4)
    antes = _salidas(conn, tg)

    _tocar(cliente, fila["token"], tg)                        # el mismo botón

    assert _salidas(conn, tg) == antes + 1                    # sólo un aviso
    assert "ya no está vigente" in _ultimo_cuerpo(conn, tg)


# --- Seguimientos de review-c10ae20ecdf4cfa0 -------------------------------


def _consumida_por_otro_turno(monkeypatch):
    """Simula la carrera: otro turno consume la pregunta entre que se la lee
    y se la consume acá, así que `consumir_modificacion` devuelve `False`."""
    real = P.consumir_modificacion

    def consumir(cur, pending_action_id, ahora):
        real(cur, pending_action_id, ahora)
        return False

    monkeypatch.setattr(P, "consumir_modificacion", consumir)


def test_responde_con_la_pregunta_ya_consumida_sigue_el_camino_normal_una_vez(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.RESPONDE)],
        guion=[Respuesta(texto="Anotado, seguimos.")])
    _consumida_por_otro_turno(monkeypatch)
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "lo terminé ayer")

    assert len(proveedor.ruteados) == 1           # sin segundo ruteo
    assert len(proveedor.recibidos) == 1          # lo atendió el agente
    assert _salidas(conn, tg) == antes + 1        # exactamente una respuesta
    assert _ultimo_cuerpo(conn, tg) == "Anotado, seguimos."
    assert _vista_previa(conn, "actualizar_estado") is None


def test_cancela_con_la_pregunta_ya_consumida_no_dice_que_la_dejo(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CANCELA)])
    _consumida_por_otro_turno(monkeypatch)
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "mejor dejalo")

    assert _salidas(conn, tg) == antes + 1
    cuerpo = _ultimo_cuerpo(conn, tg)
    assert cuerpo == gateway.AVISO_DATO_YA_NO_PENDIENTE
    assert "dejé de lado" not in cuerpo


# --- Una sola respuesta por mensaje, en cada comando ----------------------


@pytest.mark.parametrize("comando, guion, filas", [
    (RespectoPendiente.RESPONDE, [], 1),
    (RespectoPendiente.CORRIGE, [], 1),
    (RespectoPendiente.CANCELA, [], 1),
    (RespectoPendiente.CHARLA, [], 1),
    (RespectoPendiente.DUDOSO, [], 1),
    (RespectoPendiente.NO_PUEDO, [], 1),
    # La pregunta de la rama (T9-R1d): una respuesta con dos botones.
    (RespectoPendiente.OTRO_TEMA, [], 1),
])
def test_cada_comando_deja_una_sola_respuesta_para_el_mensaje(
        cliente, conn, corework, monkeypatch, comando, guion, filas):
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Ya la terminé")
    _con_rutas(monkeypatch, [_ruta(comando)], guion=guion)
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "mensaje de prueba")

    assert _salidas(conn, tg) == antes + filas


def test_responder_un_dato_del_menu_no_resuelve_los_trabajos_como_referencias(
        cliente, conn, corework, monkeypatch):
    # T9-R1b-2 (ADR 0013 regla 1, banco b-0020): la tarea la fija la pregunta;
    # un sustantivo del mensaje no abre una búsqueda ni una aclaración.
    ws = corework.workspace_id
    _tid, tg = _abrir_pregunta(cliente, conn, ws, monkeypatch, "Informar un bloqueo")
    doble = ClienteJevGuionado(guion=[])
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: doble)
    _con_rutas(monkeypatch, [IntentRoute(
        IntentAction.NORMAL_CONVERSATION, trabajos=("el variador roto",),
        respecto_pendiente=RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "se rompió el variador")

    assert doble.pedidos == []
    fila = _vista_previa(conn, "registrar_bloqueo")
    assert fila is not None and TITULO in fila["resumen"]     # la tarea guardada
    assert _abiertas(conn) == 0
    assert _salidas(conn, tg) == antes + 1
