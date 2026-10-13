/**
 * The iPhone zooms the page in when a control with text under 16px gets the focus, and the page
 * then pans sideways (J1-6). The controls used to be 16px for that; the user asked for no big
 * text at all (2026-10-13), so the zoom is stopped here instead: on iOS only, the page's viewport
 * gets `maximum-scale=1`. On iOS that only stops the zoom on focus (pinch-zoom still works); on
 * Android it would block pinch-zoom, so it is never applied there.
 */

type Device = Pick<Navigator, 'userAgent' | 'platform' | 'maxTouchPoints'>;

/** An iPhone, iPod or iPad, also inside an app (the Telegram browser keeps the iOS user agent),
 * and an iPad that says it is a Mac (iPadOS asks for desktop sites, but it has a touch screen). */
export function isIOS(device: Device): boolean {
  if (/iPhone|iPad|iPod/.test(device.userAgent)) return true;
  return device.platform === 'MacIntel' && device.maxTouchPoints > 1;
}

/** The viewport's content with `maximum-scale=1`, keeping everything else it says. */
export function withMaximumScale(content: string): string {
  const parts = content
    .split(',')
    .map((part) => part.trim())
    .filter((part) => part && !/^maximum-scale\s*=/.test(part));
  return [...parts, 'maximum-scale=1'].join(', ');
}

/** On iOS, adds `maximum-scale=1` to the page's viewport; anywhere else it changes nothing.
 * Says whether it changed it. */
export function stopFocusZoomOnIOS(doc: Document = document, device: Device = navigator): boolean {
  if (!isIOS(device)) return false;
  const meta = doc.querySelector<HTMLMetaElement>('meta[name="viewport"]');
  if (!meta) return false;
  meta.content = withMaximumScale(meta.content);
  return true;
}
