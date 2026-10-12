// One web, two doors (ADR 0022, decision 10): the path picks which one this page is. The
// server serves the same bundle at /app/ and /app/admin/; each door has its own cookie.
export function isAdminDoor(pathname: string): boolean {
  return pathname === '/app/admin' || pathname.startsWith('/app/admin/');
}
