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
- **Por suscripción** (`chatgpt`, decisión del usuario del 2026-10-07): igual que un precio
  desconocido, pero la libreta dice `precio: suscripción`.
- **El techo:** antes de cada corrida se estima lo que va a costar; si con eso se pasa del techo,
  no corre (`TechoAlcanzado`) salvo con `pasar_el_techo`, que el agente pasa sólo con el OK del
  usuario. Al llegar al 80 % avisa.
- `ClienteQueCuenta` es el cliente de la IA real que pide y guarda lo que cada llamada usó.
- **Sin crédito** (rondas 2 y 3, cortes de OpenRouter a mitad de ronda): un HTTP 402, o un error
  402 dentro de la respuesta, es `SinCredito`; el corredor corta la ronda y marca inválidas las
  corridas que lo tuvieron (`llamadas_sin_credito`). Antes de una ronda real, `credito_restante`
  pregunta cuánto le queda a la cuenta, sin imprimir la clave.
- **Sin cuota** (regresión D6, 2026-10-08: la suscripción se agotó y 145 corridas se anotaron
  fallidas, sin tokens): el HTTP 429 `usage_limit_reached` de la suscripción de ChatGPT, o ese
  código dentro del flujo, es `SinCuota`, con cuándo se renueva si el servicio lo dice
  (`resets_in_seconds` o `resets_at`). El corredor corta la ronda como con el 402
  (`llamadas_sin_cuota`, `motivo_sin_cuota`). Un 429 con otro código es un límite pasajero: sigue
  como estaba, sin cortar.
- **La libreta tomada** (regresión D6: en Windows, `os.replace` falla con `PermissionError` si
  otro proceso tiene abierto `gasto.json`, y la caída se llevó el informe de la ronda): la
  escritura reintenta un rato y, si sigue tomada, lo que no entró va a
  `gasto-pendiente-<fecha>.json`, al lado, con un aviso; entra a la libreta en la próxima
  escritura que pueda y el archivo aparte se borra. La ronda sigue y el informe se escribe.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import httpx

from leda.motor.chatgpt import ClienteChatGPT, ErrorDeChatGPT
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
# La suscripción de ChatGPT del usuario (2026-10-07): no se paga por llamada. Como un precio
# desconocido, no se estima ni cuenta para el techo, y la libreta dice por qué.
POR_SUSCRIPCION = frozenset({"chatgpt"})
PRECIO_SUSCRIPCION = "suscripción"
# Lo que se le pide a la IA en una corrida se cuenta con lo esperado (`corredor.
# llamadas_previstas`); lo que Leda manda sobre otras tareas o de más no está ahí: un margen.
MARGEN_DE_LA_ESTIMACION = 1.25
MINIMO_PARA_PROMEDIAR = 10      # llamadas con costo informado antes de usar su promedio
# La libreta tomada por otro proceso (Windows): cuántas veces se intenta escribirla y la espera
# base entre intentos (crece: 0,2 s, 0,4 s, ...; unos 2 s en total).
REINTENTOS = 5
ESPERA_S = 0.2


SIN_CREDITO = "sin crédito en el proveedor"


class TechoAlcanzado(RuntimeError):
    pass


class SinCredito(RuntimeError):
    """El proveedor dice que la cuenta no tiene crédito (HTTP 402)."""


SIN_CUOTA = "la suscripción llegó a su límite de uso"
LIMITE_DE_USO = "usage_limit_reached"


class SinCuota(RuntimeError):
    """La suscripción llegó a su límite de uso (HTTP 429 `usage_limit_reached`): no es pasajero,
    hasta que se renueva ninguna llamada va a responder."""


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


def _duracion(segundos: float) -> str:
    minutos = max(0, round(segundos / 60))
    dias, minutos = divmod(minutos, 24 * 60)
    horas, minutos = divmod(minutos, 60)
    partes = ([f"{dias} d"] if dias else []) + ([f"{horas} h"] if horas else [])
    return " ".join(partes + [f"{minutos} min"])


def cuando_se_renueva(error: dict[str, Any], ahora: datetime | None = None) -> str:
    """Cuándo se renueva la cuota, con lo que diga el servicio: `resets_in_seconds` (lo que
    falta) o `resets_at` (el momento, en segundos desde 1970)."""
    ahora = ahora or datetime.now().astimezone()

    def numero(valor: Any) -> float | None:
        return (float(valor) if isinstance(valor, (int, float)) and not isinstance(valor, bool)
                else None)

    if (falta := numero(error.get("resets_in_seconds"))) is not None:
        momento = ahora + timedelta(seconds=max(0.0, falta))
    elif (cuando := numero(error.get("resets_at"))) is not None:
        try:
            momento = max(ahora, datetime.fromtimestamp(cuando).astimezone(ahora.tzinfo))
        except (OverflowError, OSError, ValueError):
            return "no dijo cuándo se renueva"
    else:
        return "no dijo cuándo se renueva"
    return (f"se renueva en {_duracion((momento - ahora).total_seconds())} "
            f"(hacia el {momento:%Y-%m-%d %H:%M})")


def sin_cuota(e: Exception, ahora: datetime | None = None) -> SinCuota | None:
    """El `SinCuota` de un error del cliente, si es el límite de uso de la suscripción: el HTTP
    429 `usage_limit_reached` o ese código dentro del flujo (`chatgpt.ErrorDeChatGPT`). Un 429
    con otro código es pasajero: `None`."""
    if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
        try:
            error = e.response.json().get("error")
        except (ValueError, AttributeError, httpx.ResponseNotRead):
            return None
        if not isinstance(error, dict) or LIMITE_DE_USO not in (error.get("type"),
                                                                 error.get("code")):
            return None
        return SinCuota(f"{SIN_CUOTA} (HTTP 429 {LIMITE_DE_USO}); "
                        f"{cuando_se_renueva(error, ahora)}")
    if isinstance(e, ErrorDeChatGPT) and f"({LIMITE_DE_USO}" in str(e):
        return SinCuota(f"{SIN_CUOTA} ({LIMITE_DE_USO}); no dijo cuándo se renueva")
    return None


def es_sin_cuota(error: str | None) -> bool:
    """Si el error grabado de una llamada es el límite de uso: el de `SinCuota` o, en las
    grabaciones de antes de él, el del cliente."""
    return bool(error) and (error.startswith(f"{SinCuota.__name__}:")
                            or f"HTTP 429 ({LIMITE_DE_USO})" in error)


def llamadas_sin_cuota(llamadas: list[dict[str, Any]]) -> int:
    """Cuántas llamadas grabadas chocaron con el límite de uso de la suscripción."""
    return sum(es_sin_cuota(ll.get("error")) for ll in llamadas)


def motivo_sin_cuota(llamadas: list[dict[str, Any]]) -> str | None:
    """El motivo del corte para el informe, con cuándo se renueva si lo dijo el servicio: el de
    la primera llamada grabada que chocó con el límite de uso."""
    for ll in llamadas:
        error = ll.get("error")
        if es_sin_cuota(error):
            prefijo = f"{SinCuota.__name__}: "
            return (error[len(prefijo):] if error.startswith(prefijo)
                    else f"{SIN_CUOTA} (HTTP 429 {LIMITE_DE_USO}); no dijo cuándo se renueva")
    return None


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
            if (cuota := sin_cuota(e)) is not None:
                raise cuota from None
            raise
        except ErrorDeChatGPT as e:
            if (cuota := sin_cuota(e)) is not None:
                raise cuota from None
            raise
        if _sin_credito_en_la_respuesta(respuesta):
            raise SinCredito("el proveedor no tiene crédito (error 402 en la respuesta)")
        uso = respuesta.get("usage") if isinstance(respuesta, dict) else None
        self.usos.append({k: (uso or {}).get(k) for k in
                          ("prompt_tokens", "completion_tokens", "cost")})
        return respuesta


@dataclass
class ClienteChatGPTQueCuenta(ClienteQueCuenta, ClienteChatGPT):
    """El cliente de la suscripción de ChatGPT que además guarda los tokens de cada llamada (sin
    costo: es por suscripción)."""


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
        costo.update(precio=(PRECIO_SUSCRIPCION if proveedor in POR_SUSCRIPCION
                             else PRECIO_DESCONOCIDO),
                     llamadas_sin_precio=sin_precio)
    return costo


@dataclass
class Gasto:
    """La libreta del gasto de la etapa. Segura entre hilos (las corridas en paralelo)."""

    ruta: Path = field(default_factory=lambda: RUTA)
    techo: float = TECHO_USD
    avisar: Callable[[str], None] = print
    espera: float | None = None     # entre reintentos, si la libreta está tomada; `ESPERA_S`
    _candado: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _reservado: float = 0.0
    # Lo que no se pudo anotar porque la libreta estaba tomada, y el archivo aparte que lo guarda.
    _pendientes: list[dict[str, Any]] = field(default_factory=list, repr=False)
    _aparte: Path | None = field(default=None, repr=False)

    def leer(self) -> dict[str, Any]:
        if not self.ruta.exists():
            return {"techo_usd": self.techo, "corridas": []}
        return json.loads(self.ruta.read_text("utf-8"))

    def total(self) -> float:
        """Lo gastado en la etapa: la libreta y lo que espera aparte para entrar."""
        return round(sum(c["usd"] + c.get("jev_usd", 0.0)
                         for c in [*self.leer()["corridas"], *self._pendientes]), 6)

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
        """Suma una corrida real a la libreta y libera lo que tenía reservado. Si la libreta está
        tomada por otro proceso (Windows: `PermissionError` al reemplazarla), reintenta un rato;
        si sigue tomada, lo que no se pudo anotar va a un archivo aparte
        (`gasto-pendiente-<fecha>.json`), con un aviso, y entra a la libreta en la próxima
        escritura que pueda. Nunca se pierde ni corta la ronda."""
        with self._candado:
            self._pendientes.append(entrada)
            try:
                self._con_reintentos(self._escribir_la_libreta)
            except PermissionError:
                self._guardar_aparte()
            else:
                self._pendientes.clear()
                if self._aparte is not None:
                    self._aparte.unlink(missing_ok=True)
                    self.avisar(f"Aviso: lo pendiente de {self._aparte.name} ya entró a la "
                                f"libreta del gasto; el archivo aparte se borró.")
                    self._aparte = None
            finally:
                self._reservado = max(0.0, self._reservado - reservado)

    def _escribir_la_libreta(self) -> None:
        datos = self.leer()
        datos["techo_usd"] = self.techo
        datos["corridas"].extend(self._pendientes)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.ruta.with_suffix(".tmp")
        temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=1), "utf-8")
        os.replace(temporal, self.ruta)

    def _con_reintentos(self, escribir: Callable[[], None]) -> None:
        for intento in range(REINTENTOS):
            try:
                return escribir()
            except PermissionError:
                if intento == REINTENTOS - 1:
                    raise
                time.sleep((ESPERA_S if self.espera is None else self.espera) * (intento + 1))

    def _guardar_aparte(self) -> None:
        if self._aparte is None:
            self._aparte = self.ruta.with_name(
                f"{self.ruta.stem}-pendiente-{datetime.now():%Y%m%d-%H%M%S-%f}.json")
        datos = {"techo_usd": self.techo, "corridas": self._pendientes}
        try:
            self._aparte.write_text(json.dumps(datos, ensure_ascii=False, indent=1), "utf-8")
        except OSError as e:
            # Ni aparte: las corridas quedan en el aviso, para sumarlas a mano. La libreta no
            # tiene nada sensible (está versionada).
            self.avisar(f"Aviso: la libreta del gasto está tomada por otro proceso y tampoco se "
                        f"pudo escribir aparte ({type(e).__name__}); lo pendiente, para "
                        f"sumarlo a mano: {json.dumps(self._pendientes, ensure_ascii=False)}")
            return
        self.avisar(f"Aviso: la libreta del gasto ({self.ruta.name}) está tomada por otro "
                    f"proceso; {len(self._pendientes)} corrida(s) quedaron en "
                    f"{self._aparte.name} y entran a la libreta en la próxima escritura que "
                    f"pueda (si la ronda termina antes, sumarlas a mano).")

    def liberar(self, reservado: float) -> None:
        with self._candado:
            self._reservado = max(0.0, self._reservado - reservado)
