> **INVÁLIDA como medición (2026-10-06):** OpenRouter se quedó sin crédito y rechazó llamadas con HTTP 402 Payment Required desde alrededor de las 21:21 del 2026-10-05: 27 de las 85 corridas tienen llamadas rechazadas (18 enteras), 235 llamadas en total. Se guarda como evidencia del corte; el gasto que figura acá estaba inflado (la libreta, corregida).

# Ronda ronda2-sol

- **Fecha:** 2026-10-05 21:22
- **Commit:** a60cc7c
- **IA:** openrouter/openai/gpt-6-sol
- **Veces:** 5
- **Jev:** sí
- **Gasto de la etapa:** USD 9.21 de 30
- **Transcripciones:** [ronda2-invalida-sol-transcripciones.md](ronda2-invalida-sol-transcripciones.md)

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
| 12 Algo que no está en la lista (garantias) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C ok · M ok | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 1/5 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C ok · M ok | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 1/5 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C ok · M ok | 5/5 | 1/5 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 0/5 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 0/5 |  |
| 17 Llegó el switch, sigo (garantias) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 0/5 |  |

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
- **12, vez 1, paso 6** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "PLC"}]`; real `[]`
- **12, vez 1, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 1, paso 6** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "no_por_chat", "tarea": "PLC"}]`; real `[]`
- **12, vez 1, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 1, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 1, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **12, vez 2, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 2, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 2, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **12, vez 4, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 4, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 4, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **12, vez 5, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 5, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 5, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **13, vez 2, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]}`; real `[]`
- **13, vez 2, paso 1** [motor] último aviso de Marcos: esperado `["COM", "PLC"]`; real `null`
- **13, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 2, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 2, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[]`
- **13, vez 2, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 2, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **13, vez 3, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]}`; real `[]`
- **13, vez 3, paso 1** [motor] último aviso de Marcos: esperado `["COM", "PLC"]`; real `null`
- **13, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 3, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 3, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 3, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 3, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[]`
- **13, vez 3, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 3, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 3, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **13, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 4, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 4, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 4, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 4, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[]`
- **13, vez 4, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 4, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 4, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **13, vez 5, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]}`; real `[]`
- **13, vez 5, paso 1** [motor] último aviso de Marcos: esperado `["COM", "PLC"]`; real `null`
- **13, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 5, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 5, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 5, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 5, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[]`
- **13, vez 5, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 5, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **14, vez 1, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **14, vez 1, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **14, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **14, vez 1, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **14, vez 1, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **14, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "COM"}]`; real `[]`
- **14, vez 1, paso 3** [comprension] falta un efecto: estado: esperado `{"COM": "en_curso"}`; real `{}`
- **14, vez 1, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 1, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM"}]`; real `[]`
- **14, vez 2, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **14, vez 2, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **14, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **14, vez 2, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **14, vez 2, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **14, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "COM"}]`; real `[]`
- **14, vez 2, paso 3** [comprension] falta un efecto: estado: esperado `{"COM": "en_curso"}`; real `{}`
- **14, vez 2, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM"}]`; real `[]`
- **14, vez 3, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **14, vez 3, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **14, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **14, vez 3, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **14, vez 3, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **14, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "COM"}]`; real `[]`
- **14, vez 3, paso 3** [comprension] falta un efecto: estado: esperado `{"COM": "en_curso"}`; real `{}`
- **14, vez 3, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 3, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM"}]`; real `[]`
- **14, vez 4, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **14, vez 4, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **14, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **14, vez 4, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **14, vez 4, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **14, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "COM"}]`; real `[]`
- **14, vez 4, paso 3** [comprension] falta un efecto: estado: esperado `{"COM": "en_curso"}`; real `{}`
- **14, vez 4, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 4, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM"}]`; real `[]`
- **15, vez 1, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-27", "atraso_dias_habiles": 0, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 1, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`; real `[]`
- **15, vez 1, paso 2** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 1, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 1, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "presente"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-28"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **15, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"dijo": "presente", "el": "2026-10-27"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 1, paso 4** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 1, paso 5** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`; real `[]`
- **15, vez 1, paso 5** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 1, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 1, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 1, paso 5** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 1, paso 5** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "veces_sin_algo_cierto": 2, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-29"}, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **15, vez 1, paso 5** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 1, paso 6** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`; real `[]`
- **15, vez 1, paso 6** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-11-03", "motivo": "ausente"}]`; real `[]`
- **15, vez 1, paso 6** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"]}}]`; real `[]`
- **15, vez 1, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 1, paso 6** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **15, vez 1, paso 6** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **15, vez 1, paso 7** [motor] no salió lo esperado: esperado `{"a": "Ismael", "el": "2026-10-28", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-11-03", "atraso_si_se_cumple_la_prevision_dias_habiles": 5}}`; real `[]`
- **15, vez 1, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}, {"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **15, vez 1, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "pedidos_anteriores_que_no_le_llegaron": 1}, "outbox_id": null}]`
- **15, vez 1, paso 8** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC", "COM"], "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03"}}}`; real `[]`
- **15, vez 1, paso 8** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 2, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-27", "atraso_dias_habiles": 0, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 2, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`; real `[]`
- **15, vez 2, paso 2** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 2, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 2, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "presente"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-28"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **15, vez 2, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"dijo": "presente", "el": "2026-10-27"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 2, paso 4** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 2, paso 5** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`; real `[]`
- **15, vez 2, paso 5** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 2, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 2, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 2, paso 5** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 2, paso 5** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "veces_sin_algo_cierto": 2, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-29"}, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **15, vez 2, paso 5** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 2, paso 6** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`; real `[]`
- **15, vez 2, paso 6** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-11-03", "motivo": "ausente"}]`; real `[]`
- **15, vez 2, paso 6** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"]}}]`; real `[]`
- **15, vez 2, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 2, paso 6** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **15, vez 2, paso 6** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **15, vez 2, paso 7** [motor] no salió lo esperado: esperado `{"a": "Ismael", "el": "2026-10-28", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-11-03", "atraso_si_se_cumple_la_prevision_dias_habiles": 5}}`; real `[]`
- **15, vez 2, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}, {"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **15, vez 2, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "pedidos_anteriores_que_no_le_llegaron": 1}, "outbox_id": null}]`
- **15, vez 2, paso 8** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC", "COM"], "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03"}}}`; real `[]`
- **15, vez 2, paso 8** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 3, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-27", "atraso_dias_habiles": 0, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 3, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`; real `[]`
- **15, vez 3, paso 2** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 3, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 3, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "presente"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-28"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **15, vez 3, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"dijo": "presente", "el": "2026-10-27"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 3, paso 4** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 3, paso 5** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`; real `[]`
- **15, vez 3, paso 5** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 3, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 3, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 3, paso 5** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 3, paso 5** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "veces_sin_algo_cierto": 2, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-29"}, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **15, vez 3, paso 5** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 3, paso 6** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`; real `[]`
- **15, vez 3, paso 6** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-11-03", "motivo": "ausente"}]`; real `[]`
- **15, vez 3, paso 6** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"]}}]`; real `[]`
- **15, vez 3, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 3, paso 6** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **15, vez 3, paso 6** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **15, vez 3, paso 7** [motor] no salió lo esperado: esperado `{"a": "Ismael", "el": "2026-10-28", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-11-03", "atraso_si_se_cumple_la_prevision_dias_habiles": 5}}`; real `[]`
- **15, vez 3, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}, {"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **15, vez 3, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2, "pedidos_anteriores_que_no_le_llegaron": 1}, "outbox_id": null}]`
- **15, vez 3, paso 8** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC", "COM"], "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03"}}}`; real `[]`
- **15, vez 3, paso 8** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 4, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-27", "atraso_dias_habiles": 0, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 4, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "voy bien, la tengo casi lista"}]`; real `[]`
- **15, vez 4, paso 2** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 4, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 4, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "avance": {"dijo": "presente"}, "el_pedido_de_estado": "sigue_abierto", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-28"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **15, vez 4, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"dijo": "presente", "el": "2026-10-27"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **15, vez 4, paso 4** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 4, paso 5** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`; real `[]`
- **15, vez 4, paso 5** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 4, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 4, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 4, paso 5** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 4, paso 5** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "veces_sin_algo_cierto": 2, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-29"}, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **15, vez 4, paso 5** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 4, paso 6** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`; real `[]`
- **15, vez 4, paso 6** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-11-03", "motivo": "ausente"}]`; real `[]`
- **15, vez 4, paso 6** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"]}}]`; real `[]`
- **15, vez 4, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 4, paso 6** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **15, vez 4, paso 6** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **15, vez 4, paso 7** [motor] no salió lo esperado: esperado `{"a": "Ismael", "el": "2026-10-28", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-11-03", "atraso_si_se_cumple_la_prevision_dias_habiles": 5}}`; real `[{"a": "Ismael", "tipo": "escalamiento", "tareas": ["PLC"], "el": "2026-11-02", "hechos": {"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-28", "necesita_respuesta": false, "atraso_dias_habiles": 4, "pedidos_de_estado_sin_respuesta": 3}}]`
- **15, vez 4, paso 7** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-28", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}}`
- **15, vez 4, paso 7** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-29", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}}`
- **15, vez 4, paso 7** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-30", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}`
- **15, vez 4, paso 7** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "escalamiento", "tareas": ["PLC"], "el": "2026-11-02", "hechos": {"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-28", "necesita_respuesta": false, "atraso_dias_habiles": 4, "pedidos_de_estado_sin_respuesta": 3}}`
- **15, vez 4, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "escalamiento", "tarea": "PLC", "a": "Ismael", "estado": "enviado", "motivo": null, "hechos": {"aviso": "falta_de_respuesta", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "responsable": "Marcos Tarquini", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "pedido_desde": "2026-10-28", "necesita_respuesta": false, "atraso_dias_habiles": 4, "pedidos_de_estado_sin_respuesta": 3}, "outbox_id": "c18bfa23-6612-4879-9ffc-b0453d8b69d1"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}, "outbox_id": "bac57ec1-7129-4ebb-9644-914e477e2c10"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}, "outbox_id": "49e5126a-9bbe-4687-a619-d13b9182948b"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}, "outbox_id": "4d2ad595-73f2-4786-bc66-ab25fb658682"}]`
- **15, vez 4, paso 8** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC", "COM"], "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03"}}}`; real `[{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["COM"], "el": "2026-11-03", "hechos": {"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}}]`
- **15, vez 4, paso 8** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["COM"], "el": "2026-11-03", "hechos": {"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}}`
- **15, vez 5, paso 5** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`; real `[]`
- **15, vez 5, paso 5** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 5, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 5, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 5, paso 5** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 5, paso 5** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "veces_sin_algo_cierto": 2, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-29"}, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **15, vez 5, paso 5** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`
- **15, vez 5, paso 6** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`; real `[]`
- **15, vez 5, paso 6** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-11-03", "motivo": "ausente"}]`; real `[]`
- **15, vez 5, paso 6** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "dependientes": ["COM"]}}]`; real `[]`
- **15, vez 5, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 5, paso 6** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-11-03", "fecha_comprometida": "2026-10-27", "atraso_si_se_cumple_la_prevision_dias_habiles": 5, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **15, vez 5, paso 6** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`
- **15, vez 5, paso 6** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **15, vez 5, paso 7** [motor] no salió lo esperado: esperado `{"a": "Ismael", "el": "2026-10-28", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-11-03", "atraso_si_se_cumple_la_prevision_dias_habiles": 5}}`; real `[]`
- **15, vez 5, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **15, vez 5, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": "d61eb3ce-f5aa-494e-bfd9-08870531a57e"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": "b55ad8f1-266f-4ce8-a0f6-aabe6b25ba38"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}, "outbox_id": null}, {"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}, "outbox_id": "946017b1-16ec-49c4-bd24-5ce306d3f279"}]`
- **15, vez 5, paso 8** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC", "COM"], "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03"}}}`; real `[]`
- **16, vez 1, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 2, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 1, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **16, vez 1, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **16, vez 1, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **16, vez 1, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **16, vez 1, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 1, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-27"}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **16, vez 1, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`; real `[]`
- **16, vez 1, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-10-28", "motivo": "ausente"}]`; real `[]`
- **16, vez 1, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}]`; real `[]`
- **16, vez 1, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 1, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **16, vez 1, paso 3** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **16, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}`; real `[]`
- **16, vez 1, paso 5** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}]`
- **16, vez 1, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28"}}}`; real `[]`
- **16, vez 1, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **16, vez 1, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 2, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 2, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 1, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **16, vez 2, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **16, vez 2, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **16, vez 2, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **16, vez 2, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-27"}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **16, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`; real `[]`
- **16, vez 2, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-10-28", "motivo": "ausente"}]`; real `[]`
- **16, vez 2, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}]`; real `[]`
- **16, vez 2, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **16, vez 2, paso 3** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **16, vez 2, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}`; real `[]`
- **16, vez 2, paso 5** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}]`
- **16, vez 2, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28"}}}`; real `[]`
- **16, vez 2, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **16, vez 2, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 3, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 2, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 1, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **16, vez 3, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **16, vez 3, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **16, vez 3, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **16, vez 3, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 3, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-27"}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **16, vez 3, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`; real `[]`
- **16, vez 3, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-10-28", "motivo": "ausente"}]`; real `[]`
- **16, vez 3, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}]`; real `[]`
- **16, vez 3, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 3, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **16, vez 3, paso 3** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **16, vez 3, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}`; real `[]`
- **16, vez 3, paso 5** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}]`
- **16, vez 3, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28"}}}`; real `[]`
- **16, vez 3, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **16, vez 3, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 4, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 2, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 1, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **16, vez 4, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **16, vez 4, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **16, vez 4, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **16, vez 4, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 4, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-27"}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **16, vez 4, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`; real `[]`
- **16, vez 4, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-10-28", "motivo": "ausente"}]`; real `[]`
- **16, vez 4, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}]`; real `[]`
- **16, vez 4, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 4, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **16, vez 4, paso 3** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **16, vez 4, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}`; real `[]`
- **16, vez 4, paso 5** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}]`
- **16, vez 4, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28"}}}`; real `[]`
- **16, vez 4, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **16, vez 4, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 5, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 2, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 1, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **16, vez 5, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **16, vez 5, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **16, vez 5, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **16, vez 5, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 5, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-27"}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **16, vez 5, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-10-28"}]`; real `[]`
- **16, vez 5, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-10-28", "motivo": "ausente"}]`; real `[]`
- **16, vez 5, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}]`; real `[]`
- **16, vez 5, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "PLC", "prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar"}}]`; real `[]`
- **16, vez 5, paso 3** [comprension] esperas abiertas después: esperado `[]`; real `["PLC"]`
- **16, vez 5, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "PLC", "hechos": {"prevision": "2026-10-28", "fecha_comprometida": "2026-10-23", "atraso_si_se_cumple_la_prevision_dias_habiles": 3, "dependientes": ["COM"]}}`; real `[]`
- **16, vez 5, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-26", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}}`
- **16, vez 5, paso 5** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}, "outbox_id": "a86c00fc-9b79-4fa5-8c4a-4de5683dac93"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 2}, "outbox_id": null}]`
- **16, vez 5, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-10-28"}}}`; real `[{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-28", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3}}]`
- **16, vez 5, paso 6** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-28", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 3}}`
- **17, vez 1, paso 1** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 1, paso 1** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 1, paso 1** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 1, paso 1** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 1, paso 1** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 1, paso 3** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 0, "estado": "en_curso"}}`; real `[]`
- **17, vez 1, paso 3** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 1, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`; real `[]`
- **17, vez 1, paso 4** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **17, vez 1, paso 4** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **17, vez 1, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 1, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 1, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "presente", "pregunta": "quien_destraba"}]`; real `[]`
- **17, vez 1, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 1, paso 5** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 1, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 1, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **17, vez 1, paso 5** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 1, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 1, paso 5** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 1, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"jugada": "destrabar", "dijo": "presente"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **17, vez 1, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 2, paso 1** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 2, paso 1** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 2, paso 1** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 2, paso 1** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 2, paso 1** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 2, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`; real `[]`
- **17, vez 2, paso 4** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **17, vez 2, paso 4** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **17, vez 2, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 2, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 2, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "presente", "pregunta": "quien_destraba"}]`; real `[]`
- **17, vez 2, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`
- **17, vez 2, paso 5** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 2, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 2, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **17, vez 2, paso 5** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 2, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 2, paso 5** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 2, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`
- **17, vez 2, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"jugada": "destrabar", "dijo": "presente"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-26", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}}]`
- **17, vez 2, paso 6** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-10-26", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 1}}`
- **17, vez 3, paso 1** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 3, paso 1** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 3, paso 1** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 3, paso 1** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 3, paso 1** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 3, paso 3** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 0, "estado": "en_curso"}}`; real `[]`
- **17, vez 3, paso 3** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 3, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`; real `[]`
- **17, vez 3, paso 4** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **17, vez 3, paso 4** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **17, vez 3, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 3, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 3, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "presente", "pregunta": "quien_destraba"}]`; real `[]`
- **17, vez 3, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 3, paso 5** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 3, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 3, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **17, vez 3, paso 5** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 3, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 3, paso 5** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 3, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"jugada": "destrabar", "dijo": "presente"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **17, vez 3, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 4, paso 1** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 4, paso 1** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 4, paso 1** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 4, paso 1** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 4, paso 1** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 4, paso 3** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 0, "estado": "en_curso"}}`; real `[]`
- **17, vez 4, paso 3** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 4, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`; real `[]`
- **17, vez 4, paso 4** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **17, vez 4, paso 4** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **17, vez 4, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 4, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 4, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "presente", "pregunta": "quien_destraba"}]`; real `[]`
- **17, vez 4, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 4, paso 5** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 4, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 4, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **17, vez 4, paso 5** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 4, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 4, paso 5** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 4, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"jugada": "destrabar", "dijo": "presente"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **17, vez 4, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 5, paso 1** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 5, paso 1** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 5, paso 1** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 5, paso 1** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 5, paso 1** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "espero el switch"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 5, paso 3** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 0, "estado": "en_curso"}}`; real `[]`
- **17, vez 5, paso 3** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`; real `[]`
- **17, vez 5, paso 4** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **17, vez 5, paso 4** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **17, vez 5, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 5, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 5, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "presente", "pregunta": "quien_destraba"}]`; real `[]`
- **17, vez 5, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 5, paso 5** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 5, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 5, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **17, vez 5, paso 5** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 5, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 5, paso 5** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 5, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"jugada": "destrabar", "dijo": "presente"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **17, vez 5, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 3604 | 5405 |
| 02 | 5 | 6119 | 8097 |
| 03 | 15 | 5527 | 7812 |
| 05 | 15 | 7930 | 9558 |
| 06 | 10 | 4091 | 4923 |
| 07 | 10 | 3525 | 4609 |
| 08 | 15 | 4035 | 7966 |
| 09 | 10 | 3305 | 3698 |
| 10 | 10 | 4186 | 5778 |
| 11 | 20 | 4614 | 8959 |
| 12 | 30 | 5784 | 8572 |
| 13 | 10 | 425 | 4011 |
| 14 | 10 | 398 | 5839 |
| 15 | 15 | 401 | 6434 |
| 16 | 10 | 416 | 468 |
| 17 | 15 | 402 | 585 |
| **Todas** | 205 | 3682 | 9558 |

## Costo

- Llamadas a la IA: 678 (235 con el costo estimado); tokens de entrada 1182770, de salida 47787.
- Jev: 35 llamadas, USD 0.3500 (estimado).
- **Total de la ronda: USD 5.7426.**

## Jev contra la IA (decisión 7)

Jev corre en paralelo y no decide nada. Correcta: lo que el paso espera (`preguntar` o la tarea).

| Conv. | Vez | Paso | Referencia | Correcta | IA | Jev | Probabilidades | Verificación | IA acierta | Jev acierta |
|---|---|---|---|---|---|---|---|---|---|---|
| 13 | 1 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"ARI": 0.01, "COM": 0.09, "PLC": 0.9} | {"misma": 0.77, "rival": 0.62} | ok | ok |
| 13 | 2 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"PLC": 0.93, "ARI": 0.01, "COM": 0.06} | {"misma": 0.76, "rival": 0.62} | ok | ok |
| 13 | 3 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"PLC": 0.94, "COM": 0.05, "ARI": 0.01} | {"misma": 0.76, "rival": 0.63} | ok | ok |
| 13 | 4 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"COM": 0.05, "ARI": 0.01, "PLC": 0.94} | {"misma": 0.78, "rival": 0.65} | ok | ok |
| 13 | 5 | 2 | la de la comprimidora | preguntar | preguntar | ambigua | {"PLC": 0.94, "ARI": 0.01, "COM": 0.05} | {"misma": 0.76, "rival": 0.62} | ok | ok |
| 13 | 1 | 3 | la del plc | PLC | PLC | ambigua | {"ARI": 0.0, "PLC": 0.97, "COM": 0.03} | {"misma": 0.63, "rival": 0.53} | ok | FALLA |
| 13 | 2 | 3 | la del plc | PLC | preguntar | ambigua | {"PLC": 0.97, "COM": 0.03, "ARI": 0.0} | {"misma": 0.64, "rival": 0.52} | FALLA | FALLA |
| 13 | 3 | 3 | la del plc | PLC | preguntar | ambigua | {"COM": 0.03, "PLC": 0.97, "ARI": 0.0} | {"misma": 0.63, "rival": 0.52} | FALLA | FALLA |
| 13 | 4 | 3 | la del plc | PLC | preguntar | ambigua | {"ARI": 0.0, "COM": 0.03, "PLC": 0.97} | {"misma": 0.68, "rival": 0.52} | FALLA | FALLA |
| 13 | 5 | 3 | la del plc | PLC | preguntar | ambigua | {"ARI": 0.0, "COM": 0.03, "PLC": 0.97} | {"misma": 0.65, "rival": 0.52} | FALLA | FALLA |
| 14 | 1 | 2 | la de la comprimidora | PLC | preguntar | ambigua | {"COM": 0.12, "PLC": 0.88} | {"misma": 0.85, "rival": 0.61} | FALLA | FALLA |
| 14 | 2 | 2 | la de la comprimidora | PLC | preguntar | ambigua | {"PLC": 0.9, "COM": 0.1} | {"misma": 0.84, "rival": 0.6} | FALLA | FALLA |
| 14 | 3 | 2 | la de la comprimidora | PLC | preguntar | ambigua | {"COM": 0.13, "PLC": 0.87} | {"misma": 0.78, "rival": 0.59} | FALLA | FALLA |
| 14 | 4 | 2 | la de la comprimidora | PLC | preguntar | ambigua | {"COM": 0.12, "PLC": 0.88} | {"misma": 0.83, "rival": 0.59} | FALLA | FALLA |
| 14 | 5 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"PLC": 0.9, "COM": 0.1} | {"misma": 0.84, "rival": 0.56} | ok | FALLA |
| 14 | 1 | 3 | la otra de la comprimidora | COM | preguntar | ambigua | {"COM": 0.4, "PLC": 0.6} | null | FALLA | FALLA |
| 14 | 2 | 3 | la otra de la comprimidora | COM | preguntar | ambigua | {"PLC": 0.61, "COM": 0.39} | null | FALLA | FALLA |
| 14 | 3 | 3 | la otra de la comprimidora | COM | preguntar | ambigua | {"PLC": 0.58, "COM": 0.42} | null | FALLA | FALLA |
| 14 | 4 | 3 | la otra de la comprimidora | COM | preguntar | ambigua | {"COM": 0.44, "PLC": 0.56} | null | FALLA | FALLA |
| 14 | 5 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"COM": 0.43, "PLC": 0.57} | null | ok | FALLA |
