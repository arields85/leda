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
4. **Escribirle a quien destraba:** decidida (usuario, 2026-10-08, opción A). Leda le escribe directo,
   como Leda y no en nombre de quien está trabado, y a éste le dice en el mismo mensaje que le pregunta y
   le avisa apenas sepa algo; si contesta "no le escribas, ya hablé", no le escribe. Si quien destraba
   dice que ya habló con el trabado, Leda le pregunta qué arreglaron y para cuándo lo destraba, para que
   quede asentado.
5. **Quien destraba dice que no le corresponde:** decidida (usuario, 2026-10-08, opción A con límite).
   Leda le pregunta quién se encarga y sigue con esa persona. Si la segunda también dice que no le
   corresponde, que no sabe o nombra a otro, Leda no da más vueltas: le informa al referente con toda la
   cadena ("Marcos está trabado; dijo que le toca a Juan, Juan que a Pedro, y Pedro dijo tal cosa") para
   que determine quién lo resuelve. Va al referente del sector de lo que falta cuando se sabe cuál es; si
   no, al de la tarea trabada.
6. **Bloqueos encadenados:** decidida (usuario, 2026-10-08). Se enlazan solos (Marcos ← Juan ← Pedro) y
   Leda avisa hacia abajo al destrabar. Quien está más lejos se entera de todo avance del medio con
   avisos informativos que no piden respuesta (llegó el repuesto, Juan da fecha, Juan terminó): "son
   mensajes informativos y aportan mucho".
7. **El bloqueo viejo:** decidida (usuario, 2026-10-08, opción A). A los `bloqueos.escala_solo_a_los_dias`
   días hábiles (5 en CoreWork, ajustable desde la plataforma) Leda le informa al referente aunque la
   cadena se mueva, con la historia y las fechas dichas. "El silencio y no informar es peor que avisos
   informativos útiles."
8. **Cadencias:** decidida (usuario, 2026-10-08, opción A). Un pedido de estado por persona con la lista
   de sus tareas; el recordatorio de vencimiento del día entra en la lista ("vence hoy") y no sale
   aparte, y lo contestado cuenta para la escalera de esa tarea. Si contesta sólo una, Leda anota esa y
   pregunta una vez por las otras en la misma respuesta; si no contesta, rige la decisión 21. Primero una
   conversación de prueba con las tres tareas en un mensaje, con la IA real. Las cadencias del pack
   quedan como están para probar; después se prenden, apagan y ajustan desde la plataforma
   (`docs/product/plataforma-pendientes.md`). El informe al grupo informa avances y problemas, no juzga:
   un atraso no hablado en privado no figura (constitución §8). Modelo aprobado:
   "📋 Semana del equipo / • Terminadas: … / • En curso: …, vence el vie 16/10 / • Trabadas: …,
   esperando un repuesto que llega el lunes". Hoy las cadencias no corren en el motor (retiradas en la
   E3-7; vuelven con la C-6).
9. **Delegar:** decidida (usuario, 2026-10-08, opción C). Marcos, encargado del sector, decide; quien
   recibe acepta; Leda le avisa a Marcos. A Ismael no le llega ningún aviso: "a Ismael no le interesa
   quién lo haga mientras se haga". La re-aprobación de un cambio de responsable (mecánica §7) la da
   quien manda sobre el que recibe, declarado en el pack, y queda en la auditoría; el trabajo lo sigue
   revisando el aprobador de la tarea original. Antes del código, su enmienda al ADR 0017 (decisión 2).
10. **Lo que describe la entrega frente al criterio:** decidida (usuario, 2026-10-08, del hallazgo de la
    primera ronda con la IA real). La causa no estaba en la entrega sino en la creación de la tarea: sin
    un criterio de aceptación concreto, la IA no sabe qué tiene que describir la persona (las tareas de
    prueba tienen uno de relleno, `tests/conversaciones/carga.py`, y la entrega no lo lee).
    - **Al crear la tarea** (la plataforma, con su ADR): el criterio tiene que ser concreto y comprobable
      (mecánica §13) y, si quien la carga no sabe escribirlo, Leda lo ayuda con una propuesta, como en el
      flujo C (`alta_turno.dato_a_proponer`, en `respaldo-flujos-antes-de-d`).
    - **Al entregar:** Leda compara lo que la persona describe con el criterio y pregunta sólo lo que
      falta, nunca lo que ya dijo. Cuando falta algo, dice qué en palabras simples y da un ejemplo sacado
      del criterio (nunca un dato inventado), que la persona acepta o reescribe. Si lo descrito no cubre
      el criterio, la entrega no sale hasta que se complete, aunque la persona insista: una foto no
      certifica lo que pide el criterio, y entregarla igual sólo suma una vuelta (pedido de cambios y
      otra entrega). La función de Leda es dirigir, ayudar y evitar idas y vueltas.
    - **"Describir", no "contar"**, en lo que la IA lee sobre la entrega.
11. **No nombrar a quien aprueba ni al referente por su cuenta:** decidida (usuario, 2026-10-08). Leda
    no los usa como motivo ("Ismael va a necesitar…") sino que habla de la tarea ("Para aprobar esta
    tarea, se necesita saber si completó los 20 ciclos sin fallas"), y tampoco los nombra al informar un
    hecho: "✏️ Quedó entregada y pasa a revisión. Te aviso apenas la aprueben o si hace falta algo más." y
    "✏️ Quedó anotado que la terminás el mar 27/10. La nueva fecha queda informada." Si la persona
    pregunta a quién se le informa, Leda le dice el nombre. Reemplaza el "Ismael será notificado" del
    formato de los mensajes (conversación 20): las conversaciones y los hechos que lo esperan cambian.
12. **Después de la única pregunta de "¿cuál de las dos?":** decidida (usuario, 2026-10-08). La respuesta
    se lee como la elección y lo demás va como comentario al responsable, sin ser un pedido de cambios
    ("aprobala nomás y pasale lo de los colores": se aprueba y se le pasa el comentario). Si la respuesta
    no elige ("y bueno, fijate vos"), Leda no decide: dice que la entrega queda esperando su decisión,
    con los dos botones, y no repite la pregunta. Hoy `fichas.dos_lecturas` la repite.
13. **No interrumpir una conversación** (conversación 26, del hallazgo del 2026-10-08): decidida (usuario,
    2026-10-08). Los avisos a una persona esperan 30 minutos desde lo último que escribió; ninguno sale
    junto con una pregunta de Leda sin contestar (un tema a la vez); el de otra tarea que no pide
    respuesta sale aparte, y el que pide respuesta espera a que se cierre la pregunta abierta; nunca fuera
    del horario; al salir se relee y no se repite lo ya hablado. La regla completa, en
    `tests/conversaciones/26-no-interrumpir.md`. Construida en la D5 de la C-3d.
14. **Entregar una tarea que nunca se arrancó:** decidida (usuario, 2026-10-08). "La terminé" sobre una
    tarea asignada se recibe igual, con su vista previa y su confirmación; al confirmar, la historia dice
    que arrancó y se entregó en ese momento, sin inventar una fecha de inicio. Es la persona la que dice
    que la hizo (mecánica §3: "ya lo hice" lleva a revisión, nunca a terminada).
15. **Una pieza retirada después de entregar deja la entrega incompleta:** decidida (usuario,
    2026-10-08). Leda lo resuelve con la persona en el momento: dice qué falta para aprobar la tarea y
    pide la pieza correcta, con la misma ayuda que en la entrega. Mientras falta, la aprobación espera:
    si el aviso a quien aprueba no salió (el margen), no sale; si ya salió y quien aprueba toca Aprobar,
    Leda le dice que la entrega se está completando y que le avisa. Con la pieza nueva, la entrega vuelve
    a estar completa y a quien aprueba le llega un aviso nuevo con todo lo vigente.
16. **Si cambia quién aprueba:** decidida (usuario, 2026-10-08). El aviso de una entrega va a quien
    aprueba en el momento de salir (se relee). Si el cambio es antes de que salga, le llega al nuevo; si
    es después, al nuevo le llega el aviso de lo que espera su decisión, y un botón del aviso viejo le
    dice al anterior que esa tarea ya no la aprueba él, sin cambiar nada. Hoy queda omitido
    (`cambio_quien_aprueba`) y el nuevo no recibe nada.
17. **Agrupar los avisos en listas:** decidida (usuario, 2026-10-08). Leda junta en un solo mensaje los
    avisos que se pueden agrupar y arma listas; el tope diario cuenta mensajes, no lo que trae cada uno.
    Hoy los avisos que Leda manda por su cuenta ya salen juntos por persona, pero los de entregas para
    revisar salen uno por entrega: pasan a ser una lista ("Te entregaron 2 tareas para revisar", cada una
    con su responsable y cuántas fotos trae) con un botón por tarea ([Ver PLC] [Ver bomba]); al tocar
    una aparece esa entrega (lo entregado, las fotos, el enlace y los botones Aprobar y Pedir cambios).
    Después de decidir una, Leda muestra lo que queda por revisar, sin insistir ese día; lo que queda
    entra en los recordatorios del día hábil siguiente. La lista de recordatorios ("Esperan tu revisión
    desde ayer") también lleva un botón por tarea. Escribir ("mostrame la del tablero") vale igual.
18. **"Revisar", no "aprobar", para lo que espera:** decidida (usuario, 2026-10-08). Primero se revisa y
    después se decide (aprobar o pedir cambios); "para aprobar" inclina la respuesta. Para quien revisa:
    "Te entregaron 2 tareas para revisar", "Te queda una por revisar", "Esperan tu revisión desde ayer";
    para quien entrega: "Quedó entregada y pasa a revisión. Te aviso cuando la revisen o si hace falta algo
    más."; en la página de la tarea, "en revisión". Corrige el ejemplo "esperando aprobación" del ADR 0019
    (7c), que sólo pedía no mostrar el nombre del sistema (`en_revision`).
19. **Los avisos de una decisión, sin margen para corregir:** decidida (usuario, 2026-10-08). "Quedó
    aprobada" y el pedido de cambios le llegan al instante a quien entregó: una decisión no se corrige por
    chat, así que el margen sólo la demoraría. Si un día se puede corregir una decisión por chat, se suma
    el margen con esa función. Pedido del usuario para la plataforma: poder ajustar el margen para
    corregir (`docs/product/plataforma-pendientes.md`).
20. **Cómo probar el enlace a la página:** decidida (usuario, 2026-10-08). En la PC, con Telegram Desktop
    o Web, `LEDA_BASE_URL=http://localhost:8000` y `python -m leda servir` en otra terminal: nada queda
    expuesto. Leda y la plataforma van a correr en un VPS; ahí sólo cambia `LEDA_BASE_URL`
    (`docs/product/plataforma-pendientes.md`, "Acceso y operación"). La D6 sirvió la página con
    `uvicorn leda.entrada:app --host 127.0.0.1 --port 8000 --no-access-log` en vez de `servir`, que
    además arranca un segundo ciclo de Leda y escucha en el 8080 (`PENDIENTE`: confirmarlo con el usuario).
21. **Una pregunta de Leda sin contestar** (del `PENDIENTE` de la D5): decidida (usuario, 2026-10-08,
    opción B). Frena los otros temas de la persona hasta que Leda la repite, una sola vez en el día, a las
    4 horas (ajustable desde la plataforma, `docs/product/plataforma-pendientes.md`). Si 4 horas después
    de la repetición sigue sin contestar y todavía es horario, sale aparte el tema siguiente más urgente
    (08:55 la entrega del PLC, 12:55 su repetición, 16:55 "hoy vence el tablero"). La segunda pregunta
    guarda la primera "para después": la persona contesta cualquiera, nombrando la tarea, y al cerrarse
    una el código trae la otra enseguida, en un mensaje aparte (hoy la retoma la IA si le parece). Al día
    siguiente sigue la escalera; varias cosas esperando van de a una, primero la más urgente. El aviso de
    atraso es informar, sin nombrar a nadie ("Si mañana sigue igual, voy a informar que está atrasada"),
    nunca "la paso para que te ayuden a destrabarla"; si preguntan a quién, Leda dice el nombre. Antes del
    código, una conversación de prueba con los dos órdenes de respuesta, con la IA real (D5b).
22. **Aprobar con un comentario que le pide algo a alguien** (del hallazgo de la ronda D7, 28 paso 3, 1
    de 5: "esta bien pero que mariano revise el rotulo de los cables" se aprobó y la tarea quedó
    terminada): decidida (usuario, 2026-10-08, opción A). Antes de cerrar, Leda pregunta una vez "¿la
    aprobás así o pedís cambios?"; cerrar por error es peor que un toque más. La respuesta a esa pregunta
    es la elección (decisión 12: "aprobala nomás y pasale lo de los colores" aprueba y pasa el
    comentario). Lo decide la cocina, no la IA: la IA sólo dice que la aprobación trae un comentario.
    **Precisión del usuario (2026-10-08, de noche, opción A; D7c):** pregunta sólo cuando el comentario
    le pide algo a alguien ("esta bien pero que mariano revise el rotulo de los cables"); un elogio o
    una observación que no pide nada ("el plc de marcos aprobado, impecable") aprueba directo, como
    antes de la D7b. La IA lo dice como un dato de la jugada (`el_comentario_pide_algo`) y la cocina
    decide: si es verdadero, o si la IA no lo dijo (el lado seguro), pregunta una vez; si es falso,
    aprueba directo. La respuesta a la pregunta abierta sigue siendo la elección (decisión 12).
23. **Volver a entregar después de un pedido de cambios** (del paso 19 de la prueba por Telegram del
    2026-10-08: Marcos volvió a entregar "completo los 20 ciclos sin fallas" y Leda le preguntó si
    arranca desde el PLC, que su primera entrega ya decía; la entrega nueva sólo miraba lo mandado
    desde el pedido de cambios, y el criterio es un solo punto): decidida (usuario, 2026-10-08,
    opción A). Lo que describió la entrega anterior sigue contando, salvo lo que el pedido de
    cambios pide cambiar, y Leda pregunta sólo lo que falta de verdad (decisión 10: nunca lo que la
    persona ya dijo). Construida en la D8 (punto 10).

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
  - [x] Porción 2, la entrega con evidencia y la política por tipo (2026-10-08). Route: delegada
    (escritor único, 2+ archivos no triviales).
    - **Commits:** `0176300` (migración `0034`: la clase de cada pieza, lo que cubre, el archivo,
      `evidencia_retirada` y `archivo_de_tarea`, sólo agregar y con RLS forzado; la política por
      tipo en `tipos_de_evidencia_que_faltan`; `evidencia.tipos` en el pack; `entregar_tarea` y
      `retirar_evidencia` en la cocina), `806e85f` (la ficha `entregar` con su vista previa,
      `confirmar` con la guarda escrita, `guardar_para_la_entrega`, la corrección de la vista
      previa y el retiro) y el commit de las conversaciones 21 y 22 (YAML, el corredor aprende
      archivos, botones por etiqueta y la política de evidencia).
    - **Test primero:** `tests/motor/test_entrega.py` se vio en rojo (17 de 17) antes de la ficha, y
      el reparto de lo que cubre cada pieza también (`test_cada_pieza_cubre_lo_que_solo_ella_puede_
      cubrir`). Las garantías de la base (`tests/garantias/test_evidencia.py`) se escribieron con la
      migración, sin rojo observado.
    - **Corridas en seco** (IA guionada, `correr_conversacion`, 2026-10-08): la 21 y la 22 sin fallas;
      de las demás, sólo la 12 (pasos 6 y 7) y la 25 (paso 8) fallan, porque esperan que la entrega no
      se reciba por chat.
    - **El referente del área** no hace falta en esta porción: queda para la 4 (quién ve la página).
    - **Revisiones RDD** (2026-10-08, por commit, en carpetas temporales): `0176300` pidió una
      corrección (CRITICAL: el rollback de la `0034` borraba `evidence.texto` sin negarse), hecha en
      `1ebd31a` con su garantía en rojo y después en verde, validada y reconocida
      (`review-bc98816c7dc942e0`); `806e85f` (`review-5558dced5f73dce3`) y `3d7871a`
      (`review-55b5e057a39cce8a`), aprobadas. La 12 y la 25 se actualizaron en `dd11bf7`.
    - **Una advertencia de la revisión resultó un error:** `confirmar` nombrando una tarea sin
      entrega abierta confirmaba la entrega abierta de otra (confundir la tarea). Arreglado con su
      prueba en rojo y después en verde (`test_confirmar_nombrando_otra_tarea_no_entrega_la_que_
      espera`), en el commit que registra esto.
    - **Advertencias sin arreglar** (casos de borde, de las revisiones): un archivo mandado para otra
      jugada que se suma a la entrega; un retiro parcial; un enlace con puntuación pegada; la entrega
      de una tarea que cambió entre la vista previa y la confirmación; en el corredor, un salto del
      chequeo de formato demasiado amplio.
    - `PENDIENTE`:
      - **Decisión del usuario: una pieza retirada después de entregar** deja la política incompleta:
        la tarea sigue en revisión, no se puede aprobar y a quien aprueba no le llega nada; la salida
        hoy es que pida cambios. ¿Vuelve a en curso, se le avisa a quien aprueba, o alcanza así?
      - **Decisión del usuario: entregar sin haber arrancado.** La ficha entrega sólo desde en curso
        (ADR 0018, decisión 4): "terminé" sobre una tarea asignada dice que no se puede (la 25, paso
        8). ¿Se anota el inicio y se entrega en el mismo mensaje?
      - **Las bases que ya existen:** después de la `0034` hay que volver a importar el pack para que
        cada política tenga sus clases; hasta entonces ningún tipo se cubre (falla cerrado) y la
        evidencia de antes no cubre nada.
      - `db/pruebas.sql` inserta evidencia sin clase: quedó atrás de la `0034`.
  - Porción 3, el aviso a quien aprueba, partida en tres (2026-10-08):
    - [x] **3a, el aviso redactado por el motor con las fotos, sin el enlace** (2026-10-08). Route:
      delegada (escritor único, 2+ archivos no triviales).
      - **Commits:** `2d86ee3` (migración `0035`: `message_outbox_adjunto`, RLS forzado, claves
        compuestas por espacio, sólo agregar, sin columnas nuevas en `message_outbox`; la salida
        con adjuntos y el despachador que manda el álbum después de su texto, reusando el
        identificador de Telegram de cada foto y, si no sirve, subiendo la copia), `93a428d`
        (el aviso `entrega_para_aprobar` del motor: guardado al confirmar, con el margen para
        corregir; releído al salir, omitido con su motivo si la tarea ya no espera la
        aprobación; las fotos adjuntas y los demás archivos nombrados; una entrega nueva retira
        el que espera, T6i; la cocina deja de mandar el texto fijo en `entregar_tarea`) y
        el commit que registra esto (el corredor cuenta las fotos de un álbum y marca uno suelto; la 21 corre el
        paso 6; la 21 y la 22 esperan el aviso guardado en lugar del de la cocina).
      - **Test primero:** las garantías de la salida (`tests/garantias/test_salida_con_adjuntos.py`)
        se vieron en rojo (no existía `Adjunto` ni la tabla) antes de la migración y del
        despachador. Las del aviso del motor (`tests/motor/test_entrega.py`, sección "El aviso a
        quien aprueba") se escribieron después del primer borrador del código, sin rojo
        observado.
      - **Chequeos** (2026-10-08, sobre la punta de la porción): `pytest tests/garantias` 259
        passed; `pytest tests/motor tests/conversaciones` 737 passed; suite completa 1423 passed;
        corrida en seco de las 23 conversaciones con la IA guionada (`--ronda seco-3a`): 23 de 23
        bien, con el paso 6 de la 21 (sus informes se borraron). Sin la IA real: la regresión con
        la IA real es de la C-4.
      - **Cómo decide qué foto va adjunta:** las imágenes de la evidencia vigente que Telegram
        muestra como foto (no HEIC y de hasta 10 MB), las primeras diez; las demás se nombran.
      - **Sin botones:** el aviso sale sin Aprobar ni Pedir cambios (los trae la 3b) y su cierre
        no ofrece aprobar, porque todavía no hay con qué. Sin enlace: `_enlace_portal_tarea` sigue
        sin inventar ninguna URL (constitución §4).
      - **Queda con texto fijo** `_notificar_entrega_al_aprobador`, sólo en las entregas de la
        cocina que ningún circuito del chat alcanza (`actualizar_estado` a revisión y
        `adjuntar_evidencia`; `tests/test_entrega_con_evidencia.py`). Se retira cuando la 3b o la
        plataforma decidan qué hacer con esas herramientas.
      - **Si cambia quién aprueba** mientras el aviso espera: decidido por el usuario (decisión
        16) y construido en la D4: el aviso va a quien aprueba al salir.
      - El `.md` de la 22 (paso 7) ya dice que Ismael se entera a los 10 minutos, con el margen.
      - **Revisiones RDD** (2026-10-08): `2d86ee3` (`review-12fee547e7870e72`), `93a428d`
        (`review-ff189c1a27aaeaca`) y `97470c5` (`review-44020d6e3b194e0b`), aprobadas, más los
        commits chicos `1ebd31a..4327889` (`review-bb7ab94babd6588f`). Advertencias sin arreglar: dos
        del despachador con álbumes; las ramas de vigencia del aviso sin probar; un álbum suelto sin
        prueba en el corredor; y las fotos se descartarían si el aviso saliera junto con otros (hoy
        no pasa: un aviso de coordinación sale siempre solo, `avisos._envios`).
    - [x] **3b, la hoja de aprobación** con los botones Aprobar y Pedir cambios, como atajos
      (conversación 23; 2026-10-08). Route: delegada (escritor único, 2+ archivos no triviales).
      - **Commits:** `a2f209d` (las jugadas `aprobar` y `pedir_cambios`, con la duda, el no de
        quien no aprueba ese trabajo y lo que admite dos lecturas, `fichas.dos_lecturas`; las
        entregas que esperan la decisión de quien escribe, `aprobacion.para_decidir`; el aviso
        de la entrega con sus botones, `preguntas.ofrecer`, `botones.ConOpciones`, con la
        guarda de lo que mostró, `entrega.huella_de_lo_entregado`; los avisos al responsable,
        `tarea_aprobada` y `pedido_de_cambios`, redactados por el motor; la cocina deja de
        mandar sus textos fijos en `aprobar_tarea` y `pedir_cambios_tarea` y devuelve la
        identidad del acto; el cierre que esperaba, `cerrar_tarea_aprobada` en la cocina y
        `aprobacion.cerrar_las_que_ya_pueden` en cada vuelta del ciclo, con su aviso
        `cerrada_con_la_aprobacion` a los dos) y el commit que registra esto (el YAML de la 23,
        la 21 con los botones del aviso y el corredor: `aparte`, `de_la_tarea`, `botones` en
        lo que sale, las `aprobaciones` en los efectos, Mariano y Lucas, y un criterio de
        aceptación de la prueba en cada tarea). Sin migración: el esquema ya tenía lo que hace
        falta (`approval`, `motivo_no_cierra_tarea`).
      - **Test primero:** `tests/motor/test_aprobacion.py` se escribió antes que el código y se
        vio en rojo (no existía `leda.motor.aprobacion`: falla de colección, no prueba por
        prueba). Las garantías de la cocina (`tests/garantias/test_cierre_con_aprobacion.py`)
        se escribieron después de `cerrar_tarea_aprobada`, sin rojo observado.
      - **Chequeos** (2026-10-08): `pytest tests/garantias` 264 passed; `pytest tests/motor
        tests/conversaciones` 760 passed (una corrida anterior, 1 falla sin nombre que no se repitió: la intermitente conocida); suite completa 1451 passed;
        corrida en seco de las 24 conversaciones con la IA guionada (`--ronda seco-3b`): 24 de
        24 bien, la 23 entera (sus informes se borraron). Sin la IA real: es de la C-4.
      - **Cómo quedó lo decidido:** lo claro va directo, sin vista previa; la cocina comprueba el
        cierre en el mismo acto y, si algo lo frena, la aprobación queda anotada y los hechos
        dicen qué (`no_se_cierra_todavia`); el sistema la cierra solo, sin otra aprobación,
        cuando se resuelve (un evento del sistema que nombra la aprobación, auditado como de
        Leda a nombre de quien aprobó). Aprobar y pedir cambios juntos sobre la misma tarea no
        hacen nada y llevan una sola pregunta con dos botones (la misma, si se repite). El
        botón "Pedir cambios" pregunta qué falta (`que_cambios_pide`). La decisión que ofrece el
        aviso no es un tema abierto: quien aprueba no le debe una respuesta a la conversación
        (sus recordatorios son de la 3c), como dice el estado inicial de la 23.
      - **Los avisos de la decisión salen enseguida, sin el margen para corregir** (lo dice la
        23, pasos 2, 4 y 6): una decisión no se corrige por chat, así que el margen sólo la
        demoraría. Si el usuario quiere margen también acá, es la misma regla de `margen.py`.
      - **Las instrucciones de la IA no cambiaron** (son las que pasaron la prueba real): las
        entregas para decidir llegan en la lista de tareas con `para_decidir` y su responsable,
        con su significado, y las fichas dicen qué es cada jugada.
      - `PENDIENTE`: el enlace a la página de la tarea en los avisos al responsable (ADR 0019,
        7a) es de la porción 4 (`_enlace_portal_tarea` sigue sin inventar ninguna URL).
      - **Para la 3c:** los recordatorios a quien aprueba pueden contar las entregas que esperan
        con `aprobacion.para_decidir` (o la decisión ofrecida sin cerrar,
        `preguntas.DECISION_DE_LA_ENTREGA`, atada a su aviso por `del_aviso`); la decisión se
        cierra sola al decidir, por escrito o con el botón (`Ficha.contesta`), y un aviso nuevo
        de la misma tarea la reemplaza. Hoy no tiene espera (`pending_reply`): la 3c decide si
        la suma o si cuenta por el aviso.
    - [x] **3c, los recordatorios a quien aprueba** (conversación 24; 2026-10-08). Route: delegada
      (escritor único, 2+ archivos no triviales).
      - **Commits:** `281c34e` (la escalera de una decisión que espera, `escalera.
        _un_paso_de_una_decision`; los avisos `recordatorio_de_la_decision`, `aprobacion_trabada`
        y `aprobacion_destrabada`, con su vigencia al salir; `TipoDeAviso.recuerda`: el
        recordatorio recuerda la decisión que ofreció el aviso de la entrega, sin botones ni otra
        pregunta; `aprobacion_vigente` pasa a `avisos.py`; la 23 espera el recordatorio del lunes
        26; la IA guionada nombra una vez los avisos repetidos de un envío) y el commit que
        registra esto (el YAML de la 24, su prueba en el corredor y el README). Sin migración.
      - **Cómo cuenta (elección de implementación):** desde que salió el aviso de la entrega
        (`entrega_para_aprobar`), sin una espera nueva en `pending_reply`. Ese aviso ya es el
        pedido: la decisión queda registrada en él (`decision_de_la_entrega`, `del_aviso`), y lo
        que la corta es un hecho de la cocina (la aprobación vigente, la tarea que deja de estar
        en revisión, una entrega más nueva), que se relee en cada vuelta y al salir. Una espera
        nueva habría entrado en la escalera de las preguntas, que repite la pregunta como tema
        abierto y escala por la ruta de falta de respuesta: otra regla que la decidida. Así se
        reusan `avisos.guardar`, `TIPOS` con su vigencia, `sale`, el calendario y el candado de
        la tarea, como la escalera de siempre.
      - **Cómo quedó lo decidido:** un recordatorio por día hábil, sin tope, desde el siguiente
        al del aviso de la entrega; el segundo dice que al día siguiente se entera quien está
        arriba (`si_sigue_sin_decidir`), sólo si hay alguien; al día hábil siguiente del
        segundo, quien está arriba recibe el aviso sólo informativo, una vez, sin pregunta ni
        botones, y la tarea no entra en sus entregas para decidir (si intenta aprobarla, Leda le
        dice que la decide Marcos). Una decisión (aprobar, también si todavía no cierra, o pedir
        cambios) corta los recordatorios y, si quien está arriba ya se había enterado, le llega
        que se destrabó, enseguida. Quien está arriba nunca es el responsable (si lo fuera, no
        hay nadie arriba). Una ausencia de quien aprueba pausa la cuenta. Un recordatorio
        guardado que ya no corresponde se omite al salir con su motivo (`ya_decidio`,
        `tarea_cerrada`, `hay_una_entrega_mas_nueva`, `cambio_quien_aprueba`,
        `cambio_quien_esta_arriba`).
      - **Lectura del tope diario (mecánica §10), para que la confirme el usuario:** los
        recordatorios y el aviso a quien está arriba son seguimiento que Leda inicia por su
        cuenta (no los causa el acto de otra persona ese día): cuentan para el tope y salen en un
        envío por persona; el aviso de que se destrabó lo causa la decisión de quien aprueba, así
        que es de coordinación (fuera del tope), como el aviso de la decisión al responsable.
      - **Test primero:** `tests/motor/test_recordatorios_de_la_decision.py` se escribió antes que
        el código y se vio en rojo (9 de 13; las otras 4 miran que algo no pase y ya pasaban);
        después, 13 de 13. La 24 corrió en seco entera con el YAML recién escrito.
      - **Chequeos** (2026-10-08, sobre la punta de la porción): `pytest tests/garantias` 264
        passed (sobre `281c34e`); `pytest tests/motor tests/conversaciones` 775 passed; suite
        completa 1466 passed; corrida en seco de las 25 conversaciones con la IA guionada
        (`--ronda seco-3c`): 25 de 25 bien, la 24 entera (sus informes se borraron). Sin la IA
        real: es de la C-4.
      - **Las instrucciones de la IA no cambiaron** (la huella de `test_contratos.py` sigue): los
        avisos nuevos llegan con sus hechos y sus significados (`hechos.py`).
      - **La 23** recibía, el lunes 26 a las 10:30, el primer recordatorio de las tres
        entregas del viernes mientras Ismael estaba decidiendo: desde la D5 (no interrumpir)
        espera mientras decide y, releído, queda omitido.
      - `PENDIENTE`:
        - **Un aviso de la entrega que no salió** (fallido tras los cinco intentos) no empieza la
          cuenta: queda su incidente y el aviso de la falla, como desde la 3a. ¿Se le recuerda
          igual a quien aprueba?
        - **Quien aprueba ausente:** la cuenta se pausa y quien está arriba no se entera de que
          la entrega espera a alguien que no está (la mecánica §9 pide avisar al referente del
          área de las tareas sin cobertura; no está construido).
  - [x] Porción 4: la página de la tarea y su enlace (2026-10-08). Route: delegada (escritor
    único, 2+ archivos no triviales).
    - **Commits:** `364ed7d` (migración `0036`: `acceso_tarea`, sólo el hash del token, sin
      vencimiento y revocable; `vista_de_tarea`, cada vista y cada descarga, sin dirección ni
      navegador; `message_outbox_enlace`, la marca de la fila de la salida que lleva el enlace; las
      tres con RLS forzado, y `acceso_tarea` con una política más, de lectura y sólo para
      `leda_owner`, por el hash; `area.referente_membership_id`, cargado del pack con
      `areas[].referente`; las funciones `puede_ver_tarea`, `emitir_acceso_tarea`,
      `acceso_tarea_vigente`, `leer_pagina_de_tarea` y `leer_archivo_de_tarea`, de `leda_owner`,
      con `leda_app` sin privilegios sobre los accesos ni las vistas), `3c3e29d` (la página
      `GET /tarea/{token}` y sus archivos `GET /tarea/{token}/evidencia/{id}`, `tarea_vista.py`,
      con su propia conexión y candado) y el commit que registra esto (el enlace en los avisos: la
      marca `enlace_de_tarea` en `enqueue_outbox`, el despachador que lo emite al mandar y lo manda
      sin vista previa, `TipoDeAviso.enlace`, el hecho `lleva_el_enlace_a_la_pagina_de_la_tarea`
      para la IA, `_enlace_portal_tarea` que da la marca y nunca una dirección; la 21 y la 23
      esperan el enlace con `enlace: true` y el corredor lo comprueba con una dirección de prueba
      que no es de nadie, `https://leda.invalid`).
    - **Quién ve** (en SQL, revalidado en cada pedido): el responsable, quien aprueba su trabajo
      hoy y quien ya decidió sobre la tarea, el referente del área y la autoridad final. Quién
      recibe el enlace: quien aprueba, en el aviso de la entrega; el responsable, en
      `tarea_aprobada`, `pedido_de_cambios` y `cerrada_con_la_aprobacion` (a quien aprobó, no).
    - **Test primero:** `tests/garantias/test_pagina_de_la_tarea.py` se vio en rojo (25 de 25: no
      existían las funciones) antes de la migración; las dos del referente en el pack, sin rojo
      observado. `test_pagina_web_de_la_tarea.py` se vio en rojo (14 de 14, sin las rutas: error
      de la fixture, no aserción por aserción). `test_enlace_de_la_tarea.py` en rojo (9 de 9) antes
      de la salida y el despachador; en `tests/motor/test_entrega.py`, la del aviso con el enlace en
      rojo y la de sin dirección pasaba desde antes (mira que algo no pase).
    - **Chequeos** (2026-10-08, sobre la punta de la porción): `pytest tests/garantias` 315 passed;
      `pytest tests/motor tests/conversaciones` 777 passed; suite completa 1519 passed; corrida en
      seco con la IA guionada (`--ronda seco-4`): 25 de 25 bien, la 21 y la 23 con el enlace (sus
      informes no se guardaron: `seco-4` ya era el nombre de una ronda versionada de la E3, que
      quedó como estaba). Sin la IA real: es de la C-4.
    - **Las instrucciones de la IA no cambiaron** (la huella de `test_contratos.py` sigue): el
      hecho nuevo llega con su significado (`hechos.py`).
    - **Una corrección del camino:** los botones de un aviso (`botones.ConOpciones`) buscaban su
      fila por el final del texto; con el enlace al final, buscan sin el último renglón.
    - `PENDIENTE`:
      - **Pedir el enlace por chat** (ADR 0019, 7a: una jugada nueva de la lista cerrada, para
        cualquiera que pueda ver la tarea): hecho el 2026-10-09, en el ítem que sigue a esta
        porción. La huella de `test_contratos.py` no cambió: mide las instrucciones, no la lista.
      - **Operación:** el enlace sólo sale con `LEDA_BASE_URL` configurada; para abrirlo desde el
        teléfono, esa dirección tiene que llegar al servidor (`python -m leda servir`). Hoy la
        prueba por Telegram corre con el escuchador, sin servidor: decidir con el usuario cómo se
        prueba (sin la dirección, los avisos salen sin enlace y no lo prometen).
      - **Las bases que ya existen** (`leda_motor`): aplicar la `0036` y volver a importar el
        pack para cargar los referentes. No se tocó ninguna base real.
      - **Si la persona ya no puede ver la tarea al salir el mensaje** (cambió quién aprueba entre
        la redacción y el envío), sale sin el enlace con un incidente de severidad baja, y el
        texto de la IA pudo haberlo anunciado: caso de borde.
      - **Revocar los enlaces** de una persona o de una tarea (7a) existe en la base
        (`acceso_tarea.revocado_en`), sin comando todavía: va con la porción 5.
    - **Para la porción 5** (el acceso del administrador por el bot de administración): un acceso
      atado al usuario de plataforma y no a una membresía (`acceso_tarea.membership_id` es
      obligatorio: otra tabla o una columna nueva), cada vista también en `audit_log`, el comando
      para revocar y el retiro de contenido por la administración ("retirado por la
      administración" en la página).
    - **Impugnación de seguridad (2026-10-08).** Una revisión de sólo lectura de la porción
      confirmó el aislamiento en sus puntos 1 a 3 y 5 (el token, la tarea y el espacio salen de
      la base; un archivo de otra tarea o de otro espacio da la página genérica). Encontró cuatro
      cosas, corregidas con su prueba vista en rojo antes:
      - **Una pieza retirada mostraba su contenido** (el texto, el enlace y el nombre del
        archivo): la página mira primero si se retiró y sólo dice qué clase de cosa era y cuándo
        se retiró. Se corrigió sólo la página (`tarea_vista._pieza`), que alcanza para el ADR; la
        función de la base sigue devolviendo el contenido a la página, que no lo usa. `bd51562`.
      - **El token quedaba escrito en el registro de accesos** de uvicorn, con la dirección de
        quien abría el enlace: `servir` arranca con `access_log=False`. `bd51562`.
      - **Una falla al armar la página** daba un error del servidor: la página y la respuesta
        de un archivo se arman dentro de la transacción que las lee; una falla da la página
        genérica (503), una línea en la consola sin el token ni el detalle, y la vista no queda
        registrada. `bd51562`.
      - **`resolver_pendiente`** (de antes) era `security definer` sin `search_path` fijado y la
        podía ejecutar `public`; `aplicar_evento_tarea` lo fijaba sin `pg_temp` (Postgres busca
        primero las tablas temporales) y también era de `public`. Migración `0037`: las dos con
        `leda, public, pg_temp`, sin `execute` para `public`, `resolver_pendiente` sólo para
        `leda_app`; su vuelta atrás las recrea desde el catálogo para volver al privilegio de
        omisión. La regla general, para toda función elevada del esquema, está en
        `tests/garantias/test_aislamiento.py`, y la paridad entre la instalación limpia y la
        migrada compara ahora también dueño, camino y privilegios de las funciones elevadas. El
        commit que registra esto.
      - **Resuelto (2026-10-09): diez tablas con `workspace_id` sin `row level security`**
        (`acceso_tablero`, `activation_token`, `admin_notice`, `conversation_access_log`,
        `holiday`, `learning`, `model_config`, `persona_config`, `work_calendar` y
        `workspace_version`), contra la invariante de `AGENTS.md`. Route: delegada (escritor
        único, 2+ archivos no triviales). Commit `f06e699`.
        - **A cinco les faltaba:** `leda_app` las lee directamente (`select`) dentro de
          `espacio()`: `work_calendar` y `holiday` (`calendario.Calendario`), `persona_config`
          (`motor.instrucciones.tono_del_espacio`), `workspace_version` (`versiones.pack_hash`) y
          `model_config` (`motor.ia_real.desde_base`); su aislamiento dependía del `where` de
          cada lector. Migración `0041` (con su vuelta atrás) y `db/esquema.sql`: RLS forzada y
          `aislamiento_espacio`; `model_config` con la forma de `audit_log` (nulo o el espacio
          activo), para que el modelo global se siga viendo. `leda_app` sigue sólo con
          `select`. Ningún lector cambió: todos corren en `espacio()` del mismo espacio, las
          escrituras son de `admin()` y ninguna función `security definer` las lee.
        - **Las otras cinco quedan sin política, como excepciones declaradas** con su motivo
          (`EXCEPCIONES_SIN_RLS` en `tests/garantias/test_aislamiento.py`): ni `leda_app` ni
          `leda_gateway` tienen privilegios sobre ellas, y la prueba lo exige.
        - **Rojo primero:** la prueba del catálogo (toda tabla común con `workspace_id` tiene RLS
          forzada salvo las excepciones) falló nombrando las cinco, y la de comportamiento
          (dentro de `espacio()` de un espacio no se ven filas del otro; el modelo global sí)
          falló en `holiday`. **Verde:** las dos pasan; la paridad entre la instalación limpia y
          la migrada y el ensayo de vuelta atrás incluyen ahora las cinco tablas.
        - **Chequeos** (2026-10-09): `pytest tests/garantias` 328 passed;
          `pytest tests/motor tests/conversaciones` 926 passed; suite completa 1682 passed.
        - **Revisión RDD** (coordinador): `b09f46f..f06e699` `review-1f3e103485c088f9`, aprobada
          y reconocida. Advertencias: la política de la `0041` no tiene `with check` (hoy
          `leda_app` sólo lee y `leda_admin` la saltea; si un día `leda_app` escribe, hace falta);
          la prueba de comportamiento apaga los modelos globales que ya hubiera.
        - **Resuelto** (`411d680`, coordinador): `tools/restriccion_horario.py` leía y escribía
          `work_calendar` sin cambiar de rol; ahora corre bajo `admin()` (`leda_admin`).
          Comprobado con `restriccion_horario.py estado corework` sobre `leda_motor`.
      - `PENDIENTE`: el tablero (`_servir_tablero`) arma su página fuera de una guarda, como la
        página de la tarea antes de esto; no se tocó.
  - [x] **Pedir el enlace por chat** (2026-10-09; lo que quedó de la porción 4; ADR 0019, 7a y
    7b; conversación 31). Route: delegada (escritor único, 2+ archivos no triviales).
    - **La conversación primero** (`410b15c`): la 31, con su YAML. Marcos pide el de una tarea
      suya; Ismael, el de una de Marcos ya terminada y el de una de Lucas, que no están en su lista
      (la ve por ser la autoridad final); Nahuel, el de una que no puede ver. El cargador escribe
      una tarea `terminada` con la aprobación que su cierre exige. En seco, antes del código: 15
      fallas, todas del motor más el aviso al administrador de algo fuera de la lista.
    - **La jugada** (`pedir_enlace`, `leda.motor.enlace`; el commit que registra esto): la IA
      nombra la tarea por su alias o, si no está en su lista, por cómo la dijo
      (`como_la_nombra`, un dato nuevo); la cocina la busca entre las tareas del espacio de quien
      escribe, también las terminadas y canceladas, y la base dice si puede verla
      (`puede_ver_tarea`). La respuesta lleva la marca del enlace, como `ver_entrega`, y el
      despachador lo emite al mandar, con la base comprobando otra vez. Si no puede verla: ningún
      enlace y el motivo (`no_puede_ver_esa_tarea`), sin decir quién la ve. Si puede ver varias
      que coinciden, pregunta cuál (`coinciden`); sin la dirección pública, lo dice
      (`la_pagina_no_esta_disponible`); uno solo por mensaje (`ya_lleva_el_enlace_de_otra_tarea`).
      No cambia nada ni deja auditoría (es una lectura; la emisión y cada vista ya quedan en
      `acceso_tarea` y `vista_de_tarea`).
    - **Por qué este mecanismo y no ampliar la lista de la IA:** sumar a la lista de cada turno
      todas las tareas que la persona puede ver le daría a la autoridad final todas las del
      espacio en cada mensaje, para todas las jugadas (aprobar, entregar…), y cambiaría lo que
      ya se probó con la IA real. La búsqueda queda en la jugada que la necesita, la arma el
      código y compara palabras enteras, sin patrones de la base (como `integrantes_que_
      coinciden`): cada palabra dicha tiene que estar en el título o en el nombre de quien la
      tiene, un plural vale por su singular y las palabras de unión ("la del", "de") no cuentan.
      Nunca una búsqueda libre de la IA.
    - **Test primero:** `tests/motor/test_pedir_enlace.py` en rojo, 12 de 13 (la que mira que no
      cambie nada pasaba desde antes); en `tests/garantias/test_enlace_de_la_tarea.py`, las tres
      nuevas en rojo (quien no la ve nunca recibe el enlace, ni la marca ni un acceso al mandar;
      quien la ve lo recibe y se emite al mandar; una tarea de otro espacio no existe para la
      búsqueda); en `tests/motor/test_fichas.py`, las dos que nombran la lista cerrada.
      **Verde:** las 18. `OFRECIDAS` suma la jugada; `comprobar.DATOS_LIBRES`, el dato nuevo.
    - **Las instrucciones de la IA no cambiaron** (huellas de `test_contratos.py` iguales): la
      jugada llega con su ficha (`es`), su dato con su descripción (`ia_real.DATOS`) y sus
      códigos con su significado (`hechos.py`).
    - **Chequeos** (2026-10-09, sobre el código de este commit): `pytest tests/motor
      tests/conversaciones`, 940 passed; `pytest tests/garantias`, 331 passed; en seco,
      `correr --ia guionada --veces 1 --ronda seco-enlace`, 31 de 31 bien (informes borrados,
      `gasto.json` sin tocar). Sin la IA real (decisión del usuario: van en la tanda posterior).
      Sin la suite completa.
    - `PENDIENTE`:
      - **La IA real** sobre la 31, en la tanda posterior (decisión del usuario).
      - **Un nombre con un error de tipeo que la IA copie tal cual** ("tablro") no encuentra la
        tarea: Leda dice que ninguna se llama así. El dato le pide a la IA las palabras bien
        escritas; si con la IA real falla, se mira la comparación, no una lista de errores.
      - **Varias que coinciden:** Leda las nombra y la persona contesta; no es una pregunta con
        botones (la duda de siempre ofrece sólo tareas de la lista de la persona, por su alias).
      - **El administrador de plataforma** pide su enlace por el bot de administración (porción
        5), no por esta jugada.
  - [ ] Porción 5: el acceso del administrador.
- [ ] **C-3d.** Lo que decidió el usuario el 2026-10-08 (preguntas 10 a 20), en este orden. Route de
  cada una: delegada (escritor único, 2+ archivos no triviales), una por vez, revisión RDD por commit.
  - [x] **D1.** El comparador del corredor: la garantía es "lo escrito es lo confirmado"; mostrar lo
    escrito completo; aflojar en los YAML de la 21 a la 23 lo que la ficha permite; criterios de
    aceptación reales en las tareas de prueba (`carga.py`). Route: delegada (escritor único, 2+
    archivos no triviales). Hecha el 2026-10-08, sin tocar `src/`:
    - **Criterios** (`f59b42c`): cada tarea de las 25 conversaciones lleva el suyo, concreto y
      comprobable, en el YAML y en el estado inicial del `.md` (también la 26); `carga.py` deja uno
      de reserva, también concreto. Rojo primero: la prueba del cargador falló en las 25.
    - **El comparador** (`71d7739`): el corredor lee las vistas previas confirmadas en el paso
      (`confirmadas`) y la evidencia escrita que es lo confirmado cumple la garantía; si difiere del
      YAML es de comprensión (del motor, con las jugadas esperadas). Siguen de garantía lo que no es
      lo confirmado y lo de una tarea que nadie confirmó. Toda falla de filas muestra lo escrito
      entero. Rojo primero: seis pruebas de `test_comprobar.py` y una de `test_corredor.py`, que
      repite la falsa alarma de la 21 con la IA real (dio `[garantia] efecto de más: evidencia`).
    - **`puede_traer`** acepta sólo datos que la ficha declara opcionales (si no, es un error del
      YAML) y, con un valor, lo exige si el dato viene. La 21 y la 22 aceptan la tarea en
      `confirmar`; la 23, el comentario en `aprobar` (pasos 1 y 8); la 22 espera `entregar` en los
      pasos 5 y 6, que es lo que dice la ficha (sin jugada también está bien y se lee en la
      transcripción, como en la 25). No se tocaron el paso 1 de la 21 (hallazgo 1, D3) ni el 9 de
      la 23 (decisión 12, D4).
    - **Pruebas:** `pytest tests/conversaciones`, 127 passed; `pytest tests/motor
      tests/conversaciones`, 786 passed (sin la intermitente); en seco, `correr --ia guionada
      --veces 1 --ronda seco-d1`, 25 de 25 bien (informes borrados).
    - `PENDIENTE`: en la 22, paso 1, si la IA elige `guardar_para_la_entrega` sin la tarea, los
      hechos salen repetidos (la jugada y lo que trajo el mensaje): es del motor y queda para D3.
  - [x] **D2.** Las palabras (decisiones 11 y 18): no nombrar por su cuenta a quien aprueba ni al
    referente (y decir el nombre si se pregunta); "revisar" para lo que espera; "describir" en la
    entrega. Cambian los hechos, sus significados y las conversaciones que esperan "Ismael será
    notificado". Route: delegada (escritor único, 2+ archivos no triviales). Hecha el 2026-10-08:
    - **El nombre, sólo si pregunta** (`f5fede8`). Elegido: en el borde de la redacción
      (`hechos.para_redactar`), cada dato de la cocina que nombra a quien aprueba el trabajo de la
      persona a la que Leda le escribe (`hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`: los avisos al
      referente y a quien aprueba, sus correcciones, a quiénes se escaló, lo que pasa si no hay
      respuesta o si sigue sin decidir, el aviso de que se destrabó, quién aprobó o pidió cambios y
      `queda_esperando_la_aprobacion_de`) le llega con el nombre dentro de `solo_si_pregunta`, en
      el mismo lugar; lo demás (cuándo se entera), a la vista. Por qué así: `solo_si_pregunta` ya
      existía y la redacción ya lo trata igual en los hechos y en los últimos turnos, así que la
      pregunta "¿a quién le avisaste?" se contesta del registro sin una jugada nueva; los hechos de
      la cocina, la base, el registro de turnos, las pruebas y la auditoría no cambian; y es por
      dato, una lista cerrada, no una heurística sobre nombres. La otra forma (que el nombre llegue
      sólo cuando el mensaje lo pregunta) necesitaba que el código decidiera qué es una pregunta:
      frases. Quedan a la vista los datos que nombran a otra persona: el responsable para quien
      aprueba (`aviso_al_responsable`, `responsable`), quién tiene trabada la decisión para quien
      está arriba (`quien_aprueba`), y quién decide lo que la persona pidió (`quien_decide`,
      `quien_aprueba` en `no_es_quien_aprueba`), que es la respuesta a su pedido.
    - **La cocina suma dos hechos ciertos:** la vista previa dice que al confirmar pasa a revisión
      (`al_confirmar.estado`), y la entrega, que la persona se entera cuando quien la revisa decida
      (`se_le_avisa_cuando_decida`; el aviso de la decisión sale enseguida, decisión 19): de ahí
      sale "Te aviso cuando la revisen o si hace falta algo más" sin frases en las instrucciones.
    - **La instrucción de la redacción cambió a propósito** (huella `d8c6b0de58c4c2a3` →
      `3f267a24d030de4a`, `tests/motor/test_contratos.py`): "con esa persona como sujeto del verbo
      notificar" pedía el nombre; ahora el sujeto es esa persona si un hecho la nombra a la vista, y
      si no, lo que se informa ("La nueva fecha queda informada").
    - **"Revisión" para lo que espera:** `queda_esperando_la_aprobacion_de`, `entrega_para_aprobar`,
      `aprobacion_trabada` y `aprobacion_destrabada` son conceptos de la cocina y la redacción recibe
      `queda_esperando_la_revision_de`, `entrega_para_revisar`, `revision_trabada` y
      `revision_destrabada`; los significados de la espera dicen revisión; "aprobar" queda para la
      decisión. La página de la tarea dice "en revisión" (`tarea_vista.ESTADOS`).
    - **"Describir":** el significado y el dato `el_texto_cubre` (`hechos.py`, `ia_real.DATOS`).
    - **Las conversaciones** (`7bf13f2`): 02, 04, 11, 12, 15, 16, 18 a 25 esperan la fecha
      "informada", "pasa a revisión", "quedó aprobada" y "le pidieron un cambio" sin nombrar a
      Ismael, con `no_dice` del nombre; la 21 suma el paso 6, "a quien le avisaste?", que se
      contesta con el nombre y la hora (el aviso a Ismael pasa al 7). La 20 deja escrito que
      "Ismael será notificado" quedó superado.
    - **Rojo primero:** seis pruebas nuevas fallaron antes del cambio (`test_entrega`,
      `test_fichas`, `test_hechos` y tres de `test_palabras_de_la_redaccion`: el nombre a la vista,
      los nombres de la espera y "cuenta").
    - **Pruebas:** `pytest tests/motor tests/conversaciones`, 793 passed (sin la intermitente);
      `pytest tests/garantias`, 319 passed; en seco, `correr --ia guionada --veces 1 --ronda
      seco-d2`, 25 de 25 bien (informes borrados). Sin la IA real (D6).
    - `PENDIENTE` (del usuario): si "eso lo decide Ismael" ante un pedido de reasignación
      (`quien_decide`, conversaciones 12 y 19) sigue valiendo: hoy queda a la vista, como respuesta
      a lo que pidió. `PENDIENTE`: `espacios/corework.yaml` dice de la explicación "contado por
      quien lo hizo" (`en_palabras`, dato del pack, que la IA lee): cambiarlo a "descrito" es
      configuración del cliente y quedó fuera de esta unidad. La regresión con la IA real (D6) dirá
      si la IA escribe "queda informada" y contesta el nombre.
  - [x] **D3.** La entrega (decisiones 10, 14 y 15): comparar lo descrito con el criterio, preguntar
    sólo lo que falta con un ejemplo sacado del criterio y no entregar hasta cubrirlo; entregar una
    tarea sin arrancar; pedir la pieza correcta si una retirada deja la entrega incompleta. Route:
    delegada (escritor único, 2+ archivos no triviales). Hecha el 2026-10-08:
    - **Lo que llegó, una sola vez** (`2cba3bd`, el `PENDIENTE` de la D1): una jugada que toma lo
      que trajo el mensaje (`Ficha.toma_lo_que_llego`: `entregar`, `guardar_para_la_entrega`) y no
      dice la tarea deja su duda con eso (`entrega.para_la_duda`) y lo marca atendido; al terminar
      las jugadas no se vuelve a correr, y la elección usa lo de aquel mensaje. Regla general, no
      de la 22. Rojo primero: los hechos salían dos veces.
    - **Lo que describe cada texto** (`1113cba`, migración `0038` con su rollback, que se niega si
      perdería datos, y su ensayo de paridad): `evidence.describe_del_criterio`, los puntos del
      criterio que la persona confirmó que describe un texto, tal cual se decían; sólo un texto
      (restricción). La cocina lo escribe al entregar. Rojo primero: dos pruebas de garantías.
    - **El criterio como compuerta** (`ea2278e`, decisión 10). Diseño: el criterio se lee por
      puntos (`entrega.puntos_del_criterio`: renglones, oraciones y punto y coma; una oración es un
      punto aunque diga dos cosas, el código no parte por palabras). La IA que elige la jugada recibe
      los puntos (`criterio_de_aceptacion`, C1, C2...) y juzga cuáles dice todo lo descrito
      (`lo_descrito_cubre`, lista cerrada como `el_texto_cubre`); si falta alguno, escribe un
      ejemplo (`ejemplo`). El código guarda en cada texto lo que describe, calcula qué falta y sólo
      con la política y el criterio cubiertos ofrece Confirmar; lo no juzgado no está dicho; un
      "mandala así" con algo pendiente no entrega (`le_falta_algo`) y vuelve a proponer. El ejemplo
      pasa por un verificador (`problema_del_ejemplo`, como el `_problema_de_propuesta` del flujo C):
      cada número y cada nombre o sigla tiene que estar en el criterio, la tarea o lo que escribió la
      persona; si no, se propone el punto del criterio tal cual (nunca falta un ejemplo). El ejemplo
      cuenta como descrito sólo si la persona lo acepta (`acepta_el_ejemplo` en `entregar`, y sólo
      si se le propuso en un mensaje anterior); queda en la pregunta abierta, así que "¿y qué pongo?"
      (sin jugada) lo vuelve a decir. La persona corrige la lectura en la vista previa (`corregir`
      con `lo_descrito_cubre`). Hallazgo 1 de la bitácora: un texto cubre siempre lo que sólo un
      texto puede cubrir, y `el_texto_cubre` suma. El pack dice "descrito por quien lo hizo". Las
      instrucciones de la IA no cambiaron (huellas iguales): todo va en los datos de las fichas y en
      los significados. Conversaciones: la 27 nueva (README, `test_corredor`); la 22 suma el
      criterio, con el ejemplo aceptado en el paso 7 y la confirmación en el 8; la 12 pide lo que
      falta del criterio; la 21, la 23 y la 24 describen el criterio en su entrega. Rojo primero:
      doce pruebas de `test_entrega`.
    - **Una tarea sin arrancar** (`a3dbb33`, decisión 14): `entregar` vale sobre una tarea asignada;
      al confirmar, la cocina anota en el mismo acto que arrancó y se entregó en ese momento (dos
      eventos de la persona, sin fecha de inicio inventada), con la regla de siempre para arrancar
      (no con una dependencia bloqueante abierta). La 25, paso 8, deja de ser `PENDIENTE`. Rojo
      primero: cinco pruebas.
    - **Una pieza retirada** (`f96f071`, decisión 15): si un retiro deja la entrega sin lo que pide
      la política o sin un punto que dejó de estar dicho (lo que describían las piezas retiradas y
      ninguna de las que siguen), Leda pide la pieza correcta con el tema abierto de lo que falta y
      su ejemplo; el aviso a quien aprueba que no salió queda omitido (`la_entrega_esta_incompleta`,
      también al releerlo al salir), y aprobar no cambia nada (`la_entrega_se_esta_completando`, con
      `se_le_avisa_cuando_este_completa`). Con la pieza nueva confirmada, la cocina la suma a la
      tarea en revisión sin moverla (`entrega_completa`) y a quien aprueba le llega un aviso nuevo
      con todo (T6i). Rojo primero: seis pruebas.
    - **Pruebas:** `pytest tests/motor tests/conversaciones`, 813 passed y 1 failed, la
      intermitente (`test_corredor.py::test_la_corrida_en_seco_por_linea_de_comandos_graba_y_repite`,
      que pasó al repetirla sola); `pytest tests/garantias`, 323 passed; suite completa,
      1565 passed; en seco, `correr --ia guionada --veces 1 --ronda seco-d3`, 26 de 26 bien
      (informes borrados). Sin la IA real (D6).
    - `PENDIENTE`: con un criterio de una sola oración, preguntar sólo la parte que falta queda a
      cargo de la redacción (lo medirá la D6), y que la plataforma pida un punto por renglón es de
      su ADR; si la IA real elige `confirmar` en lugar de `acepta_el_ejemplo` ante un "sí" (lo
      medirá la D6); los recordatorios a quien aprueba no esperan mientras la entrega está
      incompleta; tras un retiro, el ejemplo es el punto del criterio tal cual (`corregir` no trae
      el de la IA); `leda_motor` necesita la `0038` (D6).
    - **Revisión RDD por commit, aprobadas y reconocidas:** `2cba3bd` `review-cd732b2fc3f2ce71`,
      `1113cba` `review-a595576282a67fd4`, `ea2278e` `review-f307c08e72372635`, `a3dbb33`
      `review-7f6439e18bf3b142`, `f96f071` `review-ca70ebd0113ecefa`. Advertencias abiertas (casos de
      borde): `fichas.py:1315` (la duda de `entregar` sin prueba), `herramientas.py:1783` (lo que
      describe un texto sin validar contra los puntos), `entrega.py:342` (el juicio de la IA puede
      pisar un ejemplo aceptado), `entrega.py:636` (lo que falta del criterio desactualizado),
      `entrega.py:469` (huella de entregas viejas), `entrega.py:309` (retiro y criterio sin prueba),
      `entrega.py:659` (la vista previa de una tarea sin arrancar no mira la dependencia),
      `aprobacion.py:141` (aprobar mezcla la política y el criterio incompletos) y
      `herramientas.py:1829` (sumar a una entrega acepta cualquier tarea en revisión). Las de
      `entrega.py:342` y `herramientas.py:1829` se miraron en la D4: la primera era un error
      (arreglado, `f58065b`); la segunda, no.
  - [x] **D4.** La aprobación (decisiones 12, 16 y 17): "¿cuál de las dos?" una sola vez; el aviso a
    quien aprueba al salir (si cambió); las entregas y los recordatorios en listas con un botón por
    tarea, y lo que queda por revisar después de decidir una. Route: delegada (escritor único, 2+
    archivos no triviales). Hecha el 2026-10-08:
    - **Las dos advertencias de la D3:**
      - `entrega.py` (el juicio de la IA pisaba un ejemplo aceptado) **era un error**: después de
        aceptar el ejemplo, un `entregar` sin texto nuevo con un `lo_descrito_cubre` que lo olvidaba
        le sacaba al ejemplo lo que describía, y Leda volvía a pedir lo que la persona ya había
        aceptado. Ahora el ejemplo aceptado conserva lo suyo frente al juicio de la IA; la
        corrección explícita de la persona (`corregir`) sí lo cambia. `f58065b`. Rojo primero:
        `test_el_ejemplo_aceptado_no_lo_pisa_otro_juicio_de_la_ia` (`le_falta_evidencia` en lugar
        de `para_confirmar`).
      - `herramientas.py` (sumar a una entrega acepta cualquier tarea en revisión) **no es un
        error**: la cocina exige que la tarea sea de quien entrega (`Denegado` si no) antes de
        mirar el estado; el único camino que llega a completar una entrega en revisión es la
        confirmación del motor, que sólo existe con la entrega incompleta (`entrega.entregar`,
        `falta_algo_de_lo_entregado`), y sumar evidencia del responsable a una tarea en revisión es
        lo que ya permite el dominio (`adjuntar_evidencia`, T6i). Sin cambio de código.
    - **Decisión 12, "¿cuál de las dos?" una sola vez** (`c519de1`): el tipo de pregunta declara
      que se hace una vez y qué queda si no se elige (`TipoDePregunta.sin_elegir_queda`). Si el
      mensaje siguiente no la contesta (sin jugada, o otra vez las dos lecturas), Leda no decide ni
      la repite: la cierra sin efecto y sus opciones, con lo que la persona había dicho y la huella
      de lo entregado, quedan como la decisión de la entrega ofrecida en la respuesta
      (`preguntas.ofrecer_en_la_respuesta`, atada a su fila del outbox; `botones.ConOpciones` las
      suma a la respuesta), sin ser un tema abierto; los hechos lo dicen (`no_eligio`,
      `pregunta_hecha_una_vez`, `botones`). Lo que elige sigue siendo de la IA (`elegir`, o
      `aprobar` con lo demás como comentario): el significado de `cual_de_las_dos` y el `es` de
      `aprobar` lo dicen, y el de `comentario` dice que en una aprobación no es un cambio
      pendiente. Rojo primero: dos de las tres pruebas nuevas de `test_aprobacion.py`
      (`dos_lecturas` en lugar de `no_eligio`).
    - **Decisión 17, las listas** (`4102009`): los avisos de entrega a una persona que salen juntos
      van en un solo mensaje (`TipoDeAviso.se_agrupa`): cada tarea con quién la entregó y cuántas
      fotos trae (`fotos_que_trae`), sin fotos, sin enlace ni Aprobar y Pedir cambios, y un botón
      por tarea, "Ver" y su título (`preguntas.VER_LA_ENTREGA`, que no reemplaza a otro). Uno solo
      sale como antes. Ver una entrega es una jugada nueva de la lista cerrada (`ver_entrega`, para
      quien la revisa), tocada o escrita: la respuesta trae lo entregado, las fotos en el álbum que
      sigue al texto, el enlace a la página y Aprobar y Pedir cambios con su huella. Después de
      decidir una, la respuesta dice lo que queda por revisar (`queda_por_revisar`, sin las ya
      aprobadas que esperan otra cosa) con un botón por tarea, sin ningún aviso nuevo; los
      recordatorios llevan su botón para verla (`ofrece_ver`). Los avisos de un mismo momento salen
      ordenados por el título de su tarea, para que el texto y los botones vayan siempre en el mismo
      orden. El tope diario no cambió: cuenta mensajes, y los de coordinación siguen fuera. El
      mismo commit trae la primera parte de la decisión 16 (`TipoDeAviso.va_a`) y la respuesta a un
      botón de una tarea que ya no es de la persona (`ya_no_le_corresponde`, con
      `la_revisa_otra_persona`), que también usan las listas. Rojo primero: seis de las siete
      pruebas nuevas (sin la ficha). Las instrucciones de la IA no cambiaron (huellas iguales).
    - **Decisión 16, si cambia quién aprueba** (`8ff76e7`, y `va_a` en `4102009`): el aviso de la
      entrega se relee al salir y va a quien aprueba en ese momento (la misma fila, la misma clave);
      si el cambio es después de que salió, la escalera le guarda al nuevo, una vez, el aviso de lo
      que espera su decisión (`antes_la_revisaba_otra_persona`), y su cuenta empieza cuando sale; el
      botón del aviso viejo le dice al anterior que esa tarea ya no la revisa él, sin cambiar nada.
      Rojo primero: `test_si_cambia_despues_al_nuevo_le_llega_lo_que_espera_su_decision` (ningún
      aviso al nuevo); la de antes de salir se escribió después de `va_a`, sin rojo observado en la
      prueba del motor (sí en la corrida en seco de la 29).
    - **Conversaciones:** la 28 (las listas, la pregunta una sola vez y lo que queda) y la 29 (cambia
      quién revisa), nuevas, con su YAML, en el README y en `test_corredor`; la 23 manda sus cuatro
      avisos del viernes de a uno y espera lo que queda por revisar después de cada decisión; la 24,
      el botón de cada recordatorio. El corredor aprende `Ver <clave>`, las fotos y el enlace de una
      respuesta y `cambia_quien_aprueba`. Rojo primero, en seco y antes del código: la 23 con 6
      fallas, la 28 con 20 y la 29 con 13.
    - **Chequeos** (2026-10-08, sobre `8ff76e7`): `pytest tests/motor tests/conversaciones`, 828
      passed; `pytest tests/garantias`, 323 passed; suite completa, 1579 passed; en seco,
      `correr --ia guionada --veces 1 --ronda seco-d4`, 28 de 28 bien (informes borrados). Sin la
      IA real (D6). Sin migración: el esquema ya tenía lo que hacía falta.
    - `PENDIENTE`:
      - Que la IA real elija la opción (o `aprobar` con el comentario) ante "aprobala nomás y pasale
        lo de los colores" y no otra vez las dos jugadas: si las repite, Leda no decide (seguro,
        pero no lo que quiso decir la persona). Lo mide la D6.
      - Los botones dicen "Ver" y el título entero de la tarea (hasta 80 caracteres), no un nombre
        corto como "Ver PLC": las tareas no tienen nombre corto (sería de la plataforma).
      - Una lista sale sólo con los avisos que vencen en la misma vuelta del ciclo: dos entregas
        confirmadas con minutos de diferencia salen por separado, salvo que la D5 (no interrumpir)
        las demore juntas (desde la D5: si quien revisa conversa, esperan juntas y salen en una
        lista).
      - Si en la misma respuesta vuelve una pregunta con opciones, sus botones y los de la decisión
        ofrecida salen juntos (los de la pregunta primero).
      - Los botones "Ver" no se cierran al decidir: tocar uno de una tarea ya decidida dice que ya no
        le corresponde (o que está cerrada) y no cambia nada.
      - `fotos_que_trae` cuenta las imágenes de la entrega; los videos y archivos no.
    - **Revisión RDD por commit, aprobadas y reconocidas:** `f58065b` `review-f31fb02f109ad5e9`,
      `c519de1` `review-b31c4fb8cd3980e4`, `4102009` `review-9464addc613fbf91` (su advertencia de
      que faltaba el cambio de aprobador después de salir la resuelve `8ff76e7`), `8ff76e7`
      `review-4728a51e6739d0cf`. Advertencias abiertas (casos de borde): `entrega.py:367` (lo que
      describe el ejemplo aceptado se suma sin normalizar), `fichas.py:1503` y `turno.py:224` (la
      huella y los botones ofrecidos sólo en el camino feliz), `situaciones.py:137` ("ya no está" sin
      prueba), `28-entregas-en-una-lista.yaml:229` (las fotos adjuntas sin comprobar),
      `test_aprobacion.py:700` (el filtro de lo ya aprobado sin probar) y `escalera.py:541` y
      `:594` (el aviso al aprobador nuevo no relee si la entrega sigue vigente; su escalera sin
      prueba). La de `escalera.py:541` era un error, arreglado en la D5 (`53ee594`).
  - [x] **D5.** No interrumpir (decisión 13, conversación 26 con su YAML). Route: delegada (escritor
    único, 2+ archivos no triviales). Hecha el 2026-10-08:
    - **La advertencia de la D4 (`escalera.py:541`) era un error** (`53ee594`): si cambiaba quién
      aprueba después de que salió el aviso de la entrega, la escalera le guardaba al nuevo el aviso de
      lo que espera su decisión antes de mirar si el nuevo ya la había aprobado (una aprobación que
      todavía no cierra), y al salir el aviso no miraba esa aprobación. Ahora la escalera mira primero
      si ya decidió, y el aviso de una entrega se omite al salir si quien lo recibe ya la aprobó
      (`ya_decidio`). Rojo primero: `test_si_el_nuevo_ya_decidio_no_se_le_guarda_lo_que_espera_su_
      decision` (el aviso guardado) y `test_si_el_nuevo_decide_antes_de_que_salga_el_aviso_se_omite`
      (`enviado` en lugar de `omitido`).
    - **La espera** (`daaf8a9`, `leda.motor.no_interrumpir`): un aviso a una persona espera 30
      minutos desde lo último que escribió o tocó (su último turno de entrada), o los del espacio
      (`no_interrumpir_minutos` en `workspace_setting`, 0 o más, como el margen; un valor que no
      vale usa el del producto); cada mensaje vuelve a contar. La comprobación está en
      `avisos._preparar`, después de a quién va (decisión 16) y de la ausencia: el aviso queda
      `guardado` (`en_espera`) y se vuelve a mirar en cada vuelta. Vale para todos los avisos a esa
      persona, también los de coordinación (punto 6), y nunca demora a otra persona. El fin de la
      espera pasa por `tiempo.sale`: nunca antes de la hora de salida ni fuera del horario (si cruza
      el cierre, sale el día hábil siguiente a las 10:00, releído). Sin migración: el valor por
      omisión vive en el código, como el del margen; `docs/product/plataforma-pendientes.md` ya lo
      tenía anotado y ahora dice que está construido.
    - **Lo que se le cuenta a otra persona** (`daaf8a9`): los hechos dicen cuándo se entera de verdad
      (`no_interrumpir.cuando_sale`): si quien recibe el aviso está conversando, la hora en que termina
      su espera, en `efectos._aviso` (al final del turno), en el próximo aviso de la persona
      (`efectos._lo_que_sigue`) y en la previsión vigente de la escalera (`avisos.prevision_vigente`).
      Sin esto, la 27 le decía a Marcos que Ismael se enteraba a las 15:41, y salía a las 15:55.
    - **Un tema a la vez y lo ya hablado** (`878e244`): con una pregunta de Leda sin contestar (la
      abierta, `preguntas.actual`; la decisión que ofrece una entrega no lo es), en el envío
      (`avisos._un_tema_a_la_vez`): la pregunta misma, repetida por su escalera (mismo tipo, o la
      misma espera, y la misma tarea), sale sola; uno de otra tarea que no pide respuesta sale
      aparte, sin pregunta; uno que pide respuesta (una pregunta, o decidir) y uno de la misma tarea
      esperan a que se cierre. Al salir, el aviso previo y el recordatorio del vencimiento de una
      tarea de la que la persona habló después de que se guardaron se omiten
      (`ya_se_hablo_de_la_tarea`, con su significado): "habló" es que algún hecho de un mensaje suyo
      nombra esa tarea, la lectura de `fichas._siguio_en_la_tarea`
      (`TipoDeAviso.se_omite_si_ya_se_hablo`).
    - **El `PENDIENTE` de la D4 (las listas):** avisos de entrega confirmados con minutos de
      diferencia que esperan juntos porque quien revisa está conversando salen en una sola lista
      (`test_las_entregas_que_esperan_mientras_quien_revisa_conversa_salen_en_una_lista`, escrita
      después del código, sin rojo observado). Si quien revisa no está conversando, siguen saliendo
      por separado.
    - **Conversaciones:** la 26 tiene su YAML (el hilo principal; los pasos 4 y 5 del `.md` estaban
      con las horas al revés y se ordenaron; el horario es hasta las 17:00; el `.md` dice cómo se
      leyó lo que la regla no dice); sus variantes 1 a 3 las prueban las pruebas del motor
      (`tests/motor/test_no_interrumpir.py`). En el README y en `test_corredor` (29). La 23: Marcos
      escribe a las 09:40 (no a las 10:20) para que los avisos de sus aprobaciones le lleguen
      enseguida, como dice el hilo, y el recordatorio del lunes a Ismael espera mientras decide y,
      releído el martes, queda omitido: resuelve el `PENDIENTE` de la 3c sobre la 23. La 24: el
      preludio corre cada reloj en su momento (antes, el de las 11:15 corría después del mensaje de
      Marcos de las 11:30). La 27: el aviso nuevo a Ismael sale a las 15:55 (tocó Aprobar a las
      15:25), y los hechos del paso 10 lo dicen.
    - **Las pruebas que cambiaron por la regla** (la hora, no lo que miran): `test_ancla.py`,
      `test_aprobacion.py` (tres), `test_avisos.py` (el aviso de la falla), `test_escalera.py` (el
      aviso previo del vencimiento nuevo espera detrás de la pregunta del estado que nunca se
      contestó; ver `PENDIENTE`) y la fixture de `test_recordatorios_de_la_decision.py`.
    - **Test primero:** la 26 corrió en seco con su YAML antes del código: 5 fallas (pasos 2, 4, 5 y
      6). `tests/motor/test_no_interrumpir.py`, con el módulo sólo con la espera configurable, 11 de
      22 en rojo (las otras 11: la configuración y tres que miran que algo no pase); la de lo que se
      le cuenta a otra persona, en rojo (10:11 en lugar de 10:30) antes de `cuando_sale`.
    - **Las instrucciones de la IA no cambiaron** (las huellas de `test_contratos.py` siguen): el
      motivo nuevo llega con su significado (`hechos.py`).
    - **Chequeos** (2026-10-08, sobre `878e244`): `pytest tests/motor tests/conversaciones`, 856
      passed; `pytest tests/garantias`, 323 passed; suite completa, 1607 passed; en seco, `correr
      --ia guionada --veces 1 --ronda seco-d5`, 29 de 29 bien, la 26 entera (informes borrados).
      En el estado intermedio (`daaf8a9`), `pytest tests/motor tests/conversaciones` dio 840 passed
      más las 8 de la configuración, que fallaban por un ayudante que faltaba en la prueba; corregido
      antes del commit (`test_no_interrumpir.py`, 17 passed). Sin la IA real (D6).
    - `PENDIENTE` (decisiones del usuario; lo construido es la lectura que no interrumpe):
      - **Una pregunta que nunca se contesta frena.** Mientras siga abierta, los avisos que piden
        respuesta (de cualquier tarea) y los de su misma tarea esperan, aunque pasen días, y la
        escalera de esas tareas no avanza. Ejemplo: el viernes Marcos deja sin confirmar la vista
        previa de una entrega (o no contesta un pedido de estado que ya escaló); el lunes vence otra
        tarea: el pedido de estado de ésa espera hasta que Marcos confirme o deje la vista previa, y
        si no lo hace, a Ismael no le llega nada de esa otra tarea. ¿Se acota (por ejemplo, la
        pregunta frena sólo el día en que se hizo, o hasta que escala)?
      - **Lo ya hablado** omite sólo el aviso previo y el recordatorio del vencimiento (no piden nada
        ni traen el acto de otra persona). Los demás (una previsión, una decisión, un escalamiento,
        un pedido de estado) esperan y salen releídos: omitirlos perdería algo que la persona no
        sabe. ¿Alcanza así?
      - **Un aviso de la misma tarea que la pregunta abierta** espera aunque no pida respuesta ("de
        ese tema sólo le llega la pregunta"): con la pregunta del estado sin contestar y ya escalada,
        el aviso previo de un vencimiento nuevo de esa tarea no sale (`test_escalera.py`, antes
        salía).
      - **"Pide respuesta"** incluye el aviso de una entrega (ofrece decidir) y los recordatorios
        de una decisión: esperan a que se cierre la pregunta abierta de quien revisa.
      - **Los avisos de una decisión** (aprobada, cambios pedidos), que salen sin margen (decisión
        19), esperan si el responsable está conversando (punto 6).
    - **Advertencias** (casos de borde): la hora que dicen los hechos es la del turno; si quien
      recibe el aviso sigue escribiendo después, sale más tarde que lo dicho. Lo ya hablado reconoce
      la tarea por su título, como `_siguio_en_la_tarea`: dos tareas de la persona con el mismo
      título se confunden.
    - **Revisión RDD por commit, aprobadas y reconocidas:** `53ee594` `review-1479340d13f12f6c`,
      `daaf8a9` `review-7fe30214e4f17f66`, `878e244` `review-9b5e458148257a72`. Advertencias
      abiertas (casos de borde): `no_interrumpir.py:45` (un valor enorme de la espera),
      `no_interrumpir.py:68` (un mensaje viejo corre la ventana siguiente), `no_interrumpir.py:97` y
      `avisos.py:335` (del tema abierto), y sugerencias de pruebas en `efectos.py` y `avisos.py:1084`.
  - [x] **D6.** La regresión con la IA real, `leda_motor` al día (autorizado por el usuario de
    antemano, con respaldo) y el guion de la prueba por Telegram (el enlace con `localhost`,
    decisión 20). Route: delegada (un trabajador: la ronda, el diagnóstico, la base y el guion). Hecha el
    2026-10-08:
    - **La ronda** (sol por la suscripción, 29 conversaciones, 5 veces, sobre `eec2b8a`): válida en
      tres tramos, `resultados/fase-c-d6-01-20.md`, `fase-c-d6-21-29.md` (sólo la 21 y la 22) y
      `fase-c-d6-23-29.md`. Antes, un intento entero chocó con el cupo (429 en todas las llamadas,
      informe borrado), uno se cayó al anotar el gasto (`PermissionError` de Windows sobre
      `gasto.json`, sin informe) y el tercero se quedó sin cupo en la 23; el usuario cambió de cuenta.
      Corridas empezadas: 370; válidas: 147 (las 29, 5 veces). Resultado y diagnóstico, en la bitácora
      ("La regresión de la C-3d con la IA real"): garantías 5 de 5 salvo la 25 (la lectura equivocada
      conocida), la 27 y la 28; comprensión 5 de 5 en 21 de las 29.
    - **YAML aflojados** (lo que la ficha permite; en seco `--ronda seco-d6`, 5 de 5 bien, y
      `pytest tests/conversaciones`, 131 passed): el ejemplo con las palabras de la IA en la 12, la 22,
      la 25 y la 27 (`puede_traer: [lo_descrito_cubre, ejemplo]` y `ejemplo: presente`; al aceptar el
      ejemplo puede venir `lo_descrito_cubre: [C1]`); la 23, paso 9, espera `aprobar` con el comentario
      (decisión 12), que la IA elige 5 de 5.
    - **`leda_motor`:** respaldo `db/respaldos/leda_motor-antes-fase-c-d6-20261008.dump` (283.721
      bytes, `pg_restore --list` sin error); las migraciones `0034` a `0038` aplicadas en el lugar con
      `psql -f` (todas sin error). Como `sembrar` no siembra en un espacio con tareas y las de la base
      tenían el criterio de relleno, después se recreó (`esquema --recrear`, `importar corework
      --activar`, `feriados`, `modelo gpt-6-sol --proveedor chatgpt`, `sembrar` con una copia temporal
      de la semilla fuera del repositorio, `administrador corework Ariel` y `aviso_previo_dias_habiles`
      = 3). Quedan 12 tareas (6 asignadas, 6 en curso) con criterios concretos que vencen el vie 16/10,
      la política de evidencia con las clases de cada tipo (6 áreas, 12 tipos) y 5 áreas con su
      referente; el reloj de Leda, en tiempo real. La semilla del repositorio sigue con el criterio de
      relleno.
    - **El guion:** `docs/product/guion-telegram-fase-c-parte-1.md` (`d54a041`). La página se sirve con
      `uvicorn leda.entrada:app --host 127.0.0.1 --port 8000 --no-access-log` y no con `servir`, que
      además arranca otro ciclo de Leda (avisos y la sesión de ChatGPT a la vez que el escuchador) y
      escucha en el 8080.
    - `PENDIENTE` (decisiones del usuario, con los ejemplos de la bitácora):
      - **Insistir en mandar una entrega incompleta** ("no, asi esta, mandala"): la IA no lo lleva a
        `confirmar` y cae fuera de la lista (aviso a la administración) o, una vez de cinco, lo toma como
        que acepta el ejemplo que rechazó. Es de diseño: qué jugada es "mandala así" con algo pendiente.
      - **Quién juzga lo que cubre un texto** (la 21, paso 1, 5 de 5): la IA pide confirmar que arrancó
        desde el PLC a quien escribió "20 ciclos sin una falla".
      - **"y bueno fijate vos"** cae fuera de la lista (la 28): ¿un aviso a la administración cada vez?
      - **Nombrar a Ismael al retirar un aviso** (la 11, paso 4): "Ismael no será informado…".
      - **Decisión 20:** el guion no usa `servir` (ver arriba); confirmar con el usuario.
    - **El corredor, arreglado** (2026-10-08, después de la ronda; route: delegada, un escritor, dos
      archivos no triviales; primero en rojo, después en verde; sin la IA real):
      - **El cupo agotado corta la ronda** (`01c5ffe`): el HTTP 429 `usage_limit_reached` de la
        suscripción (o ese código dentro del flujo) es `gasto.SinCuota`, con cuándo se renueva
        (`resets_in_seconds` o `resets_at`). La ronda se corta como con el 402: no empieza ninguna
        corrida más, las que lo tuvieron son inválidas, el informe dice el motivo y cuándo se renueva,
        y sale con 4 (`SALIDA_SIN_CUOTA`). Un 429 con otro código no corta. `chatgpt.py` no cambió.
      - **La libreta tomada no se lleva el informe** (`29cd66d`): `Gasto.anotar` reintenta unos 2 s
        ante el `PermissionError` y, si sigue tomada, deja lo pendiente en
        `gasto-pendiente-<fecha>.json` con un aviso; entra a la libreta en la próxima escritura que
        pueda y el archivo aparte se borra.
      - `pytest tests/conversaciones tests/motor/test_chatgpt.py`: 185 passed; en seco
        `--ronda seco-corredor`, 29 de 29 bien (informes borrados, `gasto.json` sin tocar).
    - **Revisión RDD, aprobadas y reconocidas:** `eb0cd1a` (los YAML aflojados)
      `review-bf5579572725ac35`, con advertencias: el texto del ejemplo aceptado no se comprueba en la
      22 y la 27, y el comentario de la aprobación en la 23 se compara literal; `01c5ffe..29cd66d`
      `review-ac5f83ca192bdccf`, con una advertencia en `gasto.py:402`.
  - [x] **D7.** Las fallas de Leda de la ronda de la D6, con reglas ya decididas, cada una como mecanismo
    general (2026-10-08, de noche). Route: delegada (escritor único, 2+ archivos no triviales). El punto
    4 necesitó `tests/conversaciones/test_corredor.py`, autorizado por el coordinador sólo para los
    números de paso de la 21. Sin la IA real (el cupo de ChatGPT está agotado): su chequeo es
    `PENDIENTE`.
    - **1. El nombre de quien aprueba al retirar un aviso** (la 11, paso 4, 5 de 5: "Ismael no será
      informado del atraso que habías previsto"; decisión 11). Lo anunciado que ya no va a pasar
      (`ya_no_va_a_pasar`) dice con qué dato se contó (`anuncio`); si ese dato es uno de
      `hechos.NOMBRAN_A_QUIEN_APRUEBA_SU_TRABAJO`, el nombre va dentro de `solo_si_pregunta`, como en el
      dato mismo, para cada aviso retirado o que ya no sale, también en los últimos turnos. `b792bdd`.
      Rojo primero: `test_lo_anunciado_que_ya_no_va_a_pasar_nombra_a_quien_aprueba_solo_si_pregunta`
      (Ismael a la vista). La 11, paso 4, suma `no_dice` del nombre.
    - **2. Una respuesta a la pregunta abierta nunca es un pedido nuevo** (la 27, paso 3, 4 de 5, y la
      28, paso 4, 5 de 5: aviso a la administración cada vez). Regla: mientras una pregunta de Leda está
      abierta, el mensaje que la contesta sin ser una jugada lo maneja esa pregunta y nunca avisa a la
      administración. Quién lee si contesta es la IA, con un dato nuevo de lo que no está en la lista
      (`contesta_la_pregunta`, que describe el dato, sin casos ni frases); el código decide
      (`turno.contesta_la_abierta`): con una pregunta abierta que la persona vio en un mensaje anterior,
      esa jugada no corre, no hay aviso, y el turno sigue como un mensaje sin jugada (la de lo que falta
      vuelve con su ejemplo; la de "¿cuál de las dos?" queda sin elegir, con los botones). Un pedido que
      la IA no marca así, o uno marcado sin pregunta abierta, sigue fuera de la lista con su aviso (la 12
      no cambia). Además, la ficha de `confirmar` dice que también es pedir que la entrega vaya como
      está aunque le falte algo (la cocina se niega, `le_falta_algo`): era la jugada esperada de la 27 y
      la ficha no la alcanzaba. `dde9b4e`. Rojo primero: tres de cuatro pruebas nuevas (`test_entrega`,
      `test_aprobacion`, `test_ia_real`); la del pedido nuevo con una pregunta abierta mira que algo no
      cambie y ya pasaba.
    - **3. El ejemplo que no se aceptó** (la 27, paso 3, 1 de 5: "no, así está, mandala" se leyó como
      `acepta_el_ejemplo` y la vista previa sumó "los 20 ciclos sin fallas"). Aceptar es sólo de la IA:
      la cocina no puede saber, sin frases, que "no, así está" rechaza. Lo que sí hace ahora: si el mismo
      mensaje también contesta la pregunta de otra forma (`entrega.OTRAS_RESPUESTAS`: pedir que vaya
      así, dejarla sin efecto o para más tarde, o algo fuera de la lista), las dos lecturas se excluyen y
      ni el ejemplo ni el mensaje se suman (la vez 2 de la ronda eligió `cancelar` y
      `fuera_de_la_lista`); la pieza del ejemplo aceptado es `el_ejemplo_que_acepto`, nunca
      `lo_que_escribio`, así la vista previa dice que se sumó por su sí y no que lo escribió; y el dato
      `acepta_el_ejemplo` dice que decirle que no, o pedir que vaya sin él, no es aceptarlo. `5388cea`.
      Rojo primero: las seis variantes de `test_el_ejemplo_no_se_suma_si_el_mensaje_tambien_contesta_
      otra_cosa` y la de la pieza aceptada (`lo_que_escribio` en lugar de `el_ejemplo_que_acepto`). La
      22 (paso 7) y la 27 (paso 4) esperan la pieza nueva y su `no_dice`.
    - **4. La 21, paso 1, no es una falla de Leda** (5 de 5: pide sólo si arranca desde el PLC, que
      Marcos no escribió; decisión 10). La 21 tiene ahora 8 pasos: 1, la entrega con las dos fotos (falta
      si arranca desde el PLC, con el ejemplo, sin nada que confirmar); 2 (nuevo), "si va asi"
      (`entregar` con `acepta_el_ejemplo`: la vista previa con Confirmar); 3, saca la foto del martes
      (ahora P5); 4, toca el Confirmar del paso 2; 5, la foto con "dale mandala"; 6, "dale" (seis filas de
      evidencia, con el ejemplo aceptado); 7, "a quien le avisaste?"; 8, el aviso a Ismael. `.md`, YAML y
      README. En `test_corredor.py`, sólo los números que corre el paso nuevo: las fallas del aviso pasan
      del paso 7 al 8, las jugadas reemplazadas de los pasos 4 y 5 al 5 y 6, y lo escrito, del 5 al 6 y de
      6 a 7 piezas (sin un ejemplo propuesto, el "si va asi" de ese camino es un texto más). `d9d40ec`.
      Rojo primero: con el YAML nuevo y los números viejos, las dos pruebas del corredor fallaron (el paso
      7 en lugar del 8; ninguna falla de lo escrito en el 5); la corrida en seco de la 21 mostró que el
      ejemplo aceptado va antes de lo mandado antes y corre la foto del martes a P5.
    - **5. Cómo se dice lo que falta: el modelo que aprobó el usuario** (2026-10-08), referencia de lo
      que tiene que salir de los hechos, nunca un texto para la IA:
      > 📋 Programar PLC de la comprimidora
      > ✏️ Sumé tu descripción y las dos fotos.
      > ⚠️ Para entregarla falta saber si la comprimidora arranca desde el PLC.
      >
      > Por ejemplo: «Arranca desde el PLC y completó 20 ciclos sin fallas».
      >
      > ¿Va así?

      Con el formato aprobado el 2026-10-07 (sin negrita; el cierre, solo en su renglón): la negrita y la
      pregunta en el mismo renglón del ejemplo, en la primera copia del modelo, fueron un error del
      coordinador, no un cambio de formato. Las palabras son las del usuario.

      La IA escribía "Sumé lo que contaste… Todavía no se puede entregar… La tarea no pasó a revisión… ¿La
      confirmás o preferís contarlo con tus palabras?". Por la cocina (`82816ea`): lo que escribió quien
      entrega le llega a la redacción como `su_descripcion` y la entrega incompleta como
      `para_entregarla_falta` (dos conceptos de la cocina nuevos, `lo_que_escribio` y
      `falta_evidencia`); que todavía no se entrega lo dice sólo ese resultado (los significados de
      `le_falta`, `le_falta_del_criterio`, `le_falta_algo` y `no_vale_la_confirmacion` dejaron de
      repetirlo); la entrega incompleta ya no trae `al_confirmar` (sólo la completa se confirma); lo que
      falta del criterio es la parte que la descripción no dice, hablando de la tarea; y el ejemplo es
      una descripción que Leda propone y la persona acepta o reemplaza por la suya ("con sus palabras"
      desaparece). Rojo primero: `test_que_todavia_no_se_entrega_lo_dice_un_solo_hecho`,
      `test_lo_que_falta_de_una_entrega_se_lee_como_su_descripcion` y `test_sin_la_politica_completa_
      dice_que_falta_y_no_mueve_la_tarea` (`al_confirmar`). La 12 (paso 6), la 22, la 25 y la 27 (paso
      1) suman a `dice` "una sola vez qué falta para entregarla" y a `no_dice` "contaste" o "contarlo";
      los lee una persona: el corredor no mide texto fuera del formato (`comprobar.py`, fuera de la
      superficie). El formato no cambió.
    - **Las instrucciones de la IA no cambiaron** (las huellas de `test_contratos.py` siguen): todo va en
      los datos de las jugadas (`ia_real.DATOS`, `FUERA_DE_LA_LISTA_ES`), las fichas, los nombres para
      redactar y los significados.
    - **Chequeos** (2026-10-08, sobre `d9d40ec`): `pytest tests/motor tests/conversaciones`, 877
      passed (sin la intermitente); `pytest tests/garantias`, 323 passed; en seco, `correr --ia
      guionada --veces 1 --ronda seco-d7`, 29 de 29 bien, la 21 con sus 8 pasos (informes borrados,
      `gasto.json` sin tocar).
    - `PENDIENTE`:
      - **La IA real**, cuando vuelva el cupo: una sola ronda de la 11, la 21, la 27 y la 28, 5 veces,
        sin repetir sin preguntar.
      - **El corredor no admite dos jugadas válidas para un paso:** la 28, paso 4, espera ninguna jugada;
        si la IA elige `fuera_de_la_lista` con `contesta_la_pregunta`, la garantía pasa (sin aviso) y la
        comprensión marca falla, aunque lo que ve Ismael sea lo mismo. Igual en la 27, paso 3, frente a
        `confirmar`.
      - **Un "no" leído como aceptar, sin otra jugada en el mensaje** (la vez 5): la cocina no lo puede
        frenar sin frases. Quedan la ficha de `confirmar`, el dato de `acepta_el_ejemplo` y la vista
        previa que muestra el ejemplo como aceptado, antes de confirmar. Si vuelve a pasar con la IA
        real, es de diseño (punto 4 de los disparadores): por ejemplo, que aceptar el ejemplo lleve
        siempre su propia confirmación.
      - `aviso_que_no_salio` (el aviso de la falla a quien causó un aviso) nombra a quien iba, que
        puede ser quien aprueba su trabajo, a la vista: no estaba en lo pedido y no se tocó.
  - [x] **D7b.** Lo que dejó la ronda de la D7 con la IA real (`resultados/fase-c-d7.md`, sobre
    `46cf49c`: la 11, la 21, la 27 y la 28, 5 veces) y la decisión 22 (2026-10-08, de noche). Route:
    delegada (escritor único, 2+ archivos no triviales). Sin la IA real: su chequeo lo corre el
    coordinador.
    - **1. Decisión 22, aprobar con un comentario** (`902c629`; la 28, paso 3, vez 5: "esta bien pero
      que mariano revise el rotulo de los cables" llegó como `aprobar` con su comentario, sin
      `pedir_cambios`, y la tarea quedó terminada). Lo decide la cocina con los datos de la jugada
      (`aprobacion._antes_pregunta_cual`): un `aprobar` con comentario no cierra directo y abre la
      pregunta de una sola vez de "¿cuál de las dos?" (`fichas.dos_lecturas`, con las mismas dos
      opciones y el comentario en cada una), salvo que sea la elección: una opción tocada o escrita
      (`de_la_pregunta`) o la respuesta escrita a la de cuál de las dos sobre esa tarea, que la
      persona vio en un mensaje anterior (decisión 12: "aprobala nomás y pasale lo de los colores"
      aprueba directo). La IA sólo dice que trae un comentario: el dato `comentario` y la ficha de
      `aprobar` dicen que es lo que se le pasa a la persona responsable para que lo tenga en cuenta;
      el significado de `dos_lecturas` cubre los dos casos. La ficha sigue pidiendo las dos jugadas
      cuando además pide un cambio (las dos lecturas llevan a la misma pregunta). Conversaciones: la
      23, paso 2 ("el plc de marcos aprobado, impecable") ahora pregunta, y el paso nuevo 2b toca
      Aprobar (cierra con el comentario; el aviso a Marcos pasa a las 10:31); la 28 lo anota en el
      paso 3, y su paso 4 espera `fuera_de_la_lista` con `contesta_la_pregunta` (4 de 5 en la ronda;
      sin `puede_traer`: lo que no está en la lista no tiene ficha y el corredor no compara sus
      datos, `test_comprobar` lo exige). `docs/capacidades.md`. Rojo primero: tres de las pruebas
      nuevas de `test_aprobacion.py` (`anotado` en lugar de `dos_lecturas`) y la del dato.
    - **2. "Contar"** (`1bb9342`; 6 de 10 mensajes del paso 1 decían "contaste" o "contarlo", y los
      avisos a Ismael "Marcos contó…"). Las instrucciones de la redacción usaban "contás" como el
      verbo de Leda (18 veces "contar" o "se cuenta"); pasan a "decir" ("lo que la persona contó",
      "lo que dijo"), sin ninguna regla nueva ni frases. La ficha de `entregar` dice "describir", y
      los significados de `tarea`, `hechos`, `retiradas`, `el_ejemplo_que_acepto` y el encabezado de
      la lista de significados dejan "contar" y "cuenta". **La huella de la redacción cambió a
      propósito**: `3f267a24d030de4a` → `9e419fe6bbcc420a` (`test_contratos.py`, con el porqué); la de
      las jugadas no cambió. Rojo primero: `test_nada_de_lo_que_lee_la_ia_sobre_la_entrega_dice_
      contar`.
    - **3. Que todavía no se entrega, una sola vez** (`1bb9342`; "Para entregar el trabajo falta… por
      ahora sigue como estaba"). Lo dice sólo el nombre del resultado (`para_entregarla_falta`): el
      significado de `le_falta_evidencia` dejó "hasta entonces no se entrega y la tarea sigue como
      estaba", y el de la pregunta `lo_que_falta_de_la_entrega`, "para poder entregarla". La prueba
      recorre los nombres y los significados de una entrega incompleta, con el criterio. Rojo
      primero: `test_que_todavia_no_se_entrega_lo_dice_un_solo_hecho` (lo decían el significado y la
      pregunta, además del nombre).
    - **4. Los YAML que pedían más que la ficha** (`5582d39`), mirados contra las transcripciones y
      las fichas: la 21, paso 1, `puede_traer: [el_texto_cubre, lo_descrito_cubre, ejemplo]`; la 21,
      paso 5, `entregar` (5 de 5) con `puede_traer: [el_texto_cubre, lo_descrito_cubre]` y los hechos
      `para_confirmar`, `sumo: [P5, P6]` (lo que escribe es una pieza más), con la fila de texto de
      más en el paso 6 y `lo_que_escribio` de más en el aviso del paso 8; la 27, paso 4,
      `puede_traer: [lo_descrito_cubre, el_texto_cubre]`; la 27, paso 9, `entregar` (5 de 5) con el
      mismo `puede_traer`; la 28, paso 4, en el punto 1. La prueba del corredor del otro camino de
      la 21 toma ahora `confirmar` en el paso 5 (6 filas escritas). Los `.md` cambian con su YAML.
    - **5. El corredor en paralelo** (`15c1e65`; la 28, vez 5, sin el enlace desde el paso 2):
      `_con_la_direccion_de_prueba` cambiaba la configuración del proceso y devolvía la que vio al
      entrar; con `--paralelo`, la corrida que terminaba primero la vaciaba. Ahora la pone la primera
      corrida que arranca y la devuelve la última que termina, con un candado. Rojo primero:
      `test_la_direccion_de_prueba_vale_mientras_corra_alguna_corrida` (`''` en lugar de
      `https://leda.invalid`).
    - **Chequeos** (2026-10-08, sobre `15c1e65`): `pytest tests/motor tests/conversaciones`, 884
      passed y 1 failed, `test_un_envio_por_dia.py::test_dos_pedidos_de_estado_juntos_preguntan_de_a_
      uno`, que pasó solo tres veces (intermitente, no la conocida del corredor); `pytest
      tests/garantias`, 323 passed; en seco, `correr --ia guionada --veces 1 --ronda seco-d7b`, 29 de
      29 bien (informes borrados, `gasto.json` sin tocar).
    - `PENDIENTE`:
      - **La IA real** sobre la 21, la 23, la 27 y la 28 (el coordinador).
      - **"Impecable" ahora pregunta** (la 23, paso 2): la regla de la decisión 22 vale para todo
        comentario, también un elogio, así que "aprobado, impecable" lleva un toque más. Si el usuario
        quiere que un elogio cierre directo, hace falta otra decisión (por ejemplo, que el comentario
        de una aprobación sea sólo lo que le pide algo al responsable, y un elogio no se guarde como
        comentario).
      - **La 21, paso 1, vez 2** (`el_texto_cubre: [resultado_de_prueba]`, sin la explicación) sigue
        marcando comprensión: con `puede_traer`, un dato estructurado que viene tiene que ser el
        esperado (la regla de la D1); los hechos son los mismos porque un texto cubre siempre la
        explicación. Aflojarlo es cambiar esa regla del comparador.
      - **El corredor no admite dos jugadas válidas para un paso** (sigue de la D7): la 28, paso 3,
        con sólo `aprobar` y su comentario; la 21, paso 5, y la 27, paso 9, con `entregar` y
        `confirmar` juntos.
      - La 27, paso 4, vez 4: "si, eso" guardado como un texto que describe C1 en lugar de
        `acepta_el_ejemplo` (se ve en la vista previa, no se inventa nada).
      - La 28, paso 4: ninguna vez dice que Leda no decide por él.
      - La 21, el cierre "¿Confirmás esa frase?" frente al "¿Va así?" del modelo.
      - En la 21, paso 5, lo que escribió con la foto ("y esta del tablero cerrado. dale mandala")
        entra como una descripción más y le llega a Ismael; antes el `.md` decía que era la
        confirmación.
      - `consultar_pendientes` se redacta como `contar_sus_tareas_pendientes`, y las instrucciones
        de las jugadas dicen "con lo que contó" de un avance: no son de la entrega y no se tocaron.
  - [x] **D7c.** La precisión del usuario a la decisión 22 (2026-10-08, de noche, opción A): una
    aprobación pregunta cuál de las dos sólo si su comentario le pide algo a alguien (`827d13b`).
    Route: delegada (escritor único, 2+ archivos no triviales). Resuelve el `PENDIENTE` de la D7b
    "Impecable ahora pregunta".
    - El dato `el_comentario_pide_algo` (booleano, opcional de `aprobar`, en `ia_real.DATOS` y en
      `hechos.SIGNIFICADOS`, sólo como dato, sin frases): si el comentario le pide a la persona
      responsable o a otra persona que haga o revise algo. La cocina (`aprobacion.aprobar`)
      pregunta si es verdadero o si la IA no lo dijo (el lado seguro); falso aprueba directo. La
      ficha de `aprobar` y el significado de `dos_lecturas` lo dicen. Las huellas de las
      instrucciones no cambiaron (el dato va en el esquema de la jugada, no en el texto).
    - Conversaciones: la 23, paso 2 ("el plc de marcos aprobado, impecable"), vuelve a aprobar
      directo con el dato falso (sin el paso 2b; el aviso a Marcos vuelve a las 10:30), y los
      pasos 1, 8 y 9 lo aceptan en `puede_traer`; la 28, paso 3, lo espera verdadero si viene.
    - Rojo primero: `test_aprobar_con_un_comentario_que_no_pide_nada_va_directo` (`dos_lecturas`
      en lugar de `anotado`) y `test_si_el_comentario_pide_algo_lo_dice_la_ia_como_un_dato`
      (`KeyError`).
    - **Chequeos** (2026-10-08, sobre `827d13b` sin este registro): `pytest tests/motor
      tests/conversaciones`, 888 passed; en seco, `correr --ia guionada --veces 1 --ronda
      seco-d7c`, 29 de 29 bien (informes borrados, `gasto.json` sin tocar).
    - `PENDIENTE`: la IA real sobre la 23 y la 28 (el coordinador); `docs/capacidades.md` (la hoja
      de aprobación) todavía dice que una aprobación con un comentario para el responsable nunca
      cierra directo.
  - [x] **D8.** Lo que dejó la prueba por Telegram del usuario del 2026-10-08 (el guion de la D6,
    `python -m leda.motor.leer corework --completo`), con reglas ya decididas, cada punto como
    mecanismo general, con la prueba en rojo primero y su commit (2026-10-08, de noche). Route:
    delegada (escritor único, 2+ archivos no triviales). Sin la IA real ni Telegram.
    - **1. Los álbumes de una respuesta** (`89da6fb`): el despacho inmediato envolvía el transporte
      sin `enviar_album` y cada álbum fallaba ahí ("'_ConHoraDeEnvio' object has no attribute
      'enviar_album'") y salía una vuelta más tarde. El envoltorio anota la hora de un mensaje o un
      álbum y delega todo lo demás. Rojo: `test_el_album_de_una_respuesta_sale_en_el_despacho_
      inmediato` (el álbum no salía) y la del protocolo del transporte (`AttributeError`).
    - **2. El "…" del borrador a la vista** (`3588141`): el mensaje no siempre reemplazaba al
      borrador, un envío del borrador en vuelo podía llegar después del mensaje, y una respuesta que
      no salió lo dejaba solo. Ahora el cierre, si sigue un mensaje, espera (acotado a su tope) a que
      vuelva el pedido del borrador en vuelo, así ninguno llega después; quien despachó la respuesta
      retira el borrador después, salga o no (como un turno sin mensaje: la semilla silenciosa y su
      borrado, sin otro "escribiendo…"), sólo si se llegó a pedir uno, y una falla deja su
      incidente. El escuchador despacha enseguida la respuesta de un álbum, como el webhook. La Bot
      API, según los comentarios del código: el borrador es una vista previa efímera, sin
      `message_id` propio (por eso el retiro materializa la semilla y la borra). Rojo: cuatro pruebas
      de `test_indicador.py` con el `despachador.py` anterior. La espera del borrador en vuelo es la
      de un pedido ya hecho (decenas o cientos de milisegundos), nunca un retiro antes del mensaje.
    - **3. Los envíos que fallan, nunca en silencio** (`9a6bfbb`): cada intento fallido que se
      reintenta deja un incidente de severidad baja (`entrega_mensaje_reintento`), con la falla
      saneada y la fila de la salida, sin avisar a la administración; el quinto deja el suyo. Rojo:
      `test_cada_intento_fallido_de_una_respuesta_deja_su_rastro`.
    - **4. "Mañana te la recuerdo" un viernes** (`866d7ee`): lo que queda por revisar lleva el día
      hábil siguiente del calendario del espacio (`se_las_recuerda_el`) y el significado ya no dice
      "mañana". Rojo: `test_lo_que_queda_por_revisar_se_recuerda_el_dia_habil_siguiente` (`KeyError`).
    - **5. El ejemplo aceptado, nunca "escribió"** (`0517d06`): migración `0039`
      (`evidence.es_ejemplo_aceptado`, sólo un texto, las filas de antes en `false`, sólo agregar; la
      función de la página lo devuelve; el rollback se niega si una pieza lo es). La cocina lo guarda,
      lo entregado lo relee como `el_ejemplo_que_acepto` ("la aceptó, no la escribió") y la página
      dice "Aceptó esta descripción". El ensayo de rollback y la paridad pasan
      (`tests/garantias/test_migraciones.py`, 16 passed). Rojo: `test_lo_entregado_dice_que_el_
      ejemplo_lo_acepto_y_no_que_lo_escribio` (la columna no existía). La superficie autorizada decía
      `db/migraciones/0039*`; la carpeta real es `db/migrations/`: se usó ésa.
    - **6. Ninguna pregunta abierta para siempre** (`28849d0`): aprobar o pedir cambios (las fichas
      con `decide_la_tarea`) cierra toda pregunta sin cerrar sobre esa tarea, de cualquier persona; un
      botón viejo dice que ya se decidió (`cerrada_con.ya_decidio`). Rojo: las dos variantes de
      `test_al_decidir_una_entrega_no_queda_abierta_ninguna_pregunta_de_su_tarea` con el `fichas.py`
      anterior.
    - **7. La entrega confirmada, con el texto que aprobó el usuario** (`1af2b25`, `02d4d67`): lo
      que un hecho dice que Leda le va a hacer a la persona se dice en primera persona (otra persona
      que se entera sigue en voz pasiva); la hora en que se entera quien aprueba va con su nombre en
      `solo_si_pregunta` (un código de si le llegó queda a la vista); un hecho nuevo,
      `se_le_avisa_si_hace_falta_algo_mas` (lo hace el aviso del pedido de cambios); ⚠️ sólo para lo
      que pide atención, nunca el estado de una tarea que sigue su curso; una sola pregunta en el
      cierre; el significado de `entregada` deja "No está terminada ni aprobada". **La huella de la
      redacción cambió a propósito**: `9e419fe6bbcc420a` → `420146b697b5124b` (`test_contratos.py`,
      con el porqué); la de las jugadas no cambió. Sin frases de ejemplo. Rojo:
      `test_la_entrega_confirmada_dice_lo_que_leda_le_avisa_despues` (`KeyError`) y la de la hora en
      `test_palabras_de_la_redaccion.py`.
    - **8. La lista de lo que hay para revisar** (`119dfba`): empieza por cuántas son, un hecho de la
      cocina (`lista_de_entregas_para_revisar`, `cuantas`); cada entrega de la lista es otro aviso
      (`entrega_en_la_lista`), sin `necesita_respuesta` ni el significado del aviso de una entrega
      sola ("aprobarla o pedirle cambios"); los significados del aviso de una entrega y de su decisión
      dicen que primero se revisa (decisión 18). Rojo: `test_las_entregas_que_salen_juntas_van_en_
      una_lista_con_un_boton_por_tarea`.
    - **9. Las conversaciones** (`74c05c0`): la 21 (el texto de la entrega confirmada, la hora sólo
      si pregunta, el ejemplo aceptado en el aviso a Ismael), la 27 (el ejemplo aceptado en los dos
      avisos), la 23 (`se_las_recuerda_el` y el paso nuevo 12, la entrega otra vez después del pedido
      de cambios) y la 28 (la lista no ofrece decidir). Lo que dice la IA lo lee una persona.
    - **10. Decisión 23, volver a entregar después de un pedido de cambios** (`8a38859`): la IA que
      elige recibe, en la tarea, lo que describió la entrega anterior con lo que pidió el pedido de
      cambios (`la_entrega_anterior`: `lo_que_describio`, `cambios_pedidos`), y juzga lo descrito de
      la nueva junto con eso (`lo_descrito_cubre`, su dato y su significado lo dicen); la cocina hace
      lo de siempre con ese juicio. Rojo: `test_al_entregar_otra_vez_cuenta_lo_que_ya_describio_la_
      entrega_anterior` (`KeyError`). En seco el corredor no lo distingue (la IA guionada ya da el
      juicio): lo mide la IA real.
    - **Chequeos** (2026-10-08, sobre `02d4d67`): `pytest tests/motor tests/conversaciones`, 904
      passed y 1 failed (`test_fichas.py`, la hora del aviso a quien aprueba a la vista: la regla
      nueva del punto 7; corregida en `02d4d67`, 70 passed); `pytest tests/garantias`, 326 passed;
      suite completa, 1657 passed y 2 failed: `tests/test_esqueleto.py::test_reintenta_y_abre_
      incidente` y `tests/test_saludo.py::test_falla_del_saludo_con_envio_fallido_se_reporta_una_
      sola_vez`, que cuentan todos los incidentes del espacio y ahora encuentran también el rastro de
      cada intento fallido (punto 3, a propósito). Esos dos archivos están fuera de la superficie
      autorizada de la D8 y no se tocaron (`PENDIENTE`: contar sólo los de su etapa, sin
      `entrega_mensaje_reintento`). En seco, `correr --ia guionada --veces 1 --ronda seco-d8`, 29 de
      29 bien (informes borrados, `gasto.json` sin tocar).
    - `PENDIENTE`:
      - **La IA real** sobre la 21, la 23, la 27 y la 28, y la prueba por Telegram de los puntos 2 y
        7 (el borrador después del mensaje, el texto de la entrega), por el coordinador y el usuario.
      - **Un envío que falla esperando la respuesta de Telegram** (un tiempo de espera agotado) puede
        haber llegado: la API no tiene una clave para no repetir un envío y el código no tiene cómo
        saberlo, así que el reintento puede duplicarlo. La explicación del incidente lo dice.
      - **El retiro después del mensaje** puede verse como una burbuja vacía que aparece y se borra
        debajo de la respuesta, si Telegram ya había reemplazado el borrador: lo dice la prueba por
        Telegram.
      - **Volver a entregar sólo con fotos** (sin ningún texto): la cocina no tiene dónde guardar lo
        descrito y pide una descripción, aunque la entrega anterior lo dijera.
      - **El paso 19 de la prueba** (volver a preguntar en la entrega nueva lo que ya dijo la
        primera) queda cubierto por la decisión 23; si con la IA real vuelve a pasar, es de diseño.
    - **Cierre del coordinador:** `792392b` saca los incidentes de cada reintento de los conteos de
      `tests/test_esqueleto.py` y `tests/test_saludo.py` (eran de un solo incidente); suite completa
      sobre `792392b`, 1659 passed. **Revisión RDD por tramos, aprobadas y reconocidas:**
      `647c01c..3588141` `review-70be0520f9a6c10f`, `..28849d0` `review-8d5cecf121c0b5e1`,
      `..0517d06` `review-d7da326944900d6c`, `..119dfba` `review-a2fe706ec1d91986`, `..02d4d67`
      `review-9f23c3d91a741a7f`. Advertencias abiertas: el retiro del borrador es en serie
      (`recibir.py:656`), una pregunta cerrada en el mismo turno y un deshacer que no la reabre
      (`fichas.py:368`, `preguntas.py:453`), `herramientas.py:1791` (lo del ejemplo aceptado sin
      validar contra la clase) y la ventana entre pedidos de cambios (`entrega.py:297`).
      `leda_motor` necesita la `0039` antes de la próxima prueba por Telegram.
  - [x] **D5b.** Una pregunta de Leda sin contestar (decisión 21, conversación 30 con su YAML). Route:
    delegada (escritor único, 2+ archivos no triviales). Hecha el 2026-10-09:
    - **La conversación primero** (`56cdd45`): la 30, con los dos órdenes de respuesta en un hilo
      (el miércoles Marcos contesta primero la segunda pregunta; el jueves, primero la que quedó para
      después), la repetición a las 4 horas, el tema siguiente aparte y el día siguiente. En
      `test_corredor` (30). En seco, antes del código: 17 fallas, todas del motor (pasos 3, 5 a 10 y
      12).
    - **La regla** (`9bfc40f`, `leda.motor.pregunta_sin_contestar`; migración `0040` con su rollback:
      `conversation_question.preguntada_en` y `vuelve_aparte`): con otro tema que pide respuesta
      esperando detrás, la escalera repite la pregunta abierta una vez en el día, a las 4 horas
      (`repeticion_del_dia`; `pregunta_sin_contestar_minutos` en `workspace_setting`, 240 por
      omisión, anotado en `docs/product/plataforma-pendientes.md`). Su turno termina 4 horas después
      de la repetición, o al día siguiente: de lo que espera sale aparte uno solo, el más urgente
      (`avisos._un_tema_a_la_vez`, `_urgencia`), y la pregunta queda para después. Las dos quedan
      marcadas: cuando una se cierra, el código trae la otra en su propio mensaje
      (`vuelve_la_pregunta`, `sigue_la_conversacion`: no espera los 30 minutos de la D5, sí el
      horario), y la respuesta del turno no la lleva. La misma pregunta nunca sale dos veces en un
      momento: si la repite su escalera, la repetición del día y la que vuelve quedan omitidas
      (`la_misma_pregunta_sale_en_otro_aviso`).
    - **El aviso de que se va a escalar** (punto 5 de la decisión): el significado de
      `si_no_hay_respuesta` dice ahora que se informa que la tarea está atrasada (o la pregunta sin
      respuesta) y que nadie toma la tarea por eso; el nombre ya iba en `solo_si_pregunta` (decisión
      11). Las instrucciones de la IA no cambiaron (huellas de `test_contratos.py` iguales).
    - **Test primero:** `tests/motor/test_pregunta_sin_contestar.py` con el módulo sólo con la espera
      configurable: 8 de 18 en rojo (las otras 10: la configuración y dos que miran que algo no
      pase). La del significado de lo que pasa sin respuesta se escribió con el cambio, sin rojo
      observado. La 30 se completó con el código: sus pasos 6 y 9 no declaraban el aviso guardado de
      la pregunta que vuelve.
    - **Pruebas que cambiaron:** `test_un_envio_por_dia.py` ordenaba dos preguntas abiertas en el
      mismo momento por el orden físico de las filas, que cambia al marcar `preguntada_en`; ahora la
      abierta va primero, explícito. Por la misma prueba, a igual urgencia gana la pregunta abierta
      (el tema en curso).
    - **Chequeos** (2026-10-09, sobre `9bfc40f`): `pytest tests/motor tests/conversaciones`, 925
      passed; `pytest tests/garantias`, 326 passed (la paridad y el rollback de la `0040`
      incluidos); en seco, `correr --ia guionada --veces 1 --ronda seco-d5b`, 30 de 30 bien
      (informes borrados, `gasto.json` sin tocar). Sin la IA real (decisión del usuario: van en la
      tanda posterior). Sin la suite completa.
    - **Revisión RDD por tramos (coordinador), aprobadas y reconocidas:** `7b34ba4..56cdd45` (la
      conversación 30) `review-0a0e60ef937044db`; `2ac62af..9bfc40f` `review-0b4660c4f081ffd4`, con
      una advertencia: una repetición del día que no salía (omitida o fallida) frenaba los otros
      temas hasta el día siguiente. Corregida en `0c28777` (sin repetición enviada, el turno termina
      a las 8 horas de preguntada; rojo observado, `pytest tests/motor tests/conversaciones` 926
      passed), revisada `16c0a2c..0c28777` `review-168316baac80a7f6`; su advertencia: la prueba
      simula la repetición que no salió sin un aviso omitido real. `635aae7` suma la 30 al README.
    - `PENDIENTE` (decisiones del usuario; lo construido es la lectura que no agrega mensajes):
      - **La repetición a las 4 horas sólo sale si algo espera detrás.** Sin otro tema esperando, la
        pregunta sigue su escalera de siempre (el día hábil siguiente), como en la 03 y la 26. Ejemplo:
        Marcos no contesta a las 10:20 quién destraba el PLC y no tiene nada más pendiente: hoy no
        se le repite a las 14:20, sino mañana a las 10:00. ¿O se repite igual?
      - **"Más urgente"**: el tipo de mensaje (mecánica §11) y, entre iguales, la tarea que vence
        antes; a igual vencimiento, la pregunta abierta. En la 30, el jueves sale primero el pedido
        de comunicaciones (vence el jueves) que la repetición del PLC (vence el viernes).
      - **"Al día siguiente"**: una pregunta de un día anterior ya no frena; a las 10:00 sale lo más
        urgente de lo que espera, de a uno. Lo que no sale espera con su escalera parada (un paso
        guardado sin salir la detiene), así que puede escalar más tarde.
      - **El mensaje aparte** es sólo para las dos preguntas que abrió un aviso de Leda. Cuando la
        persona cambió de tema por su cuenta (9d, la 08, la 12, la 21 y la 27), la pregunta vuelve
        en la misma respuesta, como antes. ¿También aparte?
      - **"Enseguida" fuera del horario**: si la persona contesta a las 17:05, la otra pregunta
        vuelve el día hábil siguiente a las 10:00 (una sola vez, aunque su escalera también la
        repita).
      - **Una pregunta que se hace una sola vez** (`cual_de_las_dos`, decisión 12) o que no es de una
        tarea no se repite; su turno termina a las 8 horas, como si se hubiera repetido.
      - **La IA real** sobre la 30 (y el punto 5 sobre la 04), y la prueba por Telegram, en la tanda
        posterior. `leda_motor` necesita la `0040` además de la `0039`.
- [ ] **C-4.** Regresión con la IA real y prueba por Telegram.
  - Primera ronda (2026-10-08, `resultados/fase-c-c3-regresion.md`, sobre `8b05495`): de la 01 a la 20 y
    la 24, garantías y comprensión 5 de 5; la 21 a la 23 no pasan. Diagnóstico en la bitácora ("La entrega
    y la aprobación con la IA real"): la falla de garantía de la 21 es del comparador (la cocina escribió lo
    confirmado). `PENDIENTE`, decisiones del usuario: quién juzga lo que cubre un texto de la entrega (hoy
    la IA, `el_texto_cubre`, y puede trabarla) y qué pasa después de la única pregunta de "¿cuál de las
    dos?" (hoy se repite, `fichas.dos_lecturas`). Después: arreglar el comparador, aflojar en los YAML lo
    que la ficha permite y repetir la ronda; la prueba por Telegram, con `leda_motor` al día (`0034` a
    `0037` y el pack).
  - Segunda ronda (2026-10-08, de tarde, D6, sobre `eec2b8a`): las 29 conversaciones, 5 veces. Garantías
    5 de 5 salvo la 25, la 27 y la 28; comprensión 5 de 5 en 21 de 29. Las decisiones del usuario 10 a 20
    se cumplen con la IA real; quedan dos de diseño (insistir en mandar algo incompleto y quién juzga lo
    que cubre un texto). `leda_motor` está al día y el guion de la prueba por Telegram, escrito
    (`docs/product/guion-telegram-fase-c-parte-1.md`). Falta: la prueba por Telegram del usuario.
- [ ] **C-5.** La persecución del bloqueo (preguntas 4 a 7, conversación de prueba, ficha y prueba).
- [ ] **C-6.** Las cadencias (pregunta 8).
- [ ] **C-7.** Delegar (pregunta 9 y su enmienda al ADR 0017).
  - Ya decidido como funcionalidad (`docs/ROADMAP.md`): un referente le pasa una tarea a alguien de su
    sector, Leda le pregunta si la acepta y le avisa a quien delegó. Al construirlo cambian las
    respuestas a "me la podés pasar a Nahuel" de las conversaciones 12 y 19, que hoy dicen que no se hace
    por chat y quién lo decide (`quien_decide`; usuario, 2026-10-08: queda así hasta que exista delegar).

## Próximo paso

La D7 y la D7b están hechas; el chequeo de la D7b con la IA real (la 21, la 23, la 27 y la 28) lo
corre el coordinador. La prueba
por Telegram del usuario con el guion de la D6 y las decisiones que dejó la D6 (insistir en
mandar algo incompleto y quién juzga lo que cubre un texto); después, pedir el enlace por chat (la jugada que quedó de la porción 4) y la porción 5 de la C-3: el acceso del administrador
(`docs/STATUS.md`, "Punto exacto para retomar").
