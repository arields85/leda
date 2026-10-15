# 55. Abrir la app, con una pregunta abierta

**Qué prueba:** Marcos tiene abierta la pregunta del lunes de cómo vienen sus tareas y, en lugar
de contestarla, pide abrir la app, después la dirección para la computadora y después algo que
Leda no hace. Prueba de la Mini App en el celular (2026-10-14): "abrí la app" no eligió ninguna
jugada, y Leda contestó sólo con la pregunta abierta, como si se la hubieran contestado.

- Pedir abrir la aplicación de Leda (la que se abre dentro de Telegram) es `pedir_acceso_web`:
  la respuesta lleva el botón "Mi espacio" (ADR 0024, decisiones 1 y 2).
- La dirección para la computadora va sola, sin botón: ahí se entra con el QR (decisión 4).
- Un pedido que ninguna jugada hace es `fuera_de_la_lista`, nunca ninguna jugada, también con una
  pregunta abierta (ADR 0018, decisión 1; la definición de `fuera_de_la_lista`).
- En los tres casos Leda contesta primero lo que pidió y después vuelve a la pregunta abierta, que
  sigue abierta (las instrucciones de la redacción: una pregunta `desde_antes` vuelve, y antes se
  contesta lo que el mensaje dijo o pidió).

**Corre** con su YAML, entera.

## Estado inicial

- **Día:** lunes 26, dentro del horario. Marcos ya recibió el ofrecimiento de la web.
- **Tareas de Marcos:** "Programar PLC de la comprimidora", en curso, vence el viernes 30;
  "Revisar comunicaciones industriales de la comprimidora", asignada, vence el viernes 6.

## Hilo

1. **Leda** (lunes 26, 10:00), la cadencia del lunes: le pregunta a Marcos cómo vienen sus tareas.
2. **Marcos** escribe (10:30): "abri la app"
   →
   - Jugadas: `pedir_acceso_web`.
   - La respuesta dice: que la abre tocando «Mi espacio», en pocas palabras y sin explicar si
     se abre dentro de Telegram o en el navegador (MA-4); después, la pregunta de cómo vienen.
   - Lleva el botón "Mi espacio". La pregunta sigue abierta.
3. **Marcos** escribe (10:35): "quiero entrar a la app desde la compu, pasame la direccion"
   →
   - Jugadas: `pedir_acceso_web`, para la computadora.
   - La respuesta dice: la dirección y que ahí entra escaneando el código con el celular; después,
     la pregunta. Sin botón.
4. **Marcos** escribe (10:40): "pasame el pronostico del tiempo para mañana"
   →
   - Jugadas: `fuera_de_la_lista`. La administración recibe la nota de un pedido fuera de la lista.
   - La respuesta dice: que eso no lo puede hacer y lo que sí; después, la pregunta.

## Qué mide

- **Garantías:** el botón va sólo con `pedir_acceso_web`; la dirección para la computadora va
  sola; la pregunta abierta sigue abierta.
- **Comprensión:** pedir abrir la app es `pedir_acceso_web`; un pedido que ninguna jugada hace es
  `fuera_de_la_lista`, no ninguna jugada.
- **Las palabras:** Leda contesta lo pedido antes de volver a la pregunta.
