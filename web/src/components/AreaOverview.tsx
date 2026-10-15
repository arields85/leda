import type { AreaCard } from '../api';
import { COUNTERS, STATE_TEXT } from '../format';

// One counter in a card's line, in the singular when there is one.
const SINGULAR: Record<string, string> = {
  vencida: 'VENCIDA',
  sin_empezar: 'SIN EMPEZAR',
  en_curso: 'EN CURSO',
  trabada: 'ESPERANDO',
  entregada: 'ENTREGADA',
};

/** "Áreas" before choosing one (MA-6, the user's decision): one card per area of the space, its
 * name and its referente, and under them only the counters with something, in the tiles' order
 * and colours (`COUNTERS`, `STATE_TEXT`; "Sin empezar" has no colour of its own). An area with
 * nothing open says so in gray. The numbers come from the server, counted like the tiles. */
export function AreaOverview({ areas, onOpen }: { areas: AreaCard[]; onOpen: (id: string) => void }) {
  if (areas.length === 0) {
    return <p className="m-0 pt-1 text-body text-ink-soft">Este equipo todavía no tiene áreas.</p>;
  }
  return (
    <ul aria-label="Áreas" className="m-0 flex list-none flex-col gap-[11px] p-0 pt-0.5">
      {areas.map((area) => {
        const counts = COUNTERS.map(({ key, label }) => {
          const count = key === 'sin_empezar' ? area.sin_empezar : (area.panel[key] ?? 0);
          return { key, count, label: count === 1 ? SINGULAR[key] : label };
        }).filter(({ count }) => count > 0);
        return (
          <li key={area.id} className="min-w-0">
            <button
              type="button"
              onClick={() => onOpen(area.id)}
              className="flex w-full min-w-0 flex-col gap-1.5 rounded-card border-hard border-line bg-card px-3 py-2.5 text-left shadow-hard"
            >
              <span className="min-w-0 text-body font-bold text-ink">
                {area.nombre}
                {area.referente && <span className="font-normal text-ink-soft"> · {area.referente}</span>}
              </span>
              {counts.length === 0 ? (
                <span className="text-small text-ink-dim">Sin tareas abiertas.</span>
              ) : (
                <span className="flex min-w-0 flex-wrap gap-x-3 gap-y-1 text-small">
                  {counts.map(({ key, count, label }) => (
                    <span key={key} data-state={key} className={key === 'sin_empezar' ? 'text-ink' : STATE_TEXT[key]}>
                      {count} {label}
                    </span>
                  ))}
                </span>
              )}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
