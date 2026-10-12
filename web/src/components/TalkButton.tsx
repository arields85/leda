// Only a Telegram address opens: the server builds it from the space's bot username.
const TELEGRAM = /^https:\/\/t\.me\/[A-Za-z][A-Za-z0-9_]{4,31}$/;

/** "> consultar a leda": opens the Telegram chat with the team bot (the user's decision 8,
 * 2026-10-12), with the frame, corner and shadow of the cards, in white (ADR 0022, decision 18).
 * Without the bot's address, there is no button. */
export function TalkButton({ href }: { href: string | null }) {
  if (!href || !TELEGRAM.test(href)) return null;
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex h-12 select-none items-center gap-2 rounded-card border-hard border-ink bg-card px-3.5 text-button font-bold text-ink no-underline shadow-hard-ink"
    >
      &gt; consultar a leda
    </a>
  );
}
