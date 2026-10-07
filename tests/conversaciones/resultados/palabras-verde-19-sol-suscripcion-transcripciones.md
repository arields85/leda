# Transcripciones de la ronda palabras-verde-19-sol-suscripcion

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 19 · Palabras de todos los días, no los nombres del sistema · vez 1

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre. No hace falta que respondas.»

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 5787 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; eso lo decide Ismael Soschinski. ¿Querés que, mientras tanto, anote para cuándo calculás terminarla y por qué?»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 10986 ms
- Leda → Marcos: «Quedó anotado que calculás terminar «Programar PLC de la comprimidora» el martes 27. Vence el viernes 23, así que, si terminás el 27, tendrá dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. Ismael Soschinski se va a enterar de tu previsión hoy a las 11:05. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió

**Paso 3.** Leda (2026-10-20 11:06)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos prevé terminar “Programar PLC de la comprimidora” el martes 27 de octubre. La tarea vence el viernes 23: si se cumple esa previsión, tendrá dos días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” sigue pendiente de esa tarea. No hace falta que respondas.»
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
- latencia: 6073 ms
- Leda → Marcos: «En tu caso, es el día que calculás terminar «Programar PLC de la comprimidora»: el martes 27 de octubre. No cambia el vencimiento, que sigue siendo el viernes 23. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. Calculás terminarla el martes 27; si se cumple, tendrá dos días hábiles de atraso. Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. El martes 27 te voy a preguntar cómo viene. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el viernes 23 y hoy lleva dos días hábiles de atraso. Habías calculado terminarla hoy; Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo calculás terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 2

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre. No hace falta que respondas a este aviso.»

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6795 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; ese cambio lo decide Ismael Soschinski. Sí puedo anotar para cuándo calculás terminarla y por qué. ¿Querés que lo haga?»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 7820 ms
- Leda → Marcos: «Quedó anotado que calculás terminar «Programar PLC de la comprimidora» el martes 27. Sigue venciendo el viernes 23, así que, si terminás el 27, serán dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. Ismael Soschinski se va a enterar hoy a las 11:05. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió

**Paso 3.** Leda (2026-10-20 11:06)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos dijo que terminará «Programar PLC de la comprimidora» el martes 27 de octubre. Vence el viernes 23, así que, si se cumple esa previsión, tendrá dos días hábiles de atraso. De esa tarea depende «Revisar comunicaciones industriales de la comprimidora». No hace falta que respondas.»
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
- latencia: 5172 ms
- Leda → Marcos: «Es el día que calculás terminar «Programar PLC de la comprimidora»: quedó anotado el martes 27. No cambia el vencimiento, que sigue siendo el viernes 23, ni significa que ya esté terminada. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23. Calculás terminarla el martes 27; si se cumple, tendrá dos días hábiles de atraso. Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. El martes 27 te voy a preguntar cómo viene. No hace falta que respondas a este aviso.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, hoy martes 27 es el día que calculabas terminar «Programar PLC de la comprimidora». Venció el viernes 23 y lleva dos días hábiles de atraso. Ismael Soschinski ya está al tanto, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines.

¿La terminaste o, si sigue pendiente, para cuándo calculás terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 3

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 7180 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; ese cambio lo decide Ismael Soschinski. ¿Querés que anote para cuándo calculás terminarla y por qué?»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 7589 ms
- Leda → Marcos: «Quedó anotado que calculás terminar «Programar PLC de la comprimidora» el martes 27. La tarea sigue venciendo el viernes 23: si la terminás el martes, serán dos días hábiles de atraso. De ella depende «Revisar comunicaciones industriales de la comprimidora». Ismael Soschinski se enterará hoy a las 11:05. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió

**Paso 3.** Leda (2026-10-20 11:06)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos dijo que terminará “Programar PLC de la comprimidora” el martes 27 de octubre. La tarea vence el viernes 23; si termina ese día, serán 2 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” depende de esa tarea. No hace falta que respondas.»
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
- latencia: 7389 ms
- Leda → Marcos: «Es el día que calculás terminar «Programar PLC de la comprimidora»: me dijiste el martes 27. No cambia el vencimiento, que sigue siendo el viernes 23. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23. Calculás terminarla el martes 27; si es así, tendrá dos días hábiles de atraso. Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines.

El martes 27 te voy a preguntar cómo viene. No hace falta que respondas ahora.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Hoy, martes 27, es el día que calculabas terminar «Programar PLC de la comprimidora». Lleva dos días hábiles de atraso; Ismael ya está al tanto y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines.

¿La terminaste o, si no, para cuándo calculás terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 4

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas a este aviso.»

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6995 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; ese cambio lo decide Ismael Soschinski. ¿Querés que anote para cuándo calculás terminarla y por qué?»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 10052 ms
- Leda → Marcos: «Quedó anotado que calculás terminar «Programar PLC de la comprimidora» el martes 27. Sigue venciendo el viernes 23: si terminás el 27, serán dos días hábiles de atraso. De esta tarea depende «Revisar comunicaciones industriales de la comprimidora». Ismael Soschinski se enterará hoy a las 11:05. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió

**Paso 3.** Leda (2026-10-20 11:06)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos prevé terminar «Programar PLC de la comprimidora» el martes 27 de octubre. Vence el viernes 23, así que, si cumple esa previsión, quedaría dos días hábiles atrasada. «Revisar comunicaciones industriales de la comprimidora» sigue abierta y depende de esa tarea. No hace falta que respondas.»
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
- latencia: 7467 ms
- Leda → Marcos: «Es el día que calculás terminar «Programar PLC de la comprimidora»: el martes 27 de octubre. La tarea sigue venciendo el viernes 23. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23. Quedó anotado que calculás terminarla el martes 27; si se cumple, serán dos días hábiles de atraso. Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termines esta tarea. El martes 27 te voy a preguntar cómo viene. No hace falta que respondas a este aviso.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, hoy martes 27 «Programar PLC de la comprimidora» sigue en curso y lleva dos días hábiles de atraso. Es el día que calculabas terminarla; Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo calculás terminarla y hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

## 19 · Palabras de todos los días, no los nombres del sistema · vez 5

Fuente: `tests/conversaciones/19-palabras-de-todos-los-dias.md`. Motor: `leda.motor`. IA: `chatgpt/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente esa fecha; no hace falta que respondas a este aviso.»

**Paso 1.** Marcos (2026-10-20 11:00): «me la podes pasar a nahuel?»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 6804 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; ese cambio lo decide Ismael Soschinski. ¿Querés que anote para cuándo calculás terminarla y por qué?»
- [ ] dice: que eso no lo puede hacer y que lo decide Ismael
- [ ] dice: ofrece anotar para qué día la va a terminar, con palabras de todos los días
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la tarea pasó a Nahuel

**Paso 2.** Marcos (2026-10-20 11:05): «dale, para el martes 27»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "2026-10-20T11:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27"}}}]`
- latencia: 8853 ms
- Leda → Marcos: «Anoté que calculás terminar «Programar PLC de la comprimidora» el martes 27 de octubre. Vence el viernes 23, así que, si la terminás ese día, serán dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esta tarea. Ismael Soschinski se enterará hoy a las 11:05. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: que anotó que la del PLC la termina el martes 27
- [ ] dice: que el vencimiento sigue siendo el viernes 23, dicho como el día para el que estaba
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que el martes 27 le pregunta cómo viene
- [ ] no dice: "previsión", "fecha comprometida", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: que la fecha de la tarea cambió

**Paso 3.** Leda (2026-10-20 11:06)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» el martes 27 de octubre. La tarea vence el viernes 23; si se cumple esa previsión, terminaría con dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de ese trabajo. No hace falta que respondas.»
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
- latencia: 6987 ms
- Leda → Marcos: «Es el día que calculás terminar «Programar PLC de la comprimidora»: el martes 27 de octubre. Eso quedó anotado, pero la tarea sigue venciendo el viernes 23. El martes 27 te voy a preguntar cómo viene.»
- [ ] dice: el hecho concreto que esa palabra nombra en su caso: el día que él dio para terminar la tarea del PLC, el martes 27, y que el vencimiento del viernes 23 no cambia
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una definición general del sistema (un campo, un dato, un registro, cómo lo guarda o lo usa Leda)
- [ ] no dice: otra pregunta

**Paso 5.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. Quedó anotado que calculás terminarla el martes 27; si se cumple, serán dos días hábiles de atraso. Ismael Soschinski ya lo sabe y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termines esta tarea. El martes 27 te voy a preguntar cómo viene. No hace falta que respondas a este aviso.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» venció el viernes 23 y lleva dos días hábiles de atraso. Habías calculado terminarla hoy; Ismael Soschinski ya lo sabe. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines.

¿Cómo viene la tarea: la terminaste, calculás terminarla otro día o hay algo que te traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 2}`
- [ ] dice: que hoy es el día que Marcos dio para terminar la tarea del PLC
- [ ] dice: pregunta cómo viene
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: "previsión", "fecha comprometida", "pedido de estado", "escalamiento", "referente", "dependiente" ni otro nombre de un dato o de una jugada
- [ ] no dice: un reproche

