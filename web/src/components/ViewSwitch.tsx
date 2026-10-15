import type { ViewId, ViewRef } from '../api';

interface ViewSwitchProps {
  views: ViewRef[];
  current: ViewId;
  onChange: (view: ViewId) => void;
  /** "Equipo" (J7-3), only to Dirección: one more tab, after the views. While it is open, none of
   * the views is the selected one. */
  team?: { open: boolean; onOpen: () => void };
}

/** The tabs between the views a person has ("Mis tareas", "Mi área", "Mis pedidos") and, to
 * Dirección, "Equipo", only when there is more than one. Real tabs in one row that never wraps
 * (MA-3, the user's iPhone test): each takes an equal share of the width and cuts its name before
 * going to a second line; the selected one has the ink text and a mark underneath. */
export function ViewSwitch({ views, current, onChange, team }: ViewSwitchProps) {
  const tabs = [
    ...views.map(({ vista, titulo }) => ({
      key: vista,
      titulo,
      selected: !team?.open && vista === current,
      onClick: () => onChange(vista),
    })),
    ...(team ? [{ key: 'equipo-del-espacio', titulo: 'Equipo', selected: team.open, onClick: team.onOpen }] : []),
  ];
  if (tabs.length < 2) return null;
  return (
    <nav aria-label="Vistas" className="min-w-0">
      <div role="tablist" aria-label="Vistas" className="flex min-w-0 flex-nowrap border-b-hard border-line-soft text-small">
        {tabs.map(({ key, titulo, selected, onClick }) => {
          return (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={onClick}
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
