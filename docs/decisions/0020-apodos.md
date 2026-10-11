# ADR 0020: Los apodos

- **Estado:** propuesto. Las tres decisiones de fondo son del usuario (2026-10-11): Leda aprende los
  apodos por chat, ante un apodo de dos personas pregunta con nombre y apellido, y la plataforma los
  muestra y deja agregarlos o cambiarlos sin que Leda deje de aprenderlos por chat.
- **Fecha:** 2026-10-11.
- **Reemplaza:** el punto 5 del [ADR 0005](0005-interpretacion-y-confirmacion.md) ("Los apodos se
  aprenden preguntando"), escrito para los flujos congelados.
- **Alcance:** cómo reconoce Leda a una persona del equipo cuando la nombran por un apodo, en
  cualquier jugada que nombre a alguien (quién destraba, a quién se pasa una tarea, quién se encarga).
- **Evidencia:** hoy Leda reconoce a las personas sólo por su nombre cargado; no hay nada de apodos en
  `src/` ni en `db/esquema.sql` (2026-10-11). `nucleo/constitucion.md` §5 y §13;
  `nucleo/mecanica-pm.md` §14; [ADR 0018](0018-motor-de-conversacion.md), decisiones 1 y 3.

## Contexto

En un equipo real la gente se nombra como se habla: "el Tano", "Pato", "Juanchi". Hoy, si alguien le
dice a Leda "se lo tiene que pasar el Tano", Leda contesta que "el Tano" no figura en el equipo: es
honesto, pero obliga a la persona a reescribir el mensaje con el nombre cargado. Una lista de apodos
cargada a mano envejece (ADR 0005): la gente cambia de apodo y nadie la mantiene.

## Decisión

1. **Leda aprende los apodos por chat.** Cuando alguien nombra a una persona que no coincide con
   nadie del equipo, Leda pregunta quién es ("No tengo a nadie como «el Tano», ¿quién es?"). La
   persona contesta con el nombre, y Leda confirma antes de aprender: "¿«El Tano» es Nahuel
   Gimenez?". Con el sí, el apodo queda registrado para esa persona y la jugada sigue como si la
   hubieran nombrado por su nombre. La confirmación es de una persona, nunca de la IA (constitución
   §5).
2. **Un apodo de dos personas se aclara con nombre y apellido.** Si un apodo aprendido corresponde a
   dos personas, o coincide con el nombre de otra, Leda pregunta con el nombre y apellido de cada
   una: "¿«Juan» es Juan Pérez o Juan Gómez?". Nunca elige por su cuenta.
3. **La plataforma los muestra y los deja cambiar.** La plataforma web muestra los apodos que Leda
   fue aprendiendo, con quién lo enseñó y cuándo, y deja agregarlos, cambiarlos y borrarlos. Por
   chat Leda sigue aprendiéndolos y corrigiéndolos: "el Tano no es Nahuel, es Lucas" cambia el
   apodo, también con confirmación.
4. **El apodo sirve para entender, nunca para hablar.** Leda reconoce a alguien por su apodo, pero
   siempre lo nombra por su nombre: en la confirmación, en los avisos y en el grupo. Un apodo puede
   ser burlón o íntimo y no le corresponde a Leda usarlo (constitución §8).
5. **El apodo es del espacio.** Lo que enseñó una persona lo entiende Leda con todo el equipo de ese
   espacio, y nunca en otro (constitución §13): el aislamiento se garantiza en la base, como el
   resto.
6. **No concede nada.** Un apodo no da identidad, autoridad ni permisos: sólo dice a qué integrante
   se refiere un nombre. Quién puede pedir qué lo sigue decidiendo el código con la persona ya
   reconocida.
7. **Todo queda auditado.** Cada apodo aprendido, cambiado o borrado deja su fila en `audit_log`, con
   quién lo enseñó o lo cambió, cuándo y por qué canal (chat o plataforma).

## Por qué

- **Aprender por chat** evita el mantenimiento manual y cubre el apodo nuevo el día que aparece; la
  confirmación de una persona evita que una lectura equivocada de la IA quede aprendida.
- **Nombre y apellido** es la única forma de que la persona elija sin dudas entre dos que se llaman
  igual.
- **La plataforma** da un lugar donde ver y corregir lo aprendido de un vistazo, sin depender de
  que alguien vuelva a mencionar el apodo en el chat.
- **Entender sin usarlo** separa lo que Leda aprende (cómo habla el equipo) de cómo trata a las
  personas, que no cambia.

## Alternativas rechazadas

- **Una lista cargada a mano, sólo en la plataforma.** Envejece y nadie la mantiene (ADR 0005).
- **Que la IA deduzca el apodo sin preguntar** ("Tano" se parece a "Gaetano"). Sería inventar una
  identidad (constitución §4) y el código no corrige lo que la IA escuchó con heurísticas (`AGENTS.md`,
  punto 11).
- **Un apodo por persona que lo enseñó**, en vez de uno del espacio. Obligaría a enseñárselo a Leda
  una vez por cada integrante, y el equipo nombra a la gente igual.

## Consecuencias

- **Una tabla nueva** de apodos del espacio (`workspace_id`, integrante, apodo, quién lo enseñó y
  cuándo), con `row level security` forzado y su migración con rollback y ensayo de paridad.
- **Es aprendizaje persistente, acotado.** El ADR 0018 (decisión 3) reserva la memoria por integrante
  para su propio ADR; este cubre sólo los apodos, como antes el ADR 0005. Cualquier otro aprendizaje
  sigue fuera.
- **La pregunta "¿quién es?"** es una pregunta más de la conversación, con su lugar entre las
  pendientes (una rama abierta a la vez) y su respuesta escrita; la confirmación lleva botón, como
  las demás.
- **La plataforma** suma la vista de apodos a su lista de pendientes
  (`docs/product/plataforma-pendientes.md`); se construye con la plataforma.
- **Antes del código:** la conversación de prueba (un apodo nuevo, uno de dos personas y una
  corrección) y su ronda con la IA real.
