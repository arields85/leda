"""Formato y carga de escenarios del banco.

Sigue "Estructura mínima de un escenario" de `docs/validation/README.md`: el
escenario declara sólo el objetivo, las precondiciones simuladas, el actor y
el mensaje inicial. No hay IDs internos, herramientas ni estados esperados
en el texto que Prisma recibe -- eso vive en `herramientas_esperadas` /
`herramientas_prohibidas`, que nunca se le muestran al modelo.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import yaml

SEVERIDADES = ("baja", "media", "alta", "critica")

_CAMPOS_OBLIGATORIOS = ("id", "objetivo", "actor", "mensajes")


class EscenarioInvalido(ValueError):
    pass


@dataclass(frozen=True)
class Escenario:
    id: str
    objetivo: str
    actor: str
    mensajes: list[str]
    herramientas_esperadas: tuple[str, ...] = ()
    herramientas_prohibidas: tuple[str, ...] = ()
    nombres_permitidos: tuple[str, ...] = ()
    precondiciones: dict = field(default_factory=dict)
    severidad: str = "media"
    # Estado y efectos esperados (protocolo, "Estructura mínima de un
    # escenario"): sin esto sólo se verificaba el nombre de la herramienta,
    # nunca si dejó el estado, el bloqueo o la dependencia correctos.
    efectos: dict = field(default_factory=dict)
    respuesta_menciona: tuple[str, ...] = ()
    respuesta_no_contiene_patron: tuple[str, ...] = ()


def _validar_estructura(datos: dict, origen: pathlib.Path) -> None:
    if not isinstance(datos, dict):
        raise EscenarioInvalido(f"{origen}: el escenario tiene que ser un mapeo.")

    faltantes = [c for c in _CAMPOS_OBLIGATORIOS if c not in datos or datos[c] in (None, "")]
    if faltantes:
        raise EscenarioInvalido(f"{origen}: faltan campos obligatorios {faltantes}.")

    if not isinstance(datos["id"], str) or not datos["id"].strip():
        raise EscenarioInvalido(f"{origen}: 'id' tiene que ser texto no vacío.")
    if not isinstance(datos["objetivo"], str) or not datos["objetivo"].strip():
        raise EscenarioInvalido(f"{origen}: 'objetivo' tiene que ser texto no vacío.")
    if not isinstance(datos["actor"], str) or not datos["actor"].strip():
        raise EscenarioInvalido(f"{origen}: 'actor' tiene que ser texto no vacío.")

    mensajes = datos["mensajes"]
    if (not isinstance(mensajes, list) or not mensajes
            or not all(isinstance(m, str) and m.strip() for m in mensajes)):
        raise EscenarioInvalido(
            f"{origen}: 'mensajes' tiene que ser una lista no vacía de texto.")

    for campo in ("herramientas_esperadas", "herramientas_prohibidas",
                 "nombres_permitidos"):
        valor = datos.get(campo, [])
        if not isinstance(valor, list) or not all(isinstance(v, str) for v in valor):
            raise EscenarioInvalido(f"{origen}: '{campo}' tiene que ser una lista de texto.")

    precondiciones = datos.get("precondiciones", {})
    if not isinstance(precondiciones, dict):
        raise EscenarioInvalido(f"{origen}: 'precondiciones' tiene que ser un mapeo.")

    efectos = datos.get("efectos", {})
    if not isinstance(efectos, dict):
        raise EscenarioInvalido(f"{origen}: 'efectos' tiene que ser un mapeo.")

    for campo in ("respuesta_menciona", "respuesta_no_contiene_patron"):
        valor = datos.get(campo, [])
        if not isinstance(valor, list) or not all(isinstance(v, str) for v in valor):
            raise EscenarioInvalido(f"{origen}: '{campo}' tiene que ser una lista de texto.")

    severidad = datos.get("severidad", "media")
    if severidad not in SEVERIDADES:
        raise EscenarioInvalido(
            f"{origen}: 'severidad' tiene que ser una de {SEVERIDADES}, no {severidad!r}.")


def cargar_escenario(ruta: pathlib.Path | str) -> Escenario:
    """Carga y valida un único escenario desde un archivo YAML."""
    ruta = pathlib.Path(ruta)
    datos = yaml.safe_load(ruta.read_text("utf-8"))
    _validar_estructura(datos, ruta)

    return Escenario(
        id=datos["id"].strip(),
        objetivo=datos["objetivo"].strip(),
        actor=datos["actor"].strip(),
        mensajes=list(datos["mensajes"]),
        herramientas_esperadas=tuple(datos.get("herramientas_esperadas", [])),
        herramientas_prohibidas=tuple(datos.get("herramientas_prohibidas", [])),
        nombres_permitidos=tuple(datos.get("nombres_permitidos", [])),
        precondiciones=datos.get("precondiciones", {}) or {},
        severidad=datos.get("severidad", "media"),
        efectos=datos.get("efectos", {}) or {},
        respuesta_menciona=tuple(datos.get("respuesta_menciona", [])),
        respuesta_no_contiene_patron=tuple(datos.get("respuesta_no_contiene_patron", [])),
    )


def cargar_escenarios(directorio: pathlib.Path | str) -> list[Escenario]:
    """Carga todos los `*.yaml` de un directorio. Rechaza IDs repetidos: dos
    escenarios con el mismo ID opaco no se pueden distinguir en el reporte."""
    directorio = pathlib.Path(directorio)
    escenarios = [cargar_escenario(p) for p in sorted(directorio.glob("*.yaml"))]

    vistos: dict[str, pathlib.Path] = {}
    for e, p in zip(escenarios, sorted(directorio.glob("*.yaml"))):
        if e.id in vistos:
            raise EscenarioInvalido(
                f"ID de escenario repetido: {e.id!r} en {vistos[e.id]} y {p}.")
        vistos[e.id] = p
    return escenarios
