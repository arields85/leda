# ADR 0005: interpretar con tolerancia, confirmar todo cambio, aclarar con botones

- **Estado:** aceptada
- **Fecha:** 2026-09-24
- **Alcance:** toda conversación en la que Prisma interpreta un mensaje y puede
  producir un cambio
- **Diseño y evidencia:** [`architecture/interpretacion-y-confirmacion.md`](../architecture/interpretacion-y-confirmacion.md)

## Decisión

1. **Todo cambio relevante lleva vista previa y confirmación.** Prisma muestra qué
   va a cambiar —recurso, estado actual, estado nuevo— y que todavía no se aplicó
   nada, con **Confirmar**, **Modificar** y **Cancelar**. Sin Confirmar no hay
   efecto. Vale para mensajes claros y ambiguos.

   **Precisión (2026-09-29, decisión del usuario): el borrador del alta guiada.** Su
   vista previa tenía sólo Confirmar y Cancelar, y un dato equivocado obligaba a
   cancelar y rearmar la tarea. Pasa a tener **Confirmar**, **Modificar** y
   **Cancelar**. Modificar pregunta qué dato cambiar, con un botón por dato. Un dato de
   texto muestra lo que la persona había escrito, en un bloque que se copia con un
   toque (y el botón de copiar de Telegram cuando entra en sus 256 caracteres), para
   que lo pegue, lo corrija y lo mande; un dato que se elige con botones (responsable,
   área, objetivo) vuelve a mostrar sus opciones. Cambia sólo ese dato, lo demás queda
   como estaba, y vuelve la vista previa actualizada con los mismos tres botones. La
   tarea se sigue creando sólo con Confirmar. Telegram no permite que un bot escriba
   texto editable en la caja de la persona (sólo un marcador de 1 a 64 caracteres, o
   una consulta inline precedida por el nombre del bot), por eso se copia y se pega.
2. **La vista previa es la protección principal.** Detectar la ambigüedad reduce
   preguntas y errores, pero no se confía en esa detección para evitar un efecto
   equivocado.
3. **Ante una ambigüedad material, botones con propuestas completas.** Cada botón
   dice la acción entera ("Pasar «Cablear tablero máq. 3» a revisión"), más
   **Ninguna, lo escribo**. Elegir un botón lleva a la vista previa; no aplica nada.
   Sólo la ambigüedad que cambia el efecto frena; si no hay candidatos reales, se
   pide la referencia en texto, sin botones inventados.
4. **Cuando Prisma pregunta, pregunta con botones.** Las respuestas posibles se
   ofrecen como opciones ("¿Terminaste la tarea?" → Sí / No / Todavía no sé). El
   texto libre queda para lo que no tiene opciones concretas.
5. **Los apodos se aprenden preguntando.** Una referencia a una persona que no
   coincide con nadie se aclara con botones; la respuesta registra el apodo para
   esa persona dentro del espacio. El apodo lo confirma una persona, queda visible
   y se puede borrar, se audita, y nunca concede identidad ni autoridad.
6. **El modelo interpreta; el código decide.** El modelo separa las referencias
   del mensaje sin ver tareas ni equipo. Si hay ambigüedad y qué se propone lo
   decide código determinista contra PostgreSQL.

## Por qué

**Prisma adivinaba.** En el banco conversacional, una dependencia entre dos tareas
existentes se tomó como pedido de tarea nueva en 10 de 10 corridas: el router veía
sólo el texto.

**Y ejecutaba sin mostrar.** Cambiar un estado, registrar o resolver un bloqueo y
crear una dependencia se aplicaban en el mismo turno. Un error de interpretación
se convertía directamente en un dato equivocado.

**La referencia se puede resolver bien en código.** Con las referencias separadas
por el modelo y resueltas por palabras distintivas y embeddings, los 15 mensajes
escritos por el usuario dieron el resultado correcto y ninguno eligió una tarea
equivocada (prueba 5.1).

**La intención, no.** Con `deepseek-v4-flash`, clasificar el mismo mensaje cinco
veces no mostró ninguna duda en los ocho casos ambiguos, y pedir las lecturas
posibles detectó la mitad, falló el ejemplo de puntuación del usuario y tardó
hasta 73 segundos (prueba 5.2). La literatura coincide: los modelos, por defecto,
eligen en lugar de señalar la duda. Por eso la seguridad no puede depender de que
el modelo se dé cuenta; depende de que la persona vea y confirme.

**Preguntar con botones evita la ambigüedad en su origen.** "no se iso lo que se
pidió martin" es "No sé, hizo lo que pidió Martín" o "No, se hizo lo que pidió
Martín". Si la pregunta llega con opciones, esa respuesta libre no ocurre.

**Una lista fija de apodos envejece.** La gente cambia de apodo; aprenderlo al
preguntar evita mantenimiento manual.

## Alternativas rechazadas

- **Confiar en que el modelo detecte y declare su duda.** La prueba 5.2 lo
  descartó para el modelo actual.
- **Clasificar varias veces y medir el acuerdo.** 0 de 8 ambiguos detectados.
- **Usar el `rerank` como señal de duda.** Ordena bien, pero elige con fuerza
  incluso ante referencias ambiguas.
- **Ejecutar directo los mensajes claros.** Un mensaje "claro" mal interpretado es
  justamente el error que la vista previa atrapa.
- **Una lista de apodos cargada a mano.** Envejece y nadie la mantiene.
- **Aclarar con preguntas abiertas.** Obligan a volver a escribir y vuelven a
  producir texto ambiguo.

## Consecuencias

- **Las herramientas que escriben dejan de ejecutar directo.** `registrar_bloqueo`,
  `resolver_bloqueo`, `actualizar_estado`, `crear_dependencia`,
  `quitar_dependencia`, `adjuntar_evidencia`, `aprobar_tarea` y `crear_objetivo`
  pasan a preparar una propuesta durable (`pending_action`) que sólo se aplica al
  confirmar, con relectura, revalidación de autoridad y ejecución única.
- **El router deja de decidir "tarea nueva" sin mirar lo que existe:** las
  referencias se resuelven antes contra las tareas del espacio.
- **Excepción acotada al aprendizaje persistente.** `AGENTS.md` lo deja fuera del
  producto sin decisión explícita; esta es la decisión, limitada a los apodos con
  las condiciones del punto 5. Cualquier otro aprendizaje persistente sigue fuera.
- **Más toques por cambio.** Todo cambio pide al menos un toque, y uno ambiguo,
  dos. Es el costo aceptado de no aplicar nada mal interpretado.
- **La receta de resolución es provisional.** Los cortes y reglas se ajustaron
  sobre los mismos datos que los validaron; falta confirmarlos con mensajes no
  vistos. Se ajustan en el documento de diseño sin reabrir esta decisión.
- **El banco mide la solución, no la descubre.** Sus escenarios verifican que no
  haya efecto sin confirmación, que lo ambiguo pregunte y que lo claro no
  pregunte de más.
