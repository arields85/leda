# Ronda fase-c-formato

- **Fecha:** 2026-10-11 17:04
- **Commit:** 28217b7
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Cupo de la suscripción antes:** La ventana corta (de 5 horas): 16 % usado; se renueva el 11/10 a las 18:50 (en 1 h 46 min). La ventana larga (de 7 días): 2 % usado; se renueva el 18/10 a las 13:50 (en 6 d 20 h 46 min).
- **Cupo de la suscripción después:** La ventana corta (de 5 horas): 100 % usado; se renueva el 11/10 a las 18:50 (en 1 h 46 min). La ventana larga (de 7 días): 16 % usado; se renueva el 18/10 a las 13:50 (en 6 d 20 h 46 min).
- **Transcripciones:** [fase-c-formato-transcripciones.md](fase-c-formato-transcripciones.md)

## Ronda cortada

**Motivo: la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50).** No empezó ninguna corrida más.

10 corrida(s) no corrieron o no terminaron; lo que la IA ya había gastado quedó en la libreta del gasto.

- **47, vez 1:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **47, vez 2:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **47, vez 3:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **47, vez 4:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **47, vez 5:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **48, vez 1:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **48, vez 2:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **48, vez 3:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **48, vez 4:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`
- **48, vez 5:** no corrió. `la suscripción llegó a su límite de uso (HTTP 429 usage_limit_reached); se renueva en 1 h 46 min (hacia el 2026-10-11 18:50)`

## Corridas inválidas

Alguna llamada a la IA chocó con el límite de uso de la suscripción (HTTP 429 usage_limit_reached): la corrida no mide nada y queda fuera de la tabla y de las fallas.

- **39, vez 1:** 5 llamada(s) con el límite de uso de la suscripción (HTTP 429 usage_limit_reached).
- **39, vez 2:** 4 llamada(s) con el límite de uso de la suscripción (HTTP 429 usage_limit_reached).
- **39, vez 3:** 2 llamada(s) con el límite de uso de la suscripción (HTTP 429 usage_limit_reached).
- **39, vez 4:** 21 llamada(s) con el límite de uso de la suscripción (HTTP 429 usage_limit_reached).
- **39, vez 5:** 14 llamada(s) con el límite de uso de la suscripción (HTTP 429 usage_limit_reached).

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|---|
| 23 Quien aprueba decide (garantias) | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | 5/5 | 5/5 | 0/5 |  |
| 35 Bloqueos encadenados (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G FALLA · C FALLA · M ok · F ok | 4/5 | 4/5 | 5/5 |  |
| 36 El bloqueo viejo (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 5/5 |  |
| 38 Delegar una tarea por chat (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 5/5 |  |

## Fallas

- **23, vez 1, paso 2** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te quedan tres entregas por revisar:"`
- **23, vez 1, paso 4** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te quedan dos entregas por revisar:"`
- **23, vez 1, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda una entrega por revisar:"`
- **23, vez 1, paso 8** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"No me queda claro si querés aprobar la entrega y dejarle a Ariel el comentario sobre los colores, o pedirle que los revise antes de aprobarla."`
- **23, vez 2, paso 2** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te quedan tres entregas por revisar:"`
- **23, vez 2, paso 4** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te quedan dos entregas por revisar:"`
- **23, vez 2, paso 4b** [formato] formato del mensaje a Marcos: esperado `"el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️"`; real `"⚠️ Falta que Lucas termine Cambiar switch industrial de la sala de servidores."`
- **23, vez 2, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda una entrega por revisar:"`
- **23, vez 2, paso 8** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"No quedó aprobada ni se le pidieron cambios a Ariel: no me queda claro si querés aprobarla y dejarle el comentario sobre los colores del gráfico, o pedirle que los revise antes de aprobarla."`
- **23, vez 3, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda una entrega por revisar:"`
- **23, vez 4, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda por revisar la entrega de Ariel:"`
- **23, vez 4, paso 9b** [servicio] el servicio de la IA no redactó un aviso al primer intento: se reintentó: esperado `null`; real `{"falla": "ReadError"}`
- **23, vez 5, paso 2** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te quedan tres entregas por revisar:"`
- **23, vez 5, paso 6** [formato] formato del mensaje a Ismael: esperado `"en un bloque con una tarea, su renglón con 📋 es el primero: todo lo de la tarea va debajo"`; real `"Te queda por revisar la entrega de Ariel:"`
- **35, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "SRV", "causa": "falta el switch nuevo"}, {"nombre": "anotar_quien_destraba", "quien": "lucas", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "SRV", "causa": "falta el switch nuevo"}, {"nombre": "decir_cuando_destraba", "tarea": "PLC", "lo_que_dice": "todavia no la tengo, estoy parado con el servidor xq falta el switch nuevo", "su_tarea_trabada": "SRV"}, {"nombre": "anotar_quien_destraba", "tarea": "SRV", "quien": "lucas"}]`
- **35, vez 5, paso 4** [garantia] efecto de más: lo que dice quien destraba: esperado `[]`; real `{"escrito": [{"tarea": "PLC", "de": "Ariel", "para_cuando": null, "ya_esta": false, "no_le_corresponde": false, "espera_la_tarea": "SRV"}], "de_mas": [{"tarea": "PLC", "de": "Ariel", "para_cuando": null, "ya_esta": false, "no_le_corresponde": false, "espera_la_tarea": "SRV"}]}`
- **35, vez 5, paso 4** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "pregunta_a_quien_destraba", "tarea": "SRV", "a": "Lucas", "estado": "guardado", "hechos": {"necesita_respuesta": true, "pregunta": "cuando_se_destraba", "responsable": "Ariel De Simone", "causa": "presente"}}, {"tipo": "novedad_de_lo_que_espera", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "hechos": {"necesita_respuesta": false, "causa": "presente", "esperando_a": [{"de": "Ariel De Simone", "tarea": "SRV"}], "novedad": {"de": "Ariel De Simone", "tarea": "SRV", "se_trabo": {"causa": "presente"}}}}]`; real `{"escrito": [{"tipo": "lo_que_dijo_quien_destraba", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "lo_que_dijo_quien_destraba", "causa": "me falta la ip del servidor de corelabs", "tarea": "PLC", "quien_destraba": "Ariel De Simone", "necesita_respuesta": false, "dice_quien_destraba": {"lo_que_dice": "todavia no la tengo, estoy parado con el servidor xq falta el switch nuevo", "su_tarea_trabada": {"causa": "falta el switch nuevo", "tarea": "SRV", "lo_destraba": "Lucas Natuche"}}}, "clave": "motor:lo_que_dijo_quien_destraba:33e90a61-8221-45a1-ab41-db50e53c6c35:d5ded5180-61fc-4e2f-bf31-7802022cee67", "outbox_id": null}, {"tipo": "novedad_de_lo_que_espera", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "novedad_de_lo_que_espera", "causa": "me falta la ip del servidor de corelabs", "tarea": "PLC", "novedad": {"de": "Ariel De Simone", "tarea": "SRV", "se_trabo": {"causa": "falta el switch nuevo"}}, "esperando_a": [{"de": "Ariel De Simone", "tarea": "SRV"}], "necesita_respuesta": false}, "clave": "motor:novedad_de_lo_que_espera:33e90a61-8221-45a1-ab41-db50e53c6c35:y349d585b-3b42-4a5c-8dfb-661792fbd25c", "outbox_id": null}, {"tipo": "pregunta_a_quien_destraba", "tarea": "SRV", "a": "Lucas", "estado": "guardado", "motivo": null, "hechos": {"aviso": "pregunta_a_quien_destraba", "causa": "falta el switch nuevo", "tarea": "SRV", "pregunta": "cuando_se_destraba", "responsable": "Ariel De Simone", "necesita_respuesta": true}, "clave": "motor:pregunta_a_quien_destraba:ffb9bc02-d0b2-41ee-9cdd-774f79d6b0c0:uc53d168d-1d46-4f57-82e2-016ef9fcad88", "outbox_id": null}], "de_mas": [{"tipo": "lo_que_dijo_quien_destraba", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "lo_que_dijo_quien_destraba", "causa": "me falta la ip del servidor de corelabs", "tarea": "PLC", "quien_destraba": "Ariel De Simone", "necesita_respuesta": false, "dice_quien_destraba": {"lo_que_dice": "todavia no la tengo, estoy parado con el servidor xq falta el switch nuevo", "su_tarea_trabada": {"causa": "falta el switch nuevo", "tarea": "SRV", "lo_destraba": "Lucas Natuche"}}}, "clave": "motor:lo_que_dijo_quien_destraba:33e90a61-8221-45a1-ab41-db50e53c6c35:d5ded5180-61fc-4e2f-bf31-7802022cee67", "outbox_id": null}]}`
- **35, vez 5, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SRV", "avisos_a_quienes_esperan": [{"aviso_a_quien_espera": {"a": "Marcos Tarquini", "tarea": "PLC", "llega": "~2026-10-20T11:10"}}]}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "se_le_pregunta_a": {"a": "Lucas Natuche", "llega": "~2026-10-20T11:10"}}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "SRV", "causa": "falta el switch nuevo", "avisos_a_quienes_esperan": [{"aviso_a_quien_espera": {"a": "Marcos Tarquini", "tarea": "PLC", "llega": "2026-10-20T11:10:00-03:00"}}], "preguntas_ya_cerradas": ["quien_destraba"]}, {"jugada": "decir_cuando_destraba", "resultado": "anotado", "tarea": "PLC", "dice_quien_destraba": {"lo_que_dice": "todavia no la tengo, estoy parado con el servidor xq falta el switch nuevo", "su_tarea_trabada": {"tarea": "SRV", "causa": "falta el switch nuevo", "lo_destraba": "Lucas Natuche"}}, "aviso_a_quien_esta_trabado": {"a": "Marcos Tarquini", "llega": "2026-10-20T11:10:00-03:00"}}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "SRV", "quien_destraba": {"integrante": "Lucas Natuche"}, "se_le_pregunta_a": {"a": "Lucas Natuche", "llega": "2026-10-20T11:10:00-03:00"}, "lo_que_sigue": {"seguimiento": "detenido_mientras_siga_trabada"}}]`
- **36, vez 5, paso 23** [servicio] el servicio de la IA no redactó un aviso al primer intento: se reintentó: esperado `null`; real `{"falla": "ReadError"}`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 23 | 40 | 7756 | 12970 |
| 35 | 55 | 7612 | 14963 |
| 36 | 55 | 6167 | 10651 |
| 38 | 75 | 6211 | 10506 |
| **Todas** | 225 | 6765 | 14963 |

## Costo

- Llamadas a la IA: 990 (0 con el costo estimado); tokens de entrada 5505771, de salida 148351.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 940 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
