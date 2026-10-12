import '@fontsource/jetbrains-mono/latin-400.css';
import '@fontsource/jetbrains-mono/latin-500.css';
import '@fontsource/jetbrains-mono/latin-700.css';
import '@fontsource/jetbrains-mono/latin-800.css';
import './index.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { AdminApp } from './admin/AdminApp';
import { App } from './App';
import { isAdminDoor } from './door';

const root = document.getElementById('root');
if (root) {
  createRoot(root).render(
    <StrictMode>
      {isAdminDoor(window.location.pathname) ? <AdminApp /> : <App />}
    </StrictMode>,
  );
}
