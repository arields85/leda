"""Agregación de sesión del banco: tasa de aprobación por escenario, fallas
por comprobación y latencias -- baseline, sin umbrales inventados
(`docs/validation/README.md`, "Criterios de aprobación y baseline": "Latencia,
costo, duplicados, omisiones e intervenciones manuales se capturan primero
como baseline. No se inventan umbrales antes de contar con evidencia.").
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

RESULTADOS = ("aprobado", "falla", "no_concluyente", "bloqueado")


@dataclass(frozen=True)
class EntradaReporte:
    """Una corrida (escenario, índice) ya evaluada por los comprobadores."""

    escenario_id: str
    indice: int
    resultado: str
    comprobaciones: list[dict] = field(default_factory=list)
    latencia_total_s: float = 0.0
    grabacion: dict = field(default_factory=dict)
    motivo_bloqueo: str = ""


def _resumen_latencias(valores: list[float]) -> dict:
    if not valores:
        return {"min": None, "mediana": None, "max": None}
    return {"min": valores[0], "mediana": statistics.median(valores), "max": valores[-1]}


def armar_reporte(entradas: list[EntradaReporte], *, proveedor: str, modelo: str,
                  marca_de_tiempo: str) -> dict:
    """Arma el reporte de una sesión de banco: agregado por escenario y
    global. No decide aprobación ni umbrales -- sólo cuenta lo observado."""
    por_escenario: dict[str, list[EntradaReporte]] = {}
    for e in entradas:
        por_escenario.setdefault(e.escenario_id, []).append(e)

    escenarios_reporte: dict[str, dict] = {}
    for eid, corridas in por_escenario.items():
        conteos = dict.fromkeys(RESULTADOS, 0)
        fallas_por_comprobacion: dict[str, int] = {}
        for c in corridas:
            conteos[c.resultado] += 1
            for comp in c.comprobaciones:
                if comp.get("resultado") == "falla":
                    nombre = comp["nombre"]
                    fallas_por_comprobacion[nombre] = fallas_por_comprobacion.get(nombre, 0) + 1
        n = len(corridas)
        escenarios_reporte[eid] = {
            "corridas": n,
            "conteos": conteos,
            "tasa_aprobacion": (conteos["aprobado"] / n) if n else 0.0,
            "fallas_por_comprobacion": fallas_por_comprobacion,
            "latencia_s": _resumen_latencias(sorted(c.latencia_total_s for c in corridas)),
        }

    return {
        "marca_de_tiempo": marca_de_tiempo,
        "proveedor": proveedor,
        "modelo": modelo,
        "total_corridas": len(entradas),
        "escenarios": escenarios_reporte,
        "latencia_global_s": _resumen_latencias(
            sorted(e.latencia_total_s for e in entradas)),
    }


def resumen_texto(reporte: dict) -> str:
    """Texto plano para el resumen final de la terminal de pytest."""
    lineas = [
        f"Banco conversacional -- {reporte['proveedor']}/{reporte['modelo']} "
        f"({reporte['total_corridas']} corridas)"]
    for eid, datos in sorted(reporte["escenarios"].items()):
        c = datos["conteos"]
        lineas.append(
            f"  {eid}: {c['aprobado']}/{datos['corridas']} aprobado "
            f"({datos['tasa_aprobacion']:.0%}) -- falla={c['falla']} "
            f"no_concluyente={c['no_concluyente']} bloqueado={c['bloqueado']}")
        if datos["fallas_por_comprobacion"]:
            lineas.append(
                f"    fallas por comprobación: {datos['fallas_por_comprobacion']}")
    lat = reporte["latencia_global_s"]
    lineas.append(
        f"  latencia total (s): min={lat['min']} mediana={lat['mediana']} max={lat['max']}")
    return "\n".join(lineas)
