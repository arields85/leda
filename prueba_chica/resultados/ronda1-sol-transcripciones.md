# Transcripciones de la ronda ronda1-sol

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
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
- latencia: 6062 ms
- Leda → Marcos: «Quedó anotado que arrancaste hoy a la mañana con «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy y sigue en curso. ¿Cómo viene?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 2

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
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
- latencia: 7137 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora” hoy a la mañana. La tarea figura en curso.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y figura en curso. ¿Cómo viene?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 3

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23/10, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
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
- latencia: 6557 ms
- Leda → Marcos: «Quedó anotado que arrancaste esta mañana con «Programar PLC de la comprimidora». La tarea figura en curso.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y figura en curso. ¿Cómo viene?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 4

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
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
- latencia: 6482 ms
- Leda → Marcos: «Quedó anotado que arrancaste hoy a la mañana con «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y está en curso. ¿Cómo venís con la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23/10, en tres días hábiles. No hace falta que respondas a este aviso.»
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
- latencia: 6689 ms
- Leda → Marcos: «Marcos, quedó anotado que empezaste hoy a la mañana «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. ¿Cómo viene la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 02 · Llego el 27, el proveedor se demoró · vez 1

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 7306 ms
- Leda → Marcos: «Marcos, anoté que prevés llegar el 27 de octubre con “Programar PLC de la comprimidora” porque se demoró el proveedor. Son dos días hábiles después de la fecha comprometida, el 23. De esa tarea depende “Revisar comunicaciones industriales de la comprimidora”. El aviso a Ismael está guardado para salir hoy a las 15:40; todavía no se envió.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos prevé terminar «Programar PLC de la comprimidora» el 27/10 porque se demoró el proveedor, dos días hábiles después de la fecha comprometida. De esa tarea depende «Revisar comunicaciones industriales de la comprimidora».»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y sigue en curso. Tenés previsto llegar el 27 de octubre por la demora del proveedor. Ismael ya recibió el aviso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. Te pediré el estado el 27; no hace falta que respondas ahora.»
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Marcos, “Programar PLC de la comprimidora” sigue en curso. Venció el 23 y habías previsto llegar hoy por la demora del proveedor. Ismael ya recibió el aviso. “Revisar comunicaciones industriales de la comprimidora” vence el 30 y no puede arrancar hasta que termine la primera; por ese vencimiento no hace falta que respondas. ¿En qué estado está “Programar PLC de la comprimidora”?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, “Programar PLC de la comprimidora” sigue en curso. Venció el 23, hace tres días hábiles, y ya pasó la fecha que habías previsto por la demora del proveedor. Ismael recibió el aviso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿En qué estado está “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, “Programar PLC de la comprimidora” sigue en curso. Venció el 23, hace cuatro días hábiles, y ya pasó la fecha que habías previsto. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. Si no respondés, se avisará a Ismael; ese aviso todavía no salió. ¿En qué estado está “Programar PLC de la comprimidora”?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: ««Programar PLC de la comprimidora» sigue en curso, con cinco días hábiles de atraso. Marcos no respondió a los tres pedidos de estado desde el 27/10, la fecha que había previsto para terminarla por la demora del proveedor. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «Marcos, “Revisar comunicaciones industriales de la comprimidora” vence hoy y figura como asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 2

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 10312 ms
- Leda → Marcos: «Marcos, anoté que prevés llegar el 27 de octubre con «Programar PLC de la comprimidora» por la demora del proveedor. La fecha comprometida sigue siendo el 23: son dos días hábiles de diferencia y esto afecta a «Revisar comunicaciones industriales de la comprimidora». El aviso a Ismael está guardado para salir hoy a las 15:40; todavía no se envió.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Por una demora del proveedor, la previsión para «Programar PLC de la comprimidora», a cargo de Marcos Tarquini, pasó al 27/10: dos días hábiles después de la fecha comprometida, el 23/10. De esa tarea depende «Revisar comunicaciones industriales de la comprimidora».»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. Sigue anotada tu previsión de llegar el 27 de octubre por la demora del proveedor, dos días hábiles después. Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termines. El pedido de estado está previsto para el 27; todavía no se hizo. No hace falta que respondas a este aviso.»
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso. Venció el 23 de octubre y hoy es la fecha que habías previsto por la demora del proveedor. Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termines y vence el 30 de octubre; ese aviso no requiere respuesta. ¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso. Venció el 23 de octubre y ya pasó el 27, la fecha que habías previsto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termines. ¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso. Venció el 23 de octubre, hace cuatro días hábiles, y ya pasó el 27, la fecha que habías previsto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termines. Si no hay respuesta a este pedido, se avisará a Ismael; eso todavía no ocurrió. ¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos todavía no respondió los tres pedidos de estado enviados desde el 27/10 por «Programar PLC de la comprimidora». La tarea sigue en curso, con cinco días hábiles de atraso respecto del 23/10; la última previsión era el 27/10. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No necesitás responder este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «Marcos, «Revisar comunicaciones industriales de la comprimidora» vence hoy y figura como asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 3

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 13125 ms
- Leda → Marcos: «Marcos, anoté que prevés llegar el 27 de octubre con «Programar PLC de la comprimidora» porque se demoró el proveedor. La fecha comprometida es el 23, así que la previsión queda 2 días hábiles después y afecta a «Revisar comunicaciones industriales de la comprimidora». El aviso a Ismael está guardado para salir hoy a las 15:40; todavía no se envió.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «La programación del PLC de la comprimidora se demoró por el proveedor. Marcos Tarquini la prevé para el 27/10, dos días hábiles después de la fecha comprometida. De esa tarea depende “Revisar comunicaciones industriales de la comprimidora”.»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy. Tengo anotado que prevés llegar el 27 de octubre porque el proveedor se demoró. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Ismael ya recibió el aviso; te pediré el estado el 27. No hace falta que respondas ahora.»
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23 y habías previsto llegar hoy, tras la demora del proveedor. Ismael ya recibió el aviso.

«Revisar comunicaciones industriales de la comprimidora» vence el 30 y no puede arrancar hasta que termine la programación. No hace falta que respondas por ese vencimiento. ¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23 y la fecha que habías previsto, el 27, ya pasó. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» sigue en curso: venció el 23 de octubre, hace 4 días hábiles, y la fecha que habías previsto, el 27, ya pasó. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no respondés, está previsto avisar a Ismael por la falta de respuesta; ese aviso todavía no salió.

¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence hoy y figura asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «“Programar PLC de la comprimidora” sigue en curso, con cinco días hábiles de atraso. Marcos no respondió los tres pedidos de estado desde el 27/10, que era su última previsión. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. No necesitás responder este mensaje.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 10327 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el 27 de octubre por la demora del proveedor. La fecha comprometida sigue siendo el 23: son dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. El aviso a Ismael está guardado para salir hoy a las 15:40; todavía no se envió.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: ««Programar PLC de la comprimidora», a cargo de Marcos Tarquini, se demora por el proveedor. La previsión es el 27/10, dos días hábiles después de la fecha comprometida. De esta tarea depende «Revisar comunicaciones industriales de la comprimidora».»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. Tengo anotada tu previsión de terminarla el 27 de octubre por la demora del proveedor, dos días hábiles después. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Ismael ya recibió el aviso. El 27 te voy a pedir el estado; hoy no hace falta que respondas.»
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23 de octubre y tenías previsto terminarla hoy por la demora del proveedor. Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine y vence el 30 de octubre.

¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23 de octubre, hace tres días hábiles, y la fecha que habías previsto para terminarla fue ayer. Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine.

¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23 de octubre, hace cuatro días hábiles, y ya pasó la fecha que habías previsto para terminarla. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Ismael recibió el aviso de tu previsión; todavía no se le avisó por la falta de respuesta.

¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: ««Programar PLC de la comprimidora», a cargo de Marcos Tarquini, sigue en curso y lleva cinco días hábiles de atraso. La previsión del 27/10 ya pasó y no hubo respuesta a tres pedidos de estado. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence hoy y figura como asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 5

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}}]`
- latencia: 8307 ms
- Leda → Marcos: «Anoté que estimás llegar el 27 de octubre con «Programar PLC de la comprimidora» por la demora del proveedor. La fecha comprometida sigue siendo el 23, y «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. El aviso a Ismael está guardado, todavía no se envió; está previsto para hoy a las 15:40.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: ««Programar PLC de la comprimidora», a cargo de Marcos Tarquini, se demoró por el proveedor. Estaba comprometida para el 23/10 y la previsión es el 27/10, dos días hábiles después. De esta tarea depende «Revisar comunicaciones industriales de la comprimidora».»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy y sigue en curso. Tengo anotada tu previsión para el 27 de octubre por la demora del proveedor; Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas a este aviso.»
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23 y tenías previsto llegar hoy por la demora del proveedor; Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine y vence el 30. Por ese vencimiento no hace falta que respondas. ¿Cómo va «Programar PLC de la comprimidora»?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso: venció el 23 y la previsión que me diste para el 27 ya pasó. Ismael recibió el aviso, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo va «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» sigue en curso: venció el 23, hace 4 días hábiles, y la previsión que me diste para el 27 ya pasó. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Ismael recibió el aviso de tu previsión; si no respondés, se le avisará que seguimos sin novedades, pero ese aviso todavía no salió. ¿Cómo va «Programar PLC de la comprimidora»?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: ««Programar PLC de la comprimidora», a cargo de Marcos Tarquini, sigue en curso y lleva cinco días hábiles de atraso. La previsión era el 27/10, pero todavía no hubo respuesta a los tres pedidos de estado desde esa fecha. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence hoy y sigue asignada. ¿Cómo va esa tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3906 ms
- Leda → Marcos: «Anoté que estás trabado con «Programar PLC de la comprimidora» porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: ««Programar PLC de la comprimidora» sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarla?»
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
- latencia: 6338 ms
- Leda → Marcos: «Anoté que no sabés quién está comprando el repuesto para «Programar PLC de la comprimidora». ¿Preferís pedir ayuda para destrabarla o anotar una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 9921 ms
- Leda → Marcos: «Entiendo, hay que esperar a que llegue el repuesto para «Programar PLC de la comprimidora». Cerré la consulta sobre pedir ayuda o anotar una previsión; no se anotó nada nuevo.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Marcos, «Revisar comunicaciones industriales de la comprimidora» vence el 30 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 2

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3862 ms
- Leda → Marcos: «Marcos, anoté que estás trabado en «Programar PLC de la comprimidora» porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarla?»
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
- latencia: 8174 ms
- Leda → Marcos: «Anoté que no sabés quién está comprando el repuesto para «Programar PLC de la comprimidora». ¿Querés que alguien te ayude a averiguarlo o preferís anotar una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 7100 ms
- Leda → Marcos: «Entendido, para «Programar PLC de la comprimidora» hay que esperar a que llegue el repuesto. No anoté nada nuevo.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Marcos, «Revisar comunicaciones industriales de la comprimidora» vence el 30 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 3

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3840 ms
- Leda → Marcos: «Marcos, anoté que estás trabado con «Programar PLC de la comprimidora» porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «Marcos, sigo pendiente de saber quién puede destrabar «Programar PLC de la comprimidora», que está bloqueada porque falta el repuesto. ¿Quién puede conseguirlo?»
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
- latencia: 7028 ms
- Leda → Marcos: «Anoté que no sabés quién está comprando el repuesto para «Programar PLC de la comprimidora». Me decís que lo pidieron hace dos semanas. ¿Preferís que alguien ayude a averiguarlo o anotar una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 7791 ms
- Leda → Marcos: «Entiendo, Marcos: por ahora hay que esperar a que llegue el repuesto para «Programar PLC de la comprimidora». Dejé de lado la propuesta de pedir ayuda o anotar una previsión; no se anotó nada nuevo.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Marcos, «Revisar comunicaciones industriales de la comprimidora» vence el 30 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 4

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4866 ms
- Leda → Marcos: «Anoté que estás trabado con «Programar PLC de la comprimidora» porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: ««Programar PLC de la comprimidora» sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarla?»
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
- latencia: 6901 ms
- Leda → Marcos: «Anoté que no sabés quién puede destrabar «Programar PLC de la comprimidora». Entiendo que el repuesto se pidió hace dos semanas. ¿Preferís que alguien te ayude o anotar una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 7129 ms
- Leda → Marcos: «Entendido, hay que esperar a que llegue el repuesto. No anoté nada nuevo para «Programar PLC de la comprimidora».»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Marcos, «Revisar comunicaciones industriales de la comprimidora» vence el 30 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 03 · Estoy trabado, falta el repuesto · vez 5

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3729 ms
- Leda → Marcos: «Marcos, anoté que estás trabado con “Programar PLC de la comprimidora” porque falta el repuesto. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «“Programar PLC de la comprimidora” sigue bloqueada porque falta el repuesto. ¿Quién puede destrabarlo?»
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
- latencia: 8286 ms
- Leda → Marcos: «Anoté que no sabés quién está comprando el repuesto para “Programar PLC de la comprimidora”. ¿Querés que alguien te ayude o preferís que anotemos una previsión?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 6997 ms
- Leda → Marcos: «Entendido: para “Programar PLC de la comprimidora” hay que esperar a que llegue el repuesto. No anoté nada nuevo.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: un próximo paso (puede avisar cuando llegue el repuesto)
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Marcos, te recuerdo que “Revisar comunicaciones industriales de la comprimidora” vence el 30 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27/10, dentro de tres días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció ayer y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el 27/10 y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no hay respuesta, está previsto avisarle a Ismael; todavía no se le avisó. ¿Cómo viene la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: ««Programar PLC de la comprimidora», a cargo de Marcos Tarquini, sigue en curso y lleva tres días hábiles de atraso. No hubo respuesta a los tres pedidos de estado. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No necesitás responder este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 2

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 27 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y sigue en curso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cómo venís con la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” venció ayer y sigue en curso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cómo venís con la programación del PLC?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” sigue en curso y venció hace 2 días hábiles. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. Si no respondés, se avisará a Ismael Soschinski; todavía no se le avisó. ¿Cómo venís con la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, sigue en curso. Venció el 27/10 y lleva tres días hábiles de atraso. No hubo respuesta a los tres pedidos de estado, y Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No necesitás responder a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 3

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció ayer y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, «Programar PLC de la comprimidora» lleva 2 días hábiles de atraso y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no hay respuesta, se avisará a Ismael Soschinski; todavía no se le avisó. ¿Cómo viene la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Seguimos sin respuesta sobre “Programar PLC de la comprimidora” después de tres pedidos de estado. La tarea está a cargo de Marcos, venció el 27/10 y lleva tres días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 4

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso y venció ayer. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso y venció hace 2 días hábiles. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no hay respuesta, se avisará a Ismael; todavía no se le avisó. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Todavía no hubo respuesta a los tres pedidos de estado de «Programar PLC de la comprimidora» desde el 27/10. La tarea, a cargo de Marcos Tarquini, sigue en curso y lleva 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede empezar hasta que termine. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 5

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27/10, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y está en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo venís con la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso y venció ayer. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo venís con la programación del PLC?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso y lleva dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no respondés, se le avisará a Ismael Soschinski; todavía no se le avisó. ¿Cómo venís con la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Ismael, seguimos sin respuesta de Marcos sobre el estado de “Programar PLC de la comprimidora”, pese a tres pedidos. La tarea venció el 27/10 y lleva tres días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. No necesitás responder este aviso.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 05 · Varias cosas en un mensaje · vez 1

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea «Programar PLC de la comprimidora» vence el 23 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 8512 ms
- Leda → Marcos: «Anoté que arrancaste con «Programar PLC de la comprimidora». Para «Revisar comunicaciones industriales de la comprimidora», quedó anotada tu previsión del 4 de noviembre, en vez del 30 de octubre, porque esperás el switch nuevo. El aviso a Ismael está guardado para salir hoy a las 10:05; todavía no se envió.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Para «Revisar comunicaciones industriales de la comprimidora» se está esperando el switch nuevo. La previsión es el 4/11, tres días hábiles después de la fecha comprometida del 30/10. El responsable es Marcos Tarquini.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 11244 ms
- Leda → Marcos: «Anoté que estás trabado con «Programar PLC de la comprimidora». También corregí tu previsión para «Revisar comunicaciones industriales de la comprimidora»: quedó para el jueves 5 de noviembre, en lugar del 4. El aviso a Ismael está guardado para salir hoy a las 16:30; todavía no se envió.

¿Quién te puede ayudar a destrabar lo del PLC?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con el plc'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con el plc', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con el plc', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'motivo': None, 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-20T16:30:00-03:00'}}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 5689 ms
- Leda → Marcos: «Anoté que para destrabar «Programar PLC de la comprimidora» necesitás que Martín de IT te habilite el acceso a la red de planta.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de IT', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de IT'}}]

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 17077 ms
- Leda → Marcos: «Anoté que arrancaste «Programar PLC de la comprimidora»; quedó en curso. Para «Revisar comunicaciones industriales de la comprimidora», anoté tu previsión del 4 de noviembre, en lugar del 30 de octubre, porque esperás el switch nuevo. El aviso a Ismael está guardado, todavía no se envió; está previsto para hoy a las 10:05.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: ««Revisar comunicaciones industriales de la comprimidora» figura con 3 días hábiles de atraso por la espera del switch nuevo. La fecha comprometida es el 30 de octubre y Marcos Tarquini prevé el 4 de noviembre.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 12647 ms
- Leda → Marcos: «Anoté el 5 de noviembre como nueva previsión para «Revisar comunicaciones industriales de la comprimidora», en lugar del 4. El aviso a Ismael está guardado, todavía no se envió; está previsto para hoy a las 16:30.

¿Qué te está trabando con «Programar PLC de la comprimidora»?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 5846 ms
- Leda → Marcos: «Anoté que «Programar PLC de la comprimidora» está bloqueada porque te falta que Martín de IT te habilite el acceso a la red de planta. También anoté que él puede destrabarlo.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 3

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 13813 ms
- Leda → Marcos: «Anoté que empezaste «Programar PLC de la comprimidora» y quedó en curso. Para «Revisar comunicaciones industriales de la comprimidora», anoté que preveés terminar el miércoles 4 de noviembre, en lugar del 30 de octubre, porque esperás el switch nuevo. El aviso a Ismael está guardado para salir hoy a las 10:05; todavía no se envió.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «En “Revisar comunicaciones industriales de la comprimidora”, Marcos Tarquini espera el switch nuevo. La previsión es el 4/11, tres días hábiles después de la fecha comprometida del 30/10.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 8775 ms
- Leda → Marcos: «Anoté que preveés terminar «Revisar comunicaciones industriales de la comprimidora» el jueves 5 de noviembre, en lugar del 30 de octubre. El aviso a Ismael está guardado para salir hoy a las 16:30; todavía no se envió. Para anotar el bloqueo en «Programar PLC de la comprimidora», ¿qué te está trabando?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 6518 ms
- Leda → Marcos: «Anoté el bloqueo en «Programar PLC de la comprimidora»: te falta que Martín de IT te habilite el acceso a la red de planta. También anoté que él es quien puede destrabarlo.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 4

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 7153 ms
- Leda → Marcos: «Anoté que arrancaste con «Programar PLC de la comprimidora». Para «Revisar comunicaciones industriales de la comprimidora», anoté tu previsión del 4 de noviembre en lugar del 30 de octubre, porque esperás el switch nuevo. El aviso a Ismael quedó guardado para salir hoy a las 10:05; todavía no se envió.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos está esperando el switch nuevo para «Revisar comunicaciones industriales de la comprimidora». La previsión es el 4/11, tres días hábiles después de la fecha comprometida del 30/10.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 12413 ms
- Leda → Marcos: «Anoté tu nueva previsión para «Revisar comunicaciones industriales de la comprimidora»: jueves 5 de noviembre. El aviso a Ismael quedó guardado para salir hoy a las 16:30; todavía no se envió.

Para anotar el bloqueo en «Programar PLC de la comprimidora», ¿qué te está trabando?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 5856 ms
- Leda → Marcos: «Anoté que «Programar PLC de la comprimidora» está bloqueada porque te falta el acceso a la red de planta, y que Martín de IT es quien puede destrabarlo.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 5

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23/10, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}}]`
- latencia: 11504 ms
- Leda → Marcos: «Marcos, quedó anotado que empezaste «Programar PLC de la comprimidora». También registré que preveés terminar «Revisar comunicaciones industriales de la comprimidora» el 4/11, en lugar del 30/10, porque esperás el switch nuevo. El aviso a Ismael está preparado para salir hoy a las 10:05; todavía no se envió.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «En «Revisar comunicaciones industriales de la comprimidora» falta el switch nuevo. La previsión es el 4/11, tres días hábiles después de la fecha comprometida del 30/10. El responsable es Marcos Tarquini.»
  - hechos: `{"tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 9717 ms
- Leda → Marcos: «Quedó anotado que estás trabado con «Programar PLC de la comprimidora». También corregí tu previsión para «Revisar comunicaciones industriales de la comprimidora» al 5/11. El aviso a Ismael quedó preparado para salir hoy a las 16:30; todavía no se envió. ¿Quién puede ayudarte a destrabar el PLC?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'con el plc'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'con el plc', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'con el plc', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'motivo': None, 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 4, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-20T16:30:00-03:00'}}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}, real {'tipo': 'quien_destraba', 'tarea': 'PLC'}

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- latencia: 5202 ms
- Leda → Marcos: «Quedó anotado que necesitás que Martín de IT te habilite el acceso a la red de planta para destrabar «Programar PLC de la comprimidora».»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real [{'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de IT', 'no_sabe': False, 'nadie_mas': False}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de IT'}}]

## 06 · No, era la otra tarea · vez 1

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5924 ms
- Leda → Marcos: «Quedó anotado que arrancaste esta mañana con “Programar PLC de la comprimidora”. La tarea está en curso.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 7908 ms
- Leda → Marcos: «Corregí la anotación: “Programar PLC de la comprimidora” volvió a estar asignada, y quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy. ¿Cómo viene la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 8882 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste esta mañana con «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 5194 ms
- Leda → Marcos: «Tenés razón, confundí las tareas. «Programar PLC de la comprimidora» volvió a estar asignada, sin inicio anotado, y «Revisar comunicaciones industriales de la comprimidora» quedó en curso.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue asignada. ¿Cómo venís con esa tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 3

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23/10, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5494 ms
- Leda → Marcos: «Quedó anotado que arrancaste esta mañana con «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 5836 ms
- Leda → Marcos: «Tenés razón, Marcos. Corregí el registro: «Programar PLC de la comprimidora» volvió a asignada, y quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora».»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 4

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 6131 ms
- Leda → Marcos: «Quedó anotado que arrancaste esta mañana con «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 5565 ms
- Leda → Marcos: «Corregido: «Programar PLC de la comprimidora» volvió a estar asignada, y quedó anotado el inicio de «Revisar comunicaciones industriales de la comprimidora», que ahora está en curso.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy y figura asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 8605 ms
- Leda → Marcos: «Quedó anotado que arrancaste esta mañana con “Programar PLC de la comprimidora”. La tarea está en curso.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "tarea": "PLC", "corrige": "anotar_inicio", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 4884 ms
- Leda → Marcos: «Tenés razón, Marcos. Corregí el inicio: “Programar PLC de la comprimidora” volvió a estar asignada, y quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”, que ahora está en curso.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y sigue asignada. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 07 · Dejá, no importa · vez 1

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4010 ms
- Leda → Marcos: «Entiendo que estás trabado con “Programar PLC de la comprimidora”. Para poder anotar el bloqueo, ¿qué es lo que te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 7070 ms
- Leda → Marcos: «Está bien, dejamos ahí lo de “Programar PLC de la comprimidora”. No quedó anotado ningún bloqueo.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y sigue en curso. ¿Cómo venís con la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5096 ms
- Leda → Marcos: «Entiendo. Me falta la causa del bloqueo en “Programar PLC de la comprimidora”. ¿Qué te está trabando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4707 ms
- Leda → Marcos: «Está bien, dejamos ahí lo de “Programar PLC de la comprimidora”. No quedó anotado ningún bloqueo.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y sigue en curso. ¿En qué estado está?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 3

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4194 ms
- Leda → Marcos: «Entiendo que estás trabado con “Programar PLC de la comprimidora”. ¿Qué te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4723 ms
- Leda → Marcos: «Está bien, dejamos ahí lo de “Programar PLC de la comprimidora”. No quedó anotado ningún bloqueo.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y sigue en curso. ¿Cómo viene la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5091 ms
- Leda → Marcos: «Entiendo que estás trabado con “Programar PLC de la comprimidora”. Para poder anotar el bloqueo, ¿qué es lo que te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 3796 ms
- Leda → Marcos: «Está bien, dejamos ahí lo de “Programar PLC de la comprimidora”. No se anotó ningún bloqueo.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy y figura en curso. ¿Cómo viene la tarea?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 5

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea «Programar PLC de la comprimidora» vence el 23 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 3586 ms
- Leda → Marcos: «¿Qué te está trabando con «Programar PLC de la comprimidora»?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5274 ms
- Leda → Marcos: «Está bien, Marcos. Dejamos ahí lo de «Programar PLC de la comprimidora»; no quedó anotado ningún bloqueo.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: un próximo paso (que puede avisar si se traba)
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. ¿Cómo viene?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 08 · Cambio de tema · vez 1

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 6837 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». Para anotar el bloqueo, me falta saber la causa. ¿Qué te está frenando?»
- [ ] dice: una pregunta por la causa

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 8827 ms
- Leda → Marcos: «Anoté que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el 4 de noviembre, porque no llegás al 30 de octubre. El aviso a Ismael está pendiente de envío para hoy a las 10:43.

Sobre «Programar PLC de la comprimidora», ¿qué te está frenando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:cd322c6d-de85-4b8d-837d-7e5b1e9bf6bd', 'outbox_id': None}]

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Revisar comunicaciones industriales de la comprimidora» el 4 de noviembre. No llega a la fecha comprometida del 30 de octubre: son tres días hábiles de diferencia.»
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
- latencia: 5536 ms
- Leda → Marcos: «Anoté que estás trabado con «Programar PLC de la comprimidora» porque no te mandaron el programa del fabricante. ¿Quién puede ayudarte a destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 2

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea «Programar PLC de la comprimidora» vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4710 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está bloqueando?»
- [ ] dice: una pregunta por la causa

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 9357 ms
- Leda → Marcos: «Anoté que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el 4 de noviembre; la fecha comprometida es el 30 de octubre. El aviso a Ismael está guardado, todavía no se envió. Está previsto para hoy a las 10:43.

Y sobre «Programar PLC de la comprimidora», ¿qué te está bloqueando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30, necesito hasta el miercoles 4'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:8a8bb85c-e2e6-45d9-b9fa-1696dbe0bfc5', 'outbox_id': None}]

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini avisó que no llega al 30/10 con Revisar comunicaciones industriales de la comprimidora y prevé terminar el miércoles 4/11, tres días hábiles después de la fecha comprometida.»
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
- latencia: 3996 ms
- Leda → Marcos: «Anoté que no te mandaron el programa del fabricante y que eso te bloquea con «Programar PLC de la comprimidora». ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 3

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23/10. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4557 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». Para poder anotar el bloqueo, ¿qué te está frenando?»
- [ ] dice: una pregunta por la causa

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 11435 ms
- Leda → Marcos: «Anoté tu previsión del 4/11 para «Revisar comunicaciones industriales de la comprimidora»; la fecha comprometida sigue siendo el 30/10. El aviso a Ismael está guardado para salir hoy a las 10:43, pero todavía no se envió.

Sobre «Programar PLC de la comprimidora», ¿qué te está frenando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30, necesito hasta el miercoles 4'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30, necesito hasta el miercoles 4', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:bcc1d559-dabc-4c27-aa87-82a0402439fb', 'outbox_id': None}]

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini no llega al 30 de octubre con “Revisar comunicaciones industriales de la comprimidora”, la fecha comprometida. Prevé terminar el miércoles 4 de noviembre, 3 días hábiles después.»
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
- latencia: 4139 ms
- Leda → Marcos: «Anoté que estás trabado con «Programar PLC de la comprimidora» porque no te mandaron el programa del fabricante. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 4

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5446 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está frenando?»
- [ ] dice: una pregunta por la causa

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 9378 ms
- Leda → Marcos: «Anoté que para «Revisar comunicaciones industriales de la comprimidora» prevés llegar el 4 de noviembre; la fecha comprometida es el 30 de octubre. El aviso a Ismael está guardado, pero todavía no se envió.

Y con «Programar PLC de la comprimidora», ¿qué te está frenando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:24eef773-9ac6-4f65-9f09-a569309d22b3', 'outbox_id': None}]

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini no llega al 30 de octubre con «Revisar comunicaciones industriales de la comprimidora». Prevé terminarla el 4 de noviembre, tres días hábiles después de la fecha comprometida.»
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
- latencia: 4935 ms
- Leda → Marcos: «Anoté que «Programar PLC de la comprimidora» está trabada porque no te mandaron el programa del fabricante. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 5

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4212 ms
- Leda → Marcos: «Entiendo que estás trabado con “Programar PLC de la comprimidora”. Para poder anotar el bloqueo, ¿qué te está frenando?»
- [ ] dice: una pregunta por la causa

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "no llego al 30", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 7755 ms
- Leda → Marcos: «Anoté que para “Revisar comunicaciones industriales de la comprimidora” necesitás hasta el 4 de noviembre porque no llegás al 30 de octubre. El aviso a Ismael está guardado para salir hoy a las 10:43; todavía no se envió.

Sobre “Programar PLC de la comprimidora”, ¿qué te está frenando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'no llego al 30', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'tarea': 'COM', 'motivo': 'no llego al 30', 'prevision': '2026-11-04', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3}, 'clave': 'motor:nueva_prevision:fa57aff7-9d7b-4dab-8a97-cf896dd01b39', 'outbox_id': None}]

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini no llega al 30/10 con “Revisar comunicaciones industriales de la comprimidora”. Prevé terminarla el 4/11, tres días hábiles después de la fecha comprometida.»
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
- latencia: 7906 ms
- Leda → Marcos: «Anoté que estás trabado con “Programar PLC de la comprimidora” porque no te mandaron el programa del fabricante. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 09 · Duda: ¿de qué tarea habla? · vez 1

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5212 ms
- Leda → Marcos: «¿En cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}}]`
- latencia: 1423 ms
- Leda → Marcos: «Quedó anotado que arrancaste con “Revisar comunicaciones industriales de la comprimidora”. La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 2

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6456 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribirla.» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}}]`
- latencia: 1620 ms
- Leda → Marcos: «Quedó anotado que arrancaste con “Revisar comunicaciones industriales de la comprimidora”. La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 3

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6227 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}}]`
- latencia: 1654 ms
- Leda → Marcos: «Quedó anotado que arrancaste con Revisar comunicaciones industriales de la comprimidora. La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 4

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6251 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}}]`
- latencia: 1462 ms
- Leda → Marcos: «Quedó anotado que hoy arrancaste con Revisar comunicaciones industriales de la comprimidora. La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 5

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: ERROR.

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
- latencia: 7042 ms
- Leda → Marcos: «¿Con qué tarea arrancaste hoy?»
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio'}], real []
- **falla** [comprension] botones: esperado ['PLC', 'COM'], real []
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'cual_tarea'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'cual_tarea'}, real None

## 10 · Escribir en lugar de tocar un botón · vez 1

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4807 ms
- Leda → Marcos: «Para anotar el inicio, necesito saber cuál de estas tareas arrancaste: ¿“Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}}]`
- latencia: 4860 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”; está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4944 ms
- Leda → Marcos: «Para anotar el inicio, necesito saber cuál de las tareas de la comprimidora arrancaste. ¿Fue «Programar PLC de la comprimidora» o «Revisar comunicaciones industriales de la comprimidora»? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}}]`
- latencia: 4787 ms
- Leda → Marcos: «Quedó anotado que arrancaste «Programar PLC de la comprimidora»; está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4455 ms
- Leda → Marcos: «Para anotar el inicio, me falta saber cuál de las tareas arrancaste. ¿Fue “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}}]`
- latencia: 4505 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”; está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC

## 10 · Escribir en lugar de tocar un botón · vez 4

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4157 ms
- Leda → Marcos: «¿Cuál de estas arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}}]`
- latencia: 5455 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4265 ms
- Leda → Marcos: «Para anotar el inicio, necesito saber cuál de las tareas de la comprimidora arrancaste. ¿Fue “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}}]`
- latencia: 5317 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”; está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos empezaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”. Está en curso.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 1926 ms
- Leda → Marcos: «La elección de “Revisar comunicaciones industriales de la comprimidora” no cambió nada: esa pregunta ya se había cerrado con “Programar PLC de la comprimidora”.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5075 ms
- Leda → Marcos: «Quedó anotado que hoy empezaste “Revisar comunicaciones industriales de la comprimidora”. Está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- latencia: 9095 ms
- Leda → Marcos: «Anoté que preveés terminar “Revisar comunicaciones industriales de la comprimidora” el 4 de noviembre porque estás esperando el switch. La fecha comprometida era el 30 de octubre. El aviso a Ismael quedó guardado para salir el 23 de octubre a las 9; todavía no se envió. ¿Quién puede destrabar lo del switch?»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}, {'nombre': 'anotar_bloqueo', 'tarea': 'COM', 'causa': 'espero el switch'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'COM', 'causa': 'espero el switch', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'motivo': 'espero el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-23T09:00:00-03:00'}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'COM', 'causa': 'espero el switch', 'pregunta': 'quien_destraba'}]

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- latencia: 12377 ms
- Leda → Marcos: «Quedó anotado que preveés terminar “Revisar comunicaciones industriales de la comprimidora” el 30 de octubre porque llegó el switch. El aviso sobre la previsión del 4 de noviembre se retiró sin enviarse. No pude cancelar la pregunta que había quedado pendiente: ¿quién puede destrabar lo del switch?»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'cancelar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch', 'es_correccion': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': True}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'aviso_de_la_prevision_corregida': {'estado': 'retirado_sin_enviar'}}, {'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'COM'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': 'llego el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 2

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos empezaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”. Está en curso.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 1992 ms
- Leda → Marcos: «La elección de “Revisar comunicaciones industriales de la comprimidora” no cambió nada: esa pregunta ya se había cerrado con “Programar PLC de la comprimidora”.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 3879 ms
- Leda → Marcos: «Quedó anotado que hoy empezaste “Revisar comunicaciones industriales de la comprimidora”. Está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- latencia: 9455 ms
- Leda → Marcos: «Quedó anotada tu previsión del 4 de noviembre para “Revisar comunicaciones industriales de la comprimidora”, que estaba comprometida para el 30 de octubre, y que estás esperando el switch. El aviso a Ismael está guardado para salir mañana a las 9; todavía no se envió. ¿Quién puede destrabar lo del switch?»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}, {'nombre': 'anotar_bloqueo', 'tarea': 'COM', 'causa': 'espero el switch'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'COM', 'causa': 'espero el switch', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'motivo': 'espero el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-23T09:00:00-03:00'}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'COM', 'causa': 'espero el switch', 'pregunta': 'quien_destraba'}]

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- latencia: 10164 ms
- Leda → Marcos: «Quedó corregida la previsión de “Revisar comunicaciones industriales de la comprimidora” al 30 de octubre, la fecha comprometida, porque llegó el switch. El aviso sobre el 4 de noviembre se retiró sin enviarse. La pregunta anterior no se pudo cancelar y sigue pendiente: ¿quién podía destrabar lo del switch?»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'cancelar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch', 'es_correccion': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': True}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'aviso_de_la_prevision_corregida': {'estado': 'retirado_sin_enviar'}}, {'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'COM'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': 'llego el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 3

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribirla.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste «Programar PLC de la comprimidora». La tarea está en curso.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 1646 ms
- Leda → Marcos: «Esa pregunta ya se cerró con «Programar PLC de la comprimidora». Tocar «Revisar comunicaciones industriales de la comprimidora» no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5441 ms
- Leda → Marcos: «Ah, entendí: también arrancaste hoy «Revisar comunicaciones industriales de la comprimidora». Quedó anotada y está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- latencia: 9071 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el 4/11, en lugar del 30/10, y que estás esperando el switch. El aviso a Ismael está guardado, todavía no se envió; está previsto para mañana a las 9. ¿Quién puede destrabar lo del switch?»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}, {'nombre': 'anotar_bloqueo', 'tarea': 'COM', 'causa': 'espero el switch'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'COM', 'causa': 'espero el switch', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'motivo': 'espero el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-23T09:00:00-03:00'}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'COM', 'causa': 'espero el switch', 'pregunta': 'quien_destraba'}]

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "informar_avance", "tarea": "COM", "palabras": "llego el switch"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "informar_avance", "resultado": "no_se_puede", "motivo": "nadie_pidio_el_estado", "tarea": "COM"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- latencia: 12184 ms
- Leda → Marcos: «Para «Revisar comunicaciones industriales de la comprimidora», quedó anotada la previsión del 30/10, la fecha comprometida. El aviso por la previsión del 4/11 se retiró sin enviarse. No pude anotar la llegada del switch como avance porque no te había pedido el estado. La pregunta anterior sigue pendiente: ¿quién podía destrabar lo del switch?»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'cancelar'}, {'nombre': 'informar_avance', 'tarea': 'COM', 'palabras': 'llego el switch'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': None, 'es_correccion': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': True}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'aviso_de_la_prevision_corregida': {'estado': 'retirado_sin_enviar'}}, {'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'COM'}}, {'jugada': 'informar_avance', 'resultado': 'no_se_puede', 'motivo': 'nadie_pidio_el_estado', 'tarea': 'COM'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': None, 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 4

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribirla.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”. La tarea está en curso.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 1811 ms
- Leda → Marcos: «La pregunta ya se había cerrado con “Programar PLC de la comprimidora”. Al tocar “Revisar comunicaciones industriales de la comprimidora”, no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5814 ms
- Leda → Marcos: «Ah, entendí: también arrancaste hoy “Revisar comunicaciones industriales de la comprimidora”. Quedó anotada como en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- latencia: 6960 ms
- Leda → Marcos: «Quedó anotado que preveés terminar “Revisar comunicaciones industriales de la comprimidora” el 4 de noviembre, en lugar del 30 de octubre, porque estás esperando el switch. El aviso a Ismael está guardado, todavía no se envió; sale mañana a las 9. ¿Quién puede destrabar lo del switch?»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}, {'nombre': 'anotar_bloqueo', 'tarea': 'COM', 'causa': 'espero el switch'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'COM', 'causa': 'espero el switch', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'motivo': 'espero el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-23T09:00:00-03:00'}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'COM', 'causa': 'espero el switch', 'pregunta': 'quien_destraba'}]

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- latencia: 13241 ms
- Leda → Marcos: «Quedó corregida al 30 de octubre la previsión para “Revisar comunicaciones industriales de la comprimidora”, porque llegó el switch. El aviso por la fecha del 4 de noviembre se retiró sin enviar. La pregunta que había quedado pendiente no se pudo cancelar: ¿quién podía destrabar lo del switch?»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'cancelar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch', 'es_correccion': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': True}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'aviso_de_la_prevision_corregida': {'estado': 'retirado_sin_enviar'}}, {'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'COM'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': 'llego el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 5

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora? Podés elegir una opción o escribirme el título.» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora. Está en curso.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 1797 ms
- Leda → Marcos: «Esa pregunta ya se cerró con Programar PLC de la comprimidora. Al elegir ahora Revisar comunicaciones industriales de la comprimidora, no cambió nada.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: un próximo paso (puede decir qué quería sobre la de comunicaciones)
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 5298 ms
- Leda → Marcos: «Quedó anotado que también arrancaste Revisar comunicaciones industriales de la comprimidora. Está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- latencia: 9734 ms
- Leda → Marcos: «Quedó anotada tu previsión del 4/11 para Revisar comunicaciones industriales de la comprimidora, y que estás esperando el switch. La fecha comprometida era el 30/10. El aviso a Ismael está guardado para salir mañana a las 9; todavía no se envió. ¿Quién puede destrabar lo del switch?»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] no dice: que Ismael ya se enteró
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}, {'nombre': 'anotar_bloqueo', 'tarea': 'COM', 'causa': 'espero el switch'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'COM': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'COM', 'causa': 'espero el switch', 'resuelto': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '~2026-10-23T09:00'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'motivo': 'espero el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 3, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-23T09:00:00-03:00'}}, {'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'COM', 'causa': 'espero el switch', 'pregunta': 'quien_destraba'}]

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- latencia: 11582 ms
- Leda → Marcos: «Quedó anotado que llegó el switch y que tu previsión para Revisar comunicaciones industriales de la comprimidora vuelve al 30/10. El aviso sobre el 4/11 se retiró sin enviarse.

Sigue pendiente la pregunta anterior: ¿quién podía destrabar lo del switch?»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'puede_traer': ['motivo']}], real [{'nombre': 'corregir', 'tarea': 'COM', 'corrige': 'anotar_prevision'}, {'nombre': 'cancelar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-30'}], real [{'tarea': 'COM', 'fecha': '2026-10-30', 'motivo': 'llego el switch', 'es_correccion': False}]
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'quien_destraba', 'tarea': 'COM', 'desde_antes': True}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'sin_aviso': 'misma_fecha_comprometida'}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'COM', 'vuelve_a': {'fecha_comprometida': '2026-10-30'}, 'prevision_corregida': '2026-11-04', 'aviso_de_la_prevision_corregida': {'estado': 'retirado_sin_enviar'}}, {'jugada': 'cancelar', 'resultado': 'no_se_puede', 'motivo': 'la_pregunta_espera_respuesta', 'pregunta': {'tipo': 'quien_destraba', 'tarea': 'COM'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-30', 'motivo': 'llego el switch', 'fecha_comprometida': '2026-10-30', 'atraso_dias_habiles': 0, 'dependientes': [], 'aviso_al_referente': None, 'sin_aviso': 'misma_fecha_comprometida'}]

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 12 · Algo que no está en la lista · vez 1

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6493 ms
- Leda → Marcos: «No puedo pasarle “Programar PLC de la comprimidora” a Nahuel por chat; el cambio de responsable lo decide Ismael Soschinski. ¿Querés que anote una previsión para esa tarea?»
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
- latencia: 8218 ms
- Leda → Marcos: «Entendido, seguís con “Programar PLC de la comprimidora”. No anoté ninguna previsión. La tarea ya figura en curso, así que no puedo registrar otro inicio.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 5438 ms
- Leda → Marcos: «No puedo recordarte el turno con el médico el viernes. Por acá solo hago seguimiento de las tareas del equipo.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaron a alguien sobre el pedido de recordatorio del turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 5279 ms
- Leda → Marcos: «Todavía no. Hay un aviso para el administrador en cola, pero aún no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Pregunta si le avisaron a alguien sobre el pedido de recordatorio del turno con el médico'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 4216 ms
- Leda → Marcos: «Entiendo que terminaste “Programar PLC de la comprimidora”, pero la entrega todavía no se recibe por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6059 ms
- Leda → Marcos: «Te figuran dos tareas pendientes: “Programar PLC de la comprimidora” (en curso, vence el 23/10) y “Revisar comunicaciones industriales de la comprimidora” (asignada, vence el 30/10). La del PLC sigue figurando en curso, aunque me contaste que la terminaste; la entrega no se recibe por chat.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 2

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6892 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; el cambio de responsable lo decide Ismael Soschinski. ¿Querés que anote una previsión para esa tarea?»
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
- latencia: 8479 ms
- Leda → Marcos: «Entendido, no quedó anotada ninguna previsión para «Programar PLC de la comprimidora». La tarea ya figura en curso, así que no puedo registrar otro inicio.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 7435 ms
- Leda → Marcos: «No puedo recordarte el turno médico el viernes; solo hago seguimiento de las tareas del equipo.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si se le avisó a alguien sobre su pedido de recordatorio del turno médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 8171 ms
- Leda → Marcos: «Sobre tu pedido de recordatorio, hay un aviso al administrador en cola, pero todavía no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Pregunta si se le avisó a alguien sobre su pedido de recordatorio del turno médico'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 6462 ms
- Leda → Marcos: «Entiendo que terminaste «Programar PLC de la comprimidora», pero no puedo recibir la entrega por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 5559 ms
- Leda → Marcos: «Tenés pendientes «Programar PLC de la comprimidora», que sigue figurando en curso y vence el 23/10, y «Revisar comunicaciones industriales de la comprimidora», asignada y con vencimiento el 30/10.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 3

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 5959 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat: el cambio de responsable lo decide Ismael Soschinski. ¿Querés que anote una previsión para esa tarea?»
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
- latencia: 7987 ms
- Leda → Marcos: «Entendido, no anoté ninguna previsión para «Programar PLC de la comprimidora». La tarea ya figura en curso, así que no puedo registrar otro inicio.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 5926 ms
- Leda → Marcos: «No puedo recordarte turnos personales, como el del médico del viernes. Sí puedo ayudarte con el seguimiento de tus tareas de trabajo.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaste a alguien sobre su pedido de recordatorio del turno médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 6740 ms
- Leda → Marcos: «Hay un aviso para el administrador en cola, pero todavía no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Pregunta si le avisaste a alguien sobre su pedido de recordatorio del turno médico'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 5198 ms
- Leda → Marcos: «Me decís que terminaste «Programar PLC de la comprimidora». Todavía no puedo recibir la entrega por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6469 ms
- Leda → Marcos: «Además de «Programar PLC de la comprimidora», tenés pendiente «Revisar comunicaciones industriales de la comprimidora»: está asignada y vence el 30/10. La del PLC sigue figurando en curso, con vencimiento el 23/10, aunque me contaste que la terminaste.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 4

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23/10, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 8729 ms
- Leda → Marcos: «No puedo cambiar por chat el responsable de «Programar PLC de la comprimidora»; eso lo decide Ismael Soschinski. ¿Querés que anote una previsión para la tarea?»
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
- latencia: 8183 ms
- Leda → Marcos: «Entendido, no quedó anotada ninguna previsión. «Programar PLC de la comprimidora» ya figura en curso, así que no puedo registrar el inicio de nuevo.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 7007 ms
- Leda → Marcos: «No puedo programarte un recordatorio para el turno médico del viernes; solo hago seguimiento de las tareas del equipo.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaron a alguien sobre el pedido de recordatorio del turno médico."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 6677 ms
- Leda → Marcos: «Todavía no. Hay un aviso al administrador en cola, pero no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Pregunta si le avisaron a alguien sobre el pedido de recordatorio del turno médico.'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 8265 ms
- Leda → Marcos: «Entiendo que terminaste «Programar PLC de la comprimidora». Todavía no puedo recibir la entrega por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 4077 ms
- Leda → Marcos: «Te figuran dos tareas pendientes: «Programar PLC de la comprimidora», en curso, con vencimiento el 23/10; y «Revisar comunicaciones industriales de la comprimidora», asignada, con vencimiento el 30/10. Me contaste que terminaste la del PLC, pero la entrega no se recibe por chat y todavía figura en curso.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 5

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6177 ms
- Leda → Marcos: «No puedo pasarle “Programar PLC de la comprimidora” a Nahuel por chat; esa reasignación la decide Ismael Soschinski. ¿Querés que anote una previsión para la tarea?»
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
- latencia: 11082 ms
- Leda → Marcos: «Entendido, seguís con “Programar PLC de la comprimidora”. No anoté ninguna previsión. La tarea ya figura en curso, así que no puedo volver a marcarla como iniciada.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 4985 ms
- Leda → Marcos: «No puedo recordarte el turno con el médico el viernes; solo hago seguimiento de las tareas del equipo.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaste a alguien sobre el pedido de recordarle el turno con el médico."}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 6848 ms
- Leda → Marcos: «Todavía no. Hay un aviso al administrador en cola, pero aún no se envió.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [comprension] jugadas: esperado [], real [{'nombre': 'fuera_de_la_lista', 'que_pide': 'Pregunta si le avisaste a alguien sobre el pedido de recordarle el turno con el médico.'}]
- **falla** [garantia] aviso al administrador de más: esperado 0, real 1

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 5482 ms
- Leda → Marcos: «Me contás que terminaste “Programar PLC de la comprimidora”. Todavía no puedo recibir la entrega por chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 9465 ms
- Leda → Marcos: «Te figuran pendientes “Programar PLC de la comprimidora” (en curso, vence el 23/10) y “Revisar comunicaciones industriales de la comprimidora” (asignada, vence el 30/10). Aunque me contaste que terminaste la del PLC, todavía figura en curso.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, te aviso que “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 7162 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM", "ARI"], "correcta": "preguntar", "tipo": "ambigua", "eligio": null, "probabilidades": {"PLC": 0.93, "COM": 0.06, "ARI": 0.01}, "llamadas": 2, "segundos": 0.703, "acierta": true}`
- Leda → Marcos: «Marcos, ¿arrancaste con “Programar PLC de la comprimidora” o con “Revisar comunicaciones industriales de la comprimidora”?»
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
- latencia: 4582 ms
- Jev: `{"referencia": "la del plc", "candidatas": ["PLC", "COM", "ARI"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"ARI": 0.0, "COM": 0.03, "PLC": 0.97}, "llamadas": 2, "segundos": 0.565, "acierta": false}`
- Leda → Marcos: «Quedó anotado que empezaste con “Programar PLC de la comprimidora”.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 2

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, «Integrar datos de la comprimidora en CoreLabs» vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6341 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM", "ARI"], "correcta": "preguntar", "tipo": "ambigua", "eligio": null, "probabilidades": {"PLC": 0.92, "COM": 0.07, "ARI": 0.01}, "llamadas": 2, "segundos": 0.623, "acierta": true}`
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
- latencia: 4923 ms
- Jev: `{"referencia": "la del plc", "candidatas": ["PLC", "COM", "ARI"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.02, "ARI": 0.0, "PLC": 0.98}, "llamadas": 2, "segundos": 0.642, "acierta": false}`
- Leda → Marcos: «Marcos, quedó anotado que arrancaste con “Programar PLC de la comprimidora”; está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «La tarea “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 8017 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM", "ARI"], "correcta": "preguntar", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.06, "PLC": 0.93, "ARI": 0.01}, "llamadas": 2, "segundos": 0.551, "acierta": true}`
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
- latencia: 4984 ms
- Jev: `{"referencia": "la del plc", "candidatas": ["PLC", "COM", "ARI"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"ARI": 0.0, "COM": 0.03, "PLC": 0.97}, "llamadas": 2, "segundos": 0.515, "acierta": false}`
- Leda → Marcos: «Marcos, quedó anotado que empezaste “Programar PLC de la comprimidora”; la tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 4

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, «Integrar datos de la comprimidora en CoreLabs» vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5755 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM", "ARI"], "correcta": "preguntar", "tipo": "ambigua", "eligio": null, "probabilidades": {"PLC": 0.92, "ARI": 0.01, "COM": 0.07}, "llamadas": 2, "segundos": 0.625, "acierta": true}`
- Leda → Marcos: «Entiendo, Marcos. Arrancaste con una de las tareas de la comprimidora.»
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
- latencia: 4598 ms
- Jev: `{"referencia": "la del plc", "candidatas": ["PLC", "COM", "ARI"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"ARI": 0.0, "COM": 0.03, "PLC": 0.97}, "llamadas": 2, "segundos": 0.577, "acierta": false}`
- Leda → Marcos: «Marcos, quedó anotado que empezaste “Programar PLC de la comprimidora”; está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 5

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C FALLA · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, te aviso que “Integrar datos de la comprimidora en CoreLabs” vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4700 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM", "ARI"], "correcta": "preguntar", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.05, "PLC": 0.94, "ARI": 0.01}, "llamadas": 2, "segundos": 1.363, "acierta": true}`
- Leda → Marcos: «Marcos, ¿arrancaste con “Programar PLC de la comprimidora” o con “Revisar comunicaciones industriales de la comprimidora”?»
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
- latencia: 8255 ms
- Jev: `{"referencia": "la del plc", "candidatas": ["PLC", "COM", "ARI"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"PLC": 0.97, "COM": 0.03, "ARI": 0.0}, "llamadas": 2, "segundos": 0.543, "acierta": false}`
- Leda → Marcos: «Quedó anotado que arrancaste con “Programar PLC de la comprimidora”; la tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}]

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 1

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5299 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.11, "PLC": 0.89}, "llamadas": 2, "segundos": 1.527, "acierta": false}`
- Leda → Marcos: «Quedó anotado que empezaste con “Programar PLC de la comprimidora”. La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 3630 ms
- Jev: `{"referencia": "la otra de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "COM", "tipo": "ambigua", "eligio": null, "probabilidades": {"PLC": 0.63, "COM": 0.37}, "llamadas": 1, "segundos": 0.289, "acierta": false}`
- Leda → Marcos: «Quedó anotado que también empezaste “Revisar comunicaciones industriales de la comprimidora”. La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 2

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5107 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.13, "PLC": 0.87}, "llamadas": 2, "segundos": 0.584, "acierta": false}`
- Leda → Marcos: «Quedó anotado que arrancaste con “Programar PLC de la comprimidora”. La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 4636 ms
- Jev: `{"referencia": "la otra de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "COM", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.4, "PLC": 0.6}, "llamadas": 1, "segundos": 1.01, "acierta": false}`
- Leda → Marcos: «También quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”. Está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 3

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea «Programar PLC de la comprimidora» vence el 23 de octubre. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 5661 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.11, "PLC": 0.89}, "llamadas": 2, "segundos": 0.581, "acierta": false}`
- Leda → Marcos: «Quedó anotado que empezaste con «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 3852 ms
- Jev: `{"referencia": "la otra de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "COM", "tipo": "ambigua", "eligio": null, "probabilidades": {"PLC": 0.49, "COM": 0.51}, "llamadas": 1, "segundos": 0.299, "acierta": false}`
- Leda → Marcos: «Quedó anotado que también empezaste «Revisar comunicaciones industriales de la comprimidora». La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 4

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea «Programar PLC de la comprimidora» vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 4953 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.11, "PLC": 0.89}, "llamadas": 2, "segundos": 0.528, "acierta": false}`
- Leda → Marcos: «Quedó anotado que empezaste con «Programar PLC de la comprimidora». La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 4397 ms
- Jev: `{"referencia": "la otra de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "COM", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.45, "PLC": 0.55}, "llamadas": 1, "segundos": 0.293, "acierta": false}`
- Leda → Marcos: «Quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora». La tarea está en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 5

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que “Programar PLC de la comprimidora” vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 4727 ms
- Jev: `{"referencia": "la de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "PLC", "tipo": "ambigua", "eligio": null, "probabilidades": {"PLC": 0.87, "COM": 0.13}, "llamadas": 2, "segundos": 0.582, "acierta": false}`
- Leda → Marcos: «Quedó anotado que empezaste con “Programar PLC de la comprimidora”; ahora figura en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}]`
- latencia: 3768 ms
- Jev: `{"referencia": "la otra de la comprimidora", "candidatas": ["PLC", "COM"], "correcta": "COM", "tipo": "ambigua", "eligio": null, "probabilidades": {"COM": 0.36, "PLC": 0.64}, "llamadas": 1, "segundos": 0.253, "acierta": false}`
- Leda → Marcos: «Quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”; ahora figura en curso.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] no dice: que la del PLC se volvió a arrancar

## 15 · Voy bien, la tengo casi lista · vez 1

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo venís con la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6982 ms
- Leda → Marcos: «Marcos, anoté que venís bien y que tenés casi lista «Programar PLC de la comprimidora». El pedido de estado sigue abierto; quedó preparado un aviso para mañana a las 9:00.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Marcos, ayer me dijiste que tenías casi lista «Programar PLC de la comprimidora». Venció ayer y sigue en curso; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste, estimás cuándo la terminás o hay algo que te traba?»
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
- latencia: 5535 ms
- Leda → Marcos: «Marcos, anoté que seguís con «Programar PLC de la comprimidora». La fecha comprometida fue ayer y el pedido de estado sigue abierto. Hay un aviso preparado para mañana a las 9:00. ¿Para cuándo estimás terminarla?»
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
- latencia: 6589 ms
- Leda → Marcos: «Marcos, anoté que estimás terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida era el 27 de octubre y «Revisar comunicaciones industriales de la comprimidora» depende de que termine. El aviso a Ismael está preparado para hoy a las 10:45; todavía no se envió.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, figura con 5 días hábiles de atraso sobre la fecha comprometida del 27/10. La previsión es el 3/11. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso. Venció el 27 de octubre y estimabas terminarla hoy; Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine y vence el 6 de noviembre. Por ese vencimiento próximo no hace falta que respondas. ¿Cómo está la programación del PLC?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 2

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7216 ms
- Leda → Marcos: «Marcos, anoté que venís bien y que tenés casi lista «Programar PLC de la comprimidora». El pedido de estado sigue abierto; quedó guardado un mensaje para volver a consultarte mañana a las 9.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Marcos, ayer me contaste que tenías casi lista «Programar PLC de la comprimidora». Venció ayer y sigue en curso; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste, para cuándo estimás terminarla o está trabada?»
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
- latencia: 6315 ms
- Leda → Marcos: «Anoté que me contaste que todo está en orden y seguís con «Programar PLC de la comprimidora». La fecha comprometida fue ayer; el pedido de estado sigue abierto y quedó guardado un mensaje para consultarte mañana a las 9. ¿Para cuándo estimás terminarla?»
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
- latencia: 6398 ms
- Leda → Marcos: «Anoté que estimás terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida era el 27 de octubre, y «Revisar comunicaciones industriales de la comprimidora» depende de que termine. El aviso a Ismael quedó guardado para salir hoy a las 10:45.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «“Programar PLC de la comprimidora”, a cargo de Marcos Tarquini, tenía fecha comprometida el 27/10. Figura con 5 días hábiles de atraso y una previsión para el 3/11. De esa tarea depende “Revisar comunicaciones industriales de la comprimidora”.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso. Venció el 27 de octubre y estimaste terminarla hoy; Ismael ya fue avisado. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine y vence el 6 de noviembre, dentro de 3 días hábiles. Por ese vencimiento no hace falta que respondas. ¿En qué estado está hoy la programación del PLC?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 3

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Te aviso que “Programar PLC de la comprimidora” vence el 27/10, en 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 9343 ms
- Leda → Marcos: «Anoté que vas bien y que tenés casi lista “Programar PLC de la comprimidora”. El pedido de estado sigue abierto; quedó preparado un recordatorio para mañana a las 9, que todavía no se envió.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que tenías casi lista “Programar PLC de la comprimidora”. Venció ayer y “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿La terminaste, para cuándo estimás terminarla o está trabada?»
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
- latencia: 6181 ms
- Leda → Marcos: «Anoté que me contaste que todo está en orden y seguís con “Programar PLC de la comprimidora”. La fecha comprometida fue ayer. Hay un recordatorio preparado para mañana a las 9; todavía no se envió. ¿Para cuándo estimás terminarla?»
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
- latencia: 7832 ms
- Leda → Marcos: «Anoté que estimás terminar “Programar PLC de la comprimidora” el martes 3/11, cinco días hábiles después de la fecha comprometida. “Revisar comunicaciones industriales de la comprimidora” depende de esa tarea. El aviso a Ismael está preparado para hoy a las 10:45; todavía no se envió.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «La tarea “Programar PLC de la comprimidora”, a cargo de Marcos Tarquini, tiene 5 días hábiles de atraso y previsión para el 3 de noviembre. De ella depende “Revisar comunicaciones industriales de la comprimidora”.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Hoy es la fecha que estimaste para terminar “Programar PLC de la comprimidora”, que lleva cinco días hábiles de atraso. El aviso a Ismael ya se envió. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine y vence el 6/11; por ese vencimiento no hace falta que respondas.

¿En qué estado está la programación del PLC?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 4

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27/10, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo venís con la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 9179 ms
- Leda → Marcos: «Anoté que venís bien y tenés casi lista «Programar PLC de la comprimidora». El pedido de estado sigue abierto; quedó preparado un aviso para mañana a las 9 para volver a consultarte.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que tenías casi lista «Programar PLC de la comprimidora». Venció ayer y sigue en curso; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste, tenés una fecha estimada o estás trabado con algo?»
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
- latencia: 6312 ms
- Leda → Marcos: «Anoté que seguís con «Programar PLC de la comprimidora» y que todo está en orden. La fecha comprometida fue ayer; quedó preparado un aviso para mañana a las 9. ¿Para qué fecha estimás terminarla?»
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
- latencia: 6436 ms
- Leda → Marcos: «Anoté que estimás tener «Programar PLC de la comprimidora» para el martes 3/11. La fecha comprometida era el 27/10, y «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Quedó preparado un aviso para Ismael Soschinski que sale hoy a las 10:45.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: ««Programar PLC de la comprimidora», a cargo de Marcos Tarquini, tenía fecha comprometida para el 27/10 y ahora tiene una previsión para el 3/11. Figura con 5 días hábiles de atraso. De esa tarea depende «Revisar comunicaciones industriales de la comprimidora».»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 27/10 y estimaste terminarla hoy; Ismael Soschinski ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine y vence el 6/11. Por ese vencimiento no hace falta que respondas.

¿En qué estado está «Programar PLC de la comprimidora»?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 27 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo venís con la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6192 ms
- Leda → Marcos: «Anoté que vas bien y que tenés casi lista «Programar PLC de la comprimidora». Sigue pendiente confirmar si ya está terminada; quedó previsto volver a consultarte mañana a las 9.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me dijiste que tenías casi lista «Programar PLC de la comprimidora». Venció ayer y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste o, si sigue en curso, para cuándo estimás terminarla o qué te está trabando?»
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
- latencia: 7037 ms
- Leda → Marcos: «Anoté que me contaste que todo está en orden y seguís con «Programar PLC de la comprimidora». La fecha comprometida fue ayer; quedó pendiente un aviso para volver a consultarte mañana a las 9. ¿Para cuándo estimás terminarla?»
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
- latencia: 6073 ms
- Leda → Marcos: «Anoté que estimás terminar «Programar PLC de la comprimidora» el martes 3 de noviembre, cinco días hábiles después de la fecha comprometida. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. El aviso a Ismael quedó pendiente de envío para hoy a las 10:45; todavía no salió.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, figura con 5 días hábiles de atraso. La previsión es el 3/11. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.»
  - hechos: `{"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 27 de octubre y estimabas terminarla hoy, cinco días hábiles después; Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine y vence el 6 de noviembre. Por ese vencimiento no hace falta que respondas. ¿Terminaste la programación o sigue en curso?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 16 · Arranqué hoy, con la tarea vencida · vez 1

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y sigue asignada. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el 23 de octubre y sigue asignada. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 8159 ms
- Leda → Marcos: «Quedó anotado que hoy empezaste «Programar PLC de la comprimidora». La fecha comprometida era el 23 de octubre y lleva un día hábil de atraso. ¿Para cuándo estimás terminarla?»
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
- latencia: 7591 ms
- Leda → Marcos: «Anoté que estimás terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. «Revisar comunicaciones industriales de la comprimidora» depende de que termine. El aviso a Ismael está guardado para salir hoy a las 10:25; todavía no se envió.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, lleva 3 días hábiles de atraso respecto de la fecha comprometida del 23/10. La previsión es para el 28/10. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es la fecha que estimaste para terminar «Programar PLC de la comprimidora». La tarea lleva tres días hábiles de atraso e Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 2

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23/10, en tres días hábiles. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: ««Programar PLC de la comprimidora» venció el 23/10 y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 8269 ms
- Leda → Marcos: «Quedó anotado que hoy arrancaste «Programar PLC de la comprimidora». Está en curso y lleva un día hábil de atraso desde el 23/10. Mañana a las 9 está previsto volver a consultarte el estado. ¿Para qué fecha estimás terminarla?»
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
- latencia: 7692 ms
- Leda → Marcos: «Quedó anotado que estimás terminar «Programar PLC de la comprimidora» el miércoles 28/10. Serían tres días hábiles después de la fecha comprometida, y «Revisar comunicaciones industriales de la comprimidora» depende de que termine. El aviso a Ismael está guardado, todavía sin enviar; está previsto que salga hoy a las 10:25.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, figura con 3 días hábiles de atraso respecto de la fecha comprometida, el 23/10. La previsión es el 28/10. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23/10 y estimaste terminarla hoy. El aviso a Ismael ya se envió, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 3

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy y sigue asignada. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo venís con la programación del PLC?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: ««Programar PLC de la comprimidora» venció el 23 de octubre y sigue asignada, con un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿En qué estado está la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 8113 ms
- Leda → Marcos: «Anoté que hoy arrancaste «Programar PLC de la comprimidora»; quedó en curso. Venció el 23 de octubre y lleva un día hábil de atraso. Hay un pedido de estado programado para mañana a las 9, que todavía no se envió. ¿Para qué fecha estimás terminarla?»
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
- latencia: 7254 ms
- Leda → Marcos: «Anoté que estimás terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida era el 23, así que la previsión queda tres días hábiles después. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. El aviso a Ismael está guardado para enviarse hoy a las 10:25; todavía no salió.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, lleva 3 días hábiles de atraso respecto de la fecha comprometida, el 23/10. La previsión es el 28/10. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. La fecha que estimaste para terminarla es hoy, tres días hábiles después del vencimiento. Ismael ya recibió el aviso y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿En qué estado está la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea “Programar PLC de la comprimidora” vence el 23 de octubre, en 3 días hábiles. No hace falta que respondas este aviso.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence “Programar PLC de la comprimidora”. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿En qué estado está la programación?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, “Programar PLC de la comprimidora” venció el 23 de octubre y sigue asignada. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 7375 ms
- Leda → Marcos: «Anoté que hoy empezaste “Programar PLC de la comprimidora”. Sigue en curso y venció el 23 de octubre. ¿Para cuándo estimás terminarla?»
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
- latencia: 6820 ms
- Leda → Marcos: «Anoté que estimás terminar “Programar PLC de la comprimidora” el miércoles 28 de octubre. Venció el 23 y “Revisar comunicaciones industriales de la comprimidora” depende de que termine. El aviso a Ismael está pendiente de envío para hoy a las 10:25; todavía no salió.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, tenía fecha comprometida el 23/10 y registra 3 días hábiles de atraso. La previsión es el 28/10. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” sigue en curso. Venció el 23 de octubre y estimaste terminarla hoy. Ismael ya recibió el aviso, y “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿En qué estado está la programación?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 5

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas a este aviso.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el 23 de octubre y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 9381 ms
- Leda → Marcos: «Anoté que arrancaste hoy «Programar PLC de la comprimidora»; quedó en curso y lleva un día hábil de atraso. El próximo pedido de estado está previsto para mañana a las 9; todavía no se envió. ¿Qué fecha estimás para terminarla?»
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
- latencia: 6299 ms
- Leda → Marcos: «Anoté el miércoles 28 de octubre como fecha estimada para terminar «Programar PLC de la comprimidora». Es tres días hábiles después de la fecha comprometida, y «Revisar comunicaciones industriales de la comprimidora» depende de que termine. El aviso a Ismael está guardado para salir hoy a las 10:25; todavía no se envió.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Programar PLC de la comprimidora, a cargo de Marcos Tarquini, lleva 3 días hábiles de atraso respecto de la fecha comprometida del 23/10. La previsión es el 28/10. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Venció el 23 de octubre, hace tres días hábiles, y la fecha que estimaste para terminarla es hoy. Ismael ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación del PLC?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

