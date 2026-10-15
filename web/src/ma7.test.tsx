import { act, fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminApp } from './admin/AdminApp';
import { App } from './App';
import { POLL_MS } from './components/SignIn';
import { adminMe, options } from './test/adminFixtures';
import { me, view } from './test/fixtures';

// MA-7, the user's decision (2026-10-15): the computer's session stays remembered (closing the tab
// does not close it), and a "Cerrar sesión" comes back only in a browser outside Telegram, under
// the name and the area at the top right, in the team's page and in the administration. Never in
// the Mini App: each opening identifies the person, and a QR cannot be scanned from inside it.

type Reply = { status: number; body?: unknown };
const ok = (body: unknown): Reply => ({ status: 200, body });

function serve(routes: Record<string, Reply>) {
  const calls: string[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      calls.push(key);
      const route = routes[key];
      if (!route) return new Response('{"error":"no_existe"}', { status: 404 });
      return new Response(route.body === undefined ? null : JSON.stringify(route.body), {
        status: route.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }),
  );
  return calls;
}

function miniApp() {
  const app = {
    initData: 'query_id=1&hash=abc',
    platform: 'ios',
    ready: vi.fn(),
    expand: vi.fn(),
    close: vi.fn(),
    BackButton: { show: vi.fn(), hide: vi.fn(), onClick: vi.fn(), offClick: vi.fn() },
  };
  (window as unknown as { Telegram: unknown }).Telegram = { WebApp: app };
  return app;
}

const TEAM = {
  'GET /app/api/yo': ok(me({ persona: 'Marcos Tarquini', area: 'Automatización' })),
  'GET /app/api/tareas?vista=tus': ok(view()),
};

const ADMIN = {
  'POST /app/admin/api/entrar-telegram': ok({ ok: true }),
  'GET /app/admin/api/yo': ok(adminMe()),
  'GET /app/admin/api/espacios/w1/opciones': ok(options()),
};

async function openTeam(routes: Record<string, Reply> = {}) {
  const calls = serve({ ...TEAM, ...routes });
  render(<App />);
  await screen.findByText('Configurar alarmas del SCADA');
  return calls;
}

async function openAdmin(routes: Record<string, Reply> = {}) {
  window.history.replaceState(null, '', '/app/admin/');
  const calls = serve({ ...ADMIN, ...routes });
  render(<AdminApp />);
  await screen.findAllByText(/Cargar tarea|Crear objetivo/);
  return calls;
}

beforeEach(() => {
  window.history.replaceState(null, '', '/app/');
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  delete (window as unknown as { Telegram?: unknown }).Telegram;
});

describe('"Cerrar sesión" in the team page', () => {
  it('in the computer browser, goes under the name and the area at the top right', async () => {
    await openTeam();
    const who = within(screen.getByRole('banner')).getByTestId('who');
    const button = within(who).getByRole('button', { name: 'Cerrar sesión' });
    // Under the name and the area, in the same right-aligned block.
    const area = within(who).getByTestId('who-area');
    expect(area.compareDocumentPosition(button) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    // Sober: small and dim, never yellow; and only there.
    expect(button).toHaveClass('text-small', 'text-ink-dim');
    expect(button.className).not.toMatch(/yellow|amber|warn/);
    expect(screen.getAllByRole('button', { name: /cerrar sesión/i })).toEqual([button]);
  });

  it('never inside the Mini App', async () => {
    miniApp();
    await openTeam();
    expect(screen.queryByRole('button', { name: /cerrar sesión|salir/i })).toBeNull();
  });

  it('asks once, closes the session on the server and says so, with the way back in', async () => {
    const calls = await openTeam({ 'POST /app/salir': { status: 204 } });
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar sesión' }));
    expect(screen.getByText(/escanear el código otra vez/)).toBeInTheDocument();
    expect(calls).not.toContain('POST /app/salir');
    fireEvent.click(screen.getByRole('button', { name: 'sí, cerrar' }));
    expect(await screen.findByText('Cerraste la sesión.')).toBeInTheDocument();
    expect(calls).toContain('POST /app/salir');
    // The page no longer shows who was in, nor the tasks, nor the button.
    expect(screen.queryByTestId('who')).toBeNull();
    expect(screen.queryByText('Configurar alarmas del SCADA')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Cerrar sesión' })).toBeNull();
  });

  it('"no, seguir" keeps the session', async () => {
    const calls = await openTeam();
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar sesión' }));
    fireEvent.click(screen.getByRole('button', { name: 'no, seguir' }));
    expect(screen.getByRole('button', { name: 'Cerrar sesión' })).toBeInTheDocument();
    expect(calls).not.toContain('POST /app/salir');
    expect(screen.getByText('Configurar alarmas del SCADA')).toBeInTheDocument();
  });

  it('after closing, entering again with Telegram brings the person back to her tasks', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const calls = await openTeam({
      'GET /app/api/yo': ok(me({ persona: 'Marcos Tarquini', area: 'Automatización', espacio_slug: 'corework' })),
      'POST /app/salir': { status: 204 },
      'POST /app/api/entrar/qr': {
        status: 201,
        body: { pedido_id: 'p-1', enlace: 'https://t.me/Leda_PM_bot?start=compu_abc', qr: ['10', '01'] },
      },
      'GET /app/api/entrar/qr/p-1': ok({ estado: 'adentro' }),
    });
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar sesión' }));
    fireEvent.click(screen.getByRole('button', { name: 'sí, cerrar' }));
    expect(await screen.findByText('Cerraste la sesión.')).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: 'Código para entrar con Telegram' })).toBeInTheDocument();
    const asked = (key: string) => calls.filter((c) => c === key).length;
    const before = { me: asked('GET /app/api/yo'), tasks: asked('GET /app/api/tareas?vista=tus') };
    // The phone approves the QR in Telegram: the page asks the server and finds the person in.
    await act(async () => {
      vi.advanceTimersByTime(POLL_MS + 10);
    });
    expect(await screen.findByText('Configurar alarmas del SCADA')).toBeInTheDocument();
    expect(asked('GET /app/api/entrar/qr/p-1')).toBe(1);
    expect(asked('GET /app/api/yo')).toBe(before.me + 1);
    expect(asked('GET /app/api/tareas?vista=tus')).toBe(before.tasks + 1);
    expect(screen.queryByText('Cerraste la sesión.')).toBeNull();
    expect(within(screen.getByTestId('who')).getByText('Marcos Tarquini')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cerrar sesión' })).toBeInTheDocument();
  });

  it('a failure says so and keeps the page', async () => {
    await openTeam({ 'POST /app/salir': { status: 500, body: { error: 'interno' } } });
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar sesión' }));
    fireEvent.click(screen.getByRole('button', { name: 'sí, cerrar' }));
    expect(await screen.findByText(/No se pudo cerrar la sesión/)).toBeInTheDocument();
    expect(screen.queryByText('Cerraste la sesión.')).toBeNull();
    expect(screen.getByText('Configurar alarmas del SCADA')).toBeInTheDocument();
  });
});

describe('"Cerrar sesión" in the administration', () => {
  it('in the computer browser, goes under the name at the top right, not at the bottom', async () => {
    await openAdmin();
    const who = within(screen.getByRole('banner')).getByTestId('who');
    expect(who).toHaveTextContent('Ariel');
    expect(within(who).getByRole('button', { name: 'Cerrar sesión' })).toBeInTheDocument();
    expect(screen.queryByRole('contentinfo')).toBeNull();
    expect(screen.queryByRole('button', { name: /salir/ })).toBeNull();
  });

  it('never inside the Mini App', async () => {
    miniApp();
    await openAdmin();
    expect(screen.queryByRole('button', { name: /cerrar sesión|salir/i })).toBeNull();
  });

  it('closes the administration session, not the team one', async () => {
    const calls = await openAdmin({ 'POST /app/admin/salir': { status: 204 } });
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar sesión' }));
    fireEvent.click(screen.getByRole('button', { name: 'sí, cerrar' }));
    expect(await screen.findByText('Cerraste la sesión.')).toBeInTheDocument();
    expect(calls).toContain('POST /app/admin/salir');
    expect(calls).not.toContain('POST /app/salir');
    expect(screen.queryByTestId('who')).toBeNull();
  });
});
