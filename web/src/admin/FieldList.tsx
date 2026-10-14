import { Fragment } from 'react';
import { FIELD_LINK } from './controls';
import { Mark } from './FieldBlock';

/** Brings `area` to the middle of the screen with a vertical-only scroll, then focuses `target`
 * without letting the browser scroll on its own: on a phone a focus that scrolls can also move
 * the page sideways. */
export function bringTo(area: HTMLElement, target: HTMLElement) {
  const box = area.getBoundingClientRect();
  const top = window.scrollY + box.top - Math.max(16, (window.innerHeight - box.height) / 2);
  const still = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  window.scrollTo({ top: Math.max(0, top), behavior: still ? 'auto' : 'smooth' });
  target.focus({ preventScroll: true });
}

/** Takes the person to the field whose element has that id: its whole block (label, control and
 * message) in view, and the focus on the control itself (a list's button), the chosen (or first)
 * day of the calendar, or the first box of a group (the group itself when it has none). */
export function focusField(elementId: string) {
  const element = document.getElementById(elementId);
  if (!element) return;
  const target = element.matches('input, select, textarea, button')
    ? element
    : (element.querySelector<HTMLElement>('[tabindex="0"], input, select, textarea') ?? element);
  bringTo(element.closest<HTMLElement>('[data-field]') ?? element, target);
}

/** One field named in a summary: how it is called and where it is. */
export interface NamedField {
  key: string;
  name: string;
  elementId: string;
}

/** "Falta completar: criterio de aceptación, evidencia." Each name takes the focus to its field. */
export function FieldList({ label, fields }: { label: string; fields: NamedField[] }) {
  if (fields.length === 0) return null;
  return (
    <p className="m-0 flex min-w-0 items-start gap-1.5">
      <Mark />
      <span className="min-w-0">
      {label}:{' '}
      {fields.map((field, i) => (
        <Fragment key={field.key}>
          {i > 0 && ', '}
          <button type="button" className={FIELD_LINK} onClick={() => focusField(field.elementId)}>
            {field.name}
          </button>
        </Fragment>
      ))}
      .
      </span>
    </p>
  );
}
