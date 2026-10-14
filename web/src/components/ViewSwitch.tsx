import type { ViewId, ViewRef } from '../api';

interface ViewSwitchProps {
  views: ViewRef[];
  current: ViewId;
  onChange: (view: ViewId) => void;
}

/** The tabs between the views a person has ("Mis tareas", "Mi equipo", "Lo que pedí"; Dirección,
 * "Todo el equipo"), only when there is more than one. Real tabs in one row that never wraps
 * (MA-3, the user's iPhone test): each takes an equal share of the width and cuts its name before
 * going to a second line; the selected one has the ink text and a mark underneath. */
export function ViewSwitch({ views, current, onChange }: ViewSwitchProps) {
  if (views.length < 2) return null;
  return (
    <nav aria-label="Vistas" className="min-w-0">
      <div role="tablist" aria-label="Vistas" className="flex min-w-0 flex-nowrap border-b-hard border-line-soft text-small">
        {views.map(({ vista, titulo }) => {
          const selected = vista === current;
          return (
            <button
              key={vista}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => onChange(vista)}
              className={`-mb-px min-w-0 flex-1 basis-0 truncate whitespace-nowrap border-b-2 bg-transparent px-1 pb-1.5 pt-1 ${
                selected ? 'border-ink font-bold text-ink' : 'border-transparent text-ink-dim'
              }`}
            >
              {titulo}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
