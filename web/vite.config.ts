import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

// Leda's server serves the compiled web at /app/ (src/leda/web_app.py), same origin as the
// API, so the session cookie stays SameSite=Strict (ADR 0022, decisions 12 and 17).
export default defineConfig({
  base: '/app/',
  plugins: [react(), tailwindcss()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Never inline assets as data: URIs: the CSP only allows fonts from the same origin.
    assetsInlineLimit: 0,
    sourcemap: false,
  },
  // Port 8000 belongs to Leda itself; local previews use another one.
  server: { port: 5179, strictPort: true },
  preview: { port: 5179, strictPort: true },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: false,
  },
});
