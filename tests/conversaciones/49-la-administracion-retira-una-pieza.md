# 49. La administración retira una pieza de una entrega

**Estado:** corre en seco; falta la ronda con la IA real.

**Qué prueba:** Marcos entrega la tarea del PLC con lo que escribió y una foto, y la entrega le llega
a Ismael. Después la administración retira la foto por la consola, porque en ella se ve la clave del
PLC. La pieza queda retirada y su contenido se borra de verdad, pero la pieza sigue, con su huella
(decisión 57). Leda les avisa a Marcos, con el motivo, y a Ismael, sin el motivo (decisiones 58 y
60). Cuando Ismael toca Aprobar, no cambia nada, y la cocina le pasa a la IA que la pieza que falta
la retiró la administración, no Marcos (constitución §4; la regla del mozo, `AGENTS.md`, punto 11).
Nadie nombra a quien la retiró (decisión 59). `odd/tasks/fase-c.md`, decisiones 57 a 60.

## La regla

1. **Lo que retira la administración se borra de verdad** (decisión 57): el contenido del archivo
   se vacía y la pieza queda, con su huella, retirada. No es un borrado de la fila.
2. **Deja de contar, y Leda avisa** (decisión 58): a quien la entregó, que la administración retiró
   esa pieza, con el motivo, y lo que hace falta para que la revisen; a quien la revisa, si ya le
   llegó la entrega (decisión 60), que la entrega espera esa pieza nueva, sin el motivo.
3. **Quién la retiró no se dice** (decisión 59): ni a Marcos ni a Ismael.
4. **Aprobar mientras falta la pieza no cambia nada**, y lo que se le dice a quien aprueba es
   cierto: la pieza la retiró la administración (`la_entrega_espera_lo_que_retiro_la_administracion`),
   no la persona responsable (`la_entrega_se_esta_completando`, la de la 27).

## Estado inicial

- **Día:** D = jueves 22 de octubre, dentro del horario.
- **Personas:** Marcos (de OT; su trabajo lo aprueba Ismael) e Ismael. Ninguno tiene una pregunta
  de Leda abierta.
- **Tareas:** "Programar PLC de la comprimidora", de Marcos, `en_curso` desde el lunes 19, vence el
  viernes 23. Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin
  fallas".
- **Política de evidencia de OT:** cómo quedó (`explicacion`) y una foto o una captura de la
  pantalla (`captura`).
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Marcos** escribe (10:00), con una foto: "termine el plc, la comprimidora arranco desde el plc y
   completo los 20 ciclos sin fallas"
   →
   - Jugadas: `entregar`, con lo escrito como la explicación y el punto del criterio.
   - Efecto: ninguno todavía.
   - La respuesta dice: la vista previa de la entrega (lo que escribió y la foto) y pregunta si la
     confirma. Botón: "Confirmar".

2. **Marcos** escribe (10:01): "dale"
   →
   - Jugadas: `confirmar`.
   - Efecto: la tarea en revisión, con sus dos piezas, y el aviso a Ismael guardado para terminado
     el margen para corregir.
   - La respuesta dice: que la entregó y que Ismael la revisa.

3. **Leda** (10:11) le escribe a **Ismael**: que Marcos entregó la tarea del PLC, con lo que
   escribió y la foto adjunta. Botones: "Aprobar" y "Pedir cambios".

4. **La administración** (10:45) retira la foto por la consola: "en la foto se ve la clave del PLC".
   →
   - Efecto: la foto queda retirada; la pieza sigue y el contenido de su archivo se borra. Se
     guardan los dos avisos: a Marcos y a Ismael.

5. **Leda** (10:45):
   - A **Marcos**: que la administración retiró la foto de la entrega del PLC, que entregó hoy, con
     el motivo, y que hace falta otra para que la revisen. No hace falta contestar. El día de la
     foto es el de la entrega en el reloj de Leda (el del aviso a Ismael), no el que guardó la
     base.
   - A **Ismael**: que la entrega del PLC espera una pieza nueva de Marcos y que le avisa cuando
     esté completa. Sin el motivo. No hace falta contestar.
   - A ninguno: quién de la administración la retiró.

6. **Ismael** toca "Aprobar" en el aviso del paso 3 (11:00).
   →
   - Efecto: ninguno; ni aprobación ni cambio de estado.
   - La respuesta dice: que la entrega del PLC espera una pieza nueva, porque la administración
     retiró una, y que le avisa cuando esté completa.
   - La respuesta no dice: que la aprobó; que Marcos sacó algo; quién la retiró ni el motivo.

## Qué mide

- **Garantías:** el retiro deja la pieza y borra su contenido (paso 4); la pieza retirada deja de
  contar y aprobar no cambia nada (paso 6); los dos avisos salen una vez, a quien corresponde (paso
  5); a Ismael, sin el motivo; ningún mensaje nombra a quien retiró la foto.
- **Comprensión:** la IA elige `entregar` y `confirmar` como en la 27. Lo demás no depende de la
  IA: lo hacen la consola y el botón.
- **Las palabras:** lo que la IA dice del retiro sale de la cocina: a Ismael, que la retiró la
  administración y que espera la pieza nueva; nunca que la sacó Marcos (constitución §4); sin
  nombres del sistema (constitución §10); todo mensaje con su próximo paso, y los avisos, con que no
  hace falta contestar.
- **El formato:** el de la conversación 20 en cada mensaje.
