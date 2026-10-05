# Ronda 2026-10-05-en-seco-guionada

- **Fecha:** 2026-10-05 16:48
- **Commit:** 93647f3
- **IA:** guionada
- **Veces:** 1
- **Jev:** no
- **Gasto de la etapa:** sin gasto
- **Transcripciones:** [2026-10-05-en-seco-guionada-transcripciones.md](2026-10-05-en-seco-guionada-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M FALLA | 1/1 | 1/1 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 05 Varias cosas en un mensaje (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 06 No, era la otra tarea (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 07 Dejá, no importa (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 08 Cambio de tema (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 09 Duda: ¿de qué tarea habla? (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 10 Escribir en lugar de tocar un botón (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 11 Algo vencido (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 12 Algo que no está en la lista (garantias) | G ok · C ok · M FALLA | 1/1 | 1/1 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C ok · M FALLA | 1/1 | 1/1 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |

## Fallas

- **03, vez 1, paso 2** [motor] esperas abiertas después: esperado `["PLC"]`; real `[]`
- **03, vez 1, paso 3** [motor] esperas abiertas después: esperado `["PLC"]`; real `[]`
- **03, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tarea": "PLC"}`; real `[]`
- **03, vez 1, paso 4** [motor] esperas abiertas después: esperado `["PLC"]`; real `[]`
- **03, vez 1, paso 5** [motor] pregunta abierta después: esperado `{"tarea": "PLC"}`; real `null`
- **12, vez 1, paso 2** [motor] pregunta abierta después: esperado `{"tarea": "PLC"}`; real `null`
- **13, vez 1, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]}`; real `[{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}}, {"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC"], "el": "2026-10-20", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}}]`
- **13, vez 1, paso 1** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}}`
- **13, vez 1, paso 1** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC"], "el": "2026-10-20", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}}`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 1 | 15 | 15 |
| 02 | 1 | 5 | 5 |
| 03 | 3 | 6 | 7 |
| 05 | 3 | 11 | 12 |
| 06 | 2 | 10 | 10 |
| 07 | 2 | 2 | 3 |
| 08 | 3 | 5 | 8 |
| 09 | 2 | 7 | 9 |
| 10 | 2 | 8 | 11 |
| 11 | 4 | 4 | 6 |
| 12 | 6 | 2 | 8 |
| 13 | 2 | 8 | 11 |
| 14 | 2 | 8 | 10 |
| 15 | 3 | 6 | 8 |
| **Todas** | 36 | 6 | 15 |

## Costo

Sin gasto: la IA no es un proveedor real.
