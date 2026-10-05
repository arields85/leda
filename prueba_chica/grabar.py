"""Las IA del corredor: la guionada con las jugadas esperadas, la que graba y la que repite (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6: de `tests/banco` se toma la idea de grabar la
IA para repetir una falla con una IA guionada. Las tres cumplen el contrato de `ia.IA`.

- `IAPerfecta`: elige exactamente las jugadas que el YAML espera en el paso (con las tareas y las
  opciones traducidas de su clave al alias que recibe) y redacta un texto fijo que dice qué
  recibió. Es la corrida en seco: si algo falla con ella, el error es del motor o del YAML.
- `IAQueGraba`: envuelve a otra y guarda cada pedido con su respuesta (o su error), su tiempo y,
  si el proveedor lo informa, lo que costó (`gasto.ClienteQueCuenta`).
- `IARepetida`: devuelve, en orden, lo que una grabación guardó: la misma corrida otra vez, sin
  la IA real, para mirar una falla.
- `IAMixta`: las jugadas de una y la redacción de otra (el preludio: las jugadas son datos de la
  conversación; los textos los redacta la IA de la corrida, como habrían salido).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .ia import IA, Jugada

# Las claves de una jugada esperada que no son datos para la IA.
_SOLO_PARA_COMPROBAR = ("puede_traer",)


class RepeticionDesviada(RuntimeError):
    """La corrida pidió algo distinto de lo que la grabación tiene en ese lugar."""


@dataclass
class IAPerfecta:
    """La IA guionada con las jugadas que el paso espera. `titulos` es clave → título."""

    titulos: dict[str, str]
    nombre: str = "guionada"
    paso: dict[str, Any] | None = None

    def preparar(self, paso: dict[str, Any]) -> None:
        self.paso = paso

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list[Jugada]:
        if self.paso is None:
            raise RuntimeError("La IA guionada no sabe en qué paso está.")
        alias = {t["titulo"]: t["alias"] for t in situacion.get("tareas") or []}
        de_la_clave = {k: alias.get(t) for k, t in self.titulos.items()}
        opciones = {}
        abierta = ((situacion.get("estado") or {}).get("pregunta_abierta") or {})
        for o in abierta.get("opciones") or []:
            opciones[o.get("tarea")] = o["opcion"]
        jugadas = []
        for e in self.paso.get("jugadas") or []:
            datos = {k: v for k, v in e.items() if k not in ("nombre", *_SOLO_PARA_COMPROBAR)}
            for k in ("tarea", "tarea_correcta"):
                if k in datos:
                    datos[k] = de_la_clave.get(datos[k]) or datos[k]
            if "opcion" in datos:
                datos["opcion"] = opciones.get(de_la_clave.get(datos["opcion"])) or datos["opcion"]
            nombre = e["nombre"]
            jugadas.append(Jugada(nombre, datos))
        return jugadas

    def redactar(self, pedido: dict[str, Any]) -> str:
        """Un texto fijo que dice qué recibió: el mismo pedido da el mismo texto, y dos pedidos
        distintos, textos distintos (la huella de los hechos), para enlazar cada mensaje
        entregado con su fila."""
        hechos = pedido.get("hechos") or []
        pregunta = pedido.get("pregunta")
        resumen = ", ".join(str(h.get("aviso") or h.get("jugada") or "?") for h in hechos)
        huella = hashlib.sha1(json.dumps([pedido.get("persona"), hechos, pregunta],
                                         sort_keys=True, ensure_ascii=False,
                                         default=str).encode()).hexdigest()[:6]
        return (f"(IA guionada, para {pedido.get('persona')}: {resumen or 'sin hechos'}"
                + (f"; pregunta {pregunta['tipo']}" if pregunta else "") + f" · {huella})")


@dataclass
class IAMixta:
    jugadas_de: IA
    redaccion_de: IA

    @property
    def nombre(self) -> str:
        return self.redaccion_de.nombre

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list[Jugada]:
        return self.jugadas_de.elegir_jugadas(situacion)

    def redactar(self, pedido: dict[str, Any]) -> str:
        return self.redaccion_de.redactar(pedido)


@dataclass
class IAQueGraba:
    """Graba cada pedido a la IA envuelta. `llamadas` es la grabación: se guarda como JSON y la
    repite `IARepetida`."""

    ia: IA
    llamadas: list[dict[str, Any]] = field(default_factory=list)

    @property
    def nombre(self) -> str:
        return self.ia.nombre

    def preparar(self, paso: dict[str, Any]) -> None:
        if hasattr(self.ia, "preparar"):
            self.ia.preparar(paso)

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list[Jugada]:
        return self._grabar("jugadas", situacion, lambda: self.ia.elegir_jugadas(situacion),
                            lambda r: [dataclasses.asdict(j) for j in r])

    def redactar(self, pedido: dict[str, Any]) -> str:
        return self._grabar("redaccion", pedido, lambda: self.ia.redactar(pedido), lambda r: r)

    def _grabar(self, tipo: str, pedido: dict[str, Any], llamar, a_json) -> Any:
        usos = _usos(self.ia)
        antes = len(usos) if usos is not None else 0
        inicio = time.perf_counter()
        llamada: dict[str, Any] = {"tipo": tipo, "pedido": _a_json(pedido)}
        try:
            respuesta = llamar()
            llamada["respuesta"] = a_json(respuesta)
            return respuesta
        except Exception as e:      # se graba y sigue su camino: la falla también se repite
            llamada["error"] = f"{type(e).__name__}: {e}"
            raise
        finally:
            llamada["segundos"] = round(time.perf_counter() - inicio, 3)
            if usos is not None:
                llamada["usos"] = usos[antes:]
            self.llamadas.append(llamada)


@dataclass
class IARepetida:
    """Repite una grabación, en orden. Un pedido de otro tipo que el grabado es un desvío."""

    llamadas: list[dict[str, Any]]
    nombre: str = "repeticion"

    @classmethod
    def desde_archivo(cls, ruta: Path) -> IARepetida:
        datos = json.loads(Path(ruta).read_text("utf-8"))
        return cls(list(datos["llamadas"]), nombre=f"repeticion:{datos.get('ia', '?')}")

    def preparar(self, paso: dict[str, Any]) -> None:
        pass

    def elegir_jugadas(self, situacion: dict[str, Any]) -> list[Jugada]:
        r = self._siguiente("jugadas")
        return [Jugada(j["nombre"], j.get("datos") or {}) for j in r]

    def redactar(self, pedido: dict[str, Any]) -> str:
        return self._siguiente("redaccion")

    def _siguiente(self, tipo: str) -> Any:
        if not self.llamadas:
            raise RepeticionDesviada(f"La grabación se terminó (se pidió {tipo}).")
        llamada = self.llamadas.pop(0)
        if llamada["tipo"] != tipo:
            raise RepeticionDesviada(f"Se pidió {tipo} y la grabación tiene {llamada['tipo']}.")
        if "error" in llamada:
            raise RuntimeError(llamada["error"])
        return llamada["respuesta"]


def _usos(ia) -> list | None:
    cliente = getattr(ia, "cliente", None)
    return getattr(cliente, "usos", None)


def _a_json(valor: Any) -> Any:
    return json.loads(json.dumps(valor, ensure_ascii=False, default=str))
