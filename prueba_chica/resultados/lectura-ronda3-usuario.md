# Lectura del usuario: ronda 3 (GPT-6 sol)

Una corrida por conversación (decisión 10.3), elegida por la lectura provisional del agente: la que tiene algún detalle menor, si lo hay. Ninguna corrida tuvo fallas. Marcá cada casilla; anotá al final de cada conversación si se siente natural.

## 01 · Arranqué · vez 1

Fuente: `tests/conversaciones/01-arranque.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
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
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23", "estado": "todavia_no"}}}]`
- latencia: 6484 ms
- Leda → Marcos: «Quedó anotado que arrancaste hoy a la mañana “Programar PLC de la comprimidora”; está en curso. El viernes 23 de octubre te voy a pedir el estado.»
- [ ] dice: que quedó anotado que arrancó la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está terminada
- [ ] no dice: nada de la tarea de comunicaciones
- [ ] no dice: que la fecha cambió

**Paso 3.** nadie (2026-10-21 10:00, 2026-10-21 16:00, 2026-10-22 10:00, 2026-10-22 16:00)
- (Leda no manda nada)

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence hoy. ¿Cómo viene: la terminaste, tenés una fecha estimada o hay algo que te traba?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: que está en curso desde el martes
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que no arrancó
- [ ] no dice: que no contestó el aviso (no pedía respuesta)
- [ ] no dice: nada que pida arrancarla

- **Tu lectura:** 

## 02 · Llego el 27, el proveedor se demoró · vez 4

Fuente: `tests/conversaciones/02-nueva-prevision.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 15:40): «llego el 27, el proveedor se demoró»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "el proveedor se demoró"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-27", "motivo": "el proveedor se demoró", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 2, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T15:40:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-27", "estado": "todavia_no"}}}]`
- latencia: 9149 ms
- Leda → Marcos: «Anoté que prevés terminar «Programar PLC de la comprimidora» el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23; si se cumple tu previsión, serán dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esta tarea.

El aviso a Ismael Soschinski está guardado y saldrá hoy a las 15:40. Te pediré el estado el martes 27.»
- [ ] dice: la previsión del 27 y su motivo
- [ ] dice: que la fecha comprometida sigue siendo el 23
- [ ] dice: que Ismael se entera, sólo si el código informa que el aviso quedó guardado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: que Ismael aceptó
- [ ] no dice: que la tarea está bloqueada

**Paso 3.** Leda (2026-10-20 15:41)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora el martes 27 de octubre porque el proveedor se demoró. La fecha comprometida sigue siendo el viernes 23: si se cumple la previsión, serían 2 días hábiles de atraso. De esa tarea depende Revisar comunicaciones industriales de la comprimidora. No hace falta que respondas.»
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
- Leda, por su cuenta (vencimiento_con_prevision PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre, y sigue en curso. Tu previsión es terminarla el martes 27 porque el proveedor se demoró; si se cumple, tendrá dos días hábiles de atraso. El aviso a Ismael Soschinski ya salió. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine esta tarea.

Te pediré el estado el martes 27. No hace falta que respondas ahora.»
  - hechos: `{"aviso": "vencimiento_con_prevision", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pide_el_estado_el": {"fecha": "2026-10-27", "estado": "todavia_no"}, "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vencía hoy
- [ ] dice: que Marcos dio el 27 como previsión y que Ismael está al tanto (según el estado de su aviso)
- [ ] dice: que el martes 27 le va a pedir el estado, como algo que todavía no pasó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha cambió
- [ ] no dice: nada que trate a Marcos como si no hubiera avisado
- [ ] no dice: que va a escalar
- [ ] no dice: una pregunta

**Paso 5.** nadie (2026-10-23 16:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 6.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» sigue en curso y lleva dos días hábiles de atraso. Habías previsto terminarla hoy, martes 27 de octubre, porque el proveedor se demoró. El aviso a Ismael Soschinski ya salió.

«Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine la programación y vence el viernes 30 de octubre, dentro de tres días hábiles.

¿Cómo viene «Programar PLC de la comprimidora»: la terminaste, prevés otra fecha o está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 2}]`
- [ ] dice: que hoy es el día que Marcos previó para la tarea del PLC
- [ ] dice: que la fecha comprometida era el viernes 23 y el atraso, dos días hábiles
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que va a escalar
- [ ] no dice: un reproche

**Paso 7.** nadie (2026-10-27 16:00, 2026-10-28 10:00, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-10-30 16:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Lleva tres días hábiles de atraso y la previsión de terminarla ayer, martes 27 de octubre, ya pasó. El aviso a Ismael Soschinski ya salió. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine la programación.

¿Cómo viene «Programar PLC de la comprimidora»: la terminaste, prevés otra fecha o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» sigue en curso, lleva cuatro días hábiles de atraso y la previsión de terminarla el martes 27 ya pasó. Ismael Soschinski ya recibió el aviso sobre esa previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine la programación.

Si no respondés a este pedido, se avisará a Ismael; eso todavía no pasó. ¿Cómo viene «Programar PLC de la comprimidora»: la terminaste, prevés otra fecha o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": true, "atraso_dias_habiles": 4, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- Leda, por su cuenta (pedido_de_estado COM, 2026-10-30) → Marcos: ««Revisar comunicaciones industriales de la comprimidora» vence hoy, viernes 30 de octubre, y figura sin empezar. ¿Cómo viene: la terminaste, para cuándo prevés terminarla o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "COM", "vence": "2026-10-30", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado sobre Programar PLC de la comprimidora desde el martes 27. La tarea sigue en curso y lleva 5 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. No hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-27", "motivo": "el proveedor se demoró", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 2}, "necesita_respuesta": false, "atraso_dias_habiles": 5, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: el 28, el segundo pedido; el 29, el tercero, que avisa que se le va a avisar a Ismael
- [ ] dice: el 30, a Ismael: la falta de respuesta, con la previsión, la fecha comprometida y el atraso
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: a Ismael: que persiga o resuelva algo (es información)

- **Tu lectura:** 

## 03 · Estoy trabado, falta el repuesto · vez 1

Fuente: `tests/conversaciones/03-bloqueo.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:20): «estoy trabado, falta el repuesto»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta el repuesto"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta el repuesto", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5140 ms
- Leda → Marcos: «Quedó anotado que “Programar PLC de la comprimidora” está trabada porque falta el repuesto. No te voy a pedir el estado mientras siga trabada; el seguimiento vuelve cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
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
  - hechos: `{"aviso": "repregunta", "sobre": {"causa": "falta el repuesto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}`
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
- latencia: 5751 ms
- Leda → Marcos: «Quedó anotado que no sabés quién puede destrabar “Programar PLC de la comprimidora”. Mientras siga trabada, no te voy a pedir el estado; el seguimiento vuelve cuando me cuentes que se destrabó. ¿Preferís que alguien del equipo ayude con el bloqueo o anotar para cuándo prevés terminarla y por qué?»
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
- latencia: 8019 ms
- Leda → Marcos: «Entiendo, hay que esperar a que llegue el repuesto. Dejé sin efecto la propuesta sobre “Programar PLC de la comprimidora”; no se anotó nada nuevo. Avisame cuando se destrabe.»
- [ ] dice: que el bloqueo queda anotado como está
- [ ] dice: el próximo paso concreto: que puede avisar cuando llegue el repuesto; mientras siga trabada, Leda no le pide el estado
- [ ] no dice: otra vez las salidas
- [ ] no dice: un juicio sobre la decisión

**Paso 7.** nadie (2026-10-23 10:00, 2026-10-26 10:00, 2026-10-27 10:00)
- Leda, por su cuenta (aviso_previo COM, 2026-10-27) → Marcos: «“Revisar comunicaciones industriales de la comprimidora” vence el viernes 30 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-30", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: ningún recordatorio de la tarea del PLC mientras el bloqueo siga abierto
- [ ] dice: ningún mensaje a Ismael por el bloqueo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

- **Tu lectura:** 

## 04 · No contesta · vez 1

Fuente: `tests/conversaciones/04-sin-respuesta.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: ««Programar PLC de la comprimidora» vence el martes 27 de octubre, dentro de tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el martes 27
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** nadie (2026-10-22 16:00, 2026-10-23 10:00, 2026-10-23 16:00, 2026-10-24 10:00, 2026-10-25 10:00, 2026-10-26 10:00, 2026-10-26 16:00)
- (Leda no manda nada)

**Paso 3.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: ««Programar PLC de la comprimidora» vence hoy y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene: la terminaste, sabés para cuándo estará o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos no contestó el aviso del jueves
- [ ] no dice: que es urgente
- [ ] no dice: nada de la tarea de comunicaciones como si fuera otro recordatorio

**Paso 4.** nadie (2026-10-27 16:00)
- (Leda no manda nada)

**Paso 5.** Leda (2026-10-28 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso y venció ayer, martes 27 de octubre. Lleva un día hábil de atraso, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste, sabés para cuándo estará o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-29) → Marcos: ««Programar PLC de la comprimidora» sigue en curso y lleva dos días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Si no respondés, se avisará a Ismael Soschinski; todavía no se le avisó. ¿La terminaste, sabés para cuándo estará o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}`
- [ ] dice: que la tarea del PLC venció el martes
- [ ] dice: que si no hay novedades se le va a avisar a Ismael
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una amenaza ni un reproche
- [ ] no dice: que ya se avisó a Ismael

**Paso 8.** nadie (2026-10-29 16:00)
- (Leda no manda nada)

**Paso 9.** Leda (2026-10-30 10:00)
- Leda, por su cuenta (escalamiento PLC, 2026-10-30) → Ismael: «Marcos no respondió los tres pedidos de estado de «Programar PLC de la comprimidora» desde el martes 27 de octubre. La tarea sigue en curso y lleva tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. Es sólo para que estés al tanto; no hace falta que respondas.»
  - hechos: `{"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-27", "necesita_respuesta": false, "atraso_dias_habiles": 3, "pedidos_de_estado_sin_respuesta": 3}`
- [ ] dice: la tarea del PLC, que vencía el martes 27
- [ ] dice: el atraso, tres días hábiles
- [ ] dice: que a Marcos se le pidió el estado desde el martes y no hubo respuesta
- [ ] dice: que la tarea de comunicaciones depende de ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea está bloqueada o que Marcos no trabaja
- [ ] no dice: ninguna intención atribuida
- [ ] no dice: un atraso que no salga del código

- **Tu lectura:** 

## 05 · Varias cosas en un mensaje · vez 2

Fuente: `tests/conversaciones/05-varias-cosas.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:05): «arranque con el plc recien. y lo de las comunicaciones no llego al 30, va a ser el miercoles 4 xq espero el switch nuevo»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch nuevo"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23", "estado": "todavia_no"}}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch nuevo", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:05:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04", "estado": "todavia_no"}}}]`
- latencia: 15824 ms
- Leda → Marcos: «Anoté que empezaste “Programar PLC de la comprimidora”; quedó en curso. También anoté que preveés terminar “Revisar comunicaciones industriales de la comprimidora” el miércoles 4 de noviembre porque esperás el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple tu previsión, serían tres días hábiles de atraso.

El aviso a Ismael Soschinski está guardado, todavía no salió; sale hoy a las 10:05. Te voy a pedir el estado del PLC el viernes 23 de octubre y el de comunicaciones el miércoles 4 de noviembre.»
- [ ] dice: en una sola respuesta: los dos hechos anotados, cada uno con su tarea
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha de la tarea de comunicaciones cambió
- [ ] no dice: un inicio en la de comunicaciones o una previsión en la del PLC
- [ ] no dice: que falta algo

**Paso 3.** Leda (2026-10-20 10:06)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre porque espera el switch nuevo. La fecha comprometida sigue siendo el viernes 30 de octubre: si se cumple la previsión, serán 3 días hábiles de atraso. No hace falta que respondas.»
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
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-05", "estado": "todavia_no"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 9303 ms
- Leda → Marcos: «Anoté que ahora preveés terminar “Revisar comunicaciones industriales de la comprimidora” el jueves 5 de noviembre, no el miércoles 4. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple esa previsión, serían cuatro días hábiles de atraso. El aviso a Ismael Soschinski está guardado, todavía no salió: sale hoy a las 16:30. Te voy a pedir el estado de comunicaciones el jueves 5.

Para anotar el bloqueo de “Programar PLC de la comprimidora”, ¿qué te está trabando?»
- [ ] dice: primero: que quedó anotada la previsión del jueves 5
- [ ] dice: después, una sola pregunta: la causa del bloqueo de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: dos preguntas juntas

**Paso 5.** Marcos (2026-10-20 16:35): «falta que martin de IT me habilite el acceso a la red de planta»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- latencia: 6500 ms
- Leda → Marcos: «Anoté que “Programar PLC de la comprimidora” está trabada porque Martín de IT todavía no te habilitó el acceso a la red de planta. También quedó anotado que él puede destrabarla. Mientras siga trabada, no te voy a pedir el estado. Avisame cuando se destrabe para retomar el seguimiento.»
- [ ] dice: que quedó anotado el bloqueo, con su causa y con Martín como quien lo destraba
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Leda le escribió a Martín o lo va a seguir
- [ ] no dice: la pregunta de quién lo destraba, que Marcos ya contestó

- **Tu lectura:** 

## 06 · No, era la otra tarea · vez 2

Fuente: `tests/conversaciones/06-correccion.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, “Programar PLC de la comprimidora” vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:50): «ya arranque esta mañana 👍»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23", "estado": "todavia_no"}}}]`
- latencia: 5384 ms
- Leda → Marcos: «Quedó anotado que empezaste “Programar PLC de la comprimidora” y que está en curso. Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que se anotó el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:52): «nono era la otra, la de las comunicaciones. la del plc todavia no la empece»
- jugadas: `[{"nombre": "corregir", "corrige": "anotar_inicio", "tarea": "PLC", "tarea_correcta": "COM"}]`
- hechos: `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_inicio", "tarea": "PLC", "vuelve_a": {"estado": "asignada"}, "aplicado": {"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso"}}]`
- latencia: 9024 ms
- Leda → Marcos: «Tenés razón, me había confundido de tarea. Corregí lo anotado: “Programar PLC de la comprimidora” sigue asignada, sin empezar, y quedó anotado que empezaste “Revisar comunicaciones industriales de la comprimidora”, que está en curso. Avisame cuando arranques la del PLC.»
- [ ] dice: que la arrancada es la de comunicaciones y que la del PLC sigue sin arrancar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que las dos están en curso
- [ ] no dice: nada que reproche el error

**Paso 4.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, “Programar PLC de la comprimidora” figura asignada y sin empezar; vence hoy, viernes 23 de octubre. ¿Cómo viene: la terminaste, para cuándo la tendrías o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy y que todavía no arrancó
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que está en curso
- [ ] no dice: nada del inicio corregido como si hubiera valido

- **Tu lectura:** 

## 07 · Dejá, no importa · vez 4

Fuente: `tests/conversaciones/07-cancelar.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

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
- latencia: 3566 ms
- Leda → Marcos: «Entiendo que estás trabado con «Programar PLC de la comprimidora». ¿Qué te está trabando?»
- [ ] dice: una pregunta por lo único que falta, la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que el bloqueo quedó anotado
- [ ] no dice: nada que suene a reproche

**Paso 3.** Marcos (2026-10-20 11:34): «dejá, no importa»
- jugadas: `[{"nombre": "cancelar"}]`
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "causa_del_bloqueo", "tarea": "PLC"}, "no_se_anoto_nada": true}]`
- latencia: 5564 ms
- Leda → Marcos: «Listo, dejamos sin efecto la pregunta sobre «Programar PLC de la comprimidora» y no quedó nada anotado. Si más adelante querés registrar el bloqueo, contame qué te traba.»
- [ ] dice: que no quedó nada anotado
- [ ] dice: el próximo paso concreto: lo que sigue en el seguimiento de la tarea (cuándo le pide el estado), o que puede avisar si se traba
- [ ] no dice: otra vez la pregunta por la causa
- [ ] no dice: un juicio sobre la decisión

**Paso 4.** Leda (2026-10-20 16:00, 2026-10-21 10:00, 2026-10-22 10:00, 2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» sigue en curso y vence hoy, viernes 23 de octubre. ¿La terminaste, tenés una fecha estimada o hay algo que te esté trabando?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Marcos está trabado
- [ ] no dice: nada que retome el tema cancelado

- **Tu lectura:** 

## 08 · Cambio de tema · vez 3

Fuente: `tests/conversaciones/08-cambio-de-tema.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te recuerdo que “Programar PLC de la comprimidora” vence el viernes 23 de octubre. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:40): «uff con esto estoy trabado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": false}`
- latencia: 5228 ms
- Leda → Marcos: «Para anotar el bloqueo de “Programar PLC de la comprimidora”, me falta la causa. ¿Qué te está trabando?»
- [ ] dice: una pregunta por la causa
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 10:43): «che y lo de comunicaciones no llego al 30, necesito hasta el miercoles 4»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T10:43:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04", "estado": "todavia_no"}}}]`
- pregunta: `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`
- latencia: 9817 ms
- Leda → Marcos: «Anoté que prevés terminar “Revisar comunicaciones industriales de la comprimidora” el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre: si terminás el 4, serán tres días hábiles de atraso. El aviso a Ismael Soschinski está guardado y saldrá hoy a las 10:43. El miércoles 4 te voy a pedir el estado.

Sobre “Programar PLC de la comprimidora”, ¿qué te está trabando?»
- [ ] dice: que quedó anotada la previsión del miércoles 4 en la tarea de comunicaciones
- [ ] dice: la vuelta a la pregunta pendiente, la causa del bloqueo de la tarea del PLC, sin pedirle que repita que está trabado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un menú con las salidas (seguir, dejar para después, cancelar)
- [ ] no dice: otra pregunta además de la pendiente
- [ ] no dice: nada que trate la fecha como la causa del bloqueo
- [ ] no dice: que la tarea del PLC está bloqueada

**Paso 4.** Leda (2026-10-20 10:44)
- Leda, por su cuenta (nueva_prevision COM, 2026-10-20) → Ismael: «Marcos Tarquini prevé terminar «Revisar comunicaciones industriales de la comprimidora» el miércoles 4 de noviembre. La fecha comprometida sigue siendo el viernes 30 de octubre: si cumple esa previsión, serían 3 días hábiles de atraso. Es solo para que estés al tanto; no hace falta que respondas.»
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
- latencia: 6334 ms
- Leda → Marcos: «Anoté que “Programar PLC de la comprimidora” está trabada porque no te mandaron el programa del fabricante. No te voy a pedir el estado mientras siga trabada; retomo el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo con su causa
- [ ] dice: la pregunta de quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: salidas (Marcos todavía no dijo que nadie o que no sabe)
- [ ] no dice: que Ismael se va a enterar

- **Tu lectura:** 

## 09 · Duda: ¿de qué tarea habla? · vez 1

Fuente: `tests/conversaciones/09-duda.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:40): «hoy arranque»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 4190 ms
- Leda → Marcos: «¿Con cuál tarea arrancaste hoy: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos arrancó
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio
- [ ] no dice: tareas de otras personas

**Paso 2.** Marcos (2026-10-22 09:41): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30", "estado": "todavia_no"}}}]`
- latencia: 1695 ms
- Leda → Marcos: «Quedó anotado que arrancaste hoy con Revisar comunicaciones industriales de la comprimidora; está en curso. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: nada sobre la tarea del PLC

- **Tu lectura:** 

## 10 · Escribir en lugar de tocar un botón · vez 2

Fuente: `tests/conversaciones/10-escrito-en-lugar-de-boton.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Marcos (2026-10-22 09:30): «arranque una de las de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`
- pregunta: `{"tipo": "cual_tarea", "opciones": [{"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}], "desde_antes": false}`
- latencia: 3931 ms
- Leda → Marcos: «¿Arrancaste “Programar PLC de la comprimidora” o “Revisar comunicaciones industriales de la comprimidora”?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-22 09:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30", "estado": "todavia_no"}}}]`
- latencia: 9785 ms
- Leda → Marcos: «Quedó anotado que arrancaste “Programar PLC de la comprimidora”; está en curso. Te voy a pedir el estado el viernes 30 de octubre. No hace falta que respondas ahora.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

- **Tu lectura:** 

## 11 · Algo vencido · vez 4

Fuente: `tests/conversaciones/11-algo-vencido.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Marcos (2026-10-21 11:00): «arranque una de las dos»
- Leda → Marcos: «¿Cuál de las dos arrancaste: Programar PLC de la comprimidora o Revisar comunicaciones industriales de la comprimidora?» [botones: PLC, COM]

**Preludio.** Marcos (2026-10-21 11:02): «la del plc»
- Leda → Marcos: «Quedó anotado que arrancaste Programar PLC de la comprimidora; está en curso. Te voy a pedir el estado el viernes 30 de octubre.»

**Paso 1.** Marcos (2026-10-22 09:15): «[toca] Revisar comunicaciones industriales de la comprimidora»
- jugadas: `[{"nombre": "elegir", "opcion": "COM"}]`
- hechos: `[{"jugada": "elegir", "resultado": "sin_efecto", "motivo": "pregunta_cerrada", "eligio": {"opcion": "O2", "etiqueta": "COM", "tarea": "COM"}, "cerrada_con": {"cierre": "respondida", "cuando": "2026-10-21", "tarea": "PLC"}}]`
- latencia: 3031 ms
- Leda → Marcos: «La pregunta ya se había cerrado ayer con Programar PLC de la comprimidora. Al tocar Revisar comunicaciones industriales de la comprimidora no cambió nada. Si también arrancaste esa tarea, avisame por mensaje.»
- [ ] dice: que esa pregunta ya se contestó ayer con la tarea del PLC
- [ ] dice: que no se cambió nada
- [ ] dice: el próximo paso concreto: que puede decir qué quería sobre la de comunicaciones
- [ ] no dice: que arrancó la de comunicaciones
- [ ] no dice: nada técnico sobre botones

**Paso 2.** Marcos (2026-10-22 09:17): «ah no, era para decirte q esa tambien la arranque hoy»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30", "estado": "todavia_no"}}}]`
- latencia: 3376 ms
- Leda → Marcos: «Quedó anotado que hoy arrancaste Revisar comunicaciones industriales de la comprimidora; está en curso. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-22 17:20): «y lo de comunicaciones se me va al 4, espero el switch»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-04", "estado": "todavia_no"}}}]`
- latencia: 8124 ms
- Leda → Marcos: «Quedó anotado que prevés terminar Revisar comunicaciones industriales de la comprimidora el miércoles 4 de noviembre porque esperás el switch. La fecha comprometida sigue siendo el viernes 30 de octubre; si se cumple tu previsión, serían 3 días hábiles de atraso. El aviso a Ismael está guardado y saldrá mañana a las 9:00. Te voy a pedir el estado el miércoles 4 de noviembre, en lugar del viernes 30.»
- [ ] dice: que quedó anotada la previsión del 4
- [ ] dice: que Ismael se va a enterar a las 09:00 del viernes, el horario del equipo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael ya se enteró

**Paso 4.** Marcos (2026-10-23 08:30): «olvidate lo del 4, llego el switch, la termino para el 30»
- jugadas: `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "aviso_al_referente", "tarea": "Revisar comunicaciones industriales de la comprimidora", "a": "Ismael Soschinski", "estado": "retirado_sin_enviar", "motivo": "hay_una_prevision_mas_nueva"}]`
- latencia: 8379 ms
- Leda → Marcos: «Quedó anotado que, como llegó el switch, prevés terminar Revisar comunicaciones industriales de la comprimidora el viernes 30 de octubre, que sigue siendo la fecha comprometida. El aviso a Ismael sobre la previsión anterior se retiró sin enviarse: ya no va a salir. Te voy a pedir el estado el viernes 30, en lugar del miércoles 4 de noviembre.»
- [ ] dice: que la previsión del 4 quedó sin efecto y que la vigente es el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró de lo del 4

**Paso 5.** Leda (2026-10-23 09:00, 2026-10-23 10:00)
- (Leda no manda nada)
- [ ] dice: nada a Ismael: ni el aviso del 4 ni uno de que volvió al 30

- **Tu lectura:** 

## 12 · Algo que no está en la lista · vez 1

Fuente: `tests/conversaciones/12-fuera-de-la-lista.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, te aviso que «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 2.** Marcos (2026-10-20 10:10): «uh justo, me la podes pasar a nahuel? estoy tapado con lo de la paila»
- jugadas: `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`
- hechos: `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`
- pregunta: `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"], "desde_antes": false}`
- latencia: 7752 ms
- Leda → Marcos: «No puedo pasarle «Programar PLC de la comprimidora» a Nahuel por chat; el cambio de responsable lo decide Ismael Soschinski. ¿Querés que anote para cuándo prevés terminarla y el motivo?»
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
- hechos: `[{"jugada": "cancelar", "resultado": "cancelado", "pregunta": {"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}, "no_se_anoto_nada": true}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "tarea": "PLC", "estado": "en_curso"}]`
- latencia: 8439 ms
- Leda → Marcos: «Entendido. No anoté una previsión para «Programar PLC de la comprimidora». Ya figura en curso, así que no puedo volver a anotar que la arrancaste. Podés seguir con la tarea.»
- [ ] dice: que no anota ninguna previsión
- [ ] dice: que la tarea del PLC ya figura en curso desde el lunes 19
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que anotó un inicio nuevo
- [ ] no dice: otra vez el ofrecimiento

**Paso 4.** Marcos (2026-10-20 10:15): «otra cosa, me recordas el viernes q tengo turno con el medico?»
- jugadas: `[{"nombre": "fuera_de_la_lista", "que_pide": "Recordarle el viernes que tiene turno con el médico"}]`
- hechos: `[{"jugada": "fuera_de_la_lista", "resultado": "fuera_de_la_lista", "lo_que_puede_hacer": ["anotar que una tarea está trabada y por qué", "anotar que arrancó una tarea", "anotar para cuándo prevé terminar una tarea, y por qué", "anotar quién puede destrabar un bloqueo", "contar qué tareas tiene pendientes", "anotar que una tarea trabada ya puede seguir", "anotar cómo viene una tarea cuando la persona cuenta un avance sin un hecho cierto"], "solo_si_pregunta": {"aviso_al_administrador": {"estado": "en_cola_sin_enviar"}}}]`
- latencia: 8394 ms
- Leda → Marcos: «No puedo programar recordatorios personales por chat. Para acordarte del turno médico del viernes, agendá un aviso en tu calendario.»
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
- latencia: 6654 ms
- Leda → Marcos: «Todavía no. El aviso al administrador sobre tu pedido de recordatorio está en cola y sale enseguida. Para acordarte del turno médico, agendá un aviso en tu calendario.»
- [ ] dice: con honestidad: que se le informó al administrador para que lo analice
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que alguien se lo va a recordar
- [ ] no dice: nada más allá de eso

**Paso 6.** Marcos (2026-10-20 16:00): «listo, ya la termine a la del plc»
- jugadas: `[{"nombre": "entregar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "entregar", "resultado": "no_por_chat", "motivo": "la_entrega_todavia_no_se_recibe_por_chat", "tarea": "PLC"}]`
- latencia: 6200 ms
- Leda → Marcos: «Entiendo que terminaste «Programar PLC de la comprimidora». Todavía no puedo recibir la entrega por chat; presentala por fuera de este chat.»
- [ ] dice: con honestidad: que todavía no puede recibir la entrega por acá
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la tarea quedó entregada, en revisión o terminada
- [ ] no dice: que le avisó a Ismael

**Paso 7.** Marcos (2026-10-20 16:02): «y que mas tengo pendiente?»
- jugadas: `[{"nombre": "consultar_pendientes"}]`
- hechos: `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`
- latencia: 6092 ms
- Leda → Marcos: «Tenés «Programar PLC de la comprimidora» en curso, con vencimiento el viernes 23 de octubre, y «Revisar comunicaciones industriales de la comprimidora» asignada, con vencimiento el viernes 30 de octubre. Como me dijiste que terminaste la primera, presentá la entrega por fuera de este chat.»
- [ ] dice: sus dos tareas, con su estado y su fecha: la del PLC en curso, que vence el viernes 23; la de comunicaciones asignada, que vence el viernes 30
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: tareas de otras personas
- [ ] no dice: la del PLC como entregada

- **Tu lectura:** 

## 13 · Jev: dos tareas parecidas avisadas juntas · vez 3

Fuente: `tests/conversaciones/13-jev-dos-tareas-iguales.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo ARI, 2026-10-20) → Ariel: «Ariel, te aviso que “Integrar datos de la comprimidora en CoreLabs” vence el viernes 23 de octubre, dentro de tres días hábiles. No hace falta responder.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "ARI", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- Leda, por su cuenta (aviso_previo COM, PLC, 2026-10-20) → Marcos: ««Programar PLC de la comprimidora» y «Revisar comunicaciones industriales de la comprimidora» vencen el viernes 23 de octubre, dentro de tres días hábiles. Tené presente ese vencimiento; no hace falta que respondas.»
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
- latencia: 4088 ms
- Leda → Marcos: «¿Arrancaste con «Programar PLC de la comprimidora» o con «Revisar comunicaciones industriales de la comprimidora»?» [botones: PLC, COM]
- [ ] dice: una pregunta por cuál de las dos
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: un inicio anotado en cualquiera de ellas

**Paso 3.** Marcos (2026-10-20 10:32): «la del plc»
- jugadas: `[{"nombre": "elegir", "opcion": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "eligio": {"opcion": "O1", "etiqueta": "PLC", "tarea": "PLC"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23", "estado": "todavia_no"}}}]`
- latencia: 4605 ms
- Leda → Marcos: «Quedó anotado que arrancaste con «Programar PLC de la comprimidora». El viernes 23 de octubre te voy a pedir cómo viene.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

- **Tu lectura:** 

## 14 · Jev: dos tareas parecidas, y el estado dice cuál · vez 4

Fuente: `tests/conversaciones/14-jev-el-estado-decide.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Paso 1.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»
  - hechos: `{"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}`
- [ ] dice: la tarea del PLC
- [ ] dice: que vence el viernes 23
- [ ] dice: que no hace falta contestar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: la tarea de comunicaciones

**Paso 2.** Marcos (2026-10-20 10:45): «dale, ya arranque con la de la comprimidora»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23", "estado": "todavia_no"}}}]`
- latencia: 3758 ms
- Leda → Marcos: «Quedó anotado que empezaste «Programar PLC de la comprimidora»; está en curso. Te voy a pedir el estado el viernes 23 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea del PLC, nombrándola
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 3.** Marcos (2026-10-20 15:00): «y la otra de la comprimidora tambien la empece»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "COM"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30", "estado": "todavia_no"}}}]`
- latencia: 3283 ms
- Leda → Marcos: «También quedó anotado que empezaste «Revisar comunicaciones industriales de la comprimidora»; está en curso. Te voy a pedir el estado el viernes 30 de octubre.»
- [ ] dice: que quedó anotado el inicio de la tarea de comunicaciones
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la del PLC se volvió a arrancar

- **Tu lectura:** 

## 15 · Voy bien, la tengo casi lista · vez 5

Fuente: `tests/conversaciones/15-avance-vago.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-22 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-22) → Marcos: «La tarea Programar PLC de la comprimidora vence el martes 27 de octubre, en tres días hábiles. No hace falta que respondas.»

**Paso 1.** Leda (2026-10-27 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-27) → Marcos: «Marcos, Programar PLC de la comprimidora vence hoy, martes 27 de octubre, y sigue en curso. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. ¿Cómo viene Programar PLC de la comprimidora: la terminaste, tenés una fecha estimada o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-27 10:30): «voy bien, la tengo casi lista»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "voy bien, la tengo casi lista"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-28T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 7407 ms
- Leda → Marcos: «Anoté que vas bien y que tenés casi lista Programar PLC de la comprimidora. Mañana, miércoles 28 a las 9, te vuelvo a preguntar si la terminaste o cuándo estimás terminarla.»
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
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-28) → Marcos: «Ayer me contaste que tenías casi lista Programar PLC de la comprimidora. Vencía ayer y hoy lleva un día hábil de atraso; Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine. ¿La terminaste, tenés una fecha estimada para terminarla o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: lo que Marcos contó ayer
- [ ] dice: pide algo cierto: si la terminó, para cuándo la termina o si está trabada
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael o que va a escalar
- [ ] no dice: que Marcos no contestó
- [ ] no dice: un reproche

**Paso 5.** Marcos (2026-10-28 10:40): «todo en orden, sigo con eso»
- jugadas: `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`
- hechos: `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "todo en orden, sigo con eso"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-29T09:00:00-03:00"}, "veces_sin_algo_cierto": 2, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 7280 ms
- Leda → Marcos: «Anoté que todo está en orden y seguís con Programar PLC de la comprimidora. La fecha comprometida fue ayer y hoy lleva un día hábil de atraso. Tengo guardado un pedido de estado para mañana, jueves 29 a las 9. ¿Para qué día estimás tenerla lista?»
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "motivo": null, "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-28T10:45:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-11-03", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "estado": "retirado_sin_enviar", "motivo": "ya_respondio"}]`
- latencia: 6736 ms
- Leda → Marcos: «Anoté que estimás terminar Programar PLC de la comprimidora el martes 3 de noviembre. La fecha comprometida fue ayer: si se cumple tu previsión, serán cinco días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea.

El aviso a Ismael Soschinski está guardado para salir hoy a las 10:45; todavía no salió. El pedido de estado que te había anunciado para mañana a las 9 ya no va a salir, porque respondiste. Te pediré el estado el martes 3 de noviembre.»
- [ ] dice: que anotó que la termina el martes 3
- [ ] dice: que la fecha comprometida sigue siendo el martes 27
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta

**Paso 7.** nadie (2026-10-28 10:46, 2026-10-28 16:00, 2026-10-29 10:00, 2026-10-29 16:00, 2026-10-30 10:00, 2026-11-02 10:00, 2026-11-02 16:00)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-28) → Ismael: «Marcos Tarquini prevé terminar Programar PLC de la comprimidora el martes 3 de noviembre. La fecha comprometida era ayer, martes 27 de octubre; si se cumple la previsión, serán 5 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esa tarea. No hace falta que respondas.»
  - hechos: `{"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}`
- [ ] dice: a Ismael, sólo el aviso de la previsión; ningún escalamiento
- [ ] dice: a Marcos, nada hasta el martes 3: el pedido guardado para el jueves se omite con su motivo
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar

**Paso 8.** Leda (2026-11-03 10:00)
- Leda, por su cuenta (aviso_previo+pedido_de_estado COM, PLC, 2026-11-03) → Marcos: «Hoy, martes 3 de noviembre, es la fecha que estimaste para terminar Programar PLC de la comprimidora. La tarea lleva cinco días hábiles de atraso y el aviso a Ismael Soschinski ya salió. Revisar comunicaciones industriales de la comprimidora no puede arrancar hasta que termine y vence el viernes 6 de noviembre, en tres días hábiles.

¿Cómo viene Programar PLC de la comprimidora: la terminaste, tenés una fecha estimada o está trabada?»
  - hechos: `[{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "necesita_respuesta": true, "atraso_dias_habiles": 5}]`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: que la de comunicaciones vence el viernes 6, sin pedir respuesta por ella
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche
- [ ] no dice: dos preguntas

- **Tu lectura:** 

## 16 · Arranqué hoy, con la tarea vencida · vez 4

Fuente: `tests/conversaciones/16-vencida-sin-fecha.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas; tené presente el vencimiento.»

**Preludio.** Leda (2026-10-23 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence hoy y figura sin empezar. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene la programación: la terminaste, tenés una fecha estimada o estás trabado?»

**Paso 1.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-26) → Marcos: «Marcos, «Programar PLC de la comprimidora» venció el viernes 23 de octubre, lleva un día hábil de atraso y sigue figurando sin empezar. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste, tenés una fecha estimada o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

**Paso 2.** Marcos (2026-10-26 10:20): «arranque hoy, no pude antes»
- jugadas: `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- hechos: `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-27T09:00:00-03:00"}, "veces_sin_algo_cierto": 1, "pregunta": "fecha_de_la_tarea"}]`
- pregunta: `{"tipo": "fecha_de_la_tarea", "tarea": "PLC", "desde_antes": false}`
- latencia: 5864 ms
- Leda → Marcos: «Quedó anotado que empezaste hoy «Programar PLC de la comprimidora». Venció el viernes 23 de octubre y lleva un día hábil de atraso. Tengo guardado volver a pedirte el estado mañana a las 9. ¿Para qué día estimás tenerla lista?»
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
- hechos: `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "motivo": null, "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-26T10:25:00-03:00"}, "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-28", "estado": "todavia_no"}}}]`
- ya no sale: `[{"anuncio": "vuelve_a_pedir_el_estado", "tarea": "Programar PLC de la comprimidora", "estado": "retirado_sin_enviar", "motivo": "ya_respondio"}]`
- latencia: 5868 ms
- Leda → Marcos: «Quedó anotado que estimás terminar «Programar PLC de la comprimidora» el miércoles 28 de octubre. La fecha comprometida era el viernes 23; si se cumple tu previsión, serán tres días hábiles de atraso. «Revisar comunicaciones industriales de la comprimidora» depende de esa tarea.

El aviso a Ismael Soschinski está guardado para salir hoy a las 10:25. Ya no voy a pedirte el estado mañana a las 9, porque me respondiste. Te lo voy a pedir el miércoles 28.»
- [ ] dice: que anotó que la tiene el miércoles 28
- [ ] dice: que la fecha comprometida sigue siendo el viernes 23
- [ ] dice: lo del aviso a Ismael según su estado
- [ ] dice: que el pedido del estado que el paso 2 anunció para el martes ya no sale
- [ ] dice: el próximo paso concreto: que Leda le pide el estado el miércoles 28
- [ ] no dice: que la fecha comprometida cambió
- [ ] no dice: que Ismael ya lo sabe si el aviso no salió
- [ ] no dice: otra pregunta
- [ ] no dice: que mañana le vuelve a pedir el estado

**Paso 4.** Leda (2026-10-26 10:30)
- Leda, por su cuenta (nueva_prevision PLC, 2026-10-26) → Ismael: «Marcos Tarquini prevé terminar “Programar PLC de la comprimidora” pasado mañana, miércoles 28 de octubre. La fecha comprometida era el viernes 23; si se cumple la previsión, tendrá 3 días hábiles de atraso. De esa tarea depende “Revisar comunicaciones industriales de la comprimidora”.

Es solo para que estés al tanto; no hace falta que respondas.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-28) → Marcos: ««Programar PLC de la comprimidora» sigue en curso. Preveías terminarla hoy, miércoles 28 de octubre; venció el viernes 23 y lleva tres días hábiles de atraso. Ismael Soschinski ya recibió el aviso sobre tu previsión. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine.

¿Cómo viene la programación: la terminaste, tenés una nueva fecha estimada o estás trabado?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "enviado"}, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "necesita_respuesta": true, "atraso_dias_habiles": 3}`
- [ ] dice: que hoy es el día que Marcos dio para la tarea del PLC
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

- **Tu lectura:** 

## 17 · Llegó el switch, sigo · vez 1

Fuente: `tests/conversaciones/17-destrabar.md`. IA: `openrouter/openai/gpt-6-sol`. Automático: G ok · C ok · M ok.

**Preludio.** Leda (2026-10-20 10:00)
- Leda, por su cuenta (aviso_previo PLC, 2026-10-20) → Marcos: «Marcos, «Programar PLC de la comprimidora» vence el viernes 23 de octubre, en tres días hábiles. No hace falta que respondas a este aviso.»

**Preludio.** Marcos (2026-10-20 10:20): «estoy trabado, espero el switch»
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada porque esperás el switch. Mientras siga así, no te voy a pedir el estado; retomamos el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarlo?»

**Paso 1.** Marcos (2026-10-21 09:40): «llego el switch, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23", "estado": "todavia_no"}}}]`
- latencia: 7055 ms
- Leda → Marcos: «Quedó anotado que llegó el switch: «Programar PLC de la comprimidora» ya no está trabada por eso y sigue en curso. Te voy a pedir el estado pasado mañana, viernes 23 de octubre.»
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
- Leda, por su cuenta (pedido_de_estado PLC, 2026-10-23) → Marcos: ««Programar PLC de la comprimidora» vence hoy, viernes 23 de octubre, y sigue en curso. «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿Cómo viene: la terminaste, sabés para cuándo estará o está trabada?»
  - hechos: `{"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}`
- [ ] dice: que la tarea del PLC vence hoy
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: nada del bloqueo, que ya se cerró

**Paso 4.** Marcos (2026-10-23 10:20): «se quemo la fuente, otra vez parado»
- jugadas: `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`
- hechos: `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "se quemo la fuente", "pregunta": "quien_destraba", "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- pregunta: `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- latencia: 5923 ms
- Leda → Marcos: «Quedó anotado que «Programar PLC de la comprimidora» está trabada otra vez porque se quemó la fuente. Mientras siga así, no te voy a pedir el estado; retomamos el seguimiento cuando me cuentes que se destrabó. ¿Quién puede destrabarla?»
- [ ] dice: que quedó anotado el bloqueo y su causa
- [ ] dice: una sola pregunta: quién lo puede destrabar
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que Ismael se enteró o se va a enterar
- [ ] no dice: el bloqueo anterior

**Paso 5.** Marcos (2026-10-23 11:30): «ya cambie la fuente, sigo»
- jugadas: `[{"nombre": "destrabar", "tarea": "PLC"}]`
- hechos: `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- latencia: 6320 ms
- Leda → Marcos: «Quedó anotado que cambiaste la fuente: «Programar PLC de la comprimidora» ya no está trabada por eso y sigue en curso. El lunes 26 de octubre a las 9:00 te voy a pedir el estado.»
- [ ] dice: que quedó anotado que la tarea se destrabó y sigue en curso
- [ ] dice: que el lunes le vuelve a pedir el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: una fecha para terminarla
- [ ] no dice: que va a avisar a Ismael o que se escala
- [ ] no dice: un reproche
- [ ] no dice: otra pregunta

**Paso 6.** Leda (2026-10-26 10:00)
- Leda, por su cuenta (repregunta_de_estado PLC, 2026-10-26) → Marcos: «El viernes me contaste que cambiaste la fuente y seguías con «Programar PLC de la comprimidora». Sigue en curso, con un día hábil de atraso, y «Revisar comunicaciones industriales de la comprimidora» no puede arrancar hasta que termine. ¿La terminaste, sabés para cuándo estará o está trabada?»
  - hechos: `{"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-23", "dijo": "ya cambie la fuente, sigo", "jugada": "destrabar"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}`
- [ ] dice: que la tarea del PLC venció el viernes 23
- [ ] dice: lo que Marcos contó (que se destrabó)
- [ ] dice: pide el estado
- [ ] dice: el próximo paso concreto, al final y una sola vez: lo que va a hacer Leda y cuándo (si un hecho lo dice), lo que puede hacer la persona, o que no queda nada pendiente y lo que sigue; en un aviso que no pide respuesta, que no hace falta contestar
- [ ] no dice: que va a avisar a Ismael
- [ ] no dice: un reproche

- **Tu lectura:** 
