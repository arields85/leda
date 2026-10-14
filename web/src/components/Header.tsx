import { weekLine } from '../format';

interface HeaderProps {
  space: string;
  title: string;
  person?: string;
  today?: string;
  isoWeek?: number;
  /** Under the title of "Mi equipo": the referente's area (MA-3), as data. */
  subtitle?: string | null;
}

/** The header (ADR 0022, decision 18, borrowed from "11 · Plano"): space and day in small
 * gray; then, on one line that fits a phone (MA-3), the view's title on the left, which never
 * wraps nor moves, and who is looking on the right. The name is never cut: if it does not fit it
 * goes on in its own right-aligned block ("Ariel" and, under it, "De Simone"). How many tasks are
 * open left the header (MA-3). */
export function Header({ space, title, person, today, isoWeek, subtitle }: HeaderProps) {
  return (
    <header className="flex flex-col gap-2.5 pt-[18px]">
      <div className="flex items-center justify-between gap-3 text-meta text-ink-dim">
        <span className="min-w-0 truncate">{space ? `LEDA · ${space.toUpperCase()}` : 'LEDA'}</span>
        {today && isoWeek !== undefined && (
          <span className="shrink-0">{weekLine(isoWeek, today)}</span>
        )}
      </div>
      <div data-testid="title-line" className="flex min-w-0 flex-nowrap items-start justify-between gap-3">
        <h1 className="m-0 shrink-0 whitespace-nowrap text-title font-extrabold tracking-[-0.02em]">{title}</h1>
        {person && (
          <span data-testid="who" className="min-w-0 pt-1.5 text-right text-small leading-snug wrap-break-word text-ink-soft">
            {person}
          </span>
        )}
      </div>
      {subtitle && <span className="-mt-1.5 min-w-0 truncate text-small text-ink-soft">{subtitle}</span>}
    </header>
  );
}
