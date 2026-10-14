import type { ReactNode } from 'react';
import { shortDate } from '../format';
import { WARN } from './controls';
import { dayLabel } from './DatePicker';
import type { ObjectiveOptions } from './objectiveApi';
import { lateForParent, type ObjectiveDraft, parentOf, referentOf } from './objectiveDraft';
import { FIELD_HINT, FIELD_TITLE, FIELD_VALUE, PREVIEW_VALUE } from './typography';

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className={FIELD_TITLE}>{label}</dt>
      <dd className={`m-0 wrap-break-word whitespace-pre-line ${PREVIEW_VALUE}`}>{children}</dd>
    </div>
  );
}

const MISSING = <span className={PREVIEW_VALUE}>—</span>;

/** The objective as it will be created, in plain words: its name and level (with the pack's
 * names), what it hangs from, its referente, its date and who creates it. It is born active: whoever
 * creates it decides it (ADR 0023, decision 1). */
export function ObjectivePreview({
  draft,
  options,
  author,
}: {
  draft: ObjectiveDraft;
  options: ObjectiveOptions;
  author: string;
}) {
  const parent = parentOf(options, draft.padre_id);
  const referent = referentOf(options, draft.referente_id);
  const level = draft.tipo ? options.niveles[draft.tipo] : null;
  // Decision 5 (2026-10-14): it does not fall due after the one it is part of.
  const late = lateForParent(draft, options);
  return (
    <div className="flex min-w-0 flex-col gap-3">
      <p className={`m-0 wrap-break-word font-bold ${FIELD_VALUE} text-ink`}>
        {draft.titulo.trim() || '(sin nombre)'}
      </p>
      <dl className="m-0 flex flex-col gap-2.5 rounded-card border-hard border-line-soft px-3 py-2.5">
        <Row label="Nivel">{level ?? MISSING}</Row>
        <Row label="Es parte de">
          {parent ? `${parent.titulo} · ${options.niveles[parent.tipo]}` : 'ninguno'}
        </Row>
        <Row label="Referente">
          {referent ? `${referent.nombre} · ${referent.areas.join(', ')}` : MISSING}
        </Row>
        <Row label="Fecha">
          {draft.fecha ? dayLabel(draft.fecha) : MISSING}
          {late?.fecha_objetivo && (
            <span className={`block font-bold ${FIELD_HINT} ${WARN}`}>
              Vence después que «{late.titulo}» ({shortDate(late.fecha_objetivo)}).
            </span>
          )}
        </Row>
        {draft.descripcion.trim() && <Row label="Descripción">{draft.descripcion.trim()}</Row>}
        <Row label="Lo crea">
          {author}
          <span className={`block ${FIELD_HINT}`}>Queda activo al confirmarlo.</span>
        </Row>
      </dl>
    </div>
  );
}
