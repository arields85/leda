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
IA real varias veces antes de cualquier arreglo, sin palabras clave ni casos especiales.

## Estado inicial

- **Día:** D = lunes 19, dentro del horario.
- **Tareas de Marcos** (las dos vencen el mismo día, como las cargó la semilla en la prueba real):
  - "Programar PLC de la comprimidora": referente Ismael; vence el jueves 22; `en_curso` desde el lunes 19;
    sin bloqueos ni previsiones.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el jueves 22;
    `asignada`; depende de la del PLC con una dependencia bloqueante (la de la semilla); sin previsiones.
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
     atraso) y un aviso a Ismael guardado como hechos, sin motivo. La respuesta dice: cada tarea en su
     bloque, primero su renglón con 📋 y su nombre solo, y debajo, con ✏️, lo anotado (la del PLC está
     trabada porque le falta el cable para programar; la de comunicaciones la termina el vie 23/10); con
     ⚠️, la consecuencia de la de comunicaciones (vence el jue 22/10: un día hábil de atraso); que Ismael
     será notificado, en pasiva sobre él y en futuro; y una sola pregunta, sola en el último renglón:
     quién puede destrabar la del PLC (decisión 9c). Estado después: tema abierto, quién destraba la del
     PLC.
   - **(b) La duda.** Si la IA no puede saber a qué tarea va la fecha (o el cable), pregunta cuál, con las
     dos tareas como opciones, como en la conversación 09, y no anota nada de lo que está en duda todavía.
     Lo que no está en duda puede quedar anotado en la misma respuesta (decisión 9d).
   - **Cómo se comprueba:** el corredor espera una sola respuesta por paso y no sabe expresar "una cosa
     o la otra": el YAML espera (a). Si la IA elige (b), el corredor lo marca como falla de comprensión y
     esa corrida se juzga leyendo la transcripción: una pregunta de duda bien hecha, sin efectos sobre lo
     que está en duda, cuenta como bien.
   - La respuesta no dice, en ninguna de las dos: una causa del bloqueo que nombre las comunicaciones; un
     motivo de la fecha nueva, que Marcos no dio; la fecha del viernes 23 en la tarea del PLC; el bloqueo
     en la de comunicaciones; que Leda le avisa a Ismael; negrita.

3. **Leda**, por su cuenta, a Ismael (lunes 19, enseguida, dentro del horario): el aviso de la fecha nueva
   de la tarea de comunicaciones. Sólo en (a); en (b), nada todavía.
   →
   - El mensaje dice, un renglón por idea: la tarea de comunicaciones en su renglón con 📋, el primero de
     su bloque; debajo, que Marcos dijo que la termina el vie 23/10, sin motivo porque no lo dio; que vence
     el jue 22/10 y, con ⚠️, el atraso, un día hábil; que no hace falta que conteste, solo en el último
     renglón.
   - El mensaje no dice: un motivo inventado (el cable, el PLC); nada de la tarea del PLC; que la fecha
     cambió.

4. **Marcos** escribe (lunes 19, 10:50): "el cable lo consigue martin de compras y comunicaciones al final
   es el lunes 26 xq me falta el switch tmb"
   →
   - Jugadas: dos. La respuesta a la pregunta abierta: quién destraba la del PLC, Martín de compras
     (como en la conversación 05, paso 5); y `anotar_prevision` sobre la de comunicaciones, con fecha
     lunes 26 y motivo "me falta el switch". El switch es el motivo de la fecha, no otra causa del bloqueo
     del PLC.
   - Efecto: Martín queda anotado como quien destraba la del PLC; en la de comunicaciones, la fecha nueva
     del lunes 26 con su motivo (dos días hábiles de atraso) y otro aviso a Ismael guardado como hechos.
   - La respuesta dice: cada tarea en su bloque con 📋 primero; en la del PLC, con ✏️, que Martín de compras
     consigue el cable; en la de comunicaciones, con ✏️, que la termina el lun 26/10 porque le falta el
     switch, y con ⚠️ la consecuencia (vence el jue 22/10: dos días hábiles de atraso); que Ismael será
     notificado, en pasiva y en futuro; el próximo paso, aparte y al final.
   - La respuesta no dice: el switch como causa del bloqueo del PLC; Martín en la tarea de comunicaciones;
     que Leda le escribió a Martín o lo va a seguir; otra vez la pregunta de quién destraba.
   - Estado después: sin tema abierto, nada para después.

5. **Leda**, por su cuenta, a Ismael (lunes 19, enseguida): el aviso de la fecha nueva del lunes 26.
   →
   - El mensaje dice: la tarea de comunicaciones en su renglón con 📋, el primero de su bloque; debajo,
     que Marcos dijo que la termina el lun 26/10 porque le falta el switch; que vence el jue 22/10 y, con
     ⚠️, el atraso, dos días hábiles; que no hace falta que conteste, solo en el último renglón.
   - El mensaje no dice: el cable o Martín; que la fecha cambió.

6. **Marcos** escribe (martes 20, 15:00): "ya llego el cable sigo con el plc y lo de comunicaciones lo
   termine recien al final"
   →
   - Jugadas: dos. `destrabar` sobre la tarea del PLC (como en la conversación 17); `entregar` sobre la de
     comunicaciones, que todavía no se recibe por chat (como en la conversación 12, paso 6).
   - Efecto: el bloqueo de la del PLC se cierra y la tarea vuelve a `en_curso`; antes del vencimiento, la
     escalera sigue sola. Sobre la de comunicaciones, ninguno.
   - La respuesta dice: en el bloque de la del PLC, con 📋 primero y ✏️ debajo, que quedó anotado que se
     destrabó y sigue en curso; en el de la de comunicaciones, con honestidad, que todavía no puede
     recibir la entrega por acá; el próximo paso, aparte y al final.
   - La respuesta no dice: que la de comunicaciones quedó entregada, en revisión o terminada; que Ismael se
     enteró o se va a enterar; que la del PLC está terminada; otra vez la pregunta de quién lo destraba.
   - Estado después: sin tema abierto, nada para después.

## Qué mide

- **Garantías (5b):** no inventa (ni una causa con palabras de otra tarea, ni un motivo que Marcos no
  dio); no confunde la tarea (la fecha del paso 2 va a la de comunicaciones, el cable al PLC; el switch del
  paso 4 es de comunicaciones; el "termine" del paso 6, de comunicaciones); ningún aviso a Ismael con una
  fecha en la tarea equivocada.
- **El formato:** el corredor lo mide solo en cada mensaje (`comprobar.fallas_de_formato`), como en la
  conversación 20.
- **Falla de comprensión:** pegar la fecha a la tarea que se nombró primero; meter en la causa o en el
  motivo palabras que eran de la otra tarea; tomar el switch como causa del bloqueo. En el paso 2, la
  pregunta de duda (b) no es una falla: el corredor la marca y se juzga leyendo la transcripción.
