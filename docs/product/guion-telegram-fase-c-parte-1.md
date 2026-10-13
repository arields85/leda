# Guion de la prueba por Telegram: la entrega y la revisión (Fase C, parte 1)

Para el usuario, que opera las tres cuentas de prueba: Ariel, Ismael y Marcos. Mide con la IA real lo
que la regresión automática no ve: la entrega contra el criterio, la lista de lo que hay para
revisar, la decisión, la espera de 30 minutos y el enlace a la página de la tarea (pasos 1 a 21) y,
en la segunda parte, lo construido desde el 2026-10-09: quién destraba un bloqueo, los apodos, la
pregunta sin contestar, pasar una tarea, el enlace y el detalle de una tarea ajena, la lista de
tareas, el informe al grupo y la forma de los mensajes (pasos 22 a 48). Datos ficticios, base
`leda_motor` (recreada el 2026-10-08 para esta prueba y puesta al día hasta la migración `0056` el
2026-10-12; respaldos previos en `db/respaldos/`).

**Las tareas de la prueba** (vencen el viernes 16/10):

- Marcos: "Programar PLC de la comprimidora", todavía sin arrancar. Para aprobarla: "La comprimidora
  arranca desde el PLC y completa 20 ciclos sin fallas", y lleva una foto o captura.
- Marcos: "Revisar comunicaciones industriales de la comprimidora", en curso (espera al PLC).
- Ariel: "Dashboard de lotes en CoreLabs", en curso. Para aprobarla: "El dashboard muestra los lotes
  del día con su cantidad y su estado, y coinciden con el registro de producción", y lleva una foto o
  captura.
- Ariel: "Integrar datos de la comprimidora en CoreLabs", todavía sin arrancar.
- Las dos de Marcos y las dos de Ariel las revisa Ismael.
- Marcos es el encargado de OT y Ariel, el de Software e interfaz HMI (el sector de sus dos
  tareas). Mariano, Nahuel, Lucas y Martín no tienen Leda conectada. Leda no conoce ningún apodo.

## Antes de empezar

- **El estado de las tareas:** la prueba del 2026-10-08 pudo dejarlas entregadas o aprobadas. Antes
  de empezar, el agente comprueba que estén como dice arriba; si no, recrea `leda_motor` (con
  respaldo previo; ya está autorizado) y después se corre una vez, en una terminal cualquiera,
  `.venv\Scripts\python.exe -m leda.motor.reloj corework volver`.

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
  minuto. El reloj nunca deja a Leda antes de lo que ya registró: si un salto cayera antes, se niega
  (`STOP`) y dice hasta cuándo registró; no cambia nada.
- **Los enlaces** se abren con Telegram Desktop o Telegram Web en la PC. Si el enlace no se puede
  tocar, copiarlo al navegador.
- **Ariel, Ismael y Marcos:** `/start` al bot del equipo del Motor. Ariel: "hola" al bot de
  administración.
- **No correr** una ronda de conversaciones de prueba mientras corre el escuchador.

## El hilo

1. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework adelantar` → Leda pasa al día
   hábil siguiente a las 10:00 (el martes 13/10 si la prueba es el lunes 12). Anotar qué día quedó:
   la segunda parte depende de él. Esperar 2 minutos. (A observar: ese día puede llegar también el
   aviso previo de las tareas que vencen el viernes 16.)
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

## El hilo, segunda parte: lo construido desde el 2026-10-09

Sigue el mismo día, sin cortar. **En todos los mensajes de Leda** (también los de arriba): la última
oración va sola en su renglón, con un renglón en blanco antes, aunque no sea una pregunta; ningún
renglón largo junta dos ideas; un mensaje de un solo renglón queda como está. Leda nunca usa un
apodo para nombrar a alguien. Si un mensaje esperado no llega a las 17:00, sale al día hábil
siguiente: anotarlo, no es una falla.

**Un bloqueo, un apodo y la pregunta sin contestar**

22. **Marcos:** "con comunicaciones estoy parado, me falta la ip del servidor de corelabs y me la
    tiene que pasar el colo" → Leda anota que la de comunicaciones está trabada por eso y, como no
    tiene a nadie como "el Colo" en el equipo, pregunta quién es. No le escribe a nadie todavía.
23. **Marcos:** "ariel" → "¿«El Colo» es Ariel De Simone?", con Confirmar.
24. **Marcos:** toca Confirmar → quedó anotado que lo destraba Ariel; Leda le pregunta a Ariel para
    cuándo y le avisa a Marcos apenas sepa algo. No dice que ya le escribió ni nombra a Ismael.
25. **Marcos:** "pasame el link de la de comunicaciones" → el enlace a la página de esa tarea, al
    final del mensaje (es suya: no pregunta nada).
26. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 12:30`. Esperar 2 minutos
    → a Ariel le llega, de parte de Leda y no en nombre de Marcos: que Marcos está trabado con
    comunicaciones, que le falta la IP del servidor de CoreLabs, y para cuándo se la puede pasar.
    Sin reproche y sin "el Colo".
27. **Ariel:** no contesta. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora
    16:35`. Esperar 2 minutos → a Ariel le llega la misma pregunta otra vez, una sola vez (se repite
    a las 4 horas). A Marcos no le llega nada.
28. **Ariel:** "uh me olvide, mañana a la mañana se la paso" → quedó anotado y Marcos se va a enterar.
    No dice que el bloqueo se cerró.
29. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 16:50`. Esperar 2 minutos
    → a Marcos le llega que Ariel dice que mañana a la mañana le pasa la IP, que cuando pueda seguir
    lo diga y que no hace falta responder. No dice que se destrabó.

**El día siguiente: destrabar, pasar una tarea y pedir el detalle**

30. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework adelantar`. Esperar 2 minutos →
    Leda pasa al día hábil siguiente a las 10:00 (anotar cuál). A Ariel le llega si pudo pasarle la
    IP a Marcos (era el día que dio). A Ismael, un recordatorio de lo que espera su revisión (el PLC
    de Marcos), con un botón para verla. (A observar: otros avisos del día.)
31. **Ismael:** toca el botón y después Aprobar → queda aprobada y ya no le queda nada por revisar. A
    Marcos le llega que el PLC quedó aprobado, con el enlace.
32. **Marcos:** "el colo ya me paso la ip, sigo con comunicaciones" → Leda entiende que es Ariel sin
    preguntar quién es, y anota que pudo seguir: la tarea deja de estar trabada.
33. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 10:20`. Esperar 2 minutos
    → a Ariel le llega que lo de Marcos ya se resolvió y que no hace falta que haga nada. Leda no le
    vuelve a preguntar.
34. **Ariel:** "la de integrar la comprimidora en corelabs pasasela a marcos, el conoce mejor el plc"
    → la vista previa: la tarea pasa de Ariel a Marcos, y antes Leda le pregunta a Marcos si la toma;
    con Confirmar. No nombra a Ismael.
35. **Ariel:** toca Confirmar → Leda le pregunta a Marcos y le avisa a Ariel cuando conteste;
    mientras tanto la tarea sigue con Ariel.
36. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 10:50`. Esperar 2 minutos
    → a Marcos le llega que Ariel le quiere pasar "Integrar datos de la comprimidora en CoreLabs" y si
    la toma, con los botones "La tomo" y "No la tomo". A Ismael no le llega nada.
37. **Marcos:** toca "La tomo" → la tarea pasa a ser suya.
38. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 11:10`. Esperar 2 minutos
    → a Ariel le llega que Marcos tomó la tarea. A Ismael, nada.
39. **Marcos:** "con comunicaciones otra vez estoy parado, falta que mariano termine el cableado del
    tablero" → quedó anotado; a Mariano todavía no le puede escribir; ya se lo avisó al administrador
    para que lo conecte; y una sola pregunta: si hay otra persona que pueda destrabarlo, o si se lo
    pide Marcos y le cuenta. No promete escribirle a Mariano. **Ariel, en el bot de
    administración:** le llega el aviso de que hay que conectar a Mariano (a observar el texto y la
    hora).
40. **Marcos:** "se lo pido yo y te cuento" → Leda lo anota y no le escribe a nadie (a observar qué
    dice que hace después).
41. **Marcos:** "pasame el link del dashboard de lotes" → no es suya: Leda le da el resumen (de
    Ariel, aprobada) y le ofrece pedirle a Ariel el detalle con las fotos. Ningún enlace, y nunca "no
    la podés ver".
42. **Marcos:** "si dale" → Leda le pregunta a Ariel y le avisa cuando conteste.
43. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 11:30`. Esperar 2 minutos
    → a Ariel le llega que Marcos pide ver el detalle del dashboard de lotes y si se lo comparte, con
    los botones "Compartirla" y "No compartirla".
44. **Ariel:** toca "Compartirla" → que se lo comparte y que Marcos se va a enterar.
45. **Reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework hora 11:55`. Esperar 2 minutos
    → a Marcos le llega que Ariel le compartió el dashboard, con el enlace al final. Si Leda está en
    miércoles, aparte le llega también la lista de sus tareas (salía 11:30 y esperó 30 minutos desde
    su último mensaje): comunicaciones, trabada esperando el cableado de Mariano; la de integrar,
    que vence el viernes 16; y una sola pregunta, por la que se puede mover. El PLC ya no está.
46. **Marcos, en la PC:** abre el enlace del dashboard → la página de la tarea de Ariel, aprobada,
    con la foto. Nada se puede editar.
47. **Marcos** (si le llegó la lista): "la de integrar recien la agarro, el viernes la tengo" → queda
    anotado, sin otra pregunta (a observar las palabras).
48. **Reloj:** si Leda está en miércoles, `.venv\Scripts\python.exe -m leda.motor.reloj corework hora
    15:35`; si está en viernes, `hora 16:20`; otro día no hay informe (anotarlo). Esperar 2 minutos →
    en el grupo del equipo, el informe: lo terminado con el nombre de quien lo hizo (el dashboard,
    de Ariel; el PLC, de Marcos), la de comunicaciones trabada con lo que falta, y la de integrar, de
    Marcos, con su vencimiento. Cada renglón con nombre, sin comparar personas, sin "todo en orden"
    (hay una trabada) y sin pedir respuesta. Si no llega nada, anotarlo: puede ser que el bot del
    equipo del Motor no esté en el grupo.

## Para volver a empezar

- **El reloj:** `.venv\Scripts\python.exe -m leda.motor.reloj corework volver`. El reloj nunca va
  para atrás de lo ya registrado: lo guardado para "mañana" de Leda sale cuando llegue esa hora real.
  Si Leda ya registró algo más tarde que la hora real, `volver` se niega (`STOP`) y el reloj queda
  donde estaba; para seguir, `adelantar` u `hora`, que tampoco van antes de lo registrado.
  `volver --forzar` es sólo para empezar de cero con `leda_motor` recreada.
- **Las tareas y lo conversado** no se borran: para repetir la prueba desde cero, pedirle al agente
  que recree `leda_motor` (lo hace con respaldo previo; ya está autorizado).
- **Al terminar:** cortar las terminales 1 y 2 con Ctrl+C.

## Qué anotar

Por cada paso que no salga como dice la flecha: el número del paso, qué dijo Leda (dos o tres
renglones alcanzan) y la hora del reloj de Leda. Va a la bitácora de flujos.
