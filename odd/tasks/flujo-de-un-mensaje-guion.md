# Guion de la prueba real, corte 1 (alta guiada)

Base `prisma_flujo` (esquema completo, paquete, feriados, semilla ficticia, modelo
`nan`/`deepseek-v4-flash`, variante `redaccion` = B). Cuentas vinculadas: Ariel, Ismael,
Marcos. Listener del worktree (`PYTHONPATH=src`).

Por cada paso, anotar: **mejoró / empeoró / igual** respecto de la ronda 4, y si la
respuesta tardó (sí / no). Los mensajes son ejemplos: escribirlos como los escribiría
la persona, desprolijos.

| # | Quién | Mensaje | Qué se espera | Hallazgo | Resultado |
|---|---|---|---|---|---|
| 1 | Marcos | "quiero crear una tarea nueva" | Pregunta primero qué hay que hacer, sin "(hasta N)" | R4c-H4, H7 | |
| 2 | Marcos | "revisar el variador de la comprimidora" | Lo toma como título y pasa al objetivo con botones | R4c-H4 | |
| 3 | Marcos | El objetivo escrito con sus palabras, sin tocar el botón | Lo entiende; no dice "No encontré esa opción" | R4c-H4 | |
| 4 | — | (Marcos sólo puede asignar en OT) | No pregunta el área; aparece en el resumen | R4c-H10 | |
| 5 | Marcos | Fecha: "4de octubre" | La acepta y la muestra | R4c-H6 | |
| 6 | Marcos | En otra alta: "04 / 10", "el viernes", "la semana que viene" | Las acepta y muestra la fecha interpretada | R4c-H6 | |
| 7 | Marcos | Una fecha pasada: "ayer" | Dice por qué no sirve y qué sirve, sin jerga | R4c-H6 | |
| 8 | Marcos | A mitad del alta: "ah, y necesito otra tarea para Nahuel" | No reinicia ni entra en bucle: una sola pregunta por la rama | R4c-H5 | |
| 9 | Marcos | Llegar al resumen | Sin claves internas, sin "Sin descripción", el cierre coincide con "Enviar a aprobación" | R4c-H8, H9 | |
| 10 | Marcos | "necesito crear una tarea: calibrar los sensores de la línea 2" | Toma el título y salta al objetivo | R4c-H4 | |
| 11 | Ariel | Alta para sí mismo, hasta Confirmar | El cierre dice "Con Confirmar se crea la tarea…"; la tarea queda creada | R4c-H9 | |

**Huecos conocidos (no son hallazgos nuevos):**

- El objetivo más probable primero (⭐) no está construido: los objetivos salen en el
  orden de siempre.
- Una fecha relativa en el primer mensaje ("…para el viernes") no se toma todavía: se
  pregunta después.
- Los tipos de evidencia salen sin tilde ("explicacion").
- Fuera del horario laboral, lo que inicia Prisma (el borrador que le llega a Ismael)
  queda en la cola hasta las 09:00 (R4b-H6). Las respuestas a lo que uno escribe salen
  en el momento.

**Además registrar:** incidentes nuevos (`python -m prisma incidentes corework`), y
cualquier respuesta que se sienta robótica aunque no esté en la lista: se anota y se
clasifica por etapa del ADR 0014, sin corregir durante la prueba (moratoria).
