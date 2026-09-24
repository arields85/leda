"""Cliente de Jev y resolución de referencias a tarea.

Receta congelada (`docs/architecture/interpretacion-y-confirmacion.md` §5.6,
§5.8, §5.9): una llamada de alcance + tarea, y si decide clara, una segunda
de verificación. Ninguna prueba acá llama a la red: usan `ClienteJevGuionado`
o un transporte falso de `httpx`.
"""

from __future__ import annotations

import json

import httpx
import pytest

from prisma import jev
from prisma.jev import (URL, ClienteJev, ClienteJevGuionado, JevError,
                         ResolucionReferencia, TareaCandidata, TipoResolucion,
                         resolver_referencia_tarea)


def _transporte(pasos):
    """`pasos`: lista de `(status, cuerpo)` o una excepción a lanzar."""
    pedidos: list[dict] = []

    def manejador(request: httpx.Request) -> httpx.Response:
        pedidos.append(json.loads(request.content))
        paso = pasos[len(pedidos) - 1]
        if isinstance(paso, Exception):
            raise paso
        status, cuerpo = paso
        return httpx.Response(status, json=cuerpo)

    return httpx.Client(transport=httpx.MockTransport(manejador)), pedidos


def _sin_espera(_segundos: float) -> None:
    return None


# --------------------------------------------------------------------- cliente

def test_cliente_jev_envia_bearer_y_el_cuerpo_de_la_api_de_decisiones():
    http, pedidos = _transporte([
        (200, {"answers": {"q": {"choice": "si", "probabilities": {"si": 0.9},
                                  "confidence": 0.9}}}),
    ])
    cliente = ClienteJev(api_key="clave-secreta", cliente=http, dormir=_sin_espera)

    respuesta = cliente.decidir(
        {"mensaje": "hola"}, {"q": {"type": "noul", "instructions": "¿si?"}})

    assert respuesta == {"q": {"choice": "si", "probabilities": {"si": 0.9},
                                "confidence": 0.9}}
    assert pedidos[0] == {
        "model": "typesafe/jev-1.13",
        "state": {"mensaje": "hola"},
        "questions": {"q": {"type": "noul", "instructions": "¿si?"}},
    }


def test_cliente_jev_manda_la_clave_como_bearer():
    capturado = {}

    def manejador(request: httpx.Request) -> httpx.Response:
        capturado["auth"] = request.headers.get("authorization")
        capturado["url"] = str(request.url)
        return httpx.Response(200, json={"answers": {}})

    http = httpx.Client(transport=httpx.MockTransport(manejador))
    cliente = ClienteJev(api_key="mi-clave", cliente=http, dormir=_sin_espera)

    cliente.decidir({}, {})

    assert capturado["auth"] == "Bearer mi-clave"
    assert capturado["url"] == URL


def test_cliente_jev_usa_la_respuesta_completa_si_no_hay_answers():
    http, _ = _transporte([(200, {"q": {"noul": 0.4}})])
    cliente = ClienteJev(api_key="k", cliente=http, dormir=_sin_espera)

    respuesta = cliente.decidir({}, {"q": {"type": "noul", "instructions": "?"}})

    assert respuesta == {"q": {"noul": 0.4}}


def test_cliente_jev_reintenta_un_timeout_y_despues_responde_bien():
    http, pedidos = _transporte([
        httpx.TimeoutException("se colgó"),
        (200, {"answers": {"q": {"noul": 0.7}}}),
    ])
    cliente = ClienteJev(api_key="k", cliente=http, dormir=_sin_espera)

    respuesta = cliente.decidir({}, {"q": {"type": "noul", "instructions": "?"}})

    assert respuesta == {"q": {"noul": 0.7}}
    assert len(pedidos) == 2


def test_cliente_jev_reintenta_500_y_despues_responde_bien():
    http, pedidos = _transporte([
        (500, {"error": "server"}),
        (200, {"answers": {"q": {"noul": 0.7}}}),
    ])
    cliente = ClienteJev(api_key="k", cliente=http, dormir=_sin_espera)

    respuesta = cliente.decidir({}, {"q": {"type": "noul", "instructions": "?"}})

    assert respuesta == {"q": {"noul": 0.7}}
    assert len(pedidos) == 2


def test_cliente_jev_agota_los_intentos_y_lanza_jeverror_acotado():
    http, pedidos = _transporte([
        (500, {}), (502, {}), (503, {}), (504, {}),
    ])
    cliente = ClienteJev(api_key="k", cliente=http, dormir=_sin_espera, intentos=4)

    with pytest.raises(JevError):
        cliente.decidir({}, {"q": {"type": "noul", "instructions": "?"}})

    assert len(pedidos) == 4  # acotado: nunca infinito


def test_cliente_jev_no_reintenta_un_error_no_reintentable():
    http, pedidos = _transporte([(401, {"error": "clave inválida"})])
    cliente = ClienteJev(api_key="k", cliente=http, dormir=_sin_espera)

    with pytest.raises(JevError):
        cliente.decidir({}, {"q": {"type": "noul", "instructions": "?"}})

    assert len(pedidos) == 1


def test_cliente_jev_todos_los_timeouts_lanza_jeverror():
    http, pedidos = _transporte([httpx.TimeoutException("x")] * 4)
    cliente = ClienteJev(api_key="k", cliente=http, dormir=_sin_espera, intentos=4)

    with pytest.raises(JevError):
        cliente.decidir({}, {"q": {"type": "noul", "instructions": "?"}})

    assert len(pedidos) == 4


# ------------------------------------------------------------- doble guionado

def test_cliente_jev_guionado_devuelve_en_orden_y_registra_los_pedidos():
    doble = ClienteJevGuionado(guion=[{"q": {"noul": 0.9}}, {"q": {"noul": 0.1}}])

    r1 = doble.decidir({"mensaje": "a"}, {"q": {"type": "noul"}})
    r2 = doble.decidir({"mensaje": "b"}, {"q": {"type": "noul"}})

    assert r1 == {"q": {"noul": 0.9}}
    assert r2 == {"q": {"noul": 0.1}}
    assert doble.pedidos == [
        ({"mensaje": "a"}, {"q": {"type": "noul"}}),
        ({"mensaje": "b"}, {"q": {"type": "noul"}}),
    ]


def test_cliente_jev_guionado_lanza_jeverror_si_se_agota_el_guion():
    doble = ClienteJevGuionado(guion=[])

    with pytest.raises(JevError):
        doble.decidir({}, {})


# --------------------------------------------------------- resolución de tareas

# Ids con forma de identificador real (no "T1".."T3": esas son las claves
# cortas que arma el resolutor para mandarle a Jev, no lo que identifica la
# tarea en la base).
TAREA_TABLERO_3 = TareaCandidata(id="8f14e2-tablero-3", titulo="Cablear tablero máq. 3",
                                  area="Sistemas eléctricos", responsable="Mariano Naim")
TAREA_TABLERO_4 = TareaCandidata(id="2b7a91-tablero-4", titulo="Revisar tablero máq. 4",
                                  area="Sistemas eléctricos", responsable="Mariano Naim")
TAREA_HMI = TareaCandidata(id="c40d55-hmi", titulo="Actualizar HMI de CoreLabs",
                            area="Software", responsable="Ariel De Simone")


def _alcance(una_tarea=0.0, varias_tareas=0.0, ninguna=0.0):
    top = max(("una_tarea", una_tarea), ("varias_tareas", varias_tareas),
               ("ninguna", ninguna), key=lambda kv: kv[1])
    return {"choice": top[0],
            "probabilities": {"una_tarea": una_tarea, "varias_tareas": varias_tareas,
                               "ninguna": ninguna},
            "confidence": top[1]}


def _tarea(probabilidades: dict[str, float]):
    top = max(probabilidades.items(), key=lambda kv: kv[1])
    return {"choice": top[0], "probabilities": probabilidades, "confidence": top[1]}


def test_resolver_referencia_clara_llama_verificacion_y_confirma():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05, "T3": 0.05})},
        {"misma": {"noul": 0.8}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.CLARA, tarea_id=TAREA_TABLERO_3.id)
    assert len(doble.pedidos) == 2
    assert doble.pedidos[1][0]["tarea"] == (
        "Cablear tablero máq. 3 — área: Sistemas eléctricos — responsable: Mariano Naim")


def test_resolver_referencia_usa_claves_cortas_para_las_opciones_de_jev():
    """Las opciones de la elección "tarea" viajan como "T1".."Tn", en el orden
    de entrada, no con el id real (que en producción es un UUID y nunca se
    midió como clave de Jev en 5.3-5.9). La respuesta se traduce de vuelta al
    id real."""
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05, "T3": 0.05})},
        {"misma": {"noul": 0.8}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    criterios_enviados = doble.pedidos[0][1]["tarea"]["criteria"]
    assert list(criterios_enviados) == ["T1", "T2", "T3"]
    assert criterios_enviados["T1"] == TAREA_TABLERO_3.criterio()
    assert criterios_enviados["T2"] == TAREA_TABLERO_4.criterio()
    assert criterios_enviados["T3"] == TAREA_HMI.criterio()
    assert resultado.tarea_id == TAREA_TABLERO_3.id


def test_resolver_referencia_ninguna_por_alcance_no_llama_verificacion():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(ninguna=0.9),
         "tarea": _tarea({"T1": 0.05, "T2": 0.03, "T3": 0.02})},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="lo del horno", referencia="el horno",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(TipoResolucion.NINGUNA)
    assert len(doble.pedidos) == 1


def test_resolver_referencia_varias_da_ambigua_con_candidatas_ordenadas():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(varias_tareas=0.7),
         "tarea": _tarea({"T1": 0.5, "T2": 0.3, "T3": 0.05})},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="las cosas de electricidad", referencia="lo eléctrico",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.AMBIGUA, candidatas=(TAREA_TABLERO_3.id, TAREA_TABLERO_4.id))
    assert len(doble.pedidos) == 1


def test_resolver_referencia_sin_alcanzar_los_cortes_es_ambigua():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.8),
         "tarea": _tarea({"T1": 0.55, "T2": 0.4, "T3": 0.05})},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="lo del tablero", referencia="el tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.AMBIGUA, candidatas=(TAREA_TABLERO_3.id, TAREA_TABLERO_4.id))
    assert len(doble.pedidos) == 1


def test_resolver_referencia_verificacion_baja_pasa_a_ambigua_con_esa_tarea():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05, "T3": 0.05})},
        {"misma": {"noul": 0.3}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="ya esta el horno?", referencia="el horno",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.AMBIGUA, candidatas=(TAREA_TABLERO_3.id,))
    assert len(doble.pedidos) == 2


def test_resolver_referencia_lista_vacia_no_llama_a_jev():
    doble = ClienteJevGuionado(guion=[{"nunca": "se usa"}])

    resultado = resolver_referencia_tarea(
        doble, mensaje="algo", referencia="algo", tareas=(), vocabulario="")

    assert resultado == ResolucionReferencia(TipoResolucion.NINGUNA)
    assert doble.pedidos == []


def test_resolver_referencia_una_sola_tarea_sin_segunda_probabilidad():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea({"T1": 0.9})},
        {"misma": {"noul": 0.75}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3,), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.CLARA, tarea_id=TAREA_TABLERO_3.id)


def test_resolver_referencia_ignora_candidatos_que_no_estan_en_la_entrada():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T9": 0.95, "T1": 0.5})},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="algo raro", referencia="algo",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")

    # "T9" no es una clave que el resolutor haya mandado (sólo mandó T1 y
    # T2): se descarta y decide sobre lo que queda, sin romper.
    assert resultado == ResolucionReferencia(
        TipoResolucion.AMBIGUA, candidatas=(TAREA_TABLERO_3.id,))


# ------------------------------------------------- respuestas malformadas de Jev

@pytest.mark.parametrize("respuesta_mala", [
    pytest.param({}, id="vacia"),
    pytest.param({"alcance": _alcance(una_tarea=0.9)}, id="falta-tarea"),
    pytest.param({"tarea": _tarea({"T1": 0.9})}, id="falta-alcance"),
    pytest.param({"alcance": {"choice": "una_tarea"},
                  "tarea": _tarea({"T1": 0.9})}, id="alcance-sin-probabilities"),
    pytest.param({"alcance": _alcance(una_tarea=0.9),
                  "tarea": {"choice": "T1"}}, id="tarea-sin-probabilities"),
    pytest.param({"alcance": _alcance(una_tarea=0.9),
                  "tarea": {"probabilities": "no-es-un-objeto"}},
                 id="probabilities-no-es-dict"),
    pytest.param({"alcance": _alcance(una_tarea=0.9),
                  "tarea": {"probabilities": {"T1": "alta"}}},
                 id="probabilidad-no-numerica"),
])
def test_resolver_referencia_primera_llamada_malformada_lanza_jeverror(respuesta_mala):
    doble = ClienteJevGuionado(guion=[respuesta_mala])

    with pytest.raises(JevError):
        resolver_referencia_tarea(
            doble, mensaje="m", referencia="r",
            tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")


@pytest.mark.parametrize("verificacion_mala", [
    pytest.param({}, id="vacia"),
    pytest.param({"misma": {}}, id="sin-noul"),
    pytest.param({"misma": {"noul": "alta"}}, id="noul-no-numerico"),
    pytest.param({"misma": "no-es-un-objeto"}, id="misma-no-es-dict"),
])
def test_resolver_referencia_verificacion_malformada_lanza_jeverror(verificacion_mala):
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05})},
        verificacion_mala,
    ])

    with pytest.raises(JevError):
        resolver_referencia_tarea(
            doble, mensaje="m", referencia="r",
            tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")


# ------------------------------------------------- quién escribe (T4, §5.10)
#
# §5.10 midió que el dato solo -- sin pista en la instrucción -- es seguro
# (0 inseguros en 5 repeticiones) y que una pista lo empeora (1 o 2 inseguros
# por repetición). Por eso `quien_escribe` viaja como un campo más del
# `state`, nunca como texto agregado a las instrucciones.

def test_quien_escribe_viaja_en_el_state_de_las_dos_llamadas_cuando_se_pasa():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05})},
        {"misma": {"noul": 0.8}},
    ])

    resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="",
        quien_escribe="Marcos Tarquini")

    assert len(doble.pedidos) == 2
    assert doble.pedidos[0][0]["quien_escribe"] == "Marcos Tarquini"
    assert doble.pedidos[1][0]["quien_escribe"] == "Marcos Tarquini"


def test_sin_quien_escribe_no_agrega_el_campo_ni_cambia_las_instrucciones():
    """Sin `quien_escribe` (por defecto, `None`), el `state` sigue exactamente
    como antes de esta unidad: sin el campo, y sin ninguna pista agregada a
    `INSTRUCCION_ALCANCE`/`INSTRUCCION_TAREA`/`INSTRUCCION_VERIFICACION` (la
    pista medida en §5.10 empeoró la receta)."""
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05})},
        {"misma": {"noul": 0.8}},
    ])

    resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")

    assert "quien_escribe" not in doble.pedidos[0][0]
    assert "quien_escribe" not in doble.pedidos[1][0]
    for instruccion in (jev.INSTRUCCION_ALCANCE, jev.INSTRUCCION_TAREA,
                        jev.INSTRUCCION_VERIFICACION):
        assert "quien" not in instruccion.lower()
