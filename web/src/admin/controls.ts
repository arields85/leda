import { CONTROL, TEXT_SIZE } from './typography';

/**
 * The looks the load forms share (the task's and the objective's), in one place so both read the
 * same.
 */

// What is missing or wrong is said in the palette's attention color (the one of an overdue task):
// the only color on a form, and only while something needs fixing.
export const WARN = 'text-falta';

// The shared box of every control (`typography.ts`), with the attention border while it is wrong.
export const INPUT = `${CONTROL} aria-[invalid=true]:border-falta`;

// Dimmed while something required is missing, but never `disabled`: a tap still says what is
// missing and takes the person there.
export const PRIMARY = `inline-flex h-11 items-center gap-2 rounded-card border-hard border-ink bg-card px-3.5 ${TEXT_SIZE} font-bold text-ink shadow-hard-ink disabled:opacity-50 aria-disabled:opacity-50 aria-disabled:shadow-none`;

export const SECONDARY = `inline-flex h-11 items-center rounded-card border-hard border-line-soft bg-transparent px-3.5 ${TEXT_SIZE} text-ink-soft disabled:opacity-50`;

// Takes the color of the line it is in.
export const FIELD_LINK =
  'cursor-pointer border-0 bg-transparent p-0 text-left font-bold underline decoration-dotted underline-offset-2';
