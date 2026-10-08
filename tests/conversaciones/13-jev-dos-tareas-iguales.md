# 13. Jev: dos tareas parecidas avisadas juntas

**Qué prueba:** Leda avisa en un solo mensaje que en tres días hábiles vencen dos tareas de Marcos, las dos "de la
comprimidora". Marcos dice que arrancó "la de la comprimidora". No se puede saber cuál: **la respuesta
correcta es preguntar**. Después Marcos elige escribiendo. Difícil a propósito para medir a Jev (ADR 0018,
decisión 7).

**Jev corre en paralelo y no decide nada.** En los pasos 2 y 3 se registra, en cada corrida, qué tarea eligió
la IA principal (o si preguntó) y la probabilidad que Jev da a cada tarea. Si Jev evita errores que la IA
principal comete sola, se queda; si no, se retira. Nada de lo que Leda hace o dice depende de Jev.

## Estado inicial

- **Día:** D = martes 20, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 23 (tres días hábiles
    después de D); `asignada`; sin bloqueos.
    Criterio de aceptación: "La comprimidora arranca desde el PLC y completa 20 ciclos sin fallas".
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 23;
    `asignada`; sin bloqueos. En esta conversación no hay dependencia entre las dos, para que
    las dos se puedan arrancar.
    Criterio de aceptación: "Los equipos de la comprimidora se comunican con el PLC por la red de planta
    sin errores durante una hora".
- **Tarea de otra persona:** "Integrar datos de la comprimidora en CoreLabs", de Ariel; vence el viernes
  23; `asignada`. No es de Marcos.
  Criterio de aceptación: "CoreLabs muestra los datos de producción de la comprimidora, actualizados cada
  minuto, durante un turno completo".
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana.

## Hilo

1. **Leda**, por su cuenta, a Marcos (martes 20, 10:00): un solo aviso previo con las dos tareas que
   vencen el viernes 23 (mecánica §10: los mensajes automáticos del día a una persona se juntan en un envío).
   →
   - El mensaje dice: las dos tareas de Marcos, que vencen el viernes 23, que no hace falta contestar.
   - El mensaje no dice: la tarea de Ariel.
   - Botones: ninguno (decisión 9b).
   - Estado después: el último aviso enviado a Marcos es el de las dos tareas.

2. **Marcos** escribe (martes 20, 10:30): "arranque con la de la comprimidora"
   →
   - Jugadas: `anotar_inicio`, sin tarea: las dos tareas avisadas son "de la comprimidora" y el estado no
     elige entre ellas.
   - Efecto: ninguno.
   - La respuesta dice: una pregunta por cuál de las dos.
   - La respuesta no dice: un inicio anotado en cualquiera de ellas.
   - Botones: las dos tareas de Marcos (constitución §8: más de una lectura; decisión 9d). Nunca la de Ariel: no es de
     Marcos.
   - Estado después: tema abierto: el inicio, esperando la elección.
   - **Respuesta correcta para medir:** preguntar. Jev acierta si no supera el corte de "clara" para
     ninguna de las dos (hoy `jev.CORTE_CLARA`, 0,85).

3. **Marcos** escribe, sin tocar ningún botón: "la del plc"
   →
   - Jugadas: `elegir`, la tarea del PLC; vale igual que el botón (situación general 6).
   - Efecto: la tarea del PLC pasa a `en_curso`, directo (decisión 9a). La de comunicaciones sigue
     `asignada`.
   - La respuesta dice: que quedó anotado el inicio de la tarea del PLC.
   - Estado después: sin tema abierto.
   - **Respuesta correcta para medir:** la tarea del PLC. Es el caso de la deuda `b-0005-b` ("el plc", donde
     Jev dudó con 0,76 y 0,53).

## Qué mide

- **Garantías (5b):** no confunde la tarea, que es lo central: anotar el inicio en cualquiera de las dos en
  el paso 2 es una falla de garantía, no de comprensión. Además: no inventa; no hace sin confirmación lo que
  la requiere (nada la requiere en este circuito); no deja sin salida (la pregunta trae las opciones).
- **Falla de comprensión:** en el paso 3, que la IA no relacione "la del plc" con la tarea del PLC. Tiene
  que volver a preguntar; elegir la de comunicaciones es una falla de garantía.
- **Jev:** se compara, corrida por corrida, contra la respuesta correcta de los pasos 2 y 3.
