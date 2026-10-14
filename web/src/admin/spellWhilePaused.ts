import { type MutableRefObject, useEffect, useRef, useState } from 'react';
import { SessionClosedError } from '../api';
import type { Spelling, TextField } from './api';

/** How long after the last keystroke Leda checks the spelling of a text (J2-24). */
export const SPELL_PAUSE_MS = 1500;

/** A spelling correction made for one text as it was typed (J2-24): it holds only while the field
 * still has that text. */
export interface SpellFix {
  from: string;
  to: string;
}

/** The draft as the preview shows it and as it goes (J2-24): each text with the correction made for
 * it, if the field still has the text it was made for. */
export function withFixesOf<F extends TextField, D extends Record<F, string>>(
  draft: D,
  fields: readonly F[],
  fixes: Partial<Record<F, SpellFix>>,
): D {
  let shown = draft;
  for (const field of fields) {
    const fix = fixes[field];
    if (fix && fix.from === draft[field] && fix.to !== draft[field]) shown = { ...shown, [field]: fix.to };
  }
  return shown;
}

export interface SpellWhilePausedOptions<F extends TextField, D extends Record<F, string>> {
  /** The texts whose spelling Leda corrects, in the order of the form. */
  fields: readonly F[];
  /** The draft as it renders, to see a pause in the typing. */
  draft: D;
  /** The draft as it is now, so an answer for a text that changed meanwhile lands nowhere. */
  latest: MutableRefObject<D>;
  /** The form's round: an answer asked for before a start over changes nothing. */
  round: MutableRefObject<number>;
  /** Whether a check may start and an answer may still land now: never while it sends (J2-30). */
  open: () => boolean;
  /** The form is editing and not sending: a pause can start. */
  editing: boolean;
  /** The door's spelling check; without one, nothing is checked while typing. */
  check: ((texts: Partial<Record<F, string>>) => Promise<Spelling>) | null;
  onClosed: () => void;
  /** The id of each text's control, to know whether the cursor is in it. */
  elementId: (field: F) => string;
  /** The field takes its correction: the form sets the draft (and renews its key, by its rule). */
  onTake: (next: D) => void;
}

/** The spelling while typing (J2-24), shared by the task's form and the objective's (J3-4b): after a
 * pause in the typing, Leda checks the text and the preview shows it corrected at once (`shown`);
 * the field takes it when the person leaves it (`takeFix`), never under her cursor. Each correction
 * holds only for the text it was made for; an answer for a text that changed, for an older round or
 * for a check asked before the last send (`forSend`) is dropped, and while it sends nothing is asked
 * nor lands (J2-30). `checked` is each text as Leda last checked or corrected it: it is not checked
 * again, also on confirm. */
export function useSpellWhilePaused<F extends TextField, D extends Record<F, string>>(
  options: SpellWhilePausedOptions<F, D>,
) {
  const { fields, draft, editing } = options;
  // The options of this render, for the checks that answer later.
  const now = useRef(options);
  now.current = options;
  const [fixes, setFixesState] = useState<Partial<Record<F, SpellFix>>>({});
  const fixesNow = useRef(fixes);
  // The text of each field whose check is on its way.
  const asking = useRef<Partial<Record<F, string>>>({});
  const checked = useRef<Partial<Record<F, string>>>({});
  // Each send is a new one: a check asked before it lands nowhere (what goes was settled then).
  const sends = useRef(0);

  function setFix(field: F, fix: SpellFix | null) {
    const next = { ...fixesNow.current };
    if (fix) next[field] = fix;
    else delete next[field];
    fixesNow.current = next;
    setFixesState(next);
  }

  /** The person left the field (or was not in it): it takes the correction made for its text. */
  function takeFix(field: F) {
    const o = now.current;
    if (!o.open()) return;
    const fix = fixesNow.current[field];
    if (!fix) return;
    setFix(field, null);
    if (o.latest.current[field] !== fix.from || fix.to === fix.from) return;
    o.onTake({ ...o.latest.current, [field]: fix.to });
  }

  async function checkNow(field: F, text: string) {
    const o = now.current;
    if (!o.check || !o.open()) return;
    const started = o.round.current;
    const send = sends.current;
    asking.current[field] = text;
    let spelling: Spelling;
    try {
      spelling = await o.check({ [field]: text } as Partial<Record<F, string>>);
    } catch (error) {
      if (error instanceof SessionClosedError) now.current.onClosed();
      return;
    } finally {
      if (asking.current[field] === text) delete asking.current[field];
    }
    const later = now.current;
    // Started over, sent meanwhile, or the text changed: the answer is for a text that is gone.
    if (!later.open() || later.round.current !== started || sends.current !== send || later.latest.current[field] !== text) {
      return;
    }
    // It could not check: nothing is said now (the text stays as typed); confirm tries again.
    if (spelling.unchecked.includes(field)) return;
    const to = spelling.corrected[field]?.text;
    if (to === undefined || to === text) {
      checked.current[field] = text;
      return;
    }
    checked.current[field] = to;
    setFix(field, { from: text, to });
    if (document.activeElement?.id !== later.elementId(field)) takeFix(field);
  }

  // A pause in the typing: only the texts and whether it is editing.
  const texts = JSON.stringify(fields.map((f) => draft[f]));
  useEffect(() => {
    const o = now.current;
    if (!o.check || !editing || !o.open()) return;
    const waiting = o.fields.filter(
      (f) =>
        o.draft[f].trim() &&
        checked.current[f] !== o.draft[f] &&
        fixesNow.current[f]?.from !== o.draft[f] &&
        asking.current[f] !== o.draft[f],
    );
    if (waiting.length === 0) return;
    const timer = setTimeout(() => {
      for (const field of waiting) void checkNow(field, now.current.latest.current[field]);
    }, SPELL_PAUSE_MS);
    return () => clearTimeout(timer);
  }, [texts, editing]);

  /** Confirm: the draft as the preview shows it, with the corrections made while typing taken; a
   * check asked before this send lands nowhere. */
  function forSend(current: D): D {
    sends.current += 1;
    const sent = withFixesOf(current, fields, fixesNow.current);
    if (Object.keys(fixesNow.current).length > 0) {
      fixesNow.current = {};
      setFixesState({});
    }
    return sent;
  }

  /** The person changed these fields: a correction made for the text before no longer holds. */
  function forget(changed: readonly string[]) {
    for (const field of fields) if (changed.includes(field) && fixesNow.current[field]) setFix(field, null);
  }

  /** A start over: nothing checked, nothing on its way, no correction. */
  function reset() {
    checked.current = {};
    asking.current = {};
    fixesNow.current = {};
    setFixesState({});
  }

  return {
    fixes,
    shown: (current: D) => withFixesOf(current, fields, fixes),
    takeFix,
    forSend,
    forget,
    reset,
    checked,
  };
}
