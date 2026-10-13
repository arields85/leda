import { activeCount, weekLine } from '../format';

interface HeaderProps {
  space: string;
  title: string;
  person?: string;
  active?: number;
  today?: string;
  isoWeek?: number;
}

/** The header (ADR 0022, decision 18, borrowed from "11 · Plano"): space and day in small
 * gray, the view's title big, and who is looking with how many open tasks. */
export function Header({ space, title, person, active, today, isoWeek }: HeaderProps) {
  return (
    <header className="flex flex-col gap-2.5 pt-[18px]">
      <div className="flex items-center justify-between gap-3 text-meta text-ink-dim">
        <span className="min-w-0 truncate">{space ? `LEDA · ${space.toUpperCase()}` : 'LEDA'}</span>
        {today && isoWeek !== undefined && (
          <span className="shrink-0">{weekLine(isoWeek, today)}</span>
        )}
      </div>
      <div className="flex min-w-0 items-end justify-between gap-3">
        <h1 className="m-0 min-w-0 wrap-break-word text-title font-extrabold tracking-[-0.02em]">{title}</h1>
        {person && (
          <span className="pb-0.5 text-right text-small text-ink-soft">
            {person}
            {active !== undefined && <span className="text-ink-dim"> · {activeCount(active)}</span>}
          </span>
        )}
      </div>
    </header>
  );
}
