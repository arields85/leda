import { CircleAlert, Mic as MicIcon, Square } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { SessionClosedError } from '../api';
import { type Candidate, DICTATION_FAILED, type Problem, transcribe } from './api';
import { AudioBars } from './AudioBars';
import { Completing } from './Completing';
import { canDictate, Dictation, DICTATION_LIMIT_MS } from './dictation';
import { FIELD_NAME, FIELD_ORDER, length, PROBLEM_FIELD } from './draft';
import { CONTROL, FIELD_HINT, FIELD_TITLE, TEXT_SIZE } from './typography';

/** The server's own limit for the free text (src/leda/ayuda_al_cargar.py, LARGO_DEL_TEXTO). */
export const STORY_LIMIT = 1000;

export type HelpState =
  | { kind: 'idle' }
  | { kind: 'asking' }
  | { kind: 'stale' }
  | { kind: 'done'; choices: Candidate[]; nothing: boolean }
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
/** The microphone (J2-28): an icon of the same width whatever it says, so "> completar con Leda"
 * and it stay on one line on a phone ("> dejar de dictar" was wider and wrapped). */
const MIC = `inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-card border-hard border-line-soft bg-transparent text-ink-soft disabled:opacity-50`;

function Line({ children, warn }: { children: string; warn?: boolean }) {
  return (
    <p className={`m-0 flex min-w-0 items-start gap-1.5 ${warn ? 'font-bold text-falta' : 'text-ink-soft'}`}>
      <CircleAlert aria-hidden="true" strokeWidth={2.25} className="mt-[0.2em] size-[1em] shrink-0" />
      <span className="min-w-0 wrap-break-word">{children}</span>
    </p>
  );
}

/** "No pude completar: quién la hace, criterio de aceptación." for the notes that belong to a
 * field (each one also shows its own text on that field), in the order of the form. */
function missedFields(notes: Problem[]): string | null {
  const fields = FIELD_ORDER.filter((field) => notes.some((n) => PROBLEM_FIELD[n.campo] === field));
  return fields.length ? `No pude completar: ${fields.map((f) => FIELD_NAME[f]).join(', ')}.` : null;
}

/** "1:05": minutes and seconds of a recording. */
function clock(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}

/** What was written, then what was dictated: on a new line after a sentence that ends, after a
 * space otherwise. */
export function withDictated(story: string, said: string): string {
  const before = story.trimEnd();
  if (!before) return said;
  return `${before}${/[.!?…]$/.test(before) ? '\n' : ' '}${said}`;
}

type Mic = 'idle' | 'starting' | 'recording' | 'transcribing';

interface HelpBoxProps {
  spaceId: string;
  /** The administration session closed (the dictation's answer said so). */
  onClosed: () => void;
  story: string;
  onStory: (text: string) => void;
  help: HelpState;
  /** What Leda could not complete, as the form keeps it now (`LoadForm`): a field's notice goes
   * when the person fills that field, so the summary never names it after it went (review
   * review-97374544422a6d97). */
  notes: Problem[];
  onAsk: () => void;
  onChoose: (membershipId: string) => void;
}

/** "Contame qué querés hacer y te ayudo" (ADR 0023, point 4; portion J2): one free box, typed or
 * dictated, and "completar con Leda". Optional: the form below works by hand as always. The
 * microphone shows only where the browser can record (J2b: the audio goes to the server, which
 * turns it into text with Gemini; the text goes into the box, for the person to read and fix). */
export function HelpBox({ spaceId, onClosed, story, onStory, help, notes, onAsk, onChoose }: HelpBoxProps) {
  const [recordable] = useState(() => canDictate());
  const [mic, setMic] = useState<Mic>('idle');
  const [elapsed, setElapsed] = useState(0);
  const [micNote, setMicNote] = useState<string | null>(null);
  const [bars, setBars] = useState(false);
  const dictation = useRef<Dictation | null>(null);
  const readLevel = useCallback(() => dictation.current?.level() ?? null, []);
  const mounted = useRef(true);
  const storyNow = useRef(story);
  storyNow.current = story;

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      dictation.current?.cancel();
    };
  }, []);

  async function heard(audio: Blob) {
    setMic('transcribing');
    try {
      const result = await transcribe(spaceId, audio);
      if (!mounted.current) return;
      if (result.kind === 'text') {
        onStory(withDictated(storyNow.current, result.text));
        // J2-26: Gemini cut it at its limit; what was heard is in, and the rest can be dictated.
        if (result.notice) setMicNote(result.notice);
      } else setMicNote(result.text);
    } catch (error) {
      if (!mounted.current) return;
      if (error instanceof SessionClosedError) onClosed();
      else setMicNote(DICTATION_FAILED);
    } finally {
      if (mounted.current) setMic('idle');
    }
  }

  function toggleMic() {
    if (mic === 'recording') {
      dictation.current?.stop();
      return;
    }
    if (mic !== 'idle') return;
    setMicNote(null);
    setMic('starting');
    const d = new Dictation({
      onRecording: () => {
        setElapsed(0);
        setBars(d.hasLevel());
        setMic('recording');
      },
      onTick: setElapsed,
      onAudio: (audio) => {
        dictation.current = null;
        void heard(audio);
      },
      onProblem: (text) => {
        dictation.current = null;
        setMic('idle');
        setMicNote(text);
      },
    });
    dictation.current = d;
    void d.start();
  }

  const asking = help.kind === 'asking';
  const over = length(story) > STORY_LIMIT;
  const missed = help.kind === 'done' ? missedFields(notes) : null;
  const micName = mic === 'transcribing' ? 'pasando a texto…' : mic === 'recording' ? 'dejar de dictar' : 'dictar';
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
        Escribilo o dictalo como lo dirías; Leda completa lo que falta.
      </p>
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          className={BUTTON}
          onClick={onAsk}
          disabled={asking}
          aria-label={asking ? 'completando…' : undefined}
        >
          {asking ? <Completing word="completando" /> : '> completar con Leda'}
        </button>
        {recordable && (
          // J2-28: a microphone to start and a square to stop, the recorders' own signs (a crossed
          // microphone would read as "muted"); the words are in its name and its tooltip.
          <button
            type="button"
            className={MIC}
            onClick={toggleMic}
            disabled={mic === 'starting' || mic === 'transcribing'}
            aria-pressed={mic === 'recording'}
            aria-label={micName}
            title={micName}
          >
            {mic === 'recording' ? (
              <Square aria-hidden="true" strokeWidth={2.25} className="size-4 fill-current" />
            ) : (
              <MicIcon aria-hidden="true" strokeWidth={2.25} className="size-5" />
            )}
          </button>
        )}
      </div>
      {mic === 'recording' && (
        <div className={`flex min-w-0 items-center gap-2.5 ${FIELD_HINT}`}>
          {bars && <AudioBars read={readLevel} />}
          <span>
            grabando · {clock(elapsed)} de {clock(DICTATION_LIMIT_MS)}
          </span>
        </div>
      )}
      {mic === 'transcribing' && (
        <p className={`m-0 ${FIELD_HINT}`}>
          <Completing word="pasando a texto" />
        </p>
      )}
      <div role="status" className="flex min-w-0 flex-col gap-1 text-small">
        {micNote && <Line warn>{micNote}</Line>}
        {help.kind === 'failed' && <Line warn>{help.text}</Line>}
        {help.kind === 'rejected' && help.errors.map((e) => (
          <Line key={`${e.campo}-${e.motivo}`} warn>{e.texto}</Line>
        ))}
        {help.kind === 'stale' && <Line>{STALE_ANSWER}</Line>}
        {help.kind === 'done' && help.nothing && <Line>{NOTHING_TO_COMPLETE}</Line>}
        {missed && <Line warn>{missed}</Line>}
        {help.kind === 'done' && notes.filter((n) => !(n.campo in PROBLEM_FIELD)).map((n) => (
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
