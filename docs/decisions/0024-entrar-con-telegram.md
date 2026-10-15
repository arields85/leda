# ADR 0024: Entrar a la web con Telegram: la Mini App en el celular y el QR en la computadora

- **Estado:** Aceptado por el usuario el 2026-10-14 ("si"). Las decisiones son del usuario (2026-10-14, de a una, en
  `odd/tasks/plataforma-jerarquias.md`, MA1 a MA5). La redacción y la parte técnica son del agente.
- **Fecha:** 2026-10-14.
- **Alcance:** cómo se entra a las dos puertas de la web (la del equipo y la de administración),
  desde el celular y desde la computadora, y cómo Leda ofrece entrar.
- **Enmienda** el [ADR 0022](0022-plataforma-web-de-tareas.md):
  - la decisión 2 (la web instalable en la pantalla de inicio);
  - la decisión 4 (el enlace de un solo uso que ofrece Leda);
  - la decisión 6 (los administradores piden el enlace al bot de administración);
  - la decisión 12 (la sesión nace al canjear un enlace).
- **No cambia:**
  - quién ve qué (decisión 3);
  - que cada pedido revalida la membresía o el rol en la base;
  - las dos puertas y que el canal decide el sombrero (constitución §2);
  - la auditoría;
  - cómo se corta una sesión: la baja, "perdí el celular" y el corte del administrador.
- **Evidencia:** la documentación oficial de Telegram (https://core.telegram.org/bots/webapps,
  https://core.telegram.org/bots/api, `InlineKeyboardButton.web_app`: sólo en chats privados); el
  código de hoy (`web_app.py`: `sesion_web`, `sesion_de_administracion`, la política de contenido; el
  despachador, que sólo arma botones de callback o de copiar).

## Contexto

Hoy se entra a la web con un enlace de un solo uso que manda Leda. En el celular es molesto pedir
uno; en la computadora, más (usuario: "son bastante molestos tener que pedir uno cada vez"). Telegram
permite abrir una web dentro de la app (una Mini App) y le dice a esa web quién es la persona, con
una firma que el servidor comprueba con el token del bot.

## Decisión

1. **En el celular, sólo la Mini App; los enlaces desaparecen (MA1).**
   - Leda no manda enlaces ni sugiere pedirlos. Ofrece un botón, o pregunta si la persona quiere
     abrirla.
   - Se revisa cada lugar donde hoy ofrece un enlace: el pedido de acceso, el ofrecimiento de una sola
     vez, la bienvenida, los avisos y "quiero crear una tarea".
2. **El botón dice lo que va a pasar y lleva directo a eso (MA3).**
   - "Ver mis tareas" (a Dirección, "Ver el equipo"), cuando la persona lo pide y en la bienvenida.
   - "Ver la tarea" en un aviso de carga: abre esa tarea, no la página principal.
   - "Cargar la tarea" ante "quiero crear una tarea": abre el formulario. "Crear el objetivo" para
     Dirección.
   - "Administración" en el bot de administración.
   - Con la VPS, el botón fijo del menú del bot, "Tareas".
   - No va en cada mensaje ni en grupos, donde Telegram no lo permite.
   - Con el túnel, Leda arma cada botón con la dirección del momento. Un botón viejo deja de andar si
     el túnel cambia.
3. **La administración, como Mini App de `@Leda_Admin_bot` (MA2).** La Mini App del bot del equipo
   entra como integrante, y la del bot de administración como administrador. Se terminan los
   `enlace-admin` por la consola.
4. **En la computadora, un QR, como WhatsApp Web (MA1b, MA5).**
   - La web muestra un QR. Se escanea con la cámara del celular, y Telegram abre el chat de Leda con el
     botón "Entrar en la compu". Al tocarlo, la computadora entra sola.
   - No hay usuario, contraseña ni código para tipear, y desde la web no se puede averiguar quién está
     en el equipo.
   - En el navegador de un celular, fuera de Telegram, en lugar del QR aparece "Entrar con Telegram",
     que abre el mismo chat.
   - Telegram Web queda fuera.
   - Para la puerta de administración, el QR lleva al bot de administración.
   - La dirección: con la VPS, una fija que se guarda en favoritos. Con el túnel, Leda la pasa por chat
     si se le pide ("pasame la dirección para la compu"); la dirección sola no da acceso.
5. **Cuánto queda recordada una computadora, por equipo.**
   - Lo elige el administrador desde la web de administración: 1, 7, 30 o 90 días, o sin vencimiento.
   - Arranca **sin vencimiento** para todos.
   - Se corta igual con la baja, "perdí el celular", el corte del administrador o "salir" en la
     computadora.
   - Va al inventario de lo configurable (`docs/product/plataforma-pendientes.md`).
6. **Cómo se ve (MA4).**
   - El aspecto oscuro de Leda, sin los colores de cada Telegram.
   - Grande, dejando la barra de Telegram con "Cerrar" (`expand()`, sin pantalla completa).
   - El zoom con dos dedos se libera si, dentro de la Mini App, la página ya no se agranda sola al
     tocar un campo; si no, sigue la regla de hoy.

### Técnica (propuesta del agente)

7. **La firma de Telegram se comprueba siempre en el servidor.**
   - `initData` se valida con HMAC-SHA256 y la clave que deriva del token del bot de esa puerta: el
     del espacio para la puerta del equipo, `LEDA_BOT_TOKEN_ADMIN` para la de administración. El
     espacio sale del bot que firmó, nunca de lo que diga el cliente, y nunca se prueban varios
     tokens hasta que uno coincida.
   - Vale si tiene menos de 10 minutos (`auth_date`), y cada firma se acepta una sola vez: se guarda
     su huella hasta que vence.
   - El usuario de Telegram lleva a su membresía activa (o a su rol de plataforma) por
     `app_user.telegram_user_id`. Nunca se registran `initData` ni tokens.
8. **El QR de la computadora.**
   - La computadora pide un **pedido de entrada**: un secreto al azar que guarda sólo su huella, vence
     a los 5 minutos y sirve una vez. El QR lleva un enlace `t.me/<bot>?start=<código>`.
   - Al tocar "Entrar en la compu" en Telegram, la base liga ese pedido a quien lo tocó y lo marca
     aprobado.
   - La computadora pregunta cada pocos segundos si el pedido ya está aprobado. Cuando lo está, recibe
     su sesión, y el pedido se gasta.
   - Antes de entrar, el chat muestra en qué espacio y desde qué dirección se pidió, para que nadie
     apruebe un QR ajeno sin darse cuenta.
9. **Las sesiones.**
   - Las tablas de sesión dejan de exigir un enlace (`enlace_id` pasa a ser opcional) y guardan su
     origen: `mini_app`, `qr` o, mientras exista, `enlace`.
   - La cookie sigue siendo `HttpOnly`, `Secure` y `SameSite=Strict`, una por puerta.
   - La de la Mini App se renueva en cada apertura y no necesita "salir".
   - La de la computadora dura lo que diga el equipo (decisión 5).
   - Cada sesión nueva deja su fila en la auditoría con su origen.
10. **La web dentro de Telegram.** El script de Telegram se sirve desde el propio servidor, así la
    política de contenido sigue en `script-src 'self'`. Como Telegram Web queda fuera, siguen
    `frame-ancestors 'none'` y `X-Frame-Options: DENY`. Se usan `ready()`, `expand()`, el botón
    "Atrás" de Telegram atado a la navegación y los márgenes seguros. El despachador suma el botón
    `web_app` con su dirección, que sólo va en chats privados.
11. **Se retiran** el enlace de un solo uso de la puerta del equipo y `enlace-admin`, una vez que la
    Mini App y el QR andan y la prueba del usuario pasa.

### Precisión (2026-10-14, prueba en Telegram de escritorio)

12. **Telegram en una computadora abre el navegador** (usuario). Telegram de escritorio y Telegram Web muestran la Mini
    App dentro de un marco, y la web no se deja enmarcar. Por eso los botones apuntan a un **lanzador** mínimo
    (`/app/abrir/…`). En un celular sigue a la Mini App. En una computadora abre la web en el navegador, donde entra
    el QR, y dentro de Telegram dice "Abrí Leda en el navegador".
    - El lanzador es lo único que se puede mostrar dentro de un marco, y sólo desde `https://web.telegram.org`. No
      tiene sesión, datos ni formularios.
    - Todo lo demás sigue con `frame-ancestors 'none'` y `X-Frame-Options: DENY`. Esto precisa la decisión 10.

### Precisión (2026-10-14, noche: el pase de la computadora)

13. **Telegram en la computadora abre el navegador ya adentro, sin el QR** (usuario, MA-5). Esto precisa las
    decisiones 4 y 12.
    - El lanzador manda la firma de Telegram al servidor, que la valida igual que la puerta de la Mini App: el token
      del bot de esa puerta, 10 minutos, y la base la gasta una sola vez (la misma huella que la Mini App).
    - La base revisa la membresía activa del espacio de ese bot (o el rol de plataforma) y deja un pedido de entrada
      ya aprobado por esa persona, como el del QR, que vence al minuto, sirve una vez y guarda sólo la huella del
      pase. Queda auditado (`emitir_pase_a_la_compu`; migración 0076).
    - El navegador abre la dirección del pase, lo canjea y entra donde llevaba el botón, con la sesión de la
      computadora: dura lo que eligió el equipo (decisión 5).
    - Si algo falla (un Telegram viejo, el servidor, una firma vencida, una cuenta que no es del equipo), el lanzador
      abre la dirección sola, donde se entra con el QR, y lo dice en palabras, nunca con un error técnico.
    - El lanzador puede pedirle sólo a este mismo sitio (`connect-src 'self'`). El QR sigue para una computadora sin
      Telegram.

## Qué texto reemplaza a cuál

- **ADR 0022, decisión 2,** "una sola web, responsive, que se instala en el celular": la web sigue
  siendo una sola, pero en el celular se abre como Mini App de Telegram, no como web instalable.
  "Agregar a la pantalla de inicio" ya estaba descartado (ROADMAP).
- **Decisión 4,** "Leda ofrece el acceso; nadie lo pide, y no vence": Leda ofrece un botón que abre la
  Mini App donde corresponde (decisiones 1 y 2). Los enlaces de un solo uso se retiran (decisión 11).
- **Decisión 6,** "los administradores entran por el bot de administración… piden el enlace": entran
  por la Mini App de ese bot o, en la computadora, con el QR que lleva a ese bot.
- **Decisión 12,** "el enlace de un solo uso se canjea por una cookie": la sesión nace de la firma de
  Telegram o del QR (decisiones 7 a 9).

## Consecuencias

- Nadie vuelve a pedir un enlace. En el celular se toca un botón; en la computadora se escanea un QR
  una vez.
- La identidad es siempre la cuenta de Telegram, la misma que usa el chat.
- Hasta la VPS, la dirección del túnel cambia: los botones viejos dejan de andar, y la computadora
  vuelve a escanear el QR cuando la dirección cambia.
- `PENDIENTE`: "Iniciar sesión con Telegram" (el botón oficial) queda para la VPS, si hiciera falta.
