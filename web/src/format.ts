import type { Marca, Task } from './api';

const WEEKDAYS = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB'];

/** "2026-10-26" → "26.10". */
export function shortDate(iso: string): string {
  return `${iso.slice(8, 10)}.${iso.slice(5, 7)}`;
}

/** "2026-10-26" → "LUN", read as a calendar date (no time zone involved). */
export function weekdayOf(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number);
  return WEEKDAYS[new Date(Date.UTC(year, month - 1, day)).getUTCDay()];
}

export function activeCount(n: number): string {
  return n === 1 ? '1 activa' : `${n} activas`;
}

export function daysLeft(n: number): string {
  if (n <= 0) return 'vence hoy';
  return n === 1 ? 'queda 1 día' : `quedan ${n} días`;
}

/** The four states with color, in the panel's order. */
export const STATES: { marca: Marca; label: string }[] = [
  { marca: 'vencida', label: 'VENCIDA' },
  // "Trabada" is no longer said (the user, MA-3): a blocked task is waiting for something.
  { marca: 'trabada', label: 'ESPERANDO' },
  { marca: 'en_curso', label: 'EN CURSO' },
  { marca: 'entregada', label: 'ENTREGADA' },
];

/** The counters of a view, in their order and with their names, in one place (MA-3, the user's
 * decision): Vencidas · Sin empezar · En curso · Esperando · Entregadas. "Sin empezar" is not a
 * state with a colour: assigned and not started. "Esperando" is a blocked task ("trabada" is no
 * longer said). */
export const COUNTERS: { key: Marca | 'sin_empezar'; label: string }[] = [
  { key: 'vencida', label: 'VENCIDAS' },
  { key: 'sin_empezar', label: 'SIN EMPEZAR' },
  { key: 'en_curso', label: 'EN CURSO' },
  { key: 'trabada', label: 'ESPERANDO' },
  { key: 'entregada', label: 'ENTREGADAS' },
];

/** Each state's text color: the only color on a page (ADR 0022, decision 18). */
export const STATE_TEXT: Record<Marca, string> = {
  vencida: 'text-vencida',
  trabada: 'text-trabada',
  en_curso: 'text-en-curso',
  entregada: 'text-entregada',
};

// A task without a colored state shows its plain state in gray.
const PLAIN_STATES: Record<string, string> = {
  propuesta: 'PROPUESTA',
  pendiente_aprobacion: 'POR APROBAR',
  asignada: 'ASIGNADA',
};

export interface StateLabel {
  text: string;
  marca: Marca | null;
}

function markLabel(task: Task, marca: Marca): string {
  if (marca === 'vencida') {
    const late = task.dias_de_atraso;
    return late !== null && late > 0 ? `[VENCIDA +${late}d]` : '[VENCIDA]';
  }
  return `[${STATES.find((s) => s.marca === marca)?.label ?? 'ABIERTA'}]`;
}

/** The bracketed labels of a task card, one per mark the server gave: "[ESPERANDO]" and
 * "[VENCIDA +2d]" together, or "[EN CURSO]"; without a mark, its plain state in gray. */
export function stateLabels(task: Task): StateLabel[] {
  if (task.marcas.length > 0) {
    return task.marcas.map((marca) => ({ text: markLabel(task, marca), marca }));
  }
  return [{ text: `[${PLAIN_STATES[task.estado] ?? 'ABIERTA'}]`, marca: null }];
}
