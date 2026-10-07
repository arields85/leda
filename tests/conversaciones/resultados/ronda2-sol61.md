# Ronda ronda2-sol61

- **Fecha:** 2026-10-06 10:36
- **Commit:** 6655e94
- **IA:** openrouter/openai/gpt-6.1-sol
- **Veces:** 5
- **Jev:** no
- **Gasto de la etapa:** USD 10.89 de 30
- **Transcripciones:** [ronda2-sol61-transcripciones.md](ronda2-sol61-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 05 Varias cosas en un mensaje (garantias) | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | 5/5 | 0/5 |  |
| 06 No, era la otra tarea (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 07 Dejá, no importa (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 08 Cambio de tema (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 09 Duda: ¿de qué tarea habla? (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 10 Escribir en lugar de tocar un botón (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 11 Algo vencido (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 12 Algo que no está en la lista (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 17 Llegó el switch, sigo (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |

## Fallas

- **05, vez 1, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}]`
- **05, vez 1, paso 5** [comprension] falta un efecto: quién destraba: esperado `[{"tarea": "PLC", "alguien": true, "no_sabe": false}]`; real `[]`
- **05, vez 1, paso 5** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 1, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}]`
- **05, vez 1, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 2, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}]`
- **05, vez 2, paso 5** [comprension] falta un efecto: quién destraba: esperado `[{"tarea": "PLC", "alguien": true, "no_sabe": false}]`; real `[]`
- **05, vez 2, paso 5** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 2, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}]`
- **05, vez 2, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 3, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}]`
- **05, vez 3, paso 5** [comprension] falta un efecto: quién destraba: esperado `[{"tarea": "PLC", "alguien": true, "no_sabe": false}]`; real `[]`
- **05, vez 3, paso 5** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 3, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}]`
- **05, vez 3, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 4, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}]`
- **05, vez 4, paso 5** [comprension] falta un efecto: quién destraba: esperado `[{"tarea": "PLC", "alguien": true, "no_sabe": false}]`; real `[]`
- **05, vez 4, paso 5** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 4, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}]`
- **05, vez 4, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 5, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}]`
- **05, vez 5, paso 5** [comprension] falta un efecto: quién destraba: esperado `[{"tarea": "PLC", "alguien": true, "no_sabe": false}]`; real `[]`
- **05, vez 5, paso 5** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 5, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta", "pregunta": "quien_destraba"}]`
- **05, vez 5, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 8010 | 8973 |
| 02 | 5 | 8080 | 11610 |
| 03 | 15 | 6950 | 7807 |
| 05 | 15 | 6289 | 10911 |
| 06 | 10 | 10526 | 15608 |
| 07 | 10 | 7099 | 9399 |
| 08 | 15 | 5568 | 13566 |
| 09 | 10 | 5238 | 7692 |
| 10 | 10 | 7286 | 11205 |
| 11 | 20 | 6374 | 13520 |
| 12 | 30 | 6314 | 13159 |
| 13 | 10 | 7071 | 9569 |
| 14 | 10 | 7476 | 9709 |
| 15 | 15 | 6568 | 13060 |
| 16 | 10 | 7448 | 11571 |
| 17 | 15 | 6403 | 14904 |
| **Todas** | 205 | 6780 | 15608 |

## Costo

- Llamadas a la IA: 636 (5 con el costo estimado); tokens de entrada 1718418, de salida 36106.
- Jev: 0 llamadas, USD 0.0000 (estimado).
- **Total de la ronda: USD 1.9589.**
