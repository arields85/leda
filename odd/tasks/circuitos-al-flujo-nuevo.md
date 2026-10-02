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

## Relación con otros pendientes

- **P1-P7** (falla del proveedor, `odd/tasks/flujo-de-un-mensaje.md`): decidido y listo
  para hacer. Afecta a todos los circuitos, porque cualquier turno del modelo puede
  colgarse en medio de una prueba real.
- **Orden respecto de la prueba de adopción del alta:** el ADR 0014 dice que el patrón
  pasa a entrega y aprobación *después* de que el alta apruebe su prueba de adopción, con
  alguien que no conozca el guion. Esa prueba hoy no tiene fecha. `PENDIENTE` de decisión
  del usuario: esperarla o avanzar con los circuitos antes.
