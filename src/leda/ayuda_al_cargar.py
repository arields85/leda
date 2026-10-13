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
    (`entrega.problema_del_ejemplo`, punto por punto);
  - el criterio lo arma el código (J2-13): el resultado que propone la IA y, después, cómo se
    comprueba. Si la persona lo dijo, su manera, sólo si el juicio de la IA por el sentido
    (`juzgar_la_propuesta`, una llamada más, fuera del candado) dice que es concreta; si no, la
    evidencia que pide el área de quien la hace (o la del área del objetivo), en palabras de todos
    los días; sin evidencia, no se propone y el campo pide "Contame cómo se sabe que está
    terminada.".
- **La evidencia** no la propone la IA: elegir quién la hace marca la que pide su área, en la web.

**El criterio escrito, al cargar** (J2-9, J2-13 y J2-14; mecánica §13: "¿el resultado esperado
es concreto y verificable?"). Con o sin la ayuda, la carga juzga el criterio antes de guardarlo
(`juzgar_el_criterio`), por su sentido (la IA lee, el código decide, como la entrega del motor,
`lo_descrito_cubre`). J2-14: se toma como el que propone Leda. Si el área pide evidencia, cómo se
comprueba sale de ella y el criterio sólo tiene que decir un resultado: se rechaza el que no dice
ninguno (y el igual al título, sin importar la IA), siempre con un criterio propuesto (el
resultado más la evidencia, `criterio_con_la_evidencia`); el que lo dice se guarda tal cual. Si el
área no pide evidencia, tiene que decir cómo se comprueba: vacío o igual al título, no, sin la IA;
si no, la IA dice si dice una manera concreta y copia la parte que lo dice. Si la IA no juzga, no
se finge: `sin_revisar`, y la web carga con un aviso y un incidente.
"""

from __future__ import annotations

import json
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
    ("responsable", "no_encontrado"): "No encontré a «{quien}» en el equipo; elegí quién la hace.",
    ("criterio", "sin_como"): "Contame cómo se sabe que está terminada.",
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

El título, la descripción y el resultado que tiene que lograr la tarea los proponés vos, con lo \
que contó la persona. Cómo se comprueba que está hecha, sólo si la persona lo dijo o si recibiste \
la evidencia que pide el área de quien la hace; no inventás una manera. Quién la hace, la tarea \
que espera y la fecha van sólo si la persona los dijo. El objetivo, si se entiende de lo que \
contó.

Usás sólo lo que recibiste: ningún número, nombre, fecha ni dato que no esté ahí. Lo que no podés \
saber con lo que recibiste va vacío; la persona lo completa."""

_DATOS = {
    "titulo": "Una línea que dice qué hay que hacer, en imperativo.",
    "descripcion": "Lo que contó la persona sobre la tarea, ordenado y bien escrito, sin agregar "
                   "nada.",
    "resultado": "Lo que tiene que pasar para darla por terminada: el resultado de la tarea, en "
                 "una oración, sin decir cómo se comprueba.",
    "como_se_comprueba": "Cómo comprueba quien la revise que la tarea está hecha: la manera que "
                         "dijo la persona, si la dijo; si no, la evidencia que pide el área de "
                         "quien la hace, si la recibiste, aplicada a lo que hay que hacer. Si la "
                         "persona no lo dijo y no recibiste esa evidencia, va vacío.",
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
# Los datos que van sólo con otro: el resultado y cómo se comprueba, con el criterio (el código los
# junta, J2-13), y las palabras de la fecha, con la fecha.
_ACOMPANAN = {"resultado": "criterio", "como_se_comprueba": "criterio",
              "como_dijo_la_fecha": "fecha"}

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
    """La herramienta de la respuesta, con sólo los datos que se piden (el criterio, como su
    resultado y cómo se comprueba; con la fecha, las palabras con que se dijo)."""
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
            objetivo_de: Callable[[str], str | None], juicio: Juicio | None = None) -> Resultado:
    """Lo que vale de la propuesta de la IA. `coinciden(dicho)`: los integrantes del espacio que
    coinciden con lo dicho (con los apodos); `objetivo_de(task_id)`: el objetivo de una tarea del
    espacio; `juicio`: el de la manera de comprobarla que dio la IA (`juzgar_la_propuesta`)."""
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
        permitidos += [integrante["nombre"], integrante["area"]]
    evidencia = _evidencia_de_la_tarea(opciones, integrante, objetivo)
    permitidos += evidencia

    for campo in ("titulo", "descripcion"):
        if campo not in pide:
            continue
        valor = _cadena(crudo.get(campo))
        if campo == "titulo" and valor is not None:
            valor = valor.rstrip(" .") or None
        if valor is None:
            r.descartar(campo, "vacio", "sin_proponer")
            continue
        problema = _problema_del_texto(valor, permitidos, LARGOS[campo])
        if problema is not None:
            r.descartar(campo, problema, "sin_proponer")
        else:
            r.propuesta[campo] = valor
    if "criterio" in pide:
        _revisar_el_criterio(r, crudo, juicio, evidencia, permitidos)
    return r


# --- El criterio: desde la evidencia y juzgado por su sentido (J2-13) ---------------------------
#
# Mecánica §13: "¿el resultado esperado es concreto y verificable?". J2-9 juzgaba con palabras (la
# parte de cómo se comprueba tenía que traer una palabra que el resultado no dijera, sin una lista
# de palabras del marco), y en la prueba del usuario en el celular (2026-10-13) Leda propuso un
# criterio circular con sinónimos ("…está cambiado; se comprueba verificando… que fue
# reemplazado"): una regla de palabras no ve el sentido. La decisión del usuario (2026-10-13):
# - si la persona no dijo cómo se comprueba, la comprobación sale de la evidencia que pide el área
#   (`criterio_con_la_evidencia`, la misma política que marca las casillas, en palabras de todos
#   los días): una manera real, no inventada;
# - si un criterio dice cómo se comprueba lo juzga la IA por su sentido, como la entrega del motor
#   (`entrega`, `lo_descrito_cubre`): la IA dice si lo dice y copia la parte que lo dice; el código
#   decide con su juicio y con que esa parte esté dentro del criterio.
# La única guarda sin la IA no es una lista de palabras: un criterio vacío o igual al título.
#
# J2-14 (la segunda prueba del usuario en el celular, 2026-10-13): un criterio escrito a mano se
# juzgaba solo, sin mirar la evidencia que el área ya pedía, y el rechazo no proponía nada. Al
# cargar, el criterio escrito se toma como el que propone Leda: la persona escribe el resultado y
# cómo se comprueba sale de la evidencia que se pide (`juzgar_el_criterio` con `evidencia`).

def _oracion(texto: str) -> str:
    """El texto como una oración: con mayúscula al principio y su punto al final."""
    texto = " ".join(texto.split()).rstrip(" ;,")
    if not texto:
        return ""
    texto = texto[0].upper() + texto[1:]
    return texto if texto[-1] in ".!?" else f"{texto}."


def criterio_propuesto(resultado: str, como: str) -> str:
    """El criterio que propone Leda: el resultado y, después, cómo se comprueba."""
    return f"{_oracion(resultado)} {_oracion(como)}"


def criterio_con_la_evidencia(resultado: str, evidencia: Sequence[str]) -> str:
    """El criterio con la comprobación armada con la evidencia que pide el área, cada una en
    palabras de todos los días: el que propone la ayuda y el que trae un rechazo al cargar."""
    return f"{_oracion(resultado)} Se comprueba con lo que pide el área: {'; '.join(evidencia)}."


def evidencia_de_la_carga(opciones: Mapping[str, Any], responsable_id: Any,
                          tipos: Sequence[Any] | None) -> list[str]:
    """La evidencia que se eligió al cargar (`tipos`), en palabras de todos los días y en el orden
    del área de quien la hace (`_evidencia_en_palabras`: primero la que pide, después las otras que
    conoce): sólo los tipos que esa área conoce (uno que no, lo rechaza la base igual). Sin quién
    la hace o sin la política de su área, ninguna."""
    politica = _politica(opciones, _integrante(opciones, responsable_id))
    if politica is None or not tipos:
        return []
    conocidos = [*(politica.get("evidencia_requerida") or []),
                 *sorted(k for k in (politica.get("tipos") or {})
                         if k not in (politica.get("evidencia_requerida") or []))]
    elegidos = set(t for t in tipos if isinstance(t, str))
    return _evidencia_en_palabras({"tipos": politica.get("tipos") or {},
                                   "evidencia_requerida": [k for k in conocidos
                                                           if k in elegidos]})


def _evidencia_de_la_tarea(opciones, integrante, objetivo) -> list[str]:
    """La evidencia que pide el área de quien la hace; sin ella, la del área del objetivo si la
    tiene (hoy la base no les da un área a los objetivos); si no, ninguna."""
    politica = _politica(opciones, integrante)
    if politica is None and objetivo is not None and objetivo.get("area_id"):
        politica = _por_id(opciones.get("politicas") or [], "area_id", objetivo["area_id"])
    return _evidencia_en_palabras(politica)


def _revisar_el_criterio(r: Resultado, crudo: Mapping[str, Any], juicio: Juicio | None,
                         evidencia: Sequence[str], permitidos: Sequence[str]) -> None:
    """El criterio que se propone: el resultado de la IA con la manera de comprobarlo que dijo la
    persona, si el juicio por el sentido la aceptó; si no, con la evidencia del área; sin
    evidencia, no se propone y el campo pide cómo se sabe."""
    resultado = _cadena(crudo.get("resultado"))
    if resultado is None:
        r.descartar("criterio", "vacio", "sin_proponer")
        return
    problema = _problema_del_texto(resultado, permitidos, LARGOS["criterio"])
    if problema is not None:
        r.descartar("criterio", problema, "sin_proponer")
        return
    candidatos = []
    como = _cadena(crudo.get("como_se_comprueba"))
    if como is not None:
        if juicio is not None and juicio.motivo is None:
            candidatos.append(criterio_propuesto(resultado, como))
        else:
            r.descartar("criterio", juicio.motivo if juicio is not None else "sin_revisar")
    if evidencia:
        candidatos.append(criterio_con_la_evidencia(resultado, evidencia))
    for candidato in candidatos:
        problema = _problema_del_texto(candidato, permitidos, LARGOS["criterio"])
        if problema is None:
            r.propuesta["criterio"] = candidato
            return
    if candidatos:
        r.descartar("criterio", problema, "sin_proponer")
    else:
        r.descartar("criterio", "sin_como_se_comprueba", "sin_como")


NOMBRE_DEL_JUICIO = "revisar_el_criterio"

INSTRUCCIONES_DEL_JUICIO = """\
Sos Leda, la project manager del equipo. Alguien está cargando una tarea en la plataforma y \
escribió su criterio de aceptación: lo que tiene que pasar para darla por terminada. Quien la \
revise tiene que poder comprobarlo. Tu trabajo es leer el criterio y decir, por lo que significa \
y no por las palabras que usa, si dice una manera concreta de comprobar que la tarea está hecha: \
qué se mira, se prueba, se mide o se entrega, distinto del resultado mismo. Si sólo vuelve a \
decir el resultado o el título, aunque sea con otras palabras, no lo dice. Si lo dice, copiás tal \
cual la parte del criterio que lo dice. No corregís ni completás el criterio."""


# J2-14: con la evidencia que pide el área, el criterio sólo tiene que decir el resultado; la IA
# dice si lo dice y, en la misma llamada, escribe el resultado de la tarea, que el código usa para
# proponer un criterio si lo rechaza (el resultado más la evidencia del área).
INSTRUCCIONES_DEL_RESULTADO = """\
Sos Leda, la project manager del equipo. Alguien está cargando una tarea en la plataforma y \
escribió su criterio de aceptación: lo que tiene que pasar para darla por terminada. Cómo se \
comprueba que pasó lo dice la evidencia que pide el área (evidencia_que_pide_el_area), así que el \
criterio no necesita decirlo. Tu trabajo es leer el criterio y decir, por lo que significa y no \
por las palabras que usa, si dice un resultado: algo que tiene que quedar hecho o pasar con la \
tarea. Si no dice ninguno, no lo dice. Además escribís el resultado de la tarea en una oración, \
con lo que dicen el título, la descripción y el criterio, sin decir cómo se comprueba y sin \
agregar ningún dato que no esté ahí: si el criterio no se puede usar, Leda lo propone con la \
evidencia del área. No corregís el criterio."""


def entrada_del_juicio(titulo: str, descripcion: str, criterio: str,
                       evidencia: Sequence[str] = ()) -> dict[str, Any]:
    """Lo que recibe la IA para juzgar el criterio: sólo la tarea y, si el área pide evidencia,
    esa evidencia en palabras de todos los días."""
    entrada: dict[str, Any] = {"titulo": titulo, "descripcion": descripcion, "criterio": criterio}
    if evidencia:
        entrada["evidencia_que_pide_el_area"] = list(evidencia)
    return entrada


def herramienta_del_juicio() -> dict[str, Any]:
    return {"type": "function", "function": {
        "name": NOMBRE_DEL_JUICIO,
        "description": "Si el criterio de aceptación dice una manera concreta de comprobar que la "
                       "tarea está hecha, y la parte que lo dice.",
        "parameters": {
            "type": "object",
            "properties": {
                "dice_como_se_comprueba": {
                    "type": "boolean",
                    "description": "Si el criterio dice una manera concreta de comprobar que la "
                                   "tarea está hecha (qué se mira, se prueba, se mide o se "
                                   "entrega), distinta del resultado; no, si sólo vuelve a decir "
                                   "el resultado o el título, aunque sea con otras palabras."},
                "como_se_comprueba": {
                    "type": "string",
                    "description": "La parte del criterio que dice cómo se comprueba, copiada tal "
                                   "cual del criterio; vacío si no lo dice."}},
            "required": ["dice_como_se_comprueba", "como_se_comprueba"],
            "additionalProperties": False}}}


def herramienta_del_resultado() -> dict[str, Any]:
    """La herramienta del juicio con la evidencia del área (J2-14): si dice un resultado y el
    resultado de la tarea."""
    return {"type": "function", "function": {
        "name": NOMBRE_DEL_JUICIO,
        "description": "Si el criterio de aceptación dice un resultado, y el resultado de la "
                       "tarea en una oración.",
        "parameters": {
            "type": "object",
            "properties": {
                "dice_un_resultado": {
                    "type": "boolean",
                    "description": "Si el criterio dice algo que tiene que quedar hecho o pasar "
                                   "con la tarea; no, si no dice ninguno."},
                "resultado": {
                    "type": "string",
                    "description": "El resultado de la tarea en una oración, con lo que dicen el "
                                   "título, la descripción y el criterio, sin decir cómo se "
                                   "comprueba y sin agregar ningún dato."}},
            "required": ["dice_un_resultado", "resultado"],
            "additionalProperties": False}}}


@dataclass(frozen=True)
class Juicio:
    """Lo que se decidió de un criterio: `motivo` `None` si sirve; sin evidencia del área,
    `sin_comprobacion` si no dice cómo se comprueba; con ella (J2-14), `sin_resultado` si no dice
    ningún resultado, con el criterio que propone Leda (`propuesta`) o, si no se pudo armar, la
    causa (`falla`, para el incidente); y `sin_revisar` si la IA no lo juzgó (con `falla`)."""

    motivo: str | None
    falla: BaseException | None = None
    propuesta: str | None = None


def sin_nada_que_juzgar(titulo: str, criterio: str) -> bool:
    """Si el criterio está vacío (sin una letra ni un número) o es el título mismo: no hace falta
    la IA para saber que no dice cómo se comprueba. No es una lista de palabras."""
    normal = _normal(criterio or "")
    return not normal or normal == _normal(titulo or "")


def juzgar_el_criterio(ia, *, titulo: str, descripcion: str, criterio: str,
                       evidencia: Sequence[str] = (), contexto: Sequence[str] = ()) -> Juicio:
    """Si el criterio sirve. Una sola llamada a la IA del espacio (sin reintento), que lo juzga
    por su sentido; el código decide.

    - **Sin `evidencia`** (el área no pide ninguna, o es la manera que dio la ayuda): tiene que
      decir cómo se comprueba. Vacío o igual al título, no, sin la IA; si no, sí sólo si la IA
      dijo que sí y copió una parte que está dentro del criterio.
    - **Con `evidencia`** (la que pide el área, en palabras de todos los días; J2-14): cómo se
      comprueba sale de ella, y el criterio sólo tiene que decir un resultado. Vacío o igual al
      título, no, diga lo que diga la IA; si no, lo que diga la IA. Un rechazo trae el criterio
      que propone Leda: el resultado que escribió la IA más esa evidencia, si pasa los controles
      de lo inventado (`contexto`: los otros datos de esta tarea que puede nombrar).

    Una IA que no responde, que no juzgó o cuyo juicio no cierra: `sin_revisar`, nunca un rechazo
    ni un visto bueno; salvo lo que se rechaza sin ella, que queda rechazado sin propuesta."""
    titulo, descripcion, criterio = (" ".join((t or "").split())
                                     for t in (titulo, descripcion, criterio))
    evidencia = [e for e in (" ".join(str(x).split()) for x in evidencia) if e]
    if evidencia:
        return _juzgar_el_resultado(ia, titulo, descripcion, criterio, evidencia, contexto)
    if sin_nada_que_juzgar(titulo, criterio):
        return Juicio("sin_comprobacion")
    try:
        crudo = _pedir_el_juicio(ia, entrada_del_juicio(titulo, descripcion, criterio))
    except Exception as falla:  # noqa: BLE001 -- cualquier falla de la IA es que no juzgó
        return Juicio("sin_revisar", falla)
    dice, como = crudo.get("dice_como_se_comprueba"), crudo.get("como_se_comprueba")
    if not isinstance(dice, bool):
        return Juicio("sin_revisar", RespuestaInvalida("La IA no dijo si se comprueba."))
    if not dice:
        return Juicio("sin_comprobacion")
    if not isinstance(como, str) or not _normal(como):
        return Juicio("sin_revisar", RespuestaInvalida("La IA no copió cómo se comprueba."))
    if not _contiene(_normal(criterio), _normal(como)):
        return Juicio("sin_revisar", RespuestaInvalida(
            "La parte que copió la IA no está en el criterio."))
    return Juicio(None)


def _juzgar_el_resultado(ia, titulo: str, descripcion: str, criterio: str,
                         evidencia: Sequence[str], contexto: Sequence[str]) -> Juicio:
    """El juicio con la evidencia del área (J2-14): ver `juzgar_el_criterio`."""
    sin_nada = sin_nada_que_juzgar(titulo, criterio)
    try:
        crudo = _pedir_el_juicio(ia, entrada_del_juicio(titulo, descripcion, criterio, evidencia),
                                 INSTRUCCIONES_DEL_RESULTADO, herramienta_del_resultado())
    except Exception as falla:  # noqa: BLE001 -- cualquier falla de la IA es que no juzgó
        return Juicio("sin_resultado", falla) if sin_nada else Juicio("sin_revisar", falla)
    dice = crudo.get("dice_un_resultado")
    if not sin_nada:
        if not isinstance(dice, bool):
            return Juicio("sin_revisar", RespuestaInvalida("La IA no dijo si hay un resultado."))
        if dice:
            return Juicio(None)
    permitidos = [titulo, descripcion, criterio, *evidencia, *contexto]
    propuesta, problema = _propuesta_del_resultado(crudo.get("resultado"), evidencia, permitidos)
    if propuesta is None:
        return Juicio("sin_resultado", RespuestaInvalida(
            f"No se pudo proponer un criterio: el resultado de la IA no sirve ({problema})."))
    return Juicio("sin_resultado", propuesta=propuesta)


def _propuesta_del_resultado(resultado: Any, evidencia: Sequence[str],
                             permitidos: Sequence[str]) -> tuple[str | None, str | None]:
    """El criterio que propone Leda al rechazar uno escrito: el resultado de la IA más la
    evidencia del área, como en la ayuda, sólo si pasa los controles del texto (el largo, y ningún
    número ni nombre que no esté en la tarea); si no, `None` y el motivo."""
    resultado = _cadena(resultado)
    if resultado is None:
        return None, "vacio"
    candidato = criterio_con_la_evidencia(resultado, evidencia)
    problema = _problema_del_texto(candidato, permitidos, LARGOS["criterio"])
    return (candidato, None) if problema is None else (None, problema)


def juzgar_la_propuesta(ia, crudo: Mapping[str, Any] | None,
                        escrito: Mapping[str, Any]) -> Juicio | None:
    """El juicio de la manera de comprobarla que dio la IA al proponer (la que dijo la persona),
    con el mismo `juzgar_el_criterio` de la carga; `None` si no hay nada que juzgar (el criterio
    ya está escrito, o la IA no dio el resultado o la manera). Se llama fuera del candado de la
    web, entre la propuesta y lo que decide el código (`revisar`)."""
    crudo = crudo or {}
    if not _vacio(escrito.get("criterio")):
        return None
    resultado, como = _cadena(crudo.get("resultado")), _cadena(crudo.get("como_se_comprueba"))
    if resultado is None or como is None:
        return None
    titulo = (str(escrito.get("titulo") or "").strip() if not _vacio(escrito.get("titulo"))
              else _cadena(crudo.get("titulo")) or "")
    descripcion = (str(escrito.get("descripcion") or "").strip()
                   if not _vacio(escrito.get("descripcion"))
                   else _cadena(crudo.get("descripcion")) or "")
    return juzgar_el_criterio(ia, titulo=titulo, descripcion=descripcion,
                              criterio=criterio_propuesto(resultado, como))


def _pedir_el_juicio(ia, entrada: Mapping[str, Any],
                     instrucciones: str = INSTRUCCIONES_DEL_JUICIO,
                     herramienta_: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Como `pedir`, con la herramienta del juicio (la de cómo se comprueba, o la del resultado
    con la evidencia del área)."""
    cliente = getattr(ia, "cliente", None)
    if cliente is None:
        raise LookupError(getattr(ia, "motivo", "La IA del espacio no está configurada."))
    return leer(cliente.completar({
        "temperature": 0,
        "max_tokens": _tope_de_salida(cliente),
        "messages": [{"role": "system", "content": instrucciones},
                     {"role": "user",
                      "content": json.dumps(entrada, ensure_ascii=False, default=str)}],
        "tools": [herramienta_ or herramienta_del_juicio()],
        "tool_choice": "auto",
    }), NOMBRE_DEL_JUICIO)
