"""La herramienta de medición de la ayuda al crear un objetivo (`tools/medir_ayuda_al_crear_objetivo.py`,
J3-4): sin red y nunca con la IA real. Comparte con la de la carga la corrida, la IA real y lo que
es una falla de la IA o del programa; acá se prueba que en seco mida algo, que se corte sin cupo
(sale con 4, con el informe hasta donde llegó), que un error del programa corte (sale con 3) y que
los referentes se busquen con la función del servidor."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from tests.test_ayuda_al_cargar import IADeLaCarga


@pytest.fixture
def medir():
    ruta = Path(__file__).resolve().parents[1] / "tools" / "medir_ayuda_al_crear_objetivo.py"
    spec = importlib.util.spec_from_file_location("medir_ayuda_al_crear_objetivo", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class _SinCupo(Exception):
    def __init__(self) -> None:
        super().__init__("cupo")
        self.response = type("R", (), {"status_code": 429})()


def test_los_pedidos_son_entre_doce_y_dieciseis_y_cada_uno_dice_que_espera(medir):
    assert 12 <= len(medir.PEDIDOS) <= 16
    nombres = [p["nombre"] for p in medir.PEDIDOS]
    assert len(set(nombres)) == len(nombres)
    for pedido in medir.PEDIDOS:
        assert pedido["texto"] and (pedido.get("propone") or pedido.get("no_propone")
                                    or pedido.get("descarta") or pedido.get("elegir"))


def test_en_seco_la_medicion_prueba_algo(medir, tmp_path):
    """La IA en seco propone lo que contestaría una IA que entendió para el módem, los operarios,
    los dos referentes, el sábado y el fin de mes; los demás, sin guion, no proponen nada. Así la
    corrida en seco prueba los controles: el sábado no pone la fecha, el fin de mes tampoco (el
    código no entiende "antes de que termine noviembre") y "el colo" se elige."""
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "guionada", "--veces", "1", "--salida", str(salida)]) == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    bien = {r["pedido"] for r in informe["resultados"] if r["bien"]}
    assert bien == set(medir.GUION)
    assert informe["total"] == len(medir.PEDIDOS) and informe["cortada"] is None
    del_sabado = next(r for r in informe["resultados"] if r["pedido"] == "un sábado no es hábil")
    assert "fecha" not in del_sabado["propuesta"]


def test_un_pedido_que_no_da_lo_esperado_sale_mal_con_el_porque(medir):
    ia = IADeLaCarga({"titulo": "Ordenar la sala de servidores", "referente": "lucas",
                      "tipo": "estrategico", "fecha": "2026-10-23",
                      "como_dijo_la_fecha": "para el viernes 30"})
    pedido = next(p for p in medir.PEDIDOS if p["nombre"] == "el módem colgado")
    ok, detalle = medir.medir(ia, pedido)
    assert ok is False
    assert any(f.startswith("fecha:") for f in detalle["fallas"])


def test_la_medicion_rechaza_menos_de_una_vuelta(medir):
    with pytest.raises(SystemExit) as salida:
        medir.main(["--veces", "0"])
    assert salida.value.code == 2


def test_sin_cupo_la_medicion_guarda_lo_medido_y_sale_con_4(medir, monkeypatch, tmp_path):
    ia = IADeLaCarga({}, _SinCupo())
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == medir.SIN_CUPO == 4
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["cortada"] == "sin_cupo"
    assert [r["pedido"] for r in informe["resultados"]] == [medir.PEDIDOS[0]["nombre"]]
    assert len(ia.pedidos) == 2


def test_una_falla_de_la_ia_no_es_un_error_del_programa(medir, monkeypatch, tmp_path):
    from leda.motor.ia_real import PlazoAgotado

    ia = IADeLaCarga(PlazoAgotado(40), *([{}] * len(medir.PEDIDOS)))
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["resultados"][0]["falla"] == "ia"
    assert informe["cortada"] is None


def test_un_error_del_programa_corta_y_sale_con_3(medir, monkeypatch, tmp_path):
    ia = IADeLaCarga(*([{}] * len(medir.PEDIDOS)))
    monkeypatch.setattr(medir, "la_ia", lambda texto: ia)

    def revisar_roto(*a, **k):
        raise KeyError("dato")
    monkeypatch.setattr(medir.ayuda, "revisar", revisar_roto)
    salida = tmp_path / "informe.json"
    assert medir.main(["--ia", "x", "--salida", str(salida)]) == medir.ERROR_DEL_PROGRAMA == 3
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert informe["cortada"] == "error_del_programa"
    assert len(ia.pedidos) == 1


def test_los_referentes_se_buscan_con_la_funcion_del_servidor(medir, monkeypatch):
    from leda.motor import fichas

    llamadas = []
    original = fichas.integrantes_que_coinciden

    def espia(cur, dicho):
        llamadas.append(dicho)
        return original(cur, dicho)
    monkeypatch.setattr(fichas, "integrantes_que_coinciden", espia)
    assert [f["membership_id"] for f in medir.coinciden("lucas")] == ["m-lucas"]
    assert [f["membership_id"] for f in medir.coinciden("el tano")] == ["m-marcos"]
    assert {f["membership_id"] for f in medir.coinciden("el colo", medir.DOS_CON_EL_COLO)} == {
        "m-lucas", "m-nahuel"}
    assert medir.coinciden("pepe") == []
    assert llamadas == ["lucas", "el tano", "el colo", "pepe"]
