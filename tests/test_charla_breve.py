"""La charla con una pregunta pendiente (F-B5, ADR 0013 regla 1, ADR 0014): la
respuesta breve la redacta el modelo, en las dos variantes, y la pregunta
pendiente se vuelve a hacer en la MISMA respuesta visible. Si el modelo falla o
su texto no sirve, sale sólo la pregunta y queda registrado: nunca en silencio.

Los ruteos y el modelo se guionan con `ProveedorGuionado`; ninguna prueba toca
la red.
"""

from __future__ import annotations

import json

import pytest

from prisma import incidentes, llm, redaccion
from prisma.db import admin
from prisma.llm import ProveedorGuionado, RespectoPendiente
from prisma.valores import TipoValor, ValorEsperado

from tests.test_alta_pregunta_pendiente import (PREGUNTA_TITULO, _abrir_alta,
                                                _mensaje_privado)
from tests.test_menu_tarea import cliente  # noqa: F401
from tests.test_pregunta_pendiente_otras import (_con_rutas, _filas_del_chat,
                                                 _ruta, _salidas)

# Estas pruebas son de la variante A con el plazo propio y el respaldo de plantilla de B
# (el comportamiento anterior al modelo puro, `redaccion.MODELO_PURO = False`); el modelo
# puro, el de por omisión, se prueba en `test_redaccion_modelo_puro.py`.
pytestmark = pytest.mark.usefixtures("con_respaldo_de_plantilla")

BREVE = "¡Hola! Un gusto."


def _con_charla(monkeypatch, borradores):
    proveedor = _con_rutas(monkeypatch, [_ruta(RespectoPendiente.CHARLA)])
    proveedor.borradores = list(borradores)
    return proveedor


def _incidentes_de_charla(conn) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select severidad, referencia_cruda from incident "
                    "where etapa = %s", (incidentes.ETAPA_CHARLA_SIN_RESPUESTA,))
        return cur.fetchall()


# ---------------------------------------------- la respuesta, en una sola salida

def _variante(conn, ws, variante):
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'redaccion', %s::jsonb)
                       on conflict (workspace_id, clave)
                       do update set valor = excluded.valor""",
                    (ws, json.dumps({"variante": variante})))
    conn.commit()


def _json(texto, pregunta=None):
    return json.dumps({"texto": texto, "pregunta": pregunta, "afirma": []},
                      ensure_ascii=False)


def test_con_b_la_charla_responde_breve_y_repregunta_en_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _ = _abrir_alta(conn, ws)
    _variante(conn, ws, "B")
    proveedor = _con_charla(monkeypatch, [BREVE])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "hola")

    assert _salidas(conn, tg) == antes + 1                     # una sola respuesta
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"] == f"{BREVE}\n\n{PREGUNTA_TITULO}"
    assert len(proveedor.redactados) == 1
    assert _incidentes_de_charla(conn) == []


def test_con_a_la_charla_y_la_pregunta_son_un_solo_mensaje_natural_del_modelo(
        cliente, conn, corework, monkeypatch):
    """F-A2: no una frase suelta delante de la plantilla, sino un mensaje que
    contesta y pide el dato."""
    ws = corework.workspace_id
    tg, _ = _abrir_alta(conn, ws)
    _variante(conn, ws, "A")
    mensaje = "Buen día. Cuando puedas, contame: ¿qué hay que hacer?"
    proveedor = _con_charla(monkeypatch, [_json(mensaje, "title")])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "hola")

    assert _salidas(conn, tg) == antes + 1                     # una sola respuesta
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"] == mensaje
    (sistema, hechos) = proveedor.redactados[0]
    datos = json.loads(hechos)
    assert datos["charla"] == "hola"
    assert datos["falta"]["campo"] == "title"
    assert PREGUNTA_TITULO in datos["falta"]["pregunta"]
    assert _incidentes_de_charla(conn) == []                   # no es el viejo prefijo


@pytest.mark.parametrize("borrador", [
    TimeoutError("colgado"), RuntimeError("cayó"),
    _json("Hola, qué bueno tenerte por acá.", "title"),     # no pide el dato
    _json("Hola. ¿Qué hay que hacer?", None),               # no declara cuál pide
    "Hola. ¿Qué hay que hacer?",                            # no es el JSON pedido
])
def test_con_a_si_el_mensaje_no_sirve_sale_la_pregunta_sola_y_queda_registrado(
        borrador, cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _ = _abrir_alta(conn, ws)
    _variante(conn, ws, "A")
    _con_charla(monkeypatch, [borrador])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "hola")

    assert _salidas(conn, tg) == antes + 1
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"] == PREGUNTA_TITULO
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where workspace_id = %s "
                    "and accion = %s", (ws, redaccion.ACCION_REDACCION_A))
        (intento,) = cur.fetchall()
    assert intento["detalle"]["resultado"] in ("error", "timeout", "rechazada")


@pytest.mark.parametrize("error", [TimeoutError("colgado"), RuntimeError("cayó")])
def test_si_el_modelo_falla_sale_sola_la_pregunta_y_queda_registrado(
        error, cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _ = _abrir_alta(conn, ws)
    _con_charla(monkeypatch, [error])
    antes = _salidas(conn, tg)

    _mensaje_privado(cliente, tg, "hola")

    assert _salidas(conn, tg) == antes + 1
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"] == PREGUNTA_TITULO
    assert [i["severidad"] for i in _incidentes_de_charla(conn)] == ["baja"]


@pytest.mark.parametrize("borrador", [
    "",                                   # el modelo no dijo nada
    "¿Y vos cómo andás?",                 # abre otra pregunta: la pregunta es una
    "Dale. " * 80,                        # no es breve
])
def test_un_texto_que_no_sirve_se_descarta_y_sale_sola_la_pregunta(
        borrador, cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _ = _abrir_alta(conn, ws)
    _con_charla(monkeypatch, [borrador])

    _mensaje_privado(cliente, tg, "hola")

    assert _filas_del_chat(conn, tg)[-1]["cuerpo"] == PREGUNTA_TITULO
    assert len(_incidentes_de_charla(conn)) == 1


# ------------------------------------------------ el modelo recibe lo que hace falta

def test_el_modelo_recibe_el_mensaje_y_la_pregunta_pendiente_como_datos(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    tg, _ = _abrir_alta(conn, ws)
    proveedor = _con_charla(monkeypatch, [BREVE])

    _mensaje_privado(cliente, tg, "buen día")

    sistema, hechos = proveedor.redactados[0]
    assert sistema == redaccion.SISTEMA_CHARLA
    assert json.loads(hechos) == {"mensaje": "buen día",
                                  "pregunta_pendiente": PREGUNTA_TITULO}


# ------------------------------------------------ los límites de lo que se acepta

@pytest.mark.parametrize("texto", [
    "¿Cómo andás?", "Hola.\n\nHola otra vez.", "x" * 400, "", "   "])
def test_charla_valida_rechaza_lo_que_no_es_una_respuesta_breve(texto):
    assert redaccion.motivo_de_charla_invalida(texto) is not None


@pytest.mark.parametrize("texto", [
    "¡Hola!", "De nada, para eso estoy.", "Buen día, Ariel. Seguimos con lo tuyo."])
def test_charla_valida_acepta_una_respuesta_breve(texto):
    assert redaccion.motivo_de_charla_invalida(texto) is None


# ------------------------------------------------ las definiciones del ruteo

def _bloque_de_la_pregunta_pendiente() -> str:
    return llm._sistema_del_ruteo(
        "¿Cómo se sabe que la tarea está terminada?",
        ValorEsperado(TipoValor.TEXTO))


def test_el_ruteo_define_responde_por_el_contenido_que_podria_responder():
    sistema = _bloque_de_la_pregunta_pendiente()
    # Un mensaje que da contenido que podría responder la pregunta es `responde`
    # (o `dudoso` si no está claro), aunque no sea la forma esperada.
    assert "contenido que podría responder" in sistema
    assert "responde" in sistema and "dudoso" in sistema


def test_el_ruteo_limita_charla_a_saludos_agradecimientos_y_charla_sin_relacion():
    sistema = _bloque_de_la_pregunta_pendiente()
    assert "charla: sólo un saludo, un agradecimiento o conversación suelta" in sistema
    assert "nunca" in sistema.split("charla:")[1].split("dudoso:")[0]
