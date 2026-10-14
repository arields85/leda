import { useEffect, useState } from 'react';

/** How many bars the row shows: about two and a half seconds of voice, narrow enough for a phone. */
export const BARS = 28;
/** How often a new bar comes in from the right: often enough to follow the voice, like the
 * messaging apps; with reduced motion, slowly (J2-27). */
export const EVERY_MS = 90;
export const EVERY_MS_STILL = 700;
/** The lowest bar, so silence still shows a row (a percentage of the row's height). */
export const LOWEST = 12;

function stillMotion(): boolean {
  return typeof window !== 'undefined' && (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false);
}

/** "Recording": a row of thin vertical bars that scroll left as the voice comes in, like a voice
 * note in a messaging app (J2-27). A scrolling row and not a level meter: it is what those apps
 * show while recording, and it also tells that the voice was heard a moment ago, not only now.
 * `read` gives the voice now, from 0 to 1 (`Dictation.level`); it is sampled on each animation
 * frame, a new bar every `EVERY_MS`, and the loop stops when the row goes away (the recording
 * stopped). Sober: the ink's soft gray on the card, no color. Only for the eye: the recording line
 * next to it says it in words. */
export function AudioBars({ read }: { read: () => number | null }) {
  const [levels, setLevels] = useState<number[]>(() => Array.from({ length: BARS }, () => 0));

  useEffect(() => {
    const every = stillMotion() ? EVERY_MS_STILL : EVERY_MS;
    let last: number | null = null;
    let frame = requestAnimationFrame(function tick(now: number) {
      if (last === null || now - last >= every) {
        last = now;
        const level = read();
        if (level !== null) setLevels((before) => [...before.slice(1), level]);
      }
      frame = requestAnimationFrame(tick);
    });
    return () => cancelAnimationFrame(frame);
  }, [read]);

  return (
    <span data-testid="audio-bars" aria-hidden="true" className="flex h-4 shrink-0 items-center gap-[2px]">
      {levels.map((level, i) => (
        <span
          key={i}
          className="w-[2px] rounded-full bg-ink-soft"
          style={{ height: `${Math.max(LOWEST, Math.round(level * 100))}%` }}
        />
      ))}
    </span>
  );
}
