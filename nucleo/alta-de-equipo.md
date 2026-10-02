# Alta de un espacio de trabajo

**Capa:** núcleo · **Versión:** 1.0

Cómo Leda da de alta un equipo nuevo. La entrevista la conduce Leda desde el
**bot de administración**, con un administrador de plataforma. Su salida es un
pack de espacio que alguien tiene que leer y aprobar antes de que el espacio se
active.

Este documento es la contracara del formato de pack: define qué hay que
averiguar y qué no se puede dejar sin definir.

---

## Principios de la entrevista

- **Una pregunta por vez.** No se envían cuestionarios.
- **Leda no completa por su cuenta.** Si algo no se contestó, queda como
  faltante, no como valor por defecto silencioso.
- Cuando existe un valor habitual, Leda lo propone explícitamente y pide
  confirmación: "por defecto uso X, ¿te sirve?".
- Leda puede partir de una plantilla y entrevistar sólo para lo que difiere.
- Al terminar, Leda **muestra el pack completo en lenguaje natural**, no en
  YAML. La persona lo lee, corrige lo que haga falta y recién ahí aprueba.
- Un espacio no se activa sin aprobación explícita.

---

## Bloque 1 — Identidad del equipo

1. ¿Cómo se llama el equipo?
2. ¿A qué se dedica, en una o dos frases?
3. ¿Hay un objetivo grande que ordene el trabajo de los próximos meses? ¿Cuál?
4. ¿Hay nombres propios que Leda tenga que usar con precisión — productos,
   sistemas, plantas, clientes? ¿Alguno se confunde fácil con otro?

El punto 4 alimenta el glosario. Es el que evita que Leda escriba mal el nombre
de un producto o confunda el nombre del equipo con el de una de sus partes.

---

## Bloque 2 — Personas

Por cada integrante:

1. Nombre completo.
2. ¿De qué se ocupa? En una frase.
3. ¿A qué área pertenece?
4. ¿Aprueba el trabajo de alguien más? ¿De quién?
5. ¿Su trabajo lo aprueba alguien? ¿Quién?
6. ¿Qué días y horarios trabaja, si difiere del equipo?
7. ¿Algo que Leda deba tener en cuenta al escribirle?

Y sobre el conjunto:

8. ¿Quién tiene la última palabra cuando hay un desacuerdo?
9. ¿Esa persona debería recibir el seguimiento diario del equipo, o eso lo hace
   Leda y a ella le llega sólo lo relevante?

La pregunta 9 importa: sin ella, la autoridad del espacio termina recibiendo todo
y Leda pierde su función.

---

## Bloque 3 — Áreas y vocabulario

1. ¿Cómo dividís el trabajo por áreas o disciplinas?
2. ¿Cómo le dicen ustedes a una unidad de trabajo asignable? ¿Tarea, orden de
   trabajo, ticket, pedido?
3. ¿Y al conjunto de trabajos que persiguen un mismo resultado?
4. ¿Hay palabras que Leda debería evitar, o formas que el equipo no usa?

---

## Bloque 4 — Qué significa "terminado"

1. Cuando alguien dice que terminó algo, ¿alcanza con que lo diga o hace falta
   mostrar algo?
2. ¿Qué tipo de prueba usan habitualmente? ¿Archivos, fotos, resultados,
   confirmación de un tercero?
3. ¿Eso cambia según el área?
4. ¿Hay trabajos donde no hace falta ninguna prueba?

---

## Bloque 5 — Ritmo

1. ¿Qué días y en qué horario trabaja el equipo?
2. ¿Qué feriados siguen?
3. ¿Cada cuánto querés que Leda pida estado? ¿Qué días y a qué hora?
4. ¿Querés un resumen para todo el equipo? ¿Cuándo?
5. ¿Hay una reunión periódica que Leda tenga que preparar? ¿Con cuánta
   anticipación?
6. ¿Cuántos mensajes automáticos por día te parece razonable que reciba una
   persona?

---

## Bloque 6 — Urgencias y atrasos

1. ¿Qué hace que algo sea urgente en este equipo? Una condición concreta, no una
   sensación.
2. ¿Quién puede declarar una urgencia?
3. Cuando alguien se atrasa, ¿a quién avisa Leda primero?
4. ¿Y si el atraso persiste?
5. ¿Cuánto tiempo puede quedar un bloqueo abierto antes de que escale solo?

---

## Bloque 7 — Tono

1. ¿Cómo se hablan en este equipo? ¿De vos, de usted?
2. ¿Formal o distendido?
3. ¿Mensajes cortos o con contexto?
4. ¿Hay algo que te resultaría molesto que Leda haga al escribir?

---

## Bloque 8 — Canal

1. Token del bot de Telegram del espacio.
2. ¿Hay grupo de gestión? ¿Cuál es su identificador?
3. ¿Quién genera los enlaces de activación individuales y se los pasa a cada
   persona?

Los enlaces de activación se entregan **uno a uno**, nunca publicados en el
grupo. Un enlace publicado permite que cualquiera reclame la identidad de otro.

---

## Validaciones

Leda corre estas comprobaciones sobre el pack armado.

### Impiden activar el espacio

| Comprobación | Por qué |
|---|---|
| No hay ningún rol con autoridad de decisión final | El núcleo lo exige; sin esto no hay desempate posible |
| Un integrante sin área asignada | Rompe la política de aprobación |
| Un área sin aprobador y sin declaración explícita de autoaprobación | La omisión no puede pasar por decisión |
| Ciclo en la política de aprobación | A aprueba a B que aprueba a A |
| Falta el token del bot o el grupo | Leda no puede operar |
| No hay calendario laboral | Toda la escalera de recordatorios se calcula sobre él |
| El pack intenta modificar una regla del núcleo | Rechazo automático |

### Advierten, pero no impiden

| Comprobación | Qué dice Leda |
|---|---|
| Un área se autoaprueba | "El trabajo de esta área no lo revisa nadie más. ¿Es a propósito?" |
| Un solo aprobador para todo el equipo | "Todo pasa por una persona. Si no está, se frena el equipo." |
| Un aprobador sin suplente | "¿Quién aprueba si esta persona no está?" |
| Cadencia fuera del horario declarado | "Pediste estado los sábados, pero el equipo trabaja de lunes a viernes." |
| Más mensajes automáticos por día que el máximo declarado | "Con esta cadencia, algunas personas van a recibir más mensajes de los que fijaste." |
| Nombres del glosario muy parecidos entre sí | "Estos dos nombres se confunden fácil. ¿Querés que anote las variantes incorrectas?" |
| Una persona con carga muy superior al resto | "Esta persona concentra la mayoría del trabajo." |

Cada advertencia se responde y la respuesta queda registrada en el pack. Una
advertencia aceptada a conciencia deja de aparecer; una ignorada vuelve a
mostrarse en la próxima revisión.

---

## Cierre

1. Leda arma el pack.
2. Lo presenta en lenguaje natural, sección por sección.
3. Lista las advertencias abiertas.
4. El administrador corrige lo que haga falta.
5. El administrador aprueba.
6. El espacio se activa, se genera el pack versionado y se registra quién lo
   aprobó y cuándo.
7. Leda publica su presentación en el grupo y quedan pendientes las
   activaciones individuales.

Hasta que un integrante no active su enlace, Leda no puede escribirle en
privado. Sus tareas existen igual; el seguimiento privado empieza cuando activa.

---

## Revisión periódica

Un pack no se escribe una vez. Cada **[pack]** meses Leda propone una
revisión al administrador con:

- advertencias que siguen abiertas;
- reglas que nunca se usaron;
- áreas sin actividad;
- personas cuya carga cambió mucho;
- estimaciones que fallan sistemáticamente;
- aprendizajes acumulados que sugieren cambiar la configuración.

Leda propone. El cambio lo aprueba quien corresponda y lo aplica el
administrador.
