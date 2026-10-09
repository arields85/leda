# Guion de la prueba por Telegram: la entrega y la revisión (Fase C, parte 1)

Para el usuario, que opera las tres cuentas de prueba: Ariel, Ismael y Marcos. Mide con la IA real lo
que la regresión automática no ve: la entrega contra el criterio, la lista de lo que hay para
revisar, la decisión, la espera de 30 minutos y el enlace a la página de la tarea. Datos ficticios,
base `leda_motor` (recreada el 2026-10-08 para esta prueba; respaldo previo en
`db/respaldos/leda_motor-antes-fase-c-d6-20261008.dump`).

**Las tareas de la prueba** (vencen el viernes 16/10):

- Marcos: "Programar PLC de la comprimidora", todavía sin arrancar. Para aprobarla: "La comprimidora
  arranca desde el PLC y completa 20 ciclos sin fallas", y lleva una foto o captura.
- Marcos: "Revisar comunicaciones industriales de la comprimidora", en curso (espera al PLC).
- Ariel: "Dashboard de lotes en CoreLabs", en curso. Para aprobarla: "El dashboard muestra los lotes
  del día con su cantidad y su estado, y coinciden con el registro de producción", y lleva una foto o
  captura.
- Ariel: "Integrar datos de la comprimidora en CoreLabs", todavía sin arrancar.
- Las dos de Marcos y las dos de Ariel las revisa Ismael.

## Antes de empezar

Tres terminales de PowerShell. En cada una, primero pegá esto y Enter:

```
cd D:\Proyectos\Leda-PM-worktrees\motor-de-conversacion
```

Cada bloque de abajo es **un renglón entero**: copialo completo y Enter. No escribas
`.venv\Scripts\python.exe` solo (abre Python con `>>>`; si te pasa, `exit()` y Enter).

- **Terminal 1, Leda** (queda corriendo). Dos renglones, uno por vez:

  ```
  $env:LEDA_BASE_URL = "http://localhost:8000"
  ```

  ```
  .venv\Scripts\python.exe -m leda escuchar corework
  ```

- **Terminal 2, la página de la tarea** (queda corriendo; dice `Uvicorn running on
  http://127.0.0.1:8000`):

  ```
  .venv\Scripts\python.exe -m uvicorn leda.entrada:app --host 127.0.0.1 --port 8000 --no-access-log
  ```

  No se usa `python -m leda servir`: además de la página arranca otro ciclo de Leda, que mandaría
  avisos y usaría la sesión de ChatGPT a la vez que el escuchador.
- **Terminal 3, el reloj de Leda** (para ver en qué hora está):

  ```
  .venv\Scripts\python.exe -m leda.motor.reloj corework estado
  ```

  Después de cada salto del reloj, **esperar 2 minutos reales**: los avisos se revisan una vez por
  minuto.
- **Los enlaces** se abren con Telegram Desktop o Telegram Web en la PC. Si el enlace no se puede
  tocar, copiarlo al navegador.
- **Ariel, Ismael y Marcos:** `/start` al bot del equipo del Motor. Ariel: "hola" al bot de
  administración.
- **No correr** una ronda de conversaciones de prueba mientras corre el escuchador.

## El hilo

1. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework adelantar` → Leda pasa al
   viernes 09/10 a las 10:00. Esperar 2 minutos.
2. **Marcos:** "qué tengo pendiente?" → sus dos tareas, con su estado y el vencimiento del viernes
   16. Sin nombres del sistema ("en_curso", "asignada").
3. **Marcos:** "termine el plc, ya arranca desde el plc" → Leda recibe la entrega aunque la tarea
   nunca se arrancó. Dice en palabras simples lo que falta para aprobarla, **sólo lo que falta**: los
   20 ciclos sin fallas (no vuelve a preguntar si arranca desde el PLC), con un ejemplo sacado del
   criterio, sin datos inventados. Todavía no hay botón Confirmar. No nombra a Ismael como motivo.
4. **Marcos:** "sí" → Leda toma el ejemplo como lo que Marcos describe (no es la confirmación de la
   entrega) y pide sólo lo que queda: una foto o captura.
5. **Marcos:** manda una foto cualquiera (sin texto) → la vista previa de la entrega: lo descrito,
   la foto y qué cubre cada cosa, que al confirmar pasa a revisión, con Confirmar.
6. **Marcos:** toca Confirmar → "Quedó entregada y pasa a revisión. Te aviso cuando la revisen o si
   hace falta algo más." (o algo muy parecido), **sin nombrar a Ismael**.
7. **Marcos:** "a quien le avisaste?" → ahora sí: Ismael, y cuándo se entera (unos 10 minutos
   después de confirmar, el margen para corregir).
8. **Ariel:** "termine el dashboard de lotes, muestra los lotes del dia con su cantidad y estado y
   coinciden con el registro de produccion" y una foto → la vista previa, con Confirmar (no pide
   nada más: lo escrito dice todo el criterio). Ariel toca Confirmar → quedó entregada, sin nombrar a
   Ismael.
   Hacer los pasos 3 a 8 sin pausas largas: si entre la entrega de Marcos y la de Ariel pasan más de
   10 minutos reales, a Ismael le llegan por separado (está bien así, pero no se ve la lista).
9. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 10:30`. Esperar 2 minutos
   → a Ismael le llega **un solo mensaje**: "Te entregaron 2 tareas para revisar", cada una con
   quién la entregó y cuántas fotos trae, y un botón por tarea ("Ver Dashboard de lotes en CoreLabs",
   "Ver Programar PLC de la comprimidora"). En la lista no hay Aprobar ni Pedir cambios. Dice
   "revisar", no "aprobar".
10. **Marcos:** "y la de comunicaciones como sigue?" → Leda le contesta. (Marcos queda conversando:
    sirve para el paso 16.)
11. **Ismael:** toca "Ver Programar PLC de la comprimidora" → la entrega de Marcos: lo que describió,
    la foto, el enlace a la página de la tarea y los botones Aprobar y Pedir cambios.
12. **Ismael, en la PC:** abre el enlace → la página de la tarea en el navegador: el título, "en
    revisión", lo entregado con la foto, y la historia, que dice que arrancó y se entregó en el mismo
    momento (sin una fecha de inicio inventada). Nada se puede editar.
13. **Ismael:** toca Pedir cambios → Leda pregunta qué falta. **Ismael:** "falta una foto del contador
    de ciclos" → queda pedido el cambio, y Leda le dice que le queda una por revisar, con el botón "Ver
    Dashboard de lotes en CoreLabs". No le manda ningún aviso nuevo.
14. **Marcos:** no recibe nada todavía → escribió hace menos de 30 minutos (paso 10), así que el aviso
    del pedido de cambios espera para no interrumpirlo.
15. **Ismael:** toca "Ver Dashboard de lotes en CoreLabs" → la entrega de Ariel, con la foto, el
    enlace y los dos botones. **Ismael:** "esta bien pero cambiale los colores al grafico" → mezcla
    aprobar y pedir un cambio: Leda pregunta **una sola vez** cuál de las dos, con dos botones.
16. **Ismael:** "aprobala nomás y pasale lo de los colores" → se lee como la elección: queda aprobada
    y lo de los colores le llega a Ariel como comentario, no como pedido de cambios. No vuelve a
    preguntar. Ya no le queda nada por revisar.
    Variante (para otra pasada): si en lugar de eso Ismael escribe "y bueno, fijate vos", Leda no
    decide ni repite la pregunta: dice que la entrega queda esperando su decisión, con los dos
    botones.
17. **Ariel:** le llega que la tarea quedó aprobada, con el comentario de los colores y el enlace a la
    página (sin el margen de 10 minutos; si Ariel escribió hace menos de 30 minutos, le llega cuando
    se cumplen).
18. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 11:15` (más de 30 minutos
    después del último mensaje de Marcos). Esperar 2 minutos → a Marcos le llega el pedido de cambios
    de la tarea del PLC (la foto del contador de ciclos), con el enlace, en un solo mensaje y sin
    repetir lo que ya se habló.
19. **Marcos:** manda una foto y escribe "ahi va la del contador, completo los 20 ciclos sin fallas" →
    la vista previa de la entrega nueva, con Confirmar (si le falta algo del criterio, lo pide, y
    sólo eso). Marcos toca Confirmar → vuelve a revisión.
20. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 11:40`. Esperar 2 minutos →
    a Ismael le llega la entrega nueva, con sus fotos y el enlace.
21. **Ariel:** "termine la integracion de la comprimidora en corelabs" (la tarea que nunca arrancó)
    → Leda la recibe igual y pide sólo lo que falta del criterio (los datos actualizados cada minuto
    durante un turno completo), con un ejemplo. Ariel puede escribir "dejalo, despues la entrego" →
    no queda nada entregado.

## Para volver a empezar

- **El reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework volver`. El reloj nunca va
  para atrás de lo ya registrado: lo guardado para "mañana" de Leda sale cuando llegue esa hora real.
- **Las tareas y lo conversado** no se borran: para repetir la prueba desde cero, pedirle al agente
  que recree `leda_motor` (lo hace con respaldo previo; ya está autorizado).
- **Al terminar:** cortar las terminales 1 y 2 con Ctrl+C.

## Qué anotar

Por cada paso que no salga como dice la flecha: el número del paso, qué dijo Leda (dos o tres
renglones alcanzan) y la hora del reloj de Leda. Va a la bitácora de flujos.
