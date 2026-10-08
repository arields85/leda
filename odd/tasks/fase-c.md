# Fase C: lo que a Leda le falta por chat

**Rama:** `feat/motor-de-conversacion` · **Abierta:** 2026-10-07 · **Copia en Engram:** tema
`odd/fase-c/tasks` (proyecto `prisma-pm`)

Documento de la unidad. Viene de `odd/tasks/motor-definitivo.md` ("Fase C") y del ADR 0017 (decisión 3b).

## Objetivo

Que Leda complete el seguimiento por chat: recibir la entrega con su evidencia, recibir la aprobación o el
pedido de cambios, perseguir un bloqueo de persona en persona y pedir el estado con el ritmo del espacio.
Después, delegar.

## Por qué

Sin entrega y aprobación, una tarea nunca se cierra por chat ("ya la terminé" hoy no tiene camino:
`fichas.py`, `_entregar`, `ninguna_definida`). Y el bloqueo se anota, pero nadie lo persigue.

## Orden (usuario, 2026-10-07: la Fase C va antes que la plataforma web)

1. **Entrega y aprobación** (circuitos 7 y 8), juntas. Traen lo que necesita el resto: la confirmación
   con la guarda escrita (ADR 0018, decisión 2) y los avisos a otras personas hechos por el motor.
2. **La persecución del bloqueo** (3a).
3. **Los pedidos de estado con ritmo fijo** (circuito 5), con el tope diario y la consolidación.
4. **Delegar**, que antes necesita su enmienda al ADR 0017 (decisión 2) y una operación nueva.

## Lo que existe hoy (relevamiento del 2026-10-07)

- **Entrega:** `entregar` está en la lista de jugadas, pero responde `no_por_chat`. La cocina tiene
  `actualizar_estado(en_revision, evidencia_texto=…)` y `adjuntar_evidencia`, con la política de evidencia
  por área. El aviso al aprobador sale con texto fijo, fuera del motor (`_notificar_entrega_al_aprobador`).
  La evidencia se cuenta con una sola fila, sin mirar cada tipo que pide la política. Una foto sin texto
  se ignora.
- **Aprobación:** sin ficha. La cocina tiene `aprobar_tarea` y `pedir_cambios_tarea`, con la autoridad un
  nivel arriba (`aprobador_membership_id`) y sus avisos de texto fijo.
- **Bloqueo:** se anota y se pregunta quién lo destraba (`blocker_unblocker`). Nadie le escribe después a
  esa persona, ni se encadenan los bloqueos, ni se avisa hacia abajo al destrabar. El escalamiento de un
  bloqueo viejo (5 días en CoreWork) no se aplica en el motor.
- **Cadencias:** borradas en la E3-7. Quedan `cadence_job` (cargado del pack) y `pending_reply`.
- **Delegar:** sólo diseño.
- **Conversaciones de prueba:** la 03, la 05, la 08 y la 17 cubren parte del bloqueo; la 12, "ya la
  terminé" sin camino; la 10 y la 11 tienen pasos de la entrega escritos, sin correr.

## Lo ya decidido que rige

- La entrega lleva confirmación (ADR 0018, decisión 4) con la guarda escrita (decisión 2).
- El cierre lo verifica el código (mecánica §5); "terminé" lleva a revisión, nunca a terminada
  (constitución §11). Leda nunca cuenta como aprobadora (mecánica §7).
- Los avisos de coordinación (entregada, aprobada, cambios pedidos) quedan fuera del tope diario
  (mecánica §10, precisión del 2026-09-30).
- El aviso al referente no habla del bloqueo en sí (ADR 0018, 9c).

## Preguntas al usuario (de a una)

1. **Evidencia:** decidida (usuario, 2026-10-07). Leda acepta texto, fotos y archivos. Se guardan en la
   base, con su huella y atados a su espacio (después se puede mover el almacenamiento sin cambiar lo
   demás). El aviso a quien aprueba lleva las fotos adjuntas y un enlace a una página de la tarea, de
   sólo lectura, con su evidencia y su historia, como el tablero de hoy: enlace personal y sólo lo que esa
   persona puede ver. La página es el primer pedazo de la plataforma: lleva su ADR corto antes del código.
   Propuesta del usuario ("que se guarden en la plataforma y Leda envíe el enlace"), con los ajustes del
   agente que aceptó: fotos adjuntas en el aviso, la base como almacenamiento y el ADR primero.
2. **La aprobación escrita:** decidida (usuario, 2026-10-07). Lo claro va directo, sin vista previa: es la
   decisión de quien aprueba. Si mezcla aprobar y pedir un cambio ("aprobado, pero que revise el cable"),
   Leda pregunta una sola vez cuál de las dos, con dos botones, porque admite dos lecturas (constitución
   §8).
3. **Quien aprueba no contesta:** decidida (usuario, 2026-10-07). Un recordatorio al día hábil siguiente
   y otro al segundo. Al tercero, si tiene a alguien arriba (Marcos → Ismael), se le avisa a ese que la
   aprobación está trabada; si no hay nadie arriba, un recordatorio cordial por día. Al responsable no se
   le avisa: no depende de él. **Precisada por el usuario el mismo día** (al escribir la conversación
   24): el segundo recordatorio le avisa a quien aprueba que al día siguiente se entera quien está arriba.
   El aviso a quien está arriba es **sólo informativo**: no le pide nada ni lo convierte en aprobador ("no
   sobrecargar a Ismael; el responsable del sector se hace cargo de las tareas de su gente"). Quien aprueba
   sigue con un recordatorio cordial por día hasta decidir, y cuando decide, a quien está arriba le llega
   que se destrabó.
   - **Una aprobación que todavía no puede cerrar** (por ejemplo, la tarea espera otra que no terminó):
     queda registrada, y cuando lo que faltaba se resuelve, el código vuelve a comprobar y la cierra sola,
     con aviso al responsable y a quien aprobó (usuario, 2026-10-07).
   - **El aviso de una entrega ofrece los botones Aprobar y Pedir cambios** como atajos (usuario,
     2026-10-07). "Aprobar" aprueba con un toque; "Pedir cambios" pregunta qué falta. Escribir vale igual.
   - **Un mismo texto puede cubrir varios tipos de evidencia** ("terminé, lo probé 20 ciclos sin falla" es
     explicación y resultado de la prueba): la vista previa de la entrega dice qué cubre cada pieza y la
     persona lo confirma o lo corrige (usuario, 2026-10-07).
4. **Escribirle a quien destraba:** ¿directo, o preguntándole antes a quien lo nombró (constitución §7,
   atribución)? `PENDIENTE`.
5. **Quien destraba dice que no le corresponde:** ¿a quién va Leda? `PENDIENTE`.
6. **Bloqueos encadenados:** ¿se enlazan solos, con aviso hacia abajo al destrabar? `PENDIENTE`.
7. **El bloqueo viejo:** ¿vuelve el escalamiento a los 5 días, o alcanza la escalera de quien destraba?
   `PENDIENTE`.
8. **Cadencias:** ¿un mensaje por persona o uno por tarea, y reemplazan o se suman a la escalera de cada
   tarea? `PENDIENTE`.
9. **Delegar:** ¿el referente confirma o sólo se entera? `PENDIENTE`.

## Chequeo de rumbo (2026-10-07)

- **Clase:** circuitos nuevos sobre el motor que ya funciona; no es un hallazgo de conversación.
- **Mecanismo o caso:** mecanismo. Cada circuito es una ficha; la confirmación escrita y los avisos a otras
  personas se resuelven una vez y sirven para todos.
- **Cocina o frases al mozo:** cocina. Las operaciones existen en `herramientas.py`; falta que el motor las
  use y que sus avisos pasen por el motor (hechos que redacta la IA), no por textos fijos.
- **Qué lo demuestra:** las conversaciones de prueba de cada circuito contra la IA real, y una pasada por
  Telegram.

## Tareas

- [x] **C-1.** Las preguntas 1 a 3, decididas por el usuario (2026-10-07).
- [x] **C-1b.** El ADR 0019, la evidencia y la página de la tarea: aceptado por el usuario (2026-10-07),
  con cinco decisiones más (Ismael ve todas las páginas; resultado de prueba por texto; comprimidos y
  proyectos sin abrirlos; lo mandado antes cuenta si se incluye; videos, 60 MB con 20 MB por ahora).
- [x] **C-2.** Conversaciones de prueba de la entrega y la aprobación (2026-10-07, `47ccf57`):
  `tests/conversaciones/21-entrega-con-evidencia.md`, `22-falta-evidencia.md`, `23-aprobacion.md` y
  `24-quien-aprueba-no-contesta.md`, listadas en su README. Sólo el `.md`, sin YAML: no corren hasta
  la C-3. `pytest tests/conversaciones`: 105 passed. Los `PENDIENTE` que dejan están marcados en cada
  paso.
- [ ] **C-3.** Fichas de la entrega y la aprobación, la confirmación escrita y los avisos por el motor, en
  las cinco porciones del ADR 0019.
  - [x] Porción 1, recibir y guardar archivos (2026-10-07): `cdf7cfe`, `c21b1af` (migración `0033`,
    tablas `archivo` y `archivo_de_mensaje`, RLS forzado, sólo agregar), `a003c72`, `22988ee` (fotos,
    documentos, videos y álbumes por Telegram, límites de tamaño y de tipo por el contenido). Revisiones
    `review-bd65d58fcfca3c13` y `review-0a9143b546985a4f`. Suite completa 1317. Route: delegada (escritor
    único, 2+ archivos). La evidencia de la entrega va en otra migración.
  - [ ] Porción 2: la entrega con evidencia y la política por tipo.
  - [ ] Porción 3: el aviso a quien aprueba con fotos y botones.
  - [ ] Porción 4: la página de la tarea y su enlace.
  - [ ] Porción 5: el acceso del administrador.
- [ ] **C-4.** Regresión con la IA real y prueba por Telegram.
- [ ] **C-5.** La persecución del bloqueo (preguntas 4 a 7, conversación de prueba, ficha y prueba).
- [ ] **C-6.** Las cadencias (pregunta 8).
- [ ] **C-7.** Delegar (pregunta 9 y su enmienda al ADR 0017).

## Próximo paso

La porción 2 de C-3, después de la regresión pendiente y del hallazgo del aviso en medio de una
conversación (`docs/STATUS.md`, "Punto exacto para retomar").
