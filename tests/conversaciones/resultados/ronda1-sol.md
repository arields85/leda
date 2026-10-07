# Ronda ronda1-sol

- **Fecha:** 2026-10-05 19:30
- **Commit:** 3bc32b5
- **IA:** openrouter/openai/gpt-6-sol
- **Veces:** 5
- **Jev:** sí
- **Gasto de la etapa:** USD 2.61 de 30
- **Transcripciones:** [ronda1-sol-transcripciones.md](ronda1-sol-transcripciones.md)

## Resultado por conversación

G: garantías (5b, se comprueban solas). C: comprensión automática, **provisional** (jugadas y efectos; la lectura del usuario es la que vale, 10.3). M: lo que hace el código con las jugadas esperadas.

| Conversación | Vez 1 | Vez 2 | Vez 3 | Vez 4 | Vez 5 | Garantías | Comprensión (provisional) | Lectura del usuario |
|---|---|---|---|---|---|---|---|---|
| 01 Arranqué (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 02 Llego el 27, el proveedor se demoró (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 03 Estoy trabado, falta el repuesto (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 04 No contesta (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 05 Varias cosas en un mensaje (garantias) | G FALLA · C FALLA · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G FALLA · C FALLA · M ok | 3/5 | 3/5 |  |
| 06 No, era la otra tarea (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 07 Dejá, no importa (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 08 Cambio de tema (garantias) | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | G FALLA · C FALLA · M FALLA | 0/5 | 0/5 |  |
| 09 Duda: ¿de qué tarea habla? (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | ERROR | 4/5 | 4/5 |  |
| 10 Escribir en lugar de tocar un botón (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 11 Algo vencido (garantias) | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | 0/5 | 0/5 |  |
| 12 Algo que no está en la lista (garantias) | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | G FALLA · C FALLA · M ok | 0/5 | 0/5 |  |
| 13 Jev: dos tareas parecidas avisadas juntas (jev) | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | G ok · C FALLA · M ok | 5/5 | 0/5 |  |
| 14 Jev: dos tareas parecidas, y el estado dice cuál (jev) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 15 Voy bien, la tengo casi lista (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |
| 16 Arranqué hoy, con la tarea vencida (garantias) | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | G ok · C ok · M ok | 5/5 | 5/5 |  |

## Fallas

- **05, vez 1, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- **05, vez 1, paso 4** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **05, vez 1, paso 4** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con el plc", "resuelto": false}]`
- **05, vez 1, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 1, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- **05, vez 1, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 1, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- **05, vez 1, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **05, vez 1, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **05, vez 1, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- **05, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05", "puede_traer": ["motivo"]}]`; real `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "con el plc"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-05"}]`
- **05, vez 5, paso 4** [garantia] efecto de más: estado: esperado `{}`; real `{"PLC": "bloqueada"}`
- **05, vez 5, paso 4** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "PLC", "causa": "con el plc", "resuelto": false}]`
- **05, vez 5, paso 4** [comprension] la pregunta de la respuesta: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC", "desde_antes": false}`
- **05, vez 5, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "falta_dato", "falta": ["causa"], "tarea": "PLC", "pregunta": "causa_del_bloqueo"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "atraso_dias_habiles": 4}]`; real `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC", "causa": "con el plc", "pregunta": "quien_destraba"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-05", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 4, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-20T16:30:00-03:00"}}]`
- **05, vez 5, paso 4** [comprension] pregunta abierta después: esperado `{"tipo": "causa_del_bloqueo", "tarea": "PLC"}`; real `{"tipo": "quien_destraba", "tarea": "PLC"}`
- **05, vez 5, paso 5** [comprension] jugadas: esperado `[{"nombre": "anotar_bloqueo", "tarea": "PLC", "causa": "falta que martin de IT me habilite el acceso a la red de planta"}, {"nombre": "anotar_quien_destraba", "quien": "martin", "puede_traer": ["tarea"]}]`; real `[{"nombre": "anotar_quien_destraba", "tarea": "PLC", "quien": "martin de IT", "no_sabe": false, "nadie_mas": false}]`
- **05, vez 5, paso 5** [comprension] falta un efecto: estado: esperado `{"PLC": "bloqueada"}`; real `{}`
- **05, vez 5, paso 5** [comprension] falta un efecto: bloqueo: esperado `[{"tarea": "PLC", "causa": "presente"}]`; real `[]`
- **05, vez 5, paso 5** [comprension] hechos: esperado `[{"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "PLC"}, {"jugada": "anotar_quien_destraba", "resultado": "anotado", "salidas": "ausente"}]`; real `[{"jugada": "anotar_quien_destraba", "resultado": "anotado", "tarea": "PLC", "quien_destraba": {"externo": "martin de IT"}}]`
- **08, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- **08, vez 1, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30", "es_correccion": false}]`
- **08, vez 1, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:cd322c6d-de85-4b8d-837d-7e5b1e9bf6bd", "outbox_id": null}]`
- **08, vez 1, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 1, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4"}]`
- **08, vez 2, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4", "es_correccion": false}]`
- **08, vez 2, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:8a8bb85c-e2e6-45d9-b9fa-1696dbe0bfc5", "outbox_id": null}]`
- **08, vez 2, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 2, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4"}]`
- **08, vez 3, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30, necesito hasta el miercoles 4", "es_correccion": false}]`
- **08, vez 3, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:bcc1d559-dabc-4c27-aa87-82a0402439fb", "outbox_id": null}]`
- **08, vez 3, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 3, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30, necesito hasta el miercoles 4", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- **08, vez 4, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30", "es_correccion": false}]`
- **08, vez 4, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:24eef773-9ac6-4f65-9f09-a569309d22b3", "outbox_id": null}]`
- **08, vez 4, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 4, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
- **08, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30"}]`
- **08, vez 5, paso 3** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "ausente"}]`; real `[{"tarea": "COM", "fecha": "2026-11-04", "motivo": "no llego al 30", "es_correccion": false}]`
- **08, vez 5, paso 3** [garantia] efecto de más: aviso guardado: esperado `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}]`; real `[{"tipo": "nueva_prevision", "tarea": "COM", "a": "Ismael", "estado": "guardado", "motivo": null, "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}, "clave": "motor:nueva_prevision:fa57aff7-9d7b-4dab-8a97-cf896dd01b39", "outbox_id": null}]`
- **08, vez 5, paso 4** [motor] no salió lo esperado: esperado `{"a": "Ismael", "tipo": "nueva_prevision", "tarea": "COM", "hechos": {"prevision": "2026-11-04", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "motivo": "ausente"}}`; real `[{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}]`
- **08, vez 5, paso 4** [motor] salió algo de más: esperado `null`; real `{"a": "Ismael", "tipo": "nueva_prevision", "tareas": ["COM"], "el": "2026-10-20", "hechos": {"tarea": "COM", "motivo": "no llego al 30", "prevision": "2026-11-04", "responsable": "Marcos Tarquini", "dependientes": [], "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3}}`
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
- **11, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- **11, vez 1, paso 3** [garantia] efecto de más: estado: esperado `{}`; real `{"COM": "bloqueada"}`
- **11, vez 1, paso 3** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "COM", "causa": "espero el switch", "resuelto": false}]`
- **11, vez 1, paso 3** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- **11, vez 1, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- **11, vez 1, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- **11, vez 1, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch", "es_correccion": false}]`
- **11, vez 1, paso 4** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- **11, vez 1, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **11, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- **11, vez 2, paso 3** [garantia] efecto de más: estado: esperado `{}`; real `{"COM": "bloqueada"}`
- **11, vez 2, paso 3** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "COM", "causa": "espero el switch", "resuelto": false}]`
- **11, vez 2, paso 3** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- **11, vez 2, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- **11, vez 2, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- **11, vez 2, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch", "es_correccion": false}]`
- **11, vez 2, paso 4** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- **11, vez 2, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **11, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- **11, vez 3, paso 3** [garantia] efecto de más: estado: esperado `{}`; real `{"COM": "bloqueada"}`
- **11, vez 3, paso 3** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "COM", "causa": "espero el switch", "resuelto": false}]`
- **11, vez 3, paso 3** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- **11, vez 3, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- **11, vez 3, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "informar_avance", "tarea": "COM", "palabras": "llego el switch"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30"}]`
- **11, vez 3, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": null, "es_correccion": false}]`
- **11, vez 3, paso 4** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- **11, vez 3, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "informar_avance", "resultado": "no_se_puede", "motivo": "nadie_pidio_el_estado", "tarea": "COM"}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": null, "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **11, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- **11, vez 4, paso 3** [garantia] efecto de más: estado: esperado `{}`; real `{"COM": "bloqueada"}`
- **11, vez 4, paso 3** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "COM", "causa": "espero el switch", "resuelto": false}]`
- **11, vez 4, paso 3** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- **11, vez 4, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- **11, vez 4, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- **11, vez 4, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch", "es_correccion": false}]`
- **11, vez 4, paso 4** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- **11, vez 4, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **11, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}]`; real `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-11-04", "motivo": "espero el switch"}, {"nombre": "anotar_bloqueo", "tarea": "COM", "causa": "espero el switch"}]`
- **11, vez 5, paso 3** [garantia] efecto de más: estado: esperado `{}`; real `{"COM": "bloqueada"}`
- **11, vez 5, paso 3** [garantia] efecto de más: bloqueo: esperado `[]`; real `[{"tarea": "COM", "causa": "espero el switch", "resuelto": false}]`
- **11, vez 5, paso 3** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": false}`
- **11, vez 5, paso 3** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "~2026-10-23T09:00"}}]`; real `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-11-04", "motivo": "espero el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 3, "dependientes": [], "aviso_al_referente": {"a": "Ismael Soschinski", "estado": "guardado_sin_enviar", "sale": "2026-10-23T09:00:00-03:00"}}, {"jugada": "anotar_bloqueo", "resultado": "anotado", "tarea": "COM", "causa": "espero el switch", "pregunta": "quien_destraba"}]`
- **11, vez 5, paso 4** [comprension] jugadas: esperado `[{"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "puede_traer": ["motivo"]}]`; real `[{"nombre": "corregir", "tarea": "COM", "corrige": "anotar_prevision"}, {"nombre": "cancelar"}, {"nombre": "anotar_prevision", "tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch"}]`
- **11, vez 5, paso 4** [garantia] efecto de más: previsión: esperado `[{"tarea": "COM", "fecha": "2026-10-30"}]`; real `[{"tarea": "COM", "fecha": "2026-10-30", "motivo": "llego el switch", "es_correccion": false}]`
- **11, vez 5, paso 4** [comprension] la pregunta de la respuesta: esperado `null`; real `{"tipo": "quien_destraba", "tarea": "COM", "desde_antes": true}`
- **11, vez 5, paso 4** [comprension] hechos: esperado `[{"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "sin_aviso": "misma_fecha_comprometida"}]`; real `[{"jugada": "corregir", "resultado": "corregido", "corrige": "anotar_prevision", "tarea": "COM", "vuelve_a": {"fecha_comprometida": "2026-10-30"}, "prevision_corregida": "2026-11-04", "aviso_de_la_prevision_corregida": {"estado": "retirado_sin_enviar"}}, {"jugada": "cancelar", "resultado": "no_se_puede", "motivo": "la_pregunta_espera_respuesta", "pregunta": {"tipo": "quien_destraba", "tarea": "COM"}}, {"jugada": "anotar_prevision", "resultado": "anotado", "tarea": "COM", "prevision": "2026-10-30", "motivo": "llego el switch", "fecha_comprometida": "2026-10-30", "atraso_dias_habiles": 0, "dependientes": [], "aviso_al_referente": null, "sin_aviso": "misma_fecha_comprometida"}]`
- **12, vez 1, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaron a alguien sobre el pedido de recordatorio del turno con el médico"}]`
- **12, vez 1, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 2, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si se le avisó a alguien sobre su pedido de recordatorio del turno médico"}]`
- **12, vez 2, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 3, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaste a alguien sobre su pedido de recordatorio del turno médico"}]`
- **12, vez 3, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 4, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaron a alguien sobre el pedido de recordatorio del turno médico."}]`
- **12, vez 4, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **12, vez 5, paso 5** [comprension] jugadas: esperado `[]`; real `[{"nombre": "fuera_de_la_lista", "que_pide": "Pregunta si le avisaste a alguien sobre el pedido de recordarle el turno con el médico."}]`
- **12, vez 5, paso 5** [garantia] aviso al administrador de más: esperado `0`; real `1`
- **13, vez 1, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 1, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 1, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 1, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 1, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 1, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 2, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 2, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 2, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 2, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 2, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 2, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 3, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 3, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 3, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 3, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 3, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 3, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 4, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 4, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 4, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 4, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 4, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 4, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`
- **13, vez 5, paso 2** [comprension] jugadas: esperado `[{"nombre": "anotar_inicio"}]`; real `[]`
- **13, vez 5, paso 2** [comprension] botones: esperado `["PLC", "COM"]`; real `[]`
- **13, vez 5, paso 2** [comprension] la pregunta de la respuesta: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 5, paso 2** [comprension] hechos: esperado `[{"jugada": "anotar_inicio", "resultado": "falta_dato", "falta": ["tarea"], "pregunta": "cual_tarea"}]`; real `[]`
- **13, vez 5, paso 2** [comprension] pregunta abierta después: esperado `{"tipo": "cual_tarea"}`; real `null`
- **13, vez 5, paso 3** [comprension] jugadas: esperado `[{"nombre": "elegir", "opcion": "PLC"}]`; real `[{"nombre": "anotar_inicio", "tarea": "PLC"}]`

## Latencia por turno

Lo que tarda un turno de una persona, de que llega el mensaje a la respuesta encolada (las dos llamadas a la IA). Sin umbral (sección 6).

| Conversación | Turnos | Mediana (ms) | Peor (ms) |
|---|---|---|---|
| 01 | 5 | 6557 | 7137 |
| 02 | 5 | 10312 | 13125 |
| 03 | 15 | 6997 | 9921 |
| 05 | 15 | 8775 | 17077 |
| 06 | 10 | 5880 | 8882 |
| 07 | 10 | 4715 | 7070 |
| 08 | 15 | 5536 | 11435 |
| 09 | 9 | 5212 | 7042 |
| 10 | 10 | 4797 | 5455 |
| 11 | 20 | 6387 | 13241 |
| 12 | 30 | 6585 | 11082 |
| 13 | 10 | 5370 | 8255 |
| 14 | 10 | 4682 | 5661 |
| 15 | 15 | 6436 | 9343 |
| 16 | 10 | 7642 | 9381 |
| **Todas** | 189 | 6312 | 17077 |

## Costo

- Llamadas a la IA: 579 (0 con el costo estimado); tokens de entrada 807715, de salida 79199.
- Jev: 35 llamadas, USD 0.3500 (estimado).
- **Total de la ronda: USD 2.6127.**

## Jev contra la IA (decisión 7)

Jev corre en paralelo y no decide nada. Correcta: lo que el paso espera (`preguntar` o la tarea).

| Conv. | Vez | Paso | Referencia | Correcta | IA | Jev | Probabilidades | IA acierta | Jev acierta |
|---|---|---|---|---|---|---|---|---|---|
| 13 | 1 | 2 | la de la comprimidora | preguntar | None | ambigua | {"PLC": 0.93, "COM": 0.06, "ARI": 0.01} | FALLA | ok |
| 13 | 2 | 2 | la de la comprimidora | preguntar | None | ambigua | {"PLC": 0.92, "COM": 0.07, "ARI": 0.01} | FALLA | ok |
| 13 | 3 | 2 | la de la comprimidora | preguntar | None | ambigua | {"COM": 0.06, "PLC": 0.93, "ARI": 0.01} | FALLA | ok |
| 13 | 4 | 2 | la de la comprimidora | preguntar | None | ambigua | {"PLC": 0.92, "ARI": 0.01, "COM": 0.07} | FALLA | ok |
| 13 | 5 | 2 | la de la comprimidora | preguntar | None | ambigua | {"COM": 0.05, "PLC": 0.94, "ARI": 0.01} | FALLA | ok |
| 13 | 1 | 3 | la del plc | PLC | PLC | ambigua | {"ARI": 0.0, "COM": 0.03, "PLC": 0.97} | ok | FALLA |
| 13 | 2 | 3 | la del plc | PLC | PLC | ambigua | {"COM": 0.02, "ARI": 0.0, "PLC": 0.98} | ok | FALLA |
| 13 | 3 | 3 | la del plc | PLC | PLC | ambigua | {"ARI": 0.0, "COM": 0.03, "PLC": 0.97} | ok | FALLA |
| 13 | 4 | 3 | la del plc | PLC | PLC | ambigua | {"ARI": 0.0, "COM": 0.03, "PLC": 0.97} | ok | FALLA |
| 13 | 5 | 3 | la del plc | PLC | PLC | ambigua | {"PLC": 0.97, "COM": 0.03, "ARI": 0.0} | ok | FALLA |
| 14 | 1 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"COM": 0.11, "PLC": 0.89} | ok | FALLA |
| 14 | 2 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"COM": 0.13, "PLC": 0.87} | ok | FALLA |
| 14 | 3 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"COM": 0.11, "PLC": 0.89} | ok | FALLA |
| 14 | 4 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"COM": 0.11, "PLC": 0.89} | ok | FALLA |
| 14 | 5 | 2 | la de la comprimidora | PLC | PLC | ambigua | {"PLC": 0.87, "COM": 0.13} | ok | FALLA |
| 14 | 1 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"PLC": 0.63, "COM": 0.37} | ok | FALLA |
| 14 | 2 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"COM": 0.4, "PLC": 0.6} | ok | FALLA |
| 14 | 3 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"PLC": 0.49, "COM": 0.51} | ok | FALLA |
| 14 | 4 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"COM": 0.45, "PLC": 0.55} | ok | FALLA |
| 14 | 5 | 3 | la otra de la comprimidora | COM | COM | ambigua | {"COM": 0.36, "PLC": 0.64} | ok | FALLA |
