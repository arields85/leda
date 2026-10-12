/** "> contarle algo a leda": the frame, corner and shadow of the cards, in white (ADR 0022,
 * decision 18). It will open the chat with Leda; the server does not give its address yet,
 * so for now it does nothing. */
export function TalkButton() {
  return (
    <div
      aria-disabled="true"
      className="flex h-12 cursor-default select-none items-center gap-2 rounded-card border-hard border-ink bg-card px-3.5 text-button font-bold text-ink shadow-hard-ink"
    >
      &gt; contarle algo a leda
    </div>
  );
}
