"""Verificador del texto que redacta el modelo en la variante A (ADR 0014,
etapa 6, mecanismo M4).

Determinista, sin modelo, y general: opera sobre los hechos estructurados de
`ResultadoTurno`, no sobre frases (ADR 0013). Un texto sale sólo si

- no afirma lo que los hechos no tienen: números y fechas que no están, un
  estado del dominio que no figura, una acción hecha en primera persona sin un
  cambio que la respalde, claves internas;
- trae lo que los hechos exigen: los nombres citados, los valores aceptados,
  los estados, los datos del resumen, la pregunta de lo que falta y lo
  esencial de lo que dicen un rechazo, un cambio o un "no cambió";
- tiene un largo razonable.

`verificar` devuelve `None` si el texto sirve, o el motivo del rechazo
(`familia: detalle`) para registrarlo. No entiende el sentido: ante la duda
rechaza, y quien llama manda la plantilla de la variante B.

Límites declarados (se ajustan mirando los motivos registrados, no por frase):
la detección de acciones hechas es morfológica (primera persona del pretérito,
`-é` o `-í`) y puede rechazar un "Entendí" inocente; un cambio extra dicho con
las palabras de un cambio real no se distingue.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import fields, is_dataclass
from enum import Enum

from .resultado_turno import ResultadoTurno

LARGO_MAXIMO = 3500
# Contra la plantilla de B: la respuesta del modelo no puede ser mucho más
# larga que lo que dice B con los mismos hechos.
FACTOR_LARGO = 3
MARGEN_LARGO = 200
COBERTURA_MINIMA = 0.5

_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre")
_MES_NUMERO = {m: i + 1 for i, m in enumerate(_MESES)} | {"setiembre": 9}

# Vocabulario de estados del dominio (`estado_tarea` y sus sinónimos
# corrientes): una raíz de estas en el texto exige que los hechos la tengan.
_ESTADOS = ("propuest", "pendiente de aprob", "asignad", "en curso", "bloquead",
            "en revision", "terminad", "cancelad", "completad", "finalizad",
            "cerrad", "aprobad", "rechazad", "entregad", "vencid", "atrasad")

_ACCION_1RA_PERSONA = re.compile(r"\b[a-zñ]{3,}é\b|\b[a-zñ]{4,}í\b",
                                 re.IGNORECASE)
_CLAVE_INTERNA = re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b")
_CITADO = re.compile(r"«([^»]+)»")
_FECHA_NUMERICA = re.compile(r"\b(\d{1,2})\s*[/.\-]\s*(\d{1,2})(?:\s*[/.\-]\s*\d{2,4})?\b")
_FECHA_CON_MES = re.compile(r"\b(\d{1,2})\s*(?:de\s+)?(" + "|".join(_MES_NUMERO) + r")\b")


def _norm(texto: str) -> str:
    sin_marcas = "".join(c for c in unicodedata.normalize("NFD", texto)
                         if unicodedata.category(c) != "Mn")
    return " ".join(sin_marcas.casefold().split())


def _textos(objeto) -> list[str]:
    """Todos los textos de los hechos: lo que el texto puede nombrar."""
    if isinstance(objeto, str):
        return [objeto]
    if isinstance(objeto, Enum) or objeto is None:
        return []
    if is_dataclass(objeto):
        salida: list[str] = []
        for campo in fields(objeto):
            if campo.name in ("opciones", "cierre"):
                continue          # los botones y el cierre no son hechos que decir
            salida += _textos(getattr(objeto, campo.name))
        return salida
    if isinstance(objeto, (tuple, list)):
        return [t for item in objeto for t in _textos(item)]
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
    """El texto dice lo esencial de un hecho redactado a mano (qué cambió, por
    qué no, por qué se rechazó): al menos la mitad de sus palabras con
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


def verificar(resultado: ResultadoTurno, texto: str,
              texto_b: str | None = None) -> str | None:
    """`None` si el texto sirve; si no, el motivo `familia: detalle`."""
    if not texto or not texto.strip():
        return "vacio: el modelo no devolvió texto"
    largo_maximo = LARGO_MAXIMO
    if texto_b is not None:
        largo_maximo = min(LARGO_MAXIMO, FACTOR_LARGO * len(texto_b) + MARGEN_LARGO)
    if len(texto) > largo_maximo:
        return f"largo: {len(texto)} caracteres, máximo {largo_maximo}"

    hechos = _textos(resultado)
    hechos_norm = _norm(" ".join(hechos))
    t = _norm(texto)

    if "{" in texto or "}" in texto:
        return "formato_interno: el texto trae llaves"
    for clave in _CLAVE_INTERNA.findall(texto):
        if clave not in hechos_norm:
            return f"clave_interna: {clave}"

    # Una acción hecha en primera persona necesita un cambio que la respalde.
    respaldo = bool(resultado.cambios or resultado.valores_aceptados
                    or resultado.resumen)
    if not respaldo:
        for m in _ACCION_1RA_PERSONA.finditer(texto):
            if texto[max(0, m.start() - 3):m.start()].lower() != "no ":
                return f"accion_no_ocurrida: {m.group(0)}"

    # Números, fechas y meses que los hechos no tienen.
    fechas_hechos = _fechas(hechos_norm)
    fechas_texto = _fechas(t)
    sobrantes = _numeros(t) - _numeros(hechos_norm)
    if sobrantes:
        return f"numero_inventado: {sorted(sobrantes)[0]}"
    for dia, mes in sorted(fechas_texto - fechas_hechos):
        return f"fecha_distinta: {dia:02d}/{mes:02d}"
    meses_texto = _meses(t, fechas_texto) - _meses(hechos_norm, fechas_hechos)
    if meses_texto:
        return f"mes_inventado: {_MESES[sorted(meses_texto)[0] - 1]}"

    # Estados del dominio que los hechos no tienen.
    for raiz in _ESTADOS:
        if re.search(rf"\b{raiz}", t) and not re.search(rf"\b{raiz}", hechos_norm):
            return f"estado_inventado: {raiz}"

    # Lo que los hechos exigen.
    for hecho in hechos:
        for citado in _CITADO.findall(hecho):
            if _norm(citado) not in t:
                return f"falta_hecho: «{citado}»"
    exigidos: list[str] = [v.mostrado for v in resultado.valores_aceptados]
    exigidos += [e.estado for e in resultado.estado]
    if resultado.resumen:
        exigidos += [valor for _, valor in resultado.resumen.lineas]
    for valor in exigidos:
        if not _aparece(valor, t, fechas_texto):
            return f"falta_hecho: {valor}"
    libres = [c.que for c in resultado.cambios]
    libres += [s.motivo for s in resultado.sin_cambios]
    if resultado.rechazo:
        libres += [resultado.rechazo.razon, resultado.rechazo.se_acepta]
    raices_texto = _raices(t)
    for libre in libres:
        if not _cubre(_norm(libre), raices_texto):
            return f"falta_hecho: {libre}"
    if resultado.falta and not _pregunta_hecha(resultado.falta.pregunta, texto, t,
                                               raices_texto):
        return f"falta_pregunta: {resultado.falta.dato}"
    return None


def _pregunta_hecha(pregunta: str | None, texto: str, texto_norm: str,
                    raices_texto: set[str]) -> bool:
    """El texto hace la pregunta: trae un signo de pregunta o, si lo que se pide
    está dicho como instrucción ("Escribí parte del nombre del objetivo."),
    cubre lo esencial de esa instrucción."""
    if "?" in texto:
        return True
    return bool(pregunta) and bool(_raices(_norm(pregunta))) and _cubre(
        _norm(pregunta), raices_texto)
