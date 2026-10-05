"""La IA real del motor: una llamada estructurada y una redacción (E2-3b).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Un turno"); ADR 0018, decisiones 1, 6 y 8.
Se trae lo mínimo de la llamada estructurada de la rama congelada (`llm.py` en
`respaldo-flujos-antes-de-d`: herramienta forzada con `tool_choice` y `llamar_con_plazo`):

- `elegir_jugadas` fuerza a la IA a contestar con una sola herramienta cuyo esquema es la lista
  cerrada de jugadas, cada una con sus datos, más `fuera_de_la_lista` para decir que lo pedido
  no está en ella. El código decide después si cada jugada vale (`fichas.py`).
- `redactar` pide el texto de la respuesta desde los hechos, con el tono del espacio.

Habla el protocolo de chat de OpenAI, que es el de GPT-6 sol por OpenRouter (el modelo del
espacio sale de `model_config`, como en `leda.llm.desde_base`; la clave, del entorno, nunca del
código). Sin reintentos propios: el reintento es uno solo y lo hace el turno (decisión 8). Cada
llamada tiene un plazo total, además del tiempo por fase del cliente HTTP.
"""

from __future__ import annotations

import concurrent.futures
import json
from dataclasses import dataclass
from typing import Any

import httpx

from leda.llm import BASE_URLS, _tiempos

from .fichas import FICHAS
from .ia import Jugada
from .instrucciones import (INSTRUCCIONES_JUGADAS, INSTRUCCIONES_REDACCION, Tono,
                            bloque_de_tono, tono_del_espacio)

NOMBRE_HERRAMIENTA = "elegir_jugadas"
FUERA_DE_LA_LISTA = "fuera_de_la_lista"

# Plazo total de una llamada, en segundos (`plazo_s` en `model_config.parametros`). GPT-6 sol
# tardó 11 a 14 s por llamada en el banco del 2026-10-03 (bitácora de flujos).
PLAZO_S = 40.0
# Topes de salida (`tope_jugadas`, `tope_redaccion`): un modelo que razona por dentro gasta
# parte del tope antes de contestar.
TOPE_JUGADAS = 1500
TOPE_REDACCION = 700

# Cada dato que alguna ficha usa, con su tipo y qué es. Describen el dato, no un caso.
DATOS = {
    "tarea": ("string", "El alias de la tarea (T1, T2...), de la lista de tareas."),
    "fecha": ("string", "La fecha que dijo la persona, como AAAA-MM-DD."),
    "motivo": ("string", "Por qué, con las palabras de la persona."),
    "causa": ("string", "Qué la traba, con las palabras de la persona."),
    "quien": ("string", "Quién puede destrabarla, como lo nombró la persona."),
    "no_sabe": ("boolean", "La persona dice que no sabe quién puede destrabarla."),
    "nadie_mas": ("boolean", "La persona dice que nadie más puede destrabarla: le toca a "
                             "ella."),
    "a": ("string", "A quién quiere pasarle la tarea, como lo nombró la persona."),
    "opcion": ("string", "El alias de la opción que eligió (O1, O2...), de la pregunta "
                         "abierta."),
    "corrige": ("string", "Qué jugada ya anotada se corrige, por su nombre."),
    "tarea_correcta": ("string", "El alias de la tarea en la que sí va, si la persona la "
                                 "dice."),
    "que_pide": ("string", "Sólo con fuera_de_la_lista: qué pidió la persona, resumido."),
}


class RespuestaInvalida(ValueError):
    """La IA no devolvió la herramienta del turno, o sus argumentos no se pueden leer."""


class PlazoAgotado(TimeoutError):
    def __init__(self, plazo: float) -> None:
        super().__init__(f"sin respuesta en {plazo:g} s")


def llamar_con_plazo(llamada, plazo: float):
    """El resultado de `llamada()` o `PlazoAgotado`: el plazo acota el tiempo TOTAL (el del
    cliente HTTP es por fase). La respuesta tardía se descarta; el hilo termina solo,
    acotado por el tiempo por fase del cliente."""
    ejecutor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        futuro = ejecutor.submit(llamada)
        terminados, _ = concurrent.futures.wait([futuro], timeout=plazo)
        if not terminados:
            raise PlazoAgotado(plazo)
        return futuro.result()
    finally:
        ejecutor.shutdown(wait=False)


@dataclass
class ClienteCompatible:
    """Un proveedor que habla el protocolo de chat de OpenAI, por HTTP directo."""

    modelo: str
    base_url: str
    http: httpx.Client
    parametros: dict[str, Any]

    @classmethod
    def crear(cls, modelo: str, api_key: str, base_url: str, parametros: dict[str, Any],
              transporte: httpx.BaseTransport | None = None) -> ClienteCompatible:
        timeout, _ = _tiempos(parametros)    # los reintentos del proveedor no se usan
        http = httpx.Client(timeout=timeout, transport=transporte,
                            headers={"Authorization": f"Bearer {api_key}"})
        return cls(modelo, base_url.rstrip("/"), http, dict(parametros))

    def completar(self, cuerpo: dict[str, Any]) -> dict[str, Any]:
        plazo = float(self.parametros.get("plazo_s", PLAZO_S))

        def pedir() -> dict[str, Any]:
            r = self.http.post(f"{self.base_url}/chat/completions",
                               json={"model": self.modelo, **cuerpo})
            r.raise_for_status()
            return r.json()

        return llamar_con_plazo(pedir, plazo)


def esquema_de_jugadas(posibles: list[str]) -> dict[str, Any]:
    """La herramienta cuyo esquema es la lista cerrada: el nombre de cada jugada (más
    `fuera_de_la_lista`) y los datos que usan sus fichas."""
    usados = {d for n in posibles if n in FICHAS
              for d in FICHAS[n].necesita + FICHAS[n].opcional} | {"que_pide"}
    para_que = "; ".join(f"{n}: {FICHAS[n].para_que}" for n in posibles if n in FICHAS)
    return {"type": "function", "function": {
        "name": NOMBRE_HERRAMIENTA,
        "description": ("Las jugadas que corresponden al mensaje, en el orden en que la "
                        f"persona las dijo. {para_que}; {FUERA_DE_LA_LISTA}: algo que "
                        "ninguna jugada hace."),
        "parameters": {
            "type": "object",
            "properties": {"jugadas": {"type": "array", "items": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "enum": [*posibles, FUERA_DE_LA_LISTA]},
                    **{d: {"type": DATOS[d][0], "description": DATOS[d][1]}
                       for d in DATOS if d in usados},
                },
                "required": ["nombre"]}}},
            "required": ["jugadas"]}}}


def _datos_de(nombre: str, crudos: dict[str, Any]) -> dict[str, Any]:
    """Los datos que la jugada usa, sin los vacíos (la ficha lee vacío como "no lo dijo")."""
    if nombre == FUERA_DE_LA_LISTA:
        validos = {"que_pide"}
    elif nombre in FICHAS:
        validos = set(FICHAS[nombre].necesita + FICHAS[nombre].opcional)
    else:
        validos = set()
    return {k: v for k, v in crudos.items()
            if k in validos and v is not None and not (isinstance(v, str) and not v.strip())}


def leer_jugadas(respuesta: dict[str, Any]) -> list[Jugada]:
    """Las jugadas de la llamada a la herramienta; sin ella, o ilegible, `RespuestaInvalida`
    (para el turno, la IA no respondió: un reintento y después su camino de falla)."""
    try:
        mensaje = respuesta["choices"][0]["message"]
        llamadas = [c["function"] for c in mensaje.get("tool_calls") or []
                    if c["function"]["name"] == NOMBRE_HERRAMIENTA]
    except (KeyError, IndexError, TypeError) as e:
        raise RespuestaInvalida(f"Respuesta ilegible ({type(e).__name__}).") from e
    if not llamadas:
        raise RespuestaInvalida("La IA no llamó a la herramienta de las jugadas.")
    argumentos = llamadas[0].get("arguments")
    try:
        argumentos = json.loads(argumentos) if isinstance(argumentos, str) else argumentos
    except ValueError as e:
        raise RespuestaInvalida("Los argumentos de la herramienta no son JSON.") from e
    jugadas = argumentos.get("jugadas") if isinstance(argumentos, dict) else None
    if not isinstance(jugadas, list) or not all(
            isinstance(j, dict) and isinstance(j.get("nombre"), str) and j["nombre"]
            for j in jugadas):
        raise RespuestaInvalida("Las jugadas no tienen la forma del esquema.")
    return [Jugada(j["nombre"], _datos_de(j["nombre"], j)) for j in jugadas]


class IAReal:
    """La IA del motor sobre un proveedor real (el contrato es `ia.IA`)."""

    def __init__(self, cliente: ClienteCompatible, tono: Tono | None, *, nombre: str) -> None:
        self.cliente = cliente
        self.tono = tono
        self.nombre = nombre

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list[Jugada]:
        herramienta = esquema_de_jugadas(list(situacion["jugadas_posibles"]))
        respuesta = self.cliente.completar({
            "temperature": 0,
            "max_tokens": int(self.cliente.parametros.get("tope_jugadas", TOPE_JUGADAS)),
            "messages": [{"role": "system", "content": INSTRUCCIONES_JUGADAS},
                         {"role": "user", "content": _json(situacion)}],
            "tools": [herramienta],
            "tool_choice": {"type": "function", "function": {"name": NOMBRE_HERRAMIENTA}},
        })
        return leer_jugadas(respuesta)

    def redactar(self, pedido: dict[str, Any]) -> str:
        respuesta = self.cliente.completar({
            "temperature": self.cliente.parametros.get("temperature", 0.3),
            "max_tokens": int(self.cliente.parametros.get("tope_redaccion", TOPE_REDACCION)),
            "messages": [{"role": "system",
                          "content": f"{INSTRUCCIONES_REDACCION}\n\n{bloque_de_tono(self.tono)}"},
                         {"role": "user", "content": _json(pedido)}],
        })
        try:
            texto = respuesta["choices"][0]["message"].get("content")
        except (KeyError, IndexError, TypeError) as e:
            raise RespuestaInvalida(f"Respuesta ilegible ({type(e).__name__}).") from e
        return (texto or "").strip()


def desde_base(cur, workspace_id: str, claves) -> IAReal:
    """La IA configurada para el espacio (o la global), como `leda.llm.desde_base`. `claves`
    es la fuente de credenciales (`leda.config.config`): la clave nunca pasa por acá."""
    cur.execute(
        """select proveedor, modelo, parametros from model_config
            where activo and (workspace_id = %s or ambito = 'global')
            order by (workspace_id is not null) desc limit 1""", (workspace_id,))
    fila = cur.fetchone()
    if not fila:
        raise LookupError("No hay modelo configurado (python -m leda modelo).")
    proveedor, parametros = fila["proveedor"], fila["parametros"] or {}
    if proveedor in ("anthropic", "gemini"):
        raise LookupError(f"La prueba chica sólo habla el protocolo compatible con OpenAI; "
                          f"'{proveedor}' no lo usa.")
    base = parametros.get("base_url") or BASE_URLS.get(proveedor)
    if not base:
        raise LookupError(f"No hay dirección para el proveedor '{proveedor}'.")
    api_key = claves.clave_llm(proveedor)
    if not api_key:
        raise LookupError(f"Falta {claves.variable_clave_llm(proveedor)} para el proveedor "
                          f"'{proveedor}'.")
    cliente = ClienteCompatible.crear(fila["modelo"], api_key, base, parametros)
    return IAReal(cliente, tono_del_espacio(cur, workspace_id),
                  nombre=f"{proveedor}/{fila['modelo']}")


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, default=str)
