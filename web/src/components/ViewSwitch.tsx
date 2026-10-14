import type { ViewId, ViewRef } from '../api';
import { Switch } from './Switch';

interface ViewSwitchProps {
  views: ViewRef[];
  current: ViewId;
  onChange: (view: ViewId) => void;
}

/** The switch between the views a person has ("Tus tareas", "Tu sector", "El equipo"); only
 * shown when there is more than one. */
export function ViewSwitch({ views, current, onChange }: ViewSwitchProps) {
  if (views.length < 2) return null;
  return (
    <Switch
      nav
      label="Vistas"
      items={views.map(({ vista, titulo }) => ({ value: vista, label: titulo }))}
      current={current}
      onChange={onChange}
    />
  );
}
