import { ChevronDown, CircleAlert } from 'lucide-react';
import { type ComponentProps, Fragment, useEffect, useRef, useState, type ReactNode } from 'react';
import { SessionClosedError } from '../api';
import { shortDate } from '../format';
import { askLeda, HELP_FAILED, loadTask, type Options, type Problem, type Proposal } from './api';
import { DatePicker, dayLabel } from './DatePicker';
import { HelpBox, type HelpState } from './HelpBox';
import {
  checkDraft,
  type Draft,
  EMPTY_DRAFT,
  evidenceKinds,
  evidenceWords,
  type Field,
  FIELD_ID,
  FIELD_NAME,
  FIELD_ORDER,
  length,
  LIMITS,
  memberOf,
  newKey,
  policyOf,
  PROBLEM_FIELD,
  proposedCriterion,
  REFUSED_CRITERION,
  toInput,
  validProposal,
  waitableTasks,
  waitLabel,
} from './draft';
import { TaskPreview } from './TaskPreview';
import { CONTROL, FIELD_HINT, FIELD_TITLE, FIELD_VALUE, TEXT_SIZE } from './typography';

// The server's words when the free box is empty (src/leda/web_app.py, TEXTOS_DE_LA_AYUDA).
const STORY_MISSING = 'Contame primero qué querés hacer; con eso Leda completa lo que pueda.';

type Step =
  | { kind: 'edit'; sending: boolean; failed: boolean }
  | { kind: 'done'; warnings: Problem[]; repeated: boolean; sent: Draft };

// What is missing or wrong is said in the palette's attention color (the one of an overdue
// task): the only color on the form, and only while something needs fixing.
const WARN = 'text-falta';
// The shared box of every control (`typography.ts`), with the attention border while it is wrong.
const INPUT = `${CONTROL} aria-[invalid=true]:border-falta`;
// A list to choose from without the phone's own look, which made it bigger than a text field
// (J2-10): the same box as the others, with room for its arrow.
const SELECT = `${INPUT} appearance-none pr-9`;
// Dimmed while something required is missing, but never `disabled`: a tap still says what is
// missing and takes the person there.
const PRIMARY = `inline-flex h-11 items-center gap-2 rounded-card border-hard border-ink bg-card px-3.5 ${TEXT_SIZE} font-bold text-ink shadow-hard-ink disabled:opacity-50 aria-disabled:opacity-50 aria-disabled:shadow-none`;
const SECONDARY = `inline-flex h-11 items-center rounded-card border-hard border-line-soft bg-transparent px-3.5 ${TEXT_SIZE} text-ink-soft disabled:opacity-50`;
// Takes the color of the line it is in.
const FIELD_LINK =
  'cursor-pointer border-0 bg-transparent p-0 text-left font-bold underline decoration-dotted underline-offset-2';

/** Brings `area` to the middle of the screen with a vertical-only scroll, then focuses `target`
 * without letting the browser scroll on its own: on a phone a focus that scrolls can also move
 * the page sideways. */
function bringTo(area: HTMLElement, target: HTMLElement) {
  const box = area.getBoundingClientRect();
  const top = window.scrollY + box.top - Math.max(16, (window.innerHeight - box.height) / 2);
  const still = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  window.scrollTo({ top: Math.max(0, top), behavior: still ? 'auto' : 'smooth' });
  target.focus({ preventScroll: true });
}

/** Takes the person to a field: its whole block (label, control and message) in view, and the
 * focus on the control itself, the chosen (or first) day of the calendar, or the first evidence
 * box (the group itself when it has none). */
function focusField(field: Field) {
  const element = document.getElementById(FIELD_ID[field]);
  if (!element) return;
  const target = element.matches('input, select, textarea')
    ? element
    : (element.querySelector<HTMLElement>('[tabindex="0"], input, select, textarea') ?? element);
  bringTo(element.closest<HTMLElement>('[data-field]') ?? element, target);
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

/** "Falta completar: criterio de aceptación, evidencia." Each name takes the focus to its field. */
/** The mark in front of what the form still needs: a Lucide icon, not a "!" character (user,
 * 2026-10-13). Decorative: the text next to it says it all. */
function Mark() {
  return <CircleAlert aria-hidden="true" strokeWidth={2.25} className="mt-[0.2em] size-[1em] shrink-0" />;
}

function FieldList({ label, fields }: { label: string; fields: Field[] }) {
  if (fields.length === 0) return null;
  return (
    <p className="m-0 flex min-w-0 items-start gap-1.5">
      <Mark />
      <span className="min-w-0">
      {label}:{' '}
      {fields.map((field, i) => (
        <Fragment key={field}>
          {i > 0 && ', '}
          <button type="button" className={FIELD_LINK} onClick={() => focusField(field)}>
            {FIELD_NAME[field]}
          </button>
        </Fragment>
      ))}
      .
      </span>
    </p>
  );
}

/** The small mark of a value Leda proposed, until the person changes it. Outside the label, so
 * the field keeps its name. */
function Proposed({ on }: { on?: boolean }) {
  return on ? <span className="shrink-0 text-propuesto">· propuesto por Leda</span> : null;
}

/** A list to choose from that looks like the text fields: the same box, and an arrow of its own
 * in place of the phone's. The id, the label and the focus stay on the list itself. */
function Select({ className, ...props }: ComponentProps<'select'>) {
  return (
    <div className="relative min-w-0 max-w-full">
      <select {...props} className={className ? `${SELECT} ${className}` : SELECT} />
      <ChevronDown
        aria-hidden="true"
        size={16}
        strokeWidth={2}
        className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-ink-dim"
      />
    </div>
  );
}

function FieldBlock({
  id,
  label,
  extra,
  errors,
  hint,
  proposed,
  after,
  children,
}: {
  id: string;
  label: string;
  extra?: ReactNode;
  errors: Problem[];
  hint?: ReactNode;
  proposed?: boolean;
  // Below the messages: what Leda proposes for this field, if anything.
  after?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div data-field className="flex min-w-0 flex-col gap-1.5">
      <div className={`flex min-w-0 items-baseline justify-between gap-2 ${FIELD_HINT}`}>
        <span className="flex min-w-0 flex-wrap items-baseline gap-x-1.5">
          <label id={`${id}-label`} htmlFor={id} className={`min-w-0 ${FIELD_TITLE}`}>
            {label}
          </label>
          <Proposed on={proposed} />
        </span>
        {extra}
      </div>
      {children}
      {hint && <div className={`wrap-break-word ${FIELD_HINT}`}>{hint}</div>}
      {errors.length > 0 && (
        <ul id={`${id}-error`} className={`m-0 flex list-none flex-col gap-0.5 p-0 text-small font-bold ${WARN}`}>
          {errors.map((e) => (
            <li key={`${e.campo}-${e.motivo}`} className="flex min-w-0 items-start gap-1.5">
              <Mark />
              <span className="min-w-0">{e.texto}</span>
            </li>
          ))}
        </ul>
      )}
      {after}
    </div>
  );
}

/** The criterion Leda proposes with a refusal (J2-14): the result and the area's evidence, with a
 * one-tap button to use it. A shortcut: the person can also write her own. */
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

function Counter({ value, limit }: { value: string; limit: number }) {
  const n = length(value);
  const over = n > limit;
  return (
    <span aria-live="polite" className={`shrink-0 ${over ? `font-bold ${WARN}` : ''}`}>
      {n}/{limit}
      {over && ` · sobran ${n - limit}`}
    </span>
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
  const heading = useRef<HTMLHeadingElement>(null);
  const messages = useRef<HTMLDivElement>(null);
  // The free box (portion J2): what the person told, Leda's answer, and the fields it filled,
  // marked until the person changes them. `latest` is the draft as it is now, so a proposal that
  // arrives while the person types never overwrites what was typed in the meantime.
  const [story, setStory] = useState('');
  const [help, setHelp] = useState<HelpState>({ kind: 'idle' });
  const [proposed, setProposed] = useState<ReadonlySet<Field>>(new Set());
  // What Leda could not complete, each one shown on its field in the falta color (J2-13: in the
  // phone retest "No encontré a … en el equipo" was only a gray line in the box, out of sight),
  // until the person fills that field or asks again. The box's summary reads these same notes,
  // with the ones that belong to no field.
  const [notes, setNotes] = useState<Problem[]>([]);
  const latest = useRef(draft);
  latest.current = draft;
  const latestStory = useRef(story);
  latestStory.current = story;

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
  const objective = options.objetivos.find((o) => o.id === draft.objetivo_id);
  const waitable = waitableTasks(options);

  function change(patch: Partial<Draft>) {
    setDraft((current) => ({ ...current, ...patch }));
    // What the person changes is hers: the mark goes.
    const changed = Object.keys(patch) as Field[];
    setProposed((marked) =>
      changed.some((f) => marked.has(f)) ? new Set([...marked].filter((f) => !changed.includes(f))) : marked,
    );
    // Other data, another attempt: a new key, so it never collides with the one already sent.
    // Not while the last send's outcome is unknown: that one may have loaded the task.
    if (!unknown.current) key.current = null;
    setStep((current) => (current.kind === 'edit' && current.failed ? { ...current, failed: false } : current));
    const touched = new Set(Object.keys(patch));
    setProblems((current) => current.filter((p) => !touched.has(PROBLEM_FIELD[p.campo] ?? '')));
    setNotes((current) => current.filter((n) => !touched.has(PROBLEM_FIELD[n.campo] ?? '')));
  }

  /** Takes the criterion Leda proposed with a refusal: it fills the field (the notice goes, as
   * with any change) and stays marked as hers until the person edits it. */
  function takeCriterion(text: string) {
    change({ criterio: text });
    setProposed((marked) => new Set([...marked, 'criterio']));
  }

  function chooseResponsible(id: string) {
    const next = memberOf(options, id);
    change({ responsable_id: id, evidencia: [...(policyOf(options, next)?.evidencia_requerida ?? [])] });
  }

  /** Fills only what is still empty with what Leda proposed (only what the options offer), and
   * marks it. Choosing the responsible person ticks the evidence her area asks for, as by hand.
   * Returns how many fields it filled. */
  function apply(proposal: Proposal): number {
    const current = latest.current;
    const valid = validProposal(proposal, options);
    const filled = (Object.keys(valid) as (keyof Proposal)[]).filter((field) => !current[field].trim());
    if (filled.length === 0) return 0;
    const next: Draft = { ...current };
    for (const field of filled) next[field] = valid[field] as string;
    if (filled.includes('responsable_id') && current.evidencia.length === 0) {
      next.evidencia = [...(policyOf(options, memberOf(options, next.responsable_id))?.evidencia_requerida ?? [])];
    }
    latest.current = next;
    setDraft(next);
    // Other data, another attempt (as in `change`).
    if (!unknown.current) key.current = null;
    setProposed((marked) => new Set([...marked, ...filled]));
    setProblems((shown) => shown.filter((p) => !(filled as string[]).includes(PROBLEM_FIELD[p.campo] ?? '')));
    setNotes((shown) => shown.filter((n) => !(filled as string[]).includes(PROBLEM_FIELD[n.campo] ?? '')));
    return filled.length;
  }

  async function ask() {
    if (help.kind === 'asking') return;
    const texto = story.trim();
    if (!texto) {
      setHelp({ kind: 'rejected', errors: [{ campo: 'texto', motivo: 'falta', texto: STORY_MISSING }] });
      return;
    }
    setHelp({ kind: 'asking' });
    setNotes([]);
    const { objetivo_id, titulo, descripcion, responsable_id, fecha, espera_id, criterio } = latest.current;
    const asked = { objetivo_id, titulo, descripcion, responsable_id, fecha, espera_id, criterio };
    try {
      const result = await askLeda(spaceId, { texto, ...asked });
      // The answer is for what the form had when she asked. If she changed the free text or a
      // field meanwhile, it may no longer fit (another person, another wait, other words): it
      // fills nothing, and the box says so quietly (review review-03b5c3a74d3719b7).
      const now = latest.current;
      const changed =
        latestStory.current.trim() !== texto ||
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
      else setHelp({ kind: 'failed', text: HELP_FAILED });
    }
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
  }

  async function confirm() {
    if (step.kind !== 'edit' || step.sending) return;
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
    key.current ??= newKey();
    const sent = draft;
    setStep({ kind: 'edit', sending: true, failed: false });
    try {
      const result = await loadTask(spaceId, toInput(sent, key.current));
      if (result.kind === 'loaded') {
        key.current = null;
        unknown.current = false;
        visited.current = null;
        setProblems([]);
        setStep({ kind: 'done', warnings: result.warnings, repeated: result.repeated, sent });
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
    key.current = null;
    visited.current = null;
    setStory('');
    setHelp({ kind: 'idle' });
    setNotes([]);
    setProposed(new Set());
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
        {step.warnings.length > 0 && (
          <ul className="m-0 flex list-none flex-col gap-1 p-0 text-body text-ink-soft">
            {step.warnings.map((w) => (
              <li key={`${w.campo}-${w.motivo}`} className="flex min-w-0 items-start gap-1.5">
                <Mark />
                <span className="min-w-0">{w.texto}</span>
              </li>
            ))}
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

  const { sending, failed } = step;
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
  const described = (id: string, field: Field) => (said(field).length ? `${id}-error` : undefined);

  return (
    <div className="grid w-full min-w-0 max-w-full grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-10">
      <form
        noValidate
        onSubmit={(event) => event.preventDefault()}
        aria-label="Cargar tarea"
        className="flex min-w-0 max-w-full flex-col"
      >
        <fieldset disabled={sending} className="m-0 flex min-w-0 flex-col gap-4 border-0 p-0">
          <HelpBox story={story} onStory={setStory} help={help} notes={notes} onAsk={ask} onChoose={choose} />

          <FieldBlock id="f-objetivo" label="Objetivo" errors={said('objetivo_id')} proposed={proposed.has('objetivo_id')}
            hint={options.objetivos.length === 0 ? 'No hay objetivos abiertos en este espacio.' : undefined}>
            <Select
              id="f-objetivo"
              value={draft.objetivo_id}
              onChange={(e) => change({ objetivo_id: e.target.value })}
              aria-invalid={invalid('objetivo_id')}
              aria-describedby={described('f-objetivo', 'objetivo_id')}
            >
              <option value="">elegí un objetivo</option>
              {options.objetivos.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.titulo}
                  {o.fecha_objetivo ? ` · hasta ${shortDate(o.fecha_objetivo)}` : ''}
                </option>
              ))}
            </Select>
          </FieldBlock>

          <FieldBlock id="f-titulo" label="Título" errors={said('titulo')} proposed={proposed.has('titulo')}
            extra={<Counter value={draft.titulo} limit={LIMITS.titulo} />}>
            <input
              id="f-titulo"
              className={INPUT}
              value={draft.titulo}
              onChange={(e) => change({ titulo: e.target.value })}
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
            <Select
              id="f-responsable"
              value={draft.responsable_id}
              onChange={(e) => chooseResponsible(e.target.value)}
              aria-invalid={invalid('responsable_id')}
              aria-describedby={described('f-responsable', 'responsable_id')}
            >
              <option value="">elegí a una persona</option>
              {options.integrantes.map((m) => (
                <option key={m.membership_id} value={m.membership_id}>
                  {m.nombre} · {m.area}
                  {m.conectado ? '' : ' · sin conectar'}
                </option>
              ))}
            </Select>
          </FieldBlock>

          <FieldBlock
            id="f-fecha"
            label="Fecha"
            errors={said('fecha')}
            proposed={proposed.has('fecha')}
            extra={draft.fecha ? <span className={`shrink-0 ${FIELD_VALUE}`}>{dayLabel(draft.fecha)}</span> : undefined}
            hint={
              objective?.fecha_objetivo && draft.fecha > objective.fecha_objetivo
                ? `Es posterior a la del objetivo (${shortDate(objective.fecha_objetivo)}): se avisa, no se bloquea.`
                : 'Sólo los días hábiles del espacio, desde hoy.'
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
            <Select
              id="f-espera"
              value={draft.espera_id}
              onChange={(e) => change({ espera_id: e.target.value })}
              aria-invalid={invalid('espera_id')}
              aria-describedby={described('f-espera', 'espera_id')}
            >
              <option value="">no espera a ninguna</option>
              {waitable.map((t) => (
                <option key={t.id} value={t.id}>
                  {waitLabel(t)}
                </option>
              ))}
            </Select>
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
              <label key={kind} className={`flex min-w-0 items-center gap-2 ${FIELD_VALUE}`}>
                <input
                  type="checkbox"
                  className="h-4 w-4 shrink-0 accent-ink"
                  checked={draft.evidencia.includes(kind)}
                  onChange={(e) => toggleEvidence(kind, e.target.checked)}
                />
                <span className="min-w-0 wrap-break-word">
                  {evidenceWords(policy, kind)}
                  {policy?.evidencia_requerida.includes(kind) && (
                    <span className="text-ink-dim"> · la pide el área</span>
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
            <Select
              id="f-decidio"
              value={draft.decidio_id}
              onChange={(e) => change({ decidio_id: e.target.value })}
              aria-invalid={invalid('decidio_id')}
              aria-describedby={described('f-decidio', 'decidio_id')}
            >
              <option value="">elegí a una persona</option>
              {options.integrantes.map((m) => (
                <option key={m.membership_id} value={m.membership_id}>
                  {m.nombre} · {m.area}
                </option>
              ))}
            </Select>
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
        <TaskPreview draft={draft} options={options} admin={admin} />
        <div ref={messages} tabIndex={-1} className="flex min-w-0 flex-col gap-3 pt-1.5 outline-none">
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
              <FieldList label="Falta completar" fields={missing} />
              <FieldList label="Hay que corregir" fields={wrong} />
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
            >
              {sending ? 'cargando…' : failed ? '> probar de nuevo' : '> confirmar'}
            </button>
          </div>
        </div>
      </aside>
    </div>
  );
}
