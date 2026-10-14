"""La ayuda de la IA al cargar una tarea en la plataforma (ADR 0023, punto 4; porción J2 de
`odd/tasks/plataforma-jerarquias.md`, con su diseño corto).

La persona cuenta en un recuadro libre qué quiere hacer y Leda propone lo que el formulario todavía
tiene vacío: título, descripción, criterio de aceptación, quién la hace, a qué tarea espera, el
objetivo y la fecha. Es la regla del mozo (`AGENTS.md`, punto 11): la IA propone y el código
decide qué vale; lo que no pasa no se propone y se dice por qué (nunca en silencio). Nada se carga
acá: la persona ve cada dato marcado, lo corrige o lo acepta, y confirma como siempre.

- **Qué recibe la IA** (`entrada_de_la_ia`), sólo del espacio de la carga: el texto, lo que ya
  está escrito, hoy y los días que vienen con su día de la semana (`hechos.dia`), los objetivos
  abiertos y las tareas abiertas para esperar con un código cada una (O1…, T1…), el área y la
  evidencia de quien la hace si ya se eligió y, como hechos (J2-18), el equipo que puede hacerla
  (P1…, con su nombre y su área), la evidencia que pide cada área y los tipos de evidencia del pack
  (E1…, en palabras de todos los días). Nunca un id.
- **Lo que decide el código** (`revisar`):
  - quién la hace: si la persona lo nombró, sólo si sus palabras están en el texto y son de
    alguien del equipo (`coinciden`: `fichas.integrantes_que_coinciden`, con los apodos); con dos
    o más, Leda no elige y las muestra (ADR 0020, decisión 3); si no es nadie del equipo, se dice
    y no se pone a otro. Si no nombró a nadie (J2-18), el que propone Leda por el trabajo y las
    áreas, sólo si su código es de alguien del equipo que puede hacerla (alguien lo revisa);
  - la evidencia (J2-18 y J2-19): la que propone Leda para esta tarea, y sólo esa (lo que pide el
    área de quien la hace es un dato que Leda tiene en cuenta, no un mínimo que se suma), sólo de
    los tipos que esa área conoce; se propone junto con el criterio y si la persona no tildó
    ninguna (en el formulario nada se tilda solo: lo tildado es de la persona);
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
    (`entrega.problema_del_ejemplo`, punto por punto); un nombre de los datos que la persona
    escribió mal ("cirelabs" por CoreLabs) vale escrito como está en los datos (J2-18);
  - el criterio (J2-17): lo escribe la IA entero, con sus palabras (la evidencia que va a quedar
    tildada, la que propone Leda o la que tildó la persona, es un dato para decir cómo se
    comprueba, no un texto para copiar), y lo juzga por su sentido otra llamada
    (`juzgar_la_propuesta`, fuera del candado), ya con esa evidencia (o, sin quién la hace, la del
    área del objetivo): con evidencia, que diga un
    resultado; sin ella, que diga cómo se comprueba. Si no pasa, el criterio que escribió el
    juicio; si tampoco, el de reserva (`criterio_con_la_evidencia`, sólo con evidencia). Leda
    propone siempre: "no sé" es un pedido de ayuda. Sin quién la hace (J2-18), ninguna
    comprobación inventada: el criterio dice qué tiene que quedar hecho y cómo se comprueba sólo
    si la persona lo dijo (`INSTRUCCIONES_DEL_JUICIO_SIN_QUIEN`): cómo se comprueba lo dirá la
    evidencia del área de quien la haga, y al cargar con ella basta un resultado (J2-14).
- **La ortografía** (J2-17 y J2-18): antes de la vista previa, la IA corrige la ortografía de lo
  que se escribió en los campos de texto y pone los nombres como están en los datos del equipo
  (`revisar_la_ortografia`); el código acepta cada palabra corregida sólo si es la misma palabra
  mal escrita (`palabra_por_palabra`), la que no queda como la escribió la persona, y arma el
  texto sobre el de la persona.

**El criterio escrito, al cargar** (J2-9, J2-13, J2-14 y J2-17; mecánica §13: "¿el resultado
esperado es concreto y verificable?"). Con o sin la ayuda, la carga juzga el criterio antes de
guardarlo (`juzgar_el_criterio`), por su sentido (la IA lee, el código decide, como la entrega del
motor, `lo_descrito_cubre`). Si el área pide evidencia, cómo se comprueba sale de ella y el
criterio sólo tiene que decir un resultado; si no la pide, tiene que decir cómo se comprueba. Lo
vacío o igual al título se rechaza sin importar la IA. Todo rechazo trae el criterio que escribe la
IA con sus palabras (el de reserva, si el suyo no pasa los controles); el que pasa se guarda tal
cual. Si la IA no juzga, no se finge: `sin_revisar`, y la web carga con un aviso y un incidente.
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
todavía están vacíos (pide). Completás todo lo que se pueda saber con lo que recibiste. Lo que \
devolvés es una propuesta: la persona ve cada dato marcado y lo acepta, lo corrige o lo borra.

Quién la hace: si la persona nombró a alguien, copiás sus palabras tal cual y no proponés a nadie \
más, aunque no lo encuentres en el equipo. Si no nombró a nadie, proponés a quien del equipo le \
corresponde hacerla por el trabajo que hay que hacer y por su área.

La evidencia: de los tipos de evidencia, proponés los que sirven para comprobar esta tarea en \
particular, al menos uno. Lo que pide cada área es un dato que tenés en cuenta para saber qué se \
suele pedir en ese trabajo, no una lista para copiar entera. Cada tipo que proponés aporta algo \
que los otros no: no proponés dos que digan lo mismo.

El título, la descripción y el criterio de aceptación los escribís vos, con lo que contó la \
persona, como los escribiría alguien del equipo que conoce el trabajo: con naturalidad, en \
oraciones simples y con buena ortografía. Los nombres de personas, áreas, objetivos y tareas los \
escribís como están en los datos, aunque la persona los haya escrito con otra ortografía. El \
criterio dice, en una o dos oraciones cortas, qué tiene que quedar hecho y cómo se comprueba, \
contado desde quien hace la tarea: qué hace y qué entrega esa persona, con lo que dijo quien la \
carga y con la evidencia que proponés (o la que ya eligió la persona), y sólo con esa; no lo \
contás desde quien la revisa, como algo que alguien más va a mirar. Si no sabés quién la hace, el criterio dice qué tiene que quedar hecho, y cómo se \
sabe sólo si la persona lo dijo: cómo se comprueba lo va a decir la evidencia del área de quien la \
haga. Los datos que recibís son hechos para entender la tarea, no textos para copiar: los contás \
con tus palabras, sin repetir sus etiquetas ni armar listas con ellos. Siempre proponés un \
criterio, aunque la persona no sepa cuál poner.

La tarea que espera, si la persona dijo que tiene que esperar a otra; el objetivo, si se entiende \
de lo que contó; los dos también cuando la persona los nombra con otra ortografía. La fecha, sólo \
si la persona la dijo.

Usás sólo lo que recibiste: ningún número, nombre, fecha ni dato que no esté ahí. Lo que no podés \
saber con lo que recibiste va vacío; la persona lo completa."""

_DATOS = {
    "titulo": "Una línea que dice qué hay que hacer, en imperativo, bien escrita.",
    "descripcion": "Lo que contó la persona sobre la tarea, ordenado y bien escrito, sin agregar "
                   "nada.",
    "criterio": "El criterio de aceptación, escrito con tus palabras en una o dos oraciones "
                "cortas: qué tiene que quedar hecho y cómo se comprueba, contado desde quien hace "
                "la tarea: qué hace y qué entrega esa persona.",
    "resultado": "Lo que tiene que quedar hecho, en una oración, sin decir cómo se comprueba.",
    "responsable": "Las palabras con que la persona nombró a quien va a hacer la tarea, tal cual "
                   "las escribió; vacío si no nombró a nadie.",
    "quien_la_hace": "Si la persona no nombró a nadie, el código (P1, P2...) de quien del equipo "
                     "le corresponde hacerla por el trabajo y por su área; vacío si nombró a "
                     "alguien o si no se puede saber.",
    "evidencia": "Los códigos (E1, E2...) de los tipos de evidencia que sirven para comprobar "
                 "esta tarea, separados por comas, sin dos que digan lo mismo.",
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
# Los datos que van sólo con otro: el resultado, con el criterio (para el criterio de reserva,
# J2-17), quien propone Leda, con quién la hace (J2-18), y las palabras de la fecha, con la fecha.
_ACOMPANAN = {"resultado": "criterio", "quien_la_hace": "responsable",
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
    """Lo que Leda propone (`propuesta`, con los nombres del formulario; la evidencia, como la
    lista de los tipos que eligió Leda para esta tarea: J2-19), las personas para elegir quién la hace
    cuando hay más de una (`elegir`), lo que no se propuso y la persona tiene que saber (`avisos`,
    con su texto) y, para la auditoría, cada dato descartado con su motivo y de dónde salió quién
    la hace (`responsable_de`: `dicho`, si la persona lo nombró; `leda`, si lo propuso Leda)."""

    propuesta: dict[str, Any] = field(default_factory=dict)
    elegir: list[dict[str, str]] = field(default_factory=list)
    avisos: list[dict[str, str]] = field(default_factory=list)
    descartados: list[dict[str, str]] = field(default_factory=list)
    # El criterio, entre `revisar` y `cerrar_el_criterio` (J2-17): lo que se juzga, fuera del
    # candado (`juzgar_la_propuesta`); y de quién es el que se propuso: el de la IA (`ia`), el que
    # escribió el juicio (`juicio`) o el de reserva (`reserva`), para la auditoría.
    por_juzgar: dict[str, Any] | None = None
    criterio_de: str | None = None
    responsable_de: str | None = None

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
    """La política del área de un integrante; sin área, ninguna (nunca la de una política que
    tampoco dice su área)."""
    if integrante is None or not integrante.get("area_id"):
        return None
    return _por_id(opciones.get("politicas") or [], "area_id", integrante.get("area_id"))


def quien_y_su_politica(opciones: Mapping[str, Any], membership_id: Any) -> tuple[
        Mapping[str, Any] | None, Mapping[str, Any] | None]:
    """Quién la hace y la política de su área, de las opciones de la carga: la misma búsqueda para
    revisar la evidencia escrita (`web_app._lo_escrito`) y para proponer (`revisar`)."""
    integrante = _integrante(opciones, membership_id) if membership_id else None
    return integrante, _politica(opciones, integrante)


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


def _puede_hacerla(integrante: Mapping[str, Any]) -> bool:
    """Si a alguien se le puede dar una tarea: que la revise otra persona activa (si no, la carga
    la rechaza: `sin_quien_la_revise` o `la_hace_y_la_revisa`)."""
    revisa = integrante.get("revisa") or {}
    return bool(revisa.get("membership_id")) and \
        revisa.get("membership_id") != integrante.get("membership_id")


def _equipo(opciones) -> dict[str, Mapping[str, Any]]:
    """Quienes pueden hacer una tarea, con un código cada uno (P1…), para que Leda proponga a uno
    (J2-18)."""
    return {f"P{i}": m for i, m in enumerate(
        (m for m in opciones.get("integrantes") or [] if _puede_hacerla(m)), 1)}


def _tipos_del_pack(opciones) -> dict[str, tuple[str, str]]:
    """Los tipos de evidencia que conocen las áreas del espacio (los del pack), con un código cada
    uno (E1…, por su nombre): el código, el tipo y cómo se dice en palabras de todos los días."""
    palabras: dict[str, str] = {}
    for politica in opciones.get("politicas") or []:
        for tipo in [*(politica.get("evidencia_requerida") or []), *(politica.get("tipos") or {})]:
            if tipo not in palabras:
                palabras[tipo] = _evidencia_en_palabras(
                    {"tipos": politica.get("tipos") or {}, "evidencia_requerida": [tipo]})[0]
    return {f"E{i}": (t, palabras[t]) for i, t in enumerate(sorted(palabras), 1)}


def _lista(valor: Any) -> list[str]:
    return [v for v in valor if isinstance(v, str)] if isinstance(valor, (list, tuple)) else []


def tipos_que_conoce(politica) -> set[str]:
    """Los tipos de evidencia que conoce la política de un área: los que pide y los que acepta
    (los mismos que acepta la carga, `tipo_no_es_de_la_politica`)."""
    if politica is None:
        return set()
    return set(politica.get("evidencia_requerida") or []) | set(politica.get("tipos") or {})


def tipos_del_espacio(opciones: Mapping[str, Any]) -> set[str]:
    """Los tipos de evidencia que conoce alguna área del espacio (los del pack)."""
    return {t for p in opciones.get("politicas") or [] for t in tipos_que_conoce(p)}


def se_propone_la_evidencia(escrito: Mapping[str, Any], opciones: Mapping[str, Any]) -> bool:
    """Si Leda propone la evidencia (J2-18 y J2-19): junto con el criterio, que dice cómo se
    comprueba con ella, y sólo si la persona no tildó ninguna. En el formulario nada se tilda
    solo (J2-19): un tipo tildado lo tildó la persona o lo aceptó de Leda, y es suyo, aunque sea
    de los que pide el área. Si quién la hace ya se eligió, además, que su área tenga una
    política; si no se eligió, que haya alguna."""
    if "criterio" not in lo_que_se_pide(escrito, opciones):
        return False
    if not opciones.get("politicas") or _lista(escrito.get("evidencia")):
        return False
    if _vacio(escrito.get("responsable_id")):
        return True
    return _politica(opciones, _integrante(opciones, escrito.get("responsable_id"))) is not None


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
    """Lo que recibe la IA: sólo del espacio de las opciones y sin ids; el equipo, las áreas y la
    evidencia, como hechos con un código (J2-18)."""
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
        elegida = evidencia_de_la_carga(opciones, integrante["membership_id"],
                                        _lista(escrito.get("evidencia")))
        if elegida:
            ya["evidencia_elegida"] = elegida
    if not _vacio(escrito.get("fecha")):
        try:
            ya["fecha"] = hechos.dia(date.fromisoformat(escrito["fecha"]), hoy)
        except ValueError:
            pass
    pide = [PARA_LA_IA[c] for c in lo_que_se_pide(escrito, opciones)]
    if se_propone_la_evidencia(escrito, opciones):
        pide.append("evidencia")
    return {
        "texto": texto,
        "pide": pide,
        "ya_escrito": ya,
        "hoy": hechos.dia(hoy, hoy),
        "dias": _dias_proximos(hoy, opciones),
        "objetivos": [{"codigo": c, "titulo": o["titulo"]} for c, o in objetivos.items()],
        "tareas_abiertas": [{"codigo": c, "titulo": t["titulo"],
                             "la_hace": t.get("responsable"), "objetivo": t.get("objetivo")}
                            for c, t in tareas.items()],
        "equipo": [{"codigo": c, "nombre": m["nombre"], "area": m["area"]}
                   for c, m in _equipo(opciones).items()],
        "areas": [{"area": p["area"], "evidencia_que_pide": _evidencia_en_palabras(p)}
                  for p in opciones.get("politicas") or []],
        "tipos_de_evidencia": [{"codigo": c, "en_palabras": palabras}
                               for c, (_, palabras) in _tipos_del_pack(opciones).items()],
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
            objetivo_de: Callable[[str], str | None]) -> Resultado:
    """Lo que vale de la propuesta de la IA. `coinciden(dicho)`: los integrantes del espacio que
    coinciden con lo dicho (con los apodos); `objetivo_de(task_id)`: el objetivo de una tarea del
    espacio. El criterio queda por juzgar (`por_juzgar`): lo juzga `juzgar_la_propuesta`, fuera del
    candado, y lo decide `cerrar_el_criterio`."""
    r = Resultado()
    pide = set(lo_que_se_pide(escrito, opciones))
    objetivos, tareas = _con_codigos(opciones)

    # Quién la hace: el que nombró la persona (sólo con palabras del texto, y alguien de este
    # equipo); si no nombró a nadie, el que propone Leda (J2-18). Si nombró a alguien que no es del
    # equipo, o a varios, Leda no pone a otro.
    responsable = escrito.get("responsable_id") or None
    if "responsable_id" in pide:
        responsable = _quien_la_hace(r, crudo, texto, opciones, coinciden)

    # La evidencia que va a quedar tildada (J2-19): la que propone Leda si la persona no tildó
    # ninguna, o la que tildó la persona; nunca la del área sumada sola.
    integrante = _integrante(opciones, responsable)
    if se_propone_la_evidencia(escrito, opciones):
        tipos = _la_evidencia_de_leda(r, crudo.get("evidencia"), opciones, integrante)
    else:
        tipos = _lista(escrito.get("evidencia"))

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

    # Los textos, con lo que es de esta tarea: lo que escribió la persona, los datos elegidos y los
    # nombres de los datos que la persona escribió mal (J2-18: "cirelabs" es CoreLabs).
    permitidos = [texto, *(str(escrito.get(c) or "") for c in ("titulo", "descripcion",
                                                               "criterio"))]
    permitidos += nombres_mal_escritos(texto, opciones)
    objetivo = _por_id(opciones.get("objetivos") or [], "id",
                       r.propuesta.get("objetivo_id") or escrito.get("objetivo_id"))
    if objetivo is not None:
        permitidos.append(objetivo["titulo"])
    tarea = _por_id(opciones.get("tareas") or [], "id", espera)
    if tarea is not None:
        permitidos += [tarea["titulo"], str(tarea.get("responsable") or "")]
    if integrante is not None:
        permitidos += [integrante["nombre"], integrante["area"]]
        evidencia = evidencia_de_la_carga(opciones, responsable, tipos)
    else:
        evidencia = _evidencia_de_la_tarea(opciones, None, objetivo)
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
        r.por_juzgar = _el_criterio_por_juzgar(r, crudo, escrito, evidencia, permitidos,
                                               sin_quien=integrante is None)
    return r


def _quien_la_hace(r: Resultado, crudo: Mapping[str, Any], texto: str,
                   opciones: Mapping[str, Any],
                   coinciden: Callable[[str], list[dict[str, Any]]]) -> str | None:
    """Quién la hace, si se pidió: el que nombró la persona, si es uno solo del equipo; con varios,
    para elegir; con nadie, se dice. Si no nombró a nadie, el que propone Leda, si su código es de
    alguien del equipo que puede hacerla."""
    dicho = _cadena(crudo.get("responsable"))
    if dicho is not None:
        if not set(_normal(dicho).split()) <= set(_normal(texto).split()):
            # Las palabras no son de la persona: no nombró a nadie con ellas.
            r.descartar("responsable", "no_lo_dijo")
        else:
            encontrados = []
            for f in coinciden(dicho):
                integrante = _integrante(opciones, str(f["membership_id"]))
                if integrante is not None and integrante not in encontrados:
                    encontrados.append(integrante)
            if len(encontrados) == 1:
                r.propuesta["responsable_id"] = encontrados[0]["membership_id"]
                r.responsable_de = "dicho"
                return encontrados[0]["membership_id"]
            if encontrados:
                r.elegir = [{"membership_id": i["membership_id"], "nombre": i["nombre"],
                             "area": i["area"]} for i in encontrados]
                r.descartar("responsable", "varios", "varios", quien=dicho)
            else:
                r.descartar("responsable", "no_encontrado", "no_encontrado", quien=dicho)
            return None
    codigo = _cadena(crudo.get("quien_la_hace"))
    if codigo is None:
        return None
    integrante = _equipo(opciones).get(codigo.upper())
    if integrante is None:
        r.descartar("responsable", "no_existe")
        return None
    r.propuesta["responsable_id"] = integrante["membership_id"]
    r.responsable_de = "leda"
    return integrante["membership_id"]


def _la_evidencia_de_leda(r: Resultado, crudo: Any, opciones: Mapping[str, Any],
                          integrante: Mapping[str, Any] | None) -> list[str]:
    """Los tipos de evidencia que propone Leda para esta tarea (J2-19: el conjunto que eligió, sin
    el del área sumado), sin repetir y por su nombre: sólo los que conoce el área de quien la hace
    (uno que no, lo rechazaría la carga). Sin quién la hace, ninguno: no hay área de dónde
    salgan."""
    if isinstance(crudo, str):
        fichas = [f for f in re.split(r"[\s,;]+", crudo) if f]
    else:
        fichas = [f.strip() for f in _lista(crudo) if f.strip()]
    if not fichas:
        return []
    politica = _politica(opciones, integrante)
    if politica is None:
        r.descartar("evidencia", "sin_quien_la_hace")
        return []
    por_codigo = _tipos_del_pack(opciones)
    conoce = tipos_que_conoce(politica)
    elegidos: list[str] = []
    for ficha in fichas:
        tipo = por_codigo.get(ficha.upper(), (None,))[0]
        if tipo is None:
            r.descartar("evidencia", "no_existe")
        elif tipo not in conoce:
            r.descartar("evidencia", "no_es_del_area")
        elif tipo not in elegidos:
            elegidos.append(tipo)
    elegidos.sort()
    if elegidos:
        r.propuesta["evidencia"] = elegidos
    return elegidos


# --- El criterio: con las palabras de Leda y juzgado por su sentido (J2-13, J2-14 y J2-17) ------
#
# Mecánica §13: "¿el resultado esperado es concreto y verificable?". J2-9 juzgaba con palabras y en
# la prueba del usuario en el celular (2026-10-13) Leda propuso un criterio circular con sinónimos:
# una regla de palabras no ve el sentido. Desde la J2-13, un criterio lo juzga la IA por su sentido,
# como la entrega del motor (`entrega`, `lo_descrito_cubre`): la IA dice si lo dice y el código
# decide. La única guarda sin la IA no es una lista de palabras: un criterio vacío o igual al título.
#
# J2-14: al cargar, el criterio escrito se toma como el que propone Leda: si el área pide evidencia,
# cómo se comprueba sale de ella y basta que diga un resultado; si no, tiene que decir cómo se
# comprueba.
#
# J2-17 (la segunda prueba del usuario en el celular, 2026-10-13): la propuesta "parece sacada del
# código": la armaba una plantilla. Es la regla del mozo (`AGENTS.md`, punto 11): la cocina da el
# hecho y la IA lo dice con naturalidad. Ahora la IA escribe el criterio entero, con sus palabras y
# con la evidencia del área como dato; el código no arma ninguna oración, salvo la de reserva
# (`criterio_con_la_evidencia`), sólo cuando la IA no respondió o su texto no pasó los controles. Y
# Leda propone siempre: "no sé" es un pedido de ayuda, también sin evidencia del área.

def _oracion(texto: str) -> str:
    """El texto como una oración: con mayúscula al principio y su punto al final."""
    texto = " ".join(texto.split()).rstrip(" ;,")
    if not texto:
        return ""
    texto = texto[0].upper() + texto[1:]
    return texto if texto[-1] in ".!?" else f"{texto}."


def criterio_con_la_evidencia(resultado: str, evidencia: Sequence[str]) -> str:
    """El criterio de reserva (J2-17): el resultado y la evidencia que pide el área, cada una en
    palabras de todos los días. Sólo cuando la IA no escribió un criterio que pase los controles:
    nunca se le pega a lo que escribió la IA."""
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


def _el_criterio_por_juzgar(r: Resultado, crudo: Mapping[str, Any], escrito: Mapping[str, Any],
                            evidencia: Sequence[str], permitidos: Sequence[str], *,
                            sin_quien: bool = False) -> dict[str, Any]:
    """Lo que se juzga del criterio que escribió la IA: el texto entero, si pasa los controles de
    lo inventado (si no, vacío: el juicio igual escribe uno), con el título y la descripción de la
    tarea (los escritos o los propuestos), la evidencia de quien la hace, lo que puede nombrar y
    si se sabe quién la hace (`sin_quien`, J2-18)."""
    criterio = _cadena(crudo.get("criterio"))
    if criterio is None:
        r.descartar("criterio", "vacio")
    else:
        problema = _problema_del_texto(criterio, permitidos, LARGOS["criterio"])
        if problema is not None:
            r.descartar("criterio", problema)
            criterio = None

    def de_la_tarea(campo: str) -> str:
        if not _vacio(escrito.get(campo)):
            return " ".join(str(escrito[campo]).split())
        return r.propuesta.get(campo) or ""

    return {"titulo": de_la_tarea("titulo"), "descripcion": de_la_tarea("descripcion"),
            "criterio": criterio or "", "evidencia": list(evidencia),
            "contexto": list(permitidos), "resultado": _cadena(crudo.get("resultado")),
            "sin_quien": sin_quien}


def juzgar_la_propuesta(ia, r: Resultado) -> Juicio | None:
    """El juicio por el sentido del criterio que escribió la IA al proponer, con el mismo
    `juzgar_el_criterio` de la carga y la evidencia del área de quien la hace, que ya resolvió
    `revisar`; `None` si el criterio no se pidió. Se llama fuera del candado de la web, entre
    `revisar` y `cerrar_el_criterio`; nunca levanta (una IA que no juzga es `sin_revisar`)."""
    if r.por_juzgar is None:
        return None
    p = r.por_juzgar
    return juzgar_el_criterio(ia, titulo=p["titulo"], descripcion=p["descripcion"],
                              criterio=p["criterio"], evidencia=p["evidencia"],
                              contexto=p["contexto"], sin_quien=p.get("sin_quien", False))


def cerrar_el_criterio(r: Resultado, juicio: Juicio | None) -> None:
    """El criterio que se propone: el que escribió la IA, si el juicio dice que sirve; si no, el
    que escribió el juicio; si tampoco, el de reserva (sólo con la evidencia del área y el
    resultado que dio la IA); si no hay ninguno, el campo dice que no se pudo proponer."""
    p = r.por_juzgar
    if p is None:
        return
    juicio = juicio or Juicio("sin_revisar")
    if p["criterio"] and juicio.motivo is None:
        r.propuesta["criterio"], r.criterio_de = p["criterio"], "ia"
        return
    if p["criterio"] or juicio.motivo == "sin_revisar":
        r.descartar("criterio", juicio.motivo or "sin_revisar")
    if juicio.propuesta:
        r.propuesta["criterio"] = juicio.propuesta
        r.criterio_de = "reserva" if juicio.de_reserva else "juicio"
        return
    reserva, _ = _de_reserva(p["resultado"], p["evidencia"], p["contexto"])
    if reserva is not None:
        r.propuesta["criterio"], r.criterio_de = reserva, "reserva"
        return
    r.descartar("criterio", "sin_propuesta", "sin_proponer")


def _de_reserva(resultado: Any, evidencia: Sequence[str],
                permitidos: Sequence[str]) -> tuple[str | None, str | None]:
    """El criterio de reserva, si hay evidencia del área y un resultado que, armado, pasa los
    controles del texto; si no, `None` y el motivo."""
    resultado = _cadena(resultado)
    if not evidencia:
        return None, "sin_evidencia"
    if resultado is None:
        return None, "vacio"
    candidato = criterio_con_la_evidencia(resultado, evidencia)
    problema = _problema_del_texto(candidato, permitidos, LARGOS["criterio"])
    return (candidato, None) if problema is None else (None, problema)


NOMBRE_DEL_JUICIO = "revisar_el_criterio"

# El criterio que escribe el juicio para proponerlo si el que juzga no sirve (J2-17), como lo
# describen las dos instrucciones del juicio.
_EL_DE_LEDA = """\
Además escribís tu propio criterio para esta tarea, que Leda le propone a la persona si el suyo no \
sirve: como lo escribiría alguien del equipo que conoce el trabajo, con naturalidad, en una o dos \
oraciones cortas y con buena ortografía, que dice qué tiene que quedar hecho y cómo se comprueba, \
contado desde quien hace la tarea: qué hace y qué entrega esa persona, no lo que alguien más va a \
mirar. {como} Usás sólo lo que dicen el título, la descripción y el criterio: ningún \
número, nombre ni dato que no esté ahí."""

_DEL_JUICIO = """\
Sos Leda, la project manager del equipo. Alguien está cargando una tarea en la plataforma y \
escribió su criterio de aceptación: lo que tiene que pasar para darla por terminada. Quien la \
revise tiene que poder comprobarlo. Tu trabajo es leer el criterio y decir, por lo que significa \
y no por las palabras que usa, si dice una manera concreta de comprobar que la tarea está hecha: \
qué se mira, se prueba, se mide o se entrega, distinto del resultado mismo. Si sólo vuelve a \
decir el resultado o el título, aunque sea con otras palabras, no lo dice. Si lo dice, copiás tal \
cual la parte del criterio que lo dice. No corregís ni completás el criterio.

"""

INSTRUCCIONES_DEL_JUICIO = _DEL_JUICIO + _EL_DE_LEDA.format(
    como="Cómo se comprueba lo decís con lo que, según la tarea, hace y entrega quien la hace.")

# J2-18: al proponer sin saber quién la hace no hay evidencia de un área de donde salga cómo se
# comprueba, y lo que "la tarea misma deja ver" salía flojo o circular (la ronda de la J2-17). El
# criterio de Leda dice entonces qué tiene que quedar hecho, y cómo se comprueba sólo si lo dice la
# tarea: lo demás lo dirá la evidencia de quien la haga (al cargar con ella basta un resultado).
INSTRUCCIONES_DEL_JUICIO_SIN_QUIEN = _DEL_JUICIO + _EL_DE_LEDA.format(
    como="Todavía no se sabe quién la hace: cómo se sabe lo decís sólo si lo dicen el título, la "
         "descripción o el criterio; si no lo dicen, decís sólo qué tiene que quedar hecho, "
         "porque cómo se comprueba lo va a decir la evidencia que pida el área de quien la haga.")


# J2-14: con la evidencia que pide el área, el criterio sólo tiene que decir el resultado; la IA
# dice si lo dice y, en la misma llamada, escribe su propio criterio (J2-17) y el resultado de la
# tarea, que el código usa para el criterio de reserva.
INSTRUCCIONES_DEL_RESULTADO = """\
Sos Leda, la project manager del equipo. Alguien está cargando una tarea en la plataforma y \
escribió su criterio de aceptación: lo que tiene que pasar para darla por terminada. Cómo se \
comprueba que pasó lo dice la evidencia que se va a pedir para esta tarea \
(evidencia_que_pide_el_area), así que el criterio no necesita decirlo. Tu trabajo es leer el criterio y decir, por lo que significa y no \
por las palabras que usa, si dice un resultado: algo que tiene que quedar hecho o pasar con la \
tarea. Si no dice ninguno, no lo dice. No corregís el criterio. También escribís el resultado de \
la tarea en una oración, sin decir cómo se comprueba.

""" + _EL_DE_LEDA.format(
    como="Cómo se comprueba lo decís con esa evidencia, y sólo con ella, contada con tus palabras "
         "como lo que entrega quien hace la tarea: es un dato para entender qué se entrega, no un "
         "texto para copiar, así que no repetís sus etiquetas ni armás una lista con ellas.")

_CRITERIO_DE_LEDA = {
    "type": "string",
    "description": "Tu propio criterio de aceptación para esta tarea, con tus palabras, en una o "
                   "dos oraciones cortas: qué tiene que quedar hecho y cómo se comprueba, contado "
                   "desde quien hace la tarea: qué hace y qué entrega esa persona; sin ningún "
                   "dato que no esté en lo que recibiste."}


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
                       "tarea está hecha, la parte que lo dice y tu propio criterio.",
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
                                   "cual del criterio; vacío si no lo dice."},
                "criterio": _CRITERIO_DE_LEDA},
            "required": ["dice_como_se_comprueba", "como_se_comprueba", "criterio"],
            "additionalProperties": False}}}


def herramienta_del_resultado() -> dict[str, Any]:
    """La herramienta del juicio con la evidencia del área (J2-14): si dice un resultado, el
    resultado de la tarea y el criterio que propone Leda (J2-17)."""
    return {"type": "function", "function": {
        "name": NOMBRE_DEL_JUICIO,
        "description": "Si el criterio de aceptación dice un resultado, el resultado de la tarea "
                       "en una oración y tu propio criterio.",
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
                                   "comprueba y sin agregar ningún dato."},
                "criterio": _CRITERIO_DE_LEDA},
            "required": ["dice_un_resultado", "resultado", "criterio"],
            "additionalProperties": False}}}


@dataclass(frozen=True)
class Juicio:
    """Lo que se decidió de un criterio: `motivo` `None` si sirve; sin evidencia del área,
    `sin_comprobacion` si no dice cómo se comprueba; con ella (J2-14), `sin_resultado` si no dice
    ningún resultado; y `sin_revisar` si la IA no lo juzgó (con `falla`). Un rechazo trae el
    criterio que propone Leda (`propuesta`, el que escribió la IA o, si no pasó los controles, el
    de reserva: `de_reserva`) o, si no se pudo, la causa (`falla`, para el incidente)."""

    motivo: str | None
    falla: BaseException | None = None
    propuesta: str | None = None
    de_reserva: bool = False


def sin_nada_que_juzgar(titulo: str, criterio: str) -> bool:
    """Si el criterio está vacío (sin una letra ni un número) o es el título mismo: no hace falta
    la IA para saber que no dice cómo se comprueba. No es una lista de palabras."""
    normal = _normal(criterio or "")
    return not normal or normal == _normal(titulo or "")


def juzgar_el_criterio(ia, *, titulo: str, descripcion: str, criterio: str,
                       evidencia: Sequence[str] = (), contexto: Sequence[str] = (),
                       sin_quien: bool = False) -> Juicio:
    """Si el criterio sirve. Una sola llamada a la IA del espacio (sin reintento), que lo juzga
    por su sentido y escribe su propio criterio; el código decide.

    - **Sin `evidencia`** (el área no pide ninguna): tiene que decir cómo se comprueba. Vacío o
      igual al título, no, diga lo que diga la IA; si no, sí sólo si la IA dijo que sí y copió una
      parte que está dentro del criterio. Un rechazo es `sin_comprobacion`.
    - **Con `evidencia`** (la que pide el área, en palabras de todos los días; J2-14): cómo se
      comprueba sale de ella, y el criterio sólo tiene que decir un resultado. Vacío o igual al
      título, no, diga lo que diga la IA; si no, lo que diga la IA. Un rechazo es `sin_resultado`.

    Todo rechazo trae el criterio que propone Leda (J2-17): el que escribió la IA, si pasa los
    controles de lo inventado (`contexto`: los otros datos de esta tarea que puede nombrar); si no,
    el de reserva, con la evidencia. Una IA que no responde, que no juzgó o cuyo juicio no cierra:
    `sin_revisar`, nunca un rechazo ni un visto bueno; salvo lo que se rechaza sin ella, que queda
    rechazado sin propuesta y con la falla.

    `sin_quien` (al proponer sin saber quién la hace, J2-18): el criterio que escribe la IA no
    inventa cómo se comprueba (`INSTRUCCIONES_DEL_JUICIO_SIN_QUIEN`)."""
    titulo, descripcion, criterio = (" ".join((t or "").split())
                                     for t in (titulo, descripcion, criterio))
    evidencia = [e for e in (" ".join(str(x).split()) for x in evidencia) if e]
    sin_nada = sin_nada_que_juzgar(titulo, criterio)
    rechazo = "sin_resultado" if evidencia else "sin_comprobacion"
    try:
        if evidencia:
            crudo = _pedir_el_juicio(ia, entrada_del_juicio(titulo, descripcion, criterio,
                                                            evidencia),
                                     INSTRUCCIONES_DEL_RESULTADO, herramienta_del_resultado())
        else:
            crudo = _pedir_el_juicio(ia, entrada_del_juicio(titulo, descripcion, criterio),
                                     INSTRUCCIONES_DEL_JUICIO_SIN_QUIEN if sin_quien
                                     else INSTRUCCIONES_DEL_JUICIO)
    except Exception as falla:  # noqa: BLE001 -- cualquier falla de la IA es que no juzgó
        return Juicio(rechazo, falla) if sin_nada else Juicio("sin_revisar", falla)
    if not sin_nada:
        sirve = _lo_que_dice(crudo, criterio, evidencia)
        if isinstance(sirve, Juicio):
            return sirve
        if sirve:
            return Juicio(None)
    permitidos = [titulo, descripcion, criterio, *evidencia, *contexto]
    propuesta, de_reserva, problema = _propuesta_del_juicio(crudo, evidencia, permitidos)
    if propuesta is None:
        return Juicio(rechazo, RespuestaInvalida(
            f"No se pudo proponer un criterio: lo que escribió la IA no sirve ({problema})."))
    return Juicio(rechazo, propuesta=propuesta, de_reserva=de_reserva)


def _lo_que_dice(crudo: Mapping[str, Any], criterio: str,
                 evidencia: Sequence[str]) -> bool | Juicio:
    """Si el juicio de la IA dice que el criterio sirve (un resultado, con la evidencia del área;
    cómo se comprueba, sin ella), o el `Juicio` `sin_revisar` si no juzgó o su juicio no cierra."""
    if evidencia:
        dice = crudo.get("dice_un_resultado")
        if not isinstance(dice, bool):
            return Juicio("sin_revisar", RespuestaInvalida("La IA no dijo si hay un resultado."))
        return dice
    dice, como = crudo.get("dice_como_se_comprueba"), crudo.get("como_se_comprueba")
    if not isinstance(dice, bool):
        return Juicio("sin_revisar", RespuestaInvalida("La IA no dijo si se comprueba."))
    if not dice:
        return False
    if not isinstance(como, str) or not _normal(como):
        return Juicio("sin_revisar", RespuestaInvalida("La IA no copió cómo se comprueba."))
    if not _contiene(_normal(criterio), _normal(como)):
        return Juicio("sin_revisar", RespuestaInvalida(
            "La parte que copió la IA no está en el criterio."))
    return True


def _propuesta_del_juicio(crudo: Mapping[str, Any], evidencia: Sequence[str],
                          permitidos: Sequence[str]) -> tuple[str | None, bool, str | None]:
    """El criterio que propone Leda al rechazar uno: el que escribió la IA, tal cual, si pasa los
    controles del texto (el largo, y ningún número ni nombre que no esté en la tarea); si no, el de
    reserva (sólo con la evidencia del área); si tampoco, `None` y el motivo. Devuelve también si
    es el de reserva."""
    propio = _cadena(crudo.get("criterio"))
    problema = "vacio"
    if propio is not None:
        problema = _problema_del_texto(propio, permitidos, LARGOS["criterio"])
        if problema is None:
            return propio, False, None
    reserva, otro = _de_reserva(crudo.get("resultado"), evidencia, permitidos)
    if reserva is not None:
        return reserva, True, None
    return None, False, problema if otro in ("sin_evidencia", "vacio") else otro


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


# --- La ortografía (J2-17) ---------------------------------------------------------------------
#
# El usuario (2026-10-13): "no es cambiar el significado de mis palabras, es corregir la
# ortografía… me está ayudando". Antes de la vista previa (que es la confirmación), la IA corrige la
# ortografía de lo que la persona escribió en los campos de texto y pone los nombres como están en
# los datos del equipo; nunca cambia cómo está redactado. La cocina no le cree: compara sólo una
# corrección con la misma cantidad de palabras y, palabra por palabra en su lugar (J2-18: "q" no
# anula "batería"), acepta la que es la misma palabra mal escrita (`_misma_palabra`) y deja como la
# escribió la persona la que no; arma el texto sobre el de la persona, cambiando sólo esas palabras
# (sus renglones y su puntuación quedan). Lo que no pasa queda como lo escribió, con un incidente
# que cuenta las palabras rechazadas (nunca cuáles).
#
# `_misma_palabra`, sin un diccionario: igual sin tildes ni mayúsculas; si es una palabra de un
# nombre de los datos, con pocas letras distintas para su largo; si no, que suene igual (las letras
# que se confunden al escribir) o con una diferencia chica que pueda ser un dedo: una letra de más,
# de menos, dos dadas vuelta o una cambiada por otra vecina en el teclado o que suena igual (J2-18:
# "mesa" por "masa" ya no pasa). Una palabra de una o dos letras sólo cambia de tildes o mayúsculas
# ("a" y "ha", "q" y "que" son otras palabras), y un número nunca. Lo que no puede ver sin un
# diccionario (dos palabras que suenan igual, como "casa" y "caza") lo muestra la vista previa,
# marcado, antes de confirmar.

NOMBRE_DE_LA_ORTOGRAFIA = "corregir_la_ortografia"
CAMPOS_DE_TEXTO = ("titulo", "descripcion", "criterio")

INSTRUCCIONES_DE_LA_ORTOGRAFIA = """\
Sos Leda, la project manager del equipo. Alguien está por cargar una tarea en la plataforma y \
escribió estos textos (textos). Antes de que los confirme, le corregís la ortografía: letras, \
tildes y mayúsculas, y los nombres de personas, áreas, objetivos y tareas escritos como están en \
los datos del equipo (nombres) cuando el texto nombra a uno de ellos. Devolvés cada texto con la \
ortografía corregida. No cambiás ninguna palabra por otra, no agregás ni sacás palabras y no \
cambiás el orden ni cómo está redactado: lo que dice y cómo lo dice es de la persona. Un texto que \
está bien escrito lo devolvés igual."""

_PALABRA = re.compile(r"[^\W_]+")


def _nombres_del_equipo(opciones: Mapping[str, Any]) -> list[str]:
    """Los nombres de los datos del espacio: integrantes, áreas, objetivos y tareas abiertas, sin
    repetir."""
    nombres: list[str] = []
    for lista, claves in (("integrantes", ("nombre", "area")), ("objetivos", ("titulo",)),
                          ("tareas", ("titulo", "responsable", "objetivo"))):
        for fila in opciones.get(lista) or []:
            for clave in claves:
                valor = fila.get(clave)
                if isinstance(valor, str) and valor.strip() and valor not in nombres:
                    nombres.append(valor)
    return nombres


def entrada_de_la_ortografia(textos: Mapping[str, str],
                             opciones: Mapping[str, Any]) -> dict[str, Any]:
    """Lo que recibe la IA para corregir la ortografía: los textos y los nombres del equipo de ese
    espacio (nada de otro)."""
    return {"textos": dict(textos), "nombres": _nombres_del_equipo(opciones)}


def herramienta_de_la_ortografia(campos: Sequence[str]) -> dict[str, Any]:
    return {"type": "function", "function": {
        "name": NOMBRE_DE_LA_ORTOGRAFIA,
        "description": "Cada texto con la ortografía corregida, sin cambiar cómo está redactado.",
        "parameters": {
            "type": "object",
            "properties": {c: {"type": "string",
                               "description": f"El texto «{c}» con la ortografía corregida."}
                           for c in campos},
            "required": list(campos),
            "additionalProperties": False}}}


def pedir_la_ortografia(ia, entrada: Mapping[str, Any]) -> dict[str, Any]:
    """Una sola llamada a la IA del espacio (sin reintento), como `pedir`."""
    cliente = getattr(ia, "cliente", None)
    if cliente is None:
        raise LookupError(getattr(ia, "motivo", "La IA del espacio no está configurada."))
    return leer(cliente.completar({
        "temperature": 0,
        "max_tokens": _tope_de_salida(cliente),
        "messages": [{"role": "system", "content": INSTRUCCIONES_DE_LA_ORTOGRAFIA},
                     {"role": "user",
                      "content": json.dumps(entrada, ensure_ascii=False, default=str)}],
        "tools": [herramienta_de_la_ortografia(list(entrada.get("textos") or {}))],
        "tool_choice": "auto",
    }), NOMBRE_DE_LA_ORTOGRAFIA)


def _sin_marcas(palabra: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", palabra.casefold())
                   if unicodedata.category(c) != "Mn")


def _como_suena(palabra: str) -> str:
    """La palabra (sin tildes ni mayúsculas) como suena en el castellano del Río de la Plata: las
    letras que se confunden al escribir porque suenan igual (b y v, s, z y c, la hache, ll e y, k,
    q y c)."""
    s = palabra.replace("ch", "\x01").replace("ll", "y").replace("h", "").replace("v", "b")
    s = re.sub(r"c(?=[ei])", "s", s.replace("z", "s")).replace("qu", "k").replace("c", "k")
    return s


# El teclado (con la ñ) y las letras que suenan igual: una letra cambiada por una de éstas puede ser
# un dedo o el oído; por otra, es otra palabra.
_TECLADO = {c: (fila, col) for fila, letras in enumerate(("qwertyuiop", "asdfghjklñ", "zxcvbnm"))
            for col, c in enumerate(letras)}
_SUENAN_IGUAL = {frozenset(p) for p in ("bv", "sz", "sc", "cz", "ck", "qk", "gj", "yi")}


def _se_confunden(a: str, b: str) -> bool:
    """Si una letra escrita en lugar de la otra es una falta: vecinas en el teclado (al lado, o
    arriba o abajo) o que suenan igual."""
    if frozenset((a, b)) in _SUENAN_IGUAL:
        return True
    if a not in _TECLADO or b not in _TECLADO:
        return False
    (fa, ca), (fb, cb) = _TECLADO[a], _TECLADO[b]
    return ((fa == fb and abs(ca - cb) == 1) or (fb == fa - 1 and cb in (ca, ca + 1))
            or (fb == fa + 1 and cb in (ca - 1, ca)))


_OTRA_LETRA = 99


def _distancia(a: str, b: str, se_confunden: Callable[[str, str], bool] | None = None) -> int:
    """Las letras que hay que agregar, sacar, cambiar o dar vuelta para pasar de una a la otra.
    Con `se_confunden`, cambiar una letra por otra que no se confunde con ella no es una falta
    (cuesta más que cualquier tope)."""
    previa, fila = None, list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        nueva = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cambio = 0 if ca == cb else (1 if se_confunden is None or se_confunden(ca, cb)
                                         else _OTRA_LETRA)
            nueva[j] = min(fila[j] + 1, nueva[j - 1] + 1, fila[j - 1] + cambio)
            if previa is not None and i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                nueva[j] = min(nueva[j], previa[j - 2] + 1)
        previa, fila = fila, nueva
    return fila[-1]


def _misma_palabra(antes: str, despues: str, de_los_nombres: set[str]) -> bool:
    """Si `despues` es `antes` bien escrita (la regla, en el comentario de la sección): igual sin
    tildes ni mayúsculas; una palabra de un nombre de los datos, con pocas letras distintas para su
    largo (ninguna hasta 3 letras, una hasta 6, dos desde 7, y una más); si no, que suene igual o
    con esa diferencia, hecha sólo de letras de más, de menos, dadas vuelta o que se confunden. Una
    palabra de una o dos letras sólo cambia de tildes o mayúsculas; una con números, nunca."""
    a, d = _sin_marcas(antes), _sin_marcas(despues)
    if a == d:
        return True
    if any(c.isdigit() for c in a + d):
        return False
    # J2-19 (la prueba en el celular, 2026-10-13): la regla es simétrica, así que sin esto "CoreLabs"
    # bien escrito se podía "corregir" a "cirelabs". Una palabra que ya está como en los datos sólo
    # cambia de mayúsculas o de tildes.
    if a in de_los_nombres:
        return False
    largo = len(a)
    tope = 0 if largo <= 3 else 1 if largo <= 6 else 2
    if d in de_los_nombres:
        return _distancia(a, d) <= tope + 1
    if largo <= 2:
        return False
    if _como_suena(a) == _como_suena(d):
        return True
    return _distancia(a, d, _se_confunden) <= tope


def palabra_por_palabra(original: str, corregido: str, nombres: Sequence[str]) -> tuple[
        str, list[dict[str, str]], int] | None:
    """La corrección de `original`, palabra por palabra: el texto de la persona con cada palabra
    corregida que es la misma palabra mal escrita en su lugar (sus renglones y su puntuación
    quedan), los cambios (`antes`, `despues`) en su orden y cuántas palabras cambiadas no se
    aceptaron (quedan como las escribió la persona). `None` si la corrección no tiene la misma
    cantidad de palabras: no se puede saber cuál es cuál."""
    lugares = list(_PALABRA.finditer(original))
    nuevas = _PALABRA.findall(corregido)
    if len(lugares) != len(nuevas):
        return None
    de_los_nombres = {_sin_marcas(p) for n in nombres for p in _PALABRA.findall(n)}
    partes, desde, cambios, rechazadas = [], 0, [], 0
    for lugar, nueva in zip(lugares, nuevas):
        antes = lugar.group(0)
        if antes == nueva:
            continue
        if not _misma_palabra(antes, nueva, de_los_nombres):
            rechazadas += 1
            continue
        partes += [original[desde:lugar.start()], nueva]
        desde = lugar.end()
        cambios.append({"antes": antes, "despues": nueva})
    return "".join([*partes, original[desde:]]), cambios, rechazadas


def nombres_mal_escritos(texto: str, opciones: Mapping[str, Any]) -> list[str]:
    """Las palabras de los nombres de los datos del espacio (personas, áreas, objetivos y tareas)
    que la persona escribió mal en `texto`, como están en los datos (J2-18: "cirelabs" es
    CoreLabs): lo que Leda puede escribir bien en lo que propone sin inventar un nombre.

    Habilitar un nombre deja que la IA lo escriba aunque la persona no lo haya escrito así, así
    que la regla es la estricta (advertencia de RDD de la J2-18): sólo palabras de cuatro letras o
    más; la misma palabra mal escrita como cualquier otra (`_misma_palabra` sin la holgura de los
    nombres: que suene igual, o letras de más, de menos, dadas vuelta o cambiadas por una vecina
    del teclado o que suena igual, pocas para su largo), nunca otra letra cualquiera ("marcas" no
    es Marcos); y una palabra que ya es de un nombre de los datos no es otro nombre mal escrito
    (quien escribió "lucas" nombró a Lucas, no a Lucio)."""
    nombres = _nombres_del_equipo(opciones)
    de_los_nombres = {_sin_marcas(p) for n in nombres for p in _PALABRA.findall(n)}
    escritas = {_sin_marcas(p) for p in _PALABRA.findall(texto) if len(p) >= 4}
    escritas -= de_los_nombres
    encontradas: list[str] = []
    for nombre in nombres:
        for palabra in _PALABRA.findall(nombre):
            d = _sin_marcas(palabra)
            if len(d) < 4 or palabra in encontradas:
                continue
            if any(_misma_palabra(a, d, set()) for a in escritas):
                encontradas.append(palabra)
    return encontradas


@dataclass
class Ortografia:
    """Lo que se corrigió (`corregidos`: por campo, el texto y sus cambios; sólo los que
    cambiaron), lo que no se pudo revisar (`rechazados`, con su motivo: `sin_respuesta`,
    `no_es_ortografia` o `largo`) y, de lo revisado, cuántas palabras no se aceptaron en cada
    campo (`palabras_rechazadas`: quedan como las escribió la persona)."""

    corregidos: dict[str, dict[str, Any]] = field(default_factory=dict)
    rechazados: list[dict[str, str]] = field(default_factory=list)
    palabras_rechazadas: list[dict[str, Any]] = field(default_factory=list)


def revisar_la_ortografia(crudo: Mapping[str, Any], textos: Mapping[str, str],
                          opciones: Mapping[str, Any]) -> Ortografia:
    """Lo que vale de la corrección de la IA, campo por campo, en el orden del formulario."""
    r = Ortografia()
    nombres = _nombres_del_equipo(opciones)
    for campo in CAMPOS_DE_TEXTO:
        if campo not in textos:
            continue
        original, corregido = textos[campo], crudo.get(campo)
        if not isinstance(corregido, str) or not corregido.strip():
            r.rechazados.append({"campo": campo, "motivo": "sin_respuesta"})
            continue
        hecho = palabra_por_palabra(original, corregido, nombres)
        if hecho is None:
            r.rechazados.append({"campo": campo, "motivo": "no_es_ortografia"})
            continue
        texto, cambios, rechazadas = hecho
        if len(texto.strip()) > LARGOS[campo]:
            r.rechazados.append({"campo": campo, "motivo": "largo"})
            continue
        if cambios:
            r.corregidos[campo] = {"texto": texto, "cambios": cambios}
        if rechazadas:
            r.palabras_rechazadas.append({"campo": campo, "cantidad": rechazadas})
    return r
