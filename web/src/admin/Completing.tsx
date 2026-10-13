/** A word of work in progress ("completando", "cargando") with its three dots fading in and out
 * one after another: J2-13 for "completando…" and J2-15 for "cargando…". Always, also with reduced
 * motion, because only their opacity changes (`--animate-puntos`, `index.css`). Hidden from a
 * screen reader: the button that shows it says the word with its "…" in its `aria-label`. */
export function Completing({ word }: { word: string }) {
  return (
    <span aria-hidden="true">
      {word}
      <span className="animate-puntos [animation-delay:0ms]">.</span>
      <span className="animate-puntos [animation-delay:200ms]">.</span>
      <span className="animate-puntos [animation-delay:400ms]">.</span>
    </span>
  );
}
