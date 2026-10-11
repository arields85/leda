# Ronda fase-c-apodos-regresion-b

- **Fecha:** 2026-10-11 04:20
- **Commit:** 7d20bb2
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Cupo de la suscripción antes:** La ventana corta (de 5 horas): 22 % usado; se renueva el 11/10 a las 05:58 (en 1 h 39 min). La ventana larga (de 7 días): 3 % usado; se renueva el 18/10 a las 00:58 (en 6 d 20 h 39 min).
- **Cupo de la suscripción después:** La ventana corta (de 5 horas): 74 % usado; se renueva el 11/10 a las 05:58 (en 1 h 39 min). La ventana larga (de 7 días): 12 % usado; se renueva el 18/10 a las 00:58 (en 6 d 20 h 39 min).
- **Transcripciones:** [fase-c-apodos-regresion-b-transcripciones.md](fase-c-apodos-regresion-b-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|---|
| 23 Quien aprueba decide (garantias) | G FALLA · C FALLA · M ok · F FALLA | G FALLA · C FALLA · M ok · F FALLA | G FALLA · C FALLA · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G FALLA · C FALLA · M ok · F FALLA | 1/5 | 1/5 | 0/5 |  |
| 38 Delegar una tarea por chat (garantias) | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C FALLA · M ok · F FALLA | G ok · C ok · M ok · F FALLA | 5/5 | 4/5 | 0/5 |  |
| 39 El encargado pasa una tarea de su gente, la revisión sigue a quien era la tarea y un pase sin respuesta (garantias) | G ok · C FALLA · M ok · F FALLA | G ok · C FALLA · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C FALLA · M ok · F FALLA | G ok · C FALLA · M ok · F FALLA | 5/5 | 1/5 | 0/5 |  |

## Fallas

- **23, vez 1, paso 4** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Todavía no queda terminada: falta que Lucas termine el cambio del switch industrial de la sala de servidores. Cuando eso pase, se cerrará sin otra aprobación y Marcos y vos serán avisados."`
- **23, vez 1, paso 6** [formato] formato del mensaje a Ismael: esperado `"el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️"`; real `"Podés abrirla con el botón «Ver Dashboard de lotes en CoreLabs» o escribirme que querés verla."`
- **23, vez 1, paso 6** [formato] formato del mensaje a Ismael: esperado `"el nombre completo de una tarea, una sola vez por mensaje"`; real `"Dashboard de lotes en CoreLabs"`
- **23, vez 1, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda por revisar la entrega de Ariel:"`
- **23, vez 1, paso 8** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"Podés elegir Aprobar, si es un comentario para Ariel y la tarea queda aprobada, o Pedir cambios, si querés que revise los colores antes de aprobarla. También podés escribir tu decisión."`
- **23, vez 1, paso 12** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "TAB", "lo_descrito_cubre": ["C1"], "puede_traer": ["el_texto_cubre", "lo_descrito_cubre"]}]`; real `[{"nombre": "guardar_para_la_entrega", "tarea": "TAB"}]`
- **23, vez 1, paso 12** [garantia] efecto de más: archivo dicho de una tarea: esperado `[]`; real `{"escrito": [{"tarea": "TAB"}], "de_mas": [{"tarea": "TAB"}]}`
- **23, vez 1, paso 12** [comprension] botones: esperado `["Confirmar"]`; real `[]`
- **23, vez 1, paso 12** [comprension] la pregunta de la respuesta: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **23, vez 1, paso 12** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "para_confirmar", "tarea": "TAB", "pregunta": "confirmar_la_entrega", "le_falta_del_criterio": "ausente", "ejemplo": "ausente", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ahi va el diagrama del tablero", "describe": ["El tablero de la máquina 3 queda cableado según su diagrama y pasa la prueba de continuidad y de aislación"]}, {"pieza": "P2", "es": "una_foto"}]}]`; real `[{"jugada": "guardar_para_la_entrega", "resultado": "anotado", "tarea": "TAB", "para_cuando_la_entregue": [{"es": "una_foto"}], "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- **23, vez 1, paso 12** [comprension] pregunta abierta después: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **23, vez 2, paso 4** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Todavía no se cierra: falta que Lucas termine de cambiar el switch industrial de la sala de servidores. Cuando eso pase, quedará terminada sin otra aprobación y Marcos y vos serán avisados."`
- **23, vez 2, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda una entrega por revisar:"`
- **23, vez 2, paso 8** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"No quedó tomada ninguna decisión: no sé si aprobás la entrega con el comentario sobre los colores o si querés pedirle a Ariel que los cambie antes de aprobarla."`
- **23, vez 2, paso 12** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "TAB", "lo_descrito_cubre": ["C1"], "puede_traer": ["el_texto_cubre", "lo_descrito_cubre"]}]`; real `[{"nombre": "guardar_para_la_entrega", "tarea": "TAB"}]`
- **23, vez 2, paso 12** [garantia] efecto de más: archivo dicho de una tarea: esperado `[]`; real `{"escrito": [{"tarea": "TAB"}], "de_mas": [{"tarea": "TAB"}]}`
- **23, vez 2, paso 12** [comprension] botones: esperado `["Confirmar"]`; real `[]`
- **23, vez 2, paso 12** [comprension] la pregunta de la respuesta: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **23, vez 2, paso 12** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "para_confirmar", "tarea": "TAB", "pregunta": "confirmar_la_entrega", "le_falta_del_criterio": "ausente", "ejemplo": "ausente", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ahi va el diagrama del tablero", "describe": ["El tablero de la máquina 3 queda cableado según su diagrama y pasa la prueba de continuidad y de aislación"]}, {"pieza": "P2", "es": "una_foto"}]}]`; real `[{"jugada": "guardar_para_la_entrega", "resultado": "anotado", "tarea": "TAB", "para_cuando_la_entregue": [{"es": "una_foto"}], "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- **23, vez 2, paso 12** [comprension] pregunta abierta después: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **23, vez 3, paso 6** [formato] formato del mensaje a Ismael: esperado `"el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️"`; real `"Podés tocar «Ver Dashboard de lotes en CoreLabs» o escribir que querés revisarla."`
- **23, vez 3, paso 6** [formato] formato del mensaje a Ismael: esperado `"el nombre completo de una tarea, una sola vez por mensaje"`; real `"Dashboard de lotes en CoreLabs"`
- **23, vez 3, paso 8** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"Decís que aprobás la entrega de Ariel, pero también le pedís que revise los colores del gráfico. Todavía no anoté ninguna de las dos decisiones."`
- **23, vez 3, paso 12** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "TAB", "lo_descrito_cubre": ["C1"], "puede_traer": ["el_texto_cubre", "lo_descrito_cubre"]}]`; real `[{"nombre": "guardar_para_la_entrega", "tarea": "TAB"}]`
- **23, vez 3, paso 12** [garantia] efecto de más: archivo dicho de una tarea: esperado `[]`; real `{"escrito": [{"tarea": "TAB"}], "de_mas": [{"tarea": "TAB"}]}`
- **23, vez 3, paso 12** [comprension] botones: esperado `["Confirmar"]`; real `[]`
- **23, vez 3, paso 12** [comprension] la pregunta de la respuesta: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **23, vez 3, paso 12** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "para_confirmar", "tarea": "TAB", "pregunta": "confirmar_la_entrega", "le_falta_del_criterio": "ausente", "ejemplo": "ausente", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ahi va el diagrama del tablero", "describe": ["El tablero de la máquina 3 queda cableado según su diagrama y pasa la prueba de continuidad y de aislación"]}, {"pieza": "P2", "es": "una_foto"}]}]`; real `[{"jugada": "guardar_para_la_entrega", "resultado": "anotado", "tarea": "TAB", "para_cuando_la_entregue": [{"es": "una_foto"}], "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- **23, vez 3, paso 12** [comprension] pregunta abierta después: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **23, vez 4, paso 6** [formato] formato del mensaje a Ismael: esperado `"el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️"`; real `"Podés abrirla con «Ver Dashboard de lotes en CoreLabs» o escribirme."`
- **23, vez 4, paso 6** [formato] formato del mensaje a Ismael: esperado `"el nombre completo de una tarea, una sola vez por mensaje"`; real `"Dashboard de lotes en CoreLabs"`
- **23, vez 4, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"También te queda por revisar la entrega de Ariel:"`
- **23, vez 4, paso 8** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"Podés elegir Aprobar, si es un comentario para que Ariel lo tenga en cuenta, o Pedir cambios, si querés que revise los colores antes de aprobar. También podés escribirme tu decisión."`
- **23, vez 4, paso 11** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Ya terminó el cambio del switch industrial de la sala de servidores. Con la aprobación que tenía desde el lun 26/10, esta tarea quedó terminada."`
- **23, vez 5, paso 2** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te quedan estas entregas por revisar:"`
- **23, vez 5, paso 4** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te quedan dos entregas por revisar:"`
- **23, vez 5, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda una entrega por revisar:"`
- **23, vez 5, paso 7** [formato] formato del mensaje a Mariano: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando tengas el diagrama, subilo y volvé a entregar la tarea. No hace falta responder a este aviso."`
- **23, vez 5, paso 8** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"Entendí que aprobás la entrega de Ariel, pero también que querés que revise los colores del gráfico de lotes. Todavía no quedó tomada ninguna decisión."`
- **23, vez 5, paso 12** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "TAB", "lo_descrito_cubre": ["C1"], "puede_traer": ["el_texto_cubre", "lo_descrito_cubre"]}]`; real `[{"nombre": "guardar_para_la_entrega", "tarea": "TAB"}]`
- **23, vez 5, paso 12** [garantia] efecto de más: archivo dicho de una tarea: esperado `[]`; real `{"escrito": [{"tarea": "TAB"}], "de_mas": [{"tarea": "TAB"}]}`
- **23, vez 5, paso 12** [comprension] botones: esperado `["Confirmar"]`; real `[]`
- **23, vez 5, paso 12** [comprension] la pregunta de la respuesta: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **23, vez 5, paso 12** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "para_confirmar", "tarea": "TAB", "pregunta": "confirmar_la_entrega", "le_falta_del_criterio": "ausente", "ejemplo": "ausente", "entrega": [{"pieza": "P1", "es": "lo_que_escribio", "dice": "ahi va el diagrama del tablero", "describe": ["El tablero de la máquina 3 queda cableado según su diagrama y pasa la prueba de continuidad y de aislación"]}, {"pieza": "P2", "es": "una_foto"}]}]`; real `[{"jugada": "guardar_para_la_entrega", "resultado": "anotado", "tarea": "TAB", "para_cuando_la_entregue": [{"es": "una_foto"}], "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-30"}}}]`
- **23, vez 5, paso 12** [comprension] pregunta abierta después: esperado `{"tipo": "confirmar_la_entrega", "tarea": "TAB"}`; real `null`
- **38, vez 1, paso 7** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Todavía está a tu cargo. Si confirmás, Martín será consultado primero para decidir si pasa a Lucas. Si lo aprueba, Lucas será consultado para ver si la toma. Hasta que Lucas diga que sí, sigue a tu cargo."`
- **38, vez 1, paso 9** [formato] formato del mensaje a Martin: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Aprobás el pase a Lucas? Aprobar el pase / No aprobarlo."`
- **38, vez 2, paso 7** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora sigue a tu cargo. Si confirmás el pase, le voy a preguntar primero a Martín si lo aprueba y, si dice que sí, a Lucas si la toma. Hasta que Lucas acepte, sigue con vos."`
- **38, vez 2, paso 8** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Quedó pedido el pase a Lucas. Primero tiene que aprobarlo Martín y después Lucas tiene que aceptar la tarea. Hasta entonces, sigue a tu cargo."`
- **38, vez 2, paso 20** [formato] formato del mensaje a Nahuel: esperado `"ningún renglón de más de 140 caracteres"`; real `"Marcos puede recibirla, pero todavía no cambió de manos. Si confirmás, le voy a preguntar si la toma. Hasta que diga que sí, sigue a tu cargo."`
- **38, vez 3, paso 7** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Si confirmás el pase, le voy a preguntar primero a Martín si lo aprueba. Si lo aprueba, le voy a preguntar a Lucas si la toma. Hasta que Lucas diga que sí, la tarea sigue con vos."`
- **38, vez 4, paso 7** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"La tenés vos. Si confirmás el pase, le voy a preguntar primero a Martín si lo aprueba y después a Lucas si la toma. Hasta que Lucas diga que sí, sigue a tu cargo."`
- **38, vez 4, paso 23** [comprension] jugadas: esperado `[{"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": false, "puede_traer": ["por_que"]}]`; real `[{"nombre": "contestar_el_pase", "tarea": "SEN", "acepta": false, "por_que": "nahuel la conoce mejor"}]`
- **38, vez 5, paso 7** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora sigue a tu cargo. Si confirmás, le preguntaré primero a Martín si aprueba el pase a Lucas y después a Lucas si la toma. Sólo pasará a ser suya cuando diga que sí."`
- **39, vez 1, paso 1** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Si confirmás el pase a Lucas, primero le preguntaré a Martín si lo aprueba y después a Lucas si la toma. Hasta que Lucas diga que sí, seguirá con Nahuel."`
- **39, vez 1, paso 13** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Si confirmás, la entrega quedará aprobada por vos y, si no falta nada más, la tarea quedará terminada. Podés tocar Confirmar, escribirlo o corregir algo."`
- **39, vez 1, paso 15** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"La tarea sigue a tu cargo. Si confirmás el pase a Lucas, Martín será consultado primero. Si lo aprueba, le preguntaré a Lucas si la toma. Hasta que Lucas acepte, seguirá a tu cargo."`
- **39, vez 1, paso 20** [comprension] jugadas: esperado `[{"nombre": "contestar_el_pase", "acepta": true}]`; real `[]`
- **39, vez 1, paso 20** [comprension] hechos: esperado `[{"jugada": "contestar_el_pase", "resultado": "no_se_puede", "motivo": "no_hay_un_pase"}]`; real `[]`
- **39, vez 2, paso 1** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora sigue a cargo de Nahuel. Si confirmás el pase a Lucas, primero se le preguntará a Martín si lo aprueba y después a Lucas si la toma. Hasta que Lucas diga que sí, seguirá con Nahuel."`
- **39, vez 2, paso 15** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora la tenés vos. Si confirmás el pase a Lucas, primero le preguntaré a Martín si lo aprueba. Si dice que sí, le preguntaré a Lucas si la toma. Hasta que Lucas la tome, seguirá a tu cargo."`
- **39, vez 2, paso 20** [comprension] jugadas: esperado `[{"nombre": "contestar_el_pase", "acepta": true}]`; real `[]`
- **39, vez 2, paso 20** [comprension] hechos: esperado `[{"jugada": "contestar_el_pase", "resultado": "no_se_puede", "motivo": "no_hay_un_pase"}]`; real `[]`
- **39, vez 2, paso 21** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora la tiene Nahuel. Si confirmás, pasará a estar a tu cargo con la misma fecha y lo que ya se pide para terminarla. Nahuel será avisado del cambio."`
- **39, vez 3, paso 1** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"La tiene Nahuel. Si confirmás el pase a Lucas, primero le preguntaré a Martín si lo aprueba y después a Lucas si la toma. Hasta que Lucas diga que sí, seguirá con Nahuel."`
- **39, vez 3, paso 1** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Confirmás el pase a Lucas? Podés tocar Confirmar o escribirme."`
- **39, vez 3, paso 15** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora sigue a tu cargo. Si confirmás que querés pasársela a Lucas, Martín decidirá si puede pasar y después le preguntaré a Lucas si la toma. Hasta que Lucas diga que sí, seguirá a tu cargo."`
- **39, vez 3, paso 21** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora la tiene Nahuel. Si confirmás, pasa a estar a tu cargo con la misma fecha y lo que pide para terminarla. Nahuel será informado de que la tomaste."`
- **39, vez 4, paso 1** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Si confirmás el pase, Martín será consultado primero. Si lo aprueba, Lucas será consultado para ver si la toma. Hasta que Lucas acepte, la tarea sigue con Nahuel."`
- **39, vez 4, paso 15** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora sigue a tu cargo. Si confirmás el pase a Lucas, Martín decidirá si lo aprueba. Después le preguntaré a Lucas si la toma; hasta que diga que sí, seguirá a tu cargo."`
- **39, vez 4, paso 18** [formato] formato del mensaje a Martin: esperado `"ningún renglón de más de 140 caracteres"`; real `"Si no respondés, mañana se cierra el pedido y la tarea sigue con Marcos. Podés elegir «Aprobar el pase» o «No aprobarlo», o responder escribiendo."`
- **39, vez 4, paso 19** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Podés pedirme que se la pase a otra persona. No hace falta que respondas."`
- **39, vez 4, paso 20** [comprension] jugadas: esperado `[{"nombre": "contestar_el_pase", "acepta": true}]`; real `[]`
- **39, vez 4, paso 20** [comprension] hechos: esperado `[{"jugada": "contestar_el_pase", "resultado": "no_se_puede", "motivo": "no_hay_un_pase"}]`; real `[]`
- **39, vez 4, paso 21** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora la tiene Nahuel. Si confirmás, pasará a tu cargo con el mismo vencimiento y lo mismo que se pide para terminarla. Nahuel será informado."`
- **39, vez 5, paso 1** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora sigue con Nahuel. Si confirmás, Martín será consultado primero para decidir el pase. Si lo aprueba, Lucas será consultado para ver si la toma. Hasta que Lucas acepte, la tarea seguirá con Nahuel."`
- **39, vez 5, paso 15** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora la tenés vos. Si confirmás el pase a Lucas, Martín decidirá primero si lo aprueba; después le preguntaré a Lucas si la toma. Hasta que Lucas la tome, seguirá a tu cargo."`
- **39, vez 5, paso 20** [comprension] jugadas: esperado `[{"nombre": "contestar_el_pase", "acepta": true}]`; real `[]`
- **39, vez 5, paso 20** [comprension] hechos: esperado `[{"jugada": "contestar_el_pase", "resultado": "no_se_puede", "motivo": "no_hay_un_pase"}]`; real `[]`
- **39, vez 5, paso 21** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Por ahora la tiene Nahuel. Si confirmás que la tomás vos, pasará a ser tuya con el mismo vencimiento y lo que pide para terminarla. Nahuel será avisado de que la tomaste."`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 23 | 40 | 7620 | 13183 |
| 38 | 75 | 5747 | 9794 |
| 39 | 70 | 6240 | 46718 |
| **Todas** | 185 | 6131 | 46718 |

## Costo

- Llamadas a la IA: 561 (0 con el costo estimado); tokens de entrada 3306792, de salida 87120.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 560 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
