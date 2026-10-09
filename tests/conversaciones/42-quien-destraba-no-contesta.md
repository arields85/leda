# 42. Quien destraba no contesta

**Qué prueba:** a quien destraba y no contesta, Leda nunca lo abandona. Ariel tiene que pasarle a
Marcos la IP del servidor y no contesta: puede no contestar por no poder (perdió el celular, un
problema personal). Los días 1 a 3 Leda le repite la pregunta una vez por día; desde el 4, cada 2 días
hábiles mientras siga el bloqueo, sin escalar a nadie por eso. Si Ariel escribe por otra cosa, Leda le
contesta lo suyo y, en otro mensaje justo después, le recuerda la pregunta. A los días del espacio el
bloqueo queda asentado, como siempre. Decisión 38 del usuario (`odd/tasks/fase-c.md`, 2026-10-09; C-5b),
con las decisiones 35, 36 (el bloqueo viejo) y 50 (la pregunta que quedó por un cambio de tema vuelve
en un mensaje aparte); ADR 0017, decisión 3a (la persecución del bloqueo); constitución §8.

**Corre desde la C-5b** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-09)

1. **Días 1 a 3, una vez por día.** El día 1 es el de la pregunta; los días 2 y 3, Leda la repite.
2. **Desde el 4, cada 2 días hábiles mientras siga el bloqueo.** Nunca deja de preguntarle mientras
   la tarea siga trabada.
3. **Si escribe por otra cosa, Leda le recuerda la pregunta en ese momento**, en un mensaje aparte,
   justo después de contestarle lo suyo (decisión 50: un mensaje, un tema).
4. **A los días del espacio queda asentado** (decisiones 35 y 36; la 36 lo prueba en detalle).
5. Las ausencias (vacaciones, licencia) son una tarea aparte (C-8): **no son de esta conversación**.

Cómo se leyó lo que la regla no dice (lectura del coordinador, `odd/tasks/fase-c.md`, C-5b): "cada 2
días hábiles" cuenta desde la repetición anterior, así que el día 4 no hay mensaje y el 5 sí. A quien
destraba nunca se le dice que se va a avisar a alguien si no contesta: no escala.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tarea de Marcos** (referente de OT; quien aprueba su trabajo es Ismael): "Programar PLC de la
  comprimidora": vence el viernes 13 de noviembre; `en_curso` desde el lunes 19; sin bloqueos.
  Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
- **Tarea de Ariel De Simone** (Software e interfaz HMI): "Instalar el servidor de CoreLabs": vence el
  viernes 13 de noviembre; `asignada`. Criterio de aceptación: "El servidor de CoreLabs responde en
  la red de planta y tiene su IP fija anotada".
- **Estado de la conversación** de Marcos, de Ariel y de Ismael: sin tema abierto, nada para después,
  nada mostrado para confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Marcos** escribe (martes 20, 10:20): "estoy trabado con el plc me falta la ip del servidor de
   corelabs"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con su causa.
   - Efecto: un bloqueo abierto en la tarea del PLC; la tarea pasa a `bloqueada`.
   - La respuesta dice: que quedó anotado el bloqueo; una sola pregunta: quién lo puede destrabar.

2. **Marcos** escribe (martes 20, 10:22): "me la tiene que pasar ariel"
   →
   - Jugadas: `anotar_quien_destraba`, con Ariel.
   - Efecto: queda anotado que lo destraba Ariel; se guarda el mensaje a Ariel, que sale a las 10:32.
   - La respuesta dice: que Leda le pregunta a Ariel para cuándo y le avisa a Marcos apenas sepa algo.

3. **Leda**, por su cuenta, a Ariel (martes 20, 10:32): la pregunta (día 1).
   →
   - Efecto: un mensaje privado a Ariel; su pregunta abierta, con su espera.
   - El mensaje dice: que Marcos está trabado con la tarea del PLC porque le falta la IP del servidor
     de CoreLabs; para cuándo se la puede pasar.

4. **Leda**, por su cuenta, a Ariel (miércoles 21, 10:00): la repite (día 2).
   →
   - El mensaje dice: la misma pregunta, recordando quién está trabado y por qué.
   - El mensaje no dice: un reproche; que se va a avisar a alguien si no contesta.

5. **Leda**, por su cuenta, a Ariel (jueves 22, 10:00): la repite (día 3).

6. **Nadie** escribe hasta el viernes 23, 10:00 (día 4).
   →
   - Efecto: ningún mensaje: desde el día 4, cada 2 días hábiles.

7. **Leda**, por su cuenta, a Ariel (lunes 26, 10:00): la repite (día 5, dos días hábiles después de
   la anterior).
   →
   - El mensaje no dice: un reproche; que se va a avisar a alguien.

8. **Ariel** escribe (lunes 26, 11:00): "arranque con la instalacion del servidor"
   →
   - Jugadas: `anotar_inicio` sobre su tarea del servidor.
   - Efecto: su tarea pasa a `en_curso`. Se guarda, para salir enseguida, la vuelta a la pregunta
     del PLC (decisión 50).
   - La respuesta dice: que quedó anotado que arrancó con el servidor.
   - La respuesta no dice: nada de la tarea del PLC (va en un mensaje aparte).
   - Estado después (Ariel): la pregunta del PLC sigue abierta.

9. **Leda**, a Ariel (lunes 26, 11:01): la pregunta del PLC, en un mensaje aparte.
   →
   - El mensaje dice: la vuelta a la pregunta: para cuándo le puede pasar a Marcos la IP del servidor.
   - El mensaje no dice: nada del servidor que arrancó.

10. **Leda**, por su cuenta (martes 27, 10:00): el bloqueo viejo, a los cinco días hábiles.
    →
    - Efecto: a Ismael (quien aprueba el trabajo de Marcos, que es el referente de OT), que la tarea
      del PLC sigue trabada desde el martes 20, con la historia; a Marcos, que quedó asentado. A
      Ariel, nada ese día.

11. **Leda**, por su cuenta, a Ariel (miércoles 28, 10:00): la repite (dos días hábiles después de la
    anterior).

12. **Ariel** escribe (miércoles 28, 10:30): "perdon perdi el celular, mañana a primera hora se la
    paso"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el jueves 29.
    - Efecto: queda anotado, con sus palabras; su pregunta y su espera se cierran; se guarda el aviso
      a Marcos, que sale a las 10:40, y la pregunta a Ariel de si ya se la pasó, para el jueves 29 a
      las 10:00 (decisión 42, C-5e).
    - La respuesta dice: que quedó anotado; que Marcos se va a enterar.
    - La respuesta no dice: un reproche por no haber contestado.

13. **Leda**, por su cuenta, a Marcos (miércoles 28, 10:40): lo que dijo Ariel, como información.

14. **Leda**, por su cuenta, a Ariel (jueves 29, 10:00): el día que dijo; si ya le pasó la IP a
    Marcos (decisión 42, C-5e).
    →
    - Efecto: la pregunta vieja no se repite más (ya contestó); sale sólo ésta, que abre su pregunta.

## Qué mide

- **Garantías (5b):** a quien destraba nunca se lo deja de preguntar mientras siga el bloqueo, y
  nunca más de una vez por día de la escalera; no se escala a nadie por su silencio; no se le
  reprocha ni se le dice que se va a avisar a alguien; lo que vuelve por un cambio de tema sale en
  un mensaje aparte; ya contestado, no se le pregunta más.
- **Falla de comprensión:** que la IA no tome "arranque con la instalacion del servidor" como el
  inicio de su tarea, o "mañana a primera hora se la paso" como lo que dice quien destraba.
