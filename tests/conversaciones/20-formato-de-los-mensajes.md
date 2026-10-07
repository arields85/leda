# 20. El formato de los mensajes

**Qué prueba:** los mensajes de Leda son breves y se leen de un vistazo, no un bloque de texto rígido: las
tareas y lo importante van en negrita, cada idea en su párrafo con un renglón en blanco entre párrafos, y
varias cosas del mismo tipo van en viñetas. Vale en lo que contesta y en lo que manda por su cuenta. Lo
que cambia es la forma: los hechos, las jugadas y los efectos son los de siempre. Pedido del usuario del
2026-10-07, al aprobar M3, con capturas de antes y después.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles después
    de D); `asignada`; sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `en_curso` desde el lunes 19; sin bloqueos ni dependencias; sin previsiones anotadas.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (martes 20, 10:00), que no pide respuesta.
  A Ismael, nada.

## Hilo

1. **Marcos** escribe (martes 20, 10:10): "que tengo pendiente?"
   →
   - Jugadas: `consultar_pendientes`.
   - Efecto: ninguno.
   - La respuesta dice: sus dos tareas, una por viñeta, cada una con su nombre en negrita, su estado y su
     fecha: la del PLC sin empezar, que vence el viernes 23; la de comunicaciones en curso, que vence el
     viernes 30. Breve: lo que no es la lista va en un párrafo corto aparte.
   - La respuesta no dice: tareas de otras personas; las dos tareas en un mismo renglón o en un solo
     párrafo corrido; otra marca que no sea la negrita y las viñetas (títulos, enlaces, cursiva, código).
   - Estado después: sin tema abierto.

2. **Marcos** escribe (martes 20, 10:15): "arranque con el plc. y lo de comunicaciones no llego al 30, va
   a ser el miercoles 4 xq espero el switch nuevo"
   →
   - Jugadas: dos. `anotar_inicio` sobre la tarea del PLC; `anotar_prevision` sobre la de comunicaciones,
     con fecha miércoles 4 de noviembre y motivo "espera el switch nuevo".
   - Efecto: los dos, directo, como en la conversación 05: la tarea del PLC en `en_curso`; en la de
     comunicaciones, la fecha nueva del miércoles 4 con su motivo, con el vencimiento en el viernes 30; un
     solo aviso a Ismael, sólo de la fecha nueva.
   - La respuesta dice: cada hecho en su párrafo, con un renglón en blanco entre los dos y el nombre de su
     tarea en negrita; que Ismael se va a enterar hoy, como algo que todavía no pasó; el próximo paso,
     en pocas palabras y en su propio párrafo al final.
   - La respuesta no dice: los dos hechos mezclados en un párrafo corrido; que la fecha de la tarea de
     comunicaciones cambió; texto en negrita que no sea una tarea o el hecho importante.
   - Estado después: sin tema abierto, nada para después.

3. **Leda**, por su cuenta, a Ismael (martes 20, a la hora que dicen los hechos): el aviso de la fecha
   nueva de la tarea de comunicaciones. A Marcos, nada.
   →
   - El mensaje dice, en párrafos cortos: la tarea de comunicaciones en negrita; que Marcos la termina el
     miércoles 4 porque espera el switch nuevo; que vencía el viernes 30; el atraso, tres días hábiles;
     que no hace falta que conteste, al final.
   - El mensaje no dice: nada de la tarea del PLC; que la fecha cambió; un solo párrafo corrido.

## Qué mide

- **El formato (usuario, 2026-10-07):** se lee en las transcripciones. Es una falla un mensaje en un solo
  bloque cuando dice más de una cosa, varias tareas en un mismo renglón, una tarea sin su nombre en
  negrita cuando el mensaje habla de ella, negrita de adorno, o una marca que no sea la negrita y las
  viñetas. Las marcas nunca llegan a la persona como asteriscos: el envío las convierte en el formato de
  Telegram, y una mal cerrada sale como texto (`tests/garantias/test_formato_de_salida.py`).
- **Garantías (5b):** no inventa (lo que todavía no pasó va en futuro); no deja sin salida (cada mensaje
  termina con su próximo paso); no confunde la tarea.
- **Falla de comprensión:** que la IA no tome "que tengo pendiente?" como una consulta, o que cruce los
  dos hechos del paso 2 entre las tareas.
