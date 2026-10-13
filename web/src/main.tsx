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
import { isAdminDoor } from './door';

// Before the first render, so no control is ever focused with the zoom still on (J2-10).
stopFocusZoomOnIOS();

const root = document.getElementById('root');
if (root) {
  createRoot(root).render(
    <StrictMode>
      {isAdminDoor(window.location.pathname) ? <AdminApp /> : <App />}
    </StrictMode>,
  );
}
