# 39. El encargado pasa una tarea de su gente, la revisión sigue a quien era la tarea y un pase sin respuesta

**Qué prueba:** tres decisiones del usuario sobre delegar (2026-10-09; `odd/tasks/fase-c.md`, decisiones
26, 27 y 28, con la 43 derivada de la 28), sobre lo que construyó la 38. El encargado de un sector le pasa
a otra persona una tarea de alguien de su sector, con las mismas reglas de quién decide y quién la toma, y
Leda le avisa a quien la tenía. Una tarea que pasa al encargado que la revisaba se cierra cuando él dice
que la terminó, aprobada por él, y a Ismael no le llega nada: la revisión sigue a quien era la tarea, no a
quien la termina haciendo. Y un pase que nadie contesta se repite una vez el día hábil siguiente y, si
sigue sin respuesta, termina: la tarea sigue con quien la tenía, quien lo pidió se entera y a quien se le
preguntaba Leda le dice que ya no hace falta que conteste (decisión 39). El encargado también se queda él
con una tarea de su gente (decisión 53). ADR 0017, enmienda a la decisión 2; constitución §7 (un cambio
de responsable se confirma) y §4 (honestidad); mecánica §5 (cierre), §7 (aprobación) y §12 (auditoría).

**Corre desde las decisiones 26 a 28 de la C-7** (`odd/tasks/fase-c.md`), entera, con su YAML. Los
pasos 19 a 23 cambiaron con la corrección de la C-7 (decisiones 39 y 53, 2026-10-09).

## Las reglas

1. **El encargado pasa una tarea de su gente** (decisión 27). Marcos, encargado de OT, puede pedir que
   una tarea de Nahuel pase a otra persona. Rigen las reglas de la 38: decide el encargado del sector
   de quien recibe (si es Marcos, su pedido es la decisión) y quien recibe la toma. Al tomarla, Leda le
   avisa a quien pidió, a quien decidió y a quien la tenía, que su tarea pasó a otra persona.
2. **La revisión sigue a quien era la tarea** (decisión 28). La revisa quien aprueba el trabajo de quien
   la tenía antes de pasarla, aunque la termine haciendo esa misma persona. Tarea de Nahuel que hace
   Marcos: cuando Marcos dice que la terminó, se cierra ahí, con la auditoría de que la hizo y la aprobó
   Marcos, y a Ismael no le llega nada. Tarea de Nahuel que hace Lucas: la revisa Marcos. Tarea de Marcos
   que hace Nahuel: la revisa Ismael. Si la plataforma cambia quién aprueba a quien era la tarea, la
   revisión sigue el cambio (decisión 43; lo prueban las pruebas de la cocina).
3. **Un pase que nadie contesta** (decisión 26). Leda repite la pregunta una vez, el día hábil siguiente,
   a quien tiene que decidir o tomarla. Si sigue sin contestar, el pase termina al día hábil siguiente de
   la repetición, a la hora en que Leda escribe: le dice a quien lo pidió que no hubo respuesta y que la
   tarea sigue con quien la tenía, y quien lo pidió puede pedírselo a otra persona.
4. **Nunca un pase abierto sin que todos sepan cómo terminó** (decisión 39). Cuando un pase termina sin
   la respuesta de quien tenía que contestarlo (nadie contestó, o la tarea ya no se puede pasar), Leda
   también se lo dice a esa persona, que ya no hace falta que conteste, y deja de preguntarle: sus
   botones ya no esperan nada, y si contesta tarde, Leda le dice que no hay nada que contestar.
5. **El encargado se queda él mismo con una tarea de su gente** (decisión 53). Si Marcos dice "la del
   fusible de Nahuel la hago yo", es como pasársela a otra persona: pide, decide y la toma él, así que
   con su confirmación de la vista previa la tarea pasa a ser suya; Leda le avisa a Nahuel, y cuando
   Marcos dice que la terminó, se cierra ahí (regla 2).

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Personas:** Marcos es el encargado de OT y Nahuel es de OT; Martín es el encargado de Infraestructura
  IT y Lucas es de IT. Ismael aprueba el trabajo de Marcos y de Martín; Marcos, el de Nahuel; Martín, el de
  Lucas. Todos tienen un chat con Leda.
- **Tareas** (todas vencen el viernes 6 de noviembre; su aviso previo sale el martes 3, fuera de este
  hilo):
  - De Marcos: "Programar PLC de la comprimidora", `en_curso` desde el lunes 19.
  - De Nahuel: "Calibrar los sensores de la envasadora", `asignada`; "Ajustar el tornillo del tablero de
    la envasadora", `en_curso` desde el lunes 19, con su criterio: el tornillo queda ajustado al torque
    que indica el fabricante; "Cambiar el fusible del tablero de la envasadora", `en_curso` desde el
    lunes 19.
- **Lo que pide OT para entregar:** cómo quedó el trabajo, descrito por quien lo hizo.
- **Estado de la conversación de cada uno:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

### El encargado pasa una tarea de Nahuel (decisión 27)

1. **Marcos** escribe (martes 20, 10:00): "pasale la de los sensores de nahuel a lucas, nahuel esta
   tapado con lo de la paila"
   →
   - Jugadas: `pedir_reasignacion` sobre la de los sensores, que no está en su lista (la nombra), a
     Lucas.
   - Efecto: ninguno: es una vista previa (constitución §7).
   - La respuesta dice: la vista previa, que la de los sensores pasa de Nahuel a Lucas; que primero lo
     decide Martín, el encargado de Lucas, y después le pregunta a Lucas si la toma; que confirme.
   - La respuesta no dice: que la tarea ya pasó; que lo decide Ismael.
   - Botones: Confirmar.
   - Estado después: tema abierto, la vista previa del pase.

2. **Marcos** escribe (martes 20, 10:01): "dale"
   →
   - Jugadas: `confirmar`.
   - Efecto: el pedido queda esperando la decisión de Martín; se guarda la pregunta a Martín, que sale
     terminado el margen para corregir. La tarea sigue de Nahuel.
   - La respuesta dice: que le pregunta a Martín y le avisa; que mientras tanto la tarea sigue con Nahuel.

3. **Leda**, por su cuenta, a Martín (martes 20, 10:11): que Marcos quiere pasarle a Lucas la de los
   sensores, que tiene Nahuel; la pregunta, si lo aprueba. Botones: Aprobar el pase, No aprobarlo.

4. **Martín** escribe (martes 20, 10:30): "si dale"
   →
   - Jugadas: `contestar_el_pase` sobre la de los sensores, que sí.
   - Efecto: la decisión de Martín queda anotada; se guarda la pregunta a Lucas. La tarea sigue de Nahuel.
   - La respuesta dice: que le pregunta a Lucas si la toma.

5. **Leda**, por su cuenta, a Lucas (martes 20, 10:40): que Marcos le quiere pasar la de los sensores, que
   tiene Nahuel, y que Martín lo aprobó; la pregunta, si la toma. Botones: La tomo, No la tomo.

6. **Lucas** toca "La tomo" (martes 20, 11:00).
   →
   - Efecto: la tarea pasa a ser de Lucas; la fecha y el criterio no cambian. Se guardan los avisos a
     Marcos (lo pidió), a Martín (lo decidió) y a Nahuel (la tenía).
   - La respuesta dice: que la tarea quedó a su cargo, con su vencimiento; que se van a enterar.
   - La respuesta no dice: que Ismael se entera.

7. **Leda**, por su cuenta (martes 20, 11:10): a Marcos y a Martín, que Lucas tomó la de los sensores; a
   Nahuel, que su tarea de los sensores pasó a Lucas, a pedido de Marcos. Ninguno pide respuesta.

### La tarea de Nahuel que toma Marcos se cierra cuando él la termina (decisión 28)

8. **Nahuel** escribe (martes 20, 11:30): "le podes pasar la del tornillo a marcos? yo no llego"
   →
   - Jugadas: `pedir_reasignacion` sobre la del tornillo, a Marcos.
   - La respuesta dice: la vista previa, que pasa de Nahuel a Marcos, que decide y la toma con su
     respuesta.
   - Botones: Confirmar.

9. **Nahuel** toca "Confirmar" (martes 20, 11:31). → Se guarda la pregunta a Marcos.

10. **Leda**, por su cuenta, a Marcos (martes 20, 11:41): que Nahuel le quiere pasar la del tornillo; la
    pregunta, si la toma. Botones: La tomo, No la tomo.

11. **Marcos** escribe (martes 20, 12:00): "si la hago yo"
    →
    - Jugadas: `contestar_el_pase` sobre la del tornillo, que sí.
    - Efecto: la tarea pasa a ser de Marcos; la sigue revisando Marcos (era de Nahuel). Se guarda el aviso
      a Nahuel.

12. **Leda**, por su cuenta, a Nahuel (martes 20, 12:10): que Marcos tomó la del tornillo.

13. **Marcos** escribe (martes 20, 15:00): "listo el tornillo, quedo ajustado al torque del fabricante"
    →
    - Jugadas: `entregar` sobre la del tornillo; lo que escribió describe cómo quedó y el criterio.
    - Efecto: ninguno: la vista previa de la entrega.
    - La respuesta dice: lo que entrega; que al confirmarla queda aprobada por él (la revisa él) y
      terminada.
    - La respuesta no dice: que pasa a revisión; que Ismael la revisa o se entera.
    - Botones: Confirmar.

14. **Marcos** escribe (martes 20, 15:01): "dale"
    →
    - Jugadas: `confirmar`.
    - Efecto: la evidencia queda escrita, la tarea queda aprobada por Marcos y terminada en el mismo acto
      (auditoría: la entregó y la aprobó Marcos). Ningún aviso a Ismael ni a nadie para revisarla.
    - La respuesta dice: que la tarea quedó terminada.
    - La respuesta no dice: que espera una revisión; que Ismael se entera.

### Un pase que nadie contesta (decisión 26)

15. **Marcos** escribe (martes 20, 16:00): "la del plc pasasela a lucas"
    →
    - Jugadas: `pedir_reasignacion` sobre la del PLC, a Lucas.
    - La respuesta dice: la vista previa; que primero lo decide Martín.
    - Botones: Confirmar.

16. **Marcos** toca "Confirmar" (martes 20, 16:01). → Se guarda la pregunta a Martín.

17. **Leda**, por su cuenta, a Martín (martes 20, 16:11): que Marcos le quiere pasar la del PLC a Lucas; la
    pregunta, si lo aprueba. Martín no contesta.

18. **Leda**, por su cuenta, a Martín (miércoles 21, 10:00): la misma pregunta, otra vez, una sola; que si
    sigue sin contestar, el jueves 22 la tarea sigue con Marcos. Martín no contesta.

19. **Leda**, por su cuenta (jueves 22, 10:00): a Marcos, que Martín no contestó, que el pase terminó y
    la del PLC sigue con él, y que puede pedírselo a otra persona; a Martín, que el pase que pidió Marcos
    terminó, que la del PLC sigue con Marcos y que ya no hace falta que conteste, sin un reproche
    (decisión 39). Ninguno pide respuesta. Los botones de la pregunta a Martín ya no esperan nada.

20. **Martín** escribe (jueves 22, 10:30): "uh perdon recien lo veo, si dale"
    →
    - Jugadas: `contestar_el_pase`, que sí.
    - Efecto: ninguno: el pase ya terminó y la del PLC sigue con Marcos.
    - La respuesta dice: que ya no tiene nada que contestar.
    - La respuesta no dice: que la tarea pasó a Lucas; que lo anotó.

### El encargado se queda él mismo con una tarea de Nahuel (decisión 53)

21. **Marcos** escribe (jueves 22, 11:00): "la del fusible de nahuel la hago yo, el esta con la paila"
    →
    - Jugadas: `pedir_reasignacion` sobre la del fusible, que no está en su lista (la nombra), a Marcos.
    - Efecto: ninguno: es una vista previa (constitución §7).
    - La respuesta dice: la vista previa, que la del fusible pasa de Nahuel a él; que al confirmarla queda
      a su cargo y Leda le avisa a Nahuel; que confirme.
    - La respuesta no dice: que ya es suya; que le pregunta a alguien si lo aprueba o si la toma.
    - Botones: Confirmar.

22. **Marcos** escribe (jueves 22, 11:01): "dale"
    →
    - Jugadas: `confirmar`.
    - Efecto: la tarea pasa a ser de Marcos; la fecha y el criterio no cambian, y la revisa Marcos (era de
      Nahuel). Se guarda el aviso a Nahuel. Nadie más tiene que aprobarlo ni tomarla.
    - La respuesta dice: que la del fusible quedó a su cargo, con su vencimiento; que Nahuel se va a
      enterar.
    - La respuesta no dice: que Ismael se entera; que espera que alguien lo apruebe o la tome.

23. **Leda**, por su cuenta, a Nahuel (jueves 22, 11:11): que su tarea del fusible pasó a Marcos, a pedido
    de Marcos. No pide respuesta.

## Qué mide

- **Garantías (5b):** ningún responsable cambia sin las tres confirmaciones, también cuando lo pide el
  encargado; quien tenía la tarea se entera de que pasó a otra persona; una tarea que la hizo quien la
  revisa se cierra con su aprobación, sin que a Ismael le llegue nada; un pase sin respuesta no cambia
  nada, se repite una sola vez y termina con el aviso a quien lo pidió y a quien se le preguntaba, nunca
  en silencio; una respuesta tarde no cambia nada; el encargado que se queda con una tarea de su gente
  la tiene sólo después de confirmar la vista previa, y quien la tenía se entera.
- **Falla de comprensión:** que la IA no tome "la de los sensores de nahuel" como la tarea que nombra
  (`como_la_nombra`), "si la hago yo" como que la toma, "listo el tornillo…" como la entrega, o "la del
  fusible de nahuel la hago yo" como que se la queda él (a es Marcos).
