import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';
import { ComputerSession } from './admin/ComputerSession';
import { onAPhone, POLL_MS, QrCode, SignIn } from './components/SignIn';
import { rememberedSpace, rememberSpace, spaceOfPath } from './door';
import { bindBackButton, bootTelegram, enterWithTelegram, LEDA_DARK, telegramWebApp } from './telegram';
import { detail, me, task, view } from './test/fixtures';
import { options } from './test/adminFixtures';

// ADR 0024 in the web: the Mini App boot, the QR sign-in, the chat's deep links and the task page.

type Reply = { status: number; body?: unknown };

function serve(routes: Record<string, Reply | (() => Reply)>) {
  const calls: { key: string; body: unknown }[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      calls.push({ key, body: typeof init?.body === 'string' ? JSON.parse(init.body) : undefined });
      const route = routes[key];
      const reply = typeof route === 'function' ? route() : route;
      if (!reply) return new Response('{"error":"no_existe"}', { status: 404 });
      return new Response(reply.body === undefined ? null : JSON.stringify(reply.body), {
        status: reply.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }),
  );
  return calls;
}

const ok = (body: unknown) => ({ status: 200, body });

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
  window.history.replaceState(null, '', '/app/');
  delete (window as unknown as { Telegram?: unknown }).Telegram;
  try {
    window.localStorage.clear();
  } catch {
    // jsdom always has it.
  }
});

function fakeTelegram(initData = 'query_id=1&hash=abc') {
  const back = { show: vi.fn(), hide: vi.fn(), onClick: vi.fn(), offClick: vi.fn() };
  const app = {
    initData,
    ready: vi.fn(),
    expand: vi.fn(),
    setHeaderColor: vi.fn(),
    setBackgroundColor: vi.fn(),
    BackButton: back,
    safeAreaInset: { top: 10, bottom: 20, left: 0, right: 0 },
    contentSafeAreaInset: { top: 4, bottom: 0, left: 0, right: 0 },
    onEvent: vi.fn(),
  };
  (window as unknown as { Telegram: unknown }).Telegram = { WebApp: app };
  return app;
}

describe('the Mini App', () => {
  it('is only the page Telegram opened with its signed data', () => {
    expect(telegramWebApp()).toBeNull();
    fakeTelegram('');
    expect(telegramWebApp()).toBeNull();
    fakeTelegram();
    expect(telegramWebApp()).not.toBeNull();
  });

  it("boots ready, expanded where full screen is not available (MA-3), in Leda's dark and inside the safe areas", () => {
    const app = fakeTelegram();
    const root = document.createElement('div');
    bootTelegram(app, root);
    expect(app.ready).toHaveBeenCalled();
    expect(app.expand).toHaveBeenCalled();
    expect(app.setHeaderColor).toHaveBeenCalledWith(LEDA_DARK);
    expect(app.setBackgroundColor).toHaveBeenCalledWith(LEDA_DARK);
    expect(root.style.getPropertyValue('--tg-safe-top')).toBe('14px');
    expect(root.style.getPropertyValue('--tg-safe-bottom')).toBe('20px');
  });

  it("binds Telegram's back button to the page's navigation", () => {
    const app = fakeTelegram();
    const back = vi.fn();
    const unbind = bindBackButton(app, true, back);
    expect(app.BackButton.show).toHaveBeenCalled();
    expect(app.BackButton.onClick).toHaveBeenCalledWith(back);
    unbind();
    expect(app.BackButton.offClick).toHaveBeenCalledWith(back);
    expect(app.BackButton.hide).toHaveBeenCalled();
    bindBackButton(app, false, back);
    expect(app.BackButton.hide).toHaveBeenCalledTimes(2);
  });

  it('sends the signature to its door with the space of the address, first of all', async () => {
    const calls = serve({ 'POST /app/api/entrar-telegram': ok({ ok: true }) });
    expect(await enterWithTelegram('equipo', 'corework', 'firmado')).toEqual({ kind: 'in' });
    expect(calls[0].body).toEqual({ espacio: 'corework', init_data: 'firmado' });
    serve({ 'POST /app/admin/api/entrar-telegram': { status: 409, body: { error: 'firma_usada' } } });
    // The same opening again (a reload): it keeps the session it opened.
    expect(await enterWithTelegram('administracion', null, 'firmado')).toEqual({ kind: 'in' });
    serve({
      'POST /app/api/entrar-telegram': {
        status: 403,
        body: { error: 'sin_membresia', texto: 'Esta cuenta de Telegram no es de este equipo.' },
      },
    });
    expect(await enterWithTelegram('equipo', 'corework', 'firmado')).toEqual({
      kind: 'refused',
      text: 'Esta cuenta de Telegram no es de este equipo.',
    });
  });

  it('reads the space from the address and remembers the last one entered', () => {
    expect(spaceOfPath('/app/e/corework/')).toBe('corework');
    expect(spaceOfPath('/app/e/north-lab')).toBe('north-lab');
    expect(spaceOfPath('/app/')).toBeNull();
    expect(spaceOfPath('/app/e/../admin')).toBeNull();
    expect(rememberedSpace()).toBeNull();
    rememberSpace('corework');
    expect(rememberedSpace()).toBe('corework');
  });
});

describe('the QR sign-in', () => {
  const REQUEST = {
    pedido_id: 'p-1',
    enlace: 'https://t.me/Leda_PM_bot?start=compu_abc',
    qr: ['10', '01'],
    vence_en: '2026-10-14T18:05:00Z',
  };

  it('shows the QR on a computer and enters by itself once approved in Telegram', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    let estado = 'pendiente';
    const calls = serve({
      'POST /app/api/entrar/qr': { status: 201, body: REQUEST },
      'GET /app/api/entrar/qr/p-1': () => ok({ estado }),
    });
    const onIn = vi.fn();
    render(<SignIn door="equipo" space="corework" onIn={onIn} phone={false} />);
    expect(await screen.findByRole('img', { name: 'Código para entrar con Telegram' })).toBeInTheDocument();
    expect(calls[0].body).toEqual({ espacio: 'corework' });
    expect(screen.queryByText('Entrar con Telegram')).toBeNull();
    await act(async () => {
      vi.advanceTimersByTime(POLL_MS + 10);
    });
    await waitFor(() => expect(calls.filter((c) => c.key === 'GET /app/api/entrar/qr/p-1')).toHaveLength(1));
    expect(onIn).not.toHaveBeenCalled();
    estado = 'adentro';
    await act(async () => {
      vi.advanceTimersByTime(POLL_MS + 10);
    });
    await waitFor(() => expect(onIn).toHaveBeenCalled());
  });

  it("on a phone's browser shows «Entrar con Telegram» instead of the QR", async () => {
    serve({ 'POST /app/admin/api/entrar/qr': { status: 201, body: REQUEST } });
    render(<SignIn door="administracion" space={null} onIn={() => {}} phone />);
    const button = await screen.findByRole('link', { name: 'Entrar con Telegram' });
    expect(button).toHaveAttribute('href', REQUEST.enlace);
    expect(screen.queryByRole('img')).toBeNull();
  });

  it('an expired code offers another one', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const calls = serve({
      'POST /app/api/entrar/qr': { status: 201, body: REQUEST },
      'GET /app/api/entrar/qr/p-1': ok({ estado: 'vencido' }),
    });
    render(<SignIn door="equipo" space="corework" onIn={() => {}} phone={false} />);
    await screen.findByRole('img');
    await act(async () => {
      vi.advanceTimersByTime(POLL_MS + 10);
    });
    fireEvent.click(await screen.findByRole('button', { name: '> otro código' }));
    await waitFor(() => expect(calls.filter((c) => c.key === 'POST /app/api/entrar/qr')).toHaveLength(2));
  });

  it('knows a phone, and draws the QR dark on light', () => {
    expect(onAPhone({ userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)' })).toBe(true);
    expect(onAPhone({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130' })).toBe(false);
    const { container } = render(<QrCode rows={['10', '01']} label="qr" />);
    expect(container.querySelector('path')?.getAttribute('d')).toBe('M4,4h1v1h-1zM5,5h1v1h-1z');
    expect(container.querySelector('rect')?.getAttribute('fill')).toBe('#FFFFFF');
  });
});

describe("the chat's buttons lead straight to their target", () => {
  it('«Cargar la tarea» opens the form', async () => {
    window.history.replaceState(null, '', '/app/e/corework/?nueva=tarea');
    serve({
      'GET /app/api/yo': ok(me({ carga_tareas: true })),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/carga/opciones': ok(options()),
    });
    render(<App />);
    expect(await screen.findByRole('button', { name: '> volver a las tareas' })).toBeInTheDocument();
  });

  it("«Ver la tarea» opens that task's detail inside the app", async () => {
    window.history.replaceState(null, '', '/app/e/corework/?tarea=t1');
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'POST /app/api/tareas/t1/detalle': ok(detail({ titulo: 'Cablear el tablero' })),
    });
    render(<App />);
    expect(await screen.findByRole('article', { name: 'La tarea Cablear el tablero' })).toBeInTheDocument();
  });

  it('every task card opens its detail inside the app, never leaving the page', async () => {
    const calls = serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view({ tareas: [task({ id: 't9', titulo: 'Probar el módem' })] })),
      'POST /app/api/tareas/t9/detalle': ok(detail({ titulo: 'Probar el módem' })),
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('link', { name: 'Ver la tarea Probar el módem' }));
    expect(await screen.findByRole('article', { name: 'La tarea Probar el módem' })).toBeInTheDocument();
    expect(calls.some((c) => c.key === 'POST /app/api/tareas/t9/detalle')).toBe(true);
    expect(calls.some((c) => c.key.endsWith('/pagina'))).toBe(false);
  });

  it("remembers the space for this computer's next sign-in", async () => {
    serve({ 'GET /app/api/yo': ok(me({ espacio_slug: 'corework' })), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(rememberedSpace()).toBe('corework');
  });
});

describe('how long a computer stays remembered', () => {
  beforeEach(() => window.history.replaceState(null, '', '/app/admin/'));

  it('reads the setting of the space and saves a change at once', async () => {
    const url = '/app/admin/api/espacios/w1/sesion-en-la-compu';
    const calls = serve({ [`GET ${url}`]: ok({ dias: null }), [`POST ${url}`]: ok({ dias: 30 }) });
    render(<ComputerSession spaceId="w1" onClosed={() => {}} />);
    const button = await screen.findByRole('button', { name: /una computadora queda recordada/i });
    expect(button).toHaveTextContent('sin vencimiento');
    fireEvent.click(button);
    fireEvent.click(within(screen.getByRole('listbox')).getByRole('option', { name: '30 días' }));
    expect(await screen.findByText('Guardado.')).toBeInTheDocument();
    expect(calls.find((c) => c.key === `POST ${url}`)?.body).toEqual({ dias: 30 });
  });
});

describe('the review of the MA', () => {
  it('inside Telegram a closed session never shows a QR: it says to open Leda again', async () => {
    fakeTelegram();
    const calls = serve({});
    render(<SignIn door="equipo" space="corework" onIn={() => {}} phone={false} />);
    expect(await screen.findByText('Cerrá Leda y volvé a abrirla desde el chat de Telegram.')).toBeInTheDocument();
    expect(calls).toHaveLength(0);
  });

  it('a task that cannot be opened says so', async () => {
    serve({
      'GET /app/api/yo': ok(me()),
      'GET /app/api/tareas?vista=tus': ok(view({ tareas: [task({ id: 't9', titulo: 'Probar el módem' })] })),
      'POST /app/api/tareas/t9/detalle': { status: 403, body: { error: 'no_la_ve' } },
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('link', { name: 'Ver la tarea Probar el módem' }));
    expect(await screen.findByText('No se pudo abrir esa tarea.')).toBeInTheDocument();
  });

  it('the computer setting goes back when saving fails, and a failed read never shows the default', async () => {
    const url = '/app/admin/api/espacios/w1/sesion-en-la-compu';
    serve({ [`GET ${url}`]: ok({ dias: 7 }), [`POST ${url}`]: { status: 500, body: {} } });
    render(<ComputerSession spaceId="w1" onClosed={() => {}} />);
    const button = await screen.findByRole('button', { name: /una computadora queda recordada/i });
    expect(button).toHaveTextContent('7 días');
    fireEvent.click(button);
    fireEvent.click(within(screen.getByRole('listbox')).getByRole('option', { name: '30 días' }));
    expect(await screen.findByText('No se pudo guardar ahora; probá de nuevo.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /una computadora queda recordada/i })).toHaveTextContent('7 días');
  });

  it('a setting that cannot be read is not shown as "sin vencimiento"', async () => {
    serve({ 'GET /app/admin/api/espacios/w2/sesion-en-la-compu': { status: 500, body: {} } });
    render(<ComputerSession spaceId="w2" onClosed={() => {}} />);
    expect(await screen.findByText(/No se pudo leer cuánto dura ahora/)).toBeInTheDocument();
    expect(screen.queryByText('sin vencimiento')).toBeNull();
  });
});
