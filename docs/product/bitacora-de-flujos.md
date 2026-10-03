# Bitácora de flujos: qué se probó, qué salió y qué elegimos

Documento vivo (pedido del usuario, 2026-10-03). Junta en un solo lugar los resultados,
progresos, retrocesos y conclusiones de cada flujo y de cada modelo, para que una sesión
nueva no tenga que reconstruirlos. El detalle de cada prueba está en
`odd/tasks/circuitos-al-flujo-nuevo.md` de la rama `feat/flujo-de-un-mensaje`; los nombres
(flujo A, B, C1…, circuito 0…) están definidos en `AGENTS.md`, "Nombres que usamos".

Regla de uso: **al cerrar cada prueba real, medición o auditoría se agrega acá su
resultado y, si cambia, la conclusión vigente.** No se borran conclusiones anteriores: se
marcan como reemplazadas.

## Conclusión vigente (2026-10-03)

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

## Los flujos, uno por uno

| Flujo | Qué es | Prueba real | Lo bueno | Lo malo | Estado |
|---|---|---|---|---|---|
| A | Formulario mecánico: pasos fijos, un dato por vez, botones | Rondas 1-4 (hasta 2026-09-30) | Predecible; nunca inventa | Robótico; no entiende lo que se escribe libre | Se retira del alta (pendiente) |
| B | IA libre: lee la constitución, elige herramientas y redacta | Rondas 1-4 | Flexible | Inventó un cambio (H5); textos fijos con muletillas del agente ("Listo…", "Dale…") | Sigue para todo lo que no es el alta; se retira circuito por circuito |
| C1 | ADR 0014, una llamada: la IA interpreta y escribe antes de que el código decida | 2026-10-01: favorable ("fluidez increíble") | Gran salto contra A | Órdenes secas (12), "anoté" sin efecto (7), dos datos por pregunta (9) | Congelado |
| C2 | C1 + la personalidad como texto aparte | 2026-10-02 18:20: pasa | Menos órdenes secas | El usuario: "habla exactamente igual"; el más lento (17 s típico, 40 s peores casos) porque la personalidad contradecía la mecánica | Congelado |
| C3 | Personalidad adentro de la mecánica | No se probó en real (se saltó a C4 por la medición del banco, contra "probar en real enseguida") | Volvió a 10,6 s; cero órdenes secas, "anoté" y dos datos | Aceptaba un título vago | Congelado |
| C4 | C3 + reglas de estilo concretas | 2026-10-02 22:18: pasa | Un dato por pregunta garantizado por el código | **Retroceso:** reglas de casos ("por favor", nombre de pila, no repasar) que no daban el resultado; el verificador rechazaba el título propuesto | Congelado |
| C5 | Mecánica sólo con reglas estructurales | 2026-10-03 00:44: pasa en lo estructural | Sin reglas de estilo, lo estructural se sostuvo; textos más cortos | "Perfecto" y «¿te sirve?»; textos fijos del código | Etiqueta `respaldo-flujos-antes-de-c6` |
| C6 | Esquema del usuario: la IA interpreta, el código decide, la IA escribe desde los hechos (dos llamadas) | 2026-10-03 01:39: pasa; el usuario: "es más conversacional" | La fecha fuera de plazo con el límite real; la propuesta de título pasa el verificador; textos que coinciden con lo que pasó | Muletillas de la IA; textos fijos al final | Elegido |
| C6 + P-1 | Sin plantillas (sólo dos permitidas) | 2026-10-03 09:13 (flash): "habla sin plantillas ni muletillas" | Sin textos fijos en el camino principal; elección del botón escrita en el mensaje | Responsable fuera de opciones ignorado; el rechazo dejaba el tema abierto; causa inventada; promesa falsa | Base de lo que sigue |
| C6 + regla del mozo | La IA no decide: la cocina decide qué se pregunta, botones y propuestas | 2026-10-03 19:18 (sol) | Ariel explicado con la regla real; el rechazo vuelve como pregunta concreta; bloque para copiar | Bucle en el borrador devuelto (pedía la fecha); la misma oferta al final de cada mensaje; volvió una orden; "Soy Leda." | En arreglo (0-34) |

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
  segunda (a8f4aba): 4 y 3 de severidad baja; tercera (3e5bcb3): 4 y 3, de borde. Los
  controles automáticos que escribe el mismo escritor tienen sus mismos puntos ciegos.

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
| flash (`deepseek-v4-flash`, nan) | 19,0 / 21,8 s | ~USD 0,0002 (estimado) |
| luna (`openai/gpt-6-luna`) | 7,9 / 9,5 s | USD 0,0007 |
| sol (`openai/gpt-6-sol`) | 11,0 / 13,8 s | USD 0,016 |
| Gemini (`google/gemini-3.8-flash`), tope de siempre | 12 de 15 mensajes con aviso de falla | — |
| Gemini, tope 4000/3000 | 20,7 / 27,0 s | USD 0,011 |

Lo que se aprendió de los modelos: luna y sol mandan todos los campos vacíos (el código lee
vacío como "no lo dijo"); Gemini razona por dentro y necesita un tope de salida propio (el
tope por modelo es un pendiente importante de la plataforma); nan no limita el razonamiento
de flash, por eso es lento.
