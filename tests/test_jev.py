"""Cliente de Jev y resolución de referencias a tarea.

Receta congelada (`docs/architecture/interpretacion-y-confirmacion.md` §5.6,
§5.8, §5.9): una llamada de alcance + tarea, y si decide clara, una segunda
de verificación. Ninguna prueba acá llama a la red: usan `ClienteJevGuionado`
o un transporte falso de `httpx`.
"""

from __future__ import annotations

import dataclasses
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


def test_cliente_jev_repr_no_incluye_la_clave():
    cliente = ClienteJev(api_key="secreto-de-prueba", cliente=object())

    representacion = repr(cliente)

    assert "secreto-de-prueba" not in representacion


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


# --------------------------------------------- bloqueos abiertos en el criterio

def test_criterio_sin_bloqueos_no_cambia():
    assert TAREA_TABLERO_3.criterio() == (
        "Cablear tablero máq. 3 — área: Sistemas eléctricos — responsable: "
        "Mariano Naim")


def test_criterio_con_un_bloqueo_abierto_suma_la_causa():
    """T7, punto H (decisión del usuario, 2026-09-24: las causas de bloqueo
    pueden viajar a TypeSafe vía OpenRouter). b-0003: "ya llegó el switch que
    faltaba para el tablero, dalo por resuelto" nombra la tarea por su
    bloqueo, no por su título -- la verificación rechazaba porque el
    criterio sólo tenía el título."""
    tarea = dataclasses.replace(TAREA_TABLERO_3,
                                causas_bloqueo="falta el switch industrial en sala")
    assert tarea.criterio() == (
        "Cablear tablero máq. 3 — área: Sistemas eléctricos — responsable: "
        "Mariano Naim — bloqueada: falta el switch industrial en sala")


def test_criterio_con_varios_bloqueos_los_une():
    tarea = dataclasses.replace(
        TAREA_TABLERO_3,
        causas_bloqueo="falta el switch industrial en sala; falta aprobación del plano")
    assert "bloqueada: falta el switch industrial en sala; falta aprobación del plano" in (
        tarea.criterio())


def test_criterio_acota_una_causa_de_bloqueo_muy_larga():
    causa_larga = "x" * (jev.MAX_LONGITUD_CAUSAS_BLOQUEO + 50)
    tarea = dataclasses.replace(TAREA_TABLERO_3, causas_bloqueo=causa_larga)
    criterio = tarea.criterio()
    # La parte de la causa nunca supera la cota (más el "…" de corte); el
    # resto del criterio (título, área, responsable) no se toca.
    parte_bloqueo = criterio.split("bloqueada: ", 1)[1]
    assert len(parte_bloqueo) <= jev.MAX_LONGITUD_CAUSAS_BLOQUEO
    assert parte_bloqueo.endswith("…")
    assert criterio.startswith(TAREA_TABLERO_3.criterio())


def test_criterio_de_verificacion_tambien_lleva_el_bloqueo():
    """"Apply it to the verification call's task description too" -- como
    `resolver_referencia_tarea` arma la verificación con `top_tarea.
    criterio()`, un solo cambio en `criterio()` alcanza para las dos
    llamadas; esta prueba lo confirma de punta a punta."""
    tarea = dataclasses.replace(TAREA_TABLERO_3,
                                causas_bloqueo="falta el switch industrial en sala")
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea({"T1": 0.9})},
        {"misma": {"noul": 0.8}},
    ])

    resolver_referencia_tarea(
        doble, mensaje="dalo por resuelto", referencia="el switch que faltaba",
        tareas=(tarea,), vocabulario="")

    state_verificacion = doble.pedidos[1][0]
    assert state_verificacion["tarea"] == tarea.criterio()
    assert "bloqueada: falta el switch industrial en sala" in state_verificacion["tarea"]


def _tarea(probabilidades: dict[str, float]):
    top = max(probabilidades.items(), key=lambda kv: kv[1])
    return {"choice": top[0], "probabilities": probabilidades, "confidence": top[1]}


def test_resolver_referencia_clara_llama_verificacion_y_confirma():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05, "T3": 0.05})},
        # T2 es la subcampeona (T7, punto L, revisión del orquestador): la
        # pregunta "rival" se hace sin importar cuán baja sea su
        # probabilidad -- una respuesta baja de "rival" no cambia el
        # resultado de esta prueba (sigue clara).
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.1}},
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
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.1}},
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


def test_resolver_referencia_varias_da_varias_con_candidatas_ordenadas():
    """T7, punto C: el alcance "varias_tareas" (un área, lo de una persona o
    algo genérico) es un tipo aparte de una ambigüedad real entre pocas
    candidatas -- `gateway.py` no le abre botones (T4 los reserva para
    ambigüedad de una sola tarea); se lo pasa al modelo como contexto."""
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(varias_tareas=0.7),
         "tarea": _tarea({"T1": 0.5, "T2": 0.3, "T3": 0.05})},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="las cosas de electricidad", referencia="lo eléctrico",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.VARIAS, candidatas=(TAREA_TABLERO_3.id, TAREA_TABLERO_4.id))
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


# ------------------------------------------------- candidata subcampeona (rival)
#
# T7, punto L; decisión del usuario, 2026-09-24: "ante la duda se pregunta"
# (medido en el diseño §5.11). Cuando la receta decide clara, la MISMA
# llamada de verificación suma un segundo Noul ("rival") sobre la
# subcampeona -- la segunda más probable que Jev haya devuelto, sin importar
# su probabilidad (revisión del orquestador, 2026-09-24: b-0013 medía
# justamente 0,91 / 0,09 -- un corte por `CORTE_CANDIDATA` en la primera
# versión de esta unidad dejaba a la subcampeona afuera y "rival" nunca se
# preguntaba). Sólo cuando Jev no devolvió una segunda tarea en absoluto
# (una sola entrada en la respuesta de "tarea") no hay de quién preguntar --
# eso sigue exactamente como antes de esta unidad.

def test_instruccion_rival_pregunta_por_la_referencia_no_por_el_mensaje():
    """T7, punto M; revisión del orquestador, 2026-09-24: la redacción
    original de "rival" ("¿El mensaje también podría...") preguntaba por el
    MENSAJE completo, así que un pedido de dependencia que nombra las dos
    tareas ("el cableado del tablero no puede arrancar hasta que yo termine
    de programar el PLC") hacía que "rival" contestara que sí para las dos
    referencias -- b-0005 (9/9) y b-0015 (3/3) terminaban preguntando en vez
    de crear la dependencia. La v2 medida en el diseño §5.12 pregunta por la
    REFERENCIA, tal como está dicha, no por el mensaje entero."""
    assert jev.INSTRUCCION_RIVAL == (
        "¿La referencia, tal como está dicha, también podría estar hablando "
        "de esta otra tarea en lugar de la elegida? Respondé que sí sólo si "
        "una persona del equipo podría entender esa referencia como "
        "cualquiera de las dos.")
    assert "El mensaje también podría" not in jev.INSTRUCCION_RIVAL


def test_resolver_referencia_clara_con_subcampeona_pide_rival_en_la_misma_llamada():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.4})},
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.2}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.CLARA, tarea_id=TAREA_TABLERO_3.id)
    assert len(doble.pedidos) == 2
    preguntas_verificacion = doble.pedidos[1][1]
    assert "rival" in preguntas_verificacion
    assert preguntas_verificacion["rival"]["instructions"] == jev.INSTRUCCION_RIVAL
    state_verificacion = doble.pedidos[1][0]
    assert state_verificacion["tarea_elegida"] == TAREA_TABLERO_3.criterio()
    assert state_verificacion["otra_tarea"] == TAREA_TABLERO_4.criterio()


def test_resolver_referencia_rival_alto_baja_a_ambigua_con_las_dos():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.4})},
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.6}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.AMBIGUA, candidatas=(TAREA_TABLERO_3.id, TAREA_TABLERO_4.id))


def test_resolver_referencia_rival_justo_en_el_corte_baja_a_ambigua():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.4})},
        {"misma": {"noul": 0.8}, "rival": {"noul": jev.CORTE_RIVAL}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4, TAREA_HMI), vocabulario="")

    assert resultado.tipo is TipoResolucion.AMBIGUA


def test_resolver_referencia_rival_baja_probabilidad_igual_pide_y_puede_ambiguar_b0013():
    """Revisión del orquestador, 2026-09-24: b-0013 midió Jev devolviendo
    0,91 / 0,09 para las dos tareas del dashboard -- muy por debajo de
    `CORTE_CANDIDATA` (0,1) -- y con el corte de la primera versión de esta
    unidad, "rival" nunca se preguntaba y la referencia se resolvía sola.
    "Rival" se pide igual, sin importar cuán baja sea la probabilidad de la
    subcampeona, y si la respuesta es alta baja a ambigua con las dos."""
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.91, "T2": 0.09})},
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.6}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="cuál es el estado del dashboard", referencia="el dashboard",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.AMBIGUA, candidatas=(TAREA_TABLERO_3.id, TAREA_TABLERO_4.id))
    preguntas_verificacion = doble.pedidos[1][1]
    assert "rival" in preguntas_verificacion


def test_resolver_referencia_rival_baja_probabilidad_se_pide_y_puede_seguir_clara():
    """Misma forma que la prueba anterior (0,09 de subcampeona), pero con
    una respuesta de "rival" baja: se preguntó igual, y como la respuesta
    fue baja, sigue clara -- adapta lo que antes probaba el corte (T2 en
    0,05/0,09 ya no evita la pregunta; ahora hace falta scriptear la
    respuesta de "rival" para que la referencia siga clara)."""
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.05})},
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.1}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.CLARA, tarea_id=TAREA_TABLERO_3.id)
    preguntas_verificacion = doble.pedidos[1][1]
    assert "rival" in preguntas_verificacion
    assert preguntas_verificacion["rival"]["instructions"] == jev.INSTRUCCION_RIVAL
    state_verificacion = doble.pedidos[1][0]
    assert state_verificacion["tarea_elegida"] == TAREA_TABLERO_3.criterio()
    assert state_verificacion["otra_tarea"] == TAREA_TABLERO_4.criterio()


def test_resolver_referencia_una_sola_tarea_sigue_sin_pedir_rival():
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95), "tarea": _tarea({"T1": 0.9})},
        {"misma": {"noul": 0.75}},
    ])

    resultado = resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3,), vocabulario="")

    assert resultado == ResolucionReferencia(
        TipoResolucion.CLARA, tarea_id=TAREA_TABLERO_3.id)
    assert "rival" not in doble.pedidos[1][1]


@pytest.mark.parametrize("verificacion_mala", [
    pytest.param({"misma": {"noul": 0.8}}, id="falta-rival"),
    pytest.param({"misma": {"noul": 0.8}, "rival": {}}, id="rival-sin-noul"),
    pytest.param({"misma": {"noul": 0.8}, "rival": {"noul": "alta"}},
                 id="rival-no-numerico"),
    pytest.param({"misma": {"noul": 0.8}, "rival": "no-es-un-objeto"},
                 id="rival-no-es-dict"),
])
def test_resolver_referencia_rival_malformado_lanza_jeverror(verificacion_mala):
    doble = ClienteJevGuionado(guion=[
        {"alcance": _alcance(una_tarea=0.95),
         "tarea": _tarea({"T1": 0.9, "T2": 0.4})},
        verificacion_mala,
    ])

    with pytest.raises(JevError):
        resolver_referencia_tarea(
            doble, mensaje="m", referencia="r",
            tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")


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
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.1}},
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
        {"misma": {"noul": 0.8}, "rival": {"noul": 0.1}},
    ])

    resolver_referencia_tarea(
        doble, mensaje="pasala a revision", referencia="lo del tablero",
        tareas=(TAREA_TABLERO_3, TAREA_TABLERO_4), vocabulario="")

    assert "quien_escribe" not in doble.pedidos[0][0]
    assert "quien_escribe" not in doble.pedidos[1][0]
    for instruccion in (jev.INSTRUCCION_ALCANCE, jev.INSTRUCCION_TAREA,
                        jev.INSTRUCCION_VERIFICACION):
        assert "quien" not in instruccion.lower()


# ------------------------------------------- el objetivo más probable (F-B10)

OBJETIVOS = [("a", "Conectar equipos"), ("b", "Planos eléctricos"),
             ("c", "Servidores")]


def _probabilidades(**p):
    return {"objetivo": {"probabilities": p}}


def test_ordenar_objetivos_pone_primero_al_que_jev_elige_sin_duda():
    cliente = ClienteJevGuionado([_probabilidades(O1=0.05, O2=0.93, O3=0.02)])
    orden = jev.ordenar_objetivos(cliente, titulo="Calibrar los sensores",
                                  objetivos=OBJETIVOS, vocabulario="OT: oficina")
    assert orden.clara and orden.ids == ("b", "a", "c")
    state, preguntas = cliente.pedidos[0]
    assert state == {"tarea": "Calibrar los sensores",
                     "vocabulario_del_equipo": "OT: oficina"}
    assert preguntas["objetivo"]["criteria"] == {
        "O1": "Conectar equipos", "O2": "Planos eléctricos", "O3": "Servidores"}


def test_con_duda_no_se_destaca_ninguno_y_el_orden_es_el_de_llegada():
    cliente = ClienteJevGuionado([_probabilidades(O1=0.45, O2=0.45, O3=0.1)])
    orden = jev.ordenar_objetivos(cliente, titulo="x", objetivos=OBJETIVOS)
    assert not orden.clara and orden.ids == ("a", "b", "c")


def test_un_solo_objetivo_no_llama_a_jev():
    cliente = ClienteJevGuionado([])
    orden = jev.ordenar_objetivos(cliente, titulo="x", objetivos=OBJETIVOS[:1])
    assert orden.ids == ("a",) and not orden.clara and not cliente.pedidos


@pytest.mark.parametrize("respuesta", [{}, {"objetivo": {}},
                                       {"objetivo": {"probabilities": {}}},
                                       {"objetivo": {"probabilities": {"Z9": 0.9}}}])
def test_una_respuesta_sin_forma_es_un_error_de_jev(respuesta):
    with pytest.raises(JevError):
        jev.ordenar_objetivos(ClienteJevGuionado([respuesta]), titulo="x",
                              objetivos=OBJETIVOS)
