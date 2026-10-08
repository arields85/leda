# 27. La entrega frente al criterio de aceptación

**Qué prueba:** Marcos entrega la tarea del PLC y lo que escribe no dice todo lo que pide su criterio de
aceptación. Leda le dice qué falta, en palabras simples y hablando de la tarea, con un ejemplo sacado
del criterio; le vuelve a dar el ejemplo cuando pregunta qué poner; no la entrega aunque Marcos insista;
y cuando Marcos acepta el ejemplo, la entrega se confirma como siempre. Decisión 10 del usuario
(2026-10-08; `odd/tasks/fase-c.md`, C-3d, unidad D3); constitución §4 y §8 ("lo propone en lugar de
sólo pedirlo"); mecánica §5, §6 y §13; ADR 0019, decisión 5; regla del mozo (`AGENTS.md`, punto 11).

**Comparar es leer; decidir es del código.** La IA que elige la jugada juzga, punto por punto del
criterio, si lo que Marcos describe lo dice (`lo_descrito_cubre`), y escribe el ejemplo (`ejemplo`).
El código decide qué falta y si se ofrece Confirmar, y verifica que el ejemplo no traiga un número ni un
nombre que no estén en el criterio, en la tarea o en lo que Marcos escribió.

**Corre desde la unidad D3 de la C-3d**, con su YAML.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": área OT; la aprueba Ismael; vence el viernes 23; `en_curso` desde
    el lunes 19; sin bloqueos ni dependencias.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": área OT; la aprueba Ismael; vence el viernes
    30; `asignada`; sin bloqueos ni dependencias.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Lo que pide la política de OT en esta conversación:** una explicación (texto) y una captura (imagen).
  Más corta que la del pack, para mirar sólo el criterio.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos ni a Ismael en la semana.

## Hilo

1. **Marcos** manda (jueves 22, 15:00) una foto de la pantalla con el texto: "termine el plc, ya arranca
   desde el plc"
   →
   - Jugadas: `entregar`, la tarea del PLC. La IA juzga que lo escrito no dice todo el criterio (que
     arranca desde el PLC sí, pero no que completó los 20 ciclos sin fallas) y propone un ejemplo con las
     palabras del criterio.
   - Efecto: ninguno sobre la tarea, que sigue `en_curso`. La política está completa (el texto y la
     foto), pero lo descrito no cubre el criterio: no hay vista previa para confirmar.
   - La respuesta dice: que para revisar la tarea falta saber si la comprimidora completó los 20 ciclos
     sin fallas, en palabras simples y hablando de la tarea; el ejemplo ("La comprimidora completó los 20
     ciclos sin fallas"), para que lo acepte o lo escriba con sus palabras.
   - La respuesta no dice: que la entregó o que está en revisión; el nombre de Ismael (decisión 11 del
     2026-10-08); que falta que arranque desde el PLC (ya lo dijo); un número o un nombre que no estén en
     el criterio ni en lo que escribió.
   - Botones: ninguno: no hay nada para confirmar.
   - Estado después: tema abierto, la entrega del PLC, esperando lo que falta.

2. **Marcos** escribe (15:02): "y que pongo?"
   →
   - Jugadas: ninguna. Es una pregunta sobre lo que Leda le pidió: la pregunta abierta vuelve con su
     ejemplo.
   - Efecto: ninguno.
   - La respuesta dice: el ejemplo, para que lo acepte tal cual o lo escriba con sus palabras.
   - La respuesta no dice: que la entregó; un dato inventado.
   - Estado después: tema abierto, la entrega del PLC, esperando lo que falta.

3. **Marcos** escribe (15:03): "no, asi esta, mandala"
   →
   - Jugadas: `confirmar` (con la tarea del PLC o sin ella).
   - Efecto: ninguno. Lo descrito no cubre el criterio: la entrega no sale aunque Marcos insista (una foto
     no certifica lo que pide el criterio, y entregarla igual sólo suma una vuelta: un pedido de cambios
     y otra entrega). La tarea sigue `en_curso`.
   - La respuesta dice: que todavía no la puede pasar a revisión porque falta saber si completó los 20
     ciclos sin fallas; el ejemplo otra vez, como próximo paso.
   - La respuesta no dice: que la entregó; que Ismael se enteró; un reproche.
   - Estado después: tema abierto, la entrega del PLC, esperando lo que falta.

4. **Marcos** escribe (15:05): "si, eso"
   →
   - Jugadas: `entregar`, la tarea del PLC, aceptando el ejemplo (`acepta_el_ejemplo`).
   - Efecto: el ejemplo pasa a ser lo que describe Marcos, una pieza más, con el punto del criterio que
     dice. La entrega está completa: se guarda la vista previa con su huella. La tarea sigue `en_curso`.
   - La respuesta dice: la tarea del PLC en su renglón con 📋; una pieza por renglón (lo que escribió, la
     foto y lo que aceptó); que al confirmar pasa a revisión; el cierre, aparte: si la entrega así.
   - Botones: los de la confirmación.
   - Estado después: lo último mostrado para confirmar: la entrega con tres piezas.

5. **Marcos** toca (15:06) "Confirmar".
   →
   - Efecto, en un solo acto: las tres filas de evidencia (el texto aceptado guarda el punto del
     criterio que describe) y el paso de `en_curso` a `en_revision`, con evento de Marcos y auditoría.
     El aviso a Ismael queda guardado y sale terminado el margen para corregir, a las 15:16.
   - La respuesta dice: que quedó entregada y pasa a revisión; que le avisa cuando la revisen o si hace
     falta algo más.
   - La respuesta no dice: el nombre de Ismael; que la tarea está terminada o aprobada.
   - Estado después: sin tema abierto, nada mostrado para confirmar.

## Qué mide

- **Garantías:** no pasa a revisión lo que no dice el criterio, aunque la persona insista; el ejemplo
  cuenta como lo descrito sólo si la persona lo acepta; el ejemplo no inventa datos (lo verifica el
  código); no deja sin salida (cada respuesta dice qué falta y cómo describirlo).
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA dé por cubierto el criterio con "ya arranca desde el plc", que lea
  "y que pongo?" como una descripción, que lea "no, asi esta, mandala" como la aceptación del ejemplo o
  "si, eso" como una confirmación. Preguntar lo que Marcos ya dijo es una falla de la redacción.
