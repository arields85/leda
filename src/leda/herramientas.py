"""Herramientas del agente.

Todo lo que Leda puede hacer en el mundo pasa por acá. El modelo de lenguaje
no escribe en la base: pide una herramienta, y la herramienta valida la
autoridad del solicitante antes de tocar nada.

Es la diferencia entre una regla en el prompt, que se puede convencer, y una
regla en el servidor, que no.

Cada herramienta declara:
  - `accion`, que es lo que `autoridad.verificar` va a evaluar;
  - un esquema de parámetros, que se le pasa al modelo;
  - un handler que recibe el cursor ya acotado al espacio activo.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import psycopg
from psycopg.types.json import Jsonb

from .autoridad import (Denegado, Solicitante, puede_aprobar_tarea,
                         requiere_confirmacion, verificar)
from . import versiones
from .db import registrar_auditoria
from .incidentes import ETAPA_EVIDENCIA_INVALIDA, registrar_incidente
from .salida import (OBJETIVO_ETIQUETA_BOTON, enqueue_outbox,
                     etiquetas_de_tarea, normalize_visible_text,
                     telegram_utf16_units, truncar_etiqueta_boton)

# Los topes de lo que una persona escribe en un borrador de tarea, en unidades UTF-16
# de Telegram (`crear_borrador_tarea`). Vivían en `ingreso_tareas.py`, que se retiró
# con el alta guiada (E3-4); los mismos valores.
USER_FIELD_LIMITS = {
    "title": 200,
    "description": 800,
    "objective": 120,
    "responsible": 120,
    "area": 120,
    "due_date": 64,
    "acceptance_criterion": 500,
}
EVIDENCE_ITEM_LIMIT = 160
EVIDENCE_TOTAL_LIMIT = 800
EVIDENCE_COUNT_LIMIT = 8


@dataclass(frozen=True)
class Herramienta:
    nombre: str
    accion: str
    descripcion: str
    parametros: dict[str, Any]
    handler: Callable[..., Any]
    # Algunas verificaciones dependen del área del sujeto, que no viene en los
    # argumentos: hay que leerla de la base primero. Esas herramientas hacen
    # la verificación adentro, con el área ya resuelta.
    valida_en_handler: bool = False
    # El chat desde el que escribieron. No está en el esquema que ve el
    # modelo y lo inyecta el servidor: si el modelo pudiera declararlo,
    # bastaría con que dijera "privado" para sortear una regla que depende
    # de dónde se pidió algo.
    necesita_chat: bool = False
    # Las herramientas que escriben declaran esto (ADR 0005, decisión 1): lee
    # el estado vigente, valida autoridad y reglas de negocio -- las mismas
    # que el handler -- y arma la vista previa humana con su huella. Devuelve
    # una `Preparacion`, o directamente el mismo dict de rechazo que el
    # handler devolvería (para que una vista previa nunca proponga algo que
    # el confirmar va a negar). `ejecutar` es quien decide, con esto, si la
    # herramienta necesita confirmación: no una lista aparte por nombre de
    # acción, que `crear_objetivo` ya demostró que se puede desalinear
    # (`accion="crear_tarea"`, corregido en esta misma unidad).
    preparar: Callable[..., Any] | None = None


REGISTRO: dict[str, Herramienta] = {}


def herramienta(nombre: str, accion: str, descripcion: str, parametros: dict,
                *, valida_en_handler: bool = False,
                necesita_chat: bool = False,
                preparar: Callable[..., Any] | None = None):
    def envoltura(fn):
        REGISTRO[nombre] = Herramienta(nombre, accion, descripcion, parametros,
                                       fn, valida_en_handler, necesita_chat,
                                       preparar)
        return fn
    return envoltura


@dataclass(frozen=True)
class Preparacion:
    """Lo que arma la preparación de una herramienta que escribe: el cambio
    en términos humanos, y una huella del estado que se leyó para armarlo.

    `cambio` no incluye el aviso de que todavía no se aplicó nada -- eso lo
    agrega `resumen`, que es lo que se muestra en la vista previa. Se arma con
    `_filas`: un dato por línea (T10-4, R3-H11).

    `hecho` es el recibo al confirmar: una oración corta con lo que pasó, en
    pasado, armada con los mismos datos que `cambio` (T10-4, R3-H14: el recibo
    ya no repite la vista previa entera). Toda preparación lo define (una prueba
    de conformidad lo exige); si llegara vacío, quien confirma cuenta el cambio
    con la vista previa, nunca un "Hecho." solo.
    """
    cambio: str
    huella: str
    hecho: str = ""

    @property
    def resumen(self) -> str:
        return f"{self.cambio}\n\nTodavía no se aplicó ningún cambio."


def _huella(*partes: Any) -> str:
    """Hash estable del estado que se leyó. Opaco para quien lo compara:
    sólo importa si es igual o distinto al que se guardó en la vista previa.
    """
    crudo = "|".join("" if p is None else str(p) for p in partes)
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()


# Público (T6k, seguimiento a review-2c5b0ffe): el banco conversacional
# (`tests/banco/comprobadores.py`) necesita este vocabulario -- una palabra
# de estado ("Bloqueada", "Asignada") es vocabulario conocido, no un nombre
# de persona -- así que se expone con nombre público en vez de que ese
# módulo importe un privado de acá.
ESTADOS_LEGIBLES = {
    "asignada": "Asignada", "en_curso": "En curso", "bloqueada": "Bloqueada",
    "en_revision": "En revisión", "terminada": "Terminada",
    "cancelada": "Cancelada",
}


def _estado_legible(estado: str | None) -> str:
    return ESTADOS_LEGIBLES.get(estado, estado or "sin estado")


def _estar(estado: str | None) -> str:
    """El estado como algo en lo que la tarea "está" ("estar en curso", "estar
    asignada"): se lee bien con cualquiera, a diferencia de "a en curso" o de
    una mayúscula en mitad de la oración (T10-4, R3-H14)."""
    return f"estar {_estado_legible(estado).lower()}"


def recibo_de_estado(titulo: str, estado: str) -> str:
    """Lo que se le dice a la persona cuando la tarea pasó de estado. Entregar
    (`en_revision`) es el caso que la persona vive como algo que hizo ella: se
    lo agradece y dice a dónde fue la tarea (R3-H9: sin nombrar a quien revisa
    ni horarios). El resto dice el estado nuevo, en minúscula, con `_estar`."""
    if estado == "en_revision":
        return f"Gracias. La tarea «{titulo}» pasó a revisión."
    return f"La tarea «{titulo}» pasó a {_estar(estado)}."


def _filas(*filas: tuple[str | None, str | None]) -> str:
    """La vista previa de un cambio: un dato por línea (T10-4, R3-H11). Cada
    fila es `(etiqueta, valor)`, o `(None, frase)` para una frase suelta; una
    fila sin valor no sale. Único lugar donde se arma el renglón: las
    preparaciones pasan sus datos, no juntan texto a mano."""
    return "\n".join(
        valor if etiqueta is None else f"{etiqueta}: {valor}"
        for etiqueta, valor in filas if valor is not None)


# El texto exacto que `db/esquema.sql: motivo_no_cierra_tarea` devuelve cuando
# la única condición de cierre que falta es la aprobación de quien revisa el
# trabajo. `_preparar_aprobar_tarea` lo usa para predecir, sin escribir nada
# todavía, si ESTA aprobación (que la vista previa todavía no insertó) va a
# alcanzar para cerrar la tarea: corre la misma función SQL y trata ese
# motivo puntual como resuelto, porque es la única condición que este acto va
# a satisfacer. Si el texto de la base cambia sin actualizar esta constante,
# el peor caso es un falso "todavía falta algo" -- nunca un cierre indebido,
# porque `_aprobar_tarea` vuelve a preguntarle a la base, ya con la
# aprobación insertada, antes de cerrar de verdad (ADR 0008).
_MOTIVO_FALTA_APROBACION = "Falta la aprobación de quien revisa ese trabajo."


class NecesitaConfirmacion(Exception):
    """La acción no se ejecuta hasta que una persona diga que sí.

    Los argumentos se llaman `argumentos` y no `args` porque `BaseException`
    ya usa ese nombre: `super().__init__(resumen)` lo pisa con `(resumen,)`.
    Guardar `e.args` acá terminaba persistiendo el texto del resumen donde
    tenían que ir los argumentos de la herramienta.
    """

    def __init__(self, resumen: str, herramienta: str, argumentos: dict,
                 huella: str | None = None) -> None:
        self.resumen = resumen
        self.herramienta = herramienta
        self.argumentos = argumentos
        self.huella = huella
        super().__init__(resumen)


class EstadoCambio(Exception):
    """El estado que se había mostrado en la vista previa ya no es el mismo.

    Se lanza al confirmar, nunca antes: la preparación se volvió a correr con
    autoridad vigente y el resultado sigue siendo una propuesta válida, pero
    su huella no coincide con la que se guardó. No se aplica nada; quien
    llama arma una vista previa nueva con `resumen` y `huella`.
    """

    def __init__(self, resumen: str, herramienta: str, argumentos: dict,
                 huella: str) -> None:
        self.resumen = resumen
        self.herramienta = herramienta
        self.argumentos = argumentos
        self.huella = huella
        super().__init__(resumen)


class NecesitaElegir(Exception):
    """Falta un dato que no se puede adivinar y hay candidatos concretos.

    No es un error: es la única respuesta honesta cuando "Mar" son tres
    personas. La herramienta no hace nada, y la elección vuelve como un
    identificador exacto.

    `descarta` nombra los argumentos de texto libre que causaron la
    ambigüedad: no vuelven a viajar, porque volverían a ser ambiguos.
    """

    def __init__(self, resumen: str, campo: str,
                 opciones: list[tuple[str, str]],
                 descarta: tuple[str, ...] = ()) -> None:
        self.resumen = resumen
        self.campo = campo
        self.opciones = opciones
        self.descarta = descarta
        self.herramienta = ""      # los completa `ejecutar`
        self.argumentos: dict = {}   # `args` es de BaseException, no se toca
        super().__init__(resumen)


# Cuántas opciones puede ofrecer el modelo con `ofrecer_opciones` (T1, ADR
# 0007: "hasta cuatro opciones más la salida"). La salida "Quiero consultar
# otra cosa" no cuenta para este tope: la agrega siempre `agente.py`.
MAX_OPCIONES_MODELO = 4


@dataclass(frozen=True)
class OpcionOfrecida:
    """Una opción ya validada de `ofrecer_opciones`: la etiqueta que ve la
    persona y el valor que vuelve al tocarla -- un dict, no un id suelto,
    porque `gateway._resolver_toque_opcion_modelo` necesita saber si lo que
    se tocó fue una tarea o un texto para retomar distinto."""
    etiqueta: str
    valor: dict[str, Any]


class NecesitaOpciones(Exception):
    """El modelo le ofrece una elección concreta a la persona en vez de
    preguntar en texto abierto (T1, ADR 0007 "Leda orienta, no charla").

    No es un argumento que falta para volver a llamar a esta misma
    herramienta -- a diferencia de `NecesitaElegir` --: es una pregunta del
    modelo que espera la respuesta de la persona como su próximo turno.
    Tocar una opción retoma la conversación con el modelo
    (`gateway._resolver_toque_opcion_modelo`); nunca vuelve a llamar a
    `ofrecer_opciones`.
    """

    def __init__(self, pregunta: str, opciones: list[OpcionOfrecida]) -> None:
        self.pregunta = pregunta
        self.opciones = opciones
        super().__init__(pregunta)


def _uuid_normalizado(valor: Any) -> str | None:
    """Forma canónica (minúsculas) de un id de tarea, o `None` si no es un
    UUID válido.

    Revisión del orquestador sobre T1: `_tareas_activas_por_id` guardaba el
    string tal como lo mandó el modelo, y Postgres compara `uuid` por valor
    -- así que un id en mayúsculas encontraba igual la fila en la base --,
    pero el diccionario que arma esa función lo indexa por `str(f["id"])`,
    que psycopg siempre devuelve en minúsculas. `_ofrecer_opciones` buscaba
    después con el id tal cual llegó, sin normalizar: un id en mayúsculas
    nunca coincidía en el diccionario y se rechazaba como si no existiera.
    Normalizar acá, en el único lugar que valida un id entrante, es lo que
    hace que las dos puntas (guardar y buscar) comparen lo mismo."""
    try:
        return str(uuid.UUID(str(valor)))
    except (ValueError, AttributeError, TypeError):
        return None


def _tareas_activas_por_id(cur: psycopg.Cursor, workspace_id: str,
                          tarea_ids: list[Any]) -> dict[str, str]:
    """Título de cada id de tarea activa del espacio, bajo el mismo cursor con
    RLS del turno (T1, ADR 0007: "el modelo no inventa candidatos"). Un id que
    no es un UUID válido, que no existe, que está cerrada o que es de otro
    espacio queda simplemente afuera del resultado -- `_ofrecer_opciones` lo
    rechaza igual que uno inexistente, sin distinguir el motivo."""
    validos = [norm for norm in (_uuid_normalizado(tid) for tid in tarea_ids)
              if norm is not None]
    if not validos:
        return {}
    cur.execute(
        """select id, titulo from task
            where workspace_id = %s and estado not in ('terminada', 'cancelada')
              and id = any(%s::uuid[])""",
        (workspace_id, validos))
    return {str(f["id"]): f["titulo"] for f in cur.fetchall()}


@herramienta(
    "ofrecer_opciones", "consultar",
    "Ofrece a la persona una elección concreta, con botones, en vez de "
    "preguntar en texto abierto (Leda orienta, no charla). Cada opción es "
    "un texto corto (campo 'texto') o una tarea existente por su id (campo "
    "'tarea_id', con 'etiqueta' opcional para el botón). El servidor valida "
    "cada tarea contra el equipo, arma los botones, agrega la salida "
    f"'Quiero consultar otra cosa' y termina el turno. Hasta "
    f"{MAX_OPCIONES_MODELO} opciones. Una opción de tarea puede, en vez de "
    "retomar la conversación al tocarla, abrir el menú de acciones de esa "
    "tarea (campo 'accion': 'menu') -- lo calcula el servidor, no vuelve a "
    "preguntarte nada. No escribas nada más ni llames a otra herramienta "
    "después de usar ésta: el turno termina acá.",
    {"pregunta": {"type": "string", "requerido": True,
                 "description": "lo que Leda pregunta, en una frase corta"},
     "opciones": {
         "type": "array", "requerido": True,
         "description": f"hasta {MAX_OPCIONES_MODELO} opciones",
         "items": {
             "type": "object",
             "properties": {
                 "texto": {"type": "string",
                          "description": "una opción de texto corto"},
                 "tarea_id": {"type": "string",
                             "description": "id de una tarea existente"},
                 "etiqueta": {"type": "string",
                             "description": "etiqueta corta para el botón de "
                                            "la tarea (si falta, se usa su "
                                            "título)"},
                 "accion": {"type": "string", "enum": ["responder", "menu"],
                           "description": "sólo para una opción de tarea: "
                                          "'responder' (por defecto) retoma "
                                          "la conversación con esa tarea "
                                          "resuelta; 'menu' abre el menú de "
                                          "acciones de la tarea."},
             }}}})
def _ofrecer_opciones(cur, quien: Solicitante, pregunta, opciones):
    pregunta = normalize_visible_text(pregunta)
    if not pregunta:
        raise Denegado("ofrecer_opciones necesita una pregunta.")
    if not isinstance(opciones, list) or not opciones:
        raise Denegado("ofrecer_opciones necesita al menos una opción.")
    if len(opciones) > MAX_OPCIONES_MODELO:
        raise Denegado(
            f"ofrecer_opciones acepta hasta {MAX_OPCIONES_MODELO} opciones "
            f"(la salida se agrega aparte); llegaron {len(opciones)}.")

    tarea_ids = [o.get("tarea_id") for o in opciones
                if isinstance(o, dict) and o.get("tarea_id")]
    titulos = (_tareas_activas_por_id(cur, quien.workspace_id, tarea_ids)
              if tarea_ids else {})

    # Primera pasada: valida cada opción tal como antes (nada cambia acá) y
    # junta lo necesario para armar la etiqueta -- eso se resuelve en la
    # segunda pasada, como CONJUNTO, después de que todas las opciones de
    # tarea pasaron su validación (hallazgo de sesión 2 por Telegram:
    # etiquetas cortas y sin ambigüedad, `salida.etiquetas_boton_distinguibles`).
    validadas: list[dict] = []
    for o in opciones:
        if not isinstance(o, dict):
            raise Denegado(
                "Cada opción tiene que ser un objeto con 'texto' o 'tarea_id'.")
        tarea_id = o.get("tarea_id")
        texto = o.get("texto")
        if tarea_id and texto:
            raise Denegado(
                "Cada opción es una tarea (tarea_id) o un texto (texto), no "
                "las dos a la vez.")
        if tarea_id:
            tarea_id_normalizado = _uuid_normalizado(tarea_id)
            titulo = titulos.get(tarea_id_normalizado) if tarea_id_normalizado else None
            if titulo is None:
                raise Denegado(
                    f"La tarea {tarea_id} no existe entre las activas de "
                    "este equipo. No inventes candidatos: consultá las "
                    "tareas primero.")
            accion = o.get("accion") or "responder"
            if accion not in ("responder", "menu"):
                raise Denegado(
                    "El campo 'accion' de una opción de tarea sólo puede "
                    f"ser 'responder' o 'menu' (llegó: {accion!r}).")
            etiqueta_modelo = normalize_visible_text(o.get("etiqueta") or "")
            validadas.append({
                "tipo": "tarea", "tarea_id": tarea_id_normalizado,
                "titulo": titulo, "accion": accion,
                "etiqueta_modelo": etiqueta_modelo})
        elif texto:
            # Texto libre: la etiqueta la eligió el modelo -- se deja tal
            # cual (T1: "cuando el modelo elige su propia etiqueta, está
            # bien"), sólo con el corte duro de siempre como red de
            # seguridad.
            texto_final = truncar_etiqueta_boton(normalize_visible_text(texto))
            if not texto_final:
                raise Denegado("Una opción de texto no puede quedar vacía.")
            validadas.append({"tipo": "texto", "texto": texto_final})
        else:
            raise Denegado("Cada opción necesita 'texto' o 'tarea_id'.")

    # Segunda pasada: etiqueta de cada opción de tarea. Si el modelo ya dio
    # una etiqueta corta (<= `OBJETIVO_ETIQUETA_BOTON`), se respeta tal cual
    # -- es su elección, y ya es corta -- y sólo cuenta como obstáculo fijo
    # para las demás. Si no dio etiqueta, o la que dio es más larga que el
    # objetivo, se acorta a partir de esa base (el título, o su propia
    # etiqueta larga) y se desambigua contra el resto del conjunto.
    indices_tarea = [i for i, v in enumerate(validadas) if v["tipo"] == "tarea"]
    if indices_tarea:
        bases = []
        fijas = []
        for i in indices_tarea:
            v = validadas[i]
            et = v["etiqueta_modelo"]
            if et and len(et) <= OBJETIVO_ETIQUETA_BOTON:
                bases.append(et)
                fijas.append(True)
            else:
                base = et or v["titulo"]
                if not base:
                    raise Denegado("La etiqueta de una opción no puede quedar vacía.")
                bases.append(base)
                fijas.append(False)
        # `salida.etiquetas_de_tarea` es la receta única (R2-002, revisión
        # 2026-09-28+1): descuenta `costo_icono(ICONO_TAREA)` antes de
        # truncar/desambiguar y antepone el ícono después -- antes copiada a
        # mano acá, igual que en `agente._opciones_lista_tareas`.
        etiquetas = etiquetas_de_tarea(bases, fijas=fijas)
        for i, etiqueta in zip(indices_tarea, etiquetas):
            validadas[i]["etiqueta"] = etiqueta

    armadas: list[OpcionOfrecida] = []
    for v in validadas:
        if v["tipo"] == "tarea":
            armadas.append(OpcionOfrecida(
                etiqueta=v["etiqueta"],
                valor={"tipo": "tarea", "tarea_id": v["tarea_id"],
                      "titulo": v["titulo"], "etiqueta": v["etiqueta"],
                      "accion": v["accion"]}))
        else:
            armadas.append(OpcionOfrecida(
                etiqueta=v["texto"], valor={"tipo": "texto", "texto": v["texto"]}))

    # Seguimiento de review-149a33fa ("etiquetas repetidas del modelo"): la
    # segunda pasada de arriba desambigua tareas ENTRE SÍ, pero sólo cuando
    # ninguna de las dos es `fija` (`salida.etiquetas_boton_distinguibles`
    # nunca numera una etiqueta que el modelo eligió, hallazgo 7, seguimiento
    # b -- a propósito, para no tocarle la elección). Eso deja dos huecos sin
    # cubrir: dos opciones de texto con el mismo texto (nunca pasan por esa
    # función), y dos tareas con la MISMA etiqueta corta propia del modelo
    # (las dos `fija`, ninguna se numera). En los dos casos la persona vería
    # dos botones idénticos sin poder distinguir a cuál tocó. Se rechaza acá,
    # sobre las etiquetas ya armadas (después de acortar/desambiguar tareas),
    # con el mismo criterio que el resto de esta herramienta: el modelo no
    # inventa candidatos, reintenta con un `Denegado` explícito.
    vistas: set[str] = set()
    for a in armadas:
        clave = a.etiqueta.casefold()
        if clave in vistas:
            raise Denegado(
                f"Dos opciones no pueden mostrar la misma etiqueta ({a.etiqueta!r}). "
                "Dale a cada opción un texto o una etiqueta distinta.")
        vistas.add(clave)

    raise NecesitaOpciones(pregunta, armadas)


def candidatos(cur: psycopg.Cursor, texto: str) -> list[tuple[str, str]]:
    """Integrantes cuyo nombre contiene `texto`, por la vista del espacio.

    Devuelve todos los que coinciden. Quedarse con el primero es justamente
    lo que hacía que una tarea terminara asignada a quien no era.
    """
    cur.execute(
        """select membership_id, nombre from integrante
            where nombre ilike %s and activo order by nombre""",
        (f"%{texto}%",))
    return [(f["nombre"], str(f["membership_id"])) for f in cur.fetchall()]


def _validar_argumentos(h: Herramienta, args: dict[str, Any]) -> None:
    """Un argumento que el modelo inventó, o uno requerido que le faltó, no
    puede tirar abajo el turno entero (T7, punto J; evidencia b-0002: el
    modelo llamó `consultar_tareas(tarea_id=...)` -- ese parámetro no existe
    -- y el `TypeError` sin atrapar abortó todo lo que quedaba de la vuelta).

    Se valida acá, antes de `preparar`/`handler`, contra los parámetros
    declarados de la herramienta (`h.parametros`, la misma fuente que arma
    `esquemas()` para el modelo) -- un solo punto para las dos rutas de
    llamada, sin depender de atrapar `TypeError` genérico (que también
    taparía un bug real adentro del handler). `Denegado` reusa el mismo
    camino, sin incidente, que ya tenía "No existe la herramienta": un
    argumento inválido es un error del modelo, no una falla del sistema."""
    desconocidos = sorted(set(args) - set(h.parametros))
    faltantes = sorted(clave for clave, esquema in h.parametros.items()
                       if esquema.get("requerido") and clave not in args)
    if not desconocidos and not faltantes:
        return
    partes = []
    if desconocidos:
        partes.append(f"no reconocidos: {', '.join(desconocidos)}")
    if faltantes:
        partes.append(f"faltan: {', '.join(faltantes)}")
    aceptados = ", ".join(sorted(h.parametros)) or "ninguno"
    raise Denegado(
        f"argumentos no válidos para '{h.nombre}' ({'; '.join(partes)}). "
        f"Parámetros aceptados: {aceptados}.")


def ejecutar(cur: psycopg.Cursor, quien: Solicitante, nombre: str,
             args: dict[str, Any], *, ya_confirmada: bool = False,
             chat_id: int | None = None, huella_previa: str | None = None,
             preparacion: dict[str, Any] | None = None) -> Any:
    """Punto único de entrada. Nada llega a la base por otro camino.

    `ya_confirmada` es para lo que vuelve de una acción pendiente: la persona
    ya dijo que sí, y volver a frenarla sería un bucle. La autoridad se
    verifica igual — confirmar no es lo mismo que tener permiso.

    `chat_id` lo pone el servidor desde el update de Telegram, y sólo lo
    reciben las herramientas que lo declaran. No viaja en el esquema que ve
    el modelo: de dónde se pidió algo es un hecho, no un argumento.

    `huella_previa` es la que se guardó al mostrar la vista previa; sólo la
    manda quien confirma por botón. Si la preparación, corrida de nuevo,
    devuelve una huella distinta, no se aplica nada (`EstadoCambio`).

    `preparacion`, si se pasa un dict, se completa con `cambio`, `hecho` y
    `huella` de la última preparación corrida acá -- así quien llama arma un
    recibo que cuenta qué pasó, sin que `ejecutar` deje de devolver sólo el
    resultado del handler.

    Toda operación que llega a correr deja su fila en `audit_log`, en esta
    misma transacción y con la versión de las reglas (`_auditar`): lo que se
    ejecutó, como `herramienta:<nombre>`; lo que la cocina rechazó por una
    regla de negocio, como `herramienta_rechazada:<nombre>`. Lo que no llegó
    a correr (sin permiso, argumentos inválidos, esperando confirmación o
    una elección) no deja ninguna.
    """
    if nombre == "crear_tarea":
        raise Denegado(
            "Para crear una tarea hay que completar primero su borrador guiado.")
    h = REGISTRO.get(nombre)
    if h is None:
        raise Denegado(f"No existe la herramienta '{nombre}'.")

    _validar_argumentos(h, args)

    if not h.valida_en_handler:
        verificar(cur, quien, h.accion, area_id=args.get("area_id"))

    if h.preparar is not None:
        prep = h.preparar(cur, quien, **args)
        if isinstance(prep, dict):
            # La preparación encontró lo mismo que encontraría el handler:
            # un rechazo de negocio, no de autoridad. Se devuelve tal cual,
            # sin pasar por confirmación -- confirmar algo imposible no
            # tiene sentido.
            _auditar(cur, quien, nombre, args, ya_confirmada=ya_confirmada,
                     rechazo=prep)
            return prep
        if preparacion is not None:
            preparacion["cambio"] = prep.cambio
            preparacion["hecho"] = prep.hecho
            preparacion["huella"] = prep.huella
        if not ya_confirmada:
            raise NecesitaConfirmacion(prep.resumen, nombre, dict(args),
                                       huella=prep.huella)
        if huella_previa is not None and prep.huella != huella_previa:
            raise EstadoCambio(prep.resumen, nombre, dict(args), prep.huella)
    elif requiere_confirmacion(h.accion) and not ya_confirmada:
        raise NecesitaConfirmacion(_resumen(h, args), nombre, dict(args))

    llamada = dict(args)
    if h.necesita_chat:
        llamada["chat_id"] = chat_id

    try:
        resultado = h.handler(cur, quien, **llamada)
    except NecesitaElegir as e:
        # La herramienta sabe qué falta; acá se completa con qué hacía falta
        # para ella. El texto ambiguo no vuelve a viajar.
        e.herramienta = nombre
        e.argumentos = {k: v for k, v in args.items() if k not in e.descarta}
        raise
    _auditar(cur, quien, nombre, args, ya_confirmada=ya_confirmada,
             rechazo=resultado if _es_rechazo(nombre, resultado) else None)
    return resultado


# De qué trata cada operación, por el argumento que nombra su sujeto, en este
# orden: el primero presente es el sujeto de la fila de auditoría.
_SUJETO_POR_ARGUMENTO = (("tarea_id", "task"), ("bloqueo_id", "blocker"),
                         ("evidencia_id", "evidence"),
                         ("dependencia_id", "dependency"),
                         ("origen_tarea_id", "task"))


def _es_rechazo(nombre: str, resultado: Any) -> bool:
    """Si el handler devolvió un impedimento de negocio sin escribir nada.

    Es la regla de la confirmación por botón de `gateway` (antes de `d002c99`):
    nunca auditar como ejecutado lo que no escribió nada. `aprobar_tarea` es la
    excepción: escribe la aprobación aunque la tarea no llegue a cerrarse
    (`cerrada` en `False`), y eso sí es un efecto (ADR 0008)."""
    if not isinstance(resultado, dict):
        return False
    if nombre == "aprobar_tarea" and resultado.get("aprobada"):
        return False
    return bool(resultado.get("error")
                or resultado.get("retirada") is False
                or resultado.get("cerrada") is False
                or resultado.get("iniciada") is False
                or resultado.get("en_revision") is False)


def _sujeto(args: dict[str, Any]) -> tuple[str | None, str | None]:
    for clave, tipo in _SUJETO_POR_ARGUMENTO:
        valor = args.get(clave)
        if valor is None:
            continue
        try:
            return tipo, str(uuid.UUID(str(valor)))
        except ValueError:
            # Un identificador que no es tal no nombra ningún sujeto; los
            # argumentos quedan igual en el detalle.
            return None, None
    return None, None


def _auditar(cur: psycopg.Cursor, quien: Solicitante, nombre: str,
             args: dict[str, Any], *, ya_confirmada: bool,
             rechazo: Any = None) -> None:
    """La fila de `audit_log` de una operación que corrió (Constitución §12).

    El actor es quien la pidió. Si la persona la confirmó (`ya_confirmada`),
    la decidió ella (`persona`); si no, la pidió Leda en su nombre (`leda`),
    como en `agente.py`. Los argumentos y el rechazo pasan por JSON con
    `default=str`, porque una fecha o un identificador también pueden viajar."""
    detalle: dict[str, Any] = {"args": args, "confirmada": ya_confirmada}
    if rechazo is not None:
        detalle["rechazo"] = rechazo
    sujeto_tipo, sujeto_id = _sujeto(args)
    registrar_auditoria(
        cur,
        accion=(f"herramienta_rechazada:{nombre}" if rechazo is not None
                else f"herramienta:{nombre}"),
        workspace_id=quien.workspace_id, actor_app_user_id=quien.app_user_id,
        actor_kind="persona" if ya_confirmada else "leda",
        sujeto_tipo=sujeto_tipo, sujeto_id=sujeto_id,
        detalle=json.loads(json.dumps(detalle, default=str)),
        pack_hash=versiones.pack_hash(cur, quien.workspace_id),
        nucleo_hash=versiones.nucleo_hash())


def _resumen(h: Herramienta, args: dict) -> str:
    detalle = ", ".join(f"{k}: {v}" for k, v in args.items() if v is not None)
    return f"{h.descripcion} ({detalle})"


# ---------------------------------------------------------------------------
# Consulta
# ---------------------------------------------------------------------------

@herramienta(
    "consultar_tareas", "consultar",
    "Lista tareas del equipo. Sin filtros devuelve las del solicitante. Si a una "
    "tarea le pidieron cambios y todavía no se volvió a entregar, trae "
    "`cambios_pedidos` (quién y qué falta): es parte de su estado, decilo.",
    {"responsable": {"type": "string", "description": "nombre de la persona"},
     "estado": {"type": "string", "enum": ["asignada", "en_curso", "bloqueada",
                                           "en_revision", "terminada"]},
     "vencidas": {"type": "boolean"}})
def _consultar_tareas(cur, quien: Solicitante, responsable=None, estado=None,
                      vencidas=False):
    sql = ["""select t.id, t.titulo, t.estado, t.fecha_objetivo, i.nombre,
                     a.slug as area
                from task t
                join integrante i on i.membership_id = t.responsable_membership_id
                join area a on a.id = t.area_id
               where t.workspace_id = %s"""]
    params: list[Any] = [quien.workspace_id]

    if responsable:
        sql.append("and i.nombre ilike %s")
        params.append(f"%{responsable}%")
    elif not estado and not vencidas:
        sql.append("and t.responsable_membership_id = %s")
        params.append(quien.membership_id)
    if estado:
        sql.append("and t.estado = %s")
        params.append(estado)
    if vencidas:
        sql.append("and t.fecha_objetivo < now() "
                   "and t.estado in ('asignada','en_curso','bloqueada')")

    sql.append("order by t.fecha_objetivo nulls last limit 25")
    cur.execute(" ".join(sql), params)
    filas = [dict(f) for f in cur.fetchall()]
    # Lo que la tarea tiene pendiente por un pedido de cambios es parte de su
    # estado real (R4-H8, ADR 0013 regla 3): de la misma fuente que el menú, para
    # que el modelo no diga "sin cambios" de una tarea a la que se los pidieron.
    from .menu_tarea import cambios_pedidos

    for fila in filas:
        if fila["estado"] in ("asignada", "en_curso"):
            linea = cambios_pedidos(cur, fila["id"])
            if linea:
                fila["cambios_pedidos"] = linea
    return filas


@herramienta(
    "consultar_personas", "consultar",
    "Quiénes son del equipo. Con un nombre parcial devuelve todos los que "
    "coinciden. Usala siempre que no estés seguro de a quién se refieren: "
    "nunca respondas de memoria quiénes coinciden con un nombre.",
    {"nombre": {"type": "string",
                "description": "parte del nombre, p. ej. 'Mar'"}})
def _consultar_personas(cur, quien: Solicitante, nombre=None):
    if not nombre:
        cur.execute(
            """select i.nombre, r.nombre as rol, a.nombre as area
                 from integrante i
                 join rol r on r.id = i.rol_id
                 join area a on a.id = i.area_id
                where i.activo order by i.nombre""")
        return [dict(f) for f in cur.fetchall()]

    cur.execute(
        """select i.nombre, r.nombre as rol, a.nombre as area
             from integrante i
             join rol r on r.id = i.rol_id
             join area a on a.id = i.area_id
            where i.activo and i.nombre ilike %s order by i.nombre""",
        (f"%{nombre}%",))
    return [dict(f) for f in cur.fetchall()]


@herramienta(
    "consultar_bloqueos", "consultar",
    "Bloqueos abiertos del equipo, con su antigüedad en días.", {})
def _consultar_bloqueos(cur, quien: Solicitante):
    cur.execute(
        """select b.id, b.causa, b.impacto, t.titulo, i.nombre,
                  extract(day from now() - b.abierto_en)::int as dias
             from blocker b
             join task t on t.id = b.task_id
             join integrante i on i.membership_id = t.responsable_membership_id
            where b.workspace_id = %s and b.resuelto_en is null
            order by b.abierto_en""",
        (quien.workspace_id,))
    return [dict(f) for f in cur.fetchall()]


# ---------------------------------------------------------------------------
# Trabajo
# ---------------------------------------------------------------------------

def _preparar_crear_objetivo(cur, quien: Solicitante, titulo, tipo,
                             padre_id=None, descripcion=None,
                             fecha_objetivo=None):
    padre_titulo = None
    padre_estado = None
    if padre_id:
        cur.execute("select titulo, estado from objective where id = %s",
                   (padre_id,))
        padre = cur.fetchone()
        if not padre:
            return {"error": "el objetivo del que iba a colgar no existe en "
                             "este equipo"}
        padre_titulo, padre_estado = padre["titulo"], padre["estado"]

    cambio = _filas(
        ("Nuevo objetivo", titulo), ("Tipo", tipo),
        ("Cuelga de", f"«{padre_titulo}»" if padre_titulo else None),
        ("Fecha objetivo", fecha_objetivo or None))
    huella = _huella("crear_objetivo", titulo, tipo, padre_id, padre_estado,
                     descripcion, fecha_objetivo)
    return Preparacion(cambio=cambio, huella=huella,
                       hecho=f"Creé el objetivo «{titulo}».")


@herramienta(
    "crear_objetivo", "crear_objetivo",
    "Crea un objetivo. Usalo cuando el trabajo que piden no encaja en ninguno "
    "de los que ya existen. Consultá primero los objetivos actuales.",
    {"titulo": {"type": "string", "requerido": True},
     "tipo": {"type": "string", "requerido": True,
              "enum": ["estrategico", "hito", "operativo"]},
     "padre_id": {"type": "string", "description": "objetivo del que cuelga"},
     "descripcion": {"type": "string"},
     "fecha_objetivo": {"type": "string", "description": "AAAA-MM-DD"}},
    preparar=_preparar_crear_objetivo)
def _crear_objetivo(cur, quien: Solicitante, titulo, tipo, padre_id=None,
                    descripcion=None, fecha_objetivo=None):
    cur.execute(
        """insert into objective (workspace_id, parent_id, tipo, titulo,
                                  descripcion, fecha_objetivo, estado)
           values (%s, %s, %s, %s, %s, %s, 'activo') returning id""",
        (quien.workspace_id, padre_id, tipo, titulo, descripcion, fecha_objetivo))
    oid = cur.fetchone()["id"]
    cur.execute(
        """insert into objective_state_event (objective_id, estado_nuevo,
                                              actor_kind, actor_app_user_id)
           values (%s, 'activo', 'persona', %s)""",
        (oid, quien.app_user_id))
    return {"id": str(oid), "titulo": titulo}


def crear_borrador_tarea(cur, quien: Solicitante, titulo, objetivo_id=None,
                         area_slug=None, responsable=None, fecha_objetivo=None,
                         criterio_aceptacion=None, descripcion=None,
                         responsable_membership_id=None):
    """Internal Unit 1A draft boundary; never exposed as a model tool."""
    verificar(cur, quien, "crear_tarea")
    titulo = normalize_visible_text(titulo)
    descripcion = normalize_visible_text(descripcion) if descripcion else None
    criterio_aceptacion = (normalize_visible_text(criterio_aceptacion)
                           if criterio_aceptacion else None)
    responsible_query = normalize_visible_text(responsable) if responsable else None
    controlled = {
        "title": titulo, "description": descripcion or "",
        "responsible": responsible_query or "",
        "acceptance_criterion": criterio_aceptacion or "",
    }
    for field, value in controlled.items():
        if telegram_utf16_units(value) > USER_FIELD_LIMITS[field]:
            raise Denegado(
                f"El campo {field} debe tener hasta {USER_FIELD_LIMITS[field]} unidades.")
    responsable = responsible_query
    # `responsable_membership_id` no está en el esquema que ve el modelo: lo
    # inyecta la opción que eligió la persona. Un identificador exacto no se
    # vuelve a resolver.
    if responsable and not responsable_membership_id:
        posibles = candidatos(cur, responsable)
        if not posibles:
            # Antes esto insertaba NULL y devolvía la tarea como creada, así
            # que Leda anunciaba una asignación que no existía.
            return {"creada": False,
                    "error": f"No encuentro a nadie que se llame "
                             f"«{responsable}» en el equipo."}
        if len(posibles) > 1:
            raise NecesitaElegir(
                resumen=f"¿A quién le asigno «{titulo}»?",
                campo="responsable_membership_id", opciones=posibles,
                descarta=("responsable",))
        responsable_membership_id = posibles[0][1]

    if responsable_membership_id:
        cur.execute(
            """select aprobador_membership_id, area_id, activo
                 from membership where id = %s""",
            (responsable_membership_id,))
        responsable_actual = cur.fetchone()
        if not responsable_actual or not responsable_actual["activo"]:
            return {"creada": False,
                    "error": "La persona responsable no está activa."}
        propone_propio = str(responsable_membership_id) == str(quien.membership_id)
        asigna_supervisado = (
            str(responsable_actual["aprobador_membership_id"] or "") ==
            str(quien.membership_id))
        if not propone_propio and not asigna_supervisado:
            raise Denegado(
                "Sólo podés proponer trabajo propio o asignar a quien supervisás.")

    cur.execute(
        """select a.id as area_id, p.evidencia_requerida, p.version
             from area a
             left join task_evidence_policy p
               on p.workspace_id = a.workspace_id and p.area_id = a.id
            where a.workspace_id = %s and a.slug = %s""",
        (quien.workspace_id, area_slug))
    politica = cur.fetchone()
    area_id = politica["area_id"] if politica else None
    evidencia = politica["evidencia_requerida"] if politica else None
    policy_version = politica["version"] if politica else None
    if evidencia is not None:
        evidence_units = [telegram_utf16_units(normalize_visible_text(item))
                          for item in evidencia]
        if (len(evidencia) > EVIDENCE_COUNT_LIMIT
                or any(units > EVIDENCE_ITEM_LIMIT for units in evidence_units)
                or sum(evidence_units) > EVIDENCE_TOTAL_LIMIT):
            registrar_incidente(
                cur, quien.workspace_id,
                "La política de evidencia excede el contrato visible.",
                etapa=ETAPA_EVIDENCIA_INVALIDA, app_user_id=quien.app_user_id)
            raise Denegado(
                "No puedo mostrar una opción configurada de este espacio. "
                "Pedile a quien lo administra que la revise.")
    if responsable_membership_id and str(responsable_actual["area_id"]) != str(area_id):
        raise Denegado("La persona responsable no pertenece al área de la tarea.")

    objetivo_snapshot = None
    if objetivo_id:
        cur.execute(
            """select jsonb_build_object('id', id, 'titulo', titulo,
                                          'estado', estado) as snapshot
                 from objective where id = %s""", (objetivo_id,))
        objetivo = cur.fetchone()
        objetivo_snapshot = objetivo["snapshot"] if objetivo else None

    cur.execute(
        """insert into task_draft
             (workspace_id, creado_por_membership_id, objective_id,
              objective_snapshot, titulo, descripcion, area_id,
              responsable_membership_id, fecha_objetivo,
              criterio_aceptacion, evidencia_requerida,
              evidencia_policy_version)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           returning id, version""",
        (quien.workspace_id, quien.membership_id, objetivo_id,
         Jsonb(objetivo_snapshot) if objetivo_snapshot is not None else None,
         titulo, descripcion, area_id,
         responsable_membership_id, fecha_objetivo, criterio_aceptacion,
         evidencia, policy_version))
    borrador = cur.fetchone()

    faltantes = []
    if objetivo_snapshot is None:
        faltantes.append("objetivo_id")
    if responsable_membership_id is None:
        faltantes.append("responsable")
    if fecha_objetivo is None:
        faltantes.append("fecha_objetivo")
    if not criterio_aceptacion or not criterio_aceptacion.strip():
        faltantes.append("criterio_aceptacion")
    if evidencia is None:
        faltantes.append("politica_evidencia")
    if faltantes:
        return {"draft_id": str(borrador["id"]), "completa": False,
                "faltantes": faltantes}

    cur.execute(
        """select m.aprobador_membership_id,
                  aprobador.app_user_id, aprobador.telegram_user_id,
                  aprobador.nombre
             from membership m
             left join integrante aprobador
               on aprobador.membership_id = m.aprobador_membership_id
            where m.id = %s""", (responsable_membership_id,))
    autoridad = cur.fetchone()
    aprobador_id = autoridad["aprobador_membership_id"] if autoridad else None
    if aprobador_id is None:
        cur.execute(
            """select i.membership_id as aprobador_membership_id,
                      i.app_user_id, i.telegram_user_id, i.nombre
                 from integrante i join rol r on r.id = i.rol_id
                where r.autoridad_final and i.activo""")
        autoridad = cur.fetchone()
        aprobador_id = autoridad["aprobador_membership_id"] if autoridad else None
    if autoridad is None or aprobador_id is None or autoridad["telegram_user_id"] is None:
        return {"draft_id": str(borrador["id"]), "completa": True,
                "pendiente_revision": True, "notificada": False}

    cur.execute(
        """select jsonb_build_object(
                 'draft_id', id::text, 'version', version,
                  'titulo', titulo, 'descripcion', descripcion,
                  'objetivo', objective_snapshot,
                 'area_id', area_id::text,
                 'responsable_membership_id', responsable_membership_id::text,
                 'fecha_objetivo', fecha_objetivo::text,
                 'criterio_aceptacion', criterio_aceptacion,
                 'evidencia_requerida', to_jsonb(evidencia_requerida),
                 'evidencia_policy_version', evidencia_policy_version
               ) as preview
             from task_draft where id = %s""", (borrador["id"],))
    preview = cur.fetchone()["preview"]
    resumen = (f"Confirmar tarea: {titulo}. Fecha: {fecha_objetivo}. "
               f"Criterio: {criterio_aceptacion}. Evidencia: "
               f"{', '.join(evidencia) if evidencia else 'ninguna' }.")

    from .autoridad import Canal
    from .pendientes import registrar

    confirmador = Solicitante(
        app_user_id=str(autoridad["app_user_id"]), canal=Canal.ESPACIO,
        workspace_id=quien.workspace_id, membership_id=str(aprobador_id))
    ahora = datetime.now(timezone.utc)
    pendiente = registrar(
        cur, confirmador, herramienta="confirmar_borrador_tarea", args={},
        resumen=resumen, vence_en=ahora + timedelta(hours=8),
        chat_id=autoridad["telegram_user_id"], draft_id=str(borrador["id"]),
        draft_version=borrador["version"], preview=preview)
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id,
        chat_id=autoridad["telegram_user_id"], text=resumen,
        recipient_membership_id=str(aprobador_id), scheduled_for=ahora,
        dedupe_key=(f"{quien.workspace_id}:draft-preview:{borrador['id']}:"
                    f"{borrador['version']}"), pending_action_id=pendiente.id,
        es_coordinacion=True,
    )
    return {"draft_id": str(borrador["id"]), "completa": True,
            "pendiente_revision": True, "notificada": True,
            "pending_action_id": pendiente.id}


_MOTIVO_FALTA_EVIDENCIA_ENTREGA = (
    "Falta la evidencia requerida. Contame brevemente qué hiciste o pasame "
    "un link.")
# El motivo tipado del mismo rechazo (R4-H3): quien lo consume decide por este
# valor y nunca por el texto, que es para el modelo.
FALTA_EVIDENCIA_DE_ENTREGA = "evidencia_de_entrega"


def _falta_evidencia_de_entrega(faltan: list[str] | None = None) -> dict:
    """El rechazo de pasar una tarea a revisión sin la evidencia que exige su
    política (ADR 0009): `en_revision` no ocurrió y `falta_tipo` dice por qué.
    `faltan`, si se sabe, son los tipos de la política que quedan sin cubrir
    (ADR 0019, decisión 5)."""
    return {"en_revision": False, "falta": _MOTIVO_FALTA_EVIDENCIA_ENTREGA,
            "falta_tipo": FALTA_EVIDENCIA_DE_ENTREGA,
            **({"faltan": list(faltan)} if faltan else {})}


# --- Las piezas de evidencia (ADR 0019, decisiones 3 y 5; migración 0034) ---------
#
# La clase de cada pieza la fija el código por el contenido, nunca la IA: un texto
# que es un enlace (y nada más) es `enlace`; otro texto, `texto`; un archivo guardado
# es `imagen` si su contenido es una imagen y `archivo` si no (la base lo comprueba
# contra `archivo.clase`). Lo que cubre cada pieza son tipos de la política que esa
# clase acepta: `tipos_que_acepta_la_clase`, en la base.

_ENLACE = re.compile(r"^https?://\S+$", re.IGNORECASE)


def clase_de_un_texto(texto: str) -> str:
    """`enlace` si el texto es un enlace y nada más; si no, `texto`."""
    return "enlace" if _ENLACE.match(texto.strip()) else "texto"


def _tipos_que_acepta(cur, tarea_id, clase: str) -> list[str]:
    cur.execute("select tipos_que_acepta_la_clase(%s, %s) as t", (tarea_id, clase))
    return list(cur.fetchone()["t"] or [])


def _tipos_que_faltan(cur, tarea_id, piezas: list[dict] | None = None) -> list[str]:
    """Los tipos de la política de la tarea que quedan sin cubrir con la evidencia
    vigente y, si se pasan, con estas piezas todavía sin escribir (cada una con su
    `clase` y su `cubre`). La regla vive en la base: `tipos_de_evidencia_que_faltan`."""
    cur.execute("select tipos_de_evidencia_que_faltan(%s, %s) as t",
                (tarea_id, Jsonb([{"clase": p["clase"], "cubre": list(p["cubre"])}
                                  for p in piezas or []])))
    return list(cur.fetchone()["t"] or [])


def _insertar_evidencia(cur, quien: Solicitante, tarea_id, pieza: dict) -> str:
    """Una fila de `evidence` para una pieza ya resuelta (`clase`, `cubre` y su
    contenido: `texto`, `uri` o `archivo_id`). `tipo` es igual a la clase."""
    # T6f (seguimiento del orquestador): `at` explícito con `clock_timestamp()` --
    # ver el comentario de `_bloquear_tarea`.
    cur.execute(
        """insert into evidence (workspace_id, task_id, tipo, clase, texto, uri,
                                 archivo_id, cubre, entregado_por, at)
           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, clock_timestamp())
           returning id""",
        (quien.workspace_id, tarea_id, pieza["clase"], pieza["clase"],
         pieza.get("texto"), pieza.get("uri"), pieza.get("archivo_id"),
         list(pieza["cubre"]), quien.membership_id))
    return str(cur.fetchone()["id"])


def _pieza_de_texto(cur, tarea_id, texto: str | None,
                    cubre: list[str] | None = None) -> dict:
    """Un texto como pieza: su clase por el contenido y, si no se dice qué cubre, todos
    los tipos de la tarea que esa clase acepta (la entrega de antes de la porción 2,
    con su vista previa de la cocina, `_preparar_actualizar_estado`). Sin texto, una
    pieza `texto` vacía, como la que guardaba `adjuntar_evidencia` sin detalle."""
    texto = (texto or "").strip()
    clase = clase_de_un_texto(texto)
    aceptados = _tipos_que_acepta(cur, tarea_id, clase)
    cubre = aceptados if cubre is None else [t for t in aceptados if t in cubre]
    contenido = {"uri": texto} if clase == "enlace" else {"texto": texto or None}
    return {"clase": clase, "cubre": cubre, **contenido}


# T6g (`odd/tasks/leda-orienta.md`; review-e719d807, review-09452c69):
# decisión del usuario (2026-09-27) -- "ya la terminé" sobre una tarea que YA
# está en_revision no es una segunda entrega, así que no hay un segundo
# `falta` que devolver: la tarea ya tiene lo que este pedido pretendía lograr.
_AVISO_YA_EN_REVISION = "Esa tarea ya está en revisión."
_AVISO_EVIDENCIA_SUMADA_EN_REVISION = (
    "Esa tarea ya está en revisión; se sumó la evidencia para quien la "
    "revisa.")


def _bloquear_tarea(cur, tarea_id) -> None:
    """T6f (`odd/tasks/leda-orienta.md`; review-3cf89bef, review-ae0ab510):
    serializa los actos que deciden o avisan sobre una misma tarea --
    "Aprobar" y "Pedir cambios" simultáneos, o dos evidencias simultáneas
    sobre una tarea `en_revision` -- para que el segundo espere a que el
    primero termine y recién ahí lea el estado, ya actualizado, en vez de
    decidir con una lectura tomada bajo `READ COMMITTED` antes de que el otro
    termine (dos avisos esperando al aprobador, uno con evidencia vieja; un
    "aprobado" contado después de un "rechazado" posterior).

    `select ... for update`/`for no key update` sobre `task` exige el
    privilegio `update` (o `delete`/`truncate`) en PostgreSQL, y `leda_app`
    sólo tiene `select` ahí (`db/esquema.sql`: "Committed tasks are created
    only by confirmar_borrador_tarea()", `revoke update, delete on task from
    leda_app`) -- verificado contra el esquema real:
    `psycopg.errors.InsufficientPrivilege: permission denied for table task`
    con las dos formas. Un advisory lock no depende de ningún privilegio
    sobre la tabla -- mismo mecanismo y misma forma de clave
    (`hashtextextended`, semilla 0) que ya usa `ingreso_tareas.start` para su
    propio borrador/chat. Alcance de transacción (`_xact_`): se libera solo
    al terminar -- commit o rollback --, nunca hace falta soltarlo a mano.

    Se llama al principio de cada handler que decide o notifica sobre la
    tarea (`_actualizar_estado`, `_adjuntar_evidencia`, `_aprobar_tarea`,
    `_pedir_cambios_tarea`), antes de la primera lectura de `task` -- nunca en
    `_preparar_*`: esas funciones sólo arman la vista previa (no escriben
    nada) y el handler ya vuelve a leer todo por su cuenta como la puerta
    real a la base, tomado el lock; una `preparar` sin confirmar nunca llega
    al handler.

    El lock por sí solo NO alcanza (corrección del orquestador tras revisar
    T6f): serializa el ORDEN DE EJECUCIÓN, pero -- hasta T6j
    (`odd/tasks/leda-orienta.md`) -- `approval.at`, `evidence.at` y
    `task_state_event.at` (`db/esquema.sql`) tenían `default now()`, que en
    PostgreSQL es la hora de INICIO de la transacción, no la del `insert`. En
    el gateway la transacción arranca mucho antes de llegar acá -- ruteo,
    llamada al modelo, fase 2 --, así que la transacción B puede haber
    arrancado antes que A, quedar esperando el lock, y terminar insertando su
    'rechazado' con un `at` ANTERIOR al 'aprobado' de A aunque A escribió
    primero. `motivo_no_cierra_tarea` (un 'rechazado' sólo cancela un
    'aprobado' con `r.at >= a.at`) y `evidencia_pendiente` (evidencia sólo
    cuenta con `e.at > último rechazado.at`) -- y, por la misma razón,
    `estado_previo_a_bloqueo`/`estado_previo_a_revision`, que ordenan
    `task_state_event` por `at desc` -- juzgarían mal con esa hora de
    arranque.

    T6j cambió el `default` de las tres columnas a `clock_timestamp()`
    (migración `0016`, `db/esquema.sql`) para que ese orden valga para
    cualquier escritor, no sólo para estos cuatro handlers -- el defecto no
    era exclusivo de ellos, cualquier otra transacción que insertara en
    `approval`, `evidence` o `task_state_event` bajo carga estaba expuesta
    igual. Cada `insert` de estos cuatro handlers sigue fijando `at =
    clock_timestamp()` de forma explícita: ya es redundante con el nuevo
    default, pero queda -- en vez de sacarlo para no duplicar -- porque es
    justo en el punto donde el lock se tomó y el orden importa de verdad, y
    documenta ahí por qué (sin depender de que quien lea este comentario
    también haya visto el de la migración `0016`, ni de que el default de la
    columna no cambie de nuevo sin que alguien note esto)."""
    cur.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
               (f"task:{tarea_id}",))


def _preparar_actualizar_estado(cur, quien: Solicitante, tarea_id, estado,
                                motivo=None, evidencia_texto=None):
    cur.execute(
        "select titulo, estado, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if str(fila["responsable_membership_id"]) != str(quien.membership_id):
        # T2b (revisión de `0814fa3`): sin este chequeo, cualquier
        # integrante autenticado del espacio podía mover el estado de
        # CUALQUIER tarea, no sólo la propia. `nucleo/constitucion.md` §3:
        # "la persona responsable informa hechos como inicio, bloqueo,
        # resolución y entrega"; los referentes "aprueban o rechazan el
        # trabajo entregado. No persiguen avances ni administran estados
        # intermedios" -- el menú (T2) ya sólo ofrece estas transiciones a
        # la relación "responsable" (`menu_tarea.calcular_menu`); esto lo
        # exige también del lado de la herramienta, para quien escriba
        # texto libre en vez de tocar un botón.
        raise Denegado("No podés cambiar el estado de una tarea que no es tuya.")

    if estado == "terminada":
        cur.execute("select motivo_no_cierra_tarea(%s) as m", (tarea_id,))
        impedimento = cur.fetchone()["m"]
        if impedimento:
            return {"cerrada": False, "falta": impedimento}

    if estado == "en_revision":
        if fila["estado"] == "en_revision":
            # T6g (`odd/tasks/leda-orienta.md`; review-e719d807,
            # review-09452c69): decisión del usuario (2026-09-27) -- una
            # entrega repetida sobre una tarea que YA está en_revision no
            # registra ningún evento de estado (nunca un
            # `en_revision -> en_revision`): ese evento hacía que
            # `estado_previo_a_revision` devolviera `en_revision` en vez del
            # estado real anterior, y "Pedir cambios" mandaba a `asignada`
            # una tarea que en realidad estaba `en_curso` (review-09452c69,
            # WARNING). Mismo criterio que `_registrar_bloqueo` con
            # `bloqueada -> bloqueada`: no hay una segunda transición al
            # mismo estado que registrar -- lo que llega de nuevo es
            # evidencia, no un cambio de estado, y se suma igual que
            # "Adjuntar evidencia" (`_preparar_adjuntar_evidencia`).
            evidencia_texto = (evidencia_texto or "").strip()
            if not evidencia_texto:
                return {"error": _AVISO_YA_EN_REVISION}
            cambio = _filas(
                ("Tarea", fila["titulo"]),
                (None, "Ya está en revisión: se suma la evidencia para quien "
                       "la revisa."),
                ("Evidencia", evidencia_texto))
            huella = _huella("actualizar_estado_evidencia_en_revision",
                             tarea_id, evidencia_texto)
            return Preparacion(
                cambio=cambio, huella=huella,
                hecho=f"Sumé la evidencia a «{fila['titulo']}» para quien la revisa.")

        # ADR 0009 (hallazgo 8, sesión 2 por Telegram, 2026-09-27): Ariel
        # tocó "Ya la terminé" y la tarea pasó a `en_revision` sin ninguna
        # evidencia, aunque su política la exige -- Ismael después aprobó a
        # ciegas. Sin evidencia y sin que la persona la haya mandado en este
        # mismo pedido, se devuelve un `falta` verdadero y nunca se mueve la
        # tarea (constitución §4: nunca se da por entregado lo que nadie
        # entregó).
        #
        # ADR 0019, decisión 5 (migración 0034): la política se cumple por tipo, así que el
        # texto que llega en el mismo pedido cuenta sólo para los tipos que un texto cubre:
        # una frase sola no cubre una foto.
        texto = (evidencia_texto or "").strip()
        faltan = _tipos_que_faltan(
            cur, tarea_id, [_pieza_de_texto(cur, tarea_id, texto)] if texto else [])
        if faltan:
            return _falta_evidencia_de_entrega(faltan)

    if estado == "en_curso":
        restaura_en_curso = False
        if fila["estado"] == "bloqueada":
            cur.execute("select estado_previo_a_bloqueo(%s) as previo", (tarea_id,))
            restaura_en_curso = cur.fetchone()["previo"] == "en_curso"
        elif fila["estado"] == "en_revision":
            # T6c (`odd/tasks/leda-orienta.md`): mismo criterio que la
            # rama de `bloqueada`, ahora también para la restauración que
            # hace `pedir_cambios_tarea` -- consistente con el disparador
            # `exigir_dependencias_resueltas` (`db/esquema.sql`). Sin esta
            # rama, este chequeo proactivo devolvería un `falta` que la base
            # no rechazaría.
            cur.execute("select estado_previo_a_revision(%s) as previo", (tarea_id,))
            restaura_en_curso = cur.fetchone()["previo"] == "en_curso"
        if not restaura_en_curso:
            cur.execute("select motivo_no_arranca_tarea(%s) as m", (tarea_id,))
            impedimento = cur.fetchone()["m"]
            if impedimento:
                return {"iniciada": False, "falta": impedimento}

    cambio = _filas(
        ("Tarea", fila["titulo"]),
        ("Estado actual", _estado_legible(fila["estado"])),
        ("Nuevo estado", _estado_legible(estado)),
        ("Evidencia", (evidencia_texto or "").strip()
         if estado == "en_revision" and evidencia_texto else None))
    huella = _huella("actualizar_estado", tarea_id, fila["estado"], estado,
                     evidencia_texto)
    return Preparacion(cambio=cambio, huella=huella,
                       hecho=recibo_de_estado(fila["titulo"], estado))


@herramienta(
    "actualizar_estado", "actualizar_estado",
    "Mueve una tarea de estado. No cierra: para terminar hace falta que se "
    "cumplan las condiciones de cierre y estén las aprobaciones. Para pasar "
    "a en_revision, si la tarea exige evidencia y todavía no tiene, hay que "
    "mandar evidencia_texto en el mismo pedido.",
    {"tarea_id": {"type": "string", "requerido": True},
     "estado": {"type": "string", "requerido": True,
                "enum": ["asignada", "en_curso", "en_revision", "terminada",
                         "cancelada"]},
     "motivo": {"type": "string"},
     "evidencia_texto": {"type": "string"}},
    preparar=_preparar_actualizar_estado)
def _actualizar_estado(cur, quien: Solicitante, tarea_id, estado, motivo=None,
                       evidencia_texto=None):
    # T6f: serializa contra cualquier otro acto sobre esta misma tarea
    # (`_bloquear_tarea`) antes de la primera lectura, para decidir siempre
    # con el estado más nuevo.
    _bloquear_tarea(cur, tarea_id)
    cur.execute(
        "select estado, titulo, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if str(fila["responsable_membership_id"]) != str(quien.membership_id):
        # Misma regla que `_preparar_actualizar_estado`, repetida acá porque
        # el handler también se llama solo (herramientas sin `preparar` no
        # existen para esta acción, pero el handler es la puerta real a la
        # base: la autoridad se verifica en las dos, igual que
        # `_resolver_bloqueo`/`_aprobar_tarea`).
        raise Denegado("No podés cambiar el estado de una tarea que no es tuya.")

    if estado == "terminada":
        cur.execute("select motivo_no_cierra_tarea(%s) as m", (tarea_id,))
        impedimento = cur.fetchone()["m"]
        if impedimento:
            # No es un error: es información que Leda tiene que transmitir.
            return {"cerrada": False, "falta": impedimento}

    evidencia_id = None
    if estado == "en_revision":
        if fila["estado"] == "en_revision":
            # T6g: mismo criterio que `_preparar_actualizar_estado`,
            # repetido acá por el mismo motivo que la autoridad de arriba
            # (el handler es la puerta real a la base). Sin evento de
            # estado: la evidencia que llegue se suma sola, igual que
            # `_adjuntar_evidencia`.
            evidencia_texto = (evidencia_texto or "").strip()
            if not evidencia_texto:
                return {"error": _AVISO_YA_EN_REVISION}
            evidencia_id = _insertar_evidencia(
                cur, quien, tarea_id, _pieza_de_texto(cur, tarea_id, evidencia_texto))
            # T6i (ADR 0009, enmienda 2026-09-27): esta entrega repetida es
            # evidencia nueva sobre una tarea ya en_revision -- si viene de
            # alguien que no es el aprobador, retira el aviso que tiene
            # esperando y manda uno nuevo con toda la evidencia vigente.
            _avisar_evidencia_nueva_en_revision(
                cur, quien, tarea_id, fila["titulo"],
                fila["responsable_membership_id"], evidencia_id,
                datetime.now(timezone.utc))
            return {"evidencia_id": str(evidencia_id),
                   "aviso": _AVISO_EVIDENCIA_SUMADA_EN_REVISION}

        # Repetido acá por el mismo motivo que la autoridad de arriba: el
        # handler es la puerta real a la base, no depende de que `preparar`
        # haya corrido antes con los mismos argumentos.
        # ADR 0019, decisión 5: con la regla por tipo, igual que `_preparar_actualizar_estado`.
        evidencia_texto = (evidencia_texto or "").strip()
        pieza = _pieza_de_texto(cur, tarea_id, evidencia_texto) if evidencia_texto else None
        faltan = _tipos_que_faltan(cur, tarea_id, [pieza] if pieza else [])
        if faltan:
            return _falta_evidencia_de_entrega(faltan)
        if pieza is not None:
            # T6b (`odd/tasks/leda-orienta.md`, decisión del usuario
            # 2026-09-27): antes, este insert corría sólo cuando
            # `evidencia_pendiente` era verdadero -- si la tarea ya tenía
            # alguna fila de `evidence` (por ejemplo de una entrega
            # anterior a "Pedir cambios"), el `evidencia_texto` nuevo se
            # descartaba en silencio, aunque la vista previa
            # (`_preparar_actualizar_estado`) y el aviso al aprobador
            # (`_notificar_entrega_al_aprobador`, abajo) ya lo mostraban.
            # Ahora se registra siempre que llegue texto: dos hechos, dos
            # filas, un solo acto -- mismo patrón que `_aprobar_tarea`
            # (ADR 0008).
            evidencia_id = _insertar_evidencia(cur, quien, tarea_id, pieza)

    if estado == "en_curso":
        # Chequeo proactivo, igual que el de arriba: sin esto, el disparador
        # `trg_exigir_dependencias_resueltas` igual frena el insert, pero como
        # un error de base -- acá se convierte en información antes de
        # intentarlo (mecánica §4).
        #
        # Corrección tras revisión: si la tarea está `bloqueada`, este mismo
        # `actualizar_estado` puede recibir la transición de vuelta -- la
        # herramienta no exige bloqueos cerrados para salir de `bloqueada`
        # (deuda conocida) --, y volver de un bloqueo es una restauración,
        # no un arranque (mecánica §3).
        #
        # Segunda corrección tras revisión: no alcanza con mirar el estado
        # actual. `asignada` -> `registrar_bloqueo` -> `bloqueada` ->
        # `actualizar_estado(en_curso)` también tiene `fila["estado"] ==
        # "bloqueada"`, y esa tarea nunca arrancó -- eximirla ahí habría
        # dejado pasar justo lo que mecánica §4 prohíbe. La restauración
        # legítima exige además que el estado previo a la ÚLTIMA entrada a
        # `bloqueada` haya sido `en_curso`, igual que el disparador.
        #
        # T6c (`odd/tasks/leda-orienta.md`): mismo criterio para la rama
        # `en_revision` -- repetido acá por el mismo motivo que el resto de
        # este chequeo proactivo (el handler es la puerta real a la base,
        # no depende de que `_preparar_actualizar_estado` haya corrido
        # antes con los mismos argumentos).
        restaura_en_curso = False
        if fila["estado"] == "bloqueada":
            cur.execute("select estado_previo_a_bloqueo(%s) as previo", (tarea_id,))
            restaura_en_curso = cur.fetchone()["previo"] == "en_curso"
        elif fila["estado"] == "en_revision":
            cur.execute("select estado_previo_a_revision(%s) as previo", (tarea_id,))
            restaura_en_curso = cur.fetchone()["previo"] == "en_curso"
        if not restaura_en_curso:
            cur.execute("select motivo_no_arranca_tarea(%s) as m", (tarea_id,))
            impedimento = cur.fetchone()["m"]
            if impedimento:
                return {"iniciada": False, "falta": impedimento}

    # Sin `returning`: `leda_app` sólo tiene `insert` sobre
    # `task_state_event` (es append-only, ver el `revoke` en
    # `db/esquema.sql`), y `returning` exige además `select`. El token de
    # deduplicación se genera acá, no se lee de la fila insertada.
    #
    # T6f (seguimiento del orquestador): `at` explícito con
    # `clock_timestamp()` -- ver el comentario de `_bloquear_tarea`.
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, actor_app_user_id, motivo, at)
           values (%s, %s, %s, 'persona', %s, %s, clock_timestamp())""",
        (tarea_id, fila["estado"], estado, quien.app_user_id, motivo))
    _avisar_dependencia_informativa(cur, quien, tarea_id, estado, uuid.uuid4())

    if estado == "en_revision":
        # ADR 0009, decisión 3: quien aprueba se entera de la entrega con
        # botones -- no sólo el responsable con un aviso de texto -- para
        # que "Aprobar" y "Pedir cambios" salgan de ese mismo mensaje.
        cur.execute(
            "select aprobador_membership_id from membership where id = %s",
            (fila["responsable_membership_id"],))
        aprob = cur.fetchone()
        aprobador_membership_id = aprob["aprobador_membership_id"] if aprob else None
        if aprobador_membership_id:
            # T6d (`odd/tasks/leda-orienta.md`): antes, sin evidencia nueva
            # (política sin evidencia requerida, o entrega sin texto nuevo),
            # esto era `uuid.uuid4()` -- una clave al azar en cada ejecución.
            # Con evidencia nueva, `evidencia_id` ya es un id real de la fila
            # que se acaba de insertar y sigue siendo la ancla (mismo patrón
            # que `aprobacion_id` en `_aprobar_tarea`, revisión ec6f7d80). Sin
            # ella no hay ninguna fila nueva para anclar -- `leda_app`
            # tampoco puede leer el id de `task_state_event` recién insertado
            # (ver el comentario de arriba).
            #
            # La clave NO puede salir de los hechos de la vista previa (tarea,
            # estado de origen, texto): entrega -> "Pedir cambios" ->
            # reentrega sin evidencia repite esos hechos, y como
            # `message_outbox.dedupe_key` es `unique` para siempre, la
            # segunda entrega quedaría sin avisar, en silencio, con los
            # botones "Aprobar"/"Pedir cambios" registrados para un mensaje
            # que nunca sale.
            #
            # La identidad estable de un acto -- sin depender de una fila que
            # esta vez no existe -- es la transacción que lo ejecuta:
            # `pg_current_xact_id()` (PostgreSQL 13+; verificado como
            # `leda_app`, sin grants extra, contra el Postgres 18 de
            # `docker-compose.yml`/desarrollo) es la misma para cualquier
            # llamada dentro de esta misma transacción y distinta de la de
            # cualquier otra transacción, sin repetirse nunca en el clúster.
            # Junto con `tarea_id` alcanza para no colisionar entre tareas.
            # Esto sólo cubre una repetición DENTRO de esta misma transacción
            # (p. ej. este mismo código invocado dos veces sin haber hecho
            # commit); una repetición del mismo acto entre transacciones
            # distintas (un reintento, una entrega de Telegram duplicada) no
            # es responsabilidad de esta clave -- ya la cubre una capa
            # anterior: la `pending_action` confirmada se ejecuta una sola
            # vez (`pendientes.resolver` la marca resuelta antes de que
            # `ejecutar` corra el handler) y el recibo del update entrante de
            # Telegram es igual de acotado. Esta clave nunca tiene que
            # resolver esa otra garantía.
            #
            # T6h (seguimiento de review-6b1efba1): `pg_current_xact_id()`
            # sólo hace falta acá, sin evidencia nueva -- con `evidencia_id`
            # ya hay un ancla real y consultar la transacción sería una
            # vuelta a la base de más en el camino más común (evidencia
            # nueva en cada entrega).
            if evidencia_id:
                dedupe_id = evidencia_id
            else:
                cur.execute("select pg_current_xact_id()::text as x")
                xact = cur.fetchone()["x"]
                dedupe_id = f"{tarea_id}:{xact}"
            _notificar_entrega_al_aprobador(
                cur, quien, tarea_id, fila["titulo"],
                aprobador_membership_id, dedupe_id,
                datetime.now(timezone.utc))

    return {"estado": estado}


def _preparar_registrar_bloqueo(cur, quien: Solicitante, tarea_id, causa,
                                impacto=None):
    cur.execute(
        "select titulo, estado, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if str(fila["responsable_membership_id"]) != str(quien.membership_id):
        # T2b: mecánica §8 describe la gestión de un bloqueo que "alguien
        # declara" sobre su propio trabajo, y constitución §3 lo atribuye a
        # "la persona responsable" como un hecho que informa. El menú (T2)
        # ya sólo ofrece "Informar un bloqueo" a la relación "responsable".
        raise Denegado("No podés declarar un bloqueo en una tarea que no es tuya.")
    if fila["estado"] in ("terminada", "cancelada"):
        return {"error": "esa tarea ya está cerrada, no se le puede agregar un bloqueo"}

    ya_bloqueada = fila["estado"] == "bloqueada"
    cambio = _filas(
        ("Tarea", fila["titulo"]), ("Causa del bloqueo", causa),
        ("Impacto", impacto or None),
        ("Estado actual", _estado_legible(fila["estado"])),
        (None, "Se suma a los bloqueos abiertos; la tarea sigue bloqueada."
         if ya_bloqueada else None),
        ("Nuevo estado", None if ya_bloqueada else _estado_legible("bloqueada")))
    hecho = (f"Registré el bloqueo en «{fila['titulo']}»: "
             + ("se suma a los bloqueos abiertos y la tarea sigue bloqueada."
                if ya_bloqueada else "la tarea quedó bloqueada."))
    huella = _huella("registrar_bloqueo", tarea_id, fila["estado"])
    return Preparacion(cambio=cambio, huella=huella, hecho=hecho)


@herramienta(
    "registrar_bloqueo", "registrar_bloqueo",
    "Registra que una tarea está trabada por una causa externa al equipo -- "
    "algo que falta, una persona fuera del equipo, un permiso -- con su "
    "causa e impacto. Si lo que la frena es otra tarea del equipo, no es un "
    "bloqueo: usá crear_dependencia.",
    {"tarea_id": {"type": "string", "requerido": True},
     "causa": {"type": "string", "requerido": True},
     "impacto": {"type": "string"}},
    preparar=_preparar_registrar_bloqueo)
def _registrar_bloqueo(cur, quien: Solicitante, tarea_id, causa, impacto=None):
    cur.execute(
        "select estado, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if str(fila["responsable_membership_id"]) != str(quien.membership_id):
        raise Denegado("No podés declarar un bloqueo en una tarea que no es tuya.")
    if fila["estado"] in ("terminada", "cancelada"):
        return {"error": "esa tarea ya está cerrada, no se le puede agregar un bloqueo"}

    cur.execute(
        """insert into blocker (workspace_id, task_id, causa, impacto, abierto_por)
           values (%s, %s, %s, %s, %s) returning id""",
        (quien.workspace_id, tarea_id, causa, impacto, quien.membership_id))
    bid = cur.fetchone()["id"]

    # Si ya estaba bloqueada, el bloqueo se suma a los que tiene: no hay una
    # segunda transición `bloqueada -> bloqueada` que registrar.
    if fila["estado"] != "bloqueada":
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind, actor_app_user_id, motivo)
               values (%s, %s, 'bloqueada', 'persona', %s, %s)""",
            (tarea_id, fila["estado"], quien.app_user_id, causa))
        _avisar_dependencia_informativa(cur, quien, tarea_id, "bloqueada", uuid.uuid4())
    return {"bloqueo_id": str(bid)}


def _preparar_resolver_bloqueo(cur, quien: Solicitante, bloqueo_id, resolucion):
    resolucion = (resolucion or "").strip()
    if not resolucion:
        raise Denegado("Hace falta contar cómo se resolvió para poder cerrarlo.")

    cur.execute(
        """select b.causa, b.task_id, b.resuelto_en, b.abierto_por, b.escalado_a,
                  t.titulo, t.estado, t.responsable_membership_id
             from blocker b join task t on t.id = b.task_id
            where b.id = %s""",
        (bloqueo_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "ese bloqueo no existe en este equipo"}
    if fila["resuelto_en"] is not None:
        return {"error": "ese bloqueo ya estaba resuelto"}

    autorizados = {str(m) for m in (fila["responsable_membership_id"],
                                    fila["abierto_por"], fila["escalado_a"])
                  if m is not None}
    if str(quien.membership_id) not in autorizados:
        raise Denegado(
            "No podés resolver ese bloqueo: no es tuyo, no lo abriste vos ni "
            "se te escaló.")

    vuelve_a = None
    quedan_abiertos = None
    if fila["estado"] == "bloqueada":
        cur.execute(
            """select count(*) n from blocker
                where task_id = %s and resuelto_en is null and id <> %s""",
            (fila["task_id"], bloqueo_id))
        quedan_abiertos = cur.fetchone()["n"] > 0
        if not quedan_abiertos:
            cur.execute("select estado_previo_a_bloqueo(%s) as previo",
                       (fila["task_id"],))
            vuelve_a = cur.fetchone()["previo"]

    sigue_bloqueada = not vuelve_a and fila["estado"] == "bloqueada"
    cambio = _filas(
        ("Tarea", fila["titulo"]), ("Bloqueo", fila["causa"]),
        ("Resolución", resolucion),
        (None, f"La tarea vuelve a {_estar(vuelve_a)}." if vuelve_a else None),
        (None, "La tarea sigue bloqueada: hay otros bloqueos abiertos."
         if sigue_bloqueada else None))
    base = f"Resolví el bloqueo de «{fila['titulo']}»"
    if vuelve_a:
        hecho = f"{base}: la tarea volvió a {_estar(vuelve_a)}."
    elif sigue_bloqueada:
        hecho = f"{base}. La tarea sigue bloqueada: quedan otros bloqueos abiertos."
    else:
        hecho = f"{base}."
    huella = _huella("resolver_bloqueo", bloqueo_id, fila["resuelto_en"],
                     fila["estado"], quedan_abiertos)
    return Preparacion(cambio=cambio, huella=huella, hecho=hecho)


@herramienta(
    "resolver_bloqueo", "resolver_bloqueo",
    "Cierra un bloqueo con su resolución. Cuando era el último abierto de la "
    "tarea, la tarea vuelve al estado que tenía antes de bloquearse.",
    {"bloqueo_id": {"type": "string", "requerido": True},
     "resolucion": {"type": "string", "requerido": True}},
    valida_en_handler=True, preparar=_preparar_resolver_bloqueo)
def _resolver_bloqueo(cur, quien: Solicitante, bloqueo_id, resolucion):
    resolucion = (resolucion or "").strip()
    if not resolucion:
        raise Denegado("Hace falta contar cómo se resolvió para poder cerrarlo.")

    cur.execute(
        """select b.task_id, b.resuelto_en, b.abierto_por, b.escalado_a,
                  t.responsable_membership_id
             from blocker b join task t on t.id = b.task_id
            where b.id = %s""",
        (bloqueo_id,))
    fila = cur.fetchone()
    if not fila:
        # RLS ya deja pasar sólo lo del espacio activo: un id de otro espacio
        # llega hasta acá igual de vacío que uno que nunca existió.
        return {"error": "ese bloqueo no existe en este equipo"}
    if fila["resuelto_en"] is not None:
        return {"error": "ese bloqueo ya estaba resuelto"}

    autorizados = {str(m) for m in (fila["responsable_membership_id"],
                                    fila["abierto_por"], fila["escalado_a"])
                  if m is not None}
    if str(quien.membership_id) not in autorizados:
        raise Denegado(
            "No podés resolver ese bloqueo: no es tuyo, no lo abriste vos ni "
            "se te escaló.")

    cur.execute(
        "update blocker set resuelto_en = now(), resolucion = %s where id = %s",
        (resolucion, bloqueo_id))

    cur.execute(
        "select count(*) n from blocker where task_id = %s and resuelto_en is null",
        (fila["task_id"],))
    quedan_abiertos = cur.fetchone()["n"] > 0

    tarea_desbloqueada = False
    if not quedan_abiertos:
        # `actualizar_estado` no exige bloqueos cerrados para salir de
        # `bloqueada` (deuda conocida, docs/STATUS.md "Pendiente": no hay
        # disparador que valide transiciones todavía), así que la tarea puede
        # haber salido por otro camino mientras este bloqueo seguía abierto.
        # Si ya no está bloqueada, no hay a qué "volver": resolver el último
        # bloqueo no la mueve.
        cur.execute("select estado from task where id = %s", (fila["task_id"],))
        estado_actual = cur.fetchone()["estado"]
        if estado_actual == "bloqueada":
            # `bloqueada` es una proyección: el estado al que se vuelve es el
            # que tenía el último evento que entró a `bloqueada`, nunca un
            # valor fijo. `task_state_event` es append-only y leda_app no
            # lo lee directo; esta función security definer es la única
            # puerta.
            cur.execute("select estado_previo_a_bloqueo(%s) as previo",
                       (fila["task_id"],))
            previo = cur.fetchone()["previo"]
            if previo is None:
                # No hay a qué volver y no se inventa un valor: ni null ni
                # `asignada` por defecto. Levanta después del `update` de
                # arriba a propósito -- la excepción deshace toda la
                # herramienta, incluida la resolución del bloqueo, dentro del
                # mismo punto de retorno por herramienta que usa `agente.py`.
                raise Denegado(
                    "No pude determinar a qué estado vuelve la tarea: no "
                    "tiene un estado anterior a bloqueada registrado.")
            cur.execute(
                """insert into task_state_event
                     (task_id, estado_anterior, estado_nuevo, actor_kind,
                      actor_app_user_id, motivo)
                   values (%s, 'bloqueada', %s, 'persona', %s, %s)""",
                (fila["task_id"], previo, quien.app_user_id, resolucion))
            _avisar_dependencia_informativa(
                cur, quien, fila["task_id"], previo, uuid.uuid4())
            tarea_desbloqueada = True
    return {"resuelto": True, "tarea_desbloqueada": tarea_desbloqueada}


def _preparar_adjuntar_evidencia(cur, quien: Solicitante, tarea_id, tipo,
                                 uri=None, descripcion=None):
    cur.execute(
        "select titulo, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if (str(fila["responsable_membership_id"]) != str(quien.membership_id)
            and not puede_aprobar_tarea(cur, quien, fila["responsable_membership_id"])):
        # T2b: a diferencia de actualizar_estado/registrar_bloqueo, mecánica
        # §6 lista "confirmación del referente" entre la evidencia que
        # Leda solicita -- el aprobador de la tarea (`puede_aprobar_tarea`,
        # un solo nivel) también puede adjuntarla, no sólo el responsable.
        raise Denegado(
            "No podés adjuntar evidencia a una tarea que no es tuya ni que revisás.")

    detalle = uri or descripcion or "(sin detalle)"
    cambio = _filas(("Tarea", fila["titulo"]), ("Nueva evidencia", detalle),
                    ("Tipo", tipo))
    huella = _huella("adjuntar_evidencia", tarea_id, tipo, uri, descripcion)
    return Preparacion(cambio=cambio, huella=huella,
                       hecho=f"Registré la evidencia en «{fila['titulo']}».")


@herramienta(
    "adjuntar_evidencia", "adjuntar_evidencia",
    "Registra la prueba de que un trabajo se hizo.",
    {"tarea_id": {"type": "string", "requerido": True},
     "tipo": {"type": "string", "requerido": True},
     "uri": {"type": "string"},
     "descripcion": {"type": "string"}},
    preparar=_preparar_adjuntar_evidencia)
def _adjuntar_evidencia(cur, quien: Solicitante, tarea_id, tipo, uri=None,
                        descripcion=None):
    # T6f: mismo motivo que `_actualizar_estado` -- dos evidencias
    # simultáneas sobre una tarea `en_revision` no pueden decidir cada una
    # con su propia lectura de qué aviso hay que retirar.
    _bloquear_tarea(cur, tarea_id)
    cur.execute(
        "select estado, titulo, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if (str(fila["responsable_membership_id"]) != str(quien.membership_id)
            and not puede_aprobar_tarea(cur, quien, fila["responsable_membership_id"])):
        raise Denegado(
            "No podés adjuntar evidencia a una tarea que no es tuya ni que revisás.")

    # ADR 0019, decisión 5: la clase por el contenido; cubre el tipo que se nombra, si es
    # uno de la política de la tarea que esa clase acepta.
    evidencia_id = _insertar_evidencia(
        cur, quien, tarea_id, _pieza_de_texto(cur, tarea_id, uri or descripcion, cubre=[tipo]))

    if fila["estado"] == "en_revision":
        # T6i (ADR 0009, enmienda 2026-09-27): mismo criterio que la entrega
        # repetida (T6g) -- evidencia nueva sobre una tarea ya en_revision,
        # de alguien que no es el aprobador, retira el aviso que tiene
        # esperando y manda uno nuevo con toda la evidencia vigente.
        _avisar_evidencia_nueva_en_revision(
            cur, quien, tarea_id, fila["titulo"], fila["responsable_membership_id"],
            evidencia_id, datetime.now(timezone.utc))

    return {"evidencia_id": str(evidencia_id)}


# --- La entrega con evidencia (ADR 0019, decisión 5; porción 2) ----------------------

def _clase_de_un_archivo(clase_del_archivo: str) -> str:
    """La clase de evidencia de un archivo guardado, por su contenido (`archivo.clase`)."""
    return "imagen" if clase_del_archivo == "imagen" else "archivo"


def _resolver_piezas(cur, tarea_id, piezas: list[dict]) -> list[dict]:
    """Las piezas de una entrega como filas a escribir: la clase la fija el código por el
    contenido (un archivo, por el suyo; un texto, si es un enlace o no) y lo que cubre se
    acota a los tipos de la tarea que esa clase acepta. Una pieza sin contenido, o con un
    archivo que no es de este espacio, es un error: no se adivina."""
    resueltas = []
    for pieza in piezas or []:
        if not isinstance(pieza, dict):
            raise ValueError("pieza")
        cubre = [str(t) for t in pieza.get("cubre") or []]
        if pieza.get("archivo_id"):
            cur.execute("select clase from archivo where id = %s", (str(pieza["archivo_id"]),))
            fila = cur.fetchone()
            if fila is None:
                raise ValueError("archivo")
            clase = _clase_de_un_archivo(fila["clase"])
            aceptados = _tipos_que_acepta(cur, tarea_id, clase)
            resueltas.append({"clase": clase, "archivo_id": str(pieza["archivo_id"]),
                              "cubre": [t for t in aceptados if t in cubre]})
        elif (pieza.get("texto") or "").strip():
            resueltas.append(_pieza_de_texto(cur, tarea_id, pieza["texto"], cubre=cubre))
        else:
            raise ValueError("contenido")
    return resueltas


@herramienta(
    "entregar_tarea", "actualizar_estado",
    "Entrega una tarea en curso con sus piezas de evidencia: en un solo acto escribe cada "
    "pieza y pasa la tarea a revisión. Sólo si la evidencia cubre la política de la tarea.",
    {"tarea_id": {"type": "string", "requerido": True},
     "piezas": {"type": "array", "requerido": True}})
def _entregar_tarea(cur, quien: Solicitante, tarea_id, piezas):
    """ADR 0019, decisión 5 (con el patrón del ADR 0009): las filas de evidencia y el paso a
    `en_revision` se escriben en el mismo acto, sólo desde `en_curso` y sólo si las piezas,
    con la evidencia vigente, cubren cada tipo que pide la política. Nunca `terminada`
    (constitución §11). Quien aprueba se entera como en la entrega de la cocina
    (`_notificar_entrega_al_aprobador`); la porción 3 lo reemplaza por el aviso del motor."""
    _bloquear_tarea(cur, tarea_id)
    cur.execute(
        "select estado, titulo, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if str(fila["responsable_membership_id"]) != str(quien.membership_id):
        raise Denegado("No podés entregar una tarea que no es tuya.")
    if fila["estado"] != "en_curso":
        return {"en_revision": False, "estado": str(fila["estado"]),
                "error": "la tarea no está en curso"}
    try:
        resueltas = _resolver_piezas(cur, tarea_id, piezas)
    except ValueError as e:
        return {"en_revision": False, "error": f"pieza inválida: {e}"}
    faltan = _tipos_que_faltan(cur, tarea_id, resueltas)
    if faltan:
        return _falta_evidencia_de_entrega(faltan)

    ids = [_insertar_evidencia(cur, quien, tarea_id, p) for p in resueltas]
    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, actor_app_user_id, motivo, at)
           values (%s, 'en_curso', 'en_revision', 'persona', %s, 'entrega con evidencia',
                   clock_timestamp())""",
        (tarea_id, quien.app_user_id))
    _avisar_dependencia_informativa(cur, quien, tarea_id, "en_revision", uuid.uuid4())
    cur.execute("select aprobador_membership_id from membership where id = %s",
                (fila["responsable_membership_id"],))
    aprob = cur.fetchone()
    if aprob and aprob["aprobador_membership_id"]:
        # La clave del aviso: la primera pieza escrita o, sin piezas (una política que no
        # pide evidencia), la transacción del acto (el mismo criterio que `_actualizar_estado`).
        if ids:
            dedupe_id = ids[0]
        else:
            cur.execute("select pg_current_xact_id()::text as x")
            dedupe_id = f"{tarea_id}:{cur.fetchone()['x']}"
        _notificar_entrega_al_aprobador(
            cur, quien, tarea_id, fila["titulo"], aprob["aprobador_membership_id"],
            dedupe_id, datetime.now(timezone.utc))
    return {"estado": "en_revision", "evidencias": ids}


@herramienta(
    "retirar_evidencia", "adjuntar_evidencia",
    "Retira una pieza de evidencia que entregó la misma persona, mientras la tarea no está "
    "aprobada. No borra nada: la pieza deja de contar.",
    {"evidencia_id": {"type": "string", "requerido": True},
     "motivo": {"type": "string"}})
def _retirar_evidencia(cur, quien: Solicitante, evidencia_id, motivo=None):
    """ADR 0019, decisión 3: "no, esa foto no era" agrega un retiro; nada se edita ni se
    borra. Sólo quien la entregó, y mientras la tarea no esté aprobada (ni terminada, ni con
    una aprobación posterior a la pieza que un pedido de cambios no dejó sin efecto)."""
    cur.execute("select task_id, entregado_por, at from evidence where id = %s",
                (evidencia_id,))
    pieza = cur.fetchone()
    if pieza is None:
        return {"retirada": False, "error": "esa evidencia no existe en este equipo"}
    _bloquear_tarea(cur, pieza["task_id"])
    if str(pieza["entregado_por"] or "") != str(quien.membership_id):
        raise Denegado("Sólo quien entregó una evidencia la puede retirar.")
    cur.execute("select estado from task where id = %s", (pieza["task_id"],))
    tarea = cur.fetchone()
    cur.execute(
        """select 1 from approval a
            where a.sujeto_tipo = 'tarea' and a.sujeto_id = %s and a.decision = 'aprobado'
              and a.at > %s
              and not exists (select 1 from approval r
                               where r.sujeto_tipo = 'tarea' and r.sujeto_id = a.sujeto_id
                                 and r.decision = 'rechazado' and r.at >= a.at)""",
        (pieza["task_id"], pieza["at"]))
    aprobada = cur.fetchone() is not None
    if tarea is None or str(tarea["estado"]) in ("terminada", "cancelada") or aprobada:
        return {"retirada": False, "error": "la tarea ya está aprobada o cerrada"}
    cur.execute("select 1 from evidencia_retirada where evidence_id = %s", (evidencia_id,))
    if cur.fetchone() is not None:
        return {"retirada": False, "error": "esa evidencia ya estaba retirada"}
    cur.execute(
        """insert into evidencia_retirada (workspace_id, evidence_id,
                                           retirada_por_membership_id, motivo, at)
           values (%s, %s, %s, %s, clock_timestamp())""",
        (quien.workspace_id, evidencia_id, quien.membership_id, motivo))
    return {"retirada": True, "tarea_id": str(pieza["task_id"]),
            "faltan": _tipos_que_faltan(cur, pieza["task_id"])}


def _exigir_puede_aprobarse(cur, tarea_id, fila) -> None:
    """ADR 0009, decisión 2: "Aprobar" sólo se permite sobre una tarea
    `en_revision` y con la evidencia que exige su política ya registrada.

    Sesión 2 por Telegram, 2026-09-27 (hallazgo 5): Ismael tocó "Aprobar" y
    Leda lo dejó aprobar a ciegas una tarea sin evidencia -- este chequeo
    es el que faltaba, y cierra también el defecto de revisión encontrado
    aparte: sin él, cualquiera con autoridad de aprobador podía aprobar (y
    de paso cerrar) una tarea `asignada`, o volver a aprobar una ya
    `terminada`, sólo con texto libre."""
    if fila["estado"] != "en_revision":
        raise Denegado(
            f"Sólo se aprueba una tarea en revisión; hoy está "
            f"{_estado_legible(fila['estado']).lower()}.")
    cur.execute("select evidencia_pendiente(%s) as f", (tarea_id,))
    if cur.fetchone()["f"]:
        responsable = _persona(cur, fila["responsable_membership_id"])
        nombre = responsable["nombre"] if responsable else "quien la tiene asignada"
        raise Denegado(
            f"Todavía no tiene la evidencia que exige; pedísela a {nombre}.")


def _preparar_aprobar_tarea(cur, quien: Solicitante, tarea_id, comentario=None):
    cur.execute(
        "select titulo, estado, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if fila["responsable_membership_id"] is None:
        return {"error": "esa tarea no tiene responsable asignado"}

    if str(fila["responsable_membership_id"]) == str(quien.membership_id):
        raise Denegado("No podés aprobar tu propio trabajo.")
    if not puede_aprobar_tarea(cur, quien, fila["responsable_membership_id"]):
        raise Denegado("No sos quien revisa el trabajo de esa persona.")
    _exigir_puede_aprobarse(cur, tarea_id, fila)

    # Decisión del usuario, 2026-09-27 (ADR 0008): aprobar registra la
    # aprobación y, si con ella alcanzan las condiciones de cierre (mecánica
    # §5), cierra la tarea en el mismo acto -- dos hechos distintos
    # (constitución §3: "aprobación y cierre son hechos distintos"), un solo
    # toque. Acá sólo se PREDICE el resultado, sin escribir nada todavía: ver
    # el comentario de `_MOTIVO_FALTA_APROBACION`.
    cur.execute("select motivo_no_cierra_tarea(%s) as m", (tarea_id,))
    motivo = cur.fetchone()["m"]
    falta = None if motivo in (None, _MOTIVO_FALTA_APROBACION) else motivo

    # Sin la palabra "falta" repetida (hallazgo 9, sesión 2 por Telegram,
    # 2026-09-27): el motivo que devuelve `motivo_no_cierra_tarea` ya
    # empieza diciendo qué falta ("Falta la evidencia requerida.", etc.).
    cambio = _filas(
        (None, f"Se aprueba «{fila['titulo']}»"
         + (" y queda terminada" if falta is None
            else f"; para cerrarla todavía: {falta}")),
        ("Comentario", comentario or None))
    huella = _huella("aprobar_tarea", tarea_id, fila["estado"],
                     fila["responsable_membership_id"], falta)
    hecho = (f"Listo: aprobaste «{fila['titulo']}». Quedó terminada."
             if falta is None
             else f"Listo: aprobaste «{fila['titulo']}»; para cerrarla "
                  f"todavía: {falta}")
    return Preparacion(cambio=cambio, huella=huella, hecho=hecho)


@herramienta(
    "aprobar_tarea", "aprobar_tarea",
    "Aprueba el trabajo de una tarea. Sólo puede quien la política del equipo "
    "designa para esa área. Si con esa aprobación se cumplen las condiciones "
    "de cierre, la tarea queda terminada en el mismo acto.",
    {"tarea_id": {"type": "string", "requerido": True},
     "comentario": {"type": "string"}},
    valida_en_handler=True, preparar=_preparar_aprobar_tarea)
def _aprobar_tarea(cur, quien: Solicitante, tarea_id, comentario=None):
    # T6f: "Aprobar" contra "Pedir cambios" simultáneos sobre la misma tarea
    # -- el que llega segundo tiene que decidir sobre lo que dejó el primero,
    # no sobre lo que leyó antes de que el primero terminara.
    _bloquear_tarea(cur, tarea_id)
    cur.execute(
        "select titulo, estado, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if fila["responsable_membership_id"] is None:
        return {"error": "esa tarea no tiene responsable asignado"}

    if str(fila["responsable_membership_id"]) == str(quien.membership_id):
        raise Denegado("No podés aprobar tu propio trabajo.")
    if not puede_aprobar_tarea(cur, quien, fila["responsable_membership_id"]):
        raise Denegado("No sos quien revisa el trabajo de esa persona.")
    _exigir_puede_aprobarse(cur, tarea_id, fila)

    # T6f (seguimiento del orquestador): `at` explícito con
    # `clock_timestamp()` -- ver el comentario de `_bloquear_tarea`.
    cur.execute(
        """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                 aprobador_membership_id, decision, comentario, at)
           values (%s, 'tarea', %s, %s, 'aprobado', %s, clock_timestamp())
           returning id""",
        (quien.workspace_id, tarea_id, quien.membership_id, comentario))
    aprobacion_id = cur.fetchone()["id"]

    # La aprobación ya está insertada: a diferencia de `preparar`, acá no
    # hace falta predecir nada -- se le vuelve a preguntar a la misma
    # función SQL (`motivo_no_cierra_tarea`, ya con esta fila adentro), que
    # es la única autoridad sobre si cierra (constitución §11: "esa
    # verificación es determinista"). Dos hechos distintos, dos filas
    # distintas: `approval` arriba, `task_state_event` acá abajo sólo si
    # corresponde -- nunca un único paso oculto.
    cur.execute("select motivo_no_cierra_tarea(%s) as m", (tarea_id,))
    falta = cur.fetchone()["m"]
    cerrada = falta is None
    if cerrada:
        # T6f (seguimiento del orquestador): `at` explícito con
        # `clock_timestamp()` -- ver el comentario de `_bloquear_tarea`.
        cur.execute(
            """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                             actor_kind, actor_app_user_id, motivo, at)
               values (%s, %s, 'terminada', 'persona', %s, %s, clock_timestamp())""",
            (tarea_id, fila["estado"], quien.app_user_id, comentario or "aprobación"))
        # Revisión (review-ec6f7d80): antes usaba `uuid.uuid4()` -- sin
        # ningún vínculo con lo que se acaba de escribir -- cuando ya había
        # un id real de negocio a mano, el de esta misma aprobación.
        _avisar_dependencia_informativa(cur, quien, tarea_id, "terminada", aprobacion_id)

    # Constitución §3: "no persiguen avances ni administran estados
    # intermedios" es sobre el responsable, no sobre enterarse de un hecho
    # que lo involucra -- sesión 2 por Telegram, 2026-09-27, hallazgo 5:
    # Ismael aprobó y nadie le avisó a Ariel. `_avisar` ya omite en silencio
    # si el responsable no tiene chat vinculado (mismo patrón que el resto
    # de los avisos automáticos); el dedupe es por esta aprobación, nunca
    # por la hora.
    _avisar(
        cur, quien, fila["responsable_membership_id"],
        (f"{quien.nombre} aprobó «{fila['titulo']}»; quedó terminada."
         if cerrada else
         f"{quien.nombre} aprobó «{fila['titulo']}»; para cerrarla todavía: {falta}"),
        dedupe_key=f"{quien.workspace_id}:aprobacion:{aprobacion_id}")

    return {"aprobada": True, "cerrada": cerrada, "falta": falta,
           "titulo": fila["titulo"]}


def _exigir_puede_pedirse_cambios(cur, fila) -> None:
    """ADR 0009, decisión 4: "Pedir cambios" es del mismo aprobador que
    "Aprobar", sobre una tarea `en_revision` -- sin el gate de evidencia:
    pedir que se corrija algo no depende de que ya haya evidencia
    registrada."""
    if fila["estado"] != "en_revision":
        raise Denegado(
            f"Sólo se piden cambios sobre una tarea en revisión; hoy está "
            f"{_estado_legible(fila['estado']).lower()}.")


def _destino_pedir_cambios(cur, tarea_id) -> str:
    """T6c (`odd/tasks/leda-orienta.md`), enmienda a la decisión 4 de ADR
    0009: a qué estado vuelve la tarea al pedirle cambios -- el que tenía
    antes de la ÚLTIMA entrada a `en_revision` (`estado_previo_a_revision`,
    `db/esquema.sql`). `en_curso` si estaba en curso: es una restauración,
    exenta del gate de arranque (`exigir_dependencias_resueltas`), igual que
    salir de `bloqueada`. Cualquier otro valor -- `asignada` si se entregó
    sin haber arrancado nunca, o nulo si no hay un evento anterior
    registrado -- devuelve `asignada`: nunca hace falta eximirla del gate,
    así que es el default seguro cuando no se puede afirmar que la tarea ya
    había arrancado.
    """
    cur.execute("select estado_previo_a_revision(%s) as previo", (tarea_id,))
    previo = cur.fetchone()["previo"]
    return previo if previo == "en_curso" else "asignada"


def _preparar_pedir_cambios_tarea(cur, quien: Solicitante, tarea_id, comentario=None):
    cur.execute(
        "select titulo, estado, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if fila["responsable_membership_id"] is None:
        return {"error": "esa tarea no tiene responsable asignado"}

    if str(fila["responsable_membership_id"]) == str(quien.membership_id):
        raise Denegado("No podés pedir cambios en tu propio trabajo.")
    if not puede_aprobar_tarea(cur, quien, fila["responsable_membership_id"]):
        raise Denegado("No sos quien revisa el trabajo de esa persona.")
    _exigir_puede_pedirse_cambios(cur, fila)

    comentario = (comentario or "").strip()
    if not comentario:
        raise Denegado("Hace falta contar qué falta corregir.")

    destino = _destino_pedir_cambios(cur, tarea_id)

    cambio = _filas(
        (None, f"Se piden cambios en «{fila['titulo']}»."),
        ("Qué falta corregir", comentario),
        (None, f"La tarea vuelve a {_estar(destino)}."))
    huella = _huella("pedir_cambios_tarea", tarea_id, fila["estado"], comentario, destino)
    return Preparacion(
        cambio=cambio, huella=huella,
        hecho=f"Pedí cambios en «{fila['titulo']}»: la tarea volvió a {_estar(destino)}.")


@herramienta(
    "pedir_cambios_tarea", "pedir_cambios_tarea",
    "Devuelve a trabajo una tarea en revisión, con el comentario de lo que "
    "falta corregir. Sólo puede quien revisa el trabajo de esa persona.",
    {"tarea_id": {"type": "string", "requerido": True},
     "comentario": {"type": "string", "requerido": True}},
    valida_en_handler=True, preparar=_preparar_pedir_cambios_tarea)
def _pedir_cambios_tarea(cur, quien: Solicitante, tarea_id, comentario=None):
    # T6f: mismo motivo que `_aprobar_tarea`.
    _bloquear_tarea(cur, tarea_id)
    cur.execute(
        "select titulo, estado, responsable_membership_id from task where id = %s",
        (tarea_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa tarea no existe en este equipo"}
    if fila["responsable_membership_id"] is None:
        return {"error": "esa tarea no tiene responsable asignado"}

    if str(fila["responsable_membership_id"]) == str(quien.membership_id):
        raise Denegado("No podés pedir cambios en tu propio trabajo.")
    if not puede_aprobar_tarea(cur, quien, fila["responsable_membership_id"]):
        raise Denegado("No sos quien revisa el trabajo de esa persona.")
    _exigir_puede_pedirse_cambios(cur, fila)

    comentario = (comentario or "").strip()
    if not comentario:
        raise Denegado("Hace falta contar qué falta corregir.")

    # T6c (`odd/tasks/leda-orienta.md`), enmienda a la decisión 4 de ADR
    # 0009: el destino ya no es siempre `en_curso` -- una tarea que se
    # entregó sin haber arrancado nunca ("Ya la terminé" se ofrece desde
    # `asignada`) vuelve a `asignada`, no a un `en_curso` que nunca tuvo. El
    # disparador `exigir_dependencias_resueltas` (`db/esquema.sql`) exime la
    # restauración a `en_curso` del gate de arranque; sin ella, esta misma
    # herramienta era la que no podía pedir cambios con una dependencia
    # bloqueante todavía abierta -- el insert de abajo lo rechazaba.
    destino = _destino_pedir_cambios(cur, tarea_id)

    # `rechazado` es el único otro valor de `decision_aprobacion`
    # (db/esquema.sql) -- no se agrega un tercero para esto: "pedir
    # cambios" es, en los hechos, un rechazo del trabajo entregado, con la
    # tarea volviendo a trabajo en vez de quedar cerrada.
    #
    # T6f (seguimiento del orquestador): `at` explícito con
    # `clock_timestamp()` en las dos inserciones de abajo -- ver el
    # comentario de `_bloquear_tarea`.
    cur.execute(
        """insert into approval (workspace_id, sujeto_tipo, sujeto_id,
                                 aprobador_membership_id, decision, comentario, at)
           values (%s, 'tarea', %s, %s, 'rechazado', %s, clock_timestamp())
           returning id""",
        (quien.workspace_id, tarea_id, quien.membership_id, comentario))
    decision_id = cur.fetchone()["id"]

    cur.execute(
        """insert into task_state_event (task_id, estado_anterior, estado_nuevo,
                                         actor_kind, actor_app_user_id, motivo, at)
           values (%s, %s, %s, 'persona', %s, %s, clock_timestamp())""",
        (tarea_id, fila["estado"], destino, quien.app_user_id, comentario))

    _avisar(
        cur, quien, fila["responsable_membership_id"],
        (f"{quien.nombre} pidió cambios en «{fila['titulo']}»: {comentario}\n"
         f"La tarea vuelve a {_estar(destino)}."),
        dedupe_key=f"{quien.workspace_id}:pedir_cambios:{decision_id}")

    return {"pedido": True, "titulo": fila["titulo"]}


# ---------------------------------------------------------------------------
# Dependencias
# ---------------------------------------------------------------------------

def _persona(cur, membership_id):
    if membership_id is None:
        return None
    cur.execute(
        "select telegram_user_id, nombre from integrante where membership_id = %s",
        (membership_id,))
    return cur.fetchone()


def _avisar(cur, quien: Solicitante, destinatario_membership_id, texto, *,
           dedupe_key, tipo="normal") -> None:
    """Un aviso de coordinación: lo que otra persona hizo sobre trabajo compartido
    y quien lo recibe necesita para actuar o enterarse (aprobación, cambios
    pedidos, dependencia). Fuera del tope diario (`es_coordinacion`). Si la persona
    todavía no activó el chat, se omite en silencio, igual que la escalera y la
    cadencia."""
    persona = _persona(cur, destinatario_membership_id)
    if not persona or persona["telegram_user_id"] is None:
        return
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=persona["telegram_user_id"],
        text=texto, recipient_membership_id=destinatario_membership_id,
        message_type=tipo, dedupe_key=dedupe_key, es_coordinacion=True)


def _enlace_portal_tarea(tarea_id) -> str | None:
    """Enlace a una vista de esta tarea en particular, para sumar al aviso
    de entrega (ADR 0009, 'pendiente'). Hoy no existe: sólo hay un tablero
    de sólo lectura por espacio (`/tablero/{token}`, sin una tarea puntual).
    Punto de enganche a propósito -- cuando exista esa vista,
    `_notificar_entrega_al_aprobador` suma lo que devuelva acá sin que nada
    más cambie; hasta entonces, ninguna URL se inventa (constitución §4)."""
    return None


def _evidencia_vigente(cur, tarea_id) -> list[dict]:
    """T6i (`odd/tasks/leda-orienta.md`): toda la evidencia del ciclo de
    entrega actual, para el aviso al aprobador -- mismo corte que
    `evidencia_pendiente` (`db/esquema.sql`): sólo cuenta la que tiene `at`
    posterior al último `approval` 'rechazado' de la tarea; sin ningún
    'rechazado', es toda la evidencia registrada. Sin esto, el aviso podía
    mostrar evidencia de un ciclo ya superado por "Pedir cambios" -- la misma
    razón por la que `evidencia_pendiente` deja de contarla (ADR 0009,
    enmienda T6b)."""
    cur.execute(
        """select e.tipo, coalesce(e.texto, e.uri, a.nombre_original) as uri
             from evidence e
             left join archivo a on a.workspace_id = e.workspace_id and a.id = e.archivo_id
            where e.task_id = %s
              and e.at > coalesce(
                (select max(r.at) from approval r
                  where r.sujeto_tipo = 'tarea' and r.sujeto_id = e.task_id
                    and r.decision = 'rechazado'),
                '-infinity'::timestamptz)
              -- ADR 0019, decisión 3: una pieza retirada no va en el aviso.
              and not exists (select 1 from evidencia_retirada w where w.evidence_id = e.id)
            order by e.at""",
        (tarea_id,))
    return cur.fetchall()


def _notificar_entrega_al_aprobador(cur, quien: Solicitante, tarea_id, titulo,
                                    aprobador_membership_id, dedupe_id, ahora,
                                    *, es_reemplazo: bool = False) -> None:
    """ADR 0009, decisión 3: cuando una tarea llega a `en_revision`, quien la
    aprueba se entera -- no sólo el responsable con `_avisar` --, con un aviso
    de coordinación: llega siempre, fuera del tope diario (mecánica §10). Se
    omite en silencio si el aprobador no tiene chat vinculado, igual que
    cualquier otro aviso automático -- nunca falla en silencio por otra causa.

    Los botones "Aprobar" y "Pedir cambios" que llevaba se retiraron con los
    flujos A y B (E3-3): sólo los resolvía su toque, que vivía en `gateway`.

    Enmienda T6i (2026-09-27): el aviso muestra TODA la evidencia vigente del
    ciclo actual (`_evidencia_vigente`), no sólo la de este llamado -- si el
    aprobador recién abre el chat después de dos entregas, tiene que ver las
    dos. `es_reemplazo` distingue el verbo de la primera entrega del que sale
    cuando llega evidencia nueva a una tarea que ya está en revisión
    (`_avisar_evidencia_nueva_en_revision`, abajo)."""
    cur.execute(
        "select telegram_user_id from integrante where membership_id = %s",
        (aprobador_membership_id,))
    aprobador = cur.fetchone()
    if not aprobador or aprobador["telegram_user_id"] is None:
        return

    verbo = "sumó evidencia nueva a" if es_reemplazo else "entregó"
    texto = f"{quien.nombre} {verbo} «{titulo}»"
    evidencias = _evidencia_vigente(cur, tarea_id)
    if evidencias:
        texto += "\nEvidencia:\n" + "\n".join(
            f"- ({e['tipo']}) {e['uri'] or 'sin detalle'}" for e in evidencias)
    enlace = _enlace_portal_tarea(tarea_id)
    if enlace:
        texto += f"\n{enlace}"

    # T6d/T6h: dos entregas dentro de la misma transacción comparten esta clave
    # y `enqueue_outbox` descarta la segunda (`on conflict (dedupe_key) do
    # nothing`): un solo aviso por acto.
    enqueue_outbox(
        cur, workspace_id=quien.workspace_id, chat_id=aprobador["telegram_user_id"],
        text=texto, recipient_membership_id=str(aprobador_membership_id),
        scheduled_for=ahora, dedupe_key=f"{quien.workspace_id}:entrega:{dedupe_id}",
        es_coordinacion=True)


def _avisar_evidencia_nueva_en_revision(cur, quien: Solicitante, tarea_id, titulo,
                                        responsable_membership_id, evidencia_id,
                                        ahora) -> None:
    """T6i (`odd/tasks/leda-orienta.md`; ADR 0009, enmienda 2026-09-27):
    evidencia nueva sobre una tarea que YA está `en_revision` -- entrega
    repetida (T6g) o "Adjuntar evidencia" -- de alguien que no es el
    aprobador le manda al aprobador un aviso nuevo con toda la evidencia
    vigente (`_notificar_entrega_al_aprobador`, `es_reemplazo`). Si quien la
    manda es el propio aprobador, no hay a quién avisar de nuevo -- ya lo
    sabe."""
    cur.execute(
        "select aprobador_membership_id from membership where id = %s",
        (responsable_membership_id,))
    aprob = cur.fetchone()
    aprobador_membership_id = aprob["aprobador_membership_id"] if aprob else None
    if not aprobador_membership_id:
        return
    if str(quien.membership_id) == str(aprobador_membership_id):
        return

    _notificar_entrega_al_aprobador(
        cur, quien, tarea_id, titulo, aprobador_membership_id,
        str(evidencia_id), ahora, es_reemplazo=True)


def _avisar_dependencia_informativa(cur, quien: Solicitante, tarea_id, estado_nuevo,
                                    event_id) -> None:
    """Mecánica §4: una dependencia informativa avisa a las dos partes cuando
    la origen cambia de fecha o de estado. Se llama después de insertar la
    fila de `task_state_event` de cada herramienta que la escribe.

    `fecha_objetivo` es inmutable una vez comprometida la tarea
    (`bloquear_estado_directo` en `db/esquema.sql` la rechaza), y ninguna
    ruta de código la cambia: el aviso por cambio de fecha queda sin
    disparador propio. Cubre sólo el cambio de estado -- gap para
    `docs/STATUS.md`.
    """
    cur.execute(
        """select d.id, o.titulo as origen_titulo,
                  o.responsable_membership_id as origen_resp,
                  t.titulo as destino_titulo,
                  t.responsable_membership_id as destino_resp
             from dependency d
             join task o on o.id = d.origen_task_id
             join task t on t.id = d.destino_task_id
            where d.origen_task_id = %s and d.tipo = 'informativa'""",
        (tarea_id,))
    for dep in cur.fetchall():
        texto = (f"«{dep['origen_titulo']}» pasó a {estado_nuevo}. Es una "
                 f"dependencia informativa con «{dep['destino_titulo']}».")
        for destinatario in {dep["origen_resp"], dep["destino_resp"]}:
            if destinatario is None:
                continue
            _avisar(cur, quien, destinatario, texto, tipo="informativo",
                   dedupe_key=(f"{quien.workspace_id}:dependencia-informativa:"
                               f"{dep['id']}:{event_id}:{destinatario}"))


def _tarea_para_dependencia(cur, tarea_id):
    cur.execute(
        """select id, estado, area_id, responsable_membership_id, titulo
             from task where id = %s""", (tarea_id,))
    return cur.fetchone()


def _autorizado_para_dependencia(cur, quien: Solicitante, origen, destino) -> bool:
    """El responsable de cualquiera de las dos tareas, o su referente
    (decisión de producto, 2026-09-22): una dependencia bloqueante frena la
    tarea de otra persona, así que no la declara cualquiera; pero exigir
    confirmación de la otra parte agrega fricción sin necesidad, porque el
    aviso ya la hace visible. "Referente" es `puede_aprobar_tarea`, la misma
    noción que usa `aprobar_tarea`."""
    quien_id = str(quien.membership_id)
    if quien_id == str(origen["responsable_membership_id"]):
        return True
    if quien_id == str(destino["responsable_membership_id"]):
        return True
    if puede_aprobar_tarea(cur, quien, origen["responsable_membership_id"]):
        return True
    if puede_aprobar_tarea(cur, quien, destino["responsable_membership_id"]):
        return True
    return False


def _destinatarios_dependencia_creada(cur, quien: Solicitante, origen, destino):
    """La otra parte, y entre áreas distintas los dos referentes (mecánica
    §4). "Referente" acá es quien aprueba el trabajo de cada responsable
    (`aprobador_membership_id`) -- la misma noción funcional que
    `puede_aprobar_tarea`, no un rol con un nombre fijo que cada pack puede
    llamar distinto."""
    quien_id = str(quien.membership_id)
    resp_origen = origen["responsable_membership_id"]
    resp_destino = destino["responsable_membership_id"]
    es_resp_origen = resp_origen is not None and quien_id == str(resp_origen)
    es_resp_destino = resp_destino is not None and quien_id == str(resp_destino)

    destinatarios: set[str] = set()
    if es_resp_origen and not es_resp_destino:
        if resp_destino is not None:
            destinatarios.add(str(resp_destino))
    elif es_resp_destino and not es_resp_origen:
        if resp_origen is not None:
            destinatarios.add(str(resp_origen))
    elif not es_resp_origen and not es_resp_destino:
        # Quien crea es referente de una de las dos, no responsable de
        # ninguna: avisa a los dos responsables.
        if resp_origen is not None:
            destinatarios.add(str(resp_origen))
        if resp_destino is not None:
            destinatarios.add(str(resp_destino))
    # Si es responsable de las dos a la vez, no hay "otra parte" a quien avisar.

    if str(origen["area_id"]) != str(destino["area_id"]):
        for resp in (resp_origen, resp_destino):
            if resp is None:
                continue
            cur.execute(
                "select aprobador_membership_id from membership where id = %s",
                (resp,))
            fila = cur.fetchone()
            if fila and fila["aprobador_membership_id"]:
                destinatarios.add(str(fila["aprobador_membership_id"]))

    destinatarios.discard(quien_id)
    return destinatarios


def _texto_dependencia_creada(tipo, origen, destino, creador_nombre) -> str:
    if tipo == "bloqueante":
        texto = (f"{creador_nombre} registró que «{destino['titulo']}» depende de "
                 f"«{origen['titulo']}»: no puede pasar a en curso hasta que esa "
                 f"tarea esté terminada.")
        if destino["estado"] == "en_curso":
            # No la mueve retroactivamente (mecánica §4 sólo frena el pase a
            # en curso, no revierte uno ya hecho); esto lo deja visible.
            texto += (f" «{destino['titulo']}» ya está en curso, así que esta "
                      f"dependencia no la frena ahora.")
        return texto
    return (f"{creador_nombre} registró una dependencia informativa entre "
           f"«{origen['titulo']}» y «{destino['titulo']}»: aviso cuando "
           f"alguna de las dos cambie de estado.")


def _preparar_crear_dependencia(cur, quien: Solicitante, origen_tarea_id,
                                destino_tarea_id, tipo="bloqueante"):
    if str(origen_tarea_id) == str(destino_tarea_id):
        return {"error": "una tarea no puede depender de sí misma"}

    origen = _tarea_para_dependencia(cur, origen_tarea_id)
    if not origen:
        return {"error": "la tarea de origen no existe en este equipo"}
    destino = _tarea_para_dependencia(cur, destino_tarea_id)
    if not destino:
        return {"error": "la tarea de destino no existe en este equipo"}

    if destino["estado"] in ("terminada", "cancelada"):
        return {"error": "esa tarea ya está cerrada, no se le puede agregar una dependencia"}

    cur.execute(
        "select 1 from dependency where origen_task_id = %s and destino_task_id = %s",
        (origen_tarea_id, destino_tarea_id))
    if cur.fetchone():
        return {"error": "ya existe una dependencia registrada entre esas tareas"}

    if not _autorizado_para_dependencia(cur, quien, origen, destino):
        raise Denegado(
            "No podés declarar una dependencia entre esas tareas: no sos "
            "responsable de ninguna de las dos, ni referente de quien lo es.")

    tipo_legible = "bloqueante" if tipo == "bloqueante" else "informativa"
    cambio = _filas(("Tarea", destino["titulo"]),
                    ("Pasa a depender de", origen["titulo"]),
                    ("Tipo", tipo_legible))
    huella = _huella("crear_dependencia", origen_tarea_id, destino_tarea_id,
                     tipo, origen["estado"], destino["estado"])
    return Preparacion(
        cambio=cambio, huella=huella,
        hecho=(f"Registré que «{destino['titulo']}» depende de "
               f"«{origen['titulo']}» ({tipo_legible})."))


@herramienta(
    "crear_dependencia", "crear_dependencia",
    "Declara que una tarea depende de otra tarea del equipo -- es lo que "
    "corresponde cuando lo que frena una tarea es otra tarea, no una causa "
    "externa (eso es registrar_bloqueo). 'bloqueante' frena que la destino "
    "pase a en curso hasta que la origen esté terminada; 'informativa' sólo "
    "avisa cuando la origen cambia de estado.",
    {"origen_tarea_id": {"type": "string", "requerido": True},
     "destino_tarea_id": {"type": "string", "requerido": True},
     "tipo": {"type": "string", "enum": ["bloqueante", "informativa"]}},
    valida_en_handler=True, preparar=_preparar_crear_dependencia)
def _crear_dependencia(cur, quien: Solicitante, origen_tarea_id, destino_tarea_id,
                       tipo="bloqueante"):
    if str(origen_tarea_id) == str(destino_tarea_id):
        return {"error": "una tarea no puede depender de sí misma"}

    origen = _tarea_para_dependencia(cur, origen_tarea_id)
    if not origen:
        return {"error": "la tarea de origen no existe en este equipo"}
    destino = _tarea_para_dependencia(cur, destino_tarea_id)
    if not destino:
        return {"error": "la tarea de destino no existe en este equipo"}

    if destino["estado"] in ("terminada", "cancelada"):
        return {"error": "esa tarea ya está cerrada, no se le puede agregar una dependencia"}

    cur.execute(
        "select 1 from dependency where origen_task_id = %s and destino_task_id = %s",
        (origen_tarea_id, destino_tarea_id))
    if cur.fetchone():
        return {"error": "ya existe una dependencia registrada entre esas tareas"}

    if not _autorizado_para_dependencia(cur, quien, origen, destino):
        raise Denegado(
            "No podés declarar una dependencia entre esas tareas: no sos "
            "responsable de ninguna de las dos, ni referente de quien lo es.")

    # Un ciclo lo rechaza `trg_evitar_ciclo_dependencia`: la excepción de la
    # base sube tal cual, y `agente.py` ya la traduce a un mensaje legible
    # para quien llama (no es un incidente).
    cur.execute(
        """insert into dependency (workspace_id, origen_task_id, destino_task_id, tipo)
           values (%s, %s, %s, %s) returning id""",
        (quien.workspace_id, origen_tarea_id, destino_tarea_id, tipo))
    dep_id = cur.fetchone()["id"]

    destinatarios = _destinatarios_dependencia_creada(cur, quien, origen, destino)
    texto = _texto_dependencia_creada(tipo, origen, destino, quien.nombre)
    for destinatario in destinatarios:
        _avisar(cur, quien, destinatario, texto,
               dedupe_key=f"{quien.workspace_id}:dependencia-creada:{dep_id}:{destinatario}")

    return {"dependencia_id": str(dep_id)}


def _preparar_quitar_dependencia(cur, quien: Solicitante, dependencia_id):
    cur.execute(
        """select d.id, o.titulo as origen_titulo, t.titulo as destino_titulo,
                  o.responsable_membership_id as origen_resp,
                  t.responsable_membership_id as destino_resp
             from dependency d
             join task o on o.id = d.origen_task_id
             join task t on t.id = d.destino_task_id
            where d.id = %s""", (dependencia_id,))
    fila = cur.fetchone()
    if not fila:
        return {"error": "esa dependencia no existe en este equipo"}

    origen = {"responsable_membership_id": fila["origen_resp"]}
    destino = {"responsable_membership_id": fila["destino_resp"]}
    if not _autorizado_para_dependencia(cur, quien, origen, destino):
        raise Denegado(
            "No podés quitar esa dependencia: no sos responsable de ninguna "
            "de las dos tareas, ni referente de quien lo es.")

    cambio = _filas(("Tarea", fila["destino_titulo"]),
                    ("Deja de depender de", fila["origen_titulo"]))
    huella = _huella("quitar_dependencia", dependencia_id)
    return Preparacion(
        cambio=cambio, huella=huella,
        hecho=(f"Eliminé la dependencia entre «{fila['destino_titulo']}» y "
               f"«{fila['origen_titulo']}»."))


@herramienta(
    "quitar_dependencia", "quitar_dependencia",
    "Elimina una dependencia entre dos tareas.",
    {"dependencia_id": {"type": "string", "requerido": True}},
    valida_en_handler=True, preparar=_preparar_quitar_dependencia)
def _quitar_dependencia(cur, quien: Solicitante, dependencia_id):
    cur.execute(
        """select d.id, o.responsable_membership_id as origen_resp,
                  t.responsable_membership_id as destino_resp
             from dependency d
             join task o on o.id = d.origen_task_id
             join task t on t.id = d.destino_task_id
            where d.id = %s""", (dependencia_id,))
    fila = cur.fetchone()
    if not fila:
        # RLS ya deja pasar sólo lo del espacio activo: una dependencia de
        # otro espacio llega hasta acá igual de vacía que una inventada.
        return {"error": "esa dependencia no existe en este equipo"}

    origen = {"responsable_membership_id": fila["origen_resp"]}
    destino = {"responsable_membership_id": fila["destino_resp"]}
    if not _autorizado_para_dependencia(cur, quien, origen, destino):
        raise Denegado(
            "No podés quitar esa dependencia: no sos responsable de ninguna "
            "de las dos tareas, ni referente de quien lo es.")

    # Baja física, no un estado "quitada": `dependency` no tiene columnas de
    # baja blanda como `blocker.resuelto_en`, y `ejecutar` audita toda
    # operación que corre (`_auditar`, accion "herramienta:quitar_dependencia",
    # con los argumentos y la dependencia como sujeto) con quién, cuándo y
    # con qué versión de las reglas, así que el rastro no depende de esta fila.
    cur.execute("delete from dependency where id = %s", (dependencia_id,))
    return {"eliminada": True}


@herramienta(
    "pedir_tablero", "consultar",
    "Devuelve un enlace personal al tablero, con el estado del equipo: avance "
    "de objetivos, carga por persona, vencidas y bloqueos. Usalo cuando "
    "pidan ver el tablero, el panel o un resumen visual.",
    {}, necesita_chat=True)
def _pedir_tablero(cur, quien: Solicitante, chat_id: int | None = None):
    """Emite un enlace al tablero, sólo por chat privado.

    Un enlace en un grupo es acceso para cualquiera que lo lea, ahora y
    dentro de seis meses cuando alguien revise el historial. Por eso el
    chat lo pone el servidor y no el modelo: si el modelo pudiera declararlo,
    bastaría con que dijera "privado".
    """
    from datetime import datetime, timezone

    from . import tablero
    from .config import config

    if chat_id is None or chat_id <= 0:
        return {"emitido": False,
                "explicacion": "El enlace al tablero se pide por chat privado, "
                               "no por el grupo. Escribime por privado y te lo mando."}

    if not config.base_url:
        return {"emitido": False,
                "explicacion": "Todavía no está configurada la dirección "
                               "pública, así que no puedo armar el enlace."}

    token = tablero.emitir(cur, quien.membership_id,
                           datetime.now(timezone.utc))
    minutos = tablero.minutos_de_vigencia(cur)
    return {"emitido": True,
            "enlace": f"{config.base_url.rstrip('/')}/tablero/{token}",
            "vence_en_minutos": minutos}


@herramienta(
    "consultar_objetivos", "consultar",
    "Objetivos del equipo con su avance.", {})
def _consultar_objetivos(cur, quien: Solicitante):
    cur.execute(
        """select o.id, o.titulo, o.tipo, o.estado, o.fecha_objetivo,
                  count(t.id) filter (where t.estado = 'terminada') as hechas,
                  count(t.id) as total
             from objective o left join task t on t.objective_id = o.id
            where o.workspace_id = %s
            group by o.id order by o.tipo, o.creado_en""",
        (quien.workspace_id,))
    return [dict(f) for f in cur.fetchall()]
