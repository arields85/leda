"""El ciclo del motor de conversación (diseño probado en la Etapa 2, E2-6).

`odd/tasks/prueba-chica-del-motor.md`, sección 4 ("Entrada propia"); mecánica §9 y §12. Corre
dentro del escuchador (`escucha.py`, E3-7), no como un proceso aparte: el escuchador ya tiene los
transportes de los dos bots, el reloj de Leda y la conexión, y hay uno solo por bot; un segundo
proceso sería otro despachador sobre la misma cola y otro comando para el usuario.

En cada vuelta del escuchador (a lo sumo unos 25 segundos):

1. **la escalera** (`escalera.correr_escalera`) y **los avisos guardados**
   (`avisos.enviar_avisos`), una vez por minuto (`CADA_S`, contado con un reloj monótono real:
   adelantar el reloj de Leda no los acelera);
2. **los mensajes sin respuesta** (`huerfanos.barrer`), en cada vuelta: un mensaje recibido
   que pasada la ventana del turno en curso no tiene ninguna respuesta (su turno murió) recibe
   el aviso neutro y deja un incidente, antes del despacho, para que salga en esta misma vuelta.
   Es la garantía de no fallar en silencio, con o sin seguimiento (E3-7);
3. **el despacho** del outbox (`despachador.despachar`), con el momento y el horario del reloj
   de Leda: las respuestas salen enseguida y lo que Leda inicia, sólo en horario;
4. **los avisos a la administración** (`despachador.despachar_avisos_admin`), con el reloj
   real: `admin_notice` lo fecha la base y no tiene horario.

Nunca importa `leda.ciclo`, `leda.reloj` ni `leda.escalera` (sus textos son fijos y corren
sobre las ramas de los flujos congelados; se retiran en la E3-7; `tests/motor/test_frontera.py`).

**Cada paso, aislado.** Corre en su transacción y se confirma solo. Si se cae, se deshace lo
suyo, se dice en la consola y queda un incidente (`ETAPA_CICLO`) la primera vez: mientras siga
cayéndose no se repite, y vuelve a registrarse si anda y se cae de nuevo. Los demás pasos y el
escuchador siguen. El incidente de los avisos a la administración no se avisa por ese mismo
canal. Si tampoco se puede registrar (la base caída), queda en la consola y se reintenta en la
vuelta siguiente: nunca en silencio.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import psycopg

from ..calendario import Calendario
from ..db import admin, espacio
from ..despachador import (Transporte, despachar, despachar_avisos_admin,
                           texto_error_seguro)
from ..huerfanos import barrer as barrer_huerfanos
from ..incidentes import registrar_incidente

from .avisos import enviar_avisos
from .botones import ConOpciones
from .escalera import correr_escalera
from .ia import IA
from .tiempo import Reloj

ETAPA_CICLO = "motor_ciclo"
CADA_S = 60.0


class Ciclo:
    def __init__(self, conn: psycopg.Connection, workspace_id: str, ia: IA, reloj: Reloj,
                 transporte: Transporte, *, transporte_admin: Transporte | None = None,
                 seguimiento: bool = True, cada_s: float = CADA_S,
                 monotono: Callable[[], float] = time.monotonic,
                 imprimir: Callable[[str], None] = print) -> None:
        self.conn = conn
        self.ws = workspace_id
        self.ia = ia
        self.reloj = reloj
        self.transporte = transporte
        self.transporte_admin = transporte_admin
        self.seguimiento = seguimiento      # sin él, sólo despacha (el escuchador de antes)
        self.cada_s = cada_s
        self.monotono = monotono
        self.imprimir = imprimir
        self._ultima: float | None = None
        self.caidos: set[str] = set()       # pasos con su incidente ya registrado

    def vuelta(self, *, admin: bool = True) -> dict[str, Any]:
        """Una vuelta: lo que toca correr, cada paso aislado. Devuelve el resultado de cada
        paso que corrió (`None` si se cayó)."""
        resultados: dict[str, Any] = {}
        if self.seguimiento and (self._ultima is None
                                 or self.monotono() - self._ultima >= self.cada_s):
            self._ultima = self.monotono()
            resultados["escalera"] = self._paso(
                "escalera", lambda: correr_escalera(self.conn, self.ws, self.reloj))
            resultados["avisos"] = self._paso(
                "avisos", lambda: enviar_avisos(self.conn, self.ws, self.ia, self.reloj))
        resultados["huerfanos"] = self._paso(
            "huerfanos", lambda: barrer_huerfanos(self.conn, self.ws, self.reloj.ahora()))
        resultados["despacho"] = self._paso("despacho", self._despachar)
        if admin and self.transporte_admin is not None:
            resultados["avisos_admin"] = self._paso("avisos_admin", self._despachar_admin)
        self._contar(resultados)
        return resultados

    # -- los pasos ---------------------------------------------------------------------------

    def _despachar(self) -> dict[str, int]:
        with espacio(self.conn, self.ws) as cur:
            # Las respuestas que preguntan una duda salen con sus opciones (`botones`).
            return despachar(cur, self.ws, ConOpciones(self.transporte, cur),
                             Calendario.desde_base(cur, self.ws), self.reloj.ahora())

    def _despachar_admin(self) -> dict[str, int]:
        with admin(self.conn) as cur:
            return despachar_avisos_admin(cur, self.transporte_admin)

    def _paso(self, nombre: str, correr: Callable[[], Any]) -> Any:
        try:
            resultado = correr()
            self.conn.commit()
        except Exception as e:  # noqa: BLE001 -- un paso no frena a los demás ni al escuchador
            self.conn.rollback()
            self._caido(nombre, e)
            return None
        if nombre in self.caidos:
            self.caidos.discard(nombre)
            self.imprimir(f"  ✓ el ciclo: {nombre} volvió a andar")
        return resultado

    def _caido(self, nombre: str, error: Exception) -> None:
        self.imprimir(f"  ! el ciclo: se cayó {nombre} ({type(error).__name__})")
        if nombre in self.caidos:
            return
        try:
            with espacio(self.conn, self.ws) as cur:
                registrar_incidente(
                    cur, self.ws,
                    f"Se cayó el paso «{nombre}» del ciclo del motor de conversación. Los "
                    f"demás pasos siguieron y éste se reintenta en cada vuelta; mientras siga "
                    f"cayéndose no se registra otro incidente.",
                    severidad="alta", referencia_cruda=texto_error_seguro(error),
                    etapa=ETAPA_CICLO, avisar_admin=nombre != "avisos_admin")
            self.conn.commit()
            self.caidos.add(nombre)
        except Exception as e:  # noqa: BLE001 -- queda en la consola; se reintenta
            self.conn.rollback()
            self.imprimir(f"  ! tampoco se pudo registrar la caída: {texto_error_seguro(e)}")

    def _contar(self, resultados: dict[str, Any]) -> None:
        """Lo que hizo la vuelta, en la consola del escuchador, sólo si hizo algo."""
        for nombre in ("escalera", "avisos"):
            if resultados.get(nombre):
                self.imprimir(f"  ⏱ {nombre}: {resultados[nombre]}")
        if resultados.get("huerfanos"):
            self.imprimir(f"  ! {resultados['huerfanos']} mensaje(s) sin respuesta: salió el "
                          f"aviso neutro y quedó el incidente")
        pospuestos = (resultados.get("despacho") or {}).get("pospuestos")
        if pospuestos:
            self.imprimir(f"  … {pospuestos} pospuesto(s) hasta la próxima jornada")
