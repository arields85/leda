"""La redacción de A ve la conversación (ADR 0014, etapa 6; F-C4 y F-C6).

El modelo que redacta recibía sólo los hechos del turno: no veía lo que ya había
dicho, así que abría casi todos los mensajes con la misma fórmula ("Entendí
que…", "Me falta…"). Ahora recibe también la conversación reciente (lo que
efectivamente se dijeron, sin el mensaje que dispara el turno) y la guía le pide
seguirla con naturalidad: no repetir lo ya dicho y decir sólo lo nuevo. Los
hechos siguen siendo la única fuente de lo que afirma (el verificador no cambia).
"""

from __future__ import annotations

import inspect
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import prisma.llm as llm
from prisma import redaccion
from prisma import ingreso_tareas as I
from prisma.db import admin, atar_al_entrante, espacio
from prisma.llm import (ProveedorAnthropic, ProveedorCompatible, ProveedorGemini,
                        ProveedorGuionado)
from prisma.resultado_turno import Falta, ResultadoTurno
from prisma.valores import TipoValor

from tests.test_alta_guiada_flujo import CHAT, _empezar, _entrante
from tests.test_alta_guiada_mensaje_entero import _a

HISTORIAL = [
    {"role": "user", "content": "necesito crear una tarea"},
    {"role": "assistant", "content": "Entendí que querés una tarea nueva. "
                                     "Me falta el título. ¿Qué hay que hacer?"},
]
HECHOS = json.dumps({"falta": {"campo": "title", "dato": "el título",
                               "tipo": "texto"}}, ensure_ascii=False)


# --- cada proveedor manda la conversación junto a los hechos --------------------

def _anthropic(cuerpos: list) -> ProveedorAnthropic:
    def crear(**kwargs):
        cuerpos.append(kwargs["messages"][0]["content"])
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="{}")])
    return ProveedorAnthropic("m", "k", cliente=SimpleNamespace(
        messages=SimpleNamespace(create=crear)))


def _gemini(cuerpos: list) -> ProveedorGemini:
    class Http:
        def post(self, url, json=None, **_):
            cuerpos.append(json["contents"][0]["parts"][0]["text"])
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"candidates": [{"content": {"parts": [
                    {"text": "{}"}]}}]})
    return ProveedorGemini("m", "k", cliente=Http())


def _compatible(cuerpos: list) -> ProveedorCompatible:
    def crear(**kwargs):
        cuerpos.append(kwargs["messages"][-1]["content"])
        return SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content="{}"))])
    return ProveedorCompatible("m", "k", "https://ejemplo.invalido",
                               cliente=SimpleNamespace(chat=SimpleNamespace(
                                   completions=SimpleNamespace(create=crear))))


ADAPTADORES = {"anthropic": _anthropic, "gemini": _gemini, "openai": _compatible}


@pytest.mark.parametrize("adaptador", ADAPTADORES)
def test_el_proveedor_manda_la_conversacion_y_los_hechos(adaptador):
    cuerpos: list[str] = []

    ADAPTADORES[adaptador](cuerpos).redactar("sistema", HECHOS,
                                             historial=HISTORIAL)

    (contenido,) = cuerpos
    assert "Persona: necesito crear una tarea" in contenido
    assert "Prisma: Entendí que querés una tarea nueva." in contenido
    assert contenido.endswith(HECHOS)           # los hechos, lo último y tal cual
    assert contenido.index("Persona:") < contenido.index(HECHOS)


@pytest.mark.parametrize("adaptador", ADAPTADORES)
@pytest.mark.parametrize("historial", [None, []])
def test_sin_conversacion_el_proveedor_manda_los_hechos_como_siempre(
        adaptador, historial):
    cuerpos: list[str] = []

    ADAPTADORES[adaptador](cuerpos).redactar("sistema", HECHOS,
                                             historial=historial)

    assert cuerpos == [HECHOS]


def test_todo_proveedor_que_redacta_acepta_la_conversacion_por_nombre():
    """El contrato: lo que `redaccion` le pasa a cualquier proveedor."""
    clases = [c for _, c in inspect.getmembers(llm, inspect.isclass)
              if "redactar" in vars(c) and c.__module__ == llm.__name__]
    assert len(clases) >= 4
    for clase in clases:
        parametro = inspect.signature(clase.redactar).parameters.get("historial")
        assert parametro is not None, clase.__name__
        assert parametro.kind is inspect.Parameter.KEYWORD_ONLY, clase.__name__
        assert parametro.default is None, clase.__name__


def test_el_guionado_anota_la_conversacion_de_cada_redaccion():
    modelo = ProveedorGuionado(guion=[], borradores=["a", "b"])

    modelo.redactar("s", "h1")
    modelo.redactar("s", "h2", historial=HISTORIAL)

    assert modelo.historiales_redactados == [[], HISTORIAL]


# --- la guía -----------------------------------------------------------------

def test_la_guia_pide_seguir_la_conversacion_sin_repetir_lo_dicho():
    guia = redaccion.SISTEMA_REDACCION
    assert "conversación reciente" in guia
    assert "no repitas" in guia
    assert "sólo lo que es nuevo" in guia
    # La conversación es contexto: nunca una fuente de hechos.
    assert "nunca una fuente de hechos" in guia


# --- redactar_turno -----------------------------------------------------------

class _Captura:
    def __init__(self):
        self.llamadas: list[dict] = []

    def redactar(self, sistema, hechos, **kwargs):
        self.llamadas.append(kwargs)
        return json.dumps({"texto": "¿Qué hay que hacer?", "pregunta": "title",
                           "afirma": []}, ensure_ascii=False)


def _resultado():
    return ResultadoTurno(falta=Falta("el título", TipoValor.TEXTO,
                                      pregunta="¿Qué hay que hacer?",
                                      campo="title"))


def test_redactar_turno_le_pasa_la_conversacion_al_modelo(intake_world, conn):
    modelo = _Captura()
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        redaccion.redactar_turno(cur, ws, _resultado(), "A", proveedor=modelo,
                                 historial=HISTORIAL)
    assert modelo.llamadas[0]["historial"] == HISTORIAL


def test_redactar_turno_sin_conversacion_llama_como_antes(intake_world, conn):
    modelo = _Captura()
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        redaccion.redactar_turno(cur, ws, _resultado(), "A", proveedor=modelo)
    assert "historial" not in modelo.llamadas[0]


# --- el alta guiada -----------------------------------------------------------

class _Eco(ProveedorGuionado):
    def __init__(self):
        super().__init__(guion=[])

    def redactar(self, sistema, hechos, **kwargs):
        self.redactados.append((sistema, hechos))
        self.historiales_redactados.append(kwargs.get("historial") or [])
        d = json.loads(hechos)
        pregunta = d.get("falta", {}).get("campo")
        frase = d.get("falta", {}).get("pregunta") or "Listo, revisalo:"
        return json.dumps({"texto": frase, "pregunta": pregunta, "afirma": []},
                          ensure_ascii=False)


def test_la_pregunta_siguiente_del_alta_ve_lo_que_ya_se_dijeron(
        intake_world, conn, monkeypatch):
    """El modelo ve la primera pregunta que salió y lo que la persona contestó,
    pero no el mensaje que dispara este turno (viaja como hecho)."""
    ws = intake_world["north-lab"]["id"]
    modelo = _Eco()
    _a(conn, ws, monkeypatch, modelo)
    ahora = datetime.now(timezone.utc)

    with espacio(conn, ws) as cur:
        actor, outcome = _empezar(cur, intake_world)
        rid = outcome.request_id
        cur.execute("""update message_outbox
                          set estado = 'enviado', enviado_en = %s
                        where chat_id = %s""", (ahora, CHAT))
        cur.execute("""update inbound_message set at = %s where chat_id = %s""",
                    (ahora - timedelta(minutes=1), CHAT))
        inbound = _entrante(cur, ws, actor, "revisar el variador", n=7001)
        atar_al_entrante(cur, inbound)
        I.consume_pending_text(
            cur, actor, chat_id=CHAT, source_inbound_id=inbound,
            source_raw_text="revisar el variador", now=ahora,
            valor={"texto": "Revisar el variador"})

    antes, despues = modelo.historiales_redactados
    assert antes == []                       # la primera pregunta: nada previo
    assert [m["role"] for m in despues] == ["user", "assistant"]
    assert "¿Qué hay que hacer?" in despues[-1]["content"]
    assert all("revisar el variador" not in m["content"] for m in despues)
    assert rid


def test_la_charla_con_una_pregunta_pendiente_tambien_ve_la_conversacion(
        intake_world, conn):
    class Charla:
        def __init__(self):
            self.llamadas: list[dict] = []

        def redactar(self, sistema, hechos, **kwargs):
            self.llamadas.append(kwargs)
            return "Hola, un gusto."

    modelo = Charla()
    ws = intake_world["north-lab"]["id"]
    with admin(conn) as cur:
        texto = redaccion.redactar_charla(cur, ws, "hola", "¿Qué hay que hacer?",
                                          proveedor=modelo, historial=HISTORIAL)
        redaccion.redactar_charla(cur, ws, "hola", "¿Qué hay que hacer?",
                                  proveedor=modelo)

    assert texto == "Hola, un gusto."
    assert modelo.llamadas[0]["historial"] == HISTORIAL
    assert "historial" not in modelo.llamadas[1]
