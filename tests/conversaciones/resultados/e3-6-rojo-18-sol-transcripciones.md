# Transcripciones de la ronda e3-6-rojo-18-sol

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 1

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6074 ms
- Leda → Marcos: «Anoté que venís bien y casi la tenés con «Programar PLC de la comprimidora». Sigue pendiente saber si ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado. Te vuelvo a pedir el estado el lunes 26 de octubre a las 10.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [motor] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'voy bien, casi la tengo'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'veces_sin_algo_cierto': 1}]

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "estado": "retirado_sin_enviar", "motivo": "ya_respondio"}]`
- latencia: 6402 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida era el viernes 23: si se cumple tu previsión, tendrá tres días hábiles de atraso. De ella depende «Revisar comunicaciones industriales de la comprimidora».

El pedido de estado que te había anunciado para hoy ya no va a salir, porque ya respondiste. El aviso a Ismael Soschinski está guardado para salir hoy a las 10. Te volveré a pedir el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [motor] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'motivo': None, 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'todavia_no'}}}]

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos prevé terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si se cumple la previsión, la tarea tendrá 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» sigue abierta y depende de esa tarea. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Hoy es el día para el que previste terminar «Programar PLC de la comprimidora». Lleva tres días hábiles de atraso y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Ismael Soschinski ya recibió el aviso. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 2

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste? Si no, contame para cuándo prevés terminarla o si está trabada.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5788 ms
- Leda → Marcos: «Quedó anotado que venís bien y casi tenés «Programar PLC de la comprimidora». Todavía falta saber si la terminaste o para cuándo prevés terminarla. El lunes 26 de octubre a las 10:00 te vuelvo a pedir el estado.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [motor] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'voy bien, casi la tengo'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'veces_sin_algo_cierto': 1}]

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "estado": "retirado_sin_enviar", "motivo": "ya_respondio"}]`
- latencia: 7026 ms
- Leda → Marcos: «Quedó anotado que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre, pasado mañana. La fecha comprometida sigue siendo el viernes 23: si se cumple tu previsión, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esta tarea.

El aviso a Ismael Soschinski está guardado para salir hoy a las 10:00; todavía no salió. El pedido de estado que te había anunciado para hoy ya no va a salir porque ya respondiste. Te vuelvo a pedir el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [motor] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'motivo': None, 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'todavia_no'}}}]

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si cumple esa previsión, tendrá 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esa tarea. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» lleva tres días hábiles de atraso y preveías terminarla hoy. El aviso a Ismael Soschinski ya salió. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine.

¿Ya la terminaste o, si no, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 3

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de 3 días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo estimás terminarla y hay algo que te trabe?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7176 ms
- Leda → Marcos: «Anoté que vas bien y casi la tenés con «Programar PLC de la comprimidora». Sigo pendiente de saber si la terminaste o, si no, para cuándo estimás terminarla y si algo te traba. El lunes 26 de octubre a las 10:00 te vuelvo a pedir el estado.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [motor] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'voy bien, casi la tengo'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'veces_sin_algo_cierto': 1}]

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "estado": "retirado_sin_enviar", "motivo": "ya_respondio"}]`
- latencia: 6708 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23: si terminás el miércoles, serán 3 días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esta tarea.

El pedido de estado que te había anunciado para hoy ya no va a salir, porque respondiste. El aviso a Ismael Soschinski está guardado para salir hoy a las 10:00. Te pediré el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [motor] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'motivo': None, 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'todavia_no'}}}]

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos prevé terminar “Programar PLC de la comprimidora” pasado mañana, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23; si se cumple la previsión, serán 3 días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” depende de esa tarea. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es la fecha que estimaste para terminar «Programar PLC de la comprimidora». Sigue anotada en curso y lleva 3 días hábiles de atraso. Ismael ya recibió el aviso, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y hay algo que te trabe?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 4

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste o, si no, para cuándo estimás terminarla y hay algo que te traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7240 ms
- Leda → Marcos: «Anoté que venís bien y casi la tenés con «Programar PLC de la comprimidora». Todavía necesito saber si la terminaste o, si no, para cuándo estimás terminarla y si hay algo que te traba. Si no me contás antes, quedó previsto volver a pedirte el estado el lunes 26 de octubre a las 10.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [motor] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'voy bien, casi la tengo'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'veces_sin_algo_cierto': 1}]

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "estado": "retirado_sin_enviar", "motivo": "ya_respondio"}]`
- latencia: 6559 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida era el viernes 23: si se cumple tu previsión, tendrá tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea.

El pedido de estado previsto para hoy ya no va a salir porque ya respondiste. Quedó guardado un aviso para Ismael Soschinski, previsto para hoy a las 10. Te voy a pedir el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [motor] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'motivo': None, 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'todavia_no'}}}]

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si cumple la previsión, la tarea tendrá 3 días hábiles de atraso. De ella depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, «Programar PLC de la comprimidora» sigue en curso. Venció el viernes 23 de octubre y lleva tres días hábiles de atraso. Habías previsto terminarla hoy, miércoles 28; Ismael Soschinski ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine.

¿La terminaste o, si no, para cuándo estimás terminarla y hay algo que te traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 5

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M FALLA.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste? Si no, contame para cuándo prevés terminarla o si estás trabado.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5712 ms
- Leda → Marcos: «Anoté que vas bien y que casi tenés «Programar PLC de la comprimidora». Todavía me falta saber si la terminaste o para cuándo prevés terminarla. El lunes 26 de octubre a las 10 te vuelvo a preguntar.»
- [ ] dice: que anotó lo que Marcos contó
- [ ] dice: que el lunes 26 le vuelve a preguntar, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que algo quedó guardado, programado, en cola o sin enviar
- [ ] no dice: ninguna pregunta
- **falla** [motor] hechos: esperado [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'presente'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'llega': '~2026-10-26', 'estado': 'ausente', 'sale': 'ausente'}, 'veces_sin_algo_cierto': 1, 'vencida': 'ausente', 'pregunta': 'ausente'}], real [{'jugada': 'informar_avance', 'resultado': 'anotado', 'tarea': 'PLC', 'avance': {'dijo': 'voy bien, casi la tengo'}, 'el_pedido_de_estado': 'sigue_abierto', 'vuelve_a_pedir_el_estado': {'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'veces_sin_algo_cierto': 1}]

**Paso 3.** nadie (2026-10-23 16:00)
- (Leda no manda nada)

**Paso 4.** Marcos (2026-10-26 08:30): «la tengo para el miercoles»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "estado": "retirado_sin_enviar", "motivo": "ya_respondio"}]`
- latencia: 5256 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre, pasado mañana. La fecha comprometida era el viernes 23: si terminás el miércoles, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. El aviso a Ismael está guardado para salir hoy a las 10. Ya no te voy a mandar el pedido de estado que había anunciado para hoy, porque me respondiste. El miércoles te pregunto cómo sigue.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado
- **falla** [motor] hechos: esperado [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': '~2026-10-26T10:00', 'estado': 'ausente', 'sale': 'ausente'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'ausente'}}}], real [{'jugada': 'anotar_prevision', 'resultado': 'anotado', 'tarea': 'PLC', 'prevision': '2026-10-28', 'motivo': None, 'fecha_comprometida': '2026-10-23', 'atraso_si_se_cumple_la_prevision_dias_habiles': 3, 'dependientes': ['COM'], 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'guardado_sin_enviar', 'sale': '2026-10-26T10:00:00-03:00'}, 'lo_que_sigue': {'pide_el_estado_el': {'fecha': '2026-10-28', 'estado': 'todavia_no'}}}]

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si se cumple la previsión, serán 3 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es la fecha que previste para terminar «Programar PLC de la comprimidora». Venció el viernes 23 y lleva tres días hábiles de atraso. El aviso a Ismael ya salió, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste? Si no, contame para cuándo prevés terminarla o si estás trabado.»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- **falla** [motor] no salió lo esperado: esperado {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tarea': 'PLC', 'hechos': {'numero': 1, 'necesita_respuesta': True, 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'llega': 'ya_le_llego', 'estado': 'ausente'}}}}, real [{'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}]
- **falla** [motor] salió algo de más: esperado None, real {'a': 'Marcos', 'tipo': 'pedido_de_estado', 'tareas': ['PLC'], 'el': '2026-10-28', 'hechos': {'aviso': 'pedido_de_estado', 'tarea': 'PLC', 'vence': '2026-10-23', 'estado': 'en_curso', 'numero': 1, 'dependientes': [{'tarea': 'COM', 'no_puede_arrancar_hasta_que_termine': True}], 'estado_desde': 'desconocido', 'seguimiento_por': 'prevision', 'prevision_vigente': {'fecha': '2026-10-28', 'aviso_al_referente': {'a': 'Ismael Soschinski', 'estado': 'enviado'}, 'atraso_si_se_cumple_la_prevision_dias_habiles': 3}, 'espera_algo_cierto': ['si_la_termino', 'para_cuando_la_termina', 'si_esta_trabada'], 'necesita_respuesta': True, 'atraso_dias_habiles': 3}}

