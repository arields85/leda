import type { ReactNode } from 'react';

interface HeaderProps {
  space: string;
  title: string;
  person?: string;
  /** The person's area, under the name (MA-4). */
  area?: string | null;
  /** Under the title of "Mi área": the referente's area (MA-3), as data. */
  subtitle?: string | null;
  /** Under the name and the area: "Cerrar sesión", only on the computer (MA-7). */
  signOut?: ReactNode;
}

/** The header (ADR 0022, decision 18, borrowed from "11 · Plano"): on the top row, the space in
 * small gray on the left and, on the right, who is looking with the area under the name, the same
 * on every tab (MA-4: in place of the week and the date). The name is never cut: if it does not
 * fit it goes on in its own right-aligned block. Under it, the view's title, which never wraps. */
export function Header({ space, title, person, area, subtitle, signOut }: HeaderProps) {
  return (
    <header className="flex flex-col gap-2.5 pt-[18px]">
      <div className="flex min-w-0 items-start justify-between gap-3 text-meta text-ink-dim">
        <span className="min-w-0 truncate">{space ? `LEDA · ${space.toUpperCase()}` : 'LEDA'}</span>
        {person && (
          <span data-testid="who" className="flex min-w-0 flex-col items-end text-right leading-snug wrap-break-word">
            <span className="text-small text-ink-soft">{person}</span>
            {area && <span data-testid="who-area">{area}</span>}
            {signOut}
          </span>
        )}
      </div>
      <div data-testid="title-line" className="flex min-w-0 flex-nowrap items-start justify-between gap-3">
        <h1 className="m-0 shrink-0 whitespace-nowrap text-title font-extrabold tracking-[-0.02em]">{title}</h1>
      </div>
      {subtitle && <span className="-mt-1.5 min-w-0 truncate text-small text-ink-soft">{subtitle}</span>}
    </header>
  );
}
