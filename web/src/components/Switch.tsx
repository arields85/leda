export interface SwitchItem<T extends string> {
  value: T;
  label: string;
}

interface SwitchProps<T extends string> {
  items: SwitchItem<T>[];
  current: T;
  onChange: (value: T) => void;
  /** The name of the group, for a screen reader. */
  label: string;
  /** A navigation between views (`nav`) or a choice inside a page (a group). */
  nav?: boolean;
}

/** The tabs of the web: the team's views ("Tus tareas", "Tu sector") and the administration's
 * "Tarea" / "Objetivo". The selected one with a lighter border and the ink text, the others dimmed.
 * Gray, like everything that is not a state. */
export function Switch<T extends string>({ items, current, onChange, label, nav = false }: SwitchProps<T>) {
  const buttons = items.map(({ value, label: name }) => {
    const selected = value === current;
    return (
      <button
        key={value}
        type="button"
        aria-pressed={selected}
        onClick={() => onChange(value)}
        className={`rounded-card border-hard px-2.5 py-1 ${selected ? 'border-line bg-card text-ink' : 'border-line-soft bg-transparent text-ink-dim'}`}
      >
        {name}
      </button>
    );
  });
  const className = 'flex flex-wrap gap-1.5 text-small';
  return nav ? (
    <nav aria-label={label} className={className}>
      {buttons}
    </nav>
  ) : (
    <div role="group" aria-label={label} className={className}>
      {buttons}
    </div>
  );
}
