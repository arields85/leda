# 27. La entrega frente al criterio de aceptación

**Qué prueba:** Marcos entrega la tarea del PLC y lo que escribe no dice todo lo que pide su criterio de
aceptación. Leda le dice qué falta, en palabras simples y hablando de la tarea, con un ejemplo sacado
del criterio; le vuelve a dar el ejemplo cuando pregunta qué poner; no la entrega aunque Marcos insista;
y cuando Marcos acepta el ejemplo, la entrega se confirma como siempre. Después retira la foto: Leda le
pide la correcta, la revisión espera (Ismael toca Aprobar y no cambia nada) y, con la foto nueva, a
Ismael le llega un aviso nuevo con todo. Al día siguiente entrega la de comunicaciones, que nunca había
arrancado, describiendo lo que pide su criterio: se recibe sin preguntas y la historia dice que arrancó
y se entregó en ese momento. Decisiones 10, 14 y 15 del usuario (2026-10-08; `odd/tasks/fase-c.md`,
C-3d, unidad D3); constitución §4 y §8 ("lo propone en lugar de sólo pedirlo"); mecánica §3, §5, §6 y
§13; ADR 0009, enmienda T6i; ADR 0019, decisión 5; regla del mozo (`AGENTS.md`, punto 11).

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
     ciclos sin fallas"), para que lo acepte o lo escriba con sus palabras; una sola vez qué falta para
     entregarla, sin repetir que todavía no se entrega o no pasa a revisión (C-3d, D7).
   - La respuesta no dice: que la entregó o que está en revisión; el nombre de Ismael (decisión 11 del
     2026-10-08); que falta que arranque desde el PLC (ya lo dijo); un número o un nombre que no estén en
     el criterio ni en lo que escribió; "contaste" o "contarlo": lo que escribió es su descripción
     (decisión 10; D7).
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
   - Jugadas: `confirmar` (con la tarea del PLC o sin ella): pide que la entrega vaya como está.
   - Efecto: ninguno. Lo descrito no cubre el criterio: la entrega no sale aunque Marcos insista (una foto
     no certifica lo que pide el criterio, y entregarla igual sólo suma una vuelta: un pedido de cambios
     y otra entrega). La tarea sigue `en_curso`. Es la respuesta a la pregunta abierta de Leda, no un
     pedido nuevo: nunca le llega un aviso a la administración, aunque la IA no la lea como ninguna
     jugada (C-3d, D7: con la IA real cayó fuera de la lista 4 de 5; la respuesta que no es una jugada
     la maneja la pregunta abierta, que vuelve con lo que falta y su ejemplo).
   - La respuesta dice: que todavía no la puede pasar a revisión porque falta saber si completó los 20
     ciclos sin fallas; el ejemplo otra vez, como próximo paso.
   - La respuesta no dice: que la entregó; que Ismael se enteró; un reproche.
   - Estado después: tema abierto, la entrega del PLC, esperando lo que falta.

4. **Marcos** escribe (15:05): "si, eso"
   →
   - Jugadas: `entregar`, la tarea del PLC, aceptando el ejemplo (`acepta_el_ejemplo`); lo que cubre
     el texto y lo descrito pueden venir o no (la ficha los declara opcionales; C-3d, D7b).
   - Efecto: el ejemplo pasa a ser lo que describe Marcos, una pieza más, con el punto del criterio que
     dice. La entrega está completa: se guarda la vista previa con su huella. La tarea sigue `en_curso`.
   - La respuesta dice: la tarea del PLC en su renglón con 📋; una pieza por renglón (lo que escribió, la
     foto y lo que aceptó); que al confirmar pasa a revisión; el cierre, aparte: si la entrega así.
   - La respuesta no dice: que el ejemplo lo escribió o lo contó Marcos: es el que aceptó, y la vista
     previa lo muestra así (C-3d, D7). Si el mismo mensaje hubiera contestado también de otra forma
     (que vaya así, dejarla), aceptar no vale y el ejemplo no se suma: son dos lecturas que se excluyen.
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

6. **Leda**, por su cuenta, a Ismael (jueves 22, 15:16, terminado el margen para corregir): el aviso
   de la entrega, con la foto adjunta y los botones "Aprobar" y "Pedir cambios", como en la
   conversación 21. A Marcos, nada.

7. **Marcos** escribe (15:20): "la foto sacala, era de otra maquina"
   →
   - Jugadas: `corregir`, sobre lo entregado: retira la foto.
   - Efecto: se agrega el retiro de la foto; nada se borra. La entrega queda sin la captura que pide
     la política: Leda lo resuelve en el momento (decisión 15 del usuario, 2026-10-08). La tarea sigue
     `en_revision`, pero la revisión espera a que se complete.
   - La respuesta dice: que sacó la foto; que para revisar la tarea falta una foto o una captura de la
     pantalla, y que la revisión espera hasta que esté; el cierre, aparte: que mande la foto correcta.
   - La respuesta no dice: que la tarea dejó de estar entregada o volvió a en curso; el nombre de Ismael.
   - Estado después: tema abierto, lo que falta de la entrega del PLC.

8. **Ismael** toca (15:25) "Aprobar" en el aviso que le llegó a las 15:16.
   →
   - Efecto: ninguno. La entrega se está completando: no se aprueba, y cuando esté completa a Ismael
     le llega un aviso nuevo con todo.
   - La respuesta dice: que Marcos está completando la entrega de la tarea del PLC y que le avisa
     cuando esté completa.
   - La respuesta no dice: que la aprobó o que quedó terminada; qué foto se retiró o por qué.

9. **Marcos** manda (15:30) otra foto, sin texto.
   →
   - Jugadas: `entregar`, la tarea del PLC (con la IA real, 5 de 5 en la ronda D7; el YAML lo espera
     desde la D7b); sin jugada es lo mismo: la foto se suma a la entrega que Leda está esperando.
   - Efecto: con la foto, la entrega queda completa; se guarda la vista previa con su huella.
   - La respuesta dice: que sumó la foto y que con eso la entrega queda completa; el cierre, aparte:
     si la suma así.
   - Botones: los de la confirmación.

10. **Marcos** escribe (15:31): "dale"
    →
    - Jugadas: `confirmar` (con la tarea del PLC o sin ella).
    - Efecto: la foto pasa a ser evidencia; la tarea sigue `en_revision`, sin otro cambio de estado.
      A Ismael le llega un aviso nuevo con todo lo vigente, terminado el margen para corregir (ADR
      0009, enmienda T6i) y cuando pasan 30 minutos desde que tocó "Aprobar" (no interrumpir una
      conversación, la 26): a las 15:55, y eso es lo que dicen los hechos.
    - La respuesta dice: que la entrega quedó completa y sigue en revisión; que le avisa cuando la
      revisen o si hace falta algo más.
    - La respuesta no dice: el nombre de Ismael; que la tarea está terminada o aprobada.

11. **Leda**, por su cuenta, a Ismael (15:55): el aviso nuevo de la entrega, con lo que describió
    Marcos, la foto nueva adjunta y los botones. Nunca la foto retirada.

12. **Marcos** manda (viernes 23, 10:00) una foto con el texto: "lo de comunicaciones ya esta, los equipos
   se comunicaron con el plc por la red de planta una hora sin errores"
   →
   - Jugadas: `entregar`, la tarea de comunicaciones, que nunca se arrancó: se recibe igual, con su
     vista previa y su confirmación (decisión 14 del usuario, 2026-10-08). Lo escrito dice lo que pide
     su criterio: la IA lo juzga y no se pregunta nada.
   - Efecto: ninguno sobre la tarea todavía, que sigue `asignada`. La entrega está completa: se guarda
     la vista previa con su huella.
   - La respuesta dice: la tarea de comunicaciones en su renglón con 📋; una pieza por renglón (lo que
     escribió y la foto); que al confirmar pasa a revisión; el cierre, aparte: si la entrega así.
   - La respuesta no dice: que no figura como arrancada o que tiene que arrancarla antes; qué falta del
     criterio.
   - Botones: los de la confirmación.
   - Estado después: lo último mostrado para confirmar: la entrega con dos piezas.

13. **Marcos** escribe (10:01): "dale"
   →
   - Jugadas: `confirmar` (con la tarea de comunicaciones o sin ella).
   - Efecto, en un solo acto: las dos filas de evidencia; la historia dice que arrancó y se entregó en
     ese momento (de `asignada` a `en_curso` y de ahí a `en_revision`, los dos con la hora de ahora y
     de Marcos, sin una fecha de inicio inventada); auditoría. Nunca `terminada` (mecánica §3). El aviso
     a Ismael queda guardado y sale terminado el margen para corregir.
   - La respuesta dice: que quedó entregada y pasa a revisión; que le avisa cuando la revisen o si hace
     falta algo más.
   - La respuesta no dice: el nombre de Ismael; que la tarea está terminada o aprobada; una fecha de
     inicio anterior a hoy.
   - Estado después: sin tema abierto, nada mostrado para confirmar.

## Qué mide

- **Garantías:** no pasa a revisión lo que no dice el criterio, aunque la persona insista; el ejemplo
  cuenta como lo descrito sólo si la persona lo acepta; el ejemplo no inventa datos (lo verifica el
  código); no deja sin salida (cada respuesta dice qué falta y cómo describirlo); "la terminé" lleva a
  revisión, nunca a terminada, aunque la tarea no figure como arrancada, y no inventa una fecha de
  inicio; mientras a una entrega le falta lo que se retiró, nadie la aprueba ni le llega un aviso de
  ella; nada se borra.
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA dé por cubierto el criterio con "ya arranca desde el plc", que lea
  "y que pongo?" como una descripción, que lea "no, asi esta, mandala" como la aceptación del ejemplo o
  "si, eso" como una confirmación. Preguntar lo que Marcos ya dijo es una falla de la redacción.
