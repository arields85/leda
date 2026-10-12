import type { ReactNode } from 'react';

/** A plain message in place of the tasks: loading, a failure, a closed session. Human words,
 * never technical details (constitution §10). */
export function Notice({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <section role="status" className="flex flex-col gap-2 pt-6">
      <p className="m-0 text-button font-bold text-ink">{title}</p>
      {children && <div className="flex flex-col gap-2 text-body text-ink-soft">{children}</div>}
    </section>
  );
}
