"""La ayuda de la IA al crear un objetivo en la plataforma (ADR 0023, punto 4; porción J3, tarea
J3-4 de `odd/tasks/plataforma-jerarquias.md`). Es la ayuda de la carga (`ayuda_al_cargar`, J2)
generalizada a los objetivos: el mismo recuadro libre, la misma regla del mozo y las mismas
comprobaciones de la cocina, sin lo propio de la tarea (el criterio, su juicio y la evidencia).

La persona cuenta qué se quiere lograr y Leda propone lo que el formulario todavía tiene vacío: el
nombre, la descripción, de qué cuelga, el tipo, el referente y la fecha. Nada se crea acá: la
persona ve cada dato marcado, lo corrige o lo acepta, y confirma como siempre.

- **Qué recibe la IA** (`entrada_de_la_ia`), sólo del espacio de las opciones del objetivo
  (`opciones_del_objetivo`): el texto, lo ya escrito, hoy y los días que vienen, los objetivos de
  los que puede colgar con un código cada uno (P1…), los tipos con los nombres del pack, los
  referentes de área con sus áreas y las áreas con referente, con un código cada una (A1…). Nunca
  un id.
- **Lo que decide el código** (`revisar`):
  - de qué cuelga, sólo un código de la lista;
  - el tipo, uno que admita el lugar donde cuelga (punto 11): sin padre, el que va sin padre; si
    la IA dio uno que no va ahí, o ninguno, el que preselecciona el formulario (el único, o el
    operativo cuando también puede ser hito);
  - el referente, sólo si sus palabras están en el texto y son de un referente de área del
    espacio (decisión 3 del usuario, 2026-10-14; `coinciden`: `fichas.integrantes_que_coinciden`,
    con los apodos); con dos o más, Leda no elige y los muestra (ADR 0020, decisión 3); con nadie,
    se dice y no se pone a otro. Si la persona no nombró a nadie (J3-4b, como la J2-18 de la
    carga: "Leda completa todo lo que puede"), el referente del área de la que trata el objetivo,
    si la IA dio el código de un área de la lista; nombrado alguien, el área no se mira;
  - la fecha, sólo si la persona la dijo, calculada por el código con sus palabras y en un día
    hábil del espacio (`ayuda_al_cargar.fecha_dicha`, la misma de la carga). Si vence después que
    el objetivo del que cuelga se propone igual: el freno del formulario (J3-3b) lo dice;
  - el nombre y la descripción, con los topes del formulario y sin un número ni un nombre que no
    estén en lo que escribió la persona o en los datos de este objetivo (de qué cuelga, el
    referente y sus áreas); un nombre de los datos que la persona escribió mal vale escrito como
    está en los datos.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from . import ayuda_al_cargar
from .ayuda_al_cargar import (_cadena, _dias_proximos, _hoy, _normal, _por_id,
                              _problema_del_texto, _revisar_la_fecha, _tope_de_salida, _vacio,
                              leer, nombres_mal_escritos)
from .motor import hechos

NOMBRE_HERRAMIENTA = "proponer_el_objetivo"

# Los datos del formulario del objetivo, en su orden, y cómo se llaman para la IA.
CAMPOS = ("titulo", "descripcion", "padre_id", "tipo", "referente_id", "fecha")
PARA_LA_IA = {"titulo": "titulo", "descripcion": "descripcion", "padre_id": "padre",
              "tipo": "tipo", "referente_id": "referente", "fecha": "fecha"}

# Los topes del formulario (migración 0068) y el del texto libre, los de la carga.
LARGOS = {"titulo": 200, "descripcion": 800}
LARGO_DEL_TEXTO = ayuda_al_cargar.LARGO_DEL_TEXTO

TEXTOS = {
    ("titulo", "sin_proponer"):
        "No pude proponer el nombre con lo que escribiste; contame qué se quiere lograr.",
    ("descripcion", "sin_proponer"):
        "No pude proponer la descripción con lo que escribiste; si hace falta, escribila vos.",
    ("referente", "no_encontrado"):
        "No encontré a «{quien}» entre los referentes de área; elegí el referente.",
    ("referente", "varios"):
        "Encontré a más de un referente para {quien}: elegí el referente.",
}

INSTRUCCIONES = """\
Sos Leda, la project manager del equipo. Una persona está creando un objetivo en la plataforma: te \
contó con sus palabras qué se quiere lograr (texto) y te pide que completes los datos del objetivo \
que todavía están vacíos (pide). Completás lo que se pueda saber con lo que recibiste. Lo que \
devolvés es una propuesta: la persona ve cada dato marcado y lo acepta, lo corrige o lo borra.

El nombre y la descripción los escribís vos, con lo que contó la persona, como los escribiría \
alguien del equipo que conoce el trabajo: con naturalidad, en oraciones simples y con buena \
ortografía. El nombre dice en pocas palabras qué se quiere lograr; la descripción cuenta lo que \
dijo la persona, ordenado, sin agregar nada. Los nombres de personas, áreas y objetivos los \
escribís como están en los datos, aunque la persona los haya escrito con otra ortografía. Los \
datos que recibís son hechos para entender el objetivo, no textos para copiar.

De qué cuelga: si lo que contó la persona es parte de uno de los objetivos que recibiste, su \
código; si no es parte de ninguno, vacío. El tipo, uno de los que admite el lugar donde cuelga; \
sin un objetivo arriba, el que va sin padre.

El referente: si la persona nombró a quien lleva el objetivo, copiás sus palabras tal cual, aunque \
no lo encuentres entre los referentes, y no proponés un área. Si no nombró a nadie, proponés el \
área de la que trata el objetivo, de la lista de áreas, si se entiende por lo que hay que lograr; \
su referente lo pone Leda. La fecha, sólo si la persona la dijo.

Usás sólo lo que recibiste: ningún número, nombre, fecha ni dato que no esté ahí. Lo que no podés \
saber con lo que recibiste va vacío; la persona lo completa."""

_DATOS = {
    "titulo": "El nombre del objetivo: en pocas palabras, qué se quiere lograr, bien escrito.",
    "descripcion": "Lo que contó la persona sobre el objetivo, ordenado y bien escrito, sin "
                   "agregar nada.",
    "padre": "El código (P1, P2...) del objetivo del que este es parte; vacío si no es parte de "
             "ninguno.",
    "tipo": "El código del tipo que le corresponde, de los que admite el lugar donde cuelga.",
    "referente": "Las palabras con que la persona nombró a quien lleva el objetivo, tal cual las "
                 "escribió; vacío si no nombró a nadie.",
    "area": "Si la persona no nombró a nadie, el código (A1, A2...) del área de la que trata el "
            "objetivo, por lo que hay que lograr; vacío si nombró a alguien o si no se puede "
            "saber.",
    "fecha":ayuda_al_cargar._DATOS["fecha"],
    "como_dijo_la_fecha": ayuda_al_cargar._DATOS["como_dijo_la_fecha"],
}
# Las palabras de la fecha van con la fecha, y el área (J3-4b), con el referente.
_ACOMPANAN = {"como_dijo_la_fecha": "fecha", "area": "referente"}


@dataclass
class Resultado(ayuda_al_cargar.Resultado):
    """Lo que Leda propone para el objetivo (`propuesta`, con los nombres del formulario), los
    referentes para elegir cuando hay más de uno (`elegir`), lo que no se propuso y la persona
    tiene que saber (`avisos`) y lo descartado con su motivo (`descartados`), como en la carga.
    La fecha se revisa con la misma función de la carga, así que sus textos son los de ella. De
    dónde salió el referente, para la auditoría (`referente_de`, J3-4b): `dicho`, si la persona lo
    nombró; `leda`, si Leda lo propuso por el área."""

    referente_de: str | None = None

    def descartar(self, campo: str, motivo: str, aviso: str | None = None, **datos: str) -> None:
        if aviso is not None and (campo, aviso) in TEXTOS:
            self.descartados.append({"campo": campo, "motivo": motivo})
            self.avisos.append({"campo": campo, "motivo": aviso,
                                "texto": TEXTOS[(campo, aviso)].format(**datos)})
            return
        super().descartar(campo, motivo, aviso, **datos)


# --- Lo que falta y lo que recibe la IA ------------------------------------------------------

def lo_que_se_pide(escrito: Mapping[str, Any], opciones: Mapping[str, Any]) -> list[str]:
    """Lo vacío que Leda puede proponer, en el orden del formulario: de qué cuelga, sólo si hay de
    dónde elegir."""
    hay = {"padre_id": bool(opciones.get("padres"))}
    return [c for c in CAMPOS if _vacio(escrito.get(c)) and hay.get(c, True)]


def _con_codigos(opciones: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {f"P{i}": p for i, p in enumerate(opciones.get("padres") or [], 1)}


def _niveles(opciones: Mapping[str, Any]) -> dict[str, str]:
    return {"estrategico": "objetivo estratégico", "hito": "hito",
            "operativo": "objetivo operativo", **(opciones.get("niveles") or {})}


def _referente(opciones: Mapping[str, Any], membership_id: Any) -> Mapping[str, Any] | None:
    return _por_id(opciones.get("referentes") or [], "membership_id", membership_id)


def _areas(opciones: Mapping[str, Any]) -> dict[str, tuple[str, Mapping[str, Any]]]:
    """Las áreas con referente, con un código cada una (A1…, por su nombre): el área y su
    referente (J3-4b). Cada nombre, una vez (advertencia de RDD de la J3-4b, R3-area-duplicada): la
    IA elige por el nombre, así que dos códigos con el mismo nombre no se distinguen. Si el mismo
    nombre es de un solo referente, queda una vez; si es de más de uno, no queda: Leda no elige
    entre personas (ADR 0020, decisión 3)."""
    por_nombre: dict[str, list[tuple[str, Mapping[str, Any]]]] = {}
    for r in opciones.get("referentes") or []:
        for area in r.get("areas") or []:
            if isinstance(area, str) and area.strip():
                por_nombre.setdefault(_normal(area), []).append((area, r))
    areas = []
    for mismas in por_nombre.values():
        if len({str(r.get("membership_id")) for _, r in mismas}) == 1:
            areas.append(mismas[0])
    areas.sort(key=lambda a: (_normal(a[0]), a[0], str(a[1].get("membership_id"))))
    return {f"A{i}": a for i, a in enumerate(areas, 1)}


def _tipos_de(opciones: Mapping[str, Any], padre_id: Any) -> list[str]:
    """Los tipos que admite el lugar donde cuelga (punto 11), como los ofrece la base."""
    if not padre_id:
        return list(opciones.get("sin_padre") or [])
    padre = _por_id(opciones.get("padres") or [], "id", padre_id)
    return list((padre or {}).get("tipos") or [])


def tipo_por_omision(tipos: Sequence[str]) -> str | None:
    """El tipo que preselecciona el formulario (`defaultType`): el operativo cuando también puede
    ser hito; si no, el único."""
    return "operativo" if "operativo" in tipos else (tipos[0] if tipos else None)


def entrada_de_la_ia(texto: str, escrito: Mapping[str, Any],
                     opciones: Mapping[str, Any]) -> dict[str, Any]:
    """Lo que recibe la IA: sólo del espacio de las opciones y sin ids."""
    hoy = _hoy(opciones)
    niveles = _niveles(opciones)
    ya: dict[str, Any] = {}
    for campo in ("titulo", "descripcion"):
        if not _vacio(escrito.get(campo)):
            ya[campo] = str(escrito[campo]).strip()
    padre = _por_id(opciones.get("padres") or [], "id", escrito.get("padre_id"))
    if padre is not None:
        ya["de_que_cuelga"] = padre["titulo"]
    if escrito.get("tipo") in niveles:
        ya["tipo"] = niveles[escrito["tipo"]]
    referente = _referente(opciones, escrito.get("referente_id"))
    if referente is not None:
        ya["referente"] = referente["nombre"]
    if not _vacio(escrito.get("fecha")):
        try:
            ya["fecha"] = hechos.dia(date.fromisoformat(escrito["fecha"]), hoy)
        except ValueError:
            pass

    def vence(p: Mapping[str, Any]) -> str | None:
        try:
            return hechos.dia(date.fromisoformat(str(p["fecha_objetivo"])), hoy) \
                if p.get("fecha_objetivo") else None
        except ValueError:
            return None

    return {
        "texto": texto,
        "pide": [PARA_LA_IA[c] for c in lo_que_se_pide(escrito, opciones)],
        "ya_escrito": ya,
        "hoy": hechos.dia(hoy, hoy),
        "dias": _dias_proximos(hoy, opciones),
        "objetivos": [{"codigo": c, "titulo": p["titulo"], "tipo": p.get("tipo"),
                       "vence": vence(p), "debajo_puede_ir": list(p.get("tipos") or [])}
                      for c, p in _con_codigos(opciones).items()],
        "tipos": [{"codigo": t, "nombre": niveles[t]} for t in ("estrategico", "hito", "operativo")],
        "sin_padre": list(opciones.get("sin_padre") or []),
        "referentes": [{"nombre": r["nombre"], "areas": list(r.get("areas") or [])}
                       for r in opciones.get("referentes") or []],
        "areas": [{"codigo": c, "area": area} for c, (area, _r) in _areas(opciones).items()],
    }


# --- La llamada -------------------------------------------------------------------------------

def herramienta(pide: Sequence[str]) -> dict[str, Any]:
    """La herramienta de la respuesta, con sólo los datos que se piden (con la fecha, las palabras
    con que se dijo)."""
    datos = [d for d in _DATOS if d in pide or _ACOMPANAN.get(d) in pide]
    return {"type": "function", "function": {
        "name": NOMBRE_HERRAMIENTA,
        "description": "Los datos del objetivo que Leda le propone a la persona; vacío lo que no "
                       "se puede saber con lo que contó.",
        "parameters": {"type": "object",
                       "properties": {d: {"type": "string", "description": _DATOS[d]}
                                      for d in datos},
                       "additionalProperties": False}}}


def pedir(ia, entrada: Mapping[str, Any]) -> dict[str, Any]:
    """Una sola llamada a la IA del espacio (sin reintento: la persona puede volver a tocar), como
    `ayuda_al_cargar.pedir`: una IA sin configurar es `LookupError`; una respuesta cortada, sin la
    herramienta o ilegible, `RespuestaInvalida`; lo demás se levanta como venga."""
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
    return leer(respuesta, NOMBRE_HERRAMIENTA)


# --- Lo que decide el código ------------------------------------------------------------------

def revisar(crudo: Mapping[str, Any], *, texto: str, escrito: Mapping[str, Any],
            opciones: Mapping[str, Any],
            coinciden: Callable[[str], list[dict[str, Any]]]) -> Resultado:
    """Lo que vale de la propuesta de la IA. `coinciden(dicho)`: los integrantes del espacio que
    coinciden con lo dicho (con los apodos)."""
    r = Resultado()
    pide = set(lo_que_se_pide(escrito, opciones))

    # De qué cuelga, de la lista.
    padre = escrito.get("padre_id") or None
    if "padre_id" in pide:
        codigo = _cadena(crudo.get("padre"))
        if codigo is not None:
            elegido = _con_codigos(opciones).get(codigo.upper())
            if elegido is None:
                r.descartar("padre", "no_existe")
            else:
                padre = elegido["id"]
                r.propuesta["padre_id"] = padre

    # El tipo, uno que admita ese lugar: también si la persona eligió un tipo que no va debajo del
    # padre que propone Leda (la web lo cambia igual al cambiar de qué cuelga).
    tipos = _tipos_de(opciones, padre)
    if "tipo" in pide or ("padre_id" in r.propuesta and escrito.get("tipo") not in tipos):
        del_la_ia = _cadena(crudo.get("tipo"))
        if del_la_ia in tipos:
            r.propuesta["tipo"] = del_la_ia
        else:
            if del_la_ia is not None:
                r.descartar("tipo", "no_corresponde")
            por_omision = tipo_por_omision(tipos)
            if por_omision is not None:
                r.propuesta["tipo"] = por_omision

    # El referente: el que nombró la persona, si es uno solo de los referentes de área; si no nombró
    # a nadie, el del área que propone Leda.
    referente = escrito.get("referente_id") or None
    if "referente_id" in pide:
        referente = _el_referente(r, crudo, texto, opciones, coinciden)

    # La fecha: el día que dicen las palabras de la persona, calculado por el código, si es el
    # mismo que dio la IA y es hábil (la misma revisión que la carga).
    fecha = crudo.get("fecha") if "fecha" in pide else None
    if fecha is not None and not (isinstance(fecha, str) and not fecha.strip()):
        _revisar_la_fecha(r, fecha, _cadena(crudo.get("como_dijo_la_fecha")), texto, opciones)

    # Los textos, con lo que es de este objetivo: lo que escribió la persona, los datos elegidos y
    # los nombres de los datos que la persona escribió mal.
    permitidos = [texto, *(str(escrito.get(c) or "") for c in ("titulo", "descripcion"))]
    permitidos += nombres_mal_escritos(texto, opciones)
    del_padre = _por_id(opciones.get("padres") or [], "id", padre)
    if del_padre is not None:
        permitidos.append(del_padre["titulo"])
    del_referente = _referente(opciones, referente)
    if del_referente is not None:
        permitidos += [del_referente["nombre"], *(del_referente.get("areas") or [])]
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
    return r


def _el_referente(r: Resultado, crudo: Mapping[str, Any], texto: str,
                  opciones: Mapping[str, Any],
                  coinciden: Callable[[str], list[dict[str, Any]]]) -> str | None:
    """El referente que nombró la persona: con uno solo de los referentes de área, ése; con
    varios, para elegir; con nadie (o con alguien del equipo que no es referente), se dice. Si no
    nombró a nadie, el referente del área que propone Leda (J3-4b), sólo un código de la lista.
    Nombrado alguien, el área no se mira, aunque no se lo encuentre."""
    dicho = _cadena(crudo.get("referente"))
    if dicho is None:
        return _el_del_area(r, crudo, opciones)
    if not set(_normal(dicho).split()) <= set(_normal(texto).split()):
        # Las palabras no son de la persona: no nombró a nadie con ellas.
        r.descartar("referente", "no_lo_dijo")
        return None
    encontrados: list[Mapping[str, Any]] = []
    for fila in coinciden(dicho):
        referente = _referente(opciones, str(fila["membership_id"]))
        if referente is not None and referente not in encontrados:
            encontrados.append(referente)
    if len(encontrados) == 1:
        r.propuesta["referente_id"] = encontrados[0]["membership_id"]
        r.referente_de = "dicho"
        return encontrados[0]["membership_id"]
    if encontrados:
        r.elegir = [{"membership_id": e["membership_id"], "nombre": e["nombre"],
                     "area": ", ".join(e.get("areas") or [])} for e in encontrados]
        r.descartar("referente", "varios", "varios", quien=dicho)
    else:
        r.descartar("referente", "no_encontrado", "no_encontrado", quien=dicho)
    return None


def _el_del_area(r: Resultado, crudo: Mapping[str, Any],
                 opciones: Mapping[str, Any]) -> str | None:
    """El referente del área que propone Leda, si su código es de la lista (J3-4b)."""
    codigo = _cadena(crudo.get("area"))
    if codigo is None:
        return None
    del_area = _areas(opciones).get(codigo.upper())
    if del_area is None:
        r.descartar("referente", "area_no_existe")
        return None
    referente = del_area[1]["membership_id"]
    r.propuesta["referente_id"] = referente
    r.referente_de = "leda"
    return referente
