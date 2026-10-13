# El acceso a la web por chat

**Rama:** `feat/motor-de-conversacion` · **Abierta:** 2026-10-12 · **Copia en Engram:** tema
`odd/acceso-por-chat/tasks` (proyecto `prisma-pm`)

## Objetivo

Que cada integrante reciba por chat su entrada a la plataforma web y pueda cortarla si pierde el celular,
como dice la decisión 4 del [ADR 0022](../../docs/decisions/0022-plataforma-web-de-tareas.md).

## Por qué

Las porciones 1 y 2 de la plataforma construyeron el enlace de un solo uso, la sesión y el corte
(`0057`), pero hoy el enlace sólo sale por la consola (`leda enlace-web`). Sin esto, nadie entra a la web.

## Decisiones del usuario (2026-10-12)

1. **El enlace que nadie usó vence a las 24 horas**, y Leda lo dice al mandarlo (precisión de la
   decisión 4 del ADR 0022). La sesión abierta no vence.
2. **Al salir la primera versión**, Leda le ofrece el acceso a cada integrante activo que nunca entró, la
   próxima vez que le escribe, al final de su respuesta (opción A).
3. **"Perdí el celular" corta el acceso enseguida, sin confirmación** (opción A), y Leda recuerda cerrar
   Telegram en ese celular desde Ajustes → Dispositivos en otro dispositivo; sin ningún dispositivo, lo
   corta el administrador desde la consola.
4. **"Lo recuerda cuando viene al caso"** queda para una porción posterior.

## Diseño

- **Dos jugadas nuevas, sin tarea:**
  - `pedir_acceso_web`: un enlace nuevo; el anterior sin usar deja de servir (`emitir_enlace_de_entrada`
    ya lo anula).
  - `perdi_el_celular`: corta todas las sesiones de la persona con el motivo `perdio_el_celular`, que la
    `0057` ya admite (`cortar_sesiones_de_membresia`; hoy el envoltorio de Python fija `administrador`).
    El hecho le dice a la IA que recuerde cerrar Telegram en ese celular.
- **El enlace no pasa por la IA**, como el de la página de una tarea: la respuesta lleva una marca, el
  despachador emite el token al mandar (dentro del mismo punto de guardado) y agrega la dirección al
  final, sin vista previa. Hace falta una marca propia (`message_outbox_enlace.task_id` es `not null`).
- **El ofrecimiento, una sola vez:** al final del turno, si la persona nunca entró a la web ni se le
  ofreció, un hecho y la marca; el despachador reclama "ya ofrecido" al mandar, como el saludo diario
  (`greeting_state`): si el envío falla, no cuenta. Sólo en respuestas a lo que la persona escribió, nunca
  en un aviso que Leda manda por su cuenta. También en la bienvenida al conectarse.
- **El vencimiento:** migración `0065`; `canjear_enlace_de_entrada` no canjea un enlace emitido hace más
  de 24 horas; la página de un enlace vencido ya dice "Pedile a Leda uno nuevo por Telegram".
- **Quién ve la web:** la de un integrante ("Tus tareas"). La puerta de administración sigue por la
  consola; que la ofrezca el bot de administración es otra porción.

## Conversación de prueba 50, "El acceso a la web" (hilo)

Marcos nunca entró a la web; Ariel ya tiene la sesión abierta.

1. **Marcos:** "que tengo pendiente?" → sus tareas, como hoy, y al final el ofrecimiento: que ahora también
   puede ver sus tareas en la web, el enlace, que sirve una vez y vence en 24 horas, y que si no lo usa
   le pida otro. Un solo mensaje.
2. **Marcos:** "dale gracias" → contesta sin volver a ofrecerlo.
3. **Ariel:** "que tengo pendiente?" → sus tareas, sin ofrecimiento (ya entró).
4. **Marcos, al día siguiente:** "no me anda el link de la web, pasame otro" → un enlace nuevo, con el
   aviso de las 24 horas; el anterior ya no sirve.
5. **Marcos:** "casi pierdo el celular en el colectivo jaja" → no corta nada.
6. **Marcos:** "perdi el celular" → cortó el acceso a la web enseguida, sin botones; le recuerda cerrar
   Telegram en ese celular desde Ajustes → Dispositivos y pedir un enlace nuevo cuando tenga otro.
7. **Aviso automático a Marcos** (por ejemplo, el aviso previo de un vencimiento) → sin ofrecimiento.

Garantías aparte, con pruebas deterministas: un enlace de hace 24 horas y un minuto no abre; el corte deja
la auditoría con su motivo; el ofrecimiento no se repite aunque se mande dos veces la misma respuesta.

## Mapa del código y decisiones técnicas del coordinador (2026-10-13, madrugada)

Explorador de sólo lectura. Lo que hay: `enlace_de_entrada` con `emitido_en` (`0057`), un solo enlace
sin usar por persona, `canjear_enlace_de_entrada` (su `update` de canje es donde entra el vencimiento),
`cortar_sesiones_de_membresia` con el motivo `perdio_el_celular` (audita una fila por sesión cortada,
no el enlace anulado), los envoltorios en `web_app.py` (`emitir_enlace`, `cortar_sesiones`, que fija
`administrador`), la marca del enlace de una tarea (`message_outbox_enlace`, `task_id not null`; el
despachador emite el token dentro del punto de guardado del envío y agrega la dirección sin vista
previa), el saludo diario como modelo de "reclamar al mandar" (`greeting_state`), y la bienvenida con
texto fijo (`onboarding.bienvenida`, bajo `admin()`). `leda_app` no lee `enlace_de_entrada` ni
`sesion_web`: "¿entró alguna vez?" necesita una función `security definer`.

Decisiones técnicas dentro del diseño aceptado (reversibles; ninguna cambia lo que ve la persona salvo
la 4, que va a la mañana):

1. **"Ya ofrecido" se reserva al armar el turno** (la IA ya escribió la frase) y se libera si el envío
   falla y no se reintenta; así no salen dos ofrecimientos antes de que salga el primero.
2. **Un enlace por mensaje:** si la respuesta ya lleva el enlace de una tarea, el ofrecimiento espera al
   turno siguiente; `pedir_acceso_web` junto con `pedir_enlace` en el mismo mensaje da el código "ya
   lleva otro enlace", como hoy dos páginas de tarea.
3. **El corte siempre deja su auditoría**, también si la persona no tenía ninguna sesión abierta (hoy
   anular sólo el enlace no deja fila): la garantía de la 50 lo pide.
4. **Un toque no lleva el ofrecimiento** (el diseño dice "a lo que la persona escribió"); sale en su
   próximo mensaje escrito. **Confirmada por el usuario (2026-10-13): "si, dejamos como esta".**
5. **Migraciones:** la `0065` el vencimiento; la `0066` la marca del enlace de entrada (tabla nueva,
   `message_outbox_entrada_web`, con RLS forzado), el estado del ofrecimiento, la función de "entró
   alguna vez" y la auditoría del corte sin sesiones.

Reparto en commits: (1) la 50 y la clave `enlace_web` del corredor; (2) `0065`; (3) `0066`; (4) las dos
jugadas y la marca en `enqueue_outbox` y el despachador; (5) el ofrecimiento una vez y la bienvenida.

## Tareas

Ruta de cada una: delegada (un escritor), porque toca la base, el motor y el corredor.

- [x] **A-1 · La conversación 50** (`.md` y `.yaml`) y la clave nueva del corredor para el enlace de la
      web. RED: el corredor en seco falla.
- [x] **A-2 · El vencimiento de 24 horas** (`0065`, su rollback y sus garantías).
- [x] **A-3 · Las dos jugadas y la marca del enlace** en la respuesta y el despachador.
- [x] **A-4 · El ofrecimiento una sola vez**, también en la bienvenida.
- [x] **A-5 · Verificación:** `correr --ia guionada` en seco, `pytest tests/garantias tests/motor
      tests/conversaciones`, revisión RDD por commit.
- [x] **A-6 · Una ronda con la IA real de la 50** (sólo con permiso del usuario).

## Criterio de aceptación

La 50 en seco, bien; las garantías del vencimiento y del corte, en verde; cada commit de código revisado
por RDD; la 50 con la IA real, garantías 5 de 5; después, la prueba del usuario en el celular (con el
túnel, tarea aparte).

## Progreso y evidencia

- 2026-10-12, noche: diseño escrito, a la espera de que el usuario acepte la conversación 50.
- **2026-10-12, noche: el usuario aceptó la conversación 50 tal como está** ("Sí, acepto la conversación 50
  tal como está") **y autorizó la ronda con la IA real para medirla** (A-6) cuando esté construida. Se
  construye de forma autónoma después de las correcciones de la prueba por Telegram
  (`correcciones-prueba-telegram.md`); frena antes del túnel y de la prueba en el celular, que necesitan
  al usuario.
- **A-1, hecha** (escritor delegado; `b6dc364`). La 50 (`50-el-acceso-a-la-web.md`/`.yaml`), los 7 pasos
  aceptados; empieza el lunes 19/10, Ariel con la sesión abierta (clave nueva del mundo
  `sesion_web_abierta`, que emite y canjea el enlace como el botón "Entrar"). El corredor reconoce
  `https://leda.invalid/app/entrar/<token>` (`ENLACE_WEB_DE_PRUEBA`), con `Salida.enlace_web`, la clave
  `enlace_web` en los pasos y en `salen`, y dos garantías nuevas (sin vista previa; la dirección no queda
  en lo que escribió la IA), en `comprobar_los_enlaces()`; `comprobar.py` ve tres efectos nuevos
  (`enlaces_de_entrada`, `enlaces_anulados`, `sesiones_cortadas`), y uno no esperado es falla de
  garantía (así el paso 5 prueba que no se cortó nada). RED: la 50 en seco, 15 fallas (las jugadas
  `fuera_de_la_lista`, sin significado, sin enlace ni ofrecimiento). `test_la_50_en_seco_pasa_entera`,
  `xfail(strict=True)` hasta la A-4. `tests/conversaciones` 225 passed y 1 xfailed; en seco 49 de 50
  (sólo la 50). **RDD:** `review-5bf7c9c04fe0c32f`, aprobada; advertencia: el `xfail` no fija qué falla
  (`test_corredor.py:913-924`); sugerencias: el motivo del enlace anulado no se mira, una consulta de
  sesiones sin filtrar por espacio en una prueba.
  **Lo que la 50 espera de la A-2 a la A-4:** paso 1, un segundo hecho `{ofrecimiento: acceso_a_la_web,
  lleva_el_enlace_de_entrada_a_la_web, sirve_una_sola_vez, vence_a_las_24_horas}`; paso 4,
  `{jugada: pedir_acceso_web, resultado: enlace_nuevo, lleva_el_enlace_de_entrada_a_la_web,
  sirve_una_sola_vez, vence_a_las_24_horas, el_anterior_ya_no_sirve}`, un enlace emitido y uno anulado;
  paso 6, `{jugada: perdi_el_celular, resultado: acceso_cortado, sesiones_cortadas: 0,
  recuerda_cerrar_telegram_en_ese_celular, puede_pedir_otro_enlace}`, un enlace anulado; paso 7, sin
  `ofrecimiento`; cada clave con su significado; el enlace se emite al despachar. **Riesgos:** en el
  corredor todos "nunca entraron", así que la A-4 necesita que el corredor dé por ofrecido a todos salvo
  que el YAML diga otra cosa; `emitido_en` usa el `now()` real, así que las 24 horas se prueban en las
  garantías deterministas, no en el corredor.
- **A-2, hecha** (escritor delegado; `e6b4402`). `0065_el_enlace_vence_a_las_24_horas`: en
  `canjear_enlace_de_entrada`, el `update` del canje suma `emitido_en > now() - interval '24 hours'`
  (en el mismo `update` que traba la fila: dos canjes a la vez siguen abriendo una sola sesión); un
  enlace vencido devuelve `null`, como uno usado o anulado, y la página dice "Pedile a Leda uno nuevo";
  no se audita el vencimiento (0057 no audita un canje fallido; se deduce de `emitido_en`) y sigue
  contando como el enlace sin usar de la persona (otro enlace o el corte lo anulan). La puerta de
  administración no cambió (`canjear_enlace_de_administracion`, otra tabla). Rollback y `esquema.sql`.
  RED: `test_enlace_y_sesion.py` 2 en rojo (el vencido abría sesión). `test_enlace_y_sesion.py` 29
  passed; `test_migraciones.py` 16 passed; `tests/garantias` 700 passed. **RDD:**
  `review-9fc81742ea92beeb`, aprobada; sugerencias: el borde exacto de las 24 horas sin prueba, el
  rollback sin ejercitar en una prueba propia. `docs/capacidades.md` ya dice que vence a las 24 horas.
  Para `leda_motor`: `psql -v ON_ERROR_STOP=1 -f db/migrations/0065_el_enlace_vence_a_las_24_horas.sql
  "host=localhost user=postgres dbname=leda_motor"` (con `PGCLIENTENCODING=UTF8`), después del
  respaldo, junto con la `0066`.
- **A-3, hecha** (escritor delegado; `38d71f3` la base y `0e3946e` el motor). `0066_la_entrada_a_la_web_por_chat`:
  `message_outbox_entrada_web` (la marca: espacio, fila del outbox, persona, `es_ofrecimiento`) y
  `ofrecimiento_web` (`reservado_en`, `ofrecido_en`), las dos con RLS forzado y permisos mínimos;
  `entro_a_la_web()` y `tiene_un_enlace_sin_usar()`, `security definer` de `leda_owner`, sólo del espacio
  de quien llama; `cortar_sesiones_de_membresia` deja siempre una fila `cortar_acceso_web` con el motivo,
  las sesiones cortadas y si anuló un enlace, también con cero sesiones (decisión técnica 3); el
  rollback se niega si las tablas tienen filas. `web_app.cortar_sesiones` recibe `motivo` y el actor.
  Motor: `pedir_acceso_web` y `perdi_el_celular` (sin confirmación), con sus hechos y significados; la
  marca va en la misma lista que el enlace de una tarea (`ctx.enlace_de_la_respuesta`), así "un enlace
  por mensaje" sale solo (`ya_lleva_otro_enlace`); `enqueue_outbox(enlace_de_entrada_web=…,
  es_ofrecimiento=…)` reserva el lugar y rechaza partir, adjuntos, bloque copiable o dos enlaces; el
  despachador emite el token como `leda_app` dentro del punto de guardado del envío, agrega la
  dirección y manda sin vista previa; si el envío falla, el token vuelve atrás; sin dirección base,
  sale sin el enlace y queda el incidente `enlace_de_entrada_web`. RED: `test_acceso_web.py` 13 en
  rojo; `test_entrada_web_por_chat.py` 14 en rojo (las pruebas sólo de la base, escritas después del
  esquema, no se vieron en rojo). `tests/garantias` 724 passed; `tests/motor` 1417 passed;
  `tests/conversaciones` 226 passed y 1 xfailed; despachador, salida y afines 130 passed; en seco 49
  de 50 (la 50 falla en los pasos 1 y 4, que dependen del ofrecimiento). **RDD:**
  `review-56e6b9278c487733` y `review-d37523bfd05ec550`, aprobadas. Advertencias: "un enlace por
  mensaje" no lo exige la base (`0066:13-14`); **`perdi_el_celular` no anula una marca de enlace que
  todavía no salió** (`fichas.py:1306-1317`): el despachador la emitiría después del corte, al
  Telegram que puede estar en el celular perdido; va en la A-4. Sugerencias: los envoltorios sin
  prueba propia; `el_anterior_ya_no_sirve` se promete antes de emitir.
- **A-4 hecha** (2026-10-13, madrugada; escritor delegado, más de dos archivos): `fb4fc9a2` (el ofrecimiento y la bienvenida), `30f4a86f` ("perdí el celular" anula los enlaces que no salieron, la advertencia de la A-3), `3964a0e8` (los mundos de prueba con dirección pública dan la web por ofrecida) y, del coordinador, `79225200` (la IA guionada nombra el hecho del ofrecimiento; se sacó el `xfail` de la 50). Cómo quedó: `turno._ofrecer_la_web` reserva en la transacción del turno (`insert … on conflict do nothing`) salvo en un toque, con `perdi_el_celular`, con otro enlace en la respuesta, sin dirección pública, ya ofrecido, ya entró o con otro enlace pendiente; si la IA no redacta, la reserva vuelve atrás; el despachador marca `ofrecido_en` dentro del punto de guardado del envío (también para un enlace pedido) y `_fallo` la libera en una falla final. La bienvenida lleva el enlace con un texto fijo (`onboarding.OFRECIMIENTO_DE_LA_WEB`), sin partir. `web_app.cortar_sesiones` descarta en la misma transacción los mensajes sin salir de esa persona con su enlace, cada uno con un incidente bajo sin avisar; en el mismo mensaje que el corte, `pedir_acceso_web` dice `no_se_puede` (`corta_el_acceso_en_este_mensaje`). Corredor: `sin_ofrecer_la_web` (la 50: Marcos y Ariel); a los demás, ya ofrecida. `reservado_en` y `ofrecido_en`, fuera de `PROMESAS_SIN_CUMPLIR`. RED: `test_ofrecimiento_web.py` 16 en rojo y 7 en verde (los "no ofrece"). `tests/garantias` 724 passed; `tests/motor` 1440 passed; `tests/conversaciones` 227 passed y 1 xfailed (antes de `79225200`). **RDD:** `review-d0e45da44cd8972b` y `review-5d66f680d46262b9`, aprobadas; advertencias en `despachador.py:1311-1313` (el ofrecimiento se da por hecho al salir) y `web_app.py:1084-1088` (el descarte de los mensajes con el enlace al cortar); sugerencias en `test_corredor.py` y `web_app.py:1066`. Casos de borde: una respuesta cerca del tope de 4096 más el lugar del enlace la rechaza `enqueue_outbox` (ya pasaba con `pedir_acceso_web`); un ofrecimiento descartado por un corte se vuelve a ofrecer en el próximo mensaje escrito.
- **A-5 hecha** (2026-10-13, 03:22, sobre `79225200`): `correr --ia guionada --veces 1`, 50 corridas, todo lo automático bien 50 y garantías bien 50 (la 50 entera); `pytest tests/conversaciones` 227 passed; `tests/garantias` 724 passed y `tests/motor` 1440 passed (sobre `3964a0e8`; `79225200` sólo toca `tests/conversaciones`). Cada commit de código, revisado por RDD y aprobado (A-1 a A-4).
- **A-6 hecha** (2026-10-13, 03:26, sobre `a9e73268`; bitácora de flujos): la 50, 5 veces con `sol-suscripcion`: garantías 5 de 5, comprensión 5 de 5, formato 4 de 5 (vez 2, paso 6: un renglón de más de 140 caracteres, la clase conocida). Informe `resultados/2026-10-13-0326-leda.motor-sol-suscripcion.md`. **Queda, con el usuario:** el túnel o HTTPS y la prueba en un celular (la decisión técnica 4, confirmada).
- **`leda_motor` en la `0066`** (2026-10-13, madrugada): respaldo
  `db/respaldos/leda_motor-antes-0065-0066-20261013.dump` (`pg_restore --list` sin error); ensayo en una
  copia restaurada con sus dueños (`leda_motor_ensayo`, borrada): las dos migraciones sin error, RLS
  forzado en las dos tablas, las cuatro funciones de `leda_owner` y `security definer`; aplicadas con
  `psql -v ON_ERROR_STOP=1 -f` como `postgres`, sin error. Sin escuchador corriendo.

