# Ronda motivo-repeticion-01-07

- **Fecha:** 2026-10-08 01:22
- **Commit:** 4cbfbef
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Transcripciones:** [motivo-repeticion-01-07-transcripciones.md](motivo-repeticion-01-07-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 3/5 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | 5/5 | 5/5 | 0/5 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 5/5 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 4/5 |  |
| 06 No, era la otra tarea (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 4/5 |  |
| 07 Dejá, no importa (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 5/5 | 5/5 | 5/5 |  |

## Fallas

- **01, vez 3, paso 4** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿La terminaste? Si no, contame para cuándo la terminás o si estás trabado."`
- **01, vez 4, paso 2** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"Te voy a preguntar cómo viene el vie 23/10. No hace falta responder."`
- **02, vez 1, paso 2** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea."`
- **02, vez 1, paso 4** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea."`
- **02, vez 1, paso 6** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Dijiste que la terminarías hoy, pero sigue en curso y lleva 2 días hábiles de atraso. Ismael ya fue notificado de la fecha que diste y del motivo."`
- **02, vez 1, paso 7** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Venció el vie 23/10 y lleva 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termine."`
- **02, vez 2, paso 2** [formato] formato del mensaje a Marcos: esperado `"el nombre completo de una tarea, en un renglón que empieza con 📋 o 🗓️"`; real `"⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. Revisar comunicaciones industriales de la comprimidora depende de esta tarea."`
- **02, vez 2, paso 6** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Terminaste la programación? Si no, ¿para cuándo la terminás o qué te está trabando?"`
- **02, vez 2, paso 7** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Terminaste la programación? Si no, contame para cuándo la terminás o qué te está trabando."`
- **02, vez 2, paso 7** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Terminaste la programación? Si no, contame para cuándo la terminás o qué te está trabando."`
- **02, vez 2, paso 7** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"Marcos había dicho que la terminaría el mar 27/10 porque el proveedor se demoró. Sigue en curso y no respondió a las tres consultas que le hice desde ese día."`
- **02, vez 3, paso 4** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea."`
- **02, vez 4, paso 6** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Lleva 2 días hábiles de atraso. Habías dicho que la terminabas hoy porque el proveedor se demoró. Ismael ya fue notificado de esa fecha y el motivo."`
- **02, vez 4, paso 7** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿La terminaste? Si no, ¿para cuándo la terminás y hay algo que te trabe?"`
- **02, vez 4, paso 7** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Lleva 4 días hábiles de atraso. Habías dicho que la terminabas el mar 27/10 porque el proveedor se demoró. Ismael ya fue notificado de esa fecha y el motivo."`
- **02, vez 5, paso 3** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Si la termina ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora depende de esta tarea."`
- **02, vez 5, paso 4** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Si la terminás ese día, tendrá 2 días hábiles de atraso. La revisión de comunicaciones industriales no puede arrancar hasta que termines esta tarea."`
- **02, vez 5, paso 7** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ La tarea sigue en curso y lleva 5 días hábiles de atraso. La revisión de comunicaciones industriales de la comprimidora no puede arrancar hasta que termine."`
- **04, vez 3, paso 3** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Ya la terminaste? Si no, decime para cuándo la terminás o si estás trabado."`
- **04, vez 3, paso 5** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Ya la terminaste? Si no, decime para cuándo la terminás o si estás trabado."`
- **04, vez 3, paso 7** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Ya la terminaste? Si no, decime para cuándo la terminás o si estás trabado."`
- **06, vez 3, paso 4** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿La empezaste? Si es así, ¿para cuándo la terminás o hay algo que te trabe?"`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 5007 | 8164 |
| 02 | 5 | 12056 | 13918 |
| 03 | 15 | 7836 | 10897 |
| 06 | 10 | 7556 | 20395 |
| 07 | 10 | 6836 | 12988 |
| **Todas** | 45 | 7471 | 20395 |

## Costo

- Llamadas a la IA: 200 (0 con el costo estimado); tokens de entrada 706215, de salida 33100.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 200 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
