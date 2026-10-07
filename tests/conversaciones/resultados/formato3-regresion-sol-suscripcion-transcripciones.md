# Transcripciones de la ronda formato3-regresion-sol-suscripcion

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

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
- latencia: 5088 ms
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
  > ¿La terminaste? Si no, ¿para cuándo calculás terminarla o hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, ¿para cuándo calculás terminarla o hay algo que te trabe?'

## 01 · Arranqué · vez 2

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en tres días hábiles.
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
- latencia: 4819 ms
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
  > ¿Cómo viene: la terminaste, para cuándo calculás terminarla o estás trabado?
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
- latencia: 6261 ms
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
  > Vence hoy.
  >
  > ¿Ya la terminaste, para cuándo la terminás o estás trabado?
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
- latencia: 5528 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy a la mañana y que estás trabajando en eso.
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
  > ¿Cómo viene: la terminaste, sabés para cuándo la terminás o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

## 01 · Arranqué · vez 5

Fuente: `tests/conversaciones/01-arranque.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

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
- latencia: 7170 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy a la mañana y ya estás con eso.
  >
  > El vie 23/10 te pregunto cómo viene.
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
  > ¿La terminaste? Si no, contame para cuándo la terminás y si hay algo que te traba.
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "2026-10-20", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, contame para cuándo la terminás y si hay algo que te traba.'

## 02 · Llego el 27, el proveedor se demoró · vez 1

Fuente: `tests/conversaciones/02-nueva-prevision.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

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

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 9266 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la terminás el mar 27/10 porque el proveedor se demoró. Sigue venciendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:40 de la fecha que diste y el motivo.
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ Depende de que se termine la programación del PLC.
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
  > Vence hoy. Quedó anotado que la terminás el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.'

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que la terminabas hoy porque el proveedor se demoró.  
  > ⚠️ Lleva 2 días hábiles de atraso. La revisión de comunicaciones no puede arrancar hasta que la termines.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence el vie 30/10, dentro de 3 días hábiles.
  >
  > ¿Terminaste la programación o, si todavía no, para cuándo la terminás y hay algo que te trabe?
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
  > Habías dicho que la terminabas ayer porque el proveedor se demoró.  
  > ⚠️ Lleva 3 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste y el motivo.
  >
  > ¿Terminaste la programación o, si todavía no, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Habías dicho que la terminabas el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Lleva 4 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿Terminaste la programación o, si todavía no, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminaría el mar 27/10 porque el proveedor se demoró. Desde ese día no respondió a tres consultas sobre cómo viene.  
  > ⚠️ Sigue en curso y lleva 5 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ Todavía no puede arrancar: la programación del PLC sigue en curso.
  >
  > ¿Para cuándo calculás terminar la revisión y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 12813 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.  
  > Ismael será notificado hoy a las 15:40.
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

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
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
  > Vence hoy. Me dijiste que pensás terminarla el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.  
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.'

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que pensabas terminarla hoy porque el proveedor se demoró.  
  > ⚠️ Lleva 2 días hábiles de atraso. Ismael ya fue notificado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10.  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Terminaste la programación, para cuándo pensás terminarla o estás trabado?
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
  > Me dijiste que pensabas terminarla ayer porque el proveedor se demoró.  
  > ⚠️ Lleva 3 días hábiles de atraso. Ismael ya fue notificado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Terminaste la programación, para cuándo pensás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que pensabas terminarla el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Lleva 4 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.  
  > Ismael ya fue notificado de la fecha que me diste. Si no respondés, será notificado de que sigo sin saber cómo viene.
  >
  > ¿La terminaste, para cuándo pensás terminarla o estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > ¿Para cuándo pensás terminar la revisión o hay algo que te impide avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos había dicho que la terminaría el mar 27/10 porque el proveedor se demoró.  
  > No respondió a las tres consultas sobre cómo viene desde ese día.  
  > ⚠️ Lleva 5 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termine la programación.
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 9413 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la terminás el mar 27/10 porque el proveedor se demoró. Sigue venciendo el vie 23/10.  
  > ⚠️ Si la terminás el mar 27/10, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:40 de la fecha que diste y el motivo.
  >
  > El mar 27/10 te voy a preguntar cómo viene.
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
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
  > Vence hoy. Me dijiste que la terminás el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Ismael ya fue notificado de la fecha que diste y el motivo.
  >
  > El mar 27/10 te voy a preguntar cómo viene. No hace falta responder.
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real 'El mar 27/10 te voy a preguntar cómo viene. No hace falta responder.'

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que la terminarías hoy porque el proveedor se demoró. Venció el vie 23/10 y lleva 2 días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste y el motivo.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC. Vence el vie 30/10, en 3 días hábiles.
  >
  > ¿Cómo viene la programación del PLC: la terminaste o, si no, para cuándo la terminás y si estás trabado?
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
  > Dijiste que la terminarías ayer porque el proveedor se demoró. Venció el vie 23/10 y lleva 3 días hábiles de atraso.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Terminaste la programación? Si no, ¿para cuándo la terminás y estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías el mar 27/10 porque el proveedor se demoró. Venció el vie 23/10 y lleva 4 días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste y el motivo.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿Terminaste la programación del PLC o, si no, para cuándo la terminás y estás trabado?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ No puede arrancar hasta que termine la programación del PLC.
  >
  > ¿Para cuándo estimás terminar la revisión y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos había dicho que la terminaría el mar 27/10 porque el proveedor se demoró. Desde ese día, no respondió las tres consultas sobre cómo viene.  
  > ⚠️ Venció el vie 23/10 y lleva 5 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termine.
  >
  > No hace falta que respondas.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Terminaste la programación? Si no, ¿para cuándo la terminás y estás trabado?'
- **falla** [formato] formato del mensaje a Ismael: esperado 'ningún renglón de más de 140 caracteres', real 'Marcos había dicho que la terminaría el mar 27/10 porque el proveedor se demoró. Desde ese día, no respondió las tres consultas sobre cómo viene.'

## 02 · Llego el 27, el proveedor se demoró · vez 4

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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 11173 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la terminarías el mar 27/10 porque el proveedor se demoró. Sigue venciendo el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:40.
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró.  
  > Vence el vie 23/10.  
  > ⚠️ Si la termina el mar 27/10, tendrá 2 días hábiles de atraso.
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
  > Vence hoy. Me dijiste que la terminarías el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Ismael ya fue notificado. Te voy a preguntar cómo viene el mar 27/10.
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
  > Dijiste que la terminarías hoy porque el proveedor se demoró. Sigue en curso y lleva 2 días hábiles de atraso.  
  > Ismael ya fue notificado.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence el vie 30/10.  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación o, si no, para cuándo calculás terminarla y hay algo que te impida avanzar?
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
  > Dijiste que la terminarías ayer. Sigue en curso y lleva 3 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines la programación.
  >
  > ¿La terminaste? Si no, ¿para cuándo calculás terminarla y hay algo que te impida avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías el mar 27/10. Sigue en curso y lleva 4 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines la programación.
  >
  > Si no respondés, Ismael será notificado.
  >
  > ¿La terminaste o, si no, para cuándo calculás terminarla y hay algo que te impida avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Para cuándo calculás terminarla y hay algo más que te impida avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió las tres consultas sobre cómo viene desde el mar 27/10, el día que dijo que la terminaría.  
  > Sigue en curso. Venció el vie 23/10.  
  > ⚠️ Lleva 5 días hábiles de atraso.
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, ¿para cuándo calculás terminarla y hay algo que te impida avanzar?'

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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 8136 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la terminarías el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > Ismael será notificado hoy a las 15:40 de la fecha que diste y el motivo.
  >
  > El mar 27/10 te voy a preguntar cómo viene.
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: que la tarea está bloqueada
- **falla** [formato] formato del mensaje a Marcos: esperado 'el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.'

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 27/10 porque el proveedor se demoró. Vence el vie 23/10.  
  > ⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
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
  > Vence hoy. Dijiste que la terminarías el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste y del motivo. El mar 27/10 te voy a preguntar cómo viene.
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.'

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías hoy porque el proveedor se demoró.  
  > ⚠️ Venció el vie 23/10 y lleva 2 días hábiles de atraso. La revisión de comunicaciones no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste y del motivo.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10, dentro de 3 días hábiles.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás y hay algo que te trabe?
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
  > Dijiste que la terminarías ayer porque el proveedor se demoró.  
  > ⚠️ Lleva 3 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste y del motivo.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la terminarías el mar 27/10 porque el proveedor se demoró.  
  > ⚠️ Lleva 4 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > Ismael ya fue notificado de la fecha que diste y del motivo. Si no respondés, será notificado de que seguimos sin novedades.
  >
  > ¿Terminaste la programación o, si no, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió a las tres consultas sobre cómo viene desde el mar 27/10, el día que había dicho que la terminaría.  
  > ⚠️ Lleva 5 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que termine.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence hoy.  
  > ⚠️ Todavía no puede arrancar: la programación del PLC sigue en curso.
  >
  > ¿Para cuándo calculás terminar la revisión y hay algo más que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "espera_a": [{"tarea": "PLC", "estado": "en_curso"}], "espera_algo_cierto": ["para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

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
- latencia: 4626 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque falta el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Volveré a pedirlo cuando me cuentes que se destrabó.
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
  > ⚠️ Sigue trabada porque falta el repuesto.
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
- latencia: 6739 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado.
  >
  > Podemos buscar a alguien del equipo que te ayude con el bloqueo, o anotar para cuándo pensás terminarla y por qué.
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
- latencia: 6120 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo, hay que esperar a que llegue el repuesto. La propuesta de buscar ayuda o anotar para cuándo la terminarías quedó sin efecto; no cambió nada.
  >
  > Avisame cuando llegue el repuesto y se destrabe la tarea.
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real 'Entiendo, hay que esperar a que llegue el repuesto. La propuesta de buscar ayuda o anotar para cuándo la terminarías quedó sin efecto; no cambió nada.'

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
- latencia: 4462 ms
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
  > ⚠️ Sigue trabada porque falta el repuesto.
  >
  > ¿Quién puede conseguir el repuesto para destrabarla?
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
- latencia: 6797 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede conseguir el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > Podemos pedirle ayuda a alguien del equipo o anotar para cuándo pensás terminarla y por qué.
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
- latencia: 7124 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo, preferís esperar a que llegue el repuesto. No quedó anotada ninguna de las dos opciones y no cambió nada.
  >
  > Cuando llegue y se destrabe la tarea, contame así retomo el seguimiento.
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
- latencia: 5565 ms
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
- latencia: 7023 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > Podemos buscar a alguien del equipo que ayude con el repuesto, o anotar para cuándo pensás terminarla y por qué.
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
- latencia: 6412 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Esperamos a que llegue el repuesto. La propuesta quedó sin efecto y no cambió nada.
  >
  > Avisame cuando se destrabe.
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
  > Vence el vie 23/10, dentro de tres días hábiles.
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
- latencia: 5484 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque falta el repuesto.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomamos el seguimiento cuando me cuentes que se destrabó.
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
- latencia: 7945 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado. Retomamos cuando me cuentes que se destrabó.
  >
  > Podemos buscar a alguien del equipo que ayude, o anotar para cuándo pensás terminarla y por qué.
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
- latencia: 7574 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo, hay que esperar a que llegue el repuesto. No quedó nada nuevo anotado.
  >
  > Cuando se destrabe, avisame para retomar el seguimiento.
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 30/10, dentro de tres días hábiles.
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
- latencia: 6903 ms
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
- latencia: 5818 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que no sabés quién puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado.
  >
  > Podemos pedir que alguien del equipo ayude, o podés decirme para cuándo la terminarías y por qué.
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
- latencia: 5638 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo, hay que esperar a que llegue el repuesto. No se anotó nada nuevo.
  >
  > Cuando llegue y se destrabe la tarea, contame.
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

## 04 · No contesta · vez 1

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
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que termines esta tarea.
  >
  > ¿Cómo viene: la terminaste, sabés para cuándo la terminás o estás trabado?
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
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste, sabés para cuándo la terminás o estás trabado?
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
  > ⚠️ Venció el mar 27/10 y lleva dos días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones no puede arrancar hasta que termines esta tarea.
  >
  > Si no respondés, Ismael será notificado de que no tenemos novedades.
  >
  > ¿La terminaste, sabés para cuándo la terminás o estás trabado?
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
  > Marcos la tiene en curso, pero no respondió las tres veces que le pregunté cómo venía desde el mar 27/10.  
  > ⚠️ Venció el mar 27/10 y lleva 3 días hábiles de atraso.
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
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termine esta tarea.
  >
  > ¿La terminaste, tenés una fecha para terminarla o estás trabado?
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
  > ¿La terminaste, tenés una fecha para terminarla o estás trabado?
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
  > ⚠️ Lleva dos días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termine.  
  > Si no respondés, Ismael será notificado.
  >
  > ¿La terminaste, tenés una fecha para terminarla o estás trabado?
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
  > Sigue en curso. Marcos no respondió cómo viene desde mar 27/10, pese a tres consultas.  
  > ⚠️ Venció el mar 27/10 y lleva 3 días hábiles de atraso.
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

## 04 · No contesta · vez 3

Fuente: `tests/conversaciones/04-sin-respuesta.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el mar 27/10, dentro de 3 días hábiles.
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
  > ¿Ya la terminaste, para cuándo la terminás o estás trabado?
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
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿Ya la terminaste, para cuándo la terminás o estás trabado?
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
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > Si no respondés, Ismael será notificado de que seguimos sin saber cómo viene.
  >
  > ¿Ya la terminaste, para cuándo la terminás o estás trabado?
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
  > Marcos no respondió los tres pedidos de avance desde el mar 27/10.  
  > ⚠️ La tarea lleva 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termine.
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
- **falla** [formato] formato del mensaje a Ismael: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ La tarea lleva 3 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termine.'

## 04 · No contesta · vez 4

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
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.
  >
  > ¿La terminaste? Si no, ¿para cuándo pensás terminarla o hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, ¿para cuándo pensás terminarla o hay algo que te trabe?'

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Venció ayer y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > ¿Cómo viene: la terminaste, sabés para cuándo la terminás o hay algo que te trabe?
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
  > Lleva 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que la termines.  
  > Si no respondés, Ismael será notificado.
  >
  > ¿La terminaste? Si no, ¿para cuándo pensás terminarla o hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La terminaste? Si no, ¿para cuándo pensás terminarla o hay algo que te trabe?'

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos no respondió las tres consultas sobre cómo viene la tarea desde mar 27/10.  
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

## 04 · No contesta · vez 5

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
  > ⚠️ Lleva 2 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
  >
  > Si no respondés, Ismael será notificado de que falta saber cómo viene.
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
  > Marcos no respondió los tres pedidos sobre cómo viene la tarea desde mar 27/10.  
  > ⚠️ Sigue en curso y lleva 3 días hábiles de atraso.
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

## 05 · Varias cosas en un mensaje · vez 1

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

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

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 11017 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:05.
  >
  > Te voy a preguntar cómo viene el PLC el vie 23/10 y cómo vienen las comunicaciones el mié 4/11. No hace falta responder.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real 'Te voy a preguntar cómo viene el PLC el vie 23/10 y cómo vienen las comunicaciones el mié 4/11. No hace falta responder.'

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo. Vence el vie 30/10.  
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7436 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Para dejar anotado que estás trabado, me falta saber qué te frena.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el jue 5/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 4 días hábiles de atraso.  
  > Ismael será notificado hoy a las 16:30. Te voy a preguntar cómo viene el jue 5/11.
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
- latencia: 6407 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque Martín de IT todavía no te habilitó el acceso a la red de planta, y que él puede destrabarlo.  
  > ⚠️ Mientras siga trabada, no te voy a preguntar cómo viene.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en tres días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7733 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo. Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás el mié 4/11, tendrá tres días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:05.
  >
  > Te voy a preguntar cómo viene el PLC el vie 23/10 y cómo vienen las comunicaciones el mié 4/11.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo. Vence el vie 30/10.  
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7917 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber qué te trabó.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el jue 5/11, en vez del mié 4/11. Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás el jue 5/11, tendrá cuatro días hábiles de atraso.  
  > Ismael será notificado hoy a las 16:30. Te voy a preguntar cómo viene el jue 5/11.
  >
  > ¿Qué te trabó con el PLC?
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 5799 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque Martín de IT todavía no te habilitó el acceso a la red de planta, y que él puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir el estado.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 3

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
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7369 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso. Ismael será notificado hoy a las 10:05.
  >
  > Te voy a preguntar cómo viene el PLC el vie 23/10 y las comunicaciones el mié 4/11.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo.  
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7900 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber qué te trabó para dejarlo anotado.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el jue 5/11, en lugar del mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 4 días hábiles de atraso. Ismael será notificado hoy a las 16:30. Te voy a preguntar cómo viene el jue 5/11.
  >
  > ¿Qué te trabó con el PLC?
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Si la terminás ese día, tendrá 4 días hábiles de atraso. Ismael será notificado hoy a las 16:30. Te voy a preguntar cómo viene el jue 5/11.'

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 7258 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque Martín de IT tiene que habilitarte el acceso a la red de planta.  
  > Mientras siga trabada, no te voy a preguntar cómo viene.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 4

Fuente: `tests/conversaciones/05-varias-cosas.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence el vie 23/10, en tres días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 9662 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que calculás terminarla el mié 4/11 porque esperás el switch nuevo. Vence el vie 30/10.  
  > ⚠️ Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:05.
  >
  > Te pregunto cómo viene el PLC el vie 23/10 y cómo vienen las comunicaciones el mié 4/11.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11 porque espera el switch nuevo. Vence el vie 30/10.  
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 7114 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Para anotar que está trabada, me falta saber qué te frena.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que calculás terminarla el jue 5/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 4 días hábiles de atraso.  
  > Ismael será notificado hoy a las 16:30. Te voy a preguntar cómo vienen las comunicaciones el jue 5/11.
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
- latencia: 7880 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque falta que Martín de IT te habilite el acceso a la red de planta, y que él puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir avances.
  >
  > Avisame cuando se destrabe para retomar el seguimiento.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 05 · Varias cosas en un mensaje · vez 5

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
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7644 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste recién.  
  > El vie 23/10 te voy a preguntar cómo viene.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch nuevo.  
  > Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy. El mié 4/11 te voy a preguntar cómo viene.
  >
  > No hace falta responder.
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que espera el switch nuevo y que terminará la tarea el mié 4/11.  
  > Vence el vie 30/10.  
  > ⚠️ Si la termina ese día, tendrá 3 días hábiles de atraso.
  >
  > No hace falta que respondas.
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
- latencia: 6599 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el jue 5/11, en lugar del mié 4/11.  
  > Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás el jue 5/11, tendrá 4 días hábiles de atraso.  
  > Ismael será notificado hoy a las 16:30. El jue 5/11 te voy a preguntar cómo viene.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que te trabaste, pero me falta saber qué pasó.
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
- latencia: 7725 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que está trabada porque Martín de IT todavía no te habilitó el acceso a la red de planta.  
  > También quedó anotado que él puede destrabarla.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene.
  >
  > Avisame cuando se destrabe.
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

## 06 · No, era la otra tarea · vez 1

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
- latencia: 4805 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste esta mañana.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 7191 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó corregido: todavía no la empezaste.
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
  > Vence hoy.
  >
  > ¿Cómo viene: la empezaste, para cuándo calculás terminarla y hay algo que te traba?
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
  > Vence el vie 23/10, en tres días hábiles.
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
- latencia: 4648 ms
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
- latencia: 5436 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo que había anotado: todavía no la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta.
  >
  > No hace falta responder.
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. La última vez me dijiste que todavía no la habías empezado.
  >
  > ¿Cómo viene ahora: ya la empezaste, para cuándo calculás terminarla y hay algo que te trabe?
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
- latencia: 5748 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que arrancaste esta mañana.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 8750 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Corregí lo que había anotado: todavía no la empezaste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta mañana.
  >
  > Avisame cuando arranques el PLC.
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
  >
  > ¿Cómo viene: pudiste empezarla, para cuándo calculás terminarla y hay algo que te trabe?
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
- latencia: 3777 ms
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
- latencia: 6943 ms
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
  > Vence hoy.
  >
  > ¿Cómo viene: la empezaste, para cuándo la terminás y hay algo que te trabe?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

## 06 · No, era la otra tarea · vez 5

Fuente: `tests/conversaciones/06-correccion.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

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
- latencia: 4572 ms
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
- latencia: 9170 ms
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
  > ¿La empezaste? ¿Para cuándo calculás terminarla? ¿Hay algo que te esté trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "espera_algo_cierto": ["si_la_empezo", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿La empezaste? ¿Para cuándo calculás terminarla? ¿Hay algo que te esté trabando?'

## 07 · Dejá, no importa · vez 1

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
- latencia: 4012 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 6807 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dejamos sin efecto la pregunta. No quedó nada anotado.
  >
  > Si más adelante querés retomarlo, contame qué te está trabando.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy. ¿Cómo viene?
  >
  > ¿La terminaste, para cuándo calculás terminarla o hay algo que te está trabando?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado
- **falla** [formato] formato del mensaje a Marcos: esperado 'la pregunta, una sola y en el último renglón', real 'Vence hoy. ¿Cómo viene?'

## 07 · Dejá, no importa · vez 2

Fuente: `tests/conversaciones/07-cancelar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

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

**Paso 2.** Marcos (2026-10-20 11:30): «estoy medio trabado con esto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5533 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber qué te está trabando.
  >
  > ¿Qué te está frenando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5435 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Quedó sin efecto la pregunta sobre qué te frena. No se anotó nada.
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
  > ¿La terminaste, para cuándo calculás terminarla o hay algo que te está trabando?
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
  > Vence el vie 23/10, en tres días hábiles.
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
- latencia: 4365 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Para dejar anotado que estás trabado, me falta saber la causa.
  >
  > ¿Qué te está frenando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4998 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dejé sin efecto la pregunta sobre qué te frena. No quedó nada anotado.
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
  > ¿Ya la terminaste, para cuándo calculás terminarla o hay algo que te está trabando?
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
- latencia: 4043 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás medio trabado. Me falta saber la causa.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5263 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dejamos sin efecto la pregunta. No quedó nada anotado.
  >
  > Si más adelante querés retomarlo, contame qué te traba.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy y sigue en curso.
  >
  > ¿La terminaste, para cuándo la terminás o hay algo que te traba?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

## 07 · Dejá, no importa · vez 5

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
- latencia: 5384 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me decís que estás trabado; me falta saber qué te frena.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 4991 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > La pregunta sobre qué te traba quedó sin efecto. No se anotó nada.
  >
  > Si querés retomarlo, contame qué te está trabando.
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Vence hoy.
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
- latencia: 4873 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber el motivo para anotar que está trabada.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 8455 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que calculás terminarla el mié 4/11. Sigue venciendo el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:43. Te voy a preguntar cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber la causa para anotar que está trabada.
  >
  > ¿Qué te está trabando?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que va a terminarla el mié 4/11. Sigue venciendo el vie 30/10.  
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

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 4420 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que está trabada porque no te mandaron el programa del fabricante.  
  > Mientras siga trabada, no te voy a pedir avances. Retomo el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla?
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
- latencia: 4504 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado con esta tarea.
  >
  > ¿Qué te está frenando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 8795 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la terminarías el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:43. Te voy a preguntar cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me dijiste que estás trabado con esta tarea.
  >
  > ¿Qué te está frenando?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
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

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 6187 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque no te mandaron el programa del fabricante.  
  > Mientras siga trabada, no te voy a pedir cómo viene. Retomaré el seguimiento cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarlo?
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
- latencia: 7953 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber qué te está frenando.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 7671 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la vas a terminar el mié 4/11; vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:43. Te voy a preguntar cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber qué te está frenando.
  >
  > ¿Qué te está trabando con el PLC?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Marcos dijo que la terminará el mié 4/11. Sigue venciendo el vie 30/10.  
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

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 9176 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que estás trabado porque no te mandaron el programa del fabricante.  
  > Mientras siga trabada, no te voy a pedir avances. Retomamos cuando me cuentes que se destrabó.
  >
  > ¿Quién puede destrabarla: alguien en particular, vos, o todavía no sabés?
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
- latencia: 5388 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado con esta tarea.
  >
  > ¿Qué te está trabando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 8538 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la terminás el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:43.  
  > Te voy a preguntar cómo viene el mié 4/11.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > ¿Qué te está trabando con esta tarea?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
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

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5690 ms
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
  > Vence el vie 23/10, dentro de 3 días hábiles.
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
- latencia: 4980 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que estás trabado. Para dejarlo anotado, me falta saber el motivo.
  >
  > ¿Qué te está frenando?
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 9706 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Anoté que la vas a terminar el mié 4/11. Vence el vie 30/10.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado hoy a las 10:43. El mié 4/11 te voy a preguntar cómo viene.
  >
  > 📋 Programar PLC de la comprimidora  
  > Me falta saber qué te está trabando para dejarlo anotado.
  >
  > ¿Qué te está frenando?
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
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

**Paso 5.** Marcos (2026-10-20 10:46): «es que no me mandaron el programa del fabricante»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5202 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que estás trabado porque no te mandaron el programa del fabricante.  
  > ⚠️ Mientras siga trabada, no te voy a pedir cómo viene. Retomo el seguimiento cuando me cuentes que se destrabó.
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
- latencia: 6085 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste hoy, me falta saber cuál de estas tareas:
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
- latencia: 2852 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy.
  >
  > El vie 30/10 te pregunto cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 2

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5474 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste hoy, necesito saber cuál tarea fue.
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
- latencia: 2173 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy.
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
- latencia: 5968 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste hoy, me falta saber en cuál tarea.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Con cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 2716 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que arrancaste hoy.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 4

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5881 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste hoy, me falta saber en qué tarea.
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
- latencia: 3273 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy. Está en curso.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

## 09 · Duda: ¿de qué tarea habla? · vez 5

Fuente: `tests/conversaciones/09-duda.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5841 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste hoy, necesito saber en cuál tarea.
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
- latencia: 2605 ms
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
- latencia: 5095 ms
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber cuál de las dos tareas de la comprimidora arrancaste.
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
- latencia: 4990 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste. Está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 5754 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber cuál de estas tareas es:
  >
  > 📋 Programar PLC de la comprimidora  
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos arrancaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 5067 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 3

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3485 ms
- Leda → Marcos: [botones: PLC, COM]
  > ¿Cuál de estas tareas arrancaste? Podés elegir una opción o escribirla:
  >
  > 🗓️ Programar PLC de la comprimidora  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál fue?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [formato] formato del mensaje a Marcos: esperado 'la pregunta, una sola y en el último renglón', real '¿Cuál de estas tareas arrancaste? Podés elegir una opción o escribirla:'

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4597 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste; está en curso.
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
- latencia: 5035 ms
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
- latencia: 5677 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 10 · Escribir en lugar de tocar un botón · vez 5

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3514 ms
- Leda → Marcos: [botones: PLC, COM]
  > ¿Con cuál de estas tareas arrancaste? Podés tocar una opción o escribirla:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- **falla** [formato] formato del mensaje a Marcos: esperado 'la pregunta, una sola y en el último renglón', real '¿Con cuál de estas tareas arrancaste? Podés tocar una opción o escribirla:'

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3693 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste esta tarea.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 11 · Algo vencido · vez 1

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Necesito saber cuál de las dos arrancaste. Podés elegir una opción o escribirme cuál:
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
- latencia: 9149 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Tocar esta opción no cambió nada: la pregunta ya estaba cerrada.
  >
  > 📋 Programar PLC de la comprimidora  
  > Se había cerrado ayer con tu respuesta sobre esta tarea.
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
- latencia: 4301 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste hoy.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 7056 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch.  
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
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- ya no va a pasar: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "llega": "no_le_va_a_llegar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 7597 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el vie 30/10, el día en que vence.
  >
  > Ismael no será notificado por el plazo anterior del mié 4/11.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

## 11 · Algo vencido · vez 2

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber cuál arrancaste para anotarlo.
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
- latencia: 8111 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Elegirla ahora no cambió nada: la pregunta ya se había cerrado ayer con la tarea del PLC.
  >
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Ayer quedó anotado que la arrancaste.
  >
  > Si también arrancaste la revisión, contámelo por mensaje.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3677 ms
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
- latencia: 6726 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el mié 4/11 porque esperás el switch.  
  > ⚠️ Vence el vie 30/10. Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado mañana a las 10 de la fecha que estimás.
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
- latencia: 6122 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que estimás terminarla el vie 30/10 porque llegó el switch. Es el día en que vence, así que, si la terminás entonces, no tendrá atraso.  
  > Ismael no será notificado de la fecha anterior.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '✏️ Quedó anotado que estimás terminarla el vie 30/10 porque llegó el switch. Es el día en que vence, así que, si la terminás entonces, no tendrá atraso.'

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
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos fue?

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 30/10.

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 5680 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > La pregunta ya se había cerrado ayer con esta tarea.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Elegirla ahora no cambió nada.
  >
  > Si también arrancaste la revisión, contámelo.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3577 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste hoy.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 6935 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el mié 4/11 porque esperás el switch.  
  > ⚠️ Si la terminás ese día, tendrá 3 días hábiles de atraso respecto del vencimiento del vie 30/10.  
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
- latencia: 8368 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que pensás terminarla el vie 30/10 porque llegó el switch.  
  > El vencimiento sigue siendo el vie 30/10. Ismael no será notificado por la fecha anterior.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
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
  > Para anotar que arrancaste, necesito saber cuál de estas tareas es:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
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
- latencia: 8014 ms
- Leda → Marcos:
  > La opción que tocaste ahora no cambió nada: esa pregunta ya se había cerrado ayer con esta tarea.
  >
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Si también arrancaste la de comunicaciones, decímelo en un mensaje nuevo.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3249 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste hoy; está en curso.
  >
  > El vie 30/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 5457 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch y que pensás terminarla el mié 4/11. Vence el vie 30/10; ese día no cambió.  
  > ⚠️ Si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.
  >
  > Ismael será notificado mañana a las 10.
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
- latencia: 7760 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que pensás terminarla el vie 30/10, el día en que vence. El vencimiento no cambió.
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

## 11 · Algo vencido · vez 5

Fuente: `tests/conversaciones/11-algo-vencido.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber cuál de las dos tareas es.
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
  > Te voy a preguntar cómo viene el vie 30/10.

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 6334 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Elegir esta opción ahora no cambió nada: la pregunta ya estaba cerrada.
  >
  > 📋 Programar PLC de la comprimidora  
  > La habías respondido ayer con esta tarea.
  >
  > Si también arrancaste la de comunicaciones, decímelo en un mensaje nuevo.
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 4665 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste hoy.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-23T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04"}}}]`
- latencia: 5978 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que esperás el switch y que calculás terminarla el mié 4/11.  
  > ⚠️ Vence el vie 30/10; si la terminás el mié 4/11, tendrá 3 días hábiles de atraso.  
  > Ismael será notificado mañana a las 10.
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
- latencia: 7153 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que llegó el switch y que calculás terminarla el vie 30/10, el día que vence.  
  > Ismael no será notificado por la fecha anterior.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
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
- latencia: 6805 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat: Ismael decide quién se encarga.
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
- latencia: 6784 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, así que no cambió su estado. Tampoco quedó anotada una fecha para terminarla.
  >
  > Seguí con la tarea.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6364 ms
- Leda → Marcos:
  > No puedo recordarte el viernes lo del turno médico.
  >
  > Agendá una alarma en tu calendario para ese día.
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
- latencia: 7223 ms
- Leda → Marcos:
  > El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno médico. Yo no puedo recordártelo el viernes.
  >
  > Agendá una alarma en tu calendario.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7519 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me contás que ya la terminaste, pero todavía no puedo recibir la entrega por chat. Aún no hay otra forma definida para entregarla.
  >
  > Por ahora, conservá la entrega.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6269 ms
- Leda → Marcos:
  > Tenés estas dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Me contaste que la terminaste, pero todavía figura en curso: la entrega no se puede recibir por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Todavía figura sin empezar.
  >
  > Por ahora, conservá la entrega del PLC y podés avanzar con la revisión de comunicaciones.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 2

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
- latencia: 9299 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat: Ismael decide quién queda a cargo.
  >
  > Puedo anotar para cuándo la vas a terminar y que estás tapado con lo de la paila.
  >
  > ¿Querés que lo haga?
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
- latencia: 9571 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No quedó anotada una fecha para terminarla ni el motivo.  
  > Ya figura en curso, aunque no tengo anotado desde cuándo.
  >
  > Seguí con la tarea; por acá no queda nada más pendiente.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6083 ms
- Leda → Marcos:
  > No puedo recordarte por acá el turno con el médico el viernes.
  >
  > Poné un recordatorio en tu calendario para ese día.
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
- latencia: 6808 ms
- Leda → Marcos:
  > El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno médico. Todavía no le llegó.
  >
  > Para el turno, poné un recordatorio en tu calendario.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 7078 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que la terminaste, pero todavía no puedo recibir la entrega por chat. No tengo indicada otra forma de presentarla.
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
- latencia: 7275 ms
- Leda → Marcos:
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Sigue figurando en curso, aunque me dijiste que la terminaste. Todavía no puedo recibir la entrega por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Está asignada, sin empezar.
  >
  > Consultá con tu equipo cómo entregar la del PLC.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 3

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
- latencia: 6952 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasársela a Nahuel por chat. Ismael decide si cambia el responsable.
  >
  > Puedo anotar para cuándo pensás terminarla, teniendo en cuenta que estás tapado con lo de la paila.
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
- latencia: 8300 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, aunque no tengo anotado desde cuándo la arrancaste.  
  > Dejé sin efecto la propuesta de anotar cuándo la terminarías; no quedó nada anotado.
  >
  > Seguí con la programación; por acá no hace falta nada más.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6060 ms
- Leda → Marcos:
  > No puedo recordarte por acá el turno con el médico del viernes.
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
- latencia: 5691 ms
- Leda → Marcos:
  > El administrador será notificado hoy a las 10:15 de que pediste un recordatorio para tu turno médico y no puedo hacerlo por acá.
  >
  > Para no olvidarte, poné un recordatorio en tu calendario.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 6483 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Entiendo que la terminaste. Todavía no puedo recibir la entrega por chat y no hay otra forma definida para hacerlo.
  >
  > Por ahora, guardá el trabajo terminado.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 9779 ms
- Leda → Marcos:
  > Tenés dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Sigue en curso. Me contaste que la terminaste, pero todavía no puedo recibir la entrega por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Está asignada y todavía no empezaste.
  >
  > Podés avanzar con la revisión de comunicaciones.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 12 · Algo que no está en la lista · vez 4

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

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
- latencia: 6598 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > No puedo pasarle la tarea a Nahuel por chat: Ismael decide el cambio de responsable.
  >
  > Puedo anotar para cuándo estimás terminarla y que estás tapado con lo de la paila.
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
- latencia: 8756 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, aunque no tengo anotado desde cuándo arrancaste.  
  > La propuesta de anotar para cuándo la terminás quedó sin efecto; no anoté nada.
  >
  > Cuando la termines, avisame.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6917 ms
- Leda → Marcos:
  > No puedo recordarte el viernes lo del médico; por acá solo hago seguimiento de las tareas del equipo.
  >
  > Agendá un recordatorio en tu celular.
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
- latencia: 6398 ms
- Leda → Marcos:
  > El administrador será notificado de que pediste un recordatorio para tu turno médico. Todavía no le llegó el aviso.
  >
  > Agendá el recordatorio en tu celular.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 9926 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me decís que ya la terminaste, pero todavía no puedo recibir la entrega por chat. No hay otra forma definida para entregarla.
  >
  > Por ahora, conservá el trabajo terminado.
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael
- [ ] no dice: que la presente por fuera de este chat o a otra persona (no hay otra forma definida)

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6109 ms
- Leda → Marcos:
  > Tenés estas dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vence vie 23/10  
  > Figura en curso. Me contaste que la terminaste, pero la entrega todavía no se recibe por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vence vie 30/10  
  > Está asignada y todavía no figura empezada.
  >
  > Por ahora, conservá el trabajo terminado del PLC.
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
- latencia: 6059 ms
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
- latencia: 8292 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Ya figura en curso, aunque no tengo anotado desde cuándo la arrancaste.  
  > La propuesta de anotar para cuándo la terminarías quedó sin efecto; no se anotó nada.
  >
  > Cuando tengas novedades, contame cómo viene.
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Que le recuerde el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo va a terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"llega": "2026-10-20T10:15:00-03:00"}}}]`
- latencia: 6633 ms
- Leda → Marcos:
  > No puedo recordarte el turno con el médico el viernes; por acá solo puedo ayudarte con las tareas del equipo.
  >
  > Para no olvidarte, poné un recordatorio en tu celular.
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
- latencia: 6346 ms
- Leda → Marcos:
  > El administrador será notificado hoy a las 10:15 de que pediste que te recuerde el turno médico.
  >
  > Para no olvidarte, poné un recordatorio en tu celular.
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC", "otra_forma_de_hacerlo": "ninguna_definida"}]`
- latencia: 8148 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Me decís que ya la terminaste. Todavía no puedo recibir la entrega por chat y no hay otra forma definida.
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
- latencia: 6730 ms
- Leda → Marcos:
  > Tenés estas dos tareas pendientes:
  >
  > 🗓️ Programar PLC de la comprimidora — vie 23/10  
  > Me dijiste que la terminaste, pero todavía figura en curso porque no se pudo recibir la entrega por chat.
  >
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vie 30/10  
  > Está asignada y aún no figura como empezada.
  >
  > Por ahora, conservá el trabajo del PLC hasta que se defina cómo entregarlo.
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 1

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
- latencia: 8662 ms
- Leda → Marcos: [botones: PLC, COM]
  > Necesito saber con cuál de las dos tareas arrancaste para anotarlo:
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
- latencia: 3945 ms
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
  > Tenés dos tareas que vencen el vie 23/10:
  >
  > 🗓️ Programar PLC de la comprimidora — vie 23/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vie 23/10
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
- latencia: 7852 ms
- Leda → Marcos: [botones: PLC, COM]
  > Todavía no quedó anotado que arrancaste: hay dos tareas de la comprimidora.
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
- latencia: 4491 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 23/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Estas dos tareas vencen el vie 23/10:
  >
  > 🗓️ Programar PLC de la comprimidora — vie 23/10  
  > 🗓️ Revisar comunicaciones industriales de la comprimidora — vie 23/10
  >
  > No hace falta responder.
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}]`
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel:
  > 📋 Integrar datos de la comprimidora en CoreLabs  
  > Vence el vie 23/10, dentro de 3 días hábiles.
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
- latencia: 4772 ms
- Leda → Marcos: [botones: PLC, COM]
  > Para anotar que arrancaste, necesito saber a cuál de estas dos tareas te referís:
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
- latencia: 6019 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que la arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 23/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 4

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Tenés dos tareas que vencen el vie 23/10:
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
- latencia: 7448 ms
- Leda → Marcos: [botones: PLC, COM]
  > Hay dos tareas de la comprimidora y necesito saber con cuál arrancaste.
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos empezaste?
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 3868 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste con esta tarea.
  >
  > Te voy a preguntar cómo viene el vie 23/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 5

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F FALLA.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel:
  > 📋 Integrar datos de la comprimidora en CoreLabs  
  > Vence el vie 23/10, en 3 días hábiles.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos:
  > Tenés dos tareas que vencen el vie 23/10:
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
- latencia: 9515 ms
- Leda → Marcos: [botones: PLC, COM]
  > Me falta saber con cuál de estas dos tareas arrancaste para anotarlo:
  >
  > 📋 Programar PLC de la comprimidora
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora
  >
  > ¿Cuál de las dos? Podés tocar una opción o escribirla.
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas
- **falla** [formato] formato del mensaje a Marcos: esperado 'el cierre, solo en su renglón y con un renglón en blanco antes', real '¿Cuál de las dos? Podés tocar una opción o escribirla.'

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4202 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste con esta tarea.
  >
  > El vie 23/10 te voy a preguntar cómo viene.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 1

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok · F ok.

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
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}]`
- latencia: 4398 ms
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
- latencia: 4859 ms
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
- latencia: 4766 ms
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
- latencia: 3216 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también arrancaste esta tarea.
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
- latencia: 4300 ms
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
- latencia: 2945 ms
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
- latencia: 5741 ms
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
- latencia: 3114 ms
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
- latencia: 5566 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 23/10.
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- latencia: 3766 ms
- Leda → Marcos:
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > ✏️ Quedó anotado que también la arrancaste.
  >
  > Te voy a preguntar cómo viene el vie 30/10.
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

## 15 · Voy bien, la tengo casi lista · vez 1

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
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste o, si no, para cuándo la terminás y hay algo que te impida avanzar?
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-28T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5919 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que venís bien y la tenés casi lista.
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
  > Ayer contaste que venías bien y la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termines esta tarea.
  >
  > ¿La terminaste o, si no, para cuándo la terminás y hay algo que te impida avanzar?
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
- latencia: 4636 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que todo está en orden y seguís con eso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para cuándo la terminás?
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
- latencia: 6666 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la vas a terminar el mar 3/11.  
  > ⚠️ Venció ayer; si la terminás ese día, tendrá 5 días hábiles de atraso.  
  > ⚠️ La revisión de comunicaciones industriales de la comprimidora espera a que termines esta tarea.
  >
  > Ismael será notificado hoy a las 10:45 de la fecha que diste.
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

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 3/11. Venció ayer.  
  > ⚠️ Si la termina ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Hoy es el día que dijiste que la terminabas.  
  > ⚠️ Venció el mar 27/10 y lleva 5 días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 6/11, en 3 días hábiles.  
  > ⚠️ No puede arrancar hasta que termines la programación del PLC.
  >
  > ¿Terminaste la programación del PLC o, si no, para cuándo la terminás y hay algo que te impida avanzar?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 2

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
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
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
- latencia: 6185 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que contaste que vas bien y la tenés casi lista.  
  > Todavía falta saber si la terminaste, para cuándo la terminás o si estás trabado.
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
  > Ayer contaste que ibas bien y la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- latencia: 6134 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que contaste que todo está en orden y seguís con eso.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día la vas a tener?
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
- latencia: 6517 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la vas a tener el mar 3/11. El vencimiento no cambió: fue ayer.  
  > ⚠️ Si la terminás ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales depende de que la termines.  
  > Ismael será notificado hoy a las 10:45 de la fecha que diste.
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

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael:
  > 📋 Programar PLC de la comprimidora  
  > Marcos dijo que la terminará el mar 3/11. Venció ayer.  
  > ⚠️ Si termina ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea.
  >
  > No hace falta responder.
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > Dijiste que la ibas a terminar hoy. Venció el mar 27/10 y lleva 5 días hábiles de atraso.  
  > Ismael ya fue notificado de la fecha que diste.
  >
  > 📋 Revisar comunicaciones industriales de la comprimidora  
  > Vence el vie 6/11, en 3 días hábiles.  
  > ⚠️ No puede arrancar hasta que termines la programación.
  >
  > ¿Terminaste la programación, para cuándo la terminás o estás trabado?
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

## 15 · Voy bien, la tengo casi lista · vez 3

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M FALLA · F FALLA.

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
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
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
- latencia: 6505 ms
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
  > Ayer contaste que la tenías casi lista.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso. La revisión de comunicaciones no puede arrancar hasta que la termines.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- latencia: 5792 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que seguís con eso y que está todo en orden.  
  > ⚠️ Venció ayer y lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día la vas a tener?
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
- latencia: 6608 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Anoté que la vas a tener el mar 3/11.  
  > ⚠️ Venció ayer. Si la terminás ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.
  >
  > Ismael será notificado hoy a las 10:45.
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
- **falla** [formato] formato del mensaje a Marcos: esperado 'ningún renglón de más de 140 caracteres', real '⚠️ Venció ayer. Si la terminás ese día, tendrá 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que la termines.'

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- (Leda no manda nada)
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 8.** Leda (2026-11-03 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 15 · Voy bien, la tengo casi lista · vez 4

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

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
  > ⚠️ La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea.
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
- latencia: 5733 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que vas bien y la tenés casi lista.
  >
  > Mañana a las 10 te vuelvo a preguntar si la terminaste, para cuándo la terminás o si estás trabado.
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
  > Ayer me contaste que ibas bien y la tenías casi lista.  
  > ⚠️ Lleva un día hábil de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que la termines.
  >
  > ¿La terminaste, para cuándo la terminás o estás trabado?
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
- latencia: 5046 ms
- Leda → Marcos:
  > 📋 Programar PLC de la comprimidora  
  > ✏️ Quedó anotado que todo está en orden y seguís con eso.  
  > ⚠️ Lleva un día hábil de atraso.
  >
  > Mañana a las 10 te vuelvo a preguntar cómo viene.
  >
  > ¿Para qué día la vas a tener terminada?
- [ ] dice: que lo anotó
- [ ] dice: que la tarea venció el martes 27
- [ ] dice: una sola pregunta, directa: para qué día la va a tener
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha propuesta por Leda
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche por el atraso
- [ ] no dice: dos preguntas juntas

**Paso 6.** Marcos (2026-10-28 10:45): «para el martes 3 la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 884 ms
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
- **falla** [comprension] pregunta abierta después: esperado None, real {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- (Leda no manda nada)
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'el': '2026-10-28', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-11-03', 'atraso_si_se_cumple_la_prevision_dias_habiles': 5}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-27', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': '63d9858a-c69b-4058-b5ac-e07263578808'}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': '5fa95a96-a07b-4fd0-9b77-1fdc870ae26b'}, {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'enviado', 'motivo': None, 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'estado': 'en_curso', 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'avance_anterior': {'el': '2026-10-27', 'dijo': 'voy bien, la tengo casi lista'}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 1}, 'outbox_id': '1a8e065f-8000-4089-aac3-62b5205f5ed6'}, {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'fallido', 'motivo': None, 'hechos': {'aviso': 'repregunta_de_estado', 'tarea': 'PLC', 'vence': '2026-10-27', 'avance_anterior': {'el': '2026-10-28', 'dijo': 'todo en orden, sigo con eso'}, 'necesita_respuesta': True}, 'outbox_id': None}]

**Paso 8.** Leda (2026-11-03 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC', 'COM'], 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-11-03'}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-22 10:00)

**Paso 1.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-27', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1007 ms
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'dijo': 'presente', 'el': '2026-10-27'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1038 ms
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
- latencia: 1052 ms
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 16 · Arranqué hoy, con la tarea vencida · vez 1

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Leda (2026-10-23 10:00)

**Paso 1.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 1, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 993 ms
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
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 914 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:25'}}], real []
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 16 · Arranqué hoy, con la tarea vencida · vez 2

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Leda (2026-10-23 10:00)

**Paso 1.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 1, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 926 ms
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
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 918 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:25'}}], real []
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 16 · Arranqué hoy, con la tarea vencida · vez 3

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Leda (2026-10-23 10:00)

**Paso 1.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 1, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1245 ms
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
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1462 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:25'}}], real []
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Leda (2026-10-23 10:00)

**Paso 1.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 1, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 891 ms
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
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1043 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:25'}}], real []
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 16 · Arranqué hoy, con la tarea vencida · vez 5

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Leda (2026-10-23 10:00)

**Paso 1.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 2, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 1, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1030 ms
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
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'fecha_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 3.** Marcos (2026-10-26 10:25): «para el miercoles la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 968 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar, y cuándo si lo dice, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28 (si nombra lo que el paso 2 anunció para el martes, como lo que va a pasar, no como un pedido que no sale)
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe
- [ ] no dice: que el aviso a Ismael está guardado, en cola o sin enviar
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:25'}}], real []
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 5.** nadie (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: a Marcos, nada el martes: el pedido guardado se omite con su motivo
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'asignada', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'espera_algo_cierto': ['si_la_empezo', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

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

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 912 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 993 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1029 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 2

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 842 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 485 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1149 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 3

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1105 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 860 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 839 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 4

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1307 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 862 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 995 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 17 · Llegó el switch, sigo · vez 5

Fuente: `tests/conversaciones/17-destrabar.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 832 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el viernes 23, el día del vencimiento, o que puede avisar si se vuelve a trabar
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
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 3.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'estado': 'en_curso'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1284 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
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
- latencia: 1068 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'destrabar', 'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [comprension] falta un efecto: bloqueo resuelto: esperado ['PLC'], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'destrabar', 'resultado': 'anotado', 'tarea': 'PLC', 'bloqueo_resuelto': {'causa': 'se quemo la fuente'}, 'estado': 'en_curso', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 6.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': True, 'avance_anterior': {'jugada': 'destrabar', 'dijo': 'presente'}, 'espera_algo_cierto': 'presente', 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 1

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1376 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, casi la tengo'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[]`
- hechos: `[]`
- latencia: 856 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 7.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 2

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 975 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, casi la tengo'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[]`
- hechos: `[]`
- latencia: 862 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 7.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 3

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1019 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, casi la tengo'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[]`
- hechos: `[]`
- latencia: 872 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 7.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 4

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 852 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, casi la tengo'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[]`
- hechos: `[]`
- latencia: 835 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 7.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 5

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'vence': '2026-10-23', 'atraso_dias_habiles': 0, 'si_no_hay_respuesta': 'ausente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1353 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [comprension] jugadas: esperado [{'nombre': 'informar_avance', 'tarea': 'PLC', 'palabras': 'voy bien, casi la tengo'}], real []
- **falla** [comprension] falta un efecto: avance: esperado [{'tarea': 'PLC'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real []

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[]`
- hechos: `[]`
- latencia: 839 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-28'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-28', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'estado': 'guardado', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real []
- **falla** [comprension] esperas abiertas después: esperado [], real ['PLC']

**Paso 5.** Leda (2026-10-26 10:00)
- (Leda no manda nada)
- [ ] dice: que Marcos prevé terminar la tarea del PLC el miércoles 28
- [ ] dice: que la fecha comprometida era el viernes 23
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] no dice: que Ismael tiene que hacer algo
- [ ] no dice: cómo funciona el aviso
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] aviso en el estado: esperado {'tipo': 'repregunta_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_respondio'}, real [{'tipo': 'aviso_previo', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'omitido', 'motivo': 'ya_vencio', 'hechos': {'aviso': 'vencimiento_proximo', 'tarea': 'PLC', 'vence': '2026-10-23', 'necesita_respuesta': False, 'dias_habiles_hasta_el_vencimiento': 3}, 'outbox_id': None}, {'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'a': 'Marcos', 'estado': 'guardado', 'motivo': None, 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 0}, 'outbox_id': None}]

**Paso 6.** nadie (2026-10-26 16:00, 2026-10-27 10:00, 2026-10-27 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]

**Paso 7.** Leda (2026-10-28 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 19 · Palabras de todos los días, no los nombres del sistema · vez 1

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 856 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1044 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-20T11:05'}}], real []

**Paso 3.** Leda (2026-10-20 11:06)
- (Leda no manda nada)
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 908 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 5.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}}, 'pide_el_estado_el': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 7.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 19 · Palabras de todos los días, no los nombres del sistema · vez 2

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 891 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1495 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-20T11:05'}}], real []

**Paso 3.** Leda (2026-10-20 11:06)
- (Leda no manda nada)
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 846 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 5.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}}, 'pide_el_estado_el': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 7.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 19 · Palabras de todos los días, no los nombres del sistema · vez 3

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 938 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[]`
- hechos: `[]`
- latencia: 984 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-20T11:05'}}], real []

**Paso 3.** Leda (2026-10-20 11:06)
- (Leda no manda nada)
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1015 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 5.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}}, 'pide_el_estado_el': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 7.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 19 · Palabras de todos los días, no los nombres del sistema · vez 4

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1159 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[]`
- hechos: `[]`
- latencia: 854 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-20T11:05'}}], real []

**Paso 3.** Leda (2026-10-20 11:06)
- (Leda no manda nada)
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 845 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 5.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}}, 'pide_el_estado_el': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 7.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 19 · Palabras de todos los días, no los nombres del sistema · vez 5

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 933 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel
- **falla** [comprension] jugadas: esperado [{'nombre': 'pedir_reasignacion', 'tarea': 'PLC', 'a': 'nahuel'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] la pregunta de la respuesta: esperado {'tipo': 'propuesta', 'tarea': 'PLC', 'propone': ['anotar_prevision']}, real None
- **falla** [comprension] hechos: esperado [{'jugada': 'pedir_reasignacion', 'resultado': 'no_por_chat', 'quien_decide': 'Ismael Soschinski', 'alternativa': 'anotar_prevision', 'tarea': 'PLC', 'pregunta': 'propuesta'}], real []
- **falla** [comprension] pregunta abierta después: esperado {'tipo': 'propuesta', 'tarea': 'PLC'}, real None

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[]`
- hechos: `[]`
- latencia: 929 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_prevision', 'tarea': 'PLC', 'fecha': '2026-10-27'}], real []
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'PLC', 'fecha': '2026-10-27', 'motivo': 'ausente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'PLC', 'a': 'Ismael', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-20T11:05'}}], real []

**Paso 3.** Leda (2026-10-20 11:06)
- (Leda no manda nada)
- [ ] dice: que Marcos la termina el martes 27
- [ ] dice: que vencía el viernes 23
- [ ] dice: el atraso, dos días hábiles
- [ ] dice: que la de comunicaciones depende de ella
- [ ] dice: que no hace falta que conteste
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que Ismael tiene que hacer algo
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'PLC', 'hechos': {'prevision': '2026-10-27', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'dependientes': ['COM']}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 4.** Marcos (2026-10-20 11:15): «que es prevision?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 829 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]

**Paso 5.** Leda (2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que tiene anotado que la termina el martes 27 y que Ismael ya lo sabe
- [ ] dice: que el martes 27 le pregunta cómo viene, como algo que todavía no pasó
- [ ] dice: que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- [ ] no dice: una pregunta
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'vencimiento_con_prevision', 'tarea': 'PLC', 'hechos': {'necesita_respuesta': False, 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27', 'atraso_si_se_cumple_la_prevision_dias_habiles': 2, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego'}}, 'pide_el_estado_el': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] esperas abiertas después: esperado [], real ['PLC']

**Paso 6.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

**Paso 7.** Leda (2026-10-27 10:00)
- (Leda no manda nada)
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'vence': '2026-10-23', 'prevision_vigente': {'fecha': '2026-10-27'}}}, real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'motor_aviso_guardado', 'severidad': 'media'}]
- **falla** [motor] pregunta abierta después: esperado {'tipo': 'estado_de_la_tarea', 'tarea': 'PLC'}, real None

## 20 · El formato de los mensajes · vez 1

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1469 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'asignada', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'en_curso', 'vence': '2026-10-30'}]}], real []

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1038 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
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
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:16)
- (Leda no manda nada)
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

## 20 · El formato de los mensajes · vez 2

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 804 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'asignada', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'en_curso', 'vence': '2026-10-30'}]}], real []

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1126 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
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
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:16)
- (Leda no manda nada)
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

## 20 · El formato de los mensajes · vez 3

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 870 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'asignada', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'en_curso', 'vence': '2026-10-30'}]}], real []

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 858 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
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
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:16)
- (Leda no manda nada)
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

## 20 · El formato de los mensajes · vez 4

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1260 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'asignada', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'en_curso', 'vence': '2026-10-30'}]}], real []

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 848 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
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
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:16)
- (Leda no manda nada)
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

## 20 · El formato de los mensajes · vez 5

Fuente: `tests/conversaciones/20-formato-de-los-mensajes.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C FALLA · M FALLA · F ok.

**Preludio.** Leda (2026-10-20 10:00)

**Paso 1.** Marcos (2026-10-20 10:10): «que tengo pendiente?»
- jugadas: `[]`
- hechos: `[]`
- latencia: 931 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
- [ ] dice: primero, en un renglón, que tiene dos tareas pendientes
- [ ] dice: las dos, cada una en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10
- [ ] dice: el próximo paso, aparte y al final
- [ ] no dice: tareas de otras personas
- [ ] no dice: las dos tareas en un mismo renglón
- [ ] no dice: negrita, viñetas u otra marca (títulos, enlaces, cursiva, código)
- [ ] no dice: una fecha larga ("viernes 23 de octubre")
- **falla** [comprension] jugadas: esperado [{'nombre': 'consultar_pendientes'}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'consultar_pendientes', 'resultado': 'leido', 'tareas': [{'titulo': 'PLC', 'estado': 'asignada', 'vence': '2026-10-23'}, {'titulo': 'COM', 'estado': 'en_curso', 'vence': '2026-10-30'}]}], real []

**Paso 2.** Marcos (2026-10-20 10:15): «arranque con el plc. y lo de comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[]`
- hechos: `[]`
- latencia: 1003 ms
- Leda → Marcos: «Tuve un problema y no pude responder tu mensaje. Ya quedó registrado para que lo revise un administrador.»
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
- **falla** [comprension] jugadas: esperado [{'nombre': 'anotar_inicio', 'tarea': 'PLC'}, {'nombre': 'anotar_prevision', 'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'espera el switch nuevo'}], real []
- **falla** [comprension] falta un efecto: estado: esperado {'PLC': 'en_curso'}, real {}
- **falla** [comprension] falta un efecto: previsión: esperado [{'tarea': 'COM', 'fecha': '2026-11-04', 'motivo': 'presente'}], real []
- **falla** [comprension] falta un efecto: aviso guardado: esperado [{'tipo': 'nueva_prevision', 'tarea': 'COM', 'a': 'Ismael', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}], real []
- **falla** [motor] incidente: esperado [], real [{'etapa': 'turno_conversacion', 'severidad': 'media'}]
- **falla** [comprension] hechos: esperado [{'jugada': 'anotar_inicio', 'resultado': 'anotado', 'tarea': 'PLC'}, {'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'COM', 'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}], real []

**Paso 3.** Leda (2026-10-20 10:16)
- (Leda no manda nada)
- [ ] dice: un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque
- [ ] dice: debajo, que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo
- [ ] dice: que vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles
- [ ] dice: que no hace falta que conteste, solo en el último renglón
- [ ] no dice: nada de la tarea del PLC
- [ ] no dice: que la fecha cambió
- [ ] no dice: quién dijo qué antes del renglón de la tarea
- [ ] no dice: una marca en el medio de un renglón
- [ ] no dice: un párrafo corrido
- [ ] no dice: Marcos con su apellido
- [ ] no dice: negrita
- **falla** [motor] no salió lo esperado: esperado {'a': 'Ismael', 'tipo': 'nueva_prevision', 'tarea': 'COM', 'hechos': {'prevision': '2026-11-04', 'fecha_comprometida': '2026-10-30', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': [], 'motivo': 'presente'}}, real []
- **falla** [motor] el aviso no salió a su hora: la IA no lo redactó: esperado None, real {'falla': 'HTTPStatusError', 'http': 429}

