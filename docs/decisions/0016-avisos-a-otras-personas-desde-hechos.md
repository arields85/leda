# ADR 0016: Los avisos a otras personas se guardan como hechos y se escriben al salir

- **Estado:** aceptada por decisión del usuario, 2026-10-03
- **Fecha:** 2026-10-03
- **Alcance:** `message_outbox`, `despachador`, `alta_conducida`, `ingreso_tareas`,
  `gateway` y la función `confirmar_borrador_tarea`. Aplica la enmienda del alta
  conducida del ADR 0014 ("nunca un texto armado") a lo que ve otra persona.
- **Evidencia:** tarea P-1b de `odd/tasks/circuitos-al-flujo-nuevo.md`; migración
  `0029_avisos_desde_hechos.sql`; `tests/test_avisos_desde_hechos.py`.

> **Nota del 2026-10-04.** Este ADR se trajo sin cambios desde la rama congelada
> `feat/flujo-de-un-mensaje` (etiqueta `respaldo-flujos-antes-de-d`). Su decisión sólo está
> implementada en esa rama: la migración `0029`, la prueba y el documento de tareas que cita no
> existen en esta. Si el motor de conversación trae este mecanismo, y con qué regla para los
> reintentos, está `PENDIENTE` en el ADR 0018 (el Motor).

## Contexto

Todo texto que ve una persona lo escribe la IA desde los hechos (P-1, decisión del
usuario del 2026-10-03). Para quien actúa, eso ya existía (P-1a): si la IA falla, un
incidente y el aviso neutro. Un aviso a OTRA persona (quien confirma un borrador, quien
lo pidió, el responsable) es distinto: nadie lo está esperando en ese momento, y el
aviso neutro le diría "no pude responder tu mensaje" a quien no escribió nada. Además
dos textos terminales los escribía una función de la base, en la transacción de la
autoridad.

## Decisión

1. **Un aviso a otra persona se encola como hechos.** `message_outbox` admite una fila
   sin texto: `hechos` (qué pasó, para quién, los botones que pone el código, lo que
   esa persona puede hacer y, si va, la lista exacta de datos del resumen), la marca
   `pendiente_de_redactar` y `intentos_redaccion`.
2. **El despachador escribe el texto justo antes de enviarlo**, después de las reglas
   de vigencia, retención por rama abierta, horario y tope: el texto refleja el estado
   de ese momento (y el saludo del día de quien lo recibe). Lo que hay que escribir va
   al final de cada pasada, para que la respuesta a quien actuó no espere esa llamada.
3. **Si la IA falla, el aviso espera.** Se reprograma con la espera creciente de los
   avisos a la administración (1, 2, 4 y 8 minutos). Al quinto intento: la fila queda
   `fallido` con sus hechos (no se pierde), un incidente para la administración y quien
   causó el aviso recibe el aviso de falla del proveedor con lo pendiente. Nunca sale un
   texto armado.
4. **La función de la base guarda hechos.** `confirmar_borrador_tarea` deja de escribir
   sus dos textos terminales: su fila lleva los hechos y un minuto de gracia. El turno
   del toque escribe el texto (la IA con el alta conversada; el alta guiada, congelada,
   conserva sus textos); si ese turno no llega, el despachador lo escribe. Una respuesta
   a quien actuó no espera: si la IA falla, sale el aviso neutro.

La idempotencia no cambia: la misma clave de deduplicación por aviso, y los avisos de
coordinación siguen fuera del tope diario.

## Consecuencias

- Una llamada más a la IA por cada aviso a otra persona, fuera del turno de quien actúa.
- Un aviso que sale fuera de horario se escribe cuando sale, no cuando se causó.
- Elegir otro comportamiento ante la falla (por ejemplo, avisar enseguida) queda para
  una configuración de la plataforma, más adelante; hoy es este.
- Deshacer: `db/rollbacks/0029_avisos_desde_hechos.sql`, que falla cerrado si queda una
  fila sin texto en la cola.
