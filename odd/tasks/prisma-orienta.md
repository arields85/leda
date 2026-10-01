# Prisma orienta

**Estado:** cerrado como feature; los hallazgos abiertos de la ronda 4 pasan a ser el
guion de prueba del ADR 0014.
**Creado:** 2026-09-25 · **Condensado:** 2026-09-30
**Origen:** [`ADR 0007`](../../docs/decisions/0007-prisma-orienta-no-charla.md);
acciones por tarea en `docs/architecture/interpretacion-y-confirmacion.md` §4.6.

**Diario completo** (cuatro rondas por Telegram, decisiones, evidencia, revisiones y rutas
por tarea, 5438 líneas, copia literal de este documento antes de condensarlo):
[`docs/historial/prisma-orienta-diario-hasta-2026-09-30.md`](../../docs/historial/prisma-orienta-diario-hasta-2026-09-30.md).

## Objetivo

Que Prisma oriente a las personas con opciones concretas en lugar de preguntas abiertas:
cada respuesta que espera algo cierra con botones y una salida, las listas de tareas son
botones y tocar una tarea ofrece lo que se puede hacer con ella.

## Estado final (2026-09-30)

Construido sobre `main`, cada unidad con pruebas. Todo el código quedó revisado por RDD
hasta `d4eefc7` (`review-cb3deef4705ea11f`, aprobada y reconocida), incluido el arnés
del banco `ffe4e85`, sobre el que la revisión dejó dos advertencias (en `docs/STATUS.md`).
Detalle en el diario.

- **T1-T4b** (commits `c253d27` a `9681973`): opciones del modelo (`ofrecer_opciones`),
  menú de tarea por estado y relación, autoridad por tarea en `actualizar_estado`,
  `registrar_bloqueo` y `adjuntar_evidencia` (T2b), listas como botones, banco con toques
  y comprobador de pregunta con opciones, cierre genérico sin opciones concretas.
- **T6/T6a-T6k** (migraciones `0013` a `0016`, ADR 0009): entrega con evidencia y
  revisión; "Pedir cambios" devuelve la tarea al estado previo, pide evidencia nueva,
  el aviso no se duplica ni se pierde, los actos sobre una tarea se serializan.
- **T7-T7c**: base nueva y siembra reproducible (`sembrar`) para la ronda 3.
- **T8** (`beda9a5`, `6c3c936`, `9818354`): latencia; clave por proveedor, ciclo del
  responder que corta, tope de 20 s con reintentos; el ruteo en paralelo (ADR 0012) se
  probó y se revirtió (`ccf5c73`).
- **T9** (ADR 0013): pregunta pendiente como contexto con comandos cerrados (R1a, R1b).
- **Ronda 4** (2026-09-30): R4-H7 y R4-H8, avisos de coordinación fuera del tope
  (migración `0024`, `b92ad89`), Rechazar con motivo (migración `0025`, `9d3ac54`),
  mensaje editado ignorado (`0665496`), íconos y encabezado del menú (`92765af`,
  `ac10063`), etiquetas de botón enteras (`4fc1365`), arnés del banco (`ffe4e85`).
- **Pruebas** (2026-09-30): suite 2279 passed, 333 deselected; banco real completo
  (n=1) 108/111, tres fallas explicadas. Circuitos A y B completos en vivo; C hasta
  "Enviar a aprobación".

Sin cerrar (no bloquean): T5 (continuidad documental de la feature), T8d, T9 (R1c en
adelante), T10 y T11 (cuarta ronda, circuito C); el diario los detalla y el ADR 0014 los
reordena.

## Hallazgos pendientes de la ronda 4: guion de prueba del ADR 0014

No es una lista de correcciones: rige la moratoria de parches de conversación. Se usan
como casos de la prueba A/B de [`ADR 0014`](../../docs/decisions/0014-flujo-de-un-mensaje.md)
y se clasifican por etapa del flujo.

- R4b-H1. "quiero entregar el dash de lotes": el modelo pidió la evidencia con sus
  palabras, sin intentar el cambio, con botones de lista.
- R4b-H2. El aviso a Ismael arranca con "👋 Buenas tardes" en un bloque aparte.
- R4b-H3. Los botones del aviso (Aprobar, Pedir cambios) sin íconos.
- R4b-H4. Evidencia mostrada como "- (texto) https://…".
- R4b-H5. **Medio-alto.** A "¿Qué falta corregir en «X»?", "necesito capturas de pantalla"
  recibe "Eso todavía no lo puedo hacer." (con una pregunta abierta, el mensaje es la
  respuesta).
- R4b-H6. Aviso "Ismael pidió cambios…" programado para el día siguiente por estar fuera
  de horario laboral (regla vigente).
- R4b-H7. Incidente `entrega_mensaje`: el resumen "Estado del equipo" falla con "chat not
  found" (el bot no está en el grupo); configuración a decidir.
- R4c-H1. **Medio.** Tras "Pedir cambios", la reentrega exige dos confirmaciones
  (agregar evidencia y luego "Ya la terminé").
- R4c-H2. **Medio.** La vista previa de "Aprobar" ofrece ✏️ Modificar y no deja ver la
  evidencia antes de aprobar.
- R4c-H3. **Alto.** "quiero ver la evidencia de la tarea de ariel" responde que no puede
  mostrarla (falso), y la aclaración ofrece una tarea sin evidencia.
- R4c-H4. **Alto (uso).** "quiero crear una tarea nueva" empieza por el objetivo antes de
  preguntar qué hay que hacer (orden decidido: primero "¿Qué hay que hacer?").
- R4c-H5. Bucle al volver a pedir una tarea nueva a mitad del alta.
- R4c-H6. **Medio.** Fechas como "4de octubre" o "04 / 10" rechazadas sin decir qué
  formato sirve.
- R4c-H7. **Medio.** Jerga en cada campo: "(hasta 200)", "(hasta 64)", "(hasta 500)".
- R4c-H8. **Medio.** El resumen muestra claves internas ("explicacion,
  resultado_de_prueba, captura, archivo").
- R4c-H9. **Bajo.** El resumen dice "Al confirmar se comprometen todos los datos
  mostrados." aunque el botón es Enviar a aprobación; muestra "Sin descripción" sin
  haberla preguntado.
- R4c-H10. Se pregunta "Elegí el área." con una sola opción real: un dato con una sola
  opción posible no se pregunta.

A observar el 01/10 a las 09:00: Rechazar con motivo del circuito C y si el despachador
descarta los avisos que dejaron de corresponder (tres de «Dashboard de lotes»).

Orden de trabajo vigente: `docs/STATUS.md`, "Próximo paso".
