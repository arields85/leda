import type { Finished, ViewId } from '../api';
import { shortDate } from '../format';

const TITLE = 'Terminadas en los últimos 30 días';

/** What was finished in the last 30 days, apart and after the open tasks, with who did it
 * (the user's decision 3, 2026-10-12): the good news, in gray like every state without color. */
export function FinishedList({ items, view }: { items: Finished[]; view: ViewId }) {
  if (items.length === 0) return null;
  return (
    <section aria-label={TITLE} className="flex flex-col gap-[11px] pt-2 text-body">
      <h2 className="m-0 text-mini font-bold tracking-wide text-ink-dim">{TITLE.toUpperCase()}</h2>
      {items.map((item) => (
        <article
          key={item.id}
          data-finished={item.id}
          className="flex min-w-0 flex-col gap-1 rounded-card border-hard border-dashed border-line-dashed px-3 py-2.5"
        >
          <div className="flex justify-between gap-2">
            <span className="font-bold text-ink-dim">[TERMINADA]</span>
            {item.terminada_el && (
              <span className="shrink-0 text-ink-dim">{shortDate(item.terminada_el)}</span>
            )}
          </div>
          <span className="wrap-break-word font-medium text-ink-soft">{item.titulo}</span>
          {view !== 'tus' && item.responsable && (
            <span className="wrap-break-word text-small text-ink-dim">└─ de {item.responsable}</span>
          )}
        </article>
      ))}
    </section>
  );
}
