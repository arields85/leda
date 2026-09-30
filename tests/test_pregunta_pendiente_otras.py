"""Una pregunta pendiente es contexto, no una trampa (T9-R1b, ADR 0013 regla
1): el mismo manejo por comando que el dato del menú (`test_pregunta_pendiente`)
para las otras dos preguntas que dejan el mensaje siguiente como respuesta.

- **Modificar** (ADR 0005 decisión 1): después de tocar "Modificar" en una vista
  previa, un saludo, un agradecimiento, otro pedido o una cancelación ya no se
  toman como la corrección.
- **"Ninguna, lo escribo"** (ADR 0005 decisión 4): lo mismo con la aclaración de
  a qué tarea se refería la persona.

Los ruteos se guionan con `ProveedorGuionado`; ninguna prueba toca la red ni el
modelo real.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from prisma import gateway
from prisma import jev as jev_modulo
from prisma import pendientes as P
from prisma.db import admin, espacio
from prisma.jev import ClienteJevGuionado
from prisma.llm import (IntentAction, IntentRoute, Llamada, ProveedorGuionado,
                        RespectoPendiente, Respuesta, RouteEnvelope)

from tests.test_menu_tarea import (_mensaje, _opciones, _pendiente, _quien,  # noqa: F401
                                   _telegram_id, _tocar, cliente)
from tests.test_modificar import _proponer, _tarea

PERSONA = "Marcos Tarquini"
CAUSA = "falta el switch"
REFERENCIA = "lo del tablero"
PEDIDO_ORIGINAL = "avisame de lo del tablero"

# Lo que Prisma le pide a la persona, según lo que abrió la pregunta.
PREGUNTAS = {"modificar": gateway.PREGUNTA_MODIFICAR,
             "ninguna": gateway.PREGUNTA_ACLARACION_NINGUNA}
DEJADAS = {"modificar": gateway.AVISO_MODIFICACION_DEJADA,
           "ninguna": gateway.AVISO_ACLARACION_DEJADA}
# Marca del contexto que el servidor le pasa al agente en cada camino.
CONTEXTOS = {"modificar": "# Corrección a una propuesta anterior",
             "ninguna": "no encontró entre las opciones"}

KINDS = ["modificar", "ninguna"]


def _ruta(comando: RespectoPendiente | None) -> IntentRoute:
    return IntentRoute(IntentAction.NORMAL_CONVERSATION,
                       respecto_pendiente=comando)


def _con_rutas(monkeypatch, rutas, guion=()) -> ProveedorGuionado:
    proveedor = ProveedorGuionado(guion=list(guion), rutas=list(rutas))
    monkeypatch.setattr("prisma.llm.desde_base", lambda cur, ws, key: proveedor)
    return proveedor


def _abrir_modificar(cliente, conn, ws) -> tuple[int, str]:
    """Una vista previa de `registrar_bloqueo` y el toque en "Modificar"."""
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        pid = _proponer(cur, ws, quien, "registrar_bloqueo",
                        {"tarea_id": tid, "causa": CAUSA}, chat_id=tg,
                        ahora=datetime.now(timezone.utc))
        modificar = P.opcion_por_etiqueta(cur, pid, "Modificar")
    conn.commit()
    assert _tocar(cliente, modificar.token, tg).status_code == 200
    assert _abiertas(conn) == 1
    return tg, tid


def _abrir_ninguna(cliente, conn, ws) -> tuple[int, str]:
    """La aclaración con botones de una referencia y el toque en "Ninguna, lo
    escribo". Devuelve también una tarea, sólo para comprobar que nada la toca."""
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        p = P.registrar(
            cur, quien, herramienta=gateway._SENTINEL_ACLARACION,
            args={"mensaje": PEDIDO_ORIGINAL, "referencia_actual": REFERENCIA,
                  "pendientes": [], "candidatas": {}, "resueltas": {},
                  "titulos_resueltas": {}, "bloque_base": "",
                  "hay_clara": False, "route_action": "normal_conversation",
                  "route_task": {}, "modificacion": None, "entrante_id": None},
            resumen=f"¿A cuál te referís con «{REFERENCIA}»?",
            vence_en=datetime.now(timezone.utc).replace(year=2099),
            campo="eleccion", chat_id=tg,
            opciones=[("Ninguna, lo escribo", gateway._OPCION_NINGUNA)])
        ninguna = P.opcion_por_etiqueta(cur, p.id, "Ninguna, lo escribo")
    conn.commit()
    assert _tocar(cliente, ninguna.token, tg).status_code == 200
    assert _abiertas(conn) == 1
    return tg, tid


def _abrir(kind, cliente, conn, ws) -> tuple[int, str]:
    abrir = _abrir_modificar if kind == "modificar" else _abrir_ninguna
    return abrir(cliente, conn, ws)


def _abiertas(conn) -> int:
    """Preguntas que esperan el mensaje siguiente de la persona."""
    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from pending_action
                where modificar_pedido_en is not null
                  and modificacion_consumida_en is null""")
        return cur.fetchone()["n"]


def _salidas(conn, chat_id) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from message_outbox where chat_id = %s",
                    (chat_id,))
        return cur.fetchone()["n"]


def _filas_del_chat(conn, chat_id) -> list[dict]:
    with admin(conn) as cur:
        cur.execute(
            """select cuerpo, pending_action_id from message_outbox
                where chat_id = %s order by programado_para""", (chat_id,))
        return cur.fetchall()


def _ultimo_cuerpo(conn, chat_id) -> str:
    return _filas_del_chat(conn, chat_id)[-1]["cuerpo"]


def _incidentes(conn, ws) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s",
                    (ws,))
        return cur.fetchone()["n"]


def _bloqueos(conn, tid) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from blocker where task_id = %s", (tid,))
        return cur.fetchone()["n"]


def _vistas_previas(conn) -> int:
    """Vistas previas esperando Confirmar (las de la corrección, no la vieja)."""
    with admin(conn) as cur:
        cur.execute(
            """select count(*) n from pending_action
                where estado = 'esperando' and herramienta = 'registrar_bloqueo'""")
        return cur.fetchone()["n"]


def _botones_de(conn, ws, herramienta: str) -> list[dict]:
    with admin(conn) as cur:
        return _opciones(cur, _pendiente(cur, ws, herramienta))


def _tocar_boton(cliente, conn, ws, etiqueta: str, tg):
    fila = next(o for o in _botones_de(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU)
                if etiqueta in o["etiqueta"])
    assert _tocar(cliente, fila["token"], tg).status_code == 200


def _contexto_del_agente(proveedor) -> str:
    return proveedor.recibidos[-1][0]


# ---------------------------------------------------------------------------
# Cada comando, en cada tipo de pregunta
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", KINDS)
def test_charla_repite_la_pregunta_y_no_consume(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, tid = _abrir(kind, cliente, conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "hola")

    assert _abiertas(conn) == 1                               # sigue abierta
    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    assert PREGUNTAS[kind] in _ultimo_cuerpo(conn, tg)
    assert proveedor.recibidos == []                          # el agente no habló
    assert _bloqueos(conn, tid) == 0


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("comando", [
    RespectoPendiente.RESPONDE, RespectoPendiente.CORRIGE])
def test_responde_y_corrige_consumen_y_siguen_el_camino_de_siempre(
        cliente, conn, corework, monkeypatch, kind, comando):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(comando)],
                           guion=[Respuesta(texto="Anotado.")])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "es la de máq. 3" if kind == "ninguna"
             else "la causa es otra")

    assert _abiertas(conn) == 0                               # se consumió
    assert len(proveedor.ruteados) == 1                       # un solo ruteo
    assert CONTEXTOS[kind] in _contexto_del_agente(proveedor)
    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    assert _ultimo_cuerpo(conn, tg) == "Anotado."


@pytest.mark.parametrize("kind", KINDS)
def test_cancela_cierra_sin_efecto_y_lo_dice(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, tid = _abrir(kind, cliente, conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CANCELA)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "mejor dejalo así")

    assert _abiertas(conn) == 0
    assert _salidas(conn, tg) == antes + 1
    assert _ultimo_cuerpo(conn, tg) == DEJADAS[kind]
    assert proveedor.recibidos == []
    assert _bloqueos(conn, tid) == 0                          # sin efecto
    assert _vistas_previas(conn) == 0                         # ni vista previa


@pytest.mark.parametrize("kind", KINDS)
def test_no_puedo_avisa_repite_la_pregunta_y_no_consume(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.NO_PUEDO)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "mandá este archivo al cliente")

    cuerpo = _ultimo_cuerpo(conn, tg)
    assert gateway.AVISO_NO_PUEDO_DATO_PENDIENTE in cuerpo
    assert PREGUNTAS[kind] in cuerpo
    assert _salidas(conn, tg) == antes + 1
    assert _abiertas(conn) == 1


@pytest.mark.parametrize("kind", KINDS)
def test_dudoso_pregunta_con_dos_botones_sin_consumir(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO)])
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "puede ser")

    assert _salidas(conn, tg) == antes + 1                    # una respuesta
    ultima = _filas_del_chat(conn, tg)[-1]
    assert ultima["cuerpo"].startswith("¿Esto es ")
    assert ultima["pending_action_id"] is not None            # con botones
    etiquetas = [o["etiqueta"]
                 for o in _botones_de(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU)]
    assert etiquetas == [gateway.ETIQUETA_ES_EL_DATO,
                         gateway.ETIQUETA_NO_ES_EL_DATO]
    assert _abiertas(conn) == 1


@pytest.mark.parametrize("kind", KINDS)
def test_dudoso_si_consume_y_sigue_con_el_texto_original(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO)],
                           guion=[Respuesta(texto="Anotado.")])
    _mensaje(cliente, tg, "puede ser")
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, "Sí", tg)

    assert _abiertas(conn) == 0
    assert proveedor.ruteados == ["puede ser", "puede ser"]   # el "sí" la rutea
    assert CONTEXTOS[kind] in _contexto_del_agente(proveedor)
    assert _salidas(conn, tg) == antes + 1
    assert _ultimo_cuerpo(conn, tg) == "Anotado."


@pytest.mark.parametrize("kind", KINDS)
def test_dudoso_no_con_el_ruteo_caido_deja_una_respuesta_y_no_consume(
        cliente, conn, corework, monkeypatch, kind):
    # Seguimiento de review-dd7cd3c9cb7e8575: el botón "No, es otra cosa"
    # vuelve a rutear el texto; si eso falla, incidente, un aviso y la
    # pregunta sigue abierta.
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    malo = RouteEnvelope(calls=())
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO), malo, malo])
    _mensaje(cliente, tg, "puede ser")
    incidentes = _incidentes(conn, ws)
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, "No", tg)

    assert _incidentes(conn, ws) == incidentes + 1
    assert _salidas(conn, tg) == antes + 1                    # exactamente una
    assert _abiertas(conn) == 1


@pytest.mark.parametrize("kind", KINDS)
def test_falla_del_ruteo_registra_incidente_y_no_consume(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    malo = RouteEnvelope(calls=())
    _con_rutas(monkeypatch, [malo, malo])
    incidentes = _incidentes(conn, ws)
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "hola")

    assert _incidentes(conn, ws) == incidentes + 1
    assert _salidas(conn, tg) == antes + 1
    assert _abiertas(conn) == 1                               # no se perdió


@pytest.mark.parametrize("kind", KINDS)
def test_el_ruteo_recibe_la_descripcion_y_la_pregunta_literal(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje(cliente, tg, "hola")

    (pendiente,) = proveedor.pendientes
    assert proveedor.ruteados == ["hola"]
    assert PREGUNTAS[kind] in pendiente                       # la literal
    if kind == "modificar":
        assert CAUSA in pendiente                             # la propuesta
    else:
        assert REFERENCIA in pendiente and PEDIDO_ORIGINAL in pendiente


@pytest.mark.parametrize("kind", KINDS)
def test_responde_con_la_pregunta_ya_consumida_sigue_el_camino_normal_una_vez(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)],
                           guion=[Respuesta(texto="Anotado, seguimos.")])
    real = P.consumir_modificacion

    def consumida_por_otro_turno(cur, pending_action_id, ahora, **kw):
        real(cur, pending_action_id, ahora, **kw)
        return False

    monkeypatch.setattr(P, "consumir_modificacion", consumida_por_otro_turno)
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "lo de siempre")

    assert len(proveedor.ruteados) == 1
    assert CONTEXTOS[kind] not in _contexto_del_agente(proveedor)
    assert _salidas(conn, tg) == antes + 1
    assert _ultimo_cuerpo(conn, tg) == "Anotado, seguimos."


# ---------------------------------------------------------------------------
# Modificar: la corrección real llega a una vista previa nueva
# ---------------------------------------------------------------------------


def test_modificar_la_correccion_real_arma_la_vista_previa_nueva(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid = _abrir_modificar(cliente, conn, ws)
    guion = [Respuesta(llamadas=[Llamada("c1", "registrar_bloqueo", {
                 "tarea_id": tid, "causa": "se rompió el variador"})]),
             Respuesta(texto="listo")]
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CORRIGE)],
                           guion=guion)

    _mensaje(cliente, tg, "la causa es que se rompió el variador")

    assert _abiertas(conn) == 0
    assert _bloqueos(conn, tid) == 0                          # nada antes de Confirmar
    with admin(conn) as cur:
        cur.execute(
            """select resumen from pending_action
                where estado = 'esperando' and herramienta = 'registrar_bloqueo'""")
        (nueva,) = cur.fetchall()
    assert "variador" in nueva["resumen"]
    assert "propuesta anterior" in _contexto_del_agente(proveedor).lower()


# ---------------------------------------------------------------------------
# Contestar una pregunta pendiente no abre una búsqueda de tareas (T9-R1b-2,
# ADR 0013 regla 1, banco b-0020-b)
# ---------------------------------------------------------------------------

SUSTANTIVO = "el variador roto"


def _con_jev(monkeypatch, guion=()) -> ClienteJevGuionado:
    """Un Jev guionado que registra cada pedido (`doble.pedidos`)."""
    doble = ClienteJevGuionado(guion=list(guion))
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: doble)
    return doble


def _alcance(**probabilidades) -> dict:
    return {"probabilities": {"una_tarea": 0.0, "varias_tareas": 0.0,
                              "ninguna": 0.0, **probabilidades}}


# Lo que Jev contesta a `SUSTANTIVO`: sin tarea que coincida, o dudando entre
# dos (T1 y T2 son las tareas activas, sea cual sea su orden).
JEV_NINGUNA = [{"alcance": _alcance(ninguna=1.0)}]
JEV_AMBIGUA = [{"alcance": _alcance(una_tarea=0.8),
                "tarea": {"probabilities": {"T1": 0.5, "T2": 0.3}}}]
JEV_CLARA = [{"alcance": _alcance(una_tarea=0.95),
              "tarea": {"probabilities": {"T1": 0.9}}},
             {"misma": {"noul": 0.8}}]


def _ruta_con_trabajos(comando: RespectoPendiente) -> IntentRoute:
    return IntentRoute(IntentAction.NORMAL_CONVERSATION, trabajos=(SUSTANTIVO,),
                       respecto_pendiente=comando)


def _aclaraciones(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action where herramienta = %s",
                    (gateway._SENTINEL_ACLARACION,))
        return cur.fetchone()["n"]


def _otra_tarea(conn, ws) -> str:
    with admin(conn) as cur:
        tid = _tarea(cur, ws, titulo="Revisar variador línea 2")
    conn.commit()
    return tid


def _correccion_de_modificar(tid: str) -> list:
    return [Respuesta(llamadas=[Llamada("c1", "registrar_bloqueo", {
                "tarea_id": tid, "causa": "se rompió el variador"})]),
            Respuesta(texto="listo")]


def _nueva_vista_previa(conn) -> dict:
    with admin(conn) as cur:
        cur.execute(
            """select resumen from pending_action
                where estado = 'esperando' and herramienta = 'registrar_bloqueo'""")
        (nueva,) = cur.fetchall()
    return nueva


@pytest.mark.parametrize("comando", [
    RespectoPendiente.RESPONDE, RespectoPendiente.CORRIGE])
@pytest.mark.parametrize("respuesta_de_jev", [JEV_NINGUNA, JEV_AMBIGUA],
                         ids=["ninguna", "ambigua"])
def test_modificar_con_una_referencia_no_clara_sigue_con_la_tarea_de_la_propuesta(
        cliente, conn, corework, monkeypatch, comando, respuesta_de_jev):
    ws = corework.workspace_id
    tg, tid = _abrir_modificar(cliente, conn, ws)
    _otra_tarea(conn, ws)
    doble = _con_jev(monkeypatch, respuesta_de_jev)
    proveedor = _con_rutas(monkeypatch, [_ruta_con_trabajos(comando)],
                           guion=_correccion_de_modificar(tid))
    antes = _salidas(conn, tg)

    _mensaje(cliente, tg, "el motivo real es que se rompió el variador")

    assert doble.pedidos                                      # Jev se consulta
    assert _aclaraciones(conn) == 0                           # sin "¿A cuál…?"
    assert _abiertas(conn) == 0                               # se consumió
    sistema = _contexto_del_agente(proveedor)
    assert "propuesta anterior" in sistema.lower()
    assert "Referencias a tareas" not in sistema              # como si no estuviera
    assert "variador" in _nueva_vista_previa(conn)["resumen"]  # la vista previa nueva
    assert _salidas(conn, tg) == antes + 1                    # una respuesta


def test_modificar_con_una_referencia_clara_a_otra_tarea_la_cambia(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid = _abrir_modificar(cliente, conn, ws)
    otra = _otra_tarea(conn, ws)
    doble = _con_jev(monkeypatch, JEV_CLARA)
    proveedor = _con_rutas(
        monkeypatch, [_ruta_con_trabajos(RespectoPendiente.CORRIGE)],
        guion=_correccion_de_modificar(otra))

    _mensaje(cliente, tg, "no, era la del variador")

    assert doble.pedidos
    assert _aclaraciones(conn) == 0
    sistema = _contexto_del_agente(proveedor)
    assert "propuesta anterior" in sistema.lower()
    assert f"«{SUSTANTIVO}» es la tarea «" in sistema         # la resolución llega
    assert "Usá esa tarea" in sistema


def test_modificar_si_es_eso_con_una_referencia_ambigua_no_abre_aclaracion(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, tid = _abrir_modificar(cliente, conn, ws)
    _otra_tarea(conn, ws)
    doble = _con_jev(monkeypatch, JEV_AMBIGUA)
    proveedor = _con_rutas(
        monkeypatch,
        [_ruta(RespectoPendiente.DUDOSO),
         IntentRoute(IntentAction.NORMAL_CONVERSATION, trabajos=(SUSTANTIVO,))],
        guion=_correccion_de_modificar(tid))
    _mensaje(cliente, tg, "puede ser el variador")
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, "Sí", tg)

    assert doble.pedidos
    assert _aclaraciones(conn) == 0
    assert "propuesta anterior" in _contexto_del_agente(proveedor).lower()
    assert "variador" in _nueva_vista_previa(conn)["resumen"]
    assert _salidas(conn, tg) == antes + 1


@pytest.mark.parametrize("solo_claras", [True, False],
                         ids=["solo_claras", "todas"])
def test_una_referencia_sin_resolucion_ni_error_se_ignora_sin_romper(
        conn, corework, monkeypatch, solo_claras):
    # Seguimiento de review-34b692649e0734e7: el contrato dice que `resolucion`
    # sólo es `None` con un error, pero un Jev que devolviera `(None, None)`
    # tiraba `AttributeError` (auditoría y filtro `solo_claras`) y el mensaje
    # se perdía. Se trata como una referencia no resuelta.
    ws = corework.workspace_id
    _con_jev(monkeypatch)
    monkeypatch.setattr(gateway, "_resolver_en_paralelo",
                        lambda *a, **k: {SUSTANTIVO: (None, None)})
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        resultado = gateway._resolver_referencias_del_turno(
            cur, quien, "el variador roto", _ruta_con_trabajos(None), ws,
            solo_claras=solo_claras)

    if solo_claras:
        assert resultado is None                       # como si no estuviera
    else:
        assert resultado is not None and not resultado.hay_clara
        assert resultado.resueltas_claras == {}


# ---------------------------------------------------------------------------
# `otro_tema` (T9-R1d): el mensaje no se atiende hasta que la persona decide;
# al dejar lo pendiente se atiende como un turno normal, referencias incluidas
# ---------------------------------------------------------------------------


def test_dejar_y_ver_lo_otro_resuelve_las_referencias_del_mensaje_guardado(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _tid = _abrir_modificar(cliente, conn, ws)
    doble = ClienteJevGuionado(guion=[
        {"alcance": {"probabilities": {"una_tarea": 0.0, "varias_tareas": 0.0,
                                       "ninguna": 1.0}}}])
    monkeypatch.setattr(jev_modulo, "desde_base", lambda api_key: doble)
    proveedor = _con_rutas(
        monkeypatch, [_ruta_con_trabajos(RespectoPendiente.OTRO_TEMA),
                      _ruta_con_trabajos(None)],
        guion=[Respuesta(texto="No encontré esa tarea.")])

    _mensaje(cliente, tg, "¿cómo va el variador roto?")

    assert doble.pedidos == []                                # todavía no se atiende
    assert proveedor.recibidos == []
    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)

    assert doble.pedidos, "las referencias del mensaje guardado sí se resuelven"
    assert SUSTANTIVO in _contexto_del_agente(proveedor)
    assert _abiertas(conn) == 0                               # lo pendiente se dejó


# ---------------------------------------------------------------------------
# "Sí, es eso" con el ruteo caído (review-e95b2d47b01f0161)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", KINDS)
def test_si_es_eso_con_el_ruteo_caido_deja_una_respuesta_y_no_consume(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    tg, _tid = _abrir(kind, cliente, conn, ws)
    malo = RouteEnvelope(calls=())
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO), malo, malo])
    _mensaje(cliente, tg, "puede ser")
    incidentes = _incidentes(conn, ws)
    antes = _salidas(conn, tg)

    _tocar_boton(cliente, conn, ws, "Sí", tg)

    assert _incidentes(conn, ws) == incidentes + 1
    assert _salidas(conn, tg) == antes + 1                    # exactamente una
    assert _abiertas(conn) == 1                               # no se perdió
