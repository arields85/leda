"""Pruebas de los comprobadores del banco: funciones puras sobre la
evidencia de una corrida contra el modelo real. TDD estricto (protocolo,
`docs/validation/README.md`, sección "Verificación de resultado").
"""

from __future__ import annotations

from tests.banco.comprobadores import (
    Evidencia,
    ResultadoComprobacion,
    comprobaciones_pregunta_con_opciones,
    comprobar_accion_sin_herramienta,
    comprobar_aclaracion,
    comprobar_contenido,
    comprobar_efectos,
    comprobar_herramientas,
    comprobar_personas_mencionadas,
    comprobar_pregunta,
    comprobar_pregunta_con_opciones,
    comprobar_sin_efectos_antes_de_confirmar,
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


# --- Defecto de revisión (Experimento 3, `odd/tasks/prisma-orienta.md`,
# hallazgo lateral de b-0002/b-0003): "Bloqueada Todavía" y "Asignada
# Todavía" marcaban no_concluyente -- una palabra de estado
# (`herramientas.ESTADOS_LEGIBLES`) seguida de "Todavía" al empezar la
# línea siguiente, ninguna de las dos en ninguna lista conocida, aunque
# ninguna sea un nombre de persona.


def test_estado_bloqueada_seguido_de_todavia_no_marca():
    ev = Evidencia(
        respuesta_texto="Estado: Bloqueada\nTodavía no llegó el plano.",
        herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "aprobado"


def test_estado_asignada_seguido_de_todavia_no_marca():
    ev = Evidencia(
        respuesta_texto="Estado: Asignada\nTodavía nadie la tomó.",
        herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "aprobado"


def test_estado_seguido_de_nombre_desconocido_sigue_marcando():
    """La palabra de estado es vocabulario conocido, pero no vuelve
    invisible a la palabra que sigue: si es un nombre real desconocido,
    sigue marcando -- la corrección no debilita la detección real."""
    ev = Evidencia(
        respuesta_texto="Estado: Bloqueada\nRodrigo Aguirre la destrabó.",
        herramientas_ejecutadas=())
    r = comprobar_personas_mencionadas(ev, _EQUIPO)
    assert r.resultado == "no_concluyente"
    assert "Rodrigo Aguirre" in r.diferencia


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
# comprobar_sin_efectos_antes_de_confirmar (T4, ADR 0005 decisión 1):
# propiedad central -- ninguna de las 8 herramientas que escriben cambia la
# base antes de tocar Confirmar. `corrida.py` arma los tres conteos que hacen
# falta -- `conteos_antes` (antes de mandar cualquier mensaje),
# `conteos_antes_del_toque` (justo después del turno, antes de simular el
# toque; `None` si no hubo propuesta) y `conteos_despues` (al final de toda
# la corrida) -- y la lista de herramientas de las 8 que ya habían dejado su
# entrada en `audit_log` antes de cualquier toque posible.
#
# Dos huecos encontrados en la revisión del orquestador (T4, 2026-09-24):
# 1. Sin propuesta, la corrida aprobaba sin más -- justo el caso que hay que
#    atrapar: una de las 8 ejecutándose directo, sin ningún Confirmar de por
#    medio. Sin toque, la comparación tiene que ser `conteos_antes` contra
#    `conteos_despues` (todo lo que la corrida haya escrito).
# 2. Un conteo por tabla no ve un UPDATE (`resolver_bloqueo` marca
#    `resuelto_en` sobre una fila que ya existía; `actualizar_estado` puede
#    cambiar `estado` sin insertar ninguna fila nueva). La señal primaria es
#    `audit_log`: sólo lleva una entrada `herramienta:<nombre>` cuando la
#    herramienta se ejecutó de verdad (nunca al levantar
#    `NecesitaConfirmacion`) -- reusa `_HERRAMIENTAS_QUE_ESCRIBEN`, el mismo
#    conjunto de las 8 que ya usa `comprobar_accion_sin_herramienta`.
# ---------------------------------------------------------------------------


def test_sin_efectos_antes_de_confirmar_sin_propuesta_y_sin_cambios_aprueba():
    # `conteos_antes_del_toque=None`: la corrida no dejó ninguna propuesta
    # con botón Confirmar. Sin cambios entre antes y después, no hay nada
    # que comprobar.
    conteos = {"task": 1, "blocker": 0, "objective": 2}
    r = comprobar_sin_efectos_antes_de_confirmar(conteos, None, dict(conteos))
    assert r.resultado == "aprobado"


def test_sin_efectos_antes_de_confirmar_sin_propuesta_pero_con_cambio_en_despues_falla():
    # Hueco 1: sin ninguna propuesta de por medio, una tabla de las 8 cambió
    # igual -- una herramienta se ejecutó sin que nadie tocara Confirmar.
    antes = {"task": 1, "blocker": 0}
    despues = {"task": 2, "blocker": 0}
    r = comprobar_sin_efectos_antes_de_confirmar(antes, None, despues)
    assert r.resultado == "falla"
    assert "task" in r.diferencia


def test_sin_efectos_antes_de_confirmar_con_propuesta_y_sin_cambios_aprueba():
    conteos = {"task": 1, "blocker": 0, "objective": 2}
    r = comprobar_sin_efectos_antes_de_confirmar(
        conteos, dict(conteos), {"task": 99})  # despues no se usa: hubo toque
    assert r.resultado == "aprobado"


def test_sin_efectos_antes_de_confirmar_con_cambio_en_task_antes_del_toque_falla():
    antes = {"task": 1, "blocker": 0}
    antes_del_toque = {"task": 2, "blocker": 0}
    r = comprobar_sin_efectos_antes_de_confirmar(antes, antes_del_toque, antes_del_toque)
    assert r.resultado == "falla"
    assert "task" in r.diferencia


def test_sin_efectos_antes_de_confirmar_con_cambio_en_objective_antes_del_toque_falla():
    # crear_objetivo escribe en 'objective'; que aparezca antes del toque es
    # justo lo que esta propiedad tiene que atrapar.
    antes = {"objective": 3}
    antes_del_toque = {"objective": 4}
    r = comprobar_sin_efectos_antes_de_confirmar(antes, antes_del_toque, antes_del_toque)
    assert r.resultado == "falla"
    assert "objective" in r.diferencia


def test_sin_efectos_antes_de_confirmar_ignora_message_outbox():
    # La vista previa sale por la cola: un mensaje nuevo antes del toque es
    # esperado, no un efecto de las 8 herramientas.
    antes = {"task": 1, "message_outbox": 5}
    antes_del_toque = {"task": 1, "message_outbox": 6}
    r = comprobar_sin_efectos_antes_de_confirmar(antes, antes_del_toque, antes_del_toque)
    assert r.resultado == "aprobado"


def test_sin_efectos_antes_de_confirmar_ignora_task_draft():
    # Abrir un borrador guiado de tarea no es un efecto de las 8 herramientas.
    antes = {"task": 1, "task_draft": 0}
    antes_del_toque = {"task": 1, "task_draft": 1}
    r = comprobar_sin_efectos_antes_de_confirmar(antes, antes_del_toque, antes_del_toque)
    assert r.resultado == "aprobado"


def test_sin_efectos_antes_de_confirmar_herramienta_ejecutada_antes_del_toque_falla():
    # Hueco 2: 'resolver_bloqueo' marca `resuelto_en` sobre una fila que ya
    # existía -- un conteo por tabla no lo ve, pero `audit_log` sí: ya dejó
    # su entrada 'herramienta:resolver_bloqueo' antes de cualquier toque.
    conteos = {"task": 1, "blocker": 1}
    r = comprobar_sin_efectos_antes_de_confirmar(
        conteos, conteos, conteos, herramientas_antes_del_toque=("resolver_bloqueo",))
    assert r.resultado == "falla"
    assert "resolver_bloqueo" in r.diferencia


def test_sin_efectos_antes_de_confirmar_ignora_herramientas_de_consulta_antes_del_toque():
    conteos = {"task": 1}
    r = comprobar_sin_efectos_antes_de_confirmar(
        conteos, conteos, conteos, herramientas_antes_del_toque=("consultar_tareas",))
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


# ---------------------------------------------------------------------------
# comprobar_pregunta -- pedido de elección en imperativo, sin "?" (T7, punto
# I): b-0011 ("Decime cuál de las dos y lo hago") y b-0012 ("decime cuál doy
# por resuelto") frenaban y pedían la elección sin signo de pregunta ni
# botones, y el comprobador los marcaba como que no preguntaron.
# ---------------------------------------------------------------------------


def test_pregunta_imperativo_decime_cual_sin_signo_de_pregunta_aprueba():
    ev = Evidencia(respuesta_texto="Decime cuál de las dos y lo hago",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_imperativo_decime_cual_minuscula_y_sin_acento_aprueba():
    ev = Evidencia(respuesta_texto="decime cual doy por resuelto",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_imperativo_confirmame_cual_aprueba():
    ev = Evidencia(respuesta_texto="Confirmame cuál es antes de tocarla.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_imperativo_elegi_sin_cual_aprueba():
    ev = Evidencia(respuesta_texto="Elegí una de las dos, por favor.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_imperativo_contame_cual_aprueba():
    ev = Evidencia(respuesta_texto="Contame cuál te sirve más.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_imperativo_decime_sin_cual_no_es_pedido_de_eleccion():
    """Negativo (pedido explícito de I): un imperativo con "decime" que no
    pide elegir entre candidatas -- una frase de cierre común al final de
    una acción ya hecha -- no puede convertir una acción en pregunta ni
    debilitar "actuó sin preguntar"."""
    ev = Evidencia(respuesta_texto="Listo, ya quedó anotado. Decime si necesitás algo más.",
                   herramientas_ejecutadas=("actualizar_estado",))
    r = comprobar_pregunta(ev)
    assert r.resultado == "falla"
    assert "actuó sin preguntar" in r.diferencia


def test_pregunta_imperativo_decime_sin_cual_y_sin_actuar_sigue_fallando():
    """Mismo texto que la negativa anterior pero sin ninguna herramienta
    ejecutada: tampoco alcanza, porque "decime si necesitás algo más" no
    pide elegir una candidata -- es una frase de cierre genérica."""
    ev = Evidencia(respuesta_texto="Decime si necesitás algo más.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "falla"
    assert "no actuó pero tampoco preguntó" in r.diferencia


def test_pregunta_imperativo_con_herramienta_que_escribe_sigue_fallando():
    """El imperativo nunca puede pesar más que "actuó sin preguntar": aunque
    la respuesta sí pida elegir, si además corrió una herramienta que
    escribe, sigue siendo una falla -- mismo criterio que ya vale para "?"."""
    ev = Evidencia(respuesta_texto="Decime cuál de las dos y lo hago",
                   herramientas_ejecutadas=("actualizar_estado",))
    r = comprobar_pregunta(ev)
    assert r.resultado == "falla"
    assert "actuó sin preguntar" in r.diferencia


# ---------------------------------------------------------------------------
# comprobar_pregunta -- "decime qué"/"contame qué" (T7, punto N): b-0010
# ("Contame qué la está frenando") y b-0011 ("decime qué preferís y lo
# muevo") pedían la elección con "qué" en vez de "cuál", sin signo de
# pregunta, y el comprobador tampoco los reconocía.
# ---------------------------------------------------------------------------


def test_pregunta_imperativo_contame_que_la_esta_frenando_aprueba():
    ev = Evidencia(respuesta_texto="Contame qué la está frenando.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_imperativo_decime_que_preferis_aprueba():
    ev = Evidencia(respuesta_texto="decime qué preferís y lo muevo",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "aprobado"


def test_pregunta_imperativo_decime_sin_cual_ni_que_no_es_pedido_de_eleccion():
    """Negativo que pide el encargo (kept): sigue sin alcanzar."""
    ev = Evidencia(respuesta_texto="Decime si necesitás algo más.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "falla"
    assert "no actuó pero tampoco preguntó" in r.diferencia


def test_pregunta_imperativo_porque_no_es_un_falso_positivo_de_que():
    """Negativo propio: "porque"/"aunque" contienen "que" como subcadena --
    el marcador de N busca la palabra "que" con borde de palabra, no
    cualquier subcadena, para no confundir un "porque" de cierre con un
    pedido real de elegir."""
    ev = Evidencia(
        respuesta_texto="Decime si hace falta algo, porque ya avisé a todos.",
        herramientas_ejecutadas=())
    r = comprobar_pregunta(ev)
    assert r.resultado == "falla"
    assert "no actuó pero tampoco preguntó" in r.diferencia


# ---------------------------------------------------------------------------
# comprobar_pregunta_con_opciones (T4, `prisma-orienta`, ADR 0007 puntos 1 y
# 5): a diferencia de `comprobar_pregunta` -- que sólo corre si el escenario
# declaró `debe_preguntar: true`, y aprueba tanto una pregunta con botones
# como una en texto abierto -- ésta corre por defecto en todo escenario y es
# estricta sobre la FORMA: si Prisma pregunta, tiene que ofrecer botones.
# Reusa `_hace_pregunta` (misma detección que `comprobar_pregunta`): "?" o el
# pedido de elección en imperativo (T7).
# ---------------------------------------------------------------------------


def test_pregunta_con_opciones_signo_de_pregunta_sin_botones_falla():
    ev = Evidencia(respuesta_texto="¿Cuál de las dos tareas es?",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta_con_opciones(ev)
    assert r.resultado == "falla"
    assert "ADR 0007" in r.diferencia


def test_pregunta_con_opciones_signo_de_pregunta_con_botones_aprueba():
    ev = Evidencia(respuesta_texto="¿Cuál de las dos tareas es?",
                   herramientas_ejecutadas=(), ofrecio_opciones=True)
    r = comprobar_pregunta_con_opciones(ev)
    assert r.resultado == "aprobado"


def test_pregunta_con_opciones_imperativo_sin_botones_falla():
    """El mismo pedido en imperativo que `comprobar_pregunta` ya reconoce
    como pregunta (T7, "Decime cuál de las dos y lo hago") -- sin botones,
    ADR 0007 lo prohíbe igual que un "?" abierto."""
    ev = Evidencia(respuesta_texto="Decime cuál de las dos y lo hago",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta_con_opciones(ev)
    assert r.resultado == "falla"


def test_pregunta_con_opciones_imperativo_con_botones_aprueba():
    ev = Evidencia(respuesta_texto="Decime cuál de las dos y lo hago",
                   herramientas_ejecutadas=(), ofrecio_opciones=True)
    r = comprobar_pregunta_con_opciones(ev)
    assert r.resultado == "aprobado"


def test_pregunta_con_opciones_aviso_que_no_pregunta_nada_aprueba_sin_botones():
    """ADR 0007, punto pendiente ('si una respuesta puede cerrar sin
    opciones'): un aviso que no le pregunta nada a la persona no tiene por
    qué llevar botones -- esta comprobación no se mete con eso, sólo exige
    botones cuando SÍ pregunta."""
    ev = Evidencia(respuesta_texto="Listo, quedó registrado.",
                   herramientas_ejecutadas=())
    r = comprobar_pregunta_con_opciones(ev)
    assert r.resultado == "aprobado"


def test_pregunta_con_opciones_lista_de_tareas_sin_pregunta_ni_botones_aprueba():
    """Una respuesta que sólo presenta información (p. ej. un conteo de
    tareas) sin preguntar nada tampoco depende de `ofrecio_opciones` acá --
    aunque T3 igual le agregue botones por servidor, esta comprobación en sí
    no lo exige salvo que el texto pregunte algo."""
    ev = Evidencia(respuesta_texto="Tenés 2 tareas pendientes.",
                   herramientas_ejecutadas=("consultar_tareas",))
    r = comprobar_pregunta_con_opciones(ev)
    assert r.resultado == "aprobado"


def test_pregunta_con_opciones_no_le_importa_si_actuo():
    """A diferencia de `comprobar_pregunta`, esta comprobación no mira
    `herramientas_ejecutadas` en absoluto -- sólo la FORMA de la pregunta.
    Una respuesta que actuó y además pregunta algo más en texto abierto,
    sin botones, sigue fallando acá (otra comprobación, `comprobar_pregunta`
    con `debe_preguntar`, es la que juzga si actuar estuvo bien)."""
    ev = Evidencia(respuesta_texto="Ya la pasé a revisión. ¿Querés que avise a alguien más?",
                   herramientas_ejecutadas=("actualizar_estado",))
    r = comprobar_pregunta_con_opciones(ev)
    assert r.resultado == "falla"


# ---------------------------------------------------------------------------
# comprobaciones_pregunta_con_opciones (T4, `prisma-orienta`, ADR 0007): la
# puerta de opt-out en un sólo lugar, revisión del orquestador 2026-09-26 --
# `test_banco.py` y `test_replays.py` la llaman igual; acá se prueba la
# puerta sola, de punta a punta contra los dos valores del campo se prueba
# en `test_replays.py` (con una corrida real de `ejecutar_escenario`).
# ---------------------------------------------------------------------------


def test_comprobaciones_pregunta_con_opciones_activa_por_defecto_devuelve_la_comprobacion():
    ev = Evidencia(respuesta_texto="¿Cuál de las dos tareas es?",
                   herramientas_ejecutadas=())
    comprobaciones = comprobaciones_pregunta_con_opciones(
        ev, permite_pregunta_sin_opciones=False)
    assert [c.nombre for c in comprobaciones] == ["pregunta_con_opciones"]
    assert comprobaciones[0].resultado == "falla"


def test_comprobaciones_pregunta_con_opciones_desactivada_no_agrega_nada():
    ev = Evidencia(respuesta_texto="¿Cuál de las dos tareas es?",
                   herramientas_ejecutadas=())
    comprobaciones = comprobaciones_pregunta_con_opciones(
        ev, permite_pregunta_sin_opciones=True)
    assert comprobaciones == []


# ---------------------------------------------------------------------------
# comprobar_aclaracion (T6, `aclaracion-con-botones`): la aclaración con
# botones ofreció las candidatas que el escenario espera -- lo que
# `corrida.ejecutar_escenario` necesitaba para poder tocar la elegida.
# ---------------------------------------------------------------------------


def test_aclaracion_ofrece_todas_las_candidatas_esperadas_aprueba():
    r = comprobar_aclaracion(
        ("Cablear tablero máq. 3", "Revisar tablero máq. 4", "Ninguna, lo escribo"),
        candidatas_esperadas=("Cablear tablero máq. 3", "Revisar tablero máq. 4"))
    assert r.resultado == "aprobado"


def test_aclaracion_sin_ofrecer_ninguna_candidata_falla():
    r = comprobar_aclaracion((), candidatas_esperadas=("Cablear tablero máq. 3",))
    assert r.resultado == "falla"
    assert "Cablear tablero máq. 3" in r.diferencia


def test_aclaracion_falta_una_candidata_esperada_falla():
    r = comprobar_aclaracion(
        ("Cablear tablero máq. 3", "Ninguna, lo escribo"),
        candidatas_esperadas=("Cablear tablero máq. 3", "Revisar tablero máq. 4"))
    assert r.resultado == "falla"
    assert "Revisar tablero máq. 4" in r.diferencia
    assert "Cablear tablero máq. 3" not in r.diferencia.split("ofrecidas")[0]


def test_aclaracion_con_candidatas_de_mas_no_le_importa():
    """Botones de más (otra candidata que Jev sumó, o el propio 'Es una
    tarea nueva') no son un problema: lo único que se exige es que las
    esperadas estén, no que sean las únicas."""
    r = comprobar_aclaracion(
        ("Cablear tablero máq. 3", "Revisar tablero máq. 4",
         "Es una tarea nueva", "Ninguna, lo escribo"),
        candidatas_esperadas=("Cablear tablero máq. 3",))
    assert r.resultado == "aprobado"


# --- Defecto de revisión (Experimento 3, `odd/tasks/prisma-orienta.md`,
# hallazgo lateral de b-0013): el comprobador comparaba la etiqueta entera
# contra el título entero, y `e7071eb`/`2bee9a9` empezaron a acortar las
# etiquetas de botón con "…" (`salida.acortar_etiqueta_boton`) -- toda
# aclaración con un título largo quedaba `falla` aunque el botón ofrecido
# fuera exactamente el que el título produce al acortarse.


def test_aclaracion_acepta_la_etiqueta_acortada_del_titulo_largo():
    from prisma.salida import acortar_etiqueta_boton

    titulo = "Actualizar el dashboard de HMI (simulado)"
    etiqueta = acortar_etiqueta_boton(titulo)
    assert etiqueta.endswith("…")   # confirma la premisa: el título se acortó
    r = comprobar_aclaracion((etiqueta,), candidatas_esperadas=(titulo,))
    assert r.resultado == "aprobado"


def test_aclaracion_acepta_la_etiqueta_acortada_con_sufijo_de_responsable():
    """`gateway._etiqueta_boton` agrega " — <nombre>" después de acortar,
    para una tarea ajena -- el sufijo nunca se recorta."""
    from prisma.salida import acortar_etiqueta_boton

    titulo = "Actualizar el dashboard de HMI (simulado)"
    etiqueta = f"{acortar_etiqueta_boton(titulo)} — Marcos"
    r = comprobar_aclaracion((etiqueta,), candidatas_esperadas=(titulo,))
    assert r.resultado == "aprobado"


def test_aclaracion_no_acepta_un_prefijo_de_otra_tarea_que_no_coincide_letra_por_letra():
    """No basta con que las primeras letras se parezcan: el prefijo antes de
    "…" tiene que ser, letra por letra, un prefijo real del título -- una
    tarea distinta con otro título no cuela sólo por empezar parecido."""
    r = comprobar_aclaracion(
        ("Actualizar el dashboard de otra…",),
        candidatas_esperadas=("Actualizar el dashboard de HMI (simulado)",))
    assert r.resultado == "falla"


def test_aclaracion_no_acepta_un_corte_a_mitad_de_palabra():
    """Defecto de revisión (T6k, seguimiento a review-2c5b0ffe): la prueba
    anterior con este nombre decía cubrir "el límite de palabra", pero su
    prefijo ("...de otra") ni siquiera coincidía letra por letra con el
    título -- `titulo.startswith(prefijo)` ya daba `False` y la función
    volvía antes de llegar a `corte_de_palabra`/`corte_duro`. Acá el prefijo
    SÍ es letra por letra un prefijo real del título ("dashboa" de
    "dashboard"), pero corta a mitad de esa palabra: ni cae en un límite de
    palabra (el carácter siguiente no es un espacio) ni alcanza el corte
    duro (mucho más corto que `TRUNCAR_ETIQUETA_BOTON`), así que de verdad
    ejercita esa rama y sigue sin aceptarse."""
    r = comprobar_aclaracion(
        ("Actualizar el dashboa…",),
        candidatas_esperadas=("Actualizar el dashboard de HMI (simulado)",))
    assert r.resultado == "falla"


def test_aclaracion_no_acepta_la_etiqueta_de_una_tarea_distinta():
    """La forma acortada de la tarea EQUIVOCADA sigue sin contar para la
    esperada, aunque las dos empiecen distinto."""
    from prisma.salida import acortar_etiqueta_boton

    esperada = "Actualizar el dashboard de HMI (simulado)"
    otra = "Revisar gráficos del dashboard HMI (simulado)"
    r = comprobar_aclaracion(
        (acortar_etiqueta_boton(otra),), candidatas_esperadas=(esperada,))
    assert r.resultado == "falla"
    assert esperada in r.diferencia


# ---------------------------------------------------------------------------
# comprobar_aclaracion -- emparejamiento uno a uno (T6k, seguimiento a
# review-2c5b0ffe): la versión anterior preguntaba, por cada candidata
# esperada, si ALGUNA etiqueta ofrecida la satisfacía, sin llevar cuenta de
# cuáles etiquetas ya estaban "gastadas" -- una sola etiqueta acortada que es
# forma ofrecida válida de dos títulos con el mismo prefijo contaba como
# oferta para las dos y daba un falso "aprobado" con un solo botón real.
# ---------------------------------------------------------------------------


def test_aclaracion_una_etiqueta_no_alcanza_para_dos_candidatas_con_prefijo_comun():
    """"Actualizar el dashboard…" es forma ofrecida válida tanto de
    "Actualizar el dashboard" (coincide entera antes del corte) como de
    "Actualizar el dashboard de HMI" (corta justo en un límite de palabra) --
    pero sólo hay UN botón, así que sólo puede cubrir una de las dos."""
    r = comprobar_aclaracion(
        ("Actualizar el dashboard…",),
        candidatas_esperadas=("Actualizar el dashboard",
                              "Actualizar el dashboard de HMI"))
    assert r.resultado == "falla"


def test_aclaracion_cada_candidata_con_su_propia_etiqueta_aprueba():
    """Mismas dos candidatas que la prueba anterior, pero con un botón
    propio para cada una: el emparejamiento uno a uno no le exige de más a
    un caso sin ambigüedad."""
    r = comprobar_aclaracion(
        ("Actualizar el dashboard", "Actualizar el dashboard de HMI"),
        candidatas_esperadas=("Actualizar el dashboard",
                              "Actualizar el dashboard de HMI"))
    assert r.resultado == "aprobado"


# ---------------------------------------------------------------------------
# Una respuesta visible por mensaje entrante (T9-R2, ADR 0013 regla 2)
# ---------------------------------------------------------------------------

import pytest  # noqa: E402


def test_una_respuesta_por_entrada_aprueba_con_un_grupo_por_mensaje():
    from tests.banco.comprobadores import comprobar_una_respuesta_por_entrada

    r = comprobar_una_respuesta_por_entrada((1, 1, 1))
    assert (r.nombre, r.resultado) == ("una_respuesta_por_entrada", "aprobado")


def test_una_respuesta_por_entrada_sin_mensajes_aprueba():
    from tests.banco.comprobadores import comprobar_una_respuesta_por_entrada

    assert comprobar_una_respuesta_por_entrada(()).resultado == "aprobado"


@pytest.mark.parametrize("conteos, dice", [
    ((1, 0), "ninguna respuesta"), ((2,), "2 respuestas"), ((1, 3), "3 respuestas")])
def test_una_respuesta_por_entrada_falla_con_cero_o_mas_de_una(conteos, dice):
    from tests.banco.comprobadores import comprobar_una_respuesta_por_entrada

    r = comprobar_una_respuesta_por_entrada(conteos)
    assert r.resultado == "falla" and dice in r.diferencia


def test_una_respuesta_por_entrada_falla_si_el_control_estructural_tuvo_que_actuar():
    from tests.banco.comprobadores import comprobar_una_respuesta_por_entrada

    # El control dejó una sola respuesta, pero un camino no la respetó: el
    # incidente es la evidencia.
    r = comprobar_una_respuesta_por_entrada(
        (1,), incidentes=("Un mensaje quedó sin ninguna respuesta.",))
    assert r.resultado == "falla" and "control estructural" in r.diferencia


@pytest.mark.parametrize("por_toque, dice", [
    ((0,), "el toque 1 no recibió ninguna respuesta"),
    ((1, 2), "el toque 2 recibió 2 respuestas")])
def test_una_respuesta_por_toque_falla_con_cero_o_mas_de_una(por_toque, dice):
    """T9-R4: la regla 2 se extiende a los toques que se procesaron (uno absorbido
    por repetido no se cuenta: no es una respuesta que falte)."""
    from tests.banco.comprobadores import comprobar_una_respuesta_por_entrada

    r = comprobar_una_respuesta_por_entrada((1,), respuestas_por_toque=por_toque)
    assert r.resultado == "falla" and dice in r.diferencia


def test_una_respuesta_por_toque_aprueba_con_un_grupo_por_toque():
    from tests.banco.comprobadores import comprobar_una_respuesta_por_entrada

    assert comprobar_una_respuesta_por_entrada(
        (1,), respuestas_por_toque=(1, 1)).resultado == "aprobado"


# --- T10-1 (R3-H4/b-0013): el botón real lleva un ícono de categoría delante
# (`salida.con_icono`); es una marca visual, no parte del título. El
# comprobador tiene que compararlo sin él, igual que el toque simulado
# (`salida.etiquetas_coinciden`).


def test_aclaracion_acepta_la_etiqueta_con_icono_del_titulo_entero():
    from prisma.salida import ICONO_TAREA, con_icono

    titulo = "Dashboard de lotes en CoreLabs"
    r = comprobar_aclaracion(
        (con_icono(titulo, ICONO_TAREA),), candidatas_esperadas=(titulo,))
    assert r.resultado == "aprobado"


def test_aclaracion_acepta_la_etiqueta_con_icono_acortada_y_con_sufijo():
    from prisma.salida import ICONO_TAREA, acortar_etiqueta_boton, con_icono

    titulo = "Actualizar el dashboard de HMI (simulado)"
    acortada = acortar_etiqueta_boton(titulo)
    assert acortada.endswith("…")
    etiqueta = con_icono(f"{acortada} — Jev", ICONO_TAREA)
    r = comprobar_aclaracion((etiqueta,), candidatas_esperadas=(titulo,))
    assert r.resultado == "aprobado"


def test_aclaracion_con_icono_sigue_fallando_si_el_titulo_es_otro():
    from prisma.salida import ICONO_TAREA, con_icono

    r = comprobar_aclaracion(
        (con_icono("Revisar tablero máq. 4", ICONO_TAREA),),
        candidatas_esperadas=("Cablear tablero máq. 3",))
    assert r.resultado == "falla"
