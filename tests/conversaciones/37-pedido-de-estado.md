# 37. El pedido de estado del lunes

**Qué prueba:** con el ritmo fijo del equipo (la cadencia del lunes), Leda le pide a cada persona
el estado de sus tareas en un solo mensaje, con la lista; el recordatorio del vencimiento de ese
día va dentro de la lista ("vence hoy") y no sale aparte. Lo que la persona contesta de cada tarea
cuenta para el seguimiento de esa tarea. Si contesta sólo una, Leda la anota y, en la misma
respuesta, pregunta una vez por las otras. Decisión 8 del usuario (`odd/tasks/fase-c.md`,
2026-10-08, opción A); ADR 0017, decisión 3b, punto 5; mecánica §9, §10 y §12.

**Corre desde la C-6** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **Un pedido de estado por persona con la lista de sus tareas**, con el ritmo del pack del espacio
   (en CoreWork, entre otros, el lunes a las 09:15).
2. **El recordatorio de vencimiento del día entra en la lista** ("vence hoy") y no sale aparte.
3. **Lo contestado cuenta para la escalera de esa tarea.**
4. **Si contesta sólo una, Leda anota esa y pregunta una vez por las otras en la misma
   respuesta**; si no contesta, rige la decisión 21 (una pregunta de Leda sin contestar).
5. Las cadencias del pack quedan como están para probar; después se prenden, apagan y ajustan desde la
   plataforma.

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-6):

- **A qué hora sale:** lo que Leda manda por su cuenta sale a una sola hora, las 10:00
  (`leda.motor.tiempo`, `HORA_DE_SALIDA`): la cadencia de las 09:15 sale a las 10:00, junto con el
  recordatorio del vencimiento de ese día. Una cadencia más tarde (el miércoles a las 11:30) sale a su
  hora, y lo que la escalera tenía para ese día sobre esas tareas espera y va en la lista.
- **Qué tareas van en la lista:** desde la decisión 32 del usuario (2026-10-09), todas las abiertas,
  cada una con su situación, también las trabadas y las entregadas; Leda pregunta cómo vienen sólo por
  las asignadas o en curso sin un bloqueo (la conversación 40). Acá todas se pueden mover.
- **Una vez por las otras:** si después de esa pregunta la persona contesta otra vez sólo una parte,
  Leda anota lo que dijo y no vuelve a preguntar por la lista. Las que vencen siguen con su escalera.
- **"Viene bien" de una tarea que todavía no vence** queda anotado con sus palabras, y Leda no le
  vuelve a preguntar por ella hasta la próxima lista completa o, si vence antes, hasta el día de su
  vencimiento; si entre la respuesta y el vencimiento no hay otra lista, lo contestado lo cubre
  (decisión 31 del usuario, 2026-10-09) y pregunta el día hábil siguiente, si sigue sin entregar. Si el
  aviso previo todavía no salió, sale antes, como siempre (decisión 44; la conversación 40).

## Estado inicial

- **Día:** D = miércoles 21, dentro del horario.
- **Cadencias del espacio:** sólo la del lunes a las 09:15, a cada integrante en privado
  (`objetivos_semanales` del pack). Las demás del pack (miércoles y viernes, y las del grupo) se suponen
  apagadas.
- **Tareas de Marcos** (OT; aprueba su trabajo Ismael):
  - "Programar PLC de la comprimidora": vence el lunes 26; `en_curso` desde el lunes 19.
  - "Revisar comunicaciones industriales de la comprimidora": vence el viernes 30; `asignada`; sin
    dependencias.
  - "Instalar el panel HMI de la comprimidora": vence el viernes 6 de noviembre; `en_curso` desde el
    lunes 19.
- **Tareas de Nahuel** (OT; aprueba su trabajo Marcos):
  - "Calibrar los sensores de la envasadora": vence el jueves 29; `en_curso` desde el martes 20. Su
    aviso previo (tres días hábiles antes) toca el lunes 26.
  - "Cambiar el motor de la cinta 4": vence el viernes 6 de noviembre; `asignada`.
  - "Cablear el tablero de la línea 2": vence el viernes 6 de noviembre; `asignada`.
- **Estado de la conversación** de todos: sin tema abierto, nada para después.
- **Ya enviado:** el aviso previo del PLC, el miércoles 21 a las 10:00 (corre por el motor, preludio).

## Hilo

1. **Leda**, por su cuenta (lunes 26, 10:00): el pedido de estado del lunes, a Marcos y a Nahuel.
   →
   - Efecto: un mensaje privado a Marcos con la lista de sus tres tareas, y el recordatorio del
     vencimiento del PLC adentro: un solo mensaje, ningún recordatorio aparte. Un mensaje privado a
     Nahuel con la lista de sus tres tareas, con el aviso previo de los sensores adentro (vencen el
     jueves). A Ismael, nada (no tiene tareas).
   - El mensaje a Marcos dice: cada tarea con su vencimiento; que la del PLC vence hoy; la pregunta de
     cómo vienen, una sola, al final.
   - El mensaje a Marcos no dice: un reproche; que se va a avisar a alguien; una pregunta por tarea.
   - Estado después: Marcos y Nahuel tienen abierta la pregunta de cómo vienen sus tareas; la espera
     del estado del PLC, abierta (la de su escalera).

2. **Marcos** escribe (lunes 26, 10:40): "el plc lo termino el miercoles q se me atraso la placa, las
   comunicasiones arranco hoy y el hmi viene bien"
   →
   - Jugadas: `anotar_prevision` sobre el PLC, para el miércoles 28, con su motivo; `anotar_inicio`
     sobre las comunicaciones; `informar_avance` sobre el panel HMI, con sus palabras.
   - Efecto: la previsión del PLC (la fecha comprometida no cambia) y su aviso a Ismael, a las 10:50;
     las comunicaciones, en curso; el avance del panel HMI anotado. La espera del PLC se cierra.
   - La respuesta dice: lo anotado de cada tarea; que del panel HMI le vuelve a preguntar el lunes 2
     (el próximo pedido de la lista), como algo que todavía no pasó.
   - La respuesta no dice: ninguna pregunta; que el panel HMI vuelve a preguntarse mañana.
   - Estado después: sin pregunta abierta.

3. **Leda**, por su cuenta (lunes 26, 10:50): el aviso a Ismael de la fecha nueva del PLC.

4. **Nahuel** escribe (lunes 26, 10:55): "los sensores ya casi estan me falta uno"
   →
   - Jugadas: `informar_avance` sobre los sensores, con sus palabras.
   - Efecto: el avance de los sensores anotado.
   - La respuesta dice: lo anotado de los sensores; que le vuelve a preguntar el viernes 30, si para
     entonces no la entregó (el jueves 29, el día en que vencen, no: ya contó cómo vienen, decisión 31);
     y, en la misma respuesta, una sola pregunta por las otras dos tareas de la lista (el motor de la
     cinta 4 y el tablero de la línea 2).
   - La respuesta no dice: una pregunta por los sensores; un reproche.
   - Estado después: la pregunta de cómo vienen sus tareas sigue abierta, con las dos que faltan.

5. **Nahuel** escribe (lunes 26, 11:30): "el motor ya lo empece"
   →
   - Jugadas: `anotar_inicio` sobre el motor de la cinta 4.
   - Efecto: el motor de la cinta 4, en curso.
   - La respuesta dice: que quedó anotado que arrancó el motor de la cinta 4.
   - La respuesta no dice: otra pregunta por el tablero de la línea 2 (ya preguntó una vez por las
     otras).
   - Estado después: sin pregunta abierta.

6. **Leda**, por su cuenta (lunes 26, 16:00): nada. Ni a Marcos ni a Nahuel se les vuelve a pedir la
   lista ese día.

## Qué mide

- **Garantías (5b):** un solo mensaje por persona con la lista, con el recordatorio del día adentro;
  ninguna fecha que nadie dio; la fecha comprometida no cambia; el aviso a Ismael sale una vez y
  después del margen para corregir; Leda pregunta una sola vez por las otras.
- **Falla de comprensión:** que la IA reparta mal lo que Marcos dijo entre las tres tareas (la placa
  que se atrasó es del PLC), o que tome "viene bien" como que el panel HMI está terminado.
