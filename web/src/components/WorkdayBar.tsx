import type { Segment } from '../api';
import { shortDate } from '../format';

const SEGMENT_COLOR: Record<Segment['momento'], string> = {
  pasado: 'bg-en-curso',
  hoy: 'bg-ink',
  futuro: 'bg-track',
};

/** The bar of a task in progress (bar "C"): one segment per working day from assignment to
 * delivery. It measures time, not work: Leda does not know a percentage. */
export function WorkdayBar({ segments }: { segments: Segment[] }) {
  if (segments.length === 0) return null;
  const columns = { gridTemplateColumns: `repeat(${segments.length}, minmax(0, 1fr))` };
  const last = segments.length - 1;
  const today = segments.findIndex((s) => s.momento === 'hoy');
  return (
    <div className="flex flex-col gap-1" aria-label="Días hábiles hasta la entrega">
      <div className="grid gap-0.5" style={columns}>
        {segments.map((segment) => (
          <span
            key={segment.fecha}
            data-moment={segment.momento}
            className={`h-1.5 ${SEGMENT_COLOR[segment.momento]}`}
          />
        ))}
      </div>
      <div className="grid whitespace-nowrap text-mini text-ink-dim" style={columns}>
        {today !== 0 && (
          <span className="justify-self-start" style={{ gridColumn: 1, gridRow: 1 }}>
            {shortDate(segments[0].fecha)}
          </span>
        )}
        {today >= 0 && (
          <span
            className={`text-ink ${today === 0 ? 'justify-self-start' : today === last ? 'justify-self-end' : 'justify-self-center'}`}
            style={{ gridColumn: today + 1, gridRow: 1 }}
          >
            hoy
          </span>
        )}
        {today !== last && last > 0 && (
          <span className="justify-self-end" style={{ gridColumn: last + 1, gridRow: 1 }}>
            {shortDate(segments[last].fecha)}
          </span>
        )}
      </div>
    </div>
  );
}
