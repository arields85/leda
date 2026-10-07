# Ronda palabras-rojo-19-sol-suscripcion

- **Fecha:** 2026-10-07 10:11
- **Commit:** 098bc80
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Transcripciones:** [palabras-rojo-19-sol-suscripcion-transcripciones.md](palabras-rojo-19-sol-suscripcion-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 19 Palabras de todos los días, no los nombres del sistema (garantias) | G FALLA · C FALLA · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G FALLA · C FALLA · M ok | 3/5 | 3/5 |  |

## Fallas

- **19, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`; real `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "no llego con los tiempos"}]`
- **19, vez 1, paso 2** [garantia] efecto de más: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-10-27", "motivo": "ausente"}]`; real `[{"tarea": "PLC", "fecha": "2026-10-27", "motivo": "no llego con los tiempos", "es_correccion": false}]`
- **19, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27"}]`; real `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-27", "motivo": "no llego con los tiempos"}]`
- **19, vez 5, paso 2** [garantia] efecto de más: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-10-27", "motivo": "ausente"}]`; real `[{"tarea": "PLC", "fecha": "2026-10-27", "motivo": "no llego con los tiempos", "es_correccion": false}]`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 19 | 15 | 8099 | 18691 |
| **Todas** | 15 | 8099 | 18691 |

## Costo

- Llamadas a la IA: 50 (0 con el costo estimado); tokens de entrada 174657, de salida 7121.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 50 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
