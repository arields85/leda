# 51. Dejar una entrega sin terminar

**Qué prueba:** Ariel dice que terminó una tarea, a la entrega le falta algo y, antes de completarla,
la deja para más adelante. Lo que dijo para la entrega nunca quedó anotado: es un borrador que espera
lo que falta y su confirmación. Leda no dice que lo anotó; dejarlo todo es dejar sin efecto la
pregunta (cancelar, sin insistir), no corregir algo anotado; no pregunta otra cosa ni repite el
ejemplo, y no lo vuelve a traer después. Cuando Ariel la entrega de verdad, la entrega empieza de
nuevo: lo que dejó no está. Hallazgo de la prueba por Telegram del usuario del 2026-10-12, paso 21
(T7 de `odd/tasks/correcciones-prueba-telegram.md`): la IA eligió corregir sin sacar nada, la cocina
contestó con otra pregunta ("¿qué saco?") y, del borrador, Leda había escrito "✏️ Anoté que
terminaste". ADR 0018, decisión 4 (situaciones generales 3 y 4) y 9d ("dice que lo deja": cancelar,
sin insistir); constitución §4; regla del mozo (`AGENTS.md`, punto 11): primero, que la cocina le
pase el hecho correcto.

**Corre** con su YAML, entera. El paso 2 admite dos lecturas: `cancelar`, la principal, o sacar todo
lo dicho de la entrega y cancelar (`o_bien`). Lo que sólo se ve con la IA real (que no lea "dejalo
pendiente" como corregir) lo miden las pruebas del motor (`tests/motor/test_borrador_no_anotado.py`):
un corregir sin nada que corregir no abre otra pregunta.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tarea de Ariel:** "Integrar datos de la comprimidora en CoreLabs": área CoreLabs; la aprueba
  Ismael; vence el viernes 13/11; `en_curso` desde el miércoles 14; sin bloqueos ni dependencias.
  Criterio de aceptación: "Los datos de la comprimidora se ven en CoreLabs y se actualizan cada
  minuto".
- **Lo que pide la política de CoreLabs en esta conversación:** una explicación (texto) y una captura
  (imagen), para mirar sólo el borrador.
- **Estado de la conversación de Ariel:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Ariel en la semana.

## Hilo

1. **Ariel** escribe (martes 20, 10:00): "termine la integracion de la comprimidora en corelabs"
   →
   - Jugadas: `entregar`, la tarea de CoreLabs. Lo escrito no dice lo que pide el criterio.
   - Efecto: ninguno sobre la tarea, que sigue `en_curso`. Falta la captura y lo que pide el criterio:
     no hay nada para confirmar. Los hechos dicen que la entrega todavía no quedó anotada.
   - La respuesta dice: lo que falta para entregarla (una captura y lo que pide la tarea, con un
     ejemplo sacado del criterio para que lo acepte o lo escriba con sus palabras); el cierre, aparte:
     que mande lo que falta.
   - La respuesta no dice: que quedó anotado o asentado; que la entregó o que está en revisión.
   - Botones: ninguno.
   - Estado después: tema abierto, lo que falta de la entrega de CoreLabs.

2. **Ariel** escribe (10:05): "no mejor dejalo pendiente despues lo hago"
   →
   - Jugadas: `cancelar`: deja todo lo que dijo para la entrega, que nunca quedó anotado. Otra lectura
     válida: sacar lo que escribió de la entrega (`corregir`, con lo que saca) y `cancelar`.
   - Efecto: ninguno sobre la tarea; la pregunta queda sin efecto, sin anotar nada.
   - La respuesta dice: que no quedó nada entregado ni anotado; el cierre, aparte: que le escriba cuando
     la tenga.
   - La respuesta no dice: otra pregunta (qué quiere sacar, si la deja); el ejemplo otra vez; lo que
     falta; un juicio sobre la decisión.
   - Estado después: sin tema abierto, nada para después.

3. **Leda**, a las 14:10 y el miércoles 21 a las 10:00.
   →
   - No le manda nada a Ariel: la entrega que dejó no vuelve, ni como recordatorio ni como pregunta.

4. **Ariel** manda (miércoles 21, 11:00) una captura con el texto: "ya esta ahi va la captura, se ve
   todo en corelabs y se actualiza cada minuto"
   →
   - Jugadas: `entregar`, la tarea de CoreLabs; lo escrito dice el criterio.
   - Efecto: ninguno sobre la tarea todavía. La entrega empieza de nuevo: lo que escribió ayer no
     está. Está completa: se muestra para confirmar.
   - La respuesta dice: la tarea en su renglón con 📋; lo que escribió hoy y la captura, cada una con
     lo que cubre; el cierre, aparte: si la entrega así.
   - La respuesta no dice: lo que escribió ayer; que quedó anotado o asentado.
   - Botones: los de la confirmación.
   - Estado después: lo último mostrado para confirmar: la entrega con dos piezas.

5. **Ariel** escribe (11:01): "dale"
   →
   - Jugadas: `confirmar`.
   - Efecto: las dos piezas de evidencia, lo de hoy, y el paso a `en_revision`, en un solo acto; el
     aviso a Ismael, guardado, sale terminado el margen para corregir.
   - La respuesta dice: que quedó entregada y pasa a revisión, y que le avisa cuando la revisen o si
     hace falta algo más, sin nombrar a Ismael.
   - Estado después: sin tema abierto, nada mostrado para confirmar.

## Qué mide

- **Garantías:** un borrador no se presenta como anotado (constitución §4); dejarlo no anota ni
  entrega nada; lo dejado no se entrega después: la evidencia es sólo lo confirmado (paso 5).
- **El formato:** el de la conversación 20 en cada mensaje.
- **Falla de comprensión:** leer "dejalo pendiente" como `corregir` sin sacar nada o como
  `dejar_para_despues` (la entrega volvería después). Con `corregir` sin nada, la cocina no abre otra
  pregunta: dice que no se anotó nada y la respuesta vuelve a la pregunta abierta.
