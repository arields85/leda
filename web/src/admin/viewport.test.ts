import { afterEach, describe, expect, it } from 'vitest';
import { isIOS, stopFocusZoomOnIOS, withMaximumScale } from './viewport';

const PAGE = 'width=device-width, initial-scale=1, viewport-fit=cover';

const IPHONE_SAFARI =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1';
// Telegram opens links in its own browser, which keeps the system's iOS user agent.
const IPHONE_TELEGRAM =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148';
const IPAD_AS_MAC =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15';
const ANDROID_CHROME =
  'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36';
const DESKTOP_CHROME =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36';

const device = (userAgent: string, platform = '', maxTouchPoints = 0) => ({ userAgent, platform, maxTouchPoints });

function pageWithViewport() {
  document.head.innerHTML = `<meta name="viewport" content="${PAGE}" />`;
  return document.querySelector('meta[name="viewport"]') as HTMLMetaElement;
}

afterEach(() => {
  document.head.innerHTML = '';
});

describe('the zoom on focus is stopped only on iOS (J2-10)', () => {
  it('knows an iPhone, the Telegram browser on an iPhone and an iPad that says it is a Mac', () => {
    expect(isIOS(device(IPHONE_SAFARI, 'iPhone', 5))).toBe(true);
    expect(isIOS(device(IPHONE_TELEGRAM, 'iPhone', 5))).toBe(true);
    expect(isIOS(device(IPAD_AS_MAC, 'MacIntel', 5))).toBe(true);
  });

  it('is not iOS on Android, on a desktop or on a Mac without a touch screen', () => {
    expect(isIOS(device(ANDROID_CHROME, 'Linux armv8l', 5))).toBe(false);
    expect(isIOS(device(DESKTOP_CHROME, 'Win32', 0))).toBe(false);
    expect(isIOS(device(IPAD_AS_MAC, 'MacIntel', 0))).toBe(false);
  });

  it('on an iPhone, adds maximum-scale=1 and keeps the rest of the viewport', () => {
    const meta = pageWithViewport();
    expect(stopFocusZoomOnIOS(document, device(IPHONE_TELEGRAM, 'iPhone', 5))).toBe(true);
    expect(meta.content).toBe('width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=1');
  });

  it('on Android and on a desktop, the viewport stays as it is, so pinch-zoom keeps working', () => {
    const meta = pageWithViewport();
    expect(stopFocusZoomOnIOS(document, device(ANDROID_CHROME, 'Linux armv8l', 5))).toBe(false);
    expect(stopFocusZoomOnIOS(document, device(DESKTOP_CHROME, 'Win32', 0))).toBe(false);
    expect(meta.content).toBe(PAGE);
  });

  it('never repeats the rule, and does nothing on a page without a viewport', () => {
    expect(withMaximumScale('width=device-width, maximum-scale=5')).toBe('width=device-width, maximum-scale=1');
    expect(withMaximumScale(withMaximumScale(PAGE))).toBe(withMaximumScale(PAGE));
    expect(stopFocusZoomOnIOS(document, device(IPHONE_SAFARI, 'iPhone', 5))).toBe(false);
  });

  it('the page itself allows zoom: the rule is only added at startup, on iOS', async () => {
    // Read as files, found from this test file, as the overflow test does in `AdminApp.test.tsx`.
    // @ts-expect-error -- this browser project has no Node types; the tests run on Node.
    const { readFileSync } = await import('node:fs');
    // @ts-expect-error -- the same: `dirname` is Node's, not in the browser's `ImportMeta`.
    const here: string = import.meta.dirname;
    const html: string = readFileSync(`${here}/../../index.html`, 'utf-8');
    expect(html).toContain(`<meta name="viewport" content="${PAGE}" />`);
    expect(html).not.toContain('maximum-scale');
    const main: string = readFileSync(`${here}/../main.tsx`, 'utf-8');
    expect(main).toMatch(/stopFocusZoomOnIOS\(\);[\s\S]*createRoot/);
  });
});
