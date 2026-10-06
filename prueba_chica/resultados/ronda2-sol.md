# Ronda ronda2-sol

- **Fecha:** 2026-10-06 10:28
- **Commit:** 6655e94
- **IA:** openrouter/openai/gpt-6-sol
- **Veces:** 5
- **Jev:** sí
- **Gasto de la etapa:** USD 8.93 de 30
- **Transcripciones:** [ronda2-sol-transcripciones.md](ronda2-sol-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 05 Varias cosas en un mensaje (garantias) | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C ok · M ok | 5/5 | 1/5 |  |
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

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 5624 | 9784 |
| 02 | 5 | 8419 | 11805 |
| 03 | 15 | 6991 | 12289 |
| 05 | 15 | 7947 | 15261 |
| 06 | 10 | 3938 | 8302 |
| 07 | 10 | 3410 | 5277 |
| 08 | 15 | 4623 | 9555 |
| 09 | 10 | 2744 | 5494 |
| 10 | 10 | 4003 | 6610 |
| 11 | 20 | 6138 | 9363 |
| 12 | 30 | 7610 | 11268 |
| 13 | 10 | 4213 | 5624 |
| 14 | 10 | 3746 | 7694 |
| 15 | 15 | 7477 | 10408 |
| 16 | 10 | 7525 | 9257 |
| 17 | 15 | 6261 | 8235 |
| **Todas** | 205 | 6248 | 15261 |

## Costo

- Llamadas a la IA: 630 (0 con el costo estimado); tokens de entrada 1716033, de salida 69085.
- Jev: 35 llamadas, USD 0.3500 (estimado).
- **Total de la ronda: USD 2.6726.**

## Jev contra la IA (decisión 7)

Jev corre en paralelo y no decide nada. Correcta: lo que el paso espera (`preguntar` o la tarea).

| Conv. | Vez | Paso | Referencia | Correcta | IA | Jev | Probabilidades | Verificación | IA acierta | Jev acierta |
|---|---|---|---|---|---|---|---|---|---|---|
| 13 | 1 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"COM": 0.06, "PLC": 0.93, "ARI": 0.01} | {"misma": 0.72, "rival": 0.64} | ok | ok |
| 13 | 2 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"PLC": 0.94, "ARI": 0.01, "COM": 0.05} | {"misma": 0.79, "rival": 0.63} | ok | ok |
| 13 | 3 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"PLC": 0.95, "ARI": 0.01, "COM": 0.04} | {"misma": 0.77, "rival": 0.66} | ok | ok |
| 13 | 4 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"ARI": 0.01, "PLC": 0.93, "COM": 0.06} | {"misma": 0.78, "rival": 0.61} | ok | ok |
| 13 | 5 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"ARI": 0.01, "PLC": 0.93, "COM": 0.06} | {"misma": 0.76, "rival": 0.62} | ok | ok |
| 13 | 1 | 3 | la del plc | PLC | PLC | ambigua | {"ARI": 0.0, "COM": 0.03, "PLC": 0.97} | {"misma": 0.66, "rival": 0.52} | ok | FALLA |
| 13 | 2 | 3 | la del plc | PLC | PLC | ambigua | {"PLC": 0.98, "ARI": 0.0, "COM": 0.02} | {"misma": 0.65, "rival": 0.54} | ok | FALLA |
| 13 | 3 | 3 | la del plc | PLC | PLC | ambigua | {"COM": 0.04, "ARI": 0.0, "PLC": 0.96} | {"misma": 0.65, "rival": 0.52} | ok | FALLA |
| 13 | 4 | 3 | la del plc | PLC | PLC | ambigua | {"PLC": 0.97, "COM": 0.03, "ARI": 0.0} | {"misma": 0.64, "rival": 0.54} | ok | FALLA |
| 13 | 5 | 3 | la del plc | PLC | PLC | ambigua | {"COM": 0.03, "PLC": 0.97, "ARI": 0.0} | {"misma": 0.62, "rival": 0.55} | ok | FALLA |
| 14 | 1 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"PLC": 0.88, "COM": 0.12} | {"misma": 0.82, "rival": 0.61} | ok | FALLA |
| 14 | 2 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"COM": 0.11, "PLC": 0.89} | {"misma": 0.84, "rival": 0.56} | ok | FALLA |
| 14 | 3 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"PLC": 0.91, "COM": 0.09} | {"misma": 0.85, "rival": 0.58} | ok | FALLA |
| 14 | 4 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"COM": 0.1, "PLC": 0.9} | {"misma": 0.84, "rival": 0.59} | ok | FALLA |
| 14 | 5 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"PLC": 0.9, "COM": 0.1} | {"misma": 0.84, "rival": 0.59} | ok | FALLA |
| 14 | 1 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"COM": 0.43, "PLC": 0.57} | null | ok | FALLA |
| 14 | 2 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"PLC": 0.55, "COM": 0.45} | null | ok | FALLA |
| 14 | 3 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"COM": 0.38, "PLC": 0.62} | null | ok | FALLA |
| 14 | 4 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"COM": 0.41, "PLC": 0.59} | null | ok | FALLA |
| 14 | 5 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"PLC": 0.57, "COM": 0.43} | null | ok | FALLA |
