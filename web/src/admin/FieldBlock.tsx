import { CircleAlert } from 'lucide-react';
import type { ReactNode } from 'react';
import type { Problem } from './api';
import { WARN } from './controls';
import { FIELD_HINT, FIELD_TITLE } from './typography';

/** The mark in front of what the form still needs: a Lucide icon, not a "!" character (user,
 * 2026-10-13). Decorative: the text next to it says it all. */
export function Mark() {
  return <CircleAlert aria-hidden="true" strokeWidth={2.25} className="mt-[0.2em] size-[1em] shrink-0" />;
}

/** The small mark of a value Leda proposed, until the person changes it. Outside the label, so
 * the field keeps its name. */
export function Proposed({ on }: { on?: boolean }) {
  return on ? <span className="shrink-0 text-propuesto">· propuesto por Leda</span> : null;
}

/** A field of a load form: its name (and, at its right, `extra`: a counter or the chosen day), the
 * control, a hint under it, what is wrong with it and, below, what Leda proposes for it. The
 * messages are `${id}-error`, so the control can point at them with `aria-describedby`. */
export function FieldBlock({
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
