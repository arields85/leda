import { useEffect, useRef, useState } from 'react';
import { SessionClosedError } from '../api';
import { shortDate } from '../format';
import type { Problem } from './api';
import { Completing } from './Completing';
import { INPUT, PRIMARY, SECONDARY, WARN } from './controls';
import { Counter } from './Counter';
import { DatePicker, dayLabel } from './DatePicker';
import { Dropdown } from './Dropdown';
import { FieldBlock, Mark } from './FieldBlock';
import { bringTo, FieldList, focusField } from './FieldList';
import { newKey } from './draft';
import type { ObjectiveApi, ObjectiveOptions, ParentObjective } from './objectiveApi';
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
  toObjectiveInput,
  typesFor,
} from './objectiveDraft';
import { ObjectivePreview } from './ObjectivePreview';
import { FIELD_TITLE, FIELD_VALUE } from './typography';

type Step = { kind: 'edit'; sending: boolean; failed: boolean } | { kind: 'done'; repeated: boolean; sent: ObjectiveDraft };

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
 * Leda's help box (J3-4) goes first in the form, above the fields. */
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

  function change(patch: Partial<ObjectiveDraft>) {
    setDraft((current) => ({ ...current, ...patch }));
    // Other data, another attempt: a new key. Not while the last send's outcome is unknown.
    if (!unknown.current) key.current = null;
    setStep((current) => (current.kind === 'edit' && current.failed ? { ...current, failed: false } : current));
    const touched = new Set<string>(Object.keys(patch));
    // A date that fell after the parent stops holding once it hangs from another one.
    setProblems((current) =>
      current.filter(
        (p) =>
          !touched.has(OBJECTIVE_PROBLEM_FIELD[p.campo] ?? '') &&
          !(p.motivo === LATE_FOR_PARENT && touched.has('padre_id')),
      ),
    );
  }

  /** What it hangs from decides the type (point 11): the only one when there is one, and the
   * operational one when it can also be a milestone. */
  function chooseParent(id: string) {
    change({ padre_id: id, tipo: defaultType(typesFor(options, id)) });
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
    const sent = draft;
    key.current ??= newKey();
    sendingRef.current = true;
    setStep({ kind: 'edit', sending: true, failed: false });
    try {
      const result = await api.create(toObjectiveInput(sent, key.current));
      if (round.current !== started) return;
      if (result.kind === 'created') {
        key.current = null;
        unknown.current = false;
        visited.current = null;
        setProblems([]);
        setStep({ kind: 'done', repeated: result.repeated, sent });
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
    round.current += 1;
    key.current = null;
    unknown.current = false;
    visited.current = null;
    setClearing(false);
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
  const invalid = (field: ObjectiveField) => (on(field).length ? true : undefined);
  const described = (field: ObjectiveField) => (on(field).length ? `${OBJECTIVE_FIELD_ID[field]}-error` : undefined);
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
  const somethingToClear = (Object.keys(blank) as ObjectiveField[]).some((f) => draft[f] !== blank[f]);
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
          {/* J3-4: Leda's help box ("Contame qué querés hacer y te ayudo") goes here, first. */}
          <FieldBlock id="o-titulo" label="Nombre" errors={on('titulo')}
            extra={<Counter value={draft.titulo} limit={OBJECTIVE_LIMITS.titulo} />}>
            <input
              id="o-titulo"
              className={INPUT}
              value={draft.titulo}
              onChange={(e) => change({ titulo: e.target.value })}
              aria-invalid={invalid('titulo')}
              aria-describedby={described('titulo')}
              autoComplete="off"
            />
          </FieldBlock>

          <FieldBlock id="o-padre" label="De qué cuelga" errors={on('padre_id')}
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

          <FieldBlock id="o-tipo" label="Tipo" errors={on('tipo')} hint={typeHint}>
            {types.length > 1 ? (
              <Dropdown
                id="o-tipo"
                labelledBy="o-tipo-label"
                value={draft.tipo}
                onChange={(value) => change({ tipo: value as ObjectiveDraft['tipo'] })}
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

          <FieldBlock id="o-referente" label="Referente" errors={on('referente_id')}
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
            errors={on('fecha')}
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

          <FieldBlock id="o-descripcion" label="Descripción (opcional)" errors={on('descripcion')}
            extra={<Counter value={draft.descripcion} limit={OBJECTIVE_LIMITS.descripcion} />}>
            <textarea
              id="o-descripcion"
              className={`${INPUT} min-h-20 resize-y`}
              value={draft.descripcion}
              onChange={(e) => change({ descripcion: e.target.value })}
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
