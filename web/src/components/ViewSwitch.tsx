import type { ViewId, ViewRef } from '../api';

interface ViewSwitchProps {
  views: ViewRef[];
  current: ViewId;
  onChange: (view: ViewId) => void;
}

/** The switch between the views a person has ("Tus tareas", "Tu sector", "El equipo"); only
 * shown when there is more than one. Gray, like everything that is not a state. */
export function ViewSwitch({ views, current, onChange }: ViewSwitchProps) {
  if (views.length < 2) return null;
  return (
    <nav aria-label="Vistas" className="flex flex-wrap gap-1.5 text-small">
      {views.map(({ vista, titulo }) => {
        const selected = vista === current;
        return (
          <button
            key={vista}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(vista)}
            className={`rounded-card border-hard px-2.5 py-1 ${selected ? 'border-line bg-card text-ink' : 'border-line-soft bg-transparent text-ink-dim'}`}
          >
            {titulo}
          </button>
        );
      })}
    </nav>
  );
}
