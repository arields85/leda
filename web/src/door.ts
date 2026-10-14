// One web, two doors (ADR 0022, decision 10): the path picks which one this page is. The
// server serves the same bundle at /app/ and /app/admin/; each door has its own cookie.
export function isAdminDoor(pathname: string): boolean {
  return pathname === '/app/admin' || pathname.startsWith('/app/admin/');
}

/** The team's space in the address the Mini App and the computer open (ADR 0024):
 * `/app/e/<space>/`. `null` anywhere else. */
export function spaceOfPath(pathname: string): string | null {
  const match = /^\/app\/e\/([a-z0-9][a-z0-9-]{0,63})(?:\/|$)/.exec(pathname);
  return match ? match[1] : null;
}

const REMEMBERED_SPACE = 'leda.espacio';

/** The space last entered from this browser, to show its QR again (a per-viewer convenience:
 * without it, the page asks to open Leda from the team's chat). */
export function rememberedSpace(): string | null {
  try {
    const value = window.localStorage.getItem(REMEMBERED_SPACE);
    return value && spaceOfPath(`/app/e/${value}/`) ? value : null;
  } catch {
    return null;
  }
}

export function rememberSpace(space: string | null | undefined): void {
  if (!space) return;
  try {
    window.localStorage.setItem(REMEMBERED_SPACE, space);
  } catch {
    // Private windows: the QR then needs the address with the space.
  }
}
