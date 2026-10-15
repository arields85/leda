import { afterEach, describe, expect, it, vi } from 'vitest';
import source from '../public/abrir.js?raw';

// The Mini App launcher (`/app/abrir/...`, MA-2): on a phone it goes on to the web inside Telegram;
// in Telegram on a computer (which shows the Mini App inside a frame) it opens the web in the
// browser, already signed in with the computer pass (MA-5), or where the QR sign-in applies when
// the pass could not be had.

const SIGNED = '#tgWebAppData=user%3D1%26hash%3Dabc&tgWebAppPlatform=tdesktop';
const PASS = '/app/entrar/pase/0b5c3f9e-1d2a-4c3b-9a8e-7f6d5c4b3a21/AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-abcd';
const ADMIN_PASS = '/app/admin/entrar/pase/0b5c3f9e-1d2a-4c3b-9a8e-7f6d5c4b3a21/AbCdEfGhIjKl';
const QR_NOTICE = 'En el navegador, entrá escaneando el código QR con el celular.';

type Reply = { status: number; body?: unknown } | 'network' | 'hang';

interface Launch {
  platform?: string;
  initData?: string;
  framed?: boolean;
  pathname?: string;
  search?: string;
  openLink?: (url: string) => void;
  reply?: Reply;
  withFetch?: boolean;
}

function launch({ platform, initData = 'user=1&hash=abc', framed = false,
                  pathname = '/app/abrir/e/corework/', search = '', openLink,
                  reply = { status: 201, body: { direccion: PASS } }, withFetch = true }: Launch) {
  document.body.innerHTML = '<main id="lanzador"></main>';
  const replace = vi.fn();
  const open = vi.fn();
  const ready = vi.fn();
  const link = vi.fn(openLink ?? (() => {}));
  const fetch = vi.fn(async () => {
    if (reply === 'network') throw new TypeError('network');
    if (reply === 'hang') return new Promise<Response>(() => {});
    return new Response(reply.body === undefined ? null : JSON.stringify(reply.body), { status: reply.status });
  });
  const self = {};
  const win = {
    Telegram: platform === undefined ? undefined : { WebApp: { platform, initData, ready, openLink: link } },
    location: { pathname, search, hash: SIGNED, origin: 'https://leda.example', replace },
    document,
    open,
    self,
    top: framed ? {} : self,
    setTimeout: (callback: () => void, ms: number) => setTimeout(callback, ms),
    ...(withFetch ? { fetch } : {}),
  };
  new Function('window', source)(win);
  return { replace, open, ready, link, fetch };
}

afterEach(() => {
  document.body.innerHTML = '';
  vi.useRealTimers();
});

describe('the Mini App launcher', () => {
  it.each(['ios', 'android', 'android_x'])('goes on to the Mini App on a phone (%s), signature kept', (platform) => {
    const { replace, link, open, fetch } = launch({ platform, search: '?tarea=t1' });
    expect(replace).toHaveBeenCalledWith(`/app/e/corework/?tarea=t1${SIGNED}`);
    expect(link).not.toHaveBeenCalled();
    expect(open).not.toHaveBeenCalled();
    expect(fetch).not.toHaveBeenCalled();
    expect(document.body.textContent).toBe('');
  });

  it.each(['tdesktop', 'macos', 'weba', 'webk', 'unigram'])(
    'in Telegram on a computer (%s) asks for the pass and opens the browser already signed in',
    async (platform) => {
      const { replace, link, ready, fetch } = launch({ platform, search: '?tarea=t1', framed: true });
      expect(replace).not.toHaveBeenCalled();
      expect(ready).toHaveBeenCalled();
      await vi.waitFor(() => expect(link).toHaveBeenCalled());
      expect(fetch).toHaveBeenCalledWith('/app/api/entrar/pase', expect.objectContaining({ method: 'POST' }));
      const [, init] = fetch.mock.calls[0] as unknown as [string, RequestInit];
      expect(JSON.parse(init.body as string)).toEqual({ espacio: 'corework', init_data: 'user=1&hash=abc' });
      expect(link).toHaveBeenCalledWith(
        `https://leda.example${PASS}?a=${encodeURIComponent('/app/e/corework/?tarea=t1')}`,
      );
      expect(document.body.textContent).toContain('Abrí Leda en el navegador');
      expect(document.body.textContent).not.toContain('QR');
      expect(document.body.textContent).not.toContain(PASS);
    },
  );

  it('asks the administration door with the administration signature alone', async () => {
    const { link, fetch } = launch({
      platform: 'tdesktop', framed: true, pathname: '/app/abrir/admin/',
      reply: { status: 201, body: { direccion: ADMIN_PASS } },
    });
    await vi.waitFor(() => expect(link).toHaveBeenCalled());
    const [url, init] = fetch.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe('/app/admin/api/entrar/pase');
    expect(JSON.parse(init.body as string)).toEqual({ init_data: 'user=1&hash=abc' });
    expect(link).toHaveBeenCalledWith(`https://leda.example${ADMIN_PASS}?a=${encodeURIComponent('/app/admin/')}`);
  });

  it.each<[string, Reply]>([
    ['an expired or used signature', { status: 401, body: { error: 'firma_invalida', texto: 'x' } }],
    ['the server down', { status: 503, body: { error: 'no_disponible' } }],
    ['no network', 'network'],
    ['an address that is not a pass', { status: 201, body: { direccion: 'https://otro.example/' } }],
  ])('with %s opens the plain address, where the QR applies, and says so', async (_, reply) => {
    const { link } = launch({ platform: 'tdesktop', framed: true, reply });
    await vi.waitFor(() => expect(link).toHaveBeenCalled());
    expect(link).toHaveBeenCalledWith('https://leda.example/app/e/corework/');
    expect(document.body.textContent).toContain(QR_NOTICE);
    expect(document.body.textContent).not.toMatch(/error|503|401|firma/i);
  });

  it('an account that is not of the team hears it in plain words', async () => {
    const texto = 'Esta cuenta de Telegram no es de este equipo. Abrí Leda desde el chat de tu equipo.';
    const { link } = launch({ platform: 'tdesktop', framed: true, reply: { status: 403, body: { error: 'sin_membresia', texto } } });
    await vi.waitFor(() => expect(link).toHaveBeenCalled());
    expect(link).toHaveBeenCalledWith('https://leda.example/app/e/corework/');
    expect(document.body.textContent).toContain(texto);
  });

  it('does not wait forever for the pass', async () => {
    vi.useFakeTimers();
    const { link } = launch({ platform: 'tdesktop', framed: true, reply: 'hang' });
    expect(link).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(6000);
    expect(link).toHaveBeenCalledWith('https://leda.example/app/e/corework/');
    expect(document.body.textContent).toContain(QR_NOTICE);
  });

  it('a Telegram that cannot send its signature goes to the QR', async () => {
    const { link, fetch } = launch({ platform: 'tdesktop', framed: true, withFetch: false });
    await vi.waitFor(() => expect(link).toHaveBeenCalled());
    expect(fetch).not.toHaveBeenCalled();
    expect(link).toHaveBeenCalledWith('https://leda.example/app/e/corework/');
  });

  it('treats an unknown platform inside a frame as a computer', async () => {
    const { replace, link } = launch({ platform: 'unknown', framed: true });
    expect(replace).not.toHaveBeenCalled();
    await vi.waitFor(() => expect(link).toHaveBeenCalled());
  });

  it('opens the same address again with the button', async () => {
    const { link } = launch({ platform: 'tdesktop', framed: true });
    await vi.waitFor(() => expect(link).toHaveBeenCalled());
    const button = document.querySelector('button');
    expect(button?.textContent).toBe('Abrir de nuevo');
    button?.click();
    expect(link).toHaveBeenCalledTimes(2);
    expect(link.mock.calls[1]).toEqual(link.mock.calls[0]);
  });

  it('falls back to the browser when Telegram cannot open the link', async () => {
    const { open } = launch({ platform: 'tdesktop', framed: true, reply: 'network', openLink: () => { throw new Error('old'); } });
    await vi.waitFor(() => expect(open).toHaveBeenCalled());
    expect(open).toHaveBeenCalledWith('https://leda.example/app/e/corework/', '_blank', 'noopener');
  });

  it('goes straight to the web outside Telegram', () => {
    const { replace } = launch({ pathname: '/app/abrir/admin/' });
    expect(replace).toHaveBeenCalledWith(`/app/admin/${SIGNED}`);
  });

  it('never leaves the web of this site, whatever the address says', async () => {
    for (const pathname of ['/app/abrir//evil.example/', '/app/abrir/e/../../x/', '/app/abrir/e/Mal/', '/elsewhere']) {
      const { replace } = launch({ platform: 'ios', pathname, search: '?x=1' });
      expect(replace).toHaveBeenCalledWith(`/app/${SIGNED}`);
    }
    const { link, fetch } = launch({ platform: 'tdesktop', framed: true, pathname: '/app/abrir//evil.example/' });
    await vi.waitFor(() => expect(link).toHaveBeenCalled());
    expect(fetch).not.toHaveBeenCalled();
    expect(link).toHaveBeenCalledWith('https://leda.example/app/');
  });
});
