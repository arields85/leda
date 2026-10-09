# 41. El informe al grupo

**Qué prueba:** con las cadencias al grupo del pack (miércoles y viernes), Leda le manda al grupo del
equipo lo que pasó con las tareas, cada renglón con el nombre de quien la tiene: las terminadas, los
atrasos ya hablados en privado (con el día en que vencían, el día que dio la persona y su motivo), las
trabadas con lo que las traba y las que siguen. Un atraso que la persona todavía no habló con Leda no
aparece como atraso; mientras no contesta, se dice que no se sabe cómo viene; cuando quedó asentado
porque no contestó, figura como atraso. Lo que sigue igual se repite. El informe sale siempre: sin nada
malo, dice que está todo en orden, y una semana buena se reconoce, sin comparar personas. Decisiones 25,
54 y 55 del usuario (`odd/tasks/fase-c.md`, 2026-10-09), sobre la decisión 8 (el informe al grupo de la
C-6) y las decisiones 35 y 49 (lo asentado figura en el informe); constitución §4 (honestidad) y §8 (los
atrasos, primero en privado); ADR 0021, reglas 1 a 3.

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
   que Leda manda lo suyo.
5. **Lo que sigue igual se repite** (decisión 54, opción A): "PLC: sigue demorada, falta que llegue el
   cable"; "no es exponer, es informar", y nadie tiene que adivinar qué pasó con ese tema. Las listas a
   cada persona preguntan; el informe al grupo sólo informa. Cada cuánto sale, en la plataforma.
6. **El informe sale siempre** (decisión 55), también como señal de que Leda funciona: sin nada malo,
   dice que está todo en orden, sólo si los hechos lo prueban; lo que Leda no sabe lo dice como no
   sabido (quien no contestó no está "bien" ni "atrasado"); cuenta lo que se terminó y quién lo hizo; y
   si la semana fue buena por reglas fijas del código, lo reconoce, breve y sin exagerar. Nunca compara
   personas ni arma rankings: "es un equipo, no una competencia".

Cómo se leyó lo que la regla no dice (decidido por el coordinador a partir de las decisiones 8, 25, 35 y
49; `odd/tasks/fase-c.md`, C-6):

- **Hablado en privado** es que la persona le dio a Leda un día posterior al vencimiento (su previsión),
  o que quedó asentado porque no contestó (el escalamiento por falta de respuesta salió). Mientras
  Leda le pregunta y no contesta (desde otro día), la tarea figura como algo que no se sabe cómo viene,
  sin el día en que vencía: ni bien ni atrasada (decisión 55). Lo preguntado hoy sigue su curso.
- **Todo en orden** lo decide el código: ningún atraso, ninguna trabada, nada que no se sepa y ningún
  atraso que la persona todavía no habló. **La semana buena**, también: además, desde el informe
  anterior nadie dio un día posterior al vencimiento, lo que vencía está entregado sin que Leda haya
  tenido que preguntar por ello ya vencido, y algo se terminó o se entregó.
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
     llegue el cable; trabado, el tablero (Lucas), esperando el repuesto, desde el lunes 26; de la
     integración (Ariel), que no se sabe cómo viene (no contestó desde el lunes); sigue, la medición
     de los sensores (Nahuel), que vence el viernes 6.
   - El mensaje no dice: que la integración de Ariel está atrasada, ni el día en que vencía (todavía
     no habló de su atraso); que está todo en orden; un reproche; a quién se le avisó.

6. **Leda**, por su cuenta (jueves 29, 10:00): a Marcos, el pedido de estado del PLC (el día que dio);
   a Ismael, que la integración de Ariel sigue sin novedades (quedó asentado).

7. **Leda**, por su cuenta (viernes 30, 10:00 y 16:15): a las 10:00, a Marcos, el segundo pedido del
   PLC; a las 16:15, a Marcos, esa pregunta repetida una vez (las 4 horas), y el informe al grupo.
   →
   - Efecto: un mensaje al grupo: atrasadas, la integración (Ariel), que vencía el viernes 23 (quedó
     asentado; sin un día que nadie dio), y el PLC (Marcos), con el día que dio y su motivo, otra vez
     (sigue igual, decisión 54); trabado, el tablero (Lucas); sigue, la medición de los sensores
     (Nahuel). El panel HMI no vuelve a aparecer: se terminó antes del informe anterior.

8. **Lucas** escribe (lunes 2 de noviembre, 09:20): "ya llego el repuesto, sigo con el tablero"
   →
   - Jugadas: `destrabar` sobre el tablero.
   - Efecto: el bloqueo resuelto; el tablero vuelve a como estaba antes (asignada).

9. **Marcos** escribe (lunes 2, 09:30): "termine el plc, arranca desde el plc y completo los 20 ciclos
   sin fallas"
   →
   - Jugadas: `entregar` el PLC, con lo descrito cubriendo su criterio.
   - La respuesta muestra la entrega y su botón Confirmar.

10. **Marcos** toca Confirmar (lunes 2, 09:31)
    →
    - Efecto: el PLC en revisión, con su descripción; el aviso a Ismael, guardado.
    - La entrega contesta la pregunta de cómo venía el PLC: no vuelve a preguntarla.

11. **Ariel** escribe (lunes 2, 09:35): "termine la integracion, corelabs muestra los datos de
    produccion de la comprimidora actualizados cada minuto" → `entregar` la integración, con su botón.

12. **Ariel** toca Confirmar (lunes 2, 09:36) → la integración en revisión; el aviso a Ismael,
    guardado; la pregunta de cómo venía, contestada.

13. **Leda**, por su cuenta (lunes 2 al miércoles 4): a Ismael, las dos entregas para revisar y sus
    recordatorios; a Nahuel, el aviso previo de los sensores; el miércoles a las 15:30, el informe al
    grupo.
    →
    - Efecto: un mensaje al grupo: entregadas, la integración (Ariel) y el PLC (Marcos), esperando la
      revisión; siguen, los sensores (Nahuel) y el tablero (Lucas); está todo en orden; y la semana
      fue buena (nada atrasado de nuevo, lo que vencía entregado a tiempo, algo entregado).
    - El mensaje dice: que está todo en orden y un reconocimiento breve al equipo, sin exagerar.
    - El mensaje no dice: una comparación entre personas, un ranking o cuántas hizo cada uno; un
      atraso; una pregunta.

14. **Leda**, por su cuenta (jueves 5 y viernes 6): a Ismael, los recordatorios; a Nahuel, el pedido de
    estado de los sensores (vencen hoy) y su repetición; el viernes a las 16:15, el informe al grupo.
    →
    - Efecto: un mensaje al grupo: lo mismo que sigue igual y que está todo en orden. Los sensores,
      preguntados hoy, siguen su curso.
    - El mensaje no dice: un reconocimiento por la semana (desde el miércoles no se terminó ni se
      entregó nada: sin exagerar); una comparación entre personas.

## Qué mide

- **Garantías (5b):** el informe va al grupo del espacio y a ningún otro chat; cada renglón con el
  nombre de quien tiene la tarea; un atraso, sólo después de hablado en privado o asentado; lo que no
  se sabe, como no sabido; ninguna fecha que nadie dio; no pide respuesta; las terminadas, sólo las de
  después del informe anterior; todo en orden y la semana buena, sólo cuando el código lo comprobó;
  ningún conteo ni comparación por persona.
- **Falla de comprensión:** que la IA tome el motivo de Marcos como otra cosa, o que lo diga como un
  reproche; que diga como atraso lo que no se sabe; que exagere el reconocimiento o nombre a alguien
  frente a otro.
