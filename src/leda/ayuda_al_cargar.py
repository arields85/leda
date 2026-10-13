"""La ayuda de la IA al cargar una tarea en la plataforma (ADR 0023, punto 4; porción J2 de
`odd/tasks/plataforma-jerarquias.md`, con su diseño corto).

La persona cuenta en un recuadro libre qué quiere hacer y Leda propone lo que el formulario todavía
tiene vacío: título, descripción, criterio de aceptación, quién la hace, a qué tarea espera, el
objetivo y la fecha. Es la regla del mozo (`AGENTS.md`, punto 11): la IA propone y el código
decide qué vale; lo que no pasa no se propone y se dice por qué (nunca en silencio). Nada se carga
acá: la persona ve cada dato marcado, lo corrige o lo acepta, y confirma como siempre.

- **Qué recibe la IA** (`entrada_de_la_ia`), sólo del espacio de la carga: el texto, lo que ya
  está escrito, hoy y los días que vienen con su día de la semana (`hechos.dia`), los objetivos
  abiertos y las tareas abiertas para esperar con un código cada una (O1…, T1…), y el área y la
  evidencia de quien la hace si ya se eligió. Nunca los nombres del equipo ni un id: quién la hace
  vuelve como las palabras con que se la nombró.
- **Lo que decide el código** (`revisar`):
  - quién la hace, sólo si sus palabras están en el texto y son de alguien del equipo
    (`coinciden`: `fichas.integrantes_que_coinciden`, con los apodos); con dos o más, Leda no
    elige y las muestra (ADR 0020, decisión 3);
  - la espera y el objetivo, de sus listas; el objetivo es el de la tarea que espera si está
    abierto;
  - la fecha, sólo si es un día hábil de las opciones y el texto la dice (`la_fecha_esta_dicha`;
    constitución §4: nunca una fecha que nadie dijo);
  - título, descripción y criterio, con los topes del formulario y sin un número ni un nombre que
    no estén en lo que escribió la persona o en los datos de esta tarea
    (`entrega.problema_del_ejemplo`, punto por punto); el criterio, además, con la parte que dice
    cómo se comprueba copiada tal cual dentro de él (la idea del alta congelada,
    `MOTIVO_CRITERIO_SIN_COMPROBACION`, comprobada por el código y no por la IA).
- **La evidencia** no la propone la IA: elegir quién la hace marca la que pide su área, en la web.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from .motor import hechos
from .motor.entrega import problema_del_ejemplo, puntos_del_criterio
from .motor.ia_real import RespuestaInvalida, sin_cortar

NOMBRE_HERRAMIENTA = "proponer_la_carga"

# Los datos del formulario, en su orden, y cómo se llaman para la IA y en los avisos (`campo`,
# los mismos nombres que usa la carga).
CAMPOS = ("objetivo_id", "titulo", "descripcion", "responsable_id", "fecha", "espera_id",
          "criterio")
PARA_LA_IA = {"objetivo_id": "objetivo", "titulo": "titulo", "descripcion": "descripcion",
              "responsable_id": "responsable", "fecha": "fecha", "espera_id": "espera",
              "criterio": "criterio"}

# Los topes del formulario (migración 0062) y el del texto libre.
LARGOS = {"titulo": 200, "descripcion": 800, "criterio": 500}
LARGO_DEL_TEXTO = 1000
# Los días que se le dan a la IA para nombrar una fecha: ocho semanas, como al motor.
DIAS_PROXIMOS = 56
TOPE_DE_SALIDA = 1500

TEXTOS = {
    ("titulo", "sin_proponer"):
        "No pude proponer el título con lo que escribiste; contame qué hay que hacer.",
    ("descripcion", "sin_proponer"):
        "No pude proponer la descripción con lo que escribiste; si hace falta, escribila vos.",
    ("criterio", "sin_proponer"):
        "No pude proponer el criterio con lo que escribiste; contame cómo se comprueba.",
    ("responsable", "no_encontrado"): "No encontré a {quien} en el equipo.",
    ("responsable", "varios"):
        "Encontré a más de una persona para {quien}: elegí quién la hace.",
    ("fecha", "no_es_habil"):
        "No puse la fecha: ese día no es hábil en este espacio o ya no se puede elegir; "
        "elegila en el calendario.",
    ("fecha", "no_dicha"):
        "No puse la fecha: no encontré en lo que escribiste qué día es; elegila en el "
        "calendario.",
}

INSTRUCCIONES = """\
Sos Leda, la project manager del equipo. Una persona está cargando una tarea en la plataforma: te \
contó con sus palabras qué quiere hacer (texto) y te pide que completes los datos de la tarea que \
todavía están vacíos (pide). Lo que devolvés es una propuesta: la persona ve cada dato marcado y lo \
acepta, lo corrige o lo borra.

El título, la descripción y el criterio los proponés vos, con lo que contó la persona. Quién la \
hace, la tarea que espera y la fecha van sólo si la persona los dijo. El objetivo, si se entiende \
de lo que contó.

Usás sólo lo que recibiste: ningún número, nombre, fecha ni dato que no esté ahí. Lo que no podés \
saber con lo que recibiste va vacío; la persona lo completa."""

_DATOS = {
    "titulo": "Una línea que dice qué hay que hacer, en imperativo.",
    "descripcion": "Lo que contó la persona sobre la tarea, ordenado y bien escrito, sin agregar "
                   "nada.",
    "criterio": "El criterio de aceptación: qué tiene que pasar para darla por terminada, dicho "
                "de manera que quien la revise pueda comprobarlo.",
    "como_se_comprueba": "La parte del criterio que dice cómo se comprueba que la tarea está "
                         "hecha, copiada tal cual del criterio.",
    "responsable": "Las palabras con que la persona nombró a quien va a hacer la tarea, tal cual "
                   "las escribió.",
    "espera": "El código (T1, T2...) de la tarea abierta que tiene que terminar antes de que "
              "esta pueda empezar.",
    "objetivo": "El código (O1, O2...) del objetivo al que contribuye la tarea.",
    "fecha": "El día para el que la persona dijo que tiene que estar, como AAAA-MM-DD, de la "
             "lista de días.",
}

_RELATIVAS = ("hoy", "manana", "pasado manana", "semana que viene", "proxima semana",
              "semana proxima", "mes que viene", "proximo mes", "mes proximo", "fin de mes")
_DIAS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")
_NUMERO = re.compile(r"\d+")


@dataclass
class Resultado:
    """Lo que Leda propone (`propuesta`, con los nombres del formulario), las personas para elegir
    quién la hace cuando hay más de una (`elegir`), lo que no se propuso y la persona tiene que
    saber (`avisos`, con su texto) y, para la auditoría, cada dato descartado con su motivo."""

    propuesta: dict[str, str] = field(default_factory=dict)
    elegir: list[dict[str, str]] = field(default_factory=list)
    avisos: list[dict[str, str]] = field(default_factory=list)
    descartados: list[dict[str, str]] = field(default_factory=list)

    def descartar(self, campo: str, motivo: str, aviso: str | None = None, **datos: str) -> None:
        self.descartados.append({"campo": campo, "motivo": motivo})
        if aviso is not None:
            self.avisos.append({"campo": campo, "motivo": aviso,
                                "texto": TEXTOS[(campo, aviso)].format(**datos)})


# --- Lo que falta y lo que recibe la IA ------------------------------------------------------

def _vacio(valor: Any) -> bool:
    return not (isinstance(valor, str) and valor.strip())


def lo_que_falta(escrito: Mapping[str, Any]) -> list[str]:
    """Los datos del formulario que están vacíos, en su orden."""
    return [c for c in CAMPOS if _vacio(escrito.get(c))]


def lo_que_se_pide(escrito: Mapping[str, Any], opciones: Mapping[str, Any]) -> list[str]:
    """Lo vacío que Leda puede proponer: la espera y el objetivo, sólo si hay de dónde elegir."""
    hay = {"espera_id": bool(opciones.get("tareas")), "objetivo_id": bool(opciones.get("objetivos"))}
    return [c for c in lo_que_falta(escrito) if hay.get(c, True)]


def _por_id(lista: Sequence[Mapping[str, Any]], clave: str, valor: Any) -> Mapping[str, Any] | None:
    return next((x for x in lista if x.get(clave) == valor), None)


def _integrante(opciones, membership_id: Any) -> Mapping[str, Any] | None:
    return _por_id(opciones.get("integrantes") or [], "membership_id", membership_id)


def _politica(opciones, integrante) -> Mapping[str, Any] | None:
    if integrante is None:
        return None
    return _por_id(opciones.get("politicas") or [], "area_id", integrante.get("area_id"))


def _evidencia_en_palabras(politica) -> list[str]:
    if politica is None:
        return []
    tipos = politica.get("tipos") or {}
    return [(tipos.get(k) or {}).get("en_palabras") or k.replace("_", " ")
            for k in politica.get("evidencia_requerida") or []]


def _con_codigos(opciones) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    objetivos = {f"O{i}": o for i, o in enumerate(opciones.get("objetivos") or [], 1)}
    tareas = {f"T{i}": t for i, t in enumerate(opciones.get("tareas") or [], 1)}
    return objetivos, tareas


def _hoy(opciones) -> date:
    return date.fromisoformat(str(opciones["hoy"]))


def entrada_de_la_ia(texto: str, escrito: Mapping[str, Any],
                     opciones: Mapping[str, Any]) -> dict[str, Any]:
    """Lo que recibe la IA: sólo del espacio de las opciones, sin ids ni los nombres del
    equipo."""
    objetivos, tareas = _con_codigos(opciones)
    hoy = _hoy(opciones)
    ya: dict[str, Any] = {}
    for campo in ("titulo", "descripcion", "criterio"):
        if not _vacio(escrito.get(campo)):
            ya[campo] = str(escrito[campo]).strip()
    objetivo = _por_id(opciones.get("objetivos") or [], "id", escrito.get("objetivo_id"))
    if objetivo is not None:
        ya["objetivo"] = objetivo["titulo"]
    espera = _por_id(opciones.get("tareas") or [], "id", escrito.get("espera_id"))
    if espera is not None:
        ya["espera"] = espera["titulo"]
    integrante = _integrante(opciones, escrito.get("responsable_id"))
    if integrante is not None:
        ya["quien_la_hace"] = {"nombre": integrante["nombre"], "area": integrante["area"],
                               "evidencia_que_pide": _evidencia_en_palabras(
                                   _politica(opciones, integrante))}
    if not _vacio(escrito.get("fecha")):
        try:
            ya["fecha"] = hechos.dia(date.fromisoformat(escrito["fecha"]), hoy)
        except ValueError:
            pass
    return {
        "texto": texto,
        "pide": [PARA_LA_IA[c] for c in lo_que_se_pide(escrito, opciones)],
        "ya_escrito": ya,
        "hoy": hechos.dia(hoy, hoy),
        "dias": [hechos.dia(hoy + timedelta(days=n), hoy) for n in range(DIAS_PROXIMOS + 1)],
        "objetivos": [{"codigo": c, "titulo": o["titulo"]} for c, o in objetivos.items()],
        "tareas_abiertas": [{"codigo": c, "titulo": t["titulo"],
                             "la_hace": t.get("responsable"), "objetivo": t.get("objetivo")}
                            for c, t in tareas.items()],
    }


# --- La llamada -------------------------------------------------------------------------------

def herramienta(pide: Sequence[str]) -> dict[str, Any]:
    """La herramienta de la respuesta, con sólo los datos que se piden (y, con el criterio, la
    parte que dice cómo se comprueba)."""
    datos = [d for d in _DATOS if d in pide or (d == "como_se_comprueba" and "criterio" in pide)]
    return {"type": "function", "function": {
        "name": NOMBRE_HERRAMIENTA,
        "description": "Los datos de la tarea que Leda le propone a la persona; vacío lo que no "
                       "se puede saber con lo que contó.",
        "parameters": {"type": "object",
                       "properties": {d: {"type": "string", "description": _DATOS[d]}
                                      for d in datos},
                       "additionalProperties": False}}}


def pedir(ia, entrada: Mapping[str, Any]) -> dict[str, Any]:
    """Una sola llamada a la IA del espacio (sin reintento: la persona puede volver a tocar), con
    la herramienta de la respuesta. Una IA sin configurar es `LookupError`; una respuesta cortada,
    sin la herramienta o ilegible, `RespuestaInvalida`; lo demás (el plazo, la red, el cupo) se
    levanta como venga: para quien llama, la IA no respondió."""
    cliente = getattr(ia, "cliente", None)
    if cliente is None:
        raise LookupError(getattr(ia, "motivo", "La IA del espacio no está configurada."))
    parametros = getattr(cliente, "parametros", {}) or {}
    respuesta = cliente.completar({
        "temperature": 0,
        "max_tokens": int(parametros.get("tope_jugadas", TOPE_DE_SALIDA)),
        "messages": [{"role": "system", "content": INSTRUCCIONES},
                     {"role": "user",
                      "content": json.dumps(entrada, ensure_ascii=False, default=str)}],
        "tools": [herramienta(entrada.get("pide") or [])],
        "tool_choice": "auto",
    })
    return leer(respuesta)


def leer(respuesta: Any) -> dict[str, Any]:
    """Los datos de la llamada a la herramienta, o `RespuestaInvalida`."""
    if not isinstance(respuesta, dict):
        raise RespuestaInvalida("Respuesta ilegible.")
    sin_cortar(respuesta)
    try:
        mensaje = respuesta["choices"][0]["message"]
        llamadas = [c["function"] for c in mensaje.get("tool_calls") or []
                    if c["function"]["name"] == NOMBRE_HERRAMIENTA]
    except (KeyError, IndexError, TypeError, AttributeError) as e:
        raise RespuestaInvalida(f"Respuesta ilegible ({type(e).__name__}).") from e
    if not llamadas:
        raise RespuestaInvalida("La IA no llamó a la herramienta de la propuesta.")
    argumentos = llamadas[0].get("arguments")
    try:
        argumentos = json.loads(argumentos) if isinstance(argumentos, str) else argumentos
    except ValueError as e:
        raise RespuestaInvalida("Los argumentos de la herramienta no son JSON.") from e
    if not isinstance(argumentos, dict):
        raise RespuestaInvalida("Los argumentos de la herramienta no son un objeto.")
    return argumentos


# --- Lo que decide el código ------------------------------------------------------------------

def _normal(texto: str) -> str:
    sin_marcas = "".join(c for c in unicodedata.normalize("NFD", texto)
                         if unicodedata.category(c) != "Mn")
    return " ".join("".join(c if c.isalnum() else " " for c in sin_marcas.casefold()).split())


def _contiene(texto: str, frase: str) -> bool:
    return f" {frase} " in f" {texto} "


def la_fecha_esta_dicha(texto: str, fecha: date) -> bool:
    """Si el texto dice esa fecha: su número, el nombre de su día de la semana o una palabra que
    nombra un día ("hoy", "mañana", "la semana que viene"...). El código no calcula a qué día se
    refiere la palabra: eso lo hizo la IA con la lista de días; acá sólo se comprueba que la
    persona dijo algo de cuándo."""
    normal = _normal(texto)
    if str(fecha.day) in {n.lstrip("0") for n in _NUMERO.findall(normal)}:
        return True
    if _contiene(normal, _DIAS[fecha.weekday()]):
        return True
    return any(_contiene(normal, r) for r in _RELATIVAS)


def _cadena(valor: Any) -> str | None:
    if not isinstance(valor, str):
        return None
    limpio = " ".join(valor.split())
    return limpio or None


def _problema_del_texto(texto: str, permitidos: Sequence[str], largo: int) -> str | None:
    """`None` si el texto sirve; si no, el motivo (`largo`, `dato`, `nombre`)."""
    if len(texto) > largo:
        return "largo"
    for punto in puntos_del_criterio(texto) or [texto]:
        problema = problema_del_ejemplo(punto, permitidos)
        if problema is not None:
            return "largo" if problema == "largo" else problema.split(":")[0]
    return None


def revisar(crudo: Mapping[str, Any], *, texto: str, escrito: Mapping[str, Any],
            opciones: Mapping[str, Any], coinciden: Callable[[str], list[dict[str, Any]]],
            objetivo_de: Callable[[str], str | None]) -> Resultado:
    """Lo que vale de la propuesta de la IA. `coinciden(dicho)`: los integrantes del espacio que
    coinciden con lo dicho (con los apodos); `objetivo_de(task_id)`: el objetivo de una tarea del
    espacio."""
    r = Resultado()
    pide = set(lo_que_se_pide(escrito, opciones))
    objetivos, tareas = _con_codigos(opciones)

    # Quién la hace: sólo con palabras del texto, y alguien de este equipo.
    responsable = escrito.get("responsable_id") or None
    dicho = _cadena(crudo.get("responsable")) if "responsable_id" in pide else None
    if dicho is not None:
        palabras_del_texto = set(_normal(texto).split())
        if not set(_normal(dicho).split()) <= palabras_del_texto:
            r.descartar("responsable", "no_lo_dijo")
        else:
            encontrados = []
            for f in coinciden(dicho):
                integrante = _integrante(opciones, str(f["membership_id"]))
                if integrante is not None and integrante not in encontrados:
                    encontrados.append(integrante)
            if len(encontrados) == 1:
                responsable = encontrados[0]["membership_id"]
                r.propuesta["responsable_id"] = responsable
            elif encontrados:
                r.elegir = [{"membership_id": i["membership_id"], "nombre": i["nombre"],
                             "area": i["area"]} for i in encontrados]
                r.descartar("responsable", "varios", "varios", quien=dicho)
            else:
                r.descartar("responsable", "no_encontrado", "no_encontrado", quien=dicho)

    # La espera, de la lista.
    espera = escrito.get("espera_id") or None
    codigo = _cadena(crudo.get("espera")) if "espera_id" in pide else None
    if codigo is not None:
        tarea = tareas.get(codigo.upper())
        if tarea is None:
            r.descartar("espera", "no_existe")
        else:
            espera = tarea["id"]
            r.propuesta["espera_id"] = espera

    # El objetivo: el de la tarea que espera, si está abierto; si no, el de la lista.
    if "objetivo_id" in pide:
        abiertos = {o["id"] for o in opciones.get("objetivos") or []}
        del_de_la_espera = objetivo_de(espera) if espera else None
        codigo = _cadena(crudo.get("objetivo"))
        if del_de_la_espera in abiertos:
            r.propuesta["objetivo_id"] = del_de_la_espera
        elif codigo is not None and codigo.upper() in objetivos:
            r.propuesta["objetivo_id"] = objetivos[codigo.upper()]["id"]
        elif codigo is not None:
            r.descartar("objetivo", "no_existe")

    # La fecha: un día hábil que la persona dijo.
    fecha = crudo.get("fecha") if "fecha" in pide else None
    if fecha is not None and not (isinstance(fecha, str) and not fecha.strip()):
        try:
            dia = date.fromisoformat(fecha) if isinstance(fecha, str) else None
        except ValueError:
            dia = None
        if dia is None:
            r.descartar("fecha", "mal_formada", "no_dicha")
        elif dia.isoformat() not in set((opciones.get("calendario") or {}).get(
                "dias_habiles") or []):
            r.descartar("fecha", "no_es_habil", "no_es_habil")
        elif not la_fecha_esta_dicha(texto, dia):
            r.descartar("fecha", "no_dicha", "no_dicha")
        else:
            r.propuesta["fecha"] = dia.isoformat()

    # Los textos, con lo que es de esta tarea: lo que escribió la persona y los datos elegidos.
    permitidos = [texto, *(str(escrito.get(c) or "") for c in ("titulo", "descripcion",
                                                               "criterio"))]
    objetivo = _por_id(opciones.get("objetivos") or [], "id",
                       r.propuesta.get("objetivo_id") or escrito.get("objetivo_id"))
    if objetivo is not None:
        permitidos.append(objetivo["titulo"])
    tarea = _por_id(opciones.get("tareas") or [], "id", espera)
    if tarea is not None:
        permitidos += [tarea["titulo"], str(tarea.get("responsable") or "")]
    integrante = _integrante(opciones, responsable)
    if integrante is not None:
        permitidos += [integrante["nombre"], integrante["area"],
                       *_evidencia_en_palabras(_politica(opciones, integrante))]

    for campo in ("titulo", "descripcion", "criterio"):
        if campo not in pide:
            continue
        valor = _cadena(crudo.get(campo))
        if campo == "titulo" and valor is not None:
            valor = valor.rstrip(" .") or None
        if valor is None:
            r.descartar(campo, "vacio", "sin_proponer")
            continue
        problema = _problema_del_texto(valor, permitidos, LARGOS[campo])
        if problema is None and campo == "criterio":
            como = _cadena(crudo.get("como_se_comprueba"))
            if como is None or _normal(como) == "" or not _contiene(_normal(valor), _normal(como)):
                problema = "sin_comprobacion"
        if problema is not None:
            r.descartar(campo, problema, "sin_proponer")
        else:
            r.propuesta[campo] = valor
    return r
