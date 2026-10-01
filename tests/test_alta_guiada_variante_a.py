"""El alta guiada con la variante A (ADR 0014, F6a): preguntas y resumen salen
del modelo, verificados por el código; si el texto no sirve o el modelo falla,
sale el de B, que lo reemplaza (una sola respuesta); con B, el modelo no se
llama y el texto es el de siempre.

El modelo de redacción se guiona; ninguna prueba toca la red.
"""

from __future__ import annotations

import json

import pytest

from prisma import incidentes, redaccion
from prisma import ingreso_tareas as I
from prisma.db import admin, espacio
from prisma.llm import ProveedorGuionado

from tests.test_alta_eleccion_confirmacion import _alta_en_confirmacion, _usuario
from tests.test_alta_enviar_a_aprobacion import (_acciones, _alta_en_revision, _fila,
                                                 _tocar)
from tests.test_alta_guiada_flujo import _cuerpos, _empezar
from tests.test_task_intake import _callback_client

PREGUNTA_B = "¿Qué hay que hacer?"


def _json(texto, pregunta=None, afirma=()):
    return json.dumps({"texto": texto, "pregunta": pregunta, "afirma": list(afirma)},
                      ensure_ascii=False)


APERTURA = "Listo, ya está el borrador. Revisalo:"


class _Eco:
    """Un modelo que escribe distinto de las plantillas pero fiel a los
    hechos: la pregunta con una frase delante y, con un resumen, sólo la
    apertura (los datos y el cierre los agrega el código)."""

    def __init__(self):
        self.redactados: list[dict] = []

    def redactar(self, sistema: str, hechos: str, **_) -> str:
        datos = json.loads(hechos)
        self.redactados.append(datos)
        if "resumen" in datos:
            return _json(APERTURA)
        partes = []
        if "entendido" in datos:
            partes.append("Anoté " + ", ".join(e["valor"] for e in datos["entendido"])
                          + ".")
        if "rechazo" in datos:
            partes.append(f"{datos['rechazo']['razon']} {datos['rechazo']['se_acepta']}")
        pregunta = None
        if "falta" in datos:
            partes.append(datos["falta"].get("pregunta") or "¿Me lo decís?")
            if "?" not in partes[-1]:       # un buen modelo pide con signos
                partes.append("¿Cuál?")
            pregunta = datos["falta"]["campo"]
        return _json("Dale. " + " ".join(partes), pregunta)


def _con_variante(conn, ws, variante, monkeypatch, proveedor):
    with admin(conn) as cur:
        cur.execute("""insert into workspace_setting (workspace_id, clave, valor)
                       values (%s, 'redaccion', %s::jsonb)""",
                    (ws, json.dumps({"variante": variante})))
    monkeypatch.setattr(redaccion, "proveedor_de_redaccion",
                        lambda cur, workspace_id: proveedor)


def _intentos(conn, ws) -> list[dict]:
    with admin(conn) as cur:
        cur.execute("select detalle from audit_log where workspace_id = %s "
                    "and accion = %s order by at", (ws, redaccion.ACCION_REDACCION_A))
        return [f["detalle"] for f in cur.fetchall()]


def _incidentes(conn) -> int:
    with admin(conn) as cur:
        cur.execute("select count(*) n from incident where etapa = %s",
                    (incidentes.ETAPA_REDACCION_RECHAZADA,))
        return cur.fetchone()["n"]


# ----------------------------------------------------------- las preguntas

def test_con_a_la_pregunta_es_el_texto_del_modelo_y_sale_una_sola_vez(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    eco = _Eco()
    _con_variante(conn, ws, "A", monkeypatch, eco)

    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, chat=73001)
        cuerpos = _cuerpos(cur, outcome.request_id)

    assert outcome.text == "Dale. " + PREGUNTA_B
    assert cuerpos == [outcome.text]                 # una sola respuesta
    assert len(eco.redactados) == 1
    assert [i["resultado"] for i in _intentos(conn, ws)] == ["aceptada"]
    assert _incidentes(conn) == 0


@pytest.mark.parametrize("error", [TimeoutError("colgado"), RuntimeError("cayó")])
def test_si_el_modelo_falla_sale_la_pregunta_de_b_una_sola_vez_y_queda_registrado(
        error, intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    _con_variante(conn, ws, "A", monkeypatch, ProveedorGuionado(
        guion=[], borradores=[error]))

    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, chat=73002)
        cuerpos = _cuerpos(cur, outcome.request_id)

    assert outcome.text == PREGUNTA_B and cuerpos == [PREGUNTA_B]
    esperado = "timeout" if isinstance(error, TimeoutError) else "error"
    assert [i["resultado"] for i in _intentos(conn, ws)] == [esperado]
    assert _incidentes(conn) == 1


def test_si_el_verificador_rechaza_sale_la_pregunta_de_b_una_sola_vez(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    _con_variante(conn, ws, "A", monkeypatch, ProveedorGuionado(
        guion=[], borradores=[_json("Anoté tu pedido, ¿qué más?")]))

    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, chat=73003)
        cuerpos = _cuerpos(cur, outcome.request_id)

    assert outcome.text == PREGUNTA_B and cuerpos == [PREGUNTA_B]
    (intento,) = _intentos(conn, ws)
    assert intento["resultado"] == "rechazada"
    assert intento["motivo"].startswith("falta_pregunta")
    assert _incidentes(conn) == 1


def test_con_b_no_se_llama_al_modelo_y_el_texto_es_el_de_siempre(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    eco = _Eco()
    _con_variante(conn, ws, "B", monkeypatch, eco)

    with espacio(conn, ws) as cur:
        _, outcome = _empezar(cur, intake_world, chat=73004)

    assert outcome.text == PREGUNTA_B
    assert eco.redactados == [] and _intentos(conn, ws) == []


# ----------------------------------------------------------- el resumen

def test_con_a_el_resumen_lo_redacta_el_modelo_una_vez_y_el_cierre_es_del_codigo(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    eco = _Eco()
    _con_variante(conn, ws, "A", monkeypatch, eco)

    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")

    resumenes = [d for d in eco.redactados if "resumen" in d]
    assert len(resumenes) == 1
    with admin(conn) as cur:
        cur.execute("select resumen from pending_action where id = %s", (pid,))
        texto = cur.fetchone()["resumen"]
    assert texto.startswith(APERTURA + "\n\nResumen para revisar\nTítulo: ")
    assert texto.endswith("\n\n" + I.CIERRE_CONFIRMAR)
    assert "Con Confirmar" not in json.dumps(resumenes[0], ensure_ascii=False)
    assert all(i["resultado"] == "aceptada" for i in _intentos(conn, ws))


def test_con_a_enviar_a_aprobacion_conserva_el_cuerpo_del_modelo_con_el_cierre_de_quien_confirma(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]
    eco = _Eco()
    _con_variante(conn, ws, "A", monkeypatch, eco)
    rid, pid = _alta_en_revision(conn, intake_world)
    (revision, *_) = _acciones(conn, rid)
    cuerpo = revision["args"]["cuerpo_resumen"]
    assert cuerpo.startswith(APERTURA + "\n\nResumen para revisar\nTítulo: ")
    assert revision["resumen"] == cuerpo + "\n\n" + I.cierre_enviar("Morgan Hale 1")
    antes = len([d for d in eco.redactados if "resumen" in d])
    assert antes == 1                                 # un solo borrador para los dos cierres

    client = _callback_client(conn, monkeypatch)
    _tocar(client, conn, _usuario(intake_world), pid, "Enviar a aprobación")

    (_, confirmacion) = _acciones(conn, rid)
    assert _fila(conn, confirmacion["id"])["cuerpo"] == (
        cuerpo + "\n\n" + I.CIERRE_CONFIRMAR)
    assert len([d for d in eco.redactados if "resumen" in d]) == 1  # no vuelve al modelo


def test_si_el_modelo_falla_en_el_resumen_sale_el_de_b_con_su_cierre(
        intake_world, conn, monkeypatch):
    ws = intake_world["north-lab"]["id"]

    class _SoloElResumenFalla(_Eco):
        def redactar(self, sistema, hechos, **_):
            if "resumen" in json.loads(hechos):
                raise TimeoutError("colgado")
            return super().redactar(sistema, hechos)

    _con_variante(conn, ws, "A", monkeypatch, _SoloElResumenFalla())

    rid, pid = _alta_en_confirmacion(conn, intake_world, responsable="Sam North")

    with admin(conn) as cur:
        cur.execute("select resumen from pending_action where id = %s", (pid,))
        texto = cur.fetchone()["resumen"]
    assert texto.startswith("Resumen para revisar\nTítulo: ")      # B, sin apertura
    assert texto.endswith("\n\n" + I.CIERRE_CONFIRMAR)
    assert [i["resultado"] for i in _intentos(conn, ws)].count("timeout") == 1
    assert _incidentes(conn) == 1
