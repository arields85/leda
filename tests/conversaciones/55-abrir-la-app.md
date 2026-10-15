# 55. Abrir la app, con una pregunta abierta

**Qué prueba:** Marcos tiene abierta la pregunta del lunes de cómo vienen sus tareas y, en lugar
de contestarla, pide abrir la app, después la dirección para la computadora y después algo que
Leda no hace, y por último, desde la computadora, abrirla en el navegador. Prueba de la Mini App en
el celular (2026-10-14): "abrí la app" no eligió ninguna jugada, y Leda contestó sólo con la
pregunta abierta, como si se la hubieran contestado. Prueba en la computadora (2026-10-14, MA-5):
a "Abrí Leda en el navegador", Leda contestó que se abre dentro de Telegram y no en el navegador:
la definición de la jugada decía que la aplicación es "la que se abre dentro de Telegram".

**Enmienda (decisión del usuario, 2026-10-14, noche; MA-5):** a pedido, la respuesta ya no lleva
el botón "Mi espacio". Leda le dice que la abre con el botón fijo "Mi espacio" del menú del chat,
al lado de donde escribe (en el celular, dentro de Telegram; en Telegram de la computadora, en el
navegador). La bienvenida sigue con su botón.

- Pedir abrir la aplicación de Leda es `pedir_acceso_web`: la respuesta no lleva ningún botón y
  dice que la abre con el botón fijo "Mi espacio" del menú (MA-5).
- La dirección para la computadora va sola, sin botón: ahí se entra con el QR (decisión 4).
- En el celular la aplicación se abre dentro de Telegram; en Telegram de la computadora, en el
  navegador. Quererla en el navegador es lo mismo que pedir abrirla (MA-5).
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
   - La respuesta dice: que la abre con el botón «Mi espacio» del menú, al lado de donde escribe,
     en pocas palabras; después, la pregunta de cómo vienen.
   - Sin botón (MA-5). La pregunta sigue abierta.
3. **Marcos** escribe (10:35): "quiero entrar a la app desde la compu, pasame la direccion"
   →
   - Jugadas: `pedir_acceso_web`, para la computadora.
   - La respuesta dice: la dirección y que ahí entra escaneando el código con el celular; después,
     la pregunta. Sin botón.
4. **Marcos** escribe (10:40): "pasame el pronostico del tiempo para mañana"
   →
   - Jugadas: `fuera_de_la_lista`. La administración recibe la nota de un pedido fuera de la lista.
   - La respuesta dice: que eso no lo puede hacer y lo que sí; después, la pregunta.
5. **Marcos**, desde la computadora, escribe (10:45): "Abrí Leda en el navegador"
   →
   - Jugadas: `pedir_acceso_web`.
   - La respuesta dice: que la abre con el botón «Mi espacio» del menú, al lado de donde escribe;
     después, la pregunta. Sin botón.
   - Nunca dice que Leda no se abre en el navegador ni que se abre sólo dentro de Telegram.

## Qué mide

- **Garantías:** ningún mensaje lleva un botón; la dirección para la computadora va sola; la
  pregunta abierta sigue abierta.
- **Comprensión:** pedir abrir la app, también en el navegador, es `pedir_acceso_web`; un pedido
  que ninguna jugada hace es `fuera_de_la_lista`, no ninguna jugada.
- **Las palabras:** Leda contesta lo pedido antes de volver a la pregunta.
