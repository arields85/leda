# 33. Ya hablé con él

**Qué prueba:** Leda le preguntó a Ariel para cuándo destraba la tarea de Marcos, y Ariel contesta que
ya lo habló con Marcos. Leda no da eso por suficiente: le pregunta qué arreglaron y para cuándo lo
destraba, para que quede asentado. Con la respuesta queda anotado, como un hecho del bloqueo, lo que
arreglaron y para cuándo, y a Marcos le llega un aviso informativo con eso. Si Ariel dice todo junto
("ya lo hablé, la libero el viernes"), queda anotado directo, sin preguntar. Decisión 4 del usuario
(`odd/tasks/fase-c.md`, 2026-10-08, opción A), segunda mitad; ADR 0017, decisión 3a; ADR 0018, 9c.

**Corre desde la porción 2 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **Si quien destraba dice que ya habló con el trabado, Leda le pregunta qué arreglaron y para cuándo
   lo destraba, para que quede asentado.**

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **"Ya lo hablé" solo no se anota todavía:** lo que queda asentado es lo que arreglaron y para cuándo.
  La pregunta de Leda sigue abierta, con su espera (la escalera de las preguntas la repite si no
  contesta, sin escalar), y recuerda que ya lo hablaron.
- **Se pregunta una vez.** Si la respuesta trae lo que arreglaron sin una fecha, queda anotado así; no
  se vuelve a preguntar.
- **A Marcos le llega lo arreglado como información,** con el margen para corregir, como todo lo que
  dice quien destraba (conversación 32). Un "ya lo hablé" no cierra el bloqueo: lo cierra Marcos.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos** (referente Ismael):
  - "Programar PLC de la comprimidora": vence el viernes 30; `en_curso` desde el lunes 19; sin
    bloqueos. Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin
    fallas".
  - "Instalar el panel HMI de la comprimidora": vence el viernes 6 de noviembre; `en_curso` desde el
    lunes 19; sin bloqueos. Criterio de aceptación: "El panel HMI muestra el estado de la comprimidora
    y permite arrancarla y pararla desde la planta".
- **Ariel De Simone** (Software e interfaz HMI) tiene un chat con Leda y ninguna tarea en esta
  conversación.
- **Estado de la conversación** de Marcos y de Ariel: sin tema abierto, nada para después, nada
  mostrado para confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Marcos** escribe (martes 20, 10:20): "estoy trabado con el plc me falta la ip del servidor de
   corelabs"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con su causa.
   - Efecto: un bloqueo abierto en la tarea del PLC, con su causa; la tarea pasa a `bloqueada`.
   - La respuesta dice: que quedó anotado el bloqueo; una sola pregunta: quién lo puede destrabar.
   - Estado después: tema abierto, quién destraba el PLC.

2. **Marcos** escribe (martes 20, 10:22): "me la tiene q pasar ariel"
   →
   - Jugadas: `anotar_quien_destraba`, con Ariel.
   - Efecto: queda anotado que lo destraba Ariel; se guarda el mensaje a Ariel, que sale a las 10:32.
   - La respuesta dice: que quedó anotado; que Leda le pregunta a Ariel y le avisa apenas sepa algo.

3. **Leda**, por su cuenta, a Ariel (martes 20, 10:32): la pregunta.
   →
   - Efecto: un mensaje privado a Ariel; una pregunta abierta de Ariel sobre la tarea del PLC, con su
     espera.
   - El mensaje dice: que Marcos está trabado con la tarea del PLC; lo que le falta; para cuándo se la
     puede pasar.

4. **Ariel** escribe (martes 20, 11:05): "si ya lo hable con marcos"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, diciendo que ya lo habló con Marcos.
   - Efecto: ninguno anotado todavía: la pregunta de Ariel sigue abierta, con su espera, y ahora
     recuerda que ya lo hablaron. Ningún aviso a Marcos.
   - La respuesta dice: una sola pregunta: qué arreglaron y para cuándo se la pasa.
   - La respuesta no dice: que quedó anotado; que Marcos se va a enterar; un reproche.
   - Estado después (Ariel): tema abierto, para cuándo destraba la tarea del PLC.

5. **Ariel** escribe (martes 20, 11:08): "quedamos q se la paso el jueves temprano"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el jueves 22, con sus palabras.
   - Efecto: queda anotado, como un hecho del bloqueo, lo que arreglaron: para el jueves 22, con sus
     palabras, atribuido a Ariel; su pregunta y su espera se cierran. Se guarda el aviso a Marcos, que
     sale terminado el margen para corregir (11:18). El bloqueo sigue abierto.
   - La respuesta dice: que quedó anotado lo que arreglaron; que Marcos se va a enterar.
   - La respuesta no dice: que el bloqueo se cerró.
   - Estado después (Ariel): sin tema abierto.

6. **Leda**, por su cuenta, a Marcos (martes 20, 11:18): lo que arreglaron.
   →
   - Efecto: un mensaje privado a Marcos, informativo.
   - El mensaje dice: la tarea del PLC; que quedó asentado lo que arreglaron con Ariel: que le pasa la
     IP el jueves (jue 22/10) temprano; que cuando pueda seguir, lo diga; que no hace falta responder.
   - El mensaje no dice: que la tarea se destrabó.

7. **Marcos** escribe (martes 20, 14:00): "el panel hmi tambien esta parado, ariel tiene q liberar la
   licencia"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del panel HMI, con su causa, y `anotar_quien_destraba`,
     con Ariel.
   - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Ariel, que sale a las 14:10.
   - La respuesta dice: que quedó anotado; que le pregunta a Ariel y le avisa apenas sepa algo.

8. **Leda**, por su cuenta, a Ariel (martes 20, 14:10): la pregunta por el panel HMI.
   →
   - Efecto: un mensaje privado a Ariel; una pregunta abierta de Ariel sobre la tarea del panel HMI.

9. **Ariel** escribe (martes 20, 14:30): "si ya lo hablamos con marcos, la libero el viernes"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del panel HMI, para el viernes 23, diciendo que
     ya lo habló con Marcos.
   - Efecto: queda anotado directo, sin preguntar: para el viernes 23, atribuido a Ariel; su pregunta y
     su espera se cierran. Se guarda el aviso a Marcos, que sale a las 14:40.
   - La respuesta dice: que quedó anotado; que Marcos se va a enterar.
   - La respuesta no dice: una pregunta por lo que arreglaron.

10. **Leda**, por su cuenta, a Marcos (martes 20, 14:40): lo que arreglaron del panel HMI.
    →
    - Efecto: un mensaje privado a Marcos, informativo.
    - El mensaje dice: la tarea del panel HMI; que quedó asentado lo que arreglaron con Ariel: que
      libera la licencia el viernes (vie 23/10); que no hace falta responder.

## Qué mide

- **Garantías (5b):** no anota una fecha que nadie dio; no da por arreglado algo que quien destraba no
  contó; no da por cerrado un bloqueo; no le avisa a Marcos lo que todavía no quedó asentado; no
  pregunta dos veces lo que ya le dijeron.
- **Falla de comprensión:** que la IA no tome "si ya lo hable con marcos" como lo que dice quien
  destraba, diciendo que ya lo habló, o que tome "quedamos q se la paso el jueves temprano" como otra
  cosa que la fecha que destraba.
