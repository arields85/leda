# 21. La entrega con su evidencia

**Qué prueba:** Marcos dice que terminó la tarea del PLC y manda las fotos. Lo que escribe no dice todo
el criterio de aceptación: Leda pregunta sólo lo que falta, con un ejemplo, y Marcos lo acepta. Leda le
muestra qué va en la entrega, también lo que mandó antes durante la tarea, que entra sólo si lo deja;
Marcos saca una pieza,
toca el botón de una vista previa vieja, manda otra foto junto con un "dale" que no vale (la guarda
escrita) y confirma. La tarea pasa a revisión, nunca a terminada, y a Ismael le llega el aviso redactado
por el motor, con las fotos adjuntas y un enlace a la página de la tarea. Circuito 7 (ADR 0017, decisión
3b); ADR 0018, decisiones 2 y 4 (situaciones generales 3, 6 y 7); ADR 0019, decisiones 4 a 6;
constitución §7 y §11. Toma los pasos "Para la prueba de la entrega" de las conversaciones 10 y 11.

**Corre desde la porción 2 de la C-3** (`odd/tasks/fase-c.md`), con su YAML, del paso 1 al 7; el paso 8,
desde la porción 3a: el aviso redactado por el motor, con las fotos adjuntas; desde la 3b, con los
botones Aprobar y Pedir cambios, y desde la 4, con el enlace a la página de la tarea.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": área OT; la aprueba Ismael; vence el viernes 23; `en_curso` desde
    el lunes 19; sin bloqueos ni dependencias.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": área OT; la aprueba Ismael; vence el viernes
    30; `asignada`; sin bloqueos ni dependencias.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Lo que pide la política de OT** (`espacios/corework.yaml`, `evidencia.por_area`, con las clases del ADR
  0019, decisión 5): una explicación (texto), un resultado de prueba (texto, archivo, imagen o enlace), una
  captura (imagen) y un archivo (archivo, imagen o enlace). Un mismo texto puede cubrir varios tipos (la
  explicación y el resultado de la prueba); lo cuenta el código, y la vista previa dice qué cubre cada
  pieza para que la persona lo confirme o lo corrija (ADR 0019, decisión 5).
- **Lo que Marcos mandó durante la tarea**, guardado como parte de la conversación y todavía no como
  evidencia (ADR 0019, decisión 4; cómo se llega a esto es la conversación 22):
  - martes 20, 11:05: una foto, sin texto; Marcos dijo que era del PLC;
  - miércoles 21, 16:00: el archivo `comprimidora_v3.zip` (el programa exportado del PLC); Marcos dijo
    que era para cuando entregara.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar. **De Ismael:** igual.
- **Ya enviado:** el aviso previo de la tarea del PLC, el martes 20 a las 10:00. A Ismael, nada.

## Hilo

1. **Marcos** manda (jueves 22, 15:10) un álbum de dos fotos (la pantalla del HMI con la comprimidora
   andando y el contador de ciclos) con el texto: "termine el plc!! ahi va la pantalla y el contador, 20
   ciclos sin una falla"
   →
   - Jugadas: `entregar`, la tarea del PLC. El álbum es un solo mensaje y un solo turno (ADR 0019,
     decisión 4).
   - Efecto: ninguno sobre la tarea todavía. El código junta las piezas: el texto, las dos fotos de hoy y
     lo que llegó durante la tarea (la foto del martes y `comprimidora_v3.zip`), y comprueba la política
     por tipo: el texto cubre la explicación y el resultado de la prueba (20 ciclos sin una falla), las
     fotos de hoy cubren la captura y, con el archivo del miércoles, la política está completa. Lo
     escrito no dice todo el criterio de aceptación: dice los 20 ciclos sin fallas, pero no que la
     comprimidora arranca desde el PLC. La IA lo juzga punto por punto y el código decide que falta
     (decisión 10 del usuario, 2026-10-08; C-3d, D7: con la IA real Leda lo preguntó 5 de 5, y era lo
     correcto). No hay nada para confirmar.
   - La respuesta dice: la tarea del PLC en su renglón con 📋; que sumó su descripción (cómo quedó y la
     prueba de 20 ciclos) y las dos fotos de hoy, y aparte, como mandadas antes, la foto del mar 20/10 y
     `comprimidora_v3.zip` del mié 21/10, que entran sólo si las deja; una sola vez qué falta para
     entregarla, hablando de la tarea: si la comprimidora arranca desde el PLC; el ejemplo, para que lo
     acepte o lo escriba con sus palabras; el cierre, aparte: si va así.
   - La respuesta no dice: que la tarea quedó entregada, en revisión o terminada; que falta saber si
     completó los 20 ciclos sin fallas (ya lo dijo); qué muestran las fotos (la IA no las mira); los
     nombres de los tipos de la política; que falta el resultado de la prueba o que lo mande aparte (el
     texto ya lo da); "contaste" o "contarlo": lo que escribió es su descripción.
   - Botones: ninguno: no hay nada para confirmar.
   - Estado después: tema abierto, la entrega del PLC, esperando lo que falta.

2. **Marcos** escribe (15:11): "si va asi"
   →
   - Jugadas: `entregar`, la tarea del PLC, aceptando el ejemplo (`acepta_el_ejemplo`).
   - Efecto: el ejemplo pasa a ser lo que describe Marcos, una pieza más, con el punto del criterio que
     dice; la entrega está completa. Se guarda la vista previa con su huella, que incluye la de cada
     archivo. La tarea sigue `en_curso`.
   - Confirmación: sí (ADR 0018, decisión 4; constitución §7).
   - La respuesta dice: una pieza por renglón, con lo que cubre cada una en palabras de todos los días:
     su descripción, el ejemplo que aceptó, las dos fotos de hoy y, aparte, lo mandado antes; que al
     confirmar la tarea pasa a revisión, sin nombrar a Ismael; el cierre, aparte: si la entrega así, o si
     saca o corrige algo.
   - La respuesta no dice: que la tarea quedó entregada, en revisión o terminada; que Ismael se enteró;
     que el ejemplo lo escribió o lo contó Marcos (es el que aceptó).
   - Botones: los de la confirmación (constitución §8).
   - Estado después: tema abierto, la entrega del PLC; lo último mostrado para confirmar: la entrega con
     seis piezas.

3. **Marcos** escribe (15:12): "la foto del martes sacala, esa era del cableado viejo"
   →
   - Jugadas: `corregir`, sobre la vista previa: sale la foto del martes.
   - Efecto: la vista previa anterior deja de valer y queda registrada como reemplazada; la nueva, sin la
     foto del martes, con huella nueva. La política sigue completa: la captura la cubre una foto de hoy.
     La foto del martes sigue guardada como parte de la conversación y nunca pasa a evidencia.
   - La respuesta dice: que sacó la foto del martes; cómo queda la entrega, una pieza por renglón; el
     cierre, aparte: si la entrega así.
   - Botones: los de la confirmación, nuevos.
   - Estado después: lo último mostrado para confirmar: la entrega con cinco piezas.

4. **Marcos** toca (15:13) "Confirmar" en la vista previa del paso 2, la vieja.
   →
   - Jugadas: ninguna nueva: el botón es de una vista previa reemplazada (situación general 7).
   - Efecto: ninguno. La tarea sigue `en_curso`; el toque recibe su señal y queda en el registro de
     turnos.
   - La respuesta dice: que esa vista previa fue reemplazada por la que no tiene la foto del martes, que
     sigue esperando su confirmación.
   - La respuesta no dice: que la entregó; nada técnico sobre botones o huellas (constitución §10).
   - Estado después: lo último mostrado para confirmar: la entrega con cinco piezas.

5. **Marcos** manda (15:15) una foto (el tablero cerrado) con el texto: "y esta del tablero cerrado. dale
   mandala"
   →
   - Jugadas: `confirmar` (con la tarea del PLC o sin ella). La foto se suma a la entrega abierta
     (ADR 0019, decisión 4).
   - Efecto: ninguno sobre la tarea. La guarda falla: llegó una pieza después de la vista previa, así que
     lo que Marcos confirma ya no es lo último (ADR 0018, decisión 2; ADR 0019, decisión 5). Se guarda la
     vista previa nueva, con la foto, y huella nueva; la anterior queda registrada como reemplazada. El
     texto de este mensaje no es otra explicación: es la confirmación.
   - La respuesta dice: que sumó la foto del tablero cerrado; cómo queda la entrega, una pieza por renglón;
     el cierre, aparte: que la confirme así.
   - La respuesta no dice: que la entregó; que Ismael se enteró.
   - Botones: los de la confirmación, nuevos.
   - Estado después: lo último mostrado para confirmar: la entrega con seis piezas (el texto, el ejemplo
     que aceptó, tres fotos de hoy y `comprimidora_v3.zip`).

6. **Marcos** escribe (15:16), sin tocar el botón: "dale"
   →
   - Jugadas: `confirmar` (con la tarea del PLC o sin ella). La guarda pasa: es lo último que Marcos
     vio y no cambió.
   - Efecto, en un solo acto: las seis filas de evidencia (el ejemplo aceptado, con lo que describe del
     criterio), cada una con su clase, lo que cubre, quién la
     mandó y cuándo; la tarea del PLC pasa de `en_curso` a `en_revision`, con evento de Marcos y auditoría. Nunca
     `terminada`. El aviso a Ismael queda guardado como hechos y sale terminado el margen para
     corregir, a las 15:26 (ADR 0018, 9n: es un aviso a otra persona por lo que dijo Marcos).
   - La respuesta dice: que quedó entregada y pasa a revisión; el próximo paso: que le avisa cuando la
     revisen o si hace falta algo más (decisiones 11 y 18 del 2026-10-08).
   - La respuesta no dice: el nombre de Ismael (Marcos no lo preguntó); que la tarea está terminada o
     aprobada; que Ismael ya la vio; la foto del martes.
   - Estado después: sin tema abierto, nada mostrado para confirmar.

7. **Marcos** escribe (15:20): "a quien le avisaste?"
   →
   - Jugadas: ninguna. Es una pregunta sobre lo que Leda hizo: se contesta desde los últimos turnos.
   - Efecto: ninguno; el turno queda en el registro.
   - La respuesta dice: que a Ismael, y que le llega hoy a las 15:26, como algo que todavía no pasó. El
     nombre lo tiene la redacción en lo que se dice sólo si la persona lo pregunta (decisión 11 del
     2026-10-08, `odd/tasks/fase-c.md`), y Marcos lo preguntó.
   - La respuesta no dice: que Ismael ya la vio o ya se enteró; que la tarea está terminada o aprobada;
     una pregunta.
   - Estado después: sin tema abierto.

8. **Leda**, por su cuenta, a Ismael (jueves 22, 15:26, terminado el margen para corregir): el aviso de
   la entrega. A Marcos, nada más.
   →
   - Efecto: al salir, el código relee la tarea y la evidencia vigente; la IA redacta desde esos hechos.
     Dos filas de la misma respuesta: el texto y, después, las tres fotos de hoy como álbum (nunca antes
     que el texto). Es un aviso de coordinación: fuera del tope diario (mecánica §10).
   - El mensaje dice: primero, que Marcos entregó; la tarea del PLC en su renglón con 📋; lo que escribió
     Marcos, en pocas palabras (20 ciclos sin una falla); que van tres fotos adjuntas y que
     `comprimidora_v3.zip` está en la página; el cierre, aparte: que puede aprobarla o pedir cambios, con
     los botones o contestando. Al final del texto, un enlace a la página de la tarea, que agrega el
     código: la IA no lo ve ni lo escribe.
   - El mensaje no dice: la foto del martes; que la tarea está terminada; un juicio sobre las fotos; un
     identificador o una huella.
   - El enlace sale sin vista previa, para que Telegram no abra la página por su cuenta; en la base
     queda sólo su hash, y ni la salida ni el registro de turnos lo guardan (ADR 0019, decisión 6).
   - Botones: dos atajos, "Aprobar" y "Pedir cambios" (`odd/tasks/fase-c.md`, decisión 3; ADR 0018,
     decisión 2). "Aprobar" aprueba con un toque, sin confirmación, porque es la decisión de quien
     aprueba; "Pedir cambios" pregunta qué falta. Escribir vale igual: la conversación 23 contesta casi
     todo por escrito y toca "Pedir cambios" una vez.
   - Estado de Ismael después: la entrega del PLC, esperando su decisión; la espera, abierta (la cuenta
     de quien aprueba y no contesta es la conversación 24).

## Qué mide

- **Garantías:** no hace sin confirmación lo que la requiere (ni el botón viejo del paso 4 ni el "dale"
  del paso 5 entregan nada); confirma sólo lo último que la persona vio (el paso 6 entrega exactamente
  seis piezas, sin la foto del martes); "terminé" lleva a revisión, nunca a terminada (constitución
  §11); nada entra a la evidencia sin que Marcos lo vea, ni lo que cubre cada pieza (el texto cuenta como
  explicación y como resultado de la prueba, y la vista previa lo dice); no inventa (el aviso dice lo que mandó Marcos,
  no lo que muestran las fotos); el enlace nunca pasa por la IA.
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA no tome "termine el plc!!" como la entrega, o "la foto del martes
  sacala" como una corrección de la vista previa. Tiene que preguntar; entregar sin vista previa, o
  dejar adentro la foto del martes, es una falla de garantía.
