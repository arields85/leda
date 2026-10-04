# Bitácora de flujos: qué se probó, qué salió y qué elegimos

Documento vivo (pedido del usuario, 2026-10-03). Junta en un solo lugar los resultados,
progresos, retrocesos y conclusiones de cada flujo y de cada modelo, para que una sesión
nueva no tenga que reconstruirlos. El detalle de cada prueba de los flujos C está en
`odd/tasks/circuitos-al-flujo-nuevo.md` de la rama `feat/flujo-de-un-mensaje`, congelada el
2026-10-04 (etiqueta `respaldo-flujos-antes-de-d`; se lee con `git show`). Los nombres
(el Motor; flujo A, B, C1…, D) están definidos en `AGENTS.md`, "Nombres que usamos".

Regla de uso: **al cerrar cada prueba real, medición o auditoría se agrega acá su
resultado y, si cambia, la conclusión vigente.** No se borran conclusiones anteriores: se
marcan como reemplazadas.

## Conclusión vigente (2026-10-04)

**Los flujos A, B y C1 a C6 quedan congelados. La línea de trabajo vigente es el Motor, y su
mecanismo para procesar un mensaje es el flujo D: un motor chico de conversación dentro de Leda,
con el alcance recortado al seguimiento.** "El Motor" nombra la línea de trabajo entera; "flujo D",
sólo el mecanismo, para compararlo con los flujos A, B y C. Es una decisión del usuario, tomada
después de la prueba real de la tarea 0-35 y de un análisis adversarial del proyecto
([`../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md)).

Qué se decidió:

- **Un motor de conversación chico dentro de Leda (el flujo D),** sin marcos de terceros (Rasa
  quedó descartado): estado de la conversación explícito, circuitos declarados y situaciones
  generales resueltas una sola vez. Se diseña en tres partes: estado exacto, registro completo de
  la conversación (con los toques de botones) y memoria por integrante, que va después y con su
  propio ADR.
- **Alcance recortado:** por ahora Leda no crea tareas ni objetivos por chat; hace seguimiento.
  Qué circuitos quedan por chat se fija en el ADR 0017 (`PENDIENTE`); las cadencias, los
  recordatorios, los bloqueos, la entrega con evidencia, la aprobación y las consultas son
  ejemplos de seguimiento, no la lista decidida. Principio: *por chat, hechos del trabajo; por la
  web, su estructura.*
- **Carga de tareas:** primero una importación por archivo que hace el administrador; después,
  un formulario en el tablero del cliente.
- **Engram:** sólo como referencia de diseño para esa memoria, no como componente.
- **Dónde sigue el trabajo:** en la rama `feat/motor-de-conversacion`. El diseño se escribe antes
  del código, en el ADR 0017 (alcance) y el ADR 0018 (motor de conversación), en preparación. Los
  flujos anteriores quedan intactos en la etiqueta `respaldo-flujos-antes-de-d` y no se corrigen.

Por qué:

- La conclusión anterior decía que los problemas de C6 se arreglaban dentro de su diseño. La
  prueba real del 2026-10-04 lo desmintió: el bucle del borrador devuelto no volvió, pero
  aparecieron cuatro fallas nuevas de la misma clase (fila "C6 + 0-35" de la tabla), después de
  cinco auditorías que encontraron 14, 7, 7, 6 y 7 hallazgos, sin bajar.
- El análisis mostró que la causa no está en un flujo en particular: la conversación está escrita
  a mano, situación por situación, sin un modelo de la conversación ("Progresos y retrocesos").
- El usuario, al cortar la prueba: "me preocupa que no se pueda seguir un hilo de conversación tan
  simple", "se siente muy estructurado todo", "siento que estamos volviendo a parchear".

La IA: las mediciones de "Modelos" son del flujo C6. Para el flujo D se mantiene GPT-6 sol y falta
volver a medir GPT-6 luna; la elección está `PENDIENTE` en el ADR 0018.

Qué haría revisar esta conclusión: el resultado de la prueba chica del motor de conversación, con
los criterios de éxito y de corte escritos antes en el ADR 0018.

El detalle de la prueba del 2026-10-04 y de la tarea 0-36, que se detuvo y no se retoma, está en
`respaldo-flujos-antes-de-d:odd/tasks/circuitos-al-flujo-nuevo.md`. El trabajo parcial de la
tarea 0-36 quedó archivado, sólo para consulta, en la etiqueta `respaldo-0-36-en-pausa`.

## Conclusión anterior (2026-10-03), reemplazada el 2026-10-04

**Flujo elegido: C6, con las plantillas fuera y la regla del mozo** (`AGENTS.md`, punto
11), aunque todavía no está terminado. **Modelo: GPT-6 sol.**

Por qué C6:

- Los problemas de los demás flujos están en su diseño; los de C6, no. El flujo A es un
  formulario (pasos fijos y botones). El flujo B deja que la IA decida y actúe libre (ahí
  inventó un cambio, H5). C1 a C5 escriben antes de que el código decida, así que la IA
  adivina, y cada adivinanza fallida terminó en una regla nueva. En los tres casos,
  arreglar un problema genera el siguiente.
- Los problemas de C6 se arreglan dentro de su diseño, sin reglas para la IA (por ejemplo,
  el bucle del borrador devuelto y la frase de ofertas repetida).
- Es el único que cumple la promesa central de Leda: no inventar. Lo que dice sale de la
  base y la IA sólo lo cuenta.
- Se puede llevar al resto de los circuitos: la llamada que escribe es la misma para
  todos; cada circuito define qué tiene que entender la IA y qué hace la cocina.

Por qué sol: fue el más fiel a los hechos en la prueba real. Si con C6 estable luna
también queda fiel, conviene volver a comparar: es unas 23 veces más barato y más rápido.

Qué haría revisar esta conclusión: si después de la tarea 0-34 vuelve a aparecer una falla
del mismo tipo en el borrador devuelto, no se cambia de flujo, pero se revisa el diseño del
borrador devuelto antes de seguir.

**Actualización (2026-10-04):** pasó. La cuarta auditoría encontró que el borrador devuelto
todavía puede entrar en bucle (otra causa, la misma clase de falla). Se mantiene C6 y se
rediseña el borrador devuelto (tarea 0-35): sin lista de datos a corregir; vuelve como un
borrador normal con el motivo, una pregunta abierta y el resumen para reenviar.

**Reemplazo (2026-10-04, después de la prueba real de 0-35):** toda esta conclusión dejó de
regir, incluida la actualización de arriba. No se mantiene C6 ni se sigue trabajando sobre el
borrador devuelto; rige la conclusión vigente del comienzo.

## La regla del mozo: por qué se decidió y cómo se aplicó en C6

> **Nota del 2026-10-04.** Esta sección cuenta cómo se aplicó la regla en el flujo C6, que quedó
> congelado. El núcleo de la regla sigue vigente (la IA no inventa datos ni efectos; los hechos
> salen de la cocina). Su extensión a cada movimiento de la conversación está en revisión en el
> ADR 0018; ver `AGENTS.md`, "Cómo pensamos juntos", punto 11. La forma de trabajar que describe
> (controlar con pruebas automáticas y con la auditoría de otro agente) tampoco es la vigente:
> ver el punto 12.

**Qué es** (decisión del usuario, 2026-10-03; `AGENTS.md`, punto 11). La IA es el mozo de
un restaurante: escucha o pregunta qué quiere la persona, lleva el pedido exacto a la
cocina y trae lo que la cocina dice, contándolo con naturalidad. La cocina es el código,
Jev y la base: valida, decide, ejecuta y sabe los hechos. El mozo no cocina ni inventa
platos: es intérprete y comunicador de la fuente de verdad, usa su fuerte (hablar e
interpretar a la persona) y **no toma decisiones**. Ante cada cambio se pregunta: ¿esto lo
resuelve la cocina o le estamos enseñando frases al mozo?

**Por qué se decidió.**

1. De C1 a C5 la IA escribía la respuesta antes de que el código decidiera: tenía que
   adivinar qué iba a pasar. Cada vez que adivinaba mal se le agregaba una regla, y la
   mecánica crecía (el retroceso de C4). El usuario lo resumió así: el actual es un mozo que
   confirma el plato antes de preguntar en la cocina.
2. C6 corrigió el orden (el mozo pregunta en la cocina antes de contestar), pero se
   construyó dejándole a la IA decisiones que no le tocan: elegía qué preguntar de una
   lista, si mostraba botones y cuándo proponer algo, y seguía llevando las reglas de casos
   heredadas de C5. La cocina, además, empezó a corregir lo que el mozo escuchaba con
   trucos propios (comparar nombres por coincidencia de letras).
3. Al revisar los arreglos de la ronda de modelos, el usuario frenó: "estamos en el límite
   de volver a cometer el error de agregar reglas puntuales para que el circuito responda
   como queremos". Propuso fijar el criterio con la analogía del mozo y la cocina, y
   después lo precisó: la IA no toma decisiones ni inventa datos; para eso va a la cocina.
   Se dejó escrito en `AGENTS.md` para que sirva de control antes de construir, no después
   de probar.

**Cómo se aplicó en C6** (tareas 0-31 a 0-34 de la rama de flujo).

- **La cocina decide y se lo dice al mozo como hechos:** qué dato se pregunta (con una
  sola regla fija), qué botones van, cuándo se propone algo (título que no dice qué hacer,
  criterio que no se puede comprobar, pedido de ayuda) y qué se ofrece en cada momento.
  También dice quién hizo qué visto desde quien lee, y el motivo real de cada cosa que no
  se tomó.
- **El mozo interpreta y cuenta:** la primera llamada entiende el mensaje (intención,
  datos, correcciones, nombres que no están entre las opciones, si el título no dice qué
  hacer, si mantiene un dato); la segunda escribe desde los hechos. Su salida sólo trae el
  texto, la propuesta cuando la cocina la pide y el dato que preguntó, que tiene que ser
  el que decidió la cocina.
- **Lo que necesita juicio sobre la base lo resuelve la pieza indicada:** un nombre fuera
  de las opciones lo compara Jev (ADR 0014), no el código ni la IA adivinando.
- **Las instrucciones describen el trabajo del mozo,** sin reglas de casos, sin ejemplos
  de lo que tiene que decir y sin límite de largo.
- **Nada fijo del código llega a la persona,** salvo lo aprobado por el usuario: las dos
  plantillas (las líneas de datos del resumen y el aviso de falla de la IA, que incluye el
  saludo del día y "Pendiente:") y, aparte, el bloque para copiar de Modificar, que no es
  una plantilla sino el propio dato de la persona (decisión del 2026-10-03, después de ver
  un ejemplo). Las etiquetas de los botones las arma el código.
- **Se controla solo:** pruebas automáticas fallan si vuelve un texto fijo, una decisión
  de la IA o una regla de caso; y después de cada vuelta, una auditoría independiente.

**Resultado en el flujo C6 (al 2026-10-03).** Prueba real con sol (2026-10-03, 19:18): Ariel
explicado con la regla real, el rechazo volvió como una pregunta concreta, el bloque para copiar
funcionó y quién hizo qué salió bien en todos los mensajes. Fallaron dos cosas, las dos de la
cocina y no del mozo: un bucle en el borrador devuelto (la cocina volvía a pedir la fecha) y la
misma oferta al final de cada mensaje (la cocina le pasaba siempre la lista de lo posible). Las
dos se trabajaron dentro de la regla en la tarea 0-34. La prueba real del 2026-10-04 mostró que
la misma clase de falla seguía apareciendo (fila "C6 + 0-35" de la tabla).

## Los flujos, uno por uno

| Flujo | Qué es | Prueba real | Lo bueno | Lo malo | Estado |
|---|---|---|---|---|---|
| A | Formulario mecánico: pasos fijos, un dato por vez, botones | Rondas 1-4 (hasta 2026-09-30) | Predecible; nunca inventa | Robótico; no entiende lo que se escribe libre | Congelado el 2026-10-04; su código en `main` se borra antes de construir el motor de conversación definitivo |
| B | IA libre: lee la constitución, elige herramientas y redacta | Rondas 1-4 | Flexible | Inventó un cambio (H5); textos fijos con muletillas del agente ("Listo…", "Dale…") | Congelado el 2026-10-04; es lo que atiende en `main` todo lo que no es el alta, y se borra antes de construir el motor de conversación definitivo |
| C1 | ADR 0014, una llamada: la IA interpreta y escribe antes de que el código decida | 2026-10-01: favorable ("fluidez increíble") | Gran salto contra A | Órdenes secas (12), "anoté" sin efecto (7), dos datos por pregunta (9) | Congelado |
| C2 | C1 + la personalidad como texto aparte | 2026-10-02 18:20: pasa | Menos órdenes secas | El usuario: "habla exactamente igual"; el más lento (17 s típico, 40 s peores casos) porque la personalidad contradecía la mecánica | Congelado |
| C3 | Personalidad adentro de la mecánica | No se probó en real (se saltó a C4 por la medición del banco, contra "probar en real enseguida") | Volvió a 10,6 s; cero órdenes secas, "anoté" y dos datos | Aceptaba un título vago | Congelado |
| C4 | C3 + reglas de estilo concretas | 2026-10-02 22:18: pasa | Un dato por pregunta garantizado por el código | **Retroceso:** reglas de casos ("por favor", nombre de pila, no repasar) que no daban el resultado; el verificador rechazaba el título propuesto | Congelado |
| C5 | Mecánica sólo con reglas estructurales | 2026-10-03 00:44: pasa en lo estructural | Sin reglas de estilo, lo estructural se sostuvo; textos más cortos | "Perfecto" y «¿te sirve?»; textos fijos del código | Congelado; etiqueta `respaldo-flujos-antes-de-c6` |
| C6 | Esquema del usuario: la IA interpreta, el código decide, la IA escribe desde los hechos (dos llamadas) | 2026-10-03 01:39: pasa; el usuario: "es más conversacional" | La fecha fuera de plazo con el límite real; la propuesta de título pasa el verificador; textos que coinciden con lo que pasó | Muletillas de la IA; textos fijos al final | Elegido el 2026-10-03; congelado el 2026-10-04 |
| C6 + P-1 | Sin plantillas (sólo dos permitidas) | 2026-10-03 09:13 (flash): "habla sin plantillas ni muletillas" | Sin textos fijos en el camino principal; elección del botón escrita en el mensaje | Responsable fuera de opciones ignorado; el rechazo dejaba el tema abierto; causa inventada; promesa falsa | Fue la base de las versiones siguientes del flujo C; congelado el 2026-10-04 |
| C6 + regla del mozo | La IA no decide: la cocina decide qué se pregunta, botones y propuestas | 2026-10-03 19:18 (sol) | Ariel explicado con la regla real; el rechazo vuelve como pregunta concreta; bloque para copiar | Bucle en el borrador devuelto (pedía la fecha); la misma oferta al final de cada mensaje; volvió una orden; "Soy Leda." | Arreglado en 0-34; congelado el 2026-10-04 |
| C6 + 0-35 | El borrador devuelto vuelve como un borrador normal (sin lista de datos a corregir), con las correcciones de la quinta auditoría | 2026-10-04 11:21-11:38 (sol), cortada antes de terminar el guion | El bucle no volvió; una corrección sobre el devuelto volvió al resumen sin pedir otros datos; el selector de Modificar pregunta en lugar de ordenar; la propuesta de la IA no pisó el criterio confirmado | Después de un turno sin cambios, la respuesta salió sin resumen ni botones; pedir por escrito el envío a aprobación no se tomó; la lista de ofertas recitada en casi todos los mensajes; un Cancelar de un resumen anterior canceló el devuelto, y el flujo B no supo del borrador cancelado y ofreció tareas ajenas | Congelado el 2026-10-04 (etiqueta `respaldo-flujos-antes-de-d`) |
| D | El mecanismo del Motor: un motor de conversación con estado explícito, circuitos declarados y situaciones generales resueltas una sola vez (ADR 0018, en preparación) | Todavía ninguna | — | — | En diseño, en la rama `feat/motor-de-conversacion` |

## Progresos y retrocesos

- **Retroceso C3 → C4:** se sumaron reglas de estilo para casos y no dieron el resultado;
  se detectó por los disparadores del punto 4 de `AGENTS.md` y se revirtió en C5.
- **Error de método:** C3 no se probó en real; la decisión de pasar a C4 se tomó sobre el
  banco.
- **Progreso C5 → C6:** cambiar el orden (la IA escribe después de que el código decide)
  eliminó los textos que contradecían lo que pasó.
- **Hallazgo:** las muletillas venían de nosotros. «¿te sirve?» salía de "aceptar o
  cambiar" en las instrucciones; "Listo…" y "Dale…" de textos fijos del flujo B que la IA
  lee en el historial. Con flash y las instrucciones corregidas, «¿te sirve?»
  desapareció; con luna y sol aparece igual (costumbre de esos modelos).
- **Error de diseño reconocido:** C6 se construyó cambiando el orden pero dejándole a la
  IA decisiones (qué preguntar, botones, cuándo proponer) y las reglas heredadas de C5. Lo
  corrigió la regla del mozo (0-31).
- **Las plantillas se perdieron dos veces** por posponerlas sin tarea; desde entonces
  todo lo que se pospone se anota como tarea en el momento.
- **Auditorías independientes:** después de que un escritor dice "cumple", siempre va una
  auditoría de otro revisor. Primera (6f85bf9): 10 textos fijos y 4 casos del mozo;
  segunda (a8f4aba): 4 y 3 de severidad baja; tercera (3e5bcb3): 4 y 3, de borde. Cuarta
  (f7dce94): 3 y 3, con el bucle del borrador devuelto de nuevo → rediseño (0-35). Quinta
  (bb1ee18, sobre el rediseño): "sí, con reservas"; el bucle no volvió. 7 hallazgos: una
  propuesta de la IA pisaba un dato confirmado (medio; contra la regla del mozo: una
  propuesta se acepta, no se guarda sola), el devuelto que esperaba otro borrador volvía
  en silencio (medio-bajo), 4 bajos (guardas, instrucción sin describir todos los hechos,
  líneas del resumen repetidas, "Pendiente:" con una oración) y la redacción de
  `PIDE_ELEGIR` y `PIDE_QUE_CAMBIAR`, que se mira en la prueba real. Arreglados los otros
  6 en `df761db`, `ba3269d` y `24e92ce`, con el mecanismo y no el caso. Los controles
  automáticos que escribe el mismo escritor tienen sus mismos puntos ciegos.
- **Prueba real de 0-35 y freno (2026-10-04).** Con la suite en verde (3.997 pruebas) y la
  quinta auditoría aprobada con reservas, la prueba real volvió a fallar en formas nuevas de la
  misma clase: el estado de la conversación y lo que la persona puede hacer se decidían en cada
  camino por su cuenta. El usuario cortó la prueba y frenó los arreglos. Es el disparador
  "pruebas en verde y el usuario dice que se siente mal" del punto 4 de `AGENTS.md`, y la misma
  clase de falla en dos rondas.
- **Análisis adversarial (2026-10-04),** pedido por el usuario: una revisión interna de sólo
  lectura y una investigación externa con fuentes. Resumen (detalle y cifras en
  [`../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md`](../research/gestion-del-dialogo-y-arquitecturas-de-agentes.md)):
  - La base no está en cuestión: PostgreSQL con las garantías en el código, y la IA que
    interpreta y redacta, coinciden con el patrón dominante. En ninguna ronda quedó registrado
    un efecto mal hecho.
  - La falla está en el medio: unas 16.000 líneas de manejo de conversación escritas a mano, sin
    un modelo de la conversación (el estado se deduce en cada mensaje; un borrador tiene al
    menos 14 estados implícitos) y con tres flujos conviviendo. Un mapa sobre el alta contó unos
    30 lugares que deciden, cada uno por su cuenta, si va el resumen, qué botones salen y qué se
    ofrece.
  - Los hallazgos no bajan: 14, 7, 7, 6 y 7 en las cinco auditorías.
  - Las pruebas miran el código, no las conversaciones: unas 70.000 líneas de pruebas, en su
    mayoría atadas a la implementación y escritas por el mismo escritor, y ninguna prueba con la
    IA real del flujo elegido.
  - El método corrió más rápido que el diseño: 254 commits en la rama entre el 2026-09-30 y el
    2026-10-04, y seis versiones del alta en tres días.
  - Ninguno de los productos y marcos relevados escribe a mano una rama por situación, y ningún
    producto verificado cubre el circuito completo de Leda dentro del chat del equipo.
- **La parte del agente (2026-10-04).** Ese día el agente delegó tres vueltas de arreglos (la
  tarea 0-35, las correcciones de la quinta auditoría y la tarea 0-36) y propuso una cuarta. Cada
  una era un "arreglo del mecanismo" razonable y ninguna cuestionaba la estructura; la suite en
  verde y la auditoría de otro agente se informaban como avance. El usuario lo señaló: "si no lo
  menciono vos volvés a caer en ese vicio y siempre estamos parcheando fallas". Desde entonces,
  un arreglo del mecanismo dentro de una estructura equivocada cuenta como parche, y lo que
  cuenta como evidencia son conversaciones reales contra la IA real (`AGENTS.md`, "Cómo pensamos
  juntos", punto 12).
- **La regla del mozo, en revisión (2026-10-04).** El análisis la encontró correcta para datos
  y efectos, y señaló como causa del código disperso su extensión a cada movimiento de la
  conversación (qué se pregunta después, cuándo va el resumen, qué se ofrece): sólo el alta
  llegó a tener 25 sucesos con hechos redactados por el código. El extremo opuesto también falló
  (el flujo B inventó). No está decidido cómo queda: qué decide la IA y qué decide el código se
  fija en el ADR 0018.

## Modelos

Pruebas reales (2026-10-03, una corrida por modelo, guiones distintos):

| | flash | luna | sol | Gemini 3.8 flash |
|---|---|---|---|---|
| Quién hizo qué | bien | **mal** (invirtió quién rechazó) | bien | bien |
| Inventa datos o propuestas que no muestra | no | **sí** | no | **sí** (un criterio) |
| Causas o promesas falsas | 2 | 0 | 0 | 0 |
| Muletillas | "Perfecto", "Listo" | «¿te sirve?» | «¿te sirve?» | "Tomamos…" |

Banco (tarea 0-24, 2026-10-03; 386 llamadas reales sin caché; por mensaje del alta):

| Modelo | Tiempo típico / peores casos | Costo por mensaje |
|---|---|---|
| flash (`deepseek-v4-flash`, por el proveedor `nan`) | 19,0 / 21,8 s | ~USD 0,0002 (estimado) |
| luna (`openai/gpt-6-luna`) | 7,9 / 9,5 s | USD 0,0007 |
| sol (`openai/gpt-6-sol`) | 11,0 / 13,8 s | USD 0,016 |
| Gemini (`google/gemini-3.8-flash`), tope de siempre | 12 de 15 mensajes con aviso de falla | — |
| Gemini, tope 4000/3000 | 20,7 / 27,0 s | USD 0,011 |

Lo que se aprendió de los modelos: luna y sol mandan todos los campos vacíos (el código lee
vacío como "no lo dijo"); Gemini razona por dentro y necesita un tope de salida propio (el
tope por modelo es un pendiente importante de la plataforma); el proveedor `nan` no limita el razonamiento
de flash, por eso es lento.

Estas mediciones son del flujo C6, congelado el 2026-10-04. Para el flujo D se mantiene GPT-6 sol
y falta volver a medir GPT-6 luna (ADR 0018).
