# Transcripciones de la ronda ronda1-luna

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23/10, en 3 días hábiles. No hace falta que respondas.»
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
- latencia: 6899 ms
- Leda → Marcos: «Anoté que arrancaste hoy a la mañana con Programar PLC de la comprimidora.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Programar PLC de la comprimidora vence hoy y figura en curso. Me habías contado que arrancaste esa mañana; ¿cómo viene ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 2

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que Programar PLC de la comprimidora vence el 23 de octubre. No hace falta que respondas.»
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
- latencia: 3007 ms
- Leda → Marcos: «Anoté que Programar PLC de la comprimidora está en curso desde hoy a la mañana.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Me habías contado que arrancaste Programar PLC de la comprimidora el lunes por la mañana. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 3

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
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
- latencia: 4321 ms
- Leda → Marcos: «Anoté que arrancaste hoy con “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Anoté que arrancaste con “Programar PLC de la comprimidora”. La tarea vence hoy. ¿Cómo viene ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 4

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
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
- latencia: 3742 ms
- Leda → Marcos: «Anoté que arrancaste hoy a la mañana con “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. Me habías contado que arrancaste a la mañana y ya estabas con la tarea. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23/10. No hace falta que respondas.»
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
- latencia: 4342 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está en curso.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” figura en curso y vence hoy. Me habías contado que arrancaste a la mañana y ya estabas en eso. ¿Qué avance concreto tiene ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 02 · Llego el 27, el proveedor se demoró · vez 1

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 10505 ms
- Leda → Marcos: «Anoté para “Programar PLC de la comprimidora” la previsión del 27/10 por la demora del proveedor. La fecha comprometida era el 23/10, así que acumula 2 días hábiles de atraso. El aviso a Ismael está guardado para salir hoy a las 15:40.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Programar PLC de la comprimidora está a cargo de Marcos Tarquini. El proveedor se demoró y la previsión es para el 27/10. Figura con fecha comprometida 23/10 y 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. La previsión es el 27/10 por la demora del proveedor, con 2 días hábiles de atraso; el aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. El 27/10 te voy a pedir una actualización. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pide_el_estado_el": {"fecha": "2026-10-27", "estado": "todavia_no"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Me habías contado que la previsión para “Programar PLC de la comprimidora” era hoy, por la demora del proveedor. Sigue en curso y tiene 2 días hábiles de atraso; Ismael ya recibió el aviso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine y vence el 30/10. ¿En qué estado está ahora “Programar PLC de la comprimidora”?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Me habías contado que la previsión para “Programar PLC de la comprimidora” era el 27/10, por la demora del proveedor. Sigue en curso y acumula 3 días hábiles de atraso. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Me habías contado que la previsión para “Programar PLC de la comprimidora” era el 27/10 por la demora del proveedor. Sigue en curso y acumula 4 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. Si no recibo respuesta»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” está asignada y vence hoy. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso y acumula 5 días hábiles de atraso. La previsión era para el 27/10, por una demora del proveedor, pero no recibimos respuesta a los pedidos de estado. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 2

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. Este aviso no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 7236 ms
- Leda → Marcos: «Anoté para “Programar PLC de la comprimidora” la previsión de llegada para el 27 de octubre, por la demora del proveedor. La fecha comprometida es el 23. El aviso a Ismael quedó guardado y sale hoy a las 15:40.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Programar PLC de la comprimidora está demorada por el proveedor. Marcos Tarquini prevé terminarla el 27/10; la fecha comprometida era el 23/10 y lleva 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. La previsión es para el 27 de octubre, por la demora del proveedor; el aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esta tarea. El 27 te vuelvo a pedir el estado. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pide_el_estado_el": {"fecha": "2026-10-27", "estado": "todavia_no"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso. La previsión era para hoy por la demora del proveedor, y el aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine y vence el 30 de octubre. ¿Cómo está ahora “Programar PLC de la comprimidora”?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Me habías contado que llegaba el 27 por la demora del proveedor. “Programar PLC de la comprimidora” sigue en curso y lleva 3 días hábiles de atraso; Ismael ya recibió el aviso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cuál es el estado actual de “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Me habías contado que llegaba el 27 por la demora del proveedor. “Programar PLC de la comprimidora” sigue en curso y lleva 4 días hábiles de atraso; Ismael ya recibió el aviso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cuál es el estado actual de “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso y lleva 5 días hábiles de atraso. Marcos había previsto terminarla el 27/10, por una demora del proveedor. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” está asignada y vence hoy. ¿Cuál es su estado actual?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 3

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 9527 ms
- Leda → Marcos: «Anoté como previsión para “Programar PLC de la comprimidora” el 27 de octubre, por la demora del proveedor. El aviso a Ismael está programado para hoy a las 15:40; todavía no se envió.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Programar PLC de la comprimidora lleva 2 días hábiles de atraso porque se demoró el proveedor. Marcos Tarquini prevé terminarla el 27/10. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. La previsión es terminar el 27 de octubre, con dos días hábiles de atraso por la demora del proveedor. El aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esta tarea. El 27 te voy a pedir el estado. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pide_el_estado_el": {"fecha": "2026-10-27", "estado": "todavia_no"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” sigue en curso; la previsión era terminar hoy, con dos días hábiles de atraso por la demora del proveedor. El aviso a Ismael ya se envió, y “Revisar comunicaciones industriales de la comprimidora” no puede empezar hasta que termine. ¿Cuál es el estado actual de “Programar PLC de la comprimidora”? “Revisar comunicaciones industriales de la comprimidora” vence el 30 de octubre.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «La previsión para “Programar PLC de la comprimidora” era terminar el 27 de octubre, pero sigue en curso. La demora del proveedor ya se avisó a Ismael. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cuál es el estado actual de “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Me habías contado que el proveedor se demoró y que la previsión para “Programar PLC de la comprimidora” era el 27 de octubre. Sigue en curso y lleva 4 días hábiles de atraso; el aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cuál es el estado actual de “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy y figura asignada. ¿Cuál es su estado actual?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso y lleva 5 días hábiles de atraso. La previsión de Marcos era terminarla el 27/10, por la demora del proveedor. Hasta que termine, no puede arrancar Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 5777 ms
- Leda → Marcos: «Anoté que estimás llegar el 27 con Programar PLC de la comprimidora porque se demoró el proveedor; la fecha comprometida era el 23. El aviso a Ismael quedó guardado y sale hoy a las 15:40.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Programar PLC de la comprimidora se demoró por el proveedor. Marcos Tarquini prevé terminarla el 27/10; la fecha comprometida era el 23/10 y lleva 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Programar PLC de la comprimidora sigue en curso y vence hoy. La previsión que compartiste es llegar el 27 por la demora del proveedor; Ismael ya fue avisado. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine la primera tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pide_el_estado_el": {"fecha": "2026-10-27", "estado": "todavia_no"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Programar PLC de la comprimidora sigue en curso y lleva 2 días hábiles de atraso. La previsión que habías compartido era llegar hoy por la demora del proveedor; Ismael ya fue avisado. Revisar comunicaciones industriales de la comprimidora vence el 30 de octubre y no puede arrancar hasta que termine la primera tarea. ¿En qué estado está ahora Programar PLC de la comprimidora?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Programar PLC de la comprimidora sigue en curso y lleva 3 días hábiles de atraso. La previsión que habías compartido era llegar el 27 por la demora del proveedor; Ismael ya fue avisado. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine la primera tarea. ¿En qué estado está ahora Programar PLC de la comprimidora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Programar PLC de la comprimidora sigue en curso y lleva 4 días hábiles de atraso. La previsión que compartiste era llegar el 27 por la demora del proveedor; Ismael ya fue avisado. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine esta tarea. ¿En qué estado está ahora Programar PLC de la comprimidora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso y lleva 5 días hábiles de atraso respecto del 23/10. La última previsión de Marcos era terminarla el 27/10, por una demora del proveedor; todavía no hay respuesta a los pedidos de estado. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «Revisar comunicaciones industriales de la comprimidora está asignada y vence hoy. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 5

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 6210 ms
- Leda → Marcos: «Anoté que “Programar PLC de la comprimidora” llegaría el 27 de octubre porque se demoró el proveedor. El aviso a Ismael está guardado y sale hoy a las 15:40.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Programar PLC de la comprimidora está demorada por el proveedor y lleva 2 días hábiles de atraso respecto de la fecha comprometida, el 23/10. Marcos Tarquini prevé terminarla el 27/10. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. La previsión es terminar el 27 de octubre por la demora del proveedor; el aviso a Ismael ya fue enviado. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pide_el_estado_el": {"fecha": "2026-10-27", "estado": "todavia_no"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y lleva 2 días hábiles de atraso. La previsión que me habías dado era terminar hoy por la demora del proveedor; Ismael ya fue avisado. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine y vence el 30 de octubre; no hace falta que respondas por ese aviso.

¿En qué estado está ahora “Programar PLC de la comprimidora”?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y acumula 3 días hábiles de atraso. Me habías dicho que la previsión era terminar el 27 por la demora del proveedor; Ismael ya fue avisado. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

¿Qué estado tiene ahora “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y acumula 4 días hábiles de atraso. Me habías dicho que preveías terminar el 27 por la demora del proveedor; Ismael ya fue avisado. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

¿Qué estado tiene ahora “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso con Marcos Tarquini y acumula 5 días hábiles de atraso. La última previsión era terminar el 27/10 por la demora del proveedor, pero esa fecha ya pasó. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy y está asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3076 ms
- Leda → Marcos: «Anoté que estás trabado con “Programar PLC de la comprimidora” porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «La tarea “Programar PLC de la comprimidora” sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarla?»
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
- latencia: 5984 ms
- Leda → Marcos: «Entiendo: no sabés quién lo está comprando y decís que lo pidieron hace dos semanas. Anoté que no sabés quién puede destrabar “Programar PLC de la comprimidora”. ¿Preferís que alguien ayude a destrabarlo o anoto una previsión? podés elegir una opción o responder por escrito.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "dejar_para_despues"}]`
- hechos: `[{"jugada": "dejar_para_despues", "resultado": "para_despues", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}}]`
- latencia: 11025 ms
- Leda → Marcos: «Entiendo, decís que hay que esperar a que llegue el repuesto. Para “Programar PLC de la comprimidora”, ¿preferís que alguien ayude a destrabarlo o que anote una previsión? Podés elegir una opción o responder por escrito.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real [{'nombre': 'dejar_para_despues'}]
- **falla** [comprension] preguntas para después: esperado [], real [{'tipo': 'propuesta', 'tarea': 'PLC'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «La tarea “Revisar comunicaciones industriales de la comprimidora” vence el 30/10, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 2

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5144 ms
- Leda → Marcos: «Anoté el bloqueo de “Programar PLC de la comprimidora” por falta del repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «La tarea “Programar PLC de la comprimidora” sigue bloqueada por falta del repuesto. ¿Quién puede destrabarla?»
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
- latencia: 5211 ms
- Leda → Marcos: «Anoté que no sabés quién puede destrabar “Programar PLC de la comprimidora”. ¿Querés que alguien te ayude o preferís anotar una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 12101 ms
- Leda → Marcos: «Entiendo, esperamos a que llegue el repuesto. No se anotó una previsión ni se pidió ayuda para “Programar PLC de la comprimidora”.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «La tarea “Revisar comunicaciones industriales de la comprimidora” vence el 30 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 3

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 6114 ms
- Leda → Marcos: «Anoté que estás trabado con Programar PLC de la comprimidora porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «Programar PLC de la comprimidora sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarlo?»
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
- latencia: 9750 ms
- Leda → Marcos: «Anoté que no sabés quién puede destrabar Programar PLC de la comprimidora; me decís que pidieron el repuesto hace dos semanas. ¿Preferís que alguien te ayude o anotamos una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "dejar_para_despues"}]`
- hechos: `[{"jugada": "dejar_para_despues", "resultado": "para_despues", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}}]`
- latencia: 11428 ms
- Leda → Marcos: «Entiendo, esperamos a que llegue el repuesto. Para Programar PLC de la comprimidora, ¿preferís que alguien te ayude o anotamos una previsión?»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real [{'nombre': 'dejar_para_despues'}]
- **falla** [comprension] preguntas para después: esperado [], real [{'tipo': 'propuesta', 'tarea': 'PLC'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Revisar comunicaciones industriales de la comprimidora vence el 30 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 4

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3914 ms
- Leda → Marcos: «Anoté que Programar PLC de la comprimidora está trabada porque falta el repuesto. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «¿Quién puede destrabar Programar PLC de la comprimidora, que sigue bloqueada por falta del repuesto?»
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
- latencia: 6415 ms
- Leda → Marcos: «Entiendo: pidieron el repuesto hace dos semanas y no sabés quién lo está comprando. Anoté que no sabés quién puede destrabar Programar PLC de la comprimidora. ¿Preferís que alguien te ayude a averiguarlo o anotar una previsión? Podés elegir una opción o responder por escrito.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 8524 ms
- Leda → Marcos: «Entiendo, preferís esperar a que llegue el repuesto. No anoté una previsión ni pedí ayuda para Programar PLC de la comprimidora.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «La tarea Revisar comunicaciones industriales de la comprimidora vence el 30 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 5

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3445 ms
- Leda → Marcos: «Anoté que estás trabado con “Programar PLC de la comprimidora” porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «La tarea “Programar PLC de la comprimidora” sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarla?»
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
- latencia: 5580 ms
- Leda → Marcos: «Anoté que no sabés quién puede destrabar “Programar PLC de la comprimidora”. Entiendo que no sabés quién está comprando el repuesto y que lo pidieron hace dos semanas. ¿Querés que alguien te ayude a destrabarlo o preferís anotar una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 7422 ms
- Leda → Marcos: «Entiendo. No anoté una previsión ni pedí ayuda para “Programar PLC de la comprimidora”.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence el 30 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 27 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Programar PLC de la comprimidora figura en curso y vence hoy. Para arrancar, tiene que terminar Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Programar PLC de la comprimidora sigue en curso y está vencida desde ayer. Para arrancar, tiene que terminar Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está la programación?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Programar PLC de la comprimidora figura en curso y venció el 27 de octubre; lleva 2 días hábiles de atraso. Para arrancar, tiene que terminar Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso y está a cargo de Marcos Tarquini. Venció el 27/10 y lleva 3 días hábiles de atraso; no hubo respuesta a los pedidos de estado desde esa fecha. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 2

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te aviso que Programar PLC de la comprimidora vence el 27 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Programar PLC de la comprimidora está en curso y vence hoy. Para arrancar, depende de que termine Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Programar PLC de la comprimidora vencía ayer y está en curso. No puede arrancar hasta que termine Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está ahora?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Programar PLC de la comprimidora sigue en curso y está vencida desde el 27 de octubre. Para arrancar, depende de que termine Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso: vencía el 27/10 y registra 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. Este aviso no requiere respuesta.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 3

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 27/10. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” está en curso y vence hoy. No puede arrancar hasta que termine “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” está en curso y vencía el 27/10. No puede arrancar hasta que termine “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” está en curso y vencía el 27/10. No puede arrancar hasta que termine “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso; la tiene Marcos Tarquini y venció el 27/10. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 4

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 27/10. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” figura en curso y vence hoy. Para arrancar, tiene que terminar “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” figura en curso y vencía el 27/10. Para avanzar, tiene que terminar “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está la programación?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” figura en curso y vencía el 27/10. Para avanzar, tiene que terminar “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora sigue en curso con Marcos Tarquini. Venció el 27/10 y lleva 3 días hábiles de atraso; Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 5

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 27 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” figura en curso y vence hoy. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” figura en curso y venció ayer. Para empezar, primero tiene que terminar “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está la programación?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” figura en curso y venció el 27 de octubre. Para empezar, primero tiene que terminar “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «El pedido de estado de Programar PLC de la comprimidora, a cargo de Marcos Tarquini, sigue sin respuesta desde el 27/10. La tarea figura en curso y venció el 27/10; Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 05 · Varias cosas en un mensaje · vez 1

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "xq espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "xq espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 9475 ms
- Leda → Marcos: «Quedó anotado que arrancaste con Programar PLC de la comprimidora. Para Revisar comunicaciones industriales de la comprimidora, anoté que la pasás al miércoles 4 de noviembre porque esperás el switch nuevo; la fecha comprometida era el 30 de octubre. El aviso a Ismael está programado para hoy a las 10:05.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora” está a la espera del switch nuevo. Marcos Tarquini figura como responsable; la fecha comprometida era el 30/10 y la previsión es el 4/11, con 3 días hábiles de atraso.»
  - hechos: `{"tarea": "COM", "motivo": "xq espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 9064 ms
- Leda → Marcos: «Anoté el bloqueo en Programar PLC de la comprimidora. ¿Quién puede ayudarte a destrabarlo?

Corregí la previsión de Revisar comunicaciones industriales de la comprimidora al jueves 5 de noviembre. El aviso a Ismael está programado para salir hoy a las 16:30.»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con el plc'}, {'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': None, 'es_correccion': True}]
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con el plc', 'resuelto': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4}}], real [{'tipo': 'correccion_de_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'se_anoto_en_la_tarea_equivocada', 'responsable': 'Marcos Tarquini', 'fecha_comprometida': '2026-10-30', 'prevision_que_no_vale': '2026-11-04'}, 'clave': 'motor:correccion_de_prevision:39a8a00a-56cf-4d4c-b9fa-c9a98dd84d0f', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con el plc', 'pregunta': 'quien_destraba'}, {'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'correccion_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-20T16:30:00-03:00'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'motivo': None, 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-20T16:30:00-03:00'}}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 6121 ms
- Leda → Marcos: «Anoté que Martín de IT tiene que habilitarte el acceso a la red de planta para destrabar Programar PLC de la comprimidora.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de IT', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de IT'}}]

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 10069 ms
- Leda → Marcos: «Anoté que empezaste con Programar PLC de la comprimidora. Revisar comunicaciones industriales de la comprimidora queda previsto para el miércoles 4 de noviembre, porque estás esperando el switch nuevo; son 3 días hábiles después del 30 de octubre. El aviso a Ismael quedó programado para hoy a las 10:05.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora” está a la espera del switch nuevo, a cargo de Marcos Tarquini. La previsión es para el 4/11; la fecha comprometida figura como 30/10 y aparece con 3 días hábiles de atraso.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me trabe con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me trabe con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 9061 ms
- Leda → Marcos: «Anoté el bloqueo de Programar PLC de la comprimidora. La previsión de Revisar comunicaciones industriales de la comprimidora quedó corregida al 4 de noviembre; el aviso a Ismael está guardado para hoy a las 16:30, todavía no se envió. ¿Quién puede destrabar el PLC?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me trabe con el plc'}, {'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': None, 'es_correccion': True}]
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'me trabe con el plc', 'resuelto': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4}}], real [{'tipo': 'correccion_de_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'se_anoto_en_la_tarea_equivocada', 'responsable': 'Marcos Tarquini', 'fecha_comprometida': '2026-10-30', 'prevision_que_no_vale': '2026-11-04'}, 'clave': 'motor:correccion_de_prevision:145ffbec-0fb0-464d-bad1-e4bc520a5443', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me trabe con el plc', 'pregunta': 'quien_destraba'}, {'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'correccion_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-20T16:30:00-03:00'}}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 6070 ms
- Leda → Marcos: «Anoté que Martín de IT tiene que habilitarte el acceso a la red de planta para destrabar Programar PLC de la comprimidora.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de IT', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de IT'}}]

## 05 · Varias cosas en un mensaje · vez 3

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 8358 ms
- Leda → Marcos: «“Programar PLC de la comprimidora” quedó en curso. Para “Revisar comunicaciones industriales de la comprimidora”, anoté como previsión el miércoles 4 de noviembre, porque estás esperando el switch nuevo. La fecha comprometida era el 30 de octubre, así que queda con 3 días hábiles de atraso.

El aviso a Ismael quedó programado para hoy a las 10:05; todavía no se envió.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora” figura con 3 días hábiles de atraso. Está esperando el switch nuevo, a cargo de Marcos, previsto para el 4/11; la fecha comprometida es el 30/10.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me trabe con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me trabe con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 11688 ms
- Leda → Marcos: «Anoté el bloqueo de “Programar PLC de la comprimidora”. La previsión de “Revisar comunicaciones industriales de la comprimidora” quedó corregida al 4 de noviembre, aunque me indicás jueves 5. El aviso corregido a Ismael quedó guardado para salir hoy a las 16:30; todavía no se envió.

¿Quién puede destrabar lo del PLC?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me trabe con el plc'}, {'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': None, 'es_correccion': True}]
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'me trabe con el plc', 'resuelto': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4}}], real [{'tipo': 'correccion_de_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'se_anoto_en_la_tarea_equivocada', 'responsable': 'Marcos Tarquini', 'fecha_comprometida': '2026-10-30', 'prevision_que_no_vale': '2026-11-04'}, 'clave': 'motor:correccion_de_prevision:8e101e41-f063-4365-8cfa-b006332eb4ca', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me trabe con el plc', 'pregunta': 'quien_destraba'}, {'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'correccion_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-20T16:30:00-03:00'}}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 4498 ms
- Leda → Marcos: «Anoté que Martín de IT puede destrabar “Programar PLC de la comprimidora” habilitándote el acceso a la red de planta.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de IT', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de IT'}}]

## 05 · Varias cosas en un mensaje · vez 4

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 6171 ms
- Leda → Marcos: «Anoté que “Programar PLC de la comprimidora” está en curso. Para “Revisar comunicaciones industriales de la comprimidora”, registré el miércoles 4 de noviembre como previsión porque estás esperando el switch nuevo; la fecha comprometida era el 30 de octubre. El aviso a Ismael quedó programado para hoy a las 10:05; todavía no se envió.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora” tiene 3 días hábiles de atraso. Marcos espera el switch nuevo y prevé avanzar el 4/11; la fecha comprometida es el 30/10.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me trabe con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me trabe con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 8740 ms
- Leda → Marcos: «Anoté el bloqueo en “Programar PLC de la comprimidora”. Para “Revisar comunicaciones industriales de la comprimidora”, la previsión quedó corregida al 4 de noviembre; el aviso a Ismael está guardado para hoy a las 16:30, todavía no se envió.

¿Quién puede destrabar el PLC?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me trabe con el plc'}, {'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': None, 'es_correccion': True}]
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'me trabe con el plc', 'resuelto': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4}}], real [{'tipo': 'correccion_de_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'se_anoto_en_la_tarea_equivocada', 'responsable': 'Marcos Tarquini', 'fecha_comprometida': '2026-10-30', 'prevision_que_no_vale': '2026-11-04'}, 'clave': 'motor:correccion_de_prevision:65215e9c-a944-427c-9a3e-f8f3b4476b0f', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me trabe con el plc', 'pregunta': 'quien_destraba'}, {'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'correccion_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-20T16:30:00-03:00'}}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 4641 ms
- Leda → Marcos: «Anoté que Martin de IT puede destrabar “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de IT', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de IT'}}]

## 05 · Varias cosas en un mensaje · vez 5

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el 23/10; faltan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 5177 ms
- Leda → Marcos: «Quedó anotado que arrancaste con Programar PLC de la comprimidora. Para Revisar comunicaciones industriales de la comprimidora, anoté que prevés terminar el 4/11 porque esperás el switch nuevo; son 3 días hábiles después de la fecha comprometida. El aviso a Ismael quedó guardado y está previsto para hoy a las 10:05.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora” sigue pendiente mientras esperan el switch nuevo. Marcos Tarquini es responsable; la previsión es para el 4/11. La fecha comprometida era el 30/10 y acumula 3 días hábiles de atraso.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "no_se_puede", "motivo": "misma_tarea", "tarea": "COM"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 9526 ms
- Leda → Marcos: «Anoté el bloqueo de Programar PLC de la comprimidora. No pude cambiar la previsión de Revisar comunicaciones industriales de la comprimidora: sigue anotada para el 4/11. ¿Quién puede ayudarte a destrabar el PLC?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con el plc'}, {'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real []
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con el plc', 'resuelto': False}]
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4}}], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con el plc', 'pregunta': 'quien_destraba'}, {'jugada': 'corregir', 'resultado': 'no_se_puede', 'motivo': 'misma_tarea', 'tarea': 'COM'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 6395 ms
- Leda → Marcos: «Quedó anotado que Martin, de IT, puede destrabar Programar PLC de la comprimidora habilitándote el acceso a la red de planta.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de IT', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de IT'}}]

## 06 · No, era la otra tarea · vez 1

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 4687 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”; está en curso.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 5939 ms
- Leda → Marcos: «Corregí el registro: “Programar PLC de la comprimidora” sigue asignada y “Revisar comunicaciones industriales de la comprimidora” quedó anotada como en curso.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” sigue asignada y vence hoy. El 20/10 comentaste que todavía no la habías empezado; ¿en qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23/10. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 4417 ms
- Leda → Marcos: «Anoté que arrancaste con Programar PLC de la comprimidora; figura en curso.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 4969 ms
- Leda → Marcos: «Corregí el registro: Programar PLC de la comprimidora sigue asignada y anoté que Revisar comunicaciones industriales de la comprimidora está en curso.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Programar PLC de la comprimidora sigue asignada y vence hoy, 23/10. La última vez me dijiste que todavía no la habías empezado; ¿en qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 3

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5915 ms
- Leda → Marcos: «Anoté que empezaste “Programar PLC de la comprimidora”.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 4987 ms
- Leda → Marcos: «Corregí la anotación: quedó registrado que empezaste “Revisar comunicaciones industriales de la comprimidora”. “Programar PLC de la comprimidora” sigue asignada.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” sigue asignada y vence hoy. La última vez me dijiste que todavía no la habías empezado. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 4

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 2702 ms
- Leda → Marcos: «Anoté que empezaste “Programar PLC de la comprimidora”.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 5341 ms
- Leda → Marcos: «Corregí la anotación: quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”. “Programar PLC de la comprimidora” sigue asignada.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” sigue asignada. El 20/10 me dijiste que todavía no la habías empezado. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23/10. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 6064 ms
- Leda → Marcos: «Anoté que arrancaste esta mañana con Programar PLC de la comprimidora.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 4994 ms
- Leda → Marcos: «Corregí la anotación: Programar PLC de la comprimidora sigue asignada. Anoté que arrancaste Revisar comunicaciones industriales de la comprimidora.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «El 20/10 me dijiste que todavía no habías empezado Programar PLC de la comprimidora, que vence hoy. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 07 · Dejá, no importa · vez 1

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23/10, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4883 ms
- Leda → Marcos: «Anoté que estás trabado con Programar PLC de la comprimidora. ¿Quién te puede ayudar a destrabarlo?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 5213 ms
- Leda → Marcos: «No puedo cerrar esto todavía: me falta saber quién te puede ayudar a destrabar Programar PLC de la comprimidora. ¿Quién sería?»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [motor] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [motor] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real [{'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'PLC'}}]
- **falla** [motor] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «Programar PLC de la comprimidora sigue bloqueada. ¿Quién te puede ayudar a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- Leda, por su cuenta (repregunta PLC, 2026-10-22) → Marcos: «Programar PLC de la comprimidora sigue bloqueada. ¿Quién te puede ayudar a destrabarla? Si no respondés, se avisará a Ismael; por ahora todavía no se le avisó.»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento_de_una_pregunta PLC, 2026-10-23) → Ismael: «Programar PLC de la comprimidora sigue bloqueada y está a cargo de Marcos Tarquini. El 20/10 te pregunté quién podía destrabarla; todavía no tengo esa respuesta. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}, {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento_de_una_pregunta', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'falta_de_respuesta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'pregunta': 'quien_destraba', 'responsable': 'Marcos Tarquini', 'preguntado_el': '2026-10-20', 'necesita_respuesta': False, 'preguntas_sin_respuesta': 3}}

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4933 ms
- Leda → Marcos: «Anoté el bloqueo en “Programar PLC de la comprimidora”. ¿Quién te puede ayudar a destrabarlo?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 4552 ms
- Leda → Marcos: «No puedo cancelar la pregunta mientras está pendiente. ¿Quién te puede ayudar a destrabar “Programar PLC de la comprimidora”?»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [motor] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [motor] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real [{'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'PLC'}}]
- **falla** [motor] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada. ¿Quién te puede ayudar a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- Leda, por su cuenta (repregunta PLC, 2026-10-22) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada. ¿Quién te puede ayudar a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento_de_una_pregunta PLC, 2026-10-23) → Ismael: «Programar PLC de la comprimidora está bloqueada y figura a cargo de Marcos Tarquini. Sigue pendiente saber quién puede destrabarla. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}, {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento_de_una_pregunta', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'falta_de_respuesta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'pregunta': 'quien_destraba', 'responsable': 'Marcos Tarquini', 'preguntado_el': '2026-10-20', 'necesita_respuesta': False, 'preguntas_sin_respuesta': 3}}

## 07 · Dejá, no importa · vez 3

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «No hace falta que respondas a este aviso: “Programar PLC de la comprimidora” vence el 23 de octubre.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4784 ms
- Leda → Marcos: «Anoté que estás trabado con “Programar PLC de la comprimidora”. ¿Quién te puede ayudar a destrabarlo?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 8288 ms
- Leda → Marcos: «No puedo dejarlo sin efecto todavía: sigue pendiente saber quién puede ayudarte con “Programar PLC de la comprimidora”. ¿Quién te puede ayudar a destrabarlo?»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [motor] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [motor] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real [{'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'PLC'}}]
- **falla** [motor] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «Sigue pendiente saber quién puede ayudarte a destrabar “Programar PLC de la comprimidora”. ¿Quién te puede ayudar?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- Leda, por su cuenta (repregunta PLC, 2026-10-22) → Marcos: «Sigue pendiente saber quién puede ayudarte con “Programar PLC de la comprimidora”. ¿Quién te puede ayudar a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento_de_una_pregunta PLC, 2026-10-23) → Ismael: «La tarea Programar PLC de la comprimidora sigue bloqueada. El 20/10 te pregunté quién puede destrabarla; no hace falta que respondas este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}, {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento_de_una_pregunta', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'falta_de_respuesta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'pregunta': 'quien_destraba', 'responsable': 'Marcos Tarquini', 'preguntado_el': '2026-10-20', 'necesita_respuesta': False, 'preguntas_sin_respuesta': 3}}

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4623 ms
- Leda → Marcos: «Quedó anotado que estás trabado con “Programar PLC de la comprimidora”. ¿Quién te puede ayudar a destrabarla?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'estoy medio trabado con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 7662 ms
- Leda → Marcos: «Sigue pendiente saber quién te puede ayudar a destrabar “Programar PLC de la comprimidora”. ¿Quién podría darte una mano?»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [motor] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [motor] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real [{'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'PLC'}}]
- **falla** [motor] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada. ¿Quién te puede ayudar a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- Leda, por su cuenta (repregunta PLC, 2026-10-22) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada. Todavía no se avisó a Ismael. ¿Quién te puede ayudar a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento_de_una_pregunta PLC, 2026-10-23) → Ismael: «Programar PLC de la comprimidora sigue bloqueada y todavía no hay respuesta sobre quién la destraba. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}, {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento_de_una_pregunta', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'falta_de_respuesta', 'sobre': {'causa': 'estoy medio trabado con esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'pregunta': 'quien_destraba', 'responsable': 'Marcos Tarquini', 'preguntado_el': '2026-10-20', 'necesita_respuesta': False, 'preguntas_sin_respuesta': 3}}

## 07 · Dejá, no importa · vez 5

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5703 ms
- Leda → Marcos: «Anoté que estás trabado con Programar PLC de la comprimidora. ¿Quién puede ayudarte a destrabarlo?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 7279 ms
- Leda → Marcos: «Entiendo. Para cerrar esto, necesito saber quién puede ayudarte a destrabar Programar PLC de la comprimidora.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión
- **falla** [motor] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [motor] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado', 'no_se_anoto_nada': True}], real [{'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'PLC'}}]
- **falla** [motor] pregunta abierta después: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «Programar PLC de la comprimidora sigue bloqueada. ¿Quién puede ayudarte a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- Leda, por su cuenta (repregunta PLC, 2026-10-22) → Marcos: «Programar PLC de la comprimidora sigue bloqueada. Si no respondés, se avisará a Ismael Soschinski; todavía no se le avisó. ¿Quién puede ayudarte a destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento_de_una_pregunta PLC, 2026-10-23) → Ismael: «Programar PLC de la comprimidora sigue bloqueada. El 20/10 te pregunté quién la destraba y todavía no tengo esa respuesta. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real [{'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}, {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 2, 'pregunta': 'quien_destraba', 'necesita_respuesta': True}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'repregunta', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'repregunta', 'sobre': {'causa': 'esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'numero': 3, 'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'si_no_hay_respuesta': {'estado': 'todavia_no', 'se_avisa_a': ['Ismael Soschinski']}}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento_de_una_pregunta', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'falta_de_respuesta', 'sobre': {'causa': 'esto', 'jugada': 'anotar_bloqueo'}, 'tarea': 'PLC', 'estado': 'bloqueada', 'pregunta': 'quien_destraba', 'responsable': 'Marcos Tarquini', 'preguntado_el': '2026-10-20', 'necesita_respuesta': False, 'preguntas_sin_respuesta': 3}}

## 08 · Cambio de tema · vez 1

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4459 ms
- Leda → Marcos: «Anoté que estás trabado con “Programar PLC de la comprimidora”. ¿Quién podría ayudarte a destrabarlo?»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 5135 ms
- Leda → Marcos: «Anoté que necesitás hasta el miércoles 4 de noviembre para “Revisar comunicaciones industriales de la comprimidora”. El aviso a Ismael quedó en cola para salir hoy a las 10:43.

¿Quién podría ayudarte a destrabar “Programar PLC de la comprimidora”?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30, necesito hasta el miercoles 4'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:6c07e201-3883-4570-aa3e-319c252dbf28', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos indicó que no llega al 30 y necesita hasta el miércoles 4 de noviembre para terminar “Revisar comunicaciones industriales de la comprimidora”.»
  - hechos: `{"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5640 ms
- Leda → Marcos: «Anoté que estás trabado con “Programar PLC de la comprimidora” porque todavía no te mandaron el programa del fabricante. ¿Quién podría ayudarte a destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}

## 08 · Cambio de tema · vez 2

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4431 ms
- Leda → Marcos: «Anoté el bloqueo en Programar PLC de la comprimidora. ¿Quién puede destrabarlo?»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 7272 ms
- Leda → Marcos: «Anoté que necesitás hasta el miércoles 4 de noviembre para Revisar comunicaciones industriales de la comprimidora; la fecha comprometida era el 30 de octubre. El aviso a Ismael está programado para salir hoy a las 10:43.

¿Quién puede destrabar Programar PLC de la comprimidora?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:19d20e11-96d2-4fad-921d-532328665f54', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora” no llegará a la fecha comprometida del 30 de octubre. Marcos Tarquini prevé terminarla el 4 de noviembre.»
  - hechos: `{"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_destraba"], "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 4561 ms
- Leda → Marcos: «Entiendo: te falta el programa del fabricante para Programar PLC de la comprimidora. ¿Quién puede destrabarlo: alguien, no sabés o nadie más?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'falta_dato', 'falta': ['quien_destraba'], 'puede_ser': ['alguien', 'no_sabe', 'nadie_mas']}]

## 08 · Cambio de tema · vez 3

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5350 ms
- Leda → Marcos: «Anoté el bloqueo en “Programar PLC de la comprimidora”. ¿Quién te puede ayudar a destrabarlo?»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 6343 ms
- Leda → Marcos: «Anoté que “Revisar comunicaciones industriales de la comprimidora” no llega al 30 de octubre y la necesitás para el miércoles 4 de noviembre. El aviso a Ismael quedó preparado para salir hoy a las 10:43.

Sobre “Programar PLC de la comprimidora”, ¿quién te puede ayudar a destrabarlo?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:2a7a8b1b-3c44-441d-b7e9-009f01813749', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora” figura con 3 días hábiles de atraso. Marcos Tarquini prevé terminarla el 4 de noviembre.»
  - hechos: `{"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_destraba"], "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 6374 ms
- Leda → Marcos: «Entiendo, estás trabado porque no te mandaron el programa del fabricante. ¿Quién te puede ayudar a destrabar “Programar PLC de la comprimidora”? Podés elegir alguien, no lo sé o nadie más.»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'falta_dato', 'falta': ['quien_destraba'], 'puede_ser': ['alguien', 'no_sabe', 'nadie_mas']}]

## 08 · Cambio de tema · vez 4

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5391 ms
- Leda → Marcos: «Anoté el bloqueo en “Programar PLC de la comprimidora”. ¿Quién puede ayudarte a destrabarlo?»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 4606 ms
- Leda → Marcos: «Anoté que prevés terminar “Revisar comunicaciones industriales de la comprimidora” el 4 de noviembre, después del 30. El aviso a Ismael está guardado para enviarse hoy a las 10:43.

¿Quién puede ayudarte a destrabar “Programar PLC de la comprimidora”?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [motor] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Revisar comunicaciones industriales de la comprimidora tiene fecha comprometida para el 30/10 y previsión para el 4/11. Figura con 3 días hábiles de atraso. La tarea está a cargo de Marcos Tarquini.»
  - hechos: `{"tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_destraba"], "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 4503 ms
- Leda → Marcos: «Entiendo que no te mandaron el programa del fabricante para “Programar PLC de la comprimidora”. ¿Quién puede ayudarte a destrabarlo: alguien, no sabés quién o no hay nadie más? Podés elegir una opción o responder por escrito.»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'no me mandaron el programa del fabricante'}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'falta_dato', 'falta': ['quien_destraba'], 'puede_ser': ['alguien', 'no_sabe', 'nadie_mas']}]

## 08 · Cambio de tema · vez 5

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4620 ms
- Leda → Marcos: «Anoté que estás trabado con “Programar PLC de la comprimidora”. ¿Quién puede destrabarlo?»
- [ ] dice: una pregunta por la causa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con esto'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con esto', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con esto', 'pregunta': 'quien_destraba'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 6906 ms
- Leda → Marcos: «Anoté que “Revisar comunicaciones industriales de la comprimidora” no llega al 30 y que la necesitás para el miércoles 4 de noviembre. El aviso a Ismael está guardado para salir hoy a las 10:43; todavía no se envió.

¿Quién puede destrabarte con “Programar PLC de la comprimidora”?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:8b119b4c-a9c8-4c67-8fa3-99db74d2d48b', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': True}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': True}
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «La tarea “Revisar comunicaciones industriales de la comprimidora”, a cargo de Marcos Tarquini, figura con 3 días hábiles de atraso. La previsión es para el 4/11; el motivo informado es que no llega al 30/10.»
  - hechos: `{"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-20', 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}}

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5832 ms
- Leda → Marcos: «Anoté que no te mandaron el programa del fabricante y eso te traba con “Programar PLC de la comprimidora”. ¿Quién puede destrabarte?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}

## 09 · Duda: ¿de qué tarea habla? · vez 1

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: ERROR.

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4952 ms
- Leda → Marcos: «¿Qué tarea arrancaste hoy?»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

## 09 · Duda: ¿de qué tarea habla? · vez 2

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: ERROR.

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4420 ms
- Leda → Marcos: «Gracias por avisar que hoy arrancaste.»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

## 09 · Duda: ¿de qué tarea habla? · vez 3

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: ERROR.

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5683 ms
- Leda → Marcos: «Gracias por avisar. ¿Qué tarea arrancaste hoy?»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

## 09 · Duda: ¿de qué tarea habla? · vez 4

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: ERROR.

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4505 ms
- Leda → Marcos: «¿Qué tarea arrancaste hoy?»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

## 09 · Duda: ¿de qué tarea habla? · vez 5

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: ERROR.

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[]`
- hechos: `[]`
- latencia: 7118 ms
- Leda → Marcos: «¿Qué tarea arrancaste hoy?»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

## 10 · Escribir en lugar de tocar un botón · vez 1

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4756 ms
- Leda → Marcos: «Me decís que arrancaste una de las tareas de la comprimidora. ¿Cuál?»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 3473 ms
- Leda → Marcos: «Anoté que arrancaste Programar PLC de la comprimidora.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4014 ms
- Leda → Marcos: «¿Cuál de las tareas de la comprimidora arrancaste?»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5158 ms
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora. Está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5672 ms
- Leda → Marcos: «Entiendo que arrancaste una de las tareas de la comprimidora. ¿Cuál empezaste?»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 3854 ms
- Leda → Marcos: «Anoté que estás trabajando en “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 10 · Escribir en lugar de tocar un botón · vez 4

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4475 ms
- Leda → Marcos: «Gracias por avisar. ¿Cuál de las tareas de la comprimidora empezaste?»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 4899 ms
- Leda → Marcos: «Quedó anotado que empezaste Programar PLC de la comprimidora.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4367 ms
- Leda → Marcos: «Me contás que arrancaste una de las tareas de la comprimidora.»
- [ ] dice: una pregunta por cuál de las dos
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 3532 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”. Está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Con cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? También podés responder tocando una opción.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 2069 ms
- Leda → Marcos: «La pregunta ya había quedado respondida ayer con Programar PLC de la comprimidora, así que elegir Revisar comunicaciones industriales de la comprimidora no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5193 ms
- Leda → Marcos: «Quedó anotado que hoy arrancaste Revisar comunicaciones industriales de la comprimidora.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- latencia: 8613 ms
- Leda → Marcos: «Quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el 4 de noviembre porque estás esperando el switch. El aviso a Ismael está guardado, todavía no se envió, y está previsto para mañana a las 9. ¿Quién puede destrabar el switch?»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}, {'nombre': 'anotar_bloqueo', 'tarea': 'COM', 'causa': 'espero el switch'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'COM', 'causa': 'espero el switch', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'motivo': 'espero el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-23T09:00:00-03:00'}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'COM', 'causa': 'espero el switch', 'pregunta': 'quien_destraba'}]

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- latencia: 7151 ms
- Leda → Marcos: «Anoté para Revisar comunicaciones industriales de la comprimidora una previsión de finalización para el 30 de octubre, por la llegada del switch. El aviso anterior a Ismael se retiró sin enviar. ¿Quién puede destrabar el switch?»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch', 'es_correccion': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': True}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'aviso_de_la_prevision_corregida': {'estado': 'retirado_sin_enviar'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': 'llego el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 2

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos tareas arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? También podés responder con los botones.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Anoté que arrancaste Programar PLC de la comprimidora.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 2888 ms
- Leda → Marcos: «La pregunta ya se había cerrado el 21/10 con Programar PLC de la comprimidora. Elegir Revisar comunicaciones industriales de la comprimidora no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5446 ms
- Leda → Marcos: «Anoté que hoy también arrancaste Revisar comunicaciones industriales de la comprimidora.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}]`
- latencia: 5726 ms
- Leda → Marcos: «Anoté tu previsión de que Revisar comunicaciones industriales de la comprimidora se te va al 4/11 porque esperás el switch; son 3 días hábiles después de la fecha comprometida del 30/10. El aviso a Ismael está guardado para salir mañana a las 9.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- latencia: 10730 ms
- Leda → Marcos: «Anoté tu previsión para Revisar comunicaciones industriales de la comprimidora: terminarla el 30/10, ahora que llegó el switch. Como coincide con la fecha comprometida, no se envía aviso.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 3

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribir el título.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Anoté como en curso “Programar PLC de la comprimidora”.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 2061 ms
- Leda → Marcos: «La consulta ya se había cerrado con “Programar PLC de la comprimidora”, así que elegir “Revisar comunicaciones industriales de la comprimidora” no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5084 ms
- Leda → Marcos: «Ah, entendido. Anoté como en curso “Revisar comunicaciones industriales de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}]`
- latencia: 2862 ms
- Leda → Marcos: «Anoté que “Revisar comunicaciones industriales de la comprimidora” se te va al 4 de noviembre porque estás esperando el switch. El aviso a Ismael está guardado y sale mañana a las 9.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llegó el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llegó el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- latencia: 8535 ms
- Leda → Marcos: «Anoté que prevés terminar “Revisar comunicaciones industriales de la comprimidora” para el 30 de octubre, ahora que llegó el switch.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 4

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Con cuál arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribir el título.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 2547 ms
- Leda → Marcos: «La pregunta sobre con cuál arrancaste ya quedó respondida: Programar PLC de la comprimidora. Esta elección no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 6294 ms
- Leda → Marcos: «Quedó anotado que arrancaste Revisar comunicaciones industriales de la comprimidora también.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}]`
- latencia: 7439 ms
- Leda → Marcos: «Anoté que Revisar comunicaciones industriales de la comprimidora se te va al 4/11 porque esperás el switch. La fecha comprometida es el 30/10, así que implica 3 días hábiles de demora. El aviso a Ismael está guardado y programado para salir mañana a las 9.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision", "tarea_correcta": "COM"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "corregir", "resultado": "no_se_puede", "motivo": "misma_tarea", "tarea": "COM"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- latencia: 12407 ms
- Leda → Marcos: «No se pudo corregir lo anterior porque corresponde a la misma tarea. Quedó anotado que Revisar comunicaciones industriales de la comprimidora»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision', 'tarea_correcta': 'COM'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'no_se_puede', 'motivo': 'misma_tarea', 'tarea': 'COM'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': 'llego el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 5

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Con cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o responder por escrito.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Anoté el inicio de Programar PLC de la comprimidora. Quedó en curso.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 2016 ms
- Leda → Marcos: «La consulta sobre con cuál arrancaste ya quedó respondida: empezaste Programar PLC de la comprimidora. Esta elección no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 6214 ms
- Leda → Marcos: «Entendido, también anoté el inicio de Revisar comunicaciones industriales de la comprimidora. Quedó en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- latencia: 7816 ms
- Leda → Marcos: «Anoté tu previsión para Revisar comunicaciones industriales de la comprimidora: se iría al 4 de noviembre porque estás esperando el switch. La fecha comprometida es el 30 de octubre, así que serían 3 días hábiles de atraso. El aviso a Ismael quedó guardado para salir mañana a las 9; todavía no se envió. ¿Quién puede destrabar lo del switch?»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}, {'nombre': 'anotar_bloqueo', 'tarea': 'COM', 'causa': 'espero el switch'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'COM', 'causa': 'espero el switch', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'motivo': 'espero el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-23T09:00:00-03:00'}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'COM', 'causa': 'espero el switch', 'pregunta': 'quien_destraba'}]

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- latencia: 4680 ms
- Leda → Marcos: «Corregí la previsión de Revisar comunicaciones industriales de la comprimidora: ahora es para el 30 de octubre. El aviso anterior a Ismael se retiró antes de enviarse; como la previsión coincide con la fecha comprometida, no se generó otro aviso.

¿Quién puede destrabar lo del switch?»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': None, 'es_correccion': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': True}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'aviso_de_la_prevision_corregida': {'estado': 'retirado_sin_enviar'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': None, 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 12 · Algo que no está en la lista · vez 1

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 4050 ms
- Leda → Marcos: «Entiendo que estás tapado con lo de la paila. No puedo cambiar por chat quién tiene a cargo “Programar PLC de la comprimidora”; eso lo define Ismael Soschinski. ¿Querés que anote una previsión para esa tarea?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 7581 ms
- Leda → Marcos: «No quedó anotada una previsión para “Programar PLC de la comprimidora”. Ya figura en curso, así que no pude registrar el inicio.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 7343 ms
- Leda → Marcos: «No puedo programarte un recordatorio para el turno del viernes desde acá.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Saber si avisaste a alguien."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 6389 ms
- Leda → Marcos: «No todavía; el aviso al administrador está en cola y aún no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Saber si avisaste a alguien.'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 5513 ms
- Leda → Marcos: «Entiendo que ya terminaste “Programar PLC de la comprimidora”, pero no puedo recibir la entrega por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 5568 ms
- Leda → Marcos: «Te figuran pendientes:

• “Programar PLC de la comprimidora”, en curso; vence el 23/10.
• “Revisar comunicaciones industriales de la comprimidora”, asignada; vence el 30/10.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 2

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 3787 ms
- Leda → Marcos: «No puedo cambiar por chat quién está a cargo de “Programar PLC de la comprimidora”; eso lo decide Ismael. ¿Querés que anote una previsión de que estás tapado con lo de la paila?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 8438 ms
- Leda → Marcos: «No quedó anotada la previsión de que estás tapado con lo de la paila. “Programar PLC de la comprimidora” ya figura en curso, así que no pude registrar otro inicio.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 7733 ms
- Leda → Marcos: «No puedo gestionar recordatorios personales por acá.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "saber si le avisaron a alguien sobre el recordatorio del turno médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 6414 ms
- Leda → Marcos: «Todavía no: el aviso al administrador está en cola y aún no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'saber si le avisaron a alguien sobre el recordatorio del turno médico'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 5655 ms
- Leda → Marcos: «Entiendo que decís que ya terminaste “Programar PLC de la comprimidora”, pero la entrega de esa tarea todavía no se recibe por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 5271 ms
- Leda → Marcos: «Tenés “Programar PLC de la comprimidora”, que todavía figura en curso y vence el 23/10, y “Revisar comunicaciones industriales de la comprimidora”, asignada y con vencimiento el 30/10.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 3

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 3648 ms
- Leda → Marcos: «No puedo cambiar por chat quién es responsable de “Programar PLC de la comprimidora”; eso lo decide Ismael. ¿Querés que anote que prevés no poder ocuparte porque estás con lo de la paila?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 14451 ms
- Leda → Marcos: «Está bien. No anoté que prevés no poder ocuparte. “Programar PLC de la comprimidora” ya figura en curso, así que no pude registrar otro inicio.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 8549 ms
- Leda → Marcos: «No puedo programar recordatorios personales; por acá puedo ayudarte con el seguimiento de las tareas del equipo.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Preguntar si le avisaron a alguien sobre que prevé no poder ocuparse de Programar PLC de la comprimidora"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 4943 ms
- Leda → Marcos: «No todavía; el aviso al administrador está en cola y aún no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Preguntar si le avisaron a alguien sobre que prevé no poder ocuparse de Programar PLC de la comprimidora'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 5649 ms
- Leda → Marcos: «Entiendo que decís que ya terminaste “Programar PLC de la comprimidora”, pero la entrega todavía no se recibe por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 5352 ms
- Leda → Marcos: «Te figuran pendientes “Programar PLC de la comprimidora”, en curso y con vencimiento el 23 de octubre, y “Revisar comunicaciones industriales de la comprimidora”, asignada y con vencimiento el 30 de octubre.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 4

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23/10, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "Nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 4635 ms
- Leda → Marcos: «No puedo cambiar por acá quién está a cargo de “Programar PLC de la comprimidora”; eso lo decide Ismael. Puedo anotar que prevés no llegar porque estás tapado con lo de la paila. ¿Querés que lo anote?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 6298 ms
- Leda → Marcos: «No anoté la previsión. “Programar PLC de la comprimidora” ya está en curso, así que no pude registrar el inicio otra vez.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 6638 ms
- Leda → Marcos: «No puedo programar recordatorios personales por acá; puedo ayudarte con el seguimiento de tareas del equipo.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Saber si eso se lo avisaste a alguien."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 7308 ms
- Leda → Marcos: «El aviso al administrador está en cola, todavía no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Saber si eso se lo avisaste a alguien.'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 5489 ms
- Leda → Marcos: «No puedo registrar por chat la entrega de “Programar PLC de la comprimidora”.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 4277 ms
- Leda → Marcos: «Tenés pendientes:
- “Programar PLC de la comprimidora”, en curso, vence el 23/10.
- “Revisar comunicaciones industriales de la comprimidora”, asignada, vence el 30/10.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 5

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. Este aviso no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 4676 ms
- Leda → Marcos: «No puedo pasarle “Programar PLC de la comprimidora” a Nahuel por chat; el cambio de responsable lo decide Ismael. ¿Querés que anote una previsión para esa tarea?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 6065 ms
- Leda → Marcos: «Dale, no anoté una previsión. “Programar PLC de la comprimidora” ya figura en curso, así que no pude registrar el inicio otra vez.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 5882 ms
- Leda → Marcos: «No puedo programar recordatorios personales desde acá.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "saber si le avisaste a alguien"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 6078 ms
- Leda → Marcos: «Todavía no: el aviso al administrador está en cola, sin enviar.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'saber si le avisaste a alguien'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 4272 ms
- Leda → Marcos: «Me decís que ya terminaste “Programar PLC de la comprimidora”, pero la entrega de esa tarea todavía no se recibe por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 4905 ms
- Leda → Marcos: «Te figuran pendientes “Programar PLC de la comprimidora” (en curso, vence el 23 de octubre) y “Revisar comunicaciones industriales de la comprimidora” (asignada, vence el 30 de octubre).»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Te recuerdo que Integrar datos de la comprimidora en CoreLabs vence el 23 de octubre.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «La respuesta no requiere acción. Programar PLC de la comprimidora y Revisar comunicaciones industriales de la comprimidora vencen el 23/10.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4879 ms
- Leda → Marcos: «Entiendo, arrancaste con la tarea de la comprimidora.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5093 ms
- Leda → Marcos: «Anoté que arrancaste con Programar PLC de la comprimidora.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 2

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «La fecha límite de “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” es el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Te aviso que “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 2507 ms
- Leda → Marcos: «Anoté que empezaste “Programar PLC de la comprimidora”.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'en_curso'}
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 8793 ms
- Leda → Marcos: «Sí, “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23/10. No hace falta que respondas a este aviso.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Te recuerdo que “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre. Este mensaje no necesita respuesta.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4968 ms
- Leda → Marcos: «¿Arrancaste con “Programar PLC de la comprimidora” o con “Revisar comunicaciones industriales de la comprimidora”?»
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5762 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”; está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 4

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «El 23/10 vence la tarea “Integrar datos de la comprimidora en CoreLabs”. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23 de octubre. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 2591 ms
- Leda → Marcos: «Quedó anotado que arrancaste con “Programar PLC de la comprimidora”.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'en_curso'}
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6799 ms
- Leda → Marcos: «Sí, “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 5

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «La tarea “Integrar datos de la comprimidora en CoreLabs” vence el 23/10. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5675 ms
- Leda → Marcos: «¿Te referís a “Programar PLC de la comprimidora” o a “Revisar comunicaciones industriales de la comprimidora”?»
- [ ] dice: una pregunta por cuál de las dos
- [ ] no dice: un inicio anotado en cualquiera de ellas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "O1"}]`
- hechos: `[{"jugada": "elegir", "resultado": "no_se_puede", "motivo": "sin_opciones"}]`
- latencia: 6751 ms
- Leda → Marcos: «Ahora no puedo seleccionar “Programar PLC de la comprimidora” porque no hay opciones disponibles.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'elegir', 'opcion': 'O1'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real [{'jugada': 'elegir', 'resultado': 'no_se_puede', 'motivo': 'sin_opciones'}]

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 1

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 4396 ms
- Leda → Marcos: «Quedó anotado que arrancaste con “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 3643 ms
- Leda → Marcos: «Quedó anotado que arrancaste con “Revisar comunicaciones industriales de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 2

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 2721 ms
- Leda → Marcos: «Anoté que arrancaste «Programar PLC de la comprimidora»: está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 6642 ms
- Leda → Marcos: «Anoté que también empezaste «Revisar comunicaciones industriales de la comprimidora».»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 3

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 3622 ms
- Leda → Marcos: «Anoté que ya arrancaste con “Programar PLC de la comprimidora”. Quedó en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 3372 ms
- Leda → Marcos: «Anoté que también empezaste “Revisar comunicaciones industriales de la comprimidora”. Quedó en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 4

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 3972 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 4240 ms
- Leda → Marcos: «Quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 5

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5714 ms
- Leda → Marcos: «Quedó anotado que empezaste con Programar PLC de la comprimidora.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 2483 ms
- Leda → Marcos: «Quedó anotado que empezaste con Revisar comunicaciones industriales de la comprimidora.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 15 · Voy bien, la tengo casi lista · vez 1

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 27/10. No hace falta que respondas a este mensaje.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» está en curso y vence hoy. Para arrancar, primero tiene que terminar «Revisar comunicaciones industriales de la comprimidora». ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 9743 ms
- Leda → Marcos: «Anoté que vas bien y que tenés casi lista “Programar PLC de la comprimidora”. ¿Ya está terminada o sigue en curso? El pedido de estado quedó programado para mañana a las 9.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer comentaste que ibas bien y que tenías casi lista “Programar PLC de la comprimidora”. Sigue en curso y venció ayer; “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿Cuál es el estado actual: terminada, en curso (¿para cuándo estimás terminarla?) o trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 17875 ms
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
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-28T10:45:00-03:00"}}]`
- latencia: 7118 ms
- Leda → Marcos: «Anoté que estimás tener “Programar PLC de la comprimidora” para el 3/11. Está vencida desde el 27/10 y “Revisar comunicaciones industriales de la comprimidora” sigue dependiendo de que la termines. El aviso a Ismael quedó programado para hoy a las 10:45; todavía no se envió.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, lleva 5 días hábiles de atraso respecto de la fecha comprometida (27/10). La previsión actual es para el 3/11.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': '87c47567-412a-4c32-af77-840a51624cde'}, {'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'enviado', 'motivo': None, 'hechos': {'tarea': 'PLC', 'motivo': None, 'prevision': '2026-11-03', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 5}, 'outbox_id': '221d536d-9392-4cfb-b2b5-05bb42249c06'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': '576011a2-92d7-4756-a8c9-98ac0ed64f09'}, {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'avance_anterior': {'el': '2026-10-27', 'dijo': 'voy bien, la tengo casi lista'}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': '4d44c424-ef95-4087-953f-0da2ed97c2d3'}]

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Habías estimado tener “Programar PLC de la comprimidora” para hoy. Sigue en curso y lleva 5 días hábiles de atraso; el aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termines la programación y vence el 6/11. ¿Ya la terminaste o sigue en curso? Si sigue, ¿para cuándo estimás terminarla?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 2

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Programar PLC de la comprimidora vence el 27/10. No hace falta que respondas a este aviso.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Programar PLC de la comprimidora figura en curso y vence hoy. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. ¿Cómo viene la tarea y qué falta?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5765 ms
- Leda → Marcos: «Anoté tu avance en Programar PLC de la comprimidora: vas bien y la tenés casi lista. Para confirmar el estado, ¿ya quedó terminada o qué falta? Mañana a las 9 te vuelvo a consultar.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer comentaste que Programar PLC de la comprimidora iba bien y la tenías casi lista. Vence desde ayer y Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. ¿Ya la terminaste? Si no, ¿para cuándo estimás terminarla y está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-29T09:00:00-03:00"}, "veces_sin_algo_cierto": 2, "pregunta": "fecha_de_la_tarea", "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 8423 ms
- Leda → Marcos: «Anoté que seguís con Programar PLC de la comprimidora. La fecha comprometida era ayer; ¿para cuándo estimás terminarla? Mañana a las 9 está previsto volver a consultarte.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-28T10:45:00-03:00"}}]`
- latencia: 7541 ms
- Leda → Marcos: «Anoté como previsión que vas a terminar Programar PLC de la comprimidora el martes 3 de noviembre. El aviso a Ismael está previsto para hoy a las 10:45; todavía no se envió.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Programar PLC de la comprimidora tiene 5 días hábiles de atraso. Marcos Tarquini figura como responsable y la previsión es para el 3/11. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Programar PLC de la comprimidora sigue en curso y tu previsión era terminarla hoy; lleva 5 días hábiles de atraso. Ismael ya recibió el aviso. Revisar comunicaciones industriales de la comprimidora vence el 6/11 y no puede arrancar hasta que termine la programación. ¿Ya la terminaste? Si no, ¿para cuándo estimás terminarla y está trabada?

No hace falta que respondas al aviso sobre el vencimiento de Revisar comunicaciones industriales.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 3

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te recuerdo que Programar PLC de la comprimidora vence el 27 de octubre. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Programar PLC de la comprimidora está en curso y vence hoy. No puede arrancar hasta que termine Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 8365 ms
- Leda → Marcos: «Anoté que vas bien y la tenés casi lista en Programar PLC de la comprimidora. ¿Ya la terminaste o sigue en curso? Mañana a las 9 te volveré a pedir el estado.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer contaste que vas bien y la tenés casi lista. Programar PLC de la comprimidora sigue en curso y Revisar comunicaciones industriales no puede arrancar hasta que termine. ¿Ya la terminaste, para cuándo estimás terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-29T09:00:00-03:00"}, "veces_sin_algo_cierto": 2, "pregunta": "fecha_de_la_tarea", "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 7087 ms
- Leda → Marcos: «Anoté que todo está en orden y seguís con Programar PLC de la comprimidora. La fecha comprometida fue el 27 de octubre y ya venció; todavía necesito saber cuándo estimás terminarla. ¿Para qué fecha calculás tenerla lista? El próximo pedido de estado está guardado para mañana a las 9, todavía no se envió.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03", "motivo": "para el martes 3 la tengo"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": "para el martes 3 la tengo", "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-28T10:45:00-03:00"}}]`
- latencia: 7812 ms
- Leda → Marcos: «Anoté que estimás tener Programar PLC de la comprimidora lista el martes 3 de noviembre. Ya lleva 5 días hábiles de atraso. El aviso a Ismael está guardado para hoy a las 10:45; todavía no se envió.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'para el martes 3 la tengo'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'para el martes 3 la tengo', 'es_correccion': False}]

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Programar PLC de la comprimidora está a cargo de Marcos Tarquini, con previsión para el martes 3 de noviembre. Tiene un atraso de 5 días hábiles respecto de la fecha comprometida, el 27 de octubre, y depende de Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": "para el martes 3 la tengo", "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Habías estimado tener Programar PLC de la comprimidora lista hoy, 3 de noviembre. Sigue en curso y lleva 5 días hábiles de atraso; el aviso a Ismael ya se envió. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine y vence el 6 de noviembre; no hace falta responder por esa tarea.

¿Ya terminaste Programar PLC de la comprimidora o sigue en curso?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "motivo": "para el martes 3 la tengo", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 4

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Programar PLC de la comprimidora vence el 27 de octubre. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Programar PLC de la comprimidora está en curso y vence hoy. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5506 ms
- Leda → Marcos: «Anoté que vas bien y que la tenés casi lista en “Programar PLC de la comprimidora”. ¿Ya quedó terminada? El pedido para que nos confirmes el estado está guardado para salir mañana a las 9.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y venció ayer. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. Ayer comentaste que la tenías casi lista. ¿Ya la terminaste, para cuándo estimás terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-29T09:00:00-03:00"}, "veces_sin_algo_cierto": 2, "pregunta": "fecha_de_la_tarea", "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 8387 ms
- Leda → Marcos: «Anoté que decís que todo está en orden y seguís con “Programar PLC de la comprimidora”. La fecha comprometida fue el 27 de octubre y ya venció. El aviso para volver a pedirte el estado está guardado para mañana a las 9; todavía no salió. ¿Para cuándo estimás terminarla?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-28T10:45:00-03:00"}}]`
- latencia: 6391 ms
- Leda → Marcos: «Anoté que estimás terminar “Programar PLC de la comprimidora” el 3 de noviembre. El aviso a Ismael está programado para hoy a las 10:45; todavía no salió.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Programar PLC de la comprimidora está a cargo de Marcos Tarquini. La fecha comprometida era el 27/10 y tiene 5 días hábiles de atraso; la previsión actual es el 3/11.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «“Programar PLC de la comprimidora” sigue en curso; la previsión era terminarla hoy, 3 de noviembre, y lleva 5 días hábiles de atraso. El aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede empezar hasta que termine la programación y vence el 6 de noviembre. ¿Cuál es el estado actual: ya terminaste la programación o sigue en curso?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te recuerdo que Programar PLC de la comprimidora vence el 27 de octubre. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Programar PLC de la comprimidora vence hoy y figura en curso. No puede arrancar hasta que termine Revisar comunicaciones industriales de la comprimidora. ¿Cómo viene el trabajo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6588 ms
- Leda → Marcos: «Anoté que vas bien y que casi tenés lista Programar PLC de la comprimidora. ¿Qué falta para terminarla? Quedó programado volver a consultarte mañana a las 9.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer contaste que vas bien y casi tenés lista Programar PLC de la comprimidora. Sigue en curso y venció ayer; Revisar comunicaciones industriales de la»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-29T09:00:00-03:00"}, "veces_sin_algo_cierto": 2, "pregunta": "fecha_de_la_tarea", "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 11686 ms
- Leda → Marcos: «Anoté que todo está en orden y seguís con Programar»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-28T10:45:00-03:00"}}]`
- latencia: 6002 ms
- Leda → Marcos: «Anoté que prevés tener Programar PLC de la comprimidora para el martes 3 de noviembre. Está vencida desde el 27 de octubre y lleva 5 días hábiles de atraso; Revisar comunicaciones industriales de la comprimidora depende de esta tarea. El aviso a Ismael quedó guardado para salir hoy a las 10:45.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Programar PLC de la comprimidora está a cargo de Marcos Tarquini. Tenía fecha comprometida para el 27/10 y lleva 5 días hábiles de atraso; la previsión es para el 3/11.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «La última previsión que diste para Programar PLC de la comprimidora fue para hoy, 3 de noviembre. Sigue en curso y lleva 5 días hábiles de atraso; el aviso a Ismael ya se envió. Revisar comunicaciones industriales de la comprimidora depende de esta tarea y vence el 6 de noviembre.

¿Cuál es el estado actual de Programar PLC de la comprimidora?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 16 · Arranqué hoy, con la tarea vencida · vez 1

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Programar PLC de la comprimidora vence hoy. Para arrancar, primero tiene que terminar Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Programar PLC de la comprimidora sigue asignada y tiene 1 día hábil de atraso. Para arrancar, primero tiene que terminar Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 6778 ms
- Leda → Marcos: «Tomo que me decís que arrancaste hoy. Programar PLC de la comprimidora figura en curso y tiene 1 día hábil de atraso respecto del 23 de octubre. ¿Para qué fecha estimás terminarla?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:25:00-03:00"}}]`
- latencia: 8516 ms
- Leda → Marcos: «Anoté el miércoles 28 de octubre como previsión para Programar PLC de la comprimidora. La tarea acumula 3 días hábiles de atraso respecto del 23. El aviso a Ismael está programado para hoy a las 10:25.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora está atrasada 3 días hábiles respecto de la fecha comprometida del 23/10. Marcos Tarquini prevé completarla el 28/10.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Me habías dicho que tendrías Programar PLC de la comprimidora para hoy, 28 de octubre. Figura en curso y acumula 3 días hábiles de atraso respecto del 23. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine; el aviso a Ismael ya se envió. ¿La terminaste o sigue en curso?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 2

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Programar PLC de la comprimidora está asignada y vence hoy. No puede arrancar hasta que termine Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Programar PLC de la comprimidora sigue asignada y está atrasada un día hábil. No puede arrancar hasta que termine Revisar comunicaciones industriales de la comprimidora. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 7782 ms
- Leda → Marcos: «Anoté que arrancaste hoy. Programar PLC de la comprimidora está atrasada un día hábil y quedó guardado un aviso para volver a consultarte mañana a las 9. ¿Para qué fecha estimás terminarla?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:25:00-03:00"}}]`
- latencia: 4373 ms
- Leda → Marcos: «Anoté que estimás terminar “Programar PLC de la comprimidora” el miércoles 28. El aviso a Ismael quedó guardado y sale hoy a las 10:25.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora está atrasada 3 días hábiles. Marcos Tarquini figura como responsable y la previsión es el 28/10. La tarea depende de Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Me habías dicho que estimabas terminar hoy “Programar PLC de la comprimidora”. Sigue en curso y está atrasada 3 días hábiles; Ismael ya recibió el aviso. ¿Ya la terminaste?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 3

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «¿En qué estado está “Programar PLC de la comprimidora”? La tarea está asignada y vence hoy, pero no puede arrancar hasta que termine “Revisar comunicaciones industriales de la comprimidora”.»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” venció el 23 de octubre y tiene 1 día hábil de atraso. Sigue asignada y no puede arrancar hasta que termine “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 8961 ms
- Leda → Marcos: «Anoté que hoy arrancaste “Programar PLC de la comprimidora”. La tarea venció el 23 de octubre y quedó en cola un aviso para mañana a las 9 para volver a pedirte el estado. ¿Para qué fecha»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:25:00-03:00"}}]`
- latencia: 7202 ms
- Leda → Marcos: «Anoté que prevés tener “Programar PLC de la comprimidora” para el miércoles 28. Quedó en cola un aviso para Ismael hoy a las 10:25.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, tiene 3 días hábiles de atraso: la fecha comprometida era el 23/10 y la previsión actual es el 28/10. Depende de Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Habías previsto tener “Programar PLC de la comprimidora” para hoy. Sigue en curso y lleva 3 días hábiles de atraso; el aviso a Ismael ya se envió. ¿En qué estado está ahora?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. Este aviso no necesita respuesta.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” está asignada y vence hoy. Para empezar, primero tiene que terminar “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está la tarea?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” está asignada y tiene 1 día hábil de atraso. Para empezar, primero tiene que terminar “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 8178 ms
- Leda → Marcos: «Quedó anotado que arrancaste hoy. “Programar PLC de la comprimidora” está en curso y tiene 1 día hábil de atraso. Hay un aviso en cola para mañana, 27 de octubre, a»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:25:00-03:00"}}]`
- latencia: 6353 ms
- Leda → Marcos: «Quedó anotado que prevés tener “Programar PLC de la comprimidora” para el miércoles 28. La tarea lleva 3 días hábiles de atraso. El aviso a Ismael está en cola para hoy a las 10:25.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora está a cargo de Marcos Tarquini. La fecha comprometida era el 23/10 y la previsión actual es el 28/10; lleva 3 días hábiles de atraso.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” figura en curso y lleva 3 días hábiles de atraso. Habías previsto tenerla hoy; el aviso a Ismael ya fue enviado. ¿Ya la terminaste?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 5

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-luna`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y no puede arrancar hasta que termine “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” sigue asignada y no puede arrancar hasta que termine “Revisar comunicaciones industriales de la comprimidora”. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 17984 ms
- Leda → Marcos: «Anoté que contás que hoy arrancaste “Programar PLC de la comprimidora”. ¿Para qué fecha estimás terminarla?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:25:00-03:00"}}]`
- latencia: 8232 ms
- Leda → Marcos: «Anoté que estimás terminar “Programar PLC de la comprimidora” el miércoles 28. El aviso a Ismael está en cola para salir hoy a las 10:25.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, tenía fecha comprometida el 23/10 y lleva 3 días hábiles de atraso. La previsión actual es el 28/10. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Habías estimado terminar hoy “Programar PLC de la comprimidora”. El aviso a Ismael ya se envió, y “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termines esta tarea. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

