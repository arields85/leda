# Transcripciones de la ronda e3-8-deepseek-flash

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
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
- latencia: 10197 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste hoy con Programar PLC de la comprimidora: la tarea queda en curso. El viernes 23 te voy a pedir el estado; por ahora no hace falta que respondas.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora y la tarea sigue en curso desde el martes 20. Contame cómo viene: si ya la terminaste, para cuándo la tenés o si estás trabado.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 2

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
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
- latencia: 10899 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste Programar PLC de la comprimidora, así que la tarea queda en curso. El viernes 23 te voy a pedir el estado.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 3

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
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
- latencia: 18436 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste con Programar PLC de la comprimidora: la tarea está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, te escribo por Programar PLC de la comprimidora: está en curso desde el martes 20 y hoy, viernes 23 de octubre, es la fecha comprometida. ¿Cómo viene: ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 4

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
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
- latencia: 9576 ms
- Leda → Marcos: «Quedó anotado que arrancaste hoy con Programar PLC de la comprimidora, y la tarea sigue en curso. Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora y sigue en curso. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»
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
- latencia: 9061 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste la Programar PLC de la comprimidora: la tarea quedó en curso.

El viernes 23 de octubre te voy a pedir el estado. No hace falta que respondas.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Hoy vence la tarea Programar PLC de la comprimidora, que está en curso desde el martes 20.

¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 02 · Llego el 27, el proveedor se demoró · vez 1

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 18401 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Programar PLC de la comprimidora el martes 27 de octubre, por la demora del proveedor. La fecha comprometida sigue siendo el viernes 23: si se cumple esa previsión, serían 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. Ismael Soschinski se entera hoy a las 15:40. El martes 27 te pido el estado.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos Tarquini me pasó una previsión nueva para Programar PLC de la comprimidora: la terminaría el martes 27 de octubre, porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si se cumple la previsión la tarea quedaría con 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Marcos, hoy, viernes 23 de octubre, vence Programar PLC de la comprimidora. Tenés anotada la previsión para el martes 27 de octubre por la demora del proveedor: si se cumple, serían 2 días hábiles de atraso. Ismael Soschinski ya se enteró. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine. El martes 27 te pido el estado. No hace falta que respondas.»
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
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Marcos, hoy te pido el estado de Programar PLC de la comprimidora: venció el viernes 23 de octubre y lleva 2 días hábiles de atraso; sigue en curso. Tenés la previsión para hoy, por la demora del proveedor, y si se cumple serían 2 días hábiles de atraso. Ismael Soschinski ya se enteró. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine.

Además, Revisar comunicaciones industriales de la comprimidora vence el viernes 30 de octubre: quedan 3 días hábiles. Eso no necesita respuesta.

¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, te pido otra vez el estado de Programar PLC de la comprimidora: venció el viernes 23 de octubre y lleva 3 días hábiles de atraso; sigue en curso. Tenés anotada la previsión para ayer, martes 27 de octubre, por la demora del proveedor: si se cumple, serían 2 días hábiles de atraso. Ismael Soschinski ya se enteró. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine.

¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, te pido el estado de Programar PLC de la comprimidora: venció el viernes 23 de octubre y lleva 4 días hábiles de atraso; sigue en curso. Tenés anotada la previsión para el martes 27 de octubre, por la demora del proveedor: si se cumple, serían 2 días hábiles de atraso. Ismael Soschinski ya se enteró. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine. Si no me contestás, se le avisa a Ismael Soschinski.

¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 2}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}

## 02 · Llego el 27, el proveedor se demoró · vez 2

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 15458 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Programar PLC de la comprimidora el martes 27 de octubre, por la demora del proveedor. La fecha comprometida sigue siendo el viernes 23: si se cumple esa previsión, serían 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. Ismael Soschinski se entera hoy a las 15:40. El martes 27 te pido el estado.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos Tarquini ahora prevé terminar Programar PLC de la comprimidora el martes 27 de octubre, porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23 de octubre; si se cumple esa previsión, serán 2 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora. Tenés anotado que prevés terminarla el martes 27 de octubre, por la demora del proveedor: si se cumple esa previsión, serían 2 días hábiles de atraso. Ismael Soschinski ya se enteró. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine. El martes 27 te pido el estado; no hace falta que respondas.»
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
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Marcos, hoy es la fecha que habías previsto para terminar Programar PLC de la comprimidora, por la demora del proveedor. La fecha comprometida era el viernes 23 de octubre, así que la tarea lleva 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termines.

También te aviso que Revisar comunicaciones industriales de la comprimidora vence el viernes 30 de octubre: quedan 3 días hábiles. Por eso no hace falta que respondas.

Contame cómo viene Programar PLC de la comprimidora: ¿ya la terminaste, está trabada o para cuándo prevés terminarla?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, Programar PLC de la comprimidora venció el viernes 23 de octubre y lleva 3 días hábiles de atraso. La fecha que habías previsto era ayer, martes 27. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine.

Contame cómo viene: ¿ya la terminaste, está trabada o para cuándo prevés terminarla?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 2}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}, {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 2}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}]
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 2}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}

## 02 · Llego el 27, el proveedor se demoró · vez 3

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 14888 ms
- Leda → Marcos: «Anoté que prevés terminar Programar PLC de la comprimidora el martes 27 de octubre, por la demora del proveedor. La fecha comprometida sigue siendo el viernes 23, así que si se cumple la previsión serán 2 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. Ismael Soschinski se entera hoy a las 15:40.

No hace falta que respondas. Te voy a pedir el estado el martes 27.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Ismael, Marcos dio una previsión nueva para Programar PLC de la comprimidora: ahora prevé terminarla el martes 27 de octubre, porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si se cumple esa previsión quedarían 2 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.

No hace falta que respondas.»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Programar PLC de la comprimidora vence hoy, viernes 23. Tu previsión sigue siendo el martes 27 de octubre: si se cumple, serán 2 días hábiles de atraso, por la demora del proveedor. De esa tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine. Ismael Soschinski ya está al tanto.

No hace falta que respondas. Te voy a pedir el estado el martes 27.»
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
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: «Marcos, hoy vence tu previsión para Programar PLC de la comprimidora. La fecha comprometida sigue siendo el viernes 23, así que si se cumple la previsión serán 2 días hábiles de atraso, por la demora del proveedor. De esa tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine. Ismael Soschinski ya está al tanto.

También te aviso que Revisar comunicaciones industriales de la comprimidora vence el viernes 30 de octubre: quedan 3 días hábiles. Ese aviso no necesita respuesta.

¿Cómo viene Programar PLC de la comprimidora: la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 2}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}]
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real [{'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 2}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}]
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': ['aviso_previo', 'pedido_de_estado'], 'tareas': ['COM', 'PLC'], 'el': '2026-10-27', 'hechos': [{'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-10-30', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-27', 'motivo': 'el proveedor se demoró', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 2}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}]}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 12060 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Programar PLC de la comprimidora el martes 27 de octubre, por la demora del proveedor. La fecha comprometida sigue siendo el viernes 23: si se cumple esa previsión, serán 2 días hábiles de atraso. Ismael Soschinski se entera hoy a las 15:40. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. El martes 27 te voy a pedir el estado.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Ismael, Marcos dio una previsión nueva para Programar PLC de la comprimidora: ahora prevé terminarla el martes 27 de octubre, porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si se cumple esa previsión quedarían 2 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora.

No hace falta que respondas.»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora. Tenés una previsión vigente para el martes 27 de octubre, así que no hace falta que respondas. Ismael Soschinski ya se enteró. El martes 27 te voy a pedir el estado. No hace falta que respondas.»
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
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- (Leda no manda nada)
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}, {'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 02 · Llego el 27, el proveedor se demoró · vez 5

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 13191 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Programar PLC de la comprimidora el martes 27 de octubre, por la demora del proveedor. La fecha comprometida sigue siendo el viernes 23: si se cumple esa previsión, la tarea quedará con 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. Ismael Soschinski se entera hoy a las 15:40.

El martes 27 te voy a pedir el estado.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos Tarquini me pasó una previsión nueva para Programar PLC de la comprimidora: la terminaría el martes 27 de octubre, porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si se cumple la previsión la tarea quedaría con 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora y sigue en curso. Tenés previsto terminarla el martes 27 de octubre; si se cumple esa previsión, quedará con 2 días hábiles de atraso. Ismael Soschinski ya se enteró. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que termine.

El martes 27 te voy a pedir el estado. No hace falta que respondas ahora.»
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
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 2, 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- (Leda no manda nada)
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-28', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'seguimiento_por': 'prevision'}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-29', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'seguimiento_por': 'prevision', 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real []
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-30', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'atraso_dias_habiles': 5, 'pedido_desde': '2026-10-27', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}, {'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 11083 ms
- Leda → Marcos: «No se pudo anotar el bloqueo: falta indicar la tarea. ¿En cuál de estas es? Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora.» [botones: PLC, COM]
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta el repuesto'}], real [{'nombre': 'anotar_bloqueo', 'causa': 'falta el repuesto'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}
- **falla** [comprension] esperas abiertas después: esperado ['PLC'], real []

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-21) → Marcos: «La tarea Programar PLC de la comprimidora vence pasado mañana, viernes 23 de octubre: quedan 2 días hábiles. No hace falta responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 2}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta', 'tarea': 'PLC', 'hechos': {'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'sobre': {'jugada': 'anotar_bloqueo', 'causa': 'presente'}}}, real [{'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 2}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 2}}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 21027 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» [botones: PLC, COM]
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'no_sabe': True, 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 21708 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» [botones: PLC, COM]
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 2

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5721 ms
- Leda → Marcos: «Marcos, no pude anotar el bloqueo porque me falta saber de qué tarea se trata. ¿Cuál de estas dos es: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta el repuesto'}], real [{'nombre': 'anotar_bloqueo', 'causa': 'falta el repuesto'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'presente', 'pregunta': 'quien_destraba'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}
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
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1663 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» [botones: PLC, COM]
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un nombre de quién compra que nadie dio
- [ ] no dice: una fecha de llegada inventada
- [ ] no dice: que Ismael se va a enterar
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'no_sabe': True, 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'no_sabe': True}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['que_alguien_ayude', 'anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'quien_destraba': {'no_sabe': True}, 'salidas': ['que_alguien_ayude', 'anotar_prevision'], 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 6.** Marcos (2026-10-21 10:30): «no, hay que esperar que llegue nomas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2365 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» [botones: PLC, COM]
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 03 · Estoy trabado, falta el repuesto · vez 3

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2574 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 2101 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 21685 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
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

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 8903 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada por falta del repuesto. Mientras siga así no te voy a pedir el estado.

¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora sigue trabada por falta del repuesto y vence pasado mañana. Te vuelvo a preguntar: ¿quién puede destrabarla?»
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "no_sabe": true, "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 12494 ms
- Leda → Marcos: «Marcos, quedó anotado que no sabés quién puede destrabar Programar PLC de la comprimidora.

Para salir del bloqueo puedo pedirle ayuda a alguien del equipo, o anotar para cuándo prevés terminarla y por qué. ¿Cuál preferís?»
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
- latencia: 22272 ms
- Leda → Marcos: «Marcos, dejé sin efecto la propuesta y no quedó nada anotado.

Programar PLC de la comprimidora sigue trabada por falta del repuesto, así que mientras siga así no te voy a pedir el estado. Avisame cuando se destrabe.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «Marcos, te aviso que la tarea Revisar comunicaciones industriales de la comprimidora vence el viernes 30 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 5

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1586 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-21) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence pasado mañana, viernes 23 de octubre: quedan 2 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 2}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta', 'tarea': 'PLC', 'hechos': {'pregunta': 'quien_destraba', 'necesita_respuesta': True, 'sobre': {'jugada': 'anotar_bloqueo', 'causa': 'presente'}}}, real [{'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 2}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-21', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 2}}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [motor] esperas abiertas después: esperado ['PLC'], real []

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2079 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que no se sabe quién lo compra
- [ ] dice: salidas: que alguien lo ayude o anotar una fecha nueva
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 20976 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, te escribo por la tarea Programar PLC de la comprimidora: vence hoy, y Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. ¿Cómo viene: ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-23) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el martes 27 de octubre: te quedan 2 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 2}`
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-23', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 2}}

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, ¿cómo viene la tarea Programar PLC de la comprimidora? Vence hoy y sigue en curso, y hasta que la termines, Revisar comunicaciones industriales de la comprimidora no puede arrancar. Contame si ya la terminaste, para cuándo prevés terminarla o si estás trabado.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció ayer y lleva 1 día hábil de atraso; sigue en curso. Hasta que la termines, Revisar comunicaciones industriales de la comprimidora no puede arrancar. ¿Cómo viene? Contame si ya la terminaste, para cuándo prevés terminarla o si estás trabado.»
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
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real []

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

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el martes 27 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el martes 27 de octubre y lleva 2 días hábiles de atraso. Está en curso, y de ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés tenerla, o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-30) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el martes 27 de octubre y ya lleva 3 días hábiles de atraso. Sigue en curso, y de ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines.

Te vuelvo a preguntar: ¿la terminaste, para cuándo prevés tenerla, o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'vence': '2026-10-27', 'atraso_dias_habiles': 3, 'pedido_desde': '2026-10-27', 'pedidos_de_estado_sin_respuesta': 3, 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-30', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}

## 04 · No contesta · vez 3

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el martes 27 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-22', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, martes 27 de octubre, y sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo prevés terminarla o está trabada?»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció ayer, martes 27 de octubre, y lleva 1 día hábil de atraso: sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo prevés terminarla o está trabada?»
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
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real []

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-30) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el martes 27 de octubre y lleva 3 días hábiles de atraso: sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. Si no me contestás, se le va a avisar a Ismael Soschinski. ¿Ya la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'escalamiento', 'tarea': 'PLC', 'hechos': {'aviso': 'falta_de_respuesta', 'vence': '2026-10-27', 'atraso_dias_habiles': 3, 'pedido_desde': '2026-10-27', 'pedidos_de_estado_sin_respuesta': 3, 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}]}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-30', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}

## 04 · No contesta · vez 4

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el martes 27 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora y sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
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
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real []

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
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

## 04 · No contesta · vez 5

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Marcos, te escribo por Programar PLC de la comprimidora: la tarea está en curso, tenía fecha comprometida el martes 27 de octubre y lleva 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

¿Cómo viene: ya la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 3, 'atraso_dias_habiles': 2, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}

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

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2329 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-20', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[]`
- hechos: `[]`
- latencia: 21857 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 21680 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'falta que martin de IT me habilite el acceso a la red de planta'}, {'nombre': 'anotar_quien_destraba', 'quien': 'martin', 'puede_traer': ['tarea']}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [comprension] falta un efecto: quién destraba: esperado [{'tarea': 'PLC', 'alguien': True, 'no_sabe': False}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}], real []

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2190 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 20876 ms
- Leda → Marcos: «Quedó anotado que para Revisar comunicaciones industriales de la comprimidora preveés terminar el jueves 5 de noviembre; la fecha comprometida sigue siendo el viernes 30 de octubre, así que si se cumple la previsión serían 4 días hábiles de atraso. Ismael Soschinski se entera hoy a las 16:30, y el estado de esa tarea te lo voy a pedir el jueves 5 de noviembre.

De Programar PLC de la comprimidora me falta la causa del bloqueo: ¿qué te trabó?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 13588 ms
- Leda → Marcos: «Quedó anotado que Programar PLC de la comprimidora está trabada porque falta que Martín de IT te habilite el acceso a la red de planta, y que es él quien puede destrabarla. Mientras siga trabada no te voy a pedir el estado: el seguimiento vuelve cuando me cuentes que se destrabó.

No hace falta que respondas.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 3

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 21056 ms
- Leda → Marcos: «Anoté que arrancaste con Programar PLC de la comprimidora: la tarea queda en curso y te voy a pedir el estado el viernes 23 de octubre.

También anoté que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre, porque esperás el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple la previsión, serían 3 días hábiles de atraso. De esto se entera hoy Ismael Soschinski.

Próximo paso: te pido el estado del PLC el viernes 23 y el de comunicaciones el miércoles 4 de noviembre.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini ahora espera terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre, porque espera el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre y, si se cumple esa nueva fecha, la tarea quedará 3 días hábiles atrasada. No hay tareas abiertas que dependan de esta. No hace falta que respondas.»
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
- latencia: 17131 ms
- Leda → Marcos: «Anoté que la previsión de Revisar comunicaciones industriales de la comprimidora pasa al jueves 5 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple la previsión, serían 4 días hábiles de atraso. De esto se entera hoy Ismael Soschinski, a las 16:30, y te voy a pedir el estado el jueves 5.

Para anotar que Programar PLC de la comprimidora está trabada me falta la causa: ¿qué te trabó?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 25077 ms
- Leda → Marcos: «Anoté que Programar PLC de la comprimidora está trabada porque falta que Martin de IT te habilite el acceso a la red de planta, y que él es quien la puede destrabar.

Mientras siga así no te voy a pedir el estado: vuelvo a pedirlo cuando me cuentes que se destrabó.

Próximo paso: avisame cuando Martin te habilite el acceso.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 4

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"proximo_aviso": {"aviso": "aviso_previo", "llega": "2026-10-20T10:00:00-03:00"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 46561 ms
- Leda → Marcos: «Anoté que arrancaste con la Programar PLC de la comprimidora, así que quedó en curso. Hoy a las 10 te llega el aviso de que vence pronto.

De Revisar comunicaciones industriales de la comprimidora quedó anotado que prevés terminarla el miércoles 4 de noviembre porque esperás el switch nuevo. Eso no cambia la fecha comprometida, que sigue siendo el viernes 30 de octubre, y con esa previsión serían 3 días hábiles de atraso. Hoy a las 10:05 se le avisa a Ismael Soschinski.

El miércoles 4 de noviembre te voy a pedir el estado de esa tarea.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La Programar PLC de la comprimidora vence pronto: el viernes 23 de octubre, en 3 días hábiles. Podés seguir con la tarea para tenerla lista para esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini ahora espera terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre, porque espera el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre y, si se cumple esa nueva fecha, la tarea quedará 3 días hábiles atrasada. No hay tareas abiertas que dependan de esta. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4 y su motivo
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['PLC'], 'el': '2026-10-20', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}

**Paso 4.** Marcos (2026-10-20 16:30): «me trabe con el plc. y lo de comunicaciones al final es el jueves 5, no el 4»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 18872 ms
- Leda → Marcos: «De la Programar PLC de la comprimidora me falta la causa del bloqueo para dejarlo anotado.

En Revisar comunicaciones industriales de la comprimidora quedó anotado que prevés terminarla el jueves 5 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre: con esa previsión serían 4 días hábiles de atraso. Hoy a las 16:30 se le avisa a Ismael Soschinski. El jueves 5 de noviembre te voy a pedir el estado de esa tarea.

¿Qué es lo que traba la Programar PLC de la comprimidora?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 16223 ms
- Leda → Marcos: «Anoté que la Programar PLC de la comprimidora está trabada porque falta que Martin de IT te habilite el acceso a la red de planta, y que él es quien puede destrabarlo. Mientras siga trabada no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.

Avisame cuando se destrabe.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 5

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 1850 ms
- Leda → Marcos: «Anoté que arrancaste con Programar PLC de la comprimidora: la tarea queda en curso y te voy a pedir el estado el viernes 23 de octubre.

También anoté que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre, porque esperás el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple la previsión, serían 3 días hábiles de atraso. De esto se entera hoy Ismael Soschinski.

Próximo paso: te pido el estado del PLC el viernes 23 y el de comunicaciones el miércoles 4 de noviembre.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini ahora espera terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre, porque espera el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre y, si se cumple esa nueva fecha, la tarea quedará 3 días hábiles atrasada. No hay tareas abiertas que dependan de esta. No hace falta que respondas.»
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
- latencia: 21206 ms
- Leda → Marcos: «Me falta saber qué te trabó con Programar PLC de la comprimidora.

Anoté que prevés terminar Revisar comunicaciones industriales de la comprimidora el jueves 5 de noviembre, no el miércoles 4. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple la previsión, serían 4 días hábiles de atraso. De esto se entera hoy Ismael Soschinski, a las 16:30.

Te voy a pedir el estado de comunicaciones el jueves 5 de noviembre.

¿Qué te trabó con el PLC?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 37377 ms
- Leda → Marcos: «Anoté que Programar PLC de la comprimidora quedó trabada: falta que Martin de IT te habilite el acceso a la red de planta. También quedó anotado que Martin de IT es quien puede destrabarla.

Mientras siga trabada no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.

Próximo paso: avisame cuando Martin te habilite el acceso.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 06 · No, era la otra tarea · vez 1

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 7042 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste con Programar PLC de la comprimidora, así que la tarea queda en curso.

El viernes 23 te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 27640 ms
- Leda → Marcos: «Marcos, corregí lo anotado: Programar PLC de la comprimidora vuelve a quedar asignada, sin empezar. El arranque quedó anotado en Revisar comunicaciones industriales de la comprimidora, que ahora está en curso.

Queda pendiente que arranques el PLC: avisame cuando la empieces y lo anoto.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora y sigue sin empezar. Contame cómo viene: si ya la empezaste, para cuándo prevés terminarla y si estás trabada.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 9651 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste con Programar PLC de la comprimidora; la tarea queda en curso. El viernes 23 te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 15927 ms
- Leda → Marcos: «Listo: lo que había quedado anotado del PLC ya no vale, así que Programar PLC de la comprimidora vuelve a quedar asignada, sin empezar. En cambio, quedó anotado que arrancaste Revisar comunicaciones industriales de la comprimidora, que ahora queda en curso.

Cuando arranques el PLC, avisame.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, Programar PLC de la comprimidora vence hoy, viernes 23 de octubre.

¿Cómo viene: ya la empezaste, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 3

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 11189 ms
- Leda → Marcos: «Marcos, anoté que arrancaste esta mañana la tarea Programar PLC de la comprimidora: quedó en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 18304 ms
- Leda → Marcos: «Marcos, corregí: la tarea Programar PLC de la comprimidora vuelve a estar asignada, sin empezar. Anoté que arrancaste Revisar comunicaciones industriales de la comprimidora: quedó en curso. Cuando arranques el PLC, avisame.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'asignada', 'atraso_dias_habiles': 0}}, real []

## 06 · No, era la otra tarea · vez 4

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 1752 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste con Programar PLC de la comprimidora; la tarea queda en curso. El viernes 23 te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 2097 ms
- Leda → Marcos: «Listo: lo que había quedado anotado del PLC ya no vale, así que Programar PLC de la comprimidora vuelve a quedar asignada, sin empezar. En cambio, quedó anotado que arrancaste Revisar comunicaciones industriales de la comprimidora, que ahora queda en curso.

Cuando arranques el PLC, avisame.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, Programar PLC de la comprimidora vence hoy, viernes 23 de octubre.

¿Cómo viene: ya la empezaste, para cuándo prevés terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 7842 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste hoy con Programar PLC de la comprimidora, así que la tarea queda en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 14547 ms
- Leda → Marcos: «Corregido, Marcos: lo del arranque de Programar PLC de la comprimidora ya no vale, la tarea vuelve a quedar asignada. Quedó anotado que arrancaste hoy con Revisar comunicaciones industriales de la comprimidora, así que esa queda en curso. Cuando empieces con la del PLC, avisame.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy, viernes 23 de octubre, vence Programar PLC de la comprimidora. Contame cómo viene: si la empezaste, para cuándo prevés terminarla y si estás trabado con algo.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 07 · Dejá, no importa · vez 1

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7790 ms
- Leda → Marcos: «Marcos, no pude anotar el bloqueo de Programar PLC de la comprimidora porque me falta la causa. ¿Qué es lo que te está trabando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 13884 ms
- Leda → Marcos: «Marcos, la pregunta sobre el bloqueo de Programar PLC de la comprimidora quedó sin efecto y no se anotó nada. La tarea sigue con vencimiento el viernes 23. Si querés que registre el bloqueo, contame qué te está trabando.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora está en curso y vence hoy, viernes 23 de octubre. ¿Cómo viene: la terminaste, para cuándo la tenés o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 6016 ms
- Leda → Marcos: «Marcos, para anotar que la tarea Programar PLC de la comprimidora está trabada me falta la causa. ¿Qué es lo que te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 12014 ms
- Leda → Marcos: «Marcos, dejé sin efecto la pregunta sobre qué estaba frenando la tarea Programar PLC de la comprimidora: no quedó nada anotado. No queda nada pendiente; no hace falta que respondas.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, viernes 23 de octubre, y sigue en curso. ¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 3

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 9312 ms
- Leda → Marcos: «Marcos, para anotar que la tarea Programar PLC de la comprimidora está trabada me falta saber qué la traba. ¿Qué es lo que te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 10424 ms
- Leda → Marcos: «Listo, Marcos: dejé sin efecto la pregunta y no quedó nada anotado sobre el bloqueo de Programar PLC de la comprimidora.

Si más adelante querés que quede registrada la traba, contame qué la frena y la anoto.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'el': '2026-10-23', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'estado': 'en_curso'}}, real []

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7470 ms
- Leda → Marcos: «Marcos, para anotar que Programar PLC de la comprimidora está trabada me falta la causa. ¿Qué es lo que te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 17432 ms
- Leda → Marcos: «Marcos, dejé sin efecto la pregunta y no quedó anotado nada sobre Programar PLC de la comprimidora. Cuando quieras, podés seguir avanzando con la tarea.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, Programar PLC de la comprimidora vence hoy, viernes 23 de octubre. ¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 5

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 2099 ms
- Leda → Marcos: «Marcos, para anotar que la tarea Programar PLC de la comprimidora está trabada me falta saber qué la traba. ¿Qué es lo que te está frenando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 2302 ms
- Leda → Marcos: «Listo, Marcos: dejé sin efecto la pregunta y no quedó nada anotado sobre el bloqueo de Programar PLC de la comprimidora.

Si más adelante querés que quede registrada la traba, contame qué la frena y la anoto.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora y veo que la tenés en curso. ¿Cómo viene: la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 08 · Cambio de tema · vez 1

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 8909 ms
- Leda → Marcos: «Marcos, entiendo que estás trabado con Programar PLC de la comprimidora. Para anotar el bloqueo me falta la causa: ¿qué es lo que te traba?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 20152 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre, así que si se cumple la previsión serían 3 días hábiles de atraso. Hoy a las 10:43 se entera Ismael Soschinski.

¿Qué es lo que te traba en Programar PLC de la comprimidora?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini dio una previsión nueva para la tarea Revisar comunicaciones industriales de la comprimidora: prevé terminarla el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre, así que si se cumple esa previsión la tarea quedaría con 3 días hábiles de atraso. No hay tareas abiertas que dependan de esta. No hace falta que respondas.»
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
- latencia: 16738 ms
- Leda → Marcos: «Marcos, quedó anotado que Programar PLC de la comprimidora está trabada porque no te mandaron el programa del fabricante. Mientras siga así no te voy a pedir el estado; cuando me cuentes que se destrabó, retomo el seguimiento.

¿Quién puede destrabarlo?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 2

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5913 ms
- Leda → Marcos: «Marcos, para anotar el bloqueo de Programar PLC de la comprimidora me falta un dato: qué es lo que te está trabando.

¿Qué te impide avanzar?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 50928 ms
- Leda → Marcos: «Marcos, anoté que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple esa previsión, serían 3 días hábiles de atraso. El aviso le va a llegar hoy a Ismael.

¿Qué es lo que te está trabando en Programar PLC de la comprimidora?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini dio una nueva previsión para la tarea Revisar comunicaciones industriales de la comprimidora: la terminaría el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre, así que, si se cumple esa previsión, serían 3 días hábiles de atraso.

No hace falta que respondas.»
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
- latencia: 10478 ms
- Leda → Marcos: «Marcos, anoté el bloqueo de Programar PLC de la comprimidora: no te mandaron el programa del fabricante. Mientras siga trabada no te voy a pedir el estado.

¿Quién lo puede destrabar?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 3

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 6508 ms
- Leda → Marcos: «Marcos, para anotar que la tarea Programar PLC de la comprimidora está trabada me falta saber qué la traba. ¿Qué es lo que te está frenando?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 25187 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple esa previsión, serían 3 días hábiles de atraso. Hoy se entera Ismael Soschinski.

Y sobre Programar PLC de la comprimidora, ¿qué es lo que la está trabando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini dio una nueva previsión para la tarea Revisar comunicaciones industriales de la comprimidora: la terminaría el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre, así que, si se cumple esa previsión, serían 3 días hábiles de atraso.

No hace falta que respondas.»
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
- latencia: 16024 ms
- Leda → Marcos: «Marcos, quedó anotado que Programar PLC de la comprimidora está trabada porque no te mandaron el programa del fabricante.

¿Quién la puede destrabar?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 4

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 1988 ms
- Leda → Marcos: «Marcos, entiendo que estás trabado con Programar PLC de la comprimidora. Para anotar el bloqueo me falta la causa: ¿qué es lo que te traba?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 14276 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre. Si se cumple esa fecha, la tarea queda 3 días hábiles atrasada respecto del viernes 30 de octubre, que sigue siendo la fecha comprometida. Le aviso a Ismael Soschinski, que se entera hoy. Y el miércoles 4 de noviembre te voy a pedir el estado de esa tarea.

Sigo con Programar PLC de la comprimidora: ¿qué es lo que te traba?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Ismael, Marcos Tarquini dio una previsión nueva para Revisar comunicaciones industriales de la comprimidora: prevé terminarla el miércoles 4 de noviembre. La fecha comprometida es el viernes 30 de octubre, así que si se cumple esa previsión la tarea quedará con 3 días hábiles de atraso. No hace falta que respondas.»
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
- latencia: 9052 ms
- Leda → Marcos: «Marcos, quedó anotado que Programar PLC de la comprimidora está trabada porque no te mandaron el programa del fabricante. Mientras siga trabada no te voy a pedir el estado: el seguimiento vuelve cuando me cuentes que se destrabó.

¿Quién la puede destrabar?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 5

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 2871 ms
- Leda → Marcos: «Marcos, para anotar el bloqueo de Programar PLC de la comprimidora me falta un dato: qué es lo que te está trabando.

¿Qué te impide avanzar?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 40776 ms
- Leda → Marcos: «Marcos, anoté que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple esa previsión, serían 3 días hábiles de atraso. El aviso le va a llegar hoy a Ismael.

¿Qué es lo que te está trabando en Programar PLC de la comprimidora?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini dio una nueva previsión para la tarea Revisar comunicaciones industriales de la comprimidora: la terminaría el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre, así que, si se cumple esa previsión, serían 3 días hábiles de atraso.

No hace falta que respondas.»
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
- latencia: 2234 ms
- Leda → Marcos: «Marcos, anoté el bloqueo de Programar PLC de la comprimidora: no te mandaron el programa del fabricante. Mientras siga trabada no te voy a pedir el estado.

¿Quién lo puede destrabar?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 09 · Duda: ¿de qué tarea habla? · vez 1

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 8295 ms
- Leda → Marcos: «No pude anotar el inicio de hoy porque falta saber de qué tarea se trata.

¿De cuál de estas dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4452 ms
- Leda → Marcos: «Anoté que hoy arrancaste Revisar comunicaciones industriales de la comprimidora; queda en curso.

El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 2

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 1888 ms
- Leda → Marcos: «No pude anotar el inicio de hoy porque falta saber de qué tarea se trata.

¿De cuál de estas dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 5367 ms
- Leda → Marcos: «Quedó anotado el inicio de Revisar comunicaciones industriales de la comprimidora, así que la tarea queda en curso.

El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 3

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 1768 ms
- Leda → Marcos: «No pude anotar el inicio de hoy porque falta saber de qué tarea se trata.

¿De cuál de estas dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 2111 ms
- Leda → Marcos: «Anoté que hoy arrancaste Revisar comunicaciones industriales de la comprimidora; queda en curso.

El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 4

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 1750 ms
- Leda → Marcos: «No pude anotar el inicio de hoy porque falta saber de qué tarea se trata.

¿De cuál de estas dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1328 ms
- Leda → Marcos: «Quedó anotado el inicio de Revisar comunicaciones industriales de la comprimidora, así que la tarea queda en curso.

El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 5

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 2182 ms
- Leda → Marcos: «No pude anotar el inicio de hoy porque falta saber de qué tarea se trata.

¿De cuál de estas dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1308 ms
- Leda → Marcos: «Anoté que hoy arrancaste Revisar comunicaciones industriales de la comprimidora; queda en curso.

El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 10 · Escribir en lugar de tocar un botón · vez 1

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6259 ms
- Leda → Marcos: «Me falta saber de qué tarea de la comprimidora se trata para anotar el inicio: ¿Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 7475 ms
- Leda → Marcos: «Anoté el inicio de Programar PLC de la comprimidora: queda en curso. El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4719 ms
- Leda → Marcos: «No pude anotar el inicio: me falta saber cuál de las tareas de la comprimidora arrancaste.

¿Cuál es?

Programar PLC de la comprimidora
Revisar comunicaciones industriales de la comprimidora» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 10077 ms
- Leda → Marcos: «Anoté el inicio de Programar PLC de la comprimidora: queda en curso.

El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4598 ms
- Leda → Marcos: «No pude anotar el inicio porque me falta saber cuál de las tareas de la comprimidora arrancaste. ¿Es Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 7822 ms
- Leda → Marcos: «Listo, anoté el inicio de Programar PLC de la comprimidora, así que queda en curso. El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 4

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 7953 ms
- Leda → Marcos: «No pude anotar el inicio porque me falta saber de qué tarea de la comprimidora se trata. ¿Cuál arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 9532 ms
- Leda → Marcos: «Anoté el inicio de Programar PLC de la comprimidora, así que quedó en curso. El viernes 30 de octubre te voy a pedir cómo va.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 2316 ms
- Leda → Marcos: «Me falta saber de qué tarea de la comprimidora se trata para anotar el inicio: ¿Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 8526 ms
- Leda → Marcos: «Quedó anotado el inicio de Programar PLC de la comprimidora: la tarea queda en curso.

El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «No pude anotar el inicio: falta saber de qué tarea se trata.

¿Cuál de las dos arrancaste?

- Programar PLC de la comprimidora
- Revisar comunicaciones industriales de la comprimidora» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Anoté el inicio de Programar PLC de la comprimidora: quedó en curso. El viernes 30 de octubre te voy a pedir el estado. No hace falta que respondas.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 8624 ms
- Leda → Marcos: «La pregunta de cuál de las dos habías arrancado ya se cerró ayer con Programar PLC de la comprimidora, así que tocar Revisar comunicaciones industriales de la comprimidora no cambió nada.

El viernes 30 de octubre te voy a pedir el estado de Programar PLC de la comprimidora. No hace falta que respondas.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 25075 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2285 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-23T10:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 20917 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Para anotar el inicio me falta saber de qué tarea se trata: ¿cuál de las dos arrancaste, Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado el inicio de Programar PLC de la comprimidora: la tarea queda en curso. El viernes 30 de octubre te voy a pedir el estado.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 5629 ms
- Leda → Marcos: «Esa opción no cambió nada: la pregunta ya se había cerrado ayer con tu respuesta sobre Programar PLC de la comprimidora, que sigue en curso.

El viernes 30 de octubre te voy a pedir el estado de esa tarea.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 12258 ms
- Leda → Marcos: «Listo, quedó anotado el inicio de Revisar comunicaciones industriales de la comprimidora: queda en curso. El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2157 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-23T10:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2643 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «Para anotar el inicio me falta saber de qué tarea se trata. ¿Cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Listo, quedó anotado el inicio de Programar PLC de la comprimidora, que queda en curso. El viernes 30 de octubre te voy a pedir el estado.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 7754 ms
- Leda → Marcos: «La opción que tocaste no cambió nada: esa pregunta ya se había cerrado ayer, cuando elegiste Programar PLC de la comprimidora. El viernes 30 de octubre te voy a pedir el estado.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6680 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2266 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-23T10:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 3931 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «No pude anotar el inicio: falta saber de qué tarea se trata.

¿Cuál de las dos arrancaste?

- Programar PLC de la comprimidora
- Revisar comunicaciones industriales de la comprimidora» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Listo: quedó anotado el inicio de Programar PLC de la comprimidora, en curso.

El viernes 30 de octubre te voy a pedir el estado. No hace falta que respondas ahora.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 10028 ms
- Leda → Marcos: «Tocaste Revisar comunicaciones industriales de la comprimidora, pero no cambió nada: la pregunta de ayer ya quedó cerrada con tu respuesta, Programar PLC de la comprimidora.

El viernes 30 de octubre te pido el estado de Programar PLC de la comprimidora.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 10286 ms
- Leda → Marcos: «Listo: quedó anotado el inicio de Revisar comunicaciones industriales de la comprimidora, en curso.

El viernes 30 de octubre te voy a pedir el estado, igual que el de Programar PLC de la comprimidora. No hace falta que respondas ahora.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2304 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-23T10:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2242 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «No pude anotar el inicio: falta saber de qué tarea se trata.

¿Cuál de las dos arrancaste?

- Programar PLC de la comprimidora
- Revisar comunicaciones industriales de la comprimidora» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Anoté el inicio de Programar PLC de la comprimidora: quedó en curso. El viernes 30 de octubre te voy a pedir el estado. No hace falta que respondas.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 8868 ms
- Leda → Marcos: «No cambió nada: esa pregunta ya se había cerrado ayer, con tu respuesta sobre Programar PLC de la comprimidora.

Si querés que anote el inicio de Revisar comunicaciones industriales de la comprimidora, decímelo.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[]`
- hechos: `[]`
- latencia: 9326 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2816 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espero el switch'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-23T10:00'}}], real []

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1647 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1585 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 21266 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1923 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1612 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2697 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)
- **falla** [comprension] jugadas: esperado [{'nombre': 'entregar', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'PLC', 'otra_forma_de_hacerlo': 'ninguna_definida'}], real []

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1604 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 2

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2604 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 40052 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1816 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 8133 ms
- Leda → Marcos: «No, de eso no avisé a nadie: no tengo registro de haberle pasado el aviso a ninguna persona. Tus mensajes de esta mañana quedaron sin respuesta de mi parte, así que tampoco quedó nada confirmado.

Decime a quién querés que le avise y lo hago.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2782 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)
- **falla** [comprension] jugadas: esperado [{'nombre': 'entregar', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'PLC', 'otra_forma_de_hacerlo': 'ninguna_definida'}], real []

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1550 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 3

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1565 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1601 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6000 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1654 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4244 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)
- **falla** [comprension] jugadas: esperado [{'nombre': 'entregar', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'PLC', 'otra_forma_de_hacerlo': 'ninguna_definida'}], real []

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 4912 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 4

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1521 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 21024 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1888 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 32725 ms
- Leda → Marcos: «Sí, eso quedó registrado para que lo revise un administrador.

Lo del recordatorio del viernes con el médico quedó sin respuesta, así que no te lo puedo confirmar. Si querés, lo retomo.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 20577 ms
- Leda → Marcos: «Marcos, la entrega de Programar PLC de la comprimidora todavía no se recibe por chat, así que no quedó registrada. Y por ahora no hay otra forma definida para pasarla.

No hace falta que respondas.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1830 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 12 · Algo que no está en la lista · vez 5

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2184 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: que lo decide Ismael
- [ ] dice: como el motivo es que no llega con el tiempo, ofrece anotar una nueva previsión
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 20812 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [comprension] jugadas: esperado [{'nombre': 'cancelar'}, {'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'cancelar', 'resultado': 'cancelado'}, {'jugada': 'anotar_inicio', 'resultado': 'no_se_puede', 'motivo': 'estado', 'estado': 'en_curso'}], real []

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1687 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer
- [ ] dice: qué puede hacer por chat con sus tareas: anotar que arrancó, una fecha nueva o un bloqueo, y contarle qué tiene pendiente
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1943 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2206 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)
- **falla** [comprension] jugadas: esperado [{'nombre': 'entregar', 'tarea': 'PLC'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'entregar', 'resultado': 'no_por_chat', 'tarea': 'PLC', 'otra_forma_de_hacerlo': 'ninguna_definida'}], real []

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1590 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'en_curso', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'asignada', 'vence': '2026-10-30'}]}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2124 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1713 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 2

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1779 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 2058 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2100 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 2310 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 4

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1692 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1617 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 5

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2917 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1659 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'elegir', 'opcion': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 1

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2239 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2242 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 2

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 11541 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste con Programar PLC de la comprimidora, así que la tarea ya está en curso. El viernes 23 te voy a pedir el estado.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1561 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 3

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1577 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1624 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 4

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- (Leda no manda nada)
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'aviso_previo', 'tarea': 'PLC', 'hechos': {'vence': '2026-10-23', 'necesita_respuesta': False}}, real []
- **falla** [motor] último aviso de Marcos: esperado 'PLC', real None

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 7231 ms
- Leda → Marcos: «Marcos, para anotar el arranque me falta saber de qué tarea de la comprimidora se trata: ¿Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real [{'nombre': 'anotar_inicio'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 21334 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.» [botones: PLC, COM]
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 5

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que Programar PLC de la comprimidora vence el viernes 23 de octubre; quedan 3 días hábiles. Podés avanzar con la tarea para tenerla lista antes de esa fecha. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[]`
- hechos: `[]`
- latencia: 2113 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}], real []

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1571 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'COM'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'COM': 'en_curso'}, real {}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'COM'}], real []

## 15 · Voy bien, la tengo casi lista · vez 1

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 14734 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

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
- latencia: 2419 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1613 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-28T10:45'}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- (Leda no manda nada)
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}, {'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'pedidos_anteriores_que_no_le_llegaron': 1}, 'outbox_id': None}]

**Paso 8.** Leda (2026-11-03 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 15 · Voy bien, la tengo casi lista · vez 2

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2089 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

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
- latencia: 1633 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1644 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-28T10:45'}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-11-02) → Marcos: «Marcos: Programar PLC de la comprimidora venció el martes 27 de octubre y lleva 4 días hábiles de atraso. Hasta que la termines, Revisar comunicaciones industriales de la comprimidora no puede arrancar.

¿Cómo viene: ya la terminaste, para cuándo la tenés o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "pedidos_anteriores_que_no_le_llegaron": 1}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-11-02', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'pedidos_anteriores_que_no_le_llegaron': 1}}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'pedidos_anteriores_que_no_le_llegaron': 1}, 'outbox_id': '1fa40d4e-a6c5-49a0-8292-8f838428eac2'}]

**Paso 8.** Leda (2026-11-03 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []

## 15 · Voy bien, la tengo casi lista · vez 3

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 1847 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

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
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 15030 ms
- Leda → Marcos: «Marcos, quedó anotado que seguís con la tarea Programar PLC de la comprimidora. Está vencida: la fecha comprometida era ayer y lleva 1 día hábil de atraso. Mañana a las 10 te vuelvo a pedir el estado. ¿Para qué día la vas a tener?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [motor] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'todo en orden, sigo con eso'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '2026-10-29T10:00:00-03:00'}, 'veces_sin_algo_cierto': 1, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}]

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 16419 ms
- Leda → Marcos: «Marcos, quedó anotado que tenés previsto terminar Programar PLC de la comprimidora el martes 3 de noviembre. La fecha comprometida no cambia: era ayer, así que si se cumple esa previsión la tarea quedará con 5 días hábiles de atraso. Ismael Soschinski se entera hoy a las 10:45. El martes 3 te pido el estado. No hace falta que respondas.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Ismael, Marcos Tarquini pasó una previsión nueva para Programar PLC de la comprimidora: prevé terminarla el martes 3 de noviembre. La fecha comprometida era ayer, martes 27 de octubre, así que si se cumple esa previsión quedarán 5 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 15 · Voy bien, la tengo casi lista · vez 4

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- latencia: 2333 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

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
- latencia: 2909 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'todo en orden, sigo con eso'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1725 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-11-03'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-11-03', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-11-03', 'fecha_comprometida': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-28T10:45'}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: «Necesito saber cómo viene la Programar PLC de la comprimidora: venció el martes 27 de octubre y lleva 2 días hábiles de atraso. Además, Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés terminarla o estás trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2, "pedidos_anteriores_que_no_le_llegaron": 1}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-11-02) → Marcos: «Marcos, necesito saber cómo viene la Programar PLC de la comprimidora: venció el martes 27 de octubre y lleva 4 días hábiles de atraso. Además, Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. Si no me contestás, le aviso a Ismael Soschinski. ¿La terminaste, para cuándo prevés terminarla o estás trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}, "pedidos_anteriores_que_no_le_llegaron": 1}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-29', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'pedidos_anteriores_que_no_le_llegaron': 1}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-11-02', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}, 'pedidos_anteriores_que_no_le_llegaron': 1}}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2, 'pedidos_anteriores_que_no_le_llegaron': 1}, 'outbox_id': '9e0f2998-15d3-45ef-9110-e1129f617b36'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 4, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}, 'pedidos_anteriores_que_no_le_llegaron': 1}, 'outbox_id': 'af0318f4-7f4b-47b7-8da3-4281eebaba8e'}]

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-11-03) → Ismael: «Ismael, Marcos Tarquini no contestó los pedidos de estado por la tarea Programar PLC de la comprimidora: le llegaron dos desde el jueves 29 de octubre y uno no le llegó. La tarea está en curso, vence el martes 27 de octubre y lleva 5 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-29", "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 2, "pedidos_de_estado_que_no_le_llegaron": 1}`
- Leda, por su cuenta (aviso_previo COM, 2026-11-03) → Marcos: «Marcos, te aviso que Revisar comunicaciones industriales de la comprimidora vence el viernes 6 de noviembre: quedan 3 días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real [{'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['COM'], 'el': '2026-11-03', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-11-06', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'escalamiento', 'tareas': ['PLC'], 'el': '2026-11-03', 'hechos': {'aviso': 'falta_de_respuesta', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'responsable': 'Marcos Tarquini', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'pedido_desde': '2026-10-29', 'necesita_respuesta': False, 'atraso_dias_habiles': 5, 'pedidos_de_estado_sin_respuesta': 2, 'pedidos_de_estado_que_no_le_llegaron': 1}}
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'aviso_previo', 'tareas': ['COM'], 'el': '2026-11-03', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'COM', 'vence': '2026-11-06', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}}

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- jugadas: `[{"nombre": "informar_avance", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5500 ms
- Leda → Marcos: «Para anotar cómo viene, me falta saber de qué tarea se trata: ¿es Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, la tengo casi lista'}], real [{'nombre': 'informar_avance', 'palabras': 'voy bien, la tengo casi lista'}]
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-28'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real [{'jugada': 'informar_avance', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció ayer, martes 27 de octubre, y lleva 1 día hábil de atraso; sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.

¿Cómo viene: la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'dijo': 'presente', 'el': '2026-10-27'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 12443 ms
- Leda → Marcos: «Marcos, anoté tu avance: todo en orden y seguís con la Programar PLC de la comprimidora. La tarea venció ayer, martes 27, y lleva 1 día hábil de atraso.

¿Para qué día la vas a tener?»
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas
- **falla** [motor] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'veces_sin_algo_cierto': 2, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-29'}, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}], real [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'todo en orden, sigo con eso'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '2026-10-29T10:00:00-03:00'}, 'veces_sin_algo_cierto': 1, 'vencida': {'fecha_comprometida': '2026-10-27', 'atraso_dias_habiles': 1}, 'pregunta': 'fecha_de_la_tarea'}]

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 17318 ms
- Leda → Marcos: «Marcos, anoté tu previsión: la Programar PLC de la comprimidora la tenés para el martes 3 de noviembre. Si se cumple, quedaría 5 días hábiles atrasada respecto de la fecha comprometida, que sigue siendo el 27 de octubre.

De ésta depende Revisar comunicaciones industriales de la comprimidora. Hoy a las 10:45 le llega el aviso a Ismael Soschinski.

El martes 3 te voy a pedir el estado.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Ismael, Marcos Tarquini pasó una previsión nueva para Programar PLC de la comprimidora: prevé terminarla el martes 3 de noviembre. La fecha comprometida era ayer, martes 27 de octubre, así que si se cumple esa previsión quedarán 5 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Marcos, la Programar PLC de la comprimidora sigue en curso: venció el martes 27 de octubre, lleva 5 días hábiles de atraso y tu previsión era para hoy. Ismael Soschinski ya recibió el aviso de esa previsión. De esta tarea depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines y vence el viernes 6 de noviembre, dentro de 3 días hábiles; sobre eso no hace falta que respondas.

¿Cómo viene: la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 16 · Arranqué hoy, con la tarea vencida · vez 1

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 8213 ms
- Leda → Marcos: «Marcos, recibí que arrancaste hoy con una tarea, pero me falta saber cuál para anotar el inicio.

¿De cuál se trata: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real [{'nombre': 'anotar_inicio'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vencida': {'fecha_comprometida': '2026-10-23', 'atraso_dias_habiles': 1}, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-27'}, 'pregunta': 'fecha_de_la_tarea'}], real [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 11077 ms
- Leda → Marcos: «Marcos, recibí que para el miércoles la tenés, pero me falta saber de qué tarea se trata para anotar la previsión.

¿Cuál es: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real [{'nombre': 'anotar_prevision', 'fecha': '2026-10-28'}]
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:25'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}
- **falla** [comprension] preguntas para después: esperado [], real [{'tipo': 'cual_tarea', 'tarea': None}]
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, te escribo por Programar PLC de la comprimidora: venció el viernes 23 de octubre, lleva 1 día hábil de atraso y sigue sin arrancar. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines ésta.

Contame cómo viene: si la empezaste, para cuándo prevés terminarla y si estás trabado.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 5.** nadie (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, te escribo por Programar PLC de la comprimidora: venció el viernes 23 de octubre y hoy lleva 2 días hábiles de atraso, y sigue sin arrancar. Revisar comunicaciones industriales de la comprimidora no puede empezar hasta que termines ésta.

¿La empezaste, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-27', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': '8f3afe08-6d00-4b79-9931-4ec584579e29'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}, 'outbox_id': 'cb97cc78-ae13-4855-b605-6a348cee812f'}]

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, te escribo por Programar PLC de la comprimidora: venció el viernes 23 de octubre y hoy lleva 3 días hábiles de atraso, y sigue sin arrancar. Revisar comunicaciones industriales de la comprimidora no puede empezar hasta que termines ésta.

Si no me contestás, le aviso a Ismael Soschinski.

¿La empezaste, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}

## 16 · Arranqué hoy, con la tarea vencida · vez 2

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

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
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 1677 ms
- Leda → Marcos: «Marcos, recibí que arrancaste hoy con una tarea, pero me falta saber cuál para anotar el inicio.

¿De cuál se trata: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real [{'nombre': 'anotar_inicio'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vencida': {'fecha_comprometida': '2026-10-23', 'atraso_dias_habiles': 1}, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-27'}, 'pregunta': 'fecha_de_la_tarea'}], real [{'jugada': 'anotar_inicio', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'cual_tarea', 'tarea': None}

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 13479 ms
- Leda → Marcos: «Marcos, para anotar que la tenés para el miércoles me falta saber de qué tarea se trata.

¿De cuál es: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real [{'nombre': 'anotar_prevision', 'fecha': '2026-10-28'}]
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [comprension] botones: esperado [], real ['PLC', 'COM']
- **falla** [comprension] la pregunta de la respuesta: esperado None, real {'tipo': 'cual_tarea', 'opciones': [{'opcion': 'O1', 'etiqueta': 'PLC', 'tarea': 'PLC'}, {'opcion': 'O2', 'etiqueta': 'COM', 'tarea': 'COM'}], 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:25'}}], real [{'jugada': 'anotar_prevision', 'resultado': 'falta_dato', 'falta': ['tarea'], 'pregunta': 'cual_tarea'}]
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'cual_tarea', 'tarea': None}
- **falla** [comprension] preguntas para después: esperado [], real [{'tipo': 'cual_tarea', 'tarea': None}]
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, Programar PLC de la comprimidora venció el viernes 23 de octubre y lleva un día hábil de atraso. Además, Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que esa termine.

¿Cómo viene: la empezaste, para cuándo la tenés y si estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso: tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo se cambia la fecha
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-26', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}}

**Paso 5.** nadie (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, Programar PLC de la comprimidora venció el viernes 23 de octubre y lleva dos días hábiles de atraso. Está asignada a vos y todavía no arrancó. Además, Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que esa termine.

¿Cómo viene: la empezaste, para cuándo la tenés y si estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-27', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': 'c8e5595e-299a-4c15-90e9-e7759923e40a'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 2}, 'outbox_id': '82c5f249-b7c8-4c24-8d0c-f742f8473165'}]

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, Programar PLC de la comprimidora venció el viernes 23 de octubre y lleva 3 días hábiles de atraso. Sigue asignada a vos y todavía no arrancó, y Revisar comunicaciones industriales de la comprimidora no puede empezar hasta que esa termine. Si no contestás, se le va a avisar a Ismael Soschinski.

¿Cómo viene: la empezaste, para cuándo la tenés y si estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 3, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3, 'si_no_hay_respuesta': {'se_avisa_a': ['Ismael Soschinski']}}}

## 16 · Arranqué hoy, con la tarea vencida · vez 3

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, te escribo por la tarea Programar PLC de la comprimidora: vence hoy, viernes 23 de octubre, y está asignada a vos. La tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines ésta. ¿Cómo viene: ya la empezaste, para cuándo calculás terminarla y si está trabada?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, te escribo por la tarea Programar PLC de la comprimidora: venció el viernes 23 de octubre y lleva 1 día hábil de atraso. Está asignada a vos, y la tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines ésta.

¿Cómo viene: ya la empezaste, para cuándo calculás terminarla y si está trabada?»
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
- latencia: 20319 ms
- Leda → Marcos: «Marcos, quedó anotado que arrancaste hoy con Programar PLC de la comprimidora. Esa tarea venció el viernes 23 de octubre y lleva 1 día hábil de atraso.

¿Para qué día calculás tenerla lista?»
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
- latencia: 24828 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Programar PLC de la comprimidora el miércoles 28 de octubre. La tarea venció el viernes 23 de octubre: si se cumple esa previsión, quedaría con 3 días hábiles de atraso, y Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. A Ismael Soschinski le va a llegar el aviso hoy.

El miércoles 28 te voy a pedir el estado. No hace falta que respondas.»
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
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini dio una nueva previsión para la tarea Programar PLC de la comprimidora: la prevé terminar el miércoles 28 de octubre, pasado mañana. La fecha comprometida era el viernes 23 de octubre, así que si se cumple la previsión serían 3 días hábiles de atraso; la fecha comprometida no cambia. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, te escribo por Programar PLC de la comprimidora: prevíste terminarla hoy, miércoles 28 de octubre. La tarea venció el viernes 23 de octubre y lleva 3 días hábiles de atraso; a Ismael Soschinski ya le llegó el aviso, y Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines ésta.

¿Cómo viene: ya la terminaste, para cuándo calculás terminarla y si está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C FALLA · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, viernes 23 de octubre, y sigue asignada sin empezar. De ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines.

¿La empezaste, para cuándo prevés terminarla y si estás trabado con algo?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el viernes 23 de octubre y hoy lunes 26 lleva 1 día hábil de atraso. Sigue asignada sin empezar. De ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines.

¿La empezaste, para cuándo prevés terminarla y si estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 43946 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que arrancó
- [ ] dice: que la tarea venció el viernes 23: un día hábil de atraso
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche por el atraso o por el pedido que no contestó
- [ ] no dice: otra pregunta además de ésa
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC', 'estado': 'en_curso', 'vencida': {'fecha_comprometida': '2026-10-23', 'atraso_dias_habiles': 1}, 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-27'}, 'pregunta': 'fecha_de_la_tarea'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- latencia: 21647 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Programar PLC de la comprimidora el miércoles 28, pasado mañana. La fecha comprometida sigue siendo el viernes 23: si se cumple esa previsión, la tarea quedaría con 3 días hábiles de atraso. De ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines.

Ismael Soschinski se entera hoy de esa previsión.

El miércoles 28 te voy a pedir el estado de la tarea.»
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
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Ismael, Marcos Tarquini dio una previsión nueva para "Programar PLC de la comprimidora": la prevé terminar el miércoles 28 de octubre, pasado mañana. La fecha comprometida era el viernes 23 de octubre, así que si se cumple la previsión quedarían 3 días hábiles de atraso. De esa tarea depende "Revisar comunicaciones industriales de la comprimidora". No hace falta que respondas.»
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
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': '89218ae5-00bd-4fe4-add7-bf31c3605368'}, {'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': None, 'prevision': '2026-10-28', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-23', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'outbox_id': '3a07cf73-3971-496b-9543-a07ab822258a'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': '51e447da-d606-44ae-89d8-1a5a5691337f'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 2, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': 'ee26b5e3-56da-4fa3-b759-638f25a52081'}]

**Paso 6.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, Programar PLC de la comprimidora venció el viernes 23 de octubre y lleva 3 días hábiles de atraso. Sigue asignada sin empezar, y de ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines. Habías previsto tenerla lista hoy.

¿La empezaste, para cuándo prevés terminarla y si estás trabado con algo?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 5

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, viernes 23 de octubre, y sigue asignada sin empezar. De ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines.

¿La empezaste, para cuándo prevés terminarla y si estás trabado con algo?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el viernes 23 de octubre y lleva 1 día hábil de atraso; sigue asignada, sin empezar. De ella depende Revisar comunicaciones industriales de la comprimidora, que no puede arrancar hasta que la termines.

¿La empezaste, para cuándo prevés terminarla y si estás trabado con algo?»
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
- latencia: 14089 ms
- Leda → Marcos: «Marcos, quedó anotado que hoy empezaste Programar PLC de la comprimidora, así que la tarea queda en curso. Venció el viernes 23 de octubre y lleva 1 día hábil de atraso.

¿Para qué día la vas a tener?»
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
- latencia: 15000 ms
- Leda → Marcos: «Marcos, quedó anotado que prevés terminar Programar PLC de la comprimidora el miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23, así que si cumplís la previsión la tarea quedaría con 3 días hábiles de atraso. De ella depende Revisar comunicaciones industriales de la comprimidora.

Ismael Soschinski se entera hoy a las 10:25.

Te voy a pedir el estado el miércoles. No hace falta que respondas.»
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
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Ismael, Marcos Tarquini dio una previsión nueva para "Programar PLC de la comprimidora": la prevé terminar el miércoles 28 de octubre, pasado mañana. La fecha comprometida era el viernes 23 de octubre, así que si se cumple la previsión quedarían 3 días hábiles de atraso. De esa tarea depende "Revisar comunicaciones industriales de la comprimidora". No hace falta que respondas.»
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
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 1

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque esperás el switch.

¿Quién la puede destrabar?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 8905 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada: llegó el switch. Sigue en curso.

El viernes 23, pasado mañana, te voy a pedir el estado.»
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
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 17310 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque se quemó la fuente.

¿Quién la puede destrabar?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 17478 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada: cambiaste la fuente. Sigue en curso.

El lunes 26 te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «Marcos, el viernes 23 me dijiste que ya habías cambiado la fuente y seguías. La tarea Programar PLC de la comprimidora venció ese día y lleva 1 día hábil de atraso; sigue en curso. La tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

¿La terminaste, para cuándo la tenés o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 2

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Marcos, anoté que Programar PLC de la comprimidora está trabada porque esperás el switch. Mientras siga así no te voy a pedir el estado de la tarea.

¿Quién la puede destrabar?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 16045 ms
- Leda → Marcos: «Quedó anotado que Programar PLC de la comprimidora ya no está trabada porque esperabas el switch. La tarea sigue en curso.

El viernes 23 de octubre te voy a pedir el estado.

No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence Programar PLC de la comprimidora y sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.

¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
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
- latencia: 10555 ms
- Leda → Marcos: «Marcos, anoté que Programar PLC de la comprimidora está trabada otra vez porque se quemó la fuente. Mientras siga así no te voy a pedir el estado de la tarea.

¿Quién la puede destrabar?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 18459 ms
- Leda → Marcos: «Marcos, quedó anotado que Programar PLC de la comprimidora ya no está trabada por la fuente quemada. La tarea sigue en curso.

El lunes 26 de octubre te voy a pedir el estado.

No hace falta que respondas.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «Marcos, Programar PLC de la comprimidora sigue en curso y venció el viernes 23 de octubre: lleva 1 día hábil de atraso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.

El viernes me contaste que cambiaste la fuente y seguías.

¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 3

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre. Quedan 3 días hábiles. No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque esperás el switch. Mientras siga así no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.

¿Quién puede destrabarla?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 7899 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada: llegó el switch. Sigue en curso.

El viernes 23 te pido el estado.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence la tarea Programar PLC de la comprimidora. La tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

¿La terminaste, para cuándo la tenés o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "causa": "se quemo la fuente", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 10548 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque se quemó la fuente. Mientras siga así no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.

¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 17293 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada: cambiaste la fuente. Sigue en curso.

El lunes 26 de octubre te pido el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el viernes 23 de octubre: lleva 1 día hábil de atraso y sigue en curso. La tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

El viernes me contaste que cambiaste la fuente y seguías. ¿La terminaste, para cuándo la tenés o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 4

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre. Quedan 3 días hábiles. No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque esperás el switch. ¿Quién la puede destrabar?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 14500 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada por la espera del switch. Sigue en curso. Te voy a pedir el estado el viernes 23, pasado mañana.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence la tarea Programar PLC de la comprimidora y sigue en curso. La tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
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
- latencia: 10285 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque se quemó la fuente. Mientras siga trabada no te voy a pedir el estado. ¿Quién la puede destrabar?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 14037 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada por la fuente quemada. Sigue en curso. Te voy a pedir el estado el lunes 26 de octubre.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el viernes 23 y sigue en curso, con 1 día hábil de atraso. El viernes contaste que ya habías cambiado la fuente y seguías. La tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines ésta. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 5

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre. Quedan 3 días hábiles. No hace falta que respondas.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque esperás el switch. Mientras siga así no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.

¿Quién puede destrabarla?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 2227 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada: llegó el switch. Sigue en curso.

El viernes 23 te pido el estado.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, hoy vence la tarea Programar PLC de la comprimidora. La tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

¿La terminaste, para cuándo la tenés o estás trabado?»
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
- latencia: 9857 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora está trabada porque se quemó la fuente. Mientras siga así no te voy a pedir el estado; retomo el seguimiento cuando me cuentes que se destrabó.

¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 13050 ms
- Leda → Marcos: «Marcos, quedó anotado que la tarea Programar PLC de la comprimidora ya no está trabada: cambiaste la fuente. Sigue en curso.

El lunes 26 te pido el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora venció el viernes 23 de octubre y lleva 1 día hábil de atraso. Sigue en curso, y la tarea Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

Me contaste que cambiaste la fuente y seguías. ¿La terminaste, para cuándo la tenés o estás trabado?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 1

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre. Quedan 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, te escribo por la tarea Programar PLC de la comprimidora: vence hoy, viernes 23 de octubre, y sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine.

¿La terminaste, prevés terminarla para alguna fecha o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 10262 ms
- Leda → Marcos: «Marcos, quedó anotado lo que me contás: la tarea Programar PLC de la comprimidora viene bien y está casi lista.

Te vuelvo a preguntar por el estado el lunes 26 de octubre.»
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
- latencia: 17725 ms
- Leda → Marcos: «Marcos, quedó anotado: la tarea Programar PLC de la comprimidora la prevés terminar el miércoles 28 de octubre. Vencía el viernes 23, así que quedaría con 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine. Ismael Soschinski se entera hoy.

Te pido el estado el miércoles 28 de octubre. No hace falta que respondas.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini dio una previsión nueva para Programar PLC de la comprimidora: la terminaría el miércoles 28 de octubre, pasado mañana. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si se cumple esa previsión la tarea quedaría con 3 días hábiles de atraso. De ella depende Revisar comunicaciones industriales de la comprimidora.

No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, te escribo por la tarea Programar PLC de la comprimidora: vencía el viernes 23 de octubre, lleva 3 días hábiles de atraso y sigue en curso. La previsión era para hoy, miércoles 28 de octubre. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que ésta termine. Ismael Soschinski ya se enteró de la previsión.

¿La terminaste, prevés terminarla para alguna fecha o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 2

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre. Quedan 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, viernes 23 de octubre, y sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que esa tarea termine. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 11356 ms
- Leda → Marcos: «Marcos, anoté que vas bien y que casi tenés lista la tarea Programar PLC de la comprimidora. Te escribo el lunes 26 para saber cómo viene.»
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
- latencia: 17997 ms
- Leda → Marcos: «Marcos, anoté que prevés terminar Programar PLC de la comprimidora el miércoles 28. Si se cumple, quedarían 3 días hábiles de atraso sobre el viernes 23. Ismael Soschinski se entera hoy a las 10. Revisar comunicaciones industriales de la comprimidora sigue esperando esa tarea. No hace falta que respondas; te escribo el miércoles para saber cómo viene.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini dio una previsión nueva para Programar PLC de la comprimidora: la terminaría el miércoles 28 de octubre, pasado mañana. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si se cumple esa previsión la tarea quedaría con 3 días hábiles de atraso. De ella depende Revisar comunicaciones industriales de la comprimidora.

No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es el día en que habías previsto terminar Programar PLC de la comprimidora, y la tarea sigue en curso, con 3 días hábiles de atraso sobre el viernes 23. Revisar comunicaciones industriales de la comprimidora sigue esperando que esa tarea termine. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 3

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence este viernes 23 de octubre: quedan 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, viernes 23 de octubre, y está en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.

¿Cómo viene: ya la terminaste, para cuándo la tenés prevista o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 11715 ms
- Leda → Marcos: «Marcos, anoté lo que me contaste sobre Programar PLC de la comprimidora: vas bien, casi la tenés.

El lunes 26 de octubre te vuelvo a preguntar cómo viene.»
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
- latencia: 50818 ms
- Leda → Marcos: «Marcos, anoté que tenés prevista Programar PLC de la comprimidora para el miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23, así que si se cumple esa previsión la tarea quedaría 3 días hábiles atrasada. Hoy le llega el aviso a Ismael Soschinski.

El miércoles 28 de octubre te vuelvo a pedir cómo viene.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini dio una previsión nueva para la tarea Programar PLC de la comprimidora: la terminaría pasado mañana, miércoles 28. La fecha comprometida era el viernes 23, así que, si se cumple, quedaría con 3 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora, que sigue abierta.

No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es el día en que tenías previsto terminar Programar PLC de la comprimidora. La fecha comprometida fue el viernes 23, así que la tarea lleva 3 días hábiles de atraso y sigue en curso.

¿Cómo viene: ya la terminaste, para cuándo la tenés prevista o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 4

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre: quedan 3 días hábiles.

No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, viernes 23 de octubre, y la tenés en curso. Mientras no la termines, Revisar comunicaciones industriales de la comprimidora no puede arrancar. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 15011 ms
- Leda → Marcos: «Marcos, quedó anotado que vas bien y que casi la tenés.

El lunes 26 te vuelvo a preguntar cómo viene Programar PLC de la comprimidora.»
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
- latencia: 17611 ms
- Leda → Marcos: «Marcos, quedó anotado que tenés Programar PLC de la comprimidora para el miércoles 28. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si cumplís esa previsión la tarea quedaría 3 días hábiles atrasada.

Mientras no la termines, Revisar comunicaciones industriales de la comprimidora no puede arrancar. Ismael Soschinski se entera hoy.

El miércoles 28 te voy a pedir el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini dio una previsión nueva para Programar PLC de la comprimidora: la terminaría el miércoles 28 de octubre, pasado mañana. La fecha comprometida sigue siendo el viernes 23 de octubre, así que si se cumple esa previsión la tarea quedaría con 3 días hábiles de atraso. De ella depende Revisar comunicaciones industriales de la comprimidora.

No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, la previsión que anotaste para Programar PLC de la comprimidora era para hoy, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23 de octubre, así que la tarea lleva 3 días hábiles de atraso. Mientras no la termines, Revisar comunicaciones industriales de la comprimidora no puede arrancar. Ismael Soschinski ya se enteró.

¿La terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 5

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `nan/deepseek-v4-flash`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre. Quedan 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence hoy, viernes 23 de octubre, y sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que esa tarea termine. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 1818 ms
- Leda → Marcos: «Marcos, anoté que vas bien y que casi tenés lista la tarea Programar PLC de la comprimidora. Te escribo el lunes 26 para saber cómo viene.»
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
- latencia: 1627 ms
- Leda → Marcos: «Marcos, anoté que prevés terminar Programar PLC de la comprimidora el miércoles 28. Si se cumple, quedarían 3 días hábiles de atraso sobre el viernes 23. Ismael Soschinski se entera hoy a las 10. Revisar comunicaciones industriales de la comprimidora sigue esperando esa tarea. No hace falta que respondas; te escribo el miércoles para saber cómo viene.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Ismael, Marcos Tarquini dio una previsión nueva para "Programar PLC de la comprimidora": la prevé terminar el miércoles 28 de octubre, pasado mañana. La fecha comprometida era el viernes 23 de octubre, así que si se cumple la previsión quedarían 3 días hábiles de atraso. De esa tarea depende "Revisar comunicaciones industriales de la comprimidora". No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, la tarea Programar PLC de la comprimidora vence el viernes 23 de octubre y lleva 3 días hábiles de atraso. La previsión es para hoy, miércoles 28, e Ismael Soschinski ya está al tanto. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esa tarea.

¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

