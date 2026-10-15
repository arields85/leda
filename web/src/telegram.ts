import { fetchAdminMe } from './admin/api';
import { fetchMe, SessionClosedError } from './api';

// Leda inside Telegram (ADR 0024): the web opens as a Mini App from a button of the team bot or the
// administration bot. Telegram's own script (`/app/telegram-web-app.js`, served by Leda itself so
// the CSP stays `script-src 'self'`) gives `window.Telegram.WebApp`; outside Telegram its
// `initData` is empty and nothing here does anything.
// https://core.telegram.org/bots/webapps

/** Leda's dark background, for Telegram's header and background (decision 6: never each
 * Telegram's own colours). */
export const LEDA_DARK = '#0F1010';

/**
 * The iOS rule of `stopFocusZoomOnIOS` (`maximum-scale=1`, so the page does not zoom in when a
 * field gets the focus) stays inside the Mini App too. Decision 6: if inside the Mini App the
 * page no longer zooms in on its own when a field is tapped, pinch-zoom is freed. To try it on the
 * phone, set this to `true` and rebuild: the rule is then skipped only inside Telegram.
 */
export const FREE_PINCH_ZOOM_IN_MINI_APP = false;

interface BackButton {
  show(): void;
  hide(): void;
  onClick(callback: () => void): void;
  offClick(callback: () => void): void;
}

interface Insets {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

export interface TelegramWebApp {
  initData: string;
  platform?: string;
  ready(): void;
  expand(): void;
  setHeaderColor(color: string): void;
  setBackgroundColor(color: string): void;
  BackButton?: BackButton;
  safeAreaInset?: Insets;
  contentSafeAreaInset?: Insets;
  onEvent?(event: string, callback: () => void): void;
  // Bot API 8.0: the whole screen, with Telegram's "Cerrar" and "…" floating over the page.
  requestFullscreen?(): void;
  isVersionAtLeast?(version: string): boolean;
  close?(): void;
}

/** Phones, where the Mini App goes full screen (MA-3); a computer never gets here (the launcher
 * sends it to the browser). */
export const PHONES = ['ios', 'android', 'android_x'];

/** The Mini App, only when Telegram opened this page with its signed data; else `null`. */
export function telegramWebApp(win: Window = window): TelegramWebApp | null {
  const app = (win as unknown as { Telegram?: { WebApp?: TelegramWebApp } }).Telegram?.WebApp;
  return app && typeof app.initData === 'string' && app.initData ? app : null;
}

/** Whether this page runs inside Telegram, with or without its signed data: Telegram's script
 * defines `WebApp` everywhere, but outside Telegram its platform is `unknown` and it has no data.
 * Used where a QR would make no sense (it cannot be scanned from inside Telegram). */
export function insideTelegram(win: Window = window): boolean {
  const app = (win as unknown as { Telegram?: { WebApp?: TelegramWebApp } }).Telegram?.WebApp;
  if (!app) return false;
  if (typeof app.initData === 'string' && app.initData) return true;
  return typeof app.platform === 'string' && app.platform !== '' && app.platform !== 'unknown';
}

function safely(action: () => void): void {
  try {
    action();
  } catch {
    // An older Telegram may lack a method: the page works without it.
  }
}

/** Full screen on a phone (MA-3, the user's iPhone test: `requestFullscreen`, Bot API 8.0),
 * where Telegram's "Cerrar" and "…" float over the page: the safe areas keep the page clear of
 * them. Where it is not available, as large as Telegram allows (`expand()`). */
function grow(app: TelegramWebApp): void {
  const phone = typeof app.platform === 'string' && PHONES.includes(app.platform);
  let fullscreen = false;
  safely(() => {
    fullscreen = phone && typeof app.requestFullscreen === 'function'
      && (typeof app.isVersionAtLeast !== 'function' || app.isVersionAtLeast('8.0'));
  });
  if (fullscreen) {
    try {
      app.requestFullscreen?.();
      return;
    } catch {
      // Below: as large as it can.
    }
  }
  safely(() => app.expand());
}

/** Ready, full screen on a phone or else large (`grow`), Leda's colours, and the safe areas as
 * CSS variables (`--tg-safe-top` and the rest): the device's (status bar, notch) plus Telegram's
 * own (its floating "Cerrar" and "…" in full screen). */
export function bootTelegram(app: TelegramWebApp, root: HTMLElement = document.documentElement): void {
  safely(() => app.ready());
  grow(app);
  safely(() => app.setHeaderColor(LEDA_DARK));
  safely(() => app.setBackgroundColor(LEDA_DARK));
  const insets = () => {
    const safe = app.safeAreaInset;
    const content = app.contentSafeAreaInset;
    for (const side of ['top', 'bottom', 'left', 'right'] as const) {
      const value = (safe?.[side] ?? 0) + (content?.[side] ?? 0);
      root.style.setProperty(`--tg-safe-${side}`, `${value}px`);
    }
  };
  insets();
  safely(() => app.onEvent?.('safeAreaChanged', insets));
  safely(() => app.onEvent?.('contentSafeAreaChanged', insets));
}

/** Telegram's "Atrás" bound to the page's own navigation: shown while there is somewhere to go
 * back to, and calling `onBack` when touched. Returns how to unbind it. */
export function bindBackButton(app: TelegramWebApp | null, canGoBack: boolean, onBack: () => void): () => void {
  const button = app?.BackButton;
  if (!button) return () => {};
  if (!canGoBack) {
    safely(() => button.hide());
    return () => {};
  }
  safely(() => button.onClick(onBack));
  safely(() => button.show());
  return () => {
    safely(() => button.offClick(onBack));
    safely(() => button.hide());
  };
}

/** What happened when the page sent Telegram's signature to its door. */
export type TelegramEntry =
  | { kind: 'in' }
  | { kind: 'refused'; text: string }
  | { kind: 'failed' };

/** What to do when Telegram's signature no longer opens the door and there is no session: close
 * this window with Telegram's own «Cerrar» and tap the bot's menu button again, which signs anew. */
export const REOPEN_TEXT: Record<'equipo' | 'administracion', string> = {
  equipo: 'Cerrá esta ventana con «Cerrar», arriba, y tocá «Mi espacio» otra vez.',
  administracion: 'Cerrá esta ventana con «Cerrar», arriba, y tocá «Administración» otra vez.',
};

type SignatureReply = TelegramEntry | { kind: 'invalid'; text: string };

async function sendSignature(door: 'equipo' | 'administracion', space: string | null,
                             initData: string): Promise<SignatureReply> {
  const url = door === 'equipo' ? '/app/api/entrar-telegram' : '/app/admin/api/entrar-telegram';
  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(door === 'equipo' ? { espacio: space, init_data: initData } : { init_data: initData }),
    });
  } catch {
    return { kind: 'failed' };
  }
  if (response.ok || response.status === 409) return { kind: 'in' };
  if (response.status === 401 || response.status === 403) {
    let text = REOPEN_TEXT[door];
    try {
      const body = (await response.json()) as { texto?: unknown };
      if (typeof body.texto === 'string' && body.texto) text = body.texto;
    } catch {
      // Below: a refusal without its words still says what to do.
    }
    // 401: the signature itself (expired, used elsewhere, malformed). 403: who the account is
    // (not of this team, no administration role), which a session never overrides.
    return response.status === 401 ? { kind: 'invalid', text } : { kind: 'refused', text };
  }
  return { kind: 'failed' };
}

/** Sends the Mini App's signed data to the door, before anything else (ADR 0024, decision 7):
 * the team door with the space of the address (`/app/e/<space>/`), the administration door alone.
 * A signature already used (the Mini App reloaded) keeps the session it opened. */
export async function enterWithTelegram(door: 'equipo' | 'administracion', space: string | null,
                                        initData: string): Promise<TelegramEntry> {
  const reply = await sendSignature(door, space, initData);
  return reply.kind === 'invalid' ? { kind: 'refused', text: reply.text } : reply;
}

/** The Mini App's way in (MA-5, the user's iPhone): Telegram keeps a minimized Mini App for hours
 * and, when it reloads, sends the ORIGINAL signature, older than its 10 minutes. A signature
 * refused as such does not stop a person whose session is still good: the door's "who am I"
 * decides. Without a session, the refusal says exactly what to do. A refusal of the account
 * itself (not of this team, no administration role) always stands. */
export async function enterTheMiniApp(door: 'equipo' | 'administracion', space: string | null,
                                      initData: string): Promise<TelegramEntry> {
  const reply = await sendSignature(door, space, initData);
  if (reply.kind !== 'invalid') return reply;
  try {
    await (door === 'equipo' ? fetchMe() : fetchAdminMe());
    return { kind: 'in' };
  } catch (error) {
    if (error instanceof SessionClosedError) return { kind: 'refused', text: REOPEN_TEXT[door] };
    // The session could not be read now: the page shows what its session allows.
    return { kind: 'failed' };
  }
}
