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
- **Ya enviado:** nada a Marcos en la semana. Ninguna de las dos vence mañana, así que no hay aviso.

## Hilo

1. **Marcos** escribe (jueves 22, 09:40): "hoy arranque"
   →
   - Jugadas: `anotar_inicio`, sin tarea: el mensaje no la dice y el estado no la sabe.
   - Efecto: ninguno.
   - La respuesta dice: una pregunta por cuál de las dos arrancó.
   - La respuesta no dice: que anotó un inicio; tareas de otras personas.
   - Botones: las dos tareas de Marcos que se pueden arrancar, y sólo ésas (constitución §8: algo con más
     de una lectura; ADR 0013: sólo opciones posibles).
   - Estado después: tema abierto: el inicio, esperando la elección de la tarea.

2. **Marcos** toca "Revisar comunicaciones industriales de la comprimidora".
   →
   - Jugadas: `elegir`, la tarea de comunicaciones; con eso se completa `anotar_inicio`.
   - Efecto: la tarea de comunicaciones pasa a `en_curso` (o se muestra la vista previa, P1). El toque
     recibe su señal y tocarlo otra vez no repite el efecto (ADR 0013, regla 4).
   - La respuesta dice: que quedó anotado (o se va a anotar) el inicio de la tarea de comunicaciones.
   - La respuesta no dice: nada sobre la tarea del PLC.
   - Estado después: sin tema abierto (o, con P1 = b, la vista previa como lo último mostrado).

3. **Marcos** toca "Confirmar" `[sólo si P1 = b]`.
   →
   - Jugadas: `confirmar`, con la guarda de la decisión 2.
   - Efecto: la de comunicaciones en `en_curso`, una sola vez; la del PLC sigue `asignada`.

## Qué mide

- **Garantías (5b):** no inventa; no hace sin confirmación lo que la requiere (P1); no deja sin salida (la
  pregunta trae las opciones); no confunde la tarea: en el paso 1 no se anota nada en ninguna.
- **Falla de comprensión:** que la IA no reconozca "hoy arranque" como un inicio. Tiene que seguir siendo
  una pregunta; elegir una tarea por su cuenta es una falla de garantía, no de comprensión.
