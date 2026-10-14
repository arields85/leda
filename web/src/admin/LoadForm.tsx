import { Check } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { SessionClosedError } from '../api';
import { shortDate } from '../format';
import {
  askLeda,
  checkSpelling,
  HELP_FAILED,
  loadTask,
  type Options,
  type Problem,
  type Proposal,
  reviewTask,
  SPELLING_FAILED,
  type Spelling,
  type TextField,
  transcribe,
} from './api';
import { Completing } from './Completing';
import { INPUT, PRIMARY, SECONDARY, WARN } from './controls';
import { Counter } from './Counter';
import { DatePicker, dayLabel } from './DatePicker';
import { Dropdown } from './Dropdown';
import { FieldBlock, Mark } from './FieldBlock';
import { bringTo, FieldList, focusField as focusElement } from './FieldList';
import { HelpBox, type HelpState, STORY_MISSING } from './HelpBox';
import {
  checkDraft,
  clearedBy,
  type Draft,
  dueAfterObjectiveText,
  EMPTY_DRAFT,
  evidenceKinds,
  evidenceWords,
  type Field,
  FIELD_ID,
  FIELD_NAME,
  FIELD_ORDER,
  LATE_FOR_OBJECTIVE,
  lateForObjective,
  LIMITS,
  memberOf,
  newKey,
  policyOf,
  PROBLEM_FIELD,
  proposedCriterion,
  REFUSED_CRITERION,
  sameKinds,
  TEXT_FIELDS,
  toCheck,
  toInput,
  validProposal,
  waitableTasks,
  waitLabel,
} from './draft';
import { useSpellWhilePaused } from './spellWhilePaused';
import { TaskPreview } from './TaskPreview';
import { FIELD_HINT, FIELD_TITLE, FIELD_VALUE } from './typography';

type Step =
  | { kind: 'edit'; sending: boolean; failed: boolean; checking?: boolean }
  | { kind: 'done'; warnings: Problem[]; repeated: boolean; sent: Draft; notice: string | null };

/** Takes the person to a field of the task form (`FieldList.focusField`). */
function focusField(field: Field) {
  focusElement(FIELD_ID[field]);
}

/** A field of the task form as a summary names it. */
function named(fields: Field[]) {
  return fields.map((field) => ({ key: field, name: FIELD_NAME[field], elementId: FIELD_ID[field] }));
}

/** Whether the server looked the key up before refusing: not with a malformed value, nor with a
 * criterion it refused (J2-9 and J2-14), which it decides before loading. */
function lookedUpTheKey(problem: Problem): boolean {
  return !problem.motivo.startsWith('mal_formad') && !(problem.campo === 'criterio' && REFUSED_CRITERION.includes(problem.motivo));
}

/** The local problems first, then the ones already shown that the local check does not repeat
 * (what the server said). */
function merge(found: Problem[], shown: Problem[]): Problem[] {
  return [...found, ...shown.filter((p) => !found.some((f) => f.campo === p.campo && f.motivo === p.motivo))];
}

/** The fields with a problem, in the order of the form. */
function fieldsWith(problems: Problem[]): Field[] {
  return FIELD_ORDER.filter((field) => problems.some((p) => PROBLEM_FIELD[p.campo] === field));
}

/** The criterion Leda proposes with a refusal (J2-14 and J2-17: written by the AI in its own
 * words), with a one-tap button to use it. A shortcut: the person can also write her own. */
function CriterionOffer({ text, onUse }: { text: string; onUse: () => void }) {
  return (
    <div className="flex min-w-0 flex-col gap-2 rounded-card border-hard border-line-soft px-3 py-2.5">
      <p className={`m-0 ${FIELD_HINT}`}>
        <span className="text-propuesto">Leda propone:</span>
      </p>
      <p className={`m-0 wrap-break-word ${FIELD_VALUE}`}>{text}</p>
      <button type="button" className={`${SECONDARY} w-fit`} onClick={onUse}>
        &gt; usar este criterio
      </button>
    </div>
  );
}

interface LoadFormProps {
  spaceId: string;
  options: Options;
  admin: string;
  onClosed: () => void;
}

/** The form that loads a committed task (decision 9): it offers only what can be chosen, shows
 * the task live as it will look ("Vista previa") with "confirmar" right below it, and saves it
 * only when confirmed (decision 6). While it sends, the form is locked, so what is shown is what
 * goes. One idempotency key per attempt: kept across retries of the same data, renewed after a
 * success or when the data changes, so a double send never loads two tasks. */
export function LoadForm({ spaceId, options, admin, onClosed }: LoadFormProps) {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [step, setStep] = useState<Step>({ kind: 'edit', sending: false, failed: false });
  const [problems, setProblems] = useState<Problem[]>([]);
  // Asks for the person to be taken to a field (null: to the messages), after the render that
  // shows its message. `n` makes every ask a new one, even for the same field.
  const [focusAsked, setFocusAsked] = useState<{ field: Field | null; n: number } | null>(null);
  // The field the last tap took the person to: the next tap goes to the next one that still has
  // a problem, in the order of the form, and back to the first after the last.
  const visited = useRef<Field | null>(null);
  const key = useRef<string | null>(null);
  // The last send got no definite answer (no network, a server failure): it may have loaded the
  // task. Until something settles it, the key stays even if the data changes, so the server can
  // tell (a different task with that key is refused, never loaded twice).
  const unknown = useRef(false);
  // A send is in progress (J2-30): from the checks on confirm to the load's answer. Meanwhile the
  // form is locked and nothing that arrives late changes it, nor the key (a correction of the
  // spelling, an answer of Leda): a retry goes with the same key and the same data.
  const sendingRef = useRef(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const messages = useRef<HTMLDivElement>(null);
  // The free box (portion J2): what the person told, Leda's answer, and the fields it filled,
  // marked until the person changes them. `latest` is the draft as it is now, so a proposal that
  // arrives while the person types never overwrites what was typed in the meantime.
  const [story, setStory] = useState('');
  const [help, setHelp] = useState<HelpState>({ kind: 'idle' });
  const [proposed, setProposed] = useState<ReadonlySet<Field>>(new Set());
  // The kinds of evidence Leda proposed and ticked (J2-18 and J2-19: only those are ticked, never
  // the area's list on its own), marked until the person changes them; they stay when she picks
  // another person whose area knows them.
  const [ledaEvidence, setLedaEvidence] = useState<ReadonlySet<string>>(new Set());
  // J2-20: "empezar de nuevo" asks first, inline, because it loses what was typed.
  const [clearing, setClearing] = useState(false);
  // Each start over is a new round: an answer of Leda asked for before it fills nothing.
  const round = useRef(0);
  // What Leda could not complete, each one shown on its field in the falta color (J2-13: in the
  // phone retest "No encontré a … en el equipo" was only a gray line in the box, out of sight),
  // until the person fills that field or asks again. The box's summary reads these same notes,
  // with the ones that belong to no field.
  const [notes, setNotes] = useState<Problem[]>([]);
  const latest = useRef(draft);
  latest.current = draft;
  const latestStory = useRef(story);
  latestStory.current = story;
  // The spelling (J2-17 and J2-23): what to say when it could not check. A correction is not
  // marked (J2-23): Leda corrects single words, never what the person says. J2-24 (the user: "la
  // ortografía la idea es que la corrija en la vista previa, sin tener que apretar confirmar"):
  // after a pause in the typing, Leda checks the text and the preview shows it corrected at once;
  // the field takes it when the person leaves it, never under her cursor (`useSpellWhilePaused`,
  // shared with the objective's form, with the J2-30 rules). `spell.checked` is each text as Leda
  // last checked or corrected it: a text that is still so is not checked again.
  const [spellNote, setSpellNote] = useState<string | null>(null);
  const spell = useSpellWhilePaused<TextField, Draft>({
    fields: TEXT_FIELDS,
    draft,
    latest,
    round,
    open: () => !sendingRef.current,
    editing: step.kind === 'edit' && !step.sending,
    check: (texts) => checkSpelling(spaceId, texts),
    onClosed,
    elementId: (field) => `f-${field}`,
    onTake: (next) => {
      latest.current = next;
      setDraft(next);
      // Other data, another attempt (as in `change`).
      if (!unknown.current) key.current = null;
    },
  });

  useEffect(() => {
    if (step.kind === 'done') heading.current?.focus();
  }, [step.kind]);

  useEffect(() => {
    if (!focusAsked) return;
    if (focusAsked.field) focusField(focusAsked.field);
    else if (messages.current) bringTo(messages.current, messages.current);
    // Only when asked: fixing a field must not move the focus.
  }, [focusAsked]);

  /** Takes the person to `field` (or to the messages) and remembers it for the next tap. */
  function takeTo(field: Field | null) {
    visited.current = field;
    setFocusAsked((current) => ({ field, n: (current?.n ?? 0) + 1 }));
  }

  const member = memberOf(options, draft.responsable_id);
  const policy = policyOf(options, member);
  const kinds = evidenceKinds(policy);
  const waitable = waitableTasks(options);

  function change(patch: Partial<Draft>) {
    setDraft((current) => ({ ...current, ...patch }));
    // What the person changes is hers: the mark goes.
    const changed = Object.keys(patch) as Field[];
    setProposed((marked) =>
      changed.some((f) => marked.has(f)) ? new Set([...marked].filter((f) => !changed.includes(f))) : marked,
    );
    // An edited text is checked again on confirm, so the notice that it could not be checked goes.
    if (TEXT_FIELDS.some((f) => changed.includes(f))) setSpellNote(null);
    // A correction made for the text before this change no longer holds (J2-24).
    spell.forget(changed);
    // Other data, another attempt: a new key, so it never collides with the one already sent.
    // Not while the last send's outcome is unknown: that one may have loaded the task.
    if (!unknown.current) key.current = null;
    setStep((current) => (current.kind === 'edit' && current.failed ? { ...current, failed: false } : current));
    const touched = new Set(Object.keys(patch));
    setProblems((current) => current.filter((p) => !clearedBy(p, touched)));
    setNotes((current) => current.filter((n) => !clearedBy(n, touched)));
  }

  /** Takes the criterion Leda proposed with a refusal: it fills the field (the notice goes, as
   * with any change) and stays marked as hers until the person edits it. */
  function takeCriterion(text: string) {
    change({ criterio: text });
    setProposed((marked) => new Set([...marked, 'criterio']));
  }

  /** Choosing who does it ticks nothing (J2-19, the user: "debería quedar sólo tildado lo que Leda
   * propone"): what her area asks for is said next to each kind, as information. What was ticked
   * stays if her area knows it, and Leda's mark with it. */
  function chooseResponsible(id: string) {
    const known = evidenceKinds(policyOf(options, memberOf(options, id)));
    const kept = latest.current.evidencia.filter((k) => known.includes(k));
    change({ responsable_id: id, evidencia: known.filter((k) => kept.includes(k)) });
    setLedaEvidence((marked) => new Set([...marked].filter((k) => kept.includes(k))));
  }

  /** Fills only what is still empty with what Leda proposed (only what the options offer), and
   * marks it. The evidence (J2-19): only what Leda proposed is ticked, and marked, only kinds the
   * area of whoever does it knows, and only when the person ticked none: what she ticked is hers.
   * What stays ticked is only what that area knows (J2-30, as in `chooseResponsible`): a kind it
   * does not know would be ticked and hidden. Returns how many fields it filled. */
  function apply(proposal: Proposal): number {
    const current = latest.current;
    const valid = validProposal(proposal, options);
    const filled = (Object.keys(valid) as Exclude<keyof Proposal, 'evidencia'>[]).filter(
      (field) => !current[field].trim(),
    );
    const next: Draft = { ...current };
    for (const field of filled) next[field] = valid[field] as string;
    const known = evidenceKinds(policyOf(options, memberOf(options, next.responsable_id)));
    const offered = Array.isArray(proposal.evidencia) ? proposal.evidencia : [];
    const added =
      current.evidencia.length > 0 ? [] : known.filter((k) => offered.includes(k));
    if (filled.length === 0 && added.length === 0) return 0;
    next.evidencia = added.length > 0 ? added : current.evidencia.filter((k) => known.includes(k));
    latest.current = next;
    setDraft(next);
    // Other data, another attempt (as in `change`).
    if (!unknown.current) key.current = null;
    setProposed((marked) => new Set([...marked, ...filled]));
    if (added.length > 0) setLedaEvidence((marked) => new Set([...marked, ...added]));
    const touched = new Set<string>([...filled, ...(added.length > 0 ? ['evidencia'] : [])]);
    setProblems((shown) => shown.filter((p) => !clearedBy(p, touched)));
    setNotes((shown) => shown.filter((n) => !clearedBy(n, touched)));
    return filled.length + added.length;
  }

  async function ask() {
    if (help.kind === 'asking') return;
    const asking = round.current;
    const texto = story.trim();
    if (!texto) {
      setHelp({ kind: 'rejected', errors: [{ campo: 'texto', motivo: 'falta', texto: STORY_MISSING }] });
      return;
    }
    setHelp({ kind: 'asking' });
    setNotes([]);
    const { objetivo_id, titulo, descripcion, responsable_id, fecha, espera_id, criterio, evidencia } =
      latest.current;
    const asked = { objetivo_id, titulo, descripcion, responsable_id, fecha, espera_id, criterio };
    try {
      const result = await askLeda(spaceId, { texto, ...asked, evidencia: [...evidencia] });
      // The person started over meanwhile (J2-20): the answer is for a form that is gone.
      if (round.current !== asking) return;
      // It is sending (J2-30): the form is locked and what goes is what it shows; nothing fills.
      if (sendingRef.current) {
        setHelp({ kind: 'stale' });
        return;
      }
      // The answer is for what the form had when she asked. If she changed the free text or a
      // field meanwhile, it may no longer fit (another person, another wait, other words): it
      // fills nothing, and the box says so quietly (review review-03b5c3a74d3719b7). The evidence
      // counts as the set of kinds ticked (R3-001: the form fills nothing when it changed, and a
      // kind ticked and unticked again is the same evidence).
      const now = latest.current;
      const changed =
        latestStory.current.trim() !== texto ||
        !sameKinds(now.evidencia, evidencia) ||
        (Object.keys(asked) as (keyof typeof asked)[]).some((field) => now[field] !== asked[field]);
      if (changed && result.kind !== 'failed') {
        setHelp({ kind: 'stale' });
      } else if (result.kind === 'proposed') {
        const filled = apply(result.proposal);
        // Only on the fields still empty: what the person wrote meanwhile is hers. A note that
        // belongs to no field stays for the box.
        setNotes(
          result.notes.filter((n) => {
            const field = PROBLEM_FIELD[n.campo];
            return field === undefined || !String(latest.current[field] ?? '').trim();
          }),
        );
        const choices = latest.current.responsable_id
          ? []
          : result.choices.filter((c) => memberOf(options, c.membership_id));
        setHelp({
          kind: 'done',
          choices,
          nothing: filled === 0 && result.notes.length === 0 && choices.length === 0,
        });
      } else if (result.kind === 'rejected') {
        setHelp({ kind: 'rejected', errors: result.errors });
      } else {
        setHelp({ kind: 'failed', text: result.text });
      }
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else if (round.current === asking) setHelp({ kind: 'failed', text: HELP_FAILED });
    }
  }

  /** The dictation at this space's administration address (J2b). */
  function dictate(audio: Blob) {
    return transcribe(spaceId, audio);
  }

  /** The person picked who does it among the ones that fit the name: her choice, not marked. */
  function choose(id: string) {
    if (memberOf(options, id)) chooseResponsible(id);
    setHelp((current) => (current.kind === 'done' ? { ...current, choices: [] } : current));
  }

  function toggleEvidence(kind: string, on: boolean) {
    const chosen = new Set(draft.evidencia);
    if (on) chosen.add(kind);
    else chosen.delete(kind);
    change({ evidencia: kinds.filter((k) => chosen.has(k)) });
    // What the person changes is hers: Leda's mark on that kind goes.
    setLedaEvidence((marked) => (marked.has(kind) ? new Set([...marked].filter((k) => k !== kind)) : marked));
  }

  async function confirm() {
    if (step.kind !== 'edit' || step.sending || sendingRef.current) return;
    // Something required is missing (the button looks disabled): nothing is sent; each field
    // shows its message and the tap takes the person to the next field with a problem.
    const found = checkDraft(draft, options);
    if (found.length > 0) {
      const shown = merge(found, problems);
      setProblems(shown);
      const fields = fieldsWith(shown);
      const after = visited.current ? FIELD_ORDER.indexOf(visited.current) : -1;
      takeTo(fields.find((field) => FIELD_ORDER.indexOf(field) > after) ?? fields[0] ?? null);
      return;
    }
    // J2-24: what loads is what the preview shows, with the corrections made while typing; the
    // form shows it too, so a retry sends the same data.
    const sent = spell.forSend(draft);
    if (sent !== draft) {
      latest.current = sent;
      setDraft(sent);
      if (!unknown.current) key.current = null;
    }
    sendingRef.current = true;
    try {
      await send(sent, spellNote);
    } finally {
      sendingRef.current = false;
    }
  }

  /** From the checks on confirm to the load's answer (`confirm`), while `sendingRef` holds. */
  async function send(draftToSend: Draft, noticeBefore: string | null) {
    let sent = draftToSend;
    let notice = noticeBefore;
    // J2-17 and J2-23: before loading, Leda corrects the spelling of the texts not checked yet as
    // they are, and what loads is the corrected text, in the same confirm and unmarked (the user:
    // "que lo corrija directamente sin resaltarlo"; the server accepts only the same word misspelled
    // or a name as the team's data has it). If it could not check, nothing blocks: it loads as
    // written, with the notice.
    const asked = toCheck(sent, spell.checked.current);
    if (asked.length > 0) {
      setStep({ kind: 'edit', sending: true, failed: false, checking: true });
      // J2-21: first what the load would refuse (the criterion's judgment and the rest), so a
      // criterion that is going to be refused is never corrected first and the person does not
      // confirm twice. Nothing loads and the key is not used; without an answer, it goes on.
      let review: Awaited<ReturnType<typeof reviewTask>>;
      try {
        review = await reviewTask(spaceId, toInput(sent, key.current ?? ''));
      } catch (error) {
        if (error instanceof SessionClosedError) {
          onClosed();
          return;
        }
        review = { kind: 'unknown' };
      }
      if (review.kind === 'rejected' && review.errors.length > 0) {
        setProblems(review.errors);
        setStep({ kind: 'edit', sending: false, failed: false });
        takeTo(fieldsWith(review.errors)[0] ?? null);
        return;
      }
      let spelling: Spelling;
      try {
        spelling = await checkSpelling(spaceId, Object.fromEntries(asked.map((f) => [f, sent[f]])));
      } catch (error) {
        if (error instanceof SessionClosedError) {
          onClosed();
          return;
        }
        spelling = { corrected: {}, unchecked: asked, notice: SPELLING_FAILED };
      }
      const fixed = asked.filter((f) => {
        const fix = spelling.corrected[f];
        return fix !== undefined && fix.text !== sent[f];
      });
      const next: Draft = { ...sent };
      for (const field of fixed) next[field] = spelling.corrected[field]!.text;
      // Only what was really checked counts as checked: a text the check could not look at (the
      // AI did not answer, no network) is checked again on the next confirm (RDD warning, J2-17).
      for (const field of asked) {
        if (!spelling.unchecked.includes(field)) spell.checked.current[field] = next[field];
      }
      notice = spelling.unchecked.length > 0 ? (spelling.notice ?? SPELLING_FAILED) : null;
      setSpellNote(notice);
      if (fixed.length > 0) {
        // The form shows what goes, so a retry sends the same data with the same key.
        latest.current = next;
        setDraft(next);
        // Other data, another attempt (as in `change`).
        if (!unknown.current) key.current = null;
      }
      sent = next;
    }
    key.current ??= newKey();
    setStep({ kind: 'edit', sending: true, failed: false });
    try {
      const result = await loadTask(spaceId, toInput(sent, key.current));
      if (result.kind === 'loaded') {
        key.current = null;
        unknown.current = false;
        visited.current = null;
        setProblems([]);
        setStep({
          kind: 'done',
          warnings: result.warnings,
          repeated: result.repeated,
          sent,
          notice,
        });
      } else {
        // A rejection writes nothing, and the server looked the key up first: nothing was loaded
        // with it, unless the key was used with other data (the conflict below), some data came
        // malformed or the criterion does not say how it is checked (then the server never looks
        // the key up).
        if (!result.errors.some((e) => e.campo === 'clave' || !lookedUpTheKey(e))) {
          unknown.current = false;
        }
        setProblems(result.errors);
        setStep({ kind: 'edit', sending: false, failed: false });
        takeTo(fieldsWith(result.errors)[0] ?? null);
      }
    } catch (error) {
      if (error instanceof SessionClosedError) {
        onClosed();
      } else {
        unknown.current = true;
        setStep({ kind: 'edit', sending: false, failed: true });
      }
    }
  }

  /** After a key conflict: the administrator checked the team's tasks and starts over. */
  function newAttempt() {
    key.current = null;
    unknown.current = false;
    setProblems((current) => current.filter((p) => p.campo !== 'clave'));
  }

  function another() {
    round.current += 1;
    // A new round also remounts the free box (`key`): a dictation in progress is cancelled.
    key.current = null;
    unknown.current = false;
    visited.current = null;
    setClearing(false);
    setStory('');
    setHelp({ kind: 'idle' });
    setNotes([]);
    setProposed(new Set());
    setLedaEvidence(new Set());
    spell.reset();
    setSpellNote(null);
    setDraft(EMPTY_DRAFT);
    setProblems([]);
    setStep({ kind: 'edit', sending: false, failed: false });
  }

  if (step.kind === 'done') {
    return (
      <section aria-labelledby="cargada" className="flex w-full min-w-0 max-w-[40rem] flex-col gap-3.5">
        <h2 id="cargada" ref={heading} tabIndex={-1} className="m-0 text-button font-bold outline-none">
          {step.repeated ? 'Esta tarea ya estaba cargada.' : 'Tarea cargada.'}
        </h2>
        {(step.warnings.length > 0 || step.notice) && (
          <ul className="m-0 flex list-none flex-col gap-1 p-0 text-body text-ink-soft">
            {step.warnings.map((w) => (
              <li key={`${w.campo}-${w.motivo}`} className="flex min-w-0 items-start gap-1.5">
                <Mark />
                <span className="min-w-0">{w.texto}</span>
              </li>
            ))}
            {step.notice && (
              <li className="flex min-w-0 items-start gap-1.5">
                <Mark />
                <span className="min-w-0">{step.notice}</span>
              </li>
            )}
          </ul>
        )}
        <TaskPreview draft={step.sent} options={options} admin={admin} />
        <div>
          <button type="button" className={PRIMARY} onClick={another}>
            &gt; cargar otra
          </button>
        </div>
      </section>
    );
  }

  const { sending, failed, checking } = step;
  const on = (field: Field) => problems.filter((p) => PROBLEM_FIELD[p.campo] === field);
  // On a field: its problems and what Leda could not complete there (never the same one twice).
  const said = (field: Field) => [
    ...on(field),
    ...notes.filter(
      (n) => PROBLEM_FIELD[n.campo] === field && !on(field).some((p) => p.campo === n.campo && p.motivo === n.motivo),
    ),
  ];
  const conflict = problems.some((p) => p.campo === 'clave' && p.motivo === 'usada_con_otros_datos');
  const general = problems.filter(
    (p) => !(p.campo in PROBLEM_FIELD) && !(p.campo === 'clave' && p.motivo === 'usada_con_otros_datos'),
  );
  // What blocks confirm right now, said from the start and updated as the fields are filled; the
  // fields themselves are marked only after a tap on confirm (or the server's answer).
  const pending = checkDraft(draft, options);
  const blocked = pending.length > 0;
  const listed = merge(pending, problems);
  const missing = fieldsWith(listed.filter((p) => p.motivo === 'falta'));
  const wrong = fieldsWith(listed).filter((field) => !missing.includes(field));
  const summary = missing.length > 0 || wrong.length > 0 || general.length > 0;
  // After a tap that found problems the summary is an alert (a new one for each ask, so it is
  // announced again); before, only a line.
  const alerted = problems.length > 0;
  const invalid = (field: Field) => (on(field).length ? true : undefined);
  const criterionOffer = proposedCriterion(on('criterio'));
  // J2-20: there is something to clear when anything was typed, chosen, ticked or told.
  const somethingToClear =
    story.trim() !== '' ||
    draft.evidencia.length > 0 ||
    (Object.keys(EMPTY_DRAFT) as Field[]).some((f) => f !== 'evidencia' && String(draft[f]).trim() !== '');
  const described = (id: string, field: Field) => (said(field).length ? `${id}-error` : undefined);
  // Decision 6 (2026-10-14): a task that falls due after its objective is stopped before loading,
  // said from the start next to the date and next to confirm; once a tap marks the date, the field
  // says it in its message instead of its hint.
  const late = lateForObjective(draft, options);
  const lateText = late ? dueAfterObjectiveText(late) : null;
  const lateOnField = on('fecha').some((p) => p.motivo === LATE_FOR_OBJECTIVE);

  return (
    <div className="grid w-full min-w-0 max-w-full grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-10">
      <form
        noValidate
        onSubmit={(event) => event.preventDefault()}
        aria-label="Cargar tarea"
        className="flex min-w-0 max-w-full flex-col"
      >
        <fieldset disabled={sending} className="m-0 flex min-w-0 flex-col gap-4 border-0 p-0">
          <HelpBox key={round.current} transcribe={dictate} onClosed={onClosed} story={story} onStory={setStory} help={help} notes={notes} onAsk={ask} onChoose={choose} />

          <FieldBlock id="f-objetivo" label="Objetivo" errors={said('objetivo_id')} proposed={proposed.has('objetivo_id')}
            hint={options.objetivos.length === 0 ? 'No hay objetivos abiertos en este espacio.' : undefined}>
            <Dropdown
              id="f-objetivo"
              labelledBy="f-objetivo-label"
              value={draft.objetivo_id}
              onChange={(value) => change({ objetivo_id: value })}
              invalid={invalid('objetivo_id')}
              describedBy={described('f-objetivo', 'objetivo_id')}
              options={[
                { value: '', label: 'elegí un objetivo' },
                ...options.objetivos.map((o) => ({
                  value: o.id,
                  label: `${o.titulo}${o.fecha_objetivo ? ` · hasta ${shortDate(o.fecha_objetivo)}` : ''}`,
                })),
              ]}
            />
          </FieldBlock>

          <FieldBlock id="f-titulo" label="Título" errors={said('titulo')} proposed={proposed.has('titulo')}
            extra={<Counter value={draft.titulo} limit={LIMITS.titulo} />}>
            <input
              id="f-titulo"
              className={INPUT}
              value={draft.titulo}
              onChange={(e) => change({ titulo: e.target.value })}
              onBlur={() => spell.takeFix('titulo')}
              aria-invalid={invalid('titulo')}
              aria-describedby={described('f-titulo', 'titulo')}
              autoComplete="off"
            />
          </FieldBlock>

          <FieldBlock id="f-descripcion" label="Descripción (opcional)" errors={said('descripcion')}
            proposed={proposed.has('descripcion')}
            extra={<Counter value={draft.descripcion} limit={LIMITS.descripcion} />}>
            <textarea
              id="f-descripcion"
              className={`${INPUT} min-h-20 resize-y`}
              value={draft.descripcion}
              onChange={(e) => change({ descripcion: e.target.value })}
              onBlur={() => spell.takeFix('descripcion')}
              aria-invalid={invalid('descripcion')}
              aria-describedby={described('f-descripcion', 'descripcion')}
            />
          </FieldBlock>

          <FieldBlock
            id="f-responsable"
            label="Quién la hace"
            errors={said('responsable_id')}
            proposed={proposed.has('responsable_id')}
            hint={
              member && (
                <span className="flex flex-wrap gap-x-2">
                  <span>{member.area}</span>
                  <span>· la revisa: {member.revisa?.nombre ?? 'nadie'}</span>
                  {!member.conectado && <span className="font-bold text-ink-soft">[SIN CONECTAR]</span>}
                </span>
              )
            }
          >
            <Dropdown
              id="f-responsable"
              labelledBy="f-responsable-label"
              value={draft.responsable_id}
              onChange={chooseResponsible}
              invalid={invalid('responsable_id')}
              describedBy={described('f-responsable', 'responsable_id')}
              options={[
                { value: '', label: 'elegí a una persona' },
                ...options.integrantes.map((m) => ({
                  value: m.membership_id,
                  label: `${m.nombre} · ${m.area}${m.conectado ? '' : ' · sin conectar'}`,
                })),
              ]}
            />
          </FieldBlock>

          <FieldBlock
            id="f-fecha"
            label="Fecha"
            errors={said('fecha')}
            proposed={proposed.has('fecha')}
            extra={draft.fecha ? <span className={`shrink-0 ${FIELD_VALUE}`}>{dayLabel(draft.fecha)}</span> : undefined}
            hint={
              lateText && !lateOnField ? (
                <span className={`font-bold ${WARN}`}>{lateText}</span>
              ) : (
                'Sólo los días hábiles del espacio, desde hoy.'
              )
            }
          >
            <DatePicker
              id="f-fecha"
              days={options.calendario.dias_habiles}
              value={draft.fecha}
              onChange={(day) => change({ fecha: day })}
              labelledBy="f-fecha-label"
              describedBy={described('f-fecha', 'fecha')}
              invalid={on('fecha').length > 0}
            />
          </FieldBlock>

          <FieldBlock
            id="f-espera"
            label="Espera a (opcional)"
            errors={said('espera_id')}
            proposed={proposed.has('espera_id')}
            hint={
              waitable.length === 0
                ? 'No hay tareas abiertas para esperar en este espacio.'
                : draft.espera_id
                  ? 'No puede empezar hasta que esa esté terminada.'
                  : 'Si no puede empezar hasta que otra tarea esté terminada.'
            }
          >
            <Dropdown
              id="f-espera"
              labelledBy="f-espera-label"
              value={draft.espera_id}
              onChange={(value) => change({ espera_id: value })}
              invalid={invalid('espera_id')}
              describedBy={described('f-espera', 'espera_id')}
              options={[
                { value: '', label: 'no espera a ninguna' },
                ...waitable.map((t) => ({ value: t.id, label: waitLabel(t) })),
              ]}
            />
          </FieldBlock>

          <FieldBlock id="f-criterio" label="Criterio de aceptación" errors={said('criterio')}
            proposed={proposed.has('criterio')}
            extra={<Counter value={draft.criterio} limit={LIMITS.criterio} />}
            hint="Qué tiene que pasar para darla por terminada."
            after={criterionOffer && (
              <CriterionOffer text={criterionOffer} onUse={() => takeCriterion(criterionOffer)} />
            )}>
            <textarea
              id="f-criterio"
              className={`${INPUT} min-h-20 resize-y`}
              value={draft.criterio}
              onChange={(e) => change({ criterio: e.target.value })}
              onBlur={() => spell.takeFix('criterio')}
              aria-invalid={invalid('criterio')}
              aria-describedby={described('f-criterio', 'criterio')}
            />
          </FieldBlock>

          <fieldset
            id="f-evidencia"
            data-field
            tabIndex={-1}
            className="m-0 flex min-w-0 flex-col gap-1.5 border-0 p-0 outline-none"
            aria-describedby={described('f-evidencia', 'evidencia')}
          >
            <legend className={`mb-1.5 p-0 ${FIELD_TITLE}`}>Evidencia que se pide</legend>
            {!member && <p className={`m-0 ${FIELD_HINT}`}>Elegí primero quién la hace.</p>}
            {member && !policy && (
              <p className={`m-0 ${FIELD_HINT}`}>El área de esa persona todavía no tiene definida qué evidencia se pide.</p>
            )}
            {member && policy && kinds.length === 0 && (
              <p className={`m-0 ${FIELD_HINT}`}>El área no pide evidencia.</p>
            )}
            {kinds.map((kind) => (
              <label key={kind} className={`flex min-w-0 cursor-pointer items-center gap-2 ${FIELD_VALUE}`}>
                {/* J2-28 (the user's phone test, 2026-10-13: ticked and empty looked alike): the
                    native checkbox stays, hidden to the eye, for the keyboard, the screen reader and
                    a tap on its words; what shows is a square with no background in either state,
                    and a check mark in ink only when it is ticked. */}
                <input
                  type="checkbox"
                  className="peer sr-only"
                  checked={draft.evidencia.includes(kind)}
                  onChange={(e) => toggleEvidence(kind, e.target.checked)}
                />
                <span
                  data-box
                  aria-hidden="true"
                  className="inline-flex size-4 shrink-0 items-center justify-center rounded-[3px] border-hard border-ink-soft bg-transparent text-ink peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-ink"
                >
                  {draft.evidencia.includes(kind) && <Check strokeWidth={3.5} className="size-3.5" />}
                </span>
                <span className="min-w-0 wrap-break-word">
                  {evidenceWords(policy, kind)}
                  {policy?.evidencia_requerida.includes(kind) && (
                    <span className="text-ink-dim"> · la pide el área</span>
                  )}
                  {ledaEvidence.has(kind) && draft.evidencia.includes(kind) && (
                    <span className="text-propuesto"> · propuesto por Leda</span>
                  )}
                </span>
              </label>
            ))}
            {on('evidencia').length > 0 && (
              <ul id="f-evidencia-error" className={`m-0 flex list-none flex-col gap-0.5 p-0 text-small font-bold ${WARN}`}>
                {on('evidencia').map((e) => (
                  <li key={`${e.campo}-${e.motivo}`} className="flex min-w-0 items-start gap-1.5">
              <Mark />
              <span className="min-w-0">{e.texto}</span>
            </li>
                ))}
              </ul>
            )}
          </fieldset>

          <FieldBlock id="f-decidio" label="Quién la decidió" errors={said('decidio_id')}>
            <Dropdown
              id="f-decidio"
              labelledBy="f-decidio-label"
              value={draft.decidio_id}
              onChange={(value) => change({ decidio_id: value })}
              invalid={invalid('decidio_id')}
              describedBy={described('f-decidio', 'decidio_id')}
              options={[
                { value: '', label: 'elegí a una persona' },
                ...options.integrantes.map((m) => ({ value: m.membership_id, label: `${m.nombre} · ${m.area}` })),
              ]}
            />
          </FieldBlock>
        </fieldset>
      </form>

      <aside
        aria-labelledby="vista-previa"
        className="flex min-w-0 max-w-full flex-col gap-2 lg:sticky lg:top-4 lg:max-h-[calc(100dvh-2rem)] lg:self-start lg:overflow-y-auto"
      >
        <h2 id="vista-previa" className={`m-0 ${FIELD_TITLE}`}>
          Vista previa
        </h2>
        <TaskPreview draft={spell.shown(draft)} options={options} admin={admin} />
        <div ref={messages} tabIndex={-1} className="flex min-w-0 flex-col gap-3 pt-1.5 outline-none">
          {spellNote && <p className="m-0 text-body text-ink-soft">{spellNote}</p>}
          {failed && (
            <p role="alert" className="m-0 text-body text-ink-soft">
              No se pudo cargar: no llegó la respuesta. Los datos siguen acá; probá de nuevo.
            </p>
          )}
          {conflict && (
            <div role="alert" className="flex flex-col gap-2 rounded-card border-hard border-line px-3 py-2.5 text-body">
              <p className="m-0 font-bold">
                Puede que ya se haya cargado: fijate en "El equipo" antes de cargarla de nuevo.
              </p>
              <p className="m-0 text-ink-soft">
                El envío anterior no tuvo respuesta y esta vez cambiaron los datos.
              </p>
              <button type="button" className={`${SECONDARY} w-fit`} onClick={newAttempt}>
                no está cargada: empezar de nuevo
              </button>
            </div>
          )}
          {summary && (
            <div
              key={alerted ? `alerta-${focusAsked?.n ?? 0}` : 'en-vivo'}
              id="lo-que-falta"
              role={alerted ? 'alert' : undefined}
              className={`flex min-w-0 flex-col gap-1 wrap-break-word text-body ${WARN} ${alerted ? 'rounded-card border-hard border-line px-3 py-2.5' : ''}`}
            >
              {alerted && <p className="m-0 font-bold text-ink">No se cargó: hay que corregir lo marcado.</p>}
              <FieldList label="Falta completar" fields={named(missing)} />
              <FieldList label="Hay que corregir" fields={named(wrong)} />
              {lateText && (
                <p className="m-0 flex min-w-0 items-start gap-1.5">
                  <Mark />
                  <span className="min-w-0">{lateText}</span>
                </p>
              )}
              {general.map((p) => (
                <p key={`${p.campo}-${p.motivo}`} className="m-0 flex min-w-0 items-start gap-1.5">
                  <Mark />
                  <span className="min-w-0">{p.texto}</span>
                </p>
              ))}
            </div>
          )}
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              className={PRIMARY}
              onClick={confirm}
              disabled={sending}
              aria-disabled={blocked && !sending ? true : undefined}
              aria-describedby={summary ? 'lo-que-falta' : undefined}
              aria-label={sending ? (checking ? 'revisando…' : 'cargando…') : undefined}
            >
              {sending ? (
                <Completing word={checking ? 'revisando' : 'cargando'} />
              ) : failed ? (
                '> probar de nuevo'
              ) : (
                '> confirmar'
              )}
            </button>
            {somethingToClear && !clearing && (
              <button type="button" className={SECONDARY} onClick={() => setClearing(true)} disabled={sending}>
                &gt; empezar de nuevo
              </button>
            )}
          </div>
          {clearing && (
            <div role="group" aria-label="Empezar de nuevo" className="flex min-w-0 flex-wrap items-center gap-3 text-body">
              <p className="m-0 text-ink-soft">¿Borro todo lo que cargaste?</p>
              <button type="button" className={SECONDARY} onClick={another} disabled={sending}>
                &gt; sí, borrar
              </button>
              <button type="button" className={SECONDARY} onClick={() => setClearing(false)}>
                &gt; no
              </button>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
