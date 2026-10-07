# Ronda ronda1-luna

- **Fecha:** 2026-10-05 19:38
- **Commit:** 3bc32b5
- **IA:** openrouter/openai/gpt-6-luna
- **Veces:** 5
- **Jev:** no
- **Gasto de la etapa:** USD 2.75 de 30
- **Transcripciones:** [ronda1-luna-transcripciones.md](ronda1-luna-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C FALLA · M ok | G ok · C ok · M ok | G ok · C FALLA · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 3/5 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 05 Varias cosas en un mensaje (garantias) | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | 0/5 | 0/5 |  |
| 06 No, era la otra tarea (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 07 Dejá, no importa (garantias) | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | 0/5 | 0/5 |  |
| 08 Cambio de tema (garantias) | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | 0/5 | 0/5 |  |
| 09 Duda: ¿de qué tarea habla? (garantias) | ERROR | ERROR | ERROR | ERROR | ERROR | 0/5 | 0/5 |  |
| 10 Escribir en lugar de tocar un botón (garantias) | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | 5/5 | 0/5 |  |
| 11 Algo vencido (garantias) | G FALLA · C FALLA · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C FALLA · M ok | G FALLA · C FALLA · M ok | 3/5 | 2/5 |  |
| 12 Algo que no está en la lista (garantias) | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | 0/5 | 0/5 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C FALLA · M ok | G FALLA · C FALLA · M ok | G ok · C FALLA · M ok | G FALLA · C FALLA · M ok | G ok · C FALLA · M ok | 3/5 | 0/5 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C FALLA · M FALLA | G ok · C ok · M ok | G FALLA · C FALLA · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 4/5 | 3/5 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |

## Fallas

- **03, vez 1, paso 6** [comprension] jugadas: esperado `[{"nombre": "cancelar"}]`; real `[{"nombre": "dejar_para_despues"}]`
- **03, vez 1, paso 6** [comprension] preguntas para después: esperado `[]`; real `[{"tipo": "propuesta", "tarea": "PLC"}]`
- **03, vez 3, paso 6** [comprension] jugadas: esperado `[{"nombre": "cancelar"}]`; real `[{"nombre": "dejar_para_despues"}]`
- **03, vez 3, paso 6** [comprension] preguntas para después: esperado `[]`; real `[{"tipo": "propuesta", "tarea": "PLC"}]`
- **05, vez 1, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- **05, vez 1, paso 4** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **05, vez 1, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-05"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": null, "es_correccion": true}]`
- **05, vez 1, paso 4** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con el plc", "resuelto": false}]`
- **05, vez 1, paso 4** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-05", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4}}]`; real `[{"tipo": "correccion_de_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "se_anoto_en_la_tarea_equivocada", "responsable": "Marcos Tarquini", "fecha_comprometida": "2026-10-30", "prevision_que_no_vale": "2026-11-04"}, "clave": "motor:correccion_de_prevision:39a8a00a-56cf-4d4c-b9fa-c9a98dd84d0f", "outbox_id": null}]`
- **05, vez 1, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 1, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- **05, vez 1, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 1, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- **05, vez 1, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **05, vez 1, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **05, vez 1, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- **05, vez 2, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me trabe con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}]`
- **05, vez 2, paso 4** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **05, vez 2, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-05"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": null, "es_correccion": true}]`
- **05, vez 2, paso 4** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "me trabe con el plc", "resuelto": false}]`
- **05, vez 2, paso 4** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-05", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4}}]`; real `[{"tipo": "correccion_de_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "se_anoto_en_la_tarea_equivocada", "responsable": "Marcos Tarquini", "fecha_comprometida": "2026-10-30", "prevision_que_no_vale": "2026-11-04"}, "clave": "motor:correccion_de_prevision:145ffbec-0fb0-464d-bad1-e4bc520a5443", "outbox_id": null}]`
- **05, vez 2, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 2, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me trabe con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- **05, vez 2, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 2, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- **05, vez 2, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **05, vez 2, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **05, vez 2, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- **05, vez 3, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me trabe con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}]`
- **05, vez 3, paso 4** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **05, vez 3, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-05"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": null, "es_correccion": true}]`
- **05, vez 3, paso 4** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "me trabe con el plc", "resuelto": false}]`
- **05, vez 3, paso 4** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-05", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4}}]`; real `[{"tipo": "correccion_de_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "se_anoto_en_la_tarea_equivocada", "responsable": "Marcos Tarquini", "fecha_comprometida": "2026-10-30", "prevision_que_no_vale": "2026-11-04"}, "clave": "motor:correccion_de_prevision:8e101e41-f063-4365-8cfa-b006332eb4ca", "outbox_id": null}]`
- **05, vez 3, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 3, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me trabe con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- **05, vez 3, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 3, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- **05, vez 3, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **05, vez 3, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **05, vez 3, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- **05, vez 4, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "me trabe con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}]`
- **05, vez 4, paso 4** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **05, vez 4, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-05"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": null, "es_correccion": true}]`
- **05, vez 4, paso 4** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "me trabe con el plc", "resuelto": false}]`
- **05, vez 4, paso 4** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-05", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4}}]`; real `[{"tipo": "correccion_de_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "se_anoto_en_la_tarea_equivocada", "responsable": "Marcos Tarquini", "fecha_comprometida": "2026-10-30", "prevision_que_no_vale": "2026-11-04"}, "clave": "motor:correccion_de_prevision:65215e9c-a944-427c-9a3e-f8f3b4476b0f", "outbox_id": null}]`
- **05, vez 4, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 4, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "me trabe con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "correccion_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- **05, vez 4, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 4, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- **05, vez 4, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **05, vez 4, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **05, vez 4, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- **05, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision", "tarea_correcta": "COM"}]`
- **05, vez 5, paso 4** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **05, vez 5, paso 4** [comprension] falta un efecto: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-05"}]`; real `[]`
- **05, vez 5, paso 4** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con el plc", "resuelto": false}]`
- **05, vez 5, paso 4** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-05", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4}}]`; real `[]`
- **05, vez 5, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 5, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "corregir", "resultado": "no_se_puede", "motivo": "misma_tarea", "tarea": "COM"}]`
- **05, vez 5, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 5, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- **05, vez 5, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **05, vez 5, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **05, vez 5, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- **07, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- **07, vez 1, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **07, vez 1, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "estoy medio trabado con esto", "resuelto": false}]`
- **07, vez 1, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **07, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- **07, vez 1, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 1, paso 3** [motor] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **07, vez 1, paso 3** [motor] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado", "no_se_anoto_nada": true}]`; real `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- **07, vez 1, paso 3** [motor] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "el": "2026-10-23", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "estado": "en_curso"}}`; real `[{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}, {"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}]`
- **07, vez 1, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}`
- **07, vez 1, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}`
- **07, vez 1, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "escalamiento_de_una_pregunta", "tareas": ["PLC"], "el": "2026-10-23", "hechos": {"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}}`
- **07, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- **07, vez 2, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **07, vez 2, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "estoy medio trabado con esto", "resuelto": false}]`
- **07, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **07, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- **07, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 2, paso 3** [motor] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **07, vez 2, paso 3** [motor] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado", "no_se_anoto_nada": true}]`; real `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- **07, vez 2, paso 3** [motor] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 2, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "el": "2026-10-23", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "estado": "en_curso"}}`; real `[{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}, {"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}]`
- **07, vez 2, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}`
- **07, vez 2, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}`
- **07, vez 2, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "escalamiento_de_una_pregunta", "tareas": ["PLC"], "el": "2026-10-23", "hechos": {"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}}`
- **07, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- **07, vez 3, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **07, vez 3, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "estoy medio trabado con esto", "resuelto": false}]`
- **07, vez 3, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **07, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- **07, vez 3, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 3, paso 3** [motor] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **07, vez 3, paso 3** [motor] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado", "no_se_anoto_nada": true}]`; real `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- **07, vez 3, paso 3** [motor] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 3, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "el": "2026-10-23", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "estado": "en_curso"}}`; real `[{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}, {"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}]`
- **07, vez 3, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}`
- **07, vez 3, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}`
- **07, vez 3, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "escalamiento_de_una_pregunta", "tareas": ["PLC"], "el": "2026-10-23", "hechos": {"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}}`
- **07, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "estoy medio trabado con esto"}]`
- **07, vez 4, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **07, vez 4, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "estoy medio trabado con esto", "resuelto": false}]`
- **07, vez 4, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **07, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "estoy medio trabado con esto", "pregunta": "quien_destraba"}]`
- **07, vez 4, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 4, paso 3** [motor] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **07, vez 4, paso 3** [motor] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado", "no_se_anoto_nada": true}]`; real `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- **07, vez 4, paso 3** [motor] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 4, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "el": "2026-10-23", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "estado": "en_curso"}}`; real `[{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}, {"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}]`
- **07, vez 4, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}`
- **07, vez 4, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}`
- **07, vez 4, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "escalamiento_de_una_pregunta", "tareas": ["PLC"], "el": "2026-10-23", "hechos": {"aviso": "falta_de_respuesta", "sobre": {"causa": "estoy medio trabado con esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}}`
- **07, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "esto"}]`
- **07, vez 5, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **07, vez 5, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "esto", "resuelto": false}]`
- **07, vez 5, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **07, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "esto", "pregunta": "quien_destraba"}]`
- **07, vez 5, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 5, paso 3** [motor] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **07, vez 5, paso 3** [motor] hechos: esperado `[{"jugada": "cancelar", "resultado": "cancelado", "no_se_anoto_nada": true}]`; real `[{"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "PLC"}}]`
- **07, vez 5, paso 3** [motor] pregunta abierta después: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **07, vez 5, paso 4** [motor] no salió lo esperado: esperado `{"a": "Marcos", "el": "2026-10-23", "tipo": "pedido_de_estado", "tarea": "PLC", "hechos": {"numero": 1, "necesita_respuesta": true, "estado": "en_curso"}}`; real `[{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}, {"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}]`
- **07, vez 5, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-21", "hechos": {"aviso": "repregunta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 2, "pregunta": "quien_destraba", "necesita_respuesta": true}}`
- **07, vez 5, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Marcos", "tipo": "repregunta", "tareas": ["PLC"], "el": "2026-10-22", "hechos": {"aviso": "repregunta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "numero": 3, "pregunta": "quien_destraba", "necesita_respuesta": true, "si_no_hay_respuesta": {"estado": "todavia_no", "se_avisa_a": ["Ismael Soschinski"]}}}`
- **07, vez 5, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "escalamiento_de_una_pregunta", "tareas": ["PLC"], "el": "2026-10-23", "hechos": {"aviso": "falta_de_respuesta", "sobre": {"causa": "esto", "jugada": "anotar_bloqueo"}, "tarea": "PLC", "estado": "bloqueada", "pregunta": "quien_destraba", "responsable": "Marcos Tarquini", "preguntado_el": "2026-10-20", "necesita_respuesta": false, "preguntas_sin_respuesta": 3}}`
- **08, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- **08, vez 1, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **08, vez 1, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con esto", "resuelto": false}]`
- **08, vez 1, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **08, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- **08, vez 1, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4"}]`
- **08, vez 1, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4", "es_correccion": false}]`
- **08, vez 1, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:6c07e201-3883-4570-aa3e-319c252dbf28", "outbox_id": null}]`
- **08, vez 1, paso 3** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **08, vez 1, paso 3** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 1, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 1, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **08, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "esto"}]`
- **08, vez 2, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **08, vez 2, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "esto", "resuelto": false}]`
- **08, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **08, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "esto", "pregunta": "quien_destraba"}]`
- **08, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- **08, vez 2, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30", "es_correccion": false}]`
- **08, vez 2, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:19d20e11-96d2-4fad-921d-532328665f54", "outbox_id": null}]`
- **08, vez 2, paso 3** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **08, vez 2, paso 3** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 2, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 2, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 2, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": false, "nadie_mas": false}]`
- **08, vez 2, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **08, vez 2, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **08, vez 2, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "pregunta": "quien_destraba"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_destraba"], "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}]`
- **08, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- **08, vez 3, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **08, vez 3, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con esto", "resuelto": false}]`
- **08, vez 3, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **08, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- **08, vez 3, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- **08, vez 3, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30", "es_correccion": false}]`
- **08, vez 3, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:2a7a8b1b-3c44-441d-b7e9-009f01813749", "outbox_id": null}]`
- **08, vez 3, paso 3** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **08, vez 3, paso 3** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 3, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 3, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 3, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": false, "nadie_mas": false}]`
- **08, vez 3, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **08, vez 3, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **08, vez 3, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "pregunta": "quien_destraba"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_destraba"], "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}]`
- **08, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- **08, vez 4, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **08, vez 4, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con esto", "resuelto": false}]`
- **08, vez 4, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **08, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- **08, vez 4, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 4, paso 3** [motor] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **08, vez 4, paso 3** [motor] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 4, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "no me mandaron el programa del fabricante"}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "no_sabe": false, "nadie_mas": false}]`
- **08, vez 4, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **08, vez 4, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **08, vez 4, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "pregunta": "quien_destraba"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "falta_dato", "falta": ["quien_destraba"], "puede_ser": ["alguien", "no_sabe", "nadie_mas"]}]`
- **08, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con esto"}]`
- **08, vez 5, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **08, vez 5, paso 2** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con esto", "resuelto": false}]`
- **08, vez 5, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **08, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC"}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con esto", "pregunta": "quien_destraba"}]`
- **08, vez 5, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- **08, vez 5, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30", "es_correccion": false}]`
- **08, vez 5, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:8b119b4c-a9c8-4c67-8fa3-99db74d2d48b", "outbox_id": null}]`
- **08, vez 5, paso 3** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC", "desde_antes": true}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": true}`
- **08, vez 5, paso 3** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **08, vez 5, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 5, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 5, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **09, vez 1:** la corrida se cayó:

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

- **09, vez 1, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **09, vez 1, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **09, vez 1, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 1, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **09, vez 1, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 2:** la corrida se cayó:

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

- **09, vez 2, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **09, vez 2, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **09, vez 2, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 2, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **09, vez 2, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 3:** la corrida se cayó:

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

- **09, vez 3, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **09, vez 3, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **09, vez 3, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 3, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **09, vez 3, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 4:** la corrida se cayó:

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

- **09, vez 4, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **09, vez 4, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **09, vez 4, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 4, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **09, vez 4, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 5:** la corrida se cayó:

```
LookupError: No hay un botón de COM para tocar.
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 227, in correr
    resultado, r.texto, r.jugadas, r.latencia_ms, r.jev = self._turno(paso, ia, preludio)
                                                          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 268, in _turno
    token, etiqueta = self._token(persona["membership_id"], paso["toca"])
                      ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion\prueba_chica\corredor.py", line 308, in _token
    raise LookupError(f"No hay un botón de {clave} para tocar.")

```

- **09, vez 5, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **09, vez 5, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **09, vez 5, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **09, vez 5, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **09, vez 5, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 1, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **10, vez 1, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **10, vez 1, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 1, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **10, vez 1, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **10, vez 2, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **10, vez 2, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **10, vez 2, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 2, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **10, vez 2, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **10, vez 3, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **10, vez 3, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **10, vez 3, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 3, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **10, vez 3, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **10, vez 4, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **10, vez 4, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **10, vez 4, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 4, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **10, vez 4, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **10, vez 5, paso 1** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **10, vez 5, paso 1** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **10, vez 5, paso 1** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 5, paso 1** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **10, vez 5, paso 1** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **10, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **11, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- **11, vez 1, paso 3** [garantia] efecto de más: estado: esperado `{}`; real `{"COM": "bloqueada"}`
- **11, vez 1, paso 3** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "COM", "causa": "espero el switch", "resuelto": false}]`
- **11, vez 1, paso 3** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- **11, vez 1, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- **11, vez 1, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- **11, vez 1, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch", "es_correccion": false}]`
- **11, vez 1, paso 4** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- **11, vez 1, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **11, vez 4, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision", "tarea_correcta": "COM"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- **11, vez 4, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "no_se_puede", "motivo": "misma_tarea", "tarea": "COM"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **11, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- **11, vez 5, paso 3** [garantia] efecto de más: estado: esperado `{}`; real `{"COM": "bloqueada"}`
- **11, vez 5, paso 3** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "COM", "causa": "espero el switch", "resuelto": false}]`
- **11, vez 5, paso 3** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- **11, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- **11, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30"}]`
- **11, vez 5, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": null, "es_correccion": false}]`
- **11, vez 5, paso 4** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- **11, vez 5, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **12, vez 1, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Saber si avisaste a alguien."}]`
- **12, vez 1, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 2, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "saber si le avisaron a alguien sobre el recordatorio del turno médico"}]`
- **12, vez 2, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 3, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Preguntar si le avisaron a alguien sobre que prevé no poder ocuparse de Programar PLC de la comprimidora"}]`
- **12, vez 3, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 4, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Saber si eso se lo avisaste a alguien."}]`
- **12, vez 4, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 5, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "saber si le avisaste a alguien"}]`
- **12, vez 5, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **13, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 1, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 1, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 1, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 2, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "en_curso"}`
- **13, vez 2, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- **13, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[]`
- **13, vez 2, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **13, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 3, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 3, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 3, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 4, paso 2** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "en_curso"}`
- **13, vez 4, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 4, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC", "estado": "en_curso"}]`
- **13, vez 4, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[]`
- **13, vez 4, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 4, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[]`
- **13, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 5, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 5, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 5, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "elegir", "opcion": "O1"}]`
- **13, vez 5, paso 3** [comprension] falta un efecto: estado: esperado `{"PLC": "en_curso"}`; real `{}`
- **13, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "anotado", "tarea": "PLC"}]`; real `[{"jugada": "elegir", "resultado": "no_se_puede", "motivo": "sin_opciones"}]`
- **15, vez 1, paso 5** [comprension] jugadas: esperado `[{"nombre": "informar_avance", "tarea": "PLC", "palabras": "todo en orden, sigo con eso"}]`; real `[]`
- **15, vez 1, paso 5** [comprension] falta un efecto: avance: esperado `[{"tarea": "PLC"}]`; real `[]`
- **15, vez 1, paso 5** [comprension] falta un efecto: aviso guardado: esperado `[{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "guardado"}]`; real `[]`
- **15, vez 1, paso 5** [motor] incidente: esperado `[]`; real `[{"etapa": "turno_conversacion", "severidad": "media"}]`
- **15, vez 1, paso 5** [comprension] la pregunta de la respuesta: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `null`
- **15, vez 1, paso 5** [comprension] hechos: esperado `[{"jugada": "informar_avance", "resultado": "anotado", "tarea": "PLC", "veces_sin_algo_cierto": 2, "vuelve_a_pedir_el_estado": {"estado": "guardado_sin_enviar", "sale": "~2026-10-29"}, "vencida": {"fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 1}, "pregunta": "fecha_de_la_tarea"}]`; real `[]`
- **15, vez 1, paso 5** [comprension] pregunta abierta después: esperado `{"tipo": "fecha_de_la_tarea", "tarea": "PLC"}`; real `{"tipo": "estado_de_la_tarea", "tarea": "PLC"}`
- **15, vez 1, paso 7** [motor] aviso en el estado: esperado `{"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "omitido", "motivo": "ya_respondio"}`; real `[{"tipo": "aviso_previo", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "vencimiento_proximo", "tarea": "PLC", "vence": "2026-10-27", "necesita_respuesta": false, "dias_habiles_hasta_el_vencimiento": 3}, "outbox_id": "87c47567-412a-4c32-af77-840a51624cde"}, {"tipo": "nueva_prevision", "tarea": "PLC", "a": "Ismael", "estado": "enviado", "motivo": null, "hechos": {"tarea": "PLC", "motivo": null, "prevision": "2026-11-03", "responsable": "Marcos Tarquini", "dependientes": ["COM"], "fecha_comprometida": "2026-10-27", "atraso_dias_habiles": 5}, "outbox_id": "221d536d-9392-4cfb-b2b5-05bb42249c06"}, {"tipo": "pedido_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "pedido_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "numero": 1, "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "necesita_respuesta": true, "atraso_dias_habiles": 0}, "outbox_id": "576011a2-92d7-4756-a8c9-98ac0ed64f09"}, {"tipo": "repregunta_de_estado", "tarea": "PLC", "a": "Marcos", "estado": "enviado", "motivo": null, "hechos": {"aviso": "repregunta_de_estado", "tarea": "PLC", "vence": "2026-10-27", "estado": "en_curso", "dependientes": [{"tarea": "COM", "no_puede_arrancar_hasta_que_termine": true}], "avance_anterior": {"el": "2026-10-27", "dijo": "voy bien, la tengo casi lista"}, "espera_algo_cierto": ["si_la_termino", "para_cuando_la_termina", "si_esta_trabada"], "necesita_respuesta": true, "atraso_dias_habiles": 1}, "outbox_id": "4d44c424-ef95-4087-953f-0da2ed97c2d3"}]`
- **15, vez 3, paso 6** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03"}]`; real `[{"nombre": "anotar_prevision", "tarea": "PLC", "fecha": "2026-11-03", "motivo": "para el martes 3 la tengo"}]`
- **15, vez 3, paso 6** [garantia] efecto de más: previsión: esperado `[{"tarea": "PLC", "fecha": "2026-11-03", "motivo": "ausente"}]`; real `[{"tarea": "PLC", "fecha": "2026-11-03", "motivo": "para el martes 3 la tengo", "es_correccion": false}]`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 4321 | 6899 |
| 02 | 5 | 7236 | 10505 |
| 03 | 15 | 6114 | 12101 |
| 05 | 15 | 8358 | 11688 |
| 06 | 10 | 4990 | 6064 |
| 07 | 10 | 5073 | 8288 |
| 08 | 15 | 5350 | 7272 |
| 09 | 5 | 4952 | 7118 |
| 10 | 10 | 4421 | 5672 |
| 11 | 20 | 5586 | 12407 |
| 12 | 30 | 5652 | 14451 |
| 13 | 10 | 5384 | 8793 |
| 14 | 10 | 3808 | 6642 |
| 15 | 15 | 7541 | 17875 |
| 16 | 10 | 7980 | 17984 |
| **Todas** | 185 | 5703 | 17984 |

## Costo

- Llamadas a la IA: 587 (0 con el costo estimado); tokens de entrada 806920, de salida 126563.
- Jev: 0 llamadas, USD 0.0000 (estimado).
- **Total de la ronda: USD 0.1371.**
