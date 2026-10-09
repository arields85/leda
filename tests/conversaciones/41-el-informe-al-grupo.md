# 41. El informe al grupo

**Qué prueba:** con las cadencias al grupo del pack (miércoles y viernes), Leda le manda al grupo del
equipo lo que pasó con las tareas, cada renglón con el nombre de quien la tiene: las terminadas, los
atrasos ya hablados en privado (con el día en que vencían, el día que dio la persona y su motivo), las
trabadas con lo que las traba y las que siguen. Un atraso que la persona todavía no habló con Leda no
aparece; cuando quedó asentado porque no contestó, sí. Decisión 25 del usuario (`odd/tasks/fase-c.md`,
2026-10-09, opción A), sobre la decisión 8 (el informe al grupo de la C-6) y las decisiones 35 y 49 (lo
asentado figura en el informe); constitución §8 (los atrasos, primero en privado).

**Corre desde la C-6** (`odd/tasks/fase-c.md`, el informe al grupo), entera, con su YAML.

## La regla (decidida por el usuario, 2026-10-09)

1. **Los atrasos en el informe al grupo** (decisión 25): un atraso ya hablado en privado aparece con el
   nombre y el motivo que dio la persona, como información, nunca como acusación ("• PLC (Marcos):
   vencía el lun 26/10, la termina el jue 29/10 (falta que llegue el cable)"). Todas las líneas llevan
   nombre. El porqué, del usuario: el grupo puede ayudar (Lucas lee que a Marcos le falta el cable, y
   él tiene uno de más).
2. **Primero en privado** (constitución §8; decisión 8): un atraso que la persona todavía no habló no
   figura.
3. **Lo asentado figura** (decisiones 35 y 49): cuando a la persona se le dijo que va a quedar asentado
   que la tarea está atrasada, "para que el equipo esté al tanto", el informe siguiente lo dice.
4. **Una sola hora de salida** (decisión 45): la cadencia sale a su hora o, si es antes, a la hora en
   que Leda manda lo suyo. Sin nada que informar, no sale nada.

Cómo se leyó lo que la regla no dice (decidido por el coordinador a partir de las decisiones 8, 25, 35 y
49; `odd/tasks/fase-c.md`, C-6):

- **Hablado en privado** es que la persona le dio a Leda un día posterior al vencimiento (su previsión),
  o que quedó asentado porque no contestó (el escalamiento por falta de respuesta salió). Mientras
  Leda le pregunta y no contesta, la tarea no figura en ninguna parte del informe.
- **Las terminadas** son las de después del informe anterior (el primero, desde el lunes).
- **Las dos cadencias al grupo llevan el mismo informe**; Leda no conversa en el grupo: el informe no
  pide respuesta.

## Estado inicial

- **Día:** D = lunes 26 de octubre, 09:00, dentro del horario.
- **El grupo del espacio**, con las dos cadencias al grupo del pack: miércoles 15:30
  (`resumen_grupal`) y viernes 16:15 (`informe_semanal`). Las de cada integrante en privado se suponen
  apagadas.
- **Tareas:**
  - "Programar PLC de la comprimidora", de Marcos: vence el lunes 26; `en_curso` desde el lunes 19.
  - "Integrar datos de la comprimidora en CoreLabs", de Ariel: venció el viernes 23; `en_curso` desde
    el lunes 19. Nadie le preguntó todavía.
  - "Cablear el tablero de la línea 2", de Lucas: vence el viernes 13 de noviembre; `bloqueada` desde
    el lunes 26, esperando el repuesto.
  - "Instalar el panel HMI de la comprimidora", de Nahuel: `terminada` (aprobada por Marcos) el lunes
    26.
  - "Medir los sensores de la comprimidora", de Nahuel: vence el viernes 6 de noviembre; `en_curso`
    desde el lunes 19.
- **Estado de la conversación** de cada persona: sin tema abierto, nada para después.
- **Ya enviado:** nada.

## Hilo

1. **Leda**, por su cuenta (lunes 26, 10:00): a Marcos, el pedido de estado del PLC (vence hoy); a
   Ariel, el de la integración (venció el viernes).

2. **Marcos** escribe (lunes 26, 10:30): "el plc lo termino el jueves, falta que llegue el cable"
   →
   - Jugadas: `anotar_prevision` sobre el PLC, con el jueves 29 y el motivo "falta que llegue el
     cable".
   - Efecto: la previsión anotada; el aviso a Ismael, guardado para después del margen.
   - La respuesta dice: lo anotado, el día que dio y que el seguimiento pasa a ese día.

3. **Leda**, por su cuenta (lunes 26, 10:40): a Ismael, la previsión del PLC.

4. **Leda**, por su cuenta (martes 27, 10:00): a Ariel, el segundo pedido de estado.

5. **Leda**, por su cuenta (miércoles 28, 10:00 y 15:30): a las 10:00, a Ariel, el tercer pedido, que
   avisa que si sigue igual va a quedar asentado; a las 15:30, a Ariel, esa pregunta repetida una vez
   (las 4 horas, decisión 29), y el informe al grupo.
   →
   - Efecto: un mensaje al grupo del espacio, que no pide respuesta: terminada, el panel HMI (Nahuel);
     atrasado, el PLC (Marcos), que vencía el lunes 26 y él termina el jueves 29 porque falta que
     llegue el cable; trabado, el tablero (Lucas), esperando el repuesto, desde el lunes 26; sigue, la
     medición de los sensores (Nahuel), que vence el viernes 6.
   - El mensaje no dice: nada de la integración de Ariel (todavía no habló de su atraso); un reproche;
     a quién se le avisó.

6. **Leda**, por su cuenta (jueves 29, 10:00): a Marcos, el pedido de estado del PLC (el día que dio);
   a Ismael, que la integración de Ariel sigue sin novedades (quedó asentado).

7. **Leda**, por su cuenta (viernes 30, 10:00 y 16:15): a las 10:00, a Marcos, el segundo pedido del
   PLC; a las 16:15, a Marcos, esa pregunta repetida una vez (las 4 horas), y el informe al grupo.
   →
   - Efecto: un mensaje al grupo: atrasadas, la integración (Ariel), que vencía el viernes 23 (quedó
     asentado; sin un día que nadie dio), y el PLC (Marcos), con el día que dio y su motivo; trabado, el
     tablero (Lucas); sigue, la medición de los sensores (Nahuel). El panel HMI no vuelve a aparecer:
     se terminó antes del informe anterior.

## Qué mide

- **Garantías (5b):** el informe va al grupo del espacio y a ningún otro chat; cada renglón con el
  nombre de quien tiene la tarea; un atraso, sólo después de hablado en privado o asentado; ninguna
  fecha que nadie dio; no pide respuesta; las terminadas, sólo las de después del informe anterior.
- **Falla de comprensión:** que la IA tome el motivo de Marcos como otra cosa, o que lo diga como un
  reproche.
