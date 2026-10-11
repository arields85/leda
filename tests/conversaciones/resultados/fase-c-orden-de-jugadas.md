# Ronda fase-c-orden-de-jugadas

- **Fecha:** 2026-10-11 14:20
- **Commit:** f0d18e6
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Cupo de la suscripción antes:** La ventana corta (de 5 horas): 0 % usado; se renueva el 11/10 a las 18:50 (en 4 h 30 min). La ventana larga (de 7 días): 0 % usado; se renueva el 18/10 a las 13:50 (en 6 d 23 h 30 min).
- **Cupo de la suscripción después:** La ventana corta (de 5 horas): 16 % usado; se renueva el 11/10 a las 18:50 (en 4 h 30 min). La ventana larga (de 7 días): 2 % usado; se renueva el 18/10 a las 13:50 (en 6 d 23 h 30 min).
- **Transcripciones:** [fase-c-orden-de-jugadas-transcripciones.md](fase-c-orden-de-jugadas-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|---|
| 35 Bloqueos encadenados (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | 5/5 | 5/5 | 2/5 |  |

## Fallas

- **35, vez 3, paso 9** [formato] formato del mensaje a Ariel: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando puedas retomar el servidor, avisame. Por ahora, no hace falta responder."`
- **35, vez 4, paso 5** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Ariel todavía no tiene la IP que necesitás. No puede configurar el servidor de CoreLabs porque falta el switch nuevo; Lucas puede destrabarlo."`
- **35, vez 4, paso 5** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando tengas la IP y puedas seguir, avisame. Por ahora no hace falta responder."`
- **35, vez 4, paso 7** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando tengas la IP y puedas seguir, avisame. Por ahora no hace falta responder."`
- **35, vez 4, paso 9** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando tengas la IP y puedas seguir, avisame. Por ahora no hace falta responder."`
- **35, vez 4, paso 11** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando tengas la IP y puedas seguir, avisame. Por ahora no hace falta responder."`
- **35, vez 4, paso 13** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando la tengas y puedas seguir, avisame. Por ahora no hace falta responder."`
- **35, vez 5, paso 19** [formato] formato del mensaje a Nahuel: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Cuando puedas seguir con los planos, avisame. Por ahora, no hace falta responder."`
- **35, vez 5, paso 21** [formato] formato del mensaje a Nahuel: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Lucas dijo que los guardamotores llegan el lun 26/10. Mariano sigue esperando eso para armar el tablero, así que los planos siguen trabados."`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 35 | 55 | 7971 | 17369 |
| **Todas** | 55 | 7971 | 17369 |

## Costo

- Llamadas a la IA: 195 (0 con el costo estimado); tokens de entrada 1126663, de salida 35778.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 195 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
