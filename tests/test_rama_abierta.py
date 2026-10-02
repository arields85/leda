"""Una sola rama de conversación abierta (T9-R1d-1a, ADR 0013 regla 1, enmienda
del 2026-09-29).

Con una pregunta pendiente (el dato de una acción del menú, Modificar, "Ninguna,
lo escribo", un campo de texto libre del alta), un mensaje de otro tema ya no se
atiende: Leda pregunta con dos botones si se sigue con lo pendiente o se lo
deja para ver lo otro. Seguir repite la pregunta; Dejar cierra lo pendiente como
`cancela` y atiende, en la misma respuesta, el mensaje que quedó guardado.

Las elecciones del alta y el borrador esperando confirmación (otras dos clases de
pregunta) se prueban en `test_alta_eleccion_confirmacion.py`.

Los ruteos se guionan con `ProveedorGuionado`; ninguna prueba toca la red ni el
modelo real.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from leda import gateway
from leda import ingreso_tareas as I
from leda import pendientes as P
from leda.db import admin, espacio
from leda.llm import RespectoPendiente, Respuesta, RouteEnvelope

from tests.test_alta_pregunta_pendiente import (_abrir_alta, _campo_del_slot,
                                                _mensaje_privado, _request)
from tests.toques import FUERA_DE_LA_VENTANA, envejecer_toques
from tests.test_menu_tarea import _mensaje, _quien, _tocar, cliente  # noqa: F401
from tests.test_pregunta_pendiente import TITULO, _abrir_pregunta
from tests.test_pregunta_pendiente_otras import (REFERENCIA,
                                                 _abiertas, _abrir_modificar,
                                                 _abrir_ninguna, _botones_de,
                                                 _con_rutas, _filas_del_chat,
                                                 _incidentes, _ruta, _salidas,
                                                 _ultimo_cuerpo)

OTRO_MENSAJE = "¿qué tengo pendiente?"
RESPUESTA = "Tenés dos tareas abiertas."

KINDS = ["dato_menu", "modificar", "ninguna", "alta_texto"]

# Cómo se nombra cada pregunta en la pregunta de la rama, qué se le pregunta a la
# persona (la que se repite al Seguir) y qué se le dice al dejarla.
NOMBRES = {
    "dato_menu": f"la evidencia de la entrega de «{TITULO}»",
    "modificar": "la corrección de la propuesta",
    "ninguna": f"la tarea a la que te referías con «{REFERENCIA}»",
    "alta_texto": "el título de la tarea nueva",
}
PREGUNTAS = {
    "dato_menu": gateway.PREGUNTA_DATO_EVIDENCIA_ENTREGA,
    "modificar": gateway.PREGUNTA_MODIFICAR,
    "ninguna": gateway.PREGUNTA_ACLARACION_NINGUNA,
    "alta_texto": "¿Qué hay que hacer?",
}
DEJADAS = {
    "dato_menu": gateway.AVISO_DATO_DEJADO_DE_LADO.format(
        descripcion=NOMBRES["dato_menu"]),
    "modificar": gateway.AVISO_MODIFICACION_DEJADA,
    "ninguna": gateway.AVISO_ACLARACION_DEJADA,
    # El alta no se cancela al dejarla para ver otra cosa (F-C6): se guarda.
    "alta_texto": gateway.AVISO_ALTA_PAUSADA.format(titulo=""),
}


class _Mundo:
    """La pregunta abierta de un `kind` y cómo escribirle a Leda en ese chat."""

    def __init__(self, kind, cliente, conn, ws, monkeypatch):
        self.kind, self.cliente, self.conn, self.ws = kind, cliente, conn, ws
        self.request_id = None
        if kind == "dato_menu":
            _tid, self.tg = _abrir_pregunta(cliente, conn, ws, monkeypatch,
                                            "Ya la terminé")
        elif kind == "modificar":
            self.tg, _tid = _abrir_modificar(cliente, conn, ws)
        elif kind == "ninguna":
            self.tg, _tid = _abrir_ninguna(cliente, conn, ws)
        else:
            self.tg, self.request_id = _abrir_alta(conn, ws)

    def escribir(self, texto):
        enviar = _mensaje_privado if self.kind == "alta_texto" else _mensaje
        assert enviar(self.cliente, self.tg, texto).status_code == 200

    def tocar(self, etiqueta):
        fila = next(o for o in _botones_de(self.conn, self.ws,
                                           P.SENTINEL_RESPUESTA_DATO_MENU)
                    if etiqueta in o["etiqueta"])
        assert _tocar(self.cliente, fila["token"], self.tg).status_code == 200
        return fila["token"]

    def sigue_abierta(self) -> bool:
        if self.kind == "alta_texto":
            return _campo_del_slot(self.conn) == "title"
        return _abiertas(self.conn) == 1

    def esta_cerrada_por_dejarla(self) -> bool:
        if self.kind == "alta_texto":
            # Guardada y pausada: sigue activa y sin ninguna pregunta abierta.
            return (_request(self.conn, self.request_id)["estado"] == "active"
                    and _campo_del_slot(self.conn) is None)
        return _abiertas(self.conn) == 0

    def cerrar_por_otro_camino(self):
        """Simula que otro camino ya cerró la pregunta (una carrera)."""
        if self.kind == "alta_texto":
            with espacio(self.conn, self.ws) as cur:
                cur.execute("select * from task_intake_request where id = %s",
                            (self.request_id,))
                solicitud = cur.fetchone()
                quien = _quien(cur, "Marcos Tarquini", self.ws)
                I._cancel(cur, solicitud, quien, datetime.now(timezone.utc),
                          enqueue=False)
        else:
            with admin(self.conn) as cur:
                cur.execute(
                    """update pending_action set modificacion_consumida_en = now()
                        where modificar_pedido_en is not null
                          and modificacion_consumida_en is null""")
        self.conn.commit()


@pytest.fixture(params=KINDS)
def mundo(request, cliente, conn, corework, monkeypatch):
    return _Mundo(request.param, cliente, conn, corework.workspace_id, monkeypatch)


def _etiquetas_de_la_rama(conn, ws) -> list[str]:
    return [o["etiqueta"]
            for o in _botones_de(conn, ws, P.SENTINEL_RESPUESTA_DATO_MENU)]


# ---------------------------------------------------------------------------
# otro_tema: una sola pregunta con dos botones, el mensaje no se atiende
# ---------------------------------------------------------------------------


def test_otro_tema_pregunta_por_la_rama_y_no_atiende_el_mensaje(
        mundo, conn, monkeypatch):
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)],
                           guion=[Respuesta(texto=RESPUESTA)])
    antes = _salidas(conn, mundo.tg)

    mundo.escribir(OTRO_MENSAJE)

    assert _salidas(conn, mundo.tg) == antes + 1              # una sola respuesta
    ultima = _filas_del_chat(conn, mundo.tg)[-1]
    assert ultima["cuerpo"] == gateway.PREGUNTA_RAMA_ABIERTA.format(
        nombre=NOMBRES[mundo.kind])
    assert ultima["pending_action_id"] is not None            # con botones
    assert _etiquetas_de_la_rama(conn, mundo.ws) == [
        gateway.ETIQUETA_SEGUIR_RAMA, gateway.ETIQUETA_DEJAR_RAMA]
    assert proveedor.recibidos == []                          # el responder no corrió
    assert len(proveedor.ruteados) == 1                       # un solo ruteo
    assert mundo.sigue_abierta()                              # lo pendiente sigue


def test_la_pregunta_de_la_rama_guarda_el_mensaje_para_atenderlo_despues(
        mundo, conn, monkeypatch):
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])

    mundo.escribir(OTRO_MENSAJE)

    with admin(conn) as cur:
        cur.execute("select args from pending_action where herramienta = %s",
                    (P.SENTINEL_RESPUESTA_DATO_MENU,))
        (fila,) = cur.fetchall()
        assert fila["args"]["texto"] == OTRO_MENSAJE
        cur.execute("select texto from inbound_message where id = %s",
                    (fila["args"]["entrante_id"],))
        assert cur.fetchone()["texto"] == OTRO_MENSAJE


# ---------------------------------------------------------------------------
# Seguir
# ---------------------------------------------------------------------------


def test_seguir_repite_la_pregunta_pendiente_y_no_cierra_nada(
        mundo, conn, monkeypatch):
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    mundo.escribir(OTRO_MENSAJE)
    antes = _salidas(conn, mundo.tg)

    mundo.tocar("Seguir")

    assert _salidas(conn, mundo.tg) == antes + 1
    assert PREGUNTAS[mundo.kind] in _ultimo_cuerpo(conn, mundo.tg)
    assert mundo.sigue_abierta()
    assert proveedor.recibidos == []


def test_seguir_con_la_pregunta_ya_cerrada_lo_dice_una_vez(
        mundo, conn, monkeypatch):
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA)])
    mundo.escribir(OTRO_MENSAJE)
    mundo.cerrar_por_otro_camino()
    antes = _salidas(conn, mundo.tg)

    mundo.tocar("Seguir")

    assert _salidas(conn, mundo.tg) == antes + 1
    assert _ultimo_cuerpo(conn, mundo.tg) == gateway.AVISO_RAMA_YA_CERRADA


# ---------------------------------------------------------------------------
# Dejar y ver lo otro
# ---------------------------------------------------------------------------


def test_dejar_cierra_lo_pendiente_y_atiende_el_mensaje_guardado_en_una_respuesta(
        mundo, conn, monkeypatch):
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(texto=RESPUESTA)])
    mundo.escribir(OTRO_MENSAJE)
    antes = _salidas(conn, mundo.tg)

    mundo.tocar("Dejarlo")

    assert mundo.esta_cerrada_por_dejarla()
    filas = _filas_del_chat(conn, mundo.tg)
    assert _salidas(conn, mundo.tg) == antes + 2              # dos partes de UNA
    assert filas[-2]["cuerpo"] == DEJADAS[mundo.kind]         # lo que se dejó...
    assert filas[-1]["cuerpo"] == RESPUESTA                   # ...y lo otro
    # El mensaje guardado se atiende como si no hubiera pregunta abierta.
    assert proveedor.ruteados == [OTRO_MENSAJE, OTRO_MENSAJE]
    assert proveedor.pendientes[-1] is None
    assert proveedor.recibidos[-1][1][-1]["content"] == OTRO_MENSAJE


def test_dejar_con_la_pregunta_ya_cerrada_atiende_el_mensaje_sin_decir_que_la_dejo(
        mundo, conn, monkeypatch):
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(texto=RESPUESTA)])
    mundo.escribir(OTRO_MENSAJE)
    mundo.cerrar_por_otro_camino()
    antes = _salidas(conn, mundo.tg)

    mundo.tocar("Dejarlo")

    assert _salidas(conn, mundo.tg) == antes + 1              # sólo la respuesta
    assert _ultimo_cuerpo(conn, mundo.tg) == RESPUESTA        # no se pierde
    assert len(proveedor.recibidos) == 1


def test_dejar_con_el_ruteo_caido_deja_una_respuesta_y_no_cierra_lo_pendiente(
        mundo, conn, monkeypatch):
    malo = RouteEnvelope(calls=())
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), malo, malo])
    mundo.escribir(OTRO_MENSAJE)
    incidentes = _incidentes(conn, mundo.ws)
    antes = _salidas(conn, mundo.tg)

    mundo.tocar("Dejarlo")

    assert _incidentes(conn, mundo.ws) == incidentes + 1
    assert _salidas(conn, mundo.tg) == antes + 1              # exactamente una
    assert mundo.sigue_abierta()                              # no se perdió nada


def test_dejar_tocado_dos_veces_no_repite_el_efecto(mundo, conn, monkeypatch):
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(texto=RESPUESTA)])
    mundo.escribir(OTRO_MENSAJE)
    token = mundo.tocar("Dejarlo")
    antes = _salidas(conn, mundo.tg)

    # Dentro de la ventana del toque repetido (T9-R4) se absorbe: ni efecto ni aviso.
    assert _tocar(mundo.cliente, token, mundo.tg).status_code == 200
    assert _salidas(conn, mundo.tg) == antes
    assert len(proveedor.recibidos) == 1

    # Fuera de la ventana se contesta como siempre.
    envejecer_toques(conn, FUERA_DE_LA_VENTANA)
    assert _tocar(mundo.cliente, token, mundo.tg).status_code == 200

    assert _salidas(conn, mundo.tg) == antes + 1              # sólo un aviso
    assert _ultimo_cuerpo(conn, mundo.tg) == gateway.AVISO_PEDIDO_NO_VIGENTE
    assert len(proveedor.recibidos) == 1                      # no se atendió dos veces


# ---------------------------------------------------------------------------
# Si la persona escribe en vez de tocar, se interpreta otra vez contra lo
# pendiente; una pregunta nueva de la rama deja sin vigencia a la anterior
# ---------------------------------------------------------------------------


def test_escribir_de_nuevo_interpreta_el_mensaje_contra_la_misma_pregunta(
        mundo, conn, monkeypatch):
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA),
                      _ruta(RespectoPendiente.CHARLA)])
    mundo.escribir(OTRO_MENSAJE)
    antes = _salidas(conn, mundo.tg)

    mundo.escribir("hola")

    # La pregunta de la rama no es una rama nueva: el ruteo vuelve a recibir la
    # misma pregunta pendiente, y `charla` la repite como siempre.
    assert proveedor.pendientes[0] == proveedor.pendientes[1]
    assert proveedor.pendientes[1] is not None
    assert _salidas(conn, mundo.tg) == antes + 1
    assert PREGUNTAS[mundo.kind] in _ultimo_cuerpo(conn, mundo.tg)
    assert mundo.sigue_abierta()


@pytest.mark.parametrize("etiqueta", ["Seguir", "Dejarlo"])
def test_una_pregunta_nueva_de_la_rama_deja_sin_vigencia_los_botones_de_la_anterior(
        mundo, conn, monkeypatch, etiqueta):
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.OTRO_TEMA),
                      _ruta(RespectoPendiente.OTRO_TEMA), _ruta(None)],
        guion=[Respuesta(texto=RESPUESTA)])
    mundo.escribir(OTRO_MENSAJE)
    vieja = next(o for o in _botones_de(conn, mundo.ws,
                                        P.SENTINEL_RESPUESTA_DATO_MENU)
                 if etiqueta in o["etiqueta"])
    mundo.escribir("¿y qué vence hoy?")
    antes = _salidas(conn, mundo.tg)

    # El toque tardío en la pregunta anterior: una sola respuesta, sin efecto.
    assert _tocar(mundo.cliente, vieja["token"], mundo.tg).status_code == 200

    assert _salidas(conn, mundo.tg) == antes + 1
    assert _ultimo_cuerpo(conn, mundo.tg) == gateway.AVISO_PEDIDO_NO_VIGENTE
    assert mundo.sigue_abierta()
    assert proveedor.recibidos == []

    # La vigente atiende el último mensaje, no el primero.
    mundo.tocar("Dejarlo")

    assert proveedor.ruteados[-1] == "¿y qué vence hoy?"
    assert proveedor.recibidos[-1][1][-1]["content"] == "¿y qué vence hoy?"
    assert mundo.esta_cerrada_por_dejarla()


def test_un_toque_en_un_boton_del_retome_de_antes_se_contesta_como_no_vigente(
        mundo, conn, monkeypatch):
    # Los botones "Dejarlo" del retome que ya se mandó antes de T9-R1d (sin
    # mensaje guardado): una sola respuesta y lo pendiente no se toca.
    proveedor = _con_rutas(monkeypatch, [])
    from datetime import timedelta
    from leda.agente import VIGENCIA_PENDIENTE
    ahora = datetime.now(timezone.utc)
    with espacio(conn, mundo.ws) as cur:
        quien = _quien(cur, "Marcos Tarquini" if mundo.kind != "dato_menu"
                       else "Nahuel Gimenez", mundo.ws)
        abierta = gateway._ver_pregunta_abierta(
            cur, quien, mundo.tg, ahora, alta=mundo.kind == "alta_texto")
        p = P.registrar(
            cur, quien, herramienta=P.SENTINEL_RESPUESTA_DATO_MENU,
            args=gateway._args_de_la_pregunta(abierta),
            resumen="¿Seguimos con eso?", vence_en=ahora + VIGENCIA_PENDIENTE,
            campo="eleccion", opciones=[("✖️ Dejarlo", "dejar")],
            chat_id=mundo.tg)
        token = P.opciones(cur, p.id)[0].token
    conn.commit()
    antes = _salidas(conn, mundo.tg)

    assert _tocar(mundo.cliente, token, mundo.tg).status_code == 200

    assert _salidas(conn, mundo.tg) == antes + 1
    assert _ultimo_cuerpo(conn, mundo.tg) == gateway.AVISO_PEDIDO_NO_VIGENTE
    assert mundo.sigue_abierta()                              # no se cerró
    assert proveedor.recibidos == []


# ---------------------------------------------------------------------------
# dudoso: "No, es otra cosa" es la misma salida que "Dejarlo y ver lo otro"
# ---------------------------------------------------------------------------


def test_dudoso_no_es_otra_cosa_deja_lo_pendiente_y_atiende_el_mensaje_que_causo_la_duda(
        mundo, conn, monkeypatch):
    proveedor = _con_rutas(
        monkeypatch, [_ruta(RespectoPendiente.DUDOSO), _ruta(None)],
        guion=[Respuesta(texto=RESPUESTA)])
    mundo.escribir(OTRO_MENSAJE)
    antes = _salidas(conn, mundo.tg)

    mundo.tocar("No, es otra cosa")

    assert mundo.esta_cerrada_por_dejarla()
    filas = _filas_del_chat(conn, mundo.tg)
    assert _salidas(conn, mundo.tg) == antes + 2              # dos partes de UNA
    assert filas[-2]["cuerpo"] == DEJADAS[mundo.kind]
    assert filas[-1]["cuerpo"] == RESPUESTA
    assert proveedor.pendientes[-1] is None                   # sin pregunta abierta
    assert proveedor.recibidos[-1][1][-1]["content"] == OTRO_MENSAJE


# ---------------------------------------------------------------------------
# Un valor de elección inesperado no es "dejar" (review-2282ebc46e7a48e1, R3)
# ---------------------------------------------------------------------------


def test_una_eleccion_inesperada_se_contesta_como_no_vigente_y_no_cierra_nada(
        mundo, conn, monkeypatch):
    proveedor = _con_rutas(monkeypatch, [])
    from datetime import timedelta
    from leda.agente import VIGENCIA_PENDIENTE
    ahora = datetime.now(timezone.utc)
    with espacio(conn, mundo.ws) as cur:
        quien = _quien(cur, "Marcos Tarquini" if mundo.kind != "dato_menu"
                       else "Nahuel Gimenez", mundo.ws)
        abierta = gateway._ver_pregunta_abierta(
            cur, quien, mundo.tg, ahora, alta=mundo.kind == "alta_texto")
        args = {**gateway._args_de_la_pregunta(abierta),
                "texto": OTRO_MENSAJE, "entrante_id": None}
        p = P.registrar(
            cur, quien, herramienta=P.SENTINEL_RESPUESTA_DATO_MENU,
            args=args, resumen="¿Seguimos con eso?",
            vence_en=ahora + VIGENCIA_PENDIENTE, campo="eleccion",
            opciones=[("Otra", "algo_raro")], chat_id=mundo.tg)
        token = P.opciones(cur, p.id)[0].token
    conn.commit()
    antes = _salidas(conn, mundo.tg)

    assert _tocar(mundo.cliente, token, mundo.tg).status_code == 200

    assert _salidas(conn, mundo.tg) == antes + 1              # exactamente una
    assert _ultimo_cuerpo(conn, mundo.tg) == gateway.AVISO_PEDIDO_NO_VIGENTE
    assert mundo.sigue_abierta()                              # no se cerró
    assert proveedor.recibidos == []
