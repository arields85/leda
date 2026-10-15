"""El candado de la sesión de ChatGPT entre procesos (`leda.motor.chatgpt`).

La escucha y una ronda del corredor son dos procesos con la misma sesión. Si los dos ven el
acceso por vencer y renuevan a la vez, el segundo usa un token de refresco que el emisor ya
consumió (la sesión se rompe) o pisa los tokens más nuevos del otro. El candado hace que sólo
uno renueve; el otro espera, vuelve a leer el archivo y usa lo que el primero guardó.

Nunca se toca la sesión real: todo pasa en un directorio temporal, con un emisor falso.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import threading
import time
from datetime import timedelta
from pathlib import Path

import httpx
import pytest

from leda.motor import chatgpt
from leda.motor.chatgpt import SesionChatGPT, SesionChatGPTOcupada, SesionChatGPTVencida
from tests.motor.test_chatgpt import AHORA, tokens_del_emisor

POR_VENCER = AHORA + timedelta(minutes=2)


class EmisorLento:
    """`auth.openai.com`, de mentira y seguro entre hilos: cada renovación tarda un poco (para
    que la otra llegue mientras tanto) y devuelve tokens distintos."""

    def __init__(self, demora_s: float = 0.3) -> None:
        self.demora_s = demora_s
        self.renovaciones = 0
        self._candado = threading.Lock()

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        with self._candado:
            self.renovaciones += 1
            numero = self.renovaciones
        time.sleep(self.demora_s)
        return httpx.Response(200, json=tokens_del_emisor(sufijo=f"nuevo-{numero}"))


def guardar_por_vencer(ruta: Path) -> None:
    chatgpt.guardar(ruta, chatgpt.tokens_de_la_respuesta(tokens_del_emisor(vence=POR_VENCER),
                                                         AHORA))


def sesion(ruta: Path, emisor, **opciones) -> SesionChatGPT:
    return SesionChatGPT(ruta, transporte=httpx.MockTransport(emisor), reloj=lambda: AHORA,
                         **opciones)


def _proceso_que_toma_el_candado(ruta: Path, *, despues: str) -> subprocess.Popen:
    """Otro proceso de Python que toma el candado de `ruta`, avisa por su salida y después
    hace `despues` (dormir sin soltarlo, o morirse sin soltarlo)."""
    codigo = textwrap.dedent(f"""
        import os, sys, time
        from pathlib import Path
        from leda.motor import chatgpt
        with chatgpt.candado_de_la_sesion(Path({str(ruta)!r}), espera_s=5):
            print("tomado", flush=True)
            {despues}
    """)
    entorno = dict(os.environ)
    src = str(Path(chatgpt.__file__).resolve().parents[2])
    entorno["PYTHONPATH"] = src + os.pathsep + entorno.get("PYTHONPATH", "")
    proceso = subprocess.Popen([sys.executable, "-c", codigo], stdout=subprocess.PIPE,
                               text=True, env=entorno)
    assert proceso.stdout.readline().strip() == "tomado"
    return proceso


# --- Dos que renuevan a la vez ------------------------------------------------------------

def test_dos_sesiones_que_renuevan_a_la_vez_piden_una_sola_renovacion(tmp_path):
    ruta = tmp_path / "s.json"
    guardar_por_vencer(ruta)
    emisor = EmisorLento()
    # Dos sesiones separadas sobre el mismo archivo: cada una con su candado de hilos, como
    # dos procesos (la escucha y el corredor).
    sesiones = [sesion(ruta, emisor), sesion(ruta, emisor)]
    largada = threading.Barrier(2)
    accesos: list[str] = []
    fallas: list[BaseException] = []

    def renovar(s: SesionChatGPT) -> None:
        largada.wait()
        try:
            accesos.append(s.credenciales()[0])
        except BaseException as e:  # noqa: BLE001 -- se muestra en la aserción
            fallas.append(e)

    hilos = [threading.Thread(target=renovar, args=(s,)) for s in sesiones]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join(10)

    assert fallas == []
    assert emisor.renovaciones == 1
    guardado = chatgpt.cargar(ruta)
    assert accesos == [guardado.access_token] * 2
    assert guardado.refresh_token == "refresco-secreto-nuevo-1"


def test_quien_espera_el_candado_usa_lo_que_renovo_el_otro_sin_renovar(tmp_path):
    ruta = tmp_path / "s.json"
    guardar_por_vencer(ruta)
    emisor = EmisorLento(demora_s=0)
    primera, segunda = sesion(ruta, emisor), sesion(ruta, emisor)
    segunda._tokens = chatgpt.cargar(ruta)          # ya leyó lo viejo

    primera.credenciales()
    acceso, _ = segunda.credenciales()

    assert emisor.renovaciones == 1
    assert acceso == chatgpt.cargar(ruta).access_token


# --- Un candado que nadie suelta ----------------------------------------------------------

def test_otro_proceso_con_el_candado_hace_esperar_y_al_final_falla_a_la_vista(tmp_path):
    ruta = tmp_path / "s.json"
    guardar_por_vencer(ruta)
    emisor = EmisorLento(demora_s=0)
    otro = _proceso_que_toma_el_candado(ruta, despues="time.sleep(30)")
    try:
        inicio = time.monotonic()
        with pytest.raises(SesionChatGPTOcupada) as e:
            sesion(ruta, emisor, espera_del_candado_s=0.4).credenciales()
        esperado = time.monotonic() - inicio
    finally:
        otro.kill()
        otro.wait()

    assert 0.3 <= esperado < 5
    # Falla como las demás fallas de la sesión: un LookupError (incidente y texto fijo).
    assert isinstance(e.value, SesionChatGPTVencida) and isinstance(e.value, LookupError)
    assert "refresco-secreto" not in str(e.value)
    assert emisor.renovaciones == 0
    assert chatgpt.cargar(ruta).refresh_token == "refresco-secreto-1"


def test_el_candado_de_un_proceso_que_murio_no_traba_a_nadie(tmp_path):
    ruta = tmp_path / "s.json"
    guardar_por_vencer(ruta)
    otro = _proceso_que_toma_el_candado(ruta, despues="os._exit(0)")
    otro.wait()
    assert (tmp_path / "s.json.lock").exists()         # el archivo del candado quedó

    emisor = EmisorLento(demora_s=0)
    inicio = time.monotonic()
    acceso, _ = sesion(ruta, emisor, espera_del_candado_s=2).credenciales()

    assert time.monotonic() - inicio < 1.5
    assert emisor.renovaciones == 1
    assert acceso == chatgpt.cargar(ruta).access_token


def test_un_archivo_de_candado_que_quedo_de_antes_no_traba(tmp_path):
    ruta = tmp_path / "s.json"
    guardar_por_vencer(ruta)
    (tmp_path / "s.json.lock").write_text("12345 2026-10-07T12:00:00", "utf-8")

    emisor = EmisorLento(demora_s=0)
    sesion(ruta, emisor, espera_del_candado_s=1).credenciales()

    assert emisor.renovaciones == 1


def test_sin_renovar_no_se_toma_el_candado(tmp_path, monkeypatch):
    ruta = tmp_path / "s.json"
    chatgpt.guardar(ruta, chatgpt.tokens_de_la_respuesta(tokens_del_emisor(), AHORA))
    tomas: list[Path] = []
    original = chatgpt.candado_de_la_sesion

    def contar(r, *args, **kwargs):
        tomas.append(Path(r))
        return original(r, *args, **kwargs)

    monkeypatch.setattr(chatgpt, "candado_de_la_sesion", contar)
    sesion(ruta, EmisorLento(demora_s=0)).credenciales()

    assert tomas == []


# --- Lo guardado: entero o nada -----------------------------------------------------------

def _falla_al_escribir(monkeypatch):
    def a_medias(datos, archivo, *args, **kwargs):
        archivo.write('{"id_token": "a medi')
        raise OSError("disco lleno")

    monkeypatch.setattr(chatgpt.json, "dump", a_medias)


def _falla_al_renombrar(monkeypatch):
    def no_renombra(*args, **kwargs):
        raise OSError("no se pudo renombrar")

    monkeypatch.setattr(chatgpt.os, "replace", no_renombra)


@pytest.mark.parametrize("falla", [_falla_al_escribir, _falla_al_renombrar])
def test_una_escritura_que_falla_deja_la_sesion_anterior_entera_y_sin_temporales(
        tmp_path, monkeypatch, falla):
    ruta = tmp_path / "s.json"
    guardar_por_vencer(ruta)
    anterior = ruta.read_bytes()
    falla(monkeypatch)

    with pytest.raises(OSError):
        chatgpt.guardar(ruta, chatgpt.tokens_de_la_respuesta(
            tokens_del_emisor(sufijo="2"), AHORA))

    monkeypatch.undo()
    assert ruta.read_bytes() == anterior
    assert chatgpt.cargar(ruta).refresh_token == "refresco-secreto-1"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["s.json"]


def test_dos_escrituras_a_la_vez_no_comparten_el_temporal(tmp_path):
    ruta = tmp_path / "s.json"
    fallas: list[BaseException] = []
    largada = threading.Barrier(8)

    def escribir(n: int) -> None:
        largada.wait()
        try:
            for _ in range(10):
                chatgpt.guardar(ruta, chatgpt.tokens_de_la_respuesta(
                    tokens_del_emisor(sufijo=str(n)), AHORA))
        except BaseException as e:  # noqa: BLE001 -- se muestra en la aserción
            fallas.append(e)

    hilos = [threading.Thread(target=escribir, args=(n,)) for n in range(8)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join(20)

    assert fallas == []
    assert chatgpt.cargar(ruta).refresh_token.startswith("refresco-secreto-")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["s.json"]
