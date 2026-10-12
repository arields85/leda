import type { ReactNode } from 'react';
import { shortDate } from '../format';
import { TaskCard } from '../components/TaskCard';
import type { Options } from './api';
import { dayLabel } from './DatePicker';
import { type Draft, evidenceWords, memberOf, policyOf, previewTask } from './draft';

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className="text-meta text-ink-dim">{label}</dt>
      <dd className="m-0 wrap-break-word whitespace-pre-line text-body text-ink">{children}</dd>
    </div>
  );
}

const MISSING = <span className="text-ink-dim">—</span>;

/** The task as it will look (the team's card) and everything it carries: who loads it, who
 * decided it and who reviews it (decisions 6 and 9; ADR 0017, decision 2). */
export function TaskPreview({ draft, options, admin }: { draft: Draft; options: Options; admin: string }) {
  const member = memberOf(options, draft.responsable_id);
  const policy = policyOf(options, member);
  const objective = options.objetivos.find((o) => o.id === draft.objetivo_id);
  const decided = memberOf(options, draft.decidio_id);
  const late =
    objective?.fecha_objetivo && draft.fecha && draft.fecha > objective.fecha_objetivo
      ? objective.fecha_objetivo
      : null;
  return (
    <div className="flex min-w-0 flex-col gap-3">
      <div className="text-body">
        <TaskCard task={previewTask(draft, member)} view="equipo" />
      </div>
      <dl className="m-0 flex flex-col gap-2.5 rounded-card border-hard border-line-soft px-3 py-2.5">
        <Row label="objetivo">{objective?.titulo ?? MISSING}</Row>
        <Row label="fecha">
          {draft.fecha ? dayLabel(draft.fecha) : MISSING}
          {late && (
            <span className="block text-small text-ink-soft">
              Es posterior a la del objetivo ({shortDate(late)}): se avisa, no se bloquea.
            </span>
          )}
        </Row>
        {draft.descripcion.trim() && <Row label="descripción">{draft.descripcion.trim()}</Row>}
        <Row label="criterio de aceptación">{draft.criterio.trim() || MISSING}</Row>
        <Row label="evidencia">
          {draft.evidencia.length
            ? draft.evidencia.map((kind) => evidenceWords(policy, kind)).join(' · ')
            : policy && policy.evidencia_requerida.length === 0 && member
              ? 'el área no pide evidencia'
              : MISSING}
        </Row>
        <Row label="la hace">
          {member ? `${member.nombre} · ${member.area}` : MISSING}
          {member && !member.conectado && (
            <span className="block text-small text-ink-soft">
              [SIN CONECTAR] no va a recibir avisos ni seguimiento hasta que conecte Leda.
            </span>
          )}
        </Row>
        <Row label="la revisa">
          {member ? (member.revisa?.nombre ?? 'nadie: no se va a poder cargar') : MISSING}
        </Row>
        <Row label="la decidió">{decided?.nombre ?? MISSING}</Row>
        <Row label="la carga">{admin}</Row>
      </dl>
    </div>
  );
}
