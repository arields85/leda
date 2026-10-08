# 20. El formato de los mensajes

**Qué prueba:** los mensajes de Leda son breves y se leen de un vistazo, no un bloque de texto rígido.
Segunda vuelta (usuario, 2026-10-07, después de verlo en Telegram): sin negrita; un renglón por idea y un
renglón en blanco entre bloques; al principio del renglón, 📋 una tarea (su nombre solo), ✏️ lo que Leda
anotó, 🗓️ una tarea con su vencimiento en una lista y ⚠️ una consecuencia (un atraso, una tarea que espera
a otra); lo importante primero; fechas cortas (día abreviado y número/mes); el nombre completo de una
tarea una sola vez, y las personas por su nombre; el cierre aparte, al final: la pregunta o que no hace
falta responder. Vale en lo que contesta y en lo que manda por su cuenta. Lo que cambia es la forma: los
hechos, las jugadas y los efectos son los de siempre. La primera vuelta (negrita, párrafos y viñetas) fue
el pedido del usuario al aprobar M3. Tercera vuelta (usuario, 2026-10-07, después de la segunda prueba
por Telegram): 🗓️ en vez de 📅, que Telegram dibuja con una fecha fija; en un bloque con una tarea, su
renglón con 📋 es el primero y todo lo de esa tarea, también quién dijo qué, va debajo; una marca va
siempre al principio de su renglón, nunca en el medio; y cuando otra persona se entera, Leda lo dice en
pasiva, en futuro mientras no pasó, nunca como algo que ella le avisa. **Desde el 2026-10-08 (decisión 11
del usuario, `odd/tasks/fase-c.md`):** a quien aprueba el trabajo de la persona no se lo nombra por su
cuenta, así que la pasiva va sobre lo que se informa ("La nueva fecha queda informada"), no sobre él
("Ismael será notificado" quedó superado); si la persona pregunta a quién se le avisa, Leda le dice el
nombre.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `asignada`; sin bloqueos ni dependencias.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso` desde el lunes 19; sin bloqueos ni dependencias; sin previsiones anotadas.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (martes 20, 10:00), que no pide respuesta.
  A Ismael, nada.

## Hilo

1. **Marcos** escribe (martes 20, 10:10): "que tengo pendiente?"
   →
   - Jugadas: `consultar_pendientes`.
   - Efecto: ninguno.
   - La respuesta dice: primero, en un renglón, que tiene dos tareas pendientes; después las dos, cada una
     en su renglón con 🗓️, su nombre completo, su estado y su fecha corta: la del PLC sin empezar, que
     vence el vie 23/10; la de comunicaciones en curso, que vence el vie 30/10. El próximo paso, aparte y
     al final.
   - La respuesta no dice: tareas de otras personas; las dos tareas en un mismo renglón; negrita,
     viñetas u otra marca (títulos, enlaces, cursiva, código); una fecha larga ("viernes 23 de
     octubre").
   - Estado después: sin tema abierto.

2. **Marcos** escribe (martes 20, 10:15): "arranque con el plc. y lo de comunicaciones no llego al 30, va
   a ser el miercoles 4 xq espero el switch nuevo"
   →
   - Jugadas: dos. `anotar_inicio` sobre la tarea del PLC; `anotar_prevision` sobre la de comunicaciones,
     con fecha miércoles 4 de noviembre y motivo "espera el switch nuevo".
   - Efecto: los dos, directo, como en la conversación 05: la tarea del PLC en `en_curso`; en la de
     comunicaciones, la fecha nueva del miércoles 4 con su motivo, con el vencimiento en el viernes 30; un
     solo aviso a Ismael, sólo de la fecha nueva.
   - La respuesta dice: primero, en un renglón, lo que anotó; cada tarea en su bloque, separado por un
     renglón en blanco: primero un renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado (arrancó
     la del PLC; la de comunicaciones la termina el mié 4/11 porque espera el switch nuevo), con ⚠️ la
     consecuencia (vence el vie 30/10: tres días hábiles de atraso) y que la fecha nueva queda
     informada hoy, dicho en pasiva sobre lo que se informa y en futuro, como algo que todavía no pasó,
     sin nombrar a Ismael; el próximo paso, en pocas
     palabras, aparte y al final.
   - La respuesta no dice: los dos hechos mezclados en un renglón o en un párrafo corrido; lo anotado
     antes que el renglón de su tarea; que la fecha de la tarea de comunicaciones cambió; el nombre
     completo de una tarea dos veces; que Leda le avisa a Ismael ("le voy a avisar", "le avisé"); el
     nombre de Ismael; negrita.
   - Estado después: sin tema abierto, nada para después.

3. **Leda**, por su cuenta, a Ismael (martes 20, a la hora que dicen los hechos): el aviso de la fecha
   nueva de la tarea de comunicaciones. A Marcos, nada.
   →
   - El mensaje dice, un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de
     su bloque, y debajo que Marcos dijo que la termina el mié 4/11 porque espera el switch nuevo; que
     vence el vie 30/10 y, con ⚠️ al principio de su renglón, el atraso, tres días hábiles; que no hace
     falta que conteste, solo en el último renglón.
   - El mensaje no dice: nada de la tarea del PLC; que la fecha cambió; quién dijo qué antes del renglón
     de la tarea; una marca en el medio de un renglón; un párrafo corrido; Marcos con su apellido;
     negrita.

## Qué mide

- **El formato (usuario, 2026-10-07, segunda y tercera vuelta):** el corredor lo mide solo en cada
  mensaje de Leda, como falla de `formato`, aparte de las otras (`comprobar.fallas_de_formato`):
  negrita; el nombre completo de una tarea fuera de un renglón con 📋 o 🗓️, o más de una vez; un renglón
  que empieza con 📅; un renglón con 📋 que lleva algo más que el nombre; en un bloque con una tarea, un
  renglón antes del de la tarea; una marca en el medio de un renglón; Leda en primera persona
  avisándole o notificándole a otra persona; un renglón de más de 140 caracteres; una fecha larga; una
  pregunta que no es el último renglón, o más de una; que no hace falta responder, en otro lugar que el
  último renglón; un cierre que no va solo y aparte. Lo que no se mide solo (que el primer renglón diga
  lo que pasó, que cada renglón sea una idea, que la pasiva vaya en futuro mientras no pasó) se lee en
  las transcripciones. Si la IA igual escribe `**`, el envío lo convierte en negrita de Telegram, nunca
  en asteriscos (`tests/garantias/test_formato_de_salida.py`).
- **Garantías (5b):** no inventa (lo que todavía no pasó va en futuro); no deja sin salida (cada mensaje
  termina con su próximo paso); no confunde la tarea.
- **Falla de comprensión:** que la IA no tome "que tengo pendiente?" como una consulta, o que cruce los
  dos hechos del paso 2 entre las tareas.
