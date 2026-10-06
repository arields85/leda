> **INVÁLIDA como medición (2026-10-06):** OpenRouter se quedó sin crédito y rechazó llamadas con HTTP 402 Payment Required desde el arranque de la ronda (21:25 del 2026-10-05; las 59 corridas afectadas). Se guarda como evidencia del corte.

# Transcripciones de la ronda ronda2-sonnet

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea "Programar PLC de la comprimidora" vence el viernes 23/10, dentro de 3 días hábiles. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5486 ms
- Leda → Marcos: «Listo, Marcos: anoté que arrancaste hoy "Programar PLC de la comprimidora" y quedó en curso. No necesito nada más por ahora.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 01 · Arranqué · vez 2

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 792 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso'}], real []

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 01 · Arranqué · vez 3

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 764 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso'}], real []

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 01 · Arranqué · vez 4

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 872 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso'}], real []

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 767 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso'}], real []

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 02 · Llego el 27, el proveedor se demoró · vez 1

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 782 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []

**Paso 3.** Leda (2026-10-20 15:41)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}, real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}}, 'pide_el_estado_el': {'fecha': '2026-10-27', 'estado': 'todavia_no'}}}, real []
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, Programar PLC de la comprimidora vencía el 23 y lleva 1 día hábil de atraso. Está en curso, y Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

Vi tu mensaje del 20 sobre la demora del proveedor y el 27, pero eso no cambió la fecha de la tarea. ¿Cómo viene: ya la terminaste, para qué fecha la tendrías o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 6.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- (Leda no manda nada)
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}, {'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 02 · Llego el 27, el proveedor se demoró · vez 2

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 787 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []

**Paso 3.** Leda (2026-10-20 15:41)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}, real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}}, 'pide_el_estado_el': {'fecha': '2026-10-27', 'estado': 'todavia_no'}}}, real []
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Marcos, Programar PLC de la comprimidora venció el 23/10 y lleva 2 días hábiles de atraso. Me habías contado que llegaba el 27, porque el proveedor se demoró. Como hoy es 27, te consulto cómo está.

Te aviso que Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine esta tarea, y vence el 30/10, dentro de 3 días hábiles.

¿Cómo vi»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- (Leda no manda nada)
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 02 · Llego el 27, el proveedor se demoró · vez 3

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea "Programar PLC de la comprimidora" vence el viernes 23/10, dentro de 3 días hábiles. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 743 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []

**Paso 3.** Leda (2026-10-20 15:41)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}, real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}}, 'pide_el_estado_el': {'fecha': '2026-10-27', 'estado': 'todavia_no'}}}, real []
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, la tarea "Programar PLC de la comprimidora" venció el viernes 23/10 y lleva 1 día hábil de atraso. Además, "Revisar comunicaciones industriales de la comprimidora" no puede arrancar hasta que ésta termine.

Vi tu mensaje del 20 sobre el 27, pero esa fecha no quedó registrada. ¿Cómo viene la tarea: ya la terminaste, para cuándo la darías por terminada o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 6.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- (Leda no manda nada)
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}, {'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 764 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []

**Paso 3.** Leda (2026-10-20 15:41)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}, real []

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora, que figura en curso. De ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que esta termine.

Sobre lo que escribiste el martes, que llega el 27, necesito confirmarlo con vos. ¿La terminaste, para qué fecha la tenés o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}}, 'pide_el_estado_el': {'fecha': '2026-10-27', 'estado': 'todavia_no'}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}
- **falla** [motor] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- (Leda no manda nada)
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}, {'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 02 · Llego el 27, el proveedor se demoró · vez 5

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 758 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []

**Paso 3.** Leda (2026-10-20 15:41)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM'], 'motivo': 'presente'}}, real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}}, 'pide_el_estado_el': {'fecha': '2026-10-27', 'estado': 'todavia_no'}}}, real []
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, Programar PLC de la comprimidora tenía vencimiento el 23/10 y lleva 1 día hábil de atraso. Figura en curso, y Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que esta termine.

Me contaste que»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 6.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- (Leda no manda nada)
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}, {'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea "Programar PLC de la comprimidora" vence el viernes 23/10, en 3 días hábiles. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 758 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta el repuesto'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] esperas abiertas después: esperado ['PLC'], real []

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 4.** Leda (2026-10-21 10:00)
- (Leda no manda nada)
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta', 'tarea': 'PLC', 'hechos': {'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'sobre': {'jugada': 'anotar_bloqueo', 'causa': 'presente'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 757 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'no_sabe': True, 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 748 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 2

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 792 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta el repuesto'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] esperas abiertas después: esperado ['PLC'], real []

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 4.** Leda (2026-10-21 10:00)
- (Leda no manda nada)
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta', 'tarea': 'PLC', 'hechos': {'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'sobre': {'jugada': 'anotar_bloqueo', 'causa': 'presente'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 763 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'no_sabe': True, 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 756 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 3

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 761 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta el repuesto'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] esperas abiertas después: esperado ['PLC'], real []

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 4.** Leda (2026-10-21 10:00)
- (Leda no manda nada)
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta', 'tarea': 'PLC', 'hechos': {'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'sobre': {'jugada': 'anotar_bloqueo', 'causa': 'presente'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 749 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'no_sabe': True, 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 756 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 4

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 819 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta el repuesto'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] esperas abiertas después: esperado ['PLC'], real []

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 4.** Leda (2026-10-21 10:00)
- (Leda no manda nada)
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta', 'tarea': 'PLC', 'hechos': {'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'sobre': {'jugada': 'anotar_bloqueo', 'causa': 'presente'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 820 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'no_sabe': True, 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 813 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 5

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 763 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta el repuesto'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] esperas abiertas después: esperado ['PLC'], real []

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 4.** Leda (2026-10-21 10:00)
- (Leda no manda nada)
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta', 'tarea': 'PLC', 'hechos': {'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'sobre': {'jugada': 'anotar_bloqueo', 'causa': 'presente'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 836 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'no_sabe': True, 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 763 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 3.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'atraso_dias_habiles': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'vence': '2026-10-27', 'atraso_dias_habiles': 3, 'pedido_desde': '2026-10-27', 'pedidos_de_estado_sin_respuesta': 3, 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

## 04 · No contesta · vez 2

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 3.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'atraso_dias_habiles': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'vence': '2026-10-27', 'atraso_dias_habiles': 3, 'pedido_desde': '2026-10-27', 'pedidos_de_estado_sin_respuesta': 3, 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

## 04 · No contesta · vez 3

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 3.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'atraso_dias_habiles': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'vence': '2026-10-27', 'atraso_dias_habiles': 3, 'pedido_desde': '2026-10-27', 'pedidos_de_estado_sin_respuesta': 3, 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

## 04 · No contesta · vez 4

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 3.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'atraso_dias_habiles': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'vence': '2026-10-27', 'atraso_dias_habiles': 3, 'pedido_desde': '2026-10-27', 'pedidos_de_estado_sin_respuesta': 3, 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

## 04 · No contesta · vez 5

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 3.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'atraso_dias_habiles': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, te escribo por "Programar PLC de la comprimidora": venció el 27/10 y lleva 2 días hábiles de atraso. Figura en curso. Además, "Revisar comunicaciones industriales de la comprimidora" no puede arrancar hasta que ésta termine.

¿Cómo viene? ¿La terminaste, para cuándo la tendrías o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'vence': '2026-10-27', 'atraso_dias_habiles': 3, 'pedido_desde': '2026-10-27', 'pedidos_de_estado_sin_respuesta': 3, 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []

## 05 · Varias cosas en un mensaje · vez 1

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 757 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:06)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 793 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[]`
- hechos: `[]`
- latencia: 763 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'alguien': True, 'no_sabe': False}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real []

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 759 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:06)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 741 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[]`
- hechos: `[]`
- latencia: 756 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'alguien': True, 'no_sabe': False}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real []

## 05 · Varias cosas en un mensaje · vez 3

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 823 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:06)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 815 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[]`
- hechos: `[]`
- latencia: 809 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'alguien': True, 'no_sabe': False}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real []

## 05 · Varias cosas en un mensaje · vez 4

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 771 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:06)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 757 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[]`
- hechos: `[]`
- latencia: 762 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'alguien': True, 'no_sabe': False}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real []

## 05 · Varias cosas en un mensaje · vez 5

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 780 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:06)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 790 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[]`
- hechos: `[]`
- latencia: 779 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'alguien': True, 'no_sabe': False}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real []

## 06 · No, era la otra tarea · vez 1

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea "Programar PLC de la comprimidora" vence el viernes 23/10, dentro de 3 días hábiles. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 784 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 790 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'asignada', 'atraso_dias_habiles': 0}}, real []

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 856 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 871 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'asignada', 'atraso_dias_habiles': 0}}, real []

## 06 · No, era la otra tarea · vez 3

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea "Programar PLC de la comprimidora" vence el viernes 23/10, dentro de 3 días hábiles. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 826 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 843 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'asignada', 'atraso_dias_habiles': 0}}, real []

## 06 · No, era la otra tarea · vez 4

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 753 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 752 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'asignada', 'atraso_dias_habiles': 0}}, real []

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 811 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 848 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real []

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'asignada', 'atraso_dias_habiles': 0}}, real []

## 07 · Dejá, no importa · vez 1

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 783 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[]`
- hechos: `[]`
- latencia: 792 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real []

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 785 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[]`
- hechos: `[]`
- latencia: 747 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real []

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 07 · Dejá, no importa · vez 3

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 753 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[]`
- hechos: `[]`
- latencia: 778 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real []

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 767 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[]`
- hechos: `[]`
- latencia: 765 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real []

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 07 · Dejá, no importa · vez 5

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[]`
- hechos: `[]`
- latencia: 817 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[]`
- hechos: `[]`
- latencia: 833 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real []

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 08 · Cambio de tema · vez 1

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 900 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 766 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 4.** Leda (2026-10-20 10:44)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}, real []

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[]`
- hechos: `[]`
- latencia: 759 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

## 08 · Cambio de tema · vez 2

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 788 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 776 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 4.** Leda (2026-10-20 10:44)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}, real []

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[]`
- hechos: `[]`
- latencia: 822 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

## 08 · Cambio de tema · vez 3

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 797 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 852 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 4.** Leda (2026-10-20 10:44)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}, real []

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[]`
- hechos: `[]`
- latencia: 768 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

## 08 · Cambio de tema · vez 4

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 785 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 781 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 4.** Leda (2026-10-20 10:44)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}, real []

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[]`
- hechos: `[]`
- latencia: 773 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

## 08 · Cambio de tema · vez 5

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 802 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 803 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real None

**Paso 4.** Leda (2026-10-20 10:44)
- (Leda no manda nada)
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'motivo': 'ausente'}}, real []

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[]`
- hechos: `[]`
- latencia: 836 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

## 09 · Duda: ¿de qué tarea habla? · vez 1

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1079 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

## 09 · Duda: ¿de qué tarea habla? · vez 2

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 906 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

## 09 · Duda: ¿de qué tarea habla? · vez 3

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 913 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

## 09 · Duda: ¿de qué tarea habla? · vez 4

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 839 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

## 09 · Duda: ¿de qué tarea habla? · vez 5

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 944 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

## 10 · Escribir en lugar de tocar un botón · vez 1

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 838 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 762 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 847 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 767 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 841 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 771 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 4

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 831 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 789 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 784 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 774 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 740 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1056 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 789 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real []
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido'}, real []

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido', 'motivo': 'presente'}, real []

## 11 · Algo vencido · vez 2

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1045 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 774 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 775 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real []
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido'}, real []

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido', 'motivo': 'presente'}, real []

## 11 · Algo vencido · vez 3

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 762 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1393 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 802 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real []
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido'}, real []

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido', 'motivo': 'presente'}, real []

## 11 · Algo vencido · vez 4

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 756 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 774 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 770 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real []
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido'}, real []

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido', 'motivo': 'presente'}, real []

## 11 · Algo vencido · vez 5

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] COM»
- jugadas: `[]`
- hechos: `[]`
- (Leda no manda nada)
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones
- **falla** [comprension] no hay un botón para tocar: esperado 'COM', real None

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 762 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 792 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 768 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real []
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido'}, real []

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30
- **falla** [motor] aviso en el estado: esperado {'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'omitido', 'motivo': 'presente'}, real []

## 12 · Algo que no está en la lista · vez 1

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[]`
- hechos: `[]`
- latencia: 812 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[]`
- hechos: `[]`
- latencia: 815 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 842 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)
- **falla** [comprension] jugadas: esperado [{'nombre': 'fuera_de_la_lista', 'que_pide': 'que le recuerde el viernes un turno con el médico'}], real []
- **falla** [comprension] falta el aviso al administrador: esperado 1, real 0
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'resultado': 'fuera_de_la_lista', 'lo_que_puede_hacer': 'presente'}], real []

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 846 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 815 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'entregar', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'PLC'}], real []

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 846 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 2

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[]`
- hechos: `[]`
- latencia: 773 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[]`
- hechos: `[]`
- latencia: 762 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 786 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)
- **falla** [comprension] jugadas: esperado [{'nombre': 'fuera_de_la_lista', 'que_pide': 'que le recuerde el viernes un turno con el médico'}], real []
- **falla** [comprension] falta el aviso al administrador: esperado 1, real 0
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'resultado': 'fuera_de_la_lista', 'lo_que_puede_hacer': 'presente'}], real []

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 780 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 772 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'entregar', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'PLC'}], real []

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 772 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 3

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[]`
- hechos: `[]`
- latencia: 792 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[]`
- hechos: `[]`
- latencia: 772 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 790 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)
- **falla** [comprension] jugadas: esperado [{'nombre': 'fuera_de_la_lista', 'que_pide': 'que le recuerde el viernes un turno con el médico'}], real []
- **falla** [comprension] falta el aviso al administrador: esperado 1, real 0
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'resultado': 'fuera_de_la_lista', 'lo_que_puede_hacer': 'presente'}], real []

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 767 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 761 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'entregar', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'PLC'}], real []

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 771 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/anthropic/claude-sonnet-5.5`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC', 'COM']}, real []
- **falla** [motor] último aviso de Marcos: esperado ['COM', 'PLC'], real None

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 762 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 749 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

