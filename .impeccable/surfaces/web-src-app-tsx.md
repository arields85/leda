---
version: 1
slug: "web-src-app-tsx"
primary_target: "web/src/App.tsx"
related_targets: ["web/src/admin/AdminApp.tsx"]
---

# La web de Leda en el celular (Mini App) — superficie principal

**Modo:** Operate. **Construcción:** code-led (sin generador de imágenes). **Estado:** dirección elegida por el
usuario el 2026-10-15, con ajustes pendientes; todavía no aplicada al código de `web/`.

**Quién y para qué:** integrantes, referentes y Dirección, sobre todo desde el celular dentro de Telegram; ver en
segundos qué tienen, qué vence y qué les falta. La compu, para lo complejo.

**Referencias aprobadas** (abrir en el navegador): `.impeccable/mocks/decision/r7-profundidad.html` (Marcos,
referente, tres pestañas) y `.impeccable/mocks/decision/r7-profundidad-direccion.html` (Ismael, Dirección,
tres pestañas). Recorrido: «La etiqueta» → sorteos audaz y seguro → disposición «una tarea por pantalla» (gustó
la lectura, no la letra ni los íconos) → oscuros minimalistas: eligió «El pizarrón» sin la tiza → «Pizarra
técnica» (nítida pero simple) → «Profundidad» → con las pestañas siempre visibles.

## Direction contract

THESIS: Leda como un pizarrón técnico con profundidad: lo más importante del día dicho en grande y el resto en
calma; rechaza la lista gris con un acento y la monoespaciada de antes.
OWN-WORLD: fondo pizarra que baja de #2a3134 a #1b2023 con una luz muy suave arriba; tinta #ecebe6; Source Sans 3
en dos pesos y cifras tabulares; color sólo en el estado (esperando #e3a27a, en curso #9cc7a4); tareas agrupadas
en una superficie apenas elevada con filetes; sin íconos en círculos, sin brillo, sin vidrio.
STORY: la persona abre y entiende qué vence y qué le falta; toca una tarea para actuar; cambia de vista con el
pulgar.
FIRST VIEWPORT: nombre y área arriba a la izquierda, «+ Nueva» a la derecha; el resumen grande («1 vence mañana»,
la tarea y lo que falta, el conteo); la semana con hoy recuadrado; la lista agrupada; terminadas; barra flotante
pegada al borde de abajo, de lado a lado, fondo sólido, línea fina arriba, ícono y palabra en cada pestaña
(tres: Mis tareas, Mi área y Mis pedidos para un referente; Mis tareas, Áreas y Equipo para Dirección) y
una rayita sobre la activa (aceptada en `impeccable live` el 2026-10-15).
FORM: «El pizarrón» (candidato 3 de la lista propia de la ronda 3, asignado por el sorteo), refinado por el
usuario; seed key 71b06f5b.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Direction contract — alternativa «Sobria» (r8, en prueba; la r7 sigue vigente)

Fijada por el usuario (2026-10-15, noche) con tres referencias (un lanzador de Android negro con bandas y cifras
finas; un reloj circular plano en gris; y, menos, un panel de entrenamiento negro). Pedido: "bien sobrio, muy limpio";
la r7 no se pierde.
THESIS: Leda como un instrumento sobrio: cifras grandes y finas, bandas separadas por filetes, nada más; rechaza
superficies elevadas, tarjetas y gradientes.
OWN-WORLD: fondo casi negro plano (#18191a), tinta neutra (#e8e8e6), grises; Source Sans 3 en 200/300 para las
cifras y 400/600 para el texto; etiquetas en minúscula con espaciado amplio; filetes horizontales entre bandas, con
margen; el color del estado sólo en cifras y palabras, apagado. Gesto propio: hoy, dentro de un anillo de 1px.
STORY: la persona abre, lee lo urgente en una cifra grande y fina, ve la semana y cuántas tiene en cada estado, toca
uno y la lista se filtra.
FIRST VIEWPORT: nombre y «nueva» arriba; el resumen como cifra grande con dos líneas a la derecha; la semana; los
cinco contadores como cifras finas; la lista en filas con filetes; la barra de pestañas pegada abajo, en gris un tono
más claro.
FORM: fijada por el usuario (sin sorteo); seed key: ninguna.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Decidido con el usuario (2026-10-15, noche)

- **Orden de la pantalla:** resumen grande (lo más urgente), semana, contadores (Vencidas · Sin empezar · En curso ·
  Esperando · Entregadas) y la lista. Tocar un contador filtra la lista a ese estado; tocarlo de nuevo, todas. Un
  contador en cero no se toca. Vencidas va en coral (`#e5877d`); el número toma color sólo si no es cero.
- **Qué va en el resumen grande** (gana el primero que exista): 1. una vencida (la más atrasada: «1 vencida desde
  el lunes»); 2. alguien te espera para seguir (una entrega a revisar, una firma, algo tuyo que frena a otro:
  «Marcos espera tu firma»); 3. vence hoy o el próximo día hábil («1 vence mañana»); 4. una tuya lleva días esperando
  algo de otro; 5. si no hay nada, la buena noticia («Nada vence esta semana»). Varias del mismo nivel: la cifra las
  cuenta y el texto nombra la más urgente. Sale siempre de datos de la cocina.
- **La lista:** sin filtro («Abiertas», el título chico arriba de la lista) van las que la persona tiene que mover
  (sin empezar, en curso, esperando), en el mismo orden de urgencia que el resumen grande, así su primera fila es lo
  que está en grande. Las entregadas (esperan la aprobación de otro) no van ahí: se ven sólo al tocar su contador
  (opción B). Con un filtro: sólo ese estado, por fecha (vencidas: la más atrasada primero, en cualquier estado). El
  título pasa a ser el del filtro, con «Ver todas». «Terminadas esta semana» queda siempre abajo.
- **La fila de una tarea en la r8** (variante A, «agenda», elegida 2026-10-15 de `r8-lista-variantes.html`): la
  fecha a la izquierda (día chico, número fino como la semana); a la derecha el título y un solo renglón con el
  estado en su color y lo que falta («esperando · falta la firma de Ismael»). La r8 también deja el desenfoque
  progresivo bajo la barra (aceptado) y los contadores en cinco columnas iguales, alineados con la semana.

- **«Áreas» (Dirección), r8** (2026-10-15, noche, página de decisión de impeccable, sorteo `bdb69d68`): el
  **mosaico**, una baldosa por área en dos columnas separadas por filetes; en cada una, las abiertas en una cifra
  grande y fina, el nombre del área, «referente X» (o «sin referente») y sólo los estados que tienen algo, en su
  color. Muestra: `.impeccable/mocks/decision/r8-sobrio-areas.html`; descartadas «por dónde mirar primero» y
  «matriz de estados» (`areas-*.html`). En el mosaico, el total de abiertas no suma las vencidas: una vencida
  cuenta en su estado (MA-3).
- **El detalle de un área** (extensión de «Mis tareas», sin sorteo): «‹» y el nombre del área, «referente X»
  debajo; el resumen grande con la regla de urgencia aplicada al área; semana; contadores del área; filas tipo
  agenda con «de X» y, si está vencida, la fecha y la palabra en coral. Muestra:
  `.impeccable/mocks/decision/r8-sobrio-area-it.html` (la baldosa de IT del mosaico lleva ahí). Falta «Equipo».

## Pendiente

- Ajustes que el usuario va a seguir pidiendo (dijo "vamos por buen camino, tenemos que seguir haciendo
  ajustes").
- La pantalla de una tarea abierta en este estilo (le gustó la disposición «una tarea por pantalla»).
- El resumen grande sale de datos reales (la muestra de Ismael dice «Marcos espera tu firma»: gana el punto 2).
- `DESIGN.md` todavía no tiene los contadores, el filtro ni el coral de «Vencidas»: pasarlos con el documenter
  cuando el usuario cierre esta pantalla.
- Después: aplicar a `web/` con impeccable, revisión final (finish reviewer) y `DESIGN.md` (documenter).
