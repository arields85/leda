// El lanzador de la Mini App (ADR 0024; MA-2, decisión del usuario del 2026-10-14). Lo carga la
// página de `/app/abrir/...` (src/leda/entrar_con_telegram.py), lo único que se deja enmarcar, y
// sólo por Telegram. Después de `/app/telegram-web-app.js`, que da `Telegram.WebApp`.
//
// - En el celular (`ios`, `android`) y fuera de Telegram, sigue a la web: la misma puerta y el
//   mismo destino (`/app/abrir/e/<espacio>/?tarea=…` → `/app/e/<espacio>/?tarea=…`), con el
//   fragmento que dejó Telegram (la firma de la persona) para que la web entre con ella.
// - En Telegram de la computadora (`tdesktop`, `macos`, `weba`, `webk`, `unknown` dentro de un
//   marco…), donde la web no se puede mostrar, la abre en el navegador (`openLink`). Antes le pide
//   al servidor el pase de la computadora con la firma de Telegram (MA-5, decisión del usuario del
//   2026-10-14, noche): un pase de un solo uso que vence al minuto, con el que el navegador queda
//   adentro. Si no se pudo (un Telegram viejo, el servidor caído, una firma vencida, una cuenta que
//   no es del equipo), abre la dirección sola, donde se entra con el QR, y lo dice en palabras.
//   Adentro de Telegram queda "Abrí Leda en el navegador", con un botón para volver a abrirla.
//
// Sólo le pide a este mismo sitio, no lee ni guarda una sesión, no tiene formularios y nunca
// muestra el pase.
(function (win) {
  'use strict';

  var TELEFONOS = ['ios', 'android', 'android_x'];
  var DESTINO = /^\/app\/abrir\/(e\/([a-z0-9][a-z0-9-]{0,63})\/|admin\/)$/;
  var PASE = /^\/app\/(admin\/)?entrar\/pase\/[0-9a-f-]{36}\/[A-Za-z0-9_-]{1,128}$/;
  var TEXTO = 'Abrí Leda en el navegador';
  var SIN_PASE = 'En el navegador, entrá escaneando el código QR con el celular.';
  var BOTON = 'Abrir de nuevo';
  // Lo más que se espera el pase antes de abrir la dirección sola.
  var ESPERA_MS = 6000;

  var encontrado = DESTINO.exec(win.location.pathname);

  // La web a la que lleva, siempre de este mismo sitio y siempre bajo `/app/`.
  function destino(lugar) {
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

  // El pase de la computadora: `{pase}` con su dirección, o `{aviso}` con lo que se le dice a la
  // persona (la cuenta que no es del equipo, en las palabras del servidor; si no, el QR).
  function pedirElPase() {
    if (!enTelegram || !encontrado || typeof win.fetch !== 'function') {
      return Promise.resolve({ aviso: SIN_PASE });
    }
    var admin = encontrado[1] === 'admin/';
    var cuerpo = admin ? { init_data: app.initData } : { espacio: encontrado[2], init_data: app.initData };
    var pedido = win.fetch(admin ? '/app/admin/api/entrar/pase' : '/app/api/entrar/pase', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(cuerpo),
    }).then(function (respuesta) {
      return respuesta.json().then(function (datos) {
        if (respuesta.status === 201 && datos && typeof datos.direccion === 'string' &&
            PASE.test(datos.direccion)) {
          return { pase: datos.direccion };
        }
        if (respuesta.status === 403 && datos && typeof datos.texto === 'string' && datos.texto) {
          return { aviso: datos.texto };
        }
        return { aviso: SIN_PASE };
      });
    }).catch(function () {
      return { aviso: SIN_PASE };
    });
    var espera = new Promise(function (listo) {
      win.setTimeout(function () {
        listo({ aviso: SIN_PASE });
      }, ESPERA_MS);
    });
    return Promise.race([pedido, espera]);
  }

  function mostrar(direccion, aviso) {
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

    var documento = win.document;
    var lugar = documento.getElementById('lanzador') || documento.body;
    var texto = documento.createElement('p');
    texto.textContent = TEXTO;
    lugar.appendChild(texto);
    if (aviso) {
      var detalle = documento.createElement('p');
      detalle.textContent = aviso;
      lugar.appendChild(detalle);
    }
    var boton = documento.createElement('button');
    boton.type = 'button';
    boton.textContent = BOTON;
    // Otra vez el mismo pase: si ya se usó, el servidor lleva a la misma página, que el
    // navegador ya abrió con su sesión (o, sin ella, con el QR).
    boton.addEventListener('click', abrir);
    lugar.appendChild(boton);
    abrir();
  }

  try {
    if (app) app.ready();
  } catch (e) {
    // Sin `ready`, Telegram igual muestra la página.
  }
  pedirElPase().then(function (resultado) {
    if (resultado.pase) {
      mostrar(win.location.origin + resultado.pase + '?a=' + encodeURIComponent(camino), null);
    } else {
      mostrar(win.location.origin + camino, resultado.aviso);
    }
  });
})(window);
