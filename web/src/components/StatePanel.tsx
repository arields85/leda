import type { Marca } from '../api';
import { STATE_TEXT, STATES } from '../format';

/** One number per state; a state with nothing in it stays gray (ADR 0022, decision 18). */
export function StatePanel({ panel }: { panel: Record<Marca, number> }) {
  return (
    <section
      aria-label="Tareas por estado"
      className="grid grid-cols-4 rounded-card border-hard border-line bg-card shadow-hard"
    >
      {STATES.map(({ marca, label }, index) => {
        const count = panel[marca] ?? 0;
        const color = count > 0 ? STATE_TEXT[marca] : 'text-ink-dim';
        const divider = index < STATES.length - 1 ? 'border-r-hard border-line-soft' : '';
        return (
          <div key={marca} data-state={marca} className={`min-w-0 px-2.5 py-2 ${divider}`}>
            <div className={`text-count font-bold ${color}`}>{count}</div>
            <div className={`truncate text-mini ${color}`}>{label}</div>
          </div>
        );
      })}
    </section>
  );
}
