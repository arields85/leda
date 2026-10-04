# 09. Duda: ¿de qué tarea habla?

**Qué prueba:** Marcos escribe sin que haya un aviso reciente que diga de qué tarea habla, y tiene dos que
podrían ser. Leda no adivina: pregunta con las tareas posibles como opciones, y anota en la elegida. ADR
0018, decisión 4, situación general 5.

## Estado inicial

- **Día:** D = jueves 22, dentro del horario.
- **Tareas de Marcos:**
  - "Programar PLC de la comprimidora": referente Ismael; vence el viernes 30; `asignada`; sin bloqueos
    ni dependencias.
  - "Revisar comunicaciones industriales de la comprimidora": referente Ismael; vence el viernes 30;
    `asignada`; sin bloqueos ni dependencias.
- **Estado de la conversación de Marcos:** sin tema abierto, nada para después, nada mostrado para
  confirmar.
- **Ya enviado:** nada a Marcos en la semana. El aviso previo de las dos sale recién el martes 27 (tres días
  hábiles antes del viernes 30), así que no hay aviso que diga de qué tarea habla.

## Hilo

1. **Marcos** escribe (jueves 22, 09:40): "hoy arranque"
   →
   - Jugadas: `anotar_inicio`, sin tarea: el mensaje no la dice y el estado no la sabe.
   - Efecto: ninguno.
   - La respuesta dice: una pregunta por cuál de las dos arrancó.
   - La respuesta no dice: que anotó un inicio; tareas de otras personas.
   - Botones: las dos tareas de Marcos que se pueden arrancar, y sólo ésas (constitución §8: algo con más
     de una lectura; ADR 0013: sólo opciones posibles; decisión 9d: los únicos botones de la prueba chica).
   - Estado después: tema abierto: el inicio, esperando la elección de la tarea.

2. **Marcos** toca "Revisar comunicaciones industriales de la comprimidora".
   →
   - Jugadas: `elegir`, la tarea de comunicaciones; con eso se completa `anotar_inicio`.
   - Efecto: la tarea de comunicaciones pasa a `en_curso`, directo (decisión 9a), con evento de Marcos y
     auditoría; la del PLC sigue `asignada`. El toque recibe su señal y tocarlo otra vez no repite el efecto
     (ADR 0013, regla 4).
   - La respuesta dice: que quedó anotado el inicio de la tarea de comunicaciones.
   - La respuesta no dice: nada sobre la tarea del PLC.
   - Estado después: sin tema abierto.

## Qué mide

- **Garantías (5b):** no inventa; no hace sin confirmación lo que la requiere (nada la requiere en este
  circuito); no deja sin salida (la pregunta trae las opciones); no confunde la tarea: en el paso 1 no se anota nada en ninguna.
- **Falla de comprensión:** que la IA no reconozca "hoy arranque" como un inicio. Tiene que seguir siendo
  una pregunta; elegir una tarea por su cuenta es una falla de garantía, no de comprensión.
