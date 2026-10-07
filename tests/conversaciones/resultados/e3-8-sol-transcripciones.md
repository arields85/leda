# Transcripciones de la ronda e3-8-sol

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6391 ms
- Leda → Marcos: «Quedó anotado que empezaste hoy a la mañana «Programar PLC de la comprimidora»; la tarea está en curso. El viernes 23 de octubre te voy a preguntar cómo va.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. ¿La terminaste, para cuándo prevés terminarla o estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 2

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4683 ms
- Leda → Marcos: «Quedó anotado que empezaste hoy a la mañana «Programar PLC de la comprimidora» y que está en curso. El viernes 23 de octubre te voy a pedir cómo sigue.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy y sigue en curso. ¿La terminaste? Si no, contame para cuándo prevés terminarla y si estás trabado.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 3

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. Podés seguir con la tarea; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4139 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”; la tarea está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Hoy vence “Programar PLC de la comprimidora”. ¿La terminaste, para cuándo calculás terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 4

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 2993 ms
- Leda → Marcos: «Quedó anotado que empezaste hoy a la mañana «Programar PLC de la comprimidora» y que está en curso. El viernes 23 de octubre te voy a pedir cómo sigue.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. ¿La terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el título de la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- [ ] no dice: que es urgente
- [ ] no dice: ningún avance que nadie informó

**Paso 2.** Marcos (2026-10-20 11:15): «arranque hoy a la mañana, ya estoy en eso»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3274 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora” y que está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy y sigue en curso. ¿La terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 02 · Llego el 27, el proveedor se demoró · vez 1

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 7382 ms
- Leda → Marcos: «Quedó anotado que prevés terminar “Programar PLC de la comprimidora” el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23; si terminás el 27, serán dos días hábiles de atraso. De esta tarea depende “Revisar comunicaciones industriales de la comprimidora”. Ismael Soschinski recibirá el aviso hoy a las 15:40. Te voy a pedir el estado el martes 27.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos prevé terminar “Programar PLC de la comprimidora” el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23; si se cumple la previsión, serán dos días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy. Sigue vigente tu previsión de terminarla el martes 27 por la demora del proveedor; si se cumple, serán dos días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine, e Ismael Soschinski ya está al tanto.

El martes 27 te voy a pedir el estado; no hace falta que respondas ahora.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” lleva dos días hábiles de atraso. Tu previsión era terminarla hoy, martes 27 de octubre, por la demora del proveedor, e Ismael Soschinski ya está al tanto. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine y vence el viernes 30, en tres días hábiles.

¿Terminaste “Programar PLC de la comprimidora” o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” lleva tres días hábiles de atraso. Tu previsión era terminarla ayer, martes 27 de octubre, por la demora del proveedor. Ismael Soschinski ya está al tanto de esa previsión y “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

¿Terminaste “Programar PLC de la comprimidora” o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” lleva cuatro días hábiles de atraso. Tu previsión era terminarla el martes 27 de octubre por la demora del proveedor; Ismael Soschinski ya está al tanto de esa previsión. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. Si no respondés, se le avisará a Ismael.

¿Terminaste “Programar PLC de la comprimidora” o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado sobre “Programar PLC de la comprimidora” que recibió desde el martes 27, la fecha en que preveía terminarla. La tarea sigue en curso y lleva cinco días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy, viernes 30 de octubre, pero todavía no puede arrancar porque “Programar PLC de la comprimidora” sigue en curso.

¿Para cuándo prevés terminar “Revisar comunicaciones industriales de la comprimidora” y hay algo más que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 2

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 6577 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el martes 27 porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23; si terminás el 27, serán dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esta tarea. Ismael Soschinski se enterará hoy a las 15:40. Te voy a pedir el estado el martes 27.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida es el viernes 23; si se cumple la previsión, la tarea tendrá 2 días hábiles de atraso. De ella depende «Revisar comunicaciones industriales de la comprimidora». No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy y sigue en curso. La previsión es terminarla el martes 27 por la demora del proveedor; si se cumple, tendrá dos días hábiles de atraso. Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine.

Te voy a pedir el estado el martes 27; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Estaba comprometida para el viernes 23 y hoy lleva dos días hábiles de atraso. Habías previsto terminarla hoy por la demora del proveedor; Ismael ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine la primera y vence el viernes 30, en tres días hábiles.

¿Cómo viene «Programar PLC de la comprimidora»: ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. La previsión era terminarla ayer y hoy lleva tres días hábiles de atraso. Ismael ya conoce esa previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine.

¿Ya terminaste «Programar PLC de la comprimidora» o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» sigue en curso: venció el viernes 23 y lleva cuatro días hábiles de atraso. Habías previsto terminarla el martes 27; Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no respondés, se avisará a Ismael.

¿Ya terminaste «Programar PLC de la comprimidora» o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: ««Programar PLC de la comprimidora» sigue en curso y lleva 5 días hábiles de atraso. La previsión de Marcos era terminarla el martes 27 de octubre, pero no respondió a los tres pedidos de estado que recibió desde ese día. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence hoy y todavía no puede arrancar: depende de «Programar PLC de la comprimidora», que sigue en curso. ¿Para cuándo prevés terminar la revisión y hay algo más que te trabe?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 3

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el viernes 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 6478 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el martes 27 porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23: si terminás el 27, serán dos días hábiles de atraso. De esta tarea depende «Revisar comunicaciones industriales de la comprimidora». Ismael Soschinski recibirá el aviso hoy a las 15:40. El martes 27 te voy a pedir el estado.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos prevé terminar “Programar PLC de la comprimidora” el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23; si se cumple la previsión, serían dos días hábiles de atraso. De esa tarea depende “Revisar comunicaciones industriales de la comprimidora”. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy. Tu previsión sigue siendo terminarla el martes 27 porque el proveedor se demoró; si se cumple, serán dos días hábiles de atraso. Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine esta tarea. El martes 27 te voy a pedir el estado; no hace falta que respondas ahora.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Hoy es la fecha que habías previsto para terminar «Programar PLC de la comprimidora», que lleva dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» vence el viernes 30 y no puede arrancar hasta que termine la primera.

¿Terminaste «Programar PLC de la comprimidora» o, si todavía no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» vencía el viernes 23 y lleva tres días hábiles de atraso. Habías previsto terminarla ayer. Ismael Soschinski ya está al tanto, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine.

¿Terminaste «Programar PLC de la comprimidora» o, si todavía no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» lleva cuatro días hábiles de atraso. Habías previsto terminarla el martes 27 por la demora del proveedor, e Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no respondés, se le avisará a Ismael.

¿Terminaste «Programar PLC de la comprimidora» o, si todavía no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence hoy y todavía no puede arrancar hasta que termine «Programar PLC de la comprimidora», que sigue en curso.

¿Para cuándo prevés terminar la revisión y hay algo más que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió a los tres pedidos de estado de “Programar PLC de la comprimidora” desde el martes 27 de octubre. La tarea sigue en curso y hoy lleva cinco días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 7472 ms
- Leda → Marcos: «Quedó anotado que prevés terminar “Programar PLC de la comprimidora” el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23; si terminás el 27, serían dos días hábiles de atraso. De esta tarea depende “Revisar comunicaciones industriales de la comprimidora”. Ismael Soschinski recibirá el aviso hoy a las 15:40. Te pediré el estado el martes 27.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos prevé terminar Programar PLC de la comprimidora el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23; si se cumple esa previsión, serían dos días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy. Tu previsión sigue siendo terminarla el martes 27 de octubre porque el proveedor se demoró; si se cumple, serían dos días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esta tarea. Ismael Soschinski ya está al tanto.

El martes 27 te pediré el estado. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” lleva dos días hábiles de atraso. Habías previsto terminarla hoy porque el proveedor se demoró. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine esa tarea y vence el viernes 30 de octubre, dentro de tres días hábiles.

¿Terminaste “Programar PLC de la comprimidora” o, si todavía no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” lleva tres días hábiles de atraso. Habías previsto terminarla ayer, martes 27 de octubre, porque el proveedor se demoró. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine, e Ismael Soschinski ya está al tanto de tu previsión.

¿Terminaste “Programar PLC de la comprimidora” o, si todavía no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” lleva cuatro días hábiles de atraso. Habías previsto terminarla el martes 27 de octubre y todavía no sé si la terminaste. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. Si no respondés, se le avisará a Ismael Soschinski.

¿Terminaste “Programar PLC de la comprimidora” o, si todavía no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy, pero todavía no puede arrancar: “Programar PLC de la comprimidora” sigue en curso.

¿Para cuándo prevés terminar la revisión y está trabada por algo más?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado que recibió desde el martes 27 sobre Programar PLC de la comprimidora. La tarea sigue en curso, con cinco días hábiles de atraso; la fecha que había previsto para terminarla ya pasó. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 5

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 12008 ms
- Leda → Marcos: «Quedó anotado que prevés terminar “Programar PLC de la comprimidora” el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23: si se cumple tu previsión, serían dos días hábiles de atraso. De esta tarea depende “Revisar comunicaciones industriales de la comprimidora”. Ismael Soschinski se enterará hoy a las 15:40. Te voy a pedir el estado el martes 27.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23: si se cumple la previsión, serían dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": "el proveedor se demoró", "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea del PLC
- [ ] dice: que Marcos prevé llegar el martes 27 y por qué
- [ ] dice: que la fecha comprometida es el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha ya cambió
- [ ] no dice: cómo se cambia la fecha
- [ ] no dice: un atraso que no salga del código
- [ ] no dice: nada que Marcos no dijo

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy. Tu previsión sigue siendo terminarla el martes 27 porque el proveedor se demoró; si se cumple, serían dos días hábiles de atraso. Ismael Soschinski ya está al tanto, y “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termines esta tarea. Te pediré el estado el martes 27. No hace falta que respondas ahora.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «“Programar PLC de la comprimidora” lleva dos días hábiles de atraso y tu previsión era terminarla hoy. Ismael Soschinski ya está al tanto. “Revisar comunicaciones industriales de la comprimidora” vence el viernes 30, pero no puede arrancar hasta que termines la primera.

¿Terminaste “Programar PLC de la comprimidora”, para cuándo prevés terminarla o estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «“Programar PLC de la comprimidora” lleva tres días hábiles de atraso; tu previsión era terminarla ayer. Ismael Soschinski ya está al tanto y “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines.

¿Terminaste “Programar PLC de la comprimidora”, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «“Programar PLC de la comprimidora” lleva cuatro días hábiles de atraso y tu previsión de terminarla el martes 27 ya pasó. Ismael Soschinski está al tanto; “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. Si no respondés, le avisaré a Ismael.

¿Terminaste “Programar PLC de la comprimidora”, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence hoy, pero todavía no puede arrancar porque “Programar PLC de la comprimidora” sigue en curso. ¿Para cuándo prevés terminar la revisión y hay algo más que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió a los tres pedidos de estado de «Programar PLC de la comprimidora» desde el martes 27. La tarea sigue en curso: venció el viernes 23 y hoy lleva cinco días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: ««Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5848 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque falta el repuesto. Mientras siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: ««Programar PLC de la comprimidora» sigue trabada porque falta el repuesto. ¿Quién puede destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 6337 ms
- Leda → Marcos: «Quedó anotado que no sabés quién puede destrabar «Programar PLC de la comprimidora». Mientras siga trabada, no te voy a pedir el estado. ¿Preferís que alguien del equipo ayude con el bloqueo o contarme para cuándo prevés terminarla y por qué?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 6589 ms
- Leda → Marcos: «Entiendo, hay que esperar a que llegue el repuesto. Dejé sin efecto la propuesta de pedir ayuda o anotar una previsión para «Programar PLC de la comprimidora»; no se anotó nada nuevo. Avisame cuando se destrabe.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence el viernes 30 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 2

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente la fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4137 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque falta el repuesto. Mientras siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: ««Programar PLC de la comprimidora» está trabada porque falta el repuesto. ¿Quién puede destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 5561 ms
- Leda → Marcos: «Quedó anotado que no sabés quién puede destrabar «Programar PLC de la comprimidora». Mientras siga trabada, no te voy a pedir el estado. ¿Preferís que alguien del equipo ayude con el bloqueo o que anotemos para cuándo prevés terminarla y por qué?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 6288 ms
- Leda → Marcos: «Entendido, hay que esperar que llegue el repuesto. No quedó nada nuevo anotado para «Programar PLC de la comprimidora». Cuando se destrabe, avisame para retomar el seguimiento.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence el viernes 30 de octubre, en tres días hábiles. Tené presente la fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 3

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4494 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque falta el repuesto. Mientras siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: ««Programar PLC de la comprimidora» sigue trabada porque falta el repuesto. ¿Quién puede destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 5931 ms
- Leda → Marcos: «Quedó anotado que no sabés quién puede destrabar «Programar PLC de la comprimidora». Mientras siga trabada, no te voy a pedir el estado. ¿Preferís que alguien del equipo ayude con el bloqueo o anotar para cuándo prevés terminarla y por qué?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 6522 ms
- Leda → Marcos: «Entendido, hay que esperar el repuesto. Dejé sin efecto la propuesta y no quedó nada nuevo anotado. «Programar PLC de la comprimidora» sigue trabada; avisame cuando se destrabe para retomar el seguimiento.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Marcos, «Revisar comunicaciones industriales de la comprimidora» vence el viernes 30 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 4

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4714 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está trabada porque falta el repuesto. Mientras siga así, no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «“Programar PLC de la comprimidora” sigue trabada porque falta el repuesto. ¿Quién puede destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 6408 ms
- Leda → Marcos: «Quedó anotado que no sabés quién puede destrabar “Programar PLC de la comprimidora”. Mientras siga trabada, no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó. ¿Preferís que alguien del equipo ayude con el bloqueo o contarme para cuándo prevés terminarla y por qué?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 6115 ms
- Leda → Marcos: «Entendido, hay que esperar el repuesto. Dejamos de lado las opciones que te propuse y no quedó nada nuevo anotado. Avisame cuando se destrabe “Programar PLC de la comprimidora”.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence el viernes 30 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 5

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4293 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está trabada porque falta el repuesto. No te voy a pedir el estado mientras siga trabada; el seguimiento se retoma cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «“Programar PLC de la comprimidora” sigue trabada porque falta el repuesto. ¿Quién puede destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 5441 ms
- Leda → Marcos: «Quedó anotado que no sabés quién puede destrabar “Programar PLC de la comprimidora”. ¿Preferís que alguien del equipo ayude con el bloqueo o anotar para cuándo prevés terminarla y por qué?»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"]}, "no_se_anoto_nada": true}]`
- latencia: 8204 ms
- Leda → Marcos: «Entiendo, por ahora hay que esperar el repuesto. Dejé sin efecto la propuesta de pedir ayuda o anotar una previsión; no quedó nada nuevo anotado. Avisame cuando se destrabe “Programar PLC de la comprimidora”.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence el viernes 30 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el martes 27 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿Ya la terminaste o, si sigue en curso, para cuándo estimás terminarla y tenés alguna traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, “Programar PLC de la comprimidora” venció ayer y lleva un día hábil de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿Ya la terminaste o, si sigue en curso, para cuándo estimás terminarla y tenés alguna traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, “Programar PLC de la comprimidora” lleva dos días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. Si no respondés, se le avisará a Ismael Soschinski. ¿Ya la terminaste o, si sigue en curso, para cuándo estimás terminarla y tenés alguna traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió a los tres pedidos de estado sobre «Programar PLC de la comprimidora» desde el martes 27 de octubre. La tarea está en curso y lleva tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 2

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el martes 27 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, martes 27 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció ayer y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el martes 27 de octubre y lleva dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. Si no respondés, se le avisará a Ismael Soschinski. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado de “Programar PLC de la comprimidora” desde el martes 27 de octubre. La tarea figura en curso y lleva tres días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 3

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el martes 27 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Hoy vence «Programar PLC de la comprimidora». «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» venció ayer y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» venció el martes 27 y lleva dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. Si no respondés, se le avisará a Ismael Soschinski. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado sobre «Programar PLC de la comprimidora» que recibió desde el martes 27 de octubre. La tarea está en curso y lleva 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 4

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el martes 27 de octubre, dentro de tres días hábiles. No hace falta responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» vence hoy, martes 27 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si todavía no, para cuándo estimás terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» venció ayer, martes 27 de octubre, y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si todavía no, para cuándo estimás terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» venció el martes 27 de octubre y lleva dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no respondés, se le avisará a Ismael Soschinski. ¿La terminaste o, si todavía no, para cuándo estimás terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado de “Programar PLC de la comprimidora” desde el martes 27 de octubre. La tarea figura en curso y lleva tres días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine.

No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 04 · No contesta · vez 5

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el martes 27 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo estimás terminarla y tenés algún bloqueo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» venció ayer y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo estimás terminarla y tenés algún bloqueo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» venció el martes 27 de octubre y lleva dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. Si no respondés, se le avisará a Ismael Soschinski. ¿Ya la terminaste o, si no, para cuándo estimás terminarla y tenés algún bloqueo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado de «Programar PLC de la comprimidora» desde el martes 27 de octubre. La tarea sigue en curso y lleva tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

## 05 · Varias cosas en un mensaje · vez 1

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 8495 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora». También anoté que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre porque esperás el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían tres días hábiles de atraso. Ismael Soschinski recibirá el aviso hoy a las 10:05.

Te voy a pedir el estado del PLC el viernes 23 de octubre y el de comunicaciones el miércoles 4 de noviembre.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre: está esperando el switch nuevo. La fecha comprometida es el viernes 30 de octubre; si se cumple su previsión, serían 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7605 ms
- Leda → Marcos: «Quedó anotado que ahora prevés terminar «Revisar comunicaciones industriales de la comprimidora» el jueves 5 de noviembre, en lugar del miércoles 4. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple la nueva previsión, serían cuatro días hábiles de atraso. Ismael Soschinski recibirá el aviso hoy a las 16:30 y te pediré el estado de esa tarea el jueves 5.

Para anotar el bloqueo de «Programar PLC de la comprimidora», ¿qué te trabó?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5403 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque Martín de IT tiene que habilitarte el acceso a la red de planta, y que él puede destrabarla. Mientras siga trabada, no te voy a pedir el estado. Avisame cuando se destrabe para retomar el seguimiento.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 9204 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» y que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre porque esperás el switch nuevo. La fecha comprometida de comunicaciones sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían tres días hábiles de atraso. Ismael Soschinski recibirá el aviso hoy a las 10:05.

Te voy a pedir el estado del PLC el viernes 23 y el de comunicaciones el miércoles 4.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos prevé terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre porque espera el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple la previsión, serían 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 8748 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el jueves 5 de noviembre, en lugar del miércoles 4. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían cuatro días hábiles de atraso. Ismael Soschinski recibirá el aviso hoy a las 16:30 y te pediré el estado el jueves 5.

Para anotar el bloqueo de «Programar PLC de la comprimidora», ¿qué te está trabando?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 4568 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque Martín de IT tiene que habilitarte el acceso a la red de planta, y que él puede destrabarla. Mientras siga trabada, no te voy a pedir el estado. Avisame cuando tengas acceso y se destrabe.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 3

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. Tené presente la fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["fecha"]}]`
- latencia: 6314 ms
- Leda → Marcos: «Anoté que empezaste “Programar PLC de la comprimidora”. El viernes 23 de octubre te voy a pedir el estado. Para anotar la previsión de lo de las comunicaciones, ¿de qué mes es el miércoles 4?»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'motivo': 'espero el switch nuevo'}]
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-23'}}}, {'jugada': 'anotar_prevision', 'resultado': 'falta_dato', 'falta': ['fecha']}]

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
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["fecha"]}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 8517 ms
- Leda → Marcos: «Para anotar el bloqueo de “Programar PLC de la comprimidora”, me falta saber qué te trabó. Para anotar la nueva previsión de comunicaciones, el jueves 5, todavía me falta el mes. ¿Qué te traba con “Programar PLC de la comprimidora”?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-05', 'puede_traer': ['motivo']}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM'}]
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-05'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-05', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}}], real []
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-05', 'atraso_si_se_cumple_la_prevision_dias_habiles': 4}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}, {'jugada': 'anotar_prevision', 'resultado': 'falta_dato', 'falta': ['fecha']}]

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 6720 ms
- Leda → Marcos: «Anoté que “Programar PLC de la comprimidora” está trabada porque Martín de IT tiene que habilitarte el acceso a la red de planta, y que él puede destrabarla. Mientras siga trabada, no te voy a pedir el estado. Avisame cuando se destrabe para retomar el seguimiento.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 4

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente el vencimiento; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 8994 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”. Te voy a pedir el estado el viernes 23 de octubre.

También quedó anotado que prevés terminar “Revisar comunicaciones industriales de la comprimidora” el miércoles 4 de noviembre porque esperás el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían 3 días hábiles de atraso. Ismael Soschinski recibirá el aviso hoy a las 10:05.

Te pediré el estado de comunicaciones el miércoles 4 de noviembre.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos prevé terminar “Revisar comunicaciones industriales de la comprimidora” el miércoles 4 de noviembre porque espera el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple la previsión, serían 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7425 ms
- Leda → Marcos: «Quedó anotado que prevés terminar “Revisar comunicaciones industriales de la comprimidora” el jueves 5 de noviembre, en lugar del miércoles 4. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían 4 días hábiles de atraso. Ismael Soschinski recibirá el aviso hoy a las 16:30 y te pediré el estado el jueves 5.

Para anotar que estás trabado con “Programar PLC de la comprimidora”, ¿qué te está trabando?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 4999 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está trabada porque Martín de IT todavía tiene que habilitarte el acceso a la red de planta, y que él puede destrabarla. Mientras siga trabada, no te voy a pedir el estado. Avisame cuando se destrabe para retomar el seguimiento.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 5

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre. Tené presente la fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7677 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» y que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre porque esperás el switch nuevo. La fecha comprometida de comunicaciones sigue siendo el viernes 30 de octubre: si se cumple tu previsión, serán 3 días hábiles de atraso. Ismael Soschinski se enterará hoy a las 10:05.

El viernes 23 te voy a pedir el estado del PLC y el miércoles 4, el de comunicaciones.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos prevé terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre porque espera el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple esa previsión, serían 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7980 ms
- Leda → Marcos: «Quedó anotado que ahora prevés terminar «Revisar comunicaciones industriales de la comprimidora» el jueves 5 de noviembre, en vez del miércoles 4. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serán 4 días hábiles de atraso. Ismael Soschinski se enterará hoy a las 16:30 y el jueves 5 te pediré el estado de comunicaciones.

Para anotar el bloqueo de «Programar PLC de la comprimidora», ¿qué te está trabando?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5592 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque Martín de IT tiene que habilitarte el acceso a la red de planta, y que él puede destrabarla. Mientras siga trabada, no te voy a pedir el estado. Avisame cuando se destrabe para retomar el seguimiento.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 06 · No, era la otra tarea · vez 1

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4226 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» y está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 6755 ms
- Leda → Marcos: «Tenés razón, había entendido mal. Corregí el inicio de «Programar PLC de la comprimidora»: sigue asignada, sin empezar. Quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora», que está en curso. Avisame cuando arranques la del PLC.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. ¿La empezaste? Si es así, contame para cuándo calculás terminarla y si hay algo que te esté trabando.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3066 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora»; está en curso. Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 6378 ms
- Leda → Marcos: «Corregí la anotación: «Programar PLC de la comprimidora» vuelve a figurar como asignada, sin empezar. Quedó anotado que arrancaste «Revisar comunicaciones industriales de la comprimidora», que está en curso. Avisame cuando empieces la del PLC.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. La última vez me dijiste que todavía no la habías empezado. ¿Ya la empezaste, para cuándo calculás terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 3

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4122 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» esta mañana; la tarea está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 6415 ms
- Leda → Marcos: «Tenés razón, me confundí de tarea. Corregí lo anterior: «Programar PLC de la comprimidora» sigue sin empezar. Quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora». Avisame cuando arranques la del PLC.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre, y sigue anotada como sin empezar. ¿Ya la empezaste, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 4

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4201 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» esta mañana; la tarea está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 6396 ms
- Leda → Marcos: «Tenés razón, me confundí de tarea. Corregí lo anterior: «Programar PLC de la comprimidora» volvió a quedar como asignada, sin empezar. Anoté que empezaste «Revisar comunicaciones industriales de la comprimidora», que ahora está en curso. Avisame cuando arranques la del PLC.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. La última vez me dijiste que todavía no la habías empezado. ¿Cómo viene ahora: pudiste arrancarla, para cuándo calculás terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 2812 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» esta mañana. Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 4993 ms
- Leda → Marcos: «Corregido: «Programar PLC de la comprimidora» quedó como asignada, sin empezar, y quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora». Avisame cuando arranques la del PLC.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. ¿Cómo viene: ya la empezaste, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 07 · Dejá, no importa · vez 1

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: ««Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7461 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4798 ms
- Leda → Marcos: «Listo, dejamos sin efecto la pregunta sobre «Programar PLC de la comprimidora». No quedó nada anotado. Si querés retomarlo, contame qué te está frenando.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. ¿La terminaste, para cuándo calculás terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 3348 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4920 ms
- Leda → Marcos: «Está bien, dejo sin efecto la pregunta sobre «Programar PLC de la comprimidora». No quedó nada anotado. Si querés retomarlo, contame qué te está frenando.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. ¿La terminaste o, si no, para cuándo estimás terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 3

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 3207 ms
- Leda → Marcos: «Entiendo que estás trabado con “Programar PLC de la comprimidora”. ¿Qué te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4753 ms
- Leda → Marcos: «De acuerdo, dejamos ahí la pregunta sobre “Programar PLC de la comprimidora”. No quedó nada anotado. Si más adelante querés retomarlo, contame qué te está frenando.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «“Programar PLC de la comprimidora” vence hoy, viernes 23 de octubre. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4627 ms
- Leda → Marcos: «¿Qué te está trabando con «Programar PLC de la comprimidora»?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4490 ms
- Leda → Marcos: «Listo, dejamos sin efecto la pregunta sobre «Programar PLC de la comprimidora» y no quedó anotado ningún bloqueo. Si querés retomarlo, contame qué te está trabando.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre, y sigue en curso. ¿La terminaste o, si no, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 5

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el viernes 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 2763 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5350 ms
- Leda → Marcos: «Está bien, dejo sin efecto la pregunta sobre «Programar PLC de la comprimidora». No quedó nada anotado. Si querés retomar el tema más adelante, escribime.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. ¿La terminaste, para cuándo estimás terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 08 · Cambio de tema · vez 1

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5805 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». Para anotar el bloqueo, ¿qué te está impidiendo avanzar?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 7356 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple esa previsión, habrá tres días hábiles de atraso. Ismael Soschinski recibirá el aviso hoy a las 10:43 y te pediré el estado el miércoles 4.

Sobre «Programar PLC de la comprimidora», ¿qué te está impidiendo avanzar?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar “Revisar comunicaciones industriales de la comprimidora” el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple la previsión, serán 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3779 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque no te mandaron el programa del fabricante. Mientras siga trabada, no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 2

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente esa fecha para organizar el trabajo; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 2891 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está trabando?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 8161 ms
- Leda → Marcos: «Quedó anotado que preveés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serán tres días hábiles de atraso. Ismael Soschinski se enterará hoy a las 10:43 y te pediré el estado el miércoles 4.

Sobre «Programar PLC de la comprimidora», ¿qué te está trabando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar “Revisar comunicaciones industriales de la comprimidora” el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple la previsión, serían 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4504 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque no te mandaron el programa del fabricante. Mientras siga trabada, no te pediré el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 3

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 3144 ms
- Leda → Marcos: «¿Qué te está trabando con «Programar PLC de la comprimidora»?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 8557 ms
- Leda → Marcos: «Quedó anotado que preveés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si terminás el 4, serían tres días hábiles de atraso. Ismael Soschinski se va a enterar hoy a las 10:43. Te voy a pedir el estado el miércoles 4 de noviembre.

¿Y qué te está trabando con «Programar PLC de la comprimidora»?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos dio una nueva previsión para terminar «Revisar comunicaciones industriales de la comprimidora»: el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple la previsión, serían 3 días hábiles de atraso. Es solo para que estés al tanto; no hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4147 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque no te mandaron el programa del fabricante. Mientras siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede conseguirte el programa?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 4

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: ««Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente ese plazo; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 2567 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está trabando?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 7303 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si terminás el 4, serían tres días hábiles de atraso. Ismael se enterará hoy a las 10:43 y yo te pediré el estado el miércoles 4.

Sobre «Programar PLC de la comprimidora», ¿qué te está trabando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple esa previsión, la tarea tendrá 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5225 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque no te mandaron el programa del fabricante. Mientras siga así, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 5

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 2901 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está frenando?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 11219 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían tres días hábiles de atraso. Ismael Soschinski se enterará hoy a las 10:43 y te pediré el estado el miércoles 4 de noviembre.

Sobre «Programar PLC de la comprimidora», ¿qué te está frenando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple la previsión, serían 3 días hábiles de atraso. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4418 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque no te mandaron el programa del fabricante. No te pediré el estado mientras siga trabada; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 09 · Duda: ¿de qué tarea habla? · vez 1

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3217 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4179 ms
- Leda → Marcos: «Quedó anotado que hoy arrancaste Revisar comunicaciones industriales de la comprimidora. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 2

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3068 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1589 ms
- Leda → Marcos: «Quedó anotado que arrancaste con «Revisar comunicaciones industriales de la comprimidora». Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 3

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3051 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1457 ms
- Leda → Marcos: «Quedó anotado que arrancaste «Revisar comunicaciones industriales de la comprimidora». El viernes 30 de octubre te voy a pedir el estado de la tarea.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 4

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3167 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1519 ms
- Leda → Marcos: «Quedó anotado que hoy empezaste «Revisar comunicaciones industriales de la comprimidora». Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 5

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3084 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1391 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Revisar comunicaciones industriales de la comprimidora”; está en curso. El viernes 30 de octubre te voy a preguntar cómo va.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 10 · Escribir en lugar de tocar un botón · vez 1

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3321 ms
- Leda → Marcos: «¿Cuál de las dos arrancaste: “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4199 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”; está en curso. El viernes 30 de octubre te voy a preguntar cómo sigue. Por ahora no hace falta que respondas.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 2771 ms
- Leda → Marcos: «¿Cuál de las dos arrancaste: “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3883 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”. El viernes 30 de octubre te voy a pedir el estado. No hace falta que respondas ahora.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3126 ms
- Leda → Marcos: «Para anotar el inicio, ¿cuál de estas arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3718 ms
- Leda → Marcos: «Quedó anotado que arrancaste «Programar PLC de la comprimidora». Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 4

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 2793 ms
- Leda → Marcos: «Para anotar el inicio, ¿cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3661 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”. El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3203 ms
- Leda → Marcos: «¿Cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3380 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora». El viernes 30 de octubre te voy a preguntar cómo va. No hace falta que respondas ahora.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Con cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora. El viernes 30 de octubre te voy a preguntar cómo va.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 5818 ms
- Leda → Marcos: «Esa pregunta se cerró ayer con Programar PLC de la comprimidora. Tocar ahora Revisar comunicaciones industriales de la comprimidora no cambió nada. El viernes 30 de octubre te voy a preguntar cómo va Programar PLC de la comprimidora.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4679 ms
- Leda → Marcos: «Quedó anotado que hoy arrancaste Revisar comunicaciones industriales de la comprimidora. El viernes 30 de octubre te voy a preguntar cómo va.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 5509 ms
- Leda → Marcos: «Quedó anotado que preveés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre porque esperás el switch. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían tres días hábiles de atraso. Ismael Soschinski se enterará mañana a las 10. El miércoles 4 de noviembre te voy a preguntar cómo va.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 7051 ms
- Leda → Marcos: «Quedó anotado que preveés terminar Revisar comunicaciones industriales de la comprimidora el viernes 30 de octubre, la fecha comprometida. Ismael ya no recibirá el aviso sobre la previsión del 4 de noviembre. El viernes 30 te voy a preguntar cómo va.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 2

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Con cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora. Te voy a pedir el estado el viernes 30 de octubre.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 5736 ms
- Leda → Marcos: «Esa pregunta ya se había cerrado ayer con Programar PLC de la comprimidora. Elegir Revisar comunicaciones industriales de la comprimidora no cambió nada. El viernes 30 de octubre te voy a pedir el estado de Programar PLC de la comprimidora.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3340 ms
- Leda → Marcos: «Ah, entendido. Quedó anotado que hoy también arrancaste Revisar comunicaciones industriales de la comprimidora. El viernes 30 de octubre te voy a pedir el estado de esa tarea.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6366 ms
- Leda → Marcos: «Quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre porque esperás el switch. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían 3 días hábiles de atraso. Ismael Soschinski se enterará mañana a las 10:00. Te voy a pedir el estado el miércoles 4 de noviembre.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 5868 ms
- Leda → Marcos: «Quedó anotado que, como llegó el switch, ahora prevés terminar Revisar comunicaciones industriales de la comprimidora el viernes 30 de octubre, la fecha comprometida. Ismael no recibirá el aviso sobre la previsión anterior. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 3

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Con cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora; está en curso. El viernes 30 de octubre te voy a pedir el estado.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 5452 ms
- Leda → Marcos: «La pregunta ya se había cerrado ayer con Programar PLC de la comprimidora. Tocar Revisar comunicaciones industriales de la comprimidora no cambió nada. El viernes 30 de octubre te voy a pedir el estado de Programar PLC de la comprimidora.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 5223 ms
- Leda → Marcos: «Ah, entendido: también quedó anotado que arrancaste hoy Revisar comunicaciones industriales de la comprimidora; está en curso. El viernes 30 de octubre te voy a pedir el estado de esa tarea.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6061 ms
- Leda → Marcos: «Quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre porque esperás el switch. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían 3 días hábiles de atraso. Ismael Soschinski recibirá el aviso mañana a las 10. El miércoles 4 de noviembre te voy a pedir el estado de la tarea.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 7920 ms
- Leda → Marcos: «Quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el viernes 30 de octubre porque llegó el switch. Esa sigue siendo la fecha comprometida. Ismael no recibirá el aviso sobre la previsión anterior. El viernes 30 te voy a pedir el estado de la tarea.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 4

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos empezaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que empezaste Programar PLC de la comprimidora. Te voy a pedir el estado el viernes 30 de octubre.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 4758 ms
- Leda → Marcos: «La pregunta ya se había cerrado ayer con Programar PLC de la comprimidora. Al elegir Revisar comunicaciones industriales de la comprimidora, no cambió nada. Si también empezaste esa tarea, avisame por mensaje.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3084 ms
- Leda → Marcos: «Quedó anotado que hoy empezaste Revisar comunicaciones industriales de la comprimidora. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 5348 ms
- Leda → Marcos: «Quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre porque esperás el switch. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían 3 días hábiles de atraso. Ismael Soschinski se enterará mañana a las 10:00. Te voy a pedir el estado el miércoles 4 de noviembre.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 7545 ms
- Leda → Marcos: «Quedó anotado que, como llegó el switch, ahora prevés terminar Revisar comunicaciones industriales de la comprimidora el viernes 30 de octubre, la fecha comprometida. Ismael Soschinski no recibirá el aviso sobre la previsión anterior. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 5

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que empezaste Programar PLC de la comprimidora. Te voy a pedir el estado el viernes 30 de octubre.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 3730 ms
- Leda → Marcos: «Esa pregunta ya se cerró ayer con Programar PLC de la comprimidora, así que tocar Revisar comunicaciones industriales de la comprimidora no cambió nada. Te voy a pedir el estado de Programar PLC de la comprimidora el viernes 30 de octubre.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4306 ms
- Leda → Marcos: «Ah, entendí: quedó anotado que hoy empezaste Revisar comunicaciones industriales de la comprimidora. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6064 ms
- Leda → Marcos: «Quedó anotado que preveés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre porque esperás el switch. La fecha comprometida sigue siendo el viernes 30 de octubre; si terminás el 4, serían tres días hábiles de atraso. Ismael Soschinski se enterará mañana a las 10:00. Te voy a pedir el estado el miércoles 4 de noviembre.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 5940 ms
- Leda → Marcos: «Quedó anotado que, como llegó el switch, preveés terminar Revisar comunicaciones industriales de la comprimidora el viernes 30 de octubre, la fecha comprometida. Ismael Soschinski no recibirá el aviso sobre la previsión anterior. Te voy a pedir el estado el viernes 30.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 12 · Algo que no está en la lista · vez 1

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 7011 ms
- Leda → Marcos: «Entiendo que estás tapado con lo de la paila. No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; el cambio de responsable lo decide Ismael Soschinski. ¿Querés que anote para cuándo prevés terminarla, teniendo en cuenta lo de la paila?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso", "estado_desde": "desconocido"}]`
- latencia: 6556 ms
- Leda → Marcos: «Entendido, seguís con «Programar PLC de la comprimidora». No quedó anotada ninguna previsión. La tarea ya figura en curso, aunque no tengo registrado cuándo la arrancaste, así que no puedo anotar el inicio ahora. Seguí con la tarea y avisame cuando tengas una previsión.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 4769 ms
- Leda → Marcos: «No puedo recordarte el turno con el médico; hago seguimiento de las tareas del equipo. Poné un recordatorio para el viernes en tu calendario.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6370 ms
- Leda → Marcos: «Por el pedido del recordatorio, el administrador recibirá un aviso hoy a las 10:15; todavía no le llegó. Para el turno del viernes, poné un recordatorio en tu calendario.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 5138 ms
- Leda → Marcos: «Entiendo que terminaste «Programar PLC de la comprimidora». Todavía no puedo recibir la entrega por chat y no hay otra forma definida. Consultá con el equipo cómo entregarla.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6200 ms
- Leda → Marcos: «Además de «Programar PLC de la comprimidora», que todavía figura en curso y vence el viernes 23 de octubre, tenés asignada «Revisar comunicaciones industriales de la comprimidora», aún sin empezar, con vencimiento el viernes 30 de octubre. Consultá con el equipo cómo entregar la del PLC.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 2

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Programar PLC de la comprimidora vence el viernes 23 de octubre, dentro de tres días hábiles. Seguí con esa tarea; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 9741 ms
- Leda → Marcos: «Pasar Programar PLC de la comprimidora a Nahuel no se puede hacer por chat; lo decide Ismael Soschinski. Puedo anotar una previsión de cuándo la terminarías, con el motivo que ya me contaste: estás tapado con lo de la paila. ¿Querés que la anote? Si es así, decime para cuándo la ves.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso", "estado_desde": "desconocido"}]`
- latencia: 7304 ms
- Leda → Marcos: «Entendido, seguís con Programar PLC de la comprimidora. Dejé sin efecto la propuesta de anotar una previsión y no anoté ninguna. La tarea ya figura en curso, aunque no tengo registrado desde cuándo, así que no pude volver a anotar el inicio. Seguí con la tarea.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6355 ms
- Leda → Marcos: «No puedo recordarte el turno con el médico el viernes. Poné una alarma en tu celular para acordarte.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 7414 ms
- Leda → Marcos: «Si te referís al recordatorio del turno médico, al administrador le va a llegar hoy martes 20 de octubre a las 10:15 un aviso de que lo pediste. Yo no puedo recordártelo el viernes; poné una alarma en tu celular.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 6342 ms
- Leda → Marcos: «Me contás que terminaste Programar PLC de la comprimidora. Todavía no puedo recibir la entrega por chat y no hay otra forma definida para hacerlo. Conservá el trabajo por ahora.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 7336 ms
- Leda → Marcos: «Tenés dos tareas pendientes: Programar PLC de la comprimidora, que sigue en curso y vence el viernes 23 de octubre, y Revisar comunicaciones industriales de la comprimidora, que tenés asignada y vence el viernes 30 de octubre. Aunque me contaste que terminaste la del PLC, todavía figura en curso: no puedo recibir la entrega por chat. Conservá ese trabajo por ahora.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 3

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6883 ms
- Leda → Marcos: «No puedo pasarle “Programar PLC de la comprimidora” a Nahuel por chat; ese cambio lo decide Ismael Soschinski. ¿Querés que anote una previsión de cuándo podrías terminarla, por lo de la paila?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso", "estado_desde": "desconocido"}]`
- latencia: 8134 ms
- Leda → Marcos: «Entendido, no anoté ninguna previsión. “Programar PLC de la comprimidora” ya figura en curso, aunque no tengo registrado desde cuándo; por eso no puedo volver a anotar que la arrancaste. Podés seguir con la tarea.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 5676 ms
- Leda → Marcos: «No puedo recordarte el turno médico del viernes por este chat; hago seguimiento de las tareas del equipo. Para que no se te pase, agendá un recordatorio en tu calendario.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5716 ms
- Leda → Marcos: «Al administrador le va a llegar hoy a las 10:15 un aviso de que pediste un recordatorio para el turno médico. Eso no te programa el recordatorio; agendalo en tu calendario para que no se te pase.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 6536 ms
- Leda → Marcos: «Entiendo que terminaste “Programar PLC de la comprimidora”. Todavía no puedo recibir la entrega por chat y no hay otra forma definida. Cuando se defina cómo entregarla, hacelo por esa vía.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6596 ms
- Leda → Marcos: «Tenés dos tareas pendientes: “Programar PLC de la comprimidora” sigue figurando en curso, aunque me contaste que la terminaste; vence el viernes 23 de octubre. “Revisar comunicaciones industriales de la comprimidora” está asignada, todavía sin empezar, y vence el viernes 30 de octubre. Podés avanzar con la revisión de comunicaciones.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 4

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 7001 ms
- Leda → Marcos: «Entiendo que estás tapado con lo de la paila. No puedo pasarle “Programar PLC de la comprimidora” a Nahuel por chat; ese cambio lo decide Ismael Soschinski. ¿Querés que anote para cuándo preveés terminarla, teniendo en cuenta lo de la paila?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso", "estado_desde": "desconocido"}]`
- latencia: 8684 ms
- Leda → Marcos: «Entendido, seguís con “Programar PLC de la comprimidora”. No anoté una previsión ni hubo cambios: ya figura en curso, aunque no tengo registrado desde cuándo la arrancaste. Por ahora, seguí con la tarea.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6606 ms
- Leda → Marcos: «No puedo recordarte el turno médico por acá; solo hago seguimiento de las tareas del equipo. Para acordarte, poné un recordatorio para el viernes en tu calendario.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5455 ms
- Leda → Marcos: «Al administrador le va a llegar un aviso de que pediste el recordatorio del turno médico. Para acordarte, poné un recordatorio en tu calendario.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 4746 ms
- Leda → Marcos: «Entiendo que terminaste “Programar PLC de la comprimidora”. Todavía no puedo recibir la entrega por chat y no hay otra forma definida. Por ahora, conservá el trabajo terminado.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6193 ms
- Leda → Marcos: «Te figuran dos tareas pendientes: “Programar PLC de la comprimidora”, en curso y con vencimiento el viernes 23 de octubre, y “Revisar comunicaciones industriales de la comprimidora”, asignada y con vencimiento el viernes 30 de octubre. Aunque me contaste que terminaste la del PLC, sigue figurando en curso porque todavía no puedo recibir la entrega por chat.

Por ahora, conservá ese trabajo y podés avanzar con la revisión de comunicaciones.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 5

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 5884 ms
- Leda → Marcos: «Entiendo que estás tapado con lo de la paila. No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; el cambio de responsable lo decide Ismael Soschinski. ¿Querés que anote para cuándo prevés terminarla por lo de la paila?»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea pasó a Nahuel
- [ ] no dice: que le avisó a Nahuel o a Ismael
- [ ] no dice: que le va a pasar el pedido a Ismael
- [ ] no dice: "consultá con la administración" sin una persona
- [ ] no dice: nombres de jugadas o herramientas

**Paso 3.** Marcos (2026-10-20 10:12): «no, la saco igual. ya la arranque eh»
- jugadas: `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso", "estado_desde": "desconocido"}]`
- latencia: 9232 ms
- Leda → Marcos: «Entendido, seguís vos con «Programar PLC de la comprimidora». No quedó anotada ninguna previsión. La tarea ya figura en curso, aunque no tengo registrado desde cuándo la arrancaste, así que no anoté otro inicio. Seguí con ella y avisame si hay novedades.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 5410 ms
- Leda → Marcos: «No puedo recordarte por acá el turno con el médico del viernes. Poné un recordatorio en tu calendario para que no se te pase.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que le avisó al administrador
- [ ] no dice: que se lo va a recordar
- [ ] no dice: nombres de jugadas o herramientas
- [ ] no dice: el nombre de alguien (nadie se ocupa de esto en los datos)

**Paso 5.** Marcos (2026-10-20 10:16): «y eso le avisaste a alguien?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6189 ms
- Leda → Marcos: «Al administrador le va a llegar un aviso de que pediste el recordatorio hoy, martes 20 de octubre, a las 10:15. Para no olvidarte del turno, poné un recordatorio en tu calendario.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 4609 ms
- Leda → Marcos: «Entiendo que terminaste «Programar PLC de la comprimidora». Todavía no puedo recibir la entrega por chat y no hay otra forma definida para hacerlo. Por ahora, conservá el trabajo terminado.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6158 ms
- Leda → Marcos: «Tenés dos tareas pendientes: «Programar PLC de la comprimidora» todavía figura en curso y vence el viernes 23 de octubre; «Revisar comunicaciones industriales de la comprimidora» está asignada, aún sin empezar, y vence el viernes 30 de octubre. Aunque me contaste que terminaste la del PLC, todavía no puedo recibir la entrega por chat. Por ahora, conservá ese trabajo terminado y avanzá con la revisión de comunicaciones.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, «Integrar datos de la comprimidora en CoreLabs» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Te aviso que «Programar PLC de la comprimidora» y «Revisar comunicaciones industriales de la comprimidora» vencen el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3905 ms
- Leda → Marcos: «¿Cuál arrancaste: «Programar PLC de la comprimidora» o «Revisar comunicaciones industriales de la comprimidora»?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3259 ms
- Leda → Marcos: «Quedó anotado que arrancaste «Programar PLC de la comprimidora»; está en curso. El viernes 23 de octubre te voy a pedir cómo va.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 2

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, te aviso que «Integrar datos de la comprimidora en CoreLabs» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 2747 ms
- Leda → Marcos: «¿Con cuál arrancaste: “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3803 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”; está en curso. El viernes 23 de octubre te voy a pedir cómo sigue.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, te aviso que «Integrar datos de la comprimidora en CoreLabs» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que «Programar PLC de la comprimidora» y «Revisar comunicaciones industriales de la comprimidora» vencen el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3357 ms
- Leda → Marcos: «¿Cuál de las dos tareas arrancaste: «Programar PLC de la comprimidora» o «Revisar comunicaciones industriales de la comprimidora»?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3150 ms
- Leda → Marcos: «Quedó anotado que arrancaste «Programar PLC de la comprimidora»; está en curso. El viernes 23 de octubre te voy a pedir el estado de esa tarea.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 4

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, te aviso que «Integrar datos de la comprimidora en CoreLabs» vence el viernes 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3122 ms
- Leda → Marcos: «¿Arrancaste con “Programar PLC de la comprimidora” o con “Revisar comunicaciones industriales de la comprimidora”?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3263 ms
- Leda → Marcos: «Quedó anotado que arrancaste con “Programar PLC de la comprimidora”. El viernes 23 de octubre te voy a preguntar cómo va.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 5

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” y “Revisar comunicaciones industriales de la comprimidora” vencen el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: ««Integrar datos de la comprimidora en CoreLabs» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: las dos tareas de Marcos
- [ ] dice: que vencen el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de Ariel

**Paso 2.** Marcos (2026-10-20 10:30): «arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3267 ms
- Leda → Marcos: «¿Cuál de las dos empezaste: “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6415 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”; está en curso. El viernes 23 de octubre te voy a pedir cómo viene.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 1

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5507 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora». Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 2759 ms
- Leda → Marcos: «Quedó anotado que también empezaste «Revisar comunicaciones industriales de la comprimidora». Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 2

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4304 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora». El viernes 23 de octubre te voy a pedir cómo va.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3688 ms
- Leda → Marcos: «Quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora». El viernes 30 de octubre te voy a pedir cómo va.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 3

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4842 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» y que está en curso. El viernes 23 de octubre te voy a pedir cómo viene.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3243 ms
- Leda → Marcos: «Quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora» y que está en curso. El viernes 30 de octubre te voy a pedir cómo viene.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 4

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6821 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora» y está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 2991 ms
- Leda → Marcos: «Quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora» y está en curso. El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 5

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4802 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora”. Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3199 ms
- Leda → Marcos: «Quedó anotado que también empezaste “Revisar comunicaciones industriales de la comprimidora”. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 15 · Voy bien, la tengo casi lista · vez 1

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el martes 27 de octubre, en tres días hábiles. No hace falta responder.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, martes 27 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5341 ms
- Leda → Marcos: «Anoté que me contaste que «Programar PLC de la comprimidora» va bien y la tenés casi lista. Todavía falta saber si la terminaste, para cuándo prevés terminarla o si estás trabado. Mañana a las 10 te vuelvo a consultar.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que «Programar PLC de la comprimidora» iba bien y la tenías casi lista. La tarea venció ayer y lleva un día hábil de atraso; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 2, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 7146 ms
- Leda → Marcos: «Anoté que seguís con «Programar PLC de la comprimidora» y que está todo en orden. La tarea venció ayer y lleva un día hábil de atraso. ¿Para qué día prevés terminarla?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7259 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida sigue siendo el martes 27 de octubre; si la terminás el martes 3, serán cinco días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» sigue dependiendo de esa tarea. Ismael Soschinski recibirá el aviso hoy a las 10:45. Te vuelvo a pedir el estado el martes 3.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida fue ayer, martes 27 de octubre; si se cumple la previsión, serían 5 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» sigue abierta y depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence el viernes 6 de noviembre, en tres días hábiles; por ese aviso no hace falta responder.

«Programar PLC de la comprimidora» sigue en curso. Preveías terminarla hoy, martes 3, y lleva cinco días hábiles de atraso. Ismael ya conoce esa previsión. La revisión de comunicaciones no puede arrancar hasta que termines la programación. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 2

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el martes 27 de octubre, en tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, martes 27 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 4782 ms
- Leda → Marcos: «Quedó anotado que vas bien y tenés casi lista «Programar PLC de la comprimidora». Mañana, miércoles 28 de octubre a las 10, te vuelvo a preguntar si la terminaste o, si no, para cuándo prevés terminarla y si estás trabado.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que tenías casi lista «Programar PLC de la comprimidora». La tarea sigue en curso y lleva un día hábil de atraso; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 2, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 9077 ms
- Leda → Marcos: «Quedó anotado que seguís con «Programar PLC de la comprimidora» y que todo está en orden. La tarea venció ayer, martes 27 de octubre, y lleva un día hábil de atraso. Mañana, jueves 29 a las 10, te volveré a pedir el estado. ¿Para qué día prevés tenerla lista?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5741 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida sigue siendo ayer, martes 27 de octubre; si la terminás el 3, tendrá cinco días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá hoy a las 10:45 un aviso sobre tu previsión. El martes 3 te pediré el estado.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida fue ayer, martes 27 de octubre: si se cumple la previsión, la tarea tendrá 5 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Marcos, hoy es la fecha para la que preveías terminar «Programar PLC de la comprimidora». La tarea sigue en curso y lleva cinco días hábiles de atraso; Ismael ya conoce tu previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines y vence el viernes 6 de noviembre.

¿Terminaste «Programar PLC de la comprimidora» o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 3

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el martes 27 de octubre, en tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Hoy, martes 27 de octubre, vence «Programar PLC de la comprimidora». «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si no, para cuándo estimás terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5700 ms
- Leda → Marcos: «Anoté que vas bien y que tenés casi lista «Programar PLC de la comprimidora». Mañana, miércoles 28, a las 10 te vuelvo a preguntar si la terminaste o, si no, para cuándo estimás terminarla y si estás trabado.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que tenías casi lista «Programar PLC de la comprimidora». Hoy lleva un día hábil de atraso, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si no, para cuándo estimás terminarla y si estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 2, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 4634 ms
- Leda → Marcos: «Anoté que seguís con «Programar PLC de la comprimidora» y que todo está en orden. Lleva un día hábil de atraso; mañana, jueves 29, a las 10 te volveré a pedir el estado. ¿Para qué día estimás terminarla?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 6842 ms
- Leda → Marcos: «Anoté que estimás terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida fue ayer, martes 27 de octubre; si terminás el 3, serían cinco días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Hoy a las 10:45 Ismael Soschinski recibirá un aviso sobre tu previsión. En lugar de mañana, te pediré el estado el martes 3 de noviembre.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida era ayer, martes 27 de octubre; si se cumple la previsión, la tarea tendrá 5 días hábiles de atraso. De ella depende «Revisar comunicaciones industriales de la comprimidora». No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Hoy, martes 3 de noviembre, es la fecha que estimaste para terminar «Programar PLC de la comprimidora». Lleva cinco días hábiles de atraso e Ismael Soschinski ya conoce tu previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines y vence el viernes 6 de noviembre, en tres días hábiles. ¿La terminaste o, si no, para cuándo estimás terminarla y si estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 4

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el martes 27 de octubre. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Hoy, martes 27 de octubre, vence «Programar PLC de la comprimidora». «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 4754 ms
- Leda → Marcos: «Anoté que «Programar PLC de la comprimidora» va bien y la tenés casi lista. Todavía falta saber si la terminaste o, si no, para cuándo prevés terminarla y si está trabada. Mañana, miércoles 28 de octubre, a las 10 te vuelvo a pedir ese estado.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Marcos, ayer me contaste que «Programar PLC de la comprimidora» iba bien y estaba casi lista. Venció ayer y lleva un día hábil de atraso; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 2, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 6024 ms
- Leda → Marcos: «Anoté que seguís con «Programar PLC de la comprimidora». Venció ayer y lleva un día hábil de atraso. Mañana, jueves 29 de octubre, a las 10 te vuelvo a pedir el estado. ¿Para qué día prevés terminarla?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5387 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida sigue siendo el martes 27 de octubre; si se cumple tu previsión, serán cinco días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá hoy a las 10:45 un aviso sobre tu previsión. El martes 3 te voy a pedir el estado.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida fue ayer, martes 27 de octubre; si se cumple la previsión, la tarea tendrá 5 días hábiles de atraso. De ella depende «Revisar comunicaciones industriales de la comprimidora». No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence el viernes 6 de noviembre, en tres días hábiles. Por ese aviso no hace falta que respondas.

«Programar PLC de la comprimidora» lleva cinco días hábiles de atraso y preveías terminarla hoy. Ismael Soschinski ya conoce esa previsión. La revisión de comunicaciones no puede arrancar hasta que termines la programación. ¿La terminaste o, si no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el martes 27 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» vence hoy, martes 27 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo estimás terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5360 ms
- Leda → Marcos: «Anoté que vas bien con «Programar PLC de la comprimidora» y que la tenés casi lista. Mañana, miércoles 28 a las 10, te vuelvo a preguntar si la terminaste o para cuándo estimás terminarla.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que «Programar PLC de la comprimidora» estaba casi lista. Venció ayer y lleva un día hábil de atraso; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo estimás terminarla o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 2, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 5948 ms
- Leda → Marcos: «Anoté que seguís con «Programar PLC de la comprimidora» y que todo está en orden. La fecha comprometida fue ayer y lleva un día hábil de atraso. Mañana, jueves 29 a las 10, te volveré a pedir el estado. ¿Para qué día estimás tenerla lista?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5278 ms
- Leda → Marcos: «Anoté que estimás terminar «Programar PLC de la comprimidora» el martes 3 de noviembre. La fecha comprometida sigue siendo el martes 27 de octubre; si se cumple tu previsión, serán cinco días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá hoy a las 10:45 un aviso con tu previsión. El martes 3 te pediré el estado.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora el martes 3 de noviembre. La fecha comprometida fue ayer, martes 27 de octubre: si se cumple la previsión, serán 5 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Hoy, martes 3 de noviembre, es la fecha que estimaste para terminar «Programar PLC de la comprimidora». Lleva cinco días hábiles de atraso e Ismael Soschinski ya conoce tu previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines y vence el viernes 6 de noviembre, dentro de tres días hábiles. ¿La terminaste, para cuándo estimás terminarla o estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 16 · Arranqué hoy, con la tarea vencida · vez 1

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo prevés terminarla y tenés alguna traba para avanzar?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo prevés terminarla y tenés alguna traba para avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"llega": "2026-10-27T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 4940 ms
- Leda → Marcos: «Quedó anotado que empezaste hoy «Programar PLC de la comprimidora». La fecha comprometida era el viernes 23 y lleva un día hábil de atraso. Mañana a las 10 te volveré a pedir el estado. ¿Para qué día prevés tenerla terminada?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 6058 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el miércoles 28. La fecha comprometida sigue siendo el viernes 23; si la terminás el miércoles, tendrá tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá el aviso hoy a las 10:25. El miércoles te pediré el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos prevé terminar Programar PLC de la comprimidora el miércoles 28, pasado mañana. La fecha comprometida era el viernes 23; si cumple esa previsión, terminará con 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 y lleva tres días hábiles de atraso. Preveías terminarla hoy; Ismael Soschinski ya está al tanto de esa previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y tenés alguna traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 2

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo prevés terminarla y hay algo que te impida avanzar?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 de octubre y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"llega": "2026-10-27T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 5309 ms
- Leda → Marcos: «Quedó anotado que hoy empezaste «Programar PLC de la comprimidora». Venció el viernes 23 de octubre y lleva un día hábil de atraso. Mañana, martes 27 de octubre, a las 10:00 volveré a preguntarte cómo va. ¿Para qué día vas a tenerla?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5673 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23; si la terminás el miércoles, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» sigue esperando que la termines. Ismael Soschinski recibirá el aviso hoy a las 10:25. El miércoles te pediré el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el miércoles 28, pasado mañana. La fecha comprometida era el viernes 23; si se cumple la previsión, tendrá 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» sigue abierta y depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 de octubre y lleva tres días hábiles de atraso. Habías previsto terminarla hoy, miércoles 28; Ismael Soschinski ya está al tanto de esa previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 3

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: ««Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo calculás terminarla y hay algo que te impida avanzar?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 de octubre y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo calculás terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"llega": "2026-10-27T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 4901 ms
- Leda → Marcos: «Quedó anotado que arrancaste hoy «Programar PLC de la comprimidora». La fecha comprometida fue el viernes 23 de octubre y lleva un día hábil de atraso. Mañana martes a las 10 te volveré a pedir el estado. ¿Para qué día calculás terminarla?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5955 ms
- Leda → Marcos: «Quedó anotado que calculás terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23; si se cumple tu previsión, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá hoy a las 10:25 un aviso sobre la previsión. Te pediré el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos prevé terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28. La fecha comprometida era el viernes 23: si se cumple la previsión, serán 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» sigue abierta y depende de esa tarea. Es solo para que estés al tanto; no hace falta responder.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 y lleva tres días hábiles de atraso. Habías previsto terminarla hoy; Ismael Soschinski ya está al tanto de esa previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo calculás terminarla y si hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo prevés terminarla y hay algo que te esté trabando?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el viernes 23 y lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la empezaste, para cuándo prevés terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"llega": "2026-10-27T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 6560 ms
- Leda → Marcos: «Quedó anotado que empezaste hoy «Programar PLC de la comprimidora». Venció el viernes 23 y lleva un día hábil de atraso. Mañana a las 10 te volveré a pedir el estado. ¿Para qué día prevés terminarla?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5814 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el miércoles 28. La fecha comprometida sigue siendo el viernes 23: si cumplís esa previsión, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá hoy a las 10:25 un aviso sobre tu previsión. El miércoles te pediré el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos prevé terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28. La fecha comprometida era el viernes 23: si se cumple su previsión, serán 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» sigue abierta y depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 y lleva tres días hábiles de atraso. Preveías terminarla hoy e Ismael ya conoce esa previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 5

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya empezaste, para cuándo prevés terminar y hay algo que te esté trabando?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, «Programar PLC de la comprimidora» lleva un día hábil de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. Te vuelvo a consultar: ¿ya empezaste, para cuándo prevés terminar y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"llega": "2026-10-27T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 4669 ms
- Leda → Marcos: «Anoté que empezaste hoy «Programar PLC de la comprimidora». La fecha comprometida fue el viernes 23 de octubre y lleva un día hábil de atraso. Mañana martes 27 a las 10:00 te vuelvo a consultar por el estado. ¿Para cuándo prevés terminarla?»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5775 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23; si terminás el miércoles, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá el aviso hoy a las 10:25. Te consultaré por el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si cumple esa previsión, la tarea tendrá 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» lleva tres días hábiles de atraso y preveías terminarla hoy. Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 1

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Anoté que “Programar PLC de la comprimidora” está trabada porque esperás el switch. Mientras siga así, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6559 ms
- Leda → Marcos: «Anoté que llegó el switch y que “Programar PLC de la comprimidora” ya no está trabada por eso. Sigue en curso. Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Hoy, viernes 23 de octubre, vence “Programar PLC de la comprimidora”. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿Cómo viene: la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4758 ms
- Leda → Marcos: «Anoté que “Programar PLC de la comprimidora” volvió a quedar trabada porque se quemó la fuente. Mientras siga así, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 4686 ms
- Leda → Marcos: «Anoté que cambiaste la fuente y que “Programar PLC de la comprimidora” ya no está trabada por eso. Sigue en curso. Te voy a pedir el estado el lunes 26 de octubre a las 10.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «“Programar PLC de la comprimidora” lleva un día hábil de atraso. El viernes me contaste que cambiaste la fuente y seguías; “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que termine. ¿La terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 2

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. Tené presente la fecha; no hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque esperás el switch. Mientras siga así, no te voy a pedir el estado; el seguimiento se retoma cuando me cuentes que se destrabó. ¿Quién puede destrabarlo?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5127 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» ya no está trabada por la espera del switch y sigue en curso. Te voy a pedir el estado pasado mañana, viernes 23 de octubre.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 3980 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» volvió a trabarse porque se quemó la fuente. Mientras siga trabada, no te voy a pedir el estado; retomamos el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6074 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» ya no está trabada por la fuente quemada y sigue en curso. Te voy a pedir el estado el lunes 26 de octubre a las 10.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: ««Programar PLC de la comprimidora» sigue en curso y lleva un día hábil de atraso. Me contaste que cambiaste la fuente y seguís; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 3

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Quedó anotado que estás trabado con “Programar PLC de la comprimidora” porque esperás el switch. Mientras siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarlo?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5186 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” ya no está trabada por el switch y sigue en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Hoy viernes 23 de octubre vence “Programar PLC de la comprimidora”. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4673 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está otra vez trabada porque se quemó la fuente. Mientras siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6337 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” ya no está trabada por la fuente quemada y sigue en curso. El lunes 26 de octubre a las 10:00 te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «Hoy lunes 26 de octubre, “Programar PLC de la comprimidora” lleva un día hábil de atraso. El viernes me contaste que cambiaste la fuente y seguías. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 4

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque esperás el switch. Mientras siga trabada, no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6455 ms
- Leda → Marcos: «Quedó anotado que llegó el switch y que «Programar PLC de la comprimidora» ya no está trabada por eso. Sigue en curso. Pasado mañana, viernes 23 de octubre, te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Cómo viene: la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4341 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» volvió a trabarse porque se quemó la fuente. Mientras siga trabada, no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7069 ms
- Leda → Marcos: «Quedó anotado que cambiaste la fuente y que «Programar PLC de la comprimidora» ya no está trabada por eso. Sigue en curso. El lunes 26 de octubre a las 10 te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el viernes 23 de octubre y lleva un día hábil de atraso. Me contaste que cambiaste la fuente y seguiste; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 5

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque esperás el switch. Mientras siga así, no te voy a pedir el estado; retomamos el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarlo?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4636 ms
- Leda → Marcos: «Quedó anotado que llegó el switch y que «Programar PLC de la comprimidora» ya no está trabada por eso. Sigue en curso. Pasado mañana, viernes 23 de octubre, te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
- [ ] no dice: que arrancó la tarea
- [ ] no dice: una fecha para terminarla que nadie dio
- [ ] no dice: otra vez la pregunta de quién lo destraba
- [ ] no dice: que Ismael se enteró

**Paso 2.** nadie (2026-10-21 10:00, 2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: ninguna repregunta de quién lo destraba
- [ ] dice: nada a Ismael

**Paso 3.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4339 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» volvió a quedar trabada porque se quemó la fuente. Mientras siga trabada, no te voy a pedir el estado; retomamos el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5615 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» ya no está trabada por la fuente quemada y sigue en curso. El lunes 26 de octubre a las 10:00 te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 de octubre y lleva un día hábil de atraso. Me contaste que cambiaste la fuente y seguías; «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 1

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5288 ms
- Leda → Marcos: «Anoté que vas bien y que casi tenés «Programar PLC de la comprimidora». Sigo pendiente de saber si la terminaste, para cuándo prevés terminarla o si estás trabado. Te vuelvo a consultar el lunes 26 de octubre a las 10:00.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 6299 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida fue el viernes 23; si se cumple tu previsión, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. Ismael Soschinski recibirá un aviso hoy a las 10:00. Te pediré el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28 de octubre. La fecha comprometida es el viernes 23; si se cumple la previsión, tendrá 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy miércoles 28 de octubre es la fecha que preveías para terminar «Programar PLC de la comprimidora». Lleva tres días hábiles de atraso y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. Me habías contado que casi la tenías. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 2

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5403 ms
- Leda → Marcos: «Anoté que venís bien y casi tenés «Programar PLC de la comprimidora». Sigue pendiente saber si la terminaste o, si no, cuándo prevés terminarla y si está trabada. Te vuelvo a consultar el lunes 26 de octubre a las 10.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5275 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre, pasado mañana. Si se cumple, serán tres días hábiles después del vencimiento; «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá el aviso hoy a las 10. El miércoles te voy a pedir el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora el miércoles 28 de octubre, pasado mañana. La fecha comprometida era el viernes 23; si cumple esa previsión, la tarea tendrá 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora sigue abierta y depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es la fecha que previste para terminar «Programar PLC de la comprimidora». Lleva tres días hábiles de atraso e Ismael Soschinski ya está al tanto de tu previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 3

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 4893 ms
- Leda → Marcos: «Anoté que vas bien y que casi tenés «Programar PLC de la comprimidora». El lunes 26 de octubre a las 10:00 te vuelvo a preguntar cómo viene.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7274 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23: si terminás el miércoles, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esta tarea. Ismael Soschinski recibirá el aviso hoy a las 10:00. Pasado mañana te voy a pedir el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23 de octubre: si cumple la previsión, serán 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, preveías terminar «Programar PLC de la comprimidora» hoy, miércoles 28 de octubre. La tarea lleva tres días hábiles de atraso e Ismael Soschinski ya está al tanto de la previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y hay algo que te impida avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 4

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: ««Programar PLC de la comprimidora» vence el viernes 23 de octubre. Tené presente esa fecha; no hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Hoy vence «Programar PLC de la comprimidora». «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6353 ms
- Leda → Marcos: «Quedó anotado que vas bien y casi tenés «Programar PLC de la comprimidora». Todavía necesito saber si la terminaste, para cuándo prevés terminarla o si estás trabado. Te voy a volver a pedir el estado el lunes 26 de octubre a las 10.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5209 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el miércoles 28. La fecha comprometida sigue siendo el viernes 23; si la terminás el miércoles, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. Ismael Soschinski recibirá el aviso hoy a las 10. Te pediré el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si se cumple la previsión, la tarea tendrá 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora sigue abierta y depende de ella. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Hoy es la fecha para la que preveías terminar «Programar PLC de la comprimidora». Sigue en curso y lleva tres días hábiles de atraso. Ismael ya conoce tu previsión, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 5

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5440 ms
- Leda → Marcos: «Anoté que vas bien y que casi tenés «Programar PLC de la comprimidora». Todavía falta saber si la terminaste o, si no, para cuándo prevés terminarla y si estás trabado. El lunes 26 de octubre a las 10:00 te vuelvo a pedir esos datos.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 5845 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23; si terminás el miércoles, serán 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. Ismael Soschinski se enterará hoy a las 10:00. El miércoles te voy a pedir el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar “Programar PLC de la comprimidora” pasado mañana, miércoles 28. La fecha comprometida era el viernes 23; si se cumple la previsión, serán 3 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es miércoles 28, la fecha que previste para terminar «Programar PLC de la comprimidora». Lleva 3 días hábiles de atraso; Ismael Soschinski ya está al tanto y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Me habías dicho que ibas bien y casi la tenías. ¿La terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

