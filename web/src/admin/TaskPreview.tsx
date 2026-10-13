import type { ReactNode } from 'react';
import { shortDate } from '../format';
import { TaskCard } from '../components/TaskCard';
import type { Options, SpellChange, TextField } from './api';
import { dayLabel } from './DatePicker';
import { type Draft, evidenceWords, memberOf, policyOf, previewTask, waitOf } from './draft';
import { FIELD_HINT, FIELD_TITLE, PREVIEW_VALUE } from './typography';

/** The words Leda corrected in each text, shown in the preview until the person edits that text
 * (J2-17). */
export type Spelled = Partial<Record<TextField, SpellChange[]>>;

/** The mark that Leda corrected the spelling of a text, with each word as it was and as it is
 * now: gray like the help, no color (nothing is wrong), so the person sees what changed before
 * confirming. */
function SpellMark({ changes, of }: { changes?: SpellChange[]; of?: string }) {
  if (!changes) return null;
  const list = changes.map((c) => `${c.antes} → ${c.despues}`).join(', ');
  return (
    <span data-spelling className={`block ${FIELD_HINT}`}>
      {of ? `${of}: ` : ''}Leda corrigió la ortografía{list ? ` (${list})` : ''}.
    </span>
  );
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className={FIELD_TITLE}>{label}</dt>
      <dd className={`m-0 wrap-break-word whitespace-pre-line ${PREVIEW_VALUE}`}>{children}</dd>
    </div>
  );
}

const MISSING = <span className={PREVIEW_VALUE}>—</span>;

/** The task as it will look (the team's card) and everything it carries: who loads it, who
 * decided it and who reviews it (decisions 6 and 9; ADR 0017, decision 2). */
export function TaskPreview({
  draft,
  options,
  admin,
  spelled = {},
}: {
  draft: Draft;
  options: Options;
  admin: string;
  spelled?: Spelled;
}) {
  const member = memberOf(options, draft.responsable_id);
  const policy = policyOf(options, member);
  const objective = options.objetivos.find((o) => o.id === draft.objetivo_id);
  const decided = memberOf(options, draft.decidio_id);
  const wait = waitOf(options, draft.espera_id);
  const late =
    objective?.fecha_objetivo && draft.fecha && draft.fecha > objective.fecha_objetivo
      ? objective.fecha_objetivo
      : null;
  return (
    <div className="flex min-w-0 flex-col gap-3">
      <div className="text-body">
        <TaskCard task={previewTask(draft, member)} view="equipo" />
        <SpellMark changes={spelled.titulo} of="Título" />
      </div>
      <dl className="m-0 flex flex-col gap-2.5 rounded-card border-hard border-line-soft px-3 py-2.5">
        <Row label="Objetivo">{objective?.titulo ?? MISSING}</Row>
        <Row label="Fecha">
          {draft.fecha ? dayLabel(draft.fecha) : MISSING}
          {late && (
            <span className={`block ${FIELD_HINT}`}>
              Es posterior a la del objetivo ({shortDate(late)}): se avisa, no se bloquea.
            </span>
          )}
        </Row>
        {wait && (
          <Row label="Espera a">
            {[wait.titulo, wait.responsable].filter(Boolean).join(' · ')}
            <span className={`block ${FIELD_HINT}`}>
              No puede empezar hasta que esa esté terminada.
            </span>
          </Row>
        )}
        {draft.descripcion.trim() && (
          <Row label="Descripción">
            {draft.descripcion.trim()}
            <SpellMark changes={spelled.descripcion} />
          </Row>
        )}
        <Row label="Criterio de aceptación">
          {draft.criterio.trim() || MISSING}
          <SpellMark changes={spelled.criterio} />
        </Row>
        <Row label="Evidencia">
          {draft.evidencia.length
            ? draft.evidencia.map((kind) => evidenceWords(policy, kind)).join(' · ')
            : policy && policy.evidencia_requerida.length === 0 && member
              ? 'el área no pide evidencia'
              : MISSING}
        </Row>
        <Row label="La hace">
          {member ? `${member.nombre} · ${member.area}` : MISSING}
          {member && !member.conectado && (
            <span className={`block ${FIELD_HINT}`}>
              [SIN CONECTAR] no va a recibir avisos ni seguimiento hasta que conecte Leda.
            </span>
          )}
        </Row>
        <Row label="La revisa">
          {member ? (member.revisa?.nombre ?? 'nadie: no se va a poder cargar') : MISSING}
        </Row>
        <Row label="La decidió">{decided?.nombre ?? MISSING}</Row>
        <Row label="La carga">{admin}</Row>
      </dl>
    </div>
  );
}
