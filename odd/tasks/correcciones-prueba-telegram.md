# Las correcciones de la prueba por Telegram del 2026-10-12

**Rama:** `feat/motor-de-conversacion` · **Abierta:** 2026-10-12, noche · **Copia en Engram:** tema
`odd/correcciones-prueba-telegram/tasks` (proyecto `prisma-pm`)

## Objetivo

Corregir lo que mostró la prueba por Telegram de la Fase C (bitácora de flujos, "Prueba por Telegram real
de la Fase C (2026-10-12)"): las decisiones 77 a 79 y los hallazgos que les siguen en
[`fase-c.md`](fase-c.md).

## Por qué y autorización

La prueba pasó; el usuario marcó cómo habla Leda de lo que hace la cocina. Pidió avanzar de forma
autónoma con esto mientras la plataforma espera su presencia (2026-10-12, noche) y autorizó una ronda con
la IA real, al final, de las conversaciones que toquen estos cambios ("si, autorizo").

## Chequeo de rumbo

- **Qué clase de problema:** la cocina le pasa a la IA hechos que no tiene que contar (a quién y a qué
  hora llega un aviso) o con nombres que la IA repite ("pregunta"). Ya apareció con "previsión"
  (`9b7c6f4`) y se resolvió en la frontera de la redacción, no en las instrucciones. Mismo mecanismo.
- **Mecanismo general, no caso:** sí: los hechos de los avisos a otros, todos a la vez; los nombres de los
  datos, en `hechos.para_redactar`; los íconos, en la forma que da la cocina (decisión 74), por estado.
- **Qué haría innecesaria la próxima ronda:** que la regla viva en los hechos y no en frases.
- **Cocina o mozo:** cocina; la IA no recibe frases ni ejemplos nuevos (regla del mozo).
- **Qué lo demuestra:** las conversaciones tocadas, con la IA real (autorizada), y la próxima prueba del
  usuario por Telegram.
- **Para parar:** si un hallazgo pide cambiar el diseño (las tres salidas de un tema, ADR 0018, decisión
  4), se escribe su conversación de prueba y se deja la propuesta para el usuario, sin código.

## Tareas

Ruta: cada una, un escritor delegado (toca el motor, sus pruebas y las conversaciones); el coordinador
revisa, corre la revisión RDD de cada commit y lleva este documento.

- [x] **T1 · Íconos por estado (decisión 79).** Hoy la IA pone 🗓️ por instrucción
      (`motor/instrucciones.py`); la cocina reconoce los renglones de una tarea (`salida.py`) y cambia el
      ícono según el estado que dicen los hechos del turno: 🏁 terminada, 🟢 en curso y al día, ⚪ sin
      empezar o sin novedades, 🔵 entregada, 🟠 atrasada, 🔴 trabada. El 📋 de una sola tarea no cambia.
- [x] **T2 · "Consultar", no "preguntar" (decisión 78)**, en los nombres que lee la IA
      (`hechos.para_redactar`).
- [x] **T3 · Sin nombre ni hora en los avisos a otros (decisión 77).** Los hechos de un aviso a otra
      persona no le pasan a la IA el destinatario ni la hora; sí que quedó asentado y, si hace falta,
      cuándo vuelve a escribirle a la persona, en palabras de todos los días. El nombre y la hora, sólo si
      la persona los pregunta.
- [x] **T4 · El comentario de una aprobación que contesta "¿cuál de las dos?"** sale del mensaje original
      (llegó «pasale lo de los colores»).
- [x] **T5 · Una tarea terminada no "vence".**
- [x] **T4b · La advertencia de la revisión de la T4** (`aprobacion.py:246-254`): una pregunta de
      "¿cuál de las dos?" vieja que siga abierta no puede pisar el comentario de una aprobación escrita
      después, que no la contesta. Test primero.
- [x] **T4c · `fichas.dos_lecturas` sólo con la pregunta abierta** (límite de la T4b): una "¿cuál de
      las dos?" que quedó para después no se cierra ofreciendo sus botones viejos. Test primero.
- [x] **T6 · La hora de los turnos en el registro** (los pasos 22 a 25 figuran a las 10:02): investigar y,
      si quedó mal guardada, corregirla. **Evidencia (coordinador, 2026-10-12, `leda_motor`):** quedó mal
      guardada. `conversation_turn.at` sale de `reloj.ahora()` (`turno.py:232`). Turnos de Marcos
      (`inbound_message.at` real → `conversation_turn.at`): n.º 6 15:47:05 → mar 10:02:17; n.º 18
      15:54:38 → 10:31:32; n.º 26 16:22:36 → **10:02:18**; n.º 28 16:23:06 → 10:02:42; n.º 34
      16:27:13 → 10:06:50; n.º 37 16:40:03 → mié 10:03:25. A las 16:22 el reloj de Leda estaba cerca
      de las 11:58 del martes (la pregunta a Ariel se programó a las 12:15:15, 30 minutos después del
      último mensaje de Ariel, a las 11:45:15). El adelanto implícito del n.º 26 (17:39:42) es menor que
      el del n.º 18 (18:36:54): el reloj pareció ir para atrás en esos turnos.
      **Diagnóstico (explorador de sólo lectura, 2026-10-12, noche): no hubo hora mal guardada.**
      Cada turno se fechó bien con el reloj de Leda (`turno.py:235`, después de la llamada a la IA:
      restando `latencia_ms`, el adelanto es plano en cada tramo y coincide con los comandos del
      reloj). El reloj fue para atrás de verdad, unas 2 horas, a las 16:20:29 reales: un
      `adelantar` de más (al miércoles), después `volver` (adelanto 0) y otro `adelantar`, que desde
      el lunes real cayó en el martes 10:00 (adelanto 17:39:31, el de los turnos 26, 28, 30 y 34).
      El "hoy a las 12:15" a Ariel salió de eso: la regla de no interrumpir sumó 30 minutos al
      último turno de Ariel (11:45:15), que había quedado en el futuro de Leda
      (`no_interrumpir.py:57-75`). No hay dos relojes desfasados: escuchador, fondo, webhook y web
      refrescan el mismo adelanto. **Arreglo, en la herramienta del reloj y no en Leda:** un piso,
      el último momento ya registrado con la hora de Leda; `adelantar` y `hora` no lo cruzan hacia
      atrás (`HoraAtrasada`) y `volver` se niega si dejaría a Leda antes, salvo `--forzar`.
- [x] **T7 · "Dejalo pendiente, después lo hago"** en medio de una entrega, y "Anoté" dicho de un
      borrador: conversación de prueba; si pide cambiar el diseño, propuesta al usuario.
- [x] **T8 · La entrega nueva que se contradice** ("dejé la foto para cuando vuelvas a entregarla" y
      "¿confirmás la entrega así?"; contó lo que esta vez no se escribió).
- [ ] **T9 · Ronda con la IA real** de las conversaciones tocadas (autorizada), bitácora.
- [ ] **T10 · Cierre:** suites, `docs/STATUS.md`, este documento y las memorias.

## Criterio de aceptación

Cada corrección con su conversación de prueba o su prueba determinista en rojo antes y en verde después;
`correr --ia guionada` en seco, bien; `pytest tests/motor tests/garantias tests/conversaciones` en verde;
cada commit de código revisado por RDD; la ronda con la IA real sin fallas de garantía y sin horas ni
nombres de otros en los mensajes.

## Progreso y evidencia

- 2026-10-12, noche: documento abierto.
- **T1, hecha** (escritor delegado; `11780ef`, más `e599d42` del coordinador: el corrector del formato
  del corredor acepta los íconos como marca de tarea). La cocina cambia la marca de cada renglón de una
  tarea, en una lista de dos o más, por el ícono de su estado, después de que redacta la IA
  (`hechos.con_los_iconos` en `turno`, `avisos._enviar` e `informe_al_grupo._uno`; `salida.iconos_por_estado`);
  las instrucciones de la IA no cambiaron. RED: `tests/motor/test_iconos_por_estado.py` 15 de 15 en rojo.
  `pytest tests/motor` 1346 passed; `tests/conversaciones` 214 passed (más la de `e599d42`, 57 passed en
  `test_comprobar.py`); `test_formato_de_salida.py` 27 passed; en seco 48 de 48. Repaso del coordinador:
  `test_iconos_por_estado.py` 17 passed. **RDD:** `review-fd5b12f57ba236dc`, aprobada. Advertencias sin
  arreglar: el título se busca como parte del renglón y un título contenido en otro podría confundirse
  (`salida.py:546-555`); el paso de los íconos, después de la IA, no tiene una guarda propia
  (`hechos.py:1731-1747`); sugerencia: títulos repetidos (`hechos.py:1750-1757`). A observar en la ronda
  real: que la IA copie los íconos de mensajes anteriores en un mensaje de una sola tarea.
- **T2, hecha** (escritor delegado; `b2f4afa`, más `f599ca8` del coordinador). Lo que lee la IA al
  redactar dice "consulta/consultar" cuando Leda le escribe a alguien para saber algo (doce nombres
  nuevos en la frontera y otros nueve reescritos; unos 80 significados); "pregunta" queda sólo para la
  pregunta de este mensaje y para lo que la persona pregunta. Adentro no cambió ningún nombre. El
  coordinador cambió una palabra de la instrucción de redacción ("un aviso, un recordatorio o una
  consulta") y su huella (`71b74fdaea8a436d`). RED: 4 de 17 en rojo en
  `tests/motor/test_palabras_de_la_redaccion.py`. `pytest tests/motor` 1350 passed;
  `tests/conversaciones` 215 passed; en seco 48 de 48. **RDD:** `review-cdfe60231c85d84d`, aprobada; dos
  sugerencias sobre las pruebas (sólo el primer párrafo; una expresión sensible a mayúsculas).
- **T3, hecha** (escritor delegado; `8d49d42` y `9f5ac67`). En la frontera de la redacción
  (`hechos.para_redactar` → `_sin_nombre_ni_hora`), un aviso a otra persona (un hecho con `llega` o con
  su clave en `hechos.AVISOS`, unas 30) pasa a la IA sin el destinatario ni la hora, que quedan en
  `solo_si_pregunta` (el paso 7 del guion sigue: preguntado, dice a quién y cuándo); lo que Leda le va a
  hacer a la misma persona (`hechos.AVISOS_A_LA_PERSONA`) llega con el día, que la cocina ya dice "hoy",
  "mañana" o "vie 16/10", nunca la hora; los hechos de la cocina no cambian. Una prueba lee el motor y
  falla si aparece un aviso nuevo fuera de la regla. Instrucciones de redacción: lo que se entera otra
  persona "quedó asentado"; huella `1b181215b77350b8`. Además, el arreglo de la advertencia de la T1:
  si falla el paso de los íconos, el texto sale igual y queda un incidente leve
  (`motor_iconos_por_estado`). RED: `test_avisos_sin_nombre_ni_hora.py` 10 de 12 en rojo; dos de
  `test_iconos_por_estado.py`. `pytest tests/motor` 1364 passed; `tests/conversaciones` 215 passed;
  `test_formato_de_salida.py` 27 passed; en seco 48 de 48. Repaso del coordinador:
  `test_avisos_sin_nombre_ni_hora.py` 12 passed. **RDD:** `review-7f672eb05058d717`, aprobada.
  Advertencia sin arreglar: el día sale de recortar el texto de la fecha (`hechos.py:1657`); con una hora
  en UTC entre las 21 y las 24 locales daría el día siguiente (los hechos van en hora local y ningún
  aviso sale a esa hora). Sugerencias: la clave del incidente, su falla sin prueba, la unión de
  `solo_si_pregunta`, un significado vacío. A observar en la ronda real: "el administrador" sigue
  nombrado por la clave (sin la hora) y un aviso que no salió se cuenta sin a quién.
- **T4 y T5, hechas** (escritor delegado; `d9ebbf0` y `64796ac`). T4: una respuesta escrita a "¿cuál de
  las dos?" sólo elige la lectura; el comentario sale del mensaje que abrió la pregunta, guardado con la
  opción (`aprobacion._la_lectura_elegida`), como ya pasaba con el botón; la conversación 23 pide ahora
  el comentario original (`~que revise los colores`). Límite: "aprobala y además decile X" perdería X
  (sin regla). T5: de una tarea `terminada` o `cancelada`, la IA no recibe `vence` ni `fecha_objetivo`, y
  ese día sale de `dias` si ningún otro hecho lo nombra (`hechos._sin_vencimiento_si_cerro`, en
  `para_redactar`); la pregunta al encargado por el detalle lleva ahora el `estado`. RED: 5 de 8
  (T4) y 6 de 9 (T5). `pytest tests/motor` 1377 passed; `tests/conversaciones` 215 passed; en seco 48 de
  48. Repaso del coordinador: `test_terminada_no_vence.py` y `test_aprobacion.py`, 62 passed. **RDD:**
  `review-488b6f52cd3b174d`, aprobada; advertencia: una pregunta vieja abierta puede pisar el comentario
  (T4b, arriba); sugerencia: la forma del estado (`hechos.py:1510-1514`).
- **T4b, hecha** (escritor delegado; `01b3aef`). `_la_pregunta_de_cual` ya no toma cualquier "¿cuál de
  las dos?" abierta sobre la tarea: sólo la pregunta abierta (`preguntas.actual`, un tema a la vez) que
  la persona vio en un mensaje anterior, la misma guarda de lo último que vio que usan las
  confirmaciones escritas (`entrega`, `pase`, `apodos`). Una que quedó para después, tapada por otro
  tema, no pisa lo escrito ahora; `_antes_pregunta_cual` sigue la misma regla. RED:
  `test_una_pregunta_de_cual_de_las_dos_que_quedo_para_despues_no_pisa_lo_escrito_despues` (aprobar y
  pedir cambios), 2 en rojo. `test_aprobacion.py` 55 passed; `pytest tests/motor` 1379 passed;
  `tests/conversaciones` 215 passed; en seco 48 de 48. **RDD:** `review-c2a45f4469c94e9a`, aprobada;
  advertencia: la guarda compara el id como texto con `preguntas_del_turno` (`aprobacion.py:236`),
  igual que las guardas hermanas (la lista está declarada `list[str]`). Límites sin regla: una pregunta
  olvidada que sigue siendo LA abierta (nada pasó en el medio) todavía se toma como contestada; y
  `fichas.dos_lecturas` busca cualquier "¿cuál de las dos?" abierta de la tarea, así que una que quedó
  para después puede cerrarse ofreciendo sus botones viejos (más seguro que antes, pero con el
  comentario viejo en los botones). Va como T4c.
- **T7 y T8, analizadas** (explorador de sólo lectura, 2026-10-12, noche; registro de turnos de
  `leda_motor`). Las tres se arreglan dentro del diseño, en los hechos de la cocina:
  - **T7a** (fue Ariel, paso 21, no Marcos): ante "dejalo pendiente, después lo hago" la IA eligió
    `corregir` sin `saca`, porque la ficha de `cancelar` dice que dejar sin efecto algo dicho antes "es
    corregirlo" (`fichas.py:1921-1930`); pero lo de Ariel nunca quedó anotado, vive sólo en la pregunta
    abierta. Y `entrega.corregir` sin nada que corregir volvió `falta_dato` (`entrega.py:1191`), otra
    pregunta. Por la 9d del ADR 0018, "dice que lo deja" es cancelar sin insistir. Arreglo: la ficha
    describe el trabajo (lo contado para una pregunta que espera confirmación no está anotado; dejarlo
    todo es cancelar) y `corregir` sin nada que corregir lleva lo mostrado y `no_se_anoto_nada`.
    Conversación de prueba nueva: la 51, "Dejar una entrega sin terminar".
  - **T7b:** los hechos de un borrador (`sumo`, `para_entregarla_falta`) no dicen que nada quedó
    anotado, y ✏️ es "algo que quedó anotado" (`instrucciones.py:164`). Arreglo: un hecho
    `todavia_no_quedo_anotado` en lo que espera confirmación o un dato, con su significado. Misma clase
    que las decisiones 77 y 78.
  - **T8:** la IA leyó la foto como `guardar_para_la_entrega` (la misma lectura que la 23, paso 12, 4 de
    5) y la cocina pasó dos hechos que se contradicen: `para_cuando_la_entregue` ("no es parte de una
    entrega todavía") y la oferta con la foto adentro (`_ofrecer_volver_a_entregarla`,
    `entrega.py:997-1039`). "Arranca desde el PLC" no es un resto viejo: lo cubría la entrega anterior
    (decisión 23) y `entrega.py:862` lo pone en el `describe` de la pieza nueva, que la IA cuenta como
    lo escrito ahora. Arreglo: con oferta, el archivo sólo dentro de la oferta; lo que sigue contando de
    la entrega anterior, con su propia clave al redactar (sin quitarlo de lo guardado: la cobertura
    cuenta sólo desde el último pedido de cambios, `_ciclo_desde`). Conversación: la 27 se extiende
    (pedido de cambios y la foto del contador).
  - **Chequeo de rumbo:** la T8 dispara "la misma clase de hallazgo en dos rondas" (`AGENTS.md`, punto
    4). Revisado el mecanismo: el diseño de las decisiones 23 y 68 se sostiene; lo que falla son los
    hechos que la cocina le pasa a la IA (regla del mozo: primero se mira si la cocina le pasó el hecho
    correcto). No se agregan frases ni casos. Si la ronda real vuelve a mostrar la lectura de
    `guardar_para_la_entrega`, se para y se lleva al usuario.
- **T6, hecha** (escritor delegado; `ee9df64`, más `7e13768` del coordinador). Sin hora mal guardada
  (diagnóstico en la tarea): el arreglo es el piso del reloj de prueba. `reloj.ultimo_registrado` es lo
  último que Leda fechó con su reloj (`conversation_turn.at` y `scheduled_notice.creado_en`; afuera
  `programado_para`, que mira al futuro, y `message_outbox.enviado_en`, que `cli.py despachar` fecha con
  el reloj real). `hora` no va antes del piso, `volver` se niega si dejaría a Leda antes salvo
  `--forzar` (sólo para empezar de cero con la base recreada), y `adelantar` cuenta el día siguiente
  desde el más tardío entre el día de Leda y el piso, así que siempre tiene salida (advertencia de la
  revisión). El guion del reloj lo dice. RED: `test_reloj.py` 5 en rojo antes de `ee9df64`; el de
  `7e13768` no se observó en rojo (el escritor de la T4c corría la suite), pero la prueba anterior
  afirmaba la negativa en ese mismo caso. `test_reloj.py` 13 passed; `pytest tests/motor` 1385 passed
  (sobre `ee9df64`); `tests/garantias -k reloj` 2 passed. **RDD:** `review-61e666a8d017cce0` y
  `review-18ef5e4a7c6d0da7`, aprobadas; sugerencias sobre el borde exacto del piso en las pruebas.
  **Ojo con `leda_motor`:** quedó con el reloj en el miércoles 14/10 y lo registrado hasta ahí; `volver`
  ahora se niega (para empezar de cero: recrearla y `volver --forzar`).
- **T4c, hecha** (escritor delegado; `66a1f51`). `preguntas.la_que_vio(ctx, tipo, task_id)` es ahora la
  guarda compartida (la pregunta abierta de ese tipo sobre esa tarea que la persona vio en un mensaje
  anterior): la usan `aprobacion._la_pregunta_de_cual` y `fichas.dos_lecturas`. Se mantiene la decisión
  12 (la pregunta, una sola vez: si contesta mezclando otra vez, quedan los botones, `no_eligio`) sólo
  para la pregunta que la persona está contestando. Una "¿cuál de las dos?" que quedó para después se
  cierra `sin_efecto` con `reemplazada` (el mecanismo de la situación general 7, como `pase`, `entrega`
  y `apodos`) antes de abrir la nueva, con el comentario nuevo en sus opciones; `cerrar_de_tipo` aceptó
  `salvo=` para no cerrar una del mismo mensaje. RED: 2 en rojo (`'no_eligio' == 'dos_lecturas'`).
  `test_aprobacion.py` + `test_fichas.py` 127 passed; `pytest tests/motor` 1388 passed;
  `tests/conversaciones` 215 passed; en seco 48 de 48. **RDD:** `review-9939d87a9136e3cf`, aprobada; dos
  sugerencias (`fichas.py:1994-1998`, `preguntas.py:602-603`). El significado de `reemplazada`
  (`hechos.py:256`) hablaba sólo de la entrega: lo generaliza la T7.
- **T7, hecha** (escritor delegado; `5b52481` la cocina y `0ef7888` la conversación 51, con la lista
  del corredor ampliada por el coordinador). Una sola marca en un solo lugar: `fichas._nombrar_pregunta`
  pone `todavia_no_quedo_anotado` en todo hecho que nombra una pregunta con contenido sin confirmar (la
  confirmación de la entrega, lo que le falta a la entrega y la confirmación de un pase,
  `ESPERAN_PARA_ANOTARLO`), con su significado en `hechos.py`; `sumo` dice que nada queda anotado hasta
  confirmar; `reemplazada` es general (una entrega, un pase o unas opciones); la jugada `corregir` se
  nombra `corregir_algo_que_dijo_antes`. Las fichas de `cancelar` y `corregir` describen el trabajo,
  sin frases: lo que espera confirmación o un dato no está anotado; dejarlo todo es cancelar, cambiar
  una parte es corregir. `entrega.corregir` sin nada que corregir con un borrador abierto vuelve
  `sin_efecto`, `nada_que_corregir`, lo mostrado y `no_se_anoto_nada`, sin abrir otra pregunta (la
  abierta sigue siendo el tema, 9d). La huella de las instrucciones no cambió (`jugadas
  8b25f19b4bfe9b8a`, `redaccion 1b181215b77350b8`: las fichas no entran en ella). La 22 (paso 3) y la 27
  (paso 1) dicen "no dice: que quedó anotado". RED: `test_borrador_no_anotado.py` 5 en rojo; la
  conversación 51 en seco, 2 fallas sin el arreglo. `test_borrador_no_anotado.py` 9 passed; `pytest
  tests/motor` 1397 passed; `tests/conversaciones` + la nueva, 225 passed; en seco 49 de 49. **RDD:**
  `review-e8be884f3aefd3c6` y `review-09e73567d1ac0fa7` (la 51), aprobadas; advertencias: en la 51 la otra
  lectura del paso 2 no repite los "no dice" (`51-...yaml:94-96`); la marca cae en cualquier hecho que nombre esas
  preguntas, también en el retiro de una pieza de una tarea entregada que deja la evidencia incompleta
  (`fichas.py:520-521`); a observar en la ronda real. Límite: sacar todas las piezas con `corregir`
  arma un borrador vacío en vez de cancelar (es la otra lectura del paso 2, junto con `cancelar`).
  **Para la ronda real:** 51, 22, 27, 21, 23, 38 y 07.
- **T8, hecha** (escritor delegado; `bc40805`). En los hechos, sin frases ni casos: (a) con la oferta de
  volver a entregarla, el archivo aparece sólo dentro de `le_ofrece_entregarla_con_esto`; en vez de
  `para_cuando_la_entregue` va `si_no_la_entrega_queda_con_la_tarea` (fiel a la decisión 68); (b) al
  mostrar una entrega nueva (`entrega._con_lo_que_sigue_contando`), los puntos del criterio que ya
  describió la entrega anterior salen del `describe` de lo escrito ahora y van en
  `sigue_contando_de_la_entrega_anterior`; lo guardado no cambia (C1 sigue en `describe_del_criterio`,
  la revisión lo ve cubierto). La huella no cambió. Conversaciones: la 27 suma los pasos 14 a 18 (el
  pedido de cambios, la foto del contador con sus dos lecturas y "dale"); la 23, paso 12, con los dos
  "no dice". RED: `test_entrega.py` 4 en rojo sin el arreglo. `test_entrega.py` 85 passed; `pytest
  tests/motor` 1402 passed; `tests/conversaciones` 217 passed; en seco 49 de 49. **RDD:**
  `review-7136c6a53e78a211`, aprobada; advertencia: si lo escrito ahora repite un punto ya descrito (o
  el pedido de cambios era sobre ese punto), igual sale como "sigue contando de antes"
  (`entrega.py:738-747`). A observar en la ronda: el nombre de la jugada al redactar sigue siendo
  `dejarlo_para_cuando_la_entregue`; el aviso a quien aprueba todavía describe C1 con lo nuevo; una
  pregunta repetida pierde la clave nueva (`preguntas.py`); el `pedido_de_estado` de la escalera que
  llega justo después de un pedido de cambios en una tarea que vence ese día (paso 16 de la 27).
- **T9, en curso** (2026-10-13, madrugada): ronda con la IA real, sol por la suscripción, sobre
  `bc40805`: 51, 27, 23 y 22, 3 veces; 40, 41 y 44, 2 veces (cupo: la ventana de 5 horas en 0 %, la
  semanal en 41 %; 15 corridas grandes gastaron antes el 52 % de una ventana, por eso no 10 × 5).

