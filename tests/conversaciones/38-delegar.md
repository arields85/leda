# 38. Delegar una tarea por chat

**Qué prueba:** pasarle una tarea a otra persona por chat, con las garantías de siempre. Quien pide
ve una vista previa y la confirma; si decide otra persona, Leda se lo pregunta; quien recibe confirma
que la toma; recién entonces cambia el responsable, y Leda le avisa a quien pidió y, si no es la misma
persona, a quien decidió. Un "no" deja la tarea con quien la tenía y Leda se lo dice a quien pidió. A
Dirección no le llega nada. ADR 0017, enmienda a la decisión 2 (aceptada por el usuario el 2026-10-09);
`odd/tasks/fase-c.md`, decisión 9; constitución §7 (un cambio de responsable se confirma con una vista
previa); mecánica §7 (la re-aprobación la da quien decide) y §12 (auditoría).

**Corre desde la C-7** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (enmienda al ADR 0017, decisión 2)

1. **Quién puede pedirlo.** El encargado de un sector (el referente del área en el pack) le puede pasar
   una tarea suya a cualquiera; un integrante, sólo a alguien de su sector. Si un integrante pide pasarla a
   otro sector, Leda no lo hace y le dice quién lo decide: el encargado de su sector, una persona concreta.
2. **Quién decide:** el encargado del sector de quien recibe. Si quien pide es ese encargado, su pedido es
   la decisión. Si quien recibe es el encargado, decide él y su "sí" vale como decisión y como
   confirmación de que la toma. Ismael no interviene.
3. **Qué tareas:** asignadas, en curso o trabadas (una trabada se mueve con su bloqueo abierto). Una en
   revisión o terminada no se delega.
4. **Pasos:** (1) vista previa ("📋 Revisar comunicaciones pasa de Marcos a Nahuel") y confirmación, con el
   botón o escrita, con la guarda de siempre; (2) si decide otra persona, Leda se lo pregunta, y un "no"
   deja la tarea donde estaba y se le dice a quien pidió; (3) quien recibe confirma que la toma, y un "no"
   la deja donde estaba y se le dice a quien pidió; (4) al tomarla cambia el responsable y Leda le avisa a
   quien pidió y, si es otra persona, a quien decidió.
5. **Lo que no cambia:** la fecha objetivo, el criterio de aceptación y la evidencia. El trabajo lo sigue
   revisando quien revisaba la tarea antes de pasarla.

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-7):

- **Una tarea suya.** Cada persona pide pasar una tarea de la que es responsable; pasar la de otra persona
  no está en esta conversación.
- **Lo que pregunta Leda a quien decide y a quien recibe** sale terminado el margen para corregir, como
  todo lo que le llega a una persona por lo que dijo otra, con dos botones; también se contesta
  escribiendo. No se repite si no contesta.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Personas:** Marcos es el encargado de OT y Nahuel es de OT; Martín es el encargado de Infraestructura
  IT y Lucas es de IT. Ismael aprueba el trabajo de Marcos y de Martín; Marcos, el de Nahuel; Martín, el de
  Lucas. Todos tienen un chat con Leda.
- **Tareas** (todas vencen el viernes 6 de noviembre; su aviso previo sale el martes 3, fuera de este
  hilo):
  - De Marcos: "Revisar comunicaciones industriales de la comprimidora", `asignada`; "Programar PLC de la
    comprimidora", `en_curso` desde el lunes 19; "Instalar el panel HMI de la comprimidora",
    `en_revision` (entregada, espera la revisión de Ismael).
  - De Martín: "Instalar el servidor de datos de la planta", `en_curso` desde el lunes 19.
  - De Nahuel: "Calibrar los sensores de la envasadora", `asignada`.
- **Estado de la conversación de cada uno:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Marcos** escribe (martes 20, 10:00): "che me la pasas la de comunicaciones a nahuel? estoy tapado con
   lo de la paila"
   →
   - Jugadas: `pedir_reasignacion` sobre la de comunicaciones, a Nahuel.
   - Efecto: ninguno: es una vista previa (constitución §7).
   - La respuesta dice: la vista previa, que la de comunicaciones pasa de Marcos a Nahuel; que antes Leda
     le pregunta a Nahuel si la toma; que confirme con el botón o escribiéndolo.
   - La respuesta no dice: que la tarea ya pasó; que lo decide Ismael; que Ismael se entera.
   - Botones: Confirmar.
   - Estado después: tema abierto, la vista previa del pase.

2. **Marcos** escribe (martes 20, 10:01): "dale"
   →
   - Jugadas: `confirmar`. La guarda: es lo último que Marcos vio, en el mensaje anterior, sin cambios.
   - Efecto: el pedido queda anotado; Marcos lo decide al pedirlo (es el encargado de OT). Se guarda la
     pregunta a Nahuel, que sale terminado el margen para corregir. La tarea sigue de Marcos.
   - La respuesta dice: que le pregunta a Nahuel si la toma y que le avisa cuando conteste; que mientras
     tanto la tarea sigue con él.
   - La respuesta no dice: que la tarea ya es de Nahuel; que Ismael se entera.
   - Estado después: sin tema abierto.

3. **Leda**, por su cuenta, a Nahuel (martes 20, 10:11).
   →
   - El mensaje dice: que Marcos le quiere pasar la de comunicaciones, que vence el viernes 6; la pregunta,
     si la toma.
   - Botones: La tomo, No la tomo.

4. **Nahuel** toca "La tomo" (martes 20, 10:30).
   →
   - Efecto: la tarea pasa a ser de Nahuel; la fecha y el criterio no cambian. La auditoría guarda quién
     pidió, quién decidió, quién aceptó y quién la tenía. Se guarda el aviso a Marcos.
   - La respuesta dice: que la tarea quedó a su cargo, con su vencimiento; que Marcos se va a enterar.
   - La respuesta no dice: que Ismael se entera.

5. **Leda**, por su cuenta, a Marcos (martes 20, 10:40): que Nahuel tomó la de comunicaciones; que no hace
   falta contestar.

6. **Marcos** escribe (martes 20, 11:00): "y la del hmi tambien pasasela a nahuel"
   →
   - Jugadas: `pedir_reasignacion` sobre la del panel HMI, a Nahuel.
   - Efecto: ninguno. La tarea está en revisión: el trabajo ya está hecho y no se delega.
   - La respuesta dice: que esa no se puede pasar porque ya la entregó y espera la revisión.
   - La respuesta no dice: que le pregunta a Nahuel.

7. **Marcos** escribe (martes 20, 11:02): "bueno entonces la del plc pasala a lucas, martin me dijo q lo
   tiene libre"
   →
   - Jugadas: `pedir_reasignacion` sobre la del PLC, a Lucas.
   - Efecto: ninguno, la vista previa.
   - La respuesta dice: la vista previa, que la del PLC pasa de Marcos a Lucas; que primero lo decide
     Martín, el encargado de Lucas, y después le pregunta a Lucas si la toma.
   - Botones: Confirmar.

8. **Marcos** toca "Confirmar" (martes 20, 11:03).
   →
   - Efecto: el pedido queda esperando la decisión de Martín; se guarda la pregunta a Martín.
   - La respuesta dice: que le pregunta a Martín y le avisa.

9. **Leda**, por su cuenta, a Martín (martes 20, 11:13): que Marcos le quiere pasar la del PLC a Lucas; la
   pregunta, si lo aprueba. Botones: Aprobar el pase, No aprobarlo.

10. **Martín** escribe (martes 20, 11:30): "si dale, que la agarre lucas"
    →
    - Jugadas: `contestar_el_pase` sobre la del PLC, que sí.
    - Efecto: la decisión de Martín queda anotada (es la re-aprobación del cambio de responsable,
      mecánica §7); se guarda la pregunta a Lucas. La tarea sigue de Marcos.
    - La respuesta dice: que le pregunta a Lucas si la toma.

11. **Leda**, por su cuenta, a Lucas (martes 20, 11:40): que Marcos le quiere pasar la del PLC y que Martín
    lo aprobó; la pregunta, si la toma. Botones: La tomo, No la tomo.

12. **Lucas** escribe (martes 20, 12:00): "uh no puedo esta semana, estoy con lo del data center"
    →
    - Jugadas: `contestar_el_pase` sobre la del PLC, que no, con su motivo.
    - Efecto: la tarea sigue de Marcos; se guardan los avisos a Marcos, que lo pidió, y a Martín, que lo
      aprobó: quien autorizó el pase también se entera de cómo terminó (decisión 39, desde la C-5c).
    - La respuesta dice: que la tarea sigue con Marcos y que Marcos se va a enterar.

13. **Leda**, por su cuenta, a Marcos y a Martín (martes 20, 12:10): que Lucas no puede tomar la del PLC y
    que sigue con Marcos.

14. **Martín** escribe (martes 20, 14:00): "pasale lo del servidor a marcos, me pidieron otra cosa urgente"
    →
    - Jugadas: `pedir_reasignacion` sobre la del servidor, a Marcos.
    - La respuesta dice: la vista previa, que pasa de Martín a Marcos; que Marcos, encargado de OT, decide
      y la toma con su respuesta.
    - Botones: Confirmar.

15. **Martín** escribe (martes 20, 14:01): "si"
    →
    - Jugadas: `confirmar`.
    - Efecto: se guarda la pregunta a Marcos.

16. **Leda**, por su cuenta, a Marcos (martes 20, 14:11): que Martín le quiere pasar la del servidor; la
    pregunta, si la toma. Botones: La tomo, No la tomo.

17. **Marcos** escribe (martes 20, 14:30): "dale la agarro yo"
    →
    - Jugadas: `contestar_el_pase` sobre la del servidor, que sí.
    - Efecto: la tarea pasa a ser de Marcos; su "sí" vale como decisión y como confirmación. Se guarda el
      aviso a Martín.

18. **Leda**, por su cuenta, a Martín (martes 20, 14:40): que Marcos tomó la del servidor.

19. **Nahuel** escribe (martes 20, 15:00): "le podes pasar la de los sensores a lucas?"
    →
    - Jugadas: `pedir_reasignacion` sobre la de los sensores, a Lucas.
    - Efecto: ninguno: Nahuel es integrante de OT y Lucas es de otro sector.
    - La respuesta dice: que eso no lo puede hacer por él y que lo decide Marcos.
    - La respuesta no dice: que le pasa el pedido a Marcos; que lo decide Ismael o Martín.

20. **Nahuel** escribe (martes 20, 15:02): "ah ok entonces pasasela a marcos"
    →
    - Jugadas: `pedir_reasignacion` sobre la de los sensores, a Marcos.
    - La respuesta dice: la vista previa, que pasa de Nahuel a Marcos, que decide y la toma.
    - Botones: Confirmar.

21. **Nahuel** toca "Confirmar" (martes 20, 15:03). → Se guarda la pregunta a Marcos.

22. **Leda**, por su cuenta, a Marcos (martes 20, 15:13): que Nahuel le quiere pasar la de los sensores; la
    pregunta, si la toma.

23. **Marcos** escribe (martes 20, 15:30): "no, esa hacela vos nahuel que la conoces mejor"
    →
    - Jugadas: `contestar_el_pase` sobre la de los sensores, que no, con su motivo.
    - Efecto: la tarea sigue de Nahuel; se guarda el aviso a Nahuel.

24. **Leda**, por su cuenta, a Nahuel (martes 20, 15:40): que Marcos no la toma y que sigue con él, con lo
    que dijo Marcos.

## Qué mide

- **Garantías (5b):** ningún responsable cambia sin la confirmación de quien pide, la decisión de quien
  decide y la de quien recibe; un "no" no cambia nada; una tarea en revisión no se pasa; un integrante no
  pasa una tarea a otro sector; a Ismael no le llega nada; nadie se entera de algo que no pasó.
- **Falla de comprensión:** que la IA no tome "me la pasas … a nahuel" como un pedido de pase, "dale"
  como la confirmación, o "si dale, que la agarre lucas" y "no puedo esta semana" como la respuesta al
  pase.
- **El límite del cargador:** OT tiene sólo a Marcos y a Nahuel, así que el caso "Nahuel se la pasa a
  otro de OT y Marcos decide" no corre acá; lo prueban las pruebas del motor con un integrante más.
