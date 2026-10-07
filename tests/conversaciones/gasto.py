"""El gasto en IA de la Etapa 2 y su techo (decisión 10.4 del usuario, 2026-10-05).

`odd/tasks/prueba-chica-del-motor.md`, sección 10.4: USD 30 para toda la etapa, con un aviso al
acercarse y, al llegar, se le pregunta al usuario antes de seguir. El corredor (E2-7) lleva la
cuenta:

- **La libreta** (`tests/conversaciones/resultados/gasto.json`, versionada: no tiene nada
  sensible) suma cada corrida real: cuándo, qué motor, qué proveedor y qué IA, qué conversación,
  cuántas llamadas, los tokens y lo que costó. Se escribe después de cada corrida, así un corte
  no pierde la cuenta.
- **El costo** es el que informa el proveedor (OpenRouter, con `usage.include`); si no lo
  informa, una estimación por llamada (`USD_POR_LLAMADA`), marcada como estimada; una llamada
  que falló (error HTTP, plazo, sin respuesta) no se cobra ni se estima. Las corridas viejas
  con Jev (retirado de la prueba, ADR 0018, decisión 7) guardan su costo estimado en `jev_usd`,
  y el total lo sigue sumando.
- **Precio desconocido** (E3-8, la comparación de IA): un proveedor que no es OpenRouter (`nan`)
  no informa el costo y no tiene precio en esta libreta. Sus llamadas se anotan con sus tokens y
  `precio: desconocido`, cuestan 0 en la cuenta (nunca una cifra inventada), y la ronda no se
  estima ni cuenta para el techo.
- **El techo:** antes de cada corrida se estima lo que va a costar; si con eso se pasa del techo,
  no corre (`TechoAlcanzado`) salvo con `pasar_el_techo`, que el agente pasa sólo con el OK del
  usuario. Al llegar al 80 % avisa.
- `ClienteQueCuenta` es el cliente de la IA real que pide y guarda lo que cada llamada usó.
- **Sin crédito** (rondas 2 y 3, cortes de OpenRouter a mitad de ronda): un HTTP 402, o un error
  402 dentro de la respuesta, es `SinCredito`; el corredor corta la ronda y marca inválidas las
  corridas que lo tuvieron (`llamadas_sin_credito`). Antes de una ronda real, `credito_restante`
  pregunta cuánto le queda a la cuenta, sin imprimir la clave.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import httpx

from leda.motor.ia_real import ClienteCompatible

TECHO_USD = 30.0
AVISO_DESDE = 0.8
RUTA = Path(__file__).resolve().parent / "resultados" / "gasto.json"

# Estimación por llamada cuando el proveedor no informa el costo, a partir del banco del
# 2026-10-03 (bitácora de flujos, "Modelos": sol, USD 0,016 por mensaje; luna, 0,0007). Se usa
# la cifra por mensaje como cifra por llamada: queda del lado alto.
# Luna pro cuesta por token lo mismo que luna en OpenRouter (USD 0,10 de entrada y 0,50 de salida
# por millón; el de sol, 2,00 y 10,00; verificado el 2026-10-06).
USD_POR_LLAMADA = {"openai/gpt-6-sol": 0.016, "openai/gpt-6-luna": 0.0015,
                   "openai/gpt-6-luna-pro": 0.0015}
USD_POR_LLAMADA_DESCONOCIDA = 0.02
# Los proveedores que informan lo que costó cada llamada. Con los demás, el precio es
# desconocido: no se estima (`precio_conocido`).
INFORMAN_EL_COSTO = frozenset({"openrouter"})
PRECIO_DESCONOCIDO = "desconocido"
# Lo que se le pide a la IA en una corrida se cuenta con lo esperado (`corredor.
# llamadas_previstas`); lo que Leda manda sobre otras tareas o de más no está ahí: un margen.
MARGEN_DE_LA_ESTIMACION = 1.25
MINIMO_PARA_PROMEDIAR = 10      # llamadas con costo informado antes de usar su promedio


SIN_CREDITO = "sin crédito en el proveedor"


class TechoAlcanzado(RuntimeError):
    pass


class SinCredito(RuntimeError):
    """El proveedor dice que la cuenta no tiene crédito (HTTP 402)."""


def _sin_credito_en_la_respuesta(respuesta: Any) -> bool:
    error = respuesta.get("error") if isinstance(respuesta, dict) else None
    return isinstance(error, dict) and str(error.get("code")) == "402"


def es_sin_credito(error: str | None) -> bool:
    """Si el error grabado de una llamada es un 402: el de `SinCredito` o, en las grabaciones de
    antes de él, el de httpx."""
    return bool(error) and (error.startswith(f"{SinCredito.__name__}:")
                            or "402 Payment Required" in error)


def llamadas_sin_credito(llamadas: list[dict[str, Any]]) -> int:
    """Cuántas llamadas grabadas (`grabar.IAQueGraba`) chocaron con la cuenta sin crédito."""
    return sum(es_sin_credito(ll.get("error")) for ll in llamadas)


def credito_restante(clave: str, base_url: str, *,
                     transporte: httpx.BaseTransport | None = None,
                     plazo: float = 10.0) -> float | None:
    """Los USD que le quedan a la cuenta de OpenRouter: lo comprado menos lo usado
    (`/credits`) y, si la clave tiene un límite propio, lo que le queda (`/key`); el menor.
    `None` si el proveedor no lo dice (caído, sin red, otra forma). La clave sólo va en el
    encabezado; nada de esto la imprime."""
    base = base_url.rstrip("/")
    restos: list[float] = []
    with httpx.Client(timeout=plazo, transport=transporte,
                      headers={"Authorization": f"Bearer {clave}"}) as http:
        try:
            r = http.get(f"{base}/credits")
            r.raise_for_status()
            datos = r.json()["data"]
            restos.append(float(datos["total_credits"]) - float(datos["total_usage"]))
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            pass
        try:
            r = http.get(f"{base}/key")
            r.raise_for_status()
            limite = r.json()["data"].get("limit_remaining")
            if limite is not None:
                restos.append(float(limite))
        except (httpx.HTTPError, KeyError, TypeError, ValueError, AttributeError):
            pass
    return min(restos) if restos else None


@dataclass
class ClienteQueCuenta(ClienteCompatible):
    """El cliente compatible con OpenAI que además pide el uso (OpenRouter) y lo guarda."""

    usos: list[dict[str, Any]] = field(default_factory=list)

    def completar(self, cuerpo: dict[str, Any]) -> dict[str, Any]:
        if "openrouter" in self.base_url:
            cuerpo = {**cuerpo, "usage": {"include": True}}
        try:
            respuesta = super().completar(cuerpo)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 402:
                raise SinCredito("el proveedor no tiene crédito (HTTP 402)") from None
            raise
        if _sin_credito_en_la_respuesta(respuesta):
            raise SinCredito("el proveedor no tiene crédito (error 402 en la respuesta)")
        uso = respuesta.get("usage") if isinstance(respuesta, dict) else None
        self.usos.append({k: (uso or {}).get(k) for k in
                          ("prompt_tokens", "completion_tokens", "cost")})
        return respuesta


def precio_conocido(proveedor: str) -> bool:
    """Si el gasto con ese proveedor se puede estimar: el proveedor informa lo que costó."""
    return proveedor in INFORMAN_EL_COSTO


def costo_de_las_llamadas(llamadas: list[dict[str, Any]], modelo: str, *,
                          proveedor: str = "openrouter") -> dict[str, Any]:
    """Lo que costaron las llamadas grabadas (`grabar.IAQueGraba`): lo informado, y lo estimado
    para las que respondieron sin traerlo. Una llamada que falló (error HTTP, como el 402 de la
    ronda 2 sin crédito; plazo agotado; sin respuesta) no se cobra: cuesta 0 y no se estima. Sólo
    cuenta lo que haya respondido antes del error (sus `usos`). Con un proveedor de precio
    desconocido, lo que no trae su costo no se estima: se cuenta en `llamadas_sin_precio` y el
    resultado lo dice (`precio`)."""
    conocido = precio_conocido(proveedor)
    usd, estimadas, sin_precio, entrada, salida = 0.0, 0, 0, 0, 0
    por_llamada = USD_POR_LLAMADA.get(modelo, USD_POR_LLAMADA_DESCONOCIDA)

    def sin_costo_informado() -> None:
        nonlocal usd, estimadas, sin_precio
        if conocido:
            usd += por_llamada
            estimadas += 1
        else:
            sin_precio += 1

    for ll in llamadas:
        usos = ll.get("usos")
        if not usos:
            if "error" not in ll:       # respondió, pero el proveedor no informó el uso
                sin_costo_informado()
            continue
        for u in usos:
            entrada += u.get("prompt_tokens") or 0
            salida += u.get("completion_tokens") or 0
            if u.get("cost") is not None:
                usd += float(u["cost"])
            else:
                sin_costo_informado()
    costo = {"llamadas": len(llamadas), "tokens_entrada": entrada, "tokens_salida": salida,
             "usd": round(usd, 6), "llamadas_estimadas": estimadas}
    if not conocido:
        costo.update(precio=PRECIO_DESCONOCIDO, llamadas_sin_precio=sin_precio)
    return costo


@dataclass
class Gasto:
    """La libreta del gasto de la etapa. Segura entre hilos (las corridas en paralelo)."""

    ruta: Path = field(default_factory=lambda: RUTA)
    techo: float = TECHO_USD
    avisar: Callable[[str], None] = print
    _candado: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _reservado: float = 0.0

    def leer(self) -> dict[str, Any]:
        if not self.ruta.exists():
            return {"techo_usd": self.techo, "corridas": []}
        return json.loads(self.ruta.read_text("utf-8"))

    def total(self) -> float:
        return round(sum(c["usd"] + c.get("jev_usd", 0.0) for c in self.leer()["corridas"]), 6)

    def por_llamada(self, modelo: str, proveedor: str = "openrouter") -> float:
        """El costo medio medido de una llamada de ese modelo, si ya hay bastantes; si no, la
        estimación. Con un proveedor de precio desconocido, 0: no se estima."""
        if not precio_conocido(proveedor):
            return 0.0
        corridas = [c for c in self.leer()["corridas"] if c["modelo"] == modelo
                    and c.get("proveedor", "openrouter") == proveedor]
        medidas = sum(c["llamadas"] - c["llamadas_estimadas"] for c in corridas)
        if medidas >= MINIMO_PARA_PROMEDIAR:
            usd = sum(c["usd"] for c in corridas)
            return max(usd / max(1, sum(c["llamadas"] for c in corridas)), 0.0)
        return USD_POR_LLAMADA.get(modelo, USD_POR_LLAMADA_DESCONOCIDA)

    def reservar(self, estimado: float, *, pasar_el_techo: bool = False) -> None:
        """Antes de una corrida: si con lo estimado se pasa del techo, `TechoAlcanzado` (salvo
        `pasar_el_techo`); desde el 80 %, un aviso. Lo reservado se suma hasta que se anota."""
        with self._candado:
            previsto = self.total() + self._reservado + estimado
            if previsto > self.techo and not pasar_el_techo:
                raise TechoAlcanzado(
                    f"El gasto de la etapa llegaría a USD {previsto:.2f}, más que el techo de "
                    f"USD {self.techo:.2f} (decisión 10.4). Hace falta el OK del usuario para "
                    f"seguir (--pasar-el-techo).")
            if previsto >= AVISO_DESDE * self.techo:
                self.avisar(f"Aviso: el gasto de la etapa llegaría a USD {previsto:.2f}, el "
                            f"{previsto / self.techo:.0%} del techo de USD {self.techo:.2f}.")
            self._reservado += estimado

    def anotar(self, entrada: dict[str, Any], *, reservado: float = 0.0) -> None:
        """Suma una corrida real a la libreta y libera lo que tenía reservado."""
        with self._candado:
            datos = self.leer()
            datos["techo_usd"] = self.techo
            datos["corridas"].append(entrada)
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            temporal = self.ruta.with_suffix(".tmp")
            temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=1), "utf-8")
            os.replace(temporal, self.ruta)
            self._reservado = max(0.0, self._reservado - reservado)

    def liberar(self, reservado: float) -> None:
        with self._candado:
            self._reservado = max(0.0, self._reservado - reservado)
