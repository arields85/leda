import { CONTROL, TEXT_SIZE } from './typography';

/**
 * The looks the load forms share (the task's and the objective's), in one place so both read the
 * same.
 */

// What is missing or wrong is said in the palette's attention color (the one of an overdue task):
// the only color on a form, and only while something needs fixing.
export const WARN = 'text-falta';

// A task or an objective just created, said where "confirmar" was (J4 phone test, 2026-10-14):
// teal, the only other color on a form, and only for that success.
export const CREATED = 'text-creado';

// The shared box of every control (`typography.ts`), with the attention border while it is wrong.
export const INPUT = `${CONTROL} aria-[invalid=true]:border-falta`;

// A button that cannot act now reads as off (the user's phone test of the J3): dimmed text and
// border and no shadow, whether it is `disabled` (while it sends) or only `aria-disabled` (while
// something required is missing: a tap still says what and takes the person there). Gray, never a
// color: color is only for states.
export const OFF =
  'disabled:border-line-soft disabled:text-ink-dim disabled:shadow-none aria-disabled:border-line-soft aria-disabled:text-ink-dim aria-disabled:shadow-none';

export const PRIMARY = `inline-flex h-11 items-center gap-2 rounded-card border-hard border-ink bg-card px-3.5 ${TEXT_SIZE} font-bold text-ink shadow-hard-ink ${OFF}`;

// Active, it reads as active: the strong gray border and the ink text ("> cargarlo aparte",
// "> empezar de nuevo"), without the primary's weight and shadow.
export const SECONDARY = `inline-flex h-11 items-center rounded-card border-hard border-line-strong bg-transparent px-3.5 ${TEXT_SIZE} text-ink ${OFF}`;

// A square button with an icon, the same height as the others (the microphone and "borrar el
// texto" of the free box).
export const ICON = `inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-card border-hard border-line-strong bg-transparent text-ink ${OFF}`;

// Takes the color of the line it is in.
export const FIELD_LINK =
  'cursor-pointer border-0 bg-transparent p-0 text-left font-bold underline decoration-dotted underline-offset-2';
