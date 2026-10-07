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
   le avisa: no depende de él.
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
- [ ] **C-1b.** El ADR de la evidencia y la página de la tarea, aceptado por el usuario.
- [ ] **C-2.** Conversaciones de prueba de la entrega y la aprobación.
- [ ] **C-3.** Fichas de la entrega y la aprobación, la confirmación escrita y los avisos por el motor.
- [ ] **C-4.** Regresión con la IA real y prueba por Telegram.
- [ ] **C-5.** La persecución del bloqueo (preguntas 4 a 7, conversación de prueba, ficha y prueba).
- [ ] **C-6.** Las cadencias (pregunta 8).
- [ ] **C-7.** Delegar (pregunta 9 y su enmienda al ADR 0017).

## Próximo paso

El ADR de la evidencia y la página de la tarea (C-1b), y en paralelo las conversaciones de prueba de la
entrega y la aprobación (C-2).
