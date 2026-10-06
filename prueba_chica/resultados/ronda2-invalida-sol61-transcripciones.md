> **INVÁLIDA como medición (2026-10-06):** OpenRouter se quedó sin crédito y rechazó llamadas con HTTP 402 Payment Required desde el arranque de la ronda (21:22 del 2026-10-05; 75 de 85 corridas afectadas). Se guarda como evidencia del corte.

# Transcripciones de la ronda ronda2-sol61

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 495 ms
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

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 388 ms
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence mañana, 23 de octubre. Falta 1 día hábil. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 1}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 1}}

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y todavía figura sin empezar, aunque me habías contado que ya estabas en eso. ¿La terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}

## 01 · Arranqué · vez 3

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 465 ms
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-21) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de 2 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 2}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 2}}

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue como asignada. ¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}

## 01 · Arranqué · vez 4

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 403 ms
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y todavía figura como asignada. Me habías contado que ya arrancaste: ¿la terminaste, tenés una fecha para terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 386 ms
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

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 388 ms
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me habías dicho que llegabas el 27 por la demora del proveedor. ¿Seguís con esa previsión o cambió la situación?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 1 día hábil de atraso: vencía el 23/10. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me habías dicho que llegabas el 27 por la demora del proveedor. ¿La terminaste, mantenés esa previsión o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: vencía el 23/10. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines y vence el 30/10, en 3 días hábiles.

Este es el tercer pedido de estado. Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

Me habías dicho que llegabas hoy por la demora del proveedor. ¿La terminaste, tenés una nueva fecha o estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}]}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}]}

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-28) → Ismael: «Ismael, Marcos Tarquini no respondió los 3 pedidos de estado de “Programar PLC de la comprimidora” desde el 23/10. La tarea sigue en curso y lleva 3 días hábiles de atraso; vencía el 23/10.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esa tarea.

Este aviso no necesita respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-23", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy y figura asignada, todavía sin empezar.

¿La terminaste, para cuándo la podés tener o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real [{'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-23', 'necesita_respuesta': False, 'atraso_dias_habiles': 3, 'pedidos_de_estado_sin_respuesta': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-23', 'necesita_respuesta': False, 'atraso_dias_habiles': 3, 'pedidos_de_estado_sin_respuesta': 3}}

## 02 · Llego el 27, el proveedor se demoró · vez 2

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 387 ms
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: venció el 23/10.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termines esa tarea y vence el 30/10, en 3 días hábiles.

¿Cómo viene “Programar PLC de la comprimidora”: la terminaste, tenés una fecha para terminarla o está trabada?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso: venció el 23/10 y lleva 3 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Te vuelvo a consultar: ¿la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso: venció el 23/10 y lleva 4 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Este es el tercer pedido de estado. Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Cómo viene “Programar PLC de la comprimidora”: la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}, {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}, {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}

## 02 · Llego el 27, el proveedor se demoró · vez 3

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no necesitás responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 410 ms
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me habías dicho que llegabas el 27 por la demora del proveedor. ¿Seguís con esa previsión o cambió el estado de la tarea?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Vuelvo a consultarte por “Programar PLC de la comprimidora”: sigue en curso y lleva 1 día hábil de atraso desde su vencimiento del 23 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me habías dicho que llegabas el 27 por la demora del proveedor. ¿La terminaste, mantenés esa previsión o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Es el tercer pedido de estado de “Programar PLC de la comprimidora”: sigue en curso y lleva 2 días hábiles de atraso desde el 23 de octubre.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines y vence el 30 de octubre, en 3 días hábiles. Ese recordatorio no necesita respuesta.

Si no respondés sobre la programación del PLC, se le avisará a Ismael Soschinski; todavía no se le avisó.

Me habías dicho que llegabas hoy por la demora del proveedor. ¿La terminaste, tenés otra fecha de finalización o estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}]}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}]}

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-28) → Ismael: «Marcos Tarquini no respondió los 3 pedidos de estado de “Programar PLC de la comprimidora” desde el 23/10. La tarea sigue en curso, venció ese día y lleva 3 días hábiles de atraso.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

Este aviso no necesita respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-23", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy y figura asignada, todavía sin empezar.

¿La terminaste, tenés una fecha de finalización o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real [{'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-23', 'necesita_respuesta': False, 'atraso_dias_habiles': 3, 'pedidos_de_estado_sin_respuesta': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-23', 'necesita_respuesta': False, 'atraso_dias_habiles': 3, 'pedidos_de_estado_sin_respuesta': 3}}

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, en 3 días hábiles. Es solo un recordatorio; no necesitás responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[]`
- hechos: `[]`
- latencia: 413 ms
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
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 4 días hábiles de atraso respecto del 23/10. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 4, "pedidos_anteriores_que_no_le_llegaron": 1}`
- Leda, por su cuenta (pedido_de_estado COM, PLC, 2026-10-30) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 5 días hábiles de atraso respecto del 23/10. “Revisar comunicaciones industriales de la comprimidora” vence hoy, sigue sin empezar y no puede arrancar hasta que termines la programación.

Si no recibo respuesta, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Cómo viene “Programar PLC de la comprimidora”: ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `[{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 5, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}, "pedidos_anteriores_que_no_le_llegaron": 1}]`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'pedidos_anteriores_que_no_le_llegaron': 1}}, {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['COM', 'PLC'], 'el': '2026-10-30', 'hechos': [{'aviso': 'pedido_de_estado', 'tarea': 'COM', 'vence': '2026-10-30', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 5, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}, 'pedidos_anteriores_que_no_le_llegaron': 1}]}]
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'pedidos_anteriores_que_no_le_llegaron': 1}}, {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['COM', 'PLC'], 'el': '2026-10-30', 'hechos': [{'aviso': 'pedido_de_estado', 'tarea': 'COM', 'vence': '2026-10-30', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 5, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}, 'pedidos_anteriores_que_no_le_llegaron': 1}]}]
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'pedidos_anteriores_que_no_le_llegaron': 1}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['COM', 'PLC'], 'el': '2026-10-30', 'hechos': [{'aviso': 'pedido_de_estado', 'tarea': 'COM', 'vence': '2026-10-30', 'estado': 'asignada', 'numero': 1, 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 5, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}, 'pedidos_anteriores_que_no_le_llegaron': 1}]}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 02 · Llego el 27, el proveedor se demoró · vez 5

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 392 ms
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: la terminaste, tenés una fecha de finalización o está trabada?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 1 día hábil de atraso: venció el 23/10. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, tenés una fecha de finalización o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: venció el 23/10. Es el tercer pedido de estado; si no respondés, se le avisará a Ismael Soschinski. Ese aviso todavía no se envió.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines y vence el 30/10, en 3 días hábiles.

¿Cómo viene “Programar PLC de la comprimidora”: ya la terminaste, para cuándo la terminás o está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}]}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}]}

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-28) → Ismael: «Marcos Tarquini no respondió los 3 pedidos de estado de “Programar PLC de la comprimidora” desde el 23/10. La tarea sigue en curso, venció el 23/10 y lleva 3 días hábiles de atraso.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esa programación.

Este aviso no requiere respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-23", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy y figura asignada, todavía sin empezar.

¿Cómo viene: ya la terminaste, para cuándo la terminás o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski'], 'estado': 'todavia_no'}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real [{'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-23', 'necesita_respuesta': False, 'atraso_dias_habiles': 3, 'pedidos_de_estado_sin_respuesta': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-23', 'necesita_respuesta': False, 'atraso_dias_habiles': 3, 'pedidos_de_estado_sin_respuesta': 3}}

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 385 ms
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, en 3 días hábiles. Este recordatorio no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-20', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}
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
- latencia: 387 ms
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
- latencia: 385 ms
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

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4764 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está trabada porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarlo? Podés decirme un nombre, que no sabés o que me toca a mí.»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 413 ms
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
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 381 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada porque falta el repuesto. Me dijiste que no sabés quién lo está comprando y que hay que esperar a que llegue.

Si no recibo respuesta, se le avisará a Ismael Soschinski. ¿Hay alguien que pueda destrabarlo o me toca a mí?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento_de_una_pregunta PLC, 2026-10-26) → Ismael: «Marcos Tarquini tiene bloqueada la tarea “Programar PLC de la comprimidora” porque falta el repuesto. Desde el 20/10 le pregunté tres veces quién puede destrabarla, sin respuesta. Te aviso para que estés al tanto; no necesitás responder.»
  - hechos: `{"aviso": "falta_de_respuesta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}`
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence el 30/10, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'falta el repuesto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento_de_una_pregunta', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'falta_de_respuesta', 'sobre': {'causa': 'falta el repuesto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'pregunta': 'quien_destraba', 'responsable': 'Marcos Tarquini', 'preguntado_el': '2026-10-20', 'necesita_respuesta': False, 'preguntas_sin_respuesta': 3}}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 3

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 436 ms
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
- latencia: 533 ms
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
- latencia: 402 ms
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

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G FALLA · C FALLA · M FALLA.

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
- latencia: 381 ms
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, en 3 días hábiles. Este aviso no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-20', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}
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
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "no_se_puede", "motivo": "sin_bloqueo_abierto", "tarea": "PLC"}]`
- latencia: 9551 ms
- Leda → Marcos: «No pude anotar quién puede destrabar “Programar PLC de la comprimidora” porque la tarea no tiene un bloqueo abierto. Si seguís trabado por el repuesto, podés decírmelo.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'no_se_puede', 'motivo': 'sin_bloqueo_abierto', 'tarea': 'PLC'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "hay que esperar que llegue nomas"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "hay que esperar que llegue nomas", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 9995 ms
- Leda → Marcos: «Quedó anotado el bloqueo de “Programar PLC de la comprimidora”: hay que esperar que llegue el repuesto. Aunque no sepas quién lo está comprando, ¿sabés de alguien que pueda destrabar esa espera?»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'hay que esperar que llegue nomas'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'hay que esperar que llegue nomas', 'resuelto': False}]
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada a la espera del repuesto. Me dijiste que no sabés quién lo está comprando: ¿hay alguien que pueda ayudar a destrabar esa espera?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "hay que esperar que llegue nomas", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- Leda, por su cuenta (repregunta PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada a la espera del repuesto. Si no recibo respuesta, se le avisará a Ismael Soschinski.

¿Sabés quién puede destrabar esa espera? Podés decirme un nombre, que no sabés o que te toca a vos.»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "hay que esperar que llegue nomas", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'hay que esperar que llegue nomas', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'hay que esperar que llegue nomas', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 5

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «“Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5176 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está trabada porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarlo? Podés decirme un nombre, que no sabés o que te toca a vos.»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 5145 ms
- Leda → Marcos: «Quedó anotado que no sabés quién puede destrabar “Programar PLC de la comprimidora”. ¿Preferís que alguien del equipo ayude con el bloqueo o anotar para cuándo prevés terminarla y por qué? Podés elegir una opción o escribirla.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 4678 ms
- Leda → Marcos: «Entendido, dejé sin efecto la propuesta de ayuda o de anotar una previsión para “Programar PLC de la comprimidora”. No quedó nada nuevo anotado. No hace falta que respondas.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence el 30 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, para cuándo estimás terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 1 día hábil de atraso: venció el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, para cuándo estimás terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: venció el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Cómo viene: ya la terminaste, para cuándo estimás terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos Tarquini no respondió los tres pedidos de estado de “Programar PLC de la comprimidora” desde el 27/10. La tarea sigue en curso y lleva 3 días hábiles de atraso respecto de esa fecha comprometida.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

Este aviso no requiere respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 2

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 27 de octubre, dentro de 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 1 día hábil de atraso: venció el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: venció el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Este es el tercer pedido de estado. Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Cómo viene: la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos Tarquini no respondió los tres pedidos de estado de “Programar PLC de la comprimidora” desde el 27/10. La tarea sigue en curso y lleva 3 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

Te lo aviso para que estés al tanto; no necesitás responder.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 3

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «“Programar PLC de la comprimidora” vence el 27/10, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 1 día hábil de atraso: venció el 27/10. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: venció el 27/10. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

Este es el tercer pedido de estado. Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos Tarquini no respondió los 3 pedidos de estado de “Programar PLC de la comprimidora” desde el 27/10. La tarea sigue en curso y lleva 3 días hábiles de atraso.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esa tarea.

Este aviso no necesita respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 4

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, tenés una fecha de finalización o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 1 día hábil de atraso: venció el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, tenés una fecha de finalización o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: venció el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Este es el tercer pedido de estado. Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Cómo viene: ya la terminaste, tenés una fecha de finalización o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos Tarquini no respondió los tres pedidos de estado de “Programar PLC de la comprimidora” desde el 27/10. La tarea sigue en curso y lleva 3 días hábiles de atraso.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esa programación.

Este aviso no requiere respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 5

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura en curso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” venció ayer, 27 de octubre, y sigue en curso, con 1 día hábil de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Este es el tercer pedido de estado de “Programar PLC de la comprimidora”: sigue en curso y lleva 2 días hábiles de atraso desde su vencimiento el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos Tarquini no respondió los tres pedidos de estado de “Programar PLC de la comprimidora” desde el 27/10. La tarea sigue en curso y lleva 3 días hábiles de atraso.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esa programación.

Este aviso no requiere respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 05 · Varias cosas en un mensaje · vez 1

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, en 3 días hábiles. Es un recordatorio; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 386 ms
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
- latencia: 402 ms
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
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 7055 ms
- Leda → Marcos: «Quedó anotado el bloqueo de “Programar PLC de la comprimidora”: falta que Martín de IT te habilite el acceso a la red de planta. ¿Confirmás que Martín es quien puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}]
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'alguien': True, 'no_sabe': False}], real []
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 810 ms
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
- latencia: 893 ms
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
- latencia: 785 ms
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

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 770 ms
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
- latencia: 784 ms
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
- latencia: 781 ms
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

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 796 ms
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
- latencia: 783 ms
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
- latencia: 741 ms
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

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 772 ms
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
- latencia: 768 ms
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
- latencia: 764 ms
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

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 930 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}, {"nombre": "informar_avance", "tarea": "PLC", "palabras": "la del plc todavia no la empece"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}, {"jugada": "informar_avance", "resultado": "no_se_puede", "motivo": "nadie_pidio_el_estado", "tarea": "PLC"}]`
- latencia: 13304 ms
- Leda → Marcos: «Quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”.

Lo de “Programar PLC de la comprimidora” no quedó registrado como avance porque no te había pedido su estado. No hace falta que respondas.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real [{'nombre': 'anotar_inicio', 'tarea': 'COM'}, {'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'la del plc todavia no la empece'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {'COM': 'en_curso'}
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM', 'estado': 'en_curso'}, {'jugada': 'informar_avance', 'resultado': 'no_se_puede', 'motivo': 'nadie_pidio_el_estado', 'tarea': 'PLC'}]

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura como pendiente de inicio. ¿Cómo viene: la terminaste, para cuándo estimás terminarla o estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 772 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 765 ms
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

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 829 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 797 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real []

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura como pendiente de inicio. ¿Cómo viene: la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 4

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 779 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 7119 ms
- Leda → Marcos: «Quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”. No hace falta que respondas nada más.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real [{'nombre': 'anotar_inicio', 'tarea': 'COM'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {'COM': 'en_curso'}
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM', 'estado': 'en_curso'}]

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura sin empezar. ¿Cómo viene: la terminaste, para cuándo la tendrías o estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[]`
- hechos: `[]`
- latencia: 770 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 772 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error
- **falla** [comprension] jugadas: esperado [{'nombre': 'corregir', 'corrige': 'anotar_inicio', 'tarea': 'PLC', 'tarea_correcta': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'asignada', 'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'corregir', 'resultado': 'corregido', 'tarea': 'PLC', 'vuelve_a': {'estado': 'asignada'}, 'aplicado': {'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}}], real []

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue pendiente de inicio. ¿La terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 07 · Dejá, no importa · vez 1

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5543 ms
- Leda → Marcos: «Me falta saber la causa para anotar el bloqueo. ¿Qué te está trabando en “Programar PLC de la comprimidora”?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4934 ms
- Leda → Marcos: «Dejamos sin efecto la pregunta sobre qué te trababa en “Programar PLC de la comprimidora”. No quedó nada anotado. No hace falta que respondas.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. ¿La terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «“Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no necesitás responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5253 ms
- Leda → Marcos: «Para anotar el bloqueo de “Programar PLC de la comprimidora”, me falta la causa. ¿Qué te está trabando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4559 ms
- Leda → Marcos: «Dejamos sin efecto la pregunta sobre qué te traba en “Programar PLC de la comprimidora”. No quedó nada anotado y no necesitás responder.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. ¿La terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 3

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4988 ms
- Leda → Marcos: «Para anotar el bloqueo en “Programar PLC de la comprimidora”, me falta saber la causa. ¿Qué te está trabando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 6008 ms
- Leda → Marcos: «Dejamos sin efecto la pregunta sobre qué te traba en “Programar PLC de la comprimidora”. No quedó nada anotado y no hace falta que respondas.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura en curso. ¿La terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5186 ms
- Leda → Marcos: «Me falta saber la causa para anotar el bloqueo. ¿Qué te está trabando en “Programar PLC de la comprimidora”?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5073 ms
- Leda → Marcos: «Dejamos sin efecto la pregunta sobre qué te traba en “Programar PLC de la comprimidora”. No quedó nada anotado y no hace falta que respondas.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 07 · Dejá, no importa · vez 5

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5548 ms
- Leda → Marcos: «Para anotar el bloqueo en “Programar PLC de la comprimidora”, me falta la causa. ¿Qué te está trabando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[]`
- hechos: `[]`
- latencia: 3167 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 08 · Cambio de tema · vez 1

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5191 ms
- Leda → Marcos: «Me falta el motivo para anotar el bloqueo de Programar PLC de la comprimidora. ¿Qué te está trabando?»
- [ ] dice: una pregunta por la causa

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 837 ms
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
- latencia: 833 ms
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
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}

## 08 · Cambio de tema · vez 2

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 815 ms
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
- latencia: 774 ms
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
- latencia: 791 ms
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

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, dentro de 3 días hábiles. Es solo un recordatorio, no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 831 ms
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
- latencia: 777 ms
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
- latencia: 793 ms
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

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 769 ms
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
- latencia: 760 ms
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
- latencia: 761 ms
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

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 780 ms
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
- latencia: 791 ms
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
- latencia: 890 ms
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

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 892 ms
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

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 899 ms
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

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 840 ms
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

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1101 ms
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

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 815 ms
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

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 815 ms
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
- latencia: 764 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 835 ms
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
- latencia: 784 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1069 ms
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
- latencia: 829 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 4

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 884 ms
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
- latencia: 776 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 881 ms
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
- latencia: 907 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Me falta saber cuál tarea arrancaste para anotarlo. ¿Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”; está en curso. No hace falta que respondas nada más.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[]`
- latencia: 780 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [motor] hechos: esperado [{'jugada': 'elegir', 'resultado': 'sin_efecto', 'motivo': 'pregunta_cerrada', 'cerrada_con': {'tarea': 'PLC'}}], real []

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 814 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 755 ms
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

## 11 · Algo vencido · vez 2

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 902 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 864 ms
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
- latencia: 841 ms
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

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G FALLA · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Me falta saber cuál para anotar el inicio. ¿Arrancaste “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» [botones: PLC, COM]

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}}]`
- latencia: 2295 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Revisar comunicaciones industriales de la comprimidora”: está en curso. No hace falta que respondas nada más.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'en_curso'}
- **falla** [motor] hechos: esperado [{'jugada': 'elegir', 'resultado': 'sin_efecto', 'motivo': 'pregunta_cerrada', 'cerrada_con': {'tarea': 'PLC'}}], real [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM', 'estado': 'en_curso', 'eligio': {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}}]

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 822 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 764 ms
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
- latencia: 756 ms
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

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Me falta saber cuál tarea arrancaste para anotarlo. ¿Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribir el título.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora; está en curso. No hace falta que respondas nada más.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 2469 ms
- Leda → Marcos: «Esa pregunta ya se había cerrado ayer con tu respuesta: Programar PLC de la comprimidora. Elegir ahora Revisar comunicaciones industriales de la comprimidora no cambió nada. No hace falta que respondas nada más.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 763 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 762 ms
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
- latencia: 758 ms
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

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G FALLA · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «No hay opciones abiertas para elegir. Podés decirme el título completo de la tarea que arrancaste.»

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
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5835 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora” y está en curso. No hace falta que respondas nada más.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]
- **falla** [garantia] efecto de más: estado: esperado {'COM': 'en_curso'}, real {'PLC': 'en_curso'}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso'}]

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 777 ms
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
- latencia: 754 ms
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

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[]`
- hechos: `[]`
- latencia: 803 ms
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
- latencia: 742 ms
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
- latencia: 752 ms
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
- latencia: 798 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 819 ms
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
- latencia: 791 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 2

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 786 ms
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
- latencia: 839 ms
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
- latencia: 771 ms
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
- latencia: 762 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 788 ms
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
- latencia: 767 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 3

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[]`
- hechos: `[]`
- latencia: 794 ms
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
- latencia: 771 ms
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
- latencia: 774 ms
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
- latencia: 772 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 735 ms
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
- latencia: 789 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 4

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[]`
- hechos: `[]`
- latencia: 799 ms
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
- latencia: 798 ms
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
- latencia: 759 ms
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
- latencia: 752 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 782 ms
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
- latencia: 738 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 5

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 793 ms
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
- latencia: 751 ms
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
- latencia: 764 ms
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
- latencia: 770 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 801 ms
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
- latencia: 744 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «En 3 días hábiles, el 23/10, vencen estas tareas: Programar PLC de la comprimidora y Revisar comunicaciones industriales de la comprimidora.

Es solo un recordatorio; no hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Te recuerdo que “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 785 ms
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
- latencia: 792 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 2

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «En 3 días hábiles, el 23/10, vencen “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora”.

Este aviso no necesita respuesta.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «La tarea “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4920 ms
- Leda → Marcos: «Para anotar el inicio, falta saber cuál de las dos tareas arrancaste: ¿Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 744 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» [botones: PLC, COM]
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 815 ms
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
- latencia: 803 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 4

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «En 3 días hábiles, el 23/10, vencen estas tareas: Programar PLC de la comprimidora y Revisar comunicaciones industriales de la comprimidora.

Es solo un recordatorio; no hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «La tarea “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no necesitás responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5115 ms
- Leda → Marcos: «Me falta saber cuál para anotar el inicio. ¿Arrancaste con Programar PLC de la comprimidora o con Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}}]`
- latencia: 4655 ms
- Leda → Marcos: «Quedó anotado que arrancaste con Programar PLC de la comprimidora; la tarea está en curso. No hace falta que respondas.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 5

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «En 3 días hábiles, el 23/10, vencen estas tareas: Programar PLC de la comprimidora y Revisar comunicaciones industriales de la comprimidora.

Es solo un recordatorio; no hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «La tarea “Integrar datos de la comprimidora en CoreLabs” vence el 23/10, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 786 ms
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
- latencia: 783 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 1

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 788 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 779 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 2

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 823 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 795 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 3

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 825 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 800 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 4

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 801 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 4787 ms
- Leda → Marcos: «Quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”: está en curso. No hace falta que respondas.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 5

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 792 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 781 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 15 · Voy bien, la tengo casi lista · vez 1

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[]`
- hechos: `[]`
- latencia: 3357 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 1 día hábil de atraso: venció ayer, 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me contaste que la tenías casi lista. ¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'dijo': 'presente', 'el': '2026-10-27'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 756 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 769 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- (Leda no manda nada)
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': 'bdd021cd-10db-4703-a3e5-276dfbc04d2c'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': '5ebca0da-2e4c-424b-b332-484e15165cb5'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': 'b53ad76d-f4e1-4b3d-885c-a2fbda34cf61'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}, 'avisa_que_va_a_escalar': True}, 'outbox_id': None}]

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-11-03) → Ismael: «Marcos Tarquini no respondió los dos pedidos de estado que le llegaron desde el 27/10 sobre “Programar PLC de la comprimidora”; otro pedido no le llegó.

La tarea sigue en curso, venció el 27/10 y lleva 5 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

Te aviso para que estés al tanto. No necesitás responder.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 2, "pedidos_de_estado_que_no_le_llegaron": 1}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-11-03', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-27', 'necesita_respuesta': False, 'atraso_dias_habiles': 5, 'pedidos_de_estado_sin_respuesta': 2, 'pedidos_de_estado_que_no_le_llegaron': 1}}

## 15 · Voy bien, la tengo casi lista · vez 2

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6429 ms
- Leda → Marcos: «Anoté que venís bien y tenés casi lista “Programar PLC de la comprimidora”. Sigue pendiente confirmar su estado; mañana, 28 de octubre, a las 9:00 te lo voy a volver a pedir. No hace falta que respondas ahora.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que venías bien y tenías casi lista “Programar PLC de la comprimidora”. Sigue en curso y lleva 1 día hábil de atraso: venció el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Ya la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 747 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 766 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- (Leda no manda nada)
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': '94a6f6d4-9e46-4e6e-8645-e52a5a07e116'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': '110cae19-3085-4861-879a-6ae5b0fdb9f8'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}, 'outbox_id': None}, {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'avance_anterior': {'el': '2026-10-27', 'dijo': 'voy bien, la tengo casi lista'}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': 'a671673f-b97f-4634-942c-6ee3d20fe328'}]

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Me habías dicho que tendrías “Programar PLC de la comprimidora” para hoy. Sigue en curso y lleva 5 días hábiles de atraso: venció el 27 de octubre.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines y vence el 6 de noviembre, en 3 días hábiles. Ese aviso de vencimiento no necesita respuesta.

Si no respondés al pedido de estado de “Programar PLC de la comprimidora”, se le avisará a Ismael Soschinski; todavía no se le avisó.

¿Ya la terminaste, necesitás otra fecha para terminarla o está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 5, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}, "pedidos_anteriores_que_no_le_llegaron": 1}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-11-03', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-11-06', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 5, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}, 'pedidos_anteriores_que_no_le_llegaron': 1}]}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-11-03', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-11-06', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 5, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}, 'pedidos_anteriores_que_no_le_llegaron': 1}]}

## 15 · Voy bien, la tengo casi lista · vez 3

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «“Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. Es un recordatorio; no necesitás responder.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, para cuándo la vas a tener o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6983 ms
- Leda → Marcos: «Anoté que venís bien y tenés casi lista “Programar PLC de la comprimidora”. Sigue pendiente confirmar su estado; mañana 28 de octubre a las 9:00 te voy a volver a preguntar. Por ahora no necesitás responder.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que tenías casi lista “Programar PLC de la comprimidora”. Sigue en curso y lleva 1 día hábil de atraso: vencía el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Ya la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 812 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 877 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso: vencía el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me dijiste que la tendrías para el martes 3. ¿Seguís con esa fecha, ya la terminaste o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-30) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 3 días hábiles de atraso: vencía el 27 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

Me dijiste que la tendrías para el martes 3. ¿Mantenés esa fecha, ya la terminaste o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-11-02) → Ismael: «Marcos Tarquini no respondió los 3 pedidos de estado de “Programar PLC de la comprimidora” enviados desde el 28/10. El 27/10 dijo “voy bien, la tengo casi lista”, pero sigue en curso y lleva 4 días hábiles de atraso respecto del vencimiento del 27/10.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esa tarea. Este aviso no requiere respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-28", "necesita_respuesta": false, "atraso_dias_habiles": 4, "avance_sin_algo_cierto": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real [{'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-11-02', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-28', 'necesita_respuesta': False, 'atraso_dias_habiles': 4, 'avance_sin_algo_cierto': {'el': '2026-10-27', 'dijo': 'voy bien, la tengo casi lista'}, 'pedidos_de_estado_sin_respuesta': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-30', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-11-02', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-28', 'necesita_respuesta': False, 'atraso_dias_habiles': 4, 'avance_sin_algo_cierto': {'el': '2026-10-27', 'dijo': 'voy bien, la tengo casi lista'}, 'pedidos_de_estado_sin_respuesta': 3}}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': 'adea71c2-6235-490c-b955-d58a7acfa5cb'}, {'tipo': 'escalamiento', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-28', 'necesita_respuesta': False, 'atraso_dias_habiles': 4, 'avance_sin_algo_cierto': {'el': '2026-10-27', 'dijo': 'voy bien, la tengo casi lista'}, 'pedidos_de_estado_sin_respuesta': 3}, 'outbox_id': '40b51cb2-ac93-42bf-a49e-ba1830e81c48'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': '6d145da1-0d1e-4bc0-94bc-2cc74032176a'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}, 'outbox_id': 'cbbcdccf-5b4f-4ea1-a989-f50102b9eda2'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}, 'outbox_id': '245ca830-bea9-4013-9d06-589ebb4edac7'}, {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'avance_anterior': {'el': '2026-10-27', 'dijo': 'voy bien, la tengo casi lista'}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': 'a0690bee-1684-4c60-bbeb-038933fe166e'}]

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-11-03) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence el viernes 6 de noviembre, en 3 días hábiles. Este aviso no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real [{'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['COM'], 'el': '2026-11-03', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-11-06', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['COM'], 'el': '2026-11-03', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-11-06', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}

## 15 · Voy bien, la tengo casi lista · vez 4

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. Es sólo un recordatorio; no necesitás responder.»

**Paso 1.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[]`
- hechos: `[]`
- latencia: 810 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso: venció ayer, 27 de octubre, y lleva 1 día hábil de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

Me habías contado que estaba casi lista. ¿Ya la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'dijo': 'presente', 'el': '2026-10-27'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 3673 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 763 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- (Leda no manda nada)
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': '74411554-e171-498f-86fc-bbf81b4129b3'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': 'bd379e59-e199-4773-b19d-893aa5d62797'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}, 'outbox_id': None}]

**Paso 8.** Leda (2026-11-03 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-22 10:00)

**Paso 1.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1011 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'dijo': 'presente', 'el': '2026-10-27'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4891 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 826 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso: vencía ayer, 27 de octubre, y lleva 1 día hábil de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me dijiste que la tendrías para el martes 3. ¿Seguís con esa previsión, ya la terminaste o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso: vencía el 27 de octubre y lleva 2 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me dijiste que la tendrías para el martes 3. ¿Seguís con esa previsión, ya la terminaste o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-30) → Marcos: «“Programar PLC de la comprimidora” sigue en curso: vencía el 27 de octubre y lleva 3 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Este es el tercer pedido de estado. Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó.

Me dijiste que la tendrías para el martes 3. ¿Seguís con esa previsión, ya la terminaste o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-30', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'escalamiento', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'pedido_desde': '2026-10-28', 'necesita_respuesta': False, 'atraso_dias_habiles': 4, 'pedidos_de_estado_sin_respuesta': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': '48850892-737e-4999-bbbd-70211a485533'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}, 'outbox_id': '3122a7eb-c9e9-44f9-95b3-17def14658be'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}, 'outbox_id': '1f204dd3-129b-4328-b195-084747ec69d1'}]

**Paso 8.** Leda (2026-11-03 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []

## 16 · Arranqué hoy, con la tarea vencida · vez 1

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. Es un recordatorio; no hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura asignada, todavía sin empezar. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, para cuándo la tenés o está trabada?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” venció el 23 de octubre y lleva 1 día hábil de atraso. Sigue figurando asignada, todavía sin empezar. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Te vuelvo a consultar: ¿ya la terminaste, para cuándo la tenés o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 5411 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”; ahora está en curso. La fecha comprometida sigue siendo el 23 de octubre y lleva 1 día hábil de atraso.

Quedó guardado un aviso para volver a consultarte el estado mañana, 27 de octubre, a las 9:00.

¿Para qué día la vas a tener terminada?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:25:00-03:00"}}]`
- latencia: 5726 ms
- Leda → Marcos: «Quedó anotada tu previsión para terminar “Programar PLC de la comprimidora” el miércoles 28 de octubre. La fecha comprometida sigue siendo el 23 de octubre: si cumplís la previsión, serán 3 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” depende de que la termines.

El aviso a Ismael Soschinski quedó guardado y sale hoy a las 10:25; todavía no se envió. No hace falta que respondas ahora.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 16 · Arranqué hoy, con la tarea vencida · vez 2

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. Es solo un recordatorio; no necesitás responder.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura asignada, todavía sin empezar. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Ya la terminaste, tenés una fecha para terminarla o estás trabado con algo?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” venció el 23 de octubre y lleva 1 día hábil de atraso. Sigue figurando asignada, sin empezar. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Ya la terminaste, tenés una fecha para terminarla o estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 5771 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora” y está en curso. La fecha comprometida sigue siendo el 23 de octubre y lleva 1 día hábil de atraso. Mañana a las 9 te vuelvo a pedir el estado.

¿Para qué día la vas a tener terminada?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 791 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 4.** Leda (2026-10-26 10:30)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': '7a824896-f18f-4aaa-8531-effdf0ead272'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': 'd1175a7f-247c-47a5-b424-7e7646b8a57d'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': '54c24ee2-e43c-4ad1-911c-21b0ac0a12e5'}, {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'avance_anterior': {'el': '2026-10-26', 'dijo': 'arranque hoy, no pude antes', 'jugada': 'anotar_inicio'}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «El 26 de octubre me contaste que arrancaste “Programar PLC de la comprimidora”. Figura en curso y lleva 3 días hábiles de atraso desde el 23 de octubre. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

Me dijiste que la tendrías para hoy: ¿ya la terminaste, necesitás más tiempo y tenés una nueva fecha, o estás trabado con algo?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-26", "dijo": "arranque hoy, no pude antes", "jugada": "anotar_inicio"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real [{'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'avance_anterior': {'el': '2026-10-26', 'dijo': 'arranque hoy, no pude antes', 'jugada': 'anotar_inicio'}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'avance_anterior': {'el': '2026-10-26', 'dijo': 'arranque hoy, no pude antes', 'jugada': 'anotar_inicio'}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}

## 16 · Arranqué hoy, con la tarea vencida · vez 3

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue asignada, sin empezar. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: la terminaste, tenés una fecha para terminarla o está trabada?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” venció el 23 de octubre y lleva 1 día hábil de atraso. Sigue asignada, sin empezar. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: la terminaste, tenés una fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 805 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vencida': {'fecha_comprometida': '2026-10-23', 'atraso_dias_habiles': 1}, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-27'}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 775 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 4.** Leda (2026-10-26 10:30)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': '82e6e731-510f-4b0b-a578-712656dcb900'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': 'fede33cf-a876-4268-aaaf-5371b5db56c5'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': '3b9a7c00-3375-491b-a55a-b64ef8c7018b'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}, 'avisa_que_va_a_escalar': True}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” venció el 23 de octubre y lleva 3 días hábiles de atraso. Me habías contado que arrancaste y que la tendrías para hoy, aunque sigue figurando asignada, sin empezar.

“Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. Este es el tercer pedido de estado; si no hay respuesta, se le avisará a Ismael Soschinski.

¿La terminaste, tenés una nueva fecha para terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y figura asignada, todavía sin empezar. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, para cuándo la tenés o está trabada?»

**Paso 1.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 1, 'si_no_hay_respuesta': 'ausente'}}, real []

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 748 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vencida': {'fecha_comprometida': '2026-10-23', 'atraso_dias_habiles': 1}, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-27'}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 769 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 4.** Leda (2026-10-26 10:30)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': '066cea3a-8fd7-4581-9ca2-77349c46544a'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []

## 16 · Arranqué hoy, con la tarea vencida · vez 5

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Leda (2026-10-23 10:00)

**Paso 1.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 1, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 788 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vencida': {'fecha_comprometida': '2026-10-23', 'atraso_dias_habiles': 1}, 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-27'}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 804 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar'}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 4.** Leda (2026-10-26 10:30)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 1

Fuente: `tests/conversaciones/17-destrabar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 791 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: un próximo paso
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'espero el switch'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 758 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'se quemo la fuente'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 780 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 2

Fuente: `tests/conversaciones/17-destrabar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 789 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: un próximo paso
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'espero el switch'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 757 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'se quemo la fuente'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 782 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 3

Fuente: `tests/conversaciones/17-destrabar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 853 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: un próximo paso
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'espero el switch'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 750 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'se quemo la fuente'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 771 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 4

Fuente: `tests/conversaciones/17-destrabar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 797 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: un próximo paso
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'espero el switch'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 766 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'se quemo la fuente'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 806 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 5

Fuente: `tests/conversaciones/17-destrabar.md`. IA: `openrouter/openai/gpt-6.1-sol`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 758 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: un próximo paso
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'espero el switch'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 786 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'se quemo la fuente'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 758 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

