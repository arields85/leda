# Ronda seco-e3-leda-motor

- **Fecha:** 2026-10-07 00:35
- **Commit:** fb4754a
- **Motor:** leda.motor
- **IA:** guionada
- **Veces:** 1
- **Gasto de la etapa:** sin gasto
- **Transcripciones:** [seco-e3-leda-motor-transcripciones.md](seco-e3-leda-motor-transcripciones.md)

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
| 17 Llegó el switch, sigo (garantias) | G ok · C ok · M ok | 1/1 | 1/1 |  |

## Fallas

Ninguna.

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 1 | 13 | 13 |
| 02 | 1 | 10 | 10 |
| 03 | 3 | 11 | 13 |
| 05 | 3 | 22 | 37 |
| 06 | 2 | 24 | 36 |
| 07 | 2 | 6 | 6 |
| 08 | 3 | 29 | 40 |
| 09 | 2 | 12 | 17 |
| 10 | 2 | 14 | 18 |
| 11 | 4 | 11 | 12 |
| 12 | 6 | 6 | 13 |
| 13 | 2 | 12 | 17 |
| 14 | 2 | 12 | 15 |
| 15 | 3 | 13 | 15 |
| 16 | 2 | 18 | 23 |
| 17 | 3 | 13 | 15 |
| **Todas** | 41 | 13 | 40 |

## Costo

Sin gasto: la IA no es un proveedor real.
