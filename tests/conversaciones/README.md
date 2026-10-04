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

1. [`01-arranque.md`](01-arranque.md): "arranqué" después del aviso del día anterior al vencimiento.
2. [`02-nueva-prevision.md`](02-nueva-prevision.md): "llego el 27, el proveedor se demoró"; la fecha
   comprometida no cambia y el referente se entera.
3. [`03-bloqueo.md`](03-bloqueo.md): "estoy trabado, falta el repuesto"; la escalera se detiene.
4. [`04-sin-respuesta.md`](04-sin-respuesta.md): no contesta; el recordatorio llega el día hábil siguiente.
5. [`05-varias-cosas.md`](05-varias-cosas.md): un inicio y una nueva previsión, de dos tareas, en un mensaje.
6. [`06-correccion.md`](06-correccion.md): "no, era la otra tarea".
7. [`07-cancelar.md`](07-cancelar.md): "dejá, no importa" con una pregunta abierta.
8. [`08-cambio-de-tema.md`](08-cambio-de-tema.md): otro tema con uno abierto; tres salidas.
9. [`09-duda.md`](09-duda.md): no se sabe de qué tarea habla; se elige con opciones.
10. [`10-escrito-en-lugar-de-boton.md`](10-escrito-en-lugar-de-boton.md): escribir en lugar de tocar,
    con la guarda de la decisión 2, también cuando lo mostrado cambió.
11. [`11-algo-vencido.md`](11-algo-vencido.md): un botón viejo, una vista previa reemplazada y un aviso
    guardado que ya no corresponde.
12. [`12-fuera-de-la-lista.md`](12-fuera-de-la-lista.md): un pedido que no es ninguna jugada, frente a una
    jugada que existe pero no se puede hacer ahora.
13. [`13-jev-dos-tareas-iguales.md`](13-jev-dos-tareas-iguales.md): dos tareas parecidas avisadas juntas;
    lo correcto es preguntar (ADR 0018, decisión 7).
14. [`14-jev-el-estado-decide.md`](14-jev-el-estado-decide.md): dos tareas parecidas, pero el estado de la
    conversación dice cuál es.

Las cuatro primeras son las cuatro respuestas de 5a; de la 5 a la 12, cada una aplica al recordatorio una
de las ocho situaciones generales de la decisión 4.

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

Un paso marcado `[sólo si …]` corre únicamente si un punto `PENDIENTE` se decide de esa manera. Cuando el
usuario decida, el paso se integra o se borra.

### Qué dice cada flecha

La flecha describe **qué** tiene que pasar, nunca **cómo lo dice Leda**: la IA redacta libre a partir de
los hechos que informa el código (la regla del mozo, `AGENTS.md`, punto 11). Cada flecha se divide en partes
que se pueden comprobar una por una:

- **Jugadas:** las que la IA tiene que elegir de la lista cerrada (ADR 0018, decisión 1), con su tarea y
  sus datos; o "ninguna de la lista".
- **Efecto:** lo que cambia en la base (estado, eventos, avisos encolados, auditoría), o "ninguno".
- **Confirmación:** si hace falta antes del efecto.
- **La respuesta dice / no dice:** los hechos que tiene que contener y los que no puede contener ("el
  mensaje dice", cuando lo inicia Leda).
- **Botones:** los que se ofrecen, sólo donde la constitución §8 los admite (elegir entre opciones que la
  persona no conoce de memoria, algo con más de una lectura, un pedido de ayuda y las confirmaciones de §7).
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
  suponen la restricción de horario prendida; si la Etapa 2 la apaga, las horas se trasladan.
- Ninguna cadencia del espacio (los lunes 09:15, los miércoles, los viernes) cae en el período de estas
  conversaciones: cómo convive el recordatorio con ellas es otra conversación.

### Calendario de referencia

D es el día de la prueba. Las conversaciones usan octubre de 2026, sin feriados en el período: jueves 22,
viernes 23, lunes 26, martes 27, miércoles 28, viernes 30 y miércoles 4 de noviembre. Al correrlas otro día
se corren todas las fechas juntas, también las que escriben las personas ("el 27").

### Nombres de trabajo de las jugadas

La lista cerrada se declara en la Etapa 2. Estos nombres sirven sólo para leer las conversaciones; lo que
importa es el significado:

- `anotar_inicio`: la persona dice que arrancó una tarea.
- `anotar_prevision`: la persona da una fecha nueva en la que va a llegar y, si lo dice, el motivo.
- `anotar_bloqueo`: la persona dice que no puede avanzar y, si lo dice, por qué.
- `elegir`: la persona elige una de las opciones que Leda le ofreció, tocando o escribiendo.
- `confirmar`: la persona confirma lo último que Leda le mostró (decisión 2).
- `corregir`: la persona corrige algo que acaba de decir o que Leda tomó mal.
- `cancelar`: la persona deja sin efecto el tema abierto.
- `seguir`, `dejar_para_despues`: dos de las tres salidas ante un cambio de tema; la tercera es `cancelar`.

## Puntos `PENDIENTE`

Ninguna conversación los resuelve. Cada paso que depende de uno lo cita con su número.

- **P1. ¿Anotar el inicio lleva vista previa y confirmación?** (a) No: la persona informa un hecho
  (constitución §3) y §7 no lo lista. (b) Sí, como la entrega del ADR 0018, decisión 4. Conversaciones 01,
  05, 06, 09, 10, 11, 13 y 14.
- **P2. ¿Anotar un bloqueo lleva vista previa y confirmación?** Las mismas dos opciones. Conversación 03.
- **P3. ¿Anotar la nueva previsión y avisar al referente lleva confirmación de quien la pide?** (a) No: es
  un aviso de coordinación de un comportamiento decidido (ADR 0017, decisión 4; mecánica §10). (b) Sí, una
  confirmación de la previsión. (c) Borrador, confirmación y pregunta de atribución, si el aviso cuenta como
  mensaje privado no rutinario (constitución §7). Conversaciones 02, 05, 08, 10 y 11.
- **P4. ¿El aviso del día anterior y el recordatorio llevan botones?** (a) No: §8 reserva los botones para
  elegir, para lo ambiguo, para la ayuda y para las confirmaciones, y la persona contesta escribiendo.
  (b) Sí, como atajos de las respuestas más comunes. Todas las que tienen un aviso.
- **P5. Varias cosas en un mensaje: ¿cuál atiende Leda primero, y la segunda va en la misma respuesta si no
  pide nada?** (a) Primero la del tema abierto. (b) En el orden del mensaje. (c) Un orden fijo por jugada,
  como en el ejemplo de la decisión 1. Conversación 05.
- **P6. ¿Qué hechos lleva el aviso al referente de una nueva previsión?** Seguro: la tarea, la previsión y
  su motivo (ADR 0017, decisión 4). Abierto: si lleva la fecha comprometida, si dice que la fecha se cambia
  en la plataforma. Conversaciones 02, 05 y 08.
- **P7. El aviso al administrador de lo que no está en la lista:** por qué canal llega, cómo se agrupan los
  repetidos (ADR 0018, decisión 1) y si Leda le dice a la persona que avisó. Conversación 12.
- **P8. ¿La lista cerrada de la prueba chica incluye jugadas de otros circuitos**, como la entrega ("ya la
  terminé") o qué tengo pendiente? Si no, son algo que no está en la lista y generan el aviso al
  administrador. Las conversaciones evitan depender de esto.
- **P9. Después de anotar un bloqueo, ¿Leda pregunta algo más o avisa a alguien?** (a) Nada más: es el
  primer paso de la decisión 3a, sin la persecución (5a). (b) Pide lo mínimo para entenderlo (mecánica §8,
  paso 2). (c) Avisa al referente. Conversación 03.
- **P10. ¿Leda contesta fuera de horario a quien le escribe?** (a) Sí: no es un mensaje que inicia ella
  (mecánica §10 distingue la respuesta del mensaje automático). (b) No: espera a las 09:00 (constitución
  §8). Conversación 11.
- **P11. ¿Cómo se corrige un hecho ya anotado en la tarea equivocada?** (a) Con un evento de corrección que
  devuelve la tarea a su estado anterior, auditado junto al original. (b) Si P1 lleva confirmación, la
  corrección llega antes de confirmar y no hay nada que deshacer. Conversación 06.
- **P12. ¿El recordatorio del día del vencimiento espera respuesta?** (a) Sí, como mensaje de seguimiento
  (respuesta antes del cierre de la jornada, según el pack) y abre la cuenta de quién no contestó (ADR
  0017, decisión 6). (b) No: la escalera avanza sólo por fecha. Conversación 04.
- **P13. ¿Las tres salidas de un cambio de tema se ofrecen con botones?** (a) Sí: es elegir entre
  opciones (§8). (b) No: se ofrecen en el texto y la persona contesta escribiendo. Conversación 08.
- **P14. ¿Cuándo retoma Leda un tema que quedó para después?** (a) Apenas se cierra el tema nuevo. (b) En el
  próximo contacto con la persona. (c) Sólo cuando la persona lo saca. Conversación 08.
- **P15. ¿Qué pasa con un aviso guardado que dejó de corresponder antes de salir?** (a) Se redacta con los
  hechos vigentes al enviarlo (ADR 0018, decisión 8). (b) No sale, se registra la omisión y se le dice a
  quien lo causó. (c) No sale el viejo y sale uno con lo vigente. Conversación 11.
- **P16. Un pedido de reasignación, ¿a quién lo deriva Leda?** (a) Al administrador que maneja la
  plataforma. (b) A quien decide la reasignación (Ismael, Dirección). Conversación 12.
