import type { Marca } from '../api';
import { COUNTERS, STATE_TEXT } from '../format';

/** The counters of the view (ADR 0022, decision 18; MA-3, the user's decision): Vencidas · Sin
 * empezar · En curso · Esperando · Entregadas. A counter with nothing in it stays gray; "Sin
 * empezar" (assigned and not started) has no colour of its own. They may overlap: an overdue task
 * in progress counts in both. Five in one row that fits a 375-px phone: a long label goes to a
 * second line inside its cell before the row could wrap. The labels live in `COUNTERS`. */
export function StatePanel({ panel, notStarted = 0 }: { panel: Record<Marca, number>; notStarted?: number }) {
  return (
    <section
      aria-label="Tareas por estado"
      className="grid min-w-0 grid-cols-5 rounded-card border-hard border-line bg-card shadow-hard"
    >
      {COUNTERS.map(({ key, label }, index) => {
        const count = key === 'sin_empezar' ? notStarted : (panel[key] ?? 0);
        const color = count === 0 ? 'text-ink-dim' : key === 'sin_empezar' ? 'text-ink' : STATE_TEXT[key];
        const divider = index < COUNTERS.length - 1 ? 'border-r-hard border-line-soft' : '';
        return (
          <div key={key} data-state={key} className={`min-w-0 px-1 py-2 ${divider}`}>
            <div className={`text-count font-bold ${color}`}>{count}</div>
            <div className={`text-tiny leading-tight wrap-anywhere ${color}`}>{label}</div>
          </div>
        );
      })}
    </section>
  );
}
