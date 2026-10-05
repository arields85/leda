"""Jev en paralelo, sin decidir nada (ADR 0018, decisión 7; conversaciones 13 y 14).

`odd/tasks/prueba-chica-del-motor.md`, sección 6: Jev recibe cada mensaje que nombra una tarea,
con las tareas candidatas, y su elección se registra sin decidir. Corre en un hilo aparte mientras
el turno corre con la IA principal; lo que devuelve va sólo al registro de la corrida, nunca a la
base ni al turno. Si Jev falla, se anota la falla y la corrida sigue igual.

Por cada consulta queda: qué tipo de resolución dio (`clara`, `ambigua`, `varias`, `ninguna`),
qué tarea eligió si fue clara, la probabilidad de cada candidata (de la pregunta "tarea"), los
valores de la llamada de verificación si la hubo (`misma` y `rival`: con ellos se entiende una
`ambigua` con una candidata muy probable; ronda 1) y si acertó contra la respuesta correcta del
paso (`preguntar`, o la clave de una tarea).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from leda.jev import Jev, TareaCandidata, TipoResolucion, resolver_referencia_tarea

PREGUNTAR = "preguntar"


@dataclass
class JevQueGraba:
    cliente: Jev
    llamadas: list[dict[str, Any]] = field(default_factory=list)

    def decidir(self, state: dict[str, Any],
                preguntas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        inicio = time.perf_counter()
        llamada: dict[str, Any] = {"preguntas": sorted(preguntas)}
        try:
            llamada["respuesta"] = self.cliente.decidir(state, preguntas)
            return llamada["respuesta"]
        except Exception as e:
            llamada["error"] = f"{type(e).__name__}: {e}"
            raise
        finally:
            llamada["segundos"] = round(time.perf_counter() - inicio, 3)
            self.llamadas.append(llamada)


def preguntar(cliente: Jev, *, mensaje: str, referencia: str,
              candidatas: list[tuple[str, TareaCandidata]], quien: str,
              correcta: str | None = None) -> dict[str, Any]:
    """Lo que Jev dice de la referencia, por la clave de cada tarea, y si acertó."""
    graba = JevQueGraba(cliente)
    claves = [c for c, _ in candidatas]
    salida: dict[str, Any] = {"referencia": referencia, "candidatas": claves,
                              "correcta": correcta}
    try:
        r = resolver_referencia_tarea(graba, mensaje=mensaje, referencia=referencia,
                                      tareas=[t for _, t in candidatas], vocabulario="",
                                      quien_escribe=quien)
    except Exception as e:     # Jev no decide nada: su falla sólo se anota
        salida.update(error=f"{type(e).__name__}: {e}", llamadas=len(graba.llamadas))
        return salida
    por_id = {t.id: c for c, t in candidatas}
    primera = next((ll for ll in graba.llamadas if "respuesta" in ll), None)
    probabilidades = {}
    if primera is not None:
        crudas = ((primera["respuesta"] or {}).get("tarea") or {}).get("probabilities") or {}
        probabilidades = {claves[int(k[1:]) - 1]: round(float(p), 3)
                          for k, p in crudas.items()
                          if k[1:].isdigit() and 0 < int(k[1:]) <= len(claves)}
    verificacion = next((ll["respuesta"] for ll in graba.llamadas
                         if "misma" in ll["preguntas"] and "respuesta" in ll), None)
    if isinstance(verificacion, dict):
        salida["verificacion"] = {
            k: round(float(verificacion[k]["noul"]), 3) for k in ("misma", "rival")
            if isinstance(verificacion.get(k), dict) and "noul" in verificacion[k]}
    eligio = por_id.get(r.tarea_id) if r.tipo is TipoResolucion.CLARA else None
    salida.update(tipo=r.tipo.value, eligio=eligio, probabilidades=probabilidades,
                  llamadas=len(graba.llamadas),
                  segundos=round(sum(ll["segundos"] for ll in graba.llamadas), 3))
    if correcta is not None:
        salida["acierta"] = (r.tipo is not TipoResolucion.CLARA if correcta == PREGUNTAR
                             else eligio == correcta)
    return salida


def eleccion_de_la_ia(jugadas: list[dict[str, Any]]) -> str:
    """Qué tarea eligió la IA principal en un paso (por su clave), o `preguntar` si no eligió
    ninguna: no adivinó (ronda 1: con ninguna jugada, la tabla la marcaba como si se hubiera
    equivocado de tarea). Si además preguntó con botones lo mide la comprensión del paso."""
    for j in jugadas:
        if j.get("tarea"):
            return j["tarea"]
        if j.get("nombre") == "elegir" and j.get("opcion"):
            return j["opcion"]
    return PREGUNTAR
