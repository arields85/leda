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

- [ ] **T1 · Íconos por estado (decisión 79).** Hoy la IA pone 🗓️ por instrucción
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
      si quedó mal guardada, corregirla.
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
