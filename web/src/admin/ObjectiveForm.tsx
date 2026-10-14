import { useEffect, useRef, useState } from 'react';
import { SessionClosedError } from '../api';
import { shortDate } from '../format';
import { HELP_FAILED, type Problem, SPELLING_FAILED, type Spelling } from './api';
import { Completing } from './Completing';
import { INPUT, PRIMARY, SECONDARY, WARN } from './controls';
import { Counter } from './Counter';
import { DatePicker, dayLabel } from './DatePicker';
import { Dropdown } from './Dropdown';
import { FieldBlock, Mark } from './FieldBlock';
import { bringTo, FieldList, focusField } from './FieldList';
import { newKey } from './draft';
import { type HelpFields, HelpBox, type HelpState, STORY_MISSING } from './HelpBox';
import type { ObjectiveApi, ObjectiveOptions, ObjectiveProposal, ObjectiveType, ParentObjective } from './objectiveApi';
import {
  apartFrom,
  checkObjective,
  defaultType,
  dueAfterParentText,
  emptyObjective,
  type ObjectiveDraft,
  LATE_FOR_PARENT,
  lateForParent,
  type ObjectiveField,
  OBJECTIVE_FIELD_ID,
  OBJECTIVE_FIELD_NAME,
  OBJECTIVE_FIELD_ORDER,
  OBJECTIVE_LIMITS,
  OBJECTIVE_PROBLEM_FIELD,
  parentLabel,
  parentOf,
  referentOf,
  toObjectiveInput,
  typesFor,
} from './objectiveDraft';
import { ObjectivePreview } from './ObjectivePreview';
import { FIELD_TITLE, FIELD_VALUE } from './typography';

type Step =
  | { kind: 'edit'; sending: boolean; failed: boolean }
  | { kind: 'done'; repeated: boolean; sent: ObjectiveDraft; notice: string | null };

/** The texts whose spelling Leda corrects (J3-4, as the task's: J2-23 and J2-24). */
type SpellField = 'titulo' | 'descripcion';
const SPELL_FIELDS: SpellField[] = ['titulo', 'descripcion'];

/** The objective form's fields, for the help box's notes. */
const HELP_FIELDS: HelpFields = {
  order: OBJECTIVE_FIELD_ORDER,
  problemField: OBJECTIVE_PROBLEM_FIELD,
  name: OBJECTIVE_FIELD_NAME,
};

/** The local problems first, then the ones already shown that the local check does not repeat
 * (what the server said). */
function merge(found: Problem[], shown: Problem[]): Problem[] {
  return [...found, ...shown.filter((p) => !found.some((f) => f.campo === p.campo && f.motivo === p.motivo))];
}

/** The fields with a problem, in the order of the form. */
function fieldsWith(problems: Problem[]): ObjectiveField[] {
  return OBJECTIVE_FIELD_ORDER.filter((field) => problems.some((p) => OBJECTIVE_PROBLEM_FIELD[p.campo] === field));
}

function named(fields: ObjectiveField[]) {
  return fields.map((field) => ({ key: field, name: OBJECTIVE_FIELD_NAME[field], elementId: OBJECTIVE_FIELD_ID[field] }));
}

/** Whether the server looked the key up before answering: not with a malformed value, nor without
 * a session or the authority to create (it refuses those before). Only then a refusal says that
 * nothing was created with that key. */
function lookedUpTheKey(problem: Problem): boolean {
  return !problem.motivo.startsWith('mal_formad') && problem.campo !== 'sesion';
}

interface ObjectiveFormProps {
  /** The door it creates through (the administration's or the team's). */
  api: ObjectiveApi;
  options: ObjectiveOptions;
  /** Who creates it, as the preview says it. */
  author: string;
  onClosed: () => void;
  /** One column also on a wide screen: the team's page is narrow. */
  stacked?: boolean;
  /** "> crear otro" with the options read again (the one just created can be a parent); without
   * it, the same options. */
  onAnother?: () => void;
}

/** The form that creates an objective (ADR 0023, decisions 1 and 5 and point 11): its name, what it
 * hangs from, its type (only the ones that fit there, with the pack's names), its referente (an
 * area referente), its date (the space's working days) and, if wanted, a description. It shows the
 * objective live as it will be created ("Vista previa") with "confirmar" right below, and creates it
 * only when confirmed. While it sends, the form is locked, so what is shown is what goes. One
 * idempotency key per attempt: kept across retries of the same data and while an outcome is
 * unknown, renewed after a success or when the data changes, so a double send never creates two.
 * Leda's help (J3-4), when the door has it (`api.assist`): the box "Contame qué querés hacer y te
 * ayudo" goes first in the form, as in the task's (J2), and Leda fills only what is still empty and
 * never what the person wrote or chose herself, marked until the person changes it; an answer for a
 * form that changed, was cleared or is being sent fills nothing. The spelling of the name and the
 * description is corrected when the person leaves them and before creating, unmarked. */
export function ObjectiveForm({ api, options, author, onClosed, stacked = false, onAnother }: ObjectiveFormProps) {
  const [draft, setDraft] = useState<ObjectiveDraft>(() => emptyObjective(options));
  const [step, setStep] = useState<Step>({ kind: 'edit', sending: false, failed: false });
  const [problems, setProblems] = useState<Problem[]>([]);
  const [focusAsked, setFocusAsked] = useState<{ field: ObjectiveField | null; n: number } | null>(null);
  const [clearing, setClearing] = useState(false);
  const visited = useRef<ObjectiveField | null>(null);
  const key = useRef<string | null>(null);
  // The last send got no definite answer: it may have created the objective. Until something
  // settles it, the key stays even if the data changes, so the server can tell.
  const unknown = useRef(false);
  const sendingRef = useRef(false);
  // Each start over is a new round: an answer that arrives for an older one changes nothing.
  const round = useRef(0);
  const heading = useRef<HTMLHeadingElement>(null);
  const messages = useRef<HTMLDivElement>(null);
  // Leda's help (J3-4): what the person told, Leda's answer, the fields she filled (marked until the
  // person changes them) and what she could not complete, on its field. `latest` is the draft as it
  // is now, so an answer that arrives while the person types never overwrites what she typed.
  const assist = api.assist;
  const [story, setStory] = useState('');
  const [help, setHelp] = useState<HelpState>({ kind: 'idle' });
  const [proposed, setProposed] = useState<ReadonlySet<ObjectiveField>>(new Set());
  const [notes, setNotes] = useState<Problem[]>([]);
  const latest = useRef(draft);
  latest.current = draft;
  const latestStory = useRef(story);
  latestStory.current = story;
  // What the person chose herself in a list (what it hangs from, also "de ninguno", and the type):
  // Leda never changes it.
  const chosen = useRef<Set<ObjectiveField>>(new Set());
  // The spelling: each text as Leda last checked or corrected it (it is not checked again), and
  // what to say when it could not check.
  const checked = useRef<Partial<Record<SpellField, string>>>({});
  const [spellNote, setSpellNote] = useState<string | null>(null);

  useEffect(() => {
    if (step.kind === 'done') heading.current?.focus();
  }, [step.kind]);

  useEffect(() => {
    if (!focusAsked) return;
    if (focusAsked.field) focusField(OBJECTIVE_FIELD_ID[focusAsked.field]);
    else if (messages.current) bringTo(messages.current, messages.current);
  }, [focusAsked]);

  function takeTo(field: ObjectiveField | null) {
    visited.current = field;
    setFocusAsked((current) => ({ field, n: (current?.n ?? 0) + 1 }));
  }

  /** Whether a problem or a note stops holding once these fields changed: its own field, and a
   * date that fell after the parent also when it hangs from another one. */
  function clearedBy(problem: Problem, touched: ReadonlySet<string>): boolean {
    return (
      touched.has(OBJECTIVE_PROBLEM_FIELD[problem.campo] ?? '') ||
      (problem.motivo === LATE_FOR_PARENT && touched.has('padre_id'))
    );
  }

  function change(patch: Partial<ObjectiveDraft>) {
    setDraft((current) => ({ ...current, ...patch }));
    latest.current = { ...latest.current, ...patch };
    // Other data, another attempt: a new key. Not while the last send's outcome is unknown.
    if (!unknown.current) key.current = null;
    setStep((current) => (current.kind === 'edit' && current.failed ? { ...current, failed: false } : current));
    const touched = new Set<string>(Object.keys(patch));
    // What the person changes is hers: Leda's mark goes, and so does what Leda could not complete.
    setProposed((marked) =>
      [...touched].some((f) => marked.has(f as ObjectiveField))
        ? new Set([...marked].filter((f) => !touched.has(f)))
        : marked,
    );
    // An edited text is checked again on confirm, so the notice that it could not be goes.
    if (SPELL_FIELDS.some((f) => touched.has(f))) setSpellNote(null);
    setProblems((current) => current.filter((p) => !clearedBy(p, touched)));
    setNotes((current) => current.filter((n) => !clearedBy(n, touched)));
  }

  /** What it hangs from decides the type (point 11): the only one when there is one, and the
   * operational one when it can also be a milestone. The person's choice: Leda never changes it,
   * and a type she chose for the old place no longer stands. */
  function chooseParent(id: string) {
    chosen.current.add('padre_id');
    chosen.current.delete('tipo');
    change({ padre_id: id, tipo: defaultType(typesFor(options, id)) });
  }

  function chooseType(tipo: ObjectiveDraft['tipo']) {
    chosen.current.add('tipo');
    change({ tipo });
  }

  /** Fills only what is still empty (and what the person did not choose herself) with what Leda
   * proposed, only what the options offer, and marks it. The type follows where it hangs: the one
   * Leda proposed if it fits there, or the one the form preselects when Leda chose the parent.
   * Returns how many fields it filled. */
  function apply(proposal: ObjectiveProposal): number {
    const current = latest.current;
    const next: ObjectiveDraft = { ...current };
    const filled: ObjectiveField[] = [];
    const take = <F extends ObjectiveField>(field: F, value: ObjectiveDraft[F]) => {
      next[field] = value;
      filled.push(field);
    };
    for (const field of SPELL_FIELDS) {
      const value = proposal[field];
      if (typeof value === 'string' && value.trim() && !current[field].trim()) take(field, value);
    }
    if (proposal.padre_id && parentOf(options, proposal.padre_id) && !current.padre_id && !chosen.current.has('padre_id')) {
      take('padre_id', proposal.padre_id);
    }
    const types = typesFor(options, next.padre_id);
    if (!(chosen.current.has('tipo') && types.includes(current.tipo as ObjectiveType))) {
      const offered = types.find((t) => t === proposal.tipo);
      const tipo = offered ?? (filled.includes('padre_id') ? defaultType(types) : '');
      if (tipo && tipo !== current.tipo) take('tipo', tipo);
    }
    if (proposal.referente_id && referentOf(options, proposal.referente_id) && !current.referente_id) {
      take('referente_id', proposal.referente_id);
    }
    if (proposal.fecha && options.calendario.dias_habiles.includes(proposal.fecha) && !current.fecha) {
      take('fecha', proposal.fecha);
    }
    if (filled.length === 0) return 0;
    latest.current = next;
    setDraft(next);
    // Other data, another attempt (as in `change`).
    if (!unknown.current) key.current = null;
    setProposed((marked) => new Set([...marked, ...filled]));
    const touched = new Set<string>(filled);
    setProblems((shown) => shown.filter((p) => !clearedBy(p, touched)));
    return filled.length;
  }

  async function ask() {
    if (!assist || help.kind === 'asking') return;
    const asking = round.current;
    const texto = story.trim();
    if (!texto) {
      setHelp({ kind: 'rejected', errors: [{ campo: 'texto', motivo: 'falta', texto: STORY_MISSING }] });
      return;
    }
    setHelp({ kind: 'asking' });
    setNotes([]);
    const before = latest.current;
    try {
      const result = await assist.help({
        texto,
        titulo: before.titulo,
        descripcion: before.descripcion,
        padre_id: before.padre_id,
        // The type only when the person chose it: otherwise Leda proposes the one that fits.
        tipo: chosen.current.has('tipo') ? before.tipo : '',
        referente_id: before.referente_id,
        fecha: before.fecha,
      });
      // The person started over meanwhile: the answer is for a form that is gone.
      if (round.current !== asking) return;
      // It is sending: what goes is what the form shows; nothing fills.
      if (sendingRef.current) {
        setHelp({ kind: 'stale' });
        return;
      }
      // The answer is for what the form had when she asked: if she changed the free text or a
      // field meanwhile, it fills nothing, and the box says so quietly.
      const now = latest.current;
      const changed =
        latestStory.current.trim() !== texto || OBJECTIVE_FIELD_ORDER.some((field) => now[field] !== before[field]);
      if (changed && result.kind !== 'failed') {
        setHelp({ kind: 'stale' });
      } else if (result.kind === 'proposed') {
        const filled = apply(result.proposal);
        // Only on the fields still empty; a note that belongs to no field stays for the box.
        setNotes(
          result.notes.filter((n) => {
            const field = OBJECTIVE_PROBLEM_FIELD[n.campo];
            return field === undefined || !String(latest.current[field] ?? '').trim();
          }),
        );
        const choices = latest.current.referente_id ? [] : result.choices.filter((c) => referentOf(options, c.membership_id));
        setHelp({ kind: 'done', choices, nothing: filled === 0 && result.notes.length === 0 && choices.length === 0 });
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

  /** The person picked the referente among the ones that fit the name: her choice, not marked. */
  function choose(id: string) {
    if (referentOf(options, id)) change({ referente_id: id });
    setHelp((current) => (current.kind === 'done' ? { ...current, choices: [] } : current));
  }

  /** The person left a text: Leda corrects its spelling, unmarked, if it is still the same text and
   * the person is not back in it (then, the next time she leaves it). It never blocks: without an
   * answer, the text stays as written and confirm tries again. */
  async function checkOnLeave(field: SpellField) {
    if (!assist) return;
    const text = latest.current[field];
    if (!text.trim() || checked.current[field] === text || sendingRef.current) return;
    const started = round.current;
    let spelling: Spelling;
    try {
      spelling = await assist.spell({ [field]: text });
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      return;
    }
    if (sendingRef.current || round.current !== started || latest.current[field] !== text) return;
    if (spelling.unchecked.includes(field)) return;
    const to = spelling.corrected[field]?.text;
    if (to === undefined || to === text) {
      checked.current[field] = text;
      return;
    }
    if (document.activeElement?.id === OBJECTIVE_FIELD_ID[field]) return;
    checked.current[field] = to;
    const next = { ...latest.current, [field]: to };
    latest.current = next;
    setDraft(next);
    if (!unknown.current) key.current = null;
  }

  /** "> cargarlo aparte" (decision 5): it is not really part of its parent, so it goes next to it,
   * and the type is offered again for the new place, with the same preselection. */
  function apart(parent: ParentObjective) {
    chooseParent(apartFrom(options, parent));
  }

  async function confirm() {
    if (step.kind !== 'edit' || step.sending || sendingRef.current) return;
    const found = checkObjective(draft, options);
    if (found.length > 0) {
      const shown = merge(found, problems);
      setProblems(shown);
      const fields = fieldsWith(shown);
      const after = visited.current ? OBJECTIVE_FIELD_ORDER.indexOf(visited.current) : -1;
      takeTo(fields.find((field) => OBJECTIVE_FIELD_ORDER.indexOf(field) > after) ?? fields[0] ?? null);
      return;
    }
    const started = round.current;
    let sent = draft;
    let notice = spellNote;
    sendingRef.current = true;
    setStep({ kind: 'edit', sending: true, failed: false });
    try {
      // J3-4, as the task's (J2-23): before creating, Leda corrects the spelling of the texts not
      // checked yet as they are, and what is created is the corrected text, unmarked. If it could
      // not check, nothing blocks: it is created as written, with the notice.
      const asked = assist ? SPELL_FIELDS.filter((f) => sent[f].trim() && checked.current[f] !== sent[f]) : [];
      if (assist && asked.length > 0) {
        let spelling: Spelling;
        try {
          spelling = await assist.spell(Object.fromEntries(asked.map((f) => [f, sent[f]])));
        } catch (error) {
          if (error instanceof SessionClosedError) throw error;
          spelling = { corrected: {}, unchecked: asked, notice: SPELLING_FAILED };
        }
        if (round.current !== started) return;
        const next: ObjectiveDraft = { ...sent };
        for (const field of asked) {
          const fix = spelling.corrected[field];
          if (fix && fix.text !== sent[field]) next[field] = fix.text;
          // Only what was really checked counts as checked.
          if (!spelling.unchecked.includes(field)) checked.current[field] = next[field];
        }
        notice = spelling.unchecked.length > 0 ? (spelling.notice ?? SPELLING_FAILED) : null;
        setSpellNote(notice);
        if (asked.some((f) => next[f] !== sent[f])) {
          // The form shows what goes, so a retry sends the same data with the same key.
          latest.current = next;
          setDraft(next);
          if (!unknown.current) key.current = null;
        }
        sent = next;
      }
      key.current ??= newKey();
      const result = await api.create(toObjectiveInput(sent, key.current));
      if (round.current !== started) return;
      if (result.kind === 'created') {
        key.current = null;
        unknown.current = false;
        visited.current = null;
        setProblems([]);
        setStep({ kind: 'done', repeated: result.repeated, sent, notice });
      } else {
        // A refusal creates nothing, and the server looked the key up first: nothing was created
        // with it, unless the key was used with other data or the server never looked it up.
        if (!result.errors.some((e) => e.campo === 'clave' || !lookedUpTheKey(e))) unknown.current = false;
        setProblems(result.errors);
        setStep({ kind: 'edit', sending: false, failed: false });
        takeTo(fieldsWith(result.errors)[0] ?? null);
      }
    } catch (error) {
      if (error instanceof SessionClosedError) {
        onClosed();
      } else if (round.current === started) {
        unknown.current = true;
        setStep({ kind: 'edit', sending: false, failed: true });
      }
    } finally {
      sendingRef.current = false;
    }
  }

  /** After a key conflict: the person checked and starts a new attempt. */
  function newAttempt() {
    key.current = null;
    unknown.current = false;
    setProblems((current) => current.filter((p) => p.campo !== 'clave'));
  }

  function another() {
    // A new round also remounts the help box (`key`): a dictation in progress is cancelled.
    round.current += 1;
    key.current = null;
    unknown.current = false;
    visited.current = null;
    setClearing(false);
    setStory('');
    setHelp({ kind: 'idle' });
    setNotes([]);
    setProposed(new Set());
    chosen.current = new Set();
    checked.current = {};
    setSpellNote(null);
    latest.current = emptyObjective(options);
    setDraft(emptyObjective(options));
    setProblems([]);
    setStep({ kind: 'edit', sending: false, failed: false });
  }

  if (step.kind === 'done') {
    return (
      <section aria-labelledby="objetivo-creado" className="flex w-full min-w-0 max-w-[40rem] flex-col gap-3.5">
        <h2 id="objetivo-creado" ref={heading} tabIndex={-1} className="m-0 text-button font-bold outline-none">
          {step.repeated ? 'Este objetivo ya estaba creado.' : 'Objetivo creado.'}
        </h2>
        <ObjectivePreview draft={step.sent} options={options} author={author} />
        {step.notice && <p className="m-0 text-body text-ink-soft">{step.notice}</p>}
        <div>
          <button type="button" className={PRIMARY} onClick={onAnother ?? another}>
            &gt; crear otro
          </button>
        </div>
      </section>
    );
  }

  const { sending, failed } = step;
  const on = (field: ObjectiveField) => problems.filter((p) => OBJECTIVE_PROBLEM_FIELD[p.campo] === field);
  // On a field: its problems and what Leda could not complete there (never the same one twice).
  const said = (field: ObjectiveField) => [
    ...on(field),
    ...notes.filter(
      (n) =>
        OBJECTIVE_PROBLEM_FIELD[n.campo] === field && !on(field).some((p) => p.campo === n.campo && p.motivo === n.motivo),
    ),
  ];
  const invalid = (field: ObjectiveField) => (on(field).length ? true : undefined);
  const described = (field: ObjectiveField) => (said(field).length ? `${OBJECTIVE_FIELD_ID[field]}-error` : undefined);
  const conflict = problems.some((p) => p.campo === 'clave' && p.motivo === 'usada_con_otros_datos');
  const general = problems.filter(
    (p) => !(p.campo in OBJECTIVE_PROBLEM_FIELD) && !(p.campo === 'clave' && p.motivo === 'usada_con_otros_datos'),
  );
  // What blocks confirm right now, said from the start; the fields themselves are marked only after
  // a tap on confirm (or the server's answer).
  const pending = checkObjective(draft, options);
  const blocked = pending.length > 0;
  const listed = merge(pending, problems);
  const missing = fieldsWith(listed.filter((p) => p.motivo === 'falta'));
  const wrong = fieldsWith(listed).filter((field) => !missing.includes(field));
  const summary = missing.length > 0 || wrong.length > 0 || general.length > 0;
  const alerted = problems.length > 0;
  const types = typesFor(options, draft.padre_id);
  const parent = parentOf(options, draft.padre_id);
  // Decision 5 (2026-10-14): it falls due after the one it hangs from. Leda stops and offers the
  // ways out: another date up to that day, or "cargarlo aparte".
  const late = lateForParent(draft, options);
  const levels = options.niveles;
  const blank = emptyObjective(options);
  const somethingToClear =
    story.trim() !== '' || (Object.keys(blank) as ObjectiveField[]).some((f) => draft[f] !== blank[f]);
  // Named by the parent's own name, so the pack's level names need no article.
  const typeHint = !parent
    ? `Sin un objetivo arriba, es ${levels.estrategico}.`
    : types.length > 1
      ? `Debajo de «${parent.titulo}» puede ser ${types.map((t) => levels[t]).reduce((a, b) => `${a} ${/^h?o/i.test(b) ? 'u' : 'o'} ${b}`)}.`
      : `Debajo de «${parent.titulo}» es ${types[0] ? levels[types[0]] : levels.operativo}.`;

  return (
    <div
      className={`grid w-full min-w-0 max-w-full grid-cols-1 gap-8 ${stacked ? '' : 'lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-10'}`}
    >
      <form
        noValidate
        onSubmit={(event) => event.preventDefault()}
        aria-label="Crear objetivo"
        className="flex min-w-0 max-w-full flex-col"
      >
        <fieldset disabled={sending} className="m-0 flex min-w-0 flex-col gap-4 border-0 p-0">
          {assist && (
            <HelpBox
              key={round.current}
              transcribe={assist.transcribe}
              onClosed={onClosed}
              story={story}
              onStory={setStory}
              help={help}
              notes={notes}
              onAsk={ask}
              onChoose={choose}
              fields={HELP_FIELDS}
              chooseLabel="elegí el referente"
            />
          )}
          <FieldBlock id="o-titulo" label="Nombre" errors={said('titulo')} proposed={proposed.has('titulo')}
            extra={<Counter value={draft.titulo} limit={OBJECTIVE_LIMITS.titulo} />}>
            <input
              id="o-titulo"
              className={INPUT}
              value={draft.titulo}
              onChange={(e) => change({ titulo: e.target.value })}
              onBlur={() => void checkOnLeave('titulo')}
              aria-invalid={invalid('titulo')}
              aria-describedby={described('titulo')}
              autoComplete="off"
            />
          </FieldBlock>

          <FieldBlock id="o-padre" label="De qué cuelga" errors={said('padre_id')} proposed={proposed.has('padre_id')}
            hint={options.padres.length === 0 ? 'Todavía no hay objetivos abiertos de los que pueda colgar.' : undefined}>
            <Dropdown
              id="o-padre"
              labelledBy="o-padre-label"
              value={draft.padre_id}
              onChange={chooseParent}
              invalid={invalid('padre_id')}
              describedBy={described('padre_id')}
              options={[
                { value: '', label: 'de ninguno' },
                ...options.padres.map((p) => ({
                  value: p.id,
                  label: parentLabel(p, levels, p.fecha_objetivo ? shortDate(p.fecha_objetivo) : undefined),
                })),
              ]}
            />
          </FieldBlock>

          <FieldBlock id="o-tipo" label="Tipo" errors={said('tipo')} hint={typeHint} proposed={proposed.has('tipo')}>
            {types.length > 1 ? (
              <Dropdown
                id="o-tipo"
                labelledBy="o-tipo-label"
                value={draft.tipo}
                onChange={(value) => chooseType(value as ObjectiveDraft['tipo'])}
                invalid={invalid('tipo')}
                describedBy={described('tipo')}
                options={types.map((t) => ({ value: t, label: levels[t] }))}
              />
            ) : (
              // One type fits there: it is not asked, only said.
              <p id="o-tipo" tabIndex={-1} aria-labelledby="o-tipo-label" className={`m-0 outline-none ${FIELD_VALUE}`}>
                {types[0] ? levels[types[0]] : '—'}
              </p>
            )}
          </FieldBlock>

          <FieldBlock id="o-referente" label="Referente" errors={said('referente_id')} proposed={proposed.has('referente_id')}
            hint={options.referentes.length === 0 ? 'No hay referentes de área en este espacio.' : 'El referente de un área del equipo.'}>
            <Dropdown
              id="o-referente"
              labelledBy="o-referente-label"
              value={draft.referente_id}
              onChange={(value) => change({ referente_id: value })}
              invalid={invalid('referente_id')}
              describedBy={described('referente_id')}
              options={[
                { value: '', label: 'elegí a una persona' },
                ...options.referentes.map((r) => ({ value: r.membership_id, label: `${r.nombre} · ${r.areas.join(', ')}` })),
              ]}
            />
          </FieldBlock>

          <FieldBlock
            id="o-fecha"
            label="Fecha"
            errors={said('fecha')}
            proposed={proposed.has('fecha')}
            extra={draft.fecha ? <span className={`shrink-0 ${FIELD_VALUE}`}>{dayLabel(draft.fecha)}</span> : undefined}
            hint="Sólo los días hábiles del espacio, desde hoy."
          >
            <DatePicker
              id="o-fecha"
              days={options.calendario.dias_habiles}
              value={draft.fecha}
              onChange={(day) => change({ fecha: day })}
              labelledBy="o-fecha-label"
              describedBy={described('fecha')}
              invalid={on('fecha').length > 0}
            />
          </FieldBlock>

          <FieldBlock id="o-descripcion" label="Descripción (opcional)" errors={said('descripcion')}
            proposed={proposed.has('descripcion')}
            extra={<Counter value={draft.descripcion} limit={OBJECTIVE_LIMITS.descripcion} />}>
            <textarea
              id="o-descripcion"
              className={`${INPUT} min-h-20 resize-y`}
              value={draft.descripcion}
              onChange={(e) => change({ descripcion: e.target.value })}
              onBlur={() => void checkOnLeave('descripcion')}
              aria-invalid={invalid('descripcion')}
              aria-describedby={described('descripcion')}
            />
          </FieldBlock>
        </fieldset>
      </form>

      <aside
        aria-labelledby="vista-previa-objetivo"
        className={`flex min-w-0 max-w-full flex-col gap-2 ${stacked ? '' : 'lg:sticky lg:top-4 lg:max-h-[calc(100dvh-2rem)] lg:self-start lg:overflow-y-auto'}`}
      >
        <h2 id="vista-previa-objetivo" className={`m-0 ${FIELD_TITLE}`}>
          Vista previa
        </h2>
        <ObjectivePreview draft={draft} options={options} author={author} />
        <div ref={messages} tabIndex={-1} className="flex min-w-0 flex-col gap-3 pt-1.5 outline-none">
          {late && (
            <div
              role="group"
              aria-label="Vence después que el objetivo del que cuelga"
              className="flex min-w-0 flex-col gap-2 rounded-card border-hard border-line px-3 py-2.5 text-body"
            >
              <p className={`m-0 font-bold ${WARN}`}>{dueAfterParentText(late)}</p>
              <p className="m-0 text-ink-soft">
                Elegí una fecha hasta ese día o, si no es parte de «{late.titulo}», cargalo aparte.
              </p>
              <div className="flex flex-wrap gap-3">
                <button type="button" className={`${SECONDARY} w-fit`} onClick={() => apart(late)} disabled={sending}>
                  &gt; cargarlo aparte
                </button>
              </div>
            </div>
          )}
          {spellNote && <p className="m-0 text-body text-ink-soft">{spellNote}</p>}
          {failed && (
            <p role="alert" className="m-0 text-body text-ink-soft">
              No se pudo crear: no llegó la respuesta. Los datos siguen acá; probá de nuevo.
            </p>
          )}
          {conflict && (
            <div role="alert" className="flex flex-col gap-2 rounded-card border-hard border-line px-3 py-2.5 text-body">
              <p className="m-0 font-bold">
                Puede que ya se haya creado: fijate en los objetivos antes de crearlo de nuevo.
              </p>
              <p className="m-0 text-ink-soft">El envío anterior no tuvo respuesta y esta vez cambiaron los datos.</p>
              <button type="button" className={`${SECONDARY} w-fit`} onClick={newAttempt}>
                no está creado: empezar de nuevo
              </button>
            </div>
          )}
          {summary && (
            <div
              key={alerted ? `alerta-${focusAsked?.n ?? 0}` : 'en-vivo'}
              id="lo-que-falta-objetivo"
              role={alerted ? 'alert' : undefined}
              className={`flex min-w-0 flex-col gap-1 wrap-break-word text-body ${WARN} ${alerted ? 'rounded-card border-hard border-line px-3 py-2.5' : ''}`}
            >
              {alerted && <p className="m-0 font-bold text-ink">No se creó: hay que corregir lo marcado.</p>}
              <FieldList label="Falta completar" fields={named(missing)} />
              <FieldList label="Hay que corregir" fields={named(wrong)} />
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
              aria-describedby={summary ? 'lo-que-falta-objetivo' : undefined}
              aria-label={sending ? 'cargando…' : undefined}
            >
              {sending ? <Completing word="cargando" /> : failed ? '> probar de nuevo' : '> confirmar'}
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
