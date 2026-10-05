"""Corre las conversaciones de prueba: `python -m prueba_chica.correr` (E2-7).

`odd/tasks/prueba-chica-del-motor.md`, sección 6 y decisiones 10.3 y 10.4. Uso:

    python -m prueba_chica.correr [--conversacion NN ...] [--veces 5] [--ia sol|luna|guionada]
                                  [--jev] [--grabar CARPETA] [--repetir ARCHIVO] [--paralelo N]
                                  [--ronda NOMBRE] [--sin-informe] [--pasar-el-techo]

- `--ia guionada` (por omisión) elige las jugadas que cada paso espera: la corrida en seco, sin
  gasto. `sol` y `luna` son GPT-6 sol y luna por OpenRouter (decisión 6), con la clave del
  entorno, que nunca se imprime.
- `--jev` consulta a Jev en paralelo en los pasos que lo piden (conversaciones 13 y 14), sin que
  decida nada (decisión 7).
- `--grabar CARPETA` guarda lo que respondió la IA en cada corrida; `--repetir ARCHIVO` corre esa
  grabación otra vez con la IA guionada que la repite, para mirar una falla.
- `--paralelo N` corre N corridas a la vez, cada una en su base.
- Cada corrida usa una base nueva, copia de una plantilla con el esquema que se crea una vez por
  ejecución, en el servidor de `LEDA_TEST_DB_URL` (`.env.test`), y se borra al terminar. Nunca
  toca `leda`, `leda_flujo` ni `leda_motor`.
- **El techo de gasto** (USD 30 para la etapa, 10.4): antes de empezar se estima la ronda; si se
  pasa, no corre, salvo con `--pasar-el-techo`, que se usa sólo con el OK del usuario. Avisa al
  llegar al 80 %. La cuenta queda en `prueba_chica/resultados/gasto.json`.
- El informe de la ronda queda en `prueba_chica/resultados/` (`informe.py`).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MODELOS = {"sol": "openai/gpt-6-sol", "luna": "openai/gpt-6-luna"}
PROHIBIDAS = frozenset({"leda", "leda_flujo", "leda_motor"})
PREFIJO = "leda_corrida_"


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
        self.plantilla = f"{PREFIJO}plantilla_{uuid.uuid4().hex[:10]}"
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
        nombre = f"{PREFIJO}{uuid.uuid4().hex[:12]}"
        with self._candado:      # copiar de la plantilla pide que nadie más la esté copiando
            self._ejecutar(SQL("create database {} template {}").format(
                Identifier(nombre), Identifier(self.plantilla)))
        return nombre, self._url(nombre)

    def borrar(self, nombre: str) -> None:
        from psycopg.sql import SQL, Identifier
        assert nombre.startswith(PREFIJO)
        self._ejecutar(SQL("drop database if exists {} with (force)").format(Identifier(nombre)))


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, check=True,
                              capture_output=True, text=True).stdout.strip()
    except Exception:       # noqa: BLE001 -- el informe dice que no se supo
        return "?"


def _ia_real(modelo: str):
    from leda.config import config
    from leda.llm import BASE_URLS

    from .carga import TONO
    from .gasto import ClienteQueCuenta
    from .ia_real import IAReal
    from .instrucciones import Tono

    clave = config.clave_llm("openrouter")
    if not clave:
        raise SystemExit(f"Falta {config.variable_clave_llm('openrouter')} en el entorno.")
    cliente = ClienteQueCuenta.crear(modelo, clave, BASE_URLS["openrouter"], {})
    return IAReal(cliente, Tono(**TONO), nombre=f"openrouter/{modelo}")


def _jev():
    from leda.config import config
    from leda.jev import ClienteJev
    if not config.openrouter_api_key:
        raise SystemExit("Falta LEDA_OPENROUTER_API_KEY para Jev.")
    return ClienteJev(api_key=config.openrouter_api_key)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m prueba_chica.correr",
                                description="Corre las conversaciones de prueba del Motor.")
    p.add_argument("--conversacion", nargs="*", metavar="NN")
    p.add_argument("--veces", type=int, default=5)
    p.add_argument("--ia", choices=["guionada", *MODELOS], default="guionada")
    p.add_argument("--jev", action="store_true")
    p.add_argument("--grabar", type=Path, metavar="CARPETA")
    p.add_argument("--repetir", type=Path, metavar="ARCHIVO")
    p.add_argument("--paralelo", type=int, default=1)
    p.add_argument("--ronda")
    p.add_argument("--sin-informe", action="store_true")
    p.add_argument("--pasar-el-techo", action="store_true")
    a = p.parse_args(argv)
    if not sys.stdout.isatty() and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")     # una consola de Windows queda como está

    real = a.ia in MODELOS or a.jev
    if not real:
        # Sin IA real no hace falta ninguna clave: el `.env` de la carpeta no se carga.
        os.environ["LEDA_LOAD_DOTENV"] = "0"
    os.environ["LEDA_TEST_DB_URL"] = _url_de_mantenimiento()

    from leda.db import conectar

    from . import informe
    from .corredor import consultas_a_jev, correr_conversacion, elegir, llamadas_previstas
    from .gasto import (JEV_USD_POR_LLAMADA, MARGEN_DE_LA_ESTIMACION, Gasto, TechoAlcanzado,
                        costo_de_las_llamadas, modelo_de)
    from .grabar import IAPerfecta, IAQueGraba, IARepetida

    if a.repetir:
        grabada = json.loads(a.repetir.read_text("utf-8"))
        convs = elegir([grabada["conversacion"]])
        trabajos = [(convs[0], grabada.get("vez", 1))]
    else:
        convs = elegir(a.conversacion)
        trabajos = [(c, vez) for c in convs for vez in range(1, a.veces + 1)]

    def nueva_ia(conv):
        if a.repetir:
            return IAQueGraba(IARepetida.desde_archivo(a.repetir))
        if a.ia == "guionada":
            return IAQueGraba(IAPerfecta({k: t["titulo"] for k, t in conv["tareas"].items()}))
        return IAQueGraba(_ia_real(MODELOS[a.ia]))

    gasto = Gasto()
    modelo = MODELOS.get(a.ia, a.ia)

    def estimado(conv) -> float:
        usd = 0.0
        if a.ia in MODELOS and not a.repetir:
            usd += (llamadas_previstas(conv) * MARGEN_DE_LA_ESTIMACION
                    * gasto.por_llamada(modelo))
        if a.jev:
            usd += consultas_a_jev(conv) * 2 * JEV_USD_POR_LLAMADA
        return usd

    if real and not a.repetir:
        total = sum(estimado(c) for c, _ in trabajos)
        print(f"Estimado de la ronda: USD {total:.2f}; gastado en la etapa: USD "
              f"{gasto.total():.2f}; techo: USD {gasto.techo:.2f}.")
        try:
            gasto.reservar(total, pasar_el_techo=a.pasar_el_techo)
            gasto.liberar(total)
        except TechoAlcanzado as e:
            print(e)
            return 2

    jev = _jev() if a.jev else None
    bases = Bases(os.environ["LEDA_TEST_DB_URL"])
    bases.crear_plantilla()
    corridas = []
    imprimir = threading.Lock()

    def correr(trabajo):
        conv, vez = trabajo
        reservado = estimado(conv) if real and not a.repetir else 0.0
        if reservado:
            gasto.reservar(reservado, pasar_el_techo=a.pasar_el_techo)
        nombre, url = bases.nueva()
        try:
            conn = conectar(url)
            try:
                ia = nueva_ia(conv)
                corrida = correr_conversacion(conn, conv, ia, vez=vez, jev=jev)
            finally:
                conn.close()
        except BaseException:
            if reservado:
                gasto.liberar(reservado)
            raise
        finally:
            bases.borrar(nombre)
        if real and not a.repetir:
            costo = (costo_de_las_llamadas(corrida.llamadas, modelo_de(ia.nombre))
                     if a.ia in MODELOS else {"llamadas": 0, "tokens_entrada": 0,
                                              "tokens_salida": 0, "usd": 0.0,
                                              "llamadas_estimadas": 0})
            jev_llamadas = sum(p.jev.get("llamadas", 0) for p in corrida.pasos if p.jev)
            costo.update(jev_llamadas=jev_llamadas,
                         jev_usd=round(jev_llamadas * JEV_USD_POR_LLAMADA, 6))
            corrida.costo = costo
            gasto.anotar({"cuando": datetime.now().isoformat(timespec="seconds"),
                          "ronda": ronda, "modelo": modelo if a.ia in MODELOS else "-",
                          "conversacion": corrida.numero, "vez": vez, **costo},
                         reservado=reservado)
        if a.grabar:
            a.grabar.mkdir(parents=True, exist_ok=True)
            (a.grabar / f"{corrida.numero}-{a.ia}-{vez}.json").write_text(json.dumps(
                {"conversacion": corrida.numero, "vez": vez, "ia": corrida.ia,
                 "llamadas": corrida.llamadas,
                 "jev": [p.jev for p in corrida.pasos if p.jev]},
                ensure_ascii=False, indent=1, default=str), "utf-8")
        with imprimir:
            estado = "ERROR" if corrida.error else ("bien" if corrida.bien else
                                                    f"{len(corrida.fallas())} falla(s)")
            print(f"  {corrida.numero} vez {vez}: {estado}", flush=True)
        return corrida

    ronda = a.ronda or (f"{datetime.now():%Y-%m-%d-%H%M}-{a.ia}"
                        + ("-repeticion" if a.repetir else "") + ("-jev" if a.jev else ""))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, a.paralelo)) as ej:
            futuros = [ej.submit(correr, t) for t in trabajos]
            for f in concurrent.futures.as_completed(futuros):
                try:
                    corridas.append(f.result())
                except TechoAlcanzado as e:
                    print(f"  {e}")
    finally:
        bases.borrar(bases.plantilla)

    bien = sum(c.bien for c in corridas)
    print(f"Corridas: {len(corridas)}; todo lo automático bien: {bien}; con fallas: "
          f"{len(corridas) - bien}; garantías bien: {sum(c.garantias for c in corridas)}.")
    if not a.sin_informe and corridas:
        cabecera = {"Fecha": f"{datetime.now():%Y-%m-%d %H:%M}", "Commit": _commit(),
                    "IA": corridas[0].ia, "Veces": a.veces if not a.repetir else 1,
                    "Jev": "sí" if a.jev else "no",
                    "Gasto de la etapa": f"USD {gasto.total():.2f} de {gasto.techo:.0f}"
                    if real else "sin gasto"}
        resumen, _ = informe.escribir(corridas, ronda=ronda, cabecera=cabecera)
        print(f"Informe: {resumen.relative_to(RAIZ)}")
    return 0 if corridas and all(c.error is None for c in corridas) else 1


if __name__ == "__main__":
    sys.exit(main())
