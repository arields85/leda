# ADR 0022: La plataforma web de tareas

- **Estado:** aceptado por el usuario (2026-10-12). Las decisiones de producto (1 a 10) las tomó el
  usuario el 2026-10-11, una por una, y las de tecnología y aspecto (17 y 18) el 2026-10-11 y el
  2026-10-12; las técnicas (11 a 16) las propuso el agente y entraron con la aceptación del documento.
- **Fecha:** 2026-10-11 (tecnología y aspecto, 2026-10-12).
- **Alcance:** la plataforma web que pide el [ADR 0017](0017-por-chat-los-hechos-por-la-web-la-estructura.md),
  decisión 5: cargar tareas, ver su estado, cambiar fechas por retrasos y gestionar integrantes. Es
  el ADR propio que esa decisión exige antes del código, y el que dejó abierto el
  [ADR 0019](0019-evidencia-y-pagina-de-la-tarea.md) (la página de la tarea es su primer pedazo).
- **Reemplaza en parte:** el [ADR 0004](0004-dos-superficies-separadas.md) (una sola aplicación con
  dos puertas en vez de dos aplicaciones, decisión 10) y el ADR 0017, decisión 4 (la fecha la cambia
  el referente, no el administrador, decisión 8). Resuelve el `PENDIENTE` del ADR 0017, decisión 2
  (Leda avisa que se cargó una tarea, decisión 7).
- **Evidencia:** el inventario `docs/product/plataforma-pendientes.md`; `nucleo/constitucion.md` §2,
  §4, §7, §8, §12 y §13; `nucleo/mecanica-pm.md` §2, §3, §7 y §10; el código de hoy
  (`src/leda/entrada.py`, `tablero.py`, `pagina_de_tarea.py`, `siembra.py`).

## Contexto

Hoy ninguna página de Leda escribe en la base. Las tareas se cargan con `leda sembrar`, que corre
con el rol que saltea el aislamiento, no valida lo que la decisión 2 del ADR 0017 exige ni guarda
quién decidió. El tablero que se pide por chat muestra totales, no las tareas, y su enlace vence a
los 30 minutos. La página de cada tarea ya se lee bien en un celular (`tarea_vista.py`).

El inventario de lo que la plataforma tiene que permitir es enorme (horarios, cadencias, tono,
apodos, modelos de IA). Si la primera versión intenta todo, tarda semanas en llegar a una prueba
real, y el método del Motor pide lo contrario (`AGENTS.md`, punto 5).

## Decisión

### Producto (usuario, 2026-10-11)

1. **La primera versión reemplaza al comando de carga, nada más.** Hace cuatro cosas:
   - la lista de las tareas de un espacio, con su estado y su fecha;
   - el formulario para cargar una tarea, con todos sus controles (decisión 9);
   - el cambio de fecha, con el pedido de más tiempo a la vista (decisión 8);
   - el alta y la baja de integrantes.

   La configuración (horarios, feriados, cadencias, tono, apodos y lo demás del inventario) sigue
   con el paquete del espacio y la consola hasta una segunda versión.

2. **Una sola web, responsive, que se instala en el celular.** Queda con su ícono en la pantalla de
   inicio (una aplicación web instalable), sin tiendas ni una aplicación aparte.
   - **Por qué:** una sola base de código cuida una sola vez las garantías (aislamiento y auditoría);
     una aplicación aparte duplica el trabajo y pasa por las tiendas en cada cambio; los avisos al
     celular ya los da Telegram.
   - **Se pierde:** funcionar sin internet y algo de fluidez. Para mirar estados y fechas no hace
     falta.
   - **Regla:** cada página a la que lleve un enlace de Leda (la tarea, su entrega, sus fotos y
     archivos, la lista) se diseña primero para el celular y se comprueba en el ancho de un teléfono
     antes de darla por terminada.

3. **Cada persona ve lo mismo que le contaría Leda, según su puesto.** El seguimiento facilita el
   trabajo y no vigila a nadie, y los atrasos se tratan primero en privado (constitución §8):
   - **integrante:** sus tareas, las que espera de otros y las que otros esperan de él; no ve los
     atrasos de los demás en sus propias tareas;
   - **referente o encargado:** todas las tareas de su sector, con fechas, atrasos y bloqueos;
   - **autoridad final del espacio:** todo el espacio, sin rankings ni comparaciones entre personas;
   - **administrador:** todo, y además carga y cambia (decisión 6).

   La regla de quién ve qué es una sola, en la base, y la usan el chat y la web (decisión 13).

4. **Leda ofrece el acceso; nadie lo pide, y no vence.**
   - Cuando una persona se incorpora y empieza a hablar con Leda, Leda le manda el enlace con una
     explicación corta ("acá podés ver tus tareas cuando quieras; si lo agregás a la pantalla de
     inicio, te queda como una app"). Lo recuerda cuando viene al caso, sin insistir. Al salir la
     primera versión, se lo ofrece una vez a cada integrante activo.
   - El enlace que manda Leda sirve una sola vez: abre la sesión en ese celular. Si alguien reenvía
     el mensaje, quien lo recibe no entra.
   - La sesión queda abierta sin vencimiento. Se corta sólo si la persona deja el equipo (se revisa
     en cada ingreso), si un administrador la corta o si la persona le avisa a Leda que perdió el
     celular. Con un teléfono nuevo, pide un enlace nuevo.
   - **Precisión (usuario, 2026-10-12):** el enlace que nadie usó vence a las 24 horas, y Leda lo
     dice al mandarlo, para que la persona sepa que si no lo toca tiene que pedir uno nuevo. Lo
     que no vence es la sesión abierta.

5. **Sin "tablero" ni nombre de producto.** El ícono dice "Leda". Adentro, el título dice lo que
   muestra: "Tus tareas" (integrante), "Tu sector" (referente o encargado), "El equipo" (autoridad
   final). Leda habla igual: "acá podés ver tus tareas".

6. **Los administradores entran por el bot de administración.**
   - Piden el enlace al bot de administración, que ya los reconoce por su Telegram. El enlace sirve
     una vez y deja la sesión abierta, sin vencimiento, en esa computadora o ese celular.
   - Cada cambio pasa por una vista previa y una confirmación, como en el chat (constitución §7).
   - Cada cambio se avisa por el bot de administración a todos los administradores ("Ariel cargó
     'Instalar el switch de la planta' desde la web"): si alguien usa una sesión sin permiso,
     cualquiera se entera y la corta.
   - Cada administrador entra con su propio Telegram y su propio enlace; nunca una cuenta compartida.
     La auditoría dice siempre quién hizo cada cambio.
   - Si dos administradores cambian lo mismo a la vez, el segundo en guardar ve que cambió mientras
     lo tenía abierto y tiene que revisarlo antes de confirmar. Ningún cambio se pierde en silencio.
   - Nombrar a un administrador nuevo sigue siendo un acto deliberado por la consola: es el permiso
     más fuerte que existe.
   - **Para más adelante:** con clientes, alguien de cada empresa querrá cargar sus tareas. Será un
     rol del espacio, con acceso sólo a su empresa, no un administrador de toda Leda.
   - **Alternativa descartada:** usuario y contraseña con un código del celular. Es más segura si
     roban la computadora abierta, pero es la molestia que el usuario no quiso.

7. **Leda avisa que se cargó una tarea.**
   - El responsable recibe un mensaje privado con la tarea, su fecha, lo que se espera, la evidencia
     y el enlace, que no pide respuesta.
   - Quien la va a revisar recibe un aviso corto ("cuando Lucas entregue …, la revisás vos").
   - La autoridad final no recibe un mensaje por tarea: las ve en "El equipo" y en el informe al
     grupo.
   - Varias tareas para la misma persona van en un solo mensaje.

   Son avisos de coordinación: quedan fuera del tope de contacto (mecánica §10, precisión del
   2026-09-30).

8. **El pedido de más tiempo lo decide el referente, en la web.**
   - El pedido aparece arriba en "Tu sector": "Lucas pide correr 'Instalar el switch de la planta'
     del 23/10 al 30/10. Motivo: el proveedor se demoró." [Aceptar el 30/10] [No].
   - Si acepta, ve la vista previa, confirma y la fecha cambia en ese momento. Se enteran Lucas y los
     administradores, y la auditoría guarda que decidió el referente.
   - Si no, a Lucas le llega que la fecha sigue, y el seguimiento sigue contra ella.
   - Un administrador también puede cambiar una fecha (por ejemplo, si el referente se lo dijo por
     teléfono); la auditoría guarda quién la cambió y quién lo decidió.
   - Que el referente decida por chat, con un botón, sigue para más adelante (ADR 0017, decisión 4).

9. **Lo que controla el formulario de carga.** No se guarda una tarea:
   - sin objetivo, responsable, fecha, criterio de aceptación o evidencia pedida (ADR 0017,
     decisión 2);
   - con la fecha en un día no hábil del espacio (decisión 56 de la Fase C) o en el pasado;
   - para alguien que no es integrante activo del espacio;
   - con la misma persona haciéndola y revisándola, porque nadie podría aprobarla.

   Además:
   - **Leda ayuda con el criterio.** Si es vago ("que funcione bien"), propone uno comprobable con su
     evidencia, y el administrador lo acepta, lo cambia o deja el suyo (constitución §8: Leda propone
     y la persona elige).
   - **Una fecha posterior a la de su objetivo se avisa y no se bloquea:** el administrador puede saber
     algo que el sistema no sabe. Hoy ningún objetivo tiene fecha.

10. **Una sola aplicación con dos puertas** (reemplaza la separación en dos aplicaciones del
    ADR 0004, conservando su propósito).
    - **La puerta del equipo** se abre sólo con el enlace de Leda del bot del espacio y muestra sólo
      ese espacio. Nunca da funciones de administración, aunque la persona sea administradora: el
      sombrero lo define el canal (constitución §2).
    - **La puerta de administración** se abre sólo con el enlace del bot de administración. Es la
      única que carga tareas, gestiona integrantes y ve más de un espacio.
    - Ejemplo: Ariel, integrante de CoreWork y administrador de Leda, entra desde el bot del equipo y
      ve "Tus tareas"; para cargar una tarea entra por la puerta de administración.

**Integrantes sin Leda conectada** (parte de la decisión 1, usuario). Telegram no deja que un bot
escriba primero: el administrador le pasa a cada persona su enlace de activación (los que ya existen),
por donde se hablen. Se le pueden cargar tareas antes, con un aviso ("no va a recibir avisos ni
seguimiento hasta que la conecte") que también le llega a su referente. Cuando se conecta, Leda le da
la bienvenida, le manda sus tareas en un solo mensaje y le ofrece "Tus tareas". La lista de
integrantes de la web muestra quién está "conectado" y quién "sin conectar". Un código QR, por ahora
no (el usuario avisará si hace falta).

### Técnica (propuesta del agente)

11. **La web escribe sólo con funciones de la base, nunca con el rol que saltea el aislamiento.**
    Cada operación (cargar una tarea, cambiar una fecha, dar de alta o de baja a un integrante) es una
    función `security definer` con dueño explícito y verificado, que valida lo de la decisión 9,
    escribe el evento (el estado sigue siendo la proyección de eventos) y deja su fila de auditoría con
    quién la cargó, quién la decidió y las versiones del núcleo y del paquete (constitución §12). El
    espacio sale de la sesión, del lado del servidor, nunca del formulario: no se repite el patrón de
    `confirmar_borrador_tarea` (riesgo 4 de `docs/STATUS.md`). `leda sembrar` queda sólo para pruebas
    y semillas.

12. **Las sesiones.** Una tabla guarda sólo el hash de cada sesión, a qué membresía (puerta del
    equipo) o a qué rol de plataforma (puerta de administración) pertenece, cuándo se usó y si se
    cortó. El enlace de un solo uso se canjea por una cookie `HttpOnly`, `Secure` y `SameSite=Strict`;
    cada puerta tiene la suya. Cada pedido revalida la membresía o el rol en la base. Las escrituras
    llevan protección contra pedidos cruzados (CSRF). El enlace de 30 minutos del tablero se retira.

13. **Quién ve qué, una sola regla.** La regla de la decisión 3 se escribe en SQL, extendiendo la de
    `puede_ver_tarea` (ADR 0019) de una tarea a la lista; el chat y la web la usan igual.

14. **Los avisos salen por el camino de siempre.** Los de las decisiones 7 y 8 y los de cambios a los
    administradores son avisos del motor (ADR 0016 y 0018, decisión 8), por la cola de salida y con su
    auditoría; la IA los redacta desde hechos, como todos.

15. **Dos cambios a la vez.** Cada fila editable lleva su versión; guardar con una versión vieja no
    pisa: devuelve lo que cambió (decisión 6).

16. **Dónde corre y en qué orden se construye.** Primero en la PC del usuario, como hoy la página de
    la tarea (`LEDA_BASE_URL`); el servidor en internet espera su autorización. Se construye por
    porciones, cada una con su prueba real en el celular antes de la siguiente:
    1. la puerta del equipo, de sólo lectura: sesiones (decisiones 4 y 12), "Tus tareas", "Tu
       sector" y "El equipo" (decisiones 3, 5 y 13), y Leda ofreciendo el acceso;
    2. la puerta de administración y el formulario de carga, con sus avisos (decisiones 6, 7, 9, 10,
       11 y 15);
    3. el pedido de más tiempo y el cambio de fecha (decisión 8);
    4. los integrantes: alta, baja, "conectado / sin conectar" y el enlace de activación.

### Tecnología y aspecto (usuario, 2026-10-11 y 2026-10-12)

17. **La misma tecnología que la interfaz HMI, para que Leda se pueda sumar a ella más adelante.**
    La HMI HTML5 que se desarrolla en paralelo (su documento de entrega técnica, versión 1.0) es una
    aplicación web estática hecha con React, TypeScript, Vite, Tailwind CSS e íconos Lucide, que
    consume una API. La web de Leda usa la misma base, y las mismas bibliotecas de la HMI cuando
    hagan falta (React Router para las páginas, TanStack Query para los datos del servidor), para
    que en el futuro sus vistas entren en la HMI como un complemento o como widgets.
    - **El servidor no cambia:** Python y PostgreSQL, con las garantías en las funciones de la base
      (decisión 11). La web le habla a una **API interna** propia, servida por la misma aplicación que
      hoy sirve la página de la tarea (`src/leda/entrada.py`). Esa API no es la API de lectura pública
      del ADR 0017, decisión 5, que sigue esperando sus precondiciones.
    - **Mismo origen:** el servidor de Leda sirve también los archivos ya compilados de la web, así
      la cookie de la decisión 12 sigue siendo `SameSite=Strict`. Node hace falta sólo para compilar,
      no para correr Leda.
    - **Un sistema de diseño desde el principio:** los colores, letras, espacios y bordes son
      variables (tokens del tema de Tailwind) y las piezas (tarjeta de tarea, etiqueta de estado, tira
      de la semana, panel de números, árbol de esperas) son componentes reutilizables. El aspecto se
      puede pulir después sin reescribir las páginas, y Leda conserva su estilo dentro de la HMI.
    - **El estilo es distinto del de la HMI:** misma tecnología, otra apariencia (decisión 18).
    - **Alternativa descartada:** páginas armadas en el servidor, como la de la tarea hoy. Son más
      simples, pero no se integran a la HMI y quedan pobres a la vista; el usuario pidió algo
      visualmente rico y pensado para mejorar.

18. **El aspecto: sobrio, oscuro y de letra de máquina** (la propuesta "9 · Terminal" del lienzo de
    diseño, https://claude.ai/artifact/VwC3sCvufFZ7DUkv3yJt7f, elegida entre once y ajustada con el
    usuario: con el cabezal de la "11 · Plano" y la barra "C"; la "9b" muestra una semana sin nada
    vencido ni trabado).
    - **Modo oscuro y casi todo en grises.** Una sola familia tipográfica de ancho fijo (JetBrains
      Mono), esquinas casi rectas, bordes marcados y una sombra gris corrida, sin degradés.
    - **El color es del estado, y sólo si hay algo en él.** Cada estado tiene su color: `[VENCIDA]`
      ámbar, `[TRABADA]` coral, `[EN CURSO]` verde y `[ENTREGADA]` celeste. Lo llevan la palabra del
      estado en cada tarjeta, su número en el panel de arriba (en gris si está en 0) y la barra de una
      tarea en curso. Nada más lleva color: ni bordes, ni botones, ni títulos. El amarillo nunca es el
      color principal ni el resalte.
    - **El cabezal:** arriba, en gris chico, el espacio ("LEDA · COREWORK") y la semana y el día
      ("SEM 44 · LUN 26.10"); debajo, "Tus tareas" en grande y, a la derecha, el nombre y el total
      ("Marcos · 4 activas").
    - **La forma de "Tus tareas":** un panel con un número por estado; la semana día por día, con hoy
      marcado y el día en que vence algo; después, las tareas, cada una con su estado entre corchetes
      y, si está trabada, la cadena de esperas en árbol ("└─ espera: servidor de la planta (Ariel)
      └─ espera: switch nuevo (Lucas)").
    - **La barra de una tarea en curso mide el tiempo, no el trabajo** (Leda no sabe un porcentaje):
      un segmento por día hábil desde que se asignó hasta la entrega, todos de la misma altura; los
      que pasaron en verde, hoy en blanco y los que faltan en gris. Debajo, la fecha de inicio, "hoy"
      bajo el segmento blanco y la fecha de entrega bajo el último. Arriba de esa tarjeta van los días
      que quedan ("quedan 7 días"); las demás tarjetas muestran arriba su fecha.
    - **El botón para hablar con Leda**, al pie: "> contarle algo a leda", con el mismo marco, radio
      y sombra que las tarjetas, pero en blanco (borde, texto y sombra), sin cursor. Abre el chat con
      Leda.
    - "Tu sector" y "El equipo" usan las mismas piezas con más tareas; la puerta de administración
      también, con los formularios en el mismo estilo.
    - El lienzo queda como referencia; los colores exactos y los tamaños pasan a los tokens en la
      porción 1.

## Consecuencias

- **Lo que deja de existir:** el tablero de totales con enlace de 30 minutos y la carga por consola
  como camino normal.
- **Lo que no cambia:** la página de cada tarea y su enlace (ADR 0019) siguen igual; pasan a ser una
  vista más de la plataforma. Crear y aceptar tareas por chat sigue fuera (ADR 0017, decisiones 1 y
  2).
- **Riesgos:** una sesión sin vencimiento es tan fuerte como el celular donde quedó abierta; lo
  compensan el corte inmediato, la revalidación en cada pedido y, en la puerta de administración, el
  aviso de cada cambio a todos los administradores.
- **El inventario** (`docs/product/plataforma-pendientes.md`) separa lo de esta primera versión de lo
  que espera a la segunda.
- **Pruebas:** las funciones de la base, con pruebas de garantías (aislamiento entre espacios, quién
  ve qué, auditoría, un enlace que no sirve dos veces, una sesión cortada); las páginas, con
  `TestClient` y un control de ancho de celular; y cada porción, con la prueba del usuario en su
  teléfono.
