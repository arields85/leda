# Las correcciones de la prueba por Telegram del 2026-10-12

**Rama:** `feat/motor-de-conversacion` · **Abierta:** 2026-10-12, noche · **Copia en Engram:** tema
`odd/correcciones-prueba-telegram/tasks` (proyecto `prisma-pm`)

## Objetivo

Corregir lo que mostró la prueba por Telegram de la Fase C (bitácora de flujos, "Prueba por Telegram real
de la Fase C (2026-10-12)"): las decisiones 77 a 79 y los hallazgos que les siguen en
[`fase-c.md`](fase-c.md).

## Por qué y autorización

La prueba pasó; el usuario marcó cómo habla Leda de lo que hace la cocina. Pidió avanzar de forma
autónoma con esto mientras la plataforma espera su presencia (2026-10-12, noche) y autorizó una ronda con
la IA real, al final, de las conversaciones que toquen estos cambios ("si, autorizo").

## Chequeo de rumbo

- **Qué clase de problema:** la cocina le pasa a la IA hechos que no tiene que contar (a quién y a qué
  hora llega un aviso) o con nombres que la IA repite ("pregunta"). Ya apareció con "previsión"
  (`9b7c6f4`) y se resolvió en la frontera de la redacción, no en las instrucciones. Mismo mecanismo.
- **Mecanismo general, no caso:** sí: los hechos de los avisos a otros, todos a la vez; los nombres de los
  datos, en `hechos.para_redactar`; los íconos, en la forma que da la cocina (decisión 74), por estado.
- **Qué haría innecesaria la próxima ronda:** que la regla viva en los hechos y no en frases.
- **Cocina o mozo:** cocina; la IA no recibe frases ni ejemplos nuevos (regla del mozo).
- **Qué lo demuestra:** las conversaciones tocadas, con la IA real (autorizada), y la próxima prueba del
  usuario por Telegram.
- **Para parar:** si un hallazgo pide cambiar el diseño (las tres salidas de un tema, ADR 0018, decisión
  4), se escribe su conversación de prueba y se deja la propuesta para el usuario, sin código.

## Tareas

Ruta: cada una, un escritor delegado (toca el motor, sus pruebas y las conversaciones); el coordinador
revisa, corre la revisión RDD de cada commit y lleva este documento.

- [x] **T1 · Íconos por estado (decisión 79).** Hoy la IA pone 🗓️ por instrucción
      (`motor/instrucciones.py`); la cocina reconoce los renglones de una tarea (`salida.py`) y cambia el
      ícono según el estado que dicen los hechos del turno: 🏁 terminada, 🟢 en curso y al día, ⚪ sin
      empezar o sin novedades, 🔵 entregada, 🟠 atrasada, 🔴 trabada. El 📋 de una sola tarea no cambia.
- [x] **T2 · "Consultar", no "preguntar" (decisión 78)**, en los nombres que lee la IA
      (`hechos.para_redactar`).
- [x] **T3 · Sin nombre ni hora en los avisos a otros (decisión 77).** Los hechos de un aviso a otra
      persona no le pasan a la IA el destinatario ni la hora; sí que quedó asentado y, si hace falta,
      cuándo vuelve a escribirle a la persona, en palabras de todos los días. El nombre y la hora, sólo si
      la persona los pregunta.
- [x] **T4 · El comentario de una aprobación que contesta "¿cuál de las dos?"** sale del mensaje original
      (llegó «pasale lo de los colores»).
- [x] **T5 · Una tarea terminada no "vence".**
- [ ] **T4b · La advertencia de la revisión de la T4** (`aprobacion.py:246-254`): una pregunta de
      "¿cuál de las dos?" vieja que siga abierta no puede pisar el comentario de una aprobación escrita
      después, que no la contesta. Test primero.
- [ ] **T6 · La hora de los turnos en el registro** (los pasos 22 a 25 figuran a las 10:02): investigar y,
      si quedó mal guardada, corregirla. **Evidencia (coordinador, 2026-10-12, `leda_motor`):** quedó mal
      guardada. `conversation_turn.at` sale de `reloj.ahora()` (`turno.py:232`). Turnos de Marcos
      (`inbound_message.at` real → `conversation_turn.at`): n.º 6 15:47:05 → mar 10:02:17; n.º 18
      15:54:38 → 10:31:32; n.º 26 16:22:36 → **10:02:18**; n.º 28 16:23:06 → 10:02:42; n.º 34
      16:27:13 → 10:06:50; n.º 37 16:40:03 → mié 10:03:25. A las 16:22 el reloj de Leda estaba cerca
      de las 11:58 del martes (la pregunta a Ariel se programó a las 12:15:15, 30 minutos después del
      último mensaje de Ariel, a las 11:45:15). El adelanto implícito del n.º 26 (17:39:42) es menor que
      el del n.º 18 (18:36:54): el reloj pareció ir para atrás en esos turnos.
- [ ] **T7 · "Dejalo pendiente, después lo hago"** en medio de una entrega, y "Anoté" dicho de un
      borrador: conversación de prueba; si pide cambiar el diseño, propuesta al usuario.
- [ ] **T8 · La entrega nueva que se contradice** ("dejé la foto para cuando vuelvas a entregarla" y
      "¿confirmás la entrega así?"; contó lo que esta vez no se escribió).
- [ ] **T9 · Ronda con la IA real** de las conversaciones tocadas (autorizada), bitácora.
- [ ] **T10 · Cierre:** suites, `docs/STATUS.md`, este documento y las memorias.

## Criterio de aceptación

Cada corrección con su conversación de prueba o su prueba determinista en rojo antes y en verde después;
`correr --ia guionada` en seco, bien; `pytest tests/motor tests/garantias tests/conversaciones` en verde;
cada commit de código revisado por RDD; la ronda con la IA real sin fallas de garantía y sin horas ni
nombres de otros en los mensajes.

## Progreso y evidencia

- 2026-10-12, noche: documento abierto.
- **T1, hecha** (escritor delegado; `11780ef`, más `e599d42` del coordinador: el corrector del formato
  del corredor acepta los íconos como marca de tarea). La cocina cambia la marca de cada renglón de una
  tarea, en una lista de dos o más, por el ícono de su estado, después de que redacta la IA
  (`hechos.con_los_iconos` en `turno`, `avisos._enviar` e `informe_al_grupo._uno`; `salida.iconos_por_estado`);
  las instrucciones de la IA no cambiaron. RED: `tests/motor/test_iconos_por_estado.py` 15 de 15 en rojo.
  `pytest tests/motor` 1346 passed; `tests/conversaciones` 214 passed (más la de `e599d42`, 57 passed en
  `test_comprobar.py`); `test_formato_de_salida.py` 27 passed; en seco 48 de 48. Repaso del coordinador:
  `test_iconos_por_estado.py` 17 passed. **RDD:** `review-fd5b12f57ba236dc`, aprobada. Advertencias sin
  arreglar: el título se busca como parte del renglón y un título contenido en otro podría confundirse
  (`salida.py:546-555`); el paso de los íconos, después de la IA, no tiene una guarda propia
  (`hechos.py:1731-1747`); sugerencia: títulos repetidos (`hechos.py:1750-1757`). A observar en la ronda
  real: que la IA copie los íconos de mensajes anteriores en un mensaje de una sola tarea.
- **T2, hecha** (escritor delegado; `b2f4afa`, más `f599ca8` del coordinador). Lo que lee la IA al
  redactar dice "consulta/consultar" cuando Leda le escribe a alguien para saber algo (doce nombres
  nuevos en la frontera y otros nueve reescritos; unos 80 significados); "pregunta" queda sólo para la
  pregunta de este mensaje y para lo que la persona pregunta. Adentro no cambió ningún nombre. El
  coordinador cambió una palabra de la instrucción de redacción ("un aviso, un recordatorio o una
  consulta") y su huella (`71b74fdaea8a436d`). RED: 4 de 17 en rojo en
  `tests/motor/test_palabras_de_la_redaccion.py`. `pytest tests/motor` 1350 passed;
  `tests/conversaciones` 215 passed; en seco 48 de 48. **RDD:** `review-cdfe60231c85d84d`, aprobada; dos
  sugerencias sobre las pruebas (sólo el primer párrafo; una expresión sensible a mayúsculas).
- **T3, hecha** (escritor delegado; `8d49d42` y `9f5ac67`). En la frontera de la redacción
  (`hechos.para_redactar` → `_sin_nombre_ni_hora`), un aviso a otra persona (un hecho con `llega` o con
  su clave en `hechos.AVISOS`, unas 30) pasa a la IA sin el destinatario ni la hora, que quedan en
  `solo_si_pregunta` (el paso 7 del guion sigue: preguntado, dice a quién y cuándo); lo que Leda le va a
  hacer a la misma persona (`hechos.AVISOS_A_LA_PERSONA`) llega con el día, que la cocina ya dice "hoy",
  "mañana" o "vie 16/10", nunca la hora; los hechos de la cocina no cambian. Una prueba lee el motor y
  falla si aparece un aviso nuevo fuera de la regla. Instrucciones de redacción: lo que se entera otra
  persona "quedó asentado"; huella `1b181215b77350b8`. Además, el arreglo de la advertencia de la T1:
  si falla el paso de los íconos, el texto sale igual y queda un incidente leve
  (`motor_iconos_por_estado`). RED: `test_avisos_sin_nombre_ni_hora.py` 10 de 12 en rojo; dos de
  `test_iconos_por_estado.py`. `pytest tests/motor` 1364 passed; `tests/conversaciones` 215 passed;
  `test_formato_de_salida.py` 27 passed; en seco 48 de 48. Repaso del coordinador:
  `test_avisos_sin_nombre_ni_hora.py` 12 passed. **RDD:** `review-7f672eb05058d717`, aprobada.
  Advertencia sin arreglar: el día sale de recortar el texto de la fecha (`hechos.py:1657`); con una hora
  en UTC entre las 21 y las 24 locales daría el día siguiente (los hechos van en hora local y ningún
  aviso sale a esa hora). Sugerencias: la clave del incidente, su falla sin prueba, la unión de
  `solo_si_pregunta`, un significado vacío. A observar en la ronda real: "el administrador" sigue
  nombrado por la clave (sin la hora) y un aviso que no salió se cuenta sin a quién.
- **T4 y T5, hechas** (escritor delegado; `d9ebbf0` y `64796ac`). T4: una respuesta escrita a "¿cuál de
  las dos?" sólo elige la lectura; el comentario sale del mensaje que abrió la pregunta, guardado con la
  opción (`aprobacion._la_lectura_elegida`), como ya pasaba con el botón; la conversación 23 pide ahora
  el comentario original (`~que revise los colores`). Límite: "aprobala y además decile X" perdería X
  (sin regla). T5: de una tarea `terminada` o `cancelada`, la IA no recibe `vence` ni `fecha_objetivo`, y
  ese día sale de `dias` si ningún otro hecho lo nombra (`hechos._sin_vencimiento_si_cerro`, en
  `para_redactar`); la pregunta al encargado por el detalle lleva ahora el `estado`. RED: 5 de 8
  (T4) y 6 de 9 (T5). `pytest tests/motor` 1377 passed; `tests/conversaciones` 215 passed; en seco 48 de
  48. Repaso del coordinador: `test_terminada_no_vence.py` y `test_aprobacion.py`, 62 passed. **RDD:**
  `review-488b6f52cd3b174d`, aprobada; advertencia: una pregunta vieja abierta puede pisar el comentario
  (T4b, arriba); sugerencia: la forma del estado (`hechos.py:1510-1514`).
