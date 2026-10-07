# Ronda e3-6-regresion-sol

- **Fecha:** 2026-10-07 01:34
- **Commit:** 9c83ead
- **Motor:** leda.motor
- **IA:** openrouter/openai/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 23.16 de 30
- **Transcripciones:** [e3-6-regresion-sol-transcripciones.md](e3-6-regresion-sol-transcripciones.md)

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
| 08 Cambio de tema (garantias) | G ok · C ok · M ok | G ok · C FALLA · M FALLA | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 4/5 |  |
| 09 Duda: ¿de qué tarea habla? (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 10 Escribir en lugar de tocar un botón (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 11 Algo vencido (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 12 Algo que no está en la lista (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 17 Llegó el switch, sigo (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 18 Habla de lo que pasa en el mundo, no de la cocina (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |

## Fallas

- **08, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM"}]`
- **08, vez 2, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[]`
- **08, vez 2, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "motivo": "ausente"}}]`; real `[]`
- **08, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04"}]`; real `[{"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["fecha"]}]`
- **08, vez 2, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "motivo": "ausente"}}`; real `[]`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 4114 | 4552 |
| 02 | 5 | 9350 | 10206 |
| 03 | 15 | 5814 | 8702 |
| 05 | 15 | 7510 | 12898 |
| 06 | 10 | 5324 | 8083 |
| 07 | 10 | 4360 | 6438 |
| 08 | 15 | 4720 | 12378 |
| 09 | 10 | 3722 | 4695 |
| 10 | 10 | 3358 | 4664 |
| 11 | 20 | 4835 | 7513 |
| 12 | 30 | 6487 | 9197 |
| 13 | 10 | 4508 | 6420 |
| 14 | 10 | 3592 | 6532 |
| 15 | 15 | 6099 | 8050 |
| 16 | 10 | 6012 | 8360 |
| 17 | 15 | 5364 | 8419 |
| 18 | 10 | 5805 | 7805 |
| **Todas** | 215 | 5372 | 12898 |

## Costo

- Llamadas a la IA: 671 (0 con el costo estimado); tokens de entrada 2124937, de salida 98408.
- **Total de la ronda: USD 2.9672.**
