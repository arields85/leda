"""Corre las conversaciones de prueba: `python -m tests.conversaciones.correr` (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6 y decisiones 10.3 y 10.4; para el motor y la IA,
`odd/tasks/motor-definitivo.md`, E3-8. Uso:

    python -m tests.conversaciones.correr [--conversacion NN ...] [--veces 5]
                                          [--motor leda.motor]
                                          [--ia guionada|ALIAS|PROVEEDOR/MODELO]
                                          [--parametros JSON | --parametros-archivo ARCHIVO]
                                          [--grabar CARPETA] [--repetir ARCHIVO] [--paralelo N]
                                          [--ronda NOMBRE] [--sin-informe] [--pasar-el-techo]

- `--motor` elige el motor de conversación (`motores.py`): hoy hay uno solo, el definitivo, que
  es el de omisión.
- `--ia guionada` (por omisión) elige las jugadas que cada paso espera: la corrida en seco, sin
  gasto. Una IA real es `PROVEEDOR/MODELO`, con cualquier proveedor de `leda.llm.BASE_URLS`
  (`openrouter/openai/gpt-6-luna-pro`, `nan/deepseek-v4-flash`), o uno de los nombres cortos de
  `ALIAS` (`sol`, `luna`, `luna-pro`, `deepseek-flash`, `glm-flash`...). La clave es la del
  proveedor en el entorno (`leda.config.clave_llm`), que nunca se imprime. Con `chatgpt`
  (`chatgpt/gpt-6-sol`, o `sol-suscripcion`) no hay clave: es la sesión de la suscripción del
  usuario (`python -m leda chatgpt login`), y la libreta anota `precio: suscripción`.
- `--parametros '<json>'` (o `--parametros-archivo`) son los parámetros del cliente de la IA, los
  mismos de `model_config.parametros` (`leda.motor.ia_real.validar_parametros`: `timeout_s`,
  `plazo_s`, `tope_jugadas`, `tope_redaccion`, `cuerpo_extra`...); uno que no vale no corre.
  Sin ellos, los de omisión. Los nombres de `SIN_RAZONAR` (`glm-sin-razonar`,
  `deepseek-sin-razonar`) traen el modelo de `nan` con los suyos para que no razone por dentro
  (E3-8: la primera regresión los corrió sin parámetros y falló por los límites);
  `--parametros` se suma a ellos. Quedan en la cabecera del informe y en la libreta.
- `--grabar CARPETA` guarda lo que respondió la IA en cada corrida; `--repetir ARCHIVO` corre esa
  grabación otra vez con la IA guionada que la repite, para mirar una falla.
- `--paralelo N` corre N corridas a la vez, cada una en su base.
- Cada corrida usa una base nueva, copia de una plantilla con el esquema que se crea una vez por
  ejecución, en el servidor de `LEDA_TEST_DB_URL` (`.env.test`), y se borra al terminar. Nunca
  toca `leda`, `leda_flujo` ni `leda_motor`. La plantilla se borra aunque la ejecución se caiga
  (y al salir del proceso); las bases del corredor que quedaron de una ejecución muerta (con el
  nombre que él les pone y más viejas que `VIEJA`, por la fecha de ese nombre) se borran al
  empezar la siguiente; ninguna otra.
- **El techo de gasto** (USD 30 para la etapa, 10.4): antes de empezar se estima la ronda; si se
  pasa, no corre (sale con 2), salvo con `--pasar-el-techo`, que se usa sólo con el OK del
  usuario. Avisa al llegar al 80 %. La cuenta queda en `resultados/gasto.json`.
- **Una ronda cortada** (revisión de la E2-7): si una corrida llega al techo a mitad de la ronda,
  o se cae por otra cosa, lo que la IA ya gastó queda igual en la libreta (marcado `cortada`, con
  el motivo), el informe lo dice en "Ronda cortada" y la ejecución sale con error: 2 por el
  techo, 1 por otra cosa. Nunca termina en 0 con corridas que no corrieron.
- **Precio desconocido:** con un proveedor que no informa el costo (`nan`), la ronda no se estima
  ni cuenta para el techo; la libreta anota los tokens y que el precio es desconocido.
- **Sin crédito en el proveedor** (rondas 2 y 3: la cuenta se quedó sin crédito a mitad de ronda y
  el corredor siguió): antes de una ronda real por OpenRouter se pregunta cuánto crédito le queda a
  la cuenta y, si no alcanza para lo estimado, no corre (imprime sólo las dos cifras). Si no se
  puede preguntar, avisa y sigue. Con otro proveedor no se pregunta. Si una llamada a la IA
  choca con un 402 a mitad de ronda, no empieza ninguna corrida más, las que lo tuvieron son
  **inválidas** (fuera de la tabla, aparte en el informe) y la ronda queda cortada por "sin
  crédito en el proveedor"; sale con 3 (`SALIDA_SIN_CREDITO`). Las que terminaron antes valen.
- **Sin cuota en la suscripción** (regresión D6, 2026-10-08: la suscripción de ChatGPT se agotó y
  el corredor anotó 145 corridas fallidas, sin tokens): una llamada que choca con el HTTP 429
  `usage_limit_reached` (`gasto.SinCuota`) corta la ronda igual que un 402: no empieza ninguna
  corrida más, las que lo tuvieron son inválidas, el informe dice el motivo y cuándo se renueva
  la cuota, y sale con 4 (`SALIDA_SIN_CUOTA`). Un 429 con otro código no corta.
- El informe de la ronda queda en `resultados/` (`informe.py`), con el motor y la IA.
"""

from __future__ import annotations

import argparse
import atexit
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import threading
import traceback
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from leda.llm import PROVEEDORES_CON_SESION     # sin efectos: no carga el `.env`

from .motores import MOTORES, POR_OMISION

RAIZ = Path(__file__).resolve().parents[2]
GUIONADA = "guionada"
# Los nombres cortos de las IA de las rondas, `PROVEEDOR/MODELO`. Sol y luna por OpenRouter
# (decisión 6); sol61 y sonnet, de la segunda ronda (usuario, 2026-10-05); luna pro y los dos de
# `nan`, de la comparación de IA de la E3-8 (usuario, 2026-10-06).
ALIAS = {"sol": "openrouter/openai/gpt-6-sol", "luna": "openrouter/openai/gpt-6-luna",
         "luna-pro": "openrouter/openai/gpt-6-luna-pro",
         "sol61": "openrouter/openai/gpt-6.1-sol",
         "sonnet": "openrouter/anthropic/claude-sonnet-5.5",
         "deepseek-flash": "nan/deepseek-v4-flash", "glm-flash": "nan/glm5.3-flash",
         # Sol por la suscripción de ChatGPT del usuario (decisión del 2026-10-07).
         "sol-suscripcion": "chatgpt/gpt-6-sol"}
# Los dos de `nan` sin razonar por dentro (E3-8): cada uno con el campo del pedido que `nan`
# acepta para eso, y más tiempo que el de omisión. GLM cuenta lo que razona dentro del tope y
# podía volver vacío y cortado.
SIN_RAZONAR = {
    "glm-sin-razonar": ("nan/glm5.3-flash", {
        "cuerpo_extra": {"reasoning_effort": "low"}, "timeout_s": 60, "plazo_s": 90}),
    "deepseek-sin-razonar": ("nan/deepseek-v4-flash", {
        "cuerpo_extra": {"chat_template_kwargs": {"enable_thinking": False}},
        "timeout_s": 60, "plazo_s": 90}),
}
# `nan` puede devolver la misma respuesta a un pedido idéntico: lo dice el informe.
NOTA_DE_CACHE = ("nan puede guardar en caché los pedidos idénticos: las repeticiones no son "
                 "muestras del todo independientes.")
PROHIBIDAS = frozenset({"leda", "leda_flujo", "leda_motor"})
PREFIJO = "leda_corrida_"
# Lo que devuelve una ronda sin crédito en el proveedor: distinto del techo (2) y de una caída (1).
SALIDA_SIN_CREDITO = 3
# Lo que devuelve una ronda cortada por el límite de uso de la suscripción (HTTP 429).
SALIDA_SIN_CUOTA = 4
# Una base del corredor más vieja que esto es de una ejecución que murió sin borrarla: ninguna
# ronda dura tanto. La fecha va en el nombre (`_nombre`), en UTC.
VIEJA = timedelta(hours=12)
# El nombre entero de una base que crea el corredor (`_nombre`): el prefijo, la plantilla o no,
# la fecha y ocho cifras al azar. Sólo una base con este nombre es suya; cualquier otra que
# empiece con el prefijo (sin fecha, o con otra forma) no se toca nunca.
_NOMBRE_DEL_CORREDOR = re.compile(rf"^{PREFIJO}(?:plantilla_)?(\d{{14}})_[0-9a-f]{{8}}$")


def _url_de_mantenimiento() -> str:
    """`LEDA_TEST_DB_URL`, del entorno o de `.env.test` (sin cargar el `.env` de la carpeta para
    esto). Nunca se imprime."""
    if os.environ.get("LEDA_TEST_DB_URL"):
        return os.environ["LEDA_TEST_DB_URL"]
    ruta = RAIZ / ".env.test"
    if ruta.exists():
        for linea in ruta.read_text("utf-8").splitlines():
            clave, _, valor = linea.strip().partition("=")
            if clave.strip() == "LEDA_TEST_DB_URL" and valor.strip():
                return valor.strip()
    raise SystemExit("Hace falta LEDA_TEST_DB_URL (en .env.test) para crear las bases.")


class Bases:
    """Una plantilla con el esquema por ejecución; una base por corrida, copia de ella."""

    def __init__(self, mantenimiento: str) -> None:
        from psycopg.conninfo import conninfo_to_dict
        self.mantenimiento = mantenimiento
        self.partes = conninfo_to_dict(mantenimiento)
        if self.partes.get("dbname") in PROHIBIDAS:
            raise SystemExit("LEDA_TEST_DB_URL apunta a una base de trabajo: no se usa.")
        self.plantilla = _nombre("plantilla_")
        self._candado = threading.Lock()

    def _url(self, nombre: str) -> str:
        from psycopg.conninfo import make_conninfo
        assert nombre.startswith(PREFIJO) and nombre not in PROHIBIDAS
        return make_conninfo(**{**self.partes, "dbname": nombre})

    def _ejecutar(self, sql) -> None:
        import psycopg
        with psycopg.connect(self.mantenimiento, autocommit=True) as c:
            c.execute(sql)

    def crear_plantilla(self) -> None:
        import psycopg
        from psycopg.sql import SQL, Identifier
        self._ejecutar(SQL("create database {}").format(Identifier(self.plantilla)))
        with psycopg.connect(self._url(self.plantilla), autocommit=True) as c:
            c.execute((RAIZ / "db" / "esquema.sql").read_text("utf-8"))

    def nueva(self) -> tuple[str, str]:
        from psycopg.sql import SQL, Identifier
        nombre = _nombre()
        with self._candado:      # copiar de la plantilla pide que nadie más la esté copiando
            self._ejecutar(SQL("create database {} template {}").format(
                Identifier(nombre), Identifier(self.plantilla)))
        return nombre, self._url(nombre)

    def borrar(self, nombre: str) -> None:
        from psycopg.sql import SQL, Identifier
        assert nombre.startswith(PREFIJO)
        self._ejecutar(SQL("drop database if exists {} with (force)").format(Identifier(nombre)))

    def limpiar_viejas(self, ahora: datetime | None = None) -> list[str]:
        """Borra las bases del corredor que dejó una ejecución muerta: las que tienen el nombre
        que les pone el corredor (`_NOMBRE_DEL_CORREDOR`) y son más viejas que `VIEJA`. Una de
        otra ejecución que corre ahora es más nueva y queda; una con otro nombre, aunque empiece
        con el prefijo, no es suya y queda siempre. Devuelve las que borró."""
        import psycopg
        ahora = ahora or datetime.now(timezone.utc)
        with psycopg.connect(self.mantenimiento, autocommit=True) as c:
            nombres = [f[0] for f in c.execute(
                "select datname from pg_database where starts_with(datname, %s)",
                (PREFIJO,)).fetchall()]
        borradas = []
        for nombre in nombres:
            if nombre in PROHIBIDAS or nombre == self.plantilla:
                continue
            fecha = _fecha_del_nombre(nombre)
            if fecha is not None and ahora - fecha > VIEJA:
                self.borrar(nombre)
                borradas.append(nombre)
        return borradas


def _nombre(tipo: str = "") -> str:
    """El nombre de una base del corredor, con la fecha en que se creó (UTC)."""
    return f"{PREFIJO}{tipo}{datetime.now(timezone.utc):%Y%m%d%H%M%S}_{uuid.uuid4().hex[:8]}"


def _fecha_del_nombre(nombre: str) -> datetime | None:
    """La fecha de una base del corredor; `None` si el nombre no es uno que él pone."""
    m = _NOMBRE_DEL_CORREDOR.fullmatch(nombre)
    if m is None:
        return None
    return datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, check=True,
                              capture_output=True, text=True).stdout.strip()
    except Exception:       # noqa: BLE001 -- el informe dice que no se supo
        return "?"


def ia_pedida(texto: str) -> tuple[str, str] | None:
    """`(proveedor, modelo)` de lo que dice `--ia` (un nombre de `ALIAS` o `PROVEEDOR/MODELO`), o
    `None` para la guionada. Un proveedor que no está en `leda.llm.BASE_URLS` es un error."""
    if texto == GUIONADA:
        return None
    from leda.llm import BASE_URLS

    completo = SIN_RAZONAR[texto][0] if texto in SIN_RAZONAR else ALIAS.get(texto, texto)
    proveedor, _, modelo = completo.partition("/")
    if proveedor not in BASE_URLS or not modelo:
        raise ValueError(f"--ia {texto!r}: tiene que ser {GUIONADA}, uno de "
                         f"{', '.join([*ALIAS, *SIN_RAZONAR])} o PROVEEDOR/MODELO, con un "
                         f"proveedor de {', '.join(BASE_URLS)}.")
    return proveedor, modelo


def parametros_pedidos(ia: str, texto: str | None = None, *,
                       archivo: Path | None = None) -> dict:
    """Los parámetros del cliente de la IA: los del nombre de `SIN_RAZONAR`, si lo es, con los de
    `--parametros` (el JSON `texto`) o `--parametros-archivo` encima. Revisados como los de
    `model_config.parametros`; un JSON que no es un objeto o un valor que no vale es
    `ValueError`, nombrándolo."""
    from leda.motor.ia_real import validar_parametros

    parametros = dict(SIN_RAZONAR[ia][1]) if ia in SIN_RAZONAR else {}
    if archivo is not None:
        texto = archivo.read_text("utf-8")
    if texto is not None:
        try:
            explicitos = json.loads(texto)
        except ValueError as e:
            raise ValueError(f"--parametros no es JSON ({e}).") from None
        if not isinstance(explicitos, dict):
            raise ValueError(f"--parametros tiene que ser un objeto JSON; vino {texto!r}.")
        parametros.update(explicitos)
    validar_parametros(parametros)          # ParametrosInvalidos es un ValueError
    try:
        pedida = ia_pedida(ia)
    except ValueError:
        pedida = None
    if pedida is not None and pedida[0] in PROVEEDORES_CON_SESION:
        from leda.motor.chatgpt import validar_parametros_chatgpt
        validar_parametros_chatgpt(parametros)      # lo que la suscripción no recibe
    return parametros


def _nombre_de_archivo(texto: str) -> str:
    """Un nombre que sirve en un archivo: `openrouter/openai/gpt-6-sol` →
    `openrouter-openai-gpt-6-sol`."""
    return re.sub(r"[^\w.-]+", "-", texto)


def _ia_real(proveedor: str, modelo: str, motor, parametros: dict | None = None):
    """La IA real del `motor` (`motores.Motor`) en ese proveedor, con el cliente que cuenta lo
    que gasta y sus `parametros` (`parametros_pedidos`). La clave es la de ese proveedor y nunca
    se imprime."""
    from leda.config import config
    from leda.llm import BASE_URLS

    from .carga import TONO
    from .gasto import ClienteChatGPTQueCuenta, ClienteQueCuenta

    if proveedor in PROVEEDORES_CON_SESION:
        # La suscripción de ChatGPT: la sesión de `python -m leda chatgpt login`, sin clave.
        from leda.motor.chatgpt import SesionChatGPT
        try:
            sesion = SesionChatGPT.abrir()
        except (LookupError, ValueError) as e:
            raise SystemExit(str(e)) from None
        cliente = ClienteChatGPTQueCuenta.crear(modelo, sesion, parametros or {})
        return motor.IAReal(cliente, motor.Tono(**TONO), nombre=f"{proveedor}/{modelo}")
    clave = config.clave_llm(proveedor)
    if not clave:
        raise SystemExit(f"Falta {config.variable_clave_llm(proveedor)} en el entorno.")
    cliente = ClienteQueCuenta.crear(modelo, clave, BASE_URLS[proveedor], parametros or {})
    return motor.IAReal(cliente, motor.Tono(**TONO), nombre=f"{proveedor}/{modelo}")


def _credito_restante() -> float | None:
    """Los USD que le quedan a la cuenta de OpenRouter, o `None` si no se pudo saber. La clave
    es la del entorno, como para la IA, y nunca se imprime."""
    from leda.config import config
    from leda.llm import BASE_URLS

    from .gasto import credito_restante

    clave = config.clave_llm("openrouter")
    if not clave:
        return None
    return credito_restante(clave, BASE_URLS["openrouter"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tests.conversaciones.correr",
                                description="Corre las conversaciones de prueba del Motor.")
    p.add_argument("--conversacion", nargs="*", metavar="NN")
    p.add_argument("--veces", type=int, default=5)
    p.add_argument("--ia", default=GUIONADA, metavar="guionada|ALIAS|PROVEEDOR/MODELO",
                   help=f"la IA de la ronda; nombres cortos: {', '.join([*ALIAS, *SIN_RAZONAR])}")
    con_parametros = p.add_mutually_exclusive_group()
    con_parametros.add_argument("--parametros", metavar="JSON",
                                help="los parámetros del cliente de la IA, como en "
                                     "model_config.parametros")
    con_parametros.add_argument("--parametros-archivo", type=Path, metavar="ARCHIVO")
    p.add_argument("--motor", choices=MOTORES, default=POR_OMISION,
                   help="el motor de conversación que corre (hoy, sólo el definitivo)")
    p.add_argument("--grabar", type=Path, metavar="CARPETA")
    p.add_argument("--repetir", type=Path, metavar="ARCHIVO")
    p.add_argument("--paralelo", type=int, default=1)
    p.add_argument("--ronda")
    p.add_argument("--sin-informe", action="store_true")
    p.add_argument("--pasar-el-techo", action="store_true")
    a = p.parse_args(argv)
    if not sys.stdout.isatty() and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")     # una consola de Windows queda como está

    # Una repetición no llama a la IA: no gasta.
    real = a.ia != GUIONADA and not a.repetir
    if not real:
        # Sin IA real no hace falta ninguna clave: el `.env` de la carpeta no se carga.
        os.environ["LEDA_LOAD_DOTENV"] = "0"
    try:
        pedida = ia_pedida(a.ia)
    except ValueError as e:
        p.error(str(e))
    proveedor, modelo = pedida or ("-", "-")
    if (a.parametros is not None or a.parametros_archivo is not None) and not real:
        # Sin una IA real no hay cliente que los use: nunca se ignoran en silencio.
        p.error("--parametros va sólo con una IA real (no con la guionada ni con --repetir).")
    parametros: dict = {}
    if real:
        try:
            parametros = parametros_pedidos(a.ia, a.parametros, archivo=a.parametros_archivo)
        except (ValueError, OSError) as e:
            p.error(str(e))

    from . import informe
    from .motores import cargar as cargar_motor
    from .corredor import correr_conversacion, elegir, llamadas_previstas
    from .gasto import (MARGEN_DE_LA_ESTIMACION, POR_SUSCRIPCION, SIN_CREDITO, SIN_CUOTA, Gasto,
                        TechoAlcanzado, costo_de_las_llamadas, llamadas_sin_credito,
                        llamadas_sin_cuota, motivo_sin_cuota, precio_conocido)
    from .grabar import IAPerfecta, IAQueGraba, IARepetida

    motor = cargar_motor(a.motor)
    if a.repetir:
        grabada = json.loads(a.repetir.read_text("utf-8"))
        convs = elegir([grabada["conversacion"]])
        trabajos = [(convs[0], grabada.get("vez", 1))]
    else:
        convs = elegir(a.conversacion)
        trabajos = [(c, vez) for c in convs for vez in range(1, a.veces + 1)]

    def nueva_ia(conv):
        if a.repetir:
            return IAQueGraba(IARepetida.desde_archivo(a.repetir, jugada=motor.Jugada))
        if pedida is None:
            return IAQueGraba(IAPerfecta({k: t["titulo"] for k, t in conv["tareas"].items()},
                                         jugada=motor.Jugada))
        return IAQueGraba(_ia_real(proveedor, modelo, motor, parametros))

    gasto = Gasto()

    def estimado(conv) -> float:
        usd = 0.0
        if real:
            usd += (llamadas_previstas(conv) * MARGEN_DE_LA_ESTIMACION
                    * gasto.por_llamada(modelo, proveedor))
        return usd

    if real:
        total = sum(estimado(c) for c, _ in trabajos)
        if precio_conocido(proveedor):
            print(f"Estimado de la ronda: USD {total:.2f}; gastado en la etapa: USD "
                  f"{gasto.total():.2f}; techo: USD {gasto.techo:.2f}.")
        elif proveedor in POR_SUSCRIPCION:
            print(f"Por suscripción en {proveedor}: la ronda no se estima en USD ni cuenta para "
                  f"el techo; la libreta anota los tokens. Gastado en la etapa: USD "
                  f"{gasto.total():.2f}; techo: USD {gasto.techo:.2f}.")
        else:
            print(f"Precio desconocido en {proveedor}: la ronda no se estima ni cuenta para el "
                  f"techo; la libreta anota los tokens. Gastado en la etapa: USD "
                  f"{gasto.total():.2f}; techo: USD {gasto.techo:.2f}.")
        try:
            gasto.reservar(total, pasar_el_techo=a.pasar_el_techo)
            gasto.liberar(total)
        except TechoAlcanzado as e:
            print(e)
            return 2
        # El crédito se le pregunta sólo a OpenRouter: es el único que lo informa.
        restante = _credito_restante() if proveedor == "openrouter" else None
        if proveedor != "openrouter":
            print(f"Crédito en el proveedor: {proveedor} no lo informa; la ronda sigue sin esa "
                  "comprobación.")
        elif restante is None:
            print("Aviso: no se pudo consultar el crédito en el proveedor; la ronda sigue sin "
                  "esa comprobación.")
        else:
            print(f"Crédito en el proveedor: USD {restante:.2f}; la ronda necesita: USD "
                  f"{total:.2f}.")
            if restante < total:
                print("No alcanza: la ronda no empieza.")
                return SALIDA_SIN_CREDITO

    # El servidor de las bases, recién ahora: decidir el techo no lo necesita.
    os.environ["LEDA_TEST_DB_URL"] = _url_de_mantenimiento()
    import leda.db

    corridas = []
    cortes: list[dict] = []         # las corridas que no corrieron o no terminaron, y por qué
    invalidas: list = []            # (corrida, llamadas que chocaron con el proveedor)
    # Un 402 o el límite de uso de la suscripción: no empieza ninguna corrida más. El corte que
    # llegó primero manda (motivo, salida y cómo se dice en el informe).
    cortada_por_el_proveedor = threading.Event()
    corte_del_proveedor: dict = {}
    imprimir = threading.Lock()

    def anotar_el_gasto(conv, vez, ia, corrida, reservado: float, cortada: str | None,
                        invalida: str | None = None) -> None:
        """Lo que la IA gastó en la corrida, aunque se haya cortado: nunca se pierde."""
        llamadas = (corrida.llamadas if corrida is not None
                    else list(getattr(ia, "llamadas", None) or []))
        costo = (costo_de_las_llamadas(llamadas, modelo, proveedor=proveedor)
                 if ia is not None
                 else {"llamadas": 0, "tokens_entrada": 0, "tokens_salida": 0, "usd": 0.0,
                       "llamadas_estimadas": 0})
        if corrida is not None:
            corrida.costo = costo
        gasto.anotar({"cuando": datetime.now().isoformat(timespec="seconds"),
                      "ronda": ronda, "motor": motor.nombre, "proveedor": proveedor,
                      "modelo": modelo,
                      "conversacion": str(conv["numero"]).zfill(2), "vez": vez, **costo,
                      **({"parametros": parametros} if parametros else {}),
                      **({"cortada": cortada} if cortada else {}),
                      **({"invalida": invalida} if invalida else {})},
                     reservado=reservado)

    def cortar(numero: str, vez: int, motivo: str, *, techo: bool,
               credito: bool = False) -> None:
        cortes.append({"conversacion": numero, "vez": vez, "techo": techo,
                       "sin_credito": credito, "motivo": motivo})
        with imprimir:
            que = ("no corrió, llegó al techo" if techo else
                   "no corrió" if credito else "se cortó")
            print(f"  {numero} vez {vez}: {que} ({motivo})", flush=True)

    def con_corte(ia, corrida) -> tuple[int, dict | None]:
        """Cuántas llamadas de la corrida a la IA chocaron con el proveedor (un 402 o el límite
        de uso de la suscripción) y qué corte es."""
        llamadas = list(getattr(ia, "llamadas", None) or
                        (corrida.llamadas if corrida is not None else []))
        if n := llamadas_sin_credito(llamadas):
            return n, {"motivo": SIN_CREDITO, "anotada": SIN_CREDITO,
                       "salida": SALIDA_SIN_CREDITO, "con": "con 402",
                       "invalidas_por": informe.SIN_CREDITO_HTTP}
        if n := llamadas_sin_cuota(llamadas):
            return n, {"motivo": motivo_sin_cuota(llamadas), "anotada": SIN_CUOTA,
                       "salida": SALIDA_SIN_CUOTA, "con": "con el límite de uso",
                       "invalidas_por": "el límite de uso de la suscripción (HTTP 429 "
                                        "usage_limit_reached)"}
        return 0, None

    def correr(trabajo):
        conv, vez = trabajo
        numero = str(conv["numero"]).zfill(2)
        if cortada_por_el_proveedor.is_set():
            cortar(numero, vez, corte_del_proveedor["motivo"], techo=False, credito=True)
            return None
        reservado = estimado(conv) if real else 0.0
        if reservado:
            try:
                gasto.reservar(reservado, pasar_el_techo=a.pasar_el_techo)
            except TechoAlcanzado as e:
                cortar(numero, vez, str(e), techo=True)
                return None
        ia = corrida = None
        cortada: str | None = None
        n_cortadas, corte = 0, None
        try:
            nombre, url = bases.nueva()
            try:
                conn = leda.db.conectar(url)
                try:
                    ia = nueva_ia(conv)
                    corrida = correr_conversacion(conn, conv, ia, vez=vez, motor=motor)
                finally:
                    conn.close()
            finally:
                bases.borrar(nombre)
        except BaseException as e:
            cortada = "".join(traceback.format_exception_only(type(e), e)).strip()
            if not isinstance(e, Exception):
                raise                   # un corte desde la consola: el gasto se anota igual
            cortar(numero, vez, cortada, techo=False)
            return None
        finally:
            n_cortadas, corte = con_corte(ia, corrida)
            if n_cortadas:
                with imprimir:
                    if not corte_del_proveedor:
                        corte_del_proveedor.update(corte)
                cortada_por_el_proveedor.set()
            if real:
                anotar_el_gasto(conv, vez, ia, corrida, reservado, cortada,
                                corte["anotada"] if n_cortadas else None)
        if n_cortadas:
            invalidas.append((corrida, n_cortadas))
            with imprimir:
                print(f"  {corrida.numero} vez {vez}: INVÁLIDA, {corte['anotada']} ({n_cortadas} "
                      f"llamada(s) {corte['con']})", flush=True)
            return None
        if a.grabar:
            a.grabar.mkdir(parents=True, exist_ok=True)
            nombre_ia = _nombre_de_archivo(a.ia)
            (a.grabar / f"{corrida.numero}-{motor.nombre}-{nombre_ia}-{vez}.json").write_text(
                json.dumps({"conversacion": corrida.numero, "vez": vez, "ia": corrida.ia,
                            "motor": motor.nombre, "llamadas": corrida.llamadas},
                ensure_ascii=False, indent=1, default=str), "utf-8")
        with imprimir:
            estado = "ERROR" if corrida.error else ("bien" if corrida.bien else
                                                    f"{len(corrida.fallas())} falla(s)")
            print(f"  {corrida.numero} vez {vez}: {estado}", flush=True)
        return corrida

    ronda = a.ronda or (f"{datetime.now():%Y-%m-%d-%H%M}-{motor.nombre}-"
                        f"{_nombre_de_archivo(a.ia)}"
                        + ("-repeticion" if a.repetir else ""))
    bases = Bases(os.environ["LEDA_TEST_DB_URL"])
    for vieja in bases.limpiar_viejas():
        print(f"  (se borró una base que dejó una ejecución anterior: {vieja})")
    # La plantilla se borra pase lo que pase: al terminar, si algo se cae y, si el proceso
    # termina sin pasar por acá, al salir.
    borrar_la_plantilla = lambda: bases.borrar(bases.plantilla)     # noqa: E731
    atexit.register(borrar_la_plantilla)
    try:
        bases.crear_plantilla()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, a.paralelo)) as ej:
            futuros = [ej.submit(correr, t) for t in trabajos]
            for f in concurrent.futures.as_completed(futuros):
                corrida = f.result()
                if corrida is not None:
                    corridas.append(corrida)
    finally:
        atexit.unregister(borrar_la_plantilla)
        borrar_la_plantilla()

    bien = sum(c.bien for c in corridas)
    print(f"Corridas: {len(corridas)}; todo lo automático bien: {bien}; con fallas: "
          f"{len(corridas) - bien}; garantías bien: {sum(c.garantias for c in corridas)}.")
    if invalidas:
        print(f"Inválidas ({corte_del_proveedor['anotada']}): {len(invalidas)}.")
    if cortada_por_el_proveedor.is_set():
        print(f"Ronda cortada: {corte_del_proveedor['motivo']}.")
    if cortes:
        print(f"Ronda cortada: {len(cortes)} corrida(s) no corrieron o no terminaron.")
    if not a.sin_informe and (corridas or cortes or invalidas):
        cabecera = {"Fecha": f"{datetime.now():%Y-%m-%d %H:%M}", "Commit": _commit(),
                    "Motor": motor.nombre,
                    "IA": ([*corridas, *(c for c, _ in invalidas)][0].ia
                           if corridas or invalidas else a.ia),
                    "Veces": a.veces if not a.repetir else 1,
                    "Gasto de la etapa": f"USD {gasto.total():.2f} de {gasto.techo:.0f}"
                    if real else "sin gasto"}
        if real:
            cabecera["Parámetros de la IA"] = (
                f"`{json.dumps(parametros, ensure_ascii=False, sort_keys=True)}`"
                if parametros else "ninguno (los de omisión)")
        if real and proveedor == "nan":
            cabecera["Caché del proveedor"] = NOTA_DE_CACHE
        resumen, _ = informe.escribir(
            corridas, ronda=ronda, cabecera=cabecera, cortes=cortes, invalidas=invalidas,
            motivo_del_corte=corte_del_proveedor.get("motivo"),
            **({"invalidas_por": corte_del_proveedor["invalidas_por"]}
               if corte_del_proveedor else {}))
        print(f"Informe: {_relativa(resumen)}")
    if cortada_por_el_proveedor.is_set():
        return corte_del_proveedor["salida"]
    if any(c["techo"] for c in cortes):
        return 2
    return 0 if corridas and not cortes and all(c.error is None for c in corridas) else 1


def _relativa(ruta: Path) -> Path:
    try:
        return ruta.relative_to(RAIZ)
    except ValueError:
        return ruta


if __name__ == "__main__":
    sys.exit(main())
