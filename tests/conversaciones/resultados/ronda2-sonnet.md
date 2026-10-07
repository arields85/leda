# Ronda ronda2-sonnet

- **Fecha:** 2026-10-06 10:43
- **Commit:** 6655e94
- **IA:** openrouter/anthropic/claude-sonnet-5.5
- **Veces:** 5
- **Jev:** no
- **Gasto de la etapa:** USD 16.08 de 30
- **Transcripciones:** [ronda2-sonnet-transcripciones.md](ronda2-sonnet-transcripciones.md)

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
| 11 Algo vencido (garantias) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C ok · M ok | G ok · C FALLA · M FALLA | 5/5 | 1/5 |  |
| 12 Algo que no está en la lista (garantias) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 0/5 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 0/5 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 0/5 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C FALLA · M FALLA | G ok · C ok · M ok | 5/5 | 1/5 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C ok · M ok | G ok · C FALLA · M FALLA | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 4/5 |  |
| 17 Llegó el switch, sigo (garantias) | G ok · C ok · M FALLA | G ok · C ok · M FALLA | G ok · C FALLA · M FALLA | G ok · C ok · M FALLA | G ok · C FALLA · M FALLA | 5/5 | 3/5 |  |

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
- **05, vez 5, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que Martín de IT le habilite el acceso a la red de planta"}]`
- **05, vez 5, paso 5** [comprension] falta un efecto: quién destraba: esperado `[{"tarea": "PLC", "alguien": true, "no_sabe": false}]`; real `[]`
- **05, vez 5, paso 5** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 5, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "falta que Martín de IT le habilite el acceso a la red de planta", "pregunta": "quien_destraba"}]`
- **05, vez 5, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **11, vez 1, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[]`
- **11, vez 1, paso 4** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[]`
- **11, vez 1, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **11, vez 1, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[]`
- **11, vez 1, paso 4** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido"}`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "outbox_id": null}]`
- **11, vez 1, paso 5** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido", "motivo": "presente"}`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "outbox_id": null}]`
- **11, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "COM"}]`; real `[]`
- **11, vez 2, paso 2** [comprension] falta un efecto: estado: esperado `{"COM": "en_curso"}`; real `{}`
- **11, vez 2, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **11, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM"}]`; real `[]`
- **11, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[]`
- **11, vez 2, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "presente"}]`; real `[]`
- **11, vez 2, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3}}]`; real `[]`
- **11, vez 2, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **11, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[]`
- **11, vez 2, paso 4** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido"}`; real `[]`
- **11, vez 2, paso 5** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido", "motivo": "presente"}`; real `[]`
- **11, vez 3, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[]`
- **11, vez 3, paso 4** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[]`
- **11, vez 3, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **11, vez 3, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[]`
- **11, vez 3, paso 4** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido"}`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "outbox_id": null}]`
- **11, vez 3, paso 5** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido", "motivo": "presente"}`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"aviso": "nueva_prevision", "tarea": "COM", "motivo": "espero el switch", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "outbox_id": null}]`
- **11, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[]`
- **11, vez 5, paso 3** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "presente"}]`; real `[]`
- **11, vez 5, paso 3** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_si_se_cumple_la_prevision_dias_habiles": 3}}]`; real `[]`
- **11, vez 5, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **11, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[]`
- **11, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[]`
- **11, vez 5, paso 4** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[]`
- **11, vez 5, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **11, vez 5, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[]`
- **11, vez 5, paso 4** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido"}`; real `[]`
- **11, vez 5, paso 5** [motor] aviso en el estado: esperado `{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "omitido", "motivo": "presente"}`; real `[]`
- **12, vez 1, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **12, vez 1, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **12, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`; real `[{"nombre": "pedir_reasignacion", "a": "Nahuel"}]`
- **12, vez 1, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}`; real `{"tipo": "propuesta", "propone": ["anotar_prevision"], "desde_antes": false}`
- **12, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`; real `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "motivo": "cambiar_el_responsable_no_es_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "pregunta": "propuesta"}]`
- **12, vez 1, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "propuesta", "tarea": "PLC"}`; real `{"tipo": "propuesta", "tarea": null}`
- **12, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **12, vez 1, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 1, paso 3** [comprension] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado"}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "estado": "en_curso"}]`; real `[]`
- **12, vez 1, paso 3** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "propuesta", "tarea": null}`
- **12, vez 1, paso 4** [comprension] jugadas: esperado `[{"nombre": "fuera_de_la_lista", "que_pide": "que le recuerde el viernes un turno con el médico"}]`; real `[]`
- **12, vez 1, paso 4** [comprension] falta el aviso al administrador: esperado `1`; real `0`
- **12, vez 1, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 1, paso 4** [comprension] hechos: esperado `[{"resultado": "fuera_de_la_lista", "lo_que_puede_hacer": "presente"}]`; real `[]`
- **12, vez 1, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 1, paso 6** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "PLC"}]`; real `[]`
- **12, vez 1, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 1, paso 6** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "no_por_chat", "tarea": "PLC"}]`; real `[]`
- **12, vez 1, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 1, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 1, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **12, vez 2, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **12, vez 2, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **12, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`; real `[]`
- **12, vez 2, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}`; real `null`
- **12, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`; real `[]`
- **12, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "propuesta", "tarea": "PLC"}`; real `null`
- **12, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **12, vez 2, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado"}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "estado": "en_curso"}]`; real `[]`
- **12, vez 2, paso 4** [comprension] jugadas: esperado `[{"nombre": "fuera_de_la_lista", "que_pide": "que le recuerde el viernes un turno con el médico"}]`; real `[]`
- **12, vez 2, paso 4** [comprension] falta el aviso al administrador: esperado `1`; real `0`
- **12, vez 2, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 2, paso 4** [comprension] hechos: esperado `[{"resultado": "fuera_de_la_lista", "lo_que_puede_hacer": "presente"}]`; real `[]`
- **12, vez 2, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 2, paso 6** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "PLC"}]`; real `[]`
- **12, vez 2, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 2, paso 6** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "no_por_chat", "tarea": "PLC"}]`; real `[]`
- **12, vez 2, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 2, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 2, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **12, vez 3, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **12, vez 3, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **12, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`; real `[]`
- **12, vez 3, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 3, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}`; real `null`
- **12, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`; real `[]`
- **12, vez 3, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "propuesta", "tarea": "PLC"}`; real `null`
- **12, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **12, vez 3, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 3, paso 3** [comprension] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado"}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "estado": "en_curso"}]`; real `[]`
- **12, vez 3, paso 4** [comprension] jugadas: esperado `[{"nombre": "fuera_de_la_lista", "que_pide": "que le recuerde el viernes un turno con el médico"}]`; real `[]`
- **12, vez 3, paso 4** [comprension] falta el aviso al administrador: esperado `1`; real `0`
- **12, vez 3, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 3, paso 4** [comprension] hechos: esperado `[{"resultado": "fuera_de_la_lista", "lo_que_puede_hacer": "presente"}]`; real `[]`
- **12, vez 3, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 3, paso 6** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "PLC"}]`; real `[]`
- **12, vez 3, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 3, paso 6** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "no_por_chat", "tarea": "PLC"}]`; real `[]`
- **12, vez 3, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 3, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 3, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **12, vez 4, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **12, vez 4, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **12, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`; real `[]`
- **12, vez 4, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 4, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}`; real `null`
- **12, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`; real `[]`
- **12, vez 4, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "propuesta", "tarea": "PLC"}`; real `null`
- **12, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **12, vez 4, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 4, paso 3** [comprension] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado"}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "estado": "en_curso"}]`; real `[]`
- **12, vez 4, paso 4** [comprension] jugadas: esperado `[{"nombre": "fuera_de_la_lista", "que_pide": "que le recuerde el viernes un turno con el médico"}]`; real `[]`
- **12, vez 4, paso 4** [comprension] falta el aviso al administrador: esperado `1`; real `0`
- **12, vez 4, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 4, paso 4** [comprension] hechos: esperado `[{"resultado": "fuera_de_la_lista", "lo_que_puede_hacer": "presente"}]`; real `[]`
- **12, vez 4, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 4, paso 6** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "PLC"}]`; real `[]`
- **12, vez 4, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 4, paso 6** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "no_por_chat", "tarea": "PLC"}]`; real `[]`
- **12, vez 4, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 4, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 4, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **12, vez 5, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **12, vez 5, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **12, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "pedir_reasignacion", "tarea": "PLC", "a": "nahuel"}]`; real `[]`
- **12, vez 5, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 5, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "propuesta", "tarea": "PLC", "propone": ["anotar_prevision"]}`; real `null`
- **12, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "pedir_reasignacion", "resultado": "no_por_chat", "quien_decide": "Ismael Soschinski", "alternativa": "anotar_prevision", "tarea": "PLC", "pregunta": "propuesta"}]`; real `[]`
- **12, vez 5, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "propuesta", "tarea": "PLC"}`; real `null`
- **12, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "cancelar"}, {"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **12, vez 5, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado"}, {"jugada": "anotar_inicio", "resultado": "no_se_puede", "motivo": "estado", "estado": "en_curso"}]`; real `[]`
- **12, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "fuera_de_la_lista", "que_pide": "que le recuerde el viernes un turno con el médico"}]`; real `[]`
- **12, vez 5, paso 4** [comprension] falta el aviso al administrador: esperado `1`; real `0`
- **12, vez 5, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 5, paso 4** [comprension] hechos: esperado `[{"resultado": "fuera_de_la_lista", "lo_que_puede_hacer": "presente"}]`; real `[]`
- **12, vez 5, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 5, paso 6** [comprension] jugadas: esperado `[{"nombre": "entregar", "tarea": "PLC"}]`; real `[]`
- **12, vez 5, paso 6** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 5, paso 6** [comprension] hechos: esperado `[{"jugada": "entregar", "resultado": "no_por_chat", "tarea": "PLC"}]`; real `[]`
- **12, vez 5, paso 7** [comprension] jugadas: esperado `[{"nombre": "consultar_pendientes"}]`; real `[]`
- **12, vez 5, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **12, vez 5, paso 7** [comprension] hechos: esperado `[{"jugada": "consultar_pendientes", "resultado": "leido", "tareas": [{"titulo": "PLC", "estado": "en_curso", "vence": "2026-10-23"}, {"titulo": "COM", "estado": "asignada", "vence": "2026-10-30"}]}]`; real `[]`
- **13, vez 1, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]}`; real `[]`
- **13, vez 1, paso 1** [motor] último aviso de Marcos: esperado `["COM", "PLC"]`; real `null`
- **13, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 1, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 1, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 1, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 1, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[]`
- **13, vez 1, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 1, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **13, vez 1, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
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
- **13, vez 4, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tareas": ["PLC", "COM"]}`; real `[]`
- **13, vez 4, paso 1** [motor] último aviso de Marcos: esperado `["COM", "PLC"]`; real `null`
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
- **14, vez 5, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "aviso_previo", "tarea": "PLC", "hechos": {"vence": "2026-10-23", "necesita_respuesta": false}}`; real `[]`
- **14, vez 5, paso 1** [motor] último aviso de Marcos: esperado `"PLC"`; real `null`
- **14, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **14, vez 5, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **14, vez 5, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **14, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "COM"}]`; real `[]`
- **14, vez 5, paso 3** [comprension] falta un efecto: estado: esperado `{"COM": "en_curso"}`; real `{}`
- **14, vez 5, paso 3** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **14, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "COM"}]`; real `[]`
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
- **15, vez 1, paso 7** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC"], "el": "2026-11-02", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 4, "pedidos_anteriores_que_no_le_llegaron": 1}}`
- **15, vez 1, paso 7** [motor] incidente: esperado `[]`; real `[{"etapa": "motor_aviso_guardado", "severidad": "media"}]`
- **15, vez 1, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "fallido", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 2, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 4, "pedidos_anteriores_que_no_le_llegaron": 1}, "outbox_id": "19874c6c-d03f-4a21-92df-e537a51ce507"}]`
- **15, vez 1, paso 8** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tareas": ["PLC", "COM"], "hechos": {"numero": 1, "necesita_respuesta": true, "seguimiento_por": "prevision", "prevision_vigente": {"fecha": "2026-11-03"}}}`; real `[{"a": "Marcos", "tipo": ["aviso_previo", "pedido_de_estado"], "tareas": ["COM", "PLC"], "el": "2026-11-03", "hechos": [{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 5, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}, "pedidos_anteriores_que_no_le_llegaron": 1}]}]`
- **15, vez 1, paso 8** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": ["aviso_previo", "pedido_de_estado"], "tareas": ["COM", "PLC"], "el": "2026-11-03", "hechos": [{"aviso": "vencimiento_proximo", "tarea": "COM", "vence": "2026-11-06", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 3, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 5, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}, "pedidos_anteriores_que_no_le_llegaron": 1}]}`
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
- **15, vez 4, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_vencio", "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": null}, {"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "estado": "enviado", "motivo": null, "hechos": {"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 5}, "outbox_id": "b96d6a74-618a-4b85-adf7-e78e36465381"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}]`
- **16, vez 2, paso 1** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 2, "necesita_respuesta": true, "vence": "2026-10-23", "atraso_dias_habiles": 1, "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **16, vez 2, paso 1** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`; real `[]`
- **16, vez 2, paso 2** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **16, vez 2, paso 2** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **16, vez 2, paso 2** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **16, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso", "vencida": {"fecha_comprometida": "2026-10-23", "atraso_dias_habiles": 1}, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-27"}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **16, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **16, vez 2, paso 5** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-23", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": "62a50494-9e62-4f1e-9ea6-cc03846e1a7a"}, {"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "estado": "enviado", "motivo": null, "hechos": {"aviso": "nueva_prevision", "tarea": "PLC", "motivo": null, "prevision": "2026-10-28", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-23", "necesita_respuesta": false, "atraso_si_se_cumple_la_prevision_dias_habiles": 3}, "outbox_id": "f1584650-ef87-4965-9eec-454c03721b0b"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio", "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-23", "estado": "asignada", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": null}]`
- **17, vez 1, paso 5** [motor] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemó la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- **17, vez 1, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"jugada": "destrabar", "dijo": "presente"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **17, vez 1, paso 6** [motor] pregunta abierta después: esperado `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`; real `null`
- **17, vez 2, paso 5** [motor] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemó la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
- **17, vez 3, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "se quemo la fuente"}]`; real `[]`
- **17, vez 3, paso 4** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **17, vez 3, paso 4** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **17, vez 3, paso 4** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 3, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `null`
- **17, vez 3, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "presente", "pregunta": "quien_destraba"}]`; real `[]`
- **17, vez 3, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "quien_destraba", "tarea": "PLC"}`; real `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`
- **17, vez 3, paso 5** [comprension] jugadas: esperado `[{"nombre": "destrabar", "tarea": "PLC"}]`; real `[]`
- **17, vez 3, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **17, vez 3, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **17, vez 3, paso 5** [comprension] falta un efecto: bloqueo resuelto: esperado `["PLC"]`; real `[]`
- **17, vez 3, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **17, vez 3, paso 5** [comprension] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[]`
- **17, vez 3, paso 5** [comprension] pregunta abierta después: esperado `null`; real `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`
- **17, vez 3, paso 6** [motor] no salió lo esperado: esperado `{"a": "Marcos", "tipo": "repregunta_de_estado", "tarea": "PLC", "hechos": {"necesita_respuesta": true, "avance_anterior": {"jugada": "destrabar", "dijo": "presente"}, "espera_algo_cierto": "presente", "si_no_hay_respuesta": "ausente"}}`; real `[]`
- **17, vez 4, paso 5** [motor] hechos: esperado `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemo la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-26"}, "veces_sin_algo_cierto": 1, "vencida": "ausente", "pregunta": "ausente"}]`; real `[{"jugada": "destrabar", "resultado": "anotado", "tarea": "PLC", "bloqueo_resuelto": {"causa": "se quemó la fuente"}, "estado": "en_curso", "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "2026-10-26T09:00:00-03:00"}, "veces_sin_algo_cierto": 1}]`
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
| 01 | 5 | 4205 | 5289 |
| 02 | 5 | 5157 | 9859 |
| 03 | 15 | 4617 | 8687 |
| 05 | 15 | 11541 | 13583 |
| 06 | 10 | 5667 | 8519 |
| 07 | 10 | 4168 | 4648 |
| 08 | 15 | 5941 | 13198 |
| 09 | 10 | 3168 | 4352 |
| 10 | 10 | 4171 | 5670 |
| 11 | 20 | 4062 | 15536 |
| 12 | 30 | 393 | 7720 |
| 13 | 10 | 386 | 734 |
| 14 | 10 | 410 | 9060 |
| 15 | 15 | 432 | 13959 |
| 16 | 10 | 9353 | 10673 |
| 17 | 15 | 4097 | 8982 |
| **Todas** | 205 | 4135 | 15536 |

## Costo

- Llamadas a la IA: 676 (0 con el costo estimado); tokens de entrada 2090614, de salida 100998.
- Jev: 0 llamadas, USD 0.0000 (estimado).
- **Total de la ronda: USD 5.1912.**
