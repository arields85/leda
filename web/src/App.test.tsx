import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { Me, ViewData } from './api';
import { App } from './App';
import { finished, me, task, view } from './test/fixtures';

type Route = { status: number; body?: unknown };

function serve(routes: Record<string, Route>) {
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

const ok = (body: Me | ViewData): Route => ({ status: 200, body });

beforeEach(() => {
  window.history.replaceState(null, '', '/app/');
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('App', () => {
  it('shows a member only her view, with no switch', async () => {
    serve({
      'GET /app/api/yo': ok(me({ chat_con_leda: 'https://t.me/LedaCoreWorkBot' })),
      'GET /app/api/tareas?vista=tus': ok(view()),
    });
    render(<App />);
    expect(await screen.findByText('Configurar alarmas del SCADA')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Tus tareas');
    expect(screen.getByText('LEDA · COREWORK')).toBeInTheDocument();
    expect(screen.getByText('SEM 44 · LUN 26.10')).toBeInTheDocument();
    expect(screen.queryByRole('navigation', { name: 'Vistas' })).toBeNull();
    // MA-3: "> consultar a leda" is gone; in a browser, "Volver al chat" opens the bot's chat.
    expect(screen.queryByText('> consultar a leda')).toBeNull();
    expect(screen.getByRole('link', { name: 'Volver al chat' })).toHaveAttribute(
      'href',
      'https://t.me/LedaCoreWorkBot',
    );
  });

  it('a long space name shrinks inside the header instead of pushing the page sideways', async () => {
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view()),
    });
    render(<App />);
    const space = await screen.findByText('LEDA · COREWORK');
    // A truncated flex item only shrinks with min-w-0; jsdom has no layout, the phone confirms it.
    expect(space).toHaveClass('min-w-0', 'truncate');
    expect(screen.getByRole('main')).toHaveClass('min-w-0');
  });

  it('without the bot address there is no button to consult Leda', async () => {
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view()),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.queryByText('> consultar a leda')).toBeNull();
  });

  it('shows the finished tasks apart, after the open ones', async () => {
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view({ terminadas: [finished()] })),
    });
    const { container } = render(<App />);
    const done = await screen.findByText('Relevar tableros de la línea 2');
    const open = screen.getByText('Configurar alarmas del SCADA');
    expect(open.compareDocumentPosition(done) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getByRole('region', { name: 'Terminadas en los últimos 30 días' })).toBeInTheDocument();
    expect(container.querySelectorAll('article[data-task]')).toHaveLength(1);
  });

  it('switches only between the views the server gave', async () => {
    const calls = serve({
      'GET /app/api/yo': ok(
        me({
          vistas: [
            { vista: 'tus', titulo: 'Tus tareas' },
            { vista: 'sector', titulo: 'Tu sector' },
          ],
        }),
      ),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/tareas?vista=sector': ok(
        view({ vista: 'sector', titulo: 'Tu sector', tareas: [task({ id: 's', titulo: 'Ordenar el depósito', responsable: 'Lucas', papel: null })] }),
      ),
    });
    render(<App />);
    await screen.findByRole('navigation', { name: 'Vistas' });
    const tabs = screen.getAllByRole('tab').map((b) => b.textContent);
    expect(tabs).toEqual(['Tus tareas', 'Tu sector']);
    expect(screen.queryByText('El equipo')).toBeNull();

    fireEvent.click(screen.getByRole('tab', { name: 'Tu sector' }));
    expect(await screen.findByText('Ordenar el depósito')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Tu sector');
    expect(window.location.search).toBe('?vista=sector');
    expect(calls).not.toContain('GET /app/api/tareas?vista=equipo');
  });

  it('ignores a view in the address that the person does not have', async () => {
    window.history.replaceState(null, '', '/app/?vista=equipo');
    const calls = serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view()),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(calls).not.toContain('GET /app/api/tareas?vista=equipo');
  });

  it('a closed session never asks for a link: without its space, it says to open Leda from Telegram', async () => {
    serve({ 'GET /app/api/yo': { status: 401, body: { error: 'sin_sesion' } } });
    render(<App />);
    expect(await screen.findByText('Entrá desde Telegram.')).toBeInTheDocument();
    expect(screen.queryByText(/enlace/)).toBeNull();
    expect(screen.queryByText('> consultar a leda')).toBeNull();
  });

  it('a failure shows plain words, never technical details', async () => {
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': { status: 503, body: { error: 'no_disponible' } },
    });
    const { container } = render(<App />);
    expect(await screen.findByText('No se pudo cargar la página.')).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/503|no_disponible|error/i);
    expect(screen.getByRole('button', { name: /probar de nuevo/ })).toBeInTheDocument();
  });

  it('says so when there is nothing open', async () => {
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(
        view({
          tareas: [],
          activas: 0,
          panel: { vencida: 0, trabada: 0, en_curso: 0, entregada: 0 },
          terminadas: [finished()],
        }),
      ),
    });
    render(<App />);
    expect(await screen.findByText('No tenés tareas abiertas.')).toBeInTheDocument();
    expect(screen.getByText('Relevar tableros de la línea 2')).toBeInTheDocument();
    // MA-3: no total of open tasks anywhere (the user's decision).
    expect(screen.getByRole('banner')).not.toHaveTextContent(/activas/);
  });

  it('salir asks once and closes the session', async () => {
    const calls = serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'POST /app/salir': { status: 204 },
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: /salir/ }));
    expect(calls).not.toContain('POST /app/salir');
    fireEvent.click(screen.getByRole('button', { name: 'sí, salir' }));
    expect(await screen.findByText('Cerraste la sesión.')).toBeInTheDocument();
    expect(calls).toContain('POST /app/salir');
  });

  it('fits a 390px phone: nothing has a fixed width wider than the screen', async () => {
    const long = 'Revisar-las-comunicaciones-de-la-comprimidora-de-la-planta-norte-sin-espacios';
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(
        view({
          tareas: [
            task({ titulo: long }),
            task({
              id: 'b',
              marca: 'en_curso',
              marcas: ['en_curso'],
              estado: 'en_curso',
              quedan_dias_habiles: 20,
              barra: Array.from({ length: 30 }, (_, i) => ({
                fecha: `2026-11-${String(i + 1).padStart(2, '0')}`,
                momento: i < 10 ? 'pasado' : i === 10 ? 'hoy' : 'futuro',
              })),
            }),
          ],
        }),
      ),
    });
    const { container } = render(<App />);
    await screen.findByText(long);
    for (const element of container.querySelectorAll<HTMLElement>('*')) {
      const classes = element.getAttribute('class') ?? '';
      for (const [, px] of classes.matchAll(/(?:^|\s)(?:min-)?w-\[(\d+)px\]/g)) {
        expect(Number(px)).toBeLessThanOrEqual(390);
      }
      for (const property of ['width', 'minWidth'] as const) {
        const value = element.style[property];
        if (value.endsWith('px')) expect(parseFloat(value)).toBeLessThanOrEqual(390);
      }
    }
    // Long titles wrap instead of pushing the page sideways.
    expect(screen.getByText(long)).toHaveClass('wrap-break-word');
    // The outer column fills the phone, with the 20px gutter of the design.
    expect(container.firstElementChild).toHaveClass('w-full', 'px-5');
  });
});
