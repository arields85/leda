# 45. El resumen para cualquiera, el detalle a pedido

**Qué prueba:** una persona pide el enlace de una tarea que no le toca ver. Leda nunca le contesta
que no la puede ver ni la deja sin un próximo paso: le da el resumen (qué tarea, de quién, para
cuándo y cómo quedó), que cualquiera del equipo puede saber, y le ofrece pedirle el detalle (fotos,
archivos, correcciones pedidas) al encargado del sector de la tarea. Si la persona dice que sí, Leda
le pregunta al encargado si se la comparte; si dice que sí, a la persona le llega el enlace, y desde
entonces lo puede pedir como cualquiera que la ve; si dice que no, se lo cuenta (decisión 39: todos
saben cómo se cerró). Varias tareas que coinciden siguen la regla de siempre: Leda las nombra y la
persona contesta. Decisión 33 del usuario (2026-10-09; `odd/tasks/fase-c.md`); ADR 0019, decisión
7b (quién ve el detalle, igual); decisión 52 (un nombre mal escrito, como está).

## La regla

1. **El resumen lo ve cualquiera del equipo** (la jugada `pedir_enlace`, con la tarea nombrada como
   la dijo): la tarea, quién la tiene, cómo quedó y cuándo vence. Nunca el detalle ni el enlace, y
   nunca "no la podés ver".
2. **El detalle lo comparte el encargado del sector de la tarea** (el referente de su área): Leda
   dice qué sector lo ve y a quién se lo puede pedir, y se lo ofrece. Es una propuesta: un tema
   abierto como cualquier otro.
3. **Pedirlo es una jugada** (`pedir_el_detalle`): Leda le pregunta al encargado, como Leda,
   terminado el margen para corregir, con dos botones (o escrito: `contestar_el_pedido_del_detalle`).
4. **Compartirla queda escrito por persona y por tarea**, con quién la compartió y cuándo, auditado
   y revocable; la base lo cuenta al decidir quién ve la página, y el enlace se emite al mandar.

## Estado inicial

- **Día:** D = lunes 26 de octubre, dentro del horario.
- **Personas:** Nahuel (de OT; su trabajo lo aprueba Marcos), Lucas (de Infraestructura IT; su
  trabajo lo aprueba Martín), Martín (referente de Infraestructura IT: el encargado del sector),
  Mariano (referente de Sistemas eléctricos) y Ariel (referente de Software). Ninguno tiene una
  pregunta de Leda abierta.
- **Tareas:**
  - "Configurar el switch de la planta", de Lucas, `en_curso` desde el lunes 19, vence el viernes
    30. Criterio de aceptación: "El switch de la planta da red a las doce máquinas de la línea y
    responde al monitoreo".
  - "Instalar el servidor de la planta", de Lucas, `en_curso` desde el lunes 19, vence el viernes 6
    de noviembre. Criterio de aceptación: "El servidor queda en el rack de la planta, con su
    respaldo diario funcionando y probado una vez".
  - "Calibrar el sensor de la envasadora", de Mariano, asignada, vence el viernes 30. Criterio de
    aceptación: "El sensor de la envasadora mide dentro de la tolerancia del fabricante en una
    prueba de una hora".
  - "Cambiar el sensor de la paila", de Ariel, asignada, vence el viernes 30. Criterio de
    aceptación: "El sensor nuevo de la paila queda conectado y el panel muestra su lectura".
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Nahuel** escribe (10:00): "pasame el link de la tarea del switch"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo.
   - Efecto: ninguno; ningún enlace.
   - La respuesta dice: el resumen (la del switch, de Lucas, en curso, vence el vie 30/10); que el
     detalle con fotos y correcciones lo ve Infraestructura IT y que, si lo necesita, le pregunta a
     Martín.
   - La respuesta no dice: que no la puede ver; nombres de la base, de funciones o de permisos.
   - Estado después: la propuesta abierta.

2. **Nahuel** escribe (10:02): "si dale"
   →
   - Jugadas: `pedir_el_detalle`.
   - Efecto: el pedido del detalle, y la pregunta a Martín guardada para dentro de diez minutos.
   - La respuesta dice: que le pregunta a Martín y le avisa cuando conteste.
   - La respuesta no dice: que ya se la compartieron.

3. **Leda** (10:12) le escribe a **Martín**: que Nahuel pide ver el detalle de la del switch, de
   Lucas; si se la comparte. Botones: "Compartirla" y "No compartirla".

4. **Martín** toca "Compartirla" (10:30).
   →
   - Efecto: la tarea queda compartida con Nahuel, por Martín; el aviso a Nahuel, guardado.
   - La respuesta dice: que se la comparte y que Nahuel se va a enterar.

5. **Leda** (10:40) le escribe a **Nahuel**: que Martín le compartió la del switch. Al final, el
   enlace personal a la página (lo agrega el código).

6. **Nahuel** escribe (11:00): "pasame de nuevo el link del switch"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo.
   - Efecto: ninguno.
   - La respuesta dice: que ahí va el enlace; al final, el enlace.

7. **Nahuel** escribe (11:05): "y el del servidor de lucas?"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo.
   - La respuesta dice: el resumen del servidor (de Lucas, en curso, vence el vie 6/11); que el
     detalle lo ve Infraestructura IT y que, si lo necesita, le pregunta a Martín. Sin enlace.

8. **Nahuel** escribe (11:06): "si porfa"
   →
   - Jugadas: `pedir_el_detalle`.
   - Efecto: la pregunta a Martín, guardada.

9. **Leda** (11:16) le escribe a **Martín**: que Nahuel pide ver el detalle del servidor; si se la
   comparte, con los dos botones.

10. **Martín** escribe (11:30): "ese no, en las fotos se ven las claves del rack"
    →
    - Jugadas: `contestar_el_pedido_del_detalle`, la del servidor, que no.
    - Efecto: nada compartido; el aviso a Nahuel, guardado.
    - La respuesta dice: que no se la comparte y que Nahuel se va a enterar.

11. **Leda** (11:40) le escribe a **Nahuel**: que Martín no le compartió el detalle del servidor; el
    resumen lo sigue pudiendo pedir. Sin enlace.

12. **Nahuel** escribe (12:00): "y el link del sensor?"
    →
    - Jugadas: `pedir_enlace`, nombrada por cómo la dijo.
    - Efecto: ninguno.
    - La respuesta dice: que hay dos tareas con ese nombre (la de la envasadora, de Mariano, y la de
      la paila, de Ariel) y pregunta cuál.

## Qué mide

- **Garantías:** el enlace sale sólo para quien puede ver la tarea, también por haberla
  compartido el encargado (pasos 5 y 6), y nunca antes de que lo comparta ni si dice que no (pasos
  1, 7 y 11); nada queda compartido sin la decisión del encargado (pasos 2 y 10); ningún efecto en
  las tareas; la IA nunca escribe una dirección.
- **Comprensión:** la IA elige `pedir_enlace` con la tarea por cómo la dijo, `pedir_el_detalle`
  cuando Nahuel acepta lo que Leda le ofreció, y `contestar_el_pedido_del_detalle` con lo que dice
  Martín.
- **Las palabras:** nunca "no la podés ver"; sin nombres del sistema (constitución §10); todo
  mensaje con su próximo paso.
- **El formato:** el de la conversación 20 en cada mensaje.
