"""El techo de gasto de la Etapa 2 (decisión 10.4) y la cuenta de cada llamada (E2-7).

USD 30 para toda la etapa: aviso al llegar al 80 %, y una corrida que lo pasaría no empieza sin
el OK del usuario (`pasar_el_techo`). Ninguna prueba llama a un proveedor de verdad: el cliente
habla con un transporte HTTP falso.
"""

from __future__ import annotations

import json

import httpx
import pytest

from prueba_chica import correr, gasto
from prueba_chica.gasto import (ClienteQueCuenta, Gasto, TechoAlcanzado,
                                costo_de_las_llamadas)


def _corrida(usd: float, llamadas: int = 10, estimadas: int = 0, **mas) -> dict:
    return {"modelo": "openai/gpt-6-sol", "usd": usd, "llamadas": llamadas,
            "llamadas_estimadas": estimadas, "tokens_entrada": 0, "tokens_salida": 0, **mas}


def test_la_libreta_suma_cada_corrida_y_sobrevive(tmp_path):
    ruta = tmp_path / "gasto.json"
    Gasto(ruta).anotar(_corrida(1.25, jev_usd=0.02))
    Gasto(ruta).anotar(_corrida(0.5))

    assert Gasto(ruta).total() == pytest.approx(1.77)
    assert json.loads(ruta.read_text("utf-8"))["techo_usd"] == 30.0


def test_avisa_al_llegar_al_80_por_ciento(tmp_path):
    avisos = []
    libreta = Gasto(tmp_path / "gasto.json", avisar=avisos.append)
    libreta.anotar(_corrida(23.0))

    libreta.reservar(0.5)
    assert avisos == []
    libreta.reservar(0.6)               # 23 + 0,5 reservado + 0,6 = 24,1: el 80 %
    assert len(avisos) == 1 and "80%" in avisos[0]


def test_no_empieza_una_corrida_que_pasaria_el_techo_sin_el_ok(tmp_path):
    libreta = Gasto(tmp_path / "gasto.json", avisar=lambda _: None)
    libreta.anotar(_corrida(29.9))

    with pytest.raises(TechoAlcanzado, match="OK del usuario"):
        libreta.reservar(0.2)
    libreta.reservar(0.2, pasar_el_techo=True)      # con el OK del usuario, sigue


def test_lo_reservado_cuenta_hasta_que_se_anota(tmp_path):
    libreta = Gasto(tmp_path / "gasto.json", avisar=lambda _: None)
    libreta.reservar(20.0)
    with pytest.raises(TechoAlcanzado):
        libreta.reservar(15.0)            # las corridas en paralelo no se pasan juntas
    libreta.anotar(_corrida(19.0), reservado=20.0)
    libreta.reservar(10.0)


def test_el_costo_por_llamada_es_el_medido_cuando_hay_bastante(tmp_path):
    libreta = Gasto(tmp_path / "gasto.json")
    assert libreta.por_llamada("openai/gpt-6-sol") == gasto.USD_POR_LLAMADA["openai/gpt-6-sol"]
    libreta.anotar(_corrida(0.05, llamadas=10))
    assert libreta.por_llamada("openai/gpt-6-sol") == pytest.approx(0.005)


def test_el_costo_de_las_llamadas_usa_lo_informado_y_estima_lo_que_falta():
    llamadas = [{"tipo": "jugadas", "usos": [{"prompt_tokens": 100, "completion_tokens": 20,
                                               "cost": 0.004}]},
                {"tipo": "redaccion", "usos": [{"prompt_tokens": 50, "completion_tokens": 10,
                                                 "cost": None}]},
                {"tipo": "redaccion", "usos": [], "error": "PlazoAgotado: 40 s"}]

    costo = costo_de_las_llamadas(llamadas, "openai/gpt-6-sol")

    assert costo["tokens_entrada"] == 150 and costo["tokens_salida"] == 30
    assert costo["llamadas_estimadas"] == 2       # la sin costo y la que falló por plazo
    assert costo["usd"] == pytest.approx(0.004 + 2 * 0.016)


def test_el_cliente_pide_el_uso_a_openrouter_y_lo_guarda():
    pedidos = []

    def responder(pedido: httpx.Request) -> httpx.Response:
        pedidos.append(json.loads(pedido.content))
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "hola"}}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 3, "cost": 0.0007}})

    cliente = ClienteQueCuenta.crear("openai/gpt-6-luna", "clave-falsa",
                                     "https://openrouter.ai/api/v1", {},
                                     transporte=httpx.MockTransport(responder))

    cliente.completar({"messages": []})

    assert pedidos[0]["usage"] == {"include": True}
    assert cliente.usos == [{"prompt_tokens": 12, "completion_tokens": 3, "cost": 0.0007}]


def test_el_corredor_no_empieza_si_la_ronda_pasaria_el_techo(tmp_path, monkeypatch):
    ruta = tmp_path / "gasto.json"
    Gasto(ruta).anotar(_corrida(29.99))
    monkeypatch.setattr(gasto, "RUTA", ruta)
    monkeypatch.setattr(correr, "_ia_real", lambda modelo: pytest.fail("no debía crear la IA"))
    monkeypatch.setattr(correr.Bases, "crear_plantilla",
                        lambda self: pytest.fail("no debía crear bases"))

    assert correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "1"]) == 2
    assert Gasto(ruta).total() == pytest.approx(29.99)


def test_la_grabacion_guarda_lo_que_uso_cada_llamada_de_la_ia_real():
    from prueba_chica.grabar import IAQueGraba
    from prueba_chica.ia_real import IAReal

    def responder(pedido: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "hola"}}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 3, "cost": 0.0007}})

    cliente = ClienteQueCuenta.crear("openai/gpt-6-luna", "clave-falsa",
                                     "https://openrouter.ai/api/v1", {},
                                     transporte=httpx.MockTransport(responder))
    ia = IAQueGraba(IAReal(cliente, None, nombre="openrouter/openai/gpt-6-luna"))

    assert ia.redactar({"hechos": []}) == "hola"

    [llamada] = ia.llamadas
    assert llamada["usos"] == [{"prompt_tokens": 12, "completion_tokens": 3, "cost": 0.0007}]
    assert costo_de_las_llamadas(ia.llamadas, "openai/gpt-6-luna")["usd"] == pytest.approx(0.0007)
