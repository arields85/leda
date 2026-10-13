import { CircleAlert } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import type { Candidate, Problem } from './api';
import { length } from './draft';
import { heard, micProblem, type Recognizer, speechRecognition } from './speech';
import { CONTROL, FIELD_HINT, FIELD_TITLE, TEXT_SIZE } from './typography';

/** The server's own limit for the free text (src/leda/ayuda_al_cargar.py, LARGO_DEL_TEXTO). */
export const STORY_LIMIT = 1000;

export type HelpState =
  | { kind: 'idle' }
  | { kind: 'asking' }
  | { kind: 'stale' }
  | { kind: 'done'; notes: Problem[]; choices: Candidate[]; nothing: boolean }
  | { kind: 'rejected'; errors: Problem[] }
  | { kind: 'failed'; text: string };

export const NOTHING_TO_COMPLETE = 'Leda no encontró nada para completar con lo que escribiste.';
/** The person changed the free text or a field while Leda was answering: the answer was made for
 * what the form had when she asked, so it fills nothing (review review-03b5c3a74d3719b7). */
export const STALE_ANSWER = 'Cambiaste lo escrito mientras Leda completaba; tocá completar de nuevo.';

// The shared box of every control (`typography.ts`), taller for a story.
const BOX = `${CONTROL} min-h-24 resize-y`;
const BUTTON = `inline-flex h-11 items-center rounded-card border-hard border-ink bg-card px-3.5 ${TEXT_SIZE} font-bold text-ink shadow-hard-ink disabled:opacity-50`;
const QUIET = `inline-flex h-11 items-center rounded-card border-hard border-line-soft bg-transparent px-3.5 ${TEXT_SIZE} text-ink-soft disabled:opacity-50`;

function Line({ children, warn }: { children: string; warn?: boolean }) {
  return (
    <p className={`m-0 flex min-w-0 items-start gap-1.5 ${warn ? 'font-bold text-falta' : 'text-ink-soft'}`}>
      <CircleAlert aria-hidden="true" strokeWidth={2.25} className="mt-[0.2em] size-[1em] shrink-0" />
      <span className="min-w-0 wrap-break-word">{children}</span>
    </p>
  );
}

interface HelpBoxProps {
  story: string;
  onStory: (text: string) => void;
  help: HelpState;
  onAsk: () => void;
  onChoose: (membershipId: string) => void;
}

/** "Contame qué querés hacer y te ayudo" (ADR 0023, point 4; portion J2): one free box, typed or
 * dictated, and "completar con Leda". Optional: the form below works by hand as always. The
 * microphone shows only where the browser recognizes speech. */
export function HelpBox({ story, onStory, help, onAsk, onChoose }: HelpBoxProps) {
  const [Recognition] = useState(() => speechRecognition());
  const [listening, setListening] = useState(false);
  const [micNote, setMicNote] = useState<string | null>(null);
  const recognizer = useRef<Recognizer | null>(null);
  const storyNow = useRef(story);
  storyNow.current = story;

  useEffect(() => () => recognizer.current?.stop(), []);

  function toggleMic() {
    if (!Recognition) return;
    if (listening) {
      recognizer.current?.stop();
      return;
    }
    setMicNote(null);
    const r = new Recognition();
    r.lang = 'es-AR';
    r.interimResults = false;
    r.continuous = false;
    r.onresult = (event) => {
      const text = heard(event);
      if (text) onStory(storyNow.current.trim() ? `${storyNow.current.trimEnd()} ${text}` : text);
    };
    r.onerror = (event) => setMicNote(micProblem(event.error));
    r.onend = () => {
      setListening(false);
      recognizer.current = null;
    };
    recognizer.current = r;
    try {
      r.start();
      setListening(true);
    } catch {
      recognizer.current = null;
      setMicNote(micProblem('start-failed'));
    }
  }

  const asking = help.kind === 'asking';
  const over = length(story) > STORY_LIMIT;
  return (
    <div data-field className="flex min-w-0 max-w-full flex-col gap-2 rounded-card border-hard border-line-soft px-3 py-2.5">
      <div className={`flex min-w-0 items-baseline justify-between gap-2 ${FIELD_HINT}`}>
        <label htmlFor="f-contame" className={`min-w-0 ${FIELD_TITLE}`}>
          Contame qué querés hacer y te ayudo
        </label>
        <span aria-live="polite" className={`shrink-0 ${over ? 'font-bold text-falta' : ''}`}>
          {length(story)}/{STORY_LIMIT}
        </span>
      </div>
      <textarea
        id="f-contame"
        className={BOX}
        value={story}
        onChange={(e) => onStory(e.target.value)}
        aria-describedby="f-contame-ayuda"
      />
      <p id="f-contame-ayuda" className={`m-0 ${FIELD_HINT}`}>
        Como lo dirías. Leda completa lo que está vacío y lo marca; vos lo corregís y confirmás.
      </p>
      <div className="flex flex-wrap gap-3">
        <button type="button" className={BUTTON} onClick={onAsk} disabled={asking}>
          {asking ? 'completando…' : '> completar con Leda'}
        </button>
        {Recognition && (
          <button type="button" className={QUIET} onClick={toggleMic} aria-pressed={listening}>
            {listening ? '> dejar de dictar' : '> dictar'}
          </button>
        )}
      </div>
      <div role="status" className="flex min-w-0 flex-col gap-1 text-small">
        {micNote && <Line warn>{micNote}</Line>}
        {help.kind === 'failed' && <Line warn>{help.text}</Line>}
        {help.kind === 'rejected' && help.errors.map((e) => (
          <Line key={`${e.campo}-${e.motivo}`} warn>{e.texto}</Line>
        ))}
        {help.kind === 'stale' && <Line>{STALE_ANSWER}</Line>}
        {help.kind === 'done' && help.nothing && <Line>{NOTHING_TO_COMPLETE}</Line>}
        {help.kind === 'done' && help.notes.map((n) => (
          <Line key={`${n.campo}-${n.motivo}`}>{n.texto}</Line>
        ))}
      </div>
      {help.kind === 'done' && help.choices.length > 0 && (
        <div role="group" aria-label="elegí quién la hace" className="flex flex-wrap gap-2">
          {help.choices.map((c) => (
            <button key={c.membership_id} type="button" className={QUIET} onClick={() => onChoose(c.membership_id)}>
              {c.nombre} · {c.area}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
