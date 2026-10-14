import type { ReactNode } from 'react';
import { shortDate } from '../format';
import { TaskCard } from '../components/TaskCard';
import type { Options } from './api';
import { dayLabel } from './DatePicker';
import { WARN } from './controls';
import {
  type Draft,
  evidenceWords,
  lateForObjective,
  memberOf,
  policyOf,
  previewTask,
  requestNote,
  reviewerName,
  teamDoor,
  waitOf,
} from './draft';
import { FIELD_HINT, FIELD_TITLE, PREVIEW_VALUE } from './typography';

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
}: {
  draft: Draft;
  options: Options;
  admin: string;
}) {
  const member = memberOf(options, draft.responsable_id);
  const policy = policyOf(options, member);
  const objective = options.objetivos.find((o) => o.id === draft.objetivo_id);
  // Through the team's door (J4) the person who loads it decided it; through the administration's,
  // the one declared.
  const decided = teamDoor(options) ? options.yo?.nombre : memberOf(options, draft.decidio_id)?.nombre;
  const reviewer = reviewerName(draft, options);
  const request = member?.como === 'pedido_a_otra_area' || member?.como === 'pedido_a_direccion';
  const wait = waitOf(options, draft.espera_id);
  // Decision 6 (2026-10-14): a task never falls due after its objective; it does not load so.
  const late = lateForObjective(draft, options)?.fecha_objetivo ?? null;
  return (
    <div className="flex min-w-0 flex-col gap-3">
      <div className="text-body">
        <TaskCard task={previewTask(draft, member)} view="equipo" />
      </div>
      <dl className="m-0 flex flex-col gap-2.5 rounded-card border-hard border-line-soft px-3 py-2.5">
        <Row label="Objetivo">{objective?.titulo ?? MISSING}</Row>
        <Row label="Fecha">
          {draft.fecha ? dayLabel(draft.fecha) : MISSING}
          {late && (
            <span className={`block font-bold ${FIELD_HINT} ${WARN}`}>
              Vence después que su objetivo ({shortDate(late)}): así no se carga.
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
          </Row>
        )}
        <Row label="Criterio de aceptación">
          {draft.criterio.trim() || MISSING}
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
            <span className={`block ${FIELD_HINT} ${WARN}`}>
              [SIN CONECTAR] no va a recibir avisos ni seguimiento hasta que conecte Leda.
            </span>
          )}
        </Row>
        <Row label="La revisa">
          {member ? (reviewer ?? 'nadie: no se va a poder cargar') : MISSING}
        </Row>
        {/* What a request is, in one plain line, with the form's same words (J4 phone test). */}
        {request && (
          <Row label="La pide">
            {options.yo?.nombre ?? admin}
            <span className={`block ${FIELD_HINT}`}>{requestNote(options, member)}</span>
          </Row>
        )}
        <Row label="La decidió">{decided ?? MISSING}</Row>
        <Row label="La carga">{admin}</Row>
      </dl>
    </div>
  );
}
