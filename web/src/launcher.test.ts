import { afterEach, describe, expect, it, vi } from 'vitest';
import source from '../public/abrir.js?raw';

// The Mini App launcher (`/app/abrir/...`, MA-2): on a phone it goes on to the web inside Telegram;
// in Telegram on a computer (which shows the Mini App inside a frame) it opens the web in the
// browser, where the QR sign-in applies.

const SIGNED = '#tgWebAppData=user%3D1%26hash%3Dabc&tgWebAppPlatform=tdesktop';

interface Launch {
  platform?: string;
  initData?: string;
  framed?: boolean;
  pathname?: string;
  search?: string;
  openLink?: (url: string) => void;
}

function launch({ platform, initData = 'user=1&hash=abc', framed = false,
                  pathname = '/app/abrir/e/corework/', search = '', openLink }: Launch) {
  document.body.innerHTML = '<main id="lanzador"></main>';
  const replace = vi.fn();
  const open = vi.fn();
  const ready = vi.fn();
  const link = vi.fn(openLink ?? (() => {}));
  const self = {};
  const win = {
    Telegram: platform === undefined ? undefined : { WebApp: { platform, initData, ready, openLink: link } },
    location: { pathname, search, hash: SIGNED, origin: 'https://leda.example', replace },
    document,
    open,
    self,
    top: framed ? {} : self,
  };
  new Function('window', source)(win);
  return { replace, open, ready, link };
}

afterEach(() => {
  document.body.innerHTML = '';
});

describe('the Mini App launcher', () => {
  it.each(['ios', 'android', 'android_x'])('goes on to the Mini App on a phone (%s), signature kept', (platform) => {
    const { replace, link, open } = launch({ platform, search: '?tarea=t1' });
    expect(replace).toHaveBeenCalledWith(`/app/e/corework/?tarea=t1${SIGNED}`);
    expect(link).not.toHaveBeenCalled();
    expect(open).not.toHaveBeenCalled();
    expect(document.body.textContent).toBe('');
  });

  it.each(['tdesktop', 'macos', 'weba', 'webk', 'unigram'])(
    'opens the web in the browser from Telegram on a computer (%s), deep link kept, signature left out',
    (platform) => {
      const { replace, link, ready } = launch({ platform, search: '?tarea=t1', framed: true });
      expect(replace).not.toHaveBeenCalled();
      expect(link).toHaveBeenCalledWith('https://leda.example/app/e/corework/?tarea=t1');
      expect(ready).toHaveBeenCalled();
      expect(document.body.textContent).toContain('Abrí Leda en el navegador');
    },
  );

  it('treats an unknown platform inside a frame as a computer', () => {
    const { replace, link } = launch({ platform: 'unknown', framed: true });
    expect(replace).not.toHaveBeenCalled();
    expect(link).toHaveBeenCalledWith('https://leda.example/app/e/corework/');
  });

  it('opens it again with the button', () => {
    const { link } = launch({ platform: 'tdesktop', framed: true });
    const button = document.querySelector('button');
    expect(button?.textContent).toBe('Abrir de nuevo');
    button?.click();
    expect(link).toHaveBeenCalledTimes(2);
  });

  it('falls back to the browser when Telegram cannot open the link', () => {
    const { open } = launch({ platform: 'tdesktop', framed: true, openLink: () => { throw new Error('old'); } });
    expect(open).toHaveBeenCalledWith('https://leda.example/app/e/corework/', '_blank', 'noopener');
  });

  it('goes straight to the web outside Telegram', () => {
    const { replace } = launch({ pathname: '/app/abrir/admin/' });
    expect(replace).toHaveBeenCalledWith(`/app/admin/${SIGNED}`);
  });

  it('never leaves the web of this site, whatever the address says', () => {
    for (const pathname of ['/app/abrir//evil.example/', '/app/abrir/e/../../x/', '/app/abrir/e/Mal/', '/elsewhere']) {
      const { replace } = launch({ platform: 'ios', pathname, search: '?x=1' });
      expect(replace).toHaveBeenCalledWith(`/app/${SIGNED}`);
    }
    const { link } = launch({ platform: 'tdesktop', framed: true, pathname: '/app/abrir//evil.example/' });
    expect(link).toHaveBeenCalledWith('https://leda.example/app/');
  });
});
