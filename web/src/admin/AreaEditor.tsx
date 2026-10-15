import { Check } from 'lucide-react';
import { useEffect, useId, useRef, useState, type ReactNode } from 'react';
import { SessionClosedError } from '../api';
import type { Problem } from './api';
import { Completing } from './Completing';
import { INPUT, PRIMARY, SECONDARY, WARN } from './controls';
import { newKey } from './draft';
import { Mark } from './FieldBlock';
import type { Approval, AreaChange, AreaPreview, Team, TeamApi, TeamArea } from './teamApi';
import { FIELD_HINT, FIELD_TITLE, FIELD_VALUE, PREVIEW_VALUE } from './typography';

/** What the person is doing with the areas: creating one, or renaming or archiving one. */
export type AreaWork = { kind: 'crear' } | { kind: 'renombrar'; area: TeamArea } | { kind: 'archivar'; area: TeamArea };

/** What each kind of work says once it is done. */
export const DONE: Record<AreaWork['kind'], string> = {
  crear: 'Área creada.',
  renombrar: 'Área renombrada.',
  archivar: 'Área archivada.',
};

const TITLES: Record<AreaWork['kind'], (area?: TeamArea) => string> = {
  crear: () => 'Crear un área',
  renombrar: (area) => `Renombrar ${area?.nombre ?? ''}`,
  archivar: (area) => `Archivar ${area?.nombre ?? ''}`,
};

/** How each piece of the preview is named. */
const ROWS: Record<string, string> = {
  nombre: 'Nombre',
  referente: 'Referente',
  quien_aprueba: 'Quién aprueba',
  evidencia: 'Evidencia',
  estado: 'Estado',
};

const APPROVALS: { value: Approval; label: string; hint: string }[] = [
  { value: 'referente', label: 'Su referente', hint: 'Una persona del equipo revisa el trabajo del área.' },
  { value: 'autoaprobacion', label: 'El área misma', hint: 'Su trabajo se aprueba en el área: se declara a propósito.' },
  { value: 'direccion', label: 'Lo decide Dirección', hint: 'Sin referente por ahora.' },
];

type Step =
  | { kind: 'edit'; sending: boolean; errors: Problem[] }
  | { kind: 'preview'; preview: AreaPreview; change: AreaChange; sending: boolean; failed: boolean };

function text(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—';
  return typeof v === 'string' || typeof v === 'number' ? String(v) : JSON.stringify(v);
}

/** Whether the server looked the key up before refusing a confirmation (migrations 0083 and 0084):
 * not without the session's authority, nor with a malformed value or a missing preview, which it
 * decides first (shared with the people's editor). */
export function lookedUpTheKey(problem: Problem): boolean {
  return (
    problem.campo !== 'sesion' &&
    !problem.motivo.startsWith('mal_formad') &&
    !(problem.campo === 'huella' && problem.motivo === 'falta')
  );
}

/** What the server said cannot be, in its words (shared with the people's editor, J7-5). */
export function Errors({ errors }: { errors: Problem[] }) {
  if (errors.length === 0) return null;
  return (
    <ul role="alert" className={`m-0 flex list-none flex-col gap-0.5 p-0 text-body font-bold ${WARN}`}>
      {errors.map((e) => (
        <li key={`${e.campo}-${e.motivo}`} className="flex min-w-0 items-start gap-1.5">
          <Mark />
          <span className="min-w-0 wrap-break-word">{e.texto}</span>
        </li>
      ))}
    </ul>
  );
}

/** A box to tick (square) or a choice among several (round), as the load form draws them: the
 * native control stays, hidden to the eye, for the keyboard, the screen reader and a tap on its
 * words. */
function Choice({
  type,
  name,
  checked,
  onChange,
  children,
}: {
  type: 'checkbox' | 'radio';
  name?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  children: ReactNode;
}) {
  return (
    <label className={`flex min-w-0 cursor-pointer items-center gap-2 ${FIELD_VALUE}`}>
      <input
        type={type}
        name={name}
        className="peer sr-only"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span
        aria-hidden="true"
        className={`inline-flex size-4 shrink-0 items-center justify-center border-hard border-ink-soft bg-transparent text-ink peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-ink ${
          type === 'radio' ? 'rounded-full' : 'rounded-[3px]'
        }`}
      >
        {checked && <Check strokeWidth={3.5} className="size-3.5" />}
      </span>
      <span className="min-w-0 wrap-break-word">{children}</span>
    </label>
  );
}

/** What a change would do, in words: each piece with its before and after. */
function Preview({ preview }: { preview: AreaPreview }) {
  const keys = Array.from(new Set([...Object.keys(preview.antes ?? {}), ...Object.keys(preview.despues ?? {})]));
  const rows = keys
    .map((key) => {
      const before = preview.antes?.[key];
      const after = preview.despues?.[key];
      if ((after === null || after === undefined) && (before === null || before === undefined)) return null;
      const value = preview.antes && before !== after ? `${text(before)} → ${text(after)}` : text(after);
      return { key, label: ROWS[key] ?? key, value };
    })
    .filter((row): row is { key: string; label: string; value: string } => row !== null);
  return (
    <dl className="m-0 flex flex-col gap-2.5 rounded-card border-hard border-line-soft px-3 py-2.5">
      {rows.map((row) => (
        <div key={row.key} className="flex min-w-0 flex-col gap-0.5">
          <dt className={FIELD_TITLE}>{row.label}</dt>
          <dd className={`m-0 wrap-break-word ${PREVIEW_VALUE}`}>{row.value}</dd>
        </div>
      ))}
    </dl>
  );
}

/** One change to the areas (J7-4): the form (the name, who approves the area's work and what
 * evidence its tasks require, chosen on purpose, or only the new name), then "> revisar" asks the
 * server what it would do, and "> confirmar" does it with the preview's fingerprint and a key of its
 * own, kept for a retry when no answer came. Archiving goes straight to the preview: the server says
 * why it cannot, in its own words. */
export function AreaEditor({
  api,
  team,
  work,
  onDone,
  onCancel,
  onClosed,
}: {
  api: TeamApi;
  team: Team;
  work: AreaWork;
  onDone: (message: string) => void;
  onCancel: () => void;
  onClosed: () => void;
}) {
  const ids = useId();
  const area = work.kind === 'crear' ? undefined : work.area;
  const [nombre, setNombre] = useState(area?.nombre ?? '');
  const [approval, setApproval] = useState<Approval | null>(null);
  const [referente, setReferente] = useState('');
  const [evidence, setEvidence] = useState<string[]>([]);
  const [none, setNone] = useState(false);
  const [step, setStep] = useState<Step>({ kind: 'edit', sending: work.kind === 'archivar', errors: [] });
  const key = useRef<string | null>(null);
  // The last confirm got no answer: it may have done the change. Until the server settles it, the
  // key stays even after going back and reviewing again, so the server can tell (the same change
  // with that key returns what was done; another one is refused, never done twice).
  const unknown = useRef(false);
  const people = team.personas.filter((p) => p.activo).sort((a, b) => a.nombre.localeCompare(b.nombre));
  const kinds = team.tipos_de_evidencia ?? [];

  function change(): AreaChange {
    if (work.kind === 'archivar') return { accion: 'archivar', area_id: work.area.id };
    if (work.kind === 'renombrar') return { accion: 'renombrar', area_id: work.area.id, nombre };
    return {
      accion: 'crear',
      nombre,
      aprobacion: approval,
      referente_id: approval === 'referente' && referente ? referente : null,
      evidencia: none ? [] : evidence,
      sin_evidencia: none,
    };
  }

  async function review(asked: AreaChange) {
    setStep({ kind: 'edit', sending: true, errors: [] });
    try {
      const result = await api.preview(asked);
      if (result.kind === 'preview') {
        // Another review, another attempt: a new key, unless the last confirm's outcome is unknown.
        if (!unknown.current) key.current = null;
        setStep({ kind: 'preview', preview: result.preview, change: asked, sending: false, failed: false });
      } else {
        setStep({ kind: 'edit', sending: false, errors: result.errors });
      }
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else
        setStep({
          kind: 'edit',
          sending: false,
          errors: [{ campo: 'red', motivo: 'sin_respuesta', texto: 'No se pudo revisar: no llegó la respuesta. Probá de nuevo.' }],
        });
    }
  }

  async function confirm() {
    if (step.kind !== 'preview') return;
    const current = step;
    key.current ??= newKey();
    setStep({ ...current, sending: true, failed: false });
    try {
      const result = await api.confirm(current.change, key.current, current.preview.huella);
      if (result.kind === 'done') {
        key.current = null;
        unknown.current = false;
        onDone(DONE[work.kind]);
      } else {
        // A rejection writes nothing, and the server looked the key up first: nothing was done with
        // it, unless the key was used with other data or the server refused before looking it up.
        if (!result.errors.some((e) => e.campo === 'clave' || !lookedUpTheKey(e))) unknown.current = false;
        if (!unknown.current) key.current = null;
        setStep({ kind: 'edit', sending: false, errors: result.errors });
      }
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else {
        unknown.current = true;
        setStep({ ...current, sending: false, failed: true });
      }
    }
  }

  // Archiving has nothing to fill in: it asks the server right away.
  useEffect(() => {
    if (work.kind === 'archivar') void review({ accion: 'archivar', area_id: work.area.id });
    // Once per opened editor: the page opens a new one for another area.
  }, []);

  function tick(kind: string, checked: boolean) {
    setNone(false);
    setEvidence((current) => (checked ? [...current.filter((k) => k !== kind), kind] : current.filter((k) => k !== kind)));
  }

  const title = TITLES[work.kind](area);
  return (
    <section aria-label={title} className="flex min-w-0 flex-col gap-3 rounded-card border-hard border-line px-3 py-2.5">
      <h3 className="m-0 text-body font-bold text-ink">{title}</h3>
      {step.kind === 'preview' ? (
        <section aria-label="Vista previa" className="flex min-w-0 flex-col gap-3">
          <h4 className={`m-0 ${FIELD_TITLE}`}>Vista previa</h4>
          <Preview preview={step.preview} />
          {step.preview.problemas_nuevos.length > 0 && (
            <div role="alert" className={`flex min-w-0 flex-col gap-1 text-body ${WARN}`}>
              <p className="m-0 font-bold">Así el equipo no cuadraría:</p>
              {step.preview.problemas_nuevos.map((p, i) => (
                <p key={`${p.codigo}-${i}`} className="m-0 wrap-break-word">
                  {p.mensaje}
                </p>
              ))}
            </div>
          )}
          {step.failed && (
            <p role="alert" className={`m-0 text-body ${WARN}`}>
              No se pudo confirmar: no llegó la respuesta. Probá de nuevo.
            </p>
          )}
          <div className="flex flex-wrap gap-3">
            {step.preview.problemas_nuevos.length === 0 && (
              <button
                type="button"
                className={PRIMARY}
                onClick={confirm}
                disabled={step.sending}
                aria-label={step.sending ? 'confirmando…' : undefined}
              >
                {step.sending ? <Completing word="confirmando" /> : step.failed ? '> probar de nuevo' : '> confirmar'}
              </button>
            )}
            <button
              type="button"
              className={SECONDARY}
              disabled={step.sending}
              onClick={() => (work.kind === 'archivar' ? onCancel() : setStep({ kind: 'edit', sending: false, errors: [] }))}
            >
              &gt; volver
            </button>
          </div>
        </section>
      ) : (
        <div className="flex min-w-0 flex-col gap-3">
          {work.kind === 'archivar' && step.sending && <p className={`m-0 ${FIELD_HINT}`}>Revisando…</p>}
          {work.kind !== 'archivar' && (
            <div className="flex min-w-0 flex-col gap-1">
              <label htmlFor={`${ids}-nombre`} className={FIELD_TITLE}>
                Nombre
              </label>
              <input
                id={`${ids}-nombre`}
                className={INPUT}
                value={nombre}
                maxLength={80}
                onChange={(e) => setNombre(e.target.value)}
              />
            </div>
          )}
          {work.kind === 'crear' && (
            <>
              <fieldset className="m-0 flex min-w-0 flex-col gap-1.5 border-0 p-0">
                <legend className={`mb-1.5 p-0 ${FIELD_TITLE}`}>Quién aprueba su trabajo</legend>
                {APPROVALS.map((option) => (
                  <div key={option.value} className="flex min-w-0 flex-col gap-0.5">
                    <Choice
                      type="radio"
                      name={`${ids}-aprobacion`}
                      checked={approval === option.value}
                      onChange={() => setApproval(option.value)}
                    >
                      {option.label}
                    </Choice>
                    <span className={`pl-6 ${FIELD_HINT}`}>{option.hint}</span>
                  </div>
                ))}
                {approval === 'referente' && (
                  <div className="flex min-w-0 flex-col gap-1 pl-6">
                    <label htmlFor={`${ids}-referente`} className={FIELD_TITLE}>
                      Referente
                    </label>
                    <select
                      id={`${ids}-referente`}
                      className={INPUT}
                      value={referente}
                      onChange={(e) => setReferente(e.target.value)}
                    >
                      <option value="">Elegí a una persona</option>
                      {people.map((p) => (
                        <option key={p.membership_id} value={p.membership_id}>
                          {p.nombre} · {p.area}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </fieldset>
              <fieldset className="m-0 flex min-w-0 flex-col gap-1.5 border-0 p-0">
                <legend className={`mb-1.5 p-0 ${FIELD_TITLE}`}>Qué evidencia piden sus tareas</legend>
                {kinds.map((kind) => (
                  <Choice
                    key={kind.tipo}
                    type="checkbox"
                    checked={!none && evidence.includes(kind.tipo)}
                    onChange={(checked) => tick(kind.tipo, checked)}
                  >
                    {kind.en_palabras}
                  </Choice>
                ))}
                <Choice
                  type="checkbox"
                  checked={none}
                  onChange={(checked) => {
                    setNone(checked);
                    if (checked) setEvidence([]);
                  }}
                >
                  No pide evidencia
                </Choice>
              </fieldset>
            </>
          )}
          <Errors errors={step.errors} />
          <div className="flex flex-wrap gap-3">
            {work.kind !== 'archivar' && (
              <button
                type="button"
                className={PRIMARY}
                onClick={() => void review(change())}
                disabled={step.sending}
                aria-label={step.sending ? 'revisando…' : undefined}
              >
                {step.sending ? <Completing word="revisando" /> : '> revisar'}
              </button>
            )}
            <button type="button" className={SECONDARY} onClick={onCancel} disabled={step.sending && work.kind !== 'archivar'}>
              {work.kind === 'archivar' ? '> volver' : '> cancelar'}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
