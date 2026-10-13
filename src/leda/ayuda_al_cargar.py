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
  - la fecha, sólo si la persona la dijo (constitución §4: nunca una fecha que nadie dijo): la IA
    devuelve también las palabras con que la dijo (`como_dijo_la_fecha`), el código comprueba que
    están tal cual en el texto y calcula él mismo el día con ellas (`fecha_dicha`, con hoy y la
    frase entera del texto donde están; si dice "antes de" un día, el hábil anterior del
    calendario del espacio); vale sólo si es el mismo día que dio la IA y es hábil; un rango
    ("del 10 al 12") no es una fecha;
  - título, descripción y criterio, con los topes del formulario y sin un número ni un nombre que
    no estén en lo que escribió la persona o en los datos de esta tarea
    (`entrega.problema_del_ejemplo`, punto por punto); el criterio, además, con la parte que dice
    cómo se comprueba copiada tal cual dentro de él (la idea del alta congelada,
    `MOTIVO_CRITERIO_SIN_COMPROBACION`, comprobada por el código y no por la IA), y que agrega
    algo que el resto del criterio y el título no dicen (`lo_que_agrega`, J2-9).
- **La evidencia** no la propone la IA: elegir quién la hace marca la que pide su área, en la web.

**El criterio escrito, al cargar** (J2-9; mecánica §13: "¿el resultado esperado es concreto y
verificable?"). Con o sin la ayuda, la carga juzga el criterio antes de guardarlo
(`juzgar_el_criterio`): si no agrega nada al título no hace falta preguntarle a nadie ("No se");
si no, la IA del espacio copia la parte que dice cómo se comprueba (como la entrega del motor: la
IA lee, el código decide) y vale la misma regla de lo que agrega. Si la IA no juzga, no se finge:
`sin_revisar`, y la web carga con un aviso y un incidente.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from .calendario import DIAS as DIAS_DE_LA_SEMANA
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
# El tope de salida de la llamada. La propuesta puede llevar hasta 1500 caracteres de texto
# (título, descripción y criterio) más la parte que dice cómo se comprueba y el JSON, y un modelo
# que razona gasta parte del tope antes de contestar: el de elegir jugadas (1500) la podía cortar
# (revisión `review-6a44e26466b95395`), y redactar un solo mensaje ya pidió 2000. Una respuesta
# cortada igual es que la IA no respondió (`sin_cortar`), nunca una propuesta a medias.
TOPE_DE_SALIDA = 3000

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
        'No puse la fecha: dijiste "{dicho}", pero el {dia} no es día hábil en este espacio; '
        "elegila en el calendario.",
    ("fecha", "fuera_del_calendario"):
        'No puse la fecha: dijiste "{dicho}", pero el {dia} está fuera del calendario de este '
        "espacio; elegila en el calendario.",
    ("fecha", "no_entendida"):
        'No puse la fecha: no entendí qué día es "{dicho}"; elegila en el calendario.',
    ("fecha", "no_dicha"):
        "No puse la fecha: no encontré en lo que escribiste qué día es; elegila en el "
        "calendario.",
    ("fecha", "sin_habil_antes"):
        'No puse la fecha: dijiste "{dicho}", pero no encontré el día hábil anterior en el '
        "calendario de este espacio; elegila en el calendario.",
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
    "criterio": "El criterio de aceptación: qué tiene que pasar para darla por terminada y cómo "
                "lo comprueba quien la revise. Si la persona no dijo cómo se comprueba, proponé "
                "una manera concreta (qué se mira, se prueba o se entrega) con lo que contó, la "
                "tarea, el objetivo o la evidencia que pide el área, sin repetir el resultado con "
                "otras palabras.",
    "como_se_comprueba": "La parte del criterio que dice cómo se comprueba que la tarea está "
                         "hecha (qué se mira, se prueba o se entrega), copiada tal cual del "
                         "criterio; tiene que decir algo que el resultado no dice, sin repetir el "
                         "resultado con otras palabras.",
    "responsable": "Las palabras con que la persona nombró a quien va a hacer la tarea, tal cual "
                   "las escribió.",
    "espera": "El código (T1, T2...) de la tarea abierta que tiene que terminar antes de que "
              "esta pueda empezar.",
    "objetivo": "El código (O1, O2...) del objetivo al que contribuye la tarea.",
    "fecha": "El día para el que la persona dijo que tiene que estar, como AAAA-MM-DD, de la "
             "lista de días. Si dijo que tiene que estar antes de un día, es el día hábil "
             "anterior a ese.",
    "como_dijo_la_fecha": "Las palabras con que la persona dijo para cuándo tiene que estar, "
                          "copiadas tal cual de su texto y enteras, también las que dicen si es "
                          "antes de ese día.",
}
# Los datos que van sólo con otro: la parte del criterio que dice cómo se comprueba, con el
# criterio, y las palabras de la fecha, con la fecha.
_ACOMPANAN = {"como_se_comprueba": "criterio", "como_dijo_la_fecha": "fecha"}

# Las palabras de una fecha (`fecha_dicha`).
_MESES = {m: i for i, m in enumerate(
    ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
     "octubre", "noviembre", "diciembre"), 1)} | {"setiembre": 9}
# "por la mañana", "a la mañana", "esta mañana", "de mañana": una hora del día, no mañana (salvo
# "antes de mañana", que es un día).
_LA_MANANA = {"la", "esta", "de"}
# Lo que antecede al número de un día ("para el 22", "antes del 22", "el día 22").
_ANTES_DEL_DIA = {"el", "del", "dia", "al"}
_LA_SEMANA_QUE_VIENE = (("semana", "que", "viene"), ("proxima", "semana"), ("semana", "proxima"))
# Lo que une dos días en un rango o una alternativa ("del 10 al 12", "entre el 10 y el 12", "el
# lunes o el martes"), y lo que puede ir entre la unión y el día siguiente.
_UNEN = {"y", "e", "o", "u", "a", "al", "hasta"}
_ANTES_DEL_SEGUNDO = {"el", "del", "dia"}
# Una cantidad antes de "antes" ("dos días antes del jueves"): no es el día hábil anterior.
_CANTIDADES = {"dia", "dias", "semana", "semanas", "mes", "meses", "hora", "horas", "rato"}
# "22/10", "22 / 10" o "22/10/2026": una sola ficha, con la barra; con el guion, sólo con el año
# ("22-10-2026"): sin él, "10-12" es también del 10 al 12, y queda como una ficha que no es un día
# (sus números no se leen sueltos). Un número suelto al lado de otro ("la máquina 3 10 tornillos")
# no es un día y un mes.
_CON_BARRAS = re.compile(r"(?<!\d)(\d{1,2})\s*/\s*(\d{1,2})(?:\s*/\s*(\d{4}|\d{2}))?(?!\d)")
_CON_GUIONES = re.compile(r"(?<!\d)(\d{1,2})\s*-\s*(\d{1,2})(?:\s*-\s*(\d{4}))?(?!\d)")
_FICHA = re.compile(r"\d{1,2}/\d{1,2}(?:/\d{2,4})?|\d{1,2}-\d{1,2}|[^\W_]+")


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


def _dias_proximos(hoy: date, opciones) -> list[str]:
    """Hoy y los días que vienen, como los nombra el motor (`hechos.dia`), con ", no es día
    hábil" en los que no son hábiles en el calendario del espacio (para que la IA pueda dar el
    día hábil anterior a otro); sin la lista de días hábiles, sin marcas."""
    habiles = set((opciones.get("calendario") or {}).get("dias_habiles") or [])
    dias = []
    for n in range(DIAS_PROXIMOS + 1):
        dia = hoy + timedelta(days=n)
        nombre = hechos.dia(dia, hoy)
        dias.append(f"{nombre}, no es día hábil" if habiles and dia.isoformat() not in habiles
                    else nombre)
    return dias


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
        "dias": _dias_proximos(hoy, opciones),
        "objetivos": [{"codigo": c, "titulo": o["titulo"]} for c, o in objetivos.items()],
        "tareas_abiertas": [{"codigo": c, "titulo": t["titulo"],
                             "la_hace": t.get("responsable"), "objetivo": t.get("objetivo")}
                            for c, t in tareas.items()],
    }


# --- La llamada -------------------------------------------------------------------------------

def herramienta(pide: Sequence[str]) -> dict[str, Any]:
    """La herramienta de la respuesta, con sólo los datos que se piden (y, con el criterio, la
    parte que dice cómo se comprueba; con la fecha, las palabras con que se dijo)."""
    datos = [d for d in _DATOS if d in pide or _ACOMPANAN.get(d) in pide]
    return {"type": "function", "function": {
        "name": NOMBRE_HERRAMIENTA,
        "description": "Los datos de la tarea que Leda le propone a la persona; vacío lo que no "
                       "se puede saber con lo que contó.",
        "parameters": {"type": "object",
                       "properties": {d: {"type": "string", "description": _DATOS[d]}
                                      for d in datos},
                       "additionalProperties": False}}}


def _tope_de_salida(cliente) -> int:
    """`TOPE_DE_SALIDA`, y nunca menos que los topes de elegir jugadas y de redactar del
    espacio."""
    parametros = getattr(cliente, "parametros", {}) or {}
    return max(TOPE_DE_SALIDA, *(int(parametros.get(t) or 0)
                                 for t in ("tope_jugadas", "tope_redaccion")))


def pedir(ia, entrada: Mapping[str, Any]) -> dict[str, Any]:
    """Una sola llamada a la IA del espacio (sin reintento: la persona puede volver a tocar), con
    la herramienta de la respuesta. Una IA sin configurar es `LookupError`; una respuesta cortada,
    sin la herramienta o ilegible, `RespuestaInvalida`; lo demás (el plazo, la red, el cupo) se
    levanta como venga: para quien llama, la IA no respondió."""
    cliente = getattr(ia, "cliente", None)
    if cliente is None:
        raise LookupError(getattr(ia, "motivo", "La IA del espacio no está configurada."))
    respuesta = cliente.completar({
        "temperature": 0,
        "max_tokens": _tope_de_salida(cliente),
        "messages": [{"role": "system", "content": INSTRUCCIONES},
                     {"role": "user",
                      "content": json.dumps(entrada, ensure_ascii=False, default=str)}],
        "tools": [herramienta(entrada.get("pide") or [])],
        "tool_choice": "auto",
    })
    return leer(respuesta)


def leer(respuesta: Any, nombre: str = NOMBRE_HERRAMIENTA) -> dict[str, Any]:
    """Los datos de la llamada a la herramienta `nombre`, o `RespuestaInvalida`."""
    if not isinstance(respuesta, dict):
        raise RespuestaInvalida("Respuesta ilegible.")
    sin_cortar(respuesta)
    try:
        mensaje = respuesta["choices"][0]["message"]
        llamadas = [c["function"] for c in mensaje.get("tool_calls") or []
                    if c["function"]["name"] == nombre]
    except (KeyError, IndexError, TypeError, AttributeError) as e:
        raise RespuestaInvalida(f"Respuesta ilegible ({type(e).__name__}).") from e
    if not llamadas:
        raise RespuestaInvalida(f"La IA no llamó a la herramienta {nombre}.")
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


# --- La fecha que dijo la persona ---------------------------------------------------------------
#
# Constitución §4: nunca una fecha que nadie dijo. La IA nombra el día y copia las palabras con que
# la persona lo dijo; el código no le cree el día: busca esas palabras en el texto y calcula él
# mismo, con hoy, qué día dice la frase del texto donde están. Lo que entiende, y nada más:
# - "hoy", "mañana" (no "por la mañana", "a la mañana", "esta mañana" ni "de mañana", que son una
#   hora) y "pasado mañana";
# - el nombre de un día: el próximo, nunca hoy ("el viernes", "este viernes", "el viernes que
#   viene"; hoy miércoles, "el miércoles" es el de la semana que viene), o el de la semana que
#   viene si lo dice ("el viernes de la semana que viene", "de la próxima semana");
# - un número de día con lo que lo hace un día: "el 22", "del 22", "el día 22" (de este mes, o del
#   que viene si ya pasó), "22/10" (de este año, o del que viene si ya pasó), "22/10/2026" o
#   "22-10-2026", "el 22 de octubre" y "el viernes 23" (que tiene que ser viernes);
# - "antes de" uno de esos días ("antes del jueves", "antes del 22", "antes de mañana"): el día
#   hábil anterior del calendario del espacio, desde hoy (el usuario, 2026-10-13: "la persona dijo
#   'antes del jueves' no 'el jueves'"); las palabras de la IA tienen que traer el "antes", y con
#   una cantidad delante ("dos días antes del jueves") no se entiende.
# Un número suelto ("12 tornillos", "la máquina 3") nunca es un día, y "la semana que viene" sola
# no dice qué día. Un rango o una alternativa tampoco ("del 10-12", "del 10 al 12", "entre el 10 y
# el 12", "el lunes o el martes"): no dicen para cuándo. Si las palabras están en más de una frase
# con días distintos, no se entiende.

@dataclass(frozen=True)
class _Frase:
    """Una frase de fecha del texto: sus fichas (`desde` hasta `hasta`, sin incluir), su día
    (`None` si no es un día que exista, como "el 31 de febrero" o "el viernes 22" un jueves, o si
    es parte de un rango) y si dice "antes de" ese día (`antes`, y entonces empieza en "antes")."""

    desde: int
    hasta: int
    dia: date | None
    antes: bool = False


def _fichas_de_fecha(texto: str) -> list[str]:
    """Las palabras del texto sin mayúsculas ni acentos, con "22/10" (o "22-10-2026") como una
    sola, "10-12" como una sola que no es un día, y "q" como "que"."""
    sin_marcas = "".join(c for c in unicodedata.normalize("NFD", texto.casefold())
                         if unicodedata.category(c) != "Mn")
    con_barras = _CON_BARRAS.sub(lambda m: "/".join(g for g in m.groups() if g), sin_marcas)
    con_guiones = _CON_GUIONES.sub(
        lambda m: "/".join(m.groups()) if m.group(3) else f"{m.group(1)}-{m.group(2)}", con_barras)
    return ["que" if f == "q" else f for f in _FICHA.findall(con_guiones)]


def _es_un_dia_del_mes(valor: str) -> bool:
    return valor.isdigit() and len(valor) <= 2 and 1 <= int(valor) <= 31


def _empieza_un_numero_de_dia(fichas: Sequence[str], i: int) -> bool:
    ficha = fichas[i]
    if "/" in ficha:
        return True
    if not _es_un_dia_del_mes(ficha):
        return False
    previa = fichas[i - 1] if i else ""
    return (previa in _ANTES_DEL_DIA or previa in DIAS_DE_LA_SEMANA
            or (fichas[i + 1:i + 2] == ["de"] and fichas[i + 2:i + 3] != []
                and fichas[i + 2] in _MESES))


def _el_dia(dia: int, mes: int | None, anio: int | None, hoy: date) -> date | None:
    """El día con ese número: con el año, ese; con el mes, de este año o del que viene si ya
    pasó; sólo el número, de este mes o del que viene si ya pasó. `None` si no existe."""
    if anio is not None:
        try:
            return date(anio + 2000 if anio < 100 else anio, mes or 0, dia)
        except ValueError:
            return None
    meses = ([(hoy.year, mes), (hoy.year + 1, mes)] if mes is not None else
             [(hoy.year + (hoy.month - 1 + k) // 12, (hoy.month - 1 + k) % 12 + 1)
              for k in (0, 1)])
    for a, m in meses:
        try:
            candidato = date(a, m, dia)
        except ValueError:
            continue
        if candidato >= hoy:
            return candidato
    return None


def _numero_de_dia(fichas: Sequence[str], i: int, hoy: date) -> tuple[int, date | None]:
    """Hasta dónde llega la frase de un número de día que empieza en `i`, y su día."""
    ficha = fichas[i]
    if "/" in ficha:
        partes = [int(p) for p in ficha.split("/")]
        return i + 1, _el_dia(partes[0], partes[1], partes[2] if len(partes) == 3 else None, hoy)
    dia, mes, anio, hasta = int(ficha), None, None, i + 1
    if fichas[hasta:hasta + 1] == ["de"] and fichas[hasta + 1:hasta + 2] != [] \
            and fichas[hasta + 1] in _MESES:
        mes, hasta = _MESES[fichas[hasta + 1]], hasta + 2
        if fichas[hasta:hasta + 1] == ["de"] and fichas[hasta + 1:hasta + 2] != [] \
                and re.fullmatch(r"\d{4}", fichas[hasta + 1]):
            anio, hasta = int(fichas[hasta + 1]), hasta + 2
    return hasta, _el_dia(dia, mes, anio, hoy)


def _dia_de_la_semana(fichas: Sequence[str], i: int, hoy: date) -> tuple[int, date | None]:
    """Hasta dónde llega la frase del nombre de un día que está en `i`, y su día."""
    semana, hasta = DIAS_DE_LA_SEMANA.index(fichas[i]), i + 1
    if hasta < len(fichas) and _empieza_un_numero_de_dia(fichas, hasta):
        hasta, dia = _numero_de_dia(fichas, hasta, hoy)
        return hasta, dia if dia is not None and dia.weekday() == semana else None
    if fichas[hasta:hasta + 2] == ["que", "viene"]:
        hasta += 2
    else:
        j = hasta + (fichas[hasta:hasta + 1] == ["de"])
        j += fichas[j:j + 1] == ["la"]
        for frase in _LA_SEMANA_QUE_VIENE:
            if tuple(fichas[j:j + len(frase)]) == frase:
                lunes_que_viene = hoy + timedelta(days=7 - hoy.weekday())
                return j + len(frase), lunes_que_viene + timedelta(days=semana)
    return hasta, hoy + timedelta(days=(semana - hoy.weekday()) % 7 or 7)


def _es_una_hora(fichas: Sequence[str], i: int) -> bool:
    """"mañana" en "por la mañana", "esta mañana" o "de mañana" es una hora del día; en "antes de
    mañana", un día."""
    previa = fichas[i - 1] if i else ""
    return previa in _LA_MANANA and not (previa == "de" and fichas[i - 2:i - 1] == ["antes"])


def _con_el_antes(fichas: Sequence[str], f: _Frase) -> _Frase:
    """La frase con el "antes de" que la precede ("antes del jueves", "antes del día 22", "antes
    de mañana"), que empieza entonces en "antes"; con una cantidad delante ("dos días antes del
    jueves") no es un día. Sin "antes de", la misma frase."""
    k = f.desde
    k -= fichas[k - 1:k] == ["dia"] if k else 0
    k -= fichas[k - 1:k] == ["el"] if k else 0
    if k < 2 or fichas[k - 1] not in ("de", "del") or fichas[k - 2] != "antes":
        return f
    k -= 2
    previa = fichas[k - 1] if k else ""
    cantidad = previa in _CANTIDADES or previa.isdigit()
    return _Frase(k, f.hasta, None if cantidad else f.dia, antes=True)


def _sin_rangos(fichas: Sequence[str], frases: list[_Frase]) -> list[_Frase]:
    """Las frases, sin día las que son parte de un rango o de una alternativa: dos días unidos
    ("del 10 al 12", "entre el 10 y el 12", "el lunes o el martes", "del 10 a 12") o uno con
    "entre" delante. No dicen para cuándo tiene que estar."""
    empieza = {f.desde: n for n, f in enumerate(frases)}
    en_rango: set[int] = set()
    for n, f in enumerate(frases):
        k = f.desde
        while k and fichas[k - 1] in _ANTES_DEL_SEGUNDO:
            k -= 1
        if k and fichas[k - 1] == "entre":
            en_rango.add(n)
        j = f.hasta
        if j >= len(fichas) or fichas[j] not in _UNEN:
            continue
        j += 1
        while j < len(fichas) and fichas[j] in _ANTES_DEL_SEGUNDO:
            j += 1
        if j in empieza:
            en_rango |= {n, empieza[j]}
        elif (j < len(fichas) and _es_un_dia_del_mes(fichas[j])
              and (fichas[f.hasta - 1].isdigit() or "/" in fichas[f.hasta - 1])):
            en_rango.add(n)
    return [_Frase(f.desde, f.hasta, None, f.antes) if n in en_rango else f
            for n, f in enumerate(frases)]


def _frases_de_fecha(fichas: Sequence[str], hoy: date) -> list[_Frase]:
    frases: list[_Frase] = []
    i = 0
    while i < len(fichas):
        ficha = fichas[i]
        if ficha == "pasado" and fichas[i + 1:i + 2] == ["manana"]:
            frases.append(_Frase(i, i + 2, hoy + timedelta(days=2)))
            i += 2
            continue
        if ficha == "manana" and not _es_una_hora(fichas, i):
            frases.append(_Frase(i, i + 1, hoy + timedelta(days=1)))
        elif ficha == "hoy":
            frases.append(_Frase(i, i + 1, hoy))
        elif ficha in DIAS_DE_LA_SEMANA or _empieza_un_numero_de_dia(fichas, i):
            hasta, dia = (_dia_de_la_semana if ficha in DIAS_DE_LA_SEMANA
                          else _numero_de_dia)(fichas, i, hoy)
            frases.append(_Frase(i, hasta, dia))
            i = hasta
            continue
        i += 1
    return _sin_rangos(fichas, [_con_el_antes(fichas, f) for f in frases])


def _habil_anterior(dia: date, hoy: date, calendario: Mapping[str, Any] | None) -> date | None:
    """El día hábil del espacio anterior a `dia`: el primero hacia atrás, desde el día anterior
    hasta hoy, que está entre los días hábiles del calendario (`dias_habiles`, con sus
    feriados). `None` si no hay ninguno desde hoy, si el día anterior queda después del fin del
    calendario (no se sabe si es hábil) o sin calendario."""
    calendario = calendario or {}
    habiles = set(calendario.get("dias_habiles") or [])
    fin = str(calendario.get("hasta") or (max(habiles) if habiles else ""))
    anterior = dia - timedelta(days=1)
    if not fin or anterior.isoformat() > fin:
        return None
    while anterior >= hoy:
        if anterior.isoformat() in habiles:
            return anterior
        anterior -= timedelta(days=1)
    return None


def fecha_dicha(texto: str, dicho: str | None, hoy: date,
                calendario: Mapping[str, Any] | None = None) -> tuple[date | None, str | None]:
    """El día que dicen las palabras `dicho` en el texto de la persona, calculado por el código:
    `(día, None)`, o `(None, motivo)`: `no_dicha` si esas palabras no están tal cual en el texto
    (sin mayúsculas ni acentos); `no_entendida` si no son parte de una frase que nombra un solo
    día que existe. La frase es la del texto, entera: si la persona escribió "el viernes de la
    semana que viene" y la IA copió "el viernes", el día es el de la semana que viene.

    Si la frase dice "antes de" un día, las palabras tienen que traer el "antes" (si no,
    `no_entendida`) y el día es el hábil anterior de `calendario` (las opciones de la carga:
    `dias_habiles` y `hasta`), desde hoy; si no lo hay, `sin_habil_antes`."""
    buscadas = _fichas_de_fecha(dicho or "")
    if not buscadas:
        return None, "no_dicha"
    fichas = _fichas_de_fecha(texto)
    largo = len(buscadas)
    lugares = [i for i in range(len(fichas) - largo + 1) if fichas[i:i + largo] == buscadas]
    if not lugares:
        return None, "no_dicha"
    dias: set[tuple[date | None, bool]] = set()
    for f in _frases_de_fecha(fichas, hoy):
        for i in lugares:
            if f.desde < i + largo and i < f.hasta:
                # Con "antes de", lo que dijo la persona incluye el "antes".
                trae_el_antes = i <= f.desde < i + largo
                dias.add((f.dia, f.antes) if not f.antes or trae_el_antes else (None, True))
    if len(dias) != 1:
        return None, "no_entendida"
    ((dia, antes),) = dias
    if dia is None:
        return None, "no_entendida"
    if not antes:
        return dia, None
    anterior = _habil_anterior(dia, hoy, calendario)
    return (anterior, None) if anterior is not None else (None, "sin_habil_antes")


def _en_palabras(dia: date) -> str:
    """"sábado 17 de octubre", como lo nombra el motor (`hechos.dia`)."""
    return hechos.dia(dia).split(": ", 1)[1]


def _revisar_la_fecha(r: Resultado, fecha: Any, dicho: str | None, texto: str,
                      opciones: Mapping[str, Any]) -> None:
    try:
        de_la_ia = date.fromisoformat(fecha) if isinstance(fecha, str) else None
    except ValueError:
        de_la_ia = None
    if de_la_ia is None:
        r.descartar("fecha", "mal_formada", "no_dicha")
        return
    hoy = _hoy(opciones)
    calendario = opciones.get("calendario") or {}
    dia, motivo = fecha_dicha(texto, dicho, hoy, calendario)
    if dia is None:
        r.descartar("fecha", motivo, motivo, dicho=dicho or "")
        return
    if dia.isoformat() not in set(calendario.get("dias_habiles") or []):
        # Lo que se dice es el día de las palabras de la persona, no el de la IA.
        hasta = calendario.get("hasta")
        fuera = dia < hoy or (bool(hasta) and dia.isoformat() > str(hasta))
        motivo = "fuera_del_calendario" if fuera else "no_es_habil"
        r.descartar("fecha", motivo, motivo, dicho=dicho, dia=_en_palabras(dia))
    elif dia != de_la_ia:
        r.descartar("fecha", "no_coincide", "no_entendida", dicho=dicho)
    else:
        r.propuesta["fecha"] = dia.isoformat()


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

    # La fecha: el día que dicen las palabras de la persona, calculado por el código, si es el
    # mismo que dio la IA y es hábil.
    fecha = crudo.get("fecha") if "fecha" in pide else None
    if fecha is not None and not (isinstance(fecha, str) and not fecha.strip()):
        _revisar_la_fecha(r, fecha, _cadena(crudo.get("como_dijo_la_fecha")), texto, opciones)

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
            titulos = [str(escrito.get("titulo") or ""), str(crudo.get("titulo") or "")]
            if not _dice_como_se_comprueba(valor, _cadena(crudo.get("como_se_comprueba")),
                                           titulos):
                problema = "sin_comprobacion"
        if problema is not None:
            r.descartar(campo, problema, "sin_proponer")
        else:
            r.propuesta[campo] = valor
    return r


# --- Un criterio que diga cómo se comprueba (J2-9) ----------------------------------------------
#
# Lo que encontró el usuario en el celular (2026-10-13): un criterio propuesto cuya parte de cómo
# se comprueba sólo repetía el resultado ("…quedan listos… Se comprueba revisando que… estén
# listos…"), y una tarea cargada con el criterio "No se". La regla es una sola y general, nunca
# una lista de respuestas malas: la parte que dice cómo se comprueba tiene que traer una palabra
# con contenido que no esté en el resto del criterio ni en el título.
#
# No cuentan como contenido las palabras de función del castellano (artículos, preposiciones,
# conjunciones, pronombres y los verbos que sólo unen: ser, estar, haber, quedar) ni el
# vocabulario del acto mismo de comprobar o de estar terminada: es el marco de cualquier
# comprobación y nunca dice qué se mira, se prueba o se entrega.

_DE_FUNCION = frozenset("""
a al ante bajo con contra de del desde durante en entre hacia hasta mediante para por segun sin
so sobre tras el la los las lo un una unos unas y e ni o u pero sino que porque pues si como
cuando donde mientras cual cuales quien quienes cuyo cuya me te se nos le les mi mis tu tus su
sus este esta estos estas ese esa esos esas aquel aquella aquellos aquellas esto eso aquello ya
no tambien muy mas menos tan todo toda todos todas cada otro otra otros otras mismo misma mismos
mismas ser es son sea sean era eran fue fueron sera seran sido estar esta estan este esten
estaba estaban estado estada estados estadas estuvo haber ha han hay haya hayan habia habra
quedar queda quedan quede queden quedo quedaron quedara quedaran quedado quedada quedados
quedadas
""".split())
_DEL_MARCO = ("comprobar", "comprueba", "comprobado", "verificar", "revisar", "controlar",
              "chequear", "constatar", "confirmar", "probar", "prueba", "probado", "asegurar",
              "listo", "lista", "terminar", "terminado", "hecho", "hecha", "completar",
              "completo", "completa", "finalizar", "finalizado", "acabar", "acabado")
# Dos palabras son la misma si comparten al menos estas letras del principio ("integre" e
# "integración", "colgado" y "colgar").
_RAIZ_COMUN = 5


def _raiz(palabra: str) -> str:
    """La palabra sin la s o la n final y sin la vocal final, si es larga: "listos", "lista" y
    "listo" son "list"; "quedan", "qued"."""
    if len(palabra) > 4 and palabra[-1] in "sn":
        palabra = palabra[:-1]
    if len(palabra) > 4 and palabra[-1] in "aeo":
        palabra = palabra[:-1]
    return palabra


def _misma(a: str, b: str) -> bool:
    return a == b or len(os.path.commonprefix([a, b])) >= _RAIZ_COMUN


_MARCO = tuple(_raiz(p) for p in _DEL_MARCO)


def _con_contenido(texto: str) -> list[str]:
    """Las palabras con contenido del texto (sus raíces), sin mayúsculas ni acentos."""
    raices = (_raiz(p) for p in _normal(texto).split() if p not in _DE_FUNCION)
    return [r for r in raices if not any(_misma(r, m) for m in _MARCO)]


def lo_que_agrega(como: str, dicho: Sequence[str]) -> list[str]:
    """Las palabras con contenido de `como` (la parte que dice cómo se comprueba) que no están en
    `dicho` (el resto del criterio y el título): vacío si sólo repite lo dicho o no dice nada."""
    ya = [r for t in dicho for r in _con_contenido(t or "")]
    agrega: list[str] = []
    for r in _con_contenido(como or ""):
        if not any(_misma(r, d) for d in ya) and r not in agrega:
            agrega.append(r)
    return agrega


def _el_resto(criterio: str, como: str) -> str:
    """El criterio sin la parte que dice cómo se comprueba (los dos, sin mayúsculas ni
    acentos)."""
    return f" {_normal(criterio)} ".replace(f" {_normal(como)} ", " ", 1)


def _dice_como_se_comprueba(criterio: str, como: str | None, titulos: Sequence[str]) -> bool:
    """Si `como` está dentro del criterio y agrega algo que el resto del criterio y los títulos
    no dicen."""
    if como is None or not _normal(como) or not _contiene(_normal(criterio), _normal(como)):
        return False
    return bool(lo_que_agrega(como, [_el_resto(criterio, como), *titulos]))


NOMBRE_DEL_JUICIO = "revisar_el_criterio"

INSTRUCCIONES_DEL_JUICIO = """\
Sos Leda, la project manager del equipo. Alguien está cargando una tarea en la plataforma y \
escribió su criterio de aceptación: lo que tiene que pasar para darla por terminada. Quien la \
revise tiene que poder comprobarlo. Tu trabajo es leer el criterio y copiar, tal cual, la parte \
que dice cómo se comprueba que la tarea está hecha: qué se mira, se prueba, se mide o se \
entrega. Si el criterio no lo dice, o sólo repite el resultado o el título con otras palabras, \
va vacío. No corregís ni completás el criterio: sólo decís qué parte es esa."""


def entrada_del_juicio(titulo: str, descripcion: str, criterio: str) -> dict[str, str]:
    """Lo que recibe la IA para juzgar el criterio: sólo la tarea."""
    return {"titulo": titulo, "descripcion": descripcion, "criterio": criterio}


def herramienta_del_juicio() -> dict[str, Any]:
    return {"type": "function", "function": {
        "name": NOMBRE_DEL_JUICIO,
        "description": "La parte del criterio de aceptación que dice cómo se comprueba que la "
                       "tarea está hecha.",
        "parameters": {
            "type": "object",
            "properties": {"como_se_comprueba": {
                "type": "string",
                "description": "La parte del criterio que dice cómo se comprueba que la tarea "
                               "está hecha (qué se mira, se prueba, se mide o se entrega), "
                               "copiada tal cual del criterio; vacío si no lo dice o sólo "
                               "repite el resultado con otras palabras."}},
            "required": ["como_se_comprueba"],
            "additionalProperties": False}}}


@dataclass(frozen=True)
class Juicio:
    """Lo que se decidió del criterio escrito: `motivo` `None` si dice cómo se comprueba,
    `sin_comprobacion` si no, y `sin_revisar` si la IA no lo juzgó (con `falla`, para el
    incidente)."""

    motivo: str | None
    falla: BaseException | None = None


def no_agrega_nada(titulo: str, criterio: str) -> bool:
    """Si el criterio no agrega nada al título ("No se", "listo"): no hace falta la IA."""
    return not lo_que_agrega(criterio, [titulo])


def juzgar_el_criterio(ia, *, titulo: str, descripcion: str, criterio: str) -> Juicio:
    """El criterio que escribió la persona, al cargar: si no agrega nada al título, sin la IA;
    si no, una sola llamada a la IA del espacio (sin reintento), que copia la parte que dice
    cómo se comprueba, y la regla de lo que agrega. Una IA que no responde, que no juzgó o que
    copió algo que no está en el criterio: `sin_revisar`, nunca un rechazo ni un visto bueno."""
    titulo, descripcion, criterio = (" ".join((t or "").split())
                                     for t in (titulo, descripcion, criterio))
    if no_agrega_nada(titulo, criterio):
        return Juicio("sin_comprobacion")
    try:
        crudo = _pedir_el_juicio(ia, entrada_del_juicio(titulo, descripcion, criterio))
    except Exception as falla:  # noqa: BLE001 -- cualquier falla de la IA es que no juzgó
        return Juicio("sin_revisar", falla)
    como = crudo.get("como_se_comprueba")
    if not isinstance(como, str):
        return Juicio("sin_revisar", RespuestaInvalida("La IA no dijo cómo se comprueba."))
    if not _normal(como):
        return Juicio("sin_comprobacion")
    if not _contiene(_normal(criterio), _normal(como)):
        return Juicio("sin_revisar", RespuestaInvalida(
            "La parte que copió la IA no está en el criterio."))
    if not lo_que_agrega(como, [_el_resto(criterio, como), titulo]):
        return Juicio("sin_comprobacion")
    return Juicio(None)


def _pedir_el_juicio(ia, entrada: Mapping[str, Any]) -> dict[str, Any]:
    """Como `pedir`, con la herramienta del juicio."""
    cliente = getattr(ia, "cliente", None)
    if cliente is None:
        raise LookupError(getattr(ia, "motivo", "La IA del espacio no está configurada."))
    return leer(cliente.completar({
        "temperature": 0,
        "max_tokens": _tope_de_salida(cliente),
        "messages": [{"role": "system", "content": INSTRUCCIONES_DEL_JUICIO},
                     {"role": "user",
                      "content": json.dumps(entrada, ensure_ascii=False, default=str)}],
        "tools": [herramienta_del_juicio()],
        "tool_choice": "auto",
    }), NOMBRE_DEL_JUICIO)
