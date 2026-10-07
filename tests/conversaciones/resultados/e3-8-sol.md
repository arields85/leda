# Ronda e3-8-sol

- **Fecha:** 2026-10-07 03:00
- **Commit:** c6b849b
- **Motor:** leda.motor
- **IA:** openrouter/openai/gpt-6-sol
- **Veces:** 5
- **Gasto de la etapa:** USD 26.21 de 30
- **Transcripciones:** [e3-8-sol-transcripciones.md](e3-8-sol-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 05 Varias cosas en un mensaje (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C FALLA · M FALLA | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 4/5 |  |
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
| 18 Habla de lo que pasa en el mundo, no de la cocina (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |

## Fallas

- **05, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espera el switch nuevo"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "motivo": "espero el switch nuevo"}]`
- **05, vez 3, paso 2** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "presente"}]`; real `[]`
- **05, vez 3, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "motivo": "presente"}}]`; real `[]`
- **05, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3}]`; real `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "lo_que_sigue": {"pide_el_estado_el": {"fecha": "2026-10-23"}}}, {"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["fecha"]}]`
- **05, vez 3, paso 3** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": [], "motivo": "presente"}}`; real `[]`
- **05, vez 3, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM"}]`
- **05, vez 3, paso 4** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-05"}]`; real `[]`
- **05, vez 3, paso 4** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-05", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 4}}]`; real `[]`
- **05, vez 3, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_si_se_cumple_la_prevision_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "falta_dato", "falta": ["fecha"]}]`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 4139 | 6391 |
| 02 | 5 | 7382 | 12008 |
| 03 | 15 | 5931 | 8204 |
| 05 | 15 | 7605 | 9204 |
| 06 | 10 | 4610 | 6755 |
| 07 | 10 | 4690 | 7461 |
| 08 | 15 | 4504 | 11219 |
| 09 | 10 | 3060 | 4179 |
| 10 | 10 | 3350 | 4199 |
| 11 | 20 | 5622 | 7920 |
| 12 | 30 | 6362 | 9741 |
| 13 | 10 | 3265 | 6415 |
| 14 | 10 | 3996 | 6821 |
| 15 | 15 | 5700 | 9077 |
| 16 | 10 | 5724 | 6560 |
| 17 | 15 | 5127 | 7069 |
| 18 | 10 | 5422 | 7274 |
| **Todas** | 215 | 5403 | 12008 |

## Costo

- Llamadas a la IA: 670 (0 con el costo estimado); tokens de entrada 2124390, de salida 99437.
- **Total de la ronda: USD 3.0422.**
