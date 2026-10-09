# 44. Seguir la cadena hasta quien puede destrabarla

**Qué prueba:** Leda sigue la cadena hasta quien puede destrabarla. Ariel ya está trabado con el
servidor (falta el switch, lo pone Lucas) cuando Marcos dice que lo que le falta se lo tiene que pasar
Ariel: Leda no le pide a Ariel lo que no puede dar; le cuenta enseguida a Marcos que Ariel está
esperando el switch, con lo que ya dijo Lucas, y que le avisa apenas se mueva. El día que Lucas dijo,
Leda le vuelve a preguntar si llegó; la fecha nueva le llega a Ariel y a Marcos; si Lucas no contesta,
rige la regla de quien destraba y no contesta. Cuando Ariel puede seguir, ahora sí puede pasarle la IP
a Marcos: Leda le pregunta para cuándo. Decisión 42 del usuario (`odd/tasks/fase-c.md`, 2026-10-09;
C-5e), con las decisiones 6 (bloqueos encadenados), 38 (a quien no contesta no se lo abandona) y 39
(cerrar el tema para todos); ADR 0017, decisión 3a; mecánica §4 y §8.

**Corre desde la C-5e** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-09)

1. **Si quien destraba ya está trabado, Leda no le pide lo que no puede dar**: se lo cuenta enseguida
   a quien espera, y le avisa apenas se mueva.
2. **Sigue profundizando:** de quién depende lo que traba a Ariel (Lucas), le pregunta para cuándo e
   informa la fecha a Ariel, a Marcos y a toda la cadena.
3. **El día de esa fecha le vuelve a preguntar si llegó**, con la regla de la decisión 38 si no
   contesta (días 1 a 3, una vez por día; después, cada 2 días hábiles).

Cómo se leyó lo que la regla no dice (lectura del escritor de la C-5e, `odd/tasks/fase-c.md`):

- **"Ya está trabado"** es el mismo enlace de la decisión 6, nunca por adivinar: la tarea de Marcos
  depende de una tarea de Ariel (la estructura que carga la plataforma) y esa tarea tiene un bloqueo
  abierto. Ariel trabado con otra cosa sí recibe la pregunta.
- **Cuando Ariel puede seguir, ahora sí puede dar lo que falta:** Leda le pregunta para cuándo, como a
  cualquiera que destraba (decisión 4). Si contesta antes de que le llegue, la pregunta no sale.
- **Volver a preguntar el día de la fecha es una sola regla**, para cualquiera que destraba y da un
  día, no sólo al final de una cadena: sale a la hora de lo que Leda manda por su cuenta y, si ese
  momento ya pasó cuando lo dijo (dijo "hoy"), el día hábil siguiente. No sale si después dijo otra
  cosa, si el bloqueo se cerró o si lo destraba otra persona.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tarea de Ariel De Simone** (Software e interfaz HMI): "Configurar el servidor de CoreLabs de la
  comprimidora": vence el viernes 13 de noviembre; `en_curso` desde el lunes 19; sin bloqueos.
- **Tarea de Marcos** (OT; aprueba su trabajo Ismael): "Programar PLC de la comprimidora": vence el
  viernes 13 de noviembre; `en_curso` desde el lunes 19; sin bloqueos. **Depende de** la tarea del
  servidor de Ariel (una dependencia bloqueante, cargada por la plataforma).
- **Lucas Natuche** (Infraestructura IT) tiene un chat con Leda y ninguna tarea en esta conversación.
- **Estado de la conversación** de todos: sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada en la semana.

## Hilo

1. **Ariel** escribe (martes 20, 10:20): "estoy parado con el servidor xq falta el switch nuevo, lo
   pone lucas"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del servidor, con su causa, y `anotar_quien_destraba`,
     con Lucas.
   - Efecto: un bloqueo abierto en la tarea del servidor, que pasa a `bloqueada`, y que lo destraba
     Lucas; se guarda el mensaje a Lucas, a las 10:30.
   - La respuesta dice: que quedó anotado; que Leda le pregunta a Lucas.

2. **Leda**, por su cuenta, a Lucas (martes 20, 10:30): la pregunta por la tarea del servidor de Ariel.

3. **Lucas** escribe (martes 20, 10:45): "el switch llega el jueves"
   →
   - Jugadas: `decir_cuando_destraba` sobre la tarea del servidor, para el jueves 22.
   - Efecto: queda anotado; se guardan el aviso a Ariel, a las 10:55, y la pregunta de si llegó, para
     el jueves 22 a las 10:00.
   - La respuesta dice: que quedó anotado; que Ariel se va a enterar; que el jueves le pregunta.

4. **Leda**, por su cuenta, a Ariel (martes 20, 10:55): que Lucas dice que el switch llega el jueves
   (jue 22/10).

5. **Marcos** escribe (martes 20, 11:20): "estoy trabado con el plc me falta la ip del servidor de
   corelabs"
   →
   - Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con su causa.
   - Efecto: un bloqueo abierto en la tarea del PLC; la tarea pasa a `bloqueada`.
   - La respuesta dice: que quedó anotado; una sola pregunta: quién lo puede destrabar.

6. **Marcos** escribe (martes 20, 11:22): "me la tiene q pasar ariel"
   →
   - Jugadas: `anotar_quien_destraba`, con Ariel.
   - Efecto: queda anotado que lo destraba Ariel. No se guarda ningún mensaje a Ariel: está trabado con
     el servidor, que es lo que le falta a Marcos.
   - La respuesta dice: que Ariel está esperando que llegue el switch para el servidor, que lo pone
     Lucas y que Lucas dice que llega el jueves (jue 22/10); que le avisa apenas se mueva.
   - La respuesta no dice: que Leda le pregunta a Ariel.

7. **Nadie** escribe (martes 20, 11:32 y 12:00): a Ariel no le llega nada por lo de Marcos.

8. **Nadie** escribe (miércoles 21, 10:00): nada para nadie.

9. **Leda**, por su cuenta, a Lucas (jueves 22, 10:00): el día que dijo; si llegó el switch para la
   tarea del servidor de Ariel.
   →
   - Efecto: su pregunta abierta, con su espera.

10. **Lucas** escribe (jueves 22, 10:30): "no llego, el proveedor dice que mañana"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del servidor, para el viernes 23, con sus
      palabras.
    - Efecto: queda anotado; se guardan el aviso a Ariel y el aviso a Marcos de ese avance del medio, a
      las 10:40, y la pregunta de si llegó, para el viernes 23 a las 10:00.
    - La respuesta dice: que quedó anotado; que Ariel se va a enterar.

11. **Leda**, por su cuenta (jueves 22, 10:40):
    →
    - A Ariel, informativo: que Lucas dice que el switch llega mañana (vie 23/10).
    - A Marcos, informativo: lo mismo, como un avance de lo que espera su tarea (la del servidor de
      Ariel); que no hace falta responder.

12. **Leda**, por su cuenta, a Lucas (viernes 23, 10:00): el día que dijo; si llegó el switch.

13. **Leda**, por su cuenta, a Lucas (lunes 26, 10:00): Lucas no contestó; la pregunta otra vez (la
    regla de la decisión 38), sin decir que se va a avisar a nadie.

14. **Lucas** escribe (lunes 26, 11:00): "listo ya quedo instalado el switch"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del servidor, que ya está.
    - Efecto: queda anotado; se guardan el aviso a Ariel y el aviso a Marcos, a las 11:10. El bloqueo
      de Ariel sigue abierto: lo cierra Ariel.

15. **Leda**, por su cuenta (lunes 26, 11:10):
    →
    - A Ariel: que Lucas dice que ya está; que cuando pueda seguir, lo diga.
    - A Marcos, informativo: que Lucas dice que el switch ya está instalado; que no hace falta
      responder.

16. **Ariel** escribe (lunes 26, 11:30): "buenisimo ya sigo con el servidor"
    →
    - Jugadas: `destrabar` sobre la tarea del servidor.
    - Efecto: el bloqueo del servidor se cierra y la tarea vuelve a `en_curso`; se guardan el aviso a
      Marcos de que Ariel pudo seguir y el de Lucas de cómo se cerró (regla 39), a las 11:40. Ahora
      Ariel puede pasarle la IP a Marcos: se guarda la pregunta a Ariel de para cuándo.
    - La respuesta dice: que quedó anotado; que Marcos se va a enterar; que Marcos espera la IP y Leda
      le pregunta para cuándo.

17. **Leda**, por su cuenta (lunes 26, 11:40):
    →
    - A Marcos, informativo: que Ariel ya pudo seguir con la tarea del servidor.
    - A Lucas, informativo: que Ariel ya pudo seguir; que no hace falta responder.

18. **Leda**, por su cuenta, a Ariel (lunes 26, 12:00, pasada la media hora desde que escribió): la
    pregunta por la tarea del PLC de Marcos, para cuándo le pasa la IP.
    →
    - Efecto: su pregunta abierta, con su espera.

19. **Ariel** escribe (lunes 26, 12:15): "se la paso mañana temprano"
    →
    - Jugadas: `decir_cuando_destraba` sobre la tarea del PLC, para el martes 27.
    - Efecto: queda anotado; se guardan el aviso a Marcos, a las 12:25, y la pregunta de si se la pasó,
      para el martes 27 a las 10:00.

20. **Leda**, por su cuenta, a Marcos (lunes 26, 12:25): que Ariel dice que le pasa la IP mañana
    (mar 27/10) temprano; que cuando pueda seguir, lo diga.

## Qué mide

- **Garantías (5b):** nunca le pide a Ariel lo de Marcos mientras está trabado con eso; nunca da por
  destrabada la tarea de Marcos porque se destrabó la de Ariel; nunca inventa una fecha que nadie dio;
  el día de la fecha le pregunta a quien la dio, una vez, y no si ya dijo otra cosa; a quien no contesta
  nunca le dice que se va a avisar a nadie; ningún aviso del medio pide respuesta.
- **Falla de comprensión:** que la IA no tome "me la tiene q pasar ariel" como quién lo destraba; o "no
  llego, el proveedor dice que mañana" como un día nuevo de Lucas para la tarea del servidor.
