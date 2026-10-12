import type { Day, Task } from '../api';

/** The week, working day by working day: today filled white, and a day with something due
 * with a lighter border and "N VENCE". */
export function WeekStrip({ days, tasks }: { days: Day[]; tasks: Task[] }) {
  if (days.length === 0) return null;
  const due = new Map<string, number>();
  for (const task of tasks) {
    if (task.fecha_objetivo) due.set(task.fecha_objetivo, (due.get(task.fecha_objetivo) ?? 0) + 1);
  }
  return (
    <ol
      aria-label="La semana"
      className="m-0 grid list-none gap-1.5 p-0 text-meta"
      style={{ gridTemplateColumns: `repeat(${days.length}, minmax(0, 1fr))` }}
    >
      {days.map((day) => {
        const count = due.get(day.fecha) ?? (day.vence_algo ? 1 : 0);
        const frame = day.hoy
          ? 'border-ink bg-ink text-page'
          : count > 0
            ? 'border-line-strong'
            : 'border-line-soft';
        let note = '\u00a0';
        let noteClass = '';
        if (day.hoy) {
          note = 'HOY';
          noteClass = 'font-extrabold';
        } else if (count > 0) {
          note = `${count} VENCE`;
          noteClass = 'font-bold text-ink-soft';
        } else if (!day.habil) {
          note = 'FERIADO';
          noteClass = 'text-ink-dim';
        }
        return (
          <li
            key={day.fecha}
            data-today={day.hoy || undefined}
            className={`flex min-w-0 flex-col items-center gap-px rounded-card border-hard py-1.5 ${frame}`}
          >
            <span className={day.hoy ? 'font-bold' : 'text-ink-dim'}>{day.dia.toUpperCase()}</span>
            <span className={`text-day ${day.hoy ? 'font-bold' : ''}`}>{day.fecha.slice(8, 10)}</span>
            <span className={`text-tiny ${noteClass}`}>{note}</span>
          </li>
        );
      })}
    </ol>
  );
}
