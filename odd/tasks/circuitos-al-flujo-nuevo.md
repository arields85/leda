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
que rodea al modelo** ("Cómo pensamos juntos", punto 8). La tarea no se creó: Ismael
canceló para no dejarla con el objetivo equivocado.

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

## Relación con otros pendientes

- **P1-P7** (falla del proveedor, `odd/tasks/flujo-de-un-mensaje.md`): decidido y listo
  para hacer. Afecta a todos los circuitos, porque cualquier turno del modelo puede
  colgarse en medio de una prueba real.
- **Prueba con alguien que no conozca el guion:** una sola vez, al final, cuando
  aprobaron todos los circuitos (enmienda del ADR 0014, decisión del usuario del
  2026-10-02). Ningún circuito la espera para empezar.
