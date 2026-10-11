# Ronda fase-c-formato-2

- **Fecha:** 2026-10-11 18:05
- **Commit:** 1b7a48e
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Cupo de la suscripción antes:** La ventana corta (de 5 horas): 0 % usado; se renueva el 11/10 a las 22:57 (en 4 h 52 min). La ventana larga (de 7 días): 32 % usado; se renueva el 18/10 a las 00:58 (en 6 d 6 h 54 min).
- **Cupo de la suscripción después:** La ventana corta (de 5 horas): 45 % usado; se renueva el 11/10 a las 22:57 (en 4 h 52 min). La ventana larga (de 7 días): 39 % usado; se renueva el 18/10 a las 00:58 (en 6 d 6 h 54 min).
- **Transcripciones:** [fase-c-formato-2-transcripciones.md](fase-c-formato-2-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|---|
| 35 Bloqueos encadenados (garantias) | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 4/5 |  |
| 39 El encargado pasa una tarea de su gente, la revisión sigue a quien era la tarea y un pase sin respuesta (garantias) | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 4/5 |  |
| 47 Los apodos (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 5/5 |  |
| 48 El sector se queda sin encargado mientras se espera su decisión (garantias) | G ok · C ok · M ok · F ok | G ok · C FALLA · M ok · F ok | G ok · C FALLA · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 3/5 | 5/5 |  |

## Fallas

- **35, vez 1, paso 1** [formato] formato del mensaje a Marcos: esperado `"la pregunta, una sola y en el último renglón"`; real `"¿Quién puede conseguir la IP para destrabarla?"`
- **35, vez 4, paso 17** [servicio] el servicio de la IA no redactó un aviso al primer intento: se reintentó: esperado `null`; real `{"falla": "RemoteProtocolError"}`
- **39, vez 1, paso 1** [formato] formato del mensaje a Marcos: esperado `"la pregunta, una sola y en el último renglón"`; real `"¿Confirmás el pase a Lucas?"`
- **39, vez 2, paso 7** [servicio] el servicio de la IA no redactó un aviso al primer intento: se reintentó: esperado `null`; real `{"falla": "PlazoAgotado"}`
- **48, vez 2, paso 8** [servicio] el servicio de la IA no redactó un aviso al primer intento: se reintentó: esperado `null`; real `{"falla": "ReadError"}`
- **48, vez 2, paso 10** [comprension] jugadas: esperado `[{"nombre": "pedir_el_detalle", "como_la_nombra": "switch"}]`; real `[]`
- **48, vez 2, paso 10** [comprension] hechos: esperado `[{"jugada": "pedir_el_detalle", "resultado": "no_se_puede", "motivo": "sin_encargado_del_sector", "tarea": "SW"}]`; real `[]`
- **48, vez 3, paso 10** [comprension] jugadas: esperado `[{"nombre": "pedir_el_detalle", "como_la_nombra": "switch"}]`; real `[]`
- **48, vez 3, paso 10** [comprension] hechos: esperado `[{"jugada": "pedir_el_detalle", "resultado": "no_se_puede", "motivo": "sin_encargado_del_sector", "tarea": "SW"}]`; real `[]`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 35 | 55 | 8056 | 21046 |
| 39 | 70 | 6195 | 11161 |
| 47 | 55 | 6193 | 11853 |
| 48 | 30 | 6704 | 16884 |
| **Todas** | 210 | 6738 | 21046 |

## Costo

- Llamadas a la IA: 555 (0 con el costo estimado); tokens de entrada 3336727, de salida 90549.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 550 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
