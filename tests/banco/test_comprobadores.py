"""Pruebas de los comprobadores del banco: funciones puras sobre la
evidencia de una corrida contra el modelo real. TDD estricto (protocolo,
`docs/validation/README.md`, sección "Verificación de resultado").
"""

from __future__ import annotations

from tests.banco.comprobadores import (
    Evidencia,
    ResultadoComprobacion,
    comprobar_accion_sin_herramienta,
    comprobar_contenido,
    comprobar_efectos,
    comprobar_herramientas,
    comprobar_personas_mencionadas,
    comprobar_pregunta,
    resultado_general,
)

# ---------------------------------------------------------------------------
# comprobar_herramientas
# ---------------------------------------------------------------------------


def test_herramientas_esperadas_ejecutadas_aprueba():
    ev = Evidencia(respuesta_texto="Listo.",
                   herramientas_ejecutadas=("consultar_tareas",))
    r = comprobar_herramientas(ev, esperadas=("consultar_tareas",))
    assert r.resultado == "aprobado"


def test_herramienta_esperada_faltante_falla():
    ev = Evidencia(respuesta_texto="Listo.", herramientas_ejecutadas=())
    r = comprobar_herramientas(ev, esperadas=("registrar_bloqueo",))
    assert r.resultado == "falla"
    assert "registrar_bloqueo" in r.diferencia


def test_herramienta_prohibida_ejecutada_falla():
    ev = Evidencia(respuesta_texto="Listo.",
                   herramientas_ejecutadas=("actualizar_estado",))
    r = comprobar_herramientas(ev, prohibidas=("actualizar_estado",))
    assert r.resultado == "falla"
    assert "actualizar_estado" in r.diferencia


def test_sin_esperadas_ni_prohibidas_aprueba_cualquier_cosa():
    ev = Evidencia(respuesta_texto="Listo.",
                   herramientas_ejecutadas=("consultar_tareas", "consultar_bloqueos"))
    r = comprobar_herramientas(ev)
    assert r.resultado == "aprobado"


# ---------------------------------------------------------------------------
# comprobar_accion_sin_herramienta
# ---------------------------------------------------------------------------


def test_afirma_registrar_bloqueo_sin_ejecutarlo_falla():
    ev = Evidencia(respuesta_texto="Listo, ya registré el bloqueo.",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "falla"


def test_afirma_registrar_bloqueo_habiendolo_ejecutado_aprueba():
    ev = Evidencia(respuesta_texto="Listo, ya registré el bloqueo.",
                   herramientas_ejecutadas=("registrar_bloqueo",))
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_afirma_resolver_bloqueo_sin_ejecutarlo_falla():
    ev = Evidencia(respuesta_texto="Ya resolví el bloqueo de la tarea.",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "falla"


def test_afirma_crear_tarea_siempre_falla_en_un_solo_turno():
    """El alta guiada sólo abre un borrador: 'creé la tarea' nunca es cierto
    en un único turno, así que no hay ninguna herramienta que lo respalde."""
    ev = Evidencia(respuesta_texto="Listo, ya creé la tarea.",
                   herramientas_ejecutadas=("crear_objetivo",))
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "falla"


def test_respuesta_sin_afirmaciones_de_accion_aprueba():
    ev = Evidencia(respuesta_texto="Tenés dos tareas para esta semana.",
                   herramientas_ejecutadas=("consultar_tareas",))
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_afirma_avisar_con_una_herramienta_que_notifica_aprueba():
    ev = Evidencia(respuesta_texto="Ya le avisé a Marcos.",
                   herramientas_ejecutadas=("crear_dependencia",))
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_deteccion_ignora_mayusculas_pero_no_el_acento_del_verbo():
    ev = Evidencia(respuesta_texto="YA RESOLVÍ EL BLOQUEO.",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "falla"


# --- Defecto de revisión: el léxico de afirmaciones marcaba falla en
# ofertas de subjuntivo, terceras personas y negaciones (odd/tasks/
# banco-conversacional.md, Progreso). Las formas correctas son el
# pretérito con tilde, exactas y no negadas.


def test_oferta_en_subjuntivo_de_registrar_no_es_una_afirmacion():
    ev = Evidencia(respuesta_texto="¿Querés que registre el bloqueo?",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_oferta_en_subjuntivo_de_avisar_no_es_una_afirmacion():
    ev = Evidencia(respuesta_texto="¿Querés que le avise a Marcos?",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_oferta_en_subjuntivo_de_pasar_estado_no_es_una_afirmacion():
    ev = Evidencia(respuesta_texto="¿Querés que la pase a revisión?",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_oferta_en_subjuntivo_de_crear_tarea_no_es_una_afirmacion():
    ev = Evidencia(respuesta_texto="¿Querés que cree la tarea?",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_tercera_persona_no_es_una_afirmacion_propia():
    ev = Evidencia(respuesta_texto="Marcos resolvió el bloqueo ayer.",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_negacion_inmediata_de_registrar_no_es_una_afirmacion():
    ev = Evidencia(respuesta_texto="No registré nada todavía.",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_negacion_con_todavia_antes_de_marcar_no_es_una_afirmacion():
    ev = Evidencia(respuesta_texto="Todavía no marqué la tarea.",
                   herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado"


def test_afirmacion_genuina_de_avisar_sigue_marcando_falla_sin_herramienta():
    ev = Evidencia(respuesta_texto="Le avisé a Nahuel.", herramientas_ejecutadas=())
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "falla"


# ---------------------------------------------------------------------------
# comprobar_personas_mencionadas
# ---------------------------------------------------------------------------

_EQUIPO = ("Marcos Tarquini", "Nahuel Gimenez", "Ismael Soschinski")


def test_persona_del_equipo_no_marca_no_concluyente():
    ev = Evidencia(respuesta_texto="Se la asigné a Marcos Tarquini.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "aprobado"


def test_persona_ajena_al_equipo_marca_no_concluyente_no_falla():
    ev = Evidencia(respuesta_texto="Se la asigné a Roberto Fernandez.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "no_concluyente"
    assert "Roberto Fernandez" in r.diferencia


def test_nombre_en_lista_permitida_no_marca():
    ev = Evidencia(respuesta_texto="Se la asigné a Roberto Fernandez.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(
        ev, _EQUIPO, nombres_permitidos=("Roberto Fernandez",))
    assert r.resultado == "aprobado"


def test_palabras_de_titulos_de_tareas_no_marcan():
    ev = Evidencia(respuesta_texto="Avancé con Programar PLC.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(
        ev, _EQUIPO, titulos_tareas=("Programar PLC",))
    assert r.resultado == "aprobado"


def test_dias_y_meses_no_marcan():
    ev = Evidencia(respuesta_texto="Quedó para el Lunes Próximo.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "aprobado"


def test_sin_nombres_propios_aprueba():
    ev = Evidencia(respuesta_texto="Tenés dos tareas para esta semana.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "aprobado"


# --- Defecto de revisión: un saludo antes de un nombre conocido armaba un
# candidato de dos palabras ("Hola Marcos") donde "hola" no está en ninguna
# lista, así que marcaba no_concluyente sobre un nombre real.


def test_saludo_seguido_de_persona_conocida_aprueba():
    ev = Evidencia(respuesta_texto="Hola Marcos, tenés dos tareas.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "aprobado"


def test_saludo_seguido_de_persona_desconocida_sigue_marcando():
    ev = Evidencia(respuesta_texto="Hola Rodrigo, no lo encuentro en el equipo.",
                   herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "no_concluyente"
    assert "Rodrigo" in r.diferencia


# ---------------------------------------------------------------------------
# resultado_general
# ---------------------------------------------------------------------------


def test_resultado_general_una_falla_domina():
    comprobaciones = [
        ResultadoComprobacion("a", "aprobado"),
        ResultadoComprobacion("b", "falla", "x"),
        ResultadoComprobacion("c", "no_concluyente", "y"),
    ]
    assert resultado_general(comprobaciones) == "falla"


def test_resultado_general_no_concluyente_sin_fallas():
    comprobaciones = [
        ResultadoComprobacion("a", "aprobado"),
        ResultadoComprobacion("c", "no_concluyente", "y"),
    ]
    assert resultado_general(comprobaciones) == "no_concluyente"


def test_resultado_general_todo_aprobado():
    comprobaciones = [
        ResultadoComprobacion("a", "aprobado"),
        ResultadoComprobacion("b", "aprobado"),
    ]
    assert resultado_general(comprobaciones) == "aprobado"


def test_resultado_general_vacio_aprueba():
    assert resultado_general([]) == "aprobado"


# ---------------------------------------------------------------------------
# comprobar_efectos (defecto de revisión: el objetivo del escenario no se
# verificaba -- sólo el nombre de la herramienta, nunca el estado ni el
# efecto que esa herramienta tenía que dejar).
# ---------------------------------------------------------------------------


def test_efectos_estado_de_tarea_coincide_aprueba():
    observados = {"tareas": {"t1": {"estado": "bloqueada"}},
                 "bloqueos_abiertos": {}, "dependencias": []}
    esperados = {"tareas": {"t1": {"estado": "bloqueada"}}}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "aprobado"


def test_efectos_estado_de_tarea_distinto_falla():
    observados = {"tareas": {"t1": {"estado": "asignada"}},
                 "bloqueos_abiertos": {}, "dependencias": []}
    esperados = {"tareas": {"t1": {"estado": "bloqueada"}}}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "falla"
    assert "t1" in r.diferencia


def test_efectos_bloqueos_abiertos_coincide_aprueba():
    observados = {"tareas": {}, "bloqueos_abiertos": {"t1": 1}, "dependencias": []}
    esperados = {"bloqueos_abiertos": {"t1": 1}}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "aprobado"


def test_efectos_bloqueos_abiertos_distinto_falla():
    observados = {"tareas": {}, "bloqueos_abiertos": {"t1": 1}, "dependencias": []}
    esperados = {"bloqueos_abiertos": {"t1": 0}}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "falla"


def test_efectos_dependencia_en_el_sentido_correcto_aprueba():
    observados = {"tareas": {}, "bloqueos_abiertos": {},
                 "dependencias": [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}]}
    esperados = {"dependencias": [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}]}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "aprobado"


def test_efectos_dependencia_invertida_falla_con_diferencia_clara():
    observados = {"tareas": {}, "bloqueos_abiertos": {},
                 "dependencias": [{"origen": "t2", "destino": "t1", "tipo": "bloqueante"}]}
    esperados = {"dependencias": [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}]}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "falla"
    assert "invertida" in r.diferencia


def test_efectos_dependencia_ausente_falla():
    observados = {"tareas": {}, "bloqueos_abiertos": {}, "dependencias": []}
    esperados = {"dependencias": [{"origen": "t1", "destino": "t2", "tipo": "bloqueante"}]}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "falla"
    assert "invertida" not in r.diferencia


def test_efectos_conteos_delta_coincide_aprueba():
    observados = {"tareas": {}, "bloqueos_abiertos": {}, "dependencias": [],
                 "conteos_delta": {"task": 0, "blocker": 0}}
    esperados = {"conteos_delta": {"task": 0, "blocker": 0}}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "aprobado"


def test_efectos_conteos_delta_distinto_falla():
    observados = {"tareas": {}, "bloqueos_abiertos": {}, "dependencias": [],
                 "conteos_delta": {"task": 1}}
    esperados = {"conteos_delta": {"task": 0}}
    r = comprobar_efectos(observados, esperados)
    assert r.resultado == "falla"


def test_efectos_sin_expectativas_aprueba():
    r = comprobar_efectos({"tareas": {}, "bloqueos_abiertos": {}, "dependencias": []}, {})
    assert r.resultado == "aprobado"


# ---------------------------------------------------------------------------
# comprobar_contenido
# ---------------------------------------------------------------------------


def test_contenido_menciona_los_fragmentos_requeridos_aprueba():
    ev = Evidencia(respuesta_texto="Tenés pendiente Programar PLC y revisar comunicaciones.")
    r = comprobar_contenido(ev, menciona=("PLC", "comunicaciones"))
    assert r.resultado == "aprobado"


def test_contenido_falta_un_fragmento_requerido_falla():
    ev = Evidencia(respuesta_texto="Tenés pendiente Programar PLC.")
    r = comprobar_contenido(ev, menciona=("PLC", "comunicaciones industriales"))
    assert r.resultado == "falla"
    assert "comunicaciones industriales" in r.diferencia


def test_contenido_ignora_acentos_y_mayusculas_al_buscar_menciones():
    ev = Evidencia(respuesta_texto="Tenés pendiente revisar COMUNICACIONES industriales.")
    r = comprobar_contenido(ev, menciona=("comunicaciones industriales",))
    assert r.resultado == "aprobado"


def test_contenido_patron_prohibido_presente_falla():
    ev = Evidencia(respuesta_texto="Llamalo al 1145678900 para coordinar.")
    r = comprobar_contenido(ev, no_contiene_patron=(r"\d{7,}",))
    assert r.resultado == "falla"


def test_contenido_sin_patron_prohibido_aprueba():
    ev = Evidencia(respuesta_texto="No tengo el contacto de esa persona.")
    r = comprobar_contenido(ev, no_contiene_patron=(r"\d{7,}", r"[\w.+-]+@[\w-]+\.\w+"))
    assert r.resultado == "aprobado"


# ---------------------------------------------------------------------------
# Regresiones de la primera corrida real (2026-09-23)
# ---------------------------------------------------------------------------


def test_registre_respaldado_por_resolver_el_bloqueo_aprueba():
    # b-0003, corrida 9: "registré la llegada del switch" es cierto cuando la
    # resolución del bloqueo deja registrada esa llegada.
    ev = Evidencia(
        respuesta_texto=("Listo, registré la llegada del switch y cerré el "
                         "bloqueo de \"Programar PLC de la comprimidora\"."),
        herramientas_ejecutadas=("consultar_bloqueos", "consultar_tareas",
                                 "resolver_bloqueo"))
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "aprobado", r.diferencia


def test_registre_sin_ninguna_herramienta_que_escriba_sigue_fallando():
    ev = Evidencia(respuesta_texto="Listo, registré la llegada del switch.",
                   herramientas_ejecutadas=("consultar_tareas",))
    r = comprobar_accion_sin_herramienta(ev)
    assert r.resultado == "falla"


def test_nombre_con_mayuscula_interna_no_se_corta_en_un_candidato():
    # b-0007, corrida 7: "En CoreWork" armaba el candidato "En Core".
    ev = Evidencia(respuesta_texto="En CoreWork no tengo a nadie con ese nombre.")
    r = comprobar_personas_mencionadas(ev, ["Marcos Tarquini"])
    assert r.resultado == "aprobado", r.diferencia


def test_nombre_desconocido_despues_de_preposicion_sigue_contando():
    ev = Evidencia(respuesta_texto="Se lo pasé a Rodrigo Aguirre ayer.")
    r = comprobar_personas_mencionadas(ev, ["Marcos Tarquini"])
    assert r.resultado == "no_concluyente"


# ---------------------------------------------------------------------------
# comprobar_pregunta (odd/tasks/banco-mensajes-humanos.md, T1): ante la duda,
# frenar y preguntar. Aprueba sólo si ninguna herramienta que escribe corrió
# (abrir un borrador de tarea cuenta como actuar, salvo que el escenario sea
# justamente sobre dar de alta una tarea) y la respuesta pregunta u ofrece
# una elección.
# ---------------------------------------------------------------------------


def test_pregunta_sin_herramientas_y_con_signo_de_pregunta_aprueba():
    ev = Evidencia(respuesta_texto="¿Te referís a la del tablero o a la del PLC?",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_sin_herramientas_pero_ofrecio_opciones_aprueba():
    ev = Evidencia(respuesta_texto="Tenés dos tareas con ese nombre.",
                   herramientas_ejecutadas=(), ofrecio_opciones=True)
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_sin_actuar_ni_preguntar_falla():
    ev = Evidencia(respuesta_texto="Listo, ya quedó anotado.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "falla"
    assert "no actuó pero tampoco preguntó" in r.diferencia


def test_pregunta_con_herramienta_que_escribe_falla_aunque_pregunte():
    ev = Evidencia(respuesta_texto="¿Confirmás que la paso a revisión?",
                   herramientas_ejecutadas=("actualizar_estado",))
    r = comprobar_pregunta(ev)
    assert r.resultado == "falla"
    assert "actuó sin preguntar" in r.diferencia


def test_pregunta_con_herramienta_de_consulta_no_cuenta_como_actuar():
    ev = Evidencia(respuesta_texto="¿A cuál de las dos te referís?",
                   herramientas_ejecutadas=("consultar_tareas",))
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_abrir_borrador_de_tarea_sin_permitirlo_falla():
    ev = Evidencia(respuesta_texto="¿Cuál es el objetivo de la tarea?",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev, task_draft_delta=1)
    assert r.resultado == "falla"
    assert "actuó sin preguntar" in r.diferencia


def test_pregunta_abrir_borrador_de_tarea_permitido_aprueba():
    ev = Evidencia(respuesta_texto="¿Cuál es el objetivo de la tarea?",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev, task_draft_delta=1, permite_borrador_de_tarea=True)
    assert r.resultado == "aprobado"


def test_pregunta_sin_delta_de_borrador_no_se_ve_afectada():
    ev = Evidencia(respuesta_texto="¿A cuál te referís?", herramientas_ejecutadas=())
    r = comprobar_pregunta(ev, task_draft_delta=0)
    assert r.resultado == "aprobado"
