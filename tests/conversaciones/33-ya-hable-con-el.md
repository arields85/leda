# 33. Ya hablé con él

**Qué prueba:** Leda le preguntó a Ariel para cuándo destraba la tarea de Marcos, y Ariel contesta que
ya lo habló con Marcos. Leda no da eso por suficiente: le pregunta qué arreglaron y para cuándo lo
destraba, para que quede asentado, y le pregunta lo mismo a Marcos; vale lo que conteste el primero.
Con la respuesta queda anotado, como un hecho del bloqueo, lo que arreglaron y para cuándo, y Leda se
lo confirma al otro: si es así, no tiene que hacer nada; si no es lo que entendió, que avise y Leda se
lo pasa. Si corrige, Leda le lleva la corrección al primero y el tema queda cerrado para los dos. Si
Ariel dice todo junto ("ya lo hablé, la libero el viernes"), queda anotado directo, sin preguntar.
Decisión 4 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción A), segunda mitad; decisiones 47
y 48 (2026-10-09), con la 39; ADR 0017, decisión 3a; ADR 0018, 9c.

**Corre desde la porción 2 de la C-5** (`odd/tasks/fase-c.md`), entera, con su YAML; desde la C-5c,
con lo acordado que se confirma (decisión 47) y la pregunta a los dos (decisión 48).

## La regla (decidida por el usuario, 2026-10-08 y 2026-10-09)

1. **Si quien destraba dice que ya habló con el trabado, Leda le pregunta qué arreglaron y para cuándo
   lo destraba, para que quede asentado.**
2. **"Ya lo hablé" sin decir qué: Leda les pregunta a los dos; vale lo que conteste el primero**, y
   Leda se lo confirma al otro como en la regla 3 (decisión 48).
3. **Lo acordado se confirma con el otro, sin pedirle nada si está bien** (decisión 47): si es así,
   no hace falta que haga nada; si no es lo que entendió, que avise y Leda se lo pasa. Si corrige,
   Leda le lleva la corrección y les cierra el tema a los dos (decisión 39).

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, C-5):

- **"Ya lo hablé" solo no se anota todavía:** lo que queda asentado es lo que arreglaron y para cuándo.
  La pregunta de Leda sigue abierta, con su espera (la escalera de las preguntas la repite si no
  contesta, sin escalar), y recuerda que ya lo hablaron.
- **Se pregunta una vez.** Si la respuesta trae lo que arreglaron sin una fecha, queda anotado así; no
  se vuelve a preguntar.
- **Lo que le llega al otro sale con el margen para corregir,** como todo lo que dice quien destraba
  (conversación 32). Un "ya lo hablé" no cierra el bloqueo: lo cierra Marcos.
- **La corrección cierra el tema:** a quien le llega no se le pide nada más (no lleva "si no es así,
  avisame").

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos** (referente Ismael):
  - "Programar PLC de la comprimidora": vence el viernes 30; `en_curso` desde el lunes 19; sin
    bloqueos. Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin
    fallas".
  - "Instalar el panel HMI de la comprimidora": vence el viernes 6 de noviembre; `en_curso` desde el
    lunes 19; sin bloqueos. Criterio de aceptación: "El panel HMI muestra el estado de la comprimidora
    y permite arrancarla y pararla desde la planta".
  - "Revisar comunicaciones industriales de la comprimidora": vence el viernes 6 de noviembre;
    `en_curso` desde el lunes 19; sin bloqueos. Criterio de aceptación: "Los equipos de la
    comprimidora se comunican con el PLC por la red de planta sin errores durante una hora".
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
     recuerda que ya lo hablaron. Se guarda la misma pregunta para Marcos (decisión 48), que sale
     terminado el margen para corregir (11:15).
   - La respuesta dice: una sola pregunta: qué arreglaron y para cuándo se la pasa; que a Marcos
     también se lo pregunta.
   - La respuesta no dice: que quedó anotado; un reproche.
   - Estado después (Ariel): tema abierto, para cuándo destraba la tarea del PLC.

5. **Ariel** escribe (martes 20, 11:08): "quedamos q se la paso el jueves temprano"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el jueves 22, con sus palabras.
   - Efecto: queda anotado, como un hecho del bloqueo, lo que arreglaron: para el jueves 22, con sus
     palabras, atribuido a Ariel; su pregunta y su espera se cierran. Vale lo que contestó el
     primero: la pregunta a Marcos no sale (queda retirada con su motivo). Se guarda el aviso a
     Marcos, que sale terminado el margen para corregir (11:18), para confirmarle lo acordado. El
     bloqueo sigue abierto.
   - La respuesta dice: que quedó anotado lo que arreglaron; que Marcos se va a enterar.
   - La respuesta no dice: que el bloqueo se cerró.
   - Estado después (Ariel): sin tema abierto.

6. **Leda**, por su cuenta, a Marcos (martes 20, 11:18): lo que arreglaron.
   →
   - Efecto: un mensaje privado a Marcos, informativo.
   - El mensaje dice: la tarea del PLC; que Ariel dice que le pasa la IP el jueves (jue 22/10)
     temprano; que si es así, no hace falta que haga nada, y que si no es lo que entendió, que avise
     y Leda se lo pasa a Ariel.
   - El mensaje no dice: que la tarea se destrabó; una pregunta que haya que contestar sí o sí.

6b. **Marcos** escribe (martes 20, 11:40): "no, quedamos el miercoles a la mañana"
    →
    - Jugadas: `contar_lo_que_arreglaron` sobre la tarea del PLC, para el miércoles 21, con sus
      palabras.
    - Efecto: queda anotada la corrección, como un hecho del bloqueo, atribuida a Marcos. Se guarda
      el aviso a Ariel con la corrección, que sale terminado el margen para corregir (11:50); con
      eso el tema queda cerrado para los dos (decisión 39). El bloqueo sigue abierto.
    - La respuesta dice: que quedó anotado; que Ariel se va a enterar.
    - La respuesta no dice: que el bloqueo se cerró.

6c. **Leda**, por su cuenta, a Ariel (martes 20, 11:50): la corrección.
    →
    - Efecto: un mensaje privado a Ariel, informativo.
    - El mensaje dice: la tarea del PLC; que Marcos dice que quedaron el miércoles (mié 21/10) a la
      mañana; que no hace falta responder.
    - El mensaje no dice: que avise si no es así (la corrección cierra el tema).

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
     su espera se cierran. Ninguna pregunta a Marcos: ya se sabe qué arreglaron. Se guarda el aviso a
     Marcos, que sale a las 14:40.
   - La respuesta dice: que quedó anotado; que Marcos se va a enterar.
   - La respuesta no dice: una pregunta por lo que arreglaron.

10. **Leda**, por su cuenta, a Marcos (martes 20, 14:40): lo que arreglaron del panel HMI.
    →
    - Efecto: un mensaje privado a Marcos, informativo.
    - El mensaje dice: la tarea del panel HMI; que Ariel dice que libera la licencia el viernes (vie
      23/10); que si es así, no hace falta que haga nada, y que si no es lo que entendió, que avise.

11. **Marcos** escribe (martes 20, 15:00): "con comunicaciones tambien, ariel tiene q configurar el
    switch de la red"
    →
    - Jugadas: `anotar_bloqueo` sobre la tarea de comunicaciones, con su causa, y
      `anotar_quien_destraba`, con Ariel.
    - Efecto: el bloqueo y quién lo destraba; se guarda el mensaje a Ariel, que sale a las 15:10.
    - La respuesta dice: que quedó anotado; que le pregunta a Ariel y le avisa apenas sepa algo.

12. **Leda**, por su cuenta, a Ariel (martes 20, 15:10): la pregunta por comunicaciones.
    →
    - Efecto: un mensaje privado a Ariel; una pregunta abierta de Ariel sobre la tarea de
      comunicaciones.

13. **Ariel** escribe (martes 20, 15:25): "ya lo hable con marcos"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea de comunicaciones, diciendo que ya lo habló.
    - Efecto: ninguno anotado todavía; se guarda la pregunta a Marcos, que sale a las 15:35.
    - La respuesta dice: una sola pregunta: qué arreglaron y para cuándo; que a Marcos también se lo
      pregunta.
    - Estado después (Ariel): tema abierto, para cuándo destraba la tarea de comunicaciones.

14. **Leda**, por su cuenta, a Marcos (martes 20, 15:35): la pregunta por lo que arreglaron.
    →
    - Efecto: un mensaje privado a Marcos; una pregunta abierta de Marcos sobre la tarea de
      comunicaciones (qué arreglaron con Ariel), con su espera.
    - El mensaje dice: la tarea de comunicaciones; que Ariel dice que ya lo hablaron; la pregunta:
      qué arreglaron y para cuándo.

15. **Marcos** escribe (martes 20, 15:50): "quedamos q lo configura el jueves"
    →
    - Jugadas: `contar_lo_que_arreglaron` sobre la tarea de comunicaciones, para el jueves 22.
    - Efecto: queda anotado lo que arreglaron, atribuido a Marcos; su pregunta y su espera se
      cierran, y también las de Ariel: vale lo que contestó el primero. Se guarda el aviso a Ariel,
      que sale a las 16:00, para confirmarle lo acordado.
    - La respuesta dice: que quedó anotado; que Ariel se va a enterar.
    - Estado después (Marcos): sin tema abierto; (Ariel) sin tema abierto.

16. **Leda**, por su cuenta, a Ariel (martes 20, 16:00): lo que arreglaron, según Marcos.
    →
    - Efecto: un mensaje privado a Ariel, informativo.
    - El mensaje dice: la tarea de comunicaciones; que Marcos dice que quedaron en que configura el
      switch el jueves (jue 22/10); que si es así, no hace falta que haga nada, y que si no es lo que
      entendió, que avise y Leda se lo pasa a Marcos.

## Qué mide

- **Garantías (5b):** no anota una fecha que nadie dio; no da por arreglado algo que nadie contó; no
  da por cerrado un bloqueo; no le avisa a nadie lo que todavía no quedó asentado; no pregunta dos
  veces lo que ya le dijeron; después de la primera respuesta no le sigue preguntando al otro; la
  corrección le llega a quien dijo lo otro y no le pide nada más.
- **Falla de comprensión:** que la IA no tome "si ya lo hable con marcos" como lo que dice quien
  destraba, diciendo que ya lo habló; que tome "quedamos q se la paso el jueves temprano" como otra
  cosa que la fecha que destraba; o que no tome "no, quedamos el miercoles a la mañana" y "quedamos q
  lo configura el jueves" de Marcos como lo que arregló con quien destraba.
