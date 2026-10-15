import { useId, useRef, useState } from 'react';
import { SessionClosedError } from '../api';
import type { Problem } from './api';
import { Errors, lookedUpTheKey } from './AreaEditor';
import { Completing } from './Completing';
import { INPUT, PRIMARY, SECONDARY, WARN } from './controls';
import { newKey } from './draft';
import type { PersonChange, PersonPreview, Team, TeamApi, TeamPerson } from './teamApi';
import { FIELD_HINT, FIELD_TITLE, PREVIEW_VALUE } from './typography';

/** What the person is doing with the people: giving someone new a place in the team, or bringing
 * back someone who left. */
export type PersonWork = { kind: 'alta' } | { kind: 'reactivar'; person: TeamPerson };

/** How each piece of the preview is named. */
const ROWS: Record<string, string> = {
  nombre: 'Nombre',
  area: 'Área',
  rol: 'Rol',
  quien_aprueba: 'Quién aprueba',
  estado: 'Estado',
};

type Step =
  | { kind: 'edit'; sending: boolean; errors: Problem[] }
  | { kind: 'preview'; preview: PersonPreview; change: PersonChange; sending: boolean; failed: boolean };

function text(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—';
  return typeof v === 'string' || typeof v === 'number' ? String(v) : JSON.stringify(v);
}

const byName = (a: TeamPerson, b: TeamPerson) => a.nombre.localeCompare(b.nombre);

/** Who approves by default, as the server decides it: the area's active referente or, without one,
 * Dirección (J6-D6). Only to say it in the form; the preview says what the server chose. */
export function defaultApprover(team: Team, areaId: string, self?: string): TeamPerson | null {
  const active = team.personas.filter((p) => p.activo && p.membership_id !== self);
  const area = team.areas.find((a) => a.id === areaId);
  const referente =
    area?.referente && area.referente.activo
      ? active.find((p) => p.membership_id === area.referente?.membership_id)
      : undefined;
  return referente ?? active.filter((p) => p.autoridad_final).sort(byName)[0] ?? null;
}

/** What it would do, in words: each piece with its before and after, and who approves by default. */
function Preview({ preview }: { preview: PersonPreview }) {
  const keys = Array.from(new Set([...Object.keys(preview.antes ?? {}), ...Object.keys(preview.despues ?? {})]));
  const rows = keys
    .map((key) => {
      const before = preview.antes?.[key];
      const after = preview.despues?.[key];
      if ((after === null || after === undefined) && (before === null || before === undefined)) return null;
      let value = preview.antes && before !== after ? `${text(before)} → ${text(after)}` : text(after);
      if (key === 'quien_aprueba' && preview.aprobador.por_omision) value += ' (por omisión)';
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

/** Giving someone a place in the team (J7-5): the name, the area, the role and who approves her work
 * (by default the area's referente, said in the form), then "> revisar" asks the server what it
 * would do and "> confirmar" does it with the preview's fingerprint and a key of its own, kept for a
 * retry when no answer came. Someone who left comes back the same way, with her name as it was. */
export function PersonEditor({
  api,
  team,
  work,
  onDone,
  onCancel,
  onClosed,
}: {
  api: TeamApi;
  team: Team;
  work: PersonWork;
  onDone: (message: string, membershipId: string, nombre: string) => void;
  onCancel: () => void;
  onClosed: () => void;
}) {
  const ids = useId();
  const person = work.kind === 'reactivar' ? work.person : undefined;
  const areas = team.areas.filter((a) => !a.archivada);
  const roles = team.roles.filter((r) => !r.autoridad_final);
  // A new person takes the role most of the team has; someone back, hers if it still can be given.
  const usual = [...roles].sort((a, b) => b.personas - a.personas)[0]?.id ?? '';
  const [nombre, setNombre] = useState('');
  const [area, setArea] = useState(person && areas.some((a) => a.id === person.area_id) ? person.area_id : '');
  const [rol, setRol] = useState(person ? (roles.some((r) => r.id === person.rol_id) ? person.rol_id : '') : usual);
  const [aprobador, setAprobador] = useState('');
  const [step, setStep] = useState<Step>({ kind: 'edit', sending: false, errors: [] });
  const key = useRef<string | null>(null);
  // The last confirm got no answer: it may have given her the place. Until the server settles it,
  // the key stays even after going back and reviewing again, so the server can tell (the same alta
  // with that key returns the same person; another one is refused, never a second person).
  const unknown = useRef(false);
  const people = team.personas.filter((p) => p.activo && p.membership_id !== person?.membership_id).sort(byName);
  const fallback = area ? defaultApprover(team, area, person?.membership_id) : null;

  function change(): PersonChange {
    const common = { area_id: area || null, rol_id: rol || null, aprobador_id: aprobador || null };
    return person
      ? { accion: 'reactivar', membership_id: person.membership_id, ...common }
      : { accion: 'alta', nombre, ...common };
  }

  async function review(asked: PersonChange) {
    setStep({ kind: 'edit', sending: true, errors: [] });
    try {
      const result = await api.previewPerson(asked);
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
      const result = await api.confirmPerson(current.change, key.current, current.preview.huella);
      if (result.kind === 'done') {
        key.current = null;
        unknown.current = false;
        const who = text(current.preview.despues?.nombre);
        onDone(
          person ? `${who} volvió al equipo.` : `${who} quedó en el equipo, «sin conectar» hasta que abra su enlace.`,
          result.membershipId,
          who,
        );
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

  const title = person ? `Volver a sumar a ${person.nombre}` : 'Dar de alta a una persona';
  return (
    <section aria-label={title} className="flex min-w-0 flex-col gap-3 rounded-card border-hard border-line px-3 py-2.5">
      <h3 className="m-0 text-body font-bold text-ink">{title}</h3>
      {step.kind === 'preview' ? (
        <section aria-label="Vista previa" className="flex min-w-0 flex-col gap-3">
          <h4 className={`m-0 ${FIELD_TITLE}`}>Vista previa</h4>
          <Preview preview={step.preview} />
          {step.preview.avisos.map((aviso, i) => (
            <p key={`${aviso.codigo}-${i}`} className={`m-0 wrap-break-word ${FIELD_HINT}`}>
              {aviso.mensaje}
            </p>
          ))}
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
              onClick={() => setStep({ kind: 'edit', sending: false, errors: [] })}
            >
              &gt; volver
            </button>
          </div>
        </section>
      ) : (
        <div className="flex min-w-0 flex-col gap-3">
          {!person && (
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
          <div className="flex min-w-0 flex-col gap-1">
            <label htmlFor={`${ids}-area`} className={FIELD_TITLE}>
              Área
            </label>
            <select id={`${ids}-area`} className={INPUT} value={area} onChange={(e) => setArea(e.target.value)}>
              <option value="">Elegí el área</option>
              {areas.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.nombre}
                </option>
              ))}
            </select>
          </div>
          <div className="flex min-w-0 flex-col gap-1">
            <label htmlFor={`${ids}-rol`} className={FIELD_TITLE}>
              Rol
            </label>
            <select id={`${ids}-rol`} className={INPUT} value={rol} onChange={(e) => setRol(e.target.value)}>
              <option value="">Elegí el rol</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.nombre}
                </option>
              ))}
            </select>
          </div>
          <div className="flex min-w-0 flex-col gap-1">
            <label htmlFor={`${ids}-aprobador`} className={FIELD_TITLE}>
              Quién aprueba su trabajo
            </label>
            <select
              id={`${ids}-aprobador`}
              className={INPUT}
              value={aprobador}
              onChange={(e) => setAprobador(e.target.value)}
            >
              <option value="">{fallback ? `${fallback.nombre} (por omisión)` : 'Por omisión'}</option>
              {people.map((p) => (
                <option key={p.membership_id} value={p.membership_id}>
                  {p.nombre} · {p.area}
                </option>
              ))}
            </select>
            <span className={FIELD_HINT}>Por omisión, el referente del área; sin referente, Dirección.</span>
          </div>
          <Errors errors={step.errors} />
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              className={PRIMARY}
              onClick={() => void review(change())}
              disabled={step.sending}
              aria-label={step.sending ? 'revisando…' : undefined}
            >
              {step.sending ? <Completing word="revisando" /> : '> revisar'}
            </button>
            <button type="button" className={SECONDARY} onClick={onCancel} disabled={step.sending}>
              &gt; cancelar
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
