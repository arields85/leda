"""La elección con botones que Leda le pidió a la persona es una rama abierta
(T9-R1d-1c, ADR 0013 regla 1, enmienda "una sola rama de conversación abierta";
ADR 0005 decisión 3).

Una elección con botones -- la aclaración "¿A cuál te referís?", la de con cuál
otra tarea se declara una dependencia, la que pide una herramienta (`campo`) --
es algo que la persona empezó y que Leda espera de ella para terminarlo. El
mensaje siguiente se interpreta contra esa elección con el ruteo tipado, igual
que con las demás preguntas abiertas:

- `responde`: si el texto es exactamente UNA de las opciones (mismo criterio que
  la elección del alta: sin mayúsculas, sin ícono, sin acentos de más), se toma
  como el toque; si no, la elección vuelve a mostrarse con sus botones.
- `cancela`: se cierra y se dice qué se dejó de lado.
- `otro_tema`: la pregunta de la rama; "Dejarlo" cierra la elección y atiende
  el mensaje guardado.
- `charla`, `no_puedo`, `dudoso`, `corrige` y el ruteo caído: lo mismo que en
  las demás preguntas.

No son una rama las ofertas de camino: las listas de tareas, el menú de una
tarea y "Quiero consultar otra cosa" (`ofrecer_opciones`), ni lo que le llega a
alguien para decidir, ni la pregunta de la propia rama.

Los ruteos y el modelo se guionan con `ProveedorGuionado`; nada toca la red.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from leda import gateway
from leda import pendientes as P
from leda.db import admin, espacio
from leda.llm import Llamada, RespectoPendiente, Respuesta
from leda.salida import ICONO_TAREA, con_icono, enqueue_outbox

from tests.test_menu_tarea import (_mensaje, _opciones, _pendiente, _quien,  # noqa: F401
                                   _telegram_id, _tocar, cliente)
from tests.test_modificar import _proponer, _tarea
from tests.test_pregunta_pendiente_otras import (_botones_de, _con_rutas,
                                                 _filas_del_chat, _incidentes,
                                                 _ruta, _salidas, _tocar_boton,
                                                 _ultimo_cuerpo)

PERSONA = "Marcos Tarquini"
CAUSA = "falta el switch"
OTRO_MENSAJE = "¿qué tareas tengo abiertas?"
RESPUESTA = "Tenés dos tareas abiertas."
TITULO_1 = "Programar PLC de la comprimidora 3"
TITULO_2 = "Revisar variador línea 2"
KINDS = ["aclaracion", "dependencia", "herramienta"]


def _dice_el_estado_real(cuerpo: str) -> bool:
    """La respuesta a un botón vencido (C0-5): que ya no vale y el estado real de lo
    que tocaba, con un próximo paso; nunca el aviso de que no se sabe qué era."""
    return (cuerpo.startswith(gateway.AVISO_BOTON_VENCIDO)
            and cuerpo != gateway.AVISO_PEDIDO_NO_VIGENTE)


@dataclass
class _Eleccion:
    tg: int
    pid: str
    t1: str          # la tarea que se elige escribiendo "programar plc"
    t2: str
    nombre: str      # cómo se la nombra en la pregunta de la rama
    dejada: str      # lo que se dice al dejarla de lado


def _dos_tareas(conn, ws, titulos=(TITULO_1, TITULO_2)) -> tuple[str, str]:
    with admin(conn) as cur:
        t1 = _tarea(cur, ws, titulo=titulos[0])
        t2 = _tarea(cur, ws, titulo=titulos[1])
    conn.commit()
    return t1, t2


def _abrir_aclaracion(conn, ws) -> _Eleccion:
    """La aclaración con botones de una referencia ambigua, como la deja
    `gateway._preguntar_por_botones`."""
    t1, t2 = _dos_tareas(conn, ws)
    candidatas = [
        {"id": t1, "etiqueta": con_icono("Programar PLC", ICONO_TAREA),
         "titulo": TITULO_1},
        {"id": t2, "etiqueta": con_icono("Revisar variador", ICONO_TAREA),
         "titulo": TITULO_2}]
    estado = {
        "mensaje": "avisame de lo del tablero", "entrante_id": None,
        "route_action": "normal_conversation", "route_task": {},
        "resueltas": {}, "titulos_resueltas": {}, "bloque_base": "",
        "hay_clara": False, "pendientes": ["el cableado"],
        "candidatas": {"el cableado": candidatas}, "modificacion": None,
        "no_proponer": None}
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        gateway._preguntar_por_botones(cur, quien, ws, tg,
                                       datetime.now(timezone.utc), estado)
        pid = _pendiente(cur, ws, gateway._SENTINEL_ACLARACION)
    conn.commit()
    return _Eleccion(
        tg, pid, t1, t2,
        nombre="la tarea a la que te referías con «el cableado»",
        dejada=gateway.AVISO_ACLARACION_DEJADA)


def _abrir_dependencia(conn, ws) -> _Eleccion:
    """La elección de con cuál otra tarea se declara una dependencia (menú de
    una tarea): `SENTINEL_DATO_MENU_TAREA` con `campo`."""
    t1, t2 = _dos_tareas(conn, ws, ("Programar PLC", "Revisar variador"))
    with admin(conn) as cur:
        origen = _tarea(cur, ws, titulo="Cablear tablero")
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        gateway._pedir_eleccion_dependencia(
            cur, quien, ws, tg, accion="crear_dependencia_origen",
            tarea_id=origen, titulo="Cablear tablero",
            pregunta="¿De cuál de tus tareas depende «Cablear tablero»?",
            candidatas=[(t1, "Programar PLC"), (t2, "Revisar variador")],
            ahora=datetime.now(timezone.utc))
        pid = _pendiente(cur, ws, P.SENTINEL_DATO_MENU_TAREA)
    conn.commit()
    return _Eleccion(
        tg, pid, t1, t2, nombre="la elección de la otra tarea para «Cablear tablero»",
        dejada=gateway.AVISO_ELECCION_DEJADA)


def _abrir_herramienta(conn, ws) -> _Eleccion:
    """La elección que pide una herramienta con un argumento ambiguo
    (`NecesitaElegir`, `agente._encolar_eleccion`): la herramienta real y su
    `campo`."""
    t1, t2 = _dos_tareas(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        p = P.registrar(
            cur, quien, herramienta="registrar_bloqueo", args={"causa": CAUSA},
            resumen="¿En cuál tarea?", campo="tarea_id",
            opciones=[("Programar PLC", t1), ("Revisar variador", t2)],
            vence_en=datetime.now(timezone.utc) + timedelta(hours=8), chat_id=tg)
        enqueue_outbox(
            cur, workspace_id=ws, chat_id=tg,
            recipient_membership_id=quien.membership_id, text=p.resumen,
            dedupe_key=f"{ws}:elegir:test:{p.id}", is_response=True,
            pending_action_id=p.id)
        pid = p.id
    conn.commit()
    return _Eleccion(tg, pid, t1, t2, nombre="la elección que te pedí",
                     dejada=gateway.AVISO_ELECCION_DEJADA)


_ABRIR = {"aclaracion": _abrir_aclaracion, "dependencia": _abrir_dependencia,
          "herramienta": _abrir_herramienta}


def _estado(conn, pid: str) -> str:
    with admin(conn) as cur:
        cur.execute("select estado from pending_action where id = %s", (pid,))
        return cur.fetchone()["estado"]


def _mostradas(conn, tg: int, pid: str) -> list[dict]:
    """Los mensajes de este chat que llevan los botones de esta elección."""
    return [f for f in _filas_del_chat(conn, tg)
            if str(f["pending_action_id"]) == pid]


def _abierta_de(conn, ws, tg: int, *, alta: bool = False):
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        return gateway._ver_pregunta_abierta(
            cur, quien, tg, datetime.now(timezone.utc), alta=alta)


def _tocar_opcion(cliente, conn, pid: str, etiqueta: str, tg: int):
    with admin(conn) as cur:
        token = P.opcion_por_etiqueta(cur, pid, etiqueta).token
    return _tocar(cliente, token, tg)


def _bloqueos(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from blocker")
        return cur.fetchone()["n"]


def _dependencias_esperando(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select args from pending_action where estado = 'esperando' "
                    "and herramienta = 'crear_dependencia'")
        return cur.fetchall()


def _efecto_de_elegir_la_primera(kind: str, e: _Eleccion, conn, proveedor) -> None:
    """Lo que deja elegir «Programar PLC» (tocando o escribiendo)."""
    if kind == "aclaracion":
        # Retomó el pedido original con esa tarea ya resuelta.
        assert f"«{TITULO_1}»" in proveedor.recibidos[-1][0]
    elif kind == "dependencia":
        (vista,) = _dependencias_esperando(conn)            # la vista previa
        assert e.t1 in str(vista["args"])
    else:
        assert _bloqueos(conn) == 1                         # la herramienta corrió


# ---------------------------------------------------------------------------
# responde: exactamente una opción se toma como el toque; si no, vuelve a mostrarse
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("escrito", ["Programar PLC", "  programar   plc ",
                                     "PROGRAMAR PLC"])
def test_responde_con_exactamente_una_opcion_se_toma_como_el_toque(
        cliente, conn, corework, monkeypatch, kind, escrito):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)],
                           guion=[Respuesta(texto=RESPUESTA)])
    antes = _salidas(conn, e.tg)

    _mensaje(cliente, e.tg, escrito)

    assert _estado(conn, e.pid) == "resuelta"                 # como si la hubiera tocado
    assert _salidas(conn, e.tg) == antes + 1                  # una respuesta
    _efecto_de_elegir_la_primera(kind, e, conn, proveedor)
    # El botón de la otra opción ya no vale: la elección está resuelta.
    assert _tocar_opcion(cliente, conn, e.pid, "Revisar variador",
                         e.tg).status_code == 200
    assert _dice_el_estado_real(_ultimo_cuerpo(conn, e.tg))


def test_responde_con_el_titulo_completo_toma_la_opcion_de_la_aclaracion(
        cliente, conn, corework, monkeypatch):
    # El botón muestra el título acortado; el título entero de la candidata
    # también la identifica.
    ws = corework.workspace_id
    e = _abrir_aclaracion(conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)],
                           guion=[Respuesta(texto=RESPUESTA)])

    _mensaje(cliente, e.tg, TITULO_1.lower())

    assert _estado(conn, e.pid) == "resuelta"
    _efecto_de_elegir_la_primera("aclaracion", e, conn, proveedor)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("escrito", ["la de la comprimidora", "programar",
                                     "el primero", "las dos"])
def test_responde_sin_coincidir_con_una_sola_opcion_vuelve_a_mostrar_la_eleccion(
        cliente, conn, corework, monkeypatch, kind, escrito):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = _salidas(conn, e.tg)
    botones = len(_mostradas(conn, e.tg, e.pid))

    _mensaje(cliente, e.tg, escrito)

    assert _estado(conn, e.pid) == "esperando"                # nada se tomó
    assert proveedor.recibidos == []                          # el agente no habló
    assert _salidas(conn, e.tg) == antes + 1
    assert len(_mostradas(conn, e.tg, e.pid)) == botones + 1  # con sus botones
    assert _bloqueos(conn) == 0 and _dependencias_esperando(conn) == []


def test_una_opcion_repetida_no_se_toma_por_adivinanza(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    t1, t2 = _dos_tareas(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        p = P.registrar(
            cur, quien, herramienta="registrar_bloqueo", args={"causa": CAUSA},
            resumen="¿En cuál tarea?", campo="tarea_id",
            opciones=[("Programar PLC", t1), ("Programar PLC", t2)],
            vence_en=datetime.now(timezone.utc) + timedelta(hours=8), chat_id=tg)
    conn.commit()
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])

    _mensaje(cliente, tg, "programar plc")

    assert _estado(conn, p.id) == "esperando" and _bloqueos(conn) == 0


# ---------------------------------------------------------------------------
# Cada comando
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_el_ruteo_recibe_la_eleccion_con_sus_opciones_como_la_pregunta_pendiente(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])

    _mensaje(cliente, e.tg, "hola")

    (pendiente,) = proveedor.pendientes
    assert "Programar PLC" in pendiente and "Revisar variador" in pendiente


@pytest.mark.parametrize("kind", KINDS)
def test_cancela_cierra_la_eleccion_y_dice_que_se_dejo_de_lado(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CANCELA)])
    antes = _salidas(conn, e.tg)

    _mensaje(cliente, e.tg, "no, dejá, mejor no")

    assert _estado(conn, e.pid) == "cancelada"
    assert _salidas(conn, e.tg) == antes + 1
    assert _ultimo_cuerpo(conn, e.tg) == e.dejada
    assert proveedor.recibidos == []
    assert _bloqueos(conn) == 0
    _tocar_opcion(cliente, conn, e.pid, "Programar PLC", e.tg)   # el botón ya no vale
    assert _dice_el_estado_real(_ultimo_cuerpo(conn, e.tg))
    assert _bloqueos(conn) == 0 and _dependencias_esperando(conn) == []


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("comando", [RespectoPendiente.CHARLA,
                                     RespectoPendiente.NO_PUEDO])
def test_charla_y_no_puedo_vuelven_a_mostrar_la_eleccion_sin_cerrarla(
        cliente, conn, corework, monkeypatch, kind, comando):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(comando)])
    antes = _salidas(conn, e.tg)

    _mensaje(cliente, e.tg, "hola")

    assert _estado(conn, e.pid) == "esperando"
    assert _salidas(conn, e.tg) == antes + 1
    assert len(_mostradas(conn, e.tg, e.pid)) == 2            # con sus botones
    assert proveedor.recibidos == []


@pytest.mark.parametrize("kind", KINDS)
def test_dudoso_pregunta_con_dos_botones_y_no_es_otra_cosa_deja_la_eleccion(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
               guion=[Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, e.tg, "puede ser")
    assert "¿Esto es" in _ultimo_cuerpo(conn, e.tg)
    assert _estado(conn, e.pid) == "esperando"

    _tocar_boton(cliente, conn, ws, "No, es otra cosa", e.tg)

    assert _estado(conn, e.pid) == "cancelada"
    assert RESPUESTA in _ultimo_cuerpo(conn, e.tg)


@pytest.mark.parametrize("kind", KINDS)
def test_dudoso_si_es_eso_con_una_opcion_exacta_la_toma(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.DUDOSO)],
                           guion=[Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, e.tg, "programar plc")

    _tocar_boton(cliente, conn, ws, "Sí, es eso", e.tg)

    assert _estado(conn, e.pid) == "resuelta"
    _efecto_de_elegir_la_primera(kind, e, conn, proveedor)


@pytest.mark.parametrize("kind", KINDS)
def test_corrige_no_es_la_respuesta_y_lo_decide_la_persona_con_botones(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CORRIGE)])

    _mensaje(cliente, e.tg, "en realidad era otra")

    assert _estado(conn, e.pid) == "esperando"
    assert "¿Esto es" in _ultimo_cuerpo(conn, e.tg)


@pytest.mark.parametrize("kind", KINDS)
def test_ruteo_caido_deja_la_eleccion_abierta_y_avisa(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)

    class _Caido:
        recibidos: list = []

        def route_intent(self, texto, pendiente=None):
            raise RuntimeError("caído")

    monkeypatch.setattr("leda.llm.desde_base", lambda cur, w, key: _Caido())
    antes = _salidas(conn, e.tg)

    _mensaje(cliente, e.tg, "programar plc")

    assert _estado(conn, e.pid) == "esperando"
    assert _salidas(conn, e.tg) == antes + 1
    assert _incidentes(conn, ws) >= 1


# ---------------------------------------------------------------------------
# La rama: otro tema pregunta, Seguir repite la elección, Dejar cierra y atiende
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_otro_tema_pregunta_por_la_rama_sin_atender_ni_cerrar_la_eleccion(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    antes = _salidas(conn, e.tg)

    _mensaje(cliente, e.tg, OTRO_MENSAJE)

    assert _estado(conn, e.pid) == "esperando"
    assert proveedor.recibidos == []                          # el otro tema no se atiende
    assert _salidas(conn, e.tg) == antes + 1
    assert f"Estábamos con {e.nombre}" in _ultimo_cuerpo(conn, e.tg)
    assert len(_botones_de(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU)) == 2
    # La elección conserva sus propios botones mientras la rama espera.
    assert _tocar_opcion(cliente, conn, e.pid, "Programar PLC",
                         e.tg).status_code == 200
    assert _estado(conn, e.pid) == "resuelta"


@pytest.mark.parametrize("kind", KINDS)
def test_seguir_vuelve_a_mostrar_la_eleccion_con_sus_botones(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    _mensaje(cliente, e.tg, OTRO_MENSAJE)
    antes = _salidas(conn, e.tg)

    _tocar_boton(cliente, conn, ws, "Seguir", e.tg)

    assert _estado(conn, e.pid) == "esperando"
    assert _salidas(conn, e.tg) == antes + 1
    assert len(_mostradas(conn, e.tg, e.pid)) == 2


@pytest.mark.parametrize("kind", KINDS)
def test_dejar_cierra_la_eleccion_y_atiende_lo_otro_en_la_misma_respuesta(
        cliente, conn, corework, monkeypatch, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, e.tg, OTRO_MENSAJE)

    _tocar_boton(cliente, conn, ws, "Dejarlo", e.tg)

    assert _estado(conn, e.pid) == "cancelada"
    cuerpos = [f["cuerpo"] for f in _filas_del_chat(conn, e.tg)[-2:]]
    assert e.dejada in cuerpos[0] and RESPUESTA in cuerpos[1]
    assert len(proveedor.recibidos) == 1                      # lo otro sí se atendió
    assert _bloqueos(conn) == 0 and _dependencias_esperando(conn) == []


def test_dejar_una_eleccion_de_herramienta_con_su_id_no_vuelve_a_proponerla(
        cliente, conn, corework, monkeypatch):
    # La guarda es la de las demás preguntas: la herramienta sobre el id que
    # llevan sus argumentos congelados.
    ws = corework.workspace_id
    t1, _t2 = _dos_tareas(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        p = P.registrar(
            cur, quien, herramienta="registrar_bloqueo",
            args={"tarea_id": t1, "causa": CAUSA}, resumen="¿Cuál causa?",
            campo="causa", opciones=[("Falta el switch", CAUSA), ("Otra", "otra")],
            vence_en=datetime.now(timezone.utc) + timedelta(hours=8), chat_id=tg)
    conn.commit()
    _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(llamadas=[Llamada("q", "registrar_bloqueo", {
                   "tarea_id": t1, "causa": CAUSA})]),
               Respuesta(texto=RESPUESTA)])
    _mensaje(cliente, tg, OTRO_MENSAJE)

    _tocar_boton(cliente, conn, ws, "Dejarlo", tg)

    assert _estado(conn, p.id) == "cancelada"
    with admin(conn) as cur:
        cur.execute("select count(*) n from pending_action where estado = "
                    "'esperando' and herramienta = 'registrar_bloqueo'")
        assert cur.fetchone()["n"] == 0                       # no se volvió a proponer


def test_seguir_tarde_dice_que_ya_no_estaba_pendiente(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    e = _abrir_aclaracion(conn, ws)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    _mensaje(cliente, e.tg, OTRO_MENSAJE)
    _con_rutas(monkeypatch, [], guion=[Respuesta(texto=RESPUESTA)])
    assert _tocar_opcion(cliente, conn, e.pid, "Programar PLC",
                         e.tg).status_code == 200           # otro camino la cerró
    antes = _salidas(conn, e.tg)

    _tocar_boton(cliente, conn, ws, "Seguir", e.tg)

    assert _salidas(conn, e.tg) == antes + 1
    assert _ultimo_cuerpo(conn, e.tg) == gateway.AVISO_RAMA_YA_CERRADA


# ---------------------------------------------------------------------------
# Qué es y qué no es una rama, y la precedencia con las demás
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_una_eleccion_esperando_es_la_rama_abierta(conn, corework, kind):
    ws = corework.workspace_id
    e = _ABRIR[kind](conn, ws)

    abierta = _abierta_de(conn, ws, e.tg)

    assert abierta.pregunta_id == e.pid
    assert abierta.herramienta == gateway._SENTINEL_ELECCION
    if kind == "herramienta":
        assert abierta.args["herramienta"] == "registrar_bloqueo"
        assert abierta.args["campo"] == "tarea_id"


@pytest.mark.parametrize("como", ["vencida", "tocada", "cancelada"])
def test_una_eleccion_vencida_o_resuelta_no_es_una_rama(
        cliente, conn, corework, monkeypatch, como):
    ws = corework.workspace_id
    e = _abrir_aclaracion(conn, ws)
    if como == "vencida":
        with admin(conn) as cur:
            cur.execute("update pending_action set vence_en = now() - interval "
                        "'1 minute' where id = %s", (e.pid,))
        conn.commit()
    elif como == "tocada":
        _con_rutas(monkeypatch, [], guion=[Respuesta(texto=RESPUESTA)])
        _tocar_opcion(cliente, conn, e.pid, "Programar PLC", e.tg)
    else:
        with admin(conn) as cur:
            cur.execute("update pending_action set estado = 'cancelada' "
                        "where id = %s", (e.pid,))
        conn.commit()

    assert _abierta_de(conn, ws, e.tg) is None


def test_una_eleccion_de_otra_persona_o_de_otro_chat_no_es_la_rama_de_quien_escribe(
        conn, corework):
    ws = corework.workspace_id
    e = _abrir_aclaracion(conn, ws)
    with espacio(conn, ws) as cur:
        otra = _quien(cur, "Nahuel Gimenez", ws)
        propia = _quien(cur, PERSONA, ws)
        ahora = datetime.now(timezone.utc)
        assert gateway._ver_pregunta_abierta(cur, otra, e.tg, ahora,
                                             alta=False) is None
        assert gateway._ver_pregunta_abierta(cur, propia, e.tg + 1, ahora,
                                             alta=False) is None


def test_las_ofertas_de_camino_no_son_una_rama(conn, corework):
    # Listas de tareas, el menú de una tarea y "Quiero consultar otra cosa"
    # sólo ofrecen caminos; la pregunta de la propia rama tampoco.
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        vence = datetime.now(timezone.utc) + timedelta(hours=8)
        for herramienta, args in [
                (P.SENTINEL_OPCIONES_MODELO, {"pregunta": "¿Cuál?"}),
                (P.SENTINEL_MENU_TAREA, {"tarea_id": tid, "titulo": "Programar PLC"}),
                (P.SENTINEL_RESPUESTA_DATO_MENU, {"texto": "hola"})]:
            P.registrar(cur, quien, herramienta=herramienta, args=args,
                        resumen="¿Qué hacemos?", campo="eleccion", vence_en=vence,
                        opciones=[("Una", {"tipo": "texto"}), ("Otra", {})],
                        chat_id=tg)
    conn.commit()

    assert _abierta_de(conn, ws, tg) is None


def test_una_eleccion_que_le_llega_a_otro_para_decidir_no_es_una_rama_suya(
        conn, corework):
    # El aviso de entrega comparte `SENTINEL_MENU_TAREA` y `campo` con el
    # menú: es un mensaje que inicia Leda (ADR 0013, enmienda).
    ws = corework.workspace_id
    with admin(conn) as cur:
        tid = _tarea(cur, ws)
    conn.commit()
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        tg = _telegram_id(cur, PERSONA)
        P.registrar(
            cur, quien, herramienta=P.SENTINEL_MENU_TAREA,
            args={"tarea_id": tid, "titulo": "Programar PLC",
                  "aviso": P.AVISO_ENTREGA},
            resumen="Nahuel entregó «Programar PLC»", campo="eleccion",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=8),
            opciones=[("Aprobar", {"accion": "aprobar"})], chat_id=tg)
    conn.commit()

    assert _abierta_de(conn, ws, tg) is None


def test_la_eleccion_gana_a_la_vista_previa_y_pierde_con_lo_que_se_espera_escrito(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    e = _abrir_aclaracion(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        vista = _proponer(cur, ws, quien, "registrar_bloqueo",
                          {"tarea_id": e.t1, "causa": CAUSA}, chat_id=e.tg,
                          ahora=datetime.now(timezone.utc))
    conn.commit()

    # Con la vista previa esperando, la elección (lo último que se preguntó)
    # es la rama; la vista previa sigue esperando su Confirmar.
    assert _abierta_de(conn, ws, e.tg).pregunta_id == e.pid
    assert _estado(conn, vista) == "esperando"

    # Un Modificar pedido (el dato se escribe) gana a la elección.
    with espacio(conn, ws) as cur:
        modificar = P.opcion_por_etiqueta(cur, vista, "Modificar")
    conn.commit()
    assert _tocar(cliente, modificar.token, e.tg).status_code == 200
    abierta = _abierta_de(conn, ws, e.tg)
    assert abierta.pregunta_id == vista
    assert abierta.herramienta == "registrar_bloqueo"


def test_con_una_pregunta_del_alta_abierta_gana_el_alta(conn, corework):
    from tests.test_alta_pregunta_pendiente import _abrir_alta

    ws = corework.workspace_id
    tg, _request_id = _abrir_alta(conn, ws)
    with espacio(conn, ws) as cur:
        quien = _quien(cur, PERSONA, ws)
        P.registrar(
            cur, quien, herramienta=gateway._SENTINEL_ACLARACION,
            args={"referencia_actual": "el cableado", "mensaje": "hola"},
            resumen="¿A cuál te referís con «el cableado»?", campo="eleccion",
            vence_en=datetime.now(timezone.utc) + timedelta(hours=8),
            opciones=[("Ninguna, lo escribo", gateway._OPCION_NINGUNA)],
            chat_id=tg)
    conn.commit()

    assert _abierta_de(conn, ws, tg, alta=True).herramienta in gateway._TIPO_DE_ALTA
    assert _abierta_de(conn, ws, tg, alta=False).herramienta == gateway._SENTINEL_ELECCION


def test_ninguna_lo_escribo_sigue_siendo_la_pregunta_de_la_aclaracion_escrita(
        cliente, conn, corework, monkeypatch):
    # Tocar "Ninguna, lo escribo" cierra la elección y abre la pregunta escrita
    # de siempre (`_SENTINEL_ACLARACION` como corrección): no es la elección.
    ws = corework.workspace_id
    e = _abrir_aclaracion(conn, ws)

    assert _tocar_opcion(cliente, conn, e.pid, "Ninguna, lo escribo",
                         e.tg).status_code == 200

    abierta = _abierta_de(conn, ws, e.tg)
    assert abierta.herramienta == gateway._SENTINEL_ACLARACION
    assert _ultimo_cuerpo(conn, e.tg) == gateway.PREGUNTA_ACLARACION_NINGUNA


def test_una_eleccion_larga_vuelve_a_mostrarse_con_sus_botones_sin_fallar(
        cliente, conn, corework, monkeypatch):
    """La elección que entra con sus botones sólo al límite, sin el margen del
    saludo, no puede tirar el turno al volver a mostrarse sin prefijo
    (review-faccc0e9d83561b3): el texto entero sale primero, en partes, y la
    elección después, con un texto corto y sus botones. Nunca un aviso solo ni
    una respuesta vacía, ni un incidente."""
    from leda.salida import BUTTON_TEXT_LIMIT, telegram_utf16_units

    ws = corework.workspace_id
    e = _abrir_herramienta(conn, ws)
    largo = ("¿En cuál tarea? " + "detalle de la elección " * 200)[:BUTTON_TEXT_LIMIT]
    assert telegram_utf16_units(largo) <= BUTTON_TEXT_LIMIT
    with admin(conn) as cur:
        cur.execute("update pending_action set resumen = %s where id = %s",
                    (largo, e.pid))
    conn.commit()
    # La respuesta breve de la charla (F-B5) también va delante: es parte del
    # prefijo que no debe tirar el turno.
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)]).borradores = [
        "Hola, un gusto."]
    antes = _filas_del_chat(conn, e.tg)

    _mensaje(cliente, e.tg, "hola")

    assert _estado(conn, e.pid) == "esperando"
    assert _incidentes(conn, ws) == 0
    nuevas = _filas_del_chat(conn, e.tg)[len(antes):]
    assert len(nuevas) >= 2
    *partes, botones = nuevas
    assert botones["pending_action_id"] is not None            # los botones, al final
    assert all(p["pending_action_id"] is None for p in partes)
    assert botones["cuerpo"].strip()                           # nunca vacío
    texto = " ".join(p["cuerpo"].split("\n", 1)[-1] for p in partes)
    assert "detalle de la elección" in texto                   # el texto entero salió
    assert _tocar_opcion(cliente, conn, e.pid, "Programar PLC",
                         e.tg).status_code == 200              # y el botón sirve
