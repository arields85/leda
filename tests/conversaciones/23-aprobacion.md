# 23. Quien aprueba decide

**Qué prueba:** Ismael tiene cuatro entregas esperando su decisión y contesta casi todo por escrito; una
vez toca el botón "Pedir cambios" del aviso, que le pregunta qué falta. Un "aprobado" claro cierra la
tarea, si el código comprueba que se cumple todo lo demás; si algo más frena el cierre, la aprobación
queda anotada, Leda lo dice con honestidad y, cuando lo que faltaba se resuelve, el código vuelve a
comprobar y la cierra sola, con aviso al responsable y a quien aprobó. Un pedido de cambios claro
devuelve la tarea a su responsable con el comentario. Lo que mezcla aprobar y pedir un cambio, y una
aprobación con un comentario que le pide algo a alguien (decisión 22), llevan una sola pregunta con
dos botones; un comentario que no pide nada, como un elogio, aprueba directo (su precisión, D7c). Y alguien que no aprueba esa tarea no puede aprobarla. Lo claro va
directo, sin vista previa: es la decisión de quien aprueba (`odd/tasks/fase-c.md`, decisiones 2 y 3).
Circuito 8 (ADR 0017, decisión 3b); ADR 0018, decisión 2; mecánica §5 y §7; constitución §3 y §11.

**Corre desde la porción 3b de la C-3** (`23-aprobacion.yaml`). El YAML suma tres pasos de Leda que
el hilo da por hechos (4b, 9b y 9c: los avisos que salen enseguida y el aviso previo del martes) y
corre el paso 10 aparte, por el motor y sin comprobarlo. Desde la porción 4, los avisos al responsable
de los pasos 3, 4b, 7, 9b y 11 llevan al final el enlace a la página de la tarea, que agrega el
código y sale sin vista previa; el de Ismael del paso 11, no. Desde la porción 3c, el lunes 26 la
escalera le guarda a Ismael el primer recordatorio de las tres entregas que siguen esperando su
decisión (conversación 24). Desde la D5 de la C-3d (no interrumpir, conversación 26) ese recordatorio
espera mientras Ismael conversa con Leda decidiendo, y al salir se relee: como Ismael decidió las
tres, no sale y queda omitido con su motivo. Por la misma regla, Marcos escribe a las 09:40 y no a las
10:20: así los avisos de las aprobaciones de sus tareas le llegan enseguida, como dice el hilo, en
lugar de esperar a que pasen 30 minutos desde su mensaje. Desde la
D4 de la C-3d: los cuatro avisos del viernes salen de a uno, cada uno al terminar su margen para
corregir (los que salen juntos irían en una lista, la conversación 28), y después de cada decisión
(pasos 2, 4 y 6) la respuesta dice lo que le queda por revisar a Ismael, con un botón por tarea para
verla (decisión 17 del usuario, 2026-10-08). En el paso 9, "pasale lo de los colores" es lo que la
decisión 12 llama el comentario: va con la aprobación, no como un pedido de cambios.

## Estado inicial

- **Día:** D = lunes 26, dentro del horario.
- **Personas:** Ismael aprueba el trabajo de Marcos, Mariano y Ariel (`aprobado_por: ismael`) y nadie
  aprueba el suyo. Marcos aprueba el de Nahuel, no el de Mariano. Lucas es de IT.
- **Tareas esperando la decisión de Ismael**, todas `en_revision` desde el viernes 23, con la evidencia
  completa según la política de su área y el aviso de la entrega ya enviado a Ismael el viernes:
  - "Programar PLC de la comprimidora" (Marcos, OT): sin bloqueos ni dependencias.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora" (Marcos, OT): depende, con una dependencia
    bloqueante, de "Cambiar switch industrial de la sala de servidores" (Lucas, IT), que está `en_curso`
    y vence el viernes 30. La dependencia se agregó cuando la de comunicaciones ya estaba en curso, como
    en la semilla.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora". El del switch: "El switch nuevo queda instalado y todos los equipos
    de la sala de servidores se conectan a la red sin cortes durante una hora".
  - "Cablear tablero de la máquina 3" (Mariano, electricidad): vence el viernes 30; sin bloqueos ni
    dependencias.
    Criterio de aceptación: "El tablero de la máquina 3 queda cableado según su diagrama y pasa la prueba
    de continuidad y de aislación".
  - "Dashboard de lotes en CoreLabs" (Ariel, CoreLabs): sin bloqueos ni dependencias.
    Criterio de aceptación: "El dashboard muestra los lotes del día con su cantidad y su estado, y
    coinciden con el registro de producción".
- **Estado de la conversación de Ismael:** sin tema abierto; las cuatro entregas, esperando su decisión.
  **De Marcos, Mariano y Ariel:** sin tema abierto.
- **Ya enviado:** a Ismael, los cuatro avisos de entrega, el viernes 23.

## Hilo

1. **Marcos** escribe (lunes 26, 09:40): "che el tablero de la maquina 3 de mariano ya lo vi yo, esta
   joya. aprobalo asi avanza"
   →
   - Jugadas: `aprobar`, la tarea de Mariano, con o sin lo que dijo como comentario. La jugada existe
     pero Marcos no puede hacerla: no es quien aprueba el trabajo de Mariano (`puede_aprobar_tarea`).
   - Efecto: ninguno; la tarea sigue `en_revision`. Ningún aviso al administrador (es una jugada que no se
     puede hacer, no una situación nueva; ADR 0018, decisión 1) y ninguno a Ismael ni a Mariano.
   - La respuesta dice: que esa aprobación no la puede hacer él; que la decide Ismael, tomado de los datos.
   - La respuesta no dice: que la aprobó; que le pasa a Ismael lo que dijo Marcos; nombres de jugadas.
   - Estado después: sin tema abierto. Las cuatro entregas siguen esperando a Ismael.

2. **Ismael** escribe (10:30): "el plc de marcos aprobado, impecable"
   →
   - Jugadas: `aprobar`, la tarea del PLC, con el comentario "impecable", que no le pide nada a
     nadie (`el_comentario_pide_algo` falso).
   - Confirmación: ninguna; lo claro va directo. Un comentario que no le pide nada a nadie no abre
     la pregunta de cuál de las dos (la precisión del usuario a la decisión 22, 2026-10-08, D7c): la
     IA dice si el comentario pide algo y el código decide; si la IA no lo dijera, preguntaría.
   - Efecto: la aprobación, con quién y el comentario; el código comprueba el cierre (mecánica §5:
     evidencia, aprobación, sin dependencias ni bloqueos) y la tarea pasa a `terminada`, con evento de
     Ismael y auditoría. Dos hechos distintos, un solo acto. El aviso a Marcos sale enseguida.
   - La respuesta dice: que la tarea del PLC quedó terminada; que Marcos se va a enterar ahora, con el
     comentario.
   - Estado después: quedan tres entregas esperando a Ismael.

3. **Leda**, por su cuenta, a Marcos (10:30): el aviso de la aprobación.
   →
   - El mensaje dice: que quedó aprobada y terminada, sin nombrar a Ismael (decisión 11 del
     2026-10-08: el nombre, sólo si Marcos pregunta); la tarea del PLC en su renglón con 📋; el
     comentario que dejó al aprobarla; que no hace falta que responda, solo en el último renglón. Al final, un enlace
     a la página de la tarea, que agrega el código (ADR 0019, decisión 7a).
   - Estado de Marcos después: sin tema abierto.

4. **Ismael** escribe (10:35): "lo de comunicaciones tambien aprobado"
   →
   - Jugadas: `aprobar`, la tarea de comunicaciones.
   - Efecto: la aprobación queda registrada; el código comprueba el cierre y no pasa: la dependencia
     bloqueante sigue abierta (la del switch está en curso). La tarea sigue `en_revision`, esperando que
     se resuelva lo que frena el cierre (`odd/tasks/fase-c.md`, decisión 3). El aviso a Marcos sale
     enseguida.
   - La respuesta dice, con honestidad: que la aprobación quedó anotada pero la tarea todavía no queda
     terminada, porque espera que se termine la del switch de Lucas; el próximo paso: que queda terminada
     sola cuando se termine la del switch, y que les avisa a él y a Marcos.
   - La respuesta no dice: que quedó terminada; que la del switch está atrasada (no lo está); que va a
     tener que volver a aprobarla.
   - Estado después: quedan dos entregas esperando a Ismael.

4b. **Leda**, por su cuenta, a Marcos (10:35): el aviso de la aprobación anotada.
   →
   - El mensaje dice: que Ismael aprobó la tarea de comunicaciones, en su renglón con 📋; que todavía no
     queda terminada porque espera la del switch de Lucas, y que queda terminada sola cuando ésa
     termine; que no hace falta que responda, solo en el último renglón.
   - El mensaje no dice: que quedó terminada.

5. **Ismael** toca (10:39) "Pedir cambios" en el aviso de la entrega de Mariano, el del viernes.
   →
   - Jugadas: `pedir_cambios`, la tarea de Mariano, todavía sin comentario. El botón es un atajo y la
     guarda pasa: el aviso es el vigente, no llegó evidencia nueva desde el viernes (ADR 0018, decisión 2).
   - Efecto: ninguno todavía; la tarea sigue `en_revision`. El toque recibe su señal.
   - La respuesta dice: la tarea de Mariano en su renglón con 📋; una pregunta: qué le falta.
   - La respuesta no dice: que ya le pidió el cambio a Mariano.
   - Botones: ninguno.
   - Estado después: tema abierto, el pedido de cambios de la tarea de Mariano, esperando qué falta.

6. **Ismael** escribe (10:40): "le falta el diagrama del tablero, que lo suba y lo vemos"
   →
   - Jugadas: `pedir_cambios`, la tarea de Mariano, con el comentario "falta el diagrama del tablero":
     contesta la pregunta del tema abierto.
   - Confirmación: ninguna; lo claro va directo.
   - Efecto: el pedido de cambios con su comentario; la tarea vuelve al estado que tenía antes de la
     entrega, `en_curso`, con evento de Ismael y auditoría; el seguimiento de la tarea sigue con su
     vencimiento del viernes 30. El aviso a Mariano sale enseguida.
   - La respuesta dice: que le pidió el cambio a Mariano con su comentario y que Mariano se va a enterar
     ahora; el próximo paso: que la vuelve a recibir cuando Mariano la entregue.
   - La respuesta no dice: que la tarea quedó rechazada o cancelada.
   - Estado después: queda una entrega esperando a Ismael.

7. **Leda**, por su cuenta, a Mariano (10:40): el aviso del pedido de cambios.
   →
   - El mensaje dice: que le pidieron un cambio, sin nombrar a Ismael; la tarea en su renglón con 📋; lo que pidió, con sus
     palabras (falta el diagrama del tablero); que la tarea sigue en curso y vence el vie 30/10; el
     cierre, aparte: que la vuelva a entregar cuando lo tenga. Al final, un enlace a la página de la
     tarea, que agrega el código.
   - El mensaje no dice: que la tarea fue rechazada; un juicio sobre su trabajo.

8. **Ismael** escribe (10:45): "lo de ariel aprobado, pero que revise los colores del grafico de lotes"
   →
   - Jugadas: ninguna que ejecute: mezcla aprobar y pedir un cambio, y admite dos lecturas (ADR 0018,
     decisión 2: "aprobado, pero…" no es una aprobación clara).
   - Efecto: ninguno; la tarea sigue `en_revision`.
   - La respuesta dice: una sola pregunta, cuál de las dos: aprobarla y pasarle el comentario a Ariel, o
     pedirle el cambio primero.
   - Botones: dos, uno por cada lectura (constitución §8: algo con más de una lectura).
   - Estado después: tema abierto, la decisión sobre la tarea de Ariel.

9. **Ismael** escribe (10:46), sin tocar los botones: "aprobala nomas y pasale lo de los colores"
   →
   - Jugadas: `elegir`, la primera lectura: `aprobar`, con el comentario "que revise los colores del
     gráfico de lotes". Escrito vale igual que el botón (situación general 6).
   - Efecto: la aprobación con el comentario; la tarea pasa a `terminada`; el aviso a Ariel sale
     enseguida, con el comentario como algo para mirar, no como un cambio pendiente.
   - La respuesta dice: que la tarea de Ariel quedó terminada y que Ariel se va a enterar ahora, con el
     comentario.
   - Estado después: sin tema abierto; ninguna entrega esperando a Ismael (la de comunicaciones ya tiene
     su aprobación y espera la del switch).

9b. **Leda**, por su cuenta, a Ariel (10:46): el aviso de la aprobación, con el comentario de los
    colores como algo para mirar, no como un cambio pendiente; que no hace falta que responda.

9c. **Leda**, por su cuenta, a Mariano (martes 27, 10:00): el aviso previo de la tarea del tablero, que
    volvió a estar en curso y vence el vie 30/10 (la escalera de siempre).

10. **La tarea del switch de Lucas** queda `terminada` (miércoles 28, 11:00), con su entrega y su
    aprobación, que no son parte de esta conversación.
    →
    - Efecto: el código vuelve a comprobar el cierre de las tareas que esperaban por ella. La de
      comunicaciones ya tiene la aprobación de Ismael, la evidencia completa y nada más que la frene: pasa
      a `terminada` sola, con evento que lleva como origen la aprobación de Ismael del lunes 26, y
      auditoría. Nadie tiene que volver a aprobarla. Los avisos a Marcos y a Ismael salen enseguida.

11. **Leda**, por su cuenta (miércoles 28, 11:00), a Marcos y a Ismael: el aviso del cierre.
    →
    - A Marcos, el mensaje dice: que la tarea de comunicaciones quedó terminada, en su renglón con 📋;
      que la había aprobado el lun 26/10 y faltaba que se terminara la del switch de Lucas, que ya está,
      sin nombrar a Ismael; que no hace falta que responda, solo en el último renglón. Al final, un enlace a la página de
      la tarea, que agrega el código.
    - A Ismael, lo mismo, breve: que la tarea de comunicaciones de Marcos quedó terminada con la
      aprobación que dio el lun 26/10, ahora que se terminó la del switch; que no hace falta que
      responda, solo en el último renglón.
    - El mensaje no dice: que Leda la aprobó o la cerró por su cuenta; que hace falta otra aprobación.
    - Estado de Marcos y de Ismael después: sin tema abierto.

12. **Mariano** manda (miércoles 28, 11:30) una foto con el texto: "ahi va el diagrama del tablero"
    →
    - Jugadas: `entregar`, la tarea del tablero, otra vez, después del pedido de cambios del paso 6.
      Lo que describió su primera entrega ("cableado segun el diagrama y paso continuidad y
      aislacion") sigue contando, salvo lo que el pedido de cambios pidió cambiar (decisión 23 del
      usuario, 2026-10-08, opción A; D8, paso 19 de la prueba por Telegram): la IA lo recibe, con lo
      que pidió Ismael, y juzga lo nuevo junto con eso (`lo_descrito_cubre`).
    - Efecto: ninguno todavía; la vista previa de la entrega nueva, con Confirmar.
    - La respuesta dice: la entrega nueva, una pieza por renglón; que al confirmarla vuelve a
      revisión, sin nombrar a Ismael; el cierre, aparte: si la entrega así.
    - La respuesta no dice: que falta saber si quedó cableado según el diagrama o si pasó continuidad
      y aislación (ya lo dijo en la primera entrega: decisión 10, nunca lo que ya dijo); que la tarea
      quedó entregada o en revisión.
    - Estado de Mariano después: lo mostrado para confirmar.

## Qué mide

- **Garantías:** la aprobación es de quien la política designa, nunca de otro (paso 1) ni de Leda; el
  cierre lo decide el código (pasos 2, 4 y 10), y "aprobado" no es "terminada" cuando falta otra cosa;
  una aprobación que todavía no puede cerrar queda registrada y el código cierra la tarea cuando se
  resuelve lo que faltaba, con aviso al responsable y a quien aprobó (pasos 10 y 11); el botón "Pedir
  cambios" es un atajo que pregunta qué falta, y escribir vale igual (pasos 5 y 6); no hace sin
  confirmación lo que la admite con dos lecturas (paso 8); no inventa (el paso 4 dice qué frena el
  cierre); el responsable se entera de cada decisión, con el comentario.
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA tome "le falta el diagrama del tablero" del paso 6 como otra cosa
  que la respuesta al pedido de cambios, o "aprobado, pero que revise" como una aprobación clara. Tiene que preguntar;
  cerrar la tarea de Ariel sin preguntar, o aprobar la de Mariano por lo que dijo Marcos, es una falla
  de garantía.
