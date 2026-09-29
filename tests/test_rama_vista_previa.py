"""La vista previa de un cambio que la persona pidió es una rama abierta
(T9-R1d-1b, ADR 0013 regla 1, enmienda "una sola rama de conversación abierta").

Cuando Prisma le mostró a la persona la vista previa de un cambio que ella pidió
en ese chat (una `pending_action` de una herramienta que escribe, con Confirmar,
Modificar y Cancelar) y ella escribe algo, el mensaje se interpreta contra esa
vista previa con el ruteo tipado, igual que con las demás preguntas abiertas:

- `responde` ("sí, dale"): el cambio NO se aplica (sólo el botón Confirmar lo
  aplica); se dice y la vista previa sigue esperando, con sus botones.
- `corrige`: el mensaje es la corrección (el camino de Modificar).
- `cancela`: se cancela la vista previa y se dice qué se dejó de lado.
- `otro_tema`: la pregunta de la rama, con la guarda contra volver a proponer lo
  mismo al dejarla.

No son una rama: una vista previa vencida o ya resuelta, la de otra persona, los
avisos que le llegan a alguien para decidir (la entrega que le piden aprobar) y
el borrador del alta que espera a otro aprobador.

Los ruteos y el modelo se guionan con `ProveedorGuionado`; nada toca la red.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from prisma import gateway
from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.llm import Llamada, RespectoPendiente, Respuesta

from tests.test_menu_tarea import _mensaje, _quien, _tocar, cliente  # noqa: F401
from tests.test_modificar import _proponer, _tarea
from tests.test_pregunta_pendiente_otras import (_abiertas, _botones_de,
                                                 _con_rutas, _filas_del_chat,
                                                 _incidentes, _ruta, _salidas,
                                                 _tocar_boton, _ultimo_cuerpo)

PERSONA = "Marcos Tarquini"
CAUSA = "falta el switch"
OTRO_MENSAJE = "¿qué tareas tengo abiertas?"
RESPUESTA = "Tenés dos tareas abiertas."


def _abrir_vista_previa(conn, ws, *, causa: str = CAUSA):
    """La vista previa de un bloqueo que la persona pidió, esperando su
    Confirmar, en su chat. Devuelve (chat, tarea, pending_action)."""
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    (PERSONA,))
        tg = cur.fetchone()["t"]
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": causa}, chat_id=tg,
                        ahora=datetime.now(timezone.utc))
    conn.commit()
    return tg, tid, pid


def _estado(conn, pid: str) -> str:
    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        return cur.fetchone()["estado"]


def _bloqueos(conn, tid: str) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        return cur.fetchone()["n"]


def _vistas_esperando(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            """select id, resumen, args from pending_action
                where estado = 'esperando' and herramienta = 'registrar_bloqueo'
                order by creado_en""")
        return cur.fetchall()


def _mostradas(conn, tg: int, pid: str) -> list[dict]:
    """Los mensajes de este chat que llevan los botones de esta vista previa."""
    return [f for f in _filas_del_chat(conn, tg) if str(f["pending_action_id"]) == pid]


def _confirmar(cliente, conn, tg: int, pid: str):
    with admin(conn) as cur:
        token = P.opcion_por_etiqueta(cur, pid, "Confirmar").token
    return _tocar(cliente, token, tg)


# ---------------------------------------------------------------------------
# Cada comando con la vista previa esperando
# ---------------------------------------------------------------------------

def test_responde_no_aplica_el_cambio_y_dice_que_se_confirma_con_el_boton(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "sí, dale, confirmá")

    assert _bloqueos(conn, tid) == 0                          # nada se aplicó
    assert _estado(conn, pid) == "esperando"                  # sigue abierta
    assert proveedor.recibidos == []                          # el agente no habló
    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    cuerpo = _ultimo_cuerpo(conn, tg)
    assert "botón Confirmar" in cuerpo
    # Vuelve a mostrar la misma vista previa, con sus botones.
    assert len(_mostradas(conn, tg, pid)) == 2
    assert _filas_del_chat(conn, tg)[-1]["pending_action_id"] is not None
    # El botón sigue funcionando: ahí sí se aplica.
    assert _confirmar(cliente, conn, tg, pid).status_code == 200
    assert _bloqueos(conn, tid) == 1


def test_el_ruteo_recibe_la_vista_previa_como_la_pregunta_pendiente(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _tid, _pid = _abrir_vista_previa(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje(cliente, tg, "hola")

    (pendiente,) = proveedor.pendientes
    assert CAUSA in pendiente and "Confirmar" in pendiente


def test_corrige_es_el_camino_de_modificar_con_el_mensaje_como_correccion(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.CORRIGE)],
        guion=[Respuesta(llamadas=[Llamada("c1", "registrar_bloqueo", {
                   "tarea_id": tid, "causa": "se rompió el variador"})]),
               Respuesta(texto="listo")])

    _mensaje(cliente, tg, "el motivo real es que se rompió el variador")

    assert _bloqueos(conn, tid) == 0                          # nada se aplicó
    assert _estado(conn, pid) == "cancelada"                  # como Modificar
    (nueva,) = _vistas_esperando(conn)                        # la vista previa nueva
    assert "variador" in nueva["resumen"]
    # El agente recibió la propuesta anterior como contexto del servidor.
    assert "# Corrección a una propuesta anterior" in proveedor.recibidos[-1][0]
    assert _abiertas(conn) == 0                               # la corrección se consumió
    # La vista previa vieja ya no aplica nada.
    _confirmar(cliente, conn, tg, pid)
    assert _bloqueos(conn, tid) == 0


def test_cancela_cierra_la_vista_previa_y_dice_que_se_dejo_de_lado(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CANCELA)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "no, dejalo, mejor no")

    assert _estado(conn, pid) == "cancelada"
    assert _salidas(conn, tg) == antes + 1
    assert "dejé de lado" in _ultimo_cuerpo(conn, tg)
    assert proveedor.recibidos == []
    _confirmar(cliente, conn, tg, pid)                        # el botón ya no aplica
    assert _bloqueos(conn, tid) == 0
    assert gateway.AVISO_PEDIDO_NO_VIGENTE in _ultimo_cuerpo(conn, tg)


@pytest.mark.parametrize("comando", [RespectoPendiente.CHARLA,
                                     RespectoPendiente.NO_PUEDO])
def test_charla_y_no_puedo_vuelven_a_mostrar_la_vista_previa_sin_cerrarla(
        cliente, conn, corework, monkeypatch, comando):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(comando)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "hola")

    assert _estado(conn, pid) == "esperando"
    assert _salidas(conn, tg) == antes + 1
    assert len(_mostradas(conn, tg, pid)) == 2                # con sus botones
    assert CAUSA in _ultimo_cuerpo(conn, tg)
    assert proveedor.recibidos == [] and _bloqueos(conn, tid) == 0


def test_dudoso_pregunta_y_si_es_eso_dice_que_se_confirma_con_el_boton(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    # Un solo ruteo: "Sí, es eso" no vuelve a rutear el texto.
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO)])
    _mensaje(cliente, tg, "puede ser")
    assert "¿Esto es" in _ultimo_cuerpo(conn, tg)

    _tocar_boton(cliente, conn, ws, "Sí, es eso", tg)

    assert _estado(conn, pid) == "esperando" and _bloqueos(conn, tid) == 0
    assert "botón Confirmar" in _ultimo_cuerpo(conn, tg)
    assert proveedor.recibidos == []


def test_ruteo_caido_deja_la_vista_previa_abierta_y_avisa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)

    class _Caido:
        recibidos: list = []

        def route_intent(self, texto, pendiente=None):
            raise RuntimeError("caído")

    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, w, key: _Caido())
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "sí, dale")

    assert _estado(conn, pid) == "esperando" and _bloqueos(conn, tid) == 0
    assert _salidas(conn, tg) == antes + 1
    assert _incidentes(conn, ws) >= 1


# ---------------------------------------------------------------------------
# La rama: otro tema pregunta, Seguir repite, Dejar cancela y atiende lo otro
# ---------------------------------------------------------------------------

def test_otro_tema_pregunta_por_la_rama_sin_atender_ni_cerrar_la_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, OTRO_MENSAJE)

    assert _estado(conn, pid) == "esperando"
    assert proveedor.recibidos == []                          # el otro tema no se atiende
    assert _salidas(conn, tg) == antes + 1
    assert "Estábamos con el cambio que te mostré" in _ultimo_cuerpo(conn, tg)
    etiquetas = [o["etiqueta"] for o in _botones_de(
        conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU)]
    assert len(etiquetas) == 2
    # La vista previa conserva sus propios botones mientras la rama espera.
    assert _confirmar(cliente, conn, tg, pid).status_code == 200
    assert _bloqueos(conn, tid) == 1


def test_seguir_vuelve_a_mostrar_la_vista_previa(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    _mensaje(cliente, tg, OTRO_MENSAJE)
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, "Seguir", tg)

    assert _estado(conn, pid) == "esperando"
    assert _salidas(conn, tg) == antes + 1
    assert len(_mostradas(conn, tg, pid)) == 2
    assert CAUSA in _ultimo_cuerpo(conn, tg)


def test_dejar_cancela_la_vista_previa_y_atiende_lo_otro_en_la_misma_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, tg, OTRO_MENSAJE)

    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)

    assert _estado(conn, pid) == "cancelada" and _bloqueos(conn, tid) == 0
    cuerpos = [f["cuerpo"] for f in _filas_del_chat(conn, tg)[-2:]]
    assert "dejé de lado" in cuerpos[0] and RESPUESTA in cuerpos[1]
    assert len(proveedor.recibidos) == 1                      # lo otro sí se atendió


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_dejar_no_vuelve_a_proponer_lo_mismo_sobre_la_misma_tarea(
        cliente, conn, corework, monkeypatch, es_la_misma):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    with admin(conn) as cur:
        otra = _tarea(cur, ws, titulo="Revisar variador línea 2")
    conn.commit()
    destino = tid if es_la_misma else otra
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(llamadas=[Llamada("q2", "registrar_bloqueo", {
                   "tarea_id": destino, "causa": CAUSA})]),
               Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, tg, OTRO_MENSAJE)

    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)

    esperando = _vistas_esperando(conn)
    if es_la_misma:
        assert esperando == []                                # no se volvió a proponer
    else:
        (nueva,) = esperando                                  # sobre otra tarea sí
        assert nueva["args"]["tarea_id"] == otra


def test_no_es_otra_cosa_de_dudoso_es_la_misma_salida_que_dejar(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
               guion=[Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, tg, "puede ser")

    _tocar_boton(cliente, conn, ws, "No, es otra cosa", tg)

    assert _estado(conn, pid) == "cancelada" and _bloqueos(conn, tid) == 0
    assert RESPUESTA in _ultimo_cuerpo(conn, tg)


def test_seguir_tarde_dice_que_ya_no_estaba_pendiente(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    _mensaje(cliente, tg, OTRO_MENSAJE)
    assert _confirmar(cliente, conn, tg, pid).status_code == 200   # otro camino la cerró
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, "Seguir", tg)

    assert _salidas(conn, tg) == antes + 1
    assert _ultimo_cuerpo(conn, tg) == gateway.AVISO_RAMA_YA_CERRADA
    assert _bloqueos(conn, tid) == 1


# ---------------------------------------------------------------------------
# Lo que no es una rama
# ---------------------------------------------------------------------------

def _sin_pregunta_el_mensaje_sigue_el_camino_normal(cliente, conn, tg, proveedor,
                                                    antes):
    """Un mensaje sin rama abierta se rutea una sola vez, sin pregunta pendiente,
    y llega al agente."""
    _mensaje(cliente, tg, OTRO_MENSAJE)
    assert proveedor.pendientes == [None]
    assert len(proveedor.recibidos) == 1
    assert _salidas(conn, tg) == antes + 1


@pytest.mark.parametrize("como", ["vencida", "confirmada", "cancelada"])
def test_una_vista_previa_vencida_o_resuelta_no_es_una_rama(
        cliente, conn, corework, monkeypatch, como):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    if como == "vencida":
        with admin(conn) as cur:
            cur.execute("update pending_action set vence_en = now() - interval '1 minute' "
                        "where id = %s", (pid,))
        conn.commit()
    elif como == "confirmada":
        assert _confirmar(cliente, conn, tg, pid).status_code == 200
    else:
        with admin(conn) as cur:
            token = P.opcion_por_etiqueta(cur, pid, "Cancelar").token
        assert _tocar(cliente, token, tg).status_code == 200
    proveedor = _con_rutas(monkeypatch, [_ruta(None)],
                           guion=[Respuesta(texto=RESPUESTA)])
    antes = _salidas(conn, tg)

    _sin_pregunta_el_mensaje_sigue_el_camino_normal(cliente, conn, tg, proveedor,
                                                    antes)


def test_la_vista_previa_de_otra_persona_no_es_una_rama_de_quien_escribe(
        conn, corework):
    ws = corework.workspace_id
    tg, _tid, _pid = _abrir_vista_previa(conn, ws)
    with espacio(conn, ws) as cur:
        otra = _quien(cur, "Nahuel Gimenez", ws)
        propia = _quien(cur, PERSONA, ws)
        ahora = datetime.now(timezone.utc)
        assert gateway._ver_pregunta_abierta(cur, otra, tg, ahora, alta=False) is None
        assert gateway._ver_pregunta_abierta(cur, propia, tg + 1, ahora,
                                             alta=False) is None      # otro chat
        propia_abierta = gateway._ver_pregunta_abierta(cur, propia, tg, ahora,
                                                       alta=False)
    assert propia_abierta is not None


def test_una_aprobacion_que_le_piden_a_la_persona_no_es_una_rama_suya(
        cliente, conn, corework, monkeypatch):
    # El aviso de entrega que le llega al aprobador es un mensaje que inicia
    # Prisma (ADR 0013, enmienda): no le impide hablar de otra cosa.
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        aprobador = _quien(cur, PERSONA, ws)
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    (PERSONA,))
        tg = cur.fetchone()["t"]
        P.registrar(
            cur, aprobador, herramienta=P.SENTINEL_MENU_TAREA,
            args={"tarea_id": tid, "titulo": "Programar PLC",
                  "aviso": P.AVISO_ENTREGA},
            resumen="Nahuel entregó «Programar PLC»", campo="eleccion",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=8),
            opciones=[("Aprobar", {"accion": "aprobar"}),
                      ("Pedir cambios", {"accion": "pedir_cambios"})],
            chat_id=tg)
    conn.commit()
    proveedor = _con_rutas(monkeypatch, [_ruta(None)],
                           guion=[Respuesta(texto=RESPUESTA)])
    antes = _salidas(conn, tg)

    _sin_pregunta_el_mensaje_sigue_el_camino_normal(cliente, conn, tg, proveedor,
                                                    antes)


def test_una_eleccion_de_una_herramienta_no_es_una_vista_previa(conn, corework):
    # `NecesitaElegir` guarda la herramienta real pero con `campo`: pregunta
    # "¿cuál de estas?", no espera un Confirmar. Es otra rama, la de la elección
    # (`test_rama_eleccion`, T9-R1d-1c), no una vista previa.
    from prisma import herramientas as H

    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    (PERSONA,))
        tg = cur.fetchone()["t"]
        P.registrar(cur, quien, herramienta="registrar_bloqueo",
                    args={"causa": CAUSA}, resumen="¿En cuál tarea?",
                    campo="tarea_id", opciones=[("Programar PLC", tid)],
                    vence_en=datetime.now(timezone.utc) + timedelta(hours=8),
                    chat_id=tg)
        ahora = datetime.now(timezone.utc)
        assert P.ver_vista_previa_abierta(cur, quien, tg, ahora, H.REGISTRO) is None
        abierta = gateway._ver_pregunta_abierta(cur, quien, tg, ahora, alta=False)

    assert abierta.herramienta == gateway._SENTINEL_ELECCION


# ---------------------------------------------------------------------------
# Precedencia con las otras preguntas abiertas
# ---------------------------------------------------------------------------

def test_con_un_modificar_abierto_gana_el_modificar_y_la_vista_previa_espera(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        otra = _proponer(cur, ws, quien, "registrar_bloqueo",
                         {"tarea_id": tid, "causa": "otra causa"}, chat_id=tg,
                         ahora=datetime.now(timezone.utc))
        modificar = P.opcion_por_etiqueta(cur, otra, "Modificar")
    conn.commit()
    assert _tocar(cliente, modificar.token, tg).status_code == 200

    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        abierta = gateway._ver_pregunta_abierta(cur, quien, tg,
                                                datetime.now(timezone.utc),
                                                alta=False)

    assert abierta.pregunta_id == otra                        # la corrección pedida
    assert abierta.herramienta == "registrar_bloqueo"         # no la vista previa
    assert _estado(conn, pid) == "esperando"


def test_con_una_pregunta_del_alta_abierta_gana_el_alta(conn, corework):
    from tests.test_alta_pregunta_pendiente import _abrir_alta

    ws = corework.workspace_id
    tg, _request_id = _abrir_alta(conn, ws)
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        _proponer(cur, ws, quien, "registrar_bloqueo",
                  {"tarea_id": tid, "causa": CAUSA}, chat_id=tg,
                  ahora=datetime.now(timezone.utc))
    conn.commit()

    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        abierta = gateway._ver_pregunta_abierta(cur, quien, tg,
                                                datetime.now(timezone.utc),
                                                alta=True)

    assert abierta.herramienta in gateway._TIPO_DE_ALTA


def test_sin_otra_pregunta_la_vista_previa_es_la_rama_abierta(conn, corework):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        abierta = gateway._ver_pregunta_abierta(cur, quien, tg,
                                                datetime.now(timezone.utc),
                                                alta=True)

    assert abierta.pregunta_id == pid
    assert abierta.herramienta == gateway._SENTINEL_VISTA_PREVIA
    assert gateway._no_proponer_de(abierta) == {
        "herramienta": "registrar_bloqueo", "campo": "tarea_id", "valor": tid}


# ---------------------------------------------------------------------------
# Los botones de la propia vista previa siguen como siempre
# ---------------------------------------------------------------------------

def test_los_botones_de_la_vista_previa_siguen_funcionando_como_siempre(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws)

    with admin(conn) as cur:
        token = P.opcion_por_etiqueta(cur, pid, "Modificar").token
    assert _tocar(cliente, token, tg).status_code == 200
    assert _ultimo_cuerpo(conn, tg) == gateway.PREGUNTA_MODIFICAR
    assert _estado(conn, pid) == "cancelada" and _abiertas(conn) == 1

    with admin(conn) as cur:
        token = P.opcion_por_etiqueta(cur, pid, "Cancelar").token
    _tocar(cliente, token, tg)                                # ya cerrada por Modificar
    assert _bloqueos(conn, tid) == 0

    tg2, tid2, pid2 = _abrir_vista_previa(conn, ws)
    with admin(conn) as cur:
        token = P.opcion_por_etiqueta(cur, pid2, "Cancelar").token
    assert _tocar(cliente, token, tg2).status_code == 200
    assert _ultimo_cuerpo(conn, tg2) == "Listo, no lo hago."
    assert _estado(conn, pid2) == "cancelada"


# ---------------------------------------------------------------------------
# Una vista previa que no entra con el aviso delante (review-0c99f611fc23e0cd)
# ---------------------------------------------------------------------------

def _causa_que_llena_la_vista_previa() -> str:
    """Una causa tan larga que la vista previa entra sola con sus botones (así
    salió la primera vez) pero no con un aviso delante. Se calcula sobre la
    vista previa real de un bloqueo, no sobre un largo fijo."""
    from prisma.salida import (BUTTON_TEXT_LIMIT, margen_saludo,
                               telegram_utf16_units)

    base = ("Tarea: Programar PLC · Causa del bloqueo:  · Estado actual: Asignada "
            "· la tarea pasa a Bloqueada\n\nTodavía no se aplicó ningún cambio.")
    limite = BUTTON_TEXT_LIMIT - margen_saludo(personal=True)
    return "x" * (limite - telegram_utf16_units(base) - 10)


def test_con_el_aviso_delante_la_vista_previa_larga_sale_aparte_con_sus_botones(
        cliente, conn, corework, monkeypatch):
    from prisma.salida import cabe_en_mensaje

    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa(conn, ws, causa=_causa_que_llena_la_vista_previa())
    with admin(conn) as cur:
        cur.execute("select resumen from pending_action where id = %s", (pid,))
        resumen = cur.fetchone()["resumen"]
    aviso = gateway.AVISO_VISTA_PREVIA_SE_CONFIRMA_CON_EL_BOTON
    assert cabe_en_mensaje(resumen, has_buttons=True)                    # sola, entra
    assert not cabe_en_mensaje(f"{aviso}\n\n{resumen}", has_buttons=True)  # con aviso, no
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "sí, dale, confirmá")

    # Una respuesta de dos partes: primero el aviso, después la vista previa
    # completa con sus botones; nunca el aviso solo.
    assert _salidas(conn, tg) == antes + 2
    aviso_fila, vista_fila = _filas_del_chat(conn, tg)[-2:]
    assert aviso_fila["cuerpo"] == aviso and aviso_fila["pending_action_id"] is None
    assert vista_fila["cuerpo"] == resumen
    assert str(vista_fila["pending_action_id"]) == pid
    assert _estado(conn, pid) == "esperando" and _bloqueos(conn, tid) == 0
    assert _confirmar(cliente, conn, tg, pid).status_code == 200         # el botón sigue
    assert _bloqueos(conn, tid) == 1


def test_sin_aviso_la_vista_previa_que_entra_sola_sale_en_un_solo_mensaje(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _tid, pid = _abrir_vista_previa(conn, ws, causa=_causa_que_llena_la_vista_previa())
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "hola")

    assert _salidas(conn, tg) == antes + 1
    assert str(_filas_del_chat(conn, tg)[-1]["pending_action_id"]) == pid


# ---------------------------------------------------------------------------
# Otros orígenes de la vista previa: el menú y `bloqueo_id`
# (review-0c99f611fc23e0cd)
# ---------------------------------------------------------------------------

def _abrir_vista_previa_del_menu(cliente, conn, ws, monkeypatch):
    """Toca "Empezar" en el menú de una tarea: la vista previa de
    `actualizar_estado` la arma `gateway._encolar_vista_previa_menu`, no el
    agente. Devuelve (chat, tarea, pending_action)."""
    from tests.test_menu_tarea import _abrir_menu, _tocar_accion

    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    _, filas, tg = _abrir_menu(cliente, conn, ws, monkeypatch, tid, PERSONA)
    _tocar_accion(cliente, conn, ws, filas, "Empezar", tg)
    with admin(conn) as cur:
        cur.execute("select id from pending_action where estado = 'esperando' "
                    "and herramienta = 'actualizar_estado'")
        (fila,) = cur.fetchall()
    return tg, tid, str(fila["id"])


def _abierta_de(conn, ws, tg: int):
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        return gateway._ver_pregunta_abierta(
            cur, quien, tg, datetime.now(timezone.utc), alta=False)


def test_la_vista_previa_armada_desde_el_menu_es_la_rama_abierta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa_del_menu(cliente, conn, ws, monkeypatch)

    abierta = _abierta_de(conn, ws, tg)

    assert abierta.pregunta_id == pid
    assert abierta.herramienta == gateway._SENTINEL_VISTA_PREVIA
    assert gateway._no_proponer_de(abierta) == {
        "herramienta": "actualizar_estado", "campo": "tarea_id", "valor": tid}


def test_con_la_vista_previa_del_menu_responde_no_aplica_nada_y_la_vuelve_a_mostrar(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa_del_menu(cliente, conn, ws, monkeypatch)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "sí, empezala")

    assert _estado(conn, pid) == "esperando"                  # no se aplicó
    assert proveedor.recibidos == []
    assert _salidas(conn, tg) == antes + 1
    assert "botón Confirmar" in _ultimo_cuerpo(conn, tg)
    assert str(_filas_del_chat(conn, tg)[-1]["pending_action_id"]) == pid


@pytest.mark.parametrize("es_la_misma", [True, False],
                         ids=["misma_tarea_rechaza", "otra_tarea_permite"])
def test_dejar_la_vista_previa_del_menu_no_vuelve_a_proponer_lo_mismo(
        cliente, conn, corework, monkeypatch, es_la_misma):
    ws = corework.workspace_id
    tg, tid, pid = _abrir_vista_previa_del_menu(cliente, conn, ws, monkeypatch)
    with admin(conn) as cur:
        otra = _tarea(cur, ws, titulo="Revisar variador línea 2")
    conn.commit()
    destino = tid if es_la_misma else otra
    _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(llamadas=[Llamada("q2", "actualizar_estado", {
                   "tarea_id": destino, "estado": "en_curso"})]),
               Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, tg, OTRO_MENSAJE)

    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)

    assert _estado(conn, pid) == "cancelada"
    with admin(conn) as cur:
        cur.execute("select args from pending_action where estado = 'esperando' "
                    "and herramienta = 'actualizar_estado'")
        esperando = cur.fetchall()
    if es_la_misma:
        assert esperando == []                                # no se volvió a proponer
    else:
        (nueva,) = esperando
        assert nueva["args"]["tarea_id"] == otra


def _bloqueo_abierto(conn, ws, *, titulo: str) -> tuple[str, str]:
    """Una tarea de la persona con un bloqueo abierto: (tarea, bloqueo)."""
    from tests.test_menu_tarea import _bloquear

    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo=titulo)
        _bloquear(cur, ws, tid)
        cur.execute("select id from blocker where task_id = %s", (tid,))
        bid = str(cur.fetchone()["id"])
    conn.commit()
    return tid, bid


def _abrir_vista_previa_de_destrabar(conn, ws, bid: str):
    """La vista previa de `resolver_bloqueo`, cuyo id es `bloqueo_id`, no
    `tarea_id`."""
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        cur.execute("select telegram_user_id t from integrante where nombre = %s",
                    (PERSONA,))
        tg = cur.fetchone()["t"]
        pid = _proponer(cur, ws, quien, "resolver_bloqueo",
                        {"bloqueo_id": bid, "resolucion": "llegó el switch"},
                        chat_id=tg, ahora=datetime.now(timezone.utc))
    conn.commit()
    return tg, pid


def test_una_vista_previa_con_bloqueo_id_es_la_rama_y_su_guarda_compara_el_bloqueo(
        conn, corework):
    ws = corework.workspace_id
    _tid, bid = _bloqueo_abierto(conn, ws, titulo="Programar PLC")
    tg, pid = _abrir_vista_previa_de_destrabar(conn, ws, bid)

    abierta = _abierta_de(conn, ws, tg)

    assert abierta.pregunta_id == pid
    assert abierta.herramienta == gateway._SENTINEL_VISTA_PREVIA
    assert gateway._no_proponer_de(abierta) == {
        "herramienta": "resolver_bloqueo", "campo": "bloqueo_id", "valor": bid}


@pytest.mark.parametrize("es_el_mismo", [True, False],
                         ids=["mismo_bloqueo_rechaza", "otro_bloqueo_permite"])
def test_dejar_una_vista_previa_de_destrabar_no_vuelve_a_proponer_el_mismo_bloqueo(
        cliente, conn, corework, monkeypatch, es_el_mismo):
    ws = corework.workspace_id
    _tid, bid = _bloqueo_abierto(conn, ws, titulo="Programar PLC")
    _otra, otro_bid = _bloqueo_abierto(conn, ws, titulo="Revisar variador línea 2")
    tg, pid = _abrir_vista_previa_de_destrabar(conn, ws, bid)
    destino = bid if es_el_mismo else otro_bid
    _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(llamadas=[Llamada("q2", "resolver_bloqueo", {
                   "bloqueo_id": destino, "resolucion": "llegó el switch"})]),
               Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, tg, OTRO_MENSAJE)

    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)

    assert _estado(conn, pid) == "cancelada"
    with admin(conn) as cur:
        cur.execute("select args from pending_action where estado = 'esperando' "
                    "and herramienta = 'resolver_bloqueo'")
        esperando = cur.fetchall()
    if es_el_mismo:
        assert esperando == []                                # no se volvió a proponer
    else:
        (nueva,) = esperando
        assert nueva["args"]["bloqueo_id"] == otro_bid
