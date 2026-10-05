# La prueba chica del Motor (Etapa 2)

**Rama:** `feat/motor-de-conversacion` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
**Abierta:** 2026-10-04 · **Copia en Engram:** tema `odd/prueba-chica-del-motor/tasks` (proyecto `prisma-pm`)
**Estado:** decidido (sección 10, 2026-10-05); E2-1, E2-2, E2-3 y E2-3b hechas; sigue la E2-4.

## 1. Objetivo

Probar con código descartable, fuera de `src/leda`, el diseño del ADR 0018 en el circuito del recordatorio
(decisión 5a con las precisiones de la 9) y cumplir **M2**: el resultado registrado en la bitácora de flujos,
pase o no, contra los criterios 5b (aprobación) y 5c (corte).

## 2. Chequeo de rumbo

- **Clase de problema:** conversación sin estado explícito y con caminos por caso (rondas 1 a 4, C1 a C6).
- **Mecanismo o caso:** mecanismo: fichas y ocho situaciones generales resueltas una vez. Cada commit del motor
  se mira contra 5c.1 (un caso especial).
- **Qué haría innecesaria la próxima ronda:** que cada falla se resuelva en una ficha o una situación general,
  con su conversación como regresión, y que correr las 14 conversaciones cinco veces sea un comando.
- **Hipótesis:** un motor chico con estado explícito elimina "se pierde o se traba". Lo decide 5b, no el plan.
- **Mecánico o fluido:** fluido: nada se confirma (9a), botones sólo en la duda, varias cosas por mensaje,
  respuesta a cualquier hora (9e). Las garantías no se tocan.
- **Cocina o mozo:** cocina: el atraso, lo que depende y quién se entera y cuándo los calcula el código; las
  instrucciones de la IA describen su trabajo, sin frases ni casos.
- **Qué lo demuestra:** las conversaciones 01 a 14, cinco corridas cada una contra la IA real, y Telegram real.

## 3. Alcance

**Entra (ADR 0018, 5a y 9):** un aviso previo tres días hábiles antes, sin pedir respuesta; desde el
vencimiento, recordatorios que piden el estado y una escalera que avanza sólo sin respuesta, hasta escalar (9b);
inicio, nueva previsión (con su aviso al referente y el atraso) y bloqueo con el arranque de la persecución
(9a, 9c), anotados directo; "qué tengo pendiente" (9g); las ocho situaciones generales (decisión 4, 9d, 9f); el
aviso al administrador de lo que no está en la lista (9g); las fallas de la IA (decisión 8).

**No entra:** entrega y aprobación (y la guarda de la decisión 2), la persecución completa, la plataforma web,
la memoria y el motor definitivo en `src/leda` (Etapa 3).

## 4. Arquitectura

**Dónde vive:** `prueba_chica/`, en la raíz. Fuera de `src/leda` (`AGENTS.md`) y fuera de `tests/`: la suite por
defecto (`testpaths = ["tests"]`) no la corre ni le aplica `tests/conftest.py`, que importa `gateway`. Tiene su
`conftest.py`. En la Etapa 3 se borra entera.

**Imports** (prueba de frontera propia, que recorre los imports en cadena, como `tests/test_capacidades.py`).
Permitidos: `leda.db`, `leda.autoridad`, `leda.herramientas.ejecutar`, `leda.calendario`,
`leda.salida.enqueue_outbox`, `leda.despachador`, `leda.incidentes.registrar_incidente`, `leda.llm`, `leda.jev`,
`leda.config`; desde la E2-3b, lo que `ejecutar` levanta como respuesta del dominio y la activación de
`leda.onboarding` (sólo importa `salida`). Prohibidos: `gateway`, `agente`, `ingreso_tareas`, `contexto`, `respuesta_unica`, `huerfanos`,
`ciclo` y `local` (los dos importan `gateway`), `escalera` y `reloj` (textos fijos). Bordes conocidos:
`despachador._rama_activa_de` llega a `ingreso_tareas` por `pendientes.ver_rama_abierta`, dentro de la función;
`herramientas.crear_borrador_tarea` y `despachador._botones` (sólo con `intake_choice_set_id`) también, y la
prueba no los usa.

**Entrada propia:** un escuchador por long polling (`local.escuchar` importa `gateway`) que guarda el mensaje en
`inbound_message`, identifica a la persona (`identificar_en_espacio`) y llama al turno. Un ciclo propio corre cada
minuto la escalera, los avisos guardados y `despachar`; nunca `reloj` ni `ciclo`, así que la escalera vieja no
corre sobre `leda_motor`.

**Un turno:** (1) lee el estado de la persona, sus tareas y los últimos turnos; (2) la IA elige jugadas de la
lista cerrada con una sola herramienta cuyo esquema es la lista (`Proveedor.responder`, existe en `main`), y nombra
las tareas por un alias de la lista que recibe; (3) el código comprueba cada jugada contra su ficha, aplica las
situaciones generales y ejecuta con `herramientas.ejecutar(..., ya_confirmada=True)`, que verifica la autoridad
igual; (4) el resultado son hechos; (5) la IA redacta desde los hechos con el tono de `persona_config`, una
respuesta por mensaje; (6) todo va al registro de turnos. Comprobado en la E2-2: `responder` no fuerza la
herramienta en ningún proveedor, así que se trae la llamada estructurada de la rama congelada (E2-3b).

**Jugadas** (ninguna confirma, por 9a):

| Jugada | Comprueba | Hace | Después |
|---|---|---|---|
| `anotar_inicio` (tarea) | responsable; `asignada` (si ya está `en_curso`, lo dice) | `actualizar_estado` a `en_curso` | cierra la espera de esa tarea |
| `anotar_prevision` (tarea, fecha, motivo) | responsable; tarea abierta | hecho de previsión con el atraso (`Calendario.habiles_entre`) | aviso guardado al referente, salvo que vuelva a la fecha comprometida |
| `anotar_bloqueo` (tarea, causa) | responsable; tarea abierta | sin causa, pregunta; con causa, `registrar_bloqueo` | con causa, siempre pregunta quién lo puede destrabar (9c, corregida el 2026-10-05) |
| `anotar_quien_destraba` (integrante, alguien de afuera, "no sabe" o "nadie más") | bloqueo abierto | hecho de quién destraba | cierra la espera; sin otra persona que destrabe, propone salidas |
| `consultar_pendientes` | nada | lee con `consultar_tareas` | nada |
| `entregar`, `pedir_reasignacion` | nada | sin efecto; hechos de qué no se puede y quién lo decide | sin aviso al administrador (9g) |
| `elegir`, `corregir`, `cancelar`, `dejar_para_despues` | las de su situación general | | |

Hecho en la E2-3 (`prueba_chica/fichas.py`): la comprobación común (datos que faltan, la tarea
por su alias, que sea del responsable y su estado vigente) es una sola para todas las fichas.
Quién destraba llega como `quien` (texto), `no_sabe` o `nadie_mas` (le toca a la persona,
anotada como quien destraba; nombrarse a sí misma es lo mismo), y el código decide si es un
integrante (un solo nombre que coincide en el equipo) o alguien de afuera; si coinciden varios,
falta el dato. Todo bloqueo con causa pregunta quién lo puede destrabar: la IA ya no juzga si
depende de otro (`depende_de_otro` se quitó tras el primer contacto real, 2026-10-05). Una pregunta nueva con otra abierta queda para después, en el orden
en que salieron; cómo se retoma, la E2-4. Inicio, previsión, bloqueo y quién destraba contestan
la espera de su tarea (`pending_reply`). Fuera de la lista es cualquier nombre que no esté en
ella; el esquema de la IA trae `fuera_de_la_lista` para decirlo (E2-3b). `PENDIENTE`:
"en curso desde el lunes" (conversación 12, paso 3) no sale de la base, porque `leda_app` no lee
`task_state_event`; el hecho dice sólo el estado.

**Las ocho situaciones, una vez:** (1) cambio de tema: lo directo se anota y los hechos traen la pregunta
pendiente; si lo nuevo pregunta, la pendiente pasa a "para después" (9d); (2) varias cosas: lo directo en una
respuesta, las preguntas de a una y en orden; (3) corrección: un hecho de corrección, nunca un borrado (9f); (4)
cancelar: cierra la pregunta si su ficha la deja dejar (la de quién destraba espera como un pedido de estado,
9c); (5) duda: las tareas como opciones con botones; (6) escrito en lugar de botón: `elegir`, el mismo camino que
el toque; (7) algo vencido: el toque de una pregunta cerrada no hace nada y se dice con qué se cerró; (8) fuera
de la lista: ninguna jugada, hechos de qué puede hacer Leda y aviso al administrador.

**Escalera.** Propia; `escalera.py` no se toca. El aviso previo sale N días hábiles antes (N en
`workspace_setting`: 3 en CoreWork, mínimo 1, comprimido si la tarea tiene menos días). Desde V, cada
recordatorio pide el estado y abre una espera en `pending_reply` (hoy nada la escribe); sin respuesta, V+1, V+2
(avisa que va a escalar) y V+3, por la ruta `falta_persistente_de_respuesta`. Se detiene con un bloqueo abierto o
una ausencia. Hallazgo: `escalera.evaluar` escala sin mirar si hubo respuesta; la de la prueba avanza sólo con la
espera abierta.

**Avisos guardados.** Todo lo que Leda manda por su cuenta se guarda como hechos. Al llegar su hora, dentro del
horario, el código vuelve a leer la tarea; si corresponde, la IA lo redacta y va al outbox; si no, se omite con su
motivo (9b). El de una nueva previsión va como `es_coordinacion` (lo causa el acto de otra persona, mecánica §10).

**Horario (9e).** `despachador._despachar_fila` ya manda las respuestas a cualquier hora y pospone lo demás;
cuándo sale un aviso a otro es un hecho de la respuesta.

**Fallas de la IA (decisión 8).** En un turno: un reintento; si vuelve a fallar, nada se ejecuta, la persona
recibe el único texto fijo, se registra un incidente y el turno queda registrado. En un aviso: reintentos a 1, 2,
4 y 8 minutos; al quinto fallo, incidente y aviso de falla a quien lo causó.

**Aviso al administrador:** un incidente de severidad baja con etapa propia y referencia al `inbound_message`, que
`registrar_incidente` lleva al bot de administración con el mensaje (`incidentes._texto_disparador`); uno por
mensaje. Verificado en la E2-3: con una etapa que `incidentes.py` no conoce, el aviso usa la explicación genérica y
su título dice "Leda no pudo responderle a" la persona, que acá no es cierto. Resuelto en la E2-3b: la etapa
`motor_fuera_de_la_lista` tiene su entrada en `incidentes.EXPLICACION_POR_ETAPA`, con un título propio. A la
persona no se le dice que se avisó salvo que lo pregunte: el hecho lo lleva en `solo_si_pregunta`.

## 5. Datos

**`leda_motor`** (no existe; se crea con autorización), con los pasos de `PRUEBA-LOCAL.md` para una base nueva
(`esquema`, que ya trae la `0030` y la `0031`; `importar --activar`, `feriados`, `modelo` con GPT-6 sol, `sembrar`),
más el aviso previo (`aviso_previo_dias_habiles` = 3 en `workspace_setting`). `pg_dump` antes de cada prueba real.

**Migraciones `0030` y `0031`**, como las demás: rollback en `db/rollbacks/`, `db/esquema.sql` al día y el ensayo
de paridad, que descubre las nuevas solo (`tests/test_task_intake.py:_migraciones_posteriores_a`). Toda tabla
nueva lleva `workspace_id` y entra en el bucle de `row level security` forzado; ninguna lleva `chat_id` ni
`callback_data` (el `chat_id` sale del integrante al encolar).

| Tabla | Qué guarda |
|---|---|
| `conversation_state` | una fila por persona: pregunta abierta, temas para después, último aviso y su tarea; `mostrado_para_confirmar` y `huella` reservadas (decisión 3.1) |
| `conversation_turn` | el registro de turnos, sólo se agrega: sentido, mensaje o fila del outbox, opción tocada, jugadas, resultado, IA, latencia, error (3.2) |
| `conversation_question` y `conversation_option` | las preguntas de Leda (tipo, tarea, si se puede dejar, cuándo y cómo se cerró) y las opciones de una duda, con `token` único |
| `task_forecast` | las previsiones, sólo se agrega: fecha, motivo, fecha comprometida, atraso, a cuál reemplaza, si es corrección, quién; espacio derivado de la tarea por disparador |
| `blocker_unblocker` | quién destraba: un integrante, alguien de afuera o "no sabe" (exactamente uno), quién lo dijo y cuándo |
| `scheduled_notice` | los avisos guardados: tipo, tarea, destinatario, turno que lo causó, hechos, hora, estado (guardado, enviado, omitido, fallido), intentos, motivo de omisión, clave de deduplicación |

Los momentos de las tablas nuevas los pone el motor con su reloj, nunca un valor por omisión. Queda resuelto
cómo se guarda quién destraba (ADR 0017, 3a); qué pasa si dice que no le corresponde sigue `PENDIENTE`. Hechas en
la E2-1: los temas para después son preguntas sin cerrar con `para_despues_en`, y la tarea del último aviso sale
del aviso; las referencias a `membership` e `inbound_message` las comprueba un disparador (su restricción con el
espacio es de la `0002`). **Ejecución única:** `inbound_message.telegram_bot_id` y un índice único por espacio,
bot, chat y mensaje; el escuchador inserta con `on conflict do nothing` y una reentrega no crea turno. Los flujos
congelados no informan el bot y siguen igual.

**Estado inicial.** `sembrar` carga todo a diez días y rechaza un espacio con tareas, así que las corridas usan un
cargador propio que escribe como `admin` el estado de cada conversación (tareas, eventos, bloqueos,
dependencias, previsiones, estado de la conversación, lo ya enviado). Telegram parte de `sembrar` y el mismo
cargador ajusta fechas. Sin dependencias informativas: `herramientas._avisar_dependencia_informativa` les manda
un texto fijo.

## 6. Cómo se corren las conversaciones

- `tests/banco` entra por `gateway.procesar_update`: se toman sólo su idea de grabar la IA para repetir una falla
  con `ProveedorGuionado` y su reporte de latencias (`tests/banco/reporte.py`, sin imports de Leda).
- Cada conversación se traduce a un YAML en `prueba_chica/conversaciones/`; el `.md` sigue siendo la fuente.
- Cada corrida, en una base creada desde una plantilla y borrada al final (como
  `tests/conftest.py:_con_base_efimera`), con reloj simulado en las fechas de referencia (octubre y noviembre de
  2026) y `despachador.TransporteDePrueba`. La IA recibe la fecha de hoy como hecho.
- **Se comprueba solo:** jugadas y datos, efectos en la base, avisos con sus hechos (el atraso), esperas, botones,
  una respuesta por mensaje y estado de la conversación. **Lo que dice cada texto y la comprensión:** decisión
  10.3.
- **Puntaje (5b):** sobre la 01 a la 12, garantías 5 de 5 y comprensión al menos 4 de 5 en cada una; la vez que no
  entiende, pregunta sin efecto. La 13 y la 14 miden a Jev.
- GPT-6 sol decide; luna corre las mismas conversaciones aparte (decisión 6); Jev recibe cada mensaje con las
  tareas candidatas y su elección se registra sin decidir (decisión 7).
- En la bitácora, por ronda: fecha, commit, IA, la tabla de 14 por 5, tiempo por turno (mediana y peor caso, sin
  umbral), costo si el proveedor lo informa y la conclusión frente a 5b y 5c.

## 7. Prueba por Telegram real

Con las condiciones de `AGENTS.md` (espacio de prueba, datos ficticios, secreto protegido, efectos reversibles,
respaldo, nada destructivo, nada `CRITICAL` o `HIGH` abierto). El bot y el paso de los días, sección 10;
`tools/restriccion_horario.py` tiene que admitir `leda_motor`. El escuchador lo corre el usuario, con el `.env`
que copia él (el agente no lo lee). Se lee con `tools/leer_conversacion.py` (los toques se ven como su código) y
un lector del registro de turnos de la prueba.

## 8. Criterios

Los del ADR 0018, sin cambios: aprobación con los tres de 5b; corte con cualquiera de los tres de 5c. Pase o no,
el resultado va a la bitácora y cumple M2.

## 9. Tareas

Primero en rojo donde hay una prueba determinista: aislamiento de las tablas nuevas, paridad, frontera de imports,
ejecución única, outbox, días hábiles, escalera y fichas con `ProveedorGuionado`. Lo que hace la IA no tiene rojo:
su evidencia son las corridas. Unas 400 líneas por tarea es una guía, no un tope.

- [x] **E2-1. Tablas** (delegada: writer, varios archivos no triviales): `0030`, `0031`, rollbacks, `esquema.sql`,
      paridad, aislamiento, ejecución única. Evidencia (2026-10-05): `tests/test_motor_tablas.py` en rojo (14
      fallas, tablas inexistentes) y en verde (`14 passed`); `tests/test_task_intake.py tests/test_task_drafts.py`
      `132 passed` (paridad y rollbacks, ahora también con restricciones e índices); suite completa `2300 passed,
      333 deselected, 1 warning in 763.56s`. Commit `7265716`; lo registra el commit que sigue. Unas 1.400 líneas:
      cada tabla va en su migración y en `esquema.sql`. `tests/test_capacidades.py` declara las tablas, usadas desde
      `prueba_chica/`. Revisión RDD `review-03f111a243648455`, aprobada; su observación de que una previsión puede
      reemplazar a otra de otra tarea se corrige en la E2-3.
- [x] **E2-2. Esqueleto y frontera** (delegada: writer, varios archivos no triviales): `prueba_chica/`, prueba de
      imports, turno y registro, falla de la IA en un turno, el despachador sin retener en `leda_motor`. Evidencia
      (2026-10-05): `pytest prueba_chica` en rojo (no existía `prueba_chica.ia`) y en verde (`13 passed`); la
      frontera falla con un import prohibido de prueba; `tests/test_capacidades.py tests/test_motor_tablas.py`
      `17 passed`. Bordes conocidos: `pendientes.ver_rama_abierta`, `despachador._botones` (no estaba en el plan)
      y `herramientas.crear_borrador_tarea`, los tres hacia `ingreso_tareas`. Si la redacción falla, lo ya
      manejado se deshace (punto de guardado). Resuelto el `PENDIENTE` de la sección 4: `responder` no fuerza la
      herramienta en ningún proveedor; el adaptador de la E2-3b trae la llamada estructurada. Commit `1673e97`;
      lo registra el commit que sigue. Unas 980 líneas, la mitad pruebas.
- [x] **E2-3. Jugadas y fichas** (delegada: writer, varios archivos no triviales): lista cerrada, fichas,
      atraso, aviso al administrador; que una previsión sólo reemplace a otra de la misma tarea. Evidencia
      (2026-10-05): `pytest prueba_chica` en rojo con la lista vacía (`23 failed, 16 passed`) y en verde
      (`39 passed`); `tests/test_motor_tablas.py` en rojo con la previsión de otra tarea (`1 failed, 14 passed`);
      `tests/test_motor_tablas.py tests/test_capacidades.py tests/test_task_intake.py tests/test_task_drafts.py`
      `151 passed`; suite completa `2302 passed, 333 deselected, 1 warning in 782.58s`. Correcciones de las revisiones: la previsión reemplaza sólo a
      otra de su tarea (`0031`, E2-1); un mensaje corre una sola vez (candado por persona e índice único de un
      turno de entrada por mensaje), los turnos se ordenan por `conversation_turn.numero` (una columna de
      identidad no sirve: el `truncate ... restart identity` de las pruebas exige ser dueño de la secuencia) y el
      recorrido de imports entra en los paquetes y falla con un módulo que no encuentra (E2-2). El equipo de
      prueba sigue a las conversaciones (Marcos responsable, Ismael referente). Commits `249e593`, `47ede6a`,
      `43db5e1` y `4e2e182`; lo registra el commit que sigue. Unas 1.350 líneas, la mitad pruebas.
- [x] **E2-3b. Primer contacto real** (decisión del usuario, 2026-10-05; `AGENTS.md`, punto 5): se adelantan de la
      E2-6, completos y con sus pruebas, el escuchador y la redacción de la IA; el aviso se dispara con un comando,
      sin el ciclo; se crea `leda_motor` (autorizado) y el agente apunta a ella el `.env` de la carpeta
      (autorizado). Guion corto por Telegram con el usuario: "arranqué", "llego el 27" y "estoy trabado". Leda
      todavía no maneja cambio de tema, corrección ni cancelar (E2-4): una mala respuesta ahí no es falla del
      diseño. Va a la bitácora como prueba parcial, no como M2.
      **Construido (2026-10-05; falta el contacto real con el usuario):** correcciones de la revisión de la E2-3
      (lo que levanta la operación del dominio es un hecho, previsión y bloqueo exigen tarea abierta, quién
      destraba por palabras enteras sin comodines; `1dfab4a`); el aviso al administrador va en `solo_si_pregunta`
      y su etapa tiene título propio en `incidentes.py` (`031613e`); la llamada que fuerza la lista cerrada y la
      redacción, con sus instrucciones (`972dc35`); el escuchador (`1f0cd12`); el comando del aviso previo y la
      guía en `prueba_chica/README.md` (`0f2aa6b`). `pytest prueba_chica` en rojo en cada paso (24 fallas de las
      correcciones; 1 del aviso; módulos inexistentes) y en verde, `111 passed`; `tests/test_avisos_admin.py
      tests/test_capacidades.py` y `test_aviso_incidente_legible.py` `50 passed`; suite completa `2302 passed,
      333 deselected, 1 warning in 780.59s`.
      **Contacto real (2026-10-05, 12:13 a 12:35, `leda_motor`, GPT-6 sol, el usuario como Marcos):** aviso
      previo, "arranque", la previsión al 27 y el bloqueo con "no sé quién" salieron con la jugada y la tarea
      correctas, sin incidentes (bitácora de flujos, "Primer contacto real del flujo D"). Dos hallazgos, los dos
      de la cocina: (1) la respuesta dijo que Ismael estaba avisado con el aviso sólo guardado, porque su hecho
      no decía el estado; todo hecho de un efecto que pasa después lo dice ahora (`a9abb05`); (2) la IA juzgó
      que el repuesto no dependía de otro y Leda no preguntó quién lo destraba; por decisión del usuario, todo
      bloqueo con causa pregunta quién lo puede destrabar y decide la respuesta (ADR 0018, 9c, corregida;
      `13e574b`). `pytest prueba_chica` en rojo (4 y 6 fallas) y en verde, `120 passed`. La persecución
      completa (ADR 0017, decisión 3a) va a la prueba siguiente, no a la Etapa 2 (usuario, 2026-10-05). Lo
      registra el commit que sigue.
- [ ] **E2-4. Situaciones generales** (delegada): las ocho, con preguntas, opciones y correcciones. Unas 400.
- [ ] **E2-5. Escalera y avisos guardados** (delegada): aviso previo, esperas, escalamiento, relectura, omisión y
      reintentos. Unas 450.
- [ ] **E2-6. Ciclo y herramientas de prueba** (delegada): ciclo, bot de administración, comando para adelantar
      el reloj, lector de turnos, `restriccion_horario` (el escuchador y la redacción van en la E2-3b). Unas 300.
- [ ] **E2-7. Corredor** (delegada): los 14 YAML, base por corrida, reloj, comprobaciones, reporte, luna y Jev.
      Unas 650.
- [ ] **E2-8. Primera ronda real:** sol, luna y Jev; lectura de textos; bitácora; chequeo de rumbo contra 5c.
- [ ] **E2-9. Telegram real** con el usuario; su juicio; M2 en la bitácora.

**Previsión:** unas 3.600 líneas (código, pruebas y YAML). **Entrega:** `main` no recibe código hasta M2 o M3
(`AGENTS.md`), así que no hay cadena de PR que decidir ahora; cada tarea anota sus commits. Push y PR, del usuario.

## 10. Decisiones del usuario (2026-10-05)

1. **Bot de Telegram:** uno nuevo, sólo para la prueba, para que las bases nunca se mezclen. Lo crea el usuario
   en BotFather y pone el token en el `.env` de la carpeta (el agente no lo lee); se le pide antes de la E2-6.
2. **El paso de los días en Telegram:** un comando que adelanta el reloj de Leda sólo en `leda_motor` (por
   ejemplo, al día hábil siguiente, 10:00), con la restricción de horario prendida, para que los días hábiles y
   el atraso salgan bien. Va en la E2-6.
3. **Quién juzga los textos y la comprensión:** el agente lee todas las corridas contra lo que cada paso "dice" y
   "no dice" y arma la tabla; el usuario lee al menos una corrida por conversación y todas las marcadas como falla,
   y su lectura es la que vale. Sin una IA juez.
4. **Gasto en IA:** un techo de USD 30 para toda la etapa, con aviso al acercarse; al llegar, se le pregunta al
   usuario antes de seguir. El corredor (E2-7) lleva la cuenta.
5. **Avisos guardados:** en la tabla nueva `scheduled_notice`, no en columnas de `message_outbox`; el mensaje entra
   al outbox recién cuando la IA lo redactó. Anotado como precisión en el ADR 0018, decisión 8.

**Decidido en el plan:** la carpeta; las tablas como migraciones del producto (ADR 0018, decisión 3); el aviso
previo en `workspace_setting`, no en el importador; el referente es quien aprueba según la política del espacio
(resuelto en la E2-3: el `aprobador_membership_id` del responsable, la regla de `autoridad.puede_aprobar_tarea`;
`fichas.referente`); el aviso al administrador como incidente; el de previsión como coordinación.

## 11. Riesgos y próximo paso

- **El despachador retiene según las ramas de los flujos viejos** (enredo 2); en `leda_motor` esas tablas quedan
  vacías, y la E2-2 lo prueba.
- **El saludo diario** lo antepone el despachador (`saludo.reclamar_y_anteponer`); se mantiene: lo decidió el
  usuario.
- **Columnas viejas en hora real** (`blocker.abierto_en`, `task_state_event.at`) durante las corridas;
  `PENDIENTE` confirmar al escribir los YAML que ninguna conversación depende de ellas.
- **La etapa no es tan chica:** si una tarea pide un caso especial, se frena (5c.1).

**Próximo paso:** la E2-4 (situaciones generales).
