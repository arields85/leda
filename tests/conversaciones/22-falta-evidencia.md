# 22. Lo que falta, una foto sin entrega y un video que no entra

**Qué prueba:** tres cosas de la evidencia antes de que la entrega se pueda confirmar. Una foto que llega
sin ninguna entrega abierta: Leda pregunta para qué es y la guarda sin contarla como evidencia. Un
"listo" al que le falta lo que pide la política del área: Leda dice qué falta, en palabras de todos los
días, y no pasa la tarea a revisión. Un video más grande de lo que hoy se puede recibir: Leda lo dice y
propone otra forma, nunca lo descarta en silencio. Circuito 7 (ADR 0017, decisión 3b); ADR 0019,
decisiones 2, 4 y 5; ADR 0018, decisión 4 (situación general 5); mecánica §6.

**Corre desde la porción 2 de la C-3** (`odd/tasks/fase-c.md`), con su YAML. En el paso 5, con el
enlace solo, el código lo cuenta como el archivo y falta cómo se probó (un enlace sirve para los dos;
el reparto es por las clases, no por lo que dice el enlace); con el archivo del paso 6 el reparto cambia
y queda como dice este hilo. En el paso 7, el aviso a Ismael es el de texto fijo de la cocina hasta la
porción 3.

## Estado inicial

- **Día:** D = lunes 26, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": área OT; la aprueba Ismael; vence el viernes 30; `en_curso` desde
    el lunes 19; sin bloqueos ni dependencias.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": área OT; la aprueba Ismael; vence el
    viernes 30; `en_curso` desde el miércoles 21; sin bloqueos ni dependencias.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Lo que pide la política de OT:** una explicación (texto), un resultado de prueba (texto, archivo,
  imagen o enlace), una captura (imagen) y un archivo (archivo, imagen o enlace). Un mismo texto puede
  cubrir varios tipos, si lo dice (la explicación y cómo se probó); la vista previa dice qué cubre cada
  pieza (ADR 0019, decisión 5).
- **El límite de un archivo:** 60 MB en el producto; mientras no esté el servidor propio de la API de
  bots, el del canal, 20 MB (ADR 0019, decisión 2).
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana.

## Hilo

1. **Marcos** manda (lunes 26, 09:40) una foto, sin texto.
   →
   - Jugadas: ninguna de la entrega: no hay una entrega abierta y la foto no dice nada.
   - Efecto: la foto queda guardada como parte de la conversación, con su huella y atada al espacio; no es
     evidencia de ninguna tarea.
   - La respuesta dice: que le llegó la foto; una pregunta: para qué es.
   - La respuesta no dice: qué muestra la foto (la IA no la mira); que la anotó como entrega.
   - Botones: sus dos tareas como opciones, porque admite más de una lectura (situación general 5).
   - Estado después: tema abierto, para qué es la foto.

2. **Marcos** escribe (09:42): "es de comunicaciones, la pantalla del switch con todos los puertos
   arriba. todavia no la termine eh"
   →
   - Jugadas: `elegir`, la tarea de comunicaciones; no es una entrega (dice que no la terminó).
   - Efecto: ninguno sobre la tarea; la foto sigue siendo parte de la conversación, no evidencia.
   - La respuesta dice: que la guarda y que se la va a mostrar cuando entregue esa tarea, para que decida
     si va.
   - La respuesta no dice: que la tarea quedó entregada o en revisión.
   - Estado después: sin tema abierto.

3. **Marcos** escribe (miércoles 28, 15:00): "listo lo de comunicaciones, quedo andando todo"
   →
   - Jugadas: `entregar`, la tarea de comunicaciones.
   - Efecto: ninguno sobre la tarea, que sigue `en_curso`. El código cuenta por tipo: el texto cubre la
     explicación, pero no dice cómo la probó, así que no cubre el resultado de la prueba (a diferencia
     del "20 ciclos sin una falla" de la conversación 21); la foto del lunes cubriría la captura si la
     deja; faltan el resultado de la prueba y un archivo. Sin la política completa no hay vista previa para confirmar (ADR 0019, decisión 5).
   - La respuesta dice: lo que falta, en palabras de todos los días, calculado por el código (cómo la
     probó y un archivo, por ejemplo la configuración del switch); que la foto del lunes va a estar en la
     entrega; que la tarea pasa a esperar la aprobación de Ismael cuando esté todo; el cierre, aparte: que
     mande lo que falta.
   - La respuesta no dice: que la entregó, que está en revisión o terminada; los nombres de los tipos de
     la política ("resultado_de_prueba", "captura"); que Ismael se enteró.
   - Botones: ninguno: no hay nada para confirmar.
   - Estado después: tema abierto, la entrega de comunicaciones, esperando lo que falta.

4. **Marcos** manda (15:20) un video de 48 MB, sin texto.
   →
   - Jugadas: ninguna: el archivo no se pudo recibir.
   - Efecto: no se guarda nada (el canal no deja bajar más de 20 MB); el intento queda en el registro de
     turnos. La entrega sigue abierta y le sigue faltando lo mismo.
   - La respuesta dice, en palabras de todos los días: que el video es muy pesado para recibirlo por acá;
     qué puede hacer (mandar uno más corto o un enlace al video); que sigue faltando un archivo.
   - La respuesta no dice: que lo recibió; el límite en términos técnicos o un error (constitución §10).
   - Estado después: tema abierto, la entrega de comunicaciones, esperando lo que falta.

5. **Marcos** escribe (15:25): "https://drive.google.com/file/d/prueba-comunicaciones/view"
   →
   - Jugadas: ninguna nueva: el enlace se suma a la entrega abierta.
   - Efecto: el enlace queda como pieza de la clase enlace; cubre el resultado de la prueba. Falta el
     archivo.
   - La respuesta dice: que sumó el enlace al video; que falta un archivo; el cierre, aparte: que lo mande.
   - Estado después: tema abierto, la entrega de comunicaciones, esperando lo que falta.

6. **Marcos** manda (15:30) el archivo `config-switch-planta.txt`, sin texto.
   →
   - Jugadas: ninguna nueva: el archivo se suma a la entrega abierta.
   - Efecto: la política está completa (texto, foto del lunes, enlace y archivo). Se guarda la vista
     previa con su huella; la tarea sigue `en_curso`.
   - La respuesta dice: la tarea de comunicaciones en su renglón con 📋; una pieza por renglón, con lo que
     cubre cada una en palabras de todos los días y la foto del lun 26/10 aparte, como mandada antes; el
     cierre, aparte: si la entrega así, o si corrige algo.
   - Botones: los de la confirmación.
   - Estado después: lo último mostrado para confirmar: la entrega con cuatro piezas.

7. **Marcos** escribe (15:31): "si"
   →
   - Jugadas: `confirmar`; la guarda pasa.
   - Efecto: las cuatro filas de evidencia y el paso a `en_revision`, en un solo acto, con evento de
     Marcos y auditoría; el aviso a Ismael, como en la conversación 21 (la foto del lunes adjunta, el
     archivo y el enlace al video en la página).
   - La respuesta dice: que la entregó y queda esperando la aprobación de Ismael, que se va a enterar
     a las 15:41, cuando termina el margen para corregir (ADR 0018, 9n).
   - Estado después: sin tema abierto, nada mostrado para confirmar.

## Qué mide

- **Garantías:** no inventa (sin la política completa no hay entrega, y una frase sola no cubre lo que
  pide un artefacto, mecánica §6); nunca falla en silencio (el video que no entra se dice, con qué hacer);
  nada cuenta como evidencia sin una entrega que lo incluya (la foto del paso 1 recién entra en el paso
  7); no deja sin salida (cada respuesta dice qué falta o qué sigue).
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA tome la foto del paso 1 o el "todavia no la termine" del paso 2
  como una entrega, o no tome "listo lo de comunicaciones" como una. Tiene que preguntar; pasar la tarea
  a revisión con piezas de menos es una falla de garantía.
