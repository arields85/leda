# Conversaciones de prueba

Son la evidencia de que la conversación del Motor funciona. Cada una es un hilo que una persona puede
seguir de arriba abajo y que dice qué tiene que pasar en cada paso, sin dictarle a Leda qué palabras usar.

- **Son la regresión de cada hallazgo** (`AGENTS.md`, "Cómo pensamos juntos", punto 12): un hallazgo de
  conversación se escribe primero acá, y la conversación queda como su prueba.
- **En la Etapa 2, cada una corre cinco veces contra la IA real** (ADR 0018, decisión 5b): las garantías
  tienen que cumplirse 5 de 5 veces y la comprensión al menos 4 de 5; la vez que Leda no entiende, pregunta.
- **Se corren solas con el corredor** ("El corredor", abajo): cada `.md` tiene al lado su YAML con lo
  que se comprueba solo, y el `.md` sigue siendo la fuente.

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
18. [`18-habla-del-mundo.md`](18-habla-del-mundo.md): un avance, una previsión antes de la hora en que
    Leda escribe por su cuenta y el pedido de estado del día previsto; Leda cuenta quién se entera de qué
    y cuándo, y qué va a hacer ella, nunca el estado interno de un aviso o de un pedido.
19. [`19-palabras-de-todos-los-dias.md`](19-palabras-de-todos-los-dias.md): una reasignación con la oferta
    de anotar para cuándo la termina, la fecha que da Marcos, "que es prevision?" y lo que Leda manda por
    su cuenta hasta ese día; Leda dice el hecho concreto con palabras de todos los días y nunca nombra un
    concepto del sistema.
20. [`20-formato-de-los-mensajes.md`](20-formato-de-los-mensajes.md): una consulta de pendientes, dos
    hechos en un mensaje y el aviso a Ismael; Leda escribe breve, un renglón por idea, con 📋, ✏️, 🗓️ y
    ⚠️ al principio del renglón (en cada bloque, la tarea primero), fechas cortas, sin negrita, quien se
    entera dicho en pasiva sobre esa persona y el cierre aparte, al final.
25. [`25-sin-puntuacion.md`](25-sin-puntuacion.md): mensajes de corrido, sin puntuación y con errores de
    tipeo, que mezclan dos tareas; el primero es el literal de la prueba por Telegram real ("con el PLC
    estoy compliacdo, me falta el cable para programar comunicaciones…"). Leda reparte cada hecho en su
    tarea o, si no puede saber a cuál va, pregunta; nunca arma una causa o un motivo con palabras de la
    otra tarea. Es la primera con dos respuestas correctas en un paso: el YAML espera el reparto y la
    pregunta de duda se juzga leyendo la transcripción. Después, Marcos corrige dentro del margen para
    corregir y a Ismael le llega un solo aviso, el de la tarea correcta.
26. [`26-no-interrumpir.md`](26-no-interrumpir.md): el aviso previo de dos tareas llega a su hora mientras
    Marcos cuenta que una se atrasa; el aviso espera 30 minutos sin que Marcos escriba, nunca sale junto
    con una pregunta sin contestar, el de otra tarea sale aparte y no repite lo que se acaba de hablar.
    Hallazgo de la prueba por Telegram real del 2026-10-08; la regla la decidió el usuario el mismo día.
    Corre desde la D5 de la C-3d: el hilo principal, con su YAML; sus variantes las prueban las pruebas
    del motor (`tests/motor/test_no_interrumpir.py`).

La entrega y la aprobación (circuitos 7 y 8; `odd/tasks/fase-c.md`, decisiones 1 a 3, y ADR 0019):

21. [`21-entrega-con-evidencia.md`](21-entrega-con-evidencia.md): "termine el plc" con un álbum de fotos,
    sin decir todo el criterio: Leda pregunta sólo lo que falta, con un ejemplo que Marcos acepta;
    la vista previa muestra también lo mandado durante la tarea, que entra sólo si queda; sacar una
    pieza, el botón de una vista previa vieja, una foto nueva con un "dale" que no vale (la guarda
    escrita) y el "dale" que sí; la tarea pasa a revisión y a Ismael le llega el aviso con las fotos y un
    enlace a la página de la tarea. Toma los pasos "Para la prueba de la entrega" de la 10 y la 11.
22. [`22-falta-evidencia.md`](22-falta-evidencia.md): una foto sin ninguna entrega abierta (Leda pregunta
    para qué es), un "listo" al que le falta lo que pide el área (Leda dice qué falta y no la pasa a
    revisión) y un video que no entra (Leda lo dice y propone un enlace o uno más corto).
23. [`23-aprobacion.md`](23-aprobacion.md): "aprobado" que cierra; "aprobado" que no cierra porque falta
    otra cosa, dicho con honestidad; un pedido de cambios con su comentario; "aprobado, pero que
    revise…", con una sola pregunta y dos botones; quien no aprueba esa tarea intenta aprobarla; y la
    entrega otra vez después del pedido de cambios, que no vuelve a pedir lo que ya dijo la primera
    (decisión 23).
24. [`24-quien-aprueba-no-contesta.md`](24-quien-aprueba-no-contesta.md): un recordatorio a quien aprueba
    por día hábil hasta que decide; el segundo avisa que al día siguiente se entera quien está arriba
    (Marcos → Ismael), que al tercero recibe un aviso sólo informativo, una vez, y después que se
    destrabó; sin nadie arriba, sólo el recordatorio; al responsable, nada.
27. [`27-entrega-contra-el-criterio.md`](27-entrega-contra-el-criterio.md): lo que Marcos describe al
    entregar no dice todo el criterio de aceptación; Leda dice qué falta con un ejemplo sacado del
    criterio, se lo vuelve a dar cuando pregunta qué poner, no la entrega aunque insista, y con el
    ejemplo aceptado la entrega se confirma; una foto retirada deja la entrega incompleta y Leda pide
    la correcta mientras la revisión espera; la de una tarea que nunca se arrancó se recibe igual y
    queda arrancada al entregarla (decisiones 10, 14 y 15 del usuario, 2026-10-08; C-3d, D3).
28. [`28-entregas-en-una-lista.md`](28-entregas-en-una-lista.md): tres entregas que salen juntas van
    en un solo mensaje, una lista con un botón por tarea ("Ver" y la tarea); al tocar uno, o al
    escribir "mostrame la del plc", aparece esa entrega con sus fotos, el enlace y Aprobar y Pedir
    cambios; "aprobado pero que revise…" lleva una sola pregunta y, si la respuesta no elige, Leda
    no decide ni la repite: la entrega sigue esperando con los dos botones; después de decidir una,
    lo que queda por revisar, y al día hábil siguiente, los recordatorios en una lista (decisiones
    12, 17 y 18 del usuario, 2026-10-08; C-3d, D4).
29. [`29-cambia-quien-revisa.md`](29-cambia-quien-revisa.md): la plataforma cambia quién aprueba el
    trabajo de Mariano mientras dos entregas esperan; el aviso que no había salido le llega al nuevo,
    al nuevo le llega también el que ya había salido, y el botón del aviso viejo le dice al anterior
    que esa tarea ya no la revisa él, sin cambiar nada (decisión 16 del usuario, 2026-10-08; D4).
30. [`30-pregunta-sin-contestar.md`](30-pregunta-sin-contestar.md): una pregunta de Leda sin contestar
    frena los otros temas hasta su única repetición del día, a las 4 horas; 4 horas después sale
    aparte el tema siguiente, y al cerrarse una de las dos preguntas el código trae la otra en un
    mensaje aparte, en los dos órdenes de respuesta (decisión 21 del usuario, 2026-10-08; D5b).

La página de la tarea (ADR 0019, decisión 7):

31. [`31-pedir-el-enlace.md`](31-pedir-el-enlace.md): pedir por chat el enlace a la página de una
    tarea: Marcos, el de una suya; Ismael, el de una de Marcos ya terminada y el de una de Lucas,
    que no están en su lista (es la autoridad final); Nahuel, el de una que no puede ver, y Leda le
    dice que ése no se lo puede pasar, sin enlace y sin decir quién la ve (lo que quedó de la
    porción 4 de la C-3).

**La 21 y la 22 corren desde la porción 2 de la C-3** (la entrega con evidencia y la política por tipo),
con su YAML para los pasos que esa porción cubre:

- **La 21**, entera desde la porción 3a: el paso 7 (el 6 hasta el 2026-10-08, cuando se sumó la
  pregunta de a quién se le avisó) es el aviso a Ismael redactado por el motor, con las
  fotos adjuntas en el álbum que sigue al texto y, desde la porción 3b, los botones Aprobar y Pedir
  cambios con el texto. El enlace a la página de la tarea (porción 4) queda anotado en el YAML, sin
  esperarse todavía.
- **La 22**, entera, con una diferencia anotada en su YAML: en el paso 5 el enlace solo cubre el archivo
  y falta cómo se probó (el reparto es por las clases; con el archivo del paso 6 queda como dice el
  `.md`). En el paso 8, el aviso a Ismael queda guardado y sale terminado el margen para corregir.
  Desde la D3 de la C-3d, el "listo" del paso 3 tampoco dice lo que pide el criterio de aceptación, y
  Marcos acepta el ejemplo en el paso 7.
- **La 27**, entera, desde la D3 de la C-3d. Su política de evidencia es más corta que la del pack
  (`evidencia` en su YAML), para mirar sólo el criterio.

**La 23 corre desde la porción 3b de la C-3** (la hoja de aprobación), entera, con tres pasos de Leda que
el hilo da por hechos (4b, 9b y 9c) y el paso 10 aparte (`aparte: true`: por el motor y sin
comprobarlo). Usa más personas que Marcos e Ismael: Mariano y Ariel (los aprueba Ismael) y Lucas (lo
aprueba Martín). Desde la porción 3c, el paso 3 espera también el primer recordatorio a Ismael de las
tres entregas que siguen esperando (el lunes es el día hábil siguiente al de las entregas).

**La 24 corre desde la porción 3c de la C-3** (quien aprueba no contesta), entera, con Nahuel (lo
aprueba Marcos). El aviso a Ismael del tercer día sale en un envío con su propio recordatorio
(mecánica §10): el YAML mira el aviso de la trabada, y el recordatorio lo miran las pruebas del
motor. Suma tres momentos que el hilo da por hechos: el lunes 2 a las 09:00, cuando la escalera ya
guardó los recordatorios del día (así el de Ismael se omite al decidir), el aviso de la aprobación a
Nahuel (paso 10) y los dos días siguientes sin nada (paso 10b).

**La 28 y la 29 corren desde la D4 de la C-3d**, enteras. Un botón que muestra una entrega se nombra
en el YAML por la clave de su tarea (`Ver TAB`, para "Ver Cablear tablero de la máquina 3"), al
esperarlo y al tocarlo; un paso escrito o tocado puede esperar las fotos y el enlace de su respuesta
(`fotos`, `enlace`), como lo que Leda manda por su cuenta; y un paso puede cambiar quién aprueba el
trabajo de una persona, como lo haría la plataforma (`cambia_quien_aprueba`, con `de` y `a`), antes
de sus relojes.

**La hoja de aprobación** (porción 3b): un paso puede tocar el botón del aviso de una de varias entregas
(`toca: Pedir cambios` con `de_la_tarea`); lo que Leda manda por su cuenta puede esperar sus botones
(`botones`), y los efectos suman las decisiones de quien aprueba (`aprobaciones`: la tarea, la decisión
y de quién). Cada tarea lleva su criterio de aceptación (`criterio`, en el YAML y en el estado inicial
del `.md`), concreto y comprobable como lo pide la mecánica §13 (C-3d, D1): sin él, ninguna se podría
cerrar al aprobarla, y la entrega lo va a comparar con lo que la persona describe (decisión 10 de
`odd/tasks/fase-c.md`). `carga.py` tiene uno de reserva, también concreto, para una tarea que no
diga el suyo.

**La 12 (paso 6) y la 25 (paso 8) esperan todavía que la entrega no se reciba por chat** (`no_por_chat`):
desde la porción 2 la entrega muestra la vista previa (o, en la 25, no se puede porque la tarea de
comunicaciones no arrancó). Sus YAML se actualizan con la porción 2: `PENDIENTE` (`odd/tasks/fase-c.md`).

Las cuatro primeras son las cuatro respuestas de 5a; de la 5 a la 12, cada una aplica al recordatorio una
de las ocho situaciones generales de la decisión 4. La 15 suma la jugada `informar_avance` (decisión del
usuario, 2026-10-05; ADR 0018, decisión 9b). La 16, la regla de la tarea vencida (decisión del usuario,
2026-10-05; ADR 0018, decisión 9j). La 17, la jugada `destrabar` (decisión del usuario, 2026-10-05;
ADR 0018, decisión 9l). La 18, hablar de lo que pasa en el mundo y no de la cocina (decisión del usuario,
2026-10-06, de la prueba por Telegram real; Etapa 3, E3-6). La 19, decir el hecho con palabras de todos
los días y no los nombres del sistema (decisión del usuario, 2026-10-07, de la prueba por Telegram real).
La 20, el formato de los mensajes (pedido del usuario, 2026-10-07, al aprobar M3; segunda y tercera
vuelta el mismo día, después de verlo en Telegram). La 25, los mensajes sin puntuación que mezclan dos
tareas (hallazgo de la prueba por Telegram real del 2026-10-07).

## El corredor

Vino de la prueba chica en la E3-8, para que la regresión sobreviviera a su borrado (2026-10-07).
Corre cada conversación por el código de verdad: carga su estado inicial (`carga.py`), corre cada paso
con el reloj en el momento que dice el `.md` (`corredor.py`), compara lo que pasó con lo esperado y
clasifica cada diferencia como garantía, comprensión o motor (`comprobar.py`). Aparte, mide el
formato de cada mensaje de Leda, respuesta o aviso, sobre lo que escribió la IA y sin el saludo del día
(`comprobar.fallas_de_formato`, segunda y tercera vuelta del formato, 2026-10-07): sin negrita; el
nombre completo de una tarea en un renglón con 📋 (solo) o 🗓️, una sola vez; ningún renglón con 📅; en
un bloque con una tarea, su renglón con 📋 primero; las marcas, sólo al principio de su renglón;
nunca Leda en primera persona avisándole o notificándole a otra persona; ningún renglón de más de 140
caracteres; fechas cortas; la pregunta, una sola y en el último renglón; que no hace falta responder,
en el último renglón; el cierre solo y con un renglón en blanco antes. Una falla de formato es de su
propia clase (`formato`, la columna F del informe) y no cambia la de las otras tres. Las IA del corredor
están en `grabar.py`: la guionada con las jugadas esperadas, la que graba y la que repite. El techo de
gasto y la libreta, en `gasto.py`; el informe de cada ronda, en `informe.py`; el comando, en `correr.py`.

**El motor** (`motores.py`): `--motor leda.motor`, el definitivo, es el único y el de omisión; hasta el
2026-10-07 también corría el de la prueba chica, para la regresión de la E3-8. El informe, la libreta del
gasto y cada grabación dicen qué motor corrió.

```
python -m tests.conversaciones.correr --ia guionada --veces 1          # en seco, sin gasto
python -m tests.conversaciones.correr --ia sol --veces 5 --paralelo 5 --grabar tests/conversaciones/grabaciones
python -m tests.conversaciones.correr --ia nan/deepseek-v4-flash --veces 5 --paralelo 5
python -m tests.conversaciones.correr --repetir tests/conversaciones/grabaciones/03-leda.motor-sol-2.json
```

**La IA:** `--ia PROVEEDOR/MODELO`, con cualquier proveedor de `leda.llm.BASE_URLS`, o un nombre corto:
`sol`, `luna` y `luna-pro` (GPT-6 sol, luna y luna pro, por OpenRouter), `deepseek-flash` y `glm-flash`
(`deepseek-v4-flash` y `glm5.3-flash`, por `nan`), `sol61` y `sonnet`. La clave es la del proveedor:
`LEDA_OPENROUTER_API_KEY` para OpenRouter y `LEDA_LLM_API_KEY` para los demás.

**Los parámetros de la IA:** `--parametros '<json>'` (o `--parametros-archivo ARCHIVO`) son los mismos de
`model_config.parametros` (`timeout_s`, `plazo_s`, `tope_jugadas`, `tope_redaccion`, `cuerpo_extra`, que
se suma al pedido); uno que no vale no corre. `glm-sin-razonar` y `deepseek-sin-razonar` traen el modelo
de `nan` con los suyos para que no razone por dentro, y `--parametros` se suma a ellos. Quedan en la
cabecera del informe y en la libreta. `nan` puede guardar en caché los pedidos idénticos: sus
repeticiones no son muestras del todo independientes (lo dice el informe).

Cada corrida va en una base nueva del servidor de `LEDA_TEST_DB_URL` (`.env.test`), copia de una
plantilla, y se borra al terminar; nunca toca `leda`, `leda_flujo` ni `leda_motor`. El transporte es
falso. Con una IA real la clave sale del entorno y nunca se imprime. **El techo:** antes de empezar se
estima la ronda; si con eso el gasto pasa de USD 30, no corre (`--pasar-el-techo`, sólo con el OK del
usuario); avisa desde el 80 %. Con un proveedor que no informa el costo (`nan`), la ronda no se estima
ni cuenta para el techo, y la libreta anota los tokens con el precio desconocido. **El crédito:** en una
ronda por OpenRouter, antes de empezar se le pregunta cuánto le queda a la cuenta y, si no alcanza, no
corre (sale con 3); un HTTP 402 a mitad de ronda la corta (sale con 3) y las corridas que lo tuvieron
quedan inválidas, aparte en el informe. La cuenta queda en
`resultados/gasto.json` y el informe de la ronda, con sus transcripciones, en `resultados/` (las
grabaciones crudas, en `grabaciones/`, no se versionan). La comprensión automática del informe es
provisional: la que vale es la lectura del usuario.

**La entrega** (porción 2 de la C-3): un paso puede **mandar** fotos, videos o archivos (`manda`, con
`que` y, si hace falta, `nombre` o `mb`; con o sin `escribe`), que se guardan como los guarda el adaptador
(varias juntas son un álbum; lo que pasa de los 20 MB del canal llega rechazado); **tocar** un botón por
su etiqueta (`toca: Confirmar`) y uno viejo (`vieja: true`, el de la pregunta anterior que lo ofreció). El
estado inicial puede traer la política de evidencia por área (`evidencia`, con las clases y las palabras
de cada tipo de `espacios/corework.yaml`) y lo que la persona dijo que era de una tarea antes de
entregarla (`mandado_antes`). Los efectos suman las piezas de evidencia (`evidencias`, por su clase y lo
que cubren), los retiros (`retiradas`) y los archivos dichos de una tarea (`archivos_de_tarea`). Lo que
Leda manda por su cuenta puede esperar sus fotos adjuntas (`fotos`, cuántas salieron en el álbum que
sigue al texto); un álbum que sale sin su texto antes es una falla de garantía (porción 3a).

**Lo escrito es lo confirmado** (C-3d, D1, de la falsa alarma de la 21 en la primera ronda con la IA
real). La evidencia sale de una vista previa que la persona confirma, así que la garantía es que la
cocina escriba lo último que la persona confirmó, no el camino ideal del YAML: el corredor lee las
vistas previas confirmadas en el paso (`confirmadas`, cada una con sus piezas) y compara con ellas
las piezas escritas de esa tarea. Si son lo confirmado y difieren de lo esperado, la falla es de
comprensión (del motor, si las jugadas del paso eran las esperadas): la IA leyó distinto en algún
paso, pero no se escribió nada que nadie confirmara. Siguen siendo de garantía una pieza que no es lo
confirmado (de más, de menos o que cubre otra cosa) y una pieza de una tarea que nadie confirmó en el
paso. Toda falla de filas (evidencia, previsiones, avisos y las demás) muestra la lista entera de lo
escrito (`escrito`) junto a lo que sobra (`de_mas`) o lo esperado que falta (`faltan`).

**Un dato opcional de una jugada** (`puede_traer`): una jugada esperada puede nombrar datos que pueden
venir o no. Sólo valen los que la ficha de esa jugada declara opcionales (`fichas.py`, `opcional`):
un YAML no afloja más de lo que permite la ficha, y uno que lo intenta es un error del YAML. Si el
dato viene, uno libre (un comentario, un motivo) tiene que ser palabras de la persona; uno
estructurado con su valor en lo esperado (`{nombre: confirmar, tarea: COM, puede_traer: [tarea]}`)
tiene que ser ése. No es una regla para todos los opcionales: un motivo o un comentario que la
persona no dio como tal sigue siendo una falla donde el YAML no lo permite (la 08: "no llegó al 30"
guardado como motivo le llegaría a Ismael).

Sus pruebas (`test_corredor.py`, `test_comprobar.py` y `test_gasto.py`) están en la suite de siempre.

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
  ellas (mecánica §10 junta en un envío los mensajes automáticos del día) es otra conversación. Es una sola
  hora para todo lo que Leda manda por su cuenta (la escalera, los avisos guardados, también a otra persona,
  y el pedido que sigue a un avance), la que dicen los hechos y a la que llega el reloj adelantado de la
  prueba por Telegram (`leda.motor.tiempo`, `HORA_DE_SALIDA`).
- **El margen para corregir** (decisión del usuario, 2026-10-07; conversación 25): un aviso a otra persona
  por algo que alguien dijo (la previsión nueva y su corrección, al referente) espera además diez minutos
  (o los del espacio, `margen_para_corregir_minutos`) antes de salir, con el horario encima: una corrección
  dentro de ese margen lo retira antes de que llegue. Por eso, en las conversaciones, el aviso a Ismael sale
  diez minutos después del mensaje de Marcos, y los hechos dicen esa hora (`leda.motor.margen`). Lo que Leda
  manda por su cuenta no lo espera.
- **No interrumpir una conversación** (decisión del usuario, 2026-10-08; conversación 26): lo que Leda manda
  por su cuenta a una persona espera 30 minutos desde lo último que esa persona escribió o tocó (o los del
  espacio, `no_interrumpir_minutos`), con el horario encima; con una pregunta de Leda sin contestar, ningún
  aviso sale junto con ella. Por eso, en una conversación, un aviso a quien acaba de escribir sale recién
  cuando pasan esos 30 minutos, y los hechos dicen esa hora (`leda.motor.no_interrumpir`). A otra persona
  no la demora.

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
  prueba de la entrega" y en la entrega (conversaciones 21 y 22): el recordatorio no confirma nada. El
  código comprueba la guarda: lo último que la persona vio, en un mensaje anterior, y sin cambios.
- `guardar_para_la_entrega`: la persona dice de qué tarea es una foto o un archivo que mandó sin
  entregarla; queda para mostrárselo en la entrega, sin ser evidencia (conversación 22).
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
- `entregar`: la persona dice que terminó una tarea; con la evidencia completa, Leda muestra la entrega
  para confirmar (conversaciones 21 y 22).
- `aprobar` y `pedir_cambios`: quien aprueba decide sobre una entrega, directo cuando es claro
  (conversaciones 23 y 24).
- `pedir_enlace`: la persona pide el enlace a la página de una tarea; sale sólo si puede verla
  (conversación 31).

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
