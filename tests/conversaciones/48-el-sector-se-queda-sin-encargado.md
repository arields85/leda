# 48. El sector se queda sin encargado mientras se espera su decisión

**Estado:** corre en seco; falta la ronda con la IA real.

**Qué prueba:** Nahuel pidió ver el detalle de dos tareas de Lucas y, mientras los pedidos esperan
la decisión de Martín, el encargado de Infraestructura IT, la plataforma deja al sector sin
encargado. Nadie puede decidir si se comparte el detalle, así que los pedidos terminan. El tema se
cierra para todos: a Martín, a quien le había llegado la pregunta del switch, le llega una vez que
el pedido terminó y que no hace falta que conteste; de la del servidor, cuya pregunta todavía no le
había llegado, no le llega nada, porque con él no había un tema abierto. A Nahuel se le dice lo
mismo que si el sector no hubiera tenido encargado al pedirlo, sin nombrar a quién se le había
preguntado. Decisión 33 del usuario (el pedido del detalle, el caso raro), con la regla de cerrar el
tema para todos (constitución §8, decisión 39) y la de no nombrar a quién se informa (decisión 35);
`odd/tasks/fase-c.md`, "Al encargado anterior al que se le había pedido el detalle" (`80554c0`).
Repite el comienzo de la 45.

## La regla

1. **Un pedido del detalle sigue al encargado de ahora** (decisiones 16 y 43): si el sector se queda
   sin encargado mientras espera, nadie lo puede decidir y el pedido termina, sin compartir nada
   (`detalle.seguir_los_pedidos`, en la vuelta del seguimiento).
2. **A quien recibió la última pregunta del pedido**, que el pedido terminó y que no hace falta que
   conteste: una vez, como información de coordinación, a la hora en que Leda escribe. Sus hechos
   nombran sólo a quien lo pidió, como la pregunta que recibió; nada de la administración ni de que
   el sector se quedó sin encargado. Si la pregunta no le llegó, no se le dice nada.
3. **A quien lo pidió**, lo mismo que si el sector no hubiera tenido encargado al pedirlo: qué
   sector ve el detalle y que no hay a quién pedírselo. Si vuelve a pedirlo, la misma respuesta, sin
   preguntarle a nadie.
4. **El administrador se entera por su canal**, una vez por sector y por día.

## Estado inicial

- **Día:** D = lunes 26 de octubre, dentro del horario.
- **Personas:** Nahuel (de OT), Lucas (de Infraestructura IT; su trabajo lo aprueba Martín) y Martín
  (referente de Infraestructura IT: el encargado del sector). Ninguno tiene una pregunta de Leda
  abierta.
- **Tareas:**
  - "Configurar el switch de la planta", de Lucas, `en_curso` desde el lunes 19, vence el viernes
    30. Criterio de aceptación: "El switch de la planta da red a las doce máquinas de la línea y
    responde al monitoreo".
  - "Instalar el servidor de la planta", de Lucas, `en_curso` desde el lunes 19, vence el viernes 6
    de noviembre. Criterio de aceptación: "El servidor queda en el rack de la planta, con su
    respaldo diario funcionando y probado una vez".
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Nahuel** escribe (10:00): "pasame el link de la tarea del switch"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo.
   - Efecto: ninguno; ningún enlace.
   - La respuesta dice: el resumen (la del switch, de Lucas, en curso, vence el vie 30/10); que el
     detalle lo ve Infraestructura IT y que, si lo necesita, le pregunta a Martín.
   - La respuesta no dice: que no la puede ver.
   - Estado después: la propuesta abierta.

2. **Nahuel** escribe (10:02): "si dale"
   →
   - Jugadas: `pedir_el_detalle`.
   - Efecto: el pedido del detalle, y la pregunta a Martín guardada para dentro de diez minutos.
   - La respuesta dice: que le pregunta a Martín y le avisa cuando conteste.

3. **Leda** (10:12) le escribe a **Martín**: que Nahuel pide ver el detalle de la del switch, de
   Lucas; si se la comparte. Botones: "Compartirla" y "No compartirla".

4. **Nahuel** escribe (10:20): "y el del servidor de lucas?"
   →
   - Jugadas: `pedir_enlace`, nombrada por cómo la dijo.
   - La respuesta dice: el resumen del servidor (de Lucas, en curso, vence el vie 6/11); que el
     detalle lo ve Infraestructura IT y que, si lo necesita, le pregunta a Martín. Sin enlace.

5. **Nahuel** escribe (10:21): "si porfa"
   →
   - Jugadas: `pedir_el_detalle`.
   - Efecto: el pedido del servidor, y la pregunta a Martín guardada para las 10:31: todavía no le
     llegó.
   - La respuesta dice: que le pregunta a Martín por la del servidor y le avisa cuando conteste.

6. **La plataforma** (10:25) deja a Infraestructura IT sin encargado: Martín deja de ser su
   referente y sigue en el equipo.
   →
   - Efecto: ninguno en ese momento; lo nota el seguimiento.

7. **Leda** (10:30): los dos pedidos terminan, sin compartir nada.
   - A **Martín**: que el pedido de Nahuel para ver el detalle de la del switch terminó y que ya no
     hace falta que conteste. Sus hechos no dicen nada de la administración ni de que el sector se
     quedó sin encargado. Lleva el enlace a la página de la tarea, que Martín ve porque revisa el
     trabajo de Lucas.
   - De la del servidor, a Martín no le llega nada: la pregunta nunca le llegó, y ya no sale.
   - Al administrador, por su canal, que Infraestructura IT no tiene encargado: una vez.
   - A Nahuel, todavía nada: escribió a las 10:21 y Leda no lo interrumpe hasta las 10:51.

8. **Leda** (10:51) le escribe a **Nahuel**, un aviso por tarea: que el detalle de la del switch y
   el de la del servidor no se compartieron, porque Infraestructura IT no tiene por ahora a quién
   pedírselo; lo mismo que si no hubiera tenido encargado al pedirlo. Sin el nombre de Martín y sin
   enlace.

9. **Martín** toca "Compartirla" en la pregunta del switch (11:00).
   →
   - Efecto: ninguno; nada queda compartido.
   - La respuesta dice: que esa pregunta ya no espera su respuesta.

10. **Nahuel** escribe (11:30): "y lo del switch no se lo podes pedir igual a martin?"
    →
    - Jugadas: `pedir_el_detalle`, nombrada por cómo la dijo.
    - Efecto: ninguno; ni otro pedido ni otro aviso al administrador (ya se enteró hoy).
    - La respuesta dice: que el detalle de la del switch lo ve Infraestructura IT y que por ahora no
      tiene a quién pedírselo. Si nombra lo del servidor (la pregunta anunciada en el paso 5 ya no
      sale), lo mismo que se le dijo a las 10:51.
    - La respuesta no dice: que le pregunta a Martín; nada de la administración o de la plataforma.

## Qué mide

- **Garantías:** nada se comparte sin la decisión del encargado de ahora (pasos 7, 9 y 10); a
  quien recibió la pregunta le llega, una vez, que el tema terminó, y a quien no la recibió, nada
  (paso 7); el enlace sale sólo para quien ve la tarea (pasos 7, 8 y 10); el administrador se
  entera una vez por sector y por día (pasos 7 y 10); ningún efecto en las tareas.
- **Comprensión:** la IA elige `pedir_enlace` y `pedir_el_detalle` como en la 45, y otra vez
  `pedir_el_detalle` cuando Nahuel insiste.
- **Las palabras:** a Martín y a Nahuel, nada de la administración, de la plataforma ni de quién
  dejó de ser encargado; a Nahuel, nunca a quién se le había preguntado (decisión 35); sin nombres
  del sistema (constitución §10); todo mensaje con su próximo paso, y los avisos, con que no hace
  falta contestar.
- **El formato:** el de la conversación 20 en cada mensaje.
