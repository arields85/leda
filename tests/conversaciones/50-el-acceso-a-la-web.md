# 50. El acceso a la web

**Qué prueba:** cada integrante recibe por chat su entrada a la plataforma web y la puede cortar si
pierde el celular. Leda le ofrece el acceso, una sola vez y al final de su respuesta, a quien nunca
entró; lo manda de nuevo a pedido, con el aviso de que sirve una vez y vence en 24 horas, y el
anterior deja de servir; "perdí el celular" corta el acceso enseguida, sin confirmación, y Leda
recuerda cerrar Telegram en ese celular. ADR 0022, decisión 4, y su precisión del 2026-10-12 (el
enlace que nadie usó vence a las 24 horas, y Leda lo dice al mandarlo); decisiones 1 a 3 del usuario
en `odd/tasks/acceso-por-chat.md` (2026-10-12); ADR 0018, decisión 1 (la IA elige la jugada de la
lista cerrada; la cocina decide y ejecuta); constitución §10 (la IA nunca escribe una dirección).
El usuario aceptó este hilo tal como está (2026-10-12, noche).

**Corre desde la A-1 de `odd/tasks/acceso-por-chat.md`**, entera, con su YAML. Hasta que la A-3 y
la A-4 construyan las dos jugadas, la marca del enlace y el ofrecimiento, la corrida en seco falla:
es su RED. Desde la A-4 pasa entera. En el corredor, a las demás conversaciones la web ya se les
dio por ofrecida; en ésta, ni a Marcos ni a Ariel (`sin_ofrecer_la_web`): a Ariel no se le ofrece
porque ya entró.

## La regla

1. **Dos jugadas nuevas de la lista cerrada, sin tarea:** `pedir_acceso_web` (un enlace nuevo; el
   anterior sin usar deja de servir) y `perdi_el_celular` (corta todas las sesiones de la persona y
   su enlace sin usar, con el motivo `perdio_el_celular`).
2. **El enlace no pasa por la IA**, como el de la página de una tarea: la respuesta lleva una marca y
   el despachador emite el enlace al mandar y agrega la dirección al final, sin vista previa. Uno
   solo por mensaje.
3. **El ofrecimiento, una sola vez:** al final de la respuesta a lo que la persona escribió, si
   nunca entró a la web ni se le ofreció. Nunca en un aviso que Leda manda por su cuenta.

## Estado inicial

- **Día:** D = lunes 19, dentro del horario.
- **Personas:** Marcos (referente de OT; su trabajo lo aprueba Ismael), que **nunca entró a la
  web** ni se le ofreció; Ariel (referente de Software e interfaz HMI; su trabajo lo aprueba Ismael),
  que **ya tiene la sesión de la web abierta** (entró con su enlace antes de la conversación).
  Ninguno tiene una pregunta de Leda abierta.
- **Tareas:**
  - "Programar PLC de la comprimidora", de Marcos, `asignada`, vence el lunes 26. Criterio de
    aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora", de Marcos, `en_curso` desde el lunes
    19, vence el viernes 30. Criterio de aceptación: "Los equipos de la comprimidora se comunican
    con el PLC por la red de planta sin errores durante una hora".
  - "Integrar datos de la comprimidora en CoreLabs", de Ariel, `en_curso` desde el lunes 19, vence
    el viernes 30. Criterio de aceptación: "Los datos de la comprimidora se ven en CoreLabs, con
    menos de un minuto de demora, durante una jornada de producción".
- **Lo ya enviado:** nada que importe para el hilo.

## Hilo

1. **Marcos** escribe (lunes 19, 10:30): "que tengo pendiente?"
   →
   - Jugadas: `consultar_pendientes`.
   - Efecto: se emite su enlace de entrada a la web, al mandar (el del ofrecimiento).
   - La respuesta dice: sus dos tareas, como hoy, y al final el ofrecimiento: que ahora también
     puede ver sus tareas en la web, que ahí va el enlace, que sirve una vez y vence en 24 horas, y
     que si no lo usa le pida otro.
   - Al final, el enlace de entrada a la web (lo agrega el código, no la IA), sin vista previa.
   - Un solo mensaje. Botones: ninguno.

2. **Marcos** escribe (10:35): "dale gracias"
   →
   - Jugadas: ninguna de la lista.
   - Efecto: ninguno.
   - La respuesta: contesta sin volver a ofrecer el acceso. Sin enlace.

3. **Ariel** escribe (10:40): "que tengo pendiente?"
   →
   - Jugadas: `consultar_pendientes`.
   - Efecto: ninguno; su sesión de la web sigue abierta.
   - La respuesta dice: su tarea, sin ofrecimiento (ya entró a la web). Sin enlace.

4. **Marcos** escribe (martes 20, 10:30): "no me anda el link de la web, pasame otro"
   →
   - Jugadas: `pedir_acceso_web`.
   - Efecto: un enlace nuevo, emitido al mandar; el anterior, que no usó, queda anulado.
   - La respuesta dice: que ahí va el enlace nuevo, que sirve una vez y vence en 24 horas; que el
     anterior ya no sirve.
   - Al final, el enlace de entrada a la web, sin vista previa.
   - La respuesta no dice: que el enlace anterior tenía un problema técnico, ni ningún detalle de
     cómo funciona por dentro.

5. **Marcos** escribe (10:40): "casi pierdo el celular en el colectivo jaja"
   →
   - Jugadas: ninguna de la lista.
   - Efecto: ninguno; no corta nada (su enlace sin usar sigue sirviendo).
   - La respuesta: contesta con naturalidad. Sin enlace.
   - La respuesta no dice: que le cortó el acceso.

6. **Marcos** escribe (10:50): "perdi el celular"
   →
   - Jugadas: `perdi_el_celular`.
   - Efecto: corta el acceso a la web enseguida, sin confirmación: sus sesiones (no tiene ninguna) y
     su enlace sin usar, con el motivo `perdio_el_celular`.
   - La respuesta dice: que le cortó el acceso a la web; que cierre Telegram en ese celular desde
     otro dispositivo, en Ajustes → Dispositivos; y que pida un enlace nuevo cuando tenga otro
     celular.
   - Botones: ninguno. Sin enlace.

7. **Leda** por su cuenta (miércoles 21, 10:00): el aviso previo del vencimiento de la del PLC (vence
   el lunes 26) a Marcos.
   →
   - El mensaje dice: el aviso, como siempre, sin ofrecimiento del acceso a la web. Sin enlace.

## Qué mide

- **Garantías:** el enlace de entrada a la web sale sólo con el ofrecimiento (paso 1) o a pedido
  (paso 4), siempre al final y sin vista previa, y la IA nunca escribe su dirección; el anterior sin
  usar deja de servir (paso 4); "casi pierdo el celular" no corta nada (paso 5) y "perdí el
  celular" corta enseguida, sin botones (paso 6); la sesión de Ariel nunca se corta; ningún efecto
  en las tareas.
- **Comprensión:** la IA elige `pedir_acceso_web` en el paso 4, `perdi_el_celular` en el 6 y
  ninguna jugada en el 2 y en el 5.
- **El ofrecimiento:** una sola vez (paso 1), nunca a quien ya entró (paso 3) ni en un aviso que
  Leda manda por su cuenta (paso 7).
- **Las palabras:** sin nombres del sistema (constitución §10).
- **El formato:** el de la conversación 20 en cada mensaje.

Garantías aparte, con pruebas deterministas (A-2 a A-4): un enlace de hace 24 horas y un minuto no
abre; el corte deja la auditoría con su motivo, también sin sesiones abiertas; el ofrecimiento no se
repite aunque se mande dos veces la misma respuesta.
