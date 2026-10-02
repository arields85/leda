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

## Relación con otros pendientes

- **P1-P7** (falla del proveedor, `odd/tasks/flujo-de-un-mensaje.md`): decidido y listo
  para hacer. Afecta a todos los circuitos, porque cualquier turno del modelo puede
  colgarse en medio de una prueba real.
- **Prueba con alguien que no conozca el guion:** una sola vez, al final, cuando
  aprobaron todos los circuitos (enmienda del ADR 0014, decisión del usuario del
  2026-10-02). Ningún circuito la espera para empezar.
