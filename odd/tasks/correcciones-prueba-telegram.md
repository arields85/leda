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
- [ ] **T2 · "Consultar", no "preguntar" (decisión 78)**, en los nombres que lee la IA
      (`hechos.para_redactar`).
- [ ] **T3 · Sin nombre ni hora en los avisos a otros (decisión 77).** Los hechos de un aviso a otra
      persona no le pasan a la IA el destinatario ni la hora; sí que quedó asentado y, si hace falta,
      cuándo vuelve a escribirle a la persona, en palabras de todos los días. El nombre y la hora, sólo si
      la persona los pregunta.
- [ ] **T4 · El comentario de una aprobación que contesta "¿cuál de las dos?"** sale del mensaje original
      (llegó «pasale lo de los colores»).
- [ ] **T5 · Una tarea terminada no "vence".**
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
