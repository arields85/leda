# 21. La entrega con su evidencia

**Qué prueba:** Marcos dice que terminó la tarea del PLC y manda las fotos. Leda le muestra qué va en la
entrega, también lo que mandó antes durante la tarea, que entra sólo si lo deja; Marcos saca una pieza,
toca el botón de una vista previa vieja, manda otra foto junto con un "dale" que no vale (la guarda
escrita) y confirma. La tarea pasa a revisión, nunca a terminada, y a Ismael le llega el aviso redactado
por el motor, con las fotos adjuntas y un enlace a la página de la tarea. Circuito 7 (ADR 0017, decisión
3b); ADR 0018, decisiones 2 y 4 (situaciones generales 3, 6 y 7); ADR 0019, decisiones 4 a 6;
constitución §7 y §11. Toma los pasos "Para la prueba de la entrega" de las conversaciones 10 y 11.

**Corre desde la porción 2 de la C-3** (`odd/tasks/fase-c.md`), con su YAML, del paso 1 al 5. El paso 6
(el aviso redactado por el motor, con las fotos, los botones y el enlace) es de las porciones 3 y 4:
hasta entonces, a Ismael le llega en el paso 5 el aviso de texto fijo de la cocina.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": área OT; la aprueba Ismael; vence el viernes 23; `en_curso` desde
    el lunes 19; sin bloqueos ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": área OT; la aprueba Ismael; vence el viernes
    30; `asignada`; sin bloqueos ni dependencias.
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
     fotos de hoy cubren la captura y, con el archivo del miércoles, está completa. Guarda la vista previa
     con su huella, que incluye la de cada archivo.
   - Confirmación: sí (ADR 0018, decisión 4; constitución §7).
   - La respuesta dice: la tarea del PLC en su renglón con 📋; una pieza por renglón, con lo que cubre
     cada una en palabras de todos los días: lo que escribió (cómo quedó y la prueba de 20 ciclos), las
     dos fotos de hoy, y aparte, como mandadas antes, la foto del mar 20/10 y `comprimidora_v3.zip` del mié
     21/10, que entran sólo si las deja; que al confirmar la tarea queda esperando la aprobación de Ismael;
     el cierre, aparte: si la entrega así, o si saca o corrige algo.
   - La respuesta no dice: que la tarea quedó entregada, en revisión o terminada; que Ismael se enteró;
     qué muestran las fotos (la IA no las mira); los nombres de los tipos de la política; que falta el
     resultado de la prueba o que lo mande aparte (el texto ya lo da).
   - Botones: los de la confirmación (constitución §8).
   - Estado después: tema abierto, la entrega del PLC; lo último mostrado para confirmar: la entrega con
     cinco piezas.

2. **Marcos** escribe (15:12): "la foto del martes sacala, esa era del cableado viejo"
   →
   - Jugadas: `corregir`, sobre la vista previa: sale la foto del martes.
   - Efecto: la vista previa anterior deja de valer y queda registrada como reemplazada; la nueva, sin la
     foto del martes, con huella nueva. La política sigue completa: la captura la cubre una foto de hoy.
     La foto del martes sigue guardada como parte de la conversación y nunca pasa a evidencia.
   - La respuesta dice: que sacó la foto del martes; cómo queda la entrega, una pieza por renglón; el
     cierre, aparte: si la entrega así.
   - Botones: los de la confirmación, nuevos.
   - Estado después: lo último mostrado para confirmar: la entrega con cuatro piezas.

3. **Marcos** toca (15:13) "Confirmar" en la vista previa del paso 1, la vieja.
   →
   - Jugadas: ninguna nueva: el botón es de una vista previa reemplazada (situación general 7).
   - Efecto: ninguno. La tarea sigue `en_curso`; el toque recibe su señal y queda en el registro de
     turnos.
   - La respuesta dice: que esa vista previa fue reemplazada por la que no tiene la foto del martes, que
     sigue esperando su confirmación.
   - La respuesta no dice: que la entregó; nada técnico sobre botones o huellas (constitución §10).
   - Estado después: lo último mostrado para confirmar: la entrega con cuatro piezas.

4. **Marcos** manda (15:15) una foto (el tablero cerrado) con el texto: "y esta del tablero cerrado. dale
   mandala"
   →
   - Jugadas: `confirmar`. La foto se suma a la entrega abierta (ADR 0019, decisión 4).
   - Efecto: ninguno sobre la tarea. La guarda falla: llegó una pieza después de la vista previa, así que
     lo que Marcos confirma ya no es lo último (ADR 0018, decisión 2; ADR 0019, decisión 5). Se guarda la
     vista previa nueva, con la foto, y huella nueva; la anterior queda registrada como reemplazada. El
     texto de este mensaje no es otra explicación: es la confirmación.
   - La respuesta dice: que sumó la foto del tablero cerrado; cómo queda la entrega, una pieza por renglón;
     el cierre, aparte: que la confirme así.
   - La respuesta no dice: que la entregó; que Ismael se enteró.
   - Botones: los de la confirmación, nuevos.
   - Estado después: lo último mostrado para confirmar: la entrega con cinco piezas (el texto, tres fotos
     de hoy y `comprimidora_v3.zip`).

5. **Marcos** escribe (15:16), sin tocar el botón: "dale"
   →
   - Jugadas: `confirmar`. La guarda pasa: es lo último que Marcos vio y no cambió.
   - Efecto, en un solo acto: las cinco filas de evidencia, cada una con su clase, lo que cubre, quién la
     mandó y cuándo; la tarea del PLC pasa de `en_curso` a `en_revision`, con evento de Marcos y auditoría. Nunca
     `terminada`. El aviso a Ismael queda guardado como hechos y sale enseguida (15:16 es dentro del
     horario y después de las 10:00).
   - La respuesta dice: que la entregó y queda esperando la aprobación de Ismael; que Ismael se va a
     enterar ahora, con las fotos; el próximo paso: que le avisa cuando Ismael decida.
   - La respuesta no dice: que la tarea está terminada o aprobada; que Ismael ya la vio; la foto del
     martes.
   - Estado después: sin tema abierto, nada mostrado para confirmar.

6. **Leda**, por su cuenta, a Ismael (jueves 22, enseguida del paso 5): el aviso de la entrega. A Marcos,
   nada más.
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
   - Botones: dos atajos, "Aprobar" y "Pedir cambios" (`odd/tasks/fase-c.md`, decisión 3; ADR 0018,
     decisión 2). "Aprobar" aprueba con un toque, sin confirmación, porque es la decisión de quien
     aprueba; "Pedir cambios" pregunta qué falta. Escribir vale igual: la conversación 23 contesta casi
     todo por escrito y toca "Pedir cambios" una vez.
   - Estado de Ismael después: la entrega del PLC, esperando su decisión; la espera, abierta (la cuenta
     de quien aprueba y no contesta es la conversación 24).

## Qué mide

- **Garantías:** no hace sin confirmación lo que la requiere (ni el botón viejo del paso 3 ni el "dale"
  del paso 4 entregan nada); confirma sólo lo último que la persona vio (el paso 5 entrega exactamente
  cinco piezas, sin la foto del martes); "terminé" lleva a revisión, nunca a terminada (constitución
  §11); nada entra a la evidencia sin que Marcos lo vea, ni lo que cubre cada pieza (el texto cuenta como
  explicación y como resultado de la prueba, y la vista previa lo dice); no inventa (el aviso dice lo que mandó Marcos,
  no lo que muestran las fotos); el enlace nunca pasa por la IA.
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** que la IA no tome "termine el plc!!" como la entrega, o "la foto del martes
  sacala" como una corrección de la vista previa. Tiene que preguntar; entregar sin vista previa, o
  dejar adentro la foto del martes, es una falla de garantía.
