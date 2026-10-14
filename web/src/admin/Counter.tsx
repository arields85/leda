import { WARN } from './controls';
import { length } from './draft';

/** How many characters a text has of the ones it may have ("12/200"), as the server counts them,
 * and how many are left over when it passes the limit. */
export function Counter({ value, limit }: { value: string; limit: number }) {
  const n = length(value);
  const over = n > limit;
  return (
    <span aria-live="polite" className={`shrink-0 ${over ? `font-bold ${WARN}` : ''}`}>
      {n}/{limit}
      {over && ` · sobran ${n - limit}`}
    </span>
  );
}
