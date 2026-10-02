# Circuitos de Leda al flujo nuevo (ADR 0014)

**Prioridad del proyecto** (decisión del usuario, 2026-10-02). Cada circuito
conversacional que Leda ya sabe hacer pasa al flujo nuevo del
[ADR 0014](../../docs/decisions/0014-flujo-de-un-mensaje.md), igual que el alta
conducida: el modelo interpreta y conduce la conversación, y el código garantiza
autoridad, validación, confirmación, ejecución única y auditoría. Después, cada uno
se prueba por Telegram real, con datos ficticios, y las cuentas las opera el usuario.

**Rama:** `feat/flujo-de-un-mensaje`, base `leda_flujo`.

## Regla para cada circuito

Un circuito se tilda sólo cuando se cumplen sus cuatro pasos:

1. **Diseño:** acordado con el usuario y escrito en este documento, con su chequeo de
   rumbo ("Cómo pensamos juntos", punto 3, en `AGENTS.md`). Desde ahí queda "decidido,
   listo para hacer".
2. **Construcción:** con el flujo nuevo, con pruebas primero y revisión RDD.
3. **Retiro de lo viejo:** "un camino pasa al flujo nuevo sólo cuando se retiró lo
   viejo" (`AGENTS.md`, punto 7).
4. **Prueba real:** por Telegram, con un guion numerado. Se leen la conversación, la base,
   la auditoría y los incidentes. Pasa con los criterios de adopción del ADR 0014: al
   menos nueve de cada diez turnos del modelo aceptados al primer intento, ningún
   mensaje sin próximo paso, ninguna clase de falla repetida y ningún incidente nuevo.

## Checklist

Estado actual de cada uno: *por diseñar*, salvo el alta, que ya está construida.

- [ ] **C0. Alta de tarea: variantes que faltan probar.** El alta conducida está
      construida y su camino principal pasó la prueba real (2026-10-02, 11:07; quien
      confirma es otra persona). Faltan, en real: quien pide confirma su propia tarea;
      pedir una tarea para otra persona; Modificar un dato del resumen; Cancelar; y el
      aprobador rechaza con motivo. Falta también retirar el alta guiada vieja (M4-M9).
- [ ] **C1. Entrega con evidencia.** El responsable avisa que terminó y entrega evidencia
      (explicación, foto, archivo, resultado de prueba). La tarea pasa a `en_revision` y
      se avisa al aprobador. Mecánica §3 y §6; ADR 0009.
- [ ] **C2. Aprobación de la entrega.** El aprobador aprueba (la tarea queda
      `terminada`) o pide cambios con un motivo que el responsable ve. Mecánica §5 y §7;
      ADR 0008.
- [ ] **C3. Estados y bloqueos.** "Ya empecé" (`en_curso`), declarar un bloqueo con su
      causa, resolverlo, y que la tarea vuelva a su estado anterior. Mecánica §3 y §8.
- [ ] **C4. Consultas y menú de tarea.** "¿Qué tengo pendiente?", la lista con un botón
      por tarea, "Ver más" y el menú de cada tarea según quién la mira. ADR 0007.
- [ ] **C5. Dependencias.** "Esta no puede arrancar hasta que termine aquella", y el
      aviso en cadena cuando la primera se atrasa. Mecánica §4.
- [ ] **C6. Aclaración de referencias.** Una referencia ambigua a una tarea, una persona
      o un objetivo, y Leda pregunta cuál, con botones. Etapa 3 del ADR 0014 (Jev);
      ADR 0006.
- [ ] **C7. Cambio de tema con una pregunta abierta.** Escribir otra cosa a mitad de
      algo: "¿Seguimos con eso?", seguir o dejarlo. ADR 0013, regla 1.
- [ ] **C8. Seguimiento automático.** Recordatorios por vencimiento, pedido de estado y
      resumen del equipo, y cómo Leda conversa la respuesta de la persona. Para probarlo
      en real hay que forzar fechas y cadencias por consola (`leda escalera`,
      `leda correr`). Mecánica §9 a §11.
- [ ] **C9. Cambios sobre una tarea creada.** Cambiar el responsable, la fecha o el
      criterio de una tarea ya comprometida, con vista previa, confirmación y la
      re-aprobación cuando el cambio cruza el umbral (cambio de responsable, corrimiento
      de fecha, cambio de criterio). Hoy no existe: no hay herramienta para hacerlo.
      Constitución §7 (cambios de asignación y de fecha con confirmación humana);
      mecánica §7 (umbral de re-aprobación). Agregado el 2026-10-02 por la ronda C0-C
      (hallazgo H5): no es funcionalidad nueva, es comportamiento obligatorio del núcleo.

## C0: chequeo de rumbo y rondas (2026-10-02)

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

- **Ronda C0-A:** Ismael pide una tarea para Marcos, toca Modificar y cambia un dato, y
  confirma él mismo. Cubre "quien pide confirma", "para otra persona" y Modificar.
- **Ronda C0-B:** Marcos pide una tarea y la cancela desde el resumen. Cubre Cancelar.
- **Ronda C0-C:** Marcos pide una tarea y la envía a aprobación; Ismael la rechaza y
  escribe el motivo. Cubre el rechazo con motivo.

### Ronda C0-A (2026-10-02, 12:35-12:41): hallazgos y decisión

Ismael pidió una tarea para Marcos ("revisar el cableado del tablero de la línea 2"). Los
cinco turnos del modelo fueron aceptados al primer intento y no hubo incidentes. El modelo
entendió todo, incluido "el objetivo" escrito a mano; **las tres fallas están en el código
que rodea al modelo** ("Cómo pensamos juntos", punto 8). La tarea no se creó: a las
12:45:38 Ismael escribió "nada, cancela" y la solicitud quedó `cancelled` en el mismo
segundo, con "Listo, cancelo la tarea y no queda nada guardado. Si más adelante querés
armarla de nuevo, la empezamos cuando digas." Cancelar por texto funciona; C0-B prueba el
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

- [ ] **C0-1.** Los objetivos que ofrece el alta salen del **área de la tarea**, que es la
      del responsable, igual que el área y el aprobador. Ismael pidiendo para Marcos ve
      los objetivos de OT.
- [ ] **C0-2.** Una tarea cuelga sólo de un **objetivo operativo**, nunca del estratégico
      (mecánica §1: la tarea va bajo el objetivo operativo). Si el área de la tarea no
      tiene ningún objetivo operativo activo, Leda lo dice con el estado real y no
      completa con otro (constitución §4). Se retira la caída a los objetivos sin área.
- [ ] **C0-3.** Modificar muestra **un botón por dato modificable**, armado por el código
      desde el resumen vigente (objetivo incluido), no una lista escrita por el modelo.
- [ ] **C0-4.** Repetir la ronda C0-A en real después de C0-1 a C0-3.

Comprobaciones: RED primero con un alta pedida por alguien de otra área (Dirección para OT)
que hoy ofrece el estratégico; prueba de que Modificar arma sus botones desde el resumen;
suite completa de la rama.

### Rondas C0-B y C0-C (2026-10-02, 12:46-12:53): resultado y hallazgos

- **C0-B, Cancelar con el botón: pasa.** Marcos tocó Cancelar en el resumen (12:48:16) y
  a las 12:48:17 Leda contestó "Listo, cancelé el borrador de la tarea."
- **C0-C se desvió y quedó sin probar el rechazo con motivo.** Marcos eligió a Nahuel como
  responsable; como Marcos es el aprobador de Nahuel, tuvo Confirmar y la tarea se creó
  (12:50:25, "Calibrar los sensores de temperatura de la línea 1", a cargo de Nahuel).
  Bien: "Nahuel Gimenez todavía no activó su chat con Leda, así que no le pude avisar"
  (auditoría `omitir_aviso_asignacion_ingreso_tarea`). Hay que repetir C0-C.
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
  hechos. Lo corrige pasar ese camino al flujo nuevo (C3, C4, C9), no un parche.
- **H6. El menú de la tarea no ofrece cambios.** Marcos, aprobador de Nahuel y quien la
  creó, ve sólo "Ver detalle". Consecuencia de que no exista la capacidad (C9).

**Decisión del usuario (2026-10-02): decidido, listo para hacer.**

- [ ] **C0-5.** Un toque sobre un botón que ya no está vigente contesta con el **estado
      real** de lo que ese botón tocaba (por ejemplo, "la tarea ya quedó creada") y
      ofrece lo que se puede hacer ahora con eso, nunca un mensaje sin próximo paso
      (constitución §8). Vale para todo botón vencido, no sólo para el resumen del alta;
      corrige también C-3 de `main`.
- [ ] **C0-6.** Cuando una vista previa o una elección se resuelve (confirmada, cancelada,
      enviada o vencida), sus botones se quitan del mensaje en Telegram, para que no se
      ofrezca lo que ya no se puede hacer (ADR 0013, regla 3).
- [x] **C0-7.** Repetir la ronda C0-C (rechazo con motivo) con Marcos como responsable.
      Hecho el 2026-10-02, 13:06-13:10: ver abajo.

### Ronda C0-C repetida (2026-10-02, 13:06-13:10): pasa

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

- [ ] **C0-8.** El aviso de rechazo a quien pidió cierra con dos botones: **"Volver a
      armarla"** reabre el borrador con los mismos datos, para corregir lo que hizo falta
      y volver a enviarlo (con su resumen, Modificar y Enviar a aprobación); **"Dejarla
      así"** cierra el tema sin efectos. Toque idempotente y con estado real si el
      borrador ya no se puede reabrir (C0-5).

**Estado de C0 al 2026-10-02:** las cinco variantes ya se probaron en real (confirma quien
pide, para otra persona, Modificar, Cancelar por texto y por botón, rechazo con motivo).
Falta construir C0-1, C0-2, C0-3, C0-5, C0-6 y C0-8, retirar el alta guiada (M4-M9) y repetir
la ronda C0-A (C0-4).

## Relación con otros pendientes

- **P1-P7** (falla del proveedor, `odd/tasks/flujo-de-un-mensaje.md`): decidido y listo
  para hacer. Afecta a todos los circuitos, porque cualquier turno del modelo puede
  colgarse en medio de una prueba real.
- **Prueba con alguien que no conozca el guion:** una sola vez, al final, cuando
  aprobaron todos los circuitos (enmienda del ADR 0014, decisión del usuario del
  2026-10-02). Ningún circuito la espera para empezar.
