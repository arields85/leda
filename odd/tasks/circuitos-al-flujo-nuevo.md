# Circuitos de Leda al flujo nuevo (ADR 0014)

**Prioridad del proyecto** (decisión del usuario, 2026-10-02). Cada circuito
conversacional que Leda ya sabe hacer pasa al flujo nuevo del
[ADR 0014](../../docs/decisions/0014-flujo-de-un-mensaje.md), igual que el alta
conducida: el modelo interpreta y conduce la conversación, y el código garantiza
autoridad, validación, confirmación, ejecución única y auditoría. Después, cada uno
se prueba por Telegram real, con datos ficticios, y las cuentas las opera el usuario.

**Rama:** `feat/flujo-de-un-mensaje`, base `leda_flujo`.

**Nombres (2026-10-02):** los circuitos se llaman por número (circuito 0, circuito 1…) y sus tareas 0-1, 0-2…; hasta el 2026-10-02 se llamaban C0, C1… y C0-1, C0-2…, nombres que ahora se usan para las versiones del flujo C (glosario en `AGENTS.md`, "Nombres que usamos").

## Regla para cada circuito

Un circuito se tilda sólo cuando se cumplen sus cuatro pasos:

1. **Diseño:** acordado con el usuario y escrito en este documento, con su chequeo de
   rumbo ("Cómo pensamos juntos", punto 3, en `AGENTS.md`). Desde ahí queda "decidido,
   listo para hacer". **Todo diseño se piensa para la fluidez** (decisión del usuario,
   2026-10-02): ¿es mecánico? ¿se puede hacer más fluido y conversacional? La persona
   escribe como habla y Leda pregunta sólo lo que falta; botones sólo para elegir
   (enmienda del ADR 0013 del 2026-10-02). La fluidez nunca saltea una garantía.
2. **Construcción:** con el flujo C, con pruebas primero y revisión RDD. **Flujos
   congelados** (decisión del usuario, 2026-10-02; `AGENTS.md`, "Nombres que usamos"):
   antes de empezar hay una etiqueta de Git con la copia intacta de los flujos
   anteriores; se trabaja sólo en el flujo C y los anteriores no se corrigen ni se
   adaptan. Si un cambio los rompe, se retiran su código y sus pruebas (la versión buena
   está en la etiqueta). Sin interruptores nuevos por circuito.
3. **Retiro de lo viejo:** "un camino pasa al flujo nuevo sólo cuando se retiró lo
   viejo" (`AGENTS.md`, punto 7); lo retirado queda en la etiqueta.
4. **Prueba real:** por Telegram, con un guion numerado. Se leen la conversación, la base,
   la auditoría y los incidentes. Pasa con los criterios de adopción del ADR 0014: al
   menos nueve de cada diez turnos del modelo aceptados al primer intento, ningún
   mensaje sin próximo paso, ninguna clase de falla repetida y ningún incidente nuevo.

## Checklist

Estado actual de cada uno: *por diseñar*, salvo el alta, que ya está construida.

- [ ] **Circuito 0. Alta de tarea: variantes que faltan probar.** El alta conducida está
      construida y su camino principal pasó la prueba real (2026-10-02, 11:07; quien
      confirma es otra persona). Faltan, en real: quien pide confirma su propia tarea;
      pedir una tarea para otra persona; Modificar un dato del resumen; Cancelar; y el
      aprobador rechaza con motivo. Falta también retirar el alta guiada vieja (M4-M9).
- [ ] **Circuito 1. Entrega con evidencia.** El responsable avisa que terminó y entrega evidencia
      (explicación, foto, archivo, resultado de prueba). La tarea pasa a `en_revision` y
      se avisa al aprobador. Mecánica §3 y §6; ADR 0009.
- [ ] **Circuito 2. Aprobación de la entrega.** El aprobador aprueba (la tarea queda
      `terminada`) o pide cambios con un motivo que el responsable ve. Mecánica §5 y §7;
      ADR 0008.
- [ ] **Circuito 3. Estados y bloqueos.** "Ya empecé" (`en_curso`), declarar un bloqueo con su
      causa, resolverlo, y que la tarea vuelva a su estado anterior. Mecánica §3 y §8.
- [ ] **Circuito 4. Consultas y menú de tarea.** "¿Qué tengo pendiente?", la lista con un botón
      por tarea, "Ver más" y el menú de cada tarea según quién la mira. ADR 0007.
- [ ] **Circuito 5. Dependencias.** "Esta no puede arrancar hasta que termine aquella", y el
      aviso en cadena cuando la primera se atrasa. Mecánica §4.
- [ ] **Circuito 6. Aclaración de referencias.** Una referencia ambigua a una tarea, una persona
      o un objetivo, y Leda pregunta cuál, con botones. Etapa 3 del ADR 0014 (Jev);
      ADR 0006.
- [ ] **Circuito 7. Cambio de tema con una pregunta abierta.** Escribir otra cosa a mitad de
      algo: "¿Seguimos con eso?", seguir o dejarlo. ADR 0013, regla 1.
- [ ] **Circuito 8. Seguimiento automático.** Recordatorios por vencimiento, pedido de estado y
      resumen del equipo, y cómo Leda conversa la respuesta de la persona. Para probarlo
      en real hay que forzar fechas y cadencias por consola (`leda escalera`,
      `leda correr`). Mecánica §9 a §11.
      **Cómo tiene que comportarse** (decisión del usuario, 2026-10-02, tomada de su
      contexto de Prisma en Hermes): los atrasos y bloqueos se tratan primero en privado;
      la exposición en el grupo sólo si el problema persiste, afecta al equipo o no hay
      otra alternativa, y siempre factual y respetuosa. Ante falta de respuesta: primer
      recordatorio privado, cordial y breve; segundo, privado, con el impacto o la
      dependencia; tercero, privado, avisando el escalamiento; después, escalamiento según
      el área y la relevancia (rutas del pack). Leda ya tiene la escalera anclada al
      vencimiento (mecánica §9, `escalera.py`); faltan: (a) seguir la **falta de
      respuesta**, que hoy no se sigue (`pending_reply` no es operativo, riesgo 4 de
      `docs/STATUS.md`); (b) que los textos de los recordatorios salgan con la voz y el tono
      del cliente, no escritos fijos en `escalera.py` con voseo.
- [ ] **Circuito 10. Presentación visual de las respuestas.** Decidido (usuario, 2026-10-02, tomado
      de su contexto de Prisma en Hermes). Se aplica en el **código** que arma los
      resultados estructurados (resumen del borrador, listas, menú de tarea, avisos), no en
      el modelo, cuyo texto sigue plano (voz):
      - varios datos, en pocos bloques breves con títulos cortos o etiquetas claras; una
        idea por línea y espacio entre temas;
      - listas sólo cuando ayudan a comparar, elegir o seguir una secuencia;
      - negrita sólo en etiquetas, estados, cantidades o próximos pasos, nunca en oraciones
        enteras;
      - no repetir siempre la misma estructura cuando otra es igual de clara;
      - en resultados de gestión, un único marcador semántico en el título según el foco
        que la persona pidió (📊 resumen, 🎯 objetivo, 📋 tarea, ⚠️ bloqueo, 📎 evidencia,
        👤 integrante, 📌 estado) y `►` antes de cada encabezado de sección; nunca en
        respuestas simples, aclaraciones o mensajes de una o dos frases;
      - sin resultados: una sola frase clara, sin título, secciones, marcador ni emoji;
      - fuera de esos casos, sin emojis de decoración (los marcadores son semánticos y no
        dependen del ajuste `emojis` del cliente);
      - la presentación no alarga la respuesta, no agrega lo que no se pidió ni pierde
        precisión.
      **Requisito técnico:** hoy Leda manda todo a Telegram como texto plano (no usa
      `parse_mode`), así que la negrita no es posible; hay que activar el formato de
      Telegram en el despachador escapando lo que escriben las personas.
- [ ] **Circuito 9. Cambios sobre una tarea creada.** Cambiar el responsable, la fecha o el
      criterio de una tarea ya comprometida, con vista previa, confirmación y la
      re-aprobación cuando el cambio cruza el umbral (cambio de responsable, corrimiento
      de fecha, cambio de criterio). Hoy no existe: no hay herramienta para hacerlo.
      Constitución §7 (cambios de asignación y de fecha con confirmación humana);
      mecánica §7 (umbral de re-aprobación). Agregado el 2026-10-02 por la ronda 0-C
      (hallazgo H5): no es funcionalidad nueva, es comportamiento obligatorio del núcleo.

## circuito 0: chequeo de rumbo y rondas (2026-10-02)

1. Clase de problema: comprobar que el alta conducida cubre todas sus ramas reales, no
   sólo el camino que ya pasó. Ya apareció: los peores hallazgos de la primera corrida
   salieron de ramas poco recorridas (pausa, convivencia con el alta guiada).
2. Mecanismo general: una ronda por rama, leyendo la conversación, la base, la auditoría y
   los incidentes. Los hallazgos se clasifican por regla del ADR 0013 o por etapa del
   ADR 0014, nunca con un parche de caso.
3. Qué haría innecesaria la próxima ronda: las cinco variantes en verde y sin incidentes,
   para poder retirar el alta guiada (M4-M9) con evidencia.
4. Hipótesis vigente: el alta conducida ya es estable en su camino principal (pasó el
   2026-10-02 a las 11:07). Si una variante falla por diseño del contrato, se revisa el
   contrato, no la variante.

Quién confirma: el aprobador del **responsable** de la tarea (`_find_confirmer`). Por eso,
si Ismael pide una tarea para Marcos, la confirma él mismo (es el aprobador de Marcos).

- **Ronda 0-A:** Ismael pide una tarea para Marcos, toca Modificar y cambia un dato, y
  confirma él mismo. Cubre "quien pide confirma", "para otra persona" y Modificar.
- **Ronda 0-B:** Marcos pide una tarea y la cancela desde el resumen. Cubre Cancelar.
- **Ronda 0-C:** Marcos pide una tarea y la envía a aprobación; Ismael la rechaza y
  escribe el motivo. Cubre el rechazo con motivo.

### Ronda 0-A (2026-10-02, 12:35-12:41): hallazgos y decisión

Ismael pidió una tarea para Marcos ("revisar el cableado del tablero de la línea 2"). Los
cinco turnos del modelo fueron aceptados al primer intento y no hubo incidentes. El modelo
entendió todo, incluido "el objetivo" escrito a mano; **las tres fallas están en el código
que rodea al modelo** ("Cómo pensamos juntos", punto 8). La tarea no se creó: a las
12:45:38 Ismael escribió "nada, cancela" y la solicitud quedó `cancelled` en el mismo
segundo, con "Listo, cancelo la tarea y no queda nada guardado. Si más adelante querés
armarla de nuevo, la empezamos cuando digas." Cancelar por texto funciona; 0-B prueba el
botón.

- **H1. Objetivos del área de quien pide, no de la tarea.** `_objetivos_del_area`
  (`ingreso_tareas.py:2189`) filtra por `who.area_id`, el área de quien escribe. Ismael es
  de Dirección, que no tiene objetivos propios, así que cae en los objetivos sin área: el
  estratégico. Con una sola opción, la regla "un dato con una sola opción no se pregunta"
  (`ingreso_tareas.py:2118`) lo completa sin preguntar. El resumen era incoherente: "Área:
  OT y automatización" (sale del responsable) con el objetivo estratégico (sale de quien
  pide). Es la misma clase que el pendiente (e) de la primera prueba: segunda aparición,
  disparador del punto 4. Se corrige el mecanismo.
- **H2. Modificar sin botones y sin el objetivo.** Al tocar Modificar, Leda contestó en
  texto "puede ser el título, el responsable, la fecha o el criterio": sin botones y sin
  el objetivo, que sí se podía cambiar. La lista la escribió el modelo, no salió de los
  datos. ADR 0013, regla 3 (sólo opciones posibles) y "botones donde hay opciones".
- **H3. Latencia.** El toque de Modificar tardó 48 s en tener respuesta (turno de 40 s),
  "el objetivo" 27 s, y el primer mensaje 54 s, con el turno arrancando 33 s después de
  que llegó el mensaje. Se registra; la latencia va después de la fluidez (decisión del
  2026-10-01).

**Decisión del usuario (2026-10-02): decidido, listo para hacer.**

- [x] **0-1.** Los objetivos que ofrece el alta salen del **área de la tarea**, que es la
      del responsable, igual que el área y el aprobador. Ismael pidiendo para Marcos ve
      los objetivos de OT.
- [x] **0-2.** Una tarea cuelga sólo de un **objetivo operativo**, nunca del estratégico
      (mecánica §1: la tarea va bajo el objetivo operativo). Si el área de la tarea no
      tiene ningún objetivo operativo activo, Leda lo dice con el estado real y no
      completa con otro (constitución §4). Se retira la caída a los objetivos sin área.

**Hecho 0-1 y 0-2** (commit `616f863`, ruta delegada: un escritor).

- Mecanismo único: `_areas_de_la_tarea` y `_objetivos_de_la_tarea`
  (`ingreso_tareas.py`) reemplazan el filtro por `who.area_id`. Todo lo que busca
  objetivos pasa por `_entity_candidates`: el autocompletado de la opción única, la
  página de botones, "Otra opción", el selector de Modificar, el orden de Jev y las
  opciones que recibe el modelo. Filtro: `tipo = 'operativo'` y el área de la tarea;
  el estratégico y los objetivos sin área no se ofrecen nunca.
- Orden de los datos: sigue el de la decisión del 2026-09-30 (primero qué hay que
  hacer, después el objetivo), así que el objetivo se puede pedir antes que el
  responsable. Mientras no hay responsable, la tarea puede ser del área de cualquiera de
  las personas que pueden serlo (quien escribe y quienes aprueba, las mismas que ofrece
  el dato del responsable), y se ofrecen los operativos de esas áreas. Con el
  responsable elegido, sólo los de su área. Se descartó pedir el responsable primero:
  rompía esa decisión para quien aprueba gente de varias áreas. Si alguien puede asignar
  sólo en su área, todo sigue igual que antes.
- Si el responsable cambia a otra área, el objetivo ya elegido se saca y se dice
  ("Saqué el objetivo «…» del borrador: es de otra área…") y se vuelve a preguntar con
  los botones del área nueva (`alta_conducida._completar`; en el alta guiada,
  `_finalize`).
- Sin ningún operativo en el área de la tarea, Leda dice el estado real con el área y
  ofrece Cancelar borrador; si alguien de otra área con objetivos puede ser responsable,
  lo dice ("decime quién"). La conversación sigue abierta: el aviso se da una vez por
  área (marca `sin_objetivo_avisado` en `terminal_result`) y después el modelo atiende
  lo que se escriba (cambiar el responsable, cancelar, dejarla guardada). Si el modelo
  pide el objetivo igual, la respuesta vuelve a ser el estado real.
- La fixture `intake_world` (`tests/conftest.py`) da área a sus tres objetivos
  operativos: sin área ya no se ofrecen. El banco también: el objetivo simulado de una
  tarea sembrada (`tests/banco/corrida.py`) es operativo de su área, y las pruebas de
  `tests/banco/test_corrida.py` que suponían la regla vieja (Ismael elige entre el
  estratégico y los sin área) eligen al responsable y al objetivo por su nombre, no por
  su lugar en la lista.
- Pendiente conocido: `herramientas.crear_borrador_tarea` (camino general viejo) recibe un
  `objetivo_id` sin este filtro. Se retira con el alta guiada (M4-M9); no se tocó.
- RED (2026-10-02): `tests/test_alta_objetivo_del_area_de_la_tarea.py`, 8 de 8 en rojo.
  La falla del caso real: pedida para Sam Noble (quality), los botones eran
  `['Expand regional coverage 1', 'Vincular todo']`, el objetivo sin área y el
  estratégico. GREEN: 8 de 8 en verde. Suite completa (2026-10-02, `python -m pytest
  -q -p no:cacheprovider`): `1 failed, 3438 passed, 333 deselected, 1 warning in
  879.63s`; la única falla es la previa de abajo.
- Falla previa, para arreglar aparte:
  `tests/test_alta_conducida.py::test_un_texto_con_un_dato_inventado_se_reintenta_con_el_motivo`
  depende de la fecha de hoy ("15/03" ahora se rechaza como `fecha_distinta`, no como
  `numero_inventado`). Falla igual sin este cambio. La prueba no tiene que depender del
  día en que corre.
- [x] **0-3.** Modificar muestra **un botón por dato modificable**, armado por el código
      desde el resumen vigente (objetivo incluido), no una lista escrita por el modelo.

**Hecho 0-3** (commit `e138635`, ruta delegada: un escritor).

- Causa: `modify_from_preview` (`ingreso_tareas.py`) mandaba el toque de Modificar del
  alta conducida a `alta_conducida.modificar`, un turno del modelo con
  `{"toque": "modificar"}`: la lista de datos la escribía el modelo.
- Mecanismo: un solo selector para las dos altas. El toque abre `open_modify_picker`
  (`MODIFY_PICKER_KIND`, con "Volver al resumen") sin llamar al modelo. En el alta
  conducida, los botones salen de `alta_conducida.campos_modificables`: los datos que
  llena el alta, en el orden del resumen, sin la descripción vacía (el resumen no la
  muestra) ni un dato con una sola opción; el área y la evidencia salen del
  responsable. Elegir un dato pasa por `alta_conducida.pedir_dato`: objetivo y
  responsable, con los botones del turno (`_opciones_de_ahora`, la misma búsqueda de
  `_entity_candidates`; el toque lo guarda `conducir_toque`); título, fecha y criterio,
  por escrito con lo que tenía para copiar, y la respuesta la atiende el turno del
  modelo. Después vuelve el resumen con sus botones. Escribir el cambio en vez de tocar
  sigue yendo al modelo. Se retiró `alta_conducida.modificar`.
- RED (2026-10-02): `tests/test_alta_conducida_modificar_botones.py`, 6 de 7 en rojo
  (el toque de Modificar llamaba al modelo con `{"toque": "modificar"}` y no dejaba
  botones). GREEN: 7 de 7. Las dos pruebas de `tests/test_alta_conducida.py` que
  escriben el cambio con el selector abierto ya no guionan un turno para el toque; la
  que esperaba que Modificar fuera al modelo se retiró.
- Suite completa (2026-10-02, `python -m pytest -q -p no:cacheprovider`): `1 failed,
  3444 passed, 333 deselected, 1 warning in 963.07s`; la única falla es la previa que
  depende de la fecha (`test_un_texto_con_un_dato_inventado_se_reintenta_con_el_motivo`).
- [x] **0-4.** Repetir la ronda 0-A en real después de 0-1 a 0-3. Pasa el
      2026-10-02 a las 14:58-15:02: ver "Ronda 0-4".

Comprobaciones: RED primero con un alta pedida por alguien de otra área (Dirección para OT)
que hoy ofrece el estratégico; prueba de que Modificar arma sus botones desde el resumen;
suite completa de la rama.

### Rondas 0-B y 0-C (2026-10-02, 12:46-12:53): resultado y hallazgos

- **0-B, Cancelar con el botón: pasa.** Marcos tocó Cancelar en el resumen (12:48:16) y
  a las 12:48:17 Leda contestó "Listo, cancelé el borrador de la tarea."
- **0-C se desvió y quedó sin probar el rechazo con motivo.** Marcos eligió a Nahuel como
  responsable; como Marcos es el aprobador de Nahuel, tuvo Confirmar y la tarea se creó
  (12:50:25, "Calibrar los sensores de temperatura de la línea 1", a cargo de Nahuel).
  Bien: "Nahuel Gimenez todavía no activó su chat con Leda, así que no le pude avisar"
  (auditoría `omitir_aviso_asignacion_ingreso_tarea`). Hay que repetir 0-C.
- Los 14 turnos del alta de las tres rondas, aceptados al primer intento; sin incidentes.

- **H4. Botón viejo, callejón sin salida.** El resumen ya confirmado siguió mostrando sus
  botones. Marcos tocó Modificar (12:50:48) y Leda contestó "Ese pedido ya no está
  vigente. Si sigue haciendo falta, escribime y lo vemos de nuevo.": no dice el estado
  real (la tarea ya existe) ni qué se puede hacer. Misma clase que C-3 de `main`: segunda
  aparición, se corrige el mecanismo.
- **H5 (grave). Leda inventó un cambio.** "quiero modificar la tarea, la hago yo, no
  nahuel" (12:51:06) fue por el camino general, todavía con el método viejo, y tardó
  87 s. Leda contestó "Anoté el cambio: la tarea pasa a tu nombre… Con Confirmar el cambio
  queda aplicado… va con la confirmación de Ismael Soschinski", pero no se preparó ningún
  cambio: la auditoría muestra sólo `herramienta:consultar_tareas`, no hubo vista previa
  (`pending_action`) y los botones eran los de la lista de tareas, sin Confirmar. No
  existe herramienta para cambiar el responsable. La tarea sigue a cargo de Nahuel.
  Constitución §4 (nunca inventa) y ADR 0013, regla 3 (estado real). Tercera aparición de
  la clase "el modelo promete lo que no existe" ((a) y (f) de `docs/STATUS.md`): el
  mecanismo es que en el camino general el texto lo escribe el modelo y no sale de los
  hechos. Lo corrige pasar ese camino al flujo nuevo (circuito 3, circuito 4, circuito 9), no un parche.
- **H6. El menú de la tarea no ofrece cambios.** Marcos, aprobador de Nahuel y quien la
  creó, ve sólo "Ver detalle". Consecuencia de que no exista la capacidad (circuito 9).

**Decisión del usuario (2026-10-02): decidido, listo para hacer.**

- [x] **0-5.** Un toque sobre un botón que ya no está vigente contesta con el **estado
      real** de lo que ese botón tocaba (por ejemplo, "la tarea ya quedó creada") y
      ofrece lo que se puede hacer ahora con eso, nunca un mensaje sin próximo paso
      (constitución §8). Vale para todo botón vencido, no sólo para el resumen del alta;
      corrige también C-3 de `main`.

**Hecho 0-5** (commit `6b09cd4`, ruta delegada: un escritor).

- Mecanismo único: `gateway._contestar_boton_vencido`. Todos los caminos que contestaban
  "Ese pedido ya no está vigente…" pasan por ahí: los toques del alta (guiada y
  conducida), Modificar, Rechazar y Enviar a aprobación vencidos, `resuelta is None` de
  `pendientes.resolver`, la repetición tardía de Confirmar o Cancelar de un borrador
  (`_resolver_toque_borrador`) y los dos casos viejos de la pregunta sobre la rama. El
  estado sale de lo que el botón tocaba, leído desde su token (`_sujeto_del_boton`):
  - borrador convertido: "la tarea ya quedó creada" y el menú de la tarea
    (`_encolar_menu_tarea`, sólo lo que esa persona puede hacer según el estado). La
    tarea se encuentra por `task.source_draft_id`;
  - acción sobre una tarea (`args.tarea_id`: aviso de coordinación, menú, vista previa
    de un cambio): qué pasó con el botón ("ese cambio ya se aplicó", "esa pregunta
    venció") y "Así está la tarea ahora:" con su menú. Es C-3 de `main` (Aprobar en un
    aviso viejo de una tarea terminada);
  - borrador cancelado (también rechazado): que se canceló y la tarea no se creó, y que
    se puede volver a armar contándolo;
  - borrador enviado a aprobación, a quien lo pidió: quién lo tiene que confirmar y que
    se le avisa;
  - borrador abierto o cualquier otra pregunta o vista previa: su estado y la pregunta
    abierta de esa persona otra vez, con sus botones (`_reofrecer_lo_abierto`, el mismo
    repreguntar de un adjunto o un "no puedo"); sin pregunta abierta, un paso general;
  - botón de otra persona, o uno que ya no se puede leer: se dice así, con un paso
    general.
- RED (2026-10-02): `tests/test_botones_vencidos_estado_real.py`, 5 de 5 en rojo, todas
  con el texto del callejón sin salida. GREEN: 6 de 6 (se sumó el caso en chat privado
  que vuelve a hacer la pregunta abierta). Las 49 aserciones viejas que esperaban el
  texto anterior (alta, toques, ramas, borradores, alta guiada) ahora comprueban el
  estado real.
- C-3 de `main` queda corregido en esta rama; llega a `main` recién cuando se integre.
- [x] **0-6.** Cuando una vista previa o una elección se resuelve (confirmada, cancelada,
      enviada o vencida), sus botones se quitan del mensaje en Telegram, para que no se
      ofrezca lo que ya no se puede hacer (ADR 0013, regla 3).

**Hecho 0-6** (commit `50dc2f5`, ruta delegada: un escritor).

- Mecanismo: `despachador._quitar_botones_resueltos`, al final de cada pasada de
  `despachar`, bajo el mismo espacio y el mismo candado. Busca los mensajes ya entregados
  (con `telegram_message_id`) cuya acción pendiente ya no espera o venció, o cuya
  elección del alta ya no está activa, y les quita los botones con
  `editMessageReplyMarkup` (`Transporte.quitar_botones`; el texto no cambia). La marca
  `message_outbox.botones_quitados_en` lo hace una sola vez: queda puesta si se
  quitaron, si Telegram dice "message is not modified" o "message to edit not found"
  (nada que quitar) y también ante cualquier otra falla, que deja un incidente
  `quitar_botones` con la referencia al mensaje (nunca un silencio; reintentar sin fin
  sólo repetiría el incidente). Un toque que llegue antes o a pesar de esto lo contesta
  0-5.
- Migración `0028_quitar_botones.sql` (con su rollback): la columna, un índice parcial
  y su comentario, igual que en `db/esquema.sql`. No toca privilegios, dueño ni la RLS
  forzada de `message_outbox`. Lo ya entregado cuya acción ya no valía al aplicarla
  queda marcado sin tocar Telegram (historia anterior; un toque lo contesta 0-5). El
  ensayo de migración y rollback de la suite y la paridad entre instalación limpia y
  base migrada pasan.
- PENDIENTE (orquestador): aplicar `0028` a `leda_flujo` con el listener detenido, como
  la `0027`, con el mismo rol: en PowerShell, `$env:PGCLIENTENCODING = "UTF8"` y
  `psql -v ON_ERROR_STOP=1 -d leda_flujo -f db/migrations/0028_quitar_botones.sql`
  (ver `db/migrations/README.md`); después reiniciar el listener.
- RED (2026-10-02): `tests/test_despacho_quita_botones.py`, 7 de 7 en rojo (no existían
  la columna ni `quitar_botones`). GREEN: 7 de 7: pregunta resuelta y vencida, elección
  del alta usada, idempotencia, una que sigue esperando no se toca, otro espacio no se
  toca, "no hay nada que quitar" sin incidente, otra falla con un incidente y sin
  reintento.
- Suite completa con 0-5 y 0-6 (2026-10-02, `python -m pytest -q -p no:cacheprovider`):
  `1 failed, 3457 passed, 333 deselected, 1 warning in 1008.24s`; la única falla es la
  previa que depende de la fecha
  (`test_un_texto_con_un_dato_inventado_se_reintenta_con_el_motivo`).
- [x] **0-7.** Repetir la ronda 0-C (rechazo con motivo) con Marcos como responsable.
      Hecho el 2026-10-02, 13:06-13:10: ver abajo.

### Ronda 0-C repetida (2026-10-02, 13:06-13:10): pasa

Marcos pidió "calibrar los sensores de presión de la línea 1", eligió el objetivo y "Para
mí", escribió el criterio y tocó Enviar a aprobación (13:09:33). A Ismael le llegó el
borrador con Confirmar y Rechazar; tocó Rechazar, Leda le preguntó el motivo y él escribió
"primero hay que comprar los patrones de calibración, todavía no los tenemos". A las
13:10:21 Marcos recibió el rechazo con ese motivo textual, e Ismael la confirmación de que
se le avisó. En la base, el borrador y la solicitud quedaron `cancelled` y no se creó
ninguna tarea; la auditoría tiene `enviar_ingreso_tarea_a_aprobacion` y
`rechazar_ingreso_tarea` con el motivo. Cuatro turnos del modelo, aceptados al primer
intento; sin incidentes.

- **H7 (menor). El aviso de rechazo no deja un próximo paso a quien pidió.** Marcos
  recibe el rechazo con el motivo y nada más. Constitución §8: ningún mensaje deja a la
  persona sin un próximo paso; sin uno, el tema queda abierto en el aire.

**Decisión del usuario (2026-10-02): decidido, listo para hacer.**

- [ ] **0-8.** El aviso de rechazo a quien pidió cierra con dos botones: **"Volver a
      armarla"** reabre el borrador con los mismos datos, para corregir lo que hizo falta
      y volver a enviarlo (con su resumen, Modificar y Enviar a aprobación); **"Dejarla
      así"** cierra el tema sin efectos. Toque idempotente y con estado real si el
      borrador ya no se puede reabrir (0-5).

**Estado de circuito 0 al 2026-10-02:** las cinco variantes ya se probaron en real (confirma quien
pide, para otra persona, Modificar, Cancelar por texto y por botón, rechazo con motivo).
0-1, 0-2, 0-3, 0-5 y 0-6 ya están construidos. Falta construir 0-8, retirar el alta guiada (M4-M9) y repetir
la ronda 0-A (0-4).

### RDD de 0-1 y 0-2 (2026-10-02)

`616f863` y `cb3befb`, desde `bda7e5b`: riesgo medio, revisión debida por presupuesto
(`slice_budget_reached`), consentimiento permanente del usuario. Linaje
`review-f5b5e084057d2e82`, una lente (confiabilidad): **aprobada y reconocida**. Frontera
de revisión de la rama: `cb3befb`. Cinco observaciones no bloqueantes, para después:
R3-001 (`alta_conducida.py:747-754`, advertencia), R3-002
(`tests/test_alta_objetivo_del_area_de_la_tarea.py:152-157`, advertencia), R3-003
(`ingreso_tareas.py:2208-2214`, advertencia), R3-004 (`ingreso_tareas.py:2269-2280`,
sugerencia) y R3-005 (`ingreso_tareas.py:2770-2778`, sugerencia). La revisión entregó sólo
la ubicación y la severidad: se miran al retomar circuito 0.

### Ronda 0-4 (2026-10-02, 14:58-15:02): pasa

Con `e138635` (0-1 a 0-3) y el listener reiniciado. Ismael pidió "necesito que Marcos
revise el cableado del tablero de la línea 2 para el martes que viene":

- Objetivo con **dos botones de OT** ("Planos eléctricos correctos…" y "Conectar y
  automatizar equipos…"); el estratégico no apareció. H1 corregido.
- Modificar (15:00:11) contestó en 1 s, sin el modelo, con **un botón por dato** (Título,
  Objetivo, Responsable, Fecha objetivo, Criterio de aceptación) y "Volver al resumen".
  Objetivo ofreció los dos de OT; el cambio volvió al resumen con el objetivo nuevo.
  Fecha objetivo mostró el valor para copiar; "el jueves que viene" quedó 08/10/2026. H2
  corregido.
- Confirmar (15:02:20): la tarea quedó `asignada`, para el 08/10, bajo "Conectar y
  automatizar equipos…" (`operativo`), a cargo de Marcos; a Marcos le llegó el aviso de
  asignación con la fecha y el criterio. Auditoría: dos `modificar_ingreso_tarea`,
  `avisar_asignacion_ingreso_tarea` y `confirmar_borrador_tarea`.
- Cinco turnos del modelo, aceptados al primer intento (4,5 a 11,5 s); sin incidentes.

- **H8 (observación). La misma frase, dos fechas distintas.** "el martes que viene",
  escrita un viernes (2026-10-02), quedó 13/10 a las 12:36 y 06/10 a las 14:58. Leda
  muestra la fecha con el día en el mensaje y en el resumen, así que la persona puede
  corregirla, pero la interpretación del modelo no es estable. Etapa 2 del ADR 0014 (el
  modelo normaliza valores). No se corrige con reglas de frases.

**Decisión del usuario (2026-10-02): decidido, listo para hacer.**

- [ ] **0-9.** Cuando una fecha dicha por la persona admite dos lecturas ("el martes que
      viene" un viernes: 6/10 o 13/10), Leda no elige: pregunta "¿Para qué martes?" con
      un botón por fecha posible. Cuando la fecha tiene una sola lectura ("el 15/10",
      "mañana", "el martes 13", "dentro de dos semanas"), sigue como hoy, sin preguntar.
      Mecanismo: el modelo devuelve todas las fechas posibles en su salida estructurada
      (etapa 2 del ADR 0014) y el código arma los botones y valida cada una (etapa 4).
      Ninguna lista de frases. Vale para la fecha en cualquier punto del alta y en
      Modificar. Constitución §4 (no completa con lo más probable); "botones donde hay
      opciones".

### Botones para elegir, texto para decir (2026-10-02, después de 0-4)

Observación del usuario sobre la ronda 0-4: funcionó, pero modificar dato por dato con
botones se sintió mecánico. Quiere poder escribir varias cosas juntas ("quiero modificar
la fecha por tal día y la tarea por tal otra, ¿qué objetivos hay?"), como ya pasa en el
primer mensaje del alta ("creá una tarea para tal día, es tal cosa y la hago yo"), y que
Leda pregunte sólo lo que falta. **Decisión del usuario: enmienda del ADR 0013 del
2026-10-02, en `main`.** Botones sólo para elegir entre opciones que la persona no conoce
(objetivos, responsables), por ambigüedad (0-9), para las confirmaciones de la
constitución §7, y cuando la persona pide ayuda. Todo lo demás, por texto.

**Decidido, listo para hacer** (después de que terminen 0-5 y 0-6, que tocan código
vecino):

- [ ] **0-10.** En el alta conducida, tocar Modificar ya no abre la lista de botones por
      dato (0-3): Leda contesta con un texto armado por el código, no por el modelo
      (para que no se repita H2), del estilo "Decime qué querés cambiar, podés decirme
      varias cosas juntas". La persona puede además escribir el cambio sin tocar
      Modificar. Un mensaje con varios cambios aplica todos en un turno y pregunta sólo lo
      que falta o lo ambiguo. El selector por dato queda para el alta guiada, que se
      retira igual.
- [ ] **0-11.** Pedido de ayuda: cuando la persona pide opciones ("¿qué objetivos hay?",
      "¿qué opciones tengo?") o no entiende lo que se le pide ("no entiendo"), el modelo lo
      devuelve como un comando de la lista cerrada y el código responde: si el dato tiene
      opciones, una explicación simple con sus botones; si es libre (criterio de
      aceptación), qué se necesita y un ejemplo concreto que se acepta con un toque. Sin
      listas de frases.
- [ ] **0-12.** Repetir en real una ronda con cambios escritos juntos y un pedido de
      ayuda, después de 0-10 y 0-11.

### Una sola fuente para las reglas de conversación (2026-10-02)

Hallazgo al agregar la fluidez a la constitución (§8, `main` `25b238e`): **el alta
conducida no lee el núcleo.** Su modelo recibe sólo sus instrucciones propias
(`SISTEMA_ALTA`, `src/leda/alta_turno.py:687`); la constitución y la mecánica las recibe
sólo el camino general (`contexto._nucleo`, `src/leda/contexto.py:38`, leído una vez al
arrancar el proceso y guardado en memoria). Consecuencia: un cambio o un descubrimiento
escrito en el núcleo no llega al alta. Además, la rama tenía la constitución vieja (sin
"Leda ayuda y facilita"); se sincronizó con `main` en `677c533`.

**Decisión del usuario (2026-10-02): hay que hacerlo**, para que lo que se decida sobre
cómo conversa Leda se aplique en todos los circuitos.

- [ ] **0-13. Decidido, listo para hacer** (diseño del usuario, 2026-10-02, a partir
      del relevamiento de Hermes en `docs/research/hermes-agent.md`, "Cómo arma las
      instrucciones del agente"):
      1. **La voz de Leda en `nucleo/voz.md`**, al estilo de `SOUL.md` de Hermes: quién es,
         cómo conversa (fluida, no como un formulario), honestidad y lo que nunca hace,
         escrita como conducta con ejemplos concretos, no como lista de rasgos. Corta
         (unos 600 a 1.000 tokens) y siempre presente en todos los circuitos. La
         constitución sigue siendo la autoridad y la referencia; la voz dice cómo se
         habla, la constitución qué nunca se hace.
      2. **La constitución entera no se le manda al modelo:** lo que nunca puede pasar lo
         garantizan el código y la base.
      3. **El código elige qué sección del núcleo lleva cada circuito** (el alta, la
         mecánica del alta; la entrega, la de la entrega), desde los mismos archivos: una
         sola fuente. No la elige el modelo, porque Leda ya decide por código en qué
         circuito está y usa un modelo chico.
      4. **Lo fijo primero y lo que cambia al final** (voz, después la sección del
         circuito, después los datos del espacio, y los del turno al final), por si el
         proveedor reutiliza el comienzo idéntico. `PENDIENTE` verificar si lo hace.
      5. **Un tope de tamaño por circuito** con una prueba que falla a la vista.
      6. **Medir antes y después con el banco**: el mismo conjunto de turnos con el núcleo
         entero y con la voz más la sección del circuito; latencia y cumplimiento de reglas
         ("Cómo pensamos juntos", punto 8). Mejoras seguras: una sola fuente, la misma voz en
         todos los circuitos, cambios en un archivo, menos costo por turno. Probables, a
         medir: menos latencia (seguramente modesta) y mejor cumplimiento de reglas.
      Un cambio en `voz.md` vale al reiniciar el listener (como hoy el núcleo).
      **Ajustes del usuario (2026-10-02), a partir de su experiencia con Prisma en Hermes**
      (`docs/research/soul-y-contexto-de-prisma-en-hermes.md`):
      7. **Dos capas de voz:** `nucleo/voz.md` es la voz del producto, igual para todos los
         clientes (honestidad, fluidez, una sola pregunta clara, reconocer primero, firme
         sin hostilidad); el tono de cada cliente sale de su pack (`persona.registro`,
         glosario, equipo) y lo agrega el código según el espacio. Hallazgo: el alta tiene
         "con voseo" escrito en el código (`alta_turno.py:690`) aunque el pack ya lo define
         (`persona.registro: vos`); con un cliente que trate de usted, Leda le hablaría de
         vos. Se corrige acá.
      8. **Cada regla como conducta:** cuándo aplica, qué hace Leda, qué no hace y cómo se
         comprueba. Sin adjetivos sueltos ni ejemplos que se puedan copiar como respuesta.
      9. **Reglas que entran a la voz:** las cuatro frases distintas (acuse, efecto con
         comprobante real, propuesta, "no pude verificarlo"; nunca "quedó registrado" o
         "anoté" sin efecto real, la falla de H5); no encontrar no es que no exista; no
         anunciar "voy a consultar"; ante un dato faltante, para qué hace falta y una sola
         pregunta.
      10. **Antes de escribir cada frase, dónde va:** voz, contexto del cliente, dato de la
          base o control del código. Una prohibición escrita no reemplaza un bloqueo.
      11. **Cuatro evidencias para validar un cambio de voz:** el texto bien escrito, la
          versión cargada (huella de `voz.md` registrada como la del núcleo), los controles
          que funcionan aunque el modelo se equivoque, y la respuesta clara y con próximo
          paso en una prueba real.
      **Aprobación del texto:** `voz.md` es parte del núcleo; su texto lo aprueba el
      usuario, con la diferencia legible, antes de la prueba real.

      **Construido (borrador de voz pendiente de aprobación), 2026-10-02.** Commit
      `097d7ff`. Ruta: delegado (un escritor; más de dos archivos no triviales).
      Alcance: sólo el alta conversada; el camino general (`contexto.construir`) no
      cambió y sigue con el núcleo entero.
      - `nucleo/voz.md` (borrador 0.1): encabezado de núcleo para quien lo mantiene
        (la constitución sigue siendo la autoridad; cambios con aprobación del
        administrador) y, después de la línea divisoria, la voz que lee el modelo,
        en español neutro y escrita como conducta. Sin trato de ningún cliente.
      - `src/leda/instrucciones.py` arma las instrucciones del alta en orden fijo:
        voz, mecánica del alta (`alta_turno.MECANICA_ALTA`, que reemplaza a
        `SISTEMA_ALTA`) y tono del espacio desde su pack (`persona_config`: nombre,
        registro, formalidad, longitud, emojis). Los hechos y el historial siguen
        viajando aparte. Se leen una vez por proceso y se guardan por tono.
      - "Con voseo" salió del código del alta; la mecánica, la descripción de la
        herramienta, el esquema y la regla de fechas quedaron en tercera persona, sin
        voseo. Lo que ahora dice la voz (fluidez, honestidad, una sola pregunta, nada
        técnico, texto plano) se sacó de la mecánica.
      - Huellas: cada intento del alta registra en `audit_log` (acción
        `alta_conducida_turno`, `detalle`) `voz_hash` (SHA-256 de `voz.md`) e
        `instrucciones_hash` (SHA-256 del texto armado que recibió el modelo). No hay
        un registro de arranque de la huella del núcleo, así que no se agregó uno.
      - Tamaño, en tokens estimados (caracteres / 4): antes, `SISTEMA_ALTA` 3.703
        caracteres (~925); después, voz ~873 + mecánica ~854 + tono, en total 7.087
        caracteres (~1.771) con el tono de CoreWork. Tope: 2.000, con prueba que
        falla a la vista.
      - Pruebas: `tests/test_voz_y_instrucciones.py` (23). RED: error de colección
        (no existía `leda.instrucciones`); GREEN: 23 pasan. Se actualizaron siete
        pruebas de `tests/test_alta_turno.py` que afirmaban el texto viejo.
        Suite completa: `1 failed, 3480 passed, 333 deselected, 1 warning in 1016.53s` (2026-10-02; la única falla es la conocida `test_un_texto_con_un_dato_inventado_se_reintenta_con_el_motivo`).
      - Sin decidir: la mecánica del alta no toma ninguna sección de
        `nucleo/mecanica-pm.md` (§2 y §13 nombran datos que el alta no pide, como
        prioridad o dependencias, y empujarían al modelo a preguntarlos); queda para
        decidir con el usuario. La medición con el banco (punto 6) queda pendiente.
      **0-13 no se marca** hasta que el usuario apruebe el texto de la voz y pase la
      prueba real.

      **Segunda unidad (revisión del usuario del borrador), 2026-10-02.** Commits
      `f9a1595` (emojis desde el pack) y `92de5de` (voz 0.2). Ruta: delegado.
      - `nucleo/voz.md` 0.2, todavía **borrador pendiente de aprobación**: sección
        "Personalidad y trato" con doce rasgos escritos como rasgo, conducta y límite
        (cálida y agradable, cordial y profesional, amable sin ser informal, clara y
        breve, orientada a soluciones, respetuosa de las responsabilidades,
        persistente sin hostilidad, transparente, pide y no ordena, sin repetirse,
        acompaña y no vigila, bloqueos a tiempo). Líneas nuevas: nunca nombra un botón
        que no esté entre sus opciones, y no saluda por su cuenta (el saludo del día
        lo pone `saludo.py`). "Firme sin hostilidad" pasó entero al rasgo
        "Persistente"; la brevedad con próximo paso, al rasgo "Clara y breve"; la
        jerga, también ahí. Los emojis no están en la voz.
      - Emojis desde el pack, el mismo defecto que el voseo: `redaccion.py` tenía
        "ni emojis" y "sin emojis" fijos. Ahora `sistema_redaccion` y
        `sistema_charla` leen `persona_config.emojis` con
        `instrucciones.emojis_del_espacio`, y la redacción de la regla es una sola
        (`instrucciones.regla_de_emojis`), la misma del tono del alta. Con emojis:
        "algún emoji ocasional cuando suma calidez o claridad, no en cada respuesta ni
        como adorno". `SISTEMA_REDACCION` y `SISTEMA_CHARLA` quedan como la guía sin
        emojis. Sin cambios: "sin Markdown, sin jerga técnica y sin nombrar botones",
        y el voseo fijo de esas dos guías (fuera del alcance de esta unidad).
      - Tope del alta: 2.500 tokens estimados. Medido: voz 5.642 caracteres (~1.410),
        mecánica 3.419 (~854), total con el tono de CoreWork 9.236 (~2.309) sin emojis
        y 9.315 (~2.328) con emojis.
      - Pruebas: RED, cinco fallas en `tests/test_voz_y_instrucciones.py` y error de
        colección en `tests/test_redaccion_emojis.py` (no existía
        `sistema_redaccion`); GREEN, 389 pasan en las pruebas de voz, redacción, charla
        y alta. Suite completa con `persona.emojis: true` en `espacios/corework.yaml`:
        `2 failed, 3494 passed, 333 deselected, 1 warning in 941.85s` (la falla conocida
        y `tests/test_charla_breve.py::test_el_modelo_recibe_el_mensaje_y_la_pregunta_pendiente_como_datos`,
        que compara con la guía sin emojis).
      - **Pendiente de autorización:** el cambio de `persona.emojis` a `true` en
        `espacios/corework.yaml` no se commiteó, porque rompe esa prueba (archivo fuera
        del alcance autorizado, línea 172). Hace falta ajustar esa línea para que
        compare con la guía de emojis que corresponde al pack. Después, importar el pack
        a la base (lo hace el coordinador).

      **Tercera unidad: trato y emojis desde el pack en la redacción, 2026-10-02.**
      Commit `a251984`. El usuario autorizó `tests/test_charla_breve.py`.
      - `redaccion.py` ya no tiene voseo fijo: `sistema_redaccion` y `sistema_charla`
        reciben `registro` y `emojis` del pack (`persona_config`, por
        `instrucciones.tono_del_espacio`, la misma fuente del alta). Sin tono
        configurado no se inventa un trato. El resto de esas guías no cambió (siguen
        hablándole al modelo en voseo, en segunda persona).
      - `persona.emojis: true` en `espacios/corework.yaml`; la prueba de la charla
        compara con la guía de CoreWork (trato de vos, emojis permitidos).
      - Pruebas: RED, 8 fallas en `tests/test_redaccion_trato.py`; GREEN, 18 pasan.
        Suite completa: `1 failed, 3505 passed, 333 deselected, 1 warning in
        950.13s` (2026-10-02; sólo la falla conocida).
      - Pendiente: importar el pack a la base (coordinador).

### RDD de 0-3, 0-5 y 0-6 (2026-10-02)

Tramo desde la frontera `cb3befb` hasta `e8e6499` (0-3, 0-5, 0-6 y documentos): riesgo
medio, revisión debida por presupuesto, consentimiento permanente del usuario. Linaje
`review-a8f31237eafb9491`, una lente (confiabilidad): **aprobada y reconocida**. Nueva
frontera de revisión de la rama: `e8e6499`. Cuatro observaciones no bloqueantes, todas
en `despachador.py`, para mirar antes de la prueba real de 0-6: R3-001 (`:1002`,
advertencia), R3-002 (`:1043-1059`, advertencia), R3-003 (`:1006-1008`, sugerencia) y
R3-004 (`:185-191`, sugerencia).

**Pendiente antes de la prueba real de 0-5 y 0-6:** aplicar la migración `0028` a
`leda_flujo` con el listener detenido. **Hecho el 2026-10-02** con autorización del
usuario: respaldo previo `db/respaldos/leda_flujo-antes-de-0028-20261002.dump`, migración
con `psql -f` (29 mensajes viejos marcados), CoreWork con `emojis = true` y la restricción
de horario apagada (`tools/restriccion_horario.py`).

### Prueba real del flujo C2 (2026-10-02, 18:20-18:26): pasa

Con `1fc8db0` (voz 1.0, trato y emojis del pack, 0-1 a 0-6) y la restricción de horario
apagada. Marcos pidió "revisar los sensores de nivel de la línea 3 para el jueves que
viene, la hago yo", eligió el objetivo, pidió una sugerencia ("¿qué me sugerís?"), la
cambió por su versión y envió a aprobación; Ismael confirmó.

- **0-6 pasa:** los botones se quitaron en Telegram al resolverse: los de objetivo al
  elegir (18:22:29), los del resumen de Marcos al enviar (18:24:14) y los de Ismael al
  confirmar (18:26:31) (`message_outbox.botones_quitados_en`).
- **0-5 pasa:** Marcos tocó Modificar en el resumen viejo de las 12:50 y Leda contestó "Ese
  botón ya no está vigente: la tarea ya quedó creada", con el estado real y el menú de la
  tarea (el menú sigue sin cambios posibles: H6, circuito 9).
- **Voz:** cada turno registró `voz_hash` `3bbf0765…`, igual a la huella de
  `nucleo/voz.md` 1.0. Propuso un criterio ante el pedido de ayuda, tomó la versión de la
  persona ("Queda con tu versión"), una sola pregunta por mensaje.
- Aviso a Ismael al instante (18:24, fuera del horario original). Cuatro turnos de la IA
  aceptados al primer intento; sin incidentes.
- **Observaciones, sin decisión todavía:** (1) el primer mensaje tuvo respuesta a los 73 s:
  el turno duró 15 s pero arrancó 47 s después de llegar el mensaje; puede ser que se
  escribió antes de que el listener terminara de arrancar (Telegram lo entrega al
  arrancar); si se repite con el listener ya andando, es un hallazgo de latencia. (2)
  "Anoté revisar los sensores…" en el primer mensaje es cierto (se creó el borrador) pero
  puede leerse como tarea creada: ajuste fino de la voz. (3) El primer turno duró 15 s
  contra 7-11 s en las pruebas anteriores del día; con un caso no se sabe si es por las
  instrucciones más largas: juntar más casos antes de concluir.
- **El usuario no notó diferencia en la voz** ("habla exactamente igual que el flujo
  anterior"): disparador 4 de "Cómo pensamos juntos". Causas vistas: la mitad de los
  mensajes visibles son textos fijos del código (resumen, avisos, "Hecho. La tarea quedó
  comprometida.", el botón vencido), que ninguna voz cambia; la IA escribe una o dos
  oraciones por turno; y las instrucciones viejas ya pedían "colega atenta, cordial, clara
  y breve". En curso: medición con el banco, instrucciones de C1 contra C2 en seis
  escenarios (feliz, duda, frustración, algo imposible, varios cambios con pedido de ayuda
  y mensaje vago), tres veces cada uno.

**RDD de la voz y el trato desde el pack (2026-10-02):** tramo `e8e6499`…`1fc8db0`, riesgo
medio, revisión debida por presupuesto; linaje `review-1a8be8746c694446`, una lente
(confiabilidad): **aprobada y reconocida**. Nueva frontera: `c381d4d`. Cuatro
observaciones no bloqueantes: R3-001 (`espacios/corework.yaml:353`), R3-002
(`src/leda/alta_conducida.py:400-402`), R3-003 (`tests/test_voz_y_instrucciones.py:110-126`)
y R3-004 (`tests/test_redaccion_trato.py:68-71`).

## Relación con otros pendientes

- **P1-P7** (falla del proveedor, `odd/tasks/flujo-de-un-mensaje.md`): decidido y listo
  para hacer. Afecta a todos los circuitos, porque cualquier turno del modelo puede
  colgarse en medio de una prueba real.
- **Prueba con alguien que no conozca el guion:** una sola vez, al final, cuando
  aprobaron todos los circuitos (enmienda del ADR 0014, decisión del usuario del
  2026-10-02). Ningún circuito la espera para empezar.
