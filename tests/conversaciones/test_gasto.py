"""El techo de gasto de la Etapa 2 (decisión 10.4) y la cuenta de cada llamada (E2-7).

USD 30 para toda la etapa: aviso al llegar al 80 %, y una corrida que lo pasaría no empieza sin
el OK del usuario (`pasar_el_techo`). Ninguna prueba llama a un proveedor de verdad: el cliente
habla con un transporte HTTP falso.
"""

from __future__ import annotations

import json

import httpx
import pytest

from tests.conversaciones import correr, gasto
from tests.conversaciones.gasto import (ClienteQueCuenta, Gasto, SinCredito, TechoAlcanzado,
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
    monkeypatch.setattr(correr, "_ia_real", lambda *a: pytest.fail("no debía crear la IA"))
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
    from tests.conversaciones import corredor, informe
    import leda.db

    monkeypatch.setattr(gasto, "RUTA", tmp_path / "gasto.json")
    monkeypatch.setattr(informe, "RESULTADOS", tmp_path / "resultados")
    monkeypatch.setenv("LEDA_TEST_DB_URL", "dbname=leda_corrida_no_se_usa")
    monkeypatch.setenv("LEDA_LOAD_DOTENV", "0")
    monkeypatch.setattr(correr, "Bases", _BasesFalsas)
    monkeypatch.setattr(correr, "_ia_real", lambda *a: _IAQueCuesta())
    monkeypatch.setattr(leda.db, "conectar", lambda url: _ConexionFalsa())
    monkeypatch.setattr(corredor, "correr_conversacion", correr_conversacion)
    # Ninguna prueba consulta el crédito de verdad: por omisión, el proveedor no lo dice.
    monkeypatch.setattr(correr, "_credito_restante", lambda: None)


def _llamada_que_costo(ia, usd: float) -> None:
    ia.llamadas.append({"tipo": "jugadas", "usos": [{"prompt_tokens": 10,
                                                      "completion_tokens": 2, "cost": usd}]})


def test_una_corrida_que_se_cae_deja_su_gasto_y_el_informe_dice_que_se_corto(
        tmp_path, monkeypatch, capsys):
    def se_cae(conn, conv, ia, *, vez=1, motor=None):
        _llamada_que_costo(ia, 0.5)       # la IA ya cobró antes de que se cayera
        raise RuntimeError("se cayó la conexión")

    _ronda_sin_servidor(monkeypatch, tmp_path, se_cae)

    codigo = correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "1",
                          "--ronda", "cortada"])

    assert codigo == 1           # 1 por una caída; el 2 es sólo del techo
    [anotada] = Gasto(tmp_path / "gasto.json").leer()["corridas"]
    assert anotada["usd"] == pytest.approx(0.5)
    assert anotada["motor"] == "leda.motor"         # el motor que corrió, por omisión
    assert "RuntimeError" in anotada["cortada"]
    informe = (tmp_path / "resultados" / "cortada.md").read_text("utf-8")
    assert "cortada" in informe.lower() and "RuntimeError" in informe
    assert _BasesFalsas.ultima.plantilla in _BasesFalsas.ultima.borradas
    assert _BasesFalsas.ultima.limpiadas == 1        # las viejas, antes de empezar


def test_llegar_al_techo_a_mitad_de_la_ronda_sale_con_error_y_lo_dice(tmp_path, monkeypatch):
    from tests.conversaciones.corredor import Corrida

    def bien(conn, conv, ia, *, vez=1, motor=None):
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
    from tests.conversaciones.grabar import IAQueGraba
    from leda.motor.ia_real import IAReal

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
    from tests.conversaciones.corredor import Corrida

    def bien(conn, conv, ia, *, vez=1, motor=None):
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias")

    _ronda_sin_servidor(monkeypatch, tmp_path, bien)

    codigo = correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "1",
                          "--ronda", "sin-consulta"])

    assert codigo == 0
    assert "no se pudo consultar el crédito" in capsys.readouterr().out.lower()


def test_un_402_a_mitad_de_la_ronda_la_corta_e_invalida_las_corridas_que_choco(
        tmp_path, monkeypatch):
    from tests.conversaciones.corredor import Corrida

    def primera_bien_despues_sin_credito(conn, conv, ia, *, vez=1, motor=None):
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
    from tests.conversaciones.gasto import llamadas_sin_credito

    llamadas = [{"tipo": "jugadas", "respuesta": []},
                {"tipo": "jugadas", "error": "SinCredito: el proveedor no tiene crédito"},
                # una grabación de antes de este cambio: el error crudo de httpx
                {"tipo": "redaccion", "error": "HTTPStatusError: Client error '402 Payment "
                                               "Required' for url 'https://x/chat/completions'"},
                {"tipo": "redaccion", "error": "PlazoAgotado: sin respuesta en 40 s"}]

    assert llamadas_sin_credito(llamadas) == 2

# --- Cualquier proveedor y cualquier modelo (E3-8, la comparación de IA) ----------------------
#
# Las cinco IA de la comparación: GPT-6 sol, luna y luna pro por OpenRouter; DeepSeek flash y
# GLM 5.3 flash por `nan`, que no informa el costo. Ninguna prueba llama a un proveedor.

@pytest.mark.parametrize(("ia", "esperada"), [
    ("sol", ("openrouter", "openai/gpt-6-sol")),
    ("luna", ("openrouter", "openai/gpt-6-luna")),
    ("luna-pro", ("openrouter", "openai/gpt-6-luna-pro")),
    ("openrouter/openai/gpt-6-luna-pro", ("openrouter", "openai/gpt-6-luna-pro")),
    ("deepseek-flash", ("nan", "deepseek-v4-flash")),
    ("nan/deepseek-v4-flash", ("nan", "deepseek-v4-flash")),
    ("glm-flash", ("nan", "glm5.3-flash")),
    ("nan/glm5.3-flash", ("nan", "glm5.3-flash")),
    ("guionada", None),
])
def test_la_ia_se_pide_por_su_nombre_corto_o_por_proveedor_y_modelo(ia, esperada):
    assert correr.ia_pedida(ia) == esperada


@pytest.mark.parametrize("ia", ["nadie/un-modelo", "openrouter/", "gpt-6-sol"])
def test_un_proveedor_que_no_existe_o_sin_modelo_no_corre(ia, capsys):
    with pytest.raises(ValueError, match="PROVEEDOR/MODELO"):
        correr.ia_pedida(ia)
    with pytest.raises(SystemExit):
        correr.main(["--ia", ia, "--conversacion", "01", "--veces", "1"])
    assert "PROVEEDOR/MODELO" in capsys.readouterr().err


def test_la_ia_real_usa_el_proveedor_y_la_clave_de_ese_proveedor(monkeypatch):
    import types

    import leda.config
    from leda.llm import BASE_URLS

    from tests.conversaciones import motores

    pedidas = []
    real = leda.config.config

    def clave_llm(proveedor):
        pedidas.append(proveedor)
        return "clave-falsa"

    monkeypatch.setattr(leda.config, "config", types.SimpleNamespace(
        clave_llm=clave_llm, variable_clave_llm=real.variable_clave_llm))

    ia = correr._ia_real("nan", "glm5.3-flash", motores.cargar())

    assert pedidas == ["nan"]
    assert ia.nombre == "nan/glm5.3-flash"
    assert (ia.cliente.modelo, ia.cliente.base_url) == ("glm5.3-flash",
                                                        BASE_URLS["nan"].rstrip("/"))
    assert type(ia).__module__ == "leda.motor.ia_real"

    monkeypatch.setattr(leda.config, "config", types.SimpleNamespace(
        clave_llm=lambda proveedor: "", variable_clave_llm=real.variable_clave_llm))
    with pytest.raises(SystemExit, match=real.variable_clave_llm("nan")):
        correr._ia_real("nan", "deepseek-v4-flash", motores.cargar())


def test_sin_precio_conocido_se_anotan_los_tokens_y_nunca_un_costo_inventado():
    llamadas = [{"tipo": "jugadas", "usos": [{"prompt_tokens": 100, "completion_tokens": 20,
                                               "cost": None}]},
                {"tipo": "redaccion", "usos": []},          # respondió sin decir el uso
                {"tipo": "redaccion", "usos": [], "error": "PlazoAgotado: 40 s"}]

    costo = costo_de_las_llamadas(llamadas, "deepseek-v4-flash", proveedor="nan")

    assert costo["tokens_entrada"] == 100 and costo["tokens_salida"] == 20
    assert costo["usd"] == 0.0 and costo["llamadas_estimadas"] == 0
    assert costo["precio"] == gasto.PRECIO_DESCONOCIDO
    assert costo["llamadas_sin_precio"] == 2         # la que falló no cuenta
    # Si el proveedor sí dice lo que costó una llamada, eso vale.
    con_costo = [{"tipo": "jugadas", "usos": [{"prompt_tokens": 1, "completion_tokens": 1,
                                                "cost": 0.001}]}]
    assert costo_de_las_llamadas(con_costo, "glm5.3-flash", proveedor="nan")["usd"] == \
        pytest.approx(0.001)
    # Con OpenRouter, nada cambia: lo que falta se estima.
    assert "precio" not in costo_de_las_llamadas(llamadas, "openai/gpt-6-luna-pro")


def test_sin_precio_conocido_no_se_estima_ni_cuenta_para_el_techo(tmp_path):
    libreta = Gasto(tmp_path / "gasto.json")
    libreta.anotar({**_corrida(0.0, llamadas=50), "modelo": "deepseek-v4-flash",
                    "proveedor": "nan", "precio": "desconocido", "llamadas_sin_precio": 50})

    assert libreta.por_llamada("deepseek-v4-flash", "nan") == 0.0
    assert libreta.por_llamada("openai/gpt-6-luna-pro") == \
        gasto.USD_POR_LLAMADA["openai/gpt-6-luna-pro"]


class _IAEnNan:
    nombre = "nan/deepseek-v4-flash"


def test_una_ronda_por_nan_anota_tokens_y_no_pregunta_el_credito(tmp_path, monkeypatch, capsys):
    from tests.conversaciones.corredor import Corrida

    def bien(conn, conv, ia, *, vez=1, motor=None):
        ia.llamadas.append({"tipo": "jugadas", "usos": [{"prompt_tokens": 70,
                                                          "completion_tokens": 7}]})
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias", llamadas=list(ia.llamadas), motor_usado=motor.nombre)

    _ronda_sin_servidor(monkeypatch, tmp_path, bien)
    creadas = []
    monkeypatch.setattr(correr, "_ia_real",
                        lambda proveedor, modelo, motor, parametros: creadas.append(
                            (proveedor, modelo, motor.nombre, parametros)) or _IAEnNan())
    monkeypatch.setattr(correr, "_credito_restante",
                        lambda: pytest.fail("el crédito se le pregunta sólo a OpenRouter"))

    codigo = correr.main(["--ia", "deepseek-flash", "--conversacion", "01", "--veces", "1",
                          "--ronda", "nan"])

    assert codigo == 0
    assert creadas == [("nan", "deepseek-v4-flash", "leda.motor", {})]
    salida = capsys.readouterr().out
    assert "Precio desconocido en nan" in salida and "nan no lo informa" in salida
    [anotada] = Gasto(tmp_path / "gasto.json").leer()["corridas"]
    assert (anotada["proveedor"], anotada["modelo"], anotada["motor"]) == (
        "nan", "deepseek-v4-flash", "leda.motor")
    assert anotada["precio"] == "desconocido" and anotada["usd"] == 0.0
    assert (anotada["tokens_entrada"], anotada["tokens_salida"]) == (70, 7)
    informe = (tmp_path / "resultados" / "nan.md").read_text("utf-8")
    assert "**Precio desconocido:** 1 llamada(s)" in informe
    assert "- **IA:** nan/deepseek-v4-flash" in informe


# --- Los parámetros de la IA (E3-8: los dos de `nan`, sin razonar) ----------------------------
#
# La regresión con los dos flash de `nan` falló sobre todo por los límites: el corredor creaba el
# cliente sin parámetros. `--parametros` (o `--parametros-archivo`) los pasa al cliente, y dos
# nombres cortos traen los de cada modelo sin razonar. Ninguna prueba llama a un proveedor.

GLM_SIN_RAZONAR = {"cuerpo_extra": {"reasoning_effort": "low"}, "timeout_s": 60, "plazo_s": 90}
DEEPSEEK_SIN_RAZONAR = {"cuerpo_extra": {"chat_template_kwargs": {"enable_thinking": False}},
                        "timeout_s": 60, "plazo_s": 90}


@pytest.mark.parametrize(("ia", "esperada", "parametros"), [
    ("glm-sin-razonar", ("nan", "glm5.3-flash"), GLM_SIN_RAZONAR),
    ("deepseek-sin-razonar", ("nan", "deepseek-v4-flash"), DEEPSEEK_SIN_RAZONAR),
    ("glm-flash", ("nan", "glm5.3-flash"), {}),
    ("sol", ("openrouter", "openai/gpt-6-sol"), {}),
])
def test_los_nombres_sin_razonar_traen_sus_parametros(ia, esperada, parametros):
    assert correr.ia_pedida(ia) == esperada
    assert correr.parametros_pedidos(ia) == parametros


def test_los_parametros_explicitos_se_suman_a_los_del_nombre(tmp_path):
    assert correr.parametros_pedidos("glm-flash", '{"plazo_s": 120}') == {"plazo_s": 120}
    assert correr.parametros_pedidos("glm-sin-razonar", '{"plazo_s": 120}') == {
        **GLM_SIN_RAZONAR, "plazo_s": 120}
    archivo = tmp_path / "parametros.json"
    archivo.write_text('{"tope_redaccion": 4000}', "utf-8")
    assert correr.parametros_pedidos("sol", archivo=archivo) == {"tope_redaccion": 4000}


@pytest.mark.parametrize(("texto", "nombrado"), [
    ("{no es json", "--parametros"),
    ("[1, 2]", "--parametros"),
    ('{"plazo_s": 0}', "plazo_s"),
    ('{"cuerpo_extra": {"model": "otro"}}', "model"),
    ('{"plazo": 90}', "plazo"),
])
def test_unos_parametros_que_no_valen_no_corren(texto, nombrado, capsys):
    with pytest.raises(ValueError, match=nombrado):
        correr.parametros_pedidos("glm-flash", texto)
    with pytest.raises(SystemExit):
        correr.main(["--ia", "glm-flash", "--parametros", texto, "--conversacion", "01",
                     "--veces", "1"])
    assert nombrado in capsys.readouterr().err


def test_los_parametros_sin_una_ia_real_no_se_ignoran(capsys):
    with pytest.raises(SystemExit):
        correr.main(["--parametros", '{"plazo_s": 90}', "--conversacion", "01", "--veces", "1"])
    assert "IA real" in capsys.readouterr().err


def test_la_ia_real_lleva_los_parametros_al_cliente(monkeypatch):
    import types

    import leda.config

    from tests.conversaciones import motores

    real = leda.config.config
    monkeypatch.setattr(leda.config, "config", types.SimpleNamespace(
        clave_llm=lambda proveedor: "clave-falsa", variable_clave_llm=real.variable_clave_llm))

    ia = correr._ia_real("nan", "glm5.3-flash", motores.cargar(), GLM_SIN_RAZONAR)

    assert ia.cliente.parametros["cuerpo_extra"] == {"reasoning_effort": "low"}
    assert ia.cliente.parametros["plazo_s"] == 90
    assert ia.cliente.http.timeout.read == 60


def test_una_ronda_sin_razonar_anota_sus_parametros_y_avisa_de_la_cache(
        tmp_path, monkeypatch, capsys):
    from tests.conversaciones.corredor import Corrida

    def bien(conn, conv, ia, *, vez=1, motor=None):
        ia.llamadas.append({"tipo": "jugadas", "usos": [{"prompt_tokens": 70,
                                                          "completion_tokens": 7}]})
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias", llamadas=list(ia.llamadas), motor_usado=motor.nombre)

    _ronda_sin_servidor(monkeypatch, tmp_path, bien)
    creadas = []

    class _GLM:
        nombre = "nan/glm5.3-flash"

    monkeypatch.setattr(correr, "_ia_real",
                        lambda proveedor, modelo, motor, parametros: creadas.append(
                            (proveedor, modelo, parametros)) or _GLM())

    codigo = correr.main(["--ia", "glm-sin-razonar", "--parametros", '{"plazo_s": 120}',
                          "--conversacion", "01", "--veces", "1", "--ronda", "sin-razonar"])

    assert codigo == 0
    esperados = {**GLM_SIN_RAZONAR, "plazo_s": 120}
    assert creadas == [("nan", "glm5.3-flash", esperados)]
    [anotada] = Gasto(tmp_path / "gasto.json").leer()["corridas"]
    assert anotada["parametros"] == esperados
    informe = (tmp_path / "resultados" / "sin-razonar.md").read_text("utf-8")
    assert '"reasoning_effort": "low"' in informe and '"plazo_s": 120' in informe
    assert "caché" in informe and "independientes" in informe


def test_una_ronda_sin_parametros_lo_dice_y_no_anota_parametros(tmp_path, monkeypatch):
    from tests.conversaciones.corredor import Corrida

    def bien(conn, conv, ia, *, vez=1, motor=None):
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias")

    _ronda_sin_servidor(monkeypatch, tmp_path, bien)

    assert correr.main(["--ia", "sol", "--conversacion", "01", "--veces", "1",
                        "--ronda", "sol"]) == 0
    [anotada] = Gasto(tmp_path / "gasto.json").leer()["corridas"]
    assert "parametros" not in anotada
    informe = (tmp_path / "resultados" / "sol.md").read_text("utf-8")
    assert "los de omisión" in informe
    assert "caché" not in informe             # la nota es sólo de `nan`
