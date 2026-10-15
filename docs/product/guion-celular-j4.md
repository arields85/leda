# Guion de la prueba en el celular: la carga desde la web del equipo (J4)

La web y el túnel ya están levantados con el código nuevo. Todo se hace en `leda_motor`, con datos
ficticios. Las cuentas que operás son Ariel, Ismael y Marcos. Nahuel, Lucas, Martín y Mariano no
tienen Telegram conectado.

**Antes de empezar:** reiniciá el escuchador (Ctrl+C y
`.venv\Scripts\python.exe -m leda escuchar corework`), así toma el código nuevo.

Los avisos de la carga salen a los **10 minutos** de la última carga, dentro del horario: a veces hay
que esperar.

## Marcos, referente de OT

1. **Marcos**, en Telegram: `quiero crear una tarea`.
   → Leda le dice que se cargan desde su web y le manda la entrada. Abrirla.
2. **Marcos**, en Telegram: `y un objetivo?`
   → Leda le dice que los objetivos los crea Dirección, sin enlace.
3. En la web de Marcos, tocar **"> nueva tarea"** y abrir la lista de "Quién la hace".
   → Están Nahuel (su área), él mismo, Ariel, Martín y Mariano (como pedido a su área) e Ismael (como
   pedido a Dirección). **No** está Lucas.
4. Cargar para **Ariel**: `configurar el router de la planta para el 23 de octubre`, con la ayuda o a
   mano.
   → La vista previa dice que es un pedido al área de Ariel y que Ariel decide quién lo hace.
   Confirmar.
5. Cargar para **Ismael**: `aprobar la compra del módem nuevo`, para el 21/10.
   → La vista previa dice que es un pedido a Dirección. Confirmar.
6. Cargar para **Marcos mismo**: `colgar el módem en la pared`, para el 28/10, que **espera** a
   "Aprobar la compra del módem nuevo".
   → Quien la revisa es él mismo. Confirmar.

## Ismael, Dirección

7. **Ismael**, en Telegram: `quiero crear una tarea`. Abrir la entrada.
8. Tocar **"> nueva tarea"** y cargar para **Nahuel**: `revisar el tablero de la línea 3`, para el
   22/10.
   → Aparece **"Quién la revisa"**, con Marcos ya elegido. Dejarlo así. La vista previa avisa que
   Nahuel no tiene a Leda conectada. Confirmar.

## Los avisos (esperar unos 10 minutos)

9. **Ariel**, en el chat del equipo:
   → Le llega un mensaje con lo que le pidió Marcos ("Configurar el router…", para el 23/10), que él
   decide quién lo hace, y la entrada a su web.
10. **Ismael**:
    → Le llega el pedido de Marcos ("Aprobar la compra del módem nuevo").
11. **Marcos**:
    → Le llega que Ismael le cargó a Nahuel "Revisar el tablero de la línea 3" y que la revisa él.
12. **Ariel, en el bot de administración**:
    → Le llega el aviso para conectar a Nahuel.
13. A **Marcos** no le llega nada por "Colgar el módem", porque es suya. A **Ismael** no le llega nada por
    lo que Marcos cargó para sí mismo.

## En la web

14. **Ariel**, en su web, mira "Tu sector".
    → Está "Configurar el router…", pedida por Marcos.
15. **Marcos**, en su web, mira "Mis pedidos".
    → Están el pedido a Ariel y el pedido a Ismael, cada uno con su estado.
