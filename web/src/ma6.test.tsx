import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';
import { me, task, view } from './test/fixtures';

// MA-6 (the user's decision, 2026-10-14 night): Dirección's tabs are "Mis tareas" and "Áreas".
// "Áreas" opens with one card per area (its name, its referente and the non-zero counters, in the
// tiles' colours); a card opens that area's tasks with the list and the week, and "‹ Áreas" goes
// back. The address keeps the state, so a reload and the browser's back button work.

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

const tabs = [
  { vista: 'tus' as const, titulo: 'Mis tareas' },
  { vista: 'areas' as const, titulo: 'Áreas' },
];

const OVERVIEW = {
  vista: 'areas',
  titulo: 'Áreas',
  areas: [
    {
      id: 'a1',
      nombre: 'OT y automatización',
      referente: 'Marcos',
      panel: { vencida: 2, trabada: 1, en_curso: 0, entregada: 1 },
      sin_empezar: 1,
      activas: 4,
    },
    {
      id: 'a2',
      nombre: 'Compras',
      referente: null,
      panel: { vencida: 0, trabada: 0, en_curso: 0, entregada: 0 },
      sin_empezar: 0,
      activas: 0,
    },
  ],
};

const AREA = view({
  vista: 'areas' as never,
  titulo: 'OT y automatización',
  tareas: [task({ id: 't7', titulo: 'Programar el PLC', responsable: 'Marcos' })],
});

function routes(): Record<string, Reply> {
  return {
    'GET /app/api/yo': ok(me({ persona: 'Ismael', vistas: tabs, carga_tareas: true, crea_objetivos: true })),
    'GET /app/api/tareas?vista=tus': ok(view({ titulo: 'Mis tareas' })),
    'GET /app/api/tareas?vista=areas': ok(OVERVIEW),
    'GET /app/api/tareas?vista=areas&area=a1': ok(AREA),
  };
}

beforeEach(() => {
  window.history.replaceState(null, '', '/app/');
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete (window as unknown as { Telegram?: unknown }).Telegram;
});

describe('«Áreas», Dirección\'s view', () => {
  it('opens with one card per area: name, referente and only the counters with something', async () => {
    serve(routes());
    render(<App />);
    fireEvent.click(await screen.findByRole('tab', { name: 'Áreas' }));
    const list = await screen.findByRole('list', { name: 'Áreas' });
    const [first, second] = within(list).getAllByRole('button');
    expect(first).toHaveTextContent('OT y automatización');
    expect(first).toHaveTextContent('Marcos');
    expect(within(first).getByText('2 VENCIDAS')).toHaveClass('text-vencida');
    expect(within(first).getByText('1 ESPERANDO')).toHaveClass('text-trabada');
    expect(within(first).getByText('1 ENTREGADA')).toHaveClass('text-entregada');
    expect(within(first).getByText('1 SIN EMPEZAR')).toBeInTheDocument();
    expect(within(first).queryByText(/EN CURSO/)).toBeNull();
    // Nothing open: said in gray.
    expect(within(second).getByText('Sin tareas abiertas.')).toHaveClass('text-ink-dim');
    // The overview has no tiles nor week of its own: each card has its numbers.
    expect(screen.queryByRole('region', { name: 'Tareas por estado' })).toBeNull();
    expect(window.location.search).toBe('?vista=areas');
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Áreas');
  });

  it("a card opens that area's tasks with the counters, the week and «‹ Áreas» to go back", async () => {
    const calls = serve(routes());
    window.history.replaceState(null, '', '/app/?vista=areas');
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: /OT y automatización/ }));
    expect(await screen.findByText('Programar el PLC')).toBeInTheDocument();
    expect(calls).toContain('GET /app/api/tareas?vista=areas&area=a1');
    expect(window.location.search).toBe('?vista=areas&area=a1');
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('OT y automatización');
    expect(screen.getByRole('region', { name: 'Tareas por estado' })).toBeInTheDocument();
    // The bottom buttons stay.
    expect(screen.getByRole('button', { name: '> Nueva tarea' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '‹ Áreas' }));
    expect(await screen.findByRole('list', { name: 'Áreas' })).toBeInTheDocument();
    await waitFor(() => expect(window.location.search).toBe('?vista=areas'));
  });

  it('a reload of an area opens it, and «‹ Áreas» still goes to the overview', async () => {
    serve(routes());
    window.history.replaceState(null, '', '/app/?vista=areas&area=a1');
    render(<App />);
    expect(await screen.findByText('Programar el PLC')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '‹ Áreas' }));
    expect(await screen.findByRole('list', { name: 'Áreas' })).toBeInTheDocument();
    expect(window.location.search).toBe('?vista=areas');
  });

  it("the browser's back button goes from an area to the overview", async () => {
    serve(routes());
    window.history.replaceState(null, '', '/app/?vista=areas');
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: /OT y automatización/ }));
    await screen.findByText('Programar el PLC');
    await act(async () => {
      window.history.replaceState(null, '', '/app/?vista=areas');
      window.dispatchEvent(new PopStateEvent('popstate'));
    });
    expect(await screen.findByRole('list', { name: 'Áreas' })).toBeInTheDocument();
  });

  it("the chat's button to the whole team (?vista=equipo) opens «Áreas»", async () => {
    const calls = serve(routes());
    window.history.replaceState(null, '', '/app/?vista=equipo');
    render(<App />);
    expect(await screen.findByRole('list', { name: 'Áreas' })).toBeInTheDocument();
    expect(calls).not.toContain('GET /app/api/tareas?vista=equipo');
  });
});

// The area in the address is only a hint (review of MA-6, App.tsx:117): a stale or crafted address
// never shows what the person cannot see (the server refuses it anyway) nor leaves her stuck.
describe('an area in the address that does not fit', () => {
  it('an area that does not exist (or is not of this space) falls back to the overview', async () => {
    const calls = serve(routes());
    window.history.replaceState(null, '', '/app/?vista=areas&area=otra');
    render(<App />);
    expect(await screen.findByRole('list', { name: 'Áreas' })).toBeInTheDocument();
    expect(calls).toContain('GET /app/api/tareas?vista=areas&area=otra');
    expect(window.location.search).toBe('?vista=areas');
    expect(screen.queryByText('No se pudo cargar la página.')).toBeNull();
    expect(screen.queryByRole('button', { name: '‹ Áreas' })).toBeNull();
  });

  it("someone without «Áreas» gets her own tasks, and Telegram's «Atrás» stays hidden", async () => {
    const back = { show: vi.fn(), hide: vi.fn(), onClick: vi.fn(), offClick: vi.fn() };
    (window as unknown as { Telegram: unknown }).Telegram = {
      WebApp: { initData: 'query_id=1&hash=abc', platform: 'ios', ready: vi.fn(), expand: vi.fn(), BackButton: back },
    };
    const calls = serve({
      ...routes(),
      'GET /app/api/yo': ok(me({ persona: 'Marcos', vistas: [{ vista: 'tus', titulo: 'Mis tareas' }] })),
    });
    window.history.replaceState(null, '', '/app/?vista=areas&area=a1');
    render(<App />);
    expect(await screen.findByText('Configurar alarmas del SCADA')).toBeInTheDocument();
    expect(calls.some((c) => c.includes('vista=areas'))).toBe(false);
    expect(screen.queryByRole('button', { name: '‹ Áreas' })).toBeNull();
    expect(back.show).not.toHaveBeenCalled();
  });
});
