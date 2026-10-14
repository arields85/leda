// El lanzador de la Mini App (ADR 0024; MA-2, decisión del usuario del 2026-10-14). Lo carga la
// página de `/app/abrir/...` (src/leda/entrar_con_telegram.py), lo único que se deja enmarcar, y
// sólo por Telegram. Después de `/app/telegram-web-app.js`, que da `Telegram.WebApp`.
//
// - En el celular (`ios`, `android`) y fuera de Telegram, sigue a la web: la misma puerta y el
//   mismo destino (`/app/abrir/e/<espacio>/?tarea=…` → `/app/e/<espacio>/?tarea=…`), con el
//   fragmento que dejó Telegram (la firma de la persona) para que la web entre con ella.
// - En Telegram de la computadora (`tdesktop`, `macos`, `weba`, `webk`, `unknown` dentro de un
//   marco…), donde la web no se puede mostrar, la abre en el navegador (`openLink`), sin el
//   fragmento: ahí se entra con el QR. Adentro de Telegram queda "Abrí Leda en el navegador", con
//   un botón para volver a abrirla.
//
// No pide nada al servidor, no lee ni guarda una sesión y no tiene formularios.
(function (win) {
  'use strict';

  var TELEFONOS = ['ios', 'android', 'android_x'];
  var DESTINO = /^\/app\/abrir\/(e\/[a-z0-9][a-z0-9-]{0,63}\/|admin\/)$/;
  var TEXTO = 'Abrí Leda en el navegador';
  var BOTON = 'Abrir de nuevo';

  // La web a la que lleva, siempre de este mismo sitio y siempre bajo `/app/`.
  function destino(lugar) {
    var encontrado = DESTINO.exec(lugar.pathname);
    return encontrado ? '/app/' + encontrado[1] + lugar.search : '/app/';
  }

  function enUnMarco() {
    try {
      return win.top !== win.self;
    } catch (e) {
      return true;
    }
  }

  var app = win.Telegram && win.Telegram.WebApp;
  var plataforma = (app && app.platform) || 'unknown';
  var enTelegram = Boolean(app && app.initData);
  var camino = destino(win.location);

  if (TELEFONOS.indexOf(plataforma) >= 0 || (!enTelegram && !enUnMarco())) {
    win.location.replace(camino + win.location.hash);
    return;
  }

  // En la computadora: la web en el navegador, sin nada de lo que Telegram puso en el fragmento.
  var direccion = win.location.origin + camino;

  function abrir() {
    if (app && typeof app.openLink === 'function') {
      try {
        app.openLink(direccion);
        return;
      } catch (e) {
        // Un Telegram viejo: abajo, el navegador.
      }
    }
    win.open(direccion, '_blank', 'noopener');
  }

  try {
    if (app) app.ready();
  } catch (e) {
    // Sin `ready`, Telegram igual muestra la página.
  }
  var documento = win.document;
  var lugar = documento.getElementById('lanzador') || documento.body;
  var texto = documento.createElement('p');
  texto.textContent = TEXTO;
  var boton = documento.createElement('button');
  boton.type = 'button';
  boton.textContent = BOTON;
  boton.addEventListener('click', abrir);
  lugar.appendChild(texto);
  lugar.appendChild(boton);
  abrir();
})(window);
