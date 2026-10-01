"""El ruteo recibe la conversación (ADR 0014, etapa 1: el contexto incluye "el
historial reciente de lo que efectivamente se dijo", F-C6).

Antes sólo `agente.responder` veía la conversación: el ruteo recibía el mensaje
suelto y una descripción corta de la pregunta pendiente, así que "ayudame, que
puedo poner?" se clasificaba como otro tema sin saber que Prisma acababa de
pedir el criterio de aceptación. Ahora el historial reciente (la misma fuente y
los mismos límites que `contexto.historial`: sólo lo enviado, en orden, sin el
mensaje que se rutea) entra como mensajes previos a los proveedores.

Los modelos se guionan o se simulan con clientes de juguete; nada toca la red.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

import prisma.llm as llm
from prisma import gateway
from prisma.db import admin
from prisma.llm import (IntentAction, IntentRoute, ProveedorAnthropic,
                        ProveedorCompatible, ProveedorGemini, ProveedorGuionado,
                        RespectoPendiente)

from tests.test_alta_pregunta_pendiente import (PREGUNTA_TITULO, _abrir_alta,
                                                _campo_del_slot, _campo,
                                                _mensaje_privado, _request)
from tests.test_menu_tarea import cliente  # noqa: F401
from tests.test_pregunta_pendiente_otras import _con_rutas, _filas_del_chat

HISTORIAL = [
    {"role": "user", "content": "necesito crear una tarea"},
    {"role": "assistant", "content": "¿Cómo se comprueba que quedó hecha?"},
]
MENSAJES_ESPERADOS = [*HISTORIAL,
                      {"role": "user", "content": "ayudame, que puedo poner?"}]
PENDIENTE = "el criterio de aceptación de la tarea nueva"
_LLAMADA = ("route_intent", {"action": "normal_conversation",
                             "respecto_pendiente": "dudoso"})


class _Captura:
    """El cuerpo con que cada adaptador habló con su modelo."""

    def __init__(self):
        self.cuerpos: list[dict] = []


def _anthropic(captura: _Captura) -> ProveedorAnthropic:
    def crear(**kwargs):
        captura.cuerpos.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(
            type="tool_use", id="r", name=_LLAMADA[0], input=_LLAMADA[1])])
    cliente_ = SimpleNamespace(messages=SimpleNamespace(create=crear))
    return ProveedorAnthropic("m", "k", cliente=cliente_)


def _gemini(captura: _Captura) -> ProveedorGemini:
    class Http:
        def post(self, url, json=None, **_):
            captura.cuerpos.append(json)
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"candidates": [{"content": {"parts": [
                    {"functionCall": {"name": _LLAMADA[0],
                                      "args": _LLAMADA[1]}}]}}]})
    return ProveedorGemini("m", "k", cliente=Http())


def _compatible(captura: _Captura) -> ProveedorCompatible:
    def crear(**kwargs):
        captura.cuerpos.append(kwargs)
        mensaje = SimpleNamespace(content=None, tool_calls=[SimpleNamespace(
            id="r", function=SimpleNamespace(
                name=_LLAMADA[0], arguments=json.dumps(_LLAMADA[1])))])
        return SimpleNamespace(choices=[SimpleNamespace(message=mensaje)])
    cliente_ = SimpleNamespace(chat=SimpleNamespace(
        completions=SimpleNamespace(create=crear)))
    return ProveedorCompatible("m", "k", "https://ejemplo.invalido",
                               cliente=cliente_)


def _mensajes_de(adaptador: str, cuerpo: dict) -> list[dict]:
    """Los mensajes que viajaron, sin el del sistema, con el mismo formato."""
    if adaptador == "gemini":
        return [{"role": "user" if c["role"] == "user" else "assistant",
                 "content": c["parts"][0]["text"]} for c in cuerpo["contents"]]
    mensajes = cuerpo["messages"]
    return [m for m in mensajes if m["role"] != "system"]


def _sistema_de(adaptador: str, cuerpo: dict) -> str:
    if adaptador == "anthropic":
        return cuerpo["system"]
    if adaptador == "gemini":
        return cuerpo["system_instruction"]["parts"][0]["text"]
    return next(m["content"] for m in cuerpo["messages"] if m["role"] == "system")


ADAPTADORES = {"anthropic": _anthropic, "gemini": _gemini, "openai": _compatible}


@pytest.mark.parametrize("adaptador", ADAPTADORES)
def test_el_ruteo_manda_la_conversacion_como_mensajes_previos(adaptador):
    captura = _Captura()
    proveedor = ADAPTADORES[adaptador](captura)

    ruta = proveedor.route_intent(
        "ayudame, que puedo poner?", pendiente=PENDIENTE, historial=HISTORIAL)

    assert ruta.respecto_pendiente is RespectoPendiente.DUDOSO
    (cuerpo,) = captura.cuerpos
    assert _mensajes_de(adaptador, cuerpo) == MENSAJES_ESPERADOS
    # El modelo sabe que los mensajes previos son la conversación y que el último
    # es el que se rutea: regla general de interpretación, no una lista de frases.
    sistema = _sistema_de(adaptador, cuerpo)
    assert llm.ROUTER_SYSTEM_CONVERSACION in sistema
    assert "en el contexto de esa conversación" in sistema


@pytest.mark.parametrize("adaptador", ADAPTADORES)
@pytest.mark.parametrize("historial", [None, []])
def test_sin_conversacion_el_ruteo_es_el_de_siempre(adaptador, historial):
    captura = _Captura()
    proveedor = ADAPTADORES[adaptador](captura)

    proveedor.route_intent("hola", pendiente=PENDIENTE, historial=historial)

    (cuerpo,) = captura.cuerpos
    assert _mensajes_de(adaptador, cuerpo) == [
        {"role": "user", "content": "hola"}]
    assert llm.ROUTER_SYSTEM_CONVERSACION not in _sistema_de(adaptador, cuerpo)


@pytest.mark.parametrize("adaptador", ADAPTADORES)
def test_un_mensaje_de_la_persona_sin_responder_se_le_suma_el_actual(adaptador):
    """Los proveedores no admiten dos mensajes seguidos del mismo lado."""
    captura = _Captura()
    historial = [{"role": "user", "content": "uno"},
                 {"role": "assistant", "content": "dos"},
                 {"role": "user", "content": "tres"}]

    ADAPTADORES[adaptador](captura).route_intent(
        "cuatro", pendiente=PENDIENTE, historial=historial)

    (cuerpo,) = captura.cuerpos
    assert _mensajes_de(adaptador, cuerpo) == [
        {"role": "user", "content": "uno"},
        {"role": "assistant", "content": "dos"},
        {"role": "user", "content": "tres\ncuatro"}]


@pytest.mark.parametrize("adaptador", ADAPTADORES)
def test_el_primer_mensaje_siempre_es_de_la_persona(adaptador):
    captura = _Captura()
    historial = [{"role": "assistant", "content": "un recordatorio"},
                 {"role": "user", "content": "gracias"},
                 {"role": "assistant", "content": "de nada"}]

    ADAPTADORES[adaptador](captura).route_intent(
        "y ahora?", pendiente=PENDIENTE, historial=historial)

    (cuerpo,) = captura.cuerpos
    mensajes = _mensajes_de(adaptador, cuerpo)
    assert mensajes[0]["role"] == "user"
    assert mensajes == [{"role": "user", "content": "gracias"},
                        {"role": "assistant", "content": "de nada"},
                        {"role": "user", "content": "y ahora?"}]


def test_el_sistema_dice_que_pedir_ayuda_con_la_pregunta_no_es_otro_tema():
    """Una regla general del comando, sin listas de frases."""
    assert "pide ayuda con la pregunta" in llm.ROUTER_SYSTEM_PENDIENTE
    assert "nunca es otro_tema" in llm.ROUTER_SYSTEM_PENDIENTE


def test_el_guionado_anota_la_conversacion_con_la_que_se_pidio_cada_ruteo():
    proveedor = ProveedorGuionado(guion=[])

    proveedor.route_intent("a")
    proveedor.route_intent("b", historial=HISTORIAL)

    assert proveedor.historiales == [[], HISTORIAL]


# --- el gateway ---------------------------------------------------------------

def test_el_gateway_pasa_la_conversacion_al_ruteo_sólo_si_la_hay():
    proveedor = ProveedorGuionado(guion=[])

    gateway._rutear(proveedor, "x", historial=HISTORIAL)
    gateway._rutear(proveedor, "y")

    assert proveedor.historiales == [HISTORIAL, []]


def test_un_proveedor_que_no_conoce_la_conversacion_sigue_llamandose_como_antes():
    visto = {}

    class Viejo:
        def route_intent(self, text, pendiente=None):
            visto["args"] = (text, pendiente)
            return IntentRoute(IntentAction.NORMAL_CONVERSATION)

    ruta, error = gateway._rutear(Viejo(), "hola", pendiente="p")
    assert error is None and visto["args"] == ("hola", "p")


def _marcar_enviado(conn, tg: int) -> None:
    with admin(conn) as cur:
        cur.execute("""update message_outbox
                          set estado = 'enviado', enviado_en = now()
                        where chat_id = %s""", (tg,))
    conn.commit()


def test_con_una_pregunta_abierta_el_ruteo_ve_lo_que_prisma_pregunto(
        cliente, conn, corework, monkeypatch):  # noqa: F811
    """F-C6: el ruteo clasificaba "ayudame, que puedo poner?" sin saber qué se
    había preguntado. Ahora recibe la pregunta que salió, sin el mensaje actual."""
    ws = corework.workspace_id
    tg, rid = _abrir_alta(conn, ws)
    _marcar_enviado(conn, tg)
    proveedor = _con_rutas(monkeypatch, [IntentRoute(
        IntentAction.NORMAL_CONVERSATION,
        respecto_pendiente=RespectoPendiente.DUDOSO)])

    assert _mensaje_privado(cliente, tg, "ayudame, que puedo poner?"
                            ).status_code == 200

    (conversacion,) = proveedor.historiales
    roles = [m["role"] for m in conversacion]
    assert roles[0] == "user" and roles[-1] == "assistant"
    assert PREGUNTA_TITULO in conversacion[-1]["content"]
    # El mensaje que se rutea viaja aparte: no está dos veces.
    assert all("ayudame, que puedo poner?" not in m["content"]
               for m in conversacion)
    assert proveedor.ruteados == ["ayudame, que puedo poner?"]
    assert _campo_del_slot(conn) == "title"          # nada se perdió
    assert _request(conn, rid)["estado"] == "active"
    assert _campo(conn, rid, "title")["estado"] == "missing"


def test_sin_pregunta_abierta_el_ruteo_tambien_ve_la_conversacion(
        cliente, conn, corework, monkeypatch):  # noqa: F811
    ws = corework.workspace_id
    tg, _ = _abrir_alta(conn, ws)
    _marcar_enviado(conn, tg)
    with admin(conn) as cur:
        cur.execute("""update task_intake_request set estado = 'cancelled'""")
        cur.execute("""update task_intake_free_text_slot
                          set estado = 'invalidated'""")
    conn.commit()
    proveedor = _con_rutas(monkeypatch, [IntentRoute(
        IntentAction.NORMAL_CONVERSATION)])

    _mensaje_privado(cliente, tg, "qué tengo pendiente")

    assert proveedor.ruteados == ["qué tengo pendiente"]
    assert proveedor.historiales and proveedor.historiales[0]
    assert _filas_del_chat(conn, tg)
