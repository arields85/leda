import { fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminApp } from './admin/AdminApp';
import { App } from './App';
import { bootTelegram } from './telegram';
import { adminMe, options } from './test/adminFixtures';
import { detail, me, task, view } from './test/fixtures';

// MA-3, the user's corrections from the Mini App test on an iPhone: full screen, the task's detail
// inside the app, the bottom buttons, the tabs in one row, the title on one line and the
// "Por empezar" counter.

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

function miniApp(overrides: Record<string, unknown> = {}) {
  const back = { show: vi.fn(), hide: vi.fn(), onClick: vi.fn(), offClick: vi.fn() };
  const app = {
    initData: 'query_id=1&hash=abc',
    platform: 'ios',
    ready: vi.fn(),
    expand: vi.fn(),
    requestFullscreen: vi.fn(),
    isVersionAtLeast: vi.fn(() => true),
    close: vi.fn(),
    setHeaderColor: vi.fn(),
    setBackgroundColor: vi.fn(),
    BackButton: back,
    safeAreaInset: { top: 47, bottom: 34, left: 0, right: 0 },
    contentSafeAreaInset: { top: 46, bottom: 0, left: 0, right: 0 },
    onEvent: vi.fn(),
    ...overrides,
  };
  (window as unknown as { Telegram: unknown }).Telegram = { WebApp: app };
  return app;
}

beforeEach(() => {
  window.history.replaceState(null, '', '/app/');
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete (window as unknown as { Telegram?: unknown }).Telegram;
});

describe('full screen on a phone (item 3)', () => {
  it('asks Telegram for the whole screen on iOS and Android, inside the safe areas', () => {
    for (const platform of ['ios', 'android']) {
      const app = miniApp({ platform });
      const root = document.createElement('div');
      bootTelegram(app, root);
      expect(app.requestFullscreen).toHaveBeenCalled();
      expect(app.expand).not.toHaveBeenCalled();
      // The status bar plus Telegram's floating "Cerrar" and "…": nothing sits under them.
      expect(root.style.getPropertyValue('--tg-safe-top')).toBe('93px');
      expect(root.style.getPropertyValue('--tg-safe-bottom')).toBe('34px');
    }
  });

  it('falls back to expand() where full screen is not available', () => {
    for (const overrides of [
      { requestFullscreen: undefined },
      { isVersionAtLeast: vi.fn(() => false) },
      { platform: 'tdesktop' },
      { requestFullscreen: vi.fn(() => { throw new Error('old'); }) },
    ]) {
      const app = miniApp(overrides);
      bootTelegram(app, document.createElement('div'));
      expect(app.expand).toHaveBeenCalled();
    }
  });
});

describe("the task's detail inside the app (item 2)", () => {
  const routes = () => ({
    'GET /app/api/yo': ok(me()),
    'GET /app/api/tareas?vista=tus': ok(view({ tareas: [task({ id: 't9', titulo: 'Probar el módem' })] })),
    'POST /app/api/tareas/t9/detalle': ok(detail({ titulo: 'Probar el módem' })),
  });

  it('shows who does, reviews and asked for it, the criterion and both kinds of waits', async () => {
    serve(routes());
    render(<App />);
    fireEvent.click(await screen.findByRole('link', { name: 'Ver la tarea Probar el módem' }));
    const card = await screen.findByRole('article', { name: 'La tarea Probar el módem' });
    for (const text of ['La hace', 'Marcos', 'La revisa', 'Ismael', 'La pidió', 'Ariel', 'en curso',
      'Las alarmas suenan en la sala de control.', 'Cablear el tablero', 'Una tarea que no podés ver.',
      'Una foto de la pantalla']) {
      expect(within(card).getAllByText(new RegExp(text.replace('.', '\\.'))).length).toBeGreaterThan(0);
    }
    expect(within(card).getByText('VIE 30.10')).toBeInTheDocument();
  });

  it('"> volver" goes back to the list without closing the Mini App', async () => {
    const app = miniApp();
    serve(routes());
    render(<App />);
    fireEvent.click(await screen.findByRole('link', { name: 'Ver la tarea Probar el módem' }));
    await screen.findByRole('article', { name: 'La tarea Probar el módem' });
    fireEvent.click(screen.getByRole('button', { name: '> volver' }));
    expect(await screen.findByRole('link', { name: 'Ver la tarea Probar el módem' })).toBeInTheDocument();
    expect(screen.queryByRole('article', { name: 'La tarea Probar el módem' })).toBeNull();
    expect(app.close).not.toHaveBeenCalled();
  });

  it("Telegram's BackButton does the same", async () => {
    const app = miniApp();
    serve(routes());
    render(<App />);
    fireEvent.click(await screen.findByRole('link', { name: 'Ver la tarea Probar el módem' }));
    await screen.findByRole('article', { name: 'La tarea Probar el módem' });
    expect(app.BackButton.show).toHaveBeenCalled();
    const onBack = app.BackButton.onClick.mock.calls.at(-1)?.[0] as () => void;
    onBack();
    expect(await screen.findByRole('link', { name: 'Ver la tarea Probar el módem' })).toBeInTheDocument();
    expect(app.close).not.toHaveBeenCalled();
  });
});

describe('the bottom buttons (item 4)', () => {
  // "salir" and "Volver al chat" left both the Mini App and the browser in MA-4 (`ma4.test.tsx`).

  it('"> Nueva tarea" is the big button, only to whoever loads, and nothing under the tabs', async () => {
    serve({
      'GET /app/api/yo': ok(me({ carga_tareas: true, vistas: [{ vista: 'tus', titulo: 'Mis tareas' }, { vista: 'pedidas', titulo: 'Mis pedidos' }] })),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/carga/opciones': ok(options()),
    });
    render(<App />);
    const buttons = await screen.findAllByRole('button', { name: /nueva tarea/i });
    expect(buttons.map((b) => b.textContent)).toEqual(['> Nueva tarea']);
    expect(buttons[0].closest('footer')).not.toBeNull();
    expect(buttons[0]).toHaveClass('shadow-hard-ink', 'font-bold');
    fireEvent.click(buttons[0]);
    expect(await screen.findByRole('button', { name: '> volver a las tareas' })).toBeInTheDocument();
  });

  it('a member never sees "> Nueva tarea"', async () => {
    serve({ 'GET /app/api/yo': ok(me()), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.queryByRole('button', { name: /nueva tarea/i })).toBeNull();
  });

  it('the administration inside the Mini App has no "salir" either', async () => {
    miniApp();
    serve({
      'POST /app/admin/api/entrar-telegram': ok({ ok: true }),
      'GET /app/admin/api/yo': ok(adminMe()),
      'GET /app/admin/api/espacios/w1/opciones': ok(options()),
    });
    window.history.replaceState(null, '', '/app/admin/');
    render(<AdminApp />);
    await screen.findAllByText(/Cargar tarea|Crear objetivo/);
    expect(screen.queryByRole('button', { name: /salir|cerrar sesión/i })).toBeNull();
  });
});

describe('the tabs (item 5)', () => {
  const tabs = [
    { vista: 'tus' as const, titulo: 'Mis tareas' },
    { vista: 'sector' as const, titulo: 'Mi área' },
    { vista: 'pedidas' as const, titulo: 'Mis pedidos' },
  ];

  it('are real tabs in one row that never wraps, the selected one marked', async () => {
    serve({ 'GET /app/api/yo': ok(me({ vistas: tabs })), 'GET /app/api/tareas?vista=tus': ok(view({ titulo: 'Mis tareas' })) });
    render(<App />);
    const list = await screen.findByRole('tablist', { name: 'Vistas' });
    expect(list).toHaveClass('flex', 'flex-nowrap');
    expect(list.className).not.toMatch(/flex-wrap(?!-)|\bwrap\b/);
    const all = within(list).getAllByRole('tab');
    expect(all.map((t) => t.textContent)).toEqual(['Mis tareas', 'Mi área', 'Mis pedidos']);
    // Equal shares of one row (375 px less the page's 2 × 20 px: 111 px each), cut before wrapping.
    for (const tab of all) expect(tab).toHaveClass('flex-1', 'basis-0', 'min-w-0', 'truncate', 'whitespace-nowrap');
    expect(all[0]).toHaveAttribute('aria-selected', 'true');
    expect(all[1]).toHaveAttribute('aria-selected', 'false');
  });

  it('a referente\'s "Mi área" has no subtitle: the area is already top right (MA-4)', async () => {
    window.history.replaceState(null, '', '/app/?vista=sector');
    serve({
      'GET /app/api/yo': ok(me({ vistas: tabs, area: 'OT y automatización' })),
      'GET /app/api/tareas?vista=sector': ok(view({ vista: 'sector', titulo: 'Mi área', area_del_equipo: 'Software e interfaz HMI' })),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Mi área');
    expect(screen.queryByText('Software e interfaz HMI')).toBeNull();
    expect(screen.getAllByText('OT y automatización')).toHaveLength(1);
  });
});

describe('the title line, the counters and one screen (items 6 and 7, corrected)', () => {
  it('the title never wraps, and who is looking (top right since MA-4) is never cut', async () => {
    serve({ 'GET /app/api/yo': ok(me({ persona: 'Ariel De Simone' })), 'GET /app/api/tareas?vista=tus': ok(view({ titulo: 'Mis tareas', activas: 2 })) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    const line = screen.getByTestId('title-line');
    expect(line).toHaveClass('flex', 'flex-nowrap');
    const title = within(line).getByRole('heading', { level: 1 });
    expect(title).toHaveTextContent('Mis tareas');
    expect(title).toHaveClass('shrink-0', 'whitespace-nowrap');
    const who = within(screen.getByRole('banner')).getByTestId('who');
    expect(who).toHaveTextContent('Ariel De Simone');
    // Never cut: a long name goes on under itself, right-aligned.
    expect(who).not.toHaveClass('truncate');
    expect(who.className).not.toMatch(/ellipsis|line-clamp|whitespace-nowrap/);
    expect(who).toHaveClass('min-w-0', 'text-right', 'wrap-break-word');
    // "N activas" left the header.
    expect(screen.getByRole('banner')).not.toHaveTextContent(/activas/);
  });

  it('the counters are Vencidas · Sin empezar · En curso · Esperando · Entregadas, in one row', async () => {
    serve({ 'GET /app/api/yo': ok(me()), 'GET /app/api/tareas?vista=tus': ok(view({ activas: 3, sin_empezar: 2 })) });
    render(<App />);
    const strip = await screen.findByRole('region', { name: 'Tareas por estado' });
    expect(strip).toHaveClass('grid', 'grid-cols-5');
    const cells = [...strip.querySelectorAll('[data-state]')];
    expect(cells.map((c) => c.getAttribute('data-state'))).toEqual(['vencida', 'sin_empezar', 'en_curso', 'trabada', 'entregada']);
    expect(cells.map((c) => c.lastElementChild?.textContent)).toEqual(['VENCIDAS', 'SIN EMPEZAR', 'EN CURSO', 'ESPERANDO', 'ENTREGADAS']);
    expect(strip.querySelector('[data-state="sin_empezar"]')).toHaveTextContent('2SIN EMPEZAR');
    // No total anywhere (the user's decision): neither a counter nor in the header.
    expect(strip).not.toHaveTextContent(/ACTIVAS/);
    expect(screen.getByRole('banner')).not.toHaveTextContent(/activas/);
    // A long label goes to a second line inside its cell; the row never wraps.
    for (const cell of cells) expect(cell).toHaveClass('min-w-0');
  });

  it('only the cards scroll: header, tabs, counters and week fixed above, the buttons fixed below', async () => {
    serve({
      'GET /app/api/yo': ok(me({ carga_tareas: true, vistas: [{ vista: 'tus', titulo: 'Mis tareas' }, { vista: 'pedidas', titulo: 'Mis pedidos' }] })),
      'GET /app/api/tareas?vista=tus': ok(view()),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    const scroll = screen.getByTestId('scroll');
    expect(scroll).toHaveClass('overflow-y-auto', 'flex-1', 'min-h-0');
    const top = screen.getByTestId('fixed-top');
    expect(top).toHaveClass('shrink-0');
    for (const fixedPart of [
      screen.getByRole('banner'),
      screen.getByRole('tablist', { name: 'Vistas' }),
      screen.getByRole('region', { name: 'Tareas por estado' }),
      screen.getByRole('list', { name: 'La semana' }),
    ]) {
      expect(top.contains(fixedPart)).toBe(true);
      expect(scroll.contains(fixedPart)).toBe(false);
    }
    const card = screen.getByText('Configurar alarmas del SCADA');
    expect(scroll.contains(card)).toBe(true);
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveClass('shrink-0');
    expect(scroll.contains(footer)).toBe(false);
    expect(footer.contains(screen.getByRole('button', { name: '> Nueva tarea' }))).toBe(true);
    // The page itself never scrolls: one screen high, inside the safe areas.
    const page = top.parentElement as HTMLElement;
    expect(page).toHaveClass('overflow-hidden', 'flex-col');
    expect(page.className).toContain('h-[calc(100dvh-var(--tg-safe-top,0px)-var(--tg-safe-bottom,0px))]');
  });

});
