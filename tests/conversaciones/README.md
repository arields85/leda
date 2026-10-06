# Conversaciones de prueba

Son la evidencia de que la conversación del Motor funciona. Cada una es un hilo que una persona puede
seguir de arriba abajo y que dice qué tiene que pasar en cada paso, sin dictarle a Leda qué palabras usar.

- **Son la regresión de cada hallazgo** (`AGENTS.md`, "Cómo pensamos juntos", punto 12): un hallazgo de
  conversación se escribe primero acá, y la conversación queda como su prueba.
- **En la Etapa 2, cada una corre cinco veces contra la IA real** (ADR 0018, decisión 5b): las garantías
  tienen que cumplirse 5 de 5 veces y la comprensión al menos 4 de 5; la vez que Leda no entiende, pregunta.
- **Cómo se corren de forma automática lo decide el plan de la Etapa 2.** Esta carpeta tiene sólo las
  conversaciones: ni código, ni arnés, ni datos cargables.

## Las conversaciones

El circuito es el recordatorio y lo que la persona contesta (ADR 0018, decisión 5a).

1. [`01-arranque.md`](01-arranque.md): "arranqué" después del aviso previo al vencimiento.
2. [`02-nueva-prevision.md`](02-nueva-prevision.md): "llego el 27, el proveedor se demoró"; la fecha
   comprometida no cambia y el referente se entera, con el atraso y lo que depende; el seguimiento pasa a
   la previsión (un recordatorio el día del vencimiento y el pedido de estado el día de la previsión).
3. [`03-bloqueo.md`](03-bloqueo.md): "estoy trabado, falta el repuesto"; Leda pregunta quién lo puede
   destrabar, repite la pregunta al día hábil siguiente y, como Marcos no sabe, propone salidas, sin avisar
   al referente; la escalera se detiene.
4. [`04-sin-respuesta.md`](04-sin-respuesta.md): no contesta; desde el vencimiento Leda pide el estado y la
   escalera avanza hasta escalar.
5. [`05-varias-cosas.md`](05-varias-cosas.md): dos hechos de dos tareas en un mensaje, y después uno que
   necesita una pregunta junto a otro que no.
6. [`06-correccion.md`](06-correccion.md): "no, era la otra tarea".
7. [`07-cancelar.md`](07-cancelar.md): "dejá, no importa" con una pregunta abierta.
8. [`08-cambio-de-tema.md`](08-cambio-de-tema.md): otro tema con una pregunta abierta; Leda anota lo
   nuevo y vuelve a la pregunta.
9. [`09-duda.md`](09-duda.md): no se sabe de qué tarea habla; se elige con opciones.
10. [`10-escrito-en-lugar-de-boton.md`](10-escrito-en-lugar-de-boton.md): escribir en lugar de tocar una
    opción; la guarda de la decisión 2 queda marcada para la prueba de la entrega.
11. [`11-algo-vencido.md`](11-algo-vencido.md): un botón viejo, una respuesta fuera de horario y un aviso
    guardado que ya no corresponde.
12. [`12-fuera-de-la-lista.md`](12-fuera-de-la-lista.md): un pedido que no es ninguna de las ocho cosas,
    frente a una reasignación, una entrega, un inicio repetido y "qué tengo pendiente".
13. [`13-jev-dos-tareas-iguales.md`](13-jev-dos-tareas-iguales.md): dos tareas parecidas avisadas juntas;
    lo correcto es preguntar (ADR 0018, decisión 7).
14. [`14-jev-el-estado-decide.md`](14-jev-el-estado-decide.md): dos tareas parecidas, pero el estado de la
    conversación dice cuál es.
15. [`15-avance-vago.md`](15-avance-vago.md): "voy bien, la tengo casi lista" ante el pedido de estado del
    día del vencimiento; Leda anota el avance, la espera sigue abierta y vuelve a preguntar al día hábil
    siguiente sin contarlo como silencio; con la tarea ya vencida, la segunda respuesta sin nada cierto
    lleva la pregunta de para qué día, y la fecha que da Marcos mueve el seguimiento a ella.
16. [`16-vencida-sin-fecha.md`](16-vencida-sin-fecha.md): "arranqué hoy" con la tarea vencida; Leda anota el
    inicio y, en la misma respuesta, pregunta para qué día la va a tener; la fecha que da Marcos es una
    nueva previsión y el seguimiento se mueve a ella.
17. [`17-destrabar.md`](17-destrabar.md): "llego el switch, sigo" con la tarea trabada; Leda cierra el
    bloqueo, la tarea vuelve a su estado de antes, la pregunta de quién lo destraba se cierra y el
    seguimiento vuelve; el día del vencimiento se traba y se destraba otra vez, y Leda vuelve a pedir el
    estado el día hábil siguiente.

Las cuatro primeras son las cuatro respuestas de 5a; de la 5 a la 12, cada una aplica al recordatorio una
de las ocho situaciones generales de la decisión 4. La 15 suma la jugada `informar_avance` (decisión del
usuario, 2026-10-05; ADR 0018, decisión 9b). La 16, la regla de la tarea vencida (decisión del usuario,
2026-10-05; ADR 0018, decisión 9j). La 17, la jugada `destrabar` (decisión del usuario, 2026-10-05;
ADR 0018, decisión 9l).

## Formato de cada conversación

Cuatro partes, siempre en este orden:

1. **Encabezado:** qué prueba, en una línea, y de qué decisión sale.
2. **Estado inicial.** Todo lo que el hilo da por hecho; ningún paso depende de algo que no esté acá:
   - el día y la hora, en el calendario de referencia (abajo);
   - las tareas: título, responsable, referente, vencimiento, estado, bloqueos y dependencias;
   - el estado de la conversación de cada persona (ADR 0018, decisión 3): el tema abierto, los temas que
     quedaron para después y lo último que Leda mostró para confirmar;
   - lo que ya se envió.
3. **Hilo.** Una lista numerada que se lee de arriba abajo, sin tablas ni saltos. Cada paso dice quién
   actúa (Leda, Marcos, Ismael), el texto exacto que la persona escribe o el botón que toca, y una flecha
   `→` con lo que tiene que pasar.
4. **Qué mide.** Las garantías de 5b que ejercita y qué cuenta como falla de comprensión.

Una parte titulada **"Para la prueba de la entrega"**, al final y después de "Qué mide", no corre en la
prueba chica: guarda pasos que
necesitan un circuito que confirma (decisión 9a) y se reescribe sobre la entrega cuando llegue.

### Qué dice cada flecha

La flecha describe **qué** tiene que pasar, nunca **cómo lo dice Leda**: la IA redacta libre a partir de
los hechos que informa el código (la regla del mozo, `AGENTS.md`, punto 11). Cada flecha se divide en partes
que se pueden comprobar una por una:

- **Jugadas:** las que la IA tiene que elegir de la lista cerrada (ADR 0018, decisión 1), con su tarea y
  sus datos; o "ninguna de la lista".
- **Efecto:** lo que cambia en la base (estado, eventos, avisos encolados, auditoría), o "ninguno".
- **Confirmación:** si hace falta antes del efecto. En el recordatorio, nunca (decisión 9a).
- **La respuesta dice / no dice:** los hechos que tiene que contener y los que no puede contener ("el
  mensaje dice", cuando lo inicia Leda).
- **El próximo paso** (definición del usuario, 2026-10-06; ADR 0018, decisión 9, tercera vuelta): todo
  mensaje de Leda termina con algo concreto que va a pasar o que la persona puede hacer, dicho una vez y
  en pocas palabras: lo que Leda va a hacer (por ejemplo, cuándo le vuelve a preguntar), lo que la persona
  puede hacer (por ejemplo, avisar cuando se destrabe) o, si no queda nada pendiente, eso junto con lo que
  sigue. "No hace falta que respondas" solo no cuenta, salvo en los avisos que no piden respuesta (el aviso
  previo, mecánica §10), donde tiene que estar. Vale en todos los pasos, aunque la flecha no lo repita: el
  corredor agrega la casilla para leerlo donde el paso no dice ya cuál es su próximo paso. Un mensaje
  anterior que anunció algo que ya no va a pasar se corrige en el mensaje siguiente.
- **Botones:** los que se ofrecen, sólo donde la constitución §8 los admite (elegir entre opciones que la
  persona no conoce de memoria, algo con más de una lectura, un pedido de ayuda y las confirmaciones de §7).
  En la prueba chica, sólo las tareas como opciones de una duda (decisiones 9b y 9d).
- **Estado después:** cómo queda el estado de la conversación de la persona.

### Reglas de redacción

- Nunca frases de ejemplo de Leda, moldes de preguntas ni palabras nuestras para ella: se describe la
  acción ("pregunta por la causa"), no el texto.
- Las personas escriben como escriben: rioplatense, sin tildes, con errores de tipeo.
- Los nombres son los del proyecto: Leda, la IA, el Motor, circuito, jugada, situación general.

## Datos ficticios

Personas, roles y tareas salen de `espacios/corework.yaml` y `espacios/corework.semilla-ficticia.yaml`:

- **Marcos Tarquini** es el responsable en todas las conversaciones: referente de OT, con cuenta de
  Telegram de prueba y dos tareas en la semilla.
- **Ismael Soschinski** (Dirección) es quien aprueba el trabajo de Marcos (`aprobado_por: ismael`) y el
  destino del escalamiento por falta de respuesta (`escalamiento`, `rol:direccion`). En estas
  conversaciones, "el referente" de las tareas de Marcos es Ismael.
- Los ADR 0017 y 0018 ponen de ejemplo a Ismael como responsable y a Marcos como referente; el pack dice lo
  contrario, y estas conversaciones siguen al pack.
- Las tareas de Marcos: **"Programar PLC de la comprimidora"** y **"Revisar comunicaciones industriales de
  la comprimidora"**, del objetivo "Conectar y automatizar equipos para que produzcan y entreguen datos".
  La conversación 13 suma "Integrar datos de la comprimidora en CoreLabs", que es de Ariel.
- La semilla carga todo a diez días y con una dependencia bloqueante entre las dos tareas de Marcos; cada
  conversación dice en su estado inicial qué vencimiento, qué estado y qué dependencias valen. El plan de la
  Etapa 2 adapta la carga a cada estado inicial.
- Horario del espacio: lunes a viernes, 09:00 a 17:00, con los feriados nacionales. Las conversaciones
  suponen la restricción de horario prendida; si la Etapa 2 la apaga, las horas se trasladan. El horario
  rige para lo que Leda manda por su cuenta; a quien le escribe le contesta a cualquier hora (decisión 9e).
- Las cadencias del espacio (lunes 09:15; miércoles 11:30 y 15:30; viernes 11:00 y 16:15) se suponen
  apagadas, y los mensajes que Leda manda por su cuenta salen a las 10:00: cómo convive el recordatorio con
  ellas (mecánica §10 junta en un envío los mensajes automáticos del día) es otra conversación.

### Calendario de referencia

D es el día de la prueba. Las conversaciones usan octubre y noviembre de 2026, sin feriados en el período:
lunes 19 a viernes 23, lunes 26 a viernes 30 y lunes 2 a viernes 6 de noviembre. Al correrlas otro día se
corren todas las fechas juntas, también las que escriben las personas ("el 27").

El aviso previo sale **tres días hábiles antes del vencimiento** (el valor de CoreWork, decisión 9b): para
una tarea que vence el viernes 23, el martes 20; para una que vence el viernes 30, el martes 27. Es uno solo.

### Nombres de trabajo de las jugadas

La lista cerrada se declara en la Etapa 2. Estos nombres sirven sólo para leer las conversaciones; lo que
importa es el significado:

- `anotar_inicio`: la persona dice que arrancó una tarea.
- `anotar_prevision`: la persona da una fecha nueva en la que va a llegar y, si lo dice, el motivo.
- `anotar_bloqueo`: la persona dice que no puede avanzar y, si lo dice, por qué.
- `elegir`: la persona elige una de las opciones que Leda le ofreció, tocando o escribiendo.
- `confirmar`: la persona confirma lo último que Leda le mostró (decisión 2). Sólo en las partes "Para la
  prueba de la entrega": el recordatorio no confirma nada.
- `corregir`: la persona corrige algo que acaba de decir o que Leda tomó mal.
- `cancelar`: la persona deja sin efecto el tema abierto.
- `dejar_para_despues`: la persona deja el tema abierto para más tarde. Con `cancelar` y contestar la
  pregunta, son las tres salidas de un cambio de tema, que no se ofrecen como menú (decisión 9d).
- `consultar_pendientes`: la persona pregunta qué tiene pendiente; sólo lee (decisión 9g).
- `informar_avance`: la persona cuenta cómo viene una tarea sin un hecho cierto (no dice que la
  terminó, ni para cuándo, ni que está trabada); queda anotado con sus palabras y la espera sigue
  abierta (decisión del usuario, 2026-10-05).
- `destrabar`: la persona dice que la causa de un bloqueo abierto ya no está y la tarea puede seguir;
  el bloqueo se cierra y la tarea vuelve al estado que tenía antes (decisión del usuario, 2026-10-05).

## Decisiones del usuario (2026-10-04)

Las conversaciones dejaban 16 preguntas abiertas (P1 a P16). El usuario las decidió y quedaron en el ADR
0018, decisión 9; las conversaciones ya las aplican.

- **P1, P2 y P3.** El inicio, el bloqueo y la nueva previsión, con su aviso al referente, se anotan directo y
  Leda cuenta qué anotó; si algo está mal, la persona lo corrige (9a).
- **P4.** Sin botones en el aviso previo ni en los recordatorios (9b).
- **P5.** Varias cosas en un mensaje: lo directo, todo en una respuesta; lo que necesita una pregunta, una por
  vez y en el orden en que se dijo (9d).
- **P6.** El aviso al referente lleva la tarea, la previsión, el motivo, la fecha comprometida, los días
  hábiles de atraso (los calcula el código) y lo que depende de ella (9b).
- **P7.** El aviso al administrador va por el bot de administración, sin agrupar repetidos, y a la persona no
  se le dice salvo que pregunte (9g).
- **P8.** Se ejecutan el inicio, la previsión, el bloqueo y "qué tengo pendiente"; "ya la terminé" se reconoce
  y Leda dice que todavía no la recibe por acá, sin avisar al administrador (9g).
- **P9.** "Estoy trabado": Leda pide la causa si falta; con la causa, pregunta siempre quién lo puede
  destrabar (y la repite si no hay respuesta); si la persona nombra a alguien, queda anotado, y si dice que
  nadie, que no sabe o que le toca a ella, Leda propone salidas; el referente se entera sólo por un
  escalamiento (9c, corregida el mismo día y, sin el juicio de la IA sobre la causa, el 2026-10-05).
- **P10.** Leda contesta las 24 horas; los avisos a otros esperan al horario y Leda lo dice (9e).
- **P11.** Un hecho en la tarea equivocada se corrige agregando un hecho de corrección (9f).
- **P12.** El aviso previo, uno solo y tres días hábiles antes, no pide respuesta; desde el vencimiento, cada
  recordatorio pide el estado y la escalera avanza si no hay respuesta (9b).
- **P13 y P14.** Ante un cambio de tema, Leda anota lo nuevo si es directo y vuelve en la misma respuesta a la
  pregunta pendiente, sin menú; si lo nuevo también pide una pregunta, sigue a la persona y vuelve después
  (9d).
- **P15.** Un aviso guardado se vuelve a leer al salir: si ya no corresponde, no sale y se registra la
  omisión; si la previsión volvió a la fecha comprometida, tampoco sale otro (9b).
- **P16.** Una reasignación: Leda dice que no puede y que la decide Ismael, no pasa el pedido ni avisa al
  administrador, y ofrece anotar una nueva previsión si el motivo es el tiempo (9g).

Los tres puntos que estas decisiones dejaron abiertos los decidió el usuario el mismo día (ADR 0018, 9b, 9c
y 9d). Ninguna conversación prueba todavía dos preguntas encadenadas por un cambio de tema.

## Decisiones del usuario (2026-10-05)

- **Un avance sin un hecho cierto** ("voy bien, la tengo casi lista"): se anota con las palabras de la
  persona, la espera sigue abierta y Leda vuelve a pedir el estado el día hábil siguiente, sin contarlo como
  silencio; a la segunda, pregunta para cuándo (9h; conversación 15).
- **Con una previsión posterior al vencimiento, el seguimiento se mueve a la previsión**, sin tocar la fecha
  comprometida: el día del vencimiento, un solo recordatorio que no pide nada; nada cada día hasta la
  previsión; ese día, el pedido de estado como si fuera el vencimiento y, sin respuesta, la escalera desde
  ahí. Una previsión más nueva mueve el ancla; una que vuelve a la fecha comprometida la devuelve al
  vencimiento (9i; conversación 02). El referente recibe información y las decisiones que son suyas, nunca
  trabajo de gestión.
- **Con la tarea vencida, una respuesta sin fecha lleva la pregunta de para cuándo** ("arranqué hoy",
  "voy bien", "sigo con eso"): Leda anota lo que la persona dijo y, en esa misma respuesta, le pregunta
  para qué día la va a tener, una sola pregunta. La respuesta no es algo cierto sobre cuándo: la espera
  sigue abierta y, si no contesta, Leda vuelve a pedir el estado el día hábil siguiente, como después de
  un avance. La fecha que da es una nueva previsión, con su aviso al referente, y el seguimiento se mueve
  a ella. Vale para toda jugada sobre una tarea vencida, no para una (9j; conversaciones 15 y 16). La 15
  la prueba donde 9h y 9j se tocan: el primer avance, el día del vencimiento, no lleva pregunta; el
  segundo, con la tarea ya vencida, sí.
- **Cuando la causa de un bloqueo desaparece** ("llego el switch, sigo"): Leda cierra el bloqueo, directo,
  como lo anotó; la tarea vuelve al estado que tenía antes (mecánica §3); la pregunta de quién lo
  destraba y su espera se cierran; si el bloqueo había detenido el seguimiento, vuelve: antes de su
  fecha, la escalera sigue sola; con el seguimiento ya empezado, Leda vuelve a pedir el estado el día
  hábil siguiente, como después de un avance (9l; conversación 17).
