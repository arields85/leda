"""El margen máximo de la fecha de una tarea es un ajuste del espacio
(`workspace_setting['horizonte_tarea']`, del pack): hoy más N meses de calendario,
2 por omisión. Un valor que no se entiende usa 2 y deja un incidente.

Familias: el ajuste (falta, propio, inválido), el importador, el alta guiada y el
alta conducida por el modelo (de punta a punta).
"""

from __future__ import annotations

from datetime import date

import pytest
import yaml
from psycopg.types.json import Jsonb

from prisma import incidentes
from prisma import ingreso_tareas as I
from prisma.db import admin, espacio
from prisma.valores import sumar_meses

from tests.conftest import RAIZ
from tests.test_alta_conducida import (_cuerpos, _en, _hoy, chat,  # noqa: F401
                                       conversada, salida)
from tests.test_alta_guiada_flujo import (_campo, _decir_fecha, _en_la_fecha,
                                          _slot)


@pytest.fixture(autouse=True)
def _sin_anomalias():
    I._anomalias_horizonte.clear()
    yield
    I._anomalias_horizonte.clear()


def _poner(conn, ws, valor):
    with admin(conn) as cur:
        cur.execute("delete from workspace_setting where workspace_id = %s "
                    "and clave = 'horizonte_tarea'", (ws,))
        if valor is not None:
            cur.execute(
                "insert into workspace_setting (workspace_id, clave, valor) "
                "values (%s, 'horizonte_tarea', %s)", (ws, Jsonb(valor)))
    conn.commit()


def _incidentes(conn, ws) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where workspace_id = %s "
                    "and etapa = %s", (ws, incidentes.ETAPA_HORIZONTE_TAREA))
        return cur.fetchone()["n"]


# ------------------------------------------------------------------ el ajuste

@pytest.mark.parametrize("valor,meses", [
    (None, 2), ({"meses": 2}, 2), ({"meses": 3}, 3), ({"meses": 12}, 12)])
def test_el_ajuste_dice_cuantos_meses_y_sin_el_son_dos(
        valor, meses, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    _poner(conn, ws, valor)
    with espacio(conn, ws) as cur:
        assert I.meses_de_horizonte(cur, ws) == meses
        assert I.limite_de_fecha(cur, ws, date(2026, 10, 1)) == sumar_meses(
            date(2026, 10, 1), meses)
    assert _incidentes(conn, ws) == 0


@pytest.mark.parametrize("valor", [
    {"meses": 0}, {"meses": -1}, {"meses": "dos"}, {"meses": 2.5},
    {"meses": True}, {"meses": None}, {}, "dos", 7, [2],
    {"meses": 121}, {"meses": 100000}])
def test_un_valor_invalido_usa_dos_meses_y_deja_un_incidente(
        valor, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    _poner(conn, ws, valor)
    with espacio(conn, ws) as cur:
        assert I.meses_de_horizonte(cur, ws) == 2
        assert I.meses_de_horizonte(cur, ws) == 2        # se avisa una vez
    assert _incidentes(conn, ws) == 1


# ---------------------------------------------------------------- el importador

def _importar(conn, tmp_path, **cambios):
    from prisma.importador import importar

    pack = yaml.safe_load((RAIZ / "espacios" / "corework.yaml").read_text("utf-8"))
    pack.pop("horizonte_tarea", None)
    pack.update(cambios)
    ruta = tmp_path / "p.yaml"
    ruta.write_text(yaml.safe_dump(pack, allow_unicode=True), "utf-8")
    return importar(conn, ruta)


def _guardado(conn, ws):
    with admin(conn) as cur:
        cur.execute("select valor from workspace_setting where workspace_id = %s "
                    "and clave = 'horizonte_tarea'", (ws,))
        fila = cur.fetchone()
        return fila["valor"] if fila else None


def test_el_pack_de_corework_declara_dos_meses(corework, conn):
    assert _guardado(conn, corework.workspace_id) == {"meses": 2}


def test_el_importador_guarda_el_valor_del_pack(conn, tmp_path):
    r = _importar(conn, tmp_path, horizonte_tarea={"meses": 3})
    assert _guardado(conn, r.workspace_id) == {"meses": 3}


def test_un_pack_sin_horizonte_no_siembra_nada(conn, tmp_path):
    r = _importar(conn, tmp_path)
    assert _guardado(conn, r.workspace_id) is None


@pytest.mark.parametrize("meses", ["dos", 0, 100000])
def test_un_pack_con_un_horizonte_invalido_advierte(meses, conn, tmp_path):
    r = _importar(conn, tmp_path, horizonte_tarea={"meses": meses})
    assert any("horizonte_tarea" in a for a in r.advertencias)


# ------------------------------------------------------------- el alta guiada

# NOW es 2028-02-28: con 2 meses el límite es 28/04/2028.
@pytest.mark.parametrize("iso", ["2028-04-29", "2028-10-04", "2029-01-01"])
def test_el_alta_guiada_rechaza_pasado_el_margen_y_nombra_el_limite(
        iso, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        r = _decir_fecha(cur, intake_world, actor, rid, ws, {"fecha_iso": iso})
        assert r is not None and r.inert
        assert "28/04/2028" in r.text and "ya pasó" not in r.text
        assert _campo(cur, rid, "due_date")["estado"] == "missing"
        assert _slot(cur, rid) == "due_date"


@pytest.mark.parametrize("iso", ["2028-04-28", "2028-03-05"])
def test_el_alta_guiada_acepta_hasta_el_limite_inclusive(iso, intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        _decir_fecha(cur, intake_world, actor, rid, ws, {"fecha_iso": iso})
        assert _campo(cur, rid, "due_date")["estado"] == "confirmed"


def test_el_alta_guiada_usa_el_margen_del_espacio(intake_world, conn):
    ws = intake_world["north-lab"]["id"]
    _poner(conn, ws, {"meses": 6})
    with espacio(conn, ws) as cur:
        actor, rid, ws = _en_la_fecha(cur, intake_world)
        _decir_fecha(cur, intake_world, actor, rid, ws,
                     {"fecha_iso": "2028-08-28"})
        assert _campo(cur, rid, "due_date")["estado"] == "confirmed"


# ------------------------------------------------- el alta conducida por el modelo

def _limite_mostrado(meses=2) -> str:
    return sumar_meses(_hoy(), meses).strftime("%d/%m/%Y")


def test_los_hechos_del_turno_traen_el_limite_de_la_fecha(chat):
    c = chat(salida("¿Qué hay que hacer?", pregunta=["title"]))
    c.escribir("necesito crear una tarea")
    datos = c.hechos(0)
    limite = sumar_meses(_hoy(), 2)
    assert limite.strftime("%d/%m/%Y") in datos["fechas"]
    assert limite.isoformat() in datos["fechas"]


def test_una_fecha_pasado_el_margen_se_rechaza_y_el_reintento_vuelve_a_preguntar(
        chat):
    limite = _limite_mostrado()
    c = chat(
        salida("Anotado para el 15 de agosto.",
               valores={"due_date": {"fecha_iso": _en(400)}},
               pregunta=["title"]),
        salida(f"Una tarea puede ir hasta el {limite}. ¿Para qué fecha de acá "
               "a esa la querés?", pregunta=["title", "due_date"]))

    nuevas = c.escribir("necesito crear una tarea para el 15 de agosto")

    assert len(c.modelo.conducidos) == 2
    assert any(limite in r for r in c.hechos(1)["rechazos_anteriores"])
    assert c.campo("due_date")["estado"] == "missing"
    assert len(_cuerpos(nuevas)) == 1 and limite in _cuerpos(nuevas)[0]
    assert c.incidentes("alta_conducida_fallida") == []


def test_la_fecha_justo_en_el_limite_se_guarda_en_el_alta_conducida(chat):
    limite = sumar_meses(_hoy(), 2)
    c = chat(salida("Dale.",
                    valores={"due_date": {"fecha_iso": limite.isoformat()}},
                    pregunta=["title"]))
    c.escribir("necesito crear una tarea")
    assert c.campo("due_date")["estado"] == "confirmed"
