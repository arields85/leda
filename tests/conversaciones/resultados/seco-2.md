# Ronda seco-2

- **Fecha:** 2026-10-05 17:37
- **Commit:** 5aa1a67
- **IA:** guionada
- **Veces:** 1
- **Jev:** no
- **Gasto de la etapa:** sin gasto
- **Transcripciones:** [seco-2-transcripciones.md](seco-2-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 05 Varias cosas en un mensaje (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 06 No, era la otra tarea (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 07 Dejá, no importa (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 08 Cambio de tema (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 09 Duda: ¿de qué tarea habla? (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 10 Escribir en lugar de tocar un botón (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 11 Algo vencido (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 12 Algo que no está en la lista (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |

## Fallas

Ninguna.

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 1 | 11 | 11 |
| 02 | 1 | 5 | 5 |
| 03 | 3 | 6 | 9 |
| 05 | 3 | 10 | 13 |
| 06 | 2 | 10 | 11 |
| 07 | 2 | 2 | 3 |
| 08 | 3 | 6 | 11 |
| 09 | 2 | 8 | 11 |
| 10 | 2 | 10 | 15 |
| 11 | 4 | 6 | 6 |
| 12 | 6 | 4 | 9 |
| 13 | 2 | 8 | 12 |
| 14 | 2 | 8 | 10 |
| 15 | 3 | 7 | 8 |
| 16 | 2 | 12 | 19 |
| **Todas** | 38 | 6 | 19 |

## Costo

Sin gasto: la IA no es un proveedor real.
