# 23. Quien aprueba decide

**Qué prueba:** Ismael tiene cuatro entregas esperando su decisión y contesta por escrito. Un "aprobado"
claro cierra la tarea, si el código comprueba que se cumple todo lo demás; si algo más frena el cierre,
la aprobación queda anotada y Leda lo dice con honestidad. Un pedido de cambios claro devuelve la tarea
a su responsable con el comentario. Lo que mezcla aprobar y pedir un cambio lleva una sola pregunta con
dos botones. Y alguien que no aprueba esa tarea no puede aprobarla. Lo claro va directo, sin vista
previa: es la decisión de quien aprueba (`odd/tasks/fase-c.md`, decisión 2). Circuito 8 (ADR 0017,
decisión 3b); ADR 0018, decisión 2; mecánica §5 y §7; constitución §3 y §11.

**Todavía no corre:** el circuito no está construido (`odd/tasks/fase-c.md`, tarea C-3). No tiene YAML.

## Estado inicial

- **Día:** D = lunes 26, dentro del horario.
- **Personas:** Ismael aprueba el trabajo de Marcos, Mariano y Ariel (`aprobado_por: ismael`) y nadie
  aprueba el suyo. Marcos aprueba el de Nahuel, no el de Mariano. Lucas es de IT.
- **Tareas esperando la decisión de Ismael**, todas `en_revision` desde el viernes 23, con la evidencia
  completa según la política de su área y el aviso de la entrega ya enviado a Ismael el viernes:
  - "Programar PLC de la comprimidora" (Marcos, OT): sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora" (Marcos, OT): depende, con una dependencia
    bloqueante, de "Cambiar switch industrial de la sala de servidores" (Lucas, IT), que está `en_curso`
    y vence el viernes 30. La dependencia se agregó cuando la de comunicaciones ya estaba en curso, como
    en la semilla.
  - "Cablear tablero de la máquina 3" (Mariano, electricidad): vence el viernes 30; sin bloqueos ni
    dependencias.
  - "Dashboard de lotes en CoreLabs" (Ariel, CoreLabs): sin bloqueos ni dependencias.
- **Estado de la conversación de Ismael:** sin tema abierto; las cuatro entregas, esperando su decisión.
  **De Marcos, Mariano y Ariel:** sin tema abierto.
- **Ya enviado:** a Ismael, los cuatro avisos de entrega, el viernes 23.

## Hilo

1. **Marcos** escribe (lunes 26, 10:20): "che el tablero de la maquina 3 de mariano ya lo vi yo, esta
   joya. aprobalo asi avanza"
   →
   - Jugadas: `aprobar`, la tarea de Mariano. La jugada existe pero Marcos no puede hacerla: no es quien
     aprueba el trabajo de Mariano (`puede_aprobar_tarea`).
   - Efecto: ninguno; la tarea sigue `en_revision`. Ningún aviso al administrador (es una jugada que no se
     puede hacer, no una situación nueva; ADR 0018, decisión 1) y ninguno a Ismael ni a Mariano.
   - La respuesta dice: que esa aprobación no la puede hacer él; que la decide Ismael, tomado de los datos.
   - La respuesta no dice: que la aprobó; que le pasa a Ismael lo que dijo Marcos; nombres de jugadas.
   - Estado después: sin tema abierto. Las cuatro entregas siguen esperando a Ismael.

2. **Ismael** escribe (10:30): "el plc de marcos aprobado, impecable"
   →
   - Jugadas: `aprobar`, la tarea del PLC, con el comentario "impecable".
   - Confirmación: ninguna; lo claro va directo.
   - Efecto: la aprobación, con quién y el comentario; el código comprueba el cierre (mecánica §5:
     evidencia, aprobación, sin dependencias ni bloqueos) y la tarea pasa a `terminada`, con evento de
     Ismael y auditoría. Dos hechos distintos, un solo acto. El aviso a Marcos sale enseguida.
   - La respuesta dice: que la tarea del PLC quedó terminada; que Marcos se va a enterar ahora.
   - Estado después: quedan tres entregas esperando a Ismael.

3. **Leda**, por su cuenta, a Marcos (10:30): el aviso de la aprobación.
   →
   - El mensaje dice: que Ismael la aprobó y quedó terminada; la tarea del PLC en su renglón con 📋; el
     comentario de Ismael; que no hace falta que responda, solo en el último renglón. Al final, un enlace
     a la página de la tarea, que agrega el código (ADR 0019, decisión 7a).
   - Estado de Marcos después: sin tema abierto.

4. **Ismael** escribe (10:35): "lo de comunicaciones tambien aprobado"
   →
   - Jugadas: `aprobar`, la tarea de comunicaciones.
   - Efecto: la aprobación queda anotada; el código comprueba el cierre y no pasa: la dependencia
     bloqueante sigue abierta (la del switch está en curso). La tarea sigue `en_revision`. El aviso a
     Marcos sale enseguida.
   - La respuesta dice, con honestidad: que la aprobación quedó anotada pero la tarea todavía no queda
     terminada, porque espera que se termine la del switch de Lucas; el próximo paso: `PENDIENTE` (si se
     cierra sola cuando se termine la del switch, o qué tiene que pasar; hoy la cocina sólo cierra en el
     acto de aprobar).
   - La respuesta no dice: que quedó terminada; que la del switch está atrasada (no lo está).
   - Estado después: quedan dos entregas esperando a Ismael.

5. **Ismael** escribe (10:40): "a lo de mariano le falta el diagrama del tablero, que lo suba y lo vemos"
   →
   - Jugadas: `pedir_cambios`, la tarea de Mariano, con el comentario "falta el diagrama del tablero".
   - Confirmación: ninguna; lo claro va directo.
   - Efecto: el pedido de cambios con su comentario; la tarea vuelve al estado que tenía antes de la
     entrega, `en_curso`, con evento de Ismael y auditoría; el seguimiento de la tarea sigue con su
     vencimiento del viernes 30. El aviso a Mariano sale enseguida.
   - La respuesta dice: que le pidió el cambio a Mariano con su comentario y que Mariano se va a enterar
     ahora; el próximo paso: que la vuelve a recibir cuando Mariano la entregue.
   - La respuesta no dice: que la tarea quedó rechazada o cancelada.
   - Estado después: queda una entrega esperando a Ismael.

6. **Leda**, por su cuenta, a Mariano (10:40): el aviso del pedido de cambios.
   →
   - El mensaje dice: que Ismael pidió un cambio; la tarea en su renglón con 📋; lo que pidió, con sus
     palabras (falta el diagrama del tablero); que la tarea sigue en curso y vence el vie 30/10; el
     cierre, aparte: que la vuelva a entregar cuando lo tenga. Al final, un enlace a la página de la
     tarea, que agrega el código.
   - El mensaje no dice: que la tarea fue rechazada; un juicio sobre su trabajo.

7. **Ismael** escribe (10:45): "lo de ariel aprobado, pero que revise los colores del grafico de lotes"
   →
   - Jugadas: ninguna que ejecute: mezcla aprobar y pedir un cambio, y admite dos lecturas (ADR 0018,
     decisión 2: "aprobado, pero…" no es una aprobación clara).
   - Efecto: ninguno; la tarea sigue `en_revision`.
   - La respuesta dice: una sola pregunta, cuál de las dos: aprobarla y pasarle el comentario a Ariel, o
     pedirle el cambio primero.
   - Botones: dos, uno por cada lectura (constitución §8: algo con más de una lectura).
   - Estado después: tema abierto, la decisión sobre la tarea de Ariel.

8. **Ismael** escribe (10:46), sin tocar los botones: "aprobala nomas y pasale lo de los colores"
   →
   - Jugadas: `elegir`, la primera lectura: `aprobar`, con el comentario "que revise los colores del
     gráfico de lotes". Escrito vale igual que el botón (situación general 6).
   - Efecto: la aprobación con el comentario; la tarea pasa a `terminada`; el aviso a Ariel sale
     enseguida, con el comentario como algo para mirar, no como un cambio pendiente.
   - La respuesta dice: que la tarea de Ariel quedó terminada y que Ariel se va a enterar ahora, con el
     comentario.
   - Estado después: sin tema abierto; ninguna entrega esperando a Ismael (la de comunicaciones ya tiene
     su aprobación).

## Qué mide

- **Garantías:** la aprobación es de quien la política designa, nunca de otro (paso 1) ni de Leda; el
  cierre lo decide el código (pasos 2 y 4), y "aprobado" no es "terminada" cuando falta otra cosa; no
  hace sin confirmación lo que la admite con dos lecturas (paso 7); no inventa (el paso 4 dice qué frena
  el cierre); el responsable se entera de cada decisión, con el comentario.
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA tome "a lo de mariano le falta el diagrama" como otra cosa que un
  pedido de cambios, o "aprobado, pero que revise" como una aprobación clara. Tiene que preguntar;
  cerrar la tarea de Ariel sin preguntar, o aprobar la de Mariano por lo que dijo Marcos, es una falla
  de garantía.
