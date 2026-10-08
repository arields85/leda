# Bitácora de flujos: qué se probó, qué salió y qué elegimos

Documento vivo (pedido del usuario, 2026-10-03). Junta en un solo lugar los resultados,
progresos, retrocesos y conclusiones de cada flujo y de cada modelo, para que una sesión
nueva no tenga que reconstruirlos. El detalle de cada prueba de los flujos C está en
`odd/tasks/circuitos-al-flujo-nuevo.md` de la rama `feat/flujo-de-un-mensaje`, congelada el
2026-10-04 (etiqueta `respaldo-flujos-antes-de-d`; se lee con `git show`). Los nombres
(el Motor; flujo A, B, C1…, D) están definidos en `AGENTS.md`, "Nombres que usamos".

Regla de uso: **al cerrar cada prueba real, medición o auditoría se agrega acá su
resultado y, si cambia, la conclusión vigente.** No se borran conclusiones anteriores: se
marcan como reemplazadas.

## Conclusión vigente (2026-10-04)

**Los flujos A, B y C1 a C6 quedan congelados. La línea de trabajo vigente es el Motor, y su
mecanismo para procesar un mensaje es el flujo D: un motor chico de conversación dentro de Leda,
con el alcance recortado al seguimiento.** "El Motor" nombra la línea de trabajo entera; "flujo D",
sólo el mecanismo, para compararlo con los flujos A, B y C. Es una decisión del usuario, tomada
después de la prueba real de la tarea 0-35 y de un análisis adversarial del proyecto
([`../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md)).

Qué se decidió:

- **Un motor de conversación chico dentro de Leda (el flujo D),** sin marcos de terceros (Rasa
  quedó descartado): estado de la conversación explícito, circuitos declarados y situaciones
  generales resueltas una sola vez. Se diseña en tres partes: estado exacto, registro completo de
  la conversación (con los toques de botones) y memoria por integrante, que va después y con su
  propio ADR.
- **Alcance recortado:** por ahora Leda no crea tareas ni objetivos por chat; hace seguimiento.
  Qué circuitos quedan por chat se fija en el ADR 0017 (`PENDIENTE`); las cadencias, los
  recordatorios, los bloqueos, la entrega con evidencia, la aprobación y las consultas son
  ejemplos de seguimiento, no la lista decidida. Principio: *por chat, hechos del trabajo; por la
  web, su estructura.*
- **Carga de tareas:** primero una importación por archivo que hace el administrador; después,
  un formulario en el tablero del cliente.
- **Engram:** sólo como referencia de diseño para esa memoria, no como componente.
- **Dónde sigue el trabajo:** en la rama `feat/motor-de-conversacion`. El diseño se escribe antes
  del código, en el ADR 0017 (alcance) y el ADR 0018 (motor de conversación), en preparación. Los
  flujos anteriores quedan intactos en la etiqueta `respaldo-flujos-antes-de-d` y no se corrigen.

Por qué:

- La conclusión anterior decía que los problemas de C6 se arreglaban dentro de su diseño. La
  prueba real del 2026-10-04 lo desmintió: el bucle del borrador devuelto no volvió, pero
  aparecieron cuatro fallas nuevas de la misma clase (fila "C6 + 0-35" de la tabla), después de
  cinco auditorías que encontraron 14, 7, 7, 6 y 7 hallazgos, sin bajar.
- El análisis mostró que la causa no está en un flujo en particular: la conversación está escrita
  a mano, situación por situación, sin un modelo de la conversación ("Progresos y retrocesos").
- El usuario, al cortar la prueba: "me preocupa que no se pueda seguir un hilo de conversación tan
  simple", "se siente muy estructurado todo", "siento que estamos volviendo a parchear".

La IA: las mediciones de "Modelos" son del flujo C6. Para el flujo D se mantiene GPT-6 sol y falta
volver a medir GPT-6 luna; la elección está `PENDIENTE` en el ADR 0018. **Actualización
(2026-10-06):** medido en las rondas del flujo D ("Rondas automáticas del flujo D"): se queda sol;
luna, descartada.

Qué haría revisar esta conclusión: el resultado de la prueba chica del motor de conversación, con
los criterios de éxito y de corte escritos antes en el ADR 0018. **Actualización (2026-10-06):** la
prueba chica pasó; la conclusión se sostiene ("Prueba por Telegram real del flujo D").

El detalle de la prueba del 2026-10-04 y de la tarea 0-36, que se detuvo y no se retoma, está en
`respaldo-flujos-antes-de-d:odd/tasks/circuitos-al-flujo-nuevo.md`. El trabajo parcial de la
tarea 0-36 quedó archivado, sólo para consulta, en la etiqueta `respaldo-0-36-en-pausa`.

## Primer contacto real del flujo D (2026-10-05): prueba parcial, no M2

Tarea E2-3b de `odd/tasks/prueba-chica-del-motor.md`. **Es una prueba parcial, no el paso M2:**
un guion corto, una sola corrida y sin cambio de tema, corrección ni cancelar (E2-4).

- **Cuándo y con qué:** 2026-10-05, de 12:13 a 12:35, sobre el código de `bcc421a`; base
  `leda_motor`; la IA, GPT-6 sol por OpenRouter; Telegram real con los bots de prueba nuevos y
  tareas ficticias; el usuario operó a Marcos.
- **Qué se probó:** el aviso previo, disparado con `prueba_chica.avisar`, y las respuestas del
  recordatorio: el inicio, la nueva previsión, el bloqueo y quién lo destraba.

| Paso | Qué pasó | Tiempo | Resultado |
|---|---|---|---|
| Aviso previo de "Programar PLC de la comprimidora" | Siete días hábiles hasta el 15 de octubre (el 12 es feriado); no pidió respuesta | — | Bien |
| "arranque" | `anotar_inicio` sobre esa tarea; inicio anotado; respuesta correcta | ~3,9 s | Bien |
| La previsión al 27 con el proveedor como motivo | `anotar_prevision` con fecha y motivo; atraso de 8 días hábiles, bien calculado; la tarea dependiente, nombrada | ~9,4 s | **Hallazgo 1:** la respuesta dijo que Ismael ya estaba avisado, con el aviso sólo guardado |
| "Estoy trabado" por un repuesto | `anotar_bloqueo` con su causa; la IA marcó que no dependía de otro y Leda propuso salidas | ~6,5 s | **Hallazgo 2:** no preguntó quién lo destraba |
| No sabe quién lo compra | `anotar_quien_destraba` con "no sabe", anotado; salidas propuestas | ~8,8 s | Bien |

Sin incidentes, sin errores y ninguna jugada sobre la tarea equivocada.

- **Hallazgo 1 (honestidad, constitución §4).** Causa en la cocina, no en la IA: el hecho del
  aviso al referente traía a quién y a qué hora sale, pero no que todavía no había salido (el envío
  es de la E2-5), y la IA lo leyó como hecho. Arreglo general, no del caso: todo hecho de un efecto
  que pasa después dice su estado explícito (guardado o en cola, sin enviar), también el aviso al
  administrador, y las instrucciones de redacción describen cómo se lee ese estado, sin frases
  (`a9abb05`). Regresión: la conversación 11 y una prueba determinista del hecho.
- **Hallazgo 2 (diseño, ADR 0018, 9c).** La ficha dejaba a la IA juzgar si la causa dependía de
  otra persona (`depende_de_otro`, sin descripción en el esquema), y lo juzgó mal. El usuario cambió
  la regla: todo bloqueo con causa pregunta quién lo puede destrabar, y lo que sigue lo decide la
  respuesta de la persona; un nombre queda anotado como el primer eslabón, y "nadie", "no sé" o "me
  toca a mí" llevan a las salidas (`13e574b`). La persecución completa (ADR 0017, decisión 3a) es
  de la prueba siguiente, no de la Etapa 2 (usuario, 2026-10-05).

**Conclusión del flujo D (2026-10-05), reemplazada el 2026-10-06 por la de las rondas:** el núcleo
funcionó en las cuatro respuestas: la IA eligió la jugada correcta de la lista cerrada, con sus
datos y la tarea correcta, y el código la ejecutó y calculó lo que tenía que calcular. Las dos
fallas estaban en la cocina (un hecho incompleto y un juicio que no le tocaba a la IA), no en el
mecanismo. Es una sola corrida: no reemplaza los criterios 5b y 5c del ADR 0018 ni las corridas
repetidas de la E2-8.

## Rondas automáticas del flujo D (E2-8, 2026-10-05 y 06)

Tarea E2-8 de `odd/tasks/prueba-chica-del-motor.md`. Las conversaciones de prueba (17 desde el
2026-10-05: se sumaron la 15, avance vago; la 16, vencida sin fecha; y la 17, destrabar), cinco
veces cada una contra la IA real, con `python -m prueba_chica.correr`, una base por corrida y el
reloj simulado. Informes, transcripciones y libreta del gasto en `prueba_chica/resultados/`. Las
cifras son las del corredor: garantías (5b) y comprensión provisional (jugadas y efectos).

| Ronda | IA | Corridas bien | Garantías | Costo | Nota |
|---|---|---|---|---|---|
| 1 (2026-10-05, `3bc32b5`, 16 conversaciones) | GPT-6 sol | 57 de 80 | 62 de 80 | USD 2,61 | |
| 1 | GPT-6 luna | 38 de 80 | 50 de 80 | USD 0,14 | Descartada (ADR 0018, decisión 6) |
| 2, primer intento (2026-10-05, noche) | sol, 6.1 sol y Sonnet | — | — | — | Inválido: OpenRouter sin crédito (HTTP 402); informes `ronda2-invalida-*` |
| 2 (2026-10-06) | GPT-6 sol | 81 de 85 | 85 de 85 | USD 2,67 | Sólo falla la 05 |
| 2 | GPT-6.1 sol | 80 de 85 | 85 de 85 | USD 1,96 | Referencia |
| 2 | Claude Sonnet 5.5 | incompleta | — | — | Otra vez sin crédito (28 corridas con 402) |
| 3 (2026-10-06, `ronda3b-sol`) | GPT-6 sol | **85 de 85** | **85 de 85** | USD 2,44 | Comprensión 5 de 5 en las 17; mediana 6,2 s por turno, peor 15,8 s |

- **Ronda 1: el contrato entre la IA y el código.** Las fallas no eran del mecanismo sino de lo
  que la cocina le daba a la IA: hechos sin su significado (el atraso de una previsión leído como
  el de hoy), jugadas sin una definición que las separara (un motivo que no era un porqué; una
  previsión anotada además como bloqueo), ninguna jugada ante la duda, preguntas sobre la propia
  conversación tratadas como algo fuera de la lista y respuestas sin próximo paso. El usuario
  decidió revisar el contrato entero, como reglas generales (ADR 0018, 9k), y sumó la jugada
  `destrabar` (9l) para un bloqueo cuya causa desaparece.
- **Leda sin crédito en la IA** (primer intento de la ronda 2). Se comportó como dice la decisión
  8: ningún efecto sin IA, el texto neutro fijo y un incidente por turno; las garantías se
  sostuvieron también ahí. La libreta contaba como cobradas las llamadas rechazadas; se corrigió,
  y desde la ronda 3 el corredor consulta el crédito antes de empezar y corta la ronda con un 402.
- **Ronda 2: una regla tocada dos veces.** Sólo la 05 falló, con las tres IA, por la regla "una
  sola jugada" que había agregado la ronda 1: el mismo renglón tocado por dos arreglos seguidos,
  un disparador de parar (`AGENTS.md`, punto 4). Se cambió el enfoque en lugar de parchear: las
  jugadas de un mensaje se aplican en orden. Con eso, la tercera y última vuelta de ajuste (9m):
  el próximo paso según la definición del usuario (algo concreto que va a pasar o que la persona
  puede hacer; "no hace falta que respondas" solo vale sólo en los avisos que no piden respuesta),
  lo anunciado que ya no va a pasar se dice, los días de la semana los da el código y una
  respuesta cortada es que la IA no respondió. Sonnet, en sus corridas válidas, entendió bien y
  escribió peor (días de la semana, "ayer", mensajes cortados, dos preguntas en un mensaje).
- **Jev (ADR 0018, decisión 7).** En la ronda 2 con sol, sobre los pasos de las conversaciones 13
  y 14 que eligen tarea: la IA acertó 20 de 20 y Jev 5 de 20 (sólo donde lo correcto era
  preguntar). Jev dijo siempre "ambigua": su verificación da al rival 0,5 o más, o la probabilidad
  no llega al corte, y no ve la conversación. **Jev se retira de la prueba chica** (usuario, 2026-10-06); su código
  sigue en `src/leda`. La deuda `b-0005-b` queda cerrada por esta medición.
- **Ronda 3.** Todo bien en lo automático; la lectura provisional del agente no encontró fallas,
  sólo menores. Antes de Telegram se corrigió lo que la cocina le pasaba (una sola hora, las 10:00,
  para lo que Leda manda por su cuenta; desde cuándo la tarea está en su estado; el pedido de
  estado según el estado real; una entrega que no se recibe, sin inventar otro canal).
- **Gasto de la etapa:** unos USD 19,8 del techo de 30.
- **La lectura de los textos:** el usuario no leyó las corridas (unas 1.000 líneas, "es
  muchísimo"); su juicio sale de la prueba por Telegram real, que reemplaza esa lectura.

**Conclusión vigente del flujo D (2026-10-06):** con GPT-6 sol, la ronda 3 cumple del lado
automático el criterio 5b.1 (garantías 5 de 5 y comprensión 5 de 5 en todas las conversaciones),
sin ningún caso especial (5c.1); las fallas de las rondas 1 y 2 estaban en el contrato entre la IA
y el código y se resolvieron con reglas generales. Se queda sol; luna y Jev salen. No es el paso
M2: faltan la prueba por Telegram real (5b.2) y el juicio del usuario (5b.3).

## Prueba por Telegram real del flujo D (E2-9, 2026-10-06): pasa; paso M2

Tarea E2-9 de `odd/tasks/prueba-chica-del-motor.md`, con la guía de `prueba_chica/README.md`
("Prueba por Telegram real (E2-9)").

- **Cuándo y con qué:** 2026-10-06, de 16:44 a unos 17:10 en hora real; el reloj de Leda recorrió
  del martes 6 al jueves 22 de octubre. El código, el de `a702b39`. La base `leda_motor`, recreada
  desde cero con la semilla ficticia (respaldo previo en `db/respaldos/`). La IA, GPT-6 sol por
  OpenRouter. Los bots de prueba del Motor, con la restricción de horario prendida. El usuario operó
  a Ariel, Ismael y Marcos.
- **Qué se recorrió:** la escalera entera, del aviso previo al escalamiento. Además: el inicio, un
  bloqueo con su causa y quién lo destraba, destrabar, tres previsiones con su aviso al referente,
  la consulta de pendientes y un cambio de tema con una pregunta abierta. También un pedido de
  reasignación, que no se hace por chat, y cancelar una propuesta. El usuario se salió del guion
  varias veces: preguntó qué es una previsión, preguntó por una fecha máxima, rechazó la propuesta y
  contestó días antes de lo previsto.
- **Números:** 16 mensajes de las personas y 27 de Leda, todos enviados. Ningún incidente, ningún
  envío fallido y ninguna jugada sobre la tarea equivocada. Respuesta en una mediana de 6,1 s y
  10,7 s la más lenta. **Ningún botón.**
- **La cocina** (registro de turnos y base, revisados por el agente):
  - Cuatro cambios de estado, todos dichos por la persona: dos inicios, un bloqueo y su
    destrabe, que devolvió la tarea a asignada.
  - Un bloqueo con su causa, quién lo destraba y su resolución.
  - Tres previsiones con el atraso bien calculado; la fecha comprometida no cambió.
  - Los avisos a quien no tiene Telegram quedaron omitidos con su motivo. El escalamiento a Ismael
    dijo que esos pedidos no les llegaron; no dijo que no contestaron.
- **Juicio del usuario:** "la mejor de todas las que hicimos, leda no se perdió incluso me fui del
  guion un poco en algunos casos y respondió de maravilla, esto sí se siente mucho mejor y más
  conversacional que los anteriores.. ni un botón".

Observaciones, ninguna falla de conversación:

- **Leda cuenta de más lo de la cocina.** Por ejemplo, "el aviso a Ismael está guardado, todavía no
  salió", o que un pedido de estado ya no va a salir. Es honesto, y es lo que pidió el primer
  contacto, pero se repite. Una vez anunció "sale hoy a las 10:00" cuando ya eran las 10:00:41.
  Queda para el motor definitivo.
- **El viernes 16 no salió ningún pedido de estado.** El reloj saltó más rápido que el ciclo, que
  corre por minuto real, y la escalera empezó el lunes 19 sin recuperar el día perdido. Es un
  efecto del reloj de la prueba, no del producto. Que no recupere días evita una tanda de mensajes
  juntos.
- **Los efectos del motor no van a `audit_log`.** Quedan como hechos con su autor
  (`task_state_event`, `task_forecast`, `blocker`), pero sin la versión de las reglas que pide la
  constitución §12. Queda para el motor definitivo (Etapa 3).
- **El lector de turnos falló con la base recreada:** perdía la ruta de búsqueda. Corregido en
  `e5227df`, con su regresión.

**Conclusión vigente del flujo D (2026-10-06): la prueba chica pasa.** Cumple los tres criterios
del ADR 0018 (5b):

- 5b.1, del lado automático (ronda 3);
- 5b.2: Leda no se perdió ni se trabó en Telegram real, aun fuera del guion;
- 5b.3: el usuario dice que se siente natural.

Ningún criterio de corte (5c) se disparó. Con este registro se cumple el paso **M2**. Queda la
Etapa 3: limpieza y motor de conversación definitivo.

## Prueba por Telegram real del motor definitivo (E3-8, 2026-10-07): aprobada; paso M3

La guía de la E2-9 (`odd/tasks/motor-definitivo.md`, sección 4b), sobre el motor definitivo (`leda.motor`).
- **Con qué:** GPT-6 sol por la suscripción de ChatGPT del usuario. `leda_motor` recreada con las tareas
  venciendo el viernes 16. El reloj de Leda recorrió del 07/10 al 22/10, y el paso 16 se hizo a las 22:30 con
  el comando nuevo `reloj … hora`.
- **Números:** 31 turnos, ningún incidente y ningún efecto equivocado.
- **Lo nuevo funcionó:**
  - A las 22:31 del jueves 22, "lo termino mañana" quedó anotado para el viernes 23 (la fecha en hora del
    espacio).
  - Habló del mundo y no de la cocina: "Ismael se enterará hoy a las 10:00", "mañana a las 10:00 te volveré
    a pedir el estado".
  - La escalera completa salió en sus días, y el escalamiento fue honesto con quienes no tienen Telegram.
- **Detalles anotados:**
  - Una vez anunció "hoy a las 10:00" cuando ya eran las 10:00:41.
  - Una pregunta que había quedado para después volvió dos días más tarde, en medio de otro tema.
  - Usó la palabra "previsión", que no se entiende: Marcos preguntó "¿qué es previsión?". Se corrige con la
    regla de las palabras de todos los días.
- **Juicio del usuario:** "si, aprobado. va muy bien". Pidió mensajes más breves y con formato: negrita para
  las tareas y lo importante, párrafos separados y listas con viñetas.

**Paso M3 cumplido (2026-10-07):** el motor definitivo está construido, los flujos A y B borrados, las
garantías en verde y la prueba real aprobada.

## Las palabras de todos los días (2026-10-07)

Viene de la prueba de M3: Marcos preguntó "¿qué es previsión?". La regla (decisión del usuario): Leda dice el
hecho concreto con palabras de todos los días y nunca nombra los conceptos del sistema. Conversación de prueba
19. Plan y chequeo de rumbo en `odd/tasks/motor-definitivo.md`.

Mensajes de Leda en la regresión de las 19 conversaciones por 5 (las 18 antes de la 19), con GPT-6 sol por
la suscripción:

| Ronda | Todo bien | Garantías | "previsión" | "fecha comprometida" |
|---|---|---|---|---|
| Antes (`e3-8-sol-suscripcion`, 465 mensajes) | 90 de 90 | 90 de 90 | 85 | 81 |
| Significados e instrucción (`230cf7e`, 497 mensajes) | 93 de 95 | 95 de 95 | 36 | 1 |
| Nombres de los datos (`9b7c6f4`, 499 mensajes) | 94 de 95 | 95 de 95 | **0** | **0** |

- **Primer arreglo (`230cf7e`):** los significados dicen qué es cada dato para la persona y la instrucción de
  redacción pide las palabras de todos los días. Quedó casi siempre una frase: "si se cumple esa previsión".
- **Por qué quedaba:** la IA leía en cada pedido el nombre del dato, `atraso_si_se_cumple_la_prevision_dias_habiles`,
  y lo copiaba aunque la instrucción dijera lo contrario. Era el mismo camino tocado por dos arreglos seguidos,
  un disparador de parar; el usuario eligió cambiar los nombres.
- **Segundo arreglo (`b886ad8`, `9b7c6f4`):** en la frontera con la IA que redacta, 50 nombres de datos,
  códigos y jugadas se traducen a nombres que dicen el hecho (`prevision` → `dia_que_dio_para_terminarla`).
  Adentro no cambia nada. Una prueba falla si un nombre con un concepto de la cocina llega a la IA.
  Revisiones `review-7f575a84f8d3d6f6` y `review-7151cacd0f975300`, aprobadas.
- Lo único que queda es "habías previsto terminarla el martes 27", que es castellano de todos los días.
- **Avisos que no salen a su hora:** 2 de 95 en la primera ronda (08 y 16) y 1 de 95 en la segunda (15). Al
  repetirlas, 10 de 10. Es la misma clase en dos rondas y no se conoce la causa: un intento fallido de
  redactar un aviso no dejaba rastro hasta el quinto. Decisión del usuario: primero dejar rastro de cada
  intento fallido, después decidir.
- **El rastro (`5c4f13b`, `2b4afbf`, revisión `review-a17b92496966ae08`):** cada intento fallido deja un
  incidente de severidad baja, sin avisar a la administración, y el informe de la ronda lo muestra con el tipo
  de error y nada más. La regresión siguiente dio **95 de 95** (`985b099`), sin ningún aviso atrasado y
  con "previsión" en 0 de 500 mensajes: la causa sigue sin conocerse, y el rastro queda para la próxima vez.

## El formato de los mensajes (2026-10-07)

Pedido del usuario al aprobar M3: mensajes breves, con negrita, párrafos y viñetas. Diseño y chequeo de rumbo en
`odd/tasks/motor-definitivo.md`. La IA escribe `**negrita**`, párrafos y "• "; al enviar, la cocina lo
convierte en texto plano con entidades de Telegram, sin `parse_mode`, y una marca mal cerrada sale como texto.
- **Commits:** `a61f36e` (conversación de prueba 20), `47f674d` (la salida), `25ec91d` (la instrucción) y
  `a704883` (el corredor). Revisiones `review-5f70100e7d4c1f51` y `review-a55346b24f27d539`, aprobadas. Suite
  completa: 1207.
- **Regresión de las 20 conversaciones por 5, con GPT-6 sol por la suscripción:** **100 de 100** y 100 de 100
  en garantías. La IA usa el formato: las tareas y las fechas en negrita, un párrafo por cosa y viñetas para
  listar tareas.
- **Falta:** el juicio del usuario, primero sobre ejemplos de las transcripciones y después por Telegram.
- **Prueba por Telegram del usuario (primera vuelta):** mejoró, pero seguía siendo mucho bloque de texto y
  la negrita casi no se notaba. Pidió, con capturas, un renglón por idea y emojis fijos.
- **Segunda vuelta** (`c1b3042` a `96be1a3`, revisión `review-f216946c22e36f30`): sin negrita, un renglón
  por idea, 📋 ✏️ 📅 ⚠️, fechas cortas ("vie 23/10") y el cierre aparte, con un chequeo automático del
  formato en el corredor. Regresión de 20 por 5 con otra cuenta de ChatGPT del usuario (`86cef4a`):
  garantías 100 de 100, comprensión 100 de 100 y **formato 79 de 100**. Las fallas, casi siempre dos ideas
  en un renglón o dos preguntas en el cierre. Desde esta ronda, "todo bien" incluye el formato y no se
  compara con las anteriores.
- **Prueba por Telegram del usuario (segunda vuelta, 2026-10-07):** "quedó muy bien". Tres ajustes: 🗓️ en
  vez de 📅 (Telegram dibuja 📅 con una fecha fija), en cada bloque primero la tarea y después lo anotado,
  y "Ismael será notificado / fue notificado" en vez de "le voy a avisar a Ismael". En la prueba, saltar
  días seguidos sin esperar la vuelta de un minuto del escuchador dejó sin salir los recordatorios de esos
  días; la escalera no se saltea pasos y dejó el escalamiento para después del recordatorio que lo
  anuncia, como pide la mecánica §9.
- **Tercera vuelta del formato y el "escribiendo…"** (`107b7fb`, `93b0ff3`, revisión
  `review-1087d89630436954`; el indicador, la animación y el streaming: `f82804f`, `5720fdc`,
  `review-62848d1507d6fd52`; sin demora al final: `fa52cb2`, `9a387da`, `review-99aaf83d8c79df29`). La
  regresión (`3cf974f`) se cortó en la conversación 15: la cuenta de ChatGPT se quedó sin cupo (112
  respuestas 429, que el rastro de los avisos mostró enseguida). En la 1 a la 14, comprensión 70 de 70 y
  ninguna falla de las reglas nuevas (🗓️, la tarea primero, la marca al principio, "será notificado"); siguen
  fallando a veces los renglones largos y el cierre.
- **Prueba por Telegram del usuario (tercera vuelta, 2026-10-07):** "el formato, el '…' y el streaming
  quedó perfecto". Al quitar el retiro del borrador, el mensaje final aparece enseguida, sin desaparecer,
  como pide la API de Telegram para `sendMessageDraft`. **Hallazgo:** el usuario escribió a propósito sin
  puntuación, "con el PLC estoy compliacdo, me falta el cable para programar comunicaciones estimo que la
  tengo para el viernes 23", y la IA anotó el bloqueo y la fecha en el PLC, con "comunicaciones" dentro de la
  causa y esa causa como motivo; comunicaciones quedó sin fecha, a Ismael le llegó un aviso equivocado y la
  escalera persiguió comunicaciones hasta el escalamiento. Es comprensión, no código. Se escribe como
  conversación de prueba 25 (todos los mensajes sin puntuación, pedido del usuario) y se mide con la IA real
  antes de tocar nada; la regla que ya existe es la duda (conversación 09).

## Mensajes sin puntuación, el margen para corregir y el motivo de un atraso (2026-10-07 y 08)

- **Medición** (conversación 25, todos los mensajes sin puntuación, pedido del usuario): el mensaje del
  usuario se lee mal **5 de 5**, siempre igual (la fecha y la causa en el PLC); los otros dos mensajes sin
  puntuación, bien 5 de 5. No es la falta de puntuación en general: es una frase con dos lecturas, y la IA
  nunca se da cuenta de que duda (`7898ce6`).
- **Decisión del usuario: un margen antes de avisar** (`80195d9`, `c568cb3`, revisión
  `review-681edff9caaf9741`; ADR 0018, 9n): los avisos a otra persona que salen de algo que alguien dijo
  esperan 10 minutos, y una corrección dentro del margen retira el equivocado. Con la IA real, la corrección
  funcionó 5 de 5 y las conversaciones 01 a 20 dieron 100 de 100 (`afdcbe8`).
- **Hallazgo y decisión: una fecha que atrasa lleva su explicación.** La corrección movía el motivo
  equivocado a la otra tarea. El usuario: "pasar una fecha sin motivo no es una buena idea, tiene que haber
  una explicación". Si la fecha atrasa y no hay motivo, Leda lo pregunta; el aviso espera la respuesta (o
  sale al final del día diciendo que falta); una corrección mueve sólo la fecha; un motivo ya dado se
  mantiene sólo si pasó menos de una hora y en el medio no se habló de otra cosa (`4c045d5` a `5f4ee4f`,
  revisiones `review-c35be62163024cb8` y `review-0b2732c3f4bee906`).
- **La regresión con la IA real de esta última parte quedó sin hacer:** se cortó por falta de cupo de la
  cuenta de ChatGPT. Es lo primero de la próxima sesión.
- **Prueba por Telegram del usuario (2026-10-08):** el mismo mensaje se leyó mal, Marcos corrigió, Leda
  preguntó el motivo de comunicaciones y a Ismael le llegó **un solo aviso, el correcto**, con el motivo de
  Marcos; el del PLC quedó retirado sin salir. **Hallazgo nuevo:** un aviso automático de Leda (el de que
  comunicaciones vence en 3 días) salió en medio de la conversación, repitiendo lo que se estaba hablando.
  El usuario: debería esperar a que se cierre el tema, o salir después de un rato sin respuesta. Queda como
  primera tarea de la próxima sesión, primero como conversación de prueba.
- **Regresión con la IA real de la regla del motivo** (2026-10-08, de noche, sobre `4cbfbef`, sol por la
  suscripción, 21 conversaciones, 5 veces; `resultados/2026-10-08-0032-leda.motor-sol-suscripcion.md`):
  69 de 105 corridas con todo lo automático bien. Las fallas son de tres clases, ninguna de la regla:
  - **El servicio de ChatGPT falló 16 veces** (`ErrorDeChatGPT`, `PlazoAgotado`, `RemoteProtocolError`; el
    usuario comprobó que había cupo). Un aviso que la IA no redactó a su hora sale después, con reintento
    e incidente, y descoloca los pasos siguientes: explica todas las fallas del motor de la 01 a la 07.
    **Repetidas esas seis** (`resultados/motivo-repeticion-01-07.md`): 30 de 30 bien en garantías,
    comprensión y motor; las 9 corridas con fallas lo son sólo de formato.
  - **Formato:** renglones de más de 140 caracteres que juntan dos ideas ("⚠️ Si la terminás ese día,
    tendrá 2 días hábiles de atraso. La revisión de… depende de esta tarea.") y el cierre sin su renglón
    en blanco. No empeoró: la ronda del margen ya daba 0 de 5 en la 02, la 18 y la 19. Es la deuda del
    formato registrada en `docs/STATUS.md`.
  - **La 25 se sigue leyendo mal 5 de 5**, como en su medición: sus fallas de garantía son ésas (los
    efectos caen en la tarea equivocada hasta que Marcos corrige).
  - **Conclusión vigente:** la regla del motivo funciona con la IA real; la inestabilidad del servicio no
    oficial de ChatGPT (riesgo 5) pesa en las rondas, aunque la cocina la maneja sin silencio.

## La entrega y la aprobación con la IA real (Fase C, C-4, 2026-10-08, de noche)

Primera ronda con la IA real de los circuitos nuevos (`resultados/fase-c-c3-regresion.md`, sobre
`8b05495`, sol por la suscripción, 25 conversaciones, 5 veces): 69 de 125 con todo lo automático bien.

- **De la 01 a la 20 y la 24, garantías y comprensión 5 de 5.** Las fallas que quedan ahí son de formato.
- **La 21 marcó garantías 0 de 5, y es una falsa alarma del comparador:** la cocina escribió las seis
  piezas que mostró la vista previa y que Marcos confirmó, y el aviso a Ismael dice lo mismo. El
  comparador imprime como "real" sólo las filas que no emparejó y llama garantía a una fila que sobra
  aunque sea lo confirmado (`tests/conversaciones/comprobar.py`, `filas`). Hay que arreglarlo: la
  garantía es "lo escrito es lo confirmado", no "lo escrito es el camino ideal del YAML".
- **Hallazgo 1, de diseño: la IA decide qué cubre cada texto** (`el_texto_cubre`) y eso puede trabar
  la entrega. Leyó "termine el plc!! ahi va la pantalla y el contador, 20 ciclos sin una falla" como
  resultado de la prueba y no como explicación; el código vio que faltaba la explicación y no ofreció
  Confirmar, y Leda le pidió a Marcos que contara cómo quedó, sin decirle que lo escrito podía alcanzar.
  El ADR 0019 (decisión 5) dice que la persona confirma o corrige lo que cubre cada pieza, no que lo
  decida la IA. Se discute con el usuario antes de tocar nada.
- **Hallazgo 2: "¿cuál de las dos?" se repite** (la 23, paso 9, 3 de 5): si quien aprueba vuelve a
  mezclar aprobar y pedir cambios, Leda vuelve a preguntar; la decisión del usuario es preguntar una
  sola vez. Se discute qué pasa después de esa única pregunta.
- **La 22 y la 23 en comprensión:** sobre todo el YAML más estricto que la ficha (espera ninguna
  jugada donde la IA elige `entregar`, que la ficha permite; o rechaza un dato opcional, como la tarea
  en `confirmar` o un comentario). Sin errores del servicio.
- **Conclusión vigente:** la cocina de la entrega y la aprobación hace lo que se confirma; la
  comprensión de la entrega con la IA real todavía no está: falta decidir quién juzga lo que cubre un
  texto. No hay prueba por Telegram de estos circuitos.

## La regresión de la C-3d con la IA real (Fase C, D6, 2026-10-08, de tarde)

La ronda de las 29 conversaciones, 5 veces cada una, con sol por la suscripción, sobre `eec2b8a` (D1 a D5
construidas). Comando: `.venv\Scripts\python.exe -m tests.conversaciones.correr --ia sol-suscripcion
--veces 5 --paralelo 2 --conversacion …`, en tres tramos con resultado válido:
`resultados/fase-c-d6-01-20.md`, `resultados/fase-c-d6-21-29.md` (vale sólo para la 21 y la 22) y
`resultados/fase-c-d6-23-29.md`.

- **Lo que no vale:** el primer intento (las 29) chocó con el cupo de la cuenta de ChatGPT en todas las
  llamadas (HTTP 429, `usage_limit_reached`, sin tokens); se borró su informe. El segundo (21 a 29) terminó
  sus corridas pero el corredor se cayó al anotar el gasto (`PermissionError` de Windows al reemplazar
  `gasto.json`, que otro proceso tenía abierto) y no dejó informe. El tercero (21 a 29) se quedó sin cupo en
  la 23, vez 3: de ahí en adelante, 429. El usuario cambió de cuenta y se repitieron la 23 a la 29 y la 01 a
  la 20. Ninguna falla del servicio se cuenta como de Leda; quedó un solo `PlazoAgotado` (la 16, una vez:
  un aviso que salió tarde).
- **Garantías:** 5 de 5 en todas salvo la 25, la 27 y la 28 (0 de 5). La 25 es la lectura equivocada
  conocida (los efectos caen en la otra tarea hasta que Marcos corrige). La 27 y la 28 son las fallas de
  abajo.
- **Comprensión:** 5 de 5 de la 01 a la 11, la 13 a la 20, la 24, la 26 y la 29; 0 de 5 en la 12, la 21 a
  la 23, la 25, la 27 y la 28.
- **Formato** (la deuda registrada): 0 de 5 en la 02, la 18, la 19, la 21 a la 23, la 25 y la 28; las demás,
  entre 1 y 5 de 5.

**Lo que es del YAML, no de Leda (aflojado, con la ficha que lo permite; corrida en seco 5 de 5):**

- **El ejemplo con sus palabras** (la 12, paso 6; la 22, pasos 3 a 7; la 25; la 27, pasos 1 a 4): la IA
  escribe el ejemplo sacado del criterio con su redacción, y el YAML pedía el texto exacto. Ahora el
  ejemplo puede venir con cualquier texto (`puede_traer`) y los hechos piden que esté (`presente`);
  `lo_descrito_cubre` vacío o ausente vale igual, y al aceptar el ejemplo puede traer `[C1]`.
- **"aprobala nomas y pasale lo de los colores"** (la 23, paso 9): la IA elige `aprobar` con el comentario
  5 de 5, que la decisión 12 da por válido igual que `elegir`; los efectos ya coincidían.

**Las fallas de Leda (comprensión), de la más seria a la más leve:**

1. **"no, asi esta, mandala" con algo pendiente** (la 27, paso 3): en 4 de 5 la IA lo lleva a
   `fuera_de_la_lista` ("mandar la entrega tal como está"): no se entrega nada, pero cada vez le llega un
   aviso a la administración. En 1 de 5 lo lee como que **acepta el ejemplo** que rechazó: la vista previa
   suma "los 20 ciclos sin fallas", que Marcos nunca dijo, y su "si, eso" siguiente la entrega. La vista
   previa lo mostraba y Marcos confirmó, pero Leda le puso palabras que había rechazado. La jugada esperada
   era `confirmar` (la cocina se niega: `le_falta_algo`).
2. **Lo que cubre un texto lo sigue juzgando la IA con más rigor que la persona** (la 21, paso 1, 5 de 5):
   "termine el plc!! … 20 ciclos sin una falla" no le alcanza para "arranca desde el PLC y completa 20
   ciclos sin fallas", y Leda pide que confirme que arrancó desde el PLC (con el criterio entero de
   ejemplo); en 2 de 5 tampoco lo cuenta como explicación. Es la clase del hallazgo 1 de la primera ronda:
   suma una vuelta, no rompe nada. Lo que sigue en la 21 es consecuencia.
3. **"y bueno fijate vos"** (la 28, paso 4, 5 de 5): la IA lo lleva a `fuera_de_la_lista` y la
   administración recibe un aviso cada vez. Lo que ve Ismael está bien: no decide por él, no repite la
   pregunta y le deja los dos botones.
4. **Nombrar a Ismael por su cuenta** (la 11, paso 4, 5 de 5): "Ismael no será informado del atraso que
   habías previsto", al retirar un aviso. El YAML no lo mira. (El "lo decide Ismael" de la 12, la 19 y la
   23 es `quien_decide`, a la vista a propósito: decisión pendiente del usuario.)

**Lo que se medía de la D2 a la D5:**

- **Un criterio de una sola oración** (la 27, paso 1, 5 de 5): Leda pregunta sólo lo que falta ("falta
  saber si completó 20 ciclos sin fallas"); el ejemplo es la oración entera del criterio.
- **"sí" frente a un ejemplo**: es `acepta_el_ejemplo` cuando lo pendiente es el ejemplo (la 22, paso 7,
  5 de 5; la 27, paso 4, 4 de 4) y `confirmar` cuando lo que está abierto es la vista previa (la 27, vez 5).
- **"aprobala nomas y pasale lo de los colores"**: una sola elección, 5 de 5 (`aprobar` con el
  comentario). "¿Cuál de las dos?" se pregunta una vez (la 28, paso 3).
- **"queda informada"**: aparece en las respuestas de la 01 a la 20 (45 veces en sus transcripciones), y a
  "a quien le avisaste?" (la 21, paso 6) Leda contesta Ismael y la hora cuando la entrega salió (2 de 5) y,
  honesta, que todavía nadie cuando no se confirmó (3 de 5).
- **No interrumpir** (la 26) y **cambia quién revisa** (la 29): garantías y comprensión 5 de 5.
- **Conclusión vigente:** la cocina de la entrega y la revisión hace lo que se confirma, y las reglas de la
  D2 a la D5 se cumplen con la IA real. Quedan dos cosas de comprensión que son de diseño, no de frases:
  qué hace Leda cuando la persona insiste en mandar algo incompleto (hoy cae fuera de la lista, o peor) y
  quién juzga lo que cubre un texto. No hay todavía prueba por Telegram de estos circuitos (guion en
  `guion-telegram-fase-c-parte-1.md`).

## El motor definitivo con cinco IA (E3-8, 2026-10-07)

Tarea E3-8 de `odd/tasks/motor-definitivo.md`. Las 18 conversaciones de prueba (las 17 de la Etapa 2 y la
18, hablar del mundo), cinco veces cada una, sobre el motor definitivo (`leda.motor`, con la regla de hablar
del mundo y el arreglo de la fecha). Se usó el corredor de `tests/conversaciones/`, con una base por corrida.
Informes en `tests/conversaciones/resultados/e3-8-*.md`.

| IA | Todo bien | Garantías | Mediana / peor por turno | Costo de la ronda |
|---|---|---|---|---|
| GPT-6 sol | **89 de 90** | **90 de 90** | 5,1 s / 12,0 s | USD 3,04 |
| GPT-6 luna | 75 de 90 | 83 de 90 | 7,2 s / 17,6 s | USD 0,19 |
| GPT-6 luna pro | 76 de 90 | 87 de 90 | 13,2 s / 37,7 s | USD 0,65 |
| DeepSeek flash (`nan`), razonando | 41 de 90 | 90 de 90 | 8,9 s / 50,9 s | sin precio informado |
| GLM 5.3 flash (`nan`), razonando | 12 de 90 | 90 de 90 | 3,6 s / 54,6 s | sin precio informado |
| DeepSeek flash (`nan`), sin razonar | 49 de 90 | 75 de 90 | 2,3 s / 13,7 s | sin precio informado |
| GLM 5.3 flash (`nan`), sin razonar | 49 de 90 | 80 de 90 | 2,6 s / 34,3 s | sin precio informado |

- **Los modelos de `nan`, razonando:** fallaron por límites, no por comprensión.
  - El corredor les daba los límites pensados para sol: 20 s por llamada, 40 s en total y un tope de
    salida. Los dos razonan largo en cada llamada; GLM, además, gasta el tope en razonar y devuelve una
    respuesta vacía.
  - Leda cayó en el texto fijo con su incidente. Por eso las garantías dan bien.
  - Se agregaron parámetros por modelo (tiempo, tope y campos del pedido; también para producción, con
    `python -m leda modelo … --parametros`) y se repitió con el razonamiento apagado, de a dos
    conversaciones a la vez.
  - No se midió razonando con tiempo de sobra: son 3 a 4 horas por modelo.
- **Sin razonar** responden rápido, pero entienden menos.
  - Las fallas de garantía de luna, luna pro y los flash son todas "efecto de más" del mismo tipo, en la
    08 (cambio de tema) y la 05 (varias cosas). Por ejemplo, "lo de comunicaciones no llegó al 30,
    necesito hasta el miércoles 4": la IA guarda "no llegó al 30" como motivo de la demora, y ese motivo
    inventado le llegaría a Ismael.
  - También pierden fechas y agregan jugadas que nadie pidió.
- **`nan` guarda en caché los pedidos idénticos,** así que las cinco repeticiones no son del todo
  independientes.
- **La única falla de sol** es perder una fecha a más de 14 días ("el miércoles 4 de noviembre"). Es la
  misma clase que su falla de la regresión de la E3-6 (conversación 08): la IA recibe los nombres de los
  días sólo de las próximas dos semanas (`DIAS_PROXIMOS`). Es la misma clase de hallazgo en dos rondas,
  un disparador de parar (`AGENTS.md`, punto 4): no se parchea, y la revisión del mecanismo queda para el
  usuario.
- **Gasto en OpenRouter:** unos USD 3,9. El gasto acumulado desde la Etapa 2 es de unos USD 27 (el techo
  de USD 30 era de esa etapa), y quedan unos USD 2,3 de crédito.

**Las fechas a más de dos semanas (decisión del usuario, 2026-10-07).** La lista de días con su nombre
que recibe la IA pasa de 14 a 56 días (ocho semanas): es la regla 9m, "los días de la semana los da el
código", aplicada más lejos (`aec4b0e`, revisión `review-2c521db7ea334a0b`). La prueba nueva falló
primero. Con GPT-6 sol, la 05 y la 08 dieron 5 de 5 cada una. La regresión completa queda pendiente
hasta cargar crédito en OpenRouter.

**GPT-6 sol por la suscripción de ChatGPT del usuario (2026-10-07).** Es la misma IA, por el inicio de sesión
de Codex (proveedor `chatgpt`, decisión del usuario).
- En la primera llamada real el servicio exigió `reasoning.context: all_turns` y mandó el flujo sin declarar
  su tipo. Se corrigió en `166a508`, con las pruebas en rojo primero (revisión `review-01ccc28d686e86c1`).
- **Regresión de las 18 conversaciones por 5, con la lista de días de ocho semanas:** **90 de 90** con todo lo
  automático bien y 90 de 90 en garantías. Mediana de 6,6 s por turno y el peor de 43,1 s, un caso aislado.
  Sin costo en OpenRouter.
- Es el mejor resultado medido. `leda_motor` usa ahora este proveedor para la prueba por Telegram.

**Conclusión vigente (2026-10-07): se queda GPT-6 sol.** Es el único que no hace efectos de más y el más
rápido de los que entienden bien; cuesta unos USD 0,034 por conversación de prueba. Luna y luna pro no
alcanzan con el motor nuevo, igual que en la ronda 1. Los flash de `nan` sin razonar son 15 veces más
rápidos pero entienden la mitad. Razonando con tiempo de sobra quedan sin medir, y no sirven para
conversar: tardan hasta un minuto por turno.

## Conclusión anterior (2026-10-03), reemplazada el 2026-10-04

**Flujo elegido: C6, con las plantillas fuera y la regla del mozo** (`AGENTS.md`, punto
11), aunque todavía no está terminado. **Modelo: GPT-6 sol.**

Por qué C6:

- Los problemas de los demás flujos están en su diseño; los de C6, no. El flujo A es un
  formulario (pasos fijos y botones). El flujo B deja que la IA decida y actúe libre (ahí
  inventó un cambio, H5). C1 a C5 escriben antes de que el código decida, así que la IA
  adivina, y cada adivinanza fallida terminó en una regla nueva. En los tres casos,
  arreglar un problema genera el siguiente.
- Los problemas de C6 se arreglan dentro de su diseño, sin reglas para la IA (por ejemplo,
  el bucle del borrador devuelto y la frase de ofertas repetida).
- Es el único que cumple la promesa central de Leda: no inventar. Lo que dice sale de la
  base y la IA sólo lo cuenta.
- Se puede llevar al resto de los circuitos: la llamada que escribe es la misma para
  todos; cada circuito define qué tiene que entender la IA y qué hace la cocina.

Por qué sol: fue el más fiel a los hechos en la prueba real. Si con C6 estable luna
también queda fiel, conviene volver a comparar: es unas 23 veces más barato y más rápido.

Qué haría revisar esta conclusión: si después de la tarea 0-34 vuelve a aparecer una falla
del mismo tipo en el borrador devuelto, no se cambia de flujo, pero se revisa el diseño del
borrador devuelto antes de seguir.

**Actualización (2026-10-04):** pasó. La cuarta auditoría encontró que el borrador devuelto
todavía puede entrar en bucle (otra causa, la misma clase de falla). Se mantiene C6 y se
rediseña el borrador devuelto (tarea 0-35): sin lista de datos a corregir; vuelve como un
borrador normal con el motivo, una pregunta abierta y el resumen para reenviar.

**Reemplazo (2026-10-04, después de la prueba real de 0-35):** toda esta conclusión dejó de
regir, incluida la actualización de arriba. No se mantiene C6 ni se sigue trabajando sobre el
borrador devuelto; rige la conclusión vigente del comienzo.

## La regla del mozo: por qué se decidió y cómo se aplicó en C6

> **Nota del 2026-10-04.** Esta sección cuenta cómo se aplicó la regla en el flujo C6, que quedó
> congelado. El núcleo de la regla sigue vigente (la IA no inventa datos ni efectos; los hechos
> salen de la cocina). Su extensión a cada movimiento de la conversación está en revisión en el
> ADR 0018; ver `AGENTS.md`, "Cómo pensamos juntos", punto 11. La forma de trabajar que describe
> (controlar con pruebas automáticas y con la auditoría de otro agente) tampoco es la vigente:
> ver el punto 12.

**Qué es** (decisión del usuario, 2026-10-03; `AGENTS.md`, punto 11). La IA es el mozo de
un restaurante: escucha o pregunta qué quiere la persona, lleva el pedido exacto a la
cocina y trae lo que la cocina dice, contándolo con naturalidad. La cocina es el código,
Jev y la base: valida, decide, ejecuta y sabe los hechos. El mozo no cocina ni inventa
platos: es intérprete y comunicador de la fuente de verdad, usa su fuerte (hablar e
interpretar a la persona) y **no toma decisiones**. Ante cada cambio se pregunta: ¿esto lo
resuelve la cocina o le estamos enseñando frases al mozo?

**Por qué se decidió.**

1. De C1 a C5 la IA escribía la respuesta antes de que el código decidiera: tenía que
   adivinar qué iba a pasar. Cada vez que adivinaba mal se le agregaba una regla, y la
   mecánica crecía (el retroceso de C4). El usuario lo resumió así: el actual es un mozo que
   confirma el plato antes de preguntar en la cocina.
2. C6 corrigió el orden (el mozo pregunta en la cocina antes de contestar), pero se
   construyó dejándole a la IA decisiones que no le tocan: elegía qué preguntar de una
   lista, si mostraba botones y cuándo proponer algo, y seguía llevando las reglas de casos
   heredadas de C5. La cocina, además, empezó a corregir lo que el mozo escuchaba con
   trucos propios (comparar nombres por coincidencia de letras).
3. Al revisar los arreglos de la ronda de modelos, el usuario frenó: "estamos en el límite
   de volver a cometer el error de agregar reglas puntuales para que el circuito responda
   como queremos". Propuso fijar el criterio con la analogía del mozo y la cocina, y
   después lo precisó: la IA no toma decisiones ni inventa datos; para eso va a la cocina.
   Se dejó escrito en `AGENTS.md` para que sirva de control antes de construir, no después
   de probar.

**Cómo se aplicó en C6** (tareas 0-31 a 0-34 de la rama de flujo).

- **La cocina decide y se lo dice al mozo como hechos:** qué dato se pregunta (con una
  sola regla fija), qué botones van, cuándo se propone algo (título que no dice qué hacer,
  criterio que no se puede comprobar, pedido de ayuda) y qué se ofrece en cada momento.
  También dice quién hizo qué visto desde quien lee, y el motivo real de cada cosa que no
  se tomó.
- **El mozo interpreta y cuenta:** la primera llamada entiende el mensaje (intención,
  datos, correcciones, nombres que no están entre las opciones, si el título no dice qué
  hacer, si mantiene un dato); la segunda escribe desde los hechos. Su salida sólo trae el
  texto, la propuesta cuando la cocina la pide y el dato que preguntó, que tiene que ser
  el que decidió la cocina.
- **Lo que necesita juicio sobre la base lo resuelve la pieza indicada:** un nombre fuera
  de las opciones lo compara Jev (ADR 0014), no el código ni la IA adivinando.
- **Las instrucciones describen el trabajo del mozo,** sin reglas de casos, sin ejemplos
  de lo que tiene que decir y sin límite de largo.
- **Nada fijo del código llega a la persona,** salvo lo aprobado por el usuario: las dos
  plantillas (las líneas de datos del resumen y el aviso de falla de la IA, que incluye el
  saludo del día y "Pendiente:") y, aparte, el bloque para copiar de Modificar, que no es
  una plantilla sino el propio dato de la persona (decisión del 2026-10-03, después de ver
  un ejemplo). Las etiquetas de los botones las arma el código.
- **Se controla solo:** pruebas automáticas fallan si vuelve un texto fijo, una decisión
  de la IA o una regla de caso; y después de cada vuelta, una auditoría independiente.

**Resultado en el flujo C6 (al 2026-10-03).** Prueba real con sol (2026-10-03, 19:18): Ariel
explicado con la regla real, el rechazo volvió como una pregunta concreta, el bloque para copiar
funcionó y quién hizo qué salió bien en todos los mensajes. Fallaron dos cosas, las dos de la
cocina y no del mozo: un bucle en el borrador devuelto (la cocina volvía a pedir la fecha) y la
misma oferta al final de cada mensaje (la cocina le pasaba siempre la lista de lo posible). Las
dos se trabajaron dentro de la regla en la tarea 0-34. La prueba real del 2026-10-04 mostró que
la misma clase de falla seguía apareciendo (fila "C6 + 0-35" de la tabla).

## Los flujos, uno por uno

| Flujo | Qué es | Prueba real | Lo bueno | Lo malo | Estado |
|---|---|---|---|---|---|
| A | Formulario mecánico: pasos fijos, un dato por vez, botones | Rondas 1-4 (hasta 2026-09-30) | Predecible; nunca inventa | Robótico; no entiende lo que se escribe libre | Congelado el 2026-10-04; su código en `main` se borra antes de construir el motor de conversación definitivo |
| B | IA libre: lee la constitución, elige herramientas y redacta | Rondas 1-4 | Flexible | Inventó un cambio (H5); textos fijos con muletillas del agente ("Listo…", "Dale…") | Congelado el 2026-10-04; es lo que atiende en `main` todo lo que no es el alta, y se borra antes de construir el motor de conversación definitivo |
| C1 | ADR 0014, una llamada: la IA interpreta y escribe antes de que el código decida | 2026-10-01: favorable ("fluidez increíble") | Gran salto contra A | Órdenes secas (12), "anoté" sin efecto (7), dos datos por pregunta (9) | Congelado |
| C2 | C1 + la personalidad como texto aparte | 2026-10-02 18:20: pasa | Menos órdenes secas | El usuario: "habla exactamente igual"; el más lento (17 s típico, 40 s peores casos) porque la personalidad contradecía la mecánica | Congelado |
| C3 | Personalidad adentro de la mecánica | No se probó en real (se saltó a C4 por la medición del banco, contra "probar en real enseguida") | Volvió a 10,6 s; cero órdenes secas, "anoté" y dos datos | Aceptaba un título vago | Congelado |
| C4 | C3 + reglas de estilo concretas | 2026-10-02 22:18: pasa | Un dato por pregunta garantizado por el código | **Retroceso:** reglas de casos ("por favor", nombre de pila, no repasar) que no daban el resultado; el verificador rechazaba el título propuesto | Congelado |
| C5 | Mecánica sólo con reglas estructurales | 2026-10-03 00:44: pasa en lo estructural | Sin reglas de estilo, lo estructural se sostuvo; textos más cortos | "Perfecto" y «¿te sirve?»; textos fijos del código | Congelado; etiqueta `respaldo-flujos-antes-de-c6` |
| C6 | Esquema del usuario: la IA interpreta, el código decide, la IA escribe desde los hechos (dos llamadas) | 2026-10-03 01:39: pasa; el usuario: "es más conversacional" | La fecha fuera de plazo con el límite real; la propuesta de título pasa el verificador; textos que coinciden con lo que pasó | Muletillas de la IA; textos fijos al final | Elegido el 2026-10-03; congelado el 2026-10-04 |
| C6 + P-1 | Sin plantillas (sólo dos permitidas) | 2026-10-03 09:13 (flash): "habla sin plantillas ni muletillas" | Sin textos fijos en el camino principal; elección del botón escrita en el mensaje | Responsable fuera de opciones ignorado; el rechazo dejaba el tema abierto; causa inventada; promesa falsa | Fue la base de las versiones siguientes del flujo C; congelado el 2026-10-04 |
| C6 + regla del mozo | La IA no decide: la cocina decide qué se pregunta, botones y propuestas | 2026-10-03 19:18 (sol) | Ariel explicado con la regla real; el rechazo vuelve como pregunta concreta; bloque para copiar | Bucle en el borrador devuelto (pedía la fecha); la misma oferta al final de cada mensaje; volvió una orden; "Soy Leda." | Arreglado en 0-34; congelado el 2026-10-04 |
| C6 + 0-35 | El borrador devuelto vuelve como un borrador normal (sin lista de datos a corregir), con las correcciones de la quinta auditoría | 2026-10-04 11:21-11:38 (sol), cortada antes de terminar el guion | El bucle no volvió; una corrección sobre el devuelto volvió al resumen sin pedir otros datos; el selector de Modificar pregunta en lugar de ordenar; la propuesta de la IA no pisó el criterio confirmado | Después de un turno sin cambios, la respuesta salió sin resumen ni botones; pedir por escrito el envío a aprobación no se tomó; la lista de ofertas recitada en casi todos los mensajes; un Cancelar de un resumen anterior canceló el devuelto, y el flujo B no supo del borrador cancelado y ofreció tareas ajenas | Congelado el 2026-10-04 (etiqueta `respaldo-flujos-antes-de-d`) |
| D | El mecanismo del Motor: un motor de conversación con estado explícito, circuitos declarados y situaciones generales resueltas una sola vez (ADR 0018, propuesta) | 2026-10-05 12:13 (sol): primer contacto, parcial, no M2. Rondas automáticas del 2026-10-05 y 06: la ronda 3, 85 de 85 | La jugada y la tarea correctas en las cuatro respuestas; el atraso, bien calculado; sin incidentes; en la ronda 3, garantías y comprensión 5 de 5 en las 17 conversaciones | Dijo que el referente estaba avisado con el aviso sólo guardado; no preguntó quién destraba el bloqueo (las dos, de la cocina; arregladas el mismo día); en las rondas 1 y 2, fallas del contrato entre la IA y el código | En la prueba chica (Etapa 2), en la rama `feat/motor-de-conversacion`; falta Telegram real (E2-9) |

## Progresos y retrocesos

- **Retroceso C3 → C4:** se sumaron reglas de estilo para casos y no dieron el resultado;
  se detectó por los disparadores del punto 4 de `AGENTS.md` y se revirtió en C5.
- **Error de método:** C3 no se probó en real; la decisión de pasar a C4 se tomó sobre el
  banco.
- **Progreso C5 → C6:** cambiar el orden (la IA escribe después de que el código decide)
  eliminó los textos que contradecían lo que pasó.
- **Hallazgo:** las muletillas venían de nosotros. «¿te sirve?» salía de "aceptar o
  cambiar" en las instrucciones; "Listo…" y "Dale…" de textos fijos del flujo B que la IA
  lee en el historial. Con flash y las instrucciones corregidas, «¿te sirve?»
  desapareció; con luna y sol aparece igual (costumbre de esos modelos).
- **Error de diseño reconocido:** C6 se construyó cambiando el orden pero dejándole a la
  IA decisiones (qué preguntar, botones, cuándo proponer) y las reglas heredadas de C5. Lo
  corrigió la regla del mozo (0-31).
- **Las plantillas se perdieron dos veces** por posponerlas sin tarea; desde entonces
  todo lo que se pospone se anota como tarea en el momento.
- **Auditorías independientes:** después de que un escritor dice "cumple", siempre va una
  auditoría de otro revisor. Primera (6f85bf9): 10 textos fijos y 4 casos del mozo;
  segunda (a8f4aba): 4 y 3 de severidad baja; tercera (3e5bcb3): 4 y 3, de borde. Cuarta
  (f7dce94): 3 y 3, con el bucle del borrador devuelto de nuevo → rediseño (0-35). Quinta
  (bb1ee18, sobre el rediseño): "sí, con reservas"; el bucle no volvió. 7 hallazgos: una
  propuesta de la IA pisaba un dato confirmado (medio; contra la regla del mozo: una
  propuesta se acepta, no se guarda sola), el devuelto que esperaba otro borrador volvía
  en silencio (medio-bajo), 4 bajos (guardas, instrucción sin describir todos los hechos,
  líneas del resumen repetidas, "Pendiente:" con una oración) y la redacción de
  `PIDE_ELEGIR` y `PIDE_QUE_CAMBIAR`, que se mira en la prueba real. Arreglados los otros
  6 en `df761db`, `ba3269d` y `24e92ce`, con el mecanismo y no el caso. Los controles
  automáticos que escribe el mismo escritor tienen sus mismos puntos ciegos.
- **Prueba real de 0-35 y freno (2026-10-04).** Con la suite en verde (3.997 pruebas) y la
  quinta auditoría aprobada con reservas, la prueba real volvió a fallar en formas nuevas de la
  misma clase: el estado de la conversación y lo que la persona puede hacer se decidían en cada
  camino por su cuenta. El usuario cortó la prueba y frenó los arreglos. Es el disparador
  "pruebas en verde y el usuario dice que se siente mal" del punto 4 de `AGENTS.md`, y la misma
  clase de falla en dos rondas.
- **Análisis adversarial (2026-10-04),** pedido por el usuario: una revisión interna de sólo
  lectura y una investigación externa con fuentes. Resumen (detalle y cifras en
  [`../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md)):
  - La base no está en cuestión: PostgreSQL con las garantías en el código, y la IA que
    interpreta y redacta, coinciden con el patrón dominante. En ninguna ronda quedó registrado
    un efecto mal hecho.
  - La falla está en el medio: unas 16.000 líneas de manejo de conversación escritas a mano, sin
    un modelo de la conversación (el estado se deduce en cada mensaje; un borrador tiene al
    menos 14 estados implícitos) y con tres flujos conviviendo. Un mapa sobre el alta contó unos
    30 lugares que deciden, cada uno por su cuenta, si va el resumen, qué botones salen y qué se
    ofrece.
  - Los hallazgos no bajan: 14, 7, 7, 6 y 7 en las cinco auditorías.
  - Las pruebas miran el código, no las conversaciones: unas 70.000 líneas de pruebas, en su
    mayoría atadas a la implementación y escritas por el mismo escritor, y ninguna prueba con la
    IA real del flujo elegido.
  - El método corrió más rápido que el diseño: 254 commits en la rama entre el 2026-09-30 y el
    2026-10-04, y seis versiones del alta en tres días.
  - Ninguno de los productos y marcos relevados escribe a mano una rama por situación, y ningún
    producto verificado cubre el circuito completo de Leda dentro del chat del equipo.
- **La parte del agente (2026-10-04).** Ese día el agente delegó tres vueltas de arreglos (la
  tarea 0-35, las correcciones de la quinta auditoría y la tarea 0-36) y propuso una cuarta. Cada
  una era un "arreglo del mecanismo" razonable y ninguna cuestionaba la estructura; la suite en
  verde y la auditoría de otro agente se informaban como avance. El usuario lo señaló: "si no lo
  menciono vos volvés a caer en ese vicio y siempre estamos parcheando fallas". Desde entonces,
  un arreglo del mecanismo dentro de una estructura equivocada cuenta como parche, y lo que
  cuenta como evidencia son conversaciones reales contra la IA real (`AGENTS.md`, "Cómo pensamos
  juntos", punto 12).
- **La regla del mozo, en revisión (2026-10-04).** El análisis la encontró correcta para datos
  y efectos, y señaló como causa del código disperso su extensión a cada movimiento de la
  conversación (qué se pregunta después, cuándo va el resumen, qué se ofrece): sólo el alta
  llegó a tener 25 sucesos con hechos redactados por el código. El extremo opuesto también falló
  (el flujo B inventó). No está decidido cómo queda: qué decide la IA y qué decide el código se
  fija en el ADR 0018.

## Modelos

Pruebas reales (2026-10-03, una corrida por modelo, guiones distintos):

| | flash | luna | sol | Gemini 3.8 flash |
|---|---|---|---|---|
| Quién hizo qué | bien | **mal** (invirtió quién rechazó) | bien | bien |
| Inventa datos o propuestas que no muestra | no | **sí** | no | **sí** (un criterio) |
| Causas o promesas falsas | 2 | 0 | 0 | 0 |
| Muletillas | "Perfecto", "Listo" | «¿te sirve?» | «¿te sirve?» | "Tomamos…" |

Banco (tarea 0-24, 2026-10-03; 386 llamadas reales sin caché; por mensaje del alta):

| Modelo | Tiempo típico / peores casos | Costo por mensaje |
|---|---|---|
| flash (`deepseek-v4-flash`, por el proveedor `nan`) | 19,0 / 21,8 s | ~USD 0,0002 (estimado) |
| luna (`openai/gpt-6-luna`) | 7,9 / 9,5 s | USD 0,0007 |
| sol (`openai/gpt-6-sol`) | 11,0 / 13,8 s | USD 0,016 |
| Gemini (`google/gemini-3.8-flash`), tope de siempre | 12 de 15 mensajes con aviso de falla | — |
| Gemini, tope 4000/3000 | 20,7 / 27,0 s | USD 0,011 |

Lo que se aprendió de los modelos: luna y sol mandan todos los campos vacíos (el código lee
vacío como "no lo dijo"); Gemini razona por dentro y necesita un tope de salida propio (el
tope por modelo es un pendiente importante de la plataforma); el proveedor `nan` no limita el razonamiento
de flash, por eso es lento.

Estas mediciones son del flujo C6, congelado el 2026-10-04. Para el flujo D se mantiene GPT-6 sol
y falta volver a medir GPT-6 luna (ADR 0018). Medido el 2026-10-05 y 06 (sol, luna, GPT-6.1 sol y
Claude Sonnet 5.5) en "Rondas automáticas del flujo D".
