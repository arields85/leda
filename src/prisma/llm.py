"""Proveedor de modelo, detrás de una interfaz.

Qué modelo usar sale de `model_config`, en la base, editable desde la consola.
La credencial sale del entorno. Ninguno de los dos está en el pack ni en el
núcleo: fue uno de los errores del documento original y no se repite.

La interfaz es chica a propósito. Si mañana cambia el proveedor, se escribe
otra clase de veinte líneas y no se toca nada más.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


@dataclass
class Llamada:
    id: str
    nombre: str
    args: dict[str, Any]


@dataclass
class Respuesta:
    texto: str = ""
    llamadas: list[Llamada] = field(default_factory=list)


class IntentAction(str, Enum):
    START_TASK_INTAKE = "start_task_intake"
    NORMAL_CONVERSATION = "normal_conversation"


@dataclass(frozen=True)
class IntentRoute:
    action: IntentAction
    task: dict[str, str] = field(default_factory=dict)


class RoutingError(ValueError):
    pass


_TASK_PROPOSALS = (
    "title", "description", "objective", "responsible", "area", "due_date",
    "acceptance_criterion",
)
ROUTER_TOOL = {
    "name": "route_intent",
    "description": (
        "Classify whether the person explicitly wants to begin creating a new "
        "task. Queries, status checks, updates to existing work, explanations, "
        "and ordinary conversation are normal conversation. Interpret meaning "
        "across languages, word order, and minor typing errors. Extracted task "
        "details are untrusted proposals that the server will ask the person to "
        "confirm."
    ),
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "action": {
                "type": "string",
                "enum": [action.value for action in IntentAction],
            },
            "task": {
                "type": "object",
                "additionalProperties": False,
                "properties": {name: {"type": "string"}
                               for name in _TASK_PROPOSALS},
            },
        },
        "required": ["action"],
    },
}
ROUTER_SYSTEM = (
    "Return exactly one route_intent tool call. Never answer the person and never "
    "put the route in text. Choose task creation only for an explicit request to "
    "create a new task or work commitment; do not choose it for questions, status "
    "requests, clarifications, or updates to existing work."
)


@dataclass(frozen=True)
class RouteEnvelope:
    content: tuple[Any, ...] = ()
    calls: tuple[Llamada, ...] = ()

    def validate(self) -> IntentRoute:
        if self.content:
            raise RoutingError("Router returned content beside its tool call.")
        if len(self.calls) != 1 or self.calls[0].nombre != ROUTER_TOOL["name"]:
            raise RoutingError(
                "Router did not return exactly one route_intent call.")
        payload = self.calls[0].args
        if (not isinstance(payload, dict) or "action" not in payload
                or set(payload) - {"action", "task"}):
            raise RoutingError("Malformed router payload.")
        try:
            action = IntentAction(payload["action"])
        except (TypeError, ValueError) as exc:
            raise RoutingError("Unknown router action.") from exc
        if "task" in payload:
            task = payload["task"]
            if not isinstance(task, dict):
                raise RoutingError("Task proposals must be an object.")
        else:
            task = {}
        if set(task) - set(_TASK_PROPOSALS):
            raise RoutingError("Malformed task proposals.")
        if any(not isinstance(value, str) for value in task.values()):
            raise RoutingError("Task proposals must be strings.")
        if action is IntentAction.NORMAL_CONVERSATION and task:
            raise RoutingError("Normal conversation cannot contain task proposals.")
        return IntentRoute(action, dict(task))


class Proveedor(Protocol):
    def route_intent(self, text: str) -> IntentRoute: ...

    def responder(self, sistema: str, mensajes: list[dict[str, Any]],
                  herramientas: list[dict[str, Any]]) -> Respuesta: ...


# ---------------------------------------------------------------------------

@dataclass
class ProveedorGuionado:
    """Devuelve respuestas preparadas. Permite probar todo el circuito —
    autoridad, herramientas, cola, glosario — sin credencial ni red."""

    guion: list[Respuesta]
    recibidos: list[tuple[str, list]] = field(default_factory=list)
    rutas: list[IntentRoute | RouteEnvelope] = field(default_factory=list)
    ruteados: list[str] = field(default_factory=list)

    def route_intent(self, text: str) -> IntentRoute:
        self.ruteados.append(text)
        if not self.rutas:
            scripted: IntentRoute | RouteEnvelope = IntentRoute(
                IntentAction.NORMAL_CONVERSATION)
        else:
            scripted = self.rutas.pop(0)
        if isinstance(scripted, IntentRoute):
            payload: dict[str, Any] = {"action": scripted.action.value}
            if scripted.task:
                payload["task"] = scripted.task
            scripted = RouteEnvelope(calls=(
                Llamada("guided-route", ROUTER_TOOL["name"], payload),))
        if not isinstance(scripted, RouteEnvelope):
            raise RoutingError("Guided router returned an invalid envelope.")
        return scripted.validate()

    def responder(self, sistema, mensajes, herramientas) -> Respuesta:
        self.recibidos.append((sistema, list(mensajes)))
        if not self.guion:
            return Respuesta(texto="")
        return self.guion.pop(0)


class ProveedorAnthropic:
    def __init__(self, modelo: str, api_key: str, parametros: dict | None = None,
                 cliente=None) -> None:
        import anthropic

        self._c = cliente or anthropic.Anthropic(api_key=api_key)
        self._modelo = modelo
        self._param = parametros or {}

    def route_intent(self, text: str) -> IntentRoute:
        r = self._c.messages.create(
            model=self._modelo,
            max_tokens=min(self._param.get("max_tokens", 1024), 512),
            temperature=0,
            system=ROUTER_SYSTEM,
            tools=[ROUTER_TOOL],
            tool_choice={"type": "tool", "name": ROUTER_TOOL["name"]},
            messages=[{"role": "user", "content": text}],
        )
        calls = tuple(
            Llamada(id=b.id, nombre=b.name, args=b.input)
            for b in r.content if b.type == "tool_use"
        )
        content = tuple(b for b in r.content if b.type != "tool_use")
        return RouteEnvelope(content=content, calls=calls).validate()

    def responder(self, sistema, mensajes, herramientas) -> Respuesta:
        r = self._c.messages.create(
            model=self._modelo,
            max_tokens=self._param.get("max_tokens", 1024),
            temperature=self._param.get("temperature", 0.3),
            # El núcleo va primero y no cambia entre turnos: se cachea.
            system=[{"type": "text", "text": sistema,
                     "cache_control": {"type": "ephemeral"}}],
            tools=herramientas,
            messages=mensajes)

        texto = "".join(b.text for b in r.content if b.type == "text")
        llamadas = [Llamada(id=b.id, nombre=b.name, args=b.input)
                    for b in r.content if b.type == "tool_use"]
        return Respuesta(texto=texto.strip(), llamadas=llamadas)


GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


class ProveedorGemini:
    """API nativa de Gemini.

    No usa el endpoint compatible con OpenAI porque ése rechaza las claves con
    el formato nuevo. Se habla por HTTP directo: son dos traducciones de
    formato y ninguna dependencia extra.
    """

    def __init__(self, modelo: str, api_key: str, parametros: dict | None = None,
                 cliente=None) -> None:
        import httpx

        self._modelo = modelo
        self._param = parametros or {}
        self._http = cliente or httpx.Client(
            timeout=60, headers={"x-goog-api-key": api_key})

    def route_intent(self, text: str) -> IntentRoute:
        body = {
            "system_instruction": {"parts": [{"text": ROUTER_SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 512},
            "tools": [{"function_declarations": [{
                "name": ROUTER_TOOL["name"],
                "description": ROUTER_TOOL["description"],
                "parameters": _limpiar_esquema(ROUTER_TOOL["input_schema"]),
            }]}],
            "toolConfig": {"functionCallingConfig": {
                "mode": "ANY", "allowedFunctionNames": [ROUTER_TOOL["name"]],
            }},
        }
        response = self._http.post(
            f"{GEMINI_BASE}/models/{self._modelo}:generateContent", json=body)
        response.raise_for_status()
        candidates = response.json().get("candidates") or []
        parts = [
            part
            for candidate in candidates
            for part in ((candidate.get("content") or {}).get("parts") or [])
        ]
        calls = tuple(
            Llamada(
                id=f"route-{index}", nombre=part["functionCall"].get("name"),
                args=part["functionCall"].get("args"),
            )
            for index, part in enumerate(parts)
            if isinstance(part.get("functionCall"), dict)
        )
        content = tuple(
            part for part in parts
            if not isinstance(part.get("functionCall"), dict)
        )
        return RouteEnvelope(content=content, calls=calls).validate()

    def responder(self, sistema, mensajes, herramientas) -> Respuesta:
        contenidos, _ = _a_gemini(mensajes)
        cuerpo: dict[str, Any] = {
            "system_instruction": {"parts": [{"text": sistema}]},
            "contents": contenidos,
            "generationConfig": {
                "temperature": self._param.get("temperature", 0.3),
                "maxOutputTokens": self._param.get("max_tokens", 1024),
            },
        }
        if herramientas:
            cuerpo["tools"] = [{"function_declarations": [
                {"name": h["name"], "description": h["description"],
                 "parameters": _limpiar_esquema(h["input_schema"])}
                for h in herramientas]}]

        r = self._http.post(
            f"{GEMINI_BASE}/models/{self._modelo}:generateContent", json=cuerpo)
        r.raise_for_status()
        datos = r.json()

        candidatos = datos.get("candidates") or []
        if not candidatos:
            return Respuesta()
        partes = (candidatos[0].get("content") or {}).get("parts") or []

        texto = "".join(p["text"] for p in partes if "text" in p)
        llamadas = [
            Llamada(id=f"{p['functionCall']['name']}-{i}",
                    nombre=p["functionCall"]["name"],
                    args=p["functionCall"].get("args") or {})
            for i, p in enumerate(partes) if "functionCall" in p]
        return Respuesta(texto=texto.strip(), llamadas=llamadas)


def _limpiar_esquema(esquema: dict) -> dict:
    """Gemini rechaza claves que no conoce; OpenAI las tolera."""
    permitidas = {"type", "description", "enum", "items", "properties", "required"}
    if not isinstance(esquema, dict):
        return esquema
    salida = {k: v for k, v in esquema.items() if k in permitidas}
    if "properties" in salida:
        salida["properties"] = {k: _limpiar_esquema(v)
                                for k, v in salida["properties"].items()}
    return salida


def _a_gemini(mensajes: list[dict]) -> tuple[list[dict], dict[str, str]]:
    """Traduce del formato de bloques al de Gemini.

    Gemini identifica los resultados de herramienta por nombre y no por
    identificador, así que hay que recordar qué nombre tenía cada llamada.
    """
    nombres: dict[str, str] = {}
    contenidos: list[dict] = []

    for m in mensajes:
        contenido = m["content"]
        if isinstance(contenido, str):
            contenidos.append({"role": "user", "parts": [{"text": contenido}]})
            continue

        partes: list[dict] = []
        rol = "user"
        for b in contenido:
            if b.get("type") == "text":
                partes.append({"text": b["text"]})
                rol = "model" if m["role"] == "assistant" else "user"
            elif b.get("type") == "tool_use":
                nombres[b["id"]] = b["name"]
                partes.append({"functionCall": {"name": b["name"],
                                                "args": b["input"]}})
                rol = "model"
            elif b.get("type") == "tool_result":
                nombre = nombres.get(b["tool_use_id"], "desconocida")
                partes.append({"functionResponse": {
                    "name": nombre,
                    "response": {"resultado": b["content"]}}})
                rol = "user"
        if partes:
            contenidos.append({"role": rol, "parts": partes})
    return contenidos, nombres


BASE_URLS = {
    "openai":     "https://api.openai.com/v1",
    "groq":       "https://api.groq.com/openai/v1",
    "deepseek":   "https://api.deepseek.com/v1",
    "mistral":    "https://api.mistral.ai/v1",
    "xai":        "https://api.x.ai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "nan":        "https://api.nan.builders/v1",
    "local":      "http://localhost:11434/v1",
}


class ProveedorCompatible:
    """Cualquier proveedor que hable el protocolo de OpenAI.

    Casi todos lo hacen, incluido Gemini por su endpoint de compatibilidad.
    Cambiar de proveedor es cambiar una dirección, no reescribir nada.

    La diferencia con Anthropic es sólo de forma: allá las herramientas y el
    texto vienen en bloques; acá el texto va en `content` y las herramientas
    en `tool_calls`. El resto del sistema no se entera.
    """

    def __init__(self, modelo: str, api_key: str, base_url: str,
                 parametros: dict | None = None, cliente=None) -> None:
        import openai

        self._c = cliente or openai.OpenAI(api_key=api_key, base_url=base_url)
        self._modelo = modelo
        self._param = parametros or {}

    def route_intent(self, text: str) -> IntentRoute:
        response = self._c.chat.completions.create(
            model=self._modelo,
            max_tokens=min(self._param.get("max_tokens", 1024), 512),
            temperature=0,
            messages=[{"role": "system", "content": ROUTER_SYSTEM},
                      {"role": "user", "content": text}],
            tools=[{"type": "function", "function": {
                "name": ROUTER_TOOL["name"],
                "description": ROUTER_TOOL["description"],
                "parameters": ROUTER_TOOL["input_schema"],
            }}],
            tool_choice={"type": "function",
                         "function": {"name": ROUTER_TOOL["name"]}},
        )
        calls = []
        content = ()
        try:
            for choice in response.choices:
                message = choice.message
                for call in message.tool_calls or []:
                    calls.append(Llamada(
                        id=call.id, nombre=call.function.name,
                        args=json.loads(call.function.arguments),
                    ))
                if message.content not in (None, ""):
                    content += (message.content,)
                refusal = getattr(message, "refusal", None)
                if refusal:
                    content += (refusal,)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RoutingError("Malformed router tool arguments.") from exc
        return RouteEnvelope(content=content, calls=tuple(calls)).validate()

    def responder(self, sistema, mensajes, herramientas) -> Respuesta:
        r = self._c.chat.completions.create(
            model=self._modelo,
            max_tokens=self._param.get("max_tokens", 1024),
            temperature=self._param.get("temperature", 0.3),
            messages=[{"role": "system", "content": sistema}]
                     + _a_openai(mensajes),
            tools=[{"type": "function",
                    "function": {"name": h["name"],
                                 "description": h["description"],
                                 "parameters": h["input_schema"]}}
                   for h in herramientas] or None)

        m = r.choices[0].message
        llamadas = [Llamada(id=c.id, nombre=c.function.name,
                            args=json.loads(c.function.arguments or "{}"))
                    for c in (m.tool_calls or [])]
        return Respuesta(texto=(m.content or "").strip(), llamadas=llamadas)


def _a_openai(mensajes: list[dict]) -> list[dict]:
    """Traduce los mensajes del formato de bloques al de OpenAI."""
    salida: list[dict] = []
    for m in mensajes:
        contenido = m["content"]
        if isinstance(contenido, str):
            salida.append({"role": m["role"], "content": contenido})
            continue

        texto = "".join(b["text"] for b in contenido if b.get("type") == "text")
        usos = [b for b in contenido if b.get("type") == "tool_use"]
        resultados = [b for b in contenido if b.get("type") == "tool_result"]

        if usos:
            salida.append({
                "role": "assistant",
                "content": texto or None,
                "tool_calls": [
                    {"id": b["id"], "type": "function",
                     "function": {"name": b["name"],
                                  "arguments": json.dumps(b["input"],
                                                          ensure_ascii=False)}}
                    for b in usos]})
        elif texto:
            salida.append({"role": m["role"], "content": texto})

        # Cada resultado de herramienta va como un mensaje propio.
        for b in resultados:
            salida.append({"role": "tool", "tool_call_id": b["tool_use_id"],
                           "content": b["content"]})
    return salida


def desde_base(cur, workspace_id: str, api_key: str) -> Proveedor:
    """Arma el proveedor según lo configurado, con preferencia por el ajuste
    del espacio sobre el global."""
    cur.execute(
        """select proveedor, modelo, parametros from model_config
            where activo and (workspace_id = %s or ambito = 'global')
            order by (workspace_id is not null) desc limit 1""",
        (workspace_id,))
    fila = cur.fetchone()
    if not fila:
        raise LookupError(
            "No hay modelo configurado. Se define en la consola de administración.")

    proveedor = fila["proveedor"]
    parametros = fila["parametros"] or {}

    if proveedor == "gemini":
        return ProveedorGemini(fila["modelo"], api_key, parametros)
    if proveedor == "anthropic":
        return ProveedorAnthropic(fila["modelo"], api_key, parametros)

    base = parametros.get("base_url") or BASE_URLS.get(proveedor)
    if not base:
        raise LookupError(
            f"No sé a qué dirección hablarle a '{proveedor}'. Agregala en "
            f"BASE_URLS o en los parámetros del modelo.")
    return ProveedorCompatible(fila["modelo"], api_key, base, parametros)
