"""La repregunta de una respuesta incompleta (F-B1, `valor.falta`) sale por la
redacción del turno como cualquier otra pregunta (ADR 0014, etapa 6): con la
variante B es la plantilla del código; con A la escribe el modelo y el código
la verifica, y si no sirve sale la de B. Una sola respuesta, la misma pregunta
sigue abierta.

El modelo y el ruteo se guionan; ninguna prueba toca la red.
"""

from __future__ import annotations

import json

import pytest

from prisma import incidentes, redaccion
from prisma.db import admin
from prisma.llm import RespectoPendiente

from tests.test_alta_pregunta_pendiente import (_abrir_alta, _campo_del_slot,
                                                _mensaje_privado, _ruta_con_valor)
from tests.test_menu_tarea import cliente  # noqa: F401
from tests.test_pregunta_pendiente_otras import (_con_rutas, _filas_del_chat,
                                                 _salidas)


# La repregunta de B (`valores._incompleto`): lo que falta y qué sirve.
REPREGUNTA_B = ("Con eso no me alcanza para fijar un día. Decime el día exacto, "
                "por ejemplo «el viernes» o «el 4 de octubre».")


def _json(texto, pregunta=None, afirma=()):
    return json.dumps({"texto": texto, "pregunta": pregunta, "afirma": list(afirma)},
                      ensure_ascii=False)


def _variante(conn, ws, variante: str) -> None:
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'redaccion', %s::jsonb)
                       on conflict (workspace_id, clave)
                       do update set valor = excluded.valor""",
                    (ws, json.dumps({"variante": variante})))
    conn.commit()


def _rechazadas(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where etapa = %s",
                    (incidentes.ETAPA_REDACCION_RECHAZADA,))
        return cur.fetchone()["n"]


def _repreguntar_dia(cliente, conn, ws, monkeypatch, borradores):
    tg, _ = _abrir_alta(conn, ws, campo="due_date")
    proveedor = _con_rutas(monkeypatch, [_ruta_con_valor(
        {"falta": "dia"}, RespectoPendiente.RESPONDE)])
    proveedor.borradores = list(borradores)
    antes, rechazadas = _salidas(conn, tg), _rechazadas(conn)
    _mensaje_privado(cliente, tg, "la semana que viene")
    return tg, proveedor, _salidas(conn, tg) - antes, _rechazadas(conn) - rechazadas


def test_con_b_la_repregunta_es_la_plantilla_y_el_modelo_no_se_llama(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _variante(conn, ws, "B")

    tg, proveedor, salidas, _ = _repreguntar_dia(
        cliente, conn, ws, monkeypatch, [])

    assert salidas == 1 and _campo_del_slot(conn) == "due_date"
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"] == REPREGUNTA_B
    assert proveedor.redactados == []


def test_con_a_la_repregunta_la_escribe_el_modelo_en_una_sola_respuesta(
        cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _variante(conn, ws, "A")
    # El mensaje entero: la razón, qué sirve y la pregunta (ya no la plantilla).
    pregunta = ("Con eso no me alcanza para fijar un día. ¿Para qué día la "
                "necesitás? Decime el día exacto, por ejemplo «el viernes» o «el 4 "
                "de octubre».")

    tg, proveedor, salidas, _ = _repreguntar_dia(
        cliente, conn, ws, monkeypatch, [_json(pregunta, "due_date")])

    assert salidas == 1 and _campo_del_slot(conn) == "due_date"
    assert len(proveedor.redactados) == 1                 # el modelo redactó
    assert _filas_del_chat(conn, tg)[-1]["cuerpo"] == pregunta


@pytest.mark.parametrize("error", [RuntimeError("cayó"),
                                   _json("Dale, anotado."), "Dale, anotado."])
def test_con_a_si_el_modelo_falla_o_no_pasa_la_verificacion_sale_la_de_b(
        error, cliente, conn, corework, monkeypatch):
    ws = corework.workspace_id
    _variante(conn, ws, "A")

    tg, _, salidas, nuevas = _repreguntar_dia(
        cliente, conn, ws, monkeypatch, [error])

    cuerpo = _filas_del_chat(conn, tg)[-1]["cuerpo"]
    assert salidas == 1 and cuerpo == REPREGUNTA_B
    assert nuevas == 1
