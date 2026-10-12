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

/** The header line: "SEM 44 · LUN 26.10". */
export function weekLine(isoWeek: number, today: string): string {
  return `SEM ${isoWeek} · ${weekdayOf(today)} ${shortDate(today)}`;
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
  { marca: 'trabada', label: 'TRABADA' },
  { marca: 'en_curso', label: 'EN CURSO' },
  { marca: 'entregada', label: 'ENTREGADA' },
];

/** Each state's text color: the only color on a page (ADR 0022, decision 18). */
export const STATE_TEXT: Record<Marca, string> = {
  vencida: 'text-vencida',
  trabada: 'text-trabada',
  en_curso: 'text-en-curso',
  entregada: 'text-entregada',
};

// A task without a colored state shows its plain state in gray. A blocked task whose block
// this person is not shown reads "abierta": the page never tells what the server withheld.
const PLAIN_STATES: Record<string, string> = {
  propuesta: 'PROPUESTA',
  pendiente_aprobacion: 'POR APROBAR',
  asignada: 'ASIGNADA',
};

/** The bracketed label of a task card: "[VENCIDA +2d]", "[TRABADA]", "[ASIGNADA]"… */
export function stateLabel(task: Task): string {
  if (task.marca === 'vencida') {
    const late = task.dias_de_atraso;
    return late !== null && late > 0 ? `[VENCIDA +${late}d]` : '[VENCIDA]';
  }
  if (task.marca !== null) {
    return `[${STATES.find((s) => s.marca === task.marca)?.label ?? 'ABIERTA'}]`;
  }
  return `[${PLAIN_STATES[task.estado] ?? 'ABIERTA'}]`;
}
