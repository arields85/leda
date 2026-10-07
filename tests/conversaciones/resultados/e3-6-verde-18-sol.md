# Ronda e3-6-verde-18-sol

- **Fecha:** 2026-10-07 01:27
- **Commit:** 9c83ead
- **Motor:** leda.motor
- **IA:** openrouter/openai/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 20.20 de 30
- **Transcripciones:** [e3-6-verde-18-sol-transcripciones.md](e3-6-verde-18-sol-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 18 Habla de lo que pasa en el mundo, no de la cocina (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |

## Fallas

Ninguna.

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 18 | 10 | 5626 | 7089 |
| **Todas** | 10 | 5626 | 7089 |

## Costo

- Llamadas a la IA: 40 (0 con el costo estimado); tokens de entrada 119334, de salida 7183.
- **Total de la ronda: USD 0.1925.**
