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
    `tests/conversaciones/26-no-interrumpir.md`.
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
      - `PENDIENTE` (decisión del usuario): **si cambia quién aprueba** mientras el aviso espera,
        hoy queda omitido con su motivo (`cambio_quien_aprueba`) y el nuevo aprobador no recibe
        nada. ¿Se le guarda uno al nuevo?
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
      - **La 23** recibe ahora, el lunes 26 a las 10:30, el primer recordatorio de las tres
        entregas del viernes mientras Ismael está decidiendo: es la regla, y es también lo que
        pide resolver la 26 (no interrumpir), `PENDIENTE` con el usuario.
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

## Próximo paso

La regresión con la IA real de todas (con la 21, la 23 y la 24 enteras, y el enlace), pedir el enlace
por chat (la jugada que quedó de la porción 4) y la porción 5 de la C-3: el acceso del administrador
(`docs/STATUS.md`, "Punto exacto para retomar").
