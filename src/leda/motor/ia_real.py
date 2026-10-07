"""La IA real del motor: una llamada estructurada y una redacción (diseño probado en la
Etapa 2, E2-3b).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Un turno"); ADR 0018, decisiones 1, 6 y 8.
Se trae lo mínimo de la llamada estructurada de la rama congelada (`llm.py` en
`respaldo-flujos-antes-de-d`: la llamada con herramienta y `llamar_con_plazo`):

- `elegir_jugadas` le ofrece a la IA una sola herramienta cuyo esquema es la lista cerrada de
  jugadas, cada una una variante con su definición y sólo sus datos, más `fuera_de_la_lista`
  para decir que lo pedido no está en ella. El código decide después si cada jugada vale
  (`fichas.py`). La herramienta no se fuerza con `tool_choice` (Claude Sonnet 5.5 no lo
  acepta): la piden las instrucciones, y no llamarla es no responder.
- `redactar` pide el texto de la respuesta desde los hechos, con el tono del espacio.
- Los dos pedidos llevan, después de las instrucciones, el significado de cada dato y cada código
  que traen (`hechos.bloque`; revisión del contrato, 2026-10-05), y el día de la semana de cada
  fecha, con hoy, ayer, mañana o pasado mañana (`hechos.dias`; tercera vuelta, 2026-10-06).

Habla el protocolo de chat de OpenAI, que es el de GPT-6 sol por OpenRouter (el modelo del
espacio sale de `model_config`, como hacía `leda.llm.desde_base`, retirado en la E3-3; la
clave, del entorno, nunca del código). Sin reintentos propios: el reintento es uno solo y lo
hace el turno (decisión 8). Cada llamada tiene un plazo total, además del tiempo por fase del
cliente HTTP. El proveedor `chatgpt` (la suscripción del usuario, 2026-10-07) no usa clave sino
la sesión de `python -m leda chatgpt login`; su cliente (`chatgpt.ClienteChatGPT`) cumple el
mismo contrato y traduce cada pedido al formato de respuestas del servicio de Codex.

Cada modelo lleva sus parámetros (`model_config.parametros`, o un argumento para el corredor de
las conversaciones; E3-8, la comparación de IA): el tiempo por fase (`timeout_s`), el plazo total
(`plazo_s`), los topes de salida (`tope_jugadas`, `tope_redaccion`) y campos propios del pedido
(`cuerpo_extra`, por ejemplo para que un modelo no razone por dentro). `validar_parametros` los
revisa al crear el cliente: un valor que no vale, o un nombre que no se conoce, se rechaza
nombrándolo; nunca se reemplaza en silencio por el de omisión.
"""

from __future__ import annotations

import concurrent.futures
import json
import math
from dataclasses import dataclass
from typing import Any

import httpx

from ..llm import BASE_URLS, PROVEEDORES_CON_SESION, tiempos

from . import hechos
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
# Ronda 2: mensajes cortados con 700. Un tope que alcanza para un mensaje entero; si igual se
# corta, el proveedor lo dice (`finish_reason`) y es que la IA no respondió (`sin_cortar`).
TOPE_REDACCION = 2000
# Lo que el proveedor dice cuando cortó la respuesta por el tope.
CORTADA_POR_EL_TOPE = frozenset({"length", "max_tokens"})
# Los techos de los parámetros: más que esto es un error de escritura, no una espera razonable.
SEGUNDOS_MAXIMOS = 600.0
TOPE_MAXIMO = 32_768
# Los parámetros que el cliente y la IA leen; cualquier otro nombre es un error de escritura.
PARAMETROS = frozenset({"timeout_s", "reintentos", "plazo_s", "tope_jugadas", "tope_redaccion",
                        "temperature", "base_url", "cuerpo_extra"})
# Lo que arma el código en cada pedido: `cuerpo_extra` no lo puede pisar.
DEL_PEDIDO = frozenset({"model", "messages", "tools", "tool_choice", "max_tokens",
                        "max_completion_tokens", "temperature", "stream"})
# Para elegir jugadas, los días que vienen con su día de la semana: una fecha que la persona
# nombra por su día sale de ahí (`hechos.dias`). Ocho semanas, para que una previsión realista
# esté en la lista (E3-8: con dos semanas, "el miércoles 4" a 15 días se perdía).
DIAS_PROXIMOS = 56

# Cada dato que alguna ficha usa, con su tipo y qué es: qué dato es y que va sólo si la persona
# lo dijo (revisión del contrato, 2026-10-05). Describen el dato, no un caso.
DATOS = {
    "tarea": ("string", "El alias de la tarea (T1, T2...), de la lista de tareas. Sólo si el "
                        "mensaje, la pregunta abierta, el último aviso o la conversación dejan "
                        "claro de cuál se habla; si no, va vacío y Leda pregunta cuál."),
    "fecha": ("string", "La fecha para la que la persona espera terminar la tarea, como "
                        "AAAA-MM-DD, calculada desde hoy. Sólo si la dijo."),
    "motivo": ("string", "Por qué cambia la fecha: lo que la atrasa o la adelanta, con las "
                         "palabras de la persona. Sólo si lo dijo; la fecha o el atraso "
                         "mismos no son un porqué."),
    "causa": ("string", "Lo que le falta a la persona o lo que frena el trabajo, con sus "
                        "palabras. Sólo si lo dijo; nombrar la tarea o decir que está trabada "
                        "no es una causa."),
    "quien": ("string", "Quién puede destrabar el bloqueo, como lo nombró la persona. Sólo si "
                        "lo nombró."),
    "no_sabe": ("boolean", "Verdadero sólo si la persona dice que no sabe quién puede "
                           "destrabarlo."),
    "nadie_mas": ("boolean", "Verdadero sólo si la persona dice que nadie más puede "
                             "destrabarlo: le toca a la persona que escribe (nunca a "
                             "Leda)."),
    "palabras": ("string", "Lo que la persona contó de cómo viene la tarea, con sus palabras."),
    "a": ("string", "A quién quiere pasarle la tarea, como lo nombró la persona."),
    "opcion": ("string", "El alias de la opción que eligió (O1, O2...), de la pregunta "
                         "abierta."),
    "corrige": ("string", "El nombre de la jugada ya anotada que la persona dice que estuvo "
                          "mal."),
    "tarea_correcta": ("string", "El alias de la tarea en la que sí va, si la persona la "
                                 "dice."),
    "que_pide": ("string", "Qué le pidió la persona a Leda, resumido."),
}

# Qué es lo que no está en la lista: sólo un pedido de hacer algo (revisión del contrato,
# 2026-10-05; ronda 1, conversación 12).
FUERA_DE_LA_LISTA_ES = (
    "La persona le pide a Leda que haga algo que ninguna jugada hace. Es sólo un pedido de "
    "hacer algo: una pregunta sobre la conversación o sobre lo que Leda hizo o dijo no es un "
    "pedido y no lleva jugada.")


class RespuestaInvalida(ValueError):
    """La IA no devolvió la herramienta del turno, o sus argumentos no se pueden leer."""


class PlazoAgotado(TimeoutError):
    def __init__(self, plazo: float) -> None:
        super().__init__(f"sin respuesta en {plazo:g} s")


class ParametrosInvalidos(ValueError):
    """Un parámetro del modelo que no vale; el mensaje lo nombra."""


def validar_parametros(parametros: dict[str, Any]) -> dict[str, Any]:
    """Los parámetros del modelo, revisados y con los de omisión completados (`timeout_s`,
    `reintentos`, `plazo_s`, los dos topes y `cuerpo_extra`). Un valor que no vale o un nombre
    desconocido es `ParametrosInvalidos`, nombrándolo; nunca se ignora."""
    if not isinstance(parametros, dict):
        raise ParametrosInvalidos(f"Los parámetros del modelo son un objeto; vino {parametros!r}.")
    desconocidos = sorted(set(parametros) - PARAMETROS)
    if desconocidos:
        raise ParametrosInvalidos(
            f"Parámetro desconocido: {', '.join(map(repr, desconocidos))}; los que hay son "
            f"{', '.join(sorted(PARAMETROS))}.")
    try:
        timeout, reintentos = tiempos(parametros)
    except ValueError as e:
        raise ParametrosInvalidos(str(e)) from None
    if timeout > SEGUNDOS_MAXIMOS:
        raise ParametrosInvalidos(
            f"timeout_s debe ser de {SEGUNDOS_MAXIMOS:g} s o menos; vino {timeout!r}.")
    validos = {**parametros, "timeout_s": timeout, "reintentos": reintentos,
               "plazo_s": _segundos(parametros, "plazo_s", PLAZO_S),
               "tope_jugadas": _tope(parametros, "tope_jugadas", TOPE_JUGADAS),
               "tope_redaccion": _tope(parametros, "tope_redaccion", TOPE_REDACCION),
               "cuerpo_extra": _cuerpo_extra(parametros.get("cuerpo_extra", {}))}
    if "temperature" in parametros:
        t = parametros["temperature"]
        if (isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t)
                or not 0 <= t <= 2):
            raise ParametrosInvalidos(f"temperature debe ser un número de 0 a 2; vino {t!r}.")
    if "base_url" in parametros:
        b = parametros["base_url"]
        if not isinstance(b, str) or not b.strip():
            raise ParametrosInvalidos(f"base_url debe ser una dirección; vino {b!r}.")
    return validos


def _segundos(parametros: dict[str, Any], nombre: str, omision: float) -> float:
    valor = parametros.get(nombre, omision)
    if (isinstance(valor, bool) or not isinstance(valor, (int, float))
            or not math.isfinite(valor) or not 0 < valor <= SEGUNDOS_MAXIMOS):
        raise ParametrosInvalidos(
            f"{nombre} debe ser un número de segundos mayor que 0 y de {SEGUNDOS_MAXIMOS:g} o "
            f"menos; vino {valor!r}.")
    return float(valor)


def _tope(parametros: dict[str, Any], nombre: str, omision: int) -> int:
    valor = parametros.get(nombre, omision)
    # Un JSON escrito `1500.0` es un entero lógico: se acepta y se normaliza.
    if isinstance(valor, float) and math.isfinite(valor) and valor.is_integer():
        valor = int(valor)
    if isinstance(valor, bool) or not isinstance(valor, int) or not 0 < valor <= TOPE_MAXIMO:
        raise ParametrosInvalidos(
            f"{nombre} debe ser un entero de tokens mayor que 0 y de {TOPE_MAXIMO} o menos; "
            f"vino {valor!r}.")
    return valor


def _cuerpo_extra(extra: Any) -> dict[str, Any]:
    if not isinstance(extra, dict) or not all(isinstance(k, str) for k in extra):
        raise ParametrosInvalidos(
            f"cuerpo_extra debe ser un objeto con los campos que se suman al pedido; vino "
            f"{extra!r}.")
    pisados = sorted(set(extra) & DEL_PEDIDO)
    if pisados:
        raise ParametrosInvalidos(
            f"cuerpo_extra no puede llevar {', '.join(map(repr, pisados))}: lo arma el código.")
    try:
        json.dumps(extra)
    except (TypeError, ValueError) as e:
        raise ParametrosInvalidos(f"cuerpo_extra no se puede mandar como JSON ({e}).") from None
    return dict(extra)


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
        parametros = validar_parametros(parametros)
        # Los reintentos del proveedor no se usan: el reintento es uno y lo hace el turno.
        http = httpx.Client(timeout=parametros["timeout_s"], transport=transporte,
                            headers={"Authorization": f"Bearer {api_key}"})
        return cls(modelo, base_url.rstrip("/"), http, parametros)

    def completar(self, cuerpo: dict[str, Any]) -> dict[str, Any]:
        plazo = float(self.parametros.get("plazo_s", PLAZO_S))
        # Los campos propios del modelo van primero: lo que arma el código nunca se pisa.
        extra = self.parametros.get("cuerpo_extra") or {}

        def pedir() -> dict[str, Any]:
            r = self.http.post(f"{self.base_url}/chat/completions",
                               json={**extra, "model": self.modelo, **cuerpo})
            r.raise_for_status()
            return r.json()

        return llamar_con_plazo(pedir, plazo)


def esquema_de_jugadas(posibles: list[str]) -> dict[str, Any]:
    """La herramienta cuyo esquema es la lista cerrada: cada jugada (más `fuera_de_la_lista`)
    es una variante con su nombre, su definición (`Ficha.es`) y sólo sus datos (revisión del
    contrato, 2026-10-05: un esquema plano le ofrecía todos los datos a todas). Sólo el nombre
    es obligatorio: la tarea puede faltar (la duda la pregunta el código) y ningún dato se
    fuerza."""
    variantes = [_variante(n, FICHAS[n].es if n in FICHAS else n,
                           FICHAS[n].necesita + FICHAS[n].opcional if n in FICHAS else ())
                 for n in posibles]
    variantes.append(_variante(FUERA_DE_LA_LISTA, FUERA_DE_LA_LISTA_ES, ("que_pide",)))
    return {"type": "function", "function": {
        "name": NOMBRE_HERRAMIENTA,
        "description": ("Las jugadas que corresponden al mensaje, en el orden en que la "
                        "persona las dijo; ninguna si el mensaje no dice ni pide nada que una "
                        "jugada haga. Cada jugada lleva sólo sus datos."),
        "parameters": {
            "type": "object",
            "properties": {"jugadas": {"type": "array", "items": {"anyOf": variantes}}},
            "required": ["jugadas"]}}}


def _variante(nombre: str, es: str, datos: tuple[str, ...]) -> dict[str, Any]:
    return {"type": "object", "description": es,
            "properties": {"nombre": {"type": "string", "enum": [nombre]},
                           **{d: {"type": DATOS[d][0], "description": DATOS[d][1]}
                              for d in datos}},
            "required": ["nombre"], "additionalProperties": False}


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


def sin_cortar(respuesta: dict[str, Any]) -> dict[str, Any]:
    """La respuesta, si el proveedor no la cortó por el tope; si la cortó, `RespuestaInvalida`:
    una respuesta a medias es que la IA no respondió (un reintento y después su camino de
    falla), nunca un texto o unas jugadas incompletas (tercera vuelta, 2026-10-06)."""
    try:
        motivo = respuesta["choices"][0].get("finish_reason")
    except (KeyError, IndexError, TypeError, AttributeError):
        return respuesta            # sin la forma de una respuesta: lo dice quien la lee
    if motivo in CORTADA_POR_EL_TOPE:
        raise RespuestaInvalida("La respuesta se cortó por el tope de salida.")
    return respuesta


def leer_jugadas(respuesta: dict[str, Any]) -> list[Jugada]:
    """Las jugadas de la llamada a la herramienta; sin ella, ilegible o cortada,
    `RespuestaInvalida` (para el turno, la IA no respondió: un reintento y después su camino de
    falla)."""
    sin_cortar(respuesta)
    try:
        mensaje = respuesta["choices"][0]["message"]
        llamadas = [c["function"] for c in mensaje.get("tool_calls") or []
                    if c["function"]["name"] == NOMBRE_HERRAMIENTA]
    except (KeyError, IndexError, TypeError, AttributeError) as e:
        # Sin la forma de una respuesta (un mensaje vacío o que no es un objeto): la IA no
        # respondió, nunca "ninguna jugada".
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
        # El día de cada fecha y de las ocho semanas que vienen: la IA no los calcula.
        situacion = {**situacion, "dias": hechos.dias(situacion, proximos=DIAS_PROXIMOS)}
        respuesta = self.cliente.completar({
            "temperature": 0,
            "max_tokens": int(self.cliente.parametros.get("tope_jugadas", TOPE_JUGADAS)),
            "messages": [{"role": "system",
                          "content": f"{INSTRUCCIONES_JUGADAS}\n\n{hechos.bloque(situacion)}"},
                         {"role": "user", "content": _json(situacion)}],
            "tools": [herramienta],
            # Sin forzar: Claude Sonnet 5.5 rechaza `tool_choice` forzado (400, 2026-10-05).
            # La herramienta es la única ofrecida y las instrucciones piden llamarla siempre;
            # si no la llama (contesta con texto, o nada), `leer_jugadas` levanta
            # `RespuestaInvalida`: para el turno, la IA no respondió (un reintento y después su
            # camino de falla), nunca una lista vacía de jugadas.
            "tool_choice": "auto",
        })
        return leer_jugadas(respuesta)

    def redactar(self, pedido: dict[str, Any]) -> str:
        pedido = {**pedido, "dias": hechos.dias(pedido)}     # el día de cada fecha, del código
        respuesta = self.cliente.completar({
            "temperature": self.cliente.parametros.get("temperature", 0.3),
            "max_tokens": int(self.cliente.parametros.get("tope_redaccion", TOPE_REDACCION)),
            "messages": [{"role": "system",
                          "content": f"{INSTRUCCIONES_REDACCION}\n\n{hechos.bloque(pedido)}"
                                     f"\n\n{bloque_de_tono(self.tono)}"},
                         {"role": "user", "content": _json(pedido)}],
        })
        sin_cortar(respuesta)
        try:
            texto = respuesta["choices"][0]["message"].get("content")
        except (KeyError, IndexError, TypeError) as e:
            raise RespuestaInvalida(f"Respuesta ilegible ({type(e).__name__}).") from e
        return (texto or "").strip()


def desde_base(cur, workspace_id: str, claves) -> IAReal:
    """La IA configurada para el espacio (o la global), como hacía `leda.llm.desde_base`. `claves`
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
        raise LookupError(f"El motor sólo habla el protocolo compatible con OpenAI; "
                          f"'{proveedor}' no lo usa.")
    con_sesion = proveedor in PROVEEDORES_CON_SESION
    if con_sesion:
        # La suscripción de ChatGPT: sin clave, con la sesión guardada (`chatgpt.py`).
        from .chatgpt import ClienteChatGPT, SesionChatGPT, validar_parametros_chatgpt
    try:
        parametros = (validar_parametros_chatgpt if con_sesion else validar_parametros)(
            parametros)
    except ParametrosInvalidos as e:
        # Para quien llama, la IA no está configurada (incidente y aviso neutro), con el porqué.
        raise LookupError(f"Los parámetros del modelo '{proveedor}/{fila['modelo']}' no "
                          f"valen: {e}") from None
    if con_sesion:
        try:
            sesion = SesionChatGPT.abrir()      # sin sesión, `SesionChatGPTAusente`
        except ValueError as e:                 # una ruta dentro del repositorio
            raise LookupError(str(e)) from None
        return IAReal(ClienteChatGPT.crear(fila["modelo"], sesion, parametros),
                      tono_del_espacio(cur, workspace_id),
                      nombre=f"{proveedor}/{fila['modelo']}")
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
