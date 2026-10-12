import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { SessionClosedError } from '../api';
import { shortDate } from '../format';
import { loadTask, type Options, type Problem } from './api';
import { DatePicker, dayLabel } from './DatePicker';
import {
  type Draft,
  EMPTY_DRAFT,
  evidenceKinds,
  evidenceWords,
  type Field,
  length,
  LIMITS,
  memberOf,
  newKey,
  policyOf,
  PROBLEM_FIELD,
} from './draft';
import { TaskPreview } from './TaskPreview';

type Step =
  | { kind: 'edit' }
  | { kind: 'review'; sending: boolean; failed: boolean }
  | { kind: 'done'; warnings: Problem[]; repeated: boolean };

const INPUT =
  'w-full min-w-0 rounded-card border-hard border-line bg-card px-3 py-2 text-body text-ink outline-none focus:border-ink aria-[invalid=true]:border-ink-soft';
const PRIMARY =
  'inline-flex h-11 items-center gap-2 rounded-card border-hard border-ink bg-card px-3.5 text-button font-bold text-ink shadow-hard-ink disabled:opacity-50';
const SECONDARY =
  'inline-flex h-11 items-center rounded-card border-hard border-line-soft bg-transparent px-3.5 text-button text-ink-soft disabled:opacity-50';

function FieldBlock({
  id,
  label,
  extra,
  errors,
  hint,
  children,
}: {
  id: string;
  label: string;
  extra?: ReactNode;
  errors: Problem[];
  hint?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="flex min-w-0 flex-col gap-1.5">
      <div className="flex items-baseline justify-between gap-2 text-meta text-ink-dim">
        <label id={`${id}-label`} htmlFor={id} className="uppercase tracking-[0.04em]">
          {label}
        </label>
        {extra}
      </div>
      {children}
      {hint && <div className="text-small text-ink-dim">{hint}</div>}
      {errors.length > 0 && (
        <ul id={`${id}-error`} className="m-0 flex list-none flex-col gap-0.5 p-0 text-small font-bold text-ink">
          {errors.map((e) => (
            <li key={`${e.campo}-${e.motivo}`}>! {e.texto}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Counter({ value, limit }: { value: string; limit: number }) {
  const n = length(value);
  const over = n > limit;
  return (
    <span aria-live="polite" className={over ? 'font-bold text-ink' : ''}>
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
 * the task as it will look, and saves it only after "revisar" and "confirmar" (decision 6). One
 * idempotency key per attempt: kept across retries of the same data, renewed after a success or
 * when the data changes, so a double send never loads two tasks. */
export function LoadForm({ spaceId, options, admin, onClosed }: LoadFormProps) {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [step, setStep] = useState<Step>({ kind: 'edit' });
  const [problems, setProblems] = useState<Problem[]>([]);
  const key = useRef<string | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (step.kind !== 'edit') heading.current?.focus();
  }, [step.kind]);

  const member = memberOf(options, draft.responsable_id);
  const policy = policyOf(options, member);
  const kinds = evidenceKinds(policy);
  const objective = options.objetivos.find((o) => o.id === draft.objetivo_id);

  function change(patch: Partial<Draft>) {
    setDraft((current) => ({ ...current, ...patch }));
    // Other data, another attempt: a new key, so it never collides with the one already sent.
    key.current = null;
    const touched = new Set(Object.keys(patch));
    setProblems((current) => current.filter((p) => !touched.has(PROBLEM_FIELD[p.campo] ?? '')));
  }

  function chooseResponsible(id: string) {
    const next = memberOf(options, id);
    change({ responsable_id: id, evidencia: [...(policyOf(options, next)?.evidencia_requerida ?? [])] });
  }

  function toggleEvidence(kind: string, on: boolean) {
    const chosen = new Set(draft.evidencia);
    if (on) chosen.add(kind);
    else chosen.delete(kind);
    change({ evidencia: kinds.filter((k) => chosen.has(k)) });
  }

  function review(event: FormEvent) {
    event.preventDefault();
    setStep({ kind: 'review', sending: false, failed: false });
  }

  async function confirm() {
    key.current ??= newKey();
    setStep({ kind: 'review', sending: true, failed: false });
    try {
      const result = await loadTask(spaceId, { ...draft, clave: key.current });
      if (result.kind === 'loaded') {
        key.current = null;
        setProblems([]);
        setStep({ kind: 'done', warnings: result.warnings, repeated: result.repeated });
      } else {
        setProblems(result.errors);
        setStep({ kind: 'edit' });
      }
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else setStep({ kind: 'review', sending: false, failed: true });
    }
  }

  function another() {
    key.current = null;
    setDraft(EMPTY_DRAFT);
    setProblems([]);
    setStep({ kind: 'edit' });
  }

  const preview = <TaskPreview draft={draft} options={options} admin={admin} />;

  if (step.kind === 'done') {
    return (
      <section aria-labelledby="cargada" className="flex w-full max-w-[40rem] flex-col gap-3.5">
        <h2 id="cargada" ref={heading} tabIndex={-1} className="m-0 text-button font-bold outline-none">
          {step.repeated ? 'Esta tarea ya estaba cargada.' : 'Tarea cargada.'}
        </h2>
        {step.warnings.length > 0 && (
          <ul className="m-0 flex list-none flex-col gap-1 p-0 text-body text-ink-soft">
            {step.warnings.map((w) => (
              <li key={`${w.campo}-${w.motivo}`}>! {w.texto}</li>
            ))}
          </ul>
        )}
        {preview}
        <div>
          <button type="button" className={PRIMARY} onClick={another}>
            &gt; cargar otra
          </button>
        </div>
      </section>
    );
  }

  if (step.kind === 'review') {
    return (
      <section aria-labelledby="revisar" className="flex w-full max-w-[40rem] flex-col gap-3.5">
        <h2 id="revisar" ref={heading} tabIndex={-1} className="m-0 text-button font-bold outline-none">
          Revisá la tarea antes de cargarla.
        </h2>
        {preview}
        {step.failed && (
          <p role="alert" className="m-0 text-body text-ink-soft">
            No se pudo cargar: no llegó la respuesta. Los datos siguen acá; probá de nuevo.
          </p>
        )}
        <div className="flex flex-wrap gap-3">
          <button type="button" className={PRIMARY} onClick={confirm} disabled={step.sending}>
            {step.sending ? 'cargando…' : step.failed ? '> probar de nuevo' : '> confirmar'}
          </button>
          <button
            type="button"
            className={SECONDARY}
            onClick={() => setStep({ kind: 'edit' })}
            disabled={step.sending}
          >
            volver
          </button>
        </div>
      </section>
    );
  }

  const on = (field: Field) => problems.filter((p) => PROBLEM_FIELD[p.campo] === field);
  const general = problems.filter((p) => !(p.campo in PROBLEM_FIELD));
  const invalid = (field: Field) => (on(field).length ? true : undefined);
  const described = (id: string, field: Field) => (on(field).length ? `${id}-error` : undefined);

  return (
    <div className="grid w-full gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-10">
      <form noValidate onSubmit={review} aria-label="Cargar tarea" className="flex min-w-0 flex-col gap-4">
        {problems.length > 0 && (
          <div role="alert" className="flex flex-col gap-1 rounded-card border-hard border-line px-3 py-2.5 text-body">
            <p className="m-0 font-bold">No se cargó: hay que corregir lo marcado.</p>
            {general.map((p) => (
              <p key={`${p.campo}-${p.motivo}`} className="m-0 text-ink-soft">
                ! {p.texto}
              </p>
            ))}
          </div>
        )}

        <FieldBlock id="f-objetivo" label="objetivo" errors={on('objetivo_id')}
          hint={options.objetivos.length === 0 ? 'No hay objetivos abiertos en este espacio.' : undefined}>
          <select
            id="f-objetivo"
            className={INPUT}
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
          </select>
        </FieldBlock>

        <FieldBlock id="f-titulo" label="título" errors={on('titulo')}
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

        <FieldBlock id="f-descripcion" label="descripción (opcional)" errors={on('descripcion')}
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
          label="quién la hace"
          errors={on('responsable_id')}
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
          <select
            id="f-responsable"
            className={INPUT}
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
          </select>
        </FieldBlock>

        <FieldBlock
          id="f-fecha"
          label="fecha"
          errors={on('fecha')}
          extra={draft.fecha ? <span className="text-ink">{dayLabel(draft.fecha)}</span> : undefined}
          hint={
            objective?.fecha_objetivo && draft.fecha > objective.fecha_objetivo
              ? `Es posterior a la del objetivo (${shortDate(objective.fecha_objetivo)}): se avisa, no se bloquea.`
              : 'Sólo los días hábiles del espacio, desde hoy.'
          }
        >
          <DatePicker
            days={options.calendario.dias_habiles}
            value={draft.fecha}
            onChange={(day) => change({ fecha: day })}
            labelledBy="f-fecha-label"
            describedBy={described('f-fecha', 'fecha')}
          />
        </FieldBlock>

        <FieldBlock id="f-criterio" label="criterio de aceptación" errors={on('criterio')}
          extra={<Counter value={draft.criterio} limit={LIMITS.criterio} />}
          hint="Qué tiene que pasar para darla por terminada.">
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
          className="m-0 flex min-w-0 flex-col gap-1.5 border-0 p-0"
          aria-describedby={described('f-evidencia', 'evidencia')}
        >
          <legend className="mb-1.5 p-0 text-meta uppercase tracking-[0.04em] text-ink-dim">evidencia que se pide</legend>
          {!member && <p className="m-0 text-small text-ink-dim">Elegí primero quién la hace.</p>}
          {member && !policy && (
            <p className="m-0 text-small text-ink-dim">El área de esa persona todavía no tiene definida qué evidencia se pide.</p>
          )}
          {member && policy && kinds.length === 0 && (
            <p className="m-0 text-small text-ink-dim">El área no pide evidencia.</p>
          )}
          {kinds.map((kind) => (
            <label key={kind} className="flex items-center gap-2 text-body">
              <input
                type="checkbox"
                className="h-4 w-4 accent-ink"
                checked={draft.evidencia.includes(kind)}
                onChange={(e) => toggleEvidence(kind, e.target.checked)}
              />
              <span>
                {evidenceWords(policy, kind)}
                {policy?.evidencia_requerida.includes(kind) && (
                  <span className="text-ink-dim"> · la pide el área</span>
                )}
              </span>
            </label>
          ))}
          {on('evidencia').length > 0 && (
            <ul id="f-evidencia-error" className="m-0 flex list-none flex-col gap-0.5 p-0 text-small font-bold text-ink">
              {on('evidencia').map((e) => (
                <li key={`${e.campo}-${e.motivo}`}>! {e.texto}</li>
              ))}
            </ul>
          )}
        </fieldset>

        <FieldBlock id="f-decidio" label="quién la decidió" errors={on('decidio_id')}>
          <select
            id="f-decidio"
            className={INPUT}
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
          </select>
        </FieldBlock>

        <div className="pt-1">
          <button type="submit" className={PRIMARY}>
            &gt; revisar
          </button>
        </div>
      </form>

      <aside aria-label="Así se va a ver" className="flex min-w-0 flex-col gap-2 lg:sticky lg:top-4 lg:self-start">
        <p className="m-0 text-meta uppercase tracking-[0.04em] text-ink-dim">así se va a ver</p>
        {preview}
      </aside>
    </div>
  );
}
