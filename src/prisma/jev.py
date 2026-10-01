"""Cliente de Jev y resolución de referencias a tarea.

Jev (TypeSafe AI, `typesafe/jev-1.13` vía OpenRouter) no es un proveedor de
conversación: elige entre opciones con una probabilidad por opción, no
genera texto. No vive en `model_config` ni pasa por `llm.Proveedor` — es un
colaborador aparte, con su propia credencial (`PRISMA_OPENROUTER_API_KEY`).

Receta congelada, de `docs/architecture/interpretacion-y-confirmacion.md`
§5.6, §5.8 y §5.9 (ADR 0006): por referencia a tarea, una llamada con dos
preguntas (alcance y tarea) y, si decide clara, una segunda de verificación.
Si Jev no responde, no se adivina: se lanza `JevError` para que quien llama
pregunte en vez de elegir.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol, Sequence

import httpx

URL = "https://openrouter.ai/api/alpha/decisions"
MODELO = "typesafe/jev-1.13"
INTENTOS = 4
_REINTENTABLES = {429, 500, 502, 503, 504}

INSTRUCCION_ALCANCE = (
    "¿La referencia apunta a una tarea concreta, a varias tareas (todo un "
    "área, todo lo de una persona o algo genérico que abarca varias) o a "
    "ninguna tarea del equipo?")
CRITERIOS_ALCANCE = {
    "una_tarea": "Apunta a una sola tarea concreta.",
    "varias_tareas": "Abarca varias tareas: un área, lo de una persona o algo genérico.",
    "ninguna": "No corresponde a ninguna tarea del equipo.",
}
INSTRUCCION_TAREA = "Si la referencia apunta a una tarea, ¿a cuál?"
INSTRUCCION_VERIFICACION = (
    "¿La referencia del mensaje habla exactamente de esta tarea (la misma "
    "cosa, aunque esté dicha con otras palabras, con errores o con el "
    "vocabulario del equipo), y no de otra cosa parecida o del mismo tipo?")
# Pregunta de la candidata subcampeona (T7, punto L; decisión del usuario,
# 2026-09-24: "ante la duda se pregunta", medida en el diseño §5.11) -- viaja
# en la MISMA llamada de verificación que "misma", nunca aparte.
INSTRUCCION_RIVAL = (
    "¿La referencia, tal como está dicha, también podría estar hablando de "
    "esta otra tarea en lugar de la elegida? Respondé que sí sólo si una "
    "persona del equipo podría entender esa referencia como cualquiera de "
    "las dos.")

# Cortes de la receta congelada (ADR 0006; §5.6, §5.8, §5.9). Se ajustan acá,
# no en el llamador.
CORTE_NINGUNA = 0.6
CORTE_VARIAS = 0.5
CORTE_CLARA = 0.85
MARGEN_CLARA = 0.4
CORTE_CANDIDATA = 0.1
CORTE_VERIFICACION = 0.5
# T7, punto L: si la subcampeona podría ser confundida con la elegida, ya no
# es clara -- pasa a ambigua con las dos como candidatas.
CORTE_RIVAL = 0.5

# Cota del texto de bloqueo que entra en `TareaCandidata.criterio()` (T7,
# punto H): acota lo que un bloqueo con causa larga manda a Jev, sin límite
# realista para una causa escrita a mano.
MAX_LONGITUD_CAUSAS_BLOQUEO = 200


def _acotar(texto: str, limite: int) -> str:
    if len(texto) <= limite:
        return texto
    return texto[:limite - 1].rstrip() + "…"


class JevError(RuntimeError):
    """Jev no respondió tras los reintentos acotados.

    Quien llama no adivina con esto: pregunta a la persona (ADR 0006,
    consecuencias)."""


# --------------------------------------------------------------------- cliente

@dataclass
class ClienteJev:
    """Cliente delgado de la API de decisiones de OpenRouter.

    Reintenta timeouts y errores 5xx/429 hasta `intentos` veces, con espera
    creciente; nunca reintenta indefinidamente y nunca reintenta un error
    del cliente (clave inválida, pedido malformado). `dormir` es inyectable
    para que las pruebas no esperen de verdad.
    """

    # `repr=False`: el repr por defecto del dataclass mostraba la clave en
    # texto plano, y una excepción sin capturar la imprime entera en la
    # traza (se vio en un fallo real de pytest).
    api_key: str = field(repr=False)
    cliente: httpx.Client | None = None
    intentos: int = INTENTOS
    dormir: Callable[[float], None] = time.sleep

    def __post_init__(self) -> None:
        if self.cliente is None:
            self.cliente = httpx.Client(timeout=60)

    def decidir(self, state: dict[str, Any],
                preguntas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        cuerpo = {"model": MODELO, "state": state, "questions": preguntas}
        encabezados = {"Authorization": f"Bearer {self.api_key}"}
        ultimo: Exception | None = None

        for intento in range(self.intentos):
            try:
                r = self.cliente.post(URL, headers=encabezados, json=cuerpo)
            except httpx.TransportError as exc:
                ultimo = exc
                if intento < self.intentos - 1:
                    self.dormir(2 * (intento + 1))
                continue

            if r.status_code == 200:
                datos = r.json()
                return datos.get("answers") or datos

            ultimo = JevError(f"Jev respondió {r.status_code}: {r.text[:300]}")
            if r.status_code not in _REINTENTABLES or intento == self.intentos - 1:
                break
            self.dormir(2 * (intento + 1))

        raise JevError(
            f"Jev no respondió tras {self.intentos} intentos.") from ultimo


def desde_base(api_key: str) -> Jev | None:
    """Arma el cliente de Jev desde la credencial, o `None` si no hay
    (`PRISMA_OPENROUTER_API_KEY` vacía).

    Sin cliente, `gateway._turno` no resuelve ninguna referencia y el turno
    sigue exactamente como antes de esta unidad (T3, `aclaracion-con-
    botones`). Mismo patrón de reemplazo que `llm.desde_base`: `_turno` hace
    un import local de este nombre en cada turno, así que alcanza con
    reemplazar `jev.desde_base` para las pruebas y para que el banco no
    llame a Jev de verdad por defecto (`tests/banco/corrida.py`).
    """
    if not api_key:
        return None
    return ClienteJev(api_key=api_key)


@dataclass
class ClienteJevGuionado:
    """Devuelve respuestas preparadas. Permite probar la resolución de
    referencias sin credencial ni red, igual que `ProveedorGuionado` en
    `llm.py`."""

    guion: list[dict[str, dict[str, Any]]]
    pedidos: list[tuple[dict, dict]] = field(default_factory=list)

    def decidir(self, state: dict[str, Any],
                preguntas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        self.pedidos.append((state, preguntas))
        if not self.guion:
            raise JevError("Guión de Jev agotado: falta encolar una respuesta.")
        return self.guion.pop(0)


class Jev(Protocol):
    """Lo que necesita `resolver_referencia_tarea` de un cliente de Jev."""

    def decidir(self, state: dict[str, Any],
                preguntas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]: ...


# ------------------------------------------------------------ resolución

@dataclass(frozen=True)
class TareaCandidata:
    id: str
    titulo: str
    area: str
    responsable: str
    # Para decidir, del lado de quien arma los botones (T4), si la tarea es
    # de quien escribe o de otra persona -- nunca entra en `criterio()`, que
    # es lo único que viaja a Jev.
    responsable_membership_id: str | None = None
    # Causa(s) de los bloqueos abiertos de la tarea, ya unidas en un solo
    # texto (T7, punto H; decisión del usuario, 2026-09-24: las causas de
    # bloqueo pueden viajar a TypeSafe vía OpenRouter). `None`/vacío si no
    # tiene bloqueos abiertos -- entonces `criterio()` no cambia.
    causas_bloqueo: str | None = None

    def criterio(self) -> str:
        base = f"{self.titulo} — área: {self.area} — responsable: {self.responsable}"
        if not self.causas_bloqueo:
            return base
        return f"{base} — bloqueada: {_acotar(self.causas_bloqueo, MAX_LONGITUD_CAUSAS_BLOQUEO)}"


class TipoResolucion(str, Enum):
    CLARA = "clara"
    AMBIGUA = "ambigua"
    # Alcance "varias_tareas" (T7, `aclaracion-con-botones`, punto C): la
    # referencia abarca de verdad varias tareas (un área, lo de una persona
    # o algo genérico) -- no es la misma ambigüedad que "una tarea concreta,
    # pero no sé cuál": esa sigue siendo AMBIGUA y sigue abriendo botones
    # (T4); VARIAS nunca abre botones, se lo pasa al modelo como contexto
    # (el banco real medía botones de más para pedidos genéricos, p. ej.
    # "algo pendiente esta semana").
    VARIAS = "varias"
    NINGUNA = "ninguna"


@dataclass(frozen=True)
class ResolucionReferencia:
    tipo: TipoResolucion
    tarea_id: str | None = None
    candidatas: tuple[str, ...] = ()


def _es_numero(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _extraer_probabilidades(respuesta: Any, pregunta: str) -> dict[str, float]:
    """Saca `respuesta[pregunta]["probabilities"]` validando la forma.

    Una respuesta de Jev con una forma distinta a la esperada —falta una
    pregunta, falta `probabilities`, o trae un valor que no es un número— no
    es un caso para adivinar con `KeyError`/`TypeError`: es exactamente el
    caso que `JevError` existe para señalar, para que quien resuelve la
    referencia pregunte en vez de romper.
    """
    try:
        probabilidades = respuesta[pregunta]["probabilities"]
    except (KeyError, TypeError, IndexError) as exc:
        raise JevError(
            f"Respuesta de Jev sin '{pregunta}.probabilities'.") from exc
    if not isinstance(probabilidades, dict):
        raise JevError(f"'{pregunta}.probabilities' no es un objeto.")
    for opcion, valor in probabilidades.items():
        if not _es_numero(valor):
            raise JevError(
                f"'{pregunta}.probabilities' trae un valor no numérico "
                f"para {opcion!r}.")
    return {opcion: float(valor) for opcion, valor in probabilidades.items()}


def _extraer_noul(respuesta: Any, pregunta: str) -> float:
    try:
        valor = respuesta[pregunta]["noul"]
    except (KeyError, TypeError, IndexError) as exc:
        raise JevError(f"Respuesta de Jev sin '{pregunta}.noul'.") from exc
    if not _es_numero(valor):
        raise JevError(f"'{pregunta}.noul' no es numérico.")
    return float(valor)


# --------------------------------------------------- el objetivo más probable

INSTRUCCION_OBJETIVO = (
    "Alguien quiere crear esta tarea. ¿A cuál de estos objetivos pertenece? "
    "Elegí el que la contiene mejor, según su título y el vocabulario del equipo.")


@dataclass(frozen=True)
class OrdenDeObjetivos:
    """Los candidatos ordenados por qué tan probable es que la tarea sea de cada
    uno. `clara` sólo es verdadera cuando Jev decide entre ellos sin duda (mismos
    cortes que una referencia a tarea): sólo entonces el primero se destaca. Si
    no, `ids` queda en el orden en que llegaron: no se afirma una elección que
    Jev no hizo."""
    ids: tuple[str, ...]
    clara: bool = False


def ordenar_objetivos(cliente: Jev, *, titulo: str,
                      objetivos: Sequence[tuple[str, str]],
                      vocabulario: str = "") -> OrdenDeObjetivos:
    """Ordena `objetivos` (pares `(id, título)`) según la tarea `titulo` con una
    sola llamada a Jev (etapa 3 del ADR 0014: Jev decide entre las candidatas que
    salen de la base). Las opciones viajan con claves cortas ("O1".."On"), como
    las de una referencia a tarea. Una respuesta de Jev con otra forma levanta
    `JevError`: quien llama ofrece el orden de siempre y lo registra."""
    ids = tuple(id_ for id_, _ in objetivos)
    if len(ids) < 2:
        return OrdenDeObjetivos(ids)
    claves = [f"O{i}" for i in range(1, len(ids) + 1)]
    por_clave = dict(zip(claves, ids))
    state = {"tarea": titulo}
    if vocabulario:
        state["vocabulario_del_equipo"] = vocabulario
    respuesta = cliente.decidir(state, {
        "objetivo": {"type": "choice", "instructions": INSTRUCCION_OBJETIVO,
                     "criteria": {clave: titulo_objetivo for clave, (_, titulo_objetivo)
                                  in zip(claves, objetivos)}}})
    probabilidades = {clave: p for clave, p in
                      _extraer_probabilidades(respuesta, "objetivo").items()
                      if clave in por_clave}
    ordenadas = sorted(probabilidades.items(), key=lambda kv: -kv[1])
    if not ordenadas:
        raise JevError("Respuesta de Jev sin probabilidades para los objetivos.")
    top_p = ordenadas[0][1]
    segundo_p = ordenadas[1][1] if len(ordenadas) > 1 else 0.0
    if not (top_p >= CORTE_CLARA and (top_p - segundo_p) >= MARGEN_CLARA):
        return OrdenDeObjetivos(ids)
    primero = por_clave[ordenadas[0][0]]
    return OrdenDeObjetivos((primero, *(i for i in ids if i != primero)), clara=True)


def resolver_referencia_tarea(
        cliente: Jev, *, mensaje: str, referencia: str,
        tareas: Sequence[TareaCandidata], vocabulario: str,
        quien_escribe: str | None = None) -> ResolucionReferencia:
    """Resuelve UNA referencia a tarea con la receta congelada.

    Sin candidatas no hay a qué llamar (principio 5 del diseño: sin
    candidatos reales no hay botones), así que una lista vacía es `NINGUNA`
    sin tocar la red.

    Las opciones de la elección "tarea" viajan con claves cortas ("T1".."Tn",
    en el orden de `tareas`), no con el id real: 5.3-5.9 sólo midieron a Jev
    con claves así ("T1".."T12"); el id real de una tarea es un UUID y nunca
    se probó como clave de una opción. La respuesta se traduce de vuelta al
    id real antes de devolverla.

    `quien_escribe` (T4, `aclaracion-con-botones`; §5.10), si se pasa, viaja
    como un campo más del `state` en las dos llamadas -- nunca como texto
    agregado a las instrucciones: §5.10 midió que el dato solo es seguro (0
    elecciones inseguras en 5 repeticiones) y que una pista en la instrucción
    lo empeora (1 o 2 inseguras por repetición). Dónde más aporta -- ordenar
    los botones y mostrar el responsable sólo cuando la tarea es de otra
    persona -- lo decide quien arma los botones, no esta función.
    """
    if not tareas:
        return ResolucionReferencia(TipoResolucion.NINGUNA)

    claves = [f"T{i}" for i in range(1, len(tareas) + 1)]
    por_clave = dict(zip(claves, tareas))
    criterios = {clave: tarea.criterio() for clave, tarea in por_clave.items()}
    state = {"mensaje": mensaje, "referencia": referencia,
              "vocabulario_del_equipo": vocabulario}
    if quien_escribe:
        state["quien_escribe"] = quien_escribe
    respuesta = cliente.decidir(state, {
        "alcance": {"type": "choice", "instructions": INSTRUCCION_ALCANCE,
                    "criteria": CRITERIOS_ALCANCE},
        "tarea": {"type": "choice", "instructions": INSTRUCCION_TAREA,
                  "criteria": criterios},
    })

    prob_alcance = _extraer_probabilidades(respuesta, "alcance")
    # Sólo cuentan las claves que mandamos: una clave ajena en la respuesta
    # no rompe la decisión, se descarta.
    prob_tarea = {clave: p for clave, p in _extraer_probabilidades(respuesta, "tarea").items()
                  if clave in por_clave}
    ordenadas = sorted(prob_tarea.items(), key=lambda kv: -kv[1])
    candidatas_por_umbral = tuple(por_clave[clave].id for clave, p in ordenadas
                                  if p >= CORTE_CANDIDATA)

    if prob_alcance.get("ninguna", 0) >= CORTE_NINGUNA:
        return ResolucionReferencia(TipoResolucion.NINGUNA)

    if not ordenadas:
        return ResolucionReferencia(TipoResolucion.NINGUNA)

    if prob_alcance.get("varias_tareas", 0) >= CORTE_VARIAS:
        return ResolucionReferencia(TipoResolucion.VARIAS,
                                     candidatas=candidatas_por_umbral)

    top_clave, top_p = ordenadas[0]
    segundo_p = ordenadas[1][1] if len(ordenadas) > 1 else 0.0
    if not (top_p >= CORTE_CLARA and (top_p - segundo_p) >= MARGEN_CLARA):
        return ResolucionReferencia(TipoResolucion.AMBIGUA,
                                     candidatas=candidatas_por_umbral)

    top_tarea = por_clave[top_clave]
    state_verificacion = {"mensaje": mensaje, "referencia": referencia,
                          "tarea": top_tarea.criterio(),
                          "vocabulario_del_equipo": vocabulario}
    if quien_escribe:
        state_verificacion["quien_escribe"] = quien_escribe

    preguntas_verificacion = {
        "misma": {"type": "noul", "instructions": INSTRUCCION_VERIFICACION}}

    # T7, punto L: la subcampeona -- la segunda tarea más probable que Jev
    # haya devuelto, sin importar cuán baja sea su probabilidad -- suma la
    # pregunta "rival" en la MISMA llamada, nunca aparte (revisión del
    # orquestador, 2026-09-24: un corte por `CORTE_CANDIDATA` acá dejaba
    # afuera justo el caso que §5.11 midió, b-0013, con 0,91 / 0,09). Sólo
    # cuando Jev no devolvió una segunda tarea en absoluto no hay de quién
    # preguntar -- eso sigue exactamente como antes de esta unidad.
    subcampeona = None
    if len(ordenadas) > 1:
        subcampeona = por_clave[ordenadas[1][0]]
        state_verificacion["tarea_elegida"] = top_tarea.criterio()
        state_verificacion["otra_tarea"] = subcampeona.criterio()
        preguntas_verificacion["rival"] = {
            "type": "noul", "instructions": INSTRUCCION_RIVAL}

    verificacion = cliente.decidir(state_verificacion, preguntas_verificacion)
    p_misma = _extraer_noul(verificacion, "misma")
    if p_misma < CORTE_VERIFICACION:
        return ResolucionReferencia(TipoResolucion.AMBIGUA, candidatas=(top_tarea.id,))

    if subcampeona is not None:
        p_rival = _extraer_noul(verificacion, "rival")
        if p_rival >= CORTE_RIVAL:
            return ResolucionReferencia(
                TipoResolucion.AMBIGUA, candidatas=(top_tarea.id, subcampeona.id))

    return ResolucionReferencia(TipoResolucion.CLARA, tarea_id=top_tarea.id)
