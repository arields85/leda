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
    (`docs/product/plataforma-pendientes.md`, "Acceso y operación").

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
        cualquiera que pueda ver la tarea): queda como el próximo ítem. Cambia la lista de
        jugadas (y su huella en `test_contratos.py`) y lleva su conversación de prueba primero.
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
      - `PENDIENTE`: diez tablas con `workspace_id` sin `row level security` (`acceso_tablero`,
        `activation_token`, `admin_notice`, `conversation_access_log`, `holiday`, `learning`,
        `model_config`, `persona_config`, `work_calendar` y `workspace_version`, leídas del
        catálogo de una base de prueba): ver si son sólo de administración o si les falta,
        contra la invariante de `AGENTS.md`.
      - `PENDIENTE`: el tablero (`_servir_tablero`) arma su página fuera de una guarda, como la
        página de la tarea antes de esto; no se tocó.
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
  - [ ] **D6.** La regresión con la IA real, `leda_motor` al día (autorizado por el usuario de
    antemano, con respaldo) y el guion de la prueba por Telegram (el enlace con `localhost`,
    decisión 20).
- [ ] **C-4.** Regresión con la IA real y prueba por Telegram.
  - Primera ronda (2026-10-08, `resultados/fase-c-c3-regresion.md`, sobre `8b05495`): de la 01 a la 20 y
    la 24, garantías y comprensión 5 de 5; la 21 a la 23 no pasan. Diagnóstico en la bitácora ("La entrega
    y la aprobación con la IA real"): la falla de garantía de la 21 es del comparador (la cocina escribió lo
    confirmado). `PENDIENTE`, decisiones del usuario: quién juzga lo que cubre un texto de la entrega (hoy
    la IA, `el_texto_cubre`, y puede trabarla) y qué pasa después de la única pregunta de "¿cuál de las
    dos?" (hoy se repite, `fichas.dos_lecturas`). Después: arreglar el comparador, aflojar en los YAML lo
    que la ficha permite y repetir la ronda; la prueba por Telegram, con `leda_motor` al día (`0034` a
    `0037` y el pack).
- [ ] **C-5.** La persecución del bloqueo (preguntas 4 a 7, conversación de prueba, ficha y prueba).
- [ ] **C-6.** Las cadencias (pregunta 8).
- [ ] **C-7.** Delegar (pregunta 9 y su enmienda al ADR 0017).
  - Ya decidido como funcionalidad (`docs/ROADMAP.md`): un referente le pasa una tarea a alguien de su
    sector, Leda le pregunta si la acepta y le avisa a quien delegó. Al construirlo cambian las
    respuestas a "me la podés pasar a Nahuel" de las conversaciones 12 y 19, que hoy dicen que no se hace
    por chat y quién lo decide (`quien_decide`; usuario, 2026-10-08: queda así hasta que exista delegar).

## Próximo paso

La regresión con la IA real de todas (con la 21, la 23 y la 24 enteras, y el enlace), pedir el enlace
por chat (la jugada que quedó de la porción 4) y la porción 5 de la C-3: el acceso del administrador
(`docs/STATUS.md`, "Punto exacto para retomar").
