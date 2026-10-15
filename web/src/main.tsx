import '@fontsource/jetbrains-mono/latin-400.css';
import '@fontsource/jetbrains-mono/latin-500.css';
import '@fontsource/jetbrains-mono/latin-700.css';
import '@fontsource/jetbrains-mono/latin-800.css';
import './index.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { AdminApp } from './admin/AdminApp';
import { App } from './App';
import { stopFocusZoomOnIOS } from './admin/viewport';
import { Notice } from './components/Notice';
import { isAdminDoor, spaceOfPath } from './door';
import { bootTelegram, enterTheMiniApp, FREE_PINCH_ZOOM_IN_MINI_APP, telegramWebApp } from './telegram';

const telegram = telegramWebApp();

// Before the first render, so no control is ever focused with the zoom still on (J2-10). Inside
// the Mini App it can be skipped with a single constant, to try pinch-zoom on the phone (ADR 0024,
// decision 6).
if (!(telegram && FREE_PINCH_ZOOM_IN_MINI_APP)) stopFocusZoomOnIOS();

const root = document.getElementById('root');
const admin = isAdminDoor(window.location.pathname);
const page = admin ? <AdminApp /> : <App />;

async function start(target: HTMLElement) {
  const view = createRoot(target);
  if (!telegram) {
    view.render(<StrictMode>{page}</StrictMode>);
    return;
  }
  // Inside Telegram: the signature goes to the door before anything else (ADR 0024, decision 7);
  // an expired one still lets in a person whose session is good (MA-5, `enterTheMiniApp`).
  bootTelegram(telegram);
  view.render(
    <StrictMode>
      <Notice title="Cargando…" />
    </StrictMode>,
  );
  const entry = await enterTheMiniApp(admin ? 'administracion' : 'equipo',
                                      spaceOfPath(window.location.pathname), telegram.initData);
  if (entry.kind === 'refused') {
    view.render(
      <StrictMode>
        <div className="mx-auto flex w-full max-w-[32rem] flex-col px-5">
          <Notice title="No se pudo entrar.">
            <p className="m-0">{entry.text}</p>
          </Notice>
        </div>
      </StrictMode>,
    );
    return;
  }
  // In, or the signature could not be sent: the page shows what its session allows.
  view.render(<StrictMode>{page}</StrictMode>);
}

if (root) void start(root);
