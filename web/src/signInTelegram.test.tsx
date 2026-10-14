import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { SignIn } from './components/SignIn';
import { insideTelegram } from './telegram';

// Review of the MA (SignIn.tsx, Telegram detection): inside Telegram there is no QR to scan, also
// when Telegram opened the page without its signed data (a known platform, an empty `initData`);
// and the page decides it once, not on every render.

function telegramOn(platform: string, initData = '') {
  vi.stubGlobal('Telegram', { WebApp: { platform, initData } });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('Telegram detection on the sign-in page', () => {
  it('knows it is inside Telegram by its platform, even without signed data', () => {
    telegramOn('ios');
    expect(insideTelegram()).toBe(true);
    telegramOn('android', 'user=1&hash=abc');
    expect(insideTelegram()).toBe(true);
  });

  it('outside Telegram its script still defines WebApp, with platform "unknown" and no data', () => {
    telegramOn('unknown');
    expect(insideTelegram()).toBe(false);
    vi.unstubAllGlobals();
    expect(insideTelegram()).toBe(false);
  });

  it('inside Telegram without signed data it never asks for a QR', async () => {
    telegramOn('ios');
    const fetcher = vi.fn();
    vi.stubGlobal('fetch', fetcher);
    render(<SignIn door="equipo" space="corework" onIn={() => {}} phone />);
    expect(await screen.findByText('Cerrá Leda y volvé a abrirla desde el chat de Telegram.')).toBeInTheDocument();
    expect(fetcher).not.toHaveBeenCalled();
  });
});
