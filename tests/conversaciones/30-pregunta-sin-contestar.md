# 30. Una pregunta de Leda sin contestar

**Qué prueba:** una pregunta de Leda que la persona no contesta frena sus otros temas, pero no para
siempre: Leda la repite una vez en el día, a las 4 horas, y si 4 horas después sigue sin contestar y
todavía es horario, el tema siguiente más urgente sale aparte. Las dos preguntas quedan abiertas a la
vez (una para después): la persona contesta cualquiera, nombrando la tarea, y cuando una se cierra el
código trae la otra enseguida, en un mensaje aparte. Al día siguiente sigue la escalera y lo que
espera sale de a uno, primero lo más urgente. Las dos formas de contestar: el miércoles Marcos
contesta primero la segunda pregunta; el jueves, primero la que había quedado para después.
Decisión 21 del usuario (`odd/tasks/fase-c.md`, 2026-10-08, opción B), del `PENDIENTE` de la D5 (una
pregunta que nunca se contesta frenaba todo); regla de un tema a la vez (ADR 0018, decisión 4) y
conversación 26.

**Corre desde la D5b de la C-3d** (`odd/tasks/fase-c.md`), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-08)

1. **Una pregunta sin contestar frena los otros temas que piden respuesta** (decisión 13, conversación
   26), **hasta que Leda la repite, una sola vez en el día, a las 4 horas** de haberla hecho (valor
   del espacio, `pregunta_sin_contestar_minutos`, 240; después, desde la plataforma).
2. **Si 4 horas después de la repetición sigue sin contestar y todavía es horario, sale aparte el tema
   siguiente más urgente**, en su propio mensaje. Ejemplo del usuario: 08:55 la entrega del PLC, 12:55
   su repetición, 16:55 "hoy vence el tablero".
3. **La segunda pregunta guarda la primera para después.** La persona contesta cualquiera de las dos,
   nombrando la tarea. Al cerrarse una, **el código** (no la IA) trae la otra enseguida, en un mensaje
   aparte.
4. **Al día siguiente sigue la escalera.** Varias cosas esperando van de a una, primero la más urgente,
   con la misma regla.
5. **El aviso de que se va a informar el atraso es informar, sin nombrar a nadie**, nunca "la paso
   para que te ayuden a destrabarla"; si la persona pregunta a quién, Leda dice el nombre. **Con la
   forma de la decisión 35** (2026-10-09): "Si mañana sigue igual, va a quedar asentado que está
   atrasada" y, sólo si el espacio tiene informe al grupo, "para que el equipo esté al tanto"; Leda
   no dice que le informa a alguien. Lo ejercitan los pedidos de estado de la 04; acá no llega.

Cómo se leyó lo que la regla no dice (`PENDIENTE` del usuario, en `odd/tasks/fase-c.md`, D5b):

- **La repetición a las 4 horas sale siempre** (decisión 29 del usuario, 2026-10-09, que reemplaza
  la lectura de que era sólo para destrabar): haya o no otro tema esperando detrás (conversación 03).
- **"Más urgente":** el tipo de mensaje más urgente (mecánica §11) y, entre iguales, la tarea que
  vence antes.
- **"Al día siguiente":** una pregunta hecha un día anterior ya no frena: a la hora en que Leda escribe
  por su cuenta sale lo más urgente de lo que espera, que puede ser la misma pregunta, repetida por su
  escalera, o el tema de otra tarea.
- **"Enseguida":** el mensaje aparte no espera los 30 minutos de la conversación 26 (es la conversación
  que sigue) ni el horario: es parte de contestarle a lo que la persona escribió (mecánica §10), así
  que fuera del horario también sale justo después de la respuesta (decidido por el coordinador a
  partir de la decisión 50).
- **También cuando la persona cambia de tema** (decisión 50 del usuario, 2026-10-09, que reemplaza
  la lectura de que el mensaje aparte era sólo para dos temas que abrió Leda): la pregunta que quedó
  vuelve en un mensaje aparte, justo después de la respuesta a lo nuevo (conversaciones 08 y 12).

## Estado inicial

- **Día:** D = miércoles 28, dentro del horario, hasta las 17:00.
- **Tareas de Marcos** (referente Ismael):
  - "Programar PLC de la comprimidora": vence el viernes 30; `en_curso`; sin bloqueos ni previsiones.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Cablear tablero de la máquina 3": vence hoy, miércoles 28; `asignada`; sin bloqueos ni
    previsiones. Criterio de aceptación: "El tablero queda cableado según el plano y pasa la prueba de
    continuidad de todos sus circuitos".
  - "Revisar comunicaciones industriales de la comprimidora": vence el jueves 29; `asignada`; sin
    bloqueos ni previsiones. Criterio de aceptación: "Los equipos de la comprimidora se comunican con
    el PLC por la red de planta sin errores durante una hora".
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después.
- **Ya enviado:** el aviso previo de cada tarea (el lunes 26, las del tablero y comunicaciones; el
  martes 27, la del PLC).

## Hilo

1. **Marcos** escribe (miércoles 28, 08:55): "el plc esta trabado, me falta el cable de programacion"
   →
   - Jugadas: `anotar_bloqueo` sobre el PLC, con la causa.
   - Efecto: el bloqueo, directo; el PLC queda trabado.
   - La respuesta dice: que quedó anotado el bloqueo y su causa, y pregunta quién lo puede destrabar.
   - Estado después: tema abierto, quién destraba el PLC.

2. **Leda**, a las 10:00, va a pedir el estado del tablero (vence hoy).
   →
   - Efecto: el pedido pide respuesta y la pregunta del PLC sigue abierta: espera (regla, punto 1).
     Ningún mensaje para Marcos.

3. **Leda**, a las 12:55 (4 horas después de la pregunta), la repite.
   →
   - Efecto: sale sola la pregunta de quién destraba el PLC, una vez; el pedido del tablero sigue
     esperando.
   - El mensaje dice: el bloqueo del PLC por el cable y la pregunta de quién lo puede destrabar.
   - El mensaje no dice: nada del tablero; un reproche porque no contestó.

4. **Leda**, a las 16:50, vuelve a revisar.
   →
   - Efecto: todavía no pasaron 4 horas desde la repetición. Ningún mensaje.

5. **Leda**, a las 16:55 (4 horas después de la repetición, todavía en horario).
   →
   - Efecto: sale aparte el pedido de estado del tablero, que vence hoy (regla, punto 2). Su pregunta
     queda abierta y la del PLC, para después (punto 3). La de quién destraba no se repite otra vez hoy.
   - El mensaje dice: que el tablero vence hoy y pide el estado.
   - El mensaje no dice: nada del PLC.
   - Estado después: tema abierto, el estado del tablero; para después, quién destraba el PLC.

6. **Marcos** contesta primero la segunda (miércoles 28, 16:57): "el tablero lo arranque hoy"
   →
   - Jugadas: `anotar_inicio` sobre el tablero.
   - Efecto: el tablero queda en curso; el pedido de estado se contesta.
   - La respuesta dice: que quedó anotado que arrancó el tablero.
   - La respuesta no dice: la pregunta del PLC (la trae el código aparte, punto 3).
   - Estado después: tema abierto, quién destraba el PLC.

7. **Leda**, a las 16:58, trae la otra pregunta, en un mensaje aparte.
   →
   - Efecto: sale la pregunta de quién destraba el PLC, aunque Marcos escribió hace un minuto.
   - El mensaje dice: el bloqueo del PLC y la pregunta de quién lo puede destrabar.

8. **Leda**, el jueves 29 a las 10:00. Esperan dos cosas: la pregunta del PLC, que su escalera repite
   (un día hábil sin respuesta), y el pedido de estado de comunicaciones, que vence hoy.
   →
   - Efecto: la pregunta del PLC es de ayer y ya no frena: sale lo más urgente, el pedido de
     comunicaciones, que vence antes (regla, punto 4). La pregunta del PLC queda para después y su
     repetición espera.
   - El mensaje dice: que comunicaciones vence hoy y pide el estado.
   - El mensaje no dice: nada del PLC.
   - Estado después: tema abierto, el estado de comunicaciones; para después, quién destraba el PLC.

9. **Marcos** contesta primero la que había quedado para después (jueves 29, 10:20): "el cable lo
   consigue pedro de compras"
   →
   - Jugadas: `anotar_quien_destraba` sobre el PLC, "pedro de compras".
   - Efecto: quién destraba queda anotado y la pregunta del PLC se cierra.
   - La respuesta dice: que quedó anotado que el cable lo consigue Pedro de compras.
   - La respuesta no dice: la pregunta de comunicaciones (la trae el código aparte).
   - Estado después: tema abierto, el estado de comunicaciones.

10. **Leda**, a las 10:21, trae la otra pregunta, en un mensaje aparte.
    →
    - Efecto: sale el pedido de estado de comunicaciones otra vez. La repetición del PLC, que esperaba,
      no sale: Marcos está conversando, y ya contestó.
    - El mensaje dice: la tarea de comunicaciones y pide el estado.

11. **Marcos** escribe (jueves 29, 10:40): "comunicaciones la arranque recien"
    →
    - Jugadas: `anotar_inicio` sobre comunicaciones.
    - Efecto: comunicaciones queda en curso; el pedido de estado se contesta.
    - Estado después: sin tema abierto, nada para después.

12. **Leda**, a las 11:15 (30 minutos sin que Marcos escriba).
    →
    - Efecto: la repetición de la pregunta del PLC queda omitida: ya la contestó. Ningún mensaje.

## Qué mide

- **Garantías:** nunca dos preguntas de Leda en un mismo mensaje; la repetición, una sola vez en el
  día; lo que espera sale de a uno y nunca fuera del horario (salvo la pregunta que vuelve, que es
  parte de la respuesta); la pregunta contestada no vuelve; nada
  se pierde (lo que no sale queda omitido con su motivo).
- **Comprensión:** que la IA tome la respuesta de la pregunta que quedó para después (pasos 6 y 9,
  con la tarea nombrada) y no la de la abierta.
