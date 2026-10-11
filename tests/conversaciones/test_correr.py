"""El cupo de la suscripción antes y después de una ronda (`correr.main`), sin red: la consulta
del cupo es falsa y las bases, la conexión y la corrida, también (`test_gasto`)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from leda.motor import chatgpt
from tests.conversaciones import correr, gasto
from tests.conversaciones.test_gasto import _ronda_sin_servidor

AHORA = datetime(2026, 10, 11, 3, 0, tzinfo=timezone.utc)


def _cupo(corta: str, larga: str = "3", ahora: datetime = AHORA) -> chatgpt.Cupo:
    return chatgpt.cupo_de_cabeceras({
        "x-codex-primary-used-percent": corta, "x-codex-secondary-used-percent": larga,
        "x-codex-primary-window-minutes": "300", "x-codex-secondary-window-minutes": "10080",
        "x-codex-primary-reset-after-seconds": "3600",
        "x-codex-secondary-reset-after-seconds": "86400"}, ahora)


class Siguio(Exception):
    """La ronda pasó la comprobación del cupo y fue a buscar el servidor de las bases."""


def _sin_ronda(monkeypatch, tmp_path) -> None:
    """Nada después de la comprobación del cupo puede correr: llegar es `Siguio`."""
    monkeypatch.setattr(gasto, "RUTA", tmp_path / "gasto.json")
    monkeypatch.setenv("LEDA_LOAD_DOTENV", "0")
    monkeypatch.setattr(correr, "_ia_real", lambda *a: pytest.fail("no debía crear la IA"))
    monkeypatch.setattr(correr, "_credito_restante", lambda: None)

    def siguio():
        raise Siguio

    monkeypatch.setattr(correr, "_url_de_mantenimiento", siguio)


def _consulta(cupo=None, *, http=200, codigo="", falla=""):
    return chatgpt.ConsultaDeCupo(cupo=cupo, http=http, codigo=codigo, falla=falla)


@pytest.mark.parametrize("corta,larga", [("100", "3"), ("40", "100"), ("100.0", "100")])
def test_con_una_ventana_llena_la_ronda_no_empieza(tmp_path, monkeypatch, capsys, corta,
                                                   larga):
    _sin_ronda(monkeypatch, tmp_path)
    monkeypatch.setattr(correr, "_consultar_cupo", lambda: _consulta(_cupo(corta, larga)))

    codigo = correr.main(["--ia", "sol-suscripcion", "--conversacion", "01", "--veces", "1"])

    assert codigo == correr.SALIDA_SIN_CUOTA
    salida = capsys.readouterr().out
    assert "100 % usado" in salida and "no empieza" in salida


def test_con_el_limite_de_uso_en_la_consulta_la_ronda_no_empieza(tmp_path, monkeypatch,
                                                                  capsys):
    _sin_ronda(monkeypatch, tmp_path)
    monkeypatch.setattr(correr, "_consultar_cupo",
                        lambda: _consulta(http=429, codigo=chatgpt.LIMITE_DE_USO))

    assert correr.main(["--ia", "chatgpt/gpt-6-sol", "--conversacion", "01",
                        "--veces", "1"]) == correr.SALIDA_SIN_CUOTA
    assert "límite de uso" in capsys.readouterr().out


def test_con_cupo_la_ronda_sigue(tmp_path, monkeypatch, capsys):
    _sin_ronda(monkeypatch, tmp_path)
    monkeypatch.setattr(correr, "_consultar_cupo", lambda: _consulta(_cupo("99.9", "50")))

    with pytest.raises(Siguio):
        correr.main(["--ia", "sol-suscripcion", "--conversacion", "01", "--veces", "1"])
    assert "99.9 % usado" in capsys.readouterr().out


def test_sin_poder_consultar_el_cupo_avisa_y_sigue(tmp_path, monkeypatch, capsys):
    _sin_ronda(monkeypatch, tmp_path)
    monkeypatch.setattr(correr, "_consultar_cupo",
                        lambda: _consulta(http=None, falla="sin respuesta: ConnectError"))

    with pytest.raises(Siguio):
        correr.main(["--ia", "sol-suscripcion", "--conversacion", "01", "--veces", "1"])
    assert "no se pudo saber el cupo" in capsys.readouterr().out


@pytest.mark.parametrize("ia", ["guionada", "sol"])
def test_sin_la_suscripcion_no_se_consulta_el_cupo(tmp_path, monkeypatch, ia):
    _sin_ronda(monkeypatch, tmp_path)
    monkeypatch.setattr(correr, "_consultar_cupo",
                        lambda: pytest.fail("no debía consultar el cupo"))

    with pytest.raises(Siguio):
        correr.main(["--ia", ia, "--conversacion", "01", "--veces", "1"])


def test_al_terminar_dice_el_ultimo_cupo_y_el_informe_lo_anota(tmp_path, monkeypatch, capsys):
    from tests.conversaciones.corredor import Corrida

    antes = _cupo("20", "3")
    despues = _cupo("35", "4", AHORA + timedelta(minutes=30))

    def bien(conn, conv, ia, *, vez=1, motor=None):
        chatgpt.recordar_cupo(despues)      # lo que deja cada respuesta real de la ronda
        return Corrida(str(conv["numero"]), conv["titulo"], conv["fuente"], vez, ia.nombre,
                       "garantias")

    _ronda_sin_servidor(monkeypatch, tmp_path, bien)
    monkeypatch.setattr(chatgpt, "_ultimo_cupo", None)

    def consultar():
        chatgpt.recordar_cupo(antes)
        return _consulta(antes)

    monkeypatch.setattr(correr, "_consultar_cupo", consultar)

    codigo = correr.main(["--ia", "sol-suscripcion", "--conversacion", "01", "--veces", "1",
                          "--ronda", "con-cupo"])

    assert codigo == 0
    salida = capsys.readouterr().out
    assert "20 % usado" in salida and "35 % usado" in salida
    informe = (tmp_path / "resultados" / "con-cupo.md").read_text("utf-8")
    assert "Cupo de la suscripción antes" in informe and "20 % usado" in informe
    assert "Cupo de la suscripción después" in informe and "35 % usado" in informe
