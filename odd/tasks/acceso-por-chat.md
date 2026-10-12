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

## Tareas

Ruta de cada una: delegada (un escritor), porque toca la base, el motor y el corredor.

- [ ] **A-1 · La conversación 50** (`.md` y `.yaml`) y la clave nueva del corredor para el enlace de la
      web. RED: el corredor en seco falla.
- [ ] **A-2 · El vencimiento de 24 horas** (`0065`, su rollback y sus garantías).
- [ ] **A-3 · Las dos jugadas y la marca del enlace** en la respuesta y el despachador.
- [ ] **A-4 · El ofrecimiento una sola vez**, también en la bienvenida.
- [ ] **A-5 · Verificación:** `correr --ia guionada` en seco, `pytest tests/garantias tests/motor
      tests/conversaciones`, revisión RDD por commit.
- [ ] **A-6 · Una ronda con la IA real de la 50** (sólo con permiso del usuario).

## Criterio de aceptación

La 50 en seco, bien; las garantías del vencimiento y del corte, en verde; cada commit de código revisado
por RDD; la 50 con la IA real, garantías 5 de 5; después, la prueba del usuario en el celular (con el
túnel, tarea aparte).

## Progreso y evidencia

- 2026-10-12, noche: diseño escrito, a la espera de que el usuario acepte la conversación 50.
