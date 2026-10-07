# 18. Habla de lo que pasa en el mundo, no de la cocina

**Qué prueba:** Leda le cuenta a la persona lo que va a ver pasar: quién se entera de qué y cuándo, y lo
que ella misma va a hacer y cuándo. Nunca cómo lo maneja el sistema por dentro: que un aviso está
guardado, en cola, programado o sin enviar, o que un pedido "ya no sale". Sigue siendo honesta: lo que
todavía no pasó lo cuenta en futuro y nunca lo da por hecho (primer contacto real, hallazgo 1). Lo anunciado
antes que ya no va a pasar lo dice sólo si a la persona le sirve (ADR 0018, 9m). Decisión del usuario del
2026-10-06, de la prueba por Telegram real (bitácora de flujos, "Prueba por Telegram real del flujo D":
"Leda cuenta de más lo de la cocina").

## Estado inicial

- **Día:** D = viernes 23, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence hoy, viernes 23; `en_curso` desde el
    lunes 19; sin bloqueos ni previsiones.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 6 de
    noviembre (su aviso previo sale el martes 3, fuera de este hilo); `asignada`; depende de la del PLC con
    una dependencia bloqueante (la de la semilla).
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** a Marcos, el aviso previo de la tarea del PLC (martes 20), que no pide respuesta. A
  Ismael, nada.

## Hilo

1. **Leda**, por su cuenta, a Marcos (viernes 23, 10:00): el pedido de estado del día del vencimiento.
   →
   - Efecto: un mensaje privado en el outbox; queda abierta la espera de su respuesta y la pregunta del
     estado de la tarea del PLC.
   - El mensaje dice: que la tarea del PLC vence hoy; pide el estado.
   - El mensaje no dice: que va a avisar a Ismael; un reproche.
   - Botones: ninguno (decisión 9b).

2. **Marcos** escribe (viernes 23, 11:00): "voy bien, casi la tengo"
   →
   - Jugadas: `informar_avance` sobre la tarea del PLC.
   - Efecto: el avance anotado con sus palabras; la espera sigue abierta y Leda vuelve a pedir el estado el
     lunes 26, el día hábil siguiente (9h).
   - La respuesta dice: que anotó lo que Marcos contó; que el lunes 26 le vuelve a preguntar, como algo
     que todavía no pasó.
   - La respuesta no dice: que algo quedó guardado, programado, en cola o sin enviar; ninguna pregunta.
   - Estado después: sin tema abierto; la espera sigue abierta.

3. **Nadie** escribe el resto del viernes.

4. **Marcos** escribe (lunes 26, 08:30, antes de la hora en que Leda escribe por su cuenta): "la tengo para
   el miercoles"
   →
   - Jugadas: `anotar_prevision` sobre la tarea del PLC, con fecha miércoles 28.
   - Efecto: una previsión al miércoles 28; la fecha comprometida sigue siendo el viernes 23. Ismael se va
     a enterar hoy, a la hora en que Leda escribe por su cuenta (10:00), con la previsión, la fecha
     comprometida, el atraso y lo que depende de la tarea. La fecha contesta la espera: el pedido del
     estado que el paso 2 anunció para hoy ya no va a pasar, y el seguimiento se mueve a la previsión
     (9i).
   - La respuesta dice: que anotó que la tiene el miércoles 28; que la fecha comprometida sigue siendo el
     viernes 23; que Ismael se va a enterar hoy, como algo que todavía no pasó; el próximo paso concreto:
     que Leda le pide el estado el miércoles 28.
   - La respuesta no dice: que el aviso a Ismael está guardado, en cola, programado o todavía sin enviar;
     que Ismael ya se enteró; que un pedido o un aviso "ya no sale", "se retiró" o "quedó sin efecto"
     (si lo dice, lo dice como lo que va a pasar: que hoy no le vuelve a preguntar); que hoy le vuelve a
     pedir el estado.
   - Estado después: sin tema abierto, nada para después; ninguna espera abierta.

5. **Leda**, por su cuenta, a Ismael (lunes 26, 10:00): el aviso de la nueva previsión. A Marcos, nada.
   →
   - El mensaje dice: que Marcos prevé terminar la tarea del PLC el miércoles 28; que la fecha
     comprometida era el viernes 23; el atraso, tres días hábiles; que la de comunicaciones depende de ella.
   - El mensaje no dice: que Ismael tiene que hacer algo; cómo funciona el aviso.

6. **Nadie** escribe del lunes 26 al miércoles 28 a las 10:00.

7. **Leda**, por su cuenta, a Marcos (miércoles 28, 10:00): el pedido de estado del día que Marcos dio (9i).
   Ismael ya se enteró de la previsión el lunes.
   →
   - El mensaje dice: que hoy es el día que Marcos dio para la tarea del PLC; pide el estado; si nombra a
     Ismael, como alguien que ya está al tanto.
   - El mensaje no dice: que un aviso salió, se envió o estaba guardado; que va a avisar a Ismael; un
     reproche.
   - Estado después: tema abierto, la pregunta del estado de la tarea del PLC; la espera, abierta.

## Qué mide

- **La regla (usuario, 2026-10-06):** Leda cuenta lo que pasa en el mundo (quién se entera de qué y
  cuándo, qué va a hacer ella y cuándo) y nunca el estado interno de un aviso o de un pedido. Es una falla
  que la respuesta diga que algo está guardado, en cola, programado, sin enviar, que salió o que no sale.
- **Garantías (5b):** no inventa (lo que todavía no pasó va en futuro: que Ismael se enteró antes de las
  10:00 del lunes es una falla de honestidad); no deja sin salida (cada mensaje termina con su próximo
  paso); no confunde la tarea.
- **Falla de comprensión:** que la IA no tome "voy bien, casi la tengo" como un avance o "la tengo para el
  miercoles" como una nueva previsión.
