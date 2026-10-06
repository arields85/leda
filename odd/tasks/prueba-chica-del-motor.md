# La prueba chica del Motor (Etapa 2)

**Rama:** `feat/motor-de-conversacion` · **Carpeta:** `D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion`
**Abierta:** 2026-10-04 · **Copia en Engram:** tema `odd/prueba-chica-del-motor/tasks` (proyecto `prisma-pm`)
**Estado:** decidido (sección 10, 2026-10-05); E2-1 a E2-7, E2-3b, `informar_avance`, el ancla en la
previsión, los tres hallazgos de la corrida en seco, la tarea vencida (9j), la conversación 15 alineada
con 9j, la revisión de la corrida con las 16 y la jugada `destrabar` (9l, conversación 17) hechos; sigue
la E2-8.

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
| `destrabar` (tarea), desde el 2026-10-05 | responsable; tarea `bloqueada`, con un solo bloqueo abierto | `resolver_bloqueo`: la tarea vuelve al estado de antes | cierra la pregunta de quién destraba, lo propuesto y sus esperas; con el seguimiento ya empezado, vuelve a pedir el estado el día hábil siguiente (9l) |
| `consultar_pendientes` | nada | lee con `consultar_tareas` | nada |
| `informar_avance` (tarea, palabras), desde el 2026-10-05 | responsable; tarea abierta; un pedido de estado abierto | hecho de avance con sus palabras, auditado; ni estado ni fecha | la espera sigue abierta; vuelve a pedir el estado el día hábil siguiente sin contarlo como silencio; a la segunda, pregunta para cuándo |
| `entregar`, `pedir_reasignacion` | nada | sin efecto; hechos de qué no se puede y quién lo decide | sin aviso al administrador (9g) |
| `elegir`, `corregir`, `cancelar`, `dejar_para_despues` | las de su situación general | | |

Hecho en la E2-3 (`prueba_chica/fichas.py`): la comprobación común (datos que faltan, la tarea
por su alias, que sea del responsable y su estado vigente) es una sola para todas las fichas.
Quién destraba llega como `quien` (texto), `no_sabe` o `nadie_mas` (le toca a la persona,
anotada como quien destraba; nombrarse a sí misma es lo mismo), y el código decide si es un
integrante (un solo nombre que coincide en el equipo) o alguien de afuera; si coinciden varios,
falta el dato. Todo bloqueo con causa pregunta quién lo puede destrabar: la IA ya no juzga si
depende de otro (`depende_de_otro` se quitó tras el primer contacto real, 2026-10-05). El orden de
las preguntas es de la E2-4 (abajo). Inicio, previsión, bloqueo y quién destraba contestan
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

Hecho en la E2-4 (`preguntas.py`, `situaciones.py`, `botones.py`): una sola pregunta abierta por
persona y las demás para después. De varias cosas en un mensaje, la primera que pregunta queda
abierta y las otras para después; si la abierta es de un mensaje anterior, Leda sigue a la persona
y la de antes queda para después. Al terminar el turno, si no quedó una abierta, vuelve la más
vieja de las de después, y la redacción recibe la única pregunta que se hace (`pregunta`, con
`desde_antes`). Cada ficha declara qué preguntas contesta (`contesta`) y cómo se deshace lo que
anota (`deshacer`): el resto es común. La duda pregunta con las tareas en que la jugada vale; un
toque y la elección escrita corren el mismo camino (`elegir_opcion`). Una corrección sólo vale
sobre algo anotado en los últimos turnos de la persona. Los botones los agrega al entregar un
transporte del motor, porque el despachador sólo arma los de los flujos congelados.
Resuelto en la E2-5: una corrección que vuelve a una previsión anterior cuyo aviso se había
retirado sin salir lo vuelve a guardar. Desde la E2-5, una opción que ya no se puede usar deja
la duda abierta (`pregunta_sigue_abierta`); una a la que le falta un dato la cierra, y lo que
falta es la pregunta siguiente.

**Escalera.** Propia; `escalera.py` no se toca. El aviso previo sale N días hábiles antes (N en
`workspace_setting`: 3 en CoreWork, mínimo 1, comprimido si la tarea tiene menos días). Desde V, cada
recordatorio pide el estado y abre una espera en `pending_reply` (hoy nada la escribe); sin respuesta, V+1, V+2
(avisa que va a escalar) y V+3, por la ruta `falta_persistente_de_respuesta`. Se detiene con un bloqueo abierto o
una ausencia. Hallazgo: `escalera.evaluar` escala sin mirar si hubo respuesta; la de la prueba avanza sólo con la
espera abierta.

Hecho en la E2-5 (`escalera.py`): un paso por vez, nunca dos el mismo día hábil, con clave por
tarea, vencimiento y paso; el primer pedido abre la espera y, al salir, la pregunta del estado
(`estado_de_la_tarea`, que no se puede dejar sin efecto y contestan inicio, previsión, bloqueo y
quién destraba); el tercero dice a quién se va a escalar; el escalamiento va a todos los de la
ruta (la del área antes que la general), nunca al responsable. Una ausencia la pausa y lo
guardado no le llega; a la vuelta de una que tocó el período de la escalera, un reencuadre
reemplaza lo guardado (desde V pide el estado) y la escalera retoma desde donde quedó. Sin
`aviso_previo_dias_habiles`, el mínimo del núcleo (un día hábil) y un incidente de severidad baja
por cada aviso previo que sale con él; sin ruta, un incidente una vez y la espera queda escalada.
Desde la E2-6 (revisión de la E2-5): la escalera es de un vencimiento y termina al escalar o
con una respuesta (o un bloqueo); un paso que no llegó por otra cosa (la IA no lo redactó, con
su incidente) cuenta como dado y sigue el próximo, con los hechos de cuántos no le llegaron; un
vencimiento nuevo empieza de cero, con su propia espera.
Desde el 2026-10-05 (ADR 0018, 9i; `ancla.py`): la escalera corre sobre su ancla, la fecha
comprometida o la previsión vigente si es posterior. Con el ancla en la previsión, el día del
vencimiento sale un solo recordatorio que no pide nada; el día de la previsión se pide el estado y,
sin respuesta, sigue la escalera hasta escalar. El ancla va en la clave de cada paso: un ancla
nueva es una escalera nueva. La fecha comprometida y el atraso contra ella no cambian.

**Avisos guardados.** Todo lo que Leda manda por su cuenta se guarda como hechos. Al llegar su hora, dentro del
horario, el código vuelve a leer la tarea; si corresponde, la IA lo redacta y va al outbox; si no, se omite con su
motivo (9b). El de una nueva previsión va como `es_coordinacion` (lo causa el acto de otra persona, mecánica §10).
Hecho en la E2-5 (`avisos.py`): cada tipo se declara una vez con su regla de vigencia; los de la
escalera se redactan con los hechos de ese momento, y un efecto que pasa después dice su estado.
El aviso a un ausente espera a que vuelva. El comando `avisar` va por el mismo camino.

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
- [x] **E2-4. Situaciones generales** (delegada: writer, varios archivos no triviales): las ocho, con
      preguntas, opciones y correcciones; los toques en el escuchador; el arreglo del escuchador de la
      revisión de la E2-3b (una falla al recibir un update deshace lo suyo, no avanza el offset y se
      reintenta; a los tres intentos, incidente y texto fijo). Evidencia (2026-10-05): `pytest
      prueba_chica` en rojo en cada paso (escuchador, `3 failed`; situaciones contra el código anterior,
      `24 failed`; toques, error de colección sin `procesar_toque`; instrucciones, `1 failed`; botones y
      toques en el escuchador, `3 failed`; opción ajena a la duda, `1 failed`) y en verde, `159 passed`.
      Ningún caso especial por circuito (5c.1). Commits `f8bc71b`, `09ede28`, `ee7bf25` y `071092e`; lo
      registra el commit que sigue. Unas 2.070 líneas, 890 de pruebas: más que la guía, porque cada
      situación lleva su prueba de base.
- [x] **E2-5. Escalera y avisos guardados** (delegada: writer, varios archivos no triviales): aviso
      previo, esperas, escalamiento, relectura, omisión y reintentos; el envío del aviso de
      corrección; el pendiente de la E2-4 (rearmar el aviso de una previsión anterior); y los
      dos arreglos de la revisión de la E2-4 (`elegir` no cierra la duda antes de que la ficha
      diga si se pudo; un toque que falla tres veces deja incidente y texto fijo). Evidencia
      (2026-10-05): `pytest prueba_chica` en rojo en cada paso (arreglos de la revisión, `2
      failed, 1 passed`; avisos, error de colección sin `avisos.py` y el rearmado contra la
      `fichas.py` anterior, `1 failed, 11 passed`; escalera, error de colección sin
      `escalera.py` y, con la primera versión, `1 failed, 16 passed`: un paso que reemplazó un
      reencuadre no se volvía a guardar) y en verde, `191 passed in 61.99s`. Reloj fijo que
      cruza un fin de semana y el feriado del lunes 12; IA guionada. **Decisión sobre el
      `PENDIENTE` del aviso previo:** sin `aviso_previo_dias_habiles`, el mínimo del núcleo (1) y
      un incidente por cada aviso previo que sale así; nunca se escribe la configuración.
      `PENDIENTE`: una respuesta que no es una jugada que informa (por ejemplo "voy bien", sin
      fecha) no cierra la espera; qué sigue después de que una respuesta detiene la escalera
      (por ejemplo, cuando vence la previsión); una corrección no reabre la espera que cerró el
      hecho anotado en la tarea equivocada; las etapas `motor_aviso_guardado` y `motor_escalera`
      no tienen entrada propia en `incidentes.EXPLICACION_POR_ETAPA` (está en `src/`): su aviso
      usa la explicación genérica (resuelto en la E2-6). Commits `a4d4327`, `af28776` y
      `c1ca293`; lo registra el commit que sigue. Unas 1.790 líneas, 734 de pruebas: más que la
      guía, porque cada regla de la escalera lleva su prueba con el reloj.
- [x] **E2-6. Ciclo y herramientas de prueba** (delegada: writer, varios archivos no triviales): ciclo,
      bot de administración, comando para adelantar el reloj, lector de turnos, `restriccion_horario`
      y los tres arreglos de la revisión de la E2-5. **Ciclo** (`ciclo.py`), dentro del escuchador
      (ya tiene los dos bots, el reloj y la conexión; un proceso aparte sería otro despachador): cada
      minuto la escalera y los avisos guardados; cada vuelta, el despacho con el reloj de Leda y los
      avisos a la administración con el real; cada paso en su transacción, y si se cae, un incidente
      `motor_ciclo` por racha y los demás siguen. **Reloj** (`reloj.py`): un adelanto sobre el tiempo
      real en `workspace_setting` (`motor_reloj_adelanto_segundos`), que el escuchador relee en cada
      vuelta; `despachar` recibe ese momento y decide el horario con él, sin tocar `despachador.py`;
      los tres comandos se niegan fuera de `leda_motor`. Uso: `python -m prueba_chica.reloj corework
      adelantar|estado|volver` (al día hábil siguiente, 10:00) y `python -m prueba_chica.leer corework
      [--persona X] [--desde HH:MM]`. `incidentes.EXPLICACION_POR_ETAPA` tiene `motor_escalera`,
      `motor_aviso_guardado` y `motor_ciclo`. Evidencia (2026-10-05): `pytest prueba_chica` en rojo en
      cada paso (arreglos de la revisión, `4 failed, 26 passed`; ciclo, incidentes, reloj y lector,
      errores de colección sin sus módulos, y los títulos sin su entrada, `7 failed, 35 passed`) y en
      verde, `218 passed in 69.79s`; `tests/test_restriccion_horario.py` en rojo (`1 failed, 3 passed`)
      y en verde; `tests/test_avisos_admin.py tests/test_aviso_incidente_legible.py
      tests/test_capacidades.py tests/test_restriccion_horario.py` `54 passed`; suite completa
      `2306 passed, 333 deselected, 1 warning in 780.79s` (las 4 nuevas son de `restriccion_horario`). Commits `02acd53`, `52e00a6`, `877589d`, `84f1c7a` y `6a4ad8b`; lo registra el
      commit que sigue. Unas 1.590 líneas, 692 de pruebas: más que la guía, porque cada pieza lleva su
      prueba con base, reloj y transportes falsos. Qué sigue cuando vence una previsión: resuelto el
      2026-10-05 (ADR 0018, 9i; abajo). La nota de `AGENTS.md` sobre `restriccion_horario` se
      corrigió en `5679242`.
- [x] **Agregado antes de la E2-7: `informar_avance`** (decisión del usuario, 2026-10-05; ADR 0018, 9h;
      conversación 15). El avance queda en el registro de turnos, en `audit_log` (`accion =
      'informar_avance'`) y en los hechos del pedido siguiente (`repregunta_de_estado`); sin tablas
      nuevas. Evidencia: `pytest prueba_chica` en rojo (`10 failed, 216 passed`) y en verde (`226
      passed in 79.24s`). Commits `27f517d` y `bafdf64`; lo registra el commit que sigue. La E2-7 corre
      15 conversaciones. El `PENDIENTE` de un avance después de escalar se resolvió con el ancla
      (abajo).
- [x] **Agregado antes de la E2-7: el seguimiento sigue a la previsión y arreglos de las revisiones**
      (decisiones del usuario, 2026-10-05; ADR 0018, 9i; conversación 02, pasos 4 a 7). El ancla de
      la escalera (`ancla.py`) y el recordatorio del vencimiento (`vencimiento_con_prevision`); un
      escalamiento reemplazado (por un reencuadre o un avance) no cuenta como escalado; una segunda
      escalera llega a su propio escalamiento; `informar_avance` cuenta por espera (la espera en la
      clave del pedido, sin duplicados), toma la tarea con un candado que la escalera prueba antes de
      cada paso, y sin vencimiento o con la escalera ya escalada no guarda otro pedido y lo dice en
      sus hechos. Revisados los avisos al referente contra "Leda es la PM": sólo información.
      Evidencia (2026-10-05): `pytest prueba_chica/test_escalera.py` en rojo (`1 failed, 21
      passed`, el escalamiento reemplazado); `test_ancla.py` en rojo (`5 failed, 2 passed`);
      `test_avance.py` en rojo (`5 failed, 7 passed`); `pytest prueba_chica` en verde, `240
      passed`. Tres pruebas cambiaron por la decisión (una previsión ya no detiene la escalera para
      siempre). Commits `cf11eaa`, `afb17a3`, `431deef`, `5e01734` y el commit que registra esto.
      `PENDIENTE`: qué sigue después de una respuesta que no es una previsión (un inicio) cuando la
      tarea sigue sin entregar. Resuelto en la E2-7: el escalamiento espera si el responsable está
      ausente el día que sale (mecánica §9, ausencias).
- [x] **E2-7. Corredor** (delegada: writer, varios archivos no triviales). `python -m prueba_chica.correr`
      (uso en `prueba_chica/README.md`): las 15 conversaciones en YAML (`prueba_chica/conversaciones/`,
      cada una con su `fuente`), cargador del estado inicial (lo anterior corre por el motor como
      preludio), una base por corrida desde una plantilla, el reloj en los momentos del `.md`, el
      transporte falso, las comprobaciones (garantía, comprensión provisional y motor), grabar y
      repetir, Jev en paralelo, la libreta del gasto con el techo (10.4) y el informe en
      `prueba_chica/resultados/`. Arreglos de la revisión del ancla: cada anclaje (la racha de una
      fecha en la cadena de previsiones) es una escalera nueva, y repetir la misma fecha no; el
      escalamiento guardado espera la ausencia del responsable. Evidencia (2026-10-05):
      `test_ancla.py` en rojo (`2 failed, 8 passed`) y `test_escalera.py` en rojo (`1 failed`); las
      pruebas del corredor se escribieron con su código (sin rojo previo); `pytest prueba_chica` en
      verde, `275 passed in 98.61s`. **Corrida en seco** con la IA guionada que elige las jugadas
      esperadas (`--ia guionada --veces 1`, informe `resultados/2026-10-05-en-seco-guionada.md`):
      12 de 15 bien y garantías 15 de 15; las 3 fallas son del motor, no del YAML, y no se torcieron:
      (1) **03**: la pregunta de quién destraba no abre una espera ni se repite el día hábil
      siguiente (pasos 2 a 4), y las salidas propuestas no quedan como tema abierto (paso 5); (2)
      **12**: el ofrecimiento de una previsión ante una reasignación no queda como tema abierto
      (paso 2); (3) **13**: los avisos automáticos del día a una persona no se juntan en un envío
      (mecánica §10): salen dos avisos previos. Ninguna se arregla en el corredor; cómo se
      resuelven lo decide el usuario (si es una regla general del motor, sin caso especial: 5c.1).
      Confirmado al escribir los YAML: ninguna comprobación depende de `blocker.abierto_en` ni de
      `task_state_event.at` en hora real. Commits `5206bb8`, `94d5378`, `93647f3`; lo registra el
      commit que sigue. Unas 4.250 líneas, 1.400 de YAML: más que la guía, porque cada conversación
      lleva sus comprobaciones paso por paso.
      **Comandos de la E2-8** (los lanza el agente que coordina; nunca los corre una prueba):
      `python -m prueba_chica.correr --ia sol --veces 5 --jev --paralelo 5 --grabar prueba_chica/grabaciones`
      y `python -m prueba_chica.correr --ia luna --veces 5 --paralelo 5 --grabar prueba_chica/grabaciones`.
      **Costo estimado** (lo que el techo reserva antes de empezar; con las 16, abajo): unas 105
      llamadas por vuelta a las 15, con un margen de 1,25 por lo que se manda de más; sol, a USD 0,016 la llamada (la cifra
      por mensaje del banco del 2026-10-03, del lado alto), unos USD 10,5 la ronda de 5; Jev, unos
      USD 0,4 (estimado: no informa su costo); luna, unos USD 1. Las dos rondas, unos USD 12 de 30,
      debajo del aviso del 80 %. Desde la primera ronda el techo usa el costo medido por llamada.
      `PENDIENTE`: medir lo que cuesta Jev; la lectura de los textos y la comprensión que vale son
      del usuario (10.3); la sugerencia de la revisión sobre `ancla.escalo` no se aplicó (el
      writer no tenía el texto de la revisión).
- [x] **Agregado antes de la E2-8: los hallazgos de la corrida en seco, la tarea vencida y la
      revisión de la E2-7** (decisiones del usuario, 2026-10-05; ADR 0018, 9j y sus precisiones;
      delegada: writer, varios archivos no triviales). Reglas generales, sin caso por conversación
      (5c.1): (1) toda pregunta cuya ficha dice que espera respuesta abre su espera y la repite la
      escalera de quien no contestó, hasta escalar (`preguntas.TIPOS`, la escalera de una pregunta
      en `escalera.py`; la de quién destraba, conversación 03); (2) lo que Leda propone queda como
      tema abierto (`preguntas.PROPUESTA`, `Ficha.propone`; conversaciones 03 y 12); (3) los avisos
      automáticos de una persona que salen juntos van en un solo envío (mecánica §10; los de
      coordinación, aparte; conversación 13); (4) con la tarea vencida, una respuesta sin fecha se
      anota y lleva la pregunta de para cuándo (9j; conversación 16, escrita primero). Revisión de
      la E2-7: una corrida que se cae deja su gasto en la libreta y el informe dice "Ronda cortada";
      el techo a mitad de la ronda sale con 2 y otra caída con 1; la plantilla se borra aunque falle
      y al salir, y las bases viejas del corredor se borran al empezar; la prueba del techo no
      necesita el servidor; un bloqueo resuelto que falta es de comprensión; el emparejamiento es
      máximo; los avisos al administrador se cuentan por espacio; un mensaje que junta tareas se
      compara con todas; el recorrido de la cadena de previsiones no se cuelga con un ciclo; un paso
      guardado con la clave de antes sigue siendo de su ancla (lectura del agente de "compatibilidad
      del formato de la clave"); el aviso previo una sola vez tiene su prueba. Evidencia
      (2026-10-05): `pytest prueba_chica` en rojo en cada paso (corredor, `5 failed, 1 passed, 1
      error`; comparación y ancla, `4 failed, 34 passed`; preguntas que esperan y propuestas,
      `9 failed`; un envío por día, `3 failed, 1 passed` y el corredor, `1 failed, 2 passed`; la
      tarea vencida, `4 failed, 2 passed`) y en verde, `305 passed in 110.31s`. Siete pruebas
      cambiaron por las decisiones (una pregunta sin contestar ahora escala; las salidas quedan
      abiertas). **Corrida en seco** `python -m prueba_chica.correr --ia guionada --veces 1 --ronda
      seco-2` (informe `resultados/seco-2.md`): 16 de 16 bien, garantías 16 de 16, ninguna falla.
      **Con las 16** (E2-8): unas 114 llamadas por vuelta; sol, unos USD 11,4 la ronda de 5; luna,
      unos USD 1,1; Jev, unos USD 0,4: unos USD 13 de 30, debajo del aviso del 80 %. Los comandos de
      la E2-8 no cambian. `PENDIENTE`: el paso 2 de `tests/conversaciones/15-avance-vago.md` (el
      primer avance, con la tarea vencida) todavía dice que no pregunta nada (fuera de lo autorizado
      a este writer; su YAML ya sigue 9j); un aviso automático que se guarda más tarde el mismo día,
      después del envío de la persona (por ejemplo, con el comando `avisar`), sale en otro envío.
      Commits `3d6f07d`, `d2a855f`, `03a20be`, `df2d8ee`, `5aa1a67` y el commit que registra esto.
- [x] **Agregado antes de la E2-8: la conversación 15 con 9j y la revisión de la corrida con las 16**
      (2026-10-05; delegada: writer, varios archivos no triviales). Sin decisión nueva ni caso por
      conversación. **La 15** empezaba con la tarea vencida y su paso 2 contradecía 9j: ahora D es el
      martes 27 (el vencimiento); el primer avance se anota sin pregunta y Leda vuelve a pedir el estado
      el miércoles; el segundo, con la tarea ya vencida, lleva la pregunta de para qué día (9j, que acá
      coincide con 9h); la fecha es una previsión con su aviso a Ismael y el pedido del martes 3 sale con
      el aviso previo de la otra tarea en un solo envío (9i, mecánica §10). `.md`, YAML y `README.md`
      iguales; resuelto el `PENDIENTE` de esa conversación (el del ADR 0018, 9j, queda para quien edite el
      ADR). **La revisión**, reglas generales: lo que una jugada propone espera si se pregunta la fecha de
      la tarea vencida, y ninguna pregunta se pierde en los hechos; la jugada que esperaba una opción corre
      por el manejador de la lista cerrada del turno, como una escrita (la regla 9j ya valía para una
      opción escrita o tocada: dos pruebas la fijan); una pregunta que queda para después abre su espera
      cuando se hace, no antes; los avisos de un envío que la IA no redactó se reintentan juntos, y un
      texto más largo que el canal se reintenta en lugar de cortar la vuelta; el corredor compara los
      hechos esperados con el aviso de ese tipo y esa tarea; la limpieza borra sólo bases con el nombre que
      pone el corredor, y su prueba usa un momento fijo; un ciclo en la cadena de previsiones es su final;
      la regla 9j con el ancla en una previsión tiene su prueba; la ronda cortada sale con 1. Evidencia
      (2026-10-05): `pytest prueba_chica` en rojo en cada paso (un tema a la vez, `4 failed, 2 passed`;
      un envío por día, `2 failed, 4 passed`; el emparejamiento, `1 failed, 3 passed`; la limpieza, `1
      failed`; el ciclo, `1 failed, 1 passed`) y en verde, `316 passed in 116.42s`. **Corrida en seco**
      `python -m prueba_chica.correr --ia guionada --veces 1 --ronda seco-3` (informe
      `resultados/seco-3.md`): 16 de 16 bien, garantías 16 de 16, ninguna falla. Con la 15 nueva, 113
      llamadas por vuelta; el gasto previsto de la E2-8 no cambia. Commits `4b3681f`, `6a15381`,
      `8b8e7e1`, `705f99c`, `bfd7cf2` y el commit que registra esto. **Segunda revisión**
      (`review-47083832b5965548`): cada aviso cuenta sus intentos y falla solo al quinto, y los que
      siguen se reintentan juntos al próximo más cercano; cada aviso de un envío va con sus propios
      hechos; cada clave de pregunta de los hechos tiene una sola forma. Rojo `2 failed` (reintentos),
      `1 failed` (hechos), `1 failed` (clave); verde `320 passed in 116.89s` (una vez, antes,
      `1 failed, 319 passed`, intermitente, no se repitió en dos corridas); `--ronda seco-4`: 16 de
      16, garantías 16 de 16. Commits `aea7cdc`, `12e2f88`, `1fb58dd` y el que registra esto.
- [x] **Durante la E2-8: la revisión del contrato entre la IA y el código** (usuario, 2026-10-05; ADR
      0018, 9k; delegada: writer, varios archivos no triviales). **Resultado de la primera ronda**
      (`resultados/ronda1-sol.md` y `ronda1-luna.md`, commit `3bc32b5`; USD 2,61 y 0,14): con sol,
      garantías 5 de 5 en 01 a 04, 06, 07, 10 y 13 a 16; fallan 05 (3 de 5: "con el plc" como causa),
      08 (0 de 5: un motivo que no era un porqué), 09 (4 de 5; la vez 5 sin jugada hizo caer el
      corredor), 11 (0 de 5: una previsión con su porqué anotada también como bloqueo), 12 (0 de 5:
      "¿le avisaste a alguien?" como fuera de la lista, con aviso al administrador) y la comprensión
      de 13 (0 de 5: sin jugada ante la duda, sin botones). En la lectura: el atraso de una previsión
      contado como el de hoy (15 y 16), respuestas sin próximo paso (03, 07, 11, 12) y, en 11, el
      sistema narrado por dentro. Luna, peor (05, 07, 08, 09, 12 en 0 de 5). **La revisión**, como
      reglas generales, sin caso por conversación: (A) el vocabulario de los hechos
      (`hechos.py`): claves distintas para cosas distintas (`atraso_dias_habiles`, el de hoy;
      `atraso_si_se_cumple_la_prevision_dias_habiles`, el previsto), los avisos al referente dicen
      qué aviso son y que no piden respuesta, y los dos pedidos a la IA llevan el significado de cada
      clave y código que traen; un hecho sin significado es una falla del motor en la corrida; (B)
      cada jugada es una variante del esquema con su definición (`Ficha.es`) y sólo sus datos, que
      dicen qué son y que van sólo si la persona los dijo; (C) con la jugada clara y la tarea no, la
      jugada va sin la tarea y el código pregunta con botones; (D) una pregunta sobre la conversación
      no lleva jugada y se contesta desde el registro; fuera de la lista es sólo un pedido de hacer
      algo; (E) la redacción deja siempre un próximo paso y nunca narra el sistema. **Medición:** Jev
      guarda los valores de su verificación (`misma`, `rival`) y el informe los muestra; la IA que no
      elige tarea cuenta como que preguntó; un botón que no está es una falla del paso, no una caída;
      con `puede_traer`, un dato libre vale sólo si son palabras de la persona. Ningún YAML necesitó
      `puede_traer` nuevo: 05 y 11 ya lo tenían donde el `.md` no dice nada, y 08, 15 y 16 dicen "sin
      motivo". Evidencia (2026-10-05): `pytest prueba_chica` en rojo en cada paso (esquema, `4
      failed, 20 passed`; vocabulario, `5 failed, 10 passed`; medición, `4 failed, 3 passed`) y en
      verde, `334 passed in 119.69s`. **Corrida en seco** `python -m prueba_chica.correr --ia guionada
      --veces 1 --ronda seco-5` (informe `resultados/seco-5.md`): 16 de 16 bien, garantías 16 de 16,
      ninguna falla, ningún hecho sin significado. Commits `aac2261`, `78c3016`, `5bf7b3e` y el que
      registra esto. `PENDIENTE`: cerrar un bloqueo cuando su causa desaparece (11, "llegó el
      switch") no es ninguna jugada: agregarla lo decide el usuario (9k); que el proveedor real
      acepte el esquema con `anyOf` no se probó (sólo con la IA guionada); la próxima ronda real lo
      muestra. **Claude Sonnet 5.5** (2026-10-05): el esquema lo aceptan sol y Sonnet; Sonnet rechazaba
      (400) la herramienta forzada con `tool_choice`, que pasó a `auto` para todos, con las
      instrucciones pidiendo llamarla siempre (no llamarla sigue siendo no responder). Humo real 01 y
      02, una vez, con Sonnet y con sol: 2 de 2 bien, sin incidentes (USD 0,37); `pytest prueba_chica`
      `336 passed`; en seco, 16 de 16.
- [x] **La jugada `destrabar`** (decisión del usuario, 2026-10-05; ADR 0018, 9l; conversación 17,
      escrita primero; resuelve el `PENDIENTE` de 9k). Con ella, la revisión de `ia_real`: un mensaje
      sin la forma de una respuesta también es no responder, y un texto en lugar de la herramienta,
      en el turno, es un reintento y después el camino de falla. Evidencia (2026-10-05): `pytest
      prueba_chica` en rojo, `11 failed, 341 passed`; en verde, `353 passed in 126.38s`; en seco,
      `--ronda seco-7`, 17 de 17, garantías 17 de 17 (informe borrado). Commits `3ca7fa7`, `6c90cd1` y
      el que registra esto. `PENDIENTE`: deshacer un `destrabar` con `corregir` (hoy, "no se
      corrige"); elegir cuál con varios bloqueos abiertos; y, en un mismo mensaje, una jugada
      posterior que deja sin efecto el pedido que guardó una anterior (destrabar o un avance
      seguidos de una fecha): los hechos de la primera lo siguen contando.
- [x] **Los hechos de lo que pasa después, al final del turno** (ADR 0018, 9k, precisión del
      2026-10-05; resuelve el último `PENDIENTE` de arriba) y, de la revisión
      `review-e8b69f0cca8677ef`, destrabarse antes del vencimiento: el aviso previo que el bloqueo
      omitió vuelve a salir. Evidencia (2026-10-05): `pytest
      prueba_chica/test_hechos_al_final_del_turno.py` en rojo, `4 failed, 2 passed`; `pytest
      prueba_chica` en verde, `360 passed in 131.15s`; en seco, `--ronda seco-8`, 17 de 17,
      garantías 17 de 17 (informe borrado).
- [x] **Ronda 2 inválida, sin crédito** (2026-10-05, 21:21 en adelante): OpenRouter rechazó 1.226
      llamadas con HTTP 402 (sol, 235; sol61, 505; Sonnet, 486) y la libreta las estimaba como
      cobradas: mostró USD 29,84 y cortó Sonnet (26 corridas) por un techo falso. Corregido: una
      llamada que falló (error HTTP, plazo, sin respuesta) cuesta 0 y no se estima; sólo se estima
      la que respondió sin informar su uso. Libreta corregida desde las grabaciones: ronda2-sol USD
      1,63, sol61 0,68, Sonnet 0,13; **la etapa, USD 6,26 de 30** (0,70 de Jev, estimado). Informes
      como evidencia del corte en `resultados/ronda2-invalida-*.md`. **Leda durante el corte,
      observado** (decisión 8): ningún efecto sin IA (Sonnet, las 59 corridas afectadas, sin fallas de
      garantía), el texto neutro "Tuve un problema y no pude responder tu mensaje..." (134 veces en
      Sonnet) y un incidente por turno (`turno_conversacion`, `motor_aviso_guardado`). Las tres fallas
      de garantía de sol61 (03 v4, 11 v3 y 11 v5, efectos de más) son de corridas mezcladas con 402 y
      no se analizaron: la ronda se repite. Evidencia: `pytest prueba_chica/test_gasto.py` en rojo,
      `1 failed, 12 passed`; `pytest prueba_chica` en verde, `361 passed in 121.34s`.
- [x] **Tercera y última vuelta de ajuste** (usuario, 2026-10-06; ADR 0018, 9m; 5c.3), después de la
      ronda 2 válida (`resultados/ronda2-sol.md`: garantías 17 de 17 conversaciones 5 de 5;
      comprensión 05, 1 de 5; las demás 5 de 5; informes y libreta en `c50f81a`). Reglas generales,
      ningún caso: las jugadas de un mensaje se aplican en orden (reemplaza "una sola jugada", el
      renglón tocado por dos arreglos seguidos; el motor ya las aplicaba en orden en la misma
      transacción y las pruebas nuevas lo fijan); el próximo paso según la definición del usuario,
      con `lo_que_sigue` en los hechos; lo anunciado en un turno anterior que ya no va a pasar se
      dice una vez (`ya_no_sale`); el día de la semana y hoy/ayer/mañana/pasado mañana de cada
      fecha, del código (`dias`); "la persona que escribe" en lugar de "ella"; una respuesta cortada
      por el tope es no responder (tope de redacción 2000); los significados, de fondo. Las
      conversaciones: la casilla del próximo paso en cada paso en que Leda escribe, los cuatro
      próximos pasos vagos hechos concretos y la 16, paso 3, como regresión de lo anunciado.
      Evidencia (2026-10-06): en rojo, `pytest prueba_chica/test_jugadas_en_orden.py` `2 failed,
      4 passed` (las instrucciones y las fichas; las cuatro del motor ya pasaban), las de lo
      anunciado y lo que sigue, de los días y del corte, sin el código nuevo (error de importación;
      el corte, `4 failed, 38 passed`); en verde, `pytest prueba_chica` `392 passed in 127.42s`; en
      seco, `--ronda seco-9`, 17 de 17, garantías 17 de 17 (informe borrado). Commits `b15290e`,
      `7d76376`, `0faaaae`, `4ae0b9a`, `fc8df0c`, `9076d28`, `a977ad6` y el que registra esto.
      `PENDIENTE`: la ronda 3, sólo con GPT-6 sol (decisión del usuario), y su lectura; la fecha de
      `hoy` y de las horas de los últimos turnos se toma como viene escrita (un `at` en UTC cerca de
      la medianoche daría el día de UTC).
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

**Próximo paso:** la ronda 3 de la E2-8, sólo con GPT-6 sol (decisión del usuario, 2026-10-06),
cinco veces cada una de las 17, después de la tercera y última vuelta de ajuste (ADR 0018, 9m);
lectura de textos, con la casilla del próximo paso en cada mensaje, y chequeo de rumbo contra 5c:
si no se alcanza 5b, no hay otra vuelta de ajuste: se revisa el diseño con el usuario (5c.3).
