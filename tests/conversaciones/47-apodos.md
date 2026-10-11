# 47. Los apodos: Leda los aprende por chat, una persona puede tener varios y uno puede ser de dos

**Qué prueba:** el [ADR 0020](../../docs/decisions/0020-apodos.md), aceptado por el usuario el
2026-10-11. Cuando alguien nombra a una persona por un apodo que Leda no conoce, Leda pregunta quién es,
confirma con nombre y apellido y recién entonces aprende el apodo; la jugada sigue como si la hubieran
nombrado por su nombre. El apodo vale para todo el espacio, una persona puede tener varios, uno de dos
personas se aclara con nombre y apellido, y Leda nunca usa el apodo para nombrar a nadie. Constitución §4
(no inventa una identidad), §5 (la confirmación es de una persona), §8 (trato) y §13 (aislamiento);
mecánica §14 (aprendizaje).

**Estado:** construida (pasos 1 a 11): corre en seco con su YAML (`47-apodos.yaml`); falta la ronda
con la IA real. El tramo "Por decidir con el usuario" no se construyó.

## Las reglas

1. **Un apodo que Leda no conoce se pregunta.** Nada se anota todavía: Leda pregunta quién es, la
   persona contesta con un nombre y Leda confirma con nombre y apellido. Con la confirmación aprende el
   apodo y hace lo que se le había pedido.
2. **El apodo es del espacio.** Lo que enseñó Nahuel lo entiende Leda cuando lo dice Lucas, sin volver a
   preguntar.
3. **Una persona puede tener varios.** Aprender "el Chino" para Mariano no le borra "el Tano".
4. **Uno de dos personas se aclara con nombre y apellido**, con un botón por persona; Leda nunca elige.
5. **El apodo sirve para entender, no para hablar.** Las respuestas y los avisos nombran a Mariano por su
   nombre, nunca "el Tano".
6. **Cada apodo aprendido queda auditado** con quién lo enseñó y cuándo.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Personas:** las de CoreWork. Marcos es el encargado de OT y Nahuel es de OT; Martín es el encargado
  de Infraestructura IT y Lucas es de IT; Mariano es el encargado de Electricidad. Todos tienen un chat
  con Leda. Ningún apodo aprendido.
- **Tareas:** de Nahuel, "Programar el PLC de la envasadora", `en_curso`; de Lucas, "Armar el rack del
  servidor", `en_curso`, y "Configurar el switch de la planta", `en_curso`. Vencen el viernes 6 de
  noviembre.
- **Estado de la conversación de cada uno:** sin tema abierto, nada para después.

## Hilo

### Un apodo nuevo (reglas 1, 5 y 6)

1. **Nahuel** escribe (martes 20, 10:00): "el plc esta trabado, me falta el plano del tablero y me lo
   tiene que pasar el tano"
   →
   - Jugadas: `anotar_bloqueo` sobre el PLC, con la causa, y `anotar_quien_destraba` con quién lo
     destraba como lo nombró ("el tano").
   - Efecto: el bloqueo del PLC queda anotado con su causa; quién lo destraba, todavía no: "el
     tano" no es nadie del equipo ni un apodo aprendido.
   - La respuesta dice: que no tiene a nadie como "el Tano" en el equipo y le pregunta quién es.
   - Estado después: la pregunta de quién es "el tano", con el pedido de Nahuel guardado; la de
     quién lo destraba queda para después (la de quién es la precisa).

2. **Nahuel** escribe (10:01): "mariano"
   →
   - Jugadas: `decir_quien_es`, Mariano.
   - Efecto: ninguno todavía.
   - La respuesta dice: "¿«El Tano» es Mariano Naim?", para confirmar.
   - Botones: Confirmar.

3. **Nahuel** toca Confirmar (10:01)
   →
   - Efecto: el apodo "el tano" queda aprendido para Mariano, en el espacio, auditado con Nahuel como
     quien lo enseñó; el bloqueo del PLC queda anotado con Mariano como quien lo destraba, y la pregunta a
     Mariano se guarda (sale terminado el margen para corregir).
   - La respuesta dice: que el PLC quedó trabado esperando el plano de Mariano y que le va a preguntar.
   - La respuesta no dice: "el Tano" para nombrar a Mariano.

4. **Leda**, por su cuenta, a Mariano (10:11): lo que le falta a Nahuel para el PLC y para cuándo lo
   puede pasar. Lo nombra a Nahuel por su nombre; no menciona el apodo.

### El apodo vale para todo el espacio (regla 2)

5. **Lucas** escribe (11:00): "lo del rack esta trabado, el tano me tiene q pasar la medida del tablero"
   →
   - Jugadas: `avisar_bloqueo` sobre el rack, quién lo destraba como lo nombró ("el tano").
   - Efecto: el bloqueo queda anotado con Mariano como quien lo destraba, sin preguntar; la pregunta a
     Mariano se guarda.
   - La respuesta dice: que el rack quedó trabado esperando a Mariano.

### Varios apodos para la misma persona (regla 3)

6. **Lucas** escribe (11:30): "y lo del switch tambien, me falta que el chino me habilite el tablero"
   →
   - Igual que el paso 1, con "el chino": Leda pregunta quién es.

7. **Lucas** escribe (11:31): "mariano tambien" → la confirmación "¿«El Chino» es Mariano Naim?".

8. **Lucas** toca Confirmar → "el chino" queda aprendido para Mariano, y "el tano" sigue siendo de él;
   el bloqueo del switch queda anotado con Mariano.

### Un apodo de dos personas (regla 4)

9. **Estado previo del tramo:** "el flaco" está aprendido para Martín y para Marcos (cargado por la
   plataforma; ADR 0020, decisión 4).

10. **Nahuel** escribe (martes 20, 15:00): "la del plc ya no esta trabada por el plano, ahora me falta
    que el flaco me de acceso a la red"
    →
    - Jugadas: `destrabar` el PLC (ya no es el plano), `anotar_bloqueo` con la causa nueva y
      `anotar_quien_destraba` con "el flaco".
    - Efecto: el bloqueo del plano se cierra (a Mariano le llega que ya no hace falta) y el nuevo
      queda anotado; quién lo destraba, todavía no.
    - La respuesta dice: "¿«El Flaco» es Martín Forte o Marcos Tarquini?".
    - Botones: uno por persona, con nombre y apellido (Marcos Tarquini, Martín Forte).

11. **Nahuel** toca Martín Forte → quien destraba pasa a ser Martín; ningún apodo cambia.

## Por decidir con el usuario

- **Corregir un apodo que ya tiene dueño.** Si "el flaco" es Martín y alguien dice "no, el flaco es
  Marcos", ¿Leda lo cambia, o pregunta si a los dos les dicen así? Propuesta del agente: preguntar con
  dos botones, "A los dos" y "Sólo a Marcos Tarquini". Hasta que el usuario lo decida, este tramo no se
  escribe ni se construye.
