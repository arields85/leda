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
cinco pestañas). Recorrido: «La etiqueta» → sorteos audaz y seguro → disposición «una tarea por pantalla» (gustó
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
(3 a 5 según el rol) y una rayita sobre la activa (aceptada en `impeccable live` el 2026-10-15).
FORM: «El pizarrón» (candidato 3 de la lista propia de la ronda 3, asignado por el sorteo), refinado por el
usuario; seed key 71b06f5b.
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

## Pendiente

- Ajustes que el usuario va a seguir pidiendo (dijo "vamos por buen camino, tenemos que seguir haciendo
  ajustes").
- La pantalla de una tarea abierta en este estilo (le gustó la disposición «una tarea por pantalla»).
- El resumen grande sale de datos reales (la muestra de Ismael dice «Marcos espera tu firma»: gana el punto 2).
- `DESIGN.md` todavía no tiene los contadores, el filtro ni el coral de «Vencidas»: pasarlos con el documenter
  cuando el usuario cierre esta pantalla.
- Después: aplicar a `web/` con impeccable, revisión final (finish reviewer) y `DESIGN.md` (documenter).
