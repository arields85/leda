# Ronda fase-c-38b

- **Fecha:** 2026-10-10 17:28
- **Commit:** 39b21f1
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 1
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Transcripciones:** [fase-c-38b-transcripciones.md](fase-c-38b-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|
| 38 Delegar una tarea por chat (garantias) | G ok · C ok · M ok · F FALLA | 1/1 | 1/1 | 0/1 |  |

## Fallas

- **38, vez 1, paso 7** [formato] formato del mensaje a Marcos: esperado `"ningún renglón de más de 140 caracteres"`; real `"Todavía está a tu cargo. Si confirmás, Martín será consultado para decidir si pasa a Lucas. Si lo aprueba, Lucas será consultado para ver si la toma. Hasta que Lucas diga que sí, sigue a tu cargo."`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 38 | 15 | 6404 | 9141 |
| **Todas** | 15 | 6404 | 9141 |

## Costo

- Llamadas a la IA: 37 (0 con el costo estimado); tokens de entrada 220116, de salida 4953.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 37 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
