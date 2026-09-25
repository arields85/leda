# ADR 0006: Jev resuelve referencias y detecta la duda de intención

- **Estado:** aceptada
- **Fecha:** 2026-09-24
- **Alcance:** el paso de interpretación que decide a qué tarea o persona se
  refiere un mensaje y si su intención es dudosa, antes de proponer un cambio
- **Complementa:** [`ADR 0005`](0005-interpretacion-y-confirmacion.md)
- **Evidencia:** [`architecture/interpretacion-y-confirmacion.md`](../architecture/interpretacion-y-confirmacion.md), pruebas 5.1 a 5.9

## Decisión

1. **Jev** (TypeSafe AI, modelo `typesafe/jev-1.13` vía OpenRouter) decide a qué
   tarea se refiere cada referencia y si la intención de un mensaje es dudosa. Lo
   hace eligiendo entre opciones con una probabilidad por opción, no generando
   texto.
2. **El modelo de conversación sigue siendo el configurado** (hoy
   `deepseek-v4-flash` vía NaN): separa las referencias del mensaje, conversa y
   redacta. Jev no conversa.
3. **Receta inicial**, validada con un lote de mensajes no visto:
   - por referencia a tarea, una llamada con dos preguntas: alcance (una tarea,
     varias, ninguna) y cuál, entre las tareas con título, área y responsable, con
     el vocabulario del equipo como contexto;
   - si esa llamada elige una tarea sin dudar, una segunda llamada verifica con
     una pregunta de sí o no que la referencia habla exactamente de esa tarea y
     no de otra parecida; si no lo confirma, se pregunta en lugar de elegir;
   - por mensaje, una llamada con una elección entre intenciones y una pregunta de
     sí o no por intención; decide sólo si ambas coinciden en una acción;
   - los cortes viven en el documento de diseño y se ajustan ahí.
4. **Ninguna decisión de Jev aplica un cambio.** Termina en una propuesta con
   vista previa y confirmación, o en una pregunta con botones (ADR 0005).
5. **Todas las tareas activas del espacio van como opciones.** Medido con 200
   tareas: la latencia pasa de 0,39 a 0,46 s y el costo de US$ 0,00004 a 0,0004
   por llamada, sin elecciones equivocadas; pregunta más, en parte porque con más
   tareas parecidas hay más ambigüedad real. El límite es la ventana de 32.000
   tokens de Jev (unas 700 tareas a ~44 tokens cada una); recién cerca de ese
   límite se acotarían las candidatas con embeddings.

## Por qué

- Las reglas por palabras sobreajustaron: con mensajes no vistos eligieron sin
  preguntar en 3 de 15 casos, y no alcanzaban sinónimos ("wifi" y "red" por
  access points, "respaldo" por backup).
- Jev, con la receta congelada y mensajes no vistos: 11 de 15 correctos y ninguno
  que eligiera una tarea equivocada sin preguntar; el resto, preguntas de más.
- Repetida cinco veces sobre 45 mensajes, la receta sin verificación eligió mal un
  mismo mensaje en cuatro repeticiones: algo que no existe ("el horno") asignado a
  una tarea parecida ("la estufa"). Con la verificación, cero en las cinco, sin
  frenar ninguna elección correcta. Confirmado con un lote nuevo, no visto: sin
  verificación eligió mal dos mensajes en cada una de cinco repeticiones ("el switch
  de la oficina", "el backup de las notebooks"); con verificación, cero, sin frenar
  elecciones correctas.
- El modelo de conversación no señala su duda: clasificando cinco veces el mismo
  mensaje, `deepseek-v4-flash` no detectó ninguno de 8 casos ambiguos. Jev, con
  elección y sí o no combinados, detectó 7 de 8, y en el lote no visto los dos
  casos marcados por el usuario.
- Latencia de 0,35 a 0,51 s y una fracción de centavo por llamada. El agregado
  real por mensaje es de unos 0,4 s: la consulta de tareas va después de que el
  modelo de conversación separa las referencias; la de intención puede ir en
  paralelo con ese paso. La verificación suma otros 0,4 s sólo cuando Prisma está
  por decidir solo.

## Alternativas consideradas

- **Sólo el modelo de conversación y embeddings:** más simple, un proveedor
  menos; detecta peor la duda y depende de reglas por palabras que no
  generalizaron.
- **Reordenamiento (`rerank`) de NaN como señal de duda:** elige con fuerza aun
  ante referencias ambiguas.
- **Clasificar varias veces con el modelo de conversación:** 0 de 8 ambiguos.

## Consecuencias

- **Dos proveedores:** NaN para conversación y embeddings, OpenRouter para Jev.
  Clave en `PRISMA_OPENROUTER_API_KEY`. Si Jev no responde, Prisma no adivina:
  pregunta con botones o pide la referencia; la vista previa sigue protegiendo.
- **Datos que salen:** títulos de tareas, áreas, responsables, vocabulario del
  equipo y el texto del mensaje viajan a TypeSafe vía OpenRouter. El usuario
  aceptó esos términos el 2026-09-24. Ese mismo día aceptó sumar el nombre de
  quien escribe y la causa de los bloqueos abiertos de cada tarea: la gente
  nombra una tarea por lo que la frena ("ya llegó el switch que faltaba").
- **Jev está en beta y no responde idéntico en cada llamada.** Los cortes se leen
  como tendencia y se revisan con el banco.
- **Límites conocidos:** ante algo que no existe tiende a ofrecer tareas parecidas
  en lugar de decir que no hay, y sin la verificación puede elegir una; da falsas
  alarmas de intención en una de cada tres frases claras, y una duda de intención
  marcada por el usuario se detectó en 3 de 5 repeticiones. Con la verificación,
  ambos terminan en una pregunta, no en un efecto.
- **Las consultas no pasan por vista previa:** toda respuesta nombra la tarea por
  su título, para que la persona note si Prisma entendió otra cosa.
- **El vocabulario y los apodos del equipo** se pasan como contexto; su
  aprendizaje sigue la decisión 5 de ADR 0005.
