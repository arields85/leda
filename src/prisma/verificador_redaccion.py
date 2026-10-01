"""Verificador del texto que redacta el modelo en la variante A (ADR 0014,
etapa 6, mecanismo M4).

Determinista, sin modelo, y general: sólo comprueba lo que el código puede
verificar contra los hechos estructurados de `ResultadoTurno`, sin listas de
palabras ni morfología (ADR 0013: ninguna frase observada, ningún verbo que
"suena a hecho"). El modelo contesta una salida estructurada
(`{"texto", "pregunta", "afirma"}`, ver `leer_borrador`) y un borrador sale sólo si

- cada fecha, número, título entre «», y nombre propio que dice existe en los
  hechos (la comparación es normalizada: sin tildes ni mayúsculas, una fecha dicha
  de otra forma vale);
- `pregunta` es el dato que falta (de una lista cerrada: su identificador) y el
  texto pregunta; sin dato que falte, no abre una pregunta;
- `afirma` (identificadores cerrados) cuenta cada cambio del resultado y ninguno
  que no esté en `cambios`;
- trae lo que los hechos exigen: los nombres citados, los valores aceptados, los
  estados, lo entendido (si es corto) y lo esencial de un rechazo o un "no cambió";
- no trae claves internas ni llaves y tiene un largo razonable.

`verificar` devuelve `None` si el texto sirve, o el motivo del rechazo
(`familia: detalle`) para registrarlo. Ante la duda rechaza, y quien llama manda
la plantilla de la variante B.

Límite declarado: `afirma` es lo que el modelo dice de sí mismo. Un efecto
contado en el texto y omitido de `afirma` no se detecta (sin morfología ni
listas, el código no puede leer el sentido); se mira en los motivos y en la
transcripción de la prueba, no se parcha por frase.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum

from .resultado_turno import ResultadoTurno, ids_de_cambios

LARGO_MAXIMO = 3500
# Contra la plantilla de B: la respuesta del modelo no puede ser mucho más
# larga que lo que dice B con los mismos hechos.
FACTOR_LARGO = 3
MARGEN_LARGO = 200
COBERTURA_MINIMA = 0.5
# Lo entendido de más de este largo (un criterio escrito largo) se puede resumir:
# se exige copiar un valor corto (una fecha, un nombre), no un párrafo.
LARGO_ENTENDIDO_EXIGIDO = 80

_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre")
_MES_NUMERO = {m: i + 1 for i, m in enumerate(_MESES)} | {"setiembre": 9}

_CLAVE_INTERNA = re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b")
_CITADO = re.compile(r"«([^»]+)»")
_FECHA_NUMERICA = re.compile(r"\b(\d{1,2})\s*[/.\-]\s*(\d{1,2})(?:\s*[/.\-]\s*\d{2,4})?\b")
_FECHA_CON_MES = re.compile(r"\b(\d{1,2})\s*(?:de\s+)?(" + "|".join(_MES_NUMERO) + r")\b")
_LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_"
_PALABRA = re.compile(rf"[{_LETRAS}]+")
_CAPITALIZADA = re.compile(rf"(?<![{_LETRAS}])[A-ZÁÉÍÓÚÜÑ][{_LETRAS}]*")
# Lo que, antes de una palabra, la deja al principio de una oración: la
# mayúscula inicial no es un nombre propio.
_FIN_DE_ORACION = ".!?:;\n¿¡-–—•*(\"'"


@dataclass(frozen=True)
class Borrador:
    """La salida estructurada del modelo: el texto, el dato que dice pedir
    (`pregunta`, identificador cerrado o `None`) y los efectos que cuenta
    (`afirma`, identificadores cerrados de `cambios`)."""
    texto: str
    pregunta: str | None
    afirma: tuple[str, ...]


def leer_borrador(crudo: str) -> Borrador | str:
    """El `Borrador` que dice el JSON del modelo, o el motivo (`formato: ...`)
    si no es la salida pedida. Tolera vallas de código y texto alrededor del
    objeto: lee el primer objeto JSON que encuentra."""
    crudo = (crudo or "").strip()
    inicio = crudo.find("{")
    if inicio < 0:
        return "formato: el modelo no devolvió un objeto JSON"
    try:
        datos, _ = json.JSONDecoder().raw_decode(crudo[inicio:])
    except ValueError:
        return "formato: el JSON del modelo no se puede leer"
    if not isinstance(datos, dict):
        return "formato: la salida no es un objeto"
    texto = datos.get("texto")
    if not isinstance(texto, str) or not texto.strip():
        return "formato: falta el `texto`"
    pregunta = datos.get("pregunta")
    if pregunta is not None and not isinstance(pregunta, str):
        return "formato: `pregunta` no es un identificador ni null"
    afirma = datos.get("afirma", [])
    if (not isinstance(afirma, list)
            or not all(isinstance(a, str) for a in afirma)):
        return "formato: `afirma` no es una lista de identificadores"
    return Borrador(texto.strip(), pregunta or None, tuple(afirma))


def _norm(texto: str) -> str:
    sin_marcas = "".join(c for c in unicodedata.normalize("NFD", texto)
                         if unicodedata.category(c) != "Mn")
    return " ".join(sin_marcas.casefold().split())


def _textos(objeto, *, con_opciones: bool = False) -> list[str]:
    """Todos los textos de los hechos: lo que el texto puede nombrar. Las
    opciones (los botones) sólo entran como nombres que se pueden decir, no
    como hechos que se exigen; el cierre del resumen es del código."""
    if isinstance(objeto, str):
        return [objeto]
    if isinstance(objeto, Enum) or objeto is None:
        return []
    if is_dataclass(objeto):
        salida: list[str] = []
        for campo in fields(objeto):
            if campo.name == "cierre" or (campo.name == "opciones"
                                          and not con_opciones):
                continue
            salida += _textos(getattr(objeto, campo.name), con_opciones=con_opciones)
        return salida
    if isinstance(objeto, (tuple, list)):
        return [t for item in objeto for t in _textos(item, con_opciones=con_opciones)]
    return []


def _fechas(texto_norm: str) -> set[tuple[int, int]]:
    """Las fechas (día, mes) que dice un texto, en `dd/mm` o `d de mes`."""
    fechas = {(int(d), int(m)) for d, m in _FECHA_NUMERICA.findall(texto_norm)
              if 1 <= int(m) <= 12}
    fechas |= {(int(d), _MES_NUMERO[m]) for d, m in _FECHA_CON_MES.findall(texto_norm)}
    return fechas


def _meses(texto_norm: str, fechas: set[tuple[int, int]]) -> set[int]:
    nombrados = {_MES_NUMERO[m] for m in _MES_NUMERO if re.search(rf"\b{m}\b", texto_norm)}
    return nombrados | {m for _, m in fechas}


def _numeros(texto: str) -> set[int]:
    return {int(n) for n in re.findall(r"\d+", texto)}


def _raices(texto_norm: str) -> set[str]:
    """Raíz de cada palabra con contenido (4 letras o más)."""
    return {p[:4] for p in re.findall(r"[a-zñ]{4,}", texto_norm)}


def _cubre(libre_norm: str, raices_texto: set[str]) -> bool:
    """El texto dice lo esencial de un hecho redactado a mano (por qué no
    cambió, por qué se rechazó): al menos la mitad de sus palabras con
    contenido, por raíz, y siempre que el hecho tenga alguna."""
    raices = _raices(libre_norm)
    if not raices:
        return True
    return len(raices & raices_texto) / len(raices) >= COBERTURA_MINIMA


def _aparece(valor: str, texto_norm: str, fechas_texto: set[tuple[int, int]]) -> bool:
    """El valor está en el texto tal cual o, si es una fecha, dicha de otra
    forma (`04/10/2026` como `4 de octubre`)."""
    v = _norm(valor)
    if v in texto_norm:
        return True
    fechas_valor = _fechas(v)
    return bool(fechas_valor) and fechas_valor <= fechas_texto


def _nombre_propio_inventado(texto: str, palabras_hechos: set[str]) -> str | None:
    """La primera palabra con mayúscula inicial, en medio de una oración y fuera
    de las comillas «», que los hechos no tienen: un nombre que el texto no puede
    sacar de ningún lado. La mayúscula al empezar una oración no cuenta."""
    sin_citas = _CITADO.sub(" ", texto)
    for m in _CAPITALIZADA.finditer(sin_citas):
        antes = sin_citas[:m.start()].rstrip()
        if not antes or antes[-1] in _FIN_DE_ORACION:
            continue
        if _norm(m.group()) not in palabras_hechos:
            return m.group()
    return None


def verificar(resultado: ResultadoTurno, borrador: Borrador,
              texto_b: str | None = None) -> str | None:
    """`None` si el borrador sirve; si no, el motivo `familia: detalle`."""
    texto = borrador.texto
    if not texto or not texto.strip():
        return "vacio: el modelo no devolvió texto"
    largo_maximo = LARGO_MAXIMO
    if texto_b is not None:
        largo_maximo = min(LARGO_MAXIMO, FACTOR_LARGO * len(texto_b) + MARGEN_LARGO)
    if len(texto) > largo_maximo:
        return f"largo: {len(texto)} caracteres, máximo {largo_maximo}"

    todos = _textos(resultado, con_opciones=True)
    todos_norm = _norm(" ".join(todos))
    t = _norm(texto)

    if "{" in texto or "}" in texto:
        return "formato_interno: el texto trae llaves"
    for clave in _CLAVE_INTERNA.findall(texto):
        if clave not in todos_norm:
            return f"clave_interna: {clave}"

    # Números, fechas y meses que los hechos no tienen.
    fechas_hechos = _fechas(todos_norm)
    fechas_texto = _fechas(t)
    sobrantes = _numeros(t) - _numeros(todos_norm)
    if sobrantes:
        return f"numero_inventado: {sorted(sobrantes)[0]}"
    for dia, mes in sorted(fechas_texto - fechas_hechos):
        return f"fecha_distinta: {dia:02d}/{mes:02d}"
    meses_texto = _meses(t, fechas_texto) - _meses(todos_norm, fechas_hechos)
    if meses_texto:
        return f"mes_inventado: {_MESES[sorted(meses_texto)[0] - 1]}"

    # Títulos y nombres: los citados y los propios tienen que estar en los hechos.
    for citado in _CITADO.findall(texto):
        if _norm(citado) not in todos_norm:
            return f"nombre_inventado: «{citado}»"
    palabras_hechos = {_norm(p) for p in _PALABRA.findall(" ".join(todos))}
    inventado = _nombre_propio_inventado(texto, palabras_hechos)
    if inventado:
        return f"nombre_inventado: {inventado}"

    # Efectos: los que cuenta tienen que ser cambios del resultado, y todos.
    ids = ids_de_cambios(resultado)
    for efecto in borrador.afirma:
        if efecto not in ids:
            return f"efecto_no_ocurrido: {efecto}"
    omitido = [i for i in ids if i not in borrador.afirma]
    if omitido:
        return f"efecto_omitido: {omitido[0]}"

    # El dato que falta: el modelo dice cuál pide y el texto pregunta.
    if resultado.falta:
        if borrador.pregunta != resultado.falta.clave or not _hay_pregunta(texto):
            return f"falta_pregunta: {resultado.falta.dato}"
    elif borrador.pregunta is not None or _hay_pregunta(texto):
        return "pregunta_sin_falta: no hay ningún dato que pedir"

    # Lo que los hechos exigen. Los datos del resumen los agrega el código: no se
    # exigen en el texto del modelo.
    sin_resumen = replace(resultado, resumen=None)
    for hecho in _textos(sin_resumen):
        for citado in _CITADO.findall(hecho):
            if _norm(citado) not in t:
                return f"falta_hecho: «{citado}»"
    exigidos: list[str] = [v.mostrado for v in resultado.valores_aceptados]
    exigidos += [e.estado for e in resultado.estado]
    exigidos += [v.mostrado for v in resultado.entendido
                 if len(v.mostrado) <= LARGO_ENTENDIDO_EXIGIDO]
    for valor in exigidos:
        if not _aparece(valor, t, fechas_texto):
            return f"falta_hecho: {valor}"
    libres = [s.motivo for s in resultado.sin_cambios]
    if resultado.rechazo:
        libres += [resultado.rechazo.razon, resultado.rechazo.se_acepta]
    raices_texto = _raices(t)
    for libre in libres:
        if not _cubre(_norm(libre), raices_texto):
            return f"falta_hecho: {libre}"
    return None


def _hay_pregunta(texto: str) -> bool:
    return "?" in texto or "¿" in texto
