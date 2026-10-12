import type { Wait } from '../api';

interface Line {
  wait: Wait;
  level: number;
  key: string;
}

function flatten(waits: Wait[], level = 0, prefix = ''): Line[] {
  return waits.flatMap((wait, index) => {
    const key = `${prefix}${index}`;
    return [{ wait, level, key }, ...flatten(wait.esperas, level + 1, `${key}.`)];
  });
}

/** The chain of waits of a blocked task, as a tree: "└─ espera: switch nuevo (Lucas)",
 * each level indented under the one it waits for. */
export function WaitTree({ waits }: { waits: Wait[] }) {
  if (waits.length === 0) return null;
  return (
    <ul className="m-0 list-none p-0 text-small text-ink-dim" aria-label="Qué espera">
      {flatten(waits).map(({ wait, level, key }) => (
        <li key={key} data-level={level} className="wrap-break-word" style={{ paddingLeft: `${level * 3}ch` }}>
          └─ espera{wait.que ? `: ${wait.que}` : ''}
          {wait.quien ? ` (${wait.quien})` : ''}
        </li>
      ))}
    </ul>
  );
}
