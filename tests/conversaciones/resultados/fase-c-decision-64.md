# Ronda fase-c-decision-64

- **Fecha:** 2026-10-11 01:46
- **Commit:** 0def014
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Transcripciones:** [fase-c-decision-64-transcripciones.md](fase-c-decision-64-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|---|
| 42 Quien destraba no contesta (garantias) | G ok · C FALLA · M ok · F FALLA | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F ok | 5/5 | 4/5 | 2/5 |  |

## Fallas

- **42, vez 1, paso 10** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Marcos sigue trabado desde el mar 20/10: le falta la IP del servidor de Corelabs. Ese día dijo que le toca a Ariel destrabarla. Ya van 5 días hábiles."`
- **42, vez 1, paso 13b** [comprension] jugadas: esperado `[{"nombre": "pedirselo_y_contar", "tarea": "PLC", "puede_traer": ["quien"]}]`; real `[{"nombre": "pedirselo_y_contar", "tarea": "PLC", "quien": "Ariel"}]`
- **42, vez 1, paso 14** [formato] formato del mensaje a Marcos: esperado `"el cierre, solo en su renglón y con un renglón en blanco antes"`; real `"¿Cómo te fue con Ariel? ¿Qué arreglaron y para cuándo?"`
- **42, vez 3, paso 3** [servicio] el servicio de la IA no redactó un aviso al primer intento: se reintentó: esperado `null`; real `{"falla": "PlazoAgotado"}`
- **42, vez 3, paso 10** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Marcos sigue trabado desde el mar 20/10, hace 5 días hábiles: le falta la IP del servidor de Corelabs. Marcos dijo que le toca a Ariel destrabarlo."`
- **42, vez 4, paso 10** [formato] formato del mensaje a Ismael: esperado `"ningún renglón de más de 140 caracteres"`; real `"⚠️ Sigue trabada desde el mar 20/10, hace 5 días hábiles. Marcos dijo que le falta la IP del servidor de Corelabs y que le toca a Ariel destrabarla."`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 42 | 25 | 5928 | 9171 |
| **Todas** | 25 | 5928 | 9171 |

## Costo

- Llamadas a la IA: 106 (0 con el costo estimado); tokens de entrada 519309, de salida 14024.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 105 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
