# Transcripciones de la ronda e3-6-verde-18-sol

Para leer contra lo que cada paso dice y no dice (decisión 10.3). Cada casilla la marca quien lee.

## 18 · Habla de lo que pasa en el mundo, no de la cocina · vez 1

Fuente: `tests/conversaciones/18-habla-del-mundo.md`. Motor: `leda.motor`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿La terminaste, tenés una fecha prevista para terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5151 ms
- Leda → Marcos: «Anoté que vas bien y que casi tenés “Programar PLC de la comprimidora”. Todavía falta saber si la terminaste, cuándo estimás terminarla o si estás trabado. El lunes 26 de octubre a las 10 te vuelvo a pedir ese dato.»
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
- latencia: 6308 ms
- Leda → Marcos: «Anoté que prevés terminar “Programar PLC de la comprimidora” el miércoles 28 de octubre, pasado mañana. La fecha comprometida era el viernes 23: si se cumple tu previsión, serán tres días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” depende de que la termines. Ismael Soschinski se enterará hoy a las 10. El miércoles te pediré el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23: si cumple esa previsión, la tarea tendrá 3 días hábiles de atraso. De ella depende «Revisar comunicaciones industriales de la comprimidora». No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Marcos, hoy es la fecha que preveías para terminar “Programar PLC de la comprimidora”. Lleva tres días hábiles de atraso e Ismael Soschinski ya conoce tu previsión. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿La terminaste, para cuándo prevés terminarla o estás trabado?»
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «La tarea “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. Tené presente esa fecha; no hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Hoy vence “Programar PLC de la comprimidora”. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5562 ms
- Leda → Marcos: «Anoté que vas bien y casi la tenés con “Programar PLC de la comprimidora”. Todavía queda pendiente saber si la terminaste o, si no, para cuándo prevés terminarla y si estás trabado. El lunes 26 de octubre a las 10:00 te vuelvo a pedir el estado.»
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
- latencia: 6981 ms
- Leda → Marcos: «Anoté que prevés terminar “Programar PLC de la comprimidora” pasado mañana, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23; si terminás el miércoles, serán tres días hábiles de atraso. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. Ismael Soschinski se enterará de tu previsión hoy a las 10:00. Pasado mañana te pediré el estado.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23 de octubre; si se cumple la previsión, la tarea tendrá 3 días hábiles de atraso. De ella depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Hoy es el día para el que preveías terminar “Programar PLC de la comprimidora”. Lleva tres días hábiles de atraso respecto de la fecha comprometida, e Ismael Soschinski ya conoce tu previsión. “Revisar comunicaciones industriales de la comprimidora” no puede arrancar hasta que la termines. ¿La terminaste o, si no, para cuándo prevés terminarla y si estás trabado?»
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y estás trabado para avanzar?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 4831 ms
- Leda → Marcos: «Anoté que vas bien y que casi tenés «Programar PLC de la comprimidora». Todavía falta saber si la terminaste o, si no, para cuándo prevés terminarla y si estás trabado. Te vuelvo a consultar el lunes 26 de octubre a las 10.»
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
- latencia: 7089 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28. La fecha comprometida sigue siendo el viernes 23: si se cumple tu previsión, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea. Ismael Soschinski se enterará hoy a las 10. Te voy a pedir el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si se cumple su previsión, serían 3 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora sigue abierta y depende de esa tarea. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» lleva tres días hábiles de atraso y preveías terminarla hoy. Ismael ya está al tanto de esa previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Ya la terminaste o, si no, para cuándo prevés terminarla y estás trabado para avanzar?»
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo calculás terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5824 ms
- Leda → Marcos: «Anoté que venís bien y casi la tenés con «Programar PLC de la comprimidora». Todavía necesito saber si ya la terminaste, para cuándo calculás terminarla o si estás trabado. Te vuelvo a consultar el lunes 26 de octubre a las 10.»
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
- latencia: 5650 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23: si se cumple tu previsión, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski se enterará hoy a las 10. Te pediré el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora pasado mañana, miércoles 28 de octubre. La fecha comprometida sigue siendo el viernes 23 de octubre: si se cumple la previsión, serán 3 días hábiles de atraso. De esta tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» tenía fecha comprometida el viernes 23 y lleva tres días hábiles de atraso. Preveías terminarla hoy e Ismael Soschinski ya está al tanto. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿Ya la terminaste, para cuándo prevés terminarla o estás trabado?»
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
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo estimás terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-23 11:00): «voy bien, casi la tengo»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, casi la tengo"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, casi la tengo"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"llega": "2026-10-26T10:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 5531 ms
- Leda → Marcos: «Anoté que me contaste que vas bien y casi tenés «Programar PLC de la comprimidora». Sigo pendiente de saber si la terminaste, para cuándo estimás terminarla o si estás trabado. Te vuelvo a consultar el lunes 26 de octubre a las 10:00.»
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
- latencia: 5603 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el miércoles 28, pasado mañana. La fecha comprometida sigue siendo el viernes 23; si terminás el miércoles, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de que la termines. Ismael Soschinski recibirá el aviso hoy a las 10:00. Te voy a pedir el estado el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: que Ismael se va a enterar hoy, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar
- [ ] no dice: que Ismael ya se enteró
- [ ] no dice: que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto" (si lo dice, como lo que va a pasar: que hoy no le vuelve a preguntar)
- [ ] no dice: que hoy le vuelve a pedir el estado

**Paso 5.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar «Programar PLC de la comprimidora» pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23 de octubre; si cumple esa previsión, serán 3 días hábiles de atraso. De esa tarea depende «Revisar comunicaciones industriales de la comprimidora». No hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: «Hoy, miércoles 28, es la fecha que previste para terminar «Programar PLC de la comprimidora». Lleva tres días hábiles de atraso e Ismael Soschinski ya recibió el aviso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que la termines. ¿La terminaste, para cuándo estimás terminarla o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "estado_desde": "desconocido", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "llega": "ya_le_llego"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: si nombra a Ismael, como alguien que ya está al tanto
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que un aviso salió, se envió o estaba guardado
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

