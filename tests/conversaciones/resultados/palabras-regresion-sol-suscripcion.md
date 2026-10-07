# Ronda palabras-regresion-sol-suscripcion

- **Fecha:** 2026-10-07 11:15
- **Commit:** 84522cc
- **Motor:** leda.motor
- **IA:** chatgpt/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 27.47 de 30
- **Parámetros de la IA:** ninguno (los de omisión)
- **Transcripciones:** [palabras-regresion-sol-suscripcion-transcripciones.md](palabras-regresion-sol-suscripcion-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 05 Varias cosas en un mensaje (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 06 No, era la otra tarea (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 07 Dejá, no importa (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 08 Cambio de tema (garantias) | G ok · C ok · M FALLA | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 09 Duda: ¿de qué tarea habla? (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 10 Escribir en lugar de tocar un botón (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 11 Algo vencido (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 12 Algo que no está en la lista (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M FALLA | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 17 Llegó el switch, sigo (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 18 Habla de lo que pasa en el mundo, no de la cocina (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 19 Palabras de todos los días, no los nombres del sistema (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |

## Fallas

- **08, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "motivo": "ausente"}}`; real `[]`
- **16, vez 3, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 2, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 1, "si_no_hay_respuesta": "ausente"}}`; real `[]`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 5158 | 12339 |
| 02 | 5 | 10592 | 14026 |
| 03 | 15 | 8056 | 12712 |
| 05 | 15 | 8046 | 13234 |
| 06 | 10 | 6916 | 10390 |
| 07 | 10 | 6521 | 11227 |
| 08 | 15 | 12367 | 18637 |
| 09 | 10 | 6571 | 11232 |
| 10 | 10 | 5311 | 10909 |
| 11 | 20 | 8620 | 15012 |
| 12 | 30 | 12434 | 49610 |
| 13 | 10 | 7108 | 10753 |
| 14 | 10 | 9512 | 14979 |
| 15 | 15 | 10907 | 16485 |
| 16 | 10 | 8624 | 14125 |
| 17 | 15 | 10245 | 18164 |
| 18 | 10 | 12469 | 15035 |
| 19 | 15 | 11455 | 17803 |
| **Todas** | 230 | 9628 | 49610 |

## Costo

- Llamadas a la IA: 735 (0 con el costo estimado); tokens de entrada 2484555, de salida 78270.
- **Total de la ronda: USD 0.0000.**
- **Por suscripción:** 717 llamada(s) por la suscripción de ChatGPT, sin costo por llamada; el total en USD no las incluye.
