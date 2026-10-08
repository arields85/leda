# 25. Mensajes sin puntuación

**Qué prueba:** la persona escribe como escribe, de corrido, sin puntos ni comas, con errores de tipeo y
hablando de dos tareas en la misma frase. Leda reparte cada hecho en su tarea; si no puede saber a qué tarea
va algo, pregunta en lugar de elegir (la duda de la conversación 09; ADR 0018, decisión 4). Nunca inventa
una causa ni un motivo con palabras que eran de otra cosa. Sale de la prueba por Telegram real del
2026-10-07: Marcos escribió el mensaje del paso 2 sin puntuación a propósito, la IA anotó el bloqueo y la
fecha del viernes 23 en la tarea del PLC, con "comunicaciones" dentro de la causa y la misma frase como
motivo de la fecha, y el aviso equivocado le llegó a Ismael un minuto después. Lo que Marcos quiso decir:
la del PLC está trabada porque le falta el cable para programar, y la de comunicaciones la termina el
viernes 23. Es primero una conversación de prueba (`AGENTS.md`, "Hallazgos de conversación"): se mide con la
IA real varias veces antes de cualquier arreglo, sin palabras clave ni casos especiales. La IA real leyó mal
el paso 2 las cinco veces (bitácora de flujos); el usuario eligió un mecanismo general de la cocina, no un
cambio en las instrucciones de la IA (2026-10-07): lo que una persona dice y le llega a otra espera un
**margen para corregir** (10 minutos, o el del espacio; `leda.motor.margen`) antes de salir, así que una
corrección dentro de ese margen retira el aviso equivocado antes de que le llegue a Ismael (paso 3).
Desde el 2026-10-07, además, una fecha que atrasa lleva su explicación (ADR 0018, 9n): sin el porqué, Leda
pregunta qué la atrasa, de a una pregunta por vez, y el aviso a Ismael espera la respuesta hasta el final
del día; acá llega antes (paso 6) y a Ismael le llega un solo aviso, con el porqué.

## Estado inicial

- **Día:** D = lunes 19, dentro del horario.
- **Tareas de Marcos** (las dos vencen el mismo día, como las cargó la semilla en la prueba real):
  - "Programar PLC de la comprimidora": referente Ismael; vence el jueves 22; `en_curso` desde el lunes 19;
    sin bloqueos ni previsiones.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el jueves 22;
    `asignada`; depende de la del PLC con una dependencia bloqueante (la de la semilla); sin previsiones.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** nada a Marcos ni a Ismael en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (lunes 19, 10:00): el aviso previo de las dos tareas, juntas en un
   mensaje (mecánica §10, como en la conversación 13).
   →
   - El mensaje dice: las dos tareas, cada una en su renglón con 🗓️ y su fecha corta, el jue 22/10; que no
     hace falta contestar, solo en el último renglón.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de las dos tareas.

2. **Marcos** escribe (lunes 19, 10:40), literal, con la coma y el error de tipeo de la prueba real: "con
   el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la tengo para el
   viernes 23"
   → Hay dos respuestas correctas:
   - **(a) El reparto correcto.** Jugadas: `anotar_bloqueo` sobre la tarea del PLC, con la causa en
     palabras de Marcos ("me falta el cable para programar"), sin la palabra "comunicaciones"; y
     `anotar_prevision` sobre la de comunicaciones, con fecha viernes 23, sin motivo. Efecto, directo
     (decisión 9a): la tarea del PLC pasa a `bloqueada`, con su bloqueo y su causa; en la de
     comunicaciones, la fecha nueva del viernes 23, con el vencimiento en el jueves 22 (un día hábil de
     atraso) y un aviso a Ismael guardado como hechos, sin motivo, que espera el porqué hasta el final del
     día (16:30); la pregunta de qué la atrasa queda para después de la de quién destraba (un tema a la
     vez, 9n y 9d). La respuesta dice: cada tarea en su
     bloque, primero su renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado (la del PLC está
     trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10); con
     ⚠️, la consecuencia de la de comunicaciones (vence el jue 22/10: un día hábil de atraso); que la
     fecha nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael; y una sola pregunta, sola en el último renglón:
     quién puede destrabar la del PLC (decisión 9c). Estado después: tema abierto, quién destraba la del
     PLC; para después, qué atrasa la de comunicaciones.
   - **(b) La duda.** Si la IA no puede saber a qué tarea va la fecha (o el cable), pregunta cuál, con las
     dos tareas como opciones, como en la conversación 09, y no anota nada de lo que está en duda todavía.
     Lo que no está en duda puede quedar anotado en la misma respuesta (decisión 9d).
   - **Cómo se comprueba:** el corredor espera una sola respuesta por paso y no sabe expresar "una cosa
     o la otra": el YAML espera (a). Si la IA elige (b), el corredor lo marca como falla de comprensión y
     esa corrida se juzga leyendo la transcripción: una pregunta de duda bien hecha, sin efectos sobre lo
     que está en duda, cuenta como bien.
   - La respuesta no dice, en ninguna de las dos: una causa del bloqueo que nombre las comunicaciones; un
     motivo de la fecha nueva, que Marcos no dio; la fecha del viernes 23 en la tarea del PLC; el bloqueo
     en la de comunicaciones; que Leda le avisa a Ismael; dos preguntas juntas; negrita.

3. **Marcos** escribe (lunes 19, 10:44), dentro del margen para corregir del aviso del paso 2, con el mismo
   estilo: "no el 23 es comunicaciones el plc esta trabado nomas"
   → Lo que corresponde depende de cómo se leyó el paso 2:
   - **Después de (a)**, la lectura correcta: Marcos repite lo que ya quedó anotado. Jugadas:
     `anotar_prevision` sobre la de comunicaciones, con fecha viernes 23, sin motivo. Efecto: la misma
     fecha, que deja atrás el aviso del paso 2 sin que salga (nunca en silencio: con su motivo) y guarda
     otro igual, que sigue esperando el porqué hasta el final del día; el bloqueo del PLC no cambia. Como
     Marcos habla de la de comunicaciones, la pregunta de qué la atrasa pasa a ser la de ahora y la de
     quién destraba la del PLC queda para después (9d). La respuesta dice: en el bloque de la de
     comunicaciones, con 📋 primero y ✏️ debajo, que la termina el vie 23/10; que la fecha nueva queda
     informada hoy, en pasiva y en futuro, sin nombrar a Ismael; y una sola pregunta, sola en el último renglón: qué atrasa la de
     comunicaciones. Es lo que espera el YAML.
   - **Después de la lectura equivocada** de la prueba real (la fecha del viernes 23 en la tarea del PLC):
     Jugadas: `corregir` la previsión de la tarea del PLC, que era de la de comunicaciones (situación
     general 3, como en la conversación 06). Efecto: la previsión del PLC vuelve atrás con un hecho de
     corrección, su aviso a Ismael, que todavía no salió, se retira (`prevision_corregida`), y la fecha
     queda en la de comunicaciones con su propio aviso. A ella pasa sólo la fecha (9n): el porqué era de
     la otra tarea, así que Leda pregunta qué atrasa la de comunicaciones y su aviso lo espera. El
     corredor no puede expresar
     este camino en el mismo YAML: se juzga leyendo la transcripción, y la prueba determinista es
     `tests/motor/test_situaciones.py`
     (`test_una_correccion_dentro_del_margen_no_deja_salir_el_aviso_equivocado`).
   - La respuesta no dice, en ninguno de los dos: la fecha del viernes 23 en la tarea del PLC; el bloqueo
     en la de comunicaciones; que Ismael ya se enteró de algo; que Leda le avisa a Ismael; un motivo de la
     fecha nueva, que Marcos no dio; dos preguntas juntas.
   - Estado después: tema abierto, qué atrasa la de comunicaciones; para después, quién destraba la del
     PLC.

4. **Nadie** escribe (lunes 19, 10:50): a esta hora habría salido el aviso del paso 2.
   → A Ismael no le llega nada: lo dicho en el paso 3 lo dejó atrás antes de su hora. En ninguno de los dos
   caminos le llega un aviso con la fecha en la tarea equivocada.

5. **Nadie** escribe (lunes 19, 10:55): terminó el margen del paso 3.
   → A Ismael no le llega nada todavía: el aviso de la fecha nueva de la tarea de comunicaciones espera
   el porqué hasta el final del día (16:30; ADR 0018, 9n). Si Marcos no lo diera, a esa hora le llegaría
   diciendo que todavía no lo dio, nunca con un motivo inventado (el cable, el PLC).

6. **Marcos** escribe (lunes 19, 11:00): "el cable lo consigue martin de compras y comunicaciones al final
   es el lunes 26 xq me falta el switch tmb"
   →
   - Jugadas: dos, que contestan las dos preguntas. Quién destraba la del PLC, Martín de compras (como en
     la conversación 05, paso 5), la que había quedado para después; y `anotar_prevision` sobre la de
     comunicaciones, con fecha lunes 26 y motivo "me falta el switch", que contesta qué la atrasa. El
     switch es el motivo de la fecha, no otra causa del bloqueo del PLC.
   - Efecto: Martín queda anotado como quien destraba la del PLC; en la de comunicaciones, la fecha nueva
     del lunes 26 con su motivo (dos días hábiles de atraso) y otro aviso a Ismael guardado como hechos,
     con el margen para corregir; el que esperaba el porqué del viernes 23 ya no sale (lo deja atrás
     éste).
   - La respuesta dice: cada tarea en su bloque con 📋 primero; en la del PLC, con ✏️, que Martín de compras
     consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el
     switch, y con ⚠️ la consecuencia (vence el jue 22/10: dos días hábiles de atraso); que la fecha
     nueva queda informada, en pasiva y en futuro, sin nombrar a Ismael; el próximo paso, aparte y al final.
   - La respuesta no dice: el switch como causa del bloqueo del PLC; Martín en la tarea de comunicaciones;
     que Leda le escribió a Martín o lo va a seguir; otra vez la pregunta de quién destraba o la de qué
     atrasa la de comunicaciones.
   - Estado después: sin tema abierto, nada para después.

7. **Leda**, por su cuenta, a Ismael (lunes 19, 11:10, terminado el margen para corregir): el aviso de la
   fecha nueva del lunes 26, el único que le llega por los pasos 2 a 6.
   →
   - El mensaje dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque; debajo,
     que Marcos dijo que la termina el lun 26/10 porque le falta el switch; que vence el jue 22/10 y, con
     ⚠️, el atraso, dos días hábiles; que no hace falta que conteste, solo en el último renglón.
   - El mensaje no dice: el cable o Martín; que la fecha cambió.

8. **Marcos** escribe (martes 20, 15:00): "ya llego el cable sigo con el plc y lo de comunicaciones lo
   termine recien al final"
   →
   - Jugadas: dos. `destrabar` sobre la tarea del PLC (como en la conversación 17); `entregar` sobre la de
     comunicaciones, que nunca se arrancó: se recibe igual, con su vista previa y su confirmación, y al
     confirmar la historia dice que arrancó y se entregó en ese momento (decisión 14 del usuario,
     2026-10-08).
   - Efecto: el bloqueo de la del PLC se cierra y la tarea vuelve a `en_curso`; antes del vencimiento, la
     escalera sigue sola. Sobre la de comunicaciones, ninguno todavía: "lo termine recien al final" no
     dice lo que pide su criterio de aceptación (que los equipos se comunican con el PLC por la red de
     planta sin errores durante una hora), así que no hay nada para confirmar (decisión 10).
   - La respuesta dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo, que quedó anotado que se
     destrabó y sigue en curso; en el de la de comunicaciones, qué falta para revisarla, con un ejemplo
     sacado del criterio para que lo acepte o lo escriba con sus palabras; el próximo paso, aparte y al
     final.
   - La respuesta no dice: que la de comunicaciones quedó entregada, en revisión o terminada; que Ismael se
     enteró o se va a enterar; que la del PLC está terminada; otra vez la pregunta de quién lo destraba.
   - Estado después: tema abierto, la entrega de comunicaciones, esperando lo que falta.

## Qué mide

- **Garantías (5b):** no inventa (ni una causa con palabras de otra tarea, ni un motivo que Marcos no
  dio); no confunde la tarea (la fecha del paso 2 va a la de comunicaciones, el cable al PLC; el switch del
  paso 6 es de comunicaciones; el "termine" del paso 8, de comunicaciones); ningún aviso a Ismael con una
  fecha en la tarea equivocada, tampoco si el paso 2 se leyó mal y Marcos lo corrigió dentro del margen
  para corregir (pasos 3 a 5), ni uno sin el porqué mientras Marcos todavía puede darlo; una pregunta por
  vez (pasos 2 y 3).
- **El formato:** el corredor lo mide solo en cada mensaje (`comprobar.fallas_de_formato`), como en la
  conversación 20.
- **Falla de comprensión:** pegar la fecha a la tarea que se nombró primero; meter en la causa o en el
  motivo palabras que eran de la otra tarea; tomar el switch como causa del bloqueo. En el paso 2, la
  pregunta de duda (b) no es una falla: el corredor la marca y se juzga leyendo la transcripción. Lo mismo
  la corrección del paso 3 después de una lectura equivocada del paso 2.
