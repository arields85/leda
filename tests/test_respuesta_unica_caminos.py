"""Los caminos que encolan más de un mensaje visible a propósito son UNA respuesta
(T9-R2b, ADR 0013 regla 2).

`respuesta_unica.controlar` descarta todas menos una de las respuestas
independientes de un mensaje y deja un incidente: un camino que a propósito
encola varios mensajes (el texto largo en partes y aparte el mensaje con los
botones, un aviso delante de una vista previa) tiene que marcarlos con el mismo
`grupo_respuesta`, o el control se lleva contenido de la persona. Hay una prueba
por camino, con el mensaje entrando por `procesar_update`: todo lo visible que
sale comparte el grupo, nada queda descartado y no hay incidente de la respuesta.

Los caminos que hay hoy al procesar un mensaje (revisión estática de cada
`enqueue_outbox` y `_responder` alcanzable desde `procesar_update`):

1. `agente._encolar_texto_con_opciones`, del que cuelgan tres armados: la lista de
   tareas (`_encolar_respuesta_con_tareas`), `ofrecer_opciones`
   (`_encolar_opciones_modelo`) y el cierre genérico de una pregunta sin opciones
   (`_encolar_opciones_genericas`). Con un texto que no entra con los botones, el
   texto sale partido y los botones en otro mensaje.
2. `gateway._mostrar_pregunta_con_botones`: la vista previa o la elección que se
   vuelve a mostrar, con un aviso delante que no entra junto (dos mensajes) o con
   un texto que ya no entra con sus botones (tres).
3. `respuesta_unica.controlar` con la nota del adjunto (H15): una parte más de la
   respuesta, marcada en el mismo grupo.
4. `salida.enqueue_outbox` con `allow_split`: las partes de un texto partido
   comparten el prefijo de su clave (`respuesta_unica.grupo_de`).

`gateway._dejar_y_ver_lo_otro` (el aviso de lo que se dejó y el mensaje guardado)
también son dos mensajes, pero sólo se llega por un toque (T9-R4): el aviso se anota
con `respuesta_unica.dejar_nota` y el control lo agrega como una parte más de la
misma respuesta (`tests/test_toque_idempotente.py`).

Ninguna prueba toca la red ni el modelo real.
"""

from __future__ import annotations

import pytest

from prisma import gateway
from prisma.agente import _TEXTO_BOTONES_GENERICO
from prisma.db import admin
from prisma.llm import Llamada, RespectoPendiente, Respuesta
from prisma.respuesta_unica import (ETAPA_RESPUESTA_DUPLICADA,
                                    ETAPA_SIN_RESPUESTA, grupo_de)

from tests.test_menu_tarea import _mensaje, cliente  # noqa: F401
from tests.test_modificar import _tarea
from tests.test_pregunta_pendiente_otras import _con_rutas, _ruta
from tests.test_rama_vista_previa import (_abrir_vista_previa,
                                          _causa_que_llena_la_vista_previa)
from tests.test_una_respuesta import (_entrantes, _filas_de_salida, _incidentes,
                                      _tg)

PERSONA = "Marcos Tarquini"
# Más de un mensaje de Telegram con botones (`BUTTON_TEXT_LIMIT`).
TEXTO_LARGO = "\n\n".join(f"Párrafo {i}. " + "palabra " * 60 for i in range(20))


def _una_respuesta(conn, ws, tg, antes: int, *, mensajes: int, con_botones: bool):
    """Lo que salió para el mensaje que acaba de entrar (lo visible desde `antes`
    filas): `mensajes` o más mensajes, todos del mismo grupo, atados al mensaje,
    sin nada descartado ni incidente de la respuesta."""
    filas = _filas_de_salida(conn, tg)[antes:]
    assert len(filas) >= mensajes
    assert all(f["estado"] != "descartado" and f["es_respuesta"] for f in filas)
    assert len({grupo_de(f) for f in filas}) == 1, [f["dedupe_key"] for f in filas]
    entrante = _entrantes(conn, tg)[-1]
    assert {str(f["entrante_id"]) for f in filas} == {str(entrante["id"])}
    assert (sum(f["pending_action_id"] is not None for f in filas) == 1) is con_botones
    for etapa in (ETAPA_SIN_RESPUESTA, ETAPA_RESPUESTA_DUPLICADA):
        assert _incidentes(conn, ws, etapa) == []
    return filas


# ---------------------------------------------------------------------------
# 1. `_encolar_texto_con_opciones`: texto largo en partes y botones aparte
# ---------------------------------------------------------------------------


def test_la_lista_de_tareas_con_texto_largo_es_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    with admin(conn) as cur:
        _tarea(cur, ws)
    conn.commit()
    _con_rutas(monkeypatch, [_ruta(None)], guion=[
        Respuesta(llamadas=[Llamada("q1", "consultar_tareas", {})]),
        Respuesta(texto=TEXTO_LARGO)])
    tg = _tg(conn, PERSONA)
    antes = len(_filas_de_salida(conn, tg))

    assert _mensaje(cliente, tg, "pasame mis tareas").status_code == 200

    filas = _una_respuesta(conn, ws, tg, antes, mensajes=3, con_botones=True)
    assert ":lista-tareas:" in filas[-1]["dedupe_key"]        # el de los botones


def test_ofrecer_opciones_con_texto_largo_es_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _con_rutas(monkeypatch, [_ruta(None)], guion=[
        Respuesta(texto=TEXTO_LARGO, llamadas=[Llamada("q1", "ofrecer_opciones", {
            "pregunta": "Elegí una", "opciones": [{"texto": "Una"},
                                                 {"texto": "Otra"}]})]),
        Respuesta(texto="listo")])
    tg = _tg(conn, PERSONA)
    antes = len(_filas_de_salida(conn, tg))

    assert _mensaje(cliente, tg, "ayudame").status_code == 200

    filas = _una_respuesta(conn, ws, tg, antes, mensajes=3, con_botones=True)
    assert ":opciones-modelo:" in filas[-1]["dedupe_key"]


def test_el_cierre_generico_con_texto_largo_es_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _con_rutas(monkeypatch, [_ruta(None)],
               guion=[Respuesta(texto=f"{TEXTO_LARGO}\n\n¿Querés que lo revise?")])
    tg = _tg(conn, PERSONA)
    antes = len(_filas_de_salida(conn, tg))

    assert _mensaje(cliente, tg, "ayudame").status_code == 200

    filas = _una_respuesta(conn, ws, tg, antes, mensajes=3, con_botones=True)
    assert ":opciones-genericas:" in filas[-1]["dedupe_key"]


# ---------------------------------------------------------------------------
# 2. `_mostrar_pregunta_con_botones`: el aviso y la vista previa, o las tres
#    partes cuando ni la vista previa entra con sus botones
# ---------------------------------------------------------------------------


def test_el_aviso_delante_de_una_vista_previa_larga_es_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _tid, pid = _abrir_vista_previa(
        conn, ws, causa=_causa_que_llena_la_vista_previa())
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = len(_filas_de_salida(conn, tg))

    assert _mensaje(cliente, tg, "sí, dale, confirmá").status_code == 200

    filas = _una_respuesta(conn, ws, tg, antes, mensajes=2, con_botones=True)
    assert filas[0]["cuerpo"] == gateway.AVISO_VISTA_PREVIA_SE_CONFIRMA_CON_EL_BOTON
    assert str(filas[-1]["pending_action_id"]) == pid


def test_la_vista_previa_que_ya_no_entra_con_sus_botones_sale_en_tres_partes_de_una_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _tid, pid = _abrir_vista_previa(conn, ws)
    monkeypatch.setattr(gateway, "cabe_en_mensaje", lambda *a, **k: False)
    _con_rutas(monkeypatch, [_ruta(RespectoPendiente.RESPONDE)])
    antes = len(_filas_de_salida(conn, tg))

    assert _mensaje(cliente, tg, "sí, dale, confirmá").status_code == 200

    filas = _una_respuesta(conn, ws, tg, antes, mensajes=3, con_botones=True)
    assert len(filas) == 3                    # aviso, vista previa y los botones
    assert filas[-1]["cuerpo"] == _TEXTO_BOTONES_GENERICO
    assert str(filas[-1]["pending_action_id"]) == pid


# ---------------------------------------------------------------------------
# 3 y 4. La nota del adjunto y las partes de un texto partido
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tipo", ["photo", "document"])
def test_el_epigrafe_con_una_respuesta_larga_es_una_sola_respuesta(
        tipo, cliente, conn, corework, monkeypatch):
    from tests.test_una_respuesta import _con_adjunto

    ws = corework.workspace_id
    _con_rutas(monkeypatch, [_ruta(None)], guion=[Respuesta(texto=TEXTO_LARGO)])
    tg = _tg(conn, PERSONA)
    antes = len(_filas_de_salida(conn, tg))

    assert _con_adjunto(cliente, tg, tipo, "resumime esto").status_code == 200

    filas = _una_respuesta(conn, ws, tg, antes, mensajes=3, con_botones=False)
    assert filas[0]["cuerpo"] == gateway.NOTA_ADJUNTO_NO_GUARDADO
