# Transcripciones de la ronda margen-regresion-sol-suscripcion

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
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
- latencia: 3882 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy a la mañana y ya estás trabajando en eso.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿La terminaste, para cuándo calculás terminarla o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 2

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, dentro de 3 días hábiles.
  >
  > No hace falta responder.
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
- latencia: 4458 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy a la mañana.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿La terminaste, para cuándo calculás terminarla o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 3

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
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
- latencia: 5454 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que arrancaste hoy a la mañana y ya estás con eso.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: la terminaste, para cuándo calculás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 4

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
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
- latencia: 5635 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que contaste que arrancaste hoy a la mañana y ya estás con eso.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy y sigue en curso.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
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
- latencia: 5079 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy a la mañana y que ya estás trabajando en eso.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿La terminaste, para cuándo calculás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 02 · Llego el 27, el proveedor se demoró · vez 1

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 10791 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegarías al mar 27/10 porque el proveedor se demoró. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:50 de la fecha que diste y el motivo.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:51)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró. Sigue venciendo el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.
  >
  > No hace falta que respondas.
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
- **falla** [formato] formato del mensaje a Ismael: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.'

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Dijiste que la terminarías el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta.
  >
  > Ismael ya fue notificado de la fecha que diste y el motivo. Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta.'

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías hoy porque el proveedor se demoró. Lleva 2 días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste y el motivo.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10.  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Cómo viene la programación: la terminaste, para cuándo la terminás o estás trabado?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías ayer. Lleva 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías el mar 27/10. Lleva 4 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió a las tres consultas sobre cómo viene desde el mar 27/10. Ese era el día que había dado para terminarla por la demora del proveedor.  
  > ⚠️ Lleva 5 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termine.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ Todavía no puede arrancar: la programación del PLC sigue en curso.
  >
  > ¿Para cuándo podrías terminar la revisión o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [formato] formato del mensaje a Ismael: esperado 'ningún renglón de más de 140 caracteres', real 'Marcos no respondió a las tres consultas sobre cómo viene desde el mar 27/10. Ese era el día que había dado para terminarla por la demora del proveedor.'

## 02 · Llego el 27, el proveedor se demoró · vez 2

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 10003 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Vence el vie 23/10. Si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:50 de la fecha que estimás y el motivo.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Vence el vie 23/10. Si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 15:51)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará mar 27/10 porque el proveedor se demoró. Vence vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Estimás terminarla el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Ismael ya fue notificado de la fecha que estimás y el motivo. Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.'

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Estimabas terminarla hoy porque el proveedor se demoró.  
  > ⚠️ Lleva 2 días hábiles de atraso. Ismael ya fue notificado de la fecha que estimaste y el motivo.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10.  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás o qué te está trabando?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Estimabas terminarla ayer porque el proveedor se demoró.  
  > ⚠️ Lleva 3 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.
  >
  > Ismael ya fue notificado de la fecha que estimaste y el motivo.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás o qué te está trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Estimabas terminarla el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Lleva 4 días hábiles de atraso. La revisión de comunicaciones no puede arrancar hasta que termines la programación.
  >
  > Ismael ya fue notificado de la fecha que estimaste y el motivo. Si no respondés, será notificado de que todavía no sabemos cómo viene.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás o qué te está trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC, que sigue en curso.
  >
  > ¿Para cuándo estimás terminar la revisión o hay algo más que te esté trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió a las tres consultas sobre cómo viene desde mar 27/10, el día que había dicho que la terminaría.  
  > ⚠️ Venció vie 23/10 y lleva 5 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 3

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 8230 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Vence el vie 23/10: si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.
  >
  > Ismael será notificado hoy a las 15:50 de la fecha que estimaste.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Vence el vie 23/10: si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.'
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Vence el vie 23/10: si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.'

**Paso 3.** Leda (2026-10-20 15:51)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Esta tarea depende de la programación del PLC.
  >
  > No hace falta que respondas.
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Tenés previsto terminarla el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > Ismael ya fue notificado de la fecha que estimaste. Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (ya le llegó el aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.'

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías estimado terminarla hoy porque el proveedor se demoró. Ismael ya fue notificado de esa fecha.  
  > ⚠️ Lleva 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10, en 3 días hábiles.  
  > ⚠️ No puede arrancar hasta que termines el PLC.
  >
  > ¿Cómo viene el PLC: lo terminaste, para cuándo lo terminás o estás trabado?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías estimado terminarla ayer porque el proveedor se demoró. Ismael ya fue notificado de esa fecha.  
  > ⚠️ Lleva 3 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines el PLC.
  >
  > ¿Cómo viene el PLC: lo terminaste, para cuándo lo terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías estimado terminarla el mar 27/10 porque el proveedor se demoró. Ismael ya fue notificado de esa fecha.  
  > ⚠️ Lleva 4 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines el PLC.
  >
  > Si no respondés, Ismael será notificado de que seguimos sin saber cómo viene.
  >
  > ¿Terminaste el PLC, para cuándo lo terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ Todavía no puede arrancar: depende de que termines el PLC.
  >
  > ¿Para cuándo estimás terminar la revisión o hay algo más que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminaría el mar 27/10 porque el proveedor se demoró. Sigue en curso y no respondió a las tres consultas desde ese día.  
  > ⚠️ Lleva 5 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 11304 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la terminarías el mar 27/10 porque el proveedor se demoró. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:50 de la fecha que diste y el motivo.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:51)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la va a terminar el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Esta tarea depende de la programación del PLC.
  >
  > No hace falta que respondas.
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. La fecha que diste para terminarla sigue siendo el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.  
  > Ismael ya fue notificado de la fecha y el motivo.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que la terminarías hoy porque el proveedor se demoró. Lleva 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.  
  > Ismael ya fue notificado de la fecha que diste y el motivo.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence el vie 30/10.
  >
  > ¿Terminaste la programación? Si no, contame para cuándo la terminás o si estás trabado.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Terminaste la programación? Si no, contame para cuándo la terminás o si estás trabado.'

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que la terminarías ayer porque el proveedor se demoró. Lleva 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación? Si no, contame para cuándo la terminás o si estás trabado.
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que la terminarías el mar 27/10. Lleva 4 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿Terminaste la programación? Si no, contame para cuándo la terminás o si estás trabado.
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió a las tres consultas sobre cómo viene desde el mar 27/10.  
  > ⚠️ La tarea lleva 5 días hábiles de atraso. El día que había dado para terminarla ya pasó.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ No podés arrancarla hasta que termine la programación del PLC.
  >
  > ¿Para cuándo podrías terminarla? Si estás trabado, contame.
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Terminaste la programación? Si no, contame para cuándo la terminás o si estás trabado.'
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Terminaste la programación? Si no, contame para cuándo la terminás o si estás trabado.'
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Para cuándo podrías terminarla? Si estás trabado, contame.'

## 02 · Llego el 27, el proveedor se demoró · vez 5

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 12064 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la terminarías el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:50.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:51)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró. Sigue venciendo el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Esta tarea depende de la programación del PLC.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ✏️ Quedó anotado que la terminarías el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.  
  > Ismael ya fue notificado.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Habías dicho que la terminabas hoy porque el proveedor se demoró.  
  > ⚠️ Venció el vie 23/10 y lleva 2 días hábiles de atraso.  
  > Ismael ya fue notificado.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence el vie 30/10, en 3 días hábiles.  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás y si está trabada?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la terminarías ayer porque el proveedor se demoró.  
  > ⚠️ Venció el vie 23/10 y lleva 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.  
  > Ismael ya fue notificado.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás y si está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Habías dicho que la terminarías el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Venció el vie 23/10 y lleva 4 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.
  >
  > Ismael ya fue notificado del día que habías dado. Si no respondés, será notificado de que seguimos sin saber cómo viene.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás y si está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió a las tres consultas sobre cómo viene la tarea desde el mar 27/10, el día que había dicho que la terminaría porque el proveedor se demoró.  
  > ⚠️ Sigue en curso y lleva 5 días hábiles de atraso desde su vencimiento, el vie 23/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Para cuándo calculás terminar la revisión y hay algo más que te impida avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [formato] formato del mensaje a Ismael: esperado 'ningún renglón de más de 140 caracteres', real 'Marcos no respondió a las tres consultas sobre cómo viene la tarea desde el mar 27/10, el día que había dicho que la terminaría porque el proveedor se demoró.'

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5789 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque falta el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Sigue trabada porque falta el repuesto.
  >
  > ¿Quién puede destrabarla?
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 7644 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > Podemos pedirle ayuda a alguien del equipo o anotar para cuándo pensás terminarla y por qué.
  >
  > ¿Cuál preferís?
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
- latencia: 7254 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > La pregunta sobre pedir ayuda o ponerle una fecha quedó sin efecto. No se anotó nada nuevo.
  >
  > Avisame cuando llegue el repuesto y se destrabe la tarea para retomar el seguimiento.
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 2

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 6002 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque falta el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. El seguimiento se retoma cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Sigue trabada porque falta el repuesto.
  >
  > ¿Quién puede destrabarla?
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 6931 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado.
  >
  > Podemos pedirle ayuda a alguien del equipo, o podés contarme para cuándo pensás terminarla y por qué.
  >
  > ¿Cuál de esas opciones preferís?
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
- latencia: 5642 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entendido, hay que esperar a que llegue el repuesto. La propuesta quedó sin efecto y no se anotó nada nuevo.
  >
  > Cuando se destrabe, contame y retomamos el seguimiento.
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 3

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5832 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que estás trabado porque falta el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Sigue trabada porque falta el repuesto.
  >
  > ¿Quién puede destrabarla?
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 6504 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que no sabés quién puede destrabar lo del repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado.
  >
  > Podemos pedir ayuda a alguien del equipo o anotar para cuándo la vas a terminar y por qué.
  >
  > ¿Cuál preferís?
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
- latencia: 6903 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo, hay que esperar el repuesto. No quedó anotada ninguna de las dos opciones; la tarea sigue trabada.
  >
  > Cuando llegue, contame si se destrabó.
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 4

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, dentro de 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4631 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque falta el repuesto.  
  > ⚠️ No te voy a pedir el estado mientras siga trabada. El seguimiento se retoma cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Sigue trabada porque falta el repuesto.
  >
  > ¿Quién puede destrabarla?
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 6707 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado.
  >
  > Podemos pedirle ayuda a alguien del equipo o anotar para cuándo pensás terminarla y por qué.
  >
  > ¿Cuál preferís?
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
- latencia: 6607 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Sigue trabada porque falta el repuesto. Dejamos de lado las opciones que te propuse; no quedó anotado nada nuevo.
  >
  > Cuando se destrabe, avisame.
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10, dentro de 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 03 · Estoy trabado, falta el repuesto · vez 5

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5275 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque falta el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguir el repuesto para destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: cuándo llega el repuesto
- [ ] no dice: que Leda le va a escribir a alguien o lo va a seguir
- [ ] no dice: que Ismael se enteró o se va a enterar

**Paso 3.** nadie (2026-10-20 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-21 10:00)
- Leda, por su cuenta (repregunta PLC, 2026-10-21) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Sigue trabada porque falta el repuesto.
  >
  > ¿Quién puede conseguirlo para destrabarla?
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "vence": "2026-10-23", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
- [ ] dice: el bloqueo de la tarea del PLC por el repuesto
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche porque no contestó
- [ ] no dice: otra pregunta además de ésa

**Paso 5.** Marcos (2026-10-21 10:25): «ni idea quien lo esta comprando, lo pidieron hace dos semanas»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": true}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"no_sabe": true}, "salidas": ["que_alguien_ayude", "anotar_prevision"], "pregunta": "propuesta", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["que_alguien_ayude", "anotar_prevision"], "desde_antes": false}`
- latencia: 5047 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede conseguir el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > Podemos buscar a alguien del equipo que ayude o anotar para cuándo pensás terminarla y por qué.
  >
  > ¿Cuál de las dos opciones preferís?
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
- latencia: 6484 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Queda esperar a que llegue el repuesto. No se anotó ninguna de las dos opciones.
  >
  > Cuando se destrabe, contame.
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.'

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Lleva dos días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que termines esta tarea.
  >
  > Si no respondés, Ismael será notificado de que seguimos sin saber cómo viene.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió las tres consultas sobre cómo viene la tarea desde mar 27/10.  
  > ⚠️ Venció mar 27/10 y lleva tres días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación.
  >
  > No hace falta responder.
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

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Venció el mar 27/10 y lleva 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió a las tres consultas sobre cómo viene la tarea desde mar 27/10.  
  > ⚠️ Venció mar 27/10 y lleva 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta responder.
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

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo calculás terminarla o estás trabado?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Venció ayer.  
  > ⚠️ Lleva un día hábil de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo calculás terminarla o estás trabado?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Venció el mar 27/10 y lleva dos días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿La terminaste, para cuándo calculás terminarla o estás trabado?
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
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió a los tres pedidos de novedades desde mar 27/10.  
  > ⚠️ Venció mar 27/10 y lleva 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta responder.
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

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Venció ayer y lleva 1 día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Lleva 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Si no respondés, Ismael será notificado de que no hubo respuesta.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió las tres veces que le pregunté cómo viene desde mar 27/10.  
  > ⚠️ Venció mar 27/10 y lleva 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta responder.
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

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termine esta tarea.
  >
  > ¿La terminaste o, si no, para cuándo la terminás o qué te traba?
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termine esta tarea.
  >
  > ¿La terminaste? Si no, ¿para cuándo la terminás o qué te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció ayer
- [ ] dice: que la de comunicaciones no puede arrancar hasta que la del PLC esté terminada
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a escalar
- [ ] no dice: que Marcos no contestó, salvo como hecho
- [ ] no dice: ningún reproche ni intención atribuida
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, ¿para cuándo la terminás o qué te traba?'

**Paso 6.** nadie (2026-10-28 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-29 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Lleva dos días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termine esta tarea.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿La terminaste o, si no, para cuándo la terminás o qué te traba?
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
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió las tres consultas sobre cómo viene desde mar 27/10.  
  > ⚠️ Venció mar 27/10 y lleva 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta que respondas.
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

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 8170 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás terminarla el mié 4/11 porque estás esperando el switch nuevo.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:15.
  >
  > Te pregunto cómo viene el PLC el vie 23/10 y las comunicaciones el mié 4/11.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:16)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que espera el switch nuevo y que terminará la tarea el mié 4/11.  
  > El vencimiento sigue siendo el vie 30/10.  
  > ⚠️ Si la termina el mié 4/11, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 10194 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que te trabaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás terminarla el jue 5/11, en lugar del mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la terminás el jue 5/11, tendrá 4 días hábiles de atraso.  
  > Ismael será notificado hoy a las 16:40. Te pregunto cómo viene el jue 5/11.
  >
  > ¿Qué te está trabando con el PLC?
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 6666 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque Martín de IT todavía no te habilitó el acceso a la red de planta. También quedó anotado que él puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene.
  >
  > Avisame cuando tengas acceso y seguimos con el seguimiento.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Quedó anotado que está trabada porque Martín de IT todavía no te habilitó el acceso a la red de planta. También quedó anotado que él puede destrabarla.'

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7161 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste. El vie 23/10 te voy a preguntar cómo viene.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la terminarías el mié 4/11 porque esperás el switch nuevo. Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. Ismael será notificado hoy a las 10:15.  
  > El mié 4/11 te voy a preguntar cómo viene.
  >
  > No hace falta responder.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:16)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo.  
  > El vencimiento sigue siendo el vie 30/10.  
  > ⚠️ Si la termina el mié 4/11, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7528 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Para anotar que estás trabado, me falta saber qué te frena.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la terminarías el jue 5/11, no el mié 4/11. Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 4 días hábiles de atraso. Ismael será notificado hoy a las 16:40.  
  > El jue 5/11 te voy a preguntar cómo viene.
  >
  > ¿Qué te traba con el PLC?
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 7595 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque Martín de IT todavía tiene que habilitarte el acceso a la red de planta, y que él puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a preguntar cómo viene.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Quedó anotado que estás trabado porque Martín de IT todavía tiene que habilitarte el acceso a la red de planta, y que él puede destrabarla.'

## 05 · Varias cosas en un mensaje · vez 3

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6089 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste. Te voy a preguntar cómo viene el vie 23/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la terminarías el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, serán 3 días hábiles de atraso. Ismael será notificado hoy a las 10:15.  
  > Te voy a preguntar cómo viene el mié 4/11.
  >
  > No hace falta responder.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:16)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que espera el switch nuevo y que terminaría el mié 4/11.  
  > La tarea vence el vie 30/10; esa fecha no cambió.  
  > ⚠️ Si la termina el mié 4/11, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5615 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que te trabaste, pero me falta saber qué te está frenando para dejarlo anotado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la terminarías el jue 5/11, en lugar del mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, serán 4 días hábiles de atraso. Ismael será notificado hoy a las 16:40.  
  > Te voy a preguntar cómo viene el jue 5/11.
  >
  > ¿Qué te está trabando con el PLC?
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5931 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta que Martín de IT te habilite el acceso a la red de planta y que él puede destrabarlo.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene.
  >
  > Avisame cuando tengas acceso y se destrabe.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 4

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 10566 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que arrancaste.  
  > Te pregunto cómo viene el vie 23/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que calculás terminarla el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:15.
  >
  > Te pregunto cómo vienen las comunicaciones el mié 4/11.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:16)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que espera el switch nuevo y que terminará el mié 4/11.  
  > El vencimiento sigue siendo el vie 30/10.  
  > ⚠️ Si termina ese día, la tarea tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 9886 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que te trabaste. Me falta saber qué pasó para dejarlo anotado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que calculás terminarla el jue 5/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 4 días hábiles de atraso.  
  > Ismael será notificado hoy a las 16:40.  
  > Te pregunto cómo viene el jue 5/11.
  >
  > ¿Qué te está trabando con el PLC?
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5179 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que está trabada porque te falta que Martín, de IT, te habilite el acceso a la red de planta. También anoté que él puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene.
  >
  > Avisame cuando tengas acceso y retomamos el seguimiento.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Anoté que está trabada porque te falta que Martín, de IT, te habilite el acceso a la red de planta. También anoté que él puede destrabarla.'

## 05 · Varias cosas en un mensaje · vez 5

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 10077 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste recién.  
  > El vie 23/10 te voy a preguntar cómo viene.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:15 de la fecha que diste y el motivo.
  >
  > El mié 4/11 te voy a preguntar cómo viene.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:16)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo.  
  > Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 9458 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el jue 5/11, en vez del mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la terminás el jue 5/11, tendrá 4 días hábiles de atraso.  
  > Ismael será notificado hoy a las 16:40 de la nueva fecha.  
  > El jue 5/11 te voy a preguntar cómo viene.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que estás trabado. Para anotarlo, me falta saber la causa.
  >
  > ¿Qué te está trabando con el PLC?
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 6998 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque Martín de IT tiene que habilitarte el acceso a la red de planta. También quedó anotado que él puede destrabarlo.  
  > Mientras siga trabada, no te voy a pedir cómo viene.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Quedó anotado que estás trabado porque Martín de IT tiene que habilitarte el acceso a la red de planta. También quedó anotado que él puede destrabarlo.'

## 06 · No, era la otra tarea · vez 1

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4320 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta mañana. La tarea está en curso.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 6743 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo que había anotado: todavía no la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta tarea.
  >
  > Cuando arranques la del PLC, avisame.
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. La última vez me dijiste que todavía no la habías empezado.
  >
  > ¿La empezaste desde entonces, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5566 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta mañana. La tarea está en curso.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 8303 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo que había anotado: todavía no la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta mañana.
  >
  > Cuando arranques la del PLC, avisame.
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. La última vez me dijiste que todavía no la habías empezado.
  >
  > ¿Cómo viene: la empezaste, para cuándo calculás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 3

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4046 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta mañana.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 7728 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó corregido: todavía no la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta mañana.
  >
  > Cuando arranques la del PLC, avisame.
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. La última vez me dijiste que todavía no la habías empezado.
  >
  > ¿La empezaste, para cuándo calculás terminarla y hay algo que te esté trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 4

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4367 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta mañana.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 6900 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste con esta tarea.
  >
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo anterior: todavía no la empezaste.
  >
  > Por ahora no tenés que hacer nada más.
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo estimás terminarla y hay algo que te esté trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5816 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy a la mañana.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 6217 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó corregido: todavía no la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy a la mañana.
  >
  > Cuando arranques la del PLC, avisame.
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: ya la empezaste, para cuándo calculás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 07 · Dejá, no importa · vez 1

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4655 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado. Me falta saber la causa.
  >
  > ¿Qué te está frenando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5562 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dejamos ahí la pregunta sobre qué te frena. No quedó nada anotado.
  >
  > Si querés retomarlo, contame qué te está frenando.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿La terminaste, para cuándo la terminás o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 6542 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me falta el motivo para anotar que estás trabado.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 3261 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dejamos sin efecto la pregunta sobre qué te traba. No quedó nada anotado.
  >
  > Si querés retomarlo, contame qué te está trabando.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy y sigue en curso.
  >
  > ¿La terminaste, para cuándo calculás terminarla o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 3

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4487 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado. Me falta saber la causa para poder anotarlo.
  >
  > ¿Qué te está frenando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4922 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dejamos sin efecto la pregunta sobre qué te frena. No quedó nada anotado.
  >
  > Por ahora, no queda nada pendiente de este tema.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 3027 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás medio trabado. Me falta saber qué te está frenando.
  >
  > ¿Qué te traba para avanzar?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5194 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dejamos de lado la pregunta sobre qué te está trabando. No quedó nada anotado.
  >
  > Si querés retomarlo, contame qué te frena para avanzar.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Sigue en curso.
  >
  > ¿La terminaste, para cuándo calculás terminarla o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 5

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 2851 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ¿Qué te está trabando para avanzar?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Qué te está trabando para avanzar?'

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5589 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Quedó sin efecto la pregunta sobre qué te estaba trabando. No se anotó nada.
  >
  > Si querés retomar el tema, contame qué te está frenando.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy y sigue en curso.
  >
  > ¿La terminaste, para cuándo calculás terminarla o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 08 · Cambio de tema · vez 1

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 6820 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado. Para anotarlo, me falta saber qué te frena.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:53:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 7801 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que necesitás hasta el mié 4/11. El vencimiento sigue siendo el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:53. El mié 4/11 te preguntaré cómo viene.
  >
  > 📋 Programar PLC de la comprimidora  
  > Para anotar que estás trabado, todavía me falta saber la causa.
  >
  > ¿Qué te está trabando?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:54)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:55): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4963 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que estás trabado porque no te mandaron el programa del fabricante.  
  > Mientras siga trabada, no te voy a pedir avances; retomamos cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguirte el programa?
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 2

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4751 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado con esta tarea.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:53:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 7272 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que necesitás hasta el mié 4/11 para terminarla. El vencimiento sigue siendo el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:53. Te voy a preguntar cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me habías dicho que estás trabado con esta tarea.
  >
  > ¿Qué te está trabando?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:54)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:55): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 6353 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque no te mandaron el programa del fabricante.  
  > Mientras siga trabada, no te voy a preguntar cómo viene. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabar esto?
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 3

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 4779 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado.
  >
  > ¿Qué te está frenando para avanzar?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:53:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 9060 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la terminarías el mié 4/11. Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:53. Te preguntaré cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > ¿Qué te está frenando para avanzar?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:54)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:55): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5363 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque no te mandaron el programa del fabricante.  
  > ⚠️ Mientras siga trabada, no te preguntaré cómo viene. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede conseguirte el programa?
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 4

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 3132 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado con esta tarea. Me falta saber qué te está frenando.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:53:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 7552 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la vas a terminar el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:53. Te voy a preguntar cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber qué te está frenando con esta tarea.
  >
  > ¿Qué te está trabando?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:54)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:55): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5901 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque no te mandaron el programa del fabricante.  
  > Mientras siga trabada, no te voy a pedir cómo viene. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabar esto?
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 08 · Cambio de tema · vez 5

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5149 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado.
  >
  > ¿Qué te está frenando para avanzar?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:53:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 8765 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que calculás terminarla el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:53. Te voy a preguntar cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que estás trabado.
  >
  > ¿Qué te está frenando para avanzar?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:54)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11. Sigue venciendo el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: la tarea de comunicaciones
- [ ] dice: la previsión del miércoles 4, sin motivo porque Marcos no lo dio
- [ ] dice: la fecha comprometida, el viernes 30
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado
- [ ] no dice: nada del bloqueo de la tarea del PLC, que todavía no se anotó

**Paso 5.** Marcos (2026-10-20 10:55): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5957 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque no te mandaron el programa del fabricante.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

## 09 · Duda: ¿de qué tarea habla? · vez 1

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5277 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste hoy, necesito saber en cuál de estas tareas:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 2920 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 2

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6270 ms
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber en qué tarea arrancaste hoy:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál fue?
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3427 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy y que está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 3

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5690 ms
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber en qué tarea arrancaste hoy:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3330 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 4

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5795 ms
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber en cuál de estas tareas arrancaste hoy:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1929 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 5

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6580 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste hoy, necesito saber cuál de estas tareas fue. Podés elegir una opción o escribirme cuál.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál arrancaste hoy?
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 1880 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 10 · Escribir en lugar de tocar un botón · vez 1

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5912 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber cuál de estas tareas es:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > Podés tocar una opción o escribirla.
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 5764 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5911 ms
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber cuál de las tareas de la comprimidora arrancaste.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3114 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste y está en curso.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6038 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber cuál de estas tareas es:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4858 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste. Está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 4

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6058 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber cuál de las dos tareas fue:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3603 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste y está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 6103 ms
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber cuál de las tareas de la comprimidora arrancaste.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4749 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber cuál de las dos tareas fue:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál arrancaste?

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 7252 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > La pregunta ya se había cerrado ayer con esta tarea.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Tocar esa opción ahora no cambió nada.
  >
  > Si también arrancaste la revisión, avisame por mensaje.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 2776 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7866 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch y pensás terminarla el mié 4/11.  
  > ⚠️ Vence el vie 30/10: si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.
  >
  > Ismael será notificado mañana a las 10:00.
  >
  > El mié 4/11 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 8709 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y pensás terminarla el vie 30/10, el día en que vence. Si la terminás ese día, no habrá atraso.
  >
  > Ismael no será notificado por la fecha anterior.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 2

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber cuál arrancaste para anotarlo:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > Podés tocar una opción o escribirla.
  >
  > ¿Cuál de las dos arrancaste?

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste; está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 5453 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Tocaste esta opción, pero la pregunta ya se había cerrado ayer con la del PLC. No cambió nada.
  >
  > El vie 30/10 te voy a preguntar cómo viene la del PLC.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4039 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste hoy; está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6711 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch y que pensás terminarla el mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.
  >
  > Ismael será notificado mañana a las 10:00.
  >
  > El mié 4/11 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 7744 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que pensás terminarla el vie 30/10, el día en que vence.
  >
  > Ismael no será notificado por la fecha anterior que habías dado.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 3

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber cuál de las dos arrancaste:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál arrancaste?

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste. Está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 7593 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Elegirla ahora no cambió nada: ayer ya habías respondido que arrancaste la del PLC.
  >
  > El vie 30/10 te voy a preguntar cómo viene la del PLC.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4310 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste hoy. Está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6537 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch y que la terminarías el mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.
  >
  > Ismael será notificado mañana a las 10:00.
  >
  > El mié 4/11 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 8617 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que la terminarías el vie 30/10, el día en que vence.
  >
  > Ismael no será notificado por la fecha anterior.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 4

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber cuál de las dos arrancaste:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 30/10.

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 5444 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > La pregunta sobre cuál arrancaste quedó respondida ayer con esta tarea.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Elegirla ahora no cambió nada.
  >
  > Si también arrancaste la de comunicaciones, avisame.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3473 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6577 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch y que pensás terminarla el mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado mañana a las 10:00.
  >
  > Te voy a preguntar cómo viene el mié 4/11.
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 6338 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que pensás terminarla el vie 30/10, el día en que vence.  
  > Ismael ya no será notificado por la fecha anterior.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 5

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Me dijiste que arrancaste una de estas dos tareas, pero no sé cuál:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 6955 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Tocar esta opción no cambió nada: ayer ya habías elegido la del PLC.
  >
  > Si también arrancaste esta tarea, decímelo.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3332 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 4474 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch. El vencimiento sigue siendo el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.
  >
  > Ismael será notificado mañana.
  >
  > El mié 4/11 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar el viernes a las 10:00
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 6538 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el vie 30/10 porque llegó el switch. Ese día también vence la tarea.
  >
  > Ismael ya no será notificado por la fecha anterior.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 12 · Algo que no está en la lista · vez 1

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6220 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat; eso lo decide Ismael. Puedo anotar para cuándo la terminarías y que estás tapado con lo de la paila.
  >
  > ¿Para cuándo calculás que la terminarías?
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
- latencia: 7346 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, aunque no tengo anotado desde cuándo. Dejé sin efecto la pregunta sobre cuándo la terminarías y no anoté nada nuevo.
  >
  > No queda nada pendiente por ahora.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 5014 ms
- Leda → Marcos:
  > No puedo recordarte el turno con el médico el viernes; por acá solo hago seguimiento de las tareas del equipo.
  >
  > Para no olvidarte, ponete un recordatorio en el celular.
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
- latencia: 6230 ms
- Leda → Marcos:
  > El administrador será notificado hoy de que pediste un recordatorio para tu turno médico. El recordatorio no quedó programado.
  >
  > Para no olvidarte, ponete una alarma en el celular.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 6514 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me decís que la terminaste. Todavía no puedo recibir la entrega por chat y no hay otra forma definida de entregarla.
  >
  > Por ahora, conservá el trabajo.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6847 ms
- Leda → Marcos:
  > Tenés estas dos tareas pendientes:
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Está asignada y todavía no figura empezada.
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Sigue figurando en curso. Me contaste que la terminaste, pero todavía no puedo recibir la entrega por chat.
  >
  > Podés contarme cómo viene la revisión de comunicaciones.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 2

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, dentro de 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 7527 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasarle la tarea a Nahuel por chat; ese cambio lo decide Ismael.
  >
  > Puedo anotar para cuándo pensás terminarla y que estás tapado con lo de la paila.
  >
  > ¿Querés que lo anote?
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
- latencia: 10147 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, aunque no tengo anotado desde cuándo. No quedó anotada una fecha para terminarla ni lo de la paila.
  >
  > Por ahora no hace falta que hagas nada más.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6513 ms
- Leda → Marcos:
  > No puedo recordarte por chat el turno con el médico del viernes.
  >
  > Para no olvidarte, poné un recordatorio en tu calendario.
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
- latencia: 8344 ms
- Leda → Marcos:
  > Todavía no. El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno médico.
  >
  > Para no olvidarte del turno, poné un recordatorio en tu calendario.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 6595 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que la terminaste, pero todavía no puedo recibir la entrega por chat y no tengo otra forma definida para hacerlo.
  >
  > Conservá el trabajo por ahora.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6735 ms
- Leda → Marcos:
  > Te figuran dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Sigue en curso: me contaste que la terminaste, pero no puedo recibir la entrega por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Todavía figura sin empezar.
  >
  > Cuando arranques la revisión, avisame.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 3

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 7405 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat. Ismael decide quién queda a cargo.
  >
  > Puedo anotar para cuándo pensás terminarla y que estás tapado con lo de la paila.
  >
  > ¿Querés que lo anote?
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
- latencia: 8000 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, aunque no tengo anotado desde cuándo. Dejé sin efecto la propuesta de anotar para cuándo la terminarías; no quedó nada anotado.
  >
  > Por ahora no queda nada pendiente.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'Ya figura en curso, aunque no tengo anotado desde cuándo. Dejé sin efecto la propuesta de anotar para cuándo la terminarías; no quedó nada anotado.'

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6510 ms
- Leda → Marcos:
  > No puedo recordarte el turno con el médico; por chat solo hago seguimiento de tareas de trabajo.
  >
  > Para no olvidarlo, agendá un recordatorio en tu calendario.
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
- latencia: 5965 ms
- Leda → Marcos:
  > El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno médico. Eso no va a recordarte el turno a vos.
  >
  > Para no olvidarlo, agendalo en tu calendario.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7377 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que la terminaste, pero todavía no puedo recibir la entrega por chat. No tengo otra forma de recibirla definida.
  >
  > Consultá con tu equipo cómo entregarla.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 7601 ms
- Leda → Marcos:
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Figura en curso, aunque me contaste que la terminaste.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Está asignada, todavía sin empezar.
  >
  > Para la del PLC, consultá con tu equipo cómo entregarla.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 4

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6826 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat; ese cambio lo decide Ismael.  
  > Puedo anotar para cuándo la terminarías y que estás tapado con lo de la paila.
  >
  > ¿Querés que lo anote?
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
- latencia: 8823 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, así que no se volvió a anotar que arrancaste.  
  > Tampoco quedó anotado para cuándo la terminarías.
  >
  > Cuando tengas novedades, contame cómo va.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6710 ms
- Leda → Marcos:
  > No puedo recordarte por acá el turno con el médico.
  >
  > Poné un recordatorio en tu celular para el viernes.
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
- latencia: 7115 ms
- Leda → Marcos:
  > El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno con el médico. El recordatorio no quedó programado.
  >
  > Poné uno en tu celular para el viernes.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno con el médico. El recordatorio no quedó programado.'

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7684 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que la terminaste. Todavía no puedo recibir la entrega por chat y no hay otra forma definida.
  >
  > Por ahora, no la des por entregada por acá.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6029 ms
- Leda → Marcos:
  > Tenés estas dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Figura en curso. Me contaste que la terminaste, pero la entrega todavía no se recibe por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Figura asignada, sin empezar.
  >
  > Si hay novedades de alguna, contame cómo va.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 5

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6066 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat. Ismael decide si cambia de responsable.
  >
  > Puedo anotar para cuándo la terminarías y que estás tapado con lo de la paila.
  >
  > ¿Querés que lo anote?
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
- latencia: 7742 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso. No quedó anotada una fecha para terminarla y no cambió nada.
  >
  > Por ahora no queda nada pendiente.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 7438 ms
- Leda → Marcos:
  > No puedo recordarte el turno médico.
  >
  > Podés poner un recordatorio en tu teléfono para que te avise.
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
- latencia: 6645 ms
- Leda → Marcos:
  > El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno médico. Eso no programa el aviso.
  >
  > Podés poner un recordatorio en tu teléfono.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7324 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que ya la terminaste, pero todavía no puedo recibir la entrega por chat. No hay otra forma definida para entregarla.
  >
  > Por ahora, conservá el trabajo hasta que se defina cómo entregarlo.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 7691 ms
- Leda → Marcos:
  > Tenés dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Figura en curso. Me contaste que la terminaste, pero la entrega todavía no se recibe por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Está asignada y todavía no figura como empezada.
  >
  > Avisame cuando arranques la revisión.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Tenés dos tareas que vencen pronto:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 23/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel:
  > 📋 Integrar datos de la comprimidora en CoreLabs  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
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
- latencia: 5420 ms
- Leda → Marcos: [botones: PLC, COM]
  > Necesito saber con cuál de las dos arrancaste:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos es?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 2822 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste con esta tarea.
  >
  > Te voy a preguntar cómo viene el vie 23/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 2

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Estas dos tareas vencen en 3 días hábiles:
  >
  > 🗓️ Programar PLC de la comprimidora — vie 23/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vie 23/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel:
  > 📋 Integrar datos de la comprimidora en CoreLabs  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
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
- latencia: 7826 ms
- Leda → Marcos: [botones: PLC, COM]
  > Necesito saber con cuál de estas dos tareas arrancaste:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos es?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6093 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel:
  > 📋 Integrar datos de la comprimidora en CoreLabs  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Estas dos tareas vencen el vie 23/10:
  >
  > 🗓️ Programar PLC de la comprimidora — vie 23/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vie 23/10
  >
  > No hace falta responder.
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
- latencia: 6335 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber a cuál te referís:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5801 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste; está en curso.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 4

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel:
  > 📋 Integrar datos de la comprimidora en CoreLabs  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Estas dos tareas vencen el vie 23/10:
  >
  > 🗓️ Programar PLC de la comprimidora — vie 23/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vie 23/10
  >
  > No hace falta responder.
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
- latencia: 6452 ms
- Leda → Marcos: [botones: PLC, COM]
  > Todavía no quedó anotado que arrancaste: necesito saber a cuál de estas tareas te referís.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5352 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Te pregunto cómo viene el vie 23/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 5

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel:
  > 📋 Integrar datos de la comprimidora en CoreLabs  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 23/10
  >
  > No hace falta responder.
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
- latencia: 6177 ms
- Leda → Marcos: [botones: PLC, COM]
  > Todavía no quedó anotado que arrancaste: necesito saber cuál de estas dos tareas es.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3664 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 1

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, dentro de tres días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4470 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4242 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 2

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5413 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que ya la arrancaste.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3948 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la empezaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 3

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5417 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 5136 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 4

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5904 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3417 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 5

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4588 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3824 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 15 · Voy bien, la tengo casi lista · vez 1

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, dentro de 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo calculás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7062 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que venís bien y la tenés casi lista.  
  > Todavía falta saber si la terminaste o cuándo calculás terminarla.
  >
  > Mañana a las 10:00 te vuelvo a preguntar cómo viene.
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
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que ayer dijiste que venías bien y la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo calculás terminarla o estás trabado?
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
- latencia: 7397 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que dijiste que todo está en orden y seguís con eso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > Mañana a las 10:00 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día calculás terminarla?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:55:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7311 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que calculás terminarla el mar 3/11. El vencimiento no cambió: fue ayer.  
  > ⚠️ Si la terminás ese día, tendrá 5 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > Ismael será notificado hoy a las 10:55.
  >
  > El mar 3/11 te voy a preguntar cómo viene.
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:56, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 3/11. Venció ayer.  
  > ⚠️ Si la termina ese día, tendrá 5 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de que se termine la programación del PLC.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Venció el mar 27/10 y lleva 5 días hábiles de atraso. Habías calculado terminarla hoy.  
  > Ismael ya fue notificado de esa fecha.  
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que la termines.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 6/11, dentro de 3 días hábiles.
  >
  > ¿Terminaste la programación, para cuándo calculás terminarla o estás trabado?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 2

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de las comunicaciones industriales no puede arrancar hasta que termines el PLC.
  >
  > ¿La terminaste o, si sigue pendiente, para cuándo calculás terminarla y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5214 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que vas bien y la tenés casi lista.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
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
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ayer me dijiste que la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que termines el PLC.
  >
  > ¿Ya la terminaste o, si sigue pendiente, para cuándo calculás terminarla y hay algo que te trabe?
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
- latencia: 6372 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que todo está en orden y seguís con eso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día calculás terminarla?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:55:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 8472 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que calculás terminarla el mar 3/11. El vencimiento sigue siendo el mar 27/10.  
  > ⚠️ Si la terminás ese día, tendrá 5 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales sigue esperando que termines el PLC.
  >
  > Ismael será notificado hoy a las 10:55 de la fecha que diste.
  >
  > El mar 3/11 te voy a preguntar cómo viene.
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:56, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 3/11. Venció ayer.  
  > ⚠️ Si la termina ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [formato] formato del mensaje a Ismael: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la termina ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la tendrías hoy.  
  > ⚠️ Venció el mar 27/10 y lleva 5 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que termines el PLC.  
  > Ismael ya fue notificado de la fecha que diste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 6/11, en 3 días hábiles.
  >
  > ¿Ya terminaste el PLC o, si sigue pendiente, para cuándo calculás terminarlo y hay algo que te trabe?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 3

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.
  >
  > ¿La terminaste, tenés fecha para terminarla o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7681 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que vas bien y la tenés casi lista. Todavía falta saber si la terminaste, tenés fecha para terminarla o hay algo que te traba.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que mañana le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada, entregada o "casi terminada" como un hecho de Leda
- [ ] no dice: una fecha que nadie dio
- [ ] no dice: que se va a avisar a Ismael o que se escala
- [ ] no dice: ninguna pregunta
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Quedó anotado que vas bien y la tenés casi lista. Todavía falta saber si la terminaste, tenés fecha para terminarla o hay algo que te traba.'

**Paso 3.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ayer contaste que ibas bien y la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.
  >
  > ¿La terminaste, tenés fecha para terminarla o hay algo que te traba?
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Venció ayer y lleva un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.'

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-29T10:00:00-03:00"}, "veces_sin_algo_cierto": 2, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 7104 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que todo está en orden y seguís con eso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día vas a tenerla?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:55:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 6807 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que vas a tenerla el mar 3/11. El vencimiento no cambió: fue ayer.  
  > ⚠️ Si la terminás ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora sigue esperando que la termines.
  >
  > Ismael será notificado hoy a las 10:55 de la fecha que diste.
  >
  > El mar 3/11 te voy a preguntar cómo viene.
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora sigue esperando que la termines.'

**Paso 7.** nadie (2026-10-28 10:56, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 3/11. Venció ayer.  
  > ⚠️ Si la termina ese día, tendrá 5 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la tendrías hoy. Venció el mar 27/10 y lleva 5 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que la termines.  
  > Ismael ya fue notificado de la fecha que diste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 6/11, en 3 días hábiles.
  >
  > ¿Terminaste la programación, tenés otra fecha para terminarla o hay algo que te traba?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 4

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5136 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que venís bien y la tenés casi lista.  
  > Todavía falta saber si la terminaste o para cuándo la terminás.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
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
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ayer me dijiste que venías bien y la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Ya la terminaste, para cuándo la terminás o estás trabado?
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
- latencia: 6763 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que todo está en orden y seguís con eso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.  
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Qué día vas a tenerla terminada?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:55:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7828 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la vas a terminar el mar 3/11.  
  > ⚠️ Venció ayer. Si la terminás ese día, tendrá 5 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:55.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > El mar 3/11 te pregunto cómo viene.
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:56, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 3/11. Venció ayer.  
  > ⚠️ Si la termina ese día, tendrá 5 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que la terminabas hoy.  
  > ⚠️ Venció el mar 27/10 y lleva 5 días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 6/11, en 3 días hábiles.  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Ya terminaste la programación, para cuándo la terminás o estás trabado?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, en tres días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo pensás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5778 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que vas bien y la tenés casi lista. Todavía queda por saber si la terminaste.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
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
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ayer me dijiste que ibas bien y la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > ¿La terminaste, para cuándo pensás terminarla o estás trabado?
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
- latencia: 4890 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que todo está en orden y seguís con eso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día pensás terminarla?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-28T10:55:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 8555 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que pensás terminarla el mar 3/11.  
  > ⚠️ Venció ayer. Si la terminás ese día, tendrá cinco días hábiles de atraso y la revisión de comunicaciones industriales seguirá esperando.  
  > Ismael será notificado hoy a las 10:55.
  >
  > El mar 3/11 te voy a preguntar cómo viene.
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:56, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 3/11. Venció ayer.  
  > ⚠️ Si la termina ese día, tendrá 5 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Hoy es el día que dijiste que la terminarías.  
  > ⚠️ Venció el mar 27/10 y lleva cinco días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 6/11, en tres días hábiles.  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación, para cuándo pensás terminarla o estás trabado?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 16 · Arranqué hoy, con la tarea vencida · vez 1

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.
  >
  > ¿La empezaste, para cuándo calculás terminarla y hay algo que te esté trabando?

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Venció el vie 23/10 y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > ¿La empezaste, para cuándo calculás terminarla y hay algo que te esté trabando?
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
- latencia: 7947 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.  
  > ⚠️ Venció el vie 23/10 y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día calculás terminarla?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:35:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7522 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que calculás terminarla pasado mañana; el vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora sigue esperando que la termines.
  >
  > Ismael será notificado hoy a las 10:35 de la fecha que diste.
  >
  > Pasado mañana te pregunto cómo viene.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora sigue esperando que la termines.'

**Paso 4.** Leda (2026-10-26 10:36)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Venció el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales depende de esta tarea.
  >
  > No hace falta que respondas.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Hoy es el día que calculaste para terminarla. Lleva 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > ¿La terminaste o, si todavía no, para cuándo calculás terminarla y hay algo que te esté trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 2

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la empezaste, para cuándo la terminás y si está trabada?

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Lleva 1 día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La empezaste, para cuándo la terminás y si está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Lleva 1 día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.'

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"llega": "2026-10-27T10:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 6668 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.  
  > ⚠️ Vencía el vie 23/10 y lleva 1 día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día pensás terminarla?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:35:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7825 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla pasado mañana.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora sigue esperando que termines esta tarea.
  >
  > Ismael será notificado hoy a las 10:35 de la fecha que diste.
  >
  > Pasado mañana te pregunto cómo viene.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora sigue esperando que termines esta tarea.'

**Paso 4.** Leda (2026-10-26 10:36)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Venció el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que la terminabas hoy. Lleva 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.
  >
  > ¿La terminaste? Si no, ¿para cuándo la terminás o está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, ¿para cuándo la terminás o está trabada?'

## 16 · Arranqué hoy, con la tarea vencida · vez 3

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Ya empezaste, para cuándo pensás terminar y hay algo que te esté trabando?

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Venció el vie 23/10 y lleva 1 día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Ya empezaste, para cuándo pensás terminar y hay algo que te esté trabando?
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
- latencia: 6441 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.  
  > ⚠️ Venció el vie 23/10 y lleva 1 día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día pensás terminarla?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:35:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 6450 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla pasado mañana. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:35.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Sigue esperando que termines la programación del PLC.
  >
  > Pasado mañana te voy a preguntar cómo viene.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:36)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Venció el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de que Marcos termine la programación.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Pensabas terminarla hoy.  
  > ⚠️ Lleva 3 días hábiles de atraso.  
  > Ismael ya fue notificado de esa fecha.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Terminaste la programación? Si no, ¿para cuándo pensás terminarla o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Terminaste la programación? Si no, ¿para cuándo pensás terminarla o hay algo que te traba?'

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Ya empezaste, para cuándo la terminás y hay algo que te trabe?

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Venció el vie 23/10 y lleva 1 día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Ya empezaste, para cuándo la terminás y hay algo que te trabe?
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
- latencia: 4920 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.  
  > ⚠️ Venció el vie 23/10 y lleva 1 día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día la vas a tener?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:35:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7927 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la vas a tener pasado mañana. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:35.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Sigue esperando que termines la programación del PLC.
  >
  > Pasado mañana te pregunto cómo viene.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:36)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Vencía vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > No hace falta que respondas.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la ibas a tener hoy. Sigue en curso y lleva 3 días hábiles de atraso.  
  > Ismael ya fue notificado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿La terminaste, para cuándo la vas a tener o hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 16 · Arranqué hoy, con la tarea vencida · vez 5

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la empezaste, para cuándo la terminás y tenés alguna traba?

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Venció el vie 23/10 y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La empezaste, para cuándo la terminás y tenés alguna traba?
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
- latencia: 6718 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.  
  > ⚠️ Venció el vie 23/10 y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día vas a tenerla terminada?
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-26T10:35:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28"}}}]`
- ya no va a pasar: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "llega": "no_le_va_a_llegar", "motivo": "ya_respondio"}]`
- latencia: 7761 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la vas a terminar pasado mañana. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá tres días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Ismael será notificado hoy a las 10:35 de la fecha que diste.
  >
  > Pasado mañana te voy a preguntar cómo viene.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:36)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Venció el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora depende de este trabajo.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminabas hoy. Lleva tres días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste.
  >
  > ¿La terminaste? Si no, ¿para cuándo la terminás o tenés alguna traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "2026-10-26", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, ¿para cuándo la terminás o tenés alguna traba?'

## 17 · Llegó el switch, sigo · vez 1

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque esperás el switch.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. El seguimiento vuelve cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6053 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y ya podés seguir. La tarea está en curso.
  >
  > Pasado mañana te voy a preguntar cómo viene.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- latencia: 5573 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque se quemó la fuente.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 4684 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que cambiaste la fuente y ya podés seguir. La tarea está en curso.
  >
  > El lun 26/10 a las 10:00 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > El vie 23/10 me contaste que cambiaste la fuente y seguías.  
  > ⚠️ Lleva un día hábil de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 2

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque esperás el switch.  
  > Mientras siga trabada, no te voy a pedir el estado. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarlo: vos, otra persona o todavía no sabés?

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 6398 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y ya podés seguir. La tarea sigue en curso.
  >
  > Pasado mañana te pregunto cómo viene.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo la terminás o está trabada?
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
- latencia: 4327 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado otra vez porque se quemó la fuente.  
  > Mientras siga trabada, no te voy a pedir el estado. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarlo: vos, otra persona o todavía no sabés?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 10658 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que cambiaste la fuente y ya podés seguir. La tarea sigue en curso.
  >
  > El lun 26/10 a las 10:00 te pregunto cómo viene.
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > El vie 23/10 me contaste que cambiaste la fuente y seguías.  
  > ⚠️ Lleva 1 día hábil de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o está trabada?
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 3

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque esperás el switch.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 5286 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que ya podés seguir. La tarea sigue en curso.
  >
  > Pasado mañana te voy a preguntar cómo viene.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación, para cuándo la terminás o estás trabado?
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
- latencia: 4299 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque se quemó la fuente.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5124 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que cambiaste la fuente y que ya podés seguir. La tarea sigue en curso.
  >
  > El lun 26/10 a las 10:00 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me contaste que cambiaste la fuente y seguís. La tarea sigue en curso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 4

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en tres días hábiles.
  >
  > No hace falta responder.

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque esperás el switch.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 8285 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que seguís con la tarea. Ya no está trabada por esa espera.
  >
  > Pasado mañana te pregunto cómo viene.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ Revisar las comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo la terminás o está trabada?
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
- latencia: 5013 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque se quemó la fuente.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6345 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que cambiaste la fuente y seguís con la tarea. Ya no está trabada por eso.
  >
  > El lun 26/10 a las 10 te pregunto cómo viene.
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > El vie 23/10 contaste que cambiaste la fuente y seguías.  
  > ⚠️ Venció el vie 23/10 y lleva un día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿La terminaste, para cuándo la terminás o está trabada?
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 17 · Llegó el switch, sigo · vez 5

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque esperás el switch.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > Podés decirme un nombre, que no sabés o que depende de vos.
  >
  > ¿Quién puede destrabarlo?

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4867 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que ya podés seguir con la tarea.
  >
  > Pasado mañana te voy a preguntar cómo viene.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.'

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5096 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque se quemó la fuente.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > Podés decirme un nombre, que no sabés o que depende de vos.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 4949 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que cambiaste la fuente y que ya podés seguir. La tarea sigue en curso.
  >
  > El lun 26/10 a las 10:00 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > El vie 23/10 contaste que cambiaste la fuente y seguías.  
  > ⚠️ Lleva un día hábil de atraso. La revisión de comunicaciones no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o está trabada?
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 1

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo la terminás o está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7140 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que vas bien y casi la tenés. Todavía falta saber si la terminaste o para cuándo la terminás.
  >
  > El lun 26/10 a las 10:00 te voy a volver a preguntar cómo viene.
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
- latencia: 7038 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la vas a terminar pasado mañana. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:00.
  >
  > Pasado mañana te voy a preguntar cómo viene.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Vencía vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso
- **falla** [formato] formato del mensaje a Ismael: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.'

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías hoy. Lleva 3 días hábiles de atraso.  
  > Ismael ya fue notificado de esa fecha.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 2

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en tres días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termine esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo calculás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7107 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que venís bien y que casi la tenés. Todavía falta saber si la terminaste o para cuándo calculás terminarla.
  >
  > Te vuelvo a preguntar el lun 26/10 a las 10.
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
- latencia: 5985 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que calculás terminarla pasado mañana. Venció el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá tres días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora espera a que termines esta tarea.
  >
  > Ismael será notificado hoy a las 10 de la fecha que calculás.
  >
  > Te voy a preguntar cómo viene pasado mañana.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá tres días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora espera a que termines esta tarea.'

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Vencía el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso
- **falla** [formato] formato del mensaje a Ismael: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías calculado terminarla hoy. Venció el vie 23/10 y lleva tres días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Ismael ya fue notificado de que calculabas terminarla hoy.
  >
  > ¿La terminaste, para cuándo calculás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 3

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.'

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7922 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que venís bien y que casi la tenés.  
  > Todavía necesito saber si la terminaste, para cuándo la terminás o si estás trabado.
  >
  > Te vuelvo a preguntar cómo viene el lun 26/10 a las 10:00.
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
- latencia: 6411 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la terminás pasado mañana.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > ⚠️ Revisar comunicaciones industriales de la comprimidora espera a que termines esta tarea.
  >
  > Ismael será notificado hoy a las 10:00.
  >
  > Te voy a preguntar cómo viene pasado mañana.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Revisar comunicaciones industriales de la comprimidora espera a que termines esta tarea.'

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Venció el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de que Marcos termine la programación.
  >
  > No hace falta que respondas.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Hoy es el día que dijiste que la terminarías. Lleva 3 días hábiles de atraso.  
  > Ismael ya fue notificado.  
  > ⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.'

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 4

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en tres días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿Ya la terminaste? Si no, decime para cuándo la terminás o si estás trabado.
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Ya la terminaste? Si no, decime para cuándo la terminás o si estás trabado.'

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6429 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que vas bien y que casi la tenés.  
  > Sigue pendiente saber si la terminaste o para cuándo la terminás.
  >
  > Te vuelvo a preguntar el lun 26/10 a las 10:00.
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
- latencia: 8087 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la terminás pasado mañana.  
  > ⚠️ Si la terminás ese día, tendrá tres días hábiles de atraso respecto del vencimiento del vie 23/10.  
  > ⚠️ La revisión de comunicaciones industriales depende de que termines esta tarea.
  >
  > Ismael será notificado hoy a las 10:00 de la fecha que diste.
  >
  > Te voy a preguntar cómo viene pasado mañana.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana. Venció el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Esta tarea depende de la programación del PLC.
  >
  > No hace falta responder.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Hoy es el día que dijiste que la terminarías. Lleva tres días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste? Si no, decime para cuándo la terminás o si estás trabado.
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, decime para cuándo la terminás o si estás trabado.'

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 5

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines el PLC.
  >
  > ¿Terminaste el PLC, para cuándo lo terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6007 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que vas bien y casi la tenés. Todavía falta saber si la terminaste o para cuándo la terminás.
  >
  > El lun 26/10 te vuelvo a preguntar cómo viene.
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
- latencia: 7223 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la terminás pasado mañana. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora sigue esperando que termines el PLC.
  >
  > Ismael será notificado hoy.
  >
  > Pasado mañana te pregunto cómo viene.
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora sigue esperando que termines el PLC.'
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora sigue esperando que termines el PLC.'

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará pasado mañana.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso respecto del vencimiento del vie 23/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > No hace falta que respondas.
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ⚠️ Lleva 3 días hábiles de atraso. Habías dicho que la terminabas hoy.  
  > Ismael ya fue notificado de esa fecha.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines el PLC.
  >
  > ¿Terminaste el PLC, para cuándo lo terminás o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 1

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 5341 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat. Ismael decide quién queda a cargo.
  >
  > Puedo anotar para cuándo pensás terminarla.
  >
  > ¿Querés que lo anote?
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 6935 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 11:15.
  >
  > El mar 27/10 te voy a preguntar cómo viene.
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 11:16)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de que Marcos termine la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6091 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mar 27/10. Es el día que me dijiste, no el vencimiento: vence el vie 23/10.
  >
  > El mar 27/10 te voy a preguntar cómo viene.
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Quedó anotado que pensás terminarla el mar 27/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso.  
  > Ismael ya fue notificado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > El mar 27/10 te voy a preguntar cómo viene.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que pensabas terminarla hoy.  
  > ⚠️ Lleva 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.  
  > Ismael ya fue notificado.
  >
  > ¿Cómo viene: la terminaste, para cuándo pensás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 2

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 5054 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat. Ismael decide si cambia el responsable.
  >
  > ¿Querés que anote para cuándo calculás terminarla y por qué?
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 8729 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que calculás terminarla el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 11:15.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 11:16)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5540 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > La previsión es el día que calculás terminarla: mar 27/10. No significa que ya esté terminada ni cambia su vencimiento, el vie 23/10.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Calculás terminarla el mar 27/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Ismael ya fue notificado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Calculabas terminarla hoy; sigue en curso.  
  > ⚠️ Lleva 2 días hábiles de atraso. Ismael ya fue notificado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación o, si no, para cuándo calculás terminarla y estás trabado con algo?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 3

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > Tené presente la fecha; no hace falta responder.

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 4850 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat; ese cambio lo decide Ismael.
  >
  > Puedo anotar para cuándo pensás terminarla y por qué.
  >
  > ¿Querés que lo anote?
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 8252 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que pensás terminarla el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.
  >
  > Ismael será notificado hoy a las 11:15 de la fecha que diste.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora.'

**Paso 3.** Leda (2026-10-20 11:16)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5074 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Es el día que dijiste que pensás terminarla: mar 27/10. No cambia el vencimiento, que es el vie 23/10.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Dijiste que pensás terminarla el mar 27/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Ismael ya fue notificado de la fecha que diste. Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.'

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que pensabas terminarla hoy; todavía no sé si la terminaste.  
  > ⚠️ Lleva 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste o, si no, para cuándo pensás terminarla y está trabada?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 4

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6353 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat. Ese cambio lo decide Ismael.
  >
  > ¿Querés que anote para cuándo pensás terminarla y por qué?
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 8407 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mar 27/10. El vencimiento sigue siendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 11:15 de la fecha que diste.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 11:16)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de que se termine la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 5001 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Es el día que dijiste que pensás terminarla: mar 27/10. No significa que ya esté terminada ni cambia el vencimiento del vie 23/10.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Dijiste que pensás terminarla el mar 27/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Ismael ya fue notificado de la fecha que diste. Te voy a preguntar cómo viene el mar 27/10.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.'

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que pensabas terminarla hoy. ¿Cómo viene?  
  > ⚠️ Lleva 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > ¿La terminaste o, si no, para cuándo la terminás y hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- **falla** [formato] formato del mensaje a Marcos: esperado 'la pregunta, una sola y en el último renglón', real 'Dijiste que pensabas terminarla hoy. ¿Cómo viene?'

## 19 · Palabras de todos los días, no los nombres del sistema · vez 5

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 5324 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasarle la tarea a Nahuel por chat. Ese cambio lo decide Ismael.
  >
  > Puedo anotar para cuándo pensás terminarla y por qué.
  >
  > ¿Querés que anote eso?
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:15:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 9100 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mar 27/10.  
  > ⚠️ Vence el vie 23/10: si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 11:15 de la fecha que diste.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Vence el vie 23/10: si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 11:16)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-27", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 6050 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Es el día que dijiste que pensás terminarla: mar 27/10. No cambia el vencimiento del vie 23/10.
  >
  > Te voy a preguntar cómo viene el mar 27/10.
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. Dijiste que pensás terminarla el mar 27/10; si es así, tendrá 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste. El mar 27/10 te voy a preguntar cómo viene.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pide_el_estado_el": {"fecha": "2026-10-27"}, "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 7.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que pensabas terminarla hoy.  
  > ⚠️ Lleva 2 días hábiles de atraso. La revisión de comunicaciones de la comprimidora no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste.
  >
  > ¿La terminaste, para cuándo pensás terminarla o hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 20 · El formato de los mensajes · vez 1

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "asignada", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "en_curso", "vence": "2026-10-30"}]}]`
- latencia: 7026 ms
- Leda → Marcos:
  > Tenés dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora  
  > Vence el vie 23/10. Todavía no la empezaste.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10. Está en curso.
  >
  > Podés empezar por la programación del PLC.
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 8196 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:25.
  >
  > Te voy a preguntar cómo viene la programación el vie 23/10 y cómo van las comunicaciones el mié 4/11.
- [ ] dice: primero, en un renglón, lo que anotó
- [ ] dice: cada tarea en su bloque, separado por un renglón en blanco: primero un renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado: arrancó la del PLC; la de comunicaciones la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: con ⚠️, la consecuencia: vence el vie 30/10, tres días hábiles de atraso
- [ ] dice: que Ismael será notificado hoy, dicho en pasiva sobre él y en futuro, como algo que todavía no pasó
- [ ] dice: el próximo paso, en pocas palabras, aparte y al final
- [ ] no dice: los dos hechos mezclados en un renglón o en un párrafo corrido
- [ ] no dice: lo anotado antes que el renglón de su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: el nombre completo de una tarea dos veces
- [ ] no dice: que Leda le avisa a Ismael ("le voy a avisar", "le avisé")
- [ ] no dice: negrita

**Paso 3.** Leda (2026-10-20 10:26)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo.  
  > Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita

## 20 · El formato de los mensajes · vez 2

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "asignada", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "en_curso", "vence": "2026-10-30"}]}]`
- latencia: 8165 ms
- Leda → Marcos:
  > Tenés dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10.  
  > Todavía no la empezaste.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10.  
  > Está en curso.
  >
  > Podés empezar la programación y seguir con la revisión.
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7306 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch nuevo y calculás terminarla el mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:25.
  >
  > Te voy a preguntar cómo viene la programación el vie 23/10 y la revisión el mié 4/11.
- [ ] dice: primero, en un renglón, lo que anotó
- [ ] dice: cada tarea en su bloque, separado por un renglón en blanco: primero un renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado: arrancó la del PLC; la de comunicaciones la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: con ⚠️, la consecuencia: vence el vie 30/10, tres días hábiles de atraso
- [ ] dice: que Ismael será notificado hoy, dicho en pasiva sobre él y en futuro, como algo que todavía no pasó
- [ ] dice: el próximo paso, en pocas palabras, aparte y al final
- [ ] no dice: los dos hechos mezclados en un renglón o en un párrafo corrido
- [ ] no dice: lo anotado antes que el renglón de su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: el nombre completo de una tarea dos veces
- [ ] no dice: que Leda le avisa a Ismael ("le voy a avisar", "le avisé")
- [ ] no dice: negrita

**Paso 3.** Leda (2026-10-20 10:26)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo.  
  > Vence el vie 30/10; si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita

## 20 · El formato de los mensajes · vez 3

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, dentro de tres días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "asignada", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "en_curso", "vence": "2026-10-30"}]}]`
- latencia: 5788 ms
- Leda → Marcos:
  > Tenés dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence el vie 23/10; todavía no empezada.  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence el vie 30/10; en curso.
  >
  > Podés empezar la programación y seguir con la revisión.
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7379 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá tres días hábiles de atraso.  
  > Ismael será notificado hoy de la fecha que diste.
  >
  > Te voy a preguntar cómo viene la programación el vie 23/10 y la revisión el mié 4/11.
- [ ] dice: primero, en un renglón, lo que anotó
- [ ] dice: cada tarea en su bloque, separado por un renglón en blanco: primero un renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado: arrancó la del PLC; la de comunicaciones la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: con ⚠️, la consecuencia: vence el vie 30/10, tres días hábiles de atraso
- [ ] dice: que Ismael será notificado hoy, dicho en pasiva sobre él y en futuro, como algo que todavía no pasó
- [ ] dice: el próximo paso, en pocas palabras, aparte y al final
- [ ] no dice: los dos hechos mezclados en un renglón o en un párrafo corrido
- [ ] no dice: lo anotado antes que el renglón de su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: el nombre completo de una tarea dos veces
- [ ] no dice: que Leda le avisa a Ismael ("le voy a avisar", "le avisé")
- [ ] no dice: negrita

**Paso 3.** Leda (2026-10-20 10:26)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo.  
  > ⚠️ Vence el vie 30/10. Si la termina el día que indicó, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita

## 20 · El formato de los mensajes · vez 4

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "asignada", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "en_curso", "vence": "2026-10-30"}]}]`
- latencia: 5191 ms
- Leda → Marcos:
  > Tenés estas tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence el vie 23/10.  
  > Todavía no la empezaste.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence el vie 30/10.  
  > Está en curso.
  >
  > Podés seguir con la revisión y empezar la programación.
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 10298 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:25.
  >
  > El vie 23/10 te voy a preguntar cómo viene el PLC y el mié 4/11, cómo viene la revisión.
- [ ] dice: primero, en un renglón, lo que anotó
- [ ] dice: cada tarea en su bloque, separado por un renglón en blanco: primero un renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado: arrancó la del PLC; la de comunicaciones la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: con ⚠️, la consecuencia: vence el vie 30/10, tres días hábiles de atraso
- [ ] dice: que Ismael será notificado hoy, dicho en pasiva sobre él y en futuro, como algo que todavía no pasó
- [ ] dice: el próximo paso, en pocas palabras, aparte y al final
- [ ] no dice: los dos hechos mezclados en un renglón o en un párrafo corrido
- [ ] no dice: lo anotado antes que el renglón de su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: el nombre completo de una tarea dos veces
- [ ] no dice: que Leda le avisa a Ismael ("le voy a avisar", "le avisé")
- [ ] no dice: negrita

**Paso 3.** Leda (2026-10-20 10:26)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita

## 20 · El formato de los mensajes · vez 5

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "asignada", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "en_curso", "vence": "2026-10-30"}]}]`
- latencia: 5986 ms
- Leda → Marcos:
  > Tenés estas tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence el vie 23/10; todavía no la empezaste.  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence el vie 30/10; está en curso.
  >
  > Podés empezar la programación y seguir con la revisión.
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6864 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch nuevo y que calculás terminarla el mié 4/11.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:25.
  >
  > Te voy a preguntar cómo viene la programación el vie 23/10 y cómo viene la revisión el mié 4/11.
- [ ] dice: primero, en un renglón, lo que anotó
- [ ] dice: cada tarea en su bloque, separado por un renglón en blanco: primero un renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado: arrancó la del PLC; la de comunicaciones la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: con ⚠️, la consecuencia: vence el vie 30/10, tres días hábiles de atraso
- [ ] dice: que Ismael será notificado hoy, dicho en pasiva sobre él y en futuro, como algo que todavía no pasó
- [ ] dice: el próximo paso, en pocas palabras, aparte y al final
- [ ] no dice: los dos hechos mezclados en un renglón o en un párrafo corrido
- [ ] no dice: lo anotado antes que el renglón de su tarea
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: el nombre completo de una tarea dos veces
- [ ] no dice: que Leda le avisa a Ismael ("le voy a avisar", "le avisé")
- [ ] no dice: negrita

**Paso 3.** Leda (2026-10-20 10:26)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo.  
  > Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch nuevo", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}`
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita

## 25 · Mensajes sin puntuación · vez 1

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > 🗓️ Programar PLC de la comprimidora — vence jue 22/10.  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence jue 22/10.
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 10532 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el vie 23/10 porque te falta el cable para programar comunicaciones.  
  > ⚠️ Vence el jue 22/10: si la terminás el vie 23/10, tendrá 1 día hábil de atraso. La revisión de comunicaciones de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:50.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'bloqueada'}, real {}
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [comprension] falta un efecto: bloqueo: esperado [{'tarea': 'PLC', 'causa': 'presente'}], real []
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:e2a2aada-c831-4ccf-9517-e3a52e89eaa8', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-23'}}}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real None
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Vence el jue 22/10: si la terminás el vie 23/10, tendrá 1 día hábil de atraso. La revisión de comunicaciones de la comprimidora depende de esta tarea.'

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}, {"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:54:00-03:00"}}}, {"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 12444 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo que había anotado: el vie 23/10 no era para el PLC. Sigue venciendo el jue 22/10.  
  > Me decís que está trabado, pero me falta saber qué lo traba para anotarlo.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el vie 23/10 porque te falta el cable para programar comunicaciones.  
  > ⚠️ Vence el jue 22/10. Si la terminás el vie 23/10, tendrá 1 día hábil de atraso.  
  > Ismael será notificado hoy a las 10:54.
  >
  > ¿Qué está trabando el PLC?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: otra vez, sola y en el último renglón, la pregunta de quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}, {'nombre': 'anotar_bloqueo', 'tarea': 'PLC'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}, {'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:f02ee97e-37f7-4ba3-b68f-25a4a61e9915', 'outbox_id': None}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC', 'desde_antes': False}
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T10:54'}}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:54:00-03:00'}}}, {'jugada': 'anotar_bloqueo', 'resultado': 'falta_dato', 'falta': ['causa'], 'tarea': 'PLC', 'pregunta': 'causa_del_bloqueo'}]
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'quien_destraba', 'tarea': 'PLC'}, real {'tipo': 'causa_del_bloqueo', 'tarea': 'PLC'}

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-19 10:55)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones.  
  > Vence el jue 22/10.  
  > ⚠️ Si la termina el día que indicó, tendrá un día hábil de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "el cable"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "el cable", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 10185 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada por el cable y que Martín de Compras puede conseguirlo.  
  > Mientras siga trabada, no te voy a pedir cómo viene. Avisame cuando se destrabe.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10. Si la terminás el lun 26/10, tendrá 2 días hábiles de atraso.  
  > Ismael será notificado hoy a las 11:10.
  >
  > El lun 26/10 te voy a preguntar cómo viene la revisión.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_quien_destraba', 'quien': 'martin de compras', 'puede_traer': ['tarea']}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-26', 'motivo': 'me falta el switch'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'el cable'}, {'nombre': 'anotar_quien_destraba', 'tarea': 'PLC', 'quien': 'martin de compras'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-26', 'motivo': 'me falta el switch tmb'}]
- **falla** [garantia] efecto de más: estado: esperado {}, real {'PLC': 'bloqueada'}
- **falla** [garantia] efecto de más: bloqueo: esperado [], real [{'tarea': 'PLC', 'causa': 'el cable', 'resuelto': False}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'salidas': 'ausente'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-26', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'motivo': 'presente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'el cable', 'preguntas_ya_cerradas': ['quien_destraba']}, {'jugada': 'anotar_quien_destraba', 'resultado': 'anotado', 'tarea': 'PLC', 'quien_destraba': {'externo': 'martin de compras'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-26', 'motivo': 'me falta el switch tmb', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T11:10:00-03:00'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-26'}}}]

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos ahora dijo que la terminará el lun 26/10 porque también le falta el switch.  
  > Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá dos días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "el cable"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 8228 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable, que ya no está trabada por eso y que seguís con el PLC.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que la terminaste. Todavía no puedo recibir la entrega por chat y no hay otra forma definida.
  >
  > Pasado mañana te voy a preguntar cómo viene el PLC.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

## 25 · Mensajes sin puntuación · vez 2

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M ok · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Tenés dos tareas que vencen en 3 días hábiles:
  >
  > 🗓️ Programar PLC de la comprimidora — jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": null, "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 12430 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10. Vence el jue 22/10.  
  > ⚠️ Si la terminás ese día, tendrá un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:50 de la fecha que estimaste. Mientras siga trabada, no te voy a pedir avances.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': None, 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': None, 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:fab4e8c8-78cc-4baf-ad89-e1c2292d20c4', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': None, 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá un día hábil de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": null, "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:54:00-03:00"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 10416 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí la fecha: el vie 23/10 no era para esta tarea. Sigue trabada porque te falta el cable.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el vie 23/10. Vence el jue 22/10.  
  > ⚠️ Si la terminás ese día, tendrá un día hábil de atraso.  
  > Ismael será notificado hoy a las 10:54 de la fecha que estimaste.
  >
  > ¿Quién puede conseguir el cable para destrabar el PLC?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: otra vez, sola y en el último renglón, la pregunta de quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T10:54'}}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': None, 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:54:00-03:00'}}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-19 10:55)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá un día hábil de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": null, "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 8629 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Martín de compras puede conseguir el cable. Mientras siga trabada, no te voy a pedir avances.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que ahora estimás terminarla el lun 26/10 porque también te falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la terminás el lunes, tendrá dos días hábiles de atraso.  
  > Ismael será notificado hoy a las 11:10 de la nueva fecha.
  >
  > Te voy a preguntar cómo viene la revisión el lun 26/10.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque le falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá dos días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 6588 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que llegó el cable y que ya podés seguir con el PLC.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Me contás que la terminaste, pero todavía no puedo recibir la entrega por chat. Por ahora no hay otra forma definida para hacerlo.
  >
  > Te voy a preguntar cómo viene el PLC pasado mañana.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

## 25 · Mensajes sin puntuación · vez 3

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F ok.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Se acercan estos vencimientos:
  >
  > 🗓️ Programar PLC de la comprimidora — jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 11899 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, tendrá un día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de la programación del PLC.
  >
  > Ismael será notificado hoy a las 10:50. Mientras siga trabada, no te voy a pedir el estado.
  >
  > ¿Quién puede conseguir el cable para destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:af0ce7ae-dedc-4a94-b721-3086268ba0cc', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:54:00-03:00"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 9289 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo del vie 23/10: esa fecha no era para el PLC. Sigue trabado y vence el jue 22/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el vie 23/10 porque te falta el cable para programar comunicaciones.  
  > ⚠️ Vence el jue 22/10: si la terminás el viernes, tendrá un día hábil de atraso.
  >
  > Ismael será notificado hoy a las 10:54 sobre la fecha que estimás para comunicaciones.
  >
  > ¿Quién puede destrabar el PLC?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: otra vez, sola y en el último renglón, la pregunta de quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}, {'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:6a4561fa-5cb3-4e83-8c03-9dc6cf7b7f18', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T10:54'}}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:54:00-03:00'}}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-19 10:55)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones.  
  > ⚠️ Vence el jue 22/10; si la termina el viernes, tendrá un día hábil de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 8352 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Martín, de compras, puede conseguir el cable. Mientras siga trabado, no te voy a pedir cómo viene.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch.  
  > ⚠️ Vence el jue 22/10: si la terminás el lunes, tendrá dos días hábiles de atraso.
  >
  > Ismael será notificado hoy a las 11:10. El lun 26/10 te preguntaré cómo vienen las comunicaciones.
  >
  > Avisame cuando se destrabe el PLC.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque también le falta el switch.  
  > ⚠️ Vence el jue 22/10; si la termina el día que dijo, tendrá dos días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 8344 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable y que ya podés seguir. El PLC está en curso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que la terminaste, pero todavía no puedo recibir la entrega por chat. No tengo otra forma definida para hacerlo.
  >
  > Pasado mañana te preguntaré cómo viene el PLC.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

## 25 · Mensajes sin puntuación · vez 4

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F ok.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Estas tareas vencen en 3 días hábiles:  
  > 🗓️ Programar PLC de la comprimidora — jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 12245 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10. Vence el jue 22/10.  
  > ⚠️ Si la terminás ese día, tendrá un día hábil de atraso. La revisión de comunicaciones depende de esta tarea.
  >
  > Ismael será notificado hoy a las 10:50 de lo que contaste. Mientras siga trabada, no te voy a pedir el estado.
  >
  > ¿Quién puede destrabarla?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:a854f687-b3a0-4f16-a9d1-44a0d2f7249b', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:54:00-03:00"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 10116 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo del vie 23/10: esa fecha no era para el PLC. Sigue trabado y vence el jue 22/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el vie 23/10 porque te falta el cable para programar comunicaciones. Vence el jue 22/10.  
  > ⚠️ Si la terminás el vie 23/10, tendrá un día hábil de atraso.
  >
  > Ismael será notificado hoy a las 10:54 de lo que contaste sobre comunicaciones.
  >
  > ¿Quién puede destrabar el PLC?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: otra vez, sola y en el último renglón, la pregunta de quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}, {'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:edaca29c-6b10-41a7-820c-cb9dbcad97a0', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T10:54'}}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:54:00-03:00'}}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-19 10:55)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones.  
  > Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá un día hábil de atraso.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 9883 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que Martín, de compras, puede conseguir el cable. Mientras siga trabado, no te voy a pedir el estado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el lun 26/10 porque también te falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la terminás el lun 26/10, tendrá dos días hábiles de atraso.  
  > Ismael será notificado hoy a las 11:10. El lun 26/10 te voy a preguntar cómo viene.
  >
  > Avisame cuando se destrabe el PLC.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos ahora dice que la terminará el lun 26/10 porque también le falta el switch.  
  > Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá dos días hábiles de atraso.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 8177 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que llegó el cable y que ya podés seguir. La tarea está en curso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Me contás que la terminaste, pero todavía no puedo recibir la entrega por chat. Por ahora no hay otra forma definida.
  >
  > Pasado mañana te voy a preguntar cómo viene el PLC.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

## 25 · Mensajes sin puntuación · vez 5

Fuente: `tests/conversaciones/25-sin-puntuacion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G FALLA · C FALLA · M FALLA · F FALLA.

**Paso 1.** Leda (2026-10-19 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-19) → Marcos:
  > Estas dos tareas vencen pronto:
  >
  > 🗓️ Programar PLC de la comprimidora — vence jue 22/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence jue 22/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-22", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- [ ] dice: las dos tareas de Marcos, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10
- [ ] dice: que no hace falta contestar, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-19 10:40): «con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el viernes 23»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones"}, {"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me falta el cable para programar comunicaciones", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:50:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 13754 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que te falta el cable para programar comunicaciones y que estimás terminarla el vie 23/10. Vence el jue 22/10.  
  > ⚠️ Si la terminás ese día, tendrá un día hábil de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Esta tarea depende de la programación del PLC.
  >
  > Ismael será notificado hoy a las 10:50 de la demora prevista. Mientras la programación siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabar la programación del PLC?
- [ ] dice: cada tarea en su bloque, primero su renglón con 📋 y su nombre solo y debajo, con ✏️, lo anotado: la del PLC está trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, un día hábil de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: una sola pregunta, sola y en el último renglón: quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una causa del bloqueo que nombre las comunicaciones
- [ ] no dice: un motivo de la fecha nueva, que Marcos no dio
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Leda le avisa a Ismael
- [ ] no dice: negrita
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'anotar_bloqueo', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones'}, {'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'PLC', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'PLC', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': ['COM'], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:83ed93e6-eb5b-4496-a7c2-ae4b79e39e5f', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}], real [{'jugada': 'anotar_bloqueo', 'resultado': 'anotado', 'tarea': 'PLC', 'causa': 'me falta el cable para programar comunicaciones', 'pregunta': 'quien_destraba'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:50:00-03:00'}, 'lo_que_sigue': {'seguimiento': 'detenido_mientras_siga_trabada'}}]
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'Ismael será notificado hoy a las 10:50 de la demora prevista. Mientras la programación siga trabada, no te voy a pedir el estado; retomaré el seguimiento cuando me cuentes que se destrabó.'

**Paso 3.** Marcos (2026-10-19 10:44): «no el 23 es comunicaciones el plc esta trabado nomas»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_prevision", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "PLC", "vuelve_a": {"fecha_comprometida": "2026-10-22"}, "prevision_corregida": "2026-10-23", "aviso_de_la_prevision_corregida": {"a": "Ismael Soschinski", "llega": "no_le_va_a_llegar"}, "aplicado": {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-23", "motivo": "me falta el cable para programar comunicaciones", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 1, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T10:54:00-03:00"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Programar PLC de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "prevision_corregida"}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- latencia: 10823 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo anotado: el vie 23/10 no era para el PLC. Sigue trabado y vence el jue 22/10.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que estimás terminarla el vie 23/10 porque te falta el cable para programar comunicaciones. Vence el jue 22/10.  
  > ⚠️ Si la terminás ese día, tendrá un día hábil de atraso.
  >
  > Ismael será notificado hoy a las 10:54 de la fecha que estimás para comunicaciones.
  >
  > ¿Quién puede destrabar la programación del PLC?
- [ ] dice: en el bloque de la de comunicaciones, con 📋 primero y ✏️ debajo: que la termina el vie 23/10
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: otra vez, sola y en el último renglón, la pregunta de quién puede destrabar la del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la fecha del viernes 23 en la tarea del PLC
- [ ] no dice: el bloqueo en la tarea de comunicaciones
- [ ] no dice: que Ismael ya se enteró de algo
- [ ] no dice: que Leda le avisa a Ismael
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-10-23'}], real [{'nombre': 'corregir', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'tarea_correcta': 'COM'}]
- **falla** [garantia] efecto de más: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'ausente'}], real [{'tarea': 'COM', 'fecha': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'es_correccion': False}, {'tarea': 'PLC', 'fecha': '2026-10-22', 'motivo': None, 'es_correccion': True}]
- **falla** [garantia] efecto de más: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'motivo': 'ausente'}}], real [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}, 'clave': 'motor:nueva_prevision:4b006a41-1e15-400f-9cfc-83fa45f701c6', 'outbox_id': None}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-19T10:54'}}], real [{'jugada': 'corregir', 'resultado': 'corregido', 'corrige': 'anotar_prevision', 'tarea': 'PLC', 'vuelve_a': {'fecha_comprometida': '2026-10-22'}, 'prevision_corregida': '2026-10-23', 'aviso_de_la_prevision_corregida': {'a': 'Ismael Soschinski', 'llega': 'no_le_va_a_llegar'}, 'aplicado': {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-10-23', 'motivo': 'me falta el cable para programar comunicaciones', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '2026-10-19T10:54:00-03:00'}}}]

**Paso 4.** nadie (2026-10-19 10:50)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-19 10:55)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el vie 23/10 porque le falta el cable para programar comunicaciones. Vence el jue 22/10.  
  > ⚠️ Si la termina el día que dijo, tendrá 1 día hábil de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el cable para programar comunicaciones", "prevision": "2026-10-23", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 1}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el vie 23/10, sin motivo
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: un día hábil
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un motivo inventado (el cable, el PLC)
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-10-23', 'fecha_comprometida': '2026-10-22', 'atraso_si_se_cumple_la_prevision_dias_habiles': 1, 'dependientes': [], 'motivo': 'ausente'}}, real [{'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tareas': ['COM'], 'el': '2026-10-19', 'hechos': {'aviso': 'nueva_prevision', 'tarea': 'COM', 'motivo': 'me falta el cable para programar comunicaciones', 'prevision': '2026-10-23', 'responsable': 'Marcos Tarquini', 'dependientes': [], 'fecha_comprometida': '2026-10-22', 'necesita_respuesta': False, 'atraso_si_se_cumple_la_prevision_dias_habiles': 1}}

**Paso 6.** Marcos (2026-10-19 11:00): «el cable lo consigue martin de compras y comunicaciones al final es el lunes 26 xq me falta el switch tmb»
- jugadas: `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de compras"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-26", "motivo": "me falta el switch tmb"}]`
- hechos: `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de compras"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-26", "motivo": "me falta el switch tmb", "fecha_comprometida": "2026-10-22", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-19T11:10:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-26"}}}]`
- latencia: 41306 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que Martín, de Compras, puede conseguir el cable. Mientras siga trabada, no te voy a pedir el estado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que ahora estimás terminarla el lun 26/10 porque también te falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la terminás ese día, tendrá dos días hábiles de atraso.
  >
  > Ismael será notificado hoy a las 11:10 de la nueva fecha prevista.
  >
  > Te voy a preguntar cómo viene comunicaciones el lun 26/10.
- [ ] dice: cada tarea en su bloque con 📋 primero: en la del PLC, con ✏️, que Martín de compras consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el switch
- [ ] dice: con ⚠️, la consecuencia de la de comunicaciones: vence el jue 22/10, dos días hábiles de atraso
- [ ] dice: que Ismael será notificado, en pasiva sobre él y en futuro
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: el switch como causa del bloqueo del PLC
- [ ] no dice: Martín en la tarea de comunicaciones
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: otra vez la pregunta de quién destraba la del PLC

**Paso 7.** Leda (2026-10-19 11:11)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-19) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el lun 26/10 porque también le falta el switch. Vence el jue 22/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "COM", "motivo": "me falta el switch tmb", "prevision": "2026-10-26", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-22", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}`
- [ ] dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el lun 26/10 porque le falta el switch
- [ ] dice: que vence el jue 22/10 y, con ⚠️, el atraso: dos días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: el cable o Martín
- [ ] no dice: que la fecha cambió

**Paso 8.** Marcos (2026-10-20 15:00): «ya llego el cable sigo con el plc y lo de comunicaciones lo termine recien al final»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}, {"nombre": "entregar", "tarea": "COM"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "me falta el cable para programar comunicaciones"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-22"}}}, {"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "COM", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7981 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que llegó el cable y que ya podés seguir con el PLC.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Entiendo que la terminaste, pero todavía no puedo recibir la entrega por chat. No tengo otra forma definida para hacerlo.
  >
  > Te voy a preguntar cómo viene el PLC pasado mañana.
- [ ] dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo: que quedó anotado que se destrabó y sigue en curso
- [ ] dice: en el bloque de la de comunicaciones: con honestidad, que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: que la tarea de comunicaciones quedó entregada, en revisión o terminada
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: que la del PLC está terminada
- [ ] no dice: otra vez la pregunta de quién lo destraba

