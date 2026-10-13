# Ronda correcciones-t9-b

- **Fecha:** 2026-10-13 00:49
- **Commit:** 83d903a1
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 2
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Cupo de la suscripción antes:** La ventana corta (de 5 horas): 35 % usado; se renueva el 13/10 a las 04:56 (en 4 h 7 min). La ventana larga (de 7 días): 47 % usado; se renueva el 18/10 a las 00:58 (en 5 d 9 min).
- **Cupo de la suscripción después:** La ventana corta (de 5 horas): 48 % usado; se renueva el 13/10 a las 04:56 (en 4 h 7 min). La ventana larga (de 7 días): 49 % usado; se renueva el 18/10 a las 00:58 (en 5 d 9 min).
- **Transcripciones:** [correcciones-t9-b-transcripciones.md](correcciones-t9-b-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas. F: el formato de los mensajes de Leda (segunda vuelta, 2026-10-07; se comprueba solo y aparte de las otras tres).

| Conversación | Vez 1 | Vez 2 | Garantías | Comprensión (provisional) | Formato | Lectura del usuario |
|---|---|---|---|---|---|---|
| 40 La semana de las listas (garantias) | G ok · C ok · M ok · F FALLA | G ok · C ok · M ok · F ok | 2/2 | 2/2 | 1/2 |  |
| 41 El informe al grupo (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 2/2 | 2/2 | 2/2 |  |
| 44 Seguir la cadena hasta quien puede destrabarla (garantias) | G ok · C ok · M ok · F ok | G ok · C ok · M ok · F ok | 2/2 | 2/2 | 2/2 |  |

## Fallas

- **40, vez 1, paso 1** [formato] formato del mensaje a Marcos: esperado `"la pregunta, una sola y en el último renglón"`; real `"¿Terminaste el PLC, empezaste comunicaciones y el motor, o para cuándo terminás cada una si sigue pendiente?"`
- **40, vez 1, paso 7** [formato] formato del mensaje a Marcos: esperado `"la pregunta, una sola y en el último renglón"`; real `"¿Terminaste el PLC y empezaste comunicaciones?"`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 40 | 4 | 9494 | 11774 |
| 41 | 12 | 6749 | 9781 |
| 44 | 16 | 7892 | 15591 |
| **Todas** | 32 | 7794 | 15591 |

## Costo

- Llamadas a la IA: 142 (0 con el costo estimado); tokens de entrada 709845, de salida 25015.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 142 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
