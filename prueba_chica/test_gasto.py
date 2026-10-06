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
from prueba_chica.gasto import (ClienteQueCuenta, Gasto, SinCredito, TechoAlcanzado,
                                costo_de_las_llamadas, credito_restante)


def _corrida(usd: float, llamadas: int = 10, estimadas: int = 0, **mas) -> dict:
    return {"modelo": "openai/gpt-6-sol", "usd": usd, "llamadas": llamadas,
            "llamadas_estimadas": estimadas, "tokens_entrada": 0, "tokens_salida": 0, **mas}


def test_la_libreta_suma_cada_corrida_y_sobrevive(tmp_path):
    ruta = tmp_path / "gasto.json"
    Gasto(ruta).anotar(_corrida(1.25, jev_usd=0.02))   # una vieja, con Jev: también cuenta
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
                {"tipo": "redaccion", "usos": []}]

    costo = costo_de_las_llamadas(llamadas, "openai/gpt-6-sol")

    assert costo["tokens_entrada"] == 150 and costo["tokens_salida"] == 30
    assert costo["llamadas_estimadas"] == 2       # la sin costo y la que respondió sin uso
    assert costo["usd"] == pytest.approx(0.004 + 2 * 0.016)


def test_una_llamada_que_fallo_no_cuesta_ni_se_estima():
    """Ronda 2 (2026-10-05): sin crédito, OpenRouter rechazó cientos de llamadas con 402 y la
    libreta las estimó como cobradas; mostró USD 29,84 cuando se habían gastado unos 8 y cortó
    la ronda. Una llamada que falló (error HTTP, plazo, sin respuesta) no se cobra."""
    llamadas = [{"tipo": "jugadas", "usos": [], "error": "HTTPStatusError: Client error "
                 "'402 Payment Required' for url 'https://openrouter.ai/api/v1/chat/completions'"},
                {"tipo": "redaccion", "usos": [], "error": "PlazoAgotado: 40 s"},
                {"tipo": "redaccion", "error": "ConnectError: sin respuesta"},
                {"tipo": "jugadas", "usos": [{"prompt_tokens": 80, "completion_tokens": 9,
                                               "cost": 0.003}]}]

    costo = costo_de_las_llamadas(llamadas, "openai/gpt-6-sol")

    assert costo["usd"] == pytest.approx(0.003)
    assert costo["llamadas_estimadas"] == 0
    assert costo["llamadas"] == 4


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
    # Sin servidor de bases: decidir el techo no depende de él (revisión de la E2-7).
    monkeypatch.delenv("LEDA_TEST_DB_URL", raising=False)
    monkeypatch.setattr(correr, "_url_de_mantenimiento",
                        lambda: pytest.fail("no debía buscar el servidor de bases"))

    assert correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "1"]) == 2
    assert Gasto(ruta).total() == pytest.approx(29.99)


# --- Una ronda que se corta (revisión de la E2-7) --------------------------------------------
#
# Sin servidor de bases ni IA real: las bases, la conexión y la corrida son falsas, y la IA
# "real" es una que sólo deja grabado lo que habría costado cada llamada.

class _BasesFalsas:
    def __init__(self, mantenimiento: str) -> None:
        self.plantilla = "leda_corrida_plantilla_falsa"
        self.borradas: list[str] = []
        self.limpiadas = 0
        _BasesFalsas.ultima = self

    def limpiar_viejas(self) -> list[str]:
        self.limpiadas += 1
        return []

    def crear_plantilla(self) -> None:
        pass

    def nueva(self) -> tuple[str, str]:
        return "leda_corrida_falsa", "url-falsa"

    def borrar(self, nombre: str) -> None:
        self.borradas.append(nombre)


class _ConexionFalsa:
    def close(self) -> None:
        pass


class _IAQueCuesta:
    nombre = "openrouter/openai/gpt-6-sol"


def _ronda_sin_servidor(monkeypatch, tmp_path, correr_conversacion):
    from prueba_chica import corredor, informe
    import leda.db

    monkeypatch.setattr(gasto, "RUTA", tmp_path / "gasto.json")
    monkeypatch.setattr(informe, "RESULTADOS", tmp_path / "resultados")
    monkeypatch.setenv("LEDA_TEST_DB_URL", "dbname=leda_corrida_no_se_usa")
    monkeypatch.setenv("LEDA_LOAD_DOTENV", "0")
    monkeypatch.setattr(correr, "Bases", _BasesFalsas)
    monkeypatch.setattr(correr, "_ia_real", lambda modelo: _IAQueCuesta())
    monkeypatch.setattr(leda.db, "conectar", lambda url: _ConexionFalsa())
    monkeypatch.setattr(corredor, "correr_conversacion", correr_conversacion)
    # Ninguna prueba consulta el crédito de verdad: por omisión, el proveedor no lo dice.
    monkeypatch.setattr(correr, "_credito_restante", lambda: None)


def _llamada_que_costo(ia, usd: float) -> None:
    ia.llamadas.append({"tipo": "jugadas", "usos": [{"prompt_tokens": 10,
                                                      "completion_tokens": 2, "cost": usd}]})


def test_una_corrida_que_se_cae_deja_su_gasto_y_el_informe_dice_que_se_corto(
        tmp_path, monkeypatch, capsys):
    def se_cae(conn, conv, ia, *, vez=1):
        _llamada_que_costo(ia, 0.5)       # la IA ya cobró antes de que se cayera
        raise RuntimeError("se cayó la conexión")

    _ronda_sin_servidor(monkeypatch, tmp_path, se_cae)

    codigo = correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "1",
                          "--ronda", "cortada"])

    assert codigo == 1           # 1 por una caída; el 2 es sólo del techo
    [anotada] = Gasto(tmp_path / "gasto.json").leer()["corridas"]
    assert anotada["usd"] == pytest.approx(0.5)
    assert "RuntimeError" in anotada["cortada"]
    informe = (tmp_path / "resultados" / "cortada.md").read_text("utf-8")
    assert "cortada" in informe.lower() and "RuntimeError" in informe
    assert _BasesFalsas.ultima.plantilla in _BasesFalsas.ultima.borradas
    assert _BasesFalsas.ultima.limpiadas == 1        # las viejas, antes de empezar


def test_llegar_al_techo_a_mitad_de_la_ronda_sale_con_error_y_lo_dice(tmp_path, monkeypatch):
    from prueba_chica.corredor import Corrida

    def bien(conn, conv, ia, *, vez=1):
        _llamada_que_costo(ia, 0.1)
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias")

    _ronda_sin_servidor(monkeypatch, tmp_path, bien)
    reservas = []
    original = Gasto.reservar

    def reservar(self, estimado, *, pasar_el_techo=False):
        reservas.append(estimado)
        if len(reservas) == 3:          # la ronda entera y la primera corrida pasan
            raise TechoAlcanzado("El gasto de la etapa llegaría al techo.")
        return original(self, estimado, pasar_el_techo=pasar_el_techo)

    monkeypatch.setattr(Gasto, "reservar", reservar)

    codigo = correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "2",
                          "--ronda", "techo"])

    assert codigo == 2
    informe = (tmp_path / "resultados" / "techo.md").read_text("utf-8")
    assert "techo" in informe.lower() and "vez 2" in informe
    assert len(Gasto(tmp_path / "gasto.json").leer()["corridas"]) == 1


def test_si_la_plantilla_no_se_puede_crear_igual_se_borra(tmp_path, monkeypatch):
    def nunca(*a, **k):
        pytest.fail("no debía correr")

    _ronda_sin_servidor(monkeypatch, tmp_path, nunca)

    def a_medias(self):
        raise RuntimeError("se cortó el esquema a mitad")

    monkeypatch.setattr(_BasesFalsas, "crear_plantilla", a_medias)

    with pytest.raises(RuntimeError):
        correr.main(["--conversacion", "01", "--veces", "1"])
    assert _BasesFalsas.ultima.plantilla in _BasesFalsas.ultima.borradas


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


# --- Sin crédito en el proveedor (HTTP 402; rondas 2 y 3) -----------------------------------
#
# La ronda 3 siguió corriendo con la cuenta sin crédito: 62 de 85 corridas chocaron con un 402 y
# el informe las mezcló con las válidas. Ahora la ronda se corta, las corridas con un 402 son
# inválidas y se listan aparte, y antes de empezar se consulta el crédito.

def test_un_402_del_proveedor_es_sin_credito():
    def responder(pedido: httpx.Request) -> httpx.Response:
        return httpx.Response(402, json={"error": {"code": 402,
                                                   "message": "Insufficient credits"}})

    cliente = ClienteQueCuenta.crear("openai/gpt-6-sol", "clave-falsa",
                                     "https://openrouter.ai/api/v1", {},
                                     transporte=httpx.MockTransport(responder))

    with pytest.raises(SinCredito):
        cliente.completar({"messages": []})


def test_un_error_402_dentro_de_una_respuesta_200_tambien_es_sin_credito():
    def responder(pedido: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"error": {"code": 402,
                                                   "message": "Insufficient credits"}})

    cliente = ClienteQueCuenta.crear("openai/gpt-6-sol", "clave-falsa",
                                     "https://openrouter.ai/api/v1", {},
                                     transporte=httpx.MockTransport(responder))

    with pytest.raises(SinCredito):
        cliente.completar({"messages": []})


def test_el_credito_restante_es_lo_que_le_queda_a_la_cuenta_y_a_la_clave():
    pedidos = []

    def responder(pedido: httpx.Request) -> httpx.Response:
        pedidos.append((pedido.url.path, pedido.headers.get("authorization")))
        if pedido.url.path.endswith("/credits"):
            return httpx.Response(200, json={"data": {"total_credits": 20.0,
                                                      "total_usage": 17.5}})
        return httpx.Response(200, json={"data": {"limit": 10.0, "limit_remaining": 4.0}})

    restante = credito_restante("clave-falsa", "https://openrouter.ai/api/v1",
                                transporte=httpx.MockTransport(responder))

    assert restante == pytest.approx(2.5)
    assert {r for r, _ in pedidos} == {"/api/v1/credits", "/api/v1/key"}
    assert all(a == "Bearer clave-falsa" for _, a in pedidos)


def test_una_clave_sin_limite_deja_el_credito_de_la_cuenta():
    def responder(pedido: httpx.Request) -> httpx.Response:
        if pedido.url.path.endswith("/credits"):
            return httpx.Response(200, json={"data": {"total_credits": 20.0,
                                                      "total_usage": 5.0}})
        return httpx.Response(200, json={"data": {"limit": None, "limit_remaining": None}})

    assert credito_restante("clave-falsa", "https://openrouter.ai/api/v1",
                            transporte=httpx.MockTransport(responder)) == pytest.approx(15.0)


def test_si_el_proveedor_no_dice_el_credito_no_se_sabe():
    def responder(pedido: httpx.Request) -> httpx.Response:
        if pedido.url.path.endswith("/credits"):
            return httpx.Response(503, text="no disponible")
        raise httpx.ConnectError("sin red")

    assert credito_restante("clave-falsa", "https://openrouter.ai/api/v1",
                            transporte=httpx.MockTransport(responder)) is None


def test_la_ronda_no_empieza_si_el_credito_no_alcanza(tmp_path, monkeypatch, capsys):
    def nunca(*a, **k):
        pytest.fail("no debía correr")

    _ronda_sin_servidor(monkeypatch, tmp_path, nunca)
    monkeypatch.setattr(correr, "_credito_restante", lambda: 0.05)
    monkeypatch.setattr(_BasesFalsas, "crear_plantilla",
                        lambda self: pytest.fail("no debía crear bases"))

    codigo = correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "2",
                          "--ronda", "sin-credito-antes"])

    assert codigo == correr.SALIDA_SIN_CREDITO
    assert codigo not in (0, 1, 2)          # distinto del techo y de una caída
    salida = capsys.readouterr().out
    assert "USD 0.05" in salida and "clave" not in salida.lower()
    assert Gasto(tmp_path / "gasto.json").leer()["corridas"] == []


def test_si_no_se_puede_consultar_el_credito_avisa_y_sigue(tmp_path, monkeypatch, capsys):
    from prueba_chica.corredor import Corrida

    def bien(conn, conv, ia, *, vez=1):
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias")

    _ronda_sin_servidor(monkeypatch, tmp_path, bien)

    codigo = correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "1",
                          "--ronda", "sin-consulta"])

    assert codigo == 0
    assert "no se pudo consultar el crédito" in capsys.readouterr().out.lower()


def test_un_402_a_mitad_de_la_ronda_la_corta_e_invalida_las_corridas_que_choco(
        tmp_path, monkeypatch):
    from prueba_chica.corredor import Corrida

    def primera_bien_despues_sin_credito(conn, conv, ia, *, vez=1):
        if vez == 1:
            _llamada_que_costo(ia, 0.1)
        else:
            _llamada_que_costo(ia, 0.05)      # respondió una, y después se acabó el crédito
            ia.llamadas.append({"tipo": "redaccion",
                                "error": "SinCredito: el proveedor no tiene crédito (HTTP 402)"})
        # como `corredor.correr_conversacion`: la corrida lleva lo que grabó la IA
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias", llamadas=list(ia.llamadas))

    _ronda_sin_servidor(monkeypatch, tmp_path, primera_bien_despues_sin_credito)

    codigo = correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "4",
                          "--ronda", "sin-credito"])

    assert codigo == correr.SALIDA_SIN_CREDITO
    informe = (tmp_path / "resultados" / "sin-credito.md").read_text("utf-8")
    cortada, _, resto = informe.partition("## Resultado por conversación")
    assert "sin crédito en el proveedor" in cortada
    # La 2 chocó con el 402: inválida, aparte; la 3 y la 4 no empezaron.
    assert "## Corridas inválidas" in cortada and "01, vez 2" in cortada
    assert "01, vez 3" in cortada and "01, vez 4" in cortada
    tabla = resto.partition("## Fallas")[0]
    fila = next(linea for linea in tabla.splitlines() if linea.startswith("| 01 "))
    assert "1/1" in fila                    # sólo la válida cuenta
    anotadas = Gasto(tmp_path / "gasto.json").leer()["corridas"]
    assert [c["vez"] for c in anotadas] == [1, 2]       # la 3 y la 4 no gastaron nada
    assert anotadas[1]["invalida"] == "sin crédito en el proveedor"
    assert sum(c["usd"] for c in anotadas) == pytest.approx(0.15)


def test_la_grabacion_de_un_402_dice_que_fue_sin_credito():
    from prueba_chica.gasto import llamadas_sin_credito

    llamadas = [{"tipo": "jugadas", "respuesta": []},
                {"tipo": "jugadas", "error": "SinCredito: el proveedor no tiene crédito"},
                # una grabación de antes de este cambio: el error crudo de httpx
                {"tipo": "redaccion", "error": "HTTPStatusError: Client error '402 Payment "
                                               "Required' for url 'https://x/chat/completions'"},
                {"tipo": "redaccion", "error": "PlazoAgotado: sin respuesta en 40 s"}]

    assert llamadas_sin_credito(llamadas) == 2
