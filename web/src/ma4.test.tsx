import { fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';
import { me, view } from './test/fixtures';

// MA-4, the user's last adjustments after the iPhone and computer test of MA-2 and MA-3: the name
// and the area at the top right instead of the week, no "Volver al chat" nor "salir", "> Nuevo
// objetivo" at the bottom next to "> Nueva tarea", and the whole width on a computer.

type Reply = { status: number; body?: unknown };
const ok = (body: unknown): Reply => ({ status: 200, body });

function serve(routes: Record<string, Reply>) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const route = routes[`${init?.method ?? 'GET'} ${url}`];
      if (!route) return new Response('{"error":"no_existe"}', { status: 404 });
      return new Response(route.body === undefined ? null : JSON.stringify(route.body), {
        status: route.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }),
  );
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

const tabs = [
  { vista: 'tus' as const, titulo: 'Mis tareas' },
  { vista: 'equipo' as const, titulo: 'Mi área' },
  { vista: 'pedidas' as const, titulo: 'Mis pedidos' },
];

beforeEach(() => {
  window.history.replaceState(null, '', '/app/');
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete (window as unknown as { Telegram?: unknown }).Telegram;
});

describe('the name and the area at the top right (item 4)', () => {
  it('replace the week and the date, and stay on every tab', async () => {
    serve({
      'GET /app/api/yo': ok(me({ persona: 'Ismael Soschinski', area: 'Dirección', vistas: tabs })),
      'GET /app/api/tareas?vista=tus': ok(view({ titulo: 'Mis tareas' })),
      'GET /app/api/tareas?vista=equipo': ok(view({ vista: 'equipo', titulo: 'Mi área' })),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    const banner = screen.getByRole('banner');
    expect(banner).not.toHaveTextContent(/SEM \d+/);
    const who = within(banner).getByTestId('who');
    expect(who).toHaveTextContent('Ismael Soschinski');
    expect(within(who).getByTestId('who-area')).toHaveTextContent('Dirección');
    // On the top row, next to the space; the title line keeps only the title.
    expect(within(screen.getByTestId('title-line')).queryByTestId('who')).toBeNull();
    // The name is never cut.
    expect(who.className).not.toMatch(/truncate|ellipsis|line-clamp|whitespace-nowrap/);

    fireEvent.click(screen.getByRole('tab', { name: 'Mi área' }));
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Mi área');
    expect(within(screen.getByRole('banner')).getByTestId('who')).toHaveTextContent('Ismael Soschinski');
    expect(within(screen.getByRole('banner')).getByTestId('who-area')).toHaveTextContent('Dirección');
  });

  it('without an area, only the name', async () => {
    serve({ 'GET /app/api/yo': ok(me({ persona: 'Marcos', area: null })), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(within(screen.getByRole('banner')).getByTestId('who')).toHaveTextContent('Marcos');
    expect(screen.queryByTestId('who-area')).toBeNull();
  });
});

describe('no "Volver al chat" nor "salir" (item 5)', () => {
  it('inside the Mini App', async () => {
    miniApp();
    serve({ 'GET /app/api/yo': ok(me({ chat_con_leda: 'https://t.me/LedaCoreWorkBot' })), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.queryByText(/Volver al chat/)).toBeNull();
    expect(screen.queryByRole('button', { name: /salir|cerrar sesión/i })).toBeNull();
  });

  it('in the computer browser (only "Cerrar sesión", under the name, came back: MA-7)', async () => {
    serve({ 'GET /app/api/yo': ok(me({ chat_con_leda: 'https://t.me/LedaCoreWorkBot' })), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.queryByText(/Volver al chat/)).toBeNull();
    expect(screen.queryByRole('button', { name: /salir/ })).toBeNull();
    const button = within(screen.getByTestId('who')).getByRole('button', { name: 'Cerrar sesión' });
    expect(screen.getAllByRole('button', { name: /cerrar sesión/i })).toEqual([button]);
  });
});

describe('"> Nuevo objetivo" at the bottom (item 6)', () => {
  it('goes next to "> Nueva tarea", with the same style, and nothing stays under the tabs', async () => {
    serve({
      'GET /app/api/yo': ok(me({ persona: 'Ismael', crea_objetivos: true, carga_tareas: true, vistas: tabs })),
      'GET /app/api/tareas?vista=tus': ok(view()),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    const footer = screen.getByRole('contentinfo');
    const task = within(footer).getByRole('button', { name: '> Nueva tarea' });
    const objective = within(footer).getByRole('button', { name: '> Nuevo objetivo' });
    expect(objective.className).toBe(task.className);
    expect(task.parentElement).toBe(objective.parentElement);
    expect(screen.getByTestId('fixed-top')).not.toHaveTextContent(/nuevo objetivo/i);
    fireEvent.click(objective);
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Nuevo objetivo');
  });

  it('only to Dirección: a referente sees "> Nueva tarea" alone', async () => {
    serve({ 'GET /app/api/yo': ok(me({ carga_tareas: true })), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(within(screen.getByRole('contentinfo')).getByRole('button', { name: '> Nueva tarea' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /nuevo objetivo/i })).toBeNull();
  });
});

describe('the whole width on a computer (item 2)', () => {
  it('the page has no maximum width', async () => {
    serve({ 'GET /app/api/yo': ok(me()), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    const page = screen.getByTestId('fixed-top').parentElement as HTMLElement;
    expect(page).toHaveClass('w-full');
    expect(page.className).not.toMatch(/max-w-/);
  });
});
