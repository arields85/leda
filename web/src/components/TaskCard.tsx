import type { ReactNode } from 'react';
import type { Task, ViewId } from '../api';
import { daysLeft, shortDate, STATE_TEXT, stateLabels } from '../format';
import { WaitTree } from './WaitTree';
import { WorkdayBar } from './WorkdayBar';

/** Whose task it is, when it is not the person's own: "└─ de Ariel · te espera". */
function ownerLine(task: Task, view: ViewId): string | null {
  if (!task.responsable) return null;
  if (view !== 'tus') return `└─ de ${task.responsable}`;
  if (task.papel === 'espero') return `└─ de ${task.responsable} · la esperás`;
  if (task.papel === 'me_esperan') return `└─ de ${task.responsable} · te espera`;
  return null;
}

/** Top right: the working days left on a task in progress, the due date on the others, and
 * the day the person gave when a delay was already talked about ("19.10 · prevé 28.10"). */
function corner(task: Task): string | null {
  if (task.marcas.includes('en_curso') && task.quedan_dias_habiles !== null) {
    return daysLeft(task.quedan_dias_habiles);
  }
  const due = task.fecha_objetivo ? shortDate(task.fecha_objetivo) : null;
  const forecast = task.prevision ? `prevé ${shortDate(task.prevision)}` : null;
  return [due, forecast].filter(Boolean).join(' · ') || null;
}

/** A task: its states in brackets (in color only for the four states; blocked and late can come
 * together), its date, its title, and, when there is one, the chain of waits or the bar of
 * working days. `title`, when given, is shown in place of the task's title (the load preview
 * marks there the words Leda corrected, J2-19). */
export function TaskCard({ task, view, title }: { task: Task; view: ViewId; title?: ReactNode }) {
  const delivered = task.marcas.includes('entregada');
  const frame = delivered
    ? 'border-dashed border-line-dashed'
    : 'border-line bg-card shadow-hard';
  const owner = ownerLine(task, view);
  const top = corner(task);
  const waits = task.marcas.includes('trabada') && task.esperas ? task.esperas : [];
  const bar = task.barra ?? [];
  return (
    <article
      data-task={task.id}
      className={`flex min-w-0 flex-col rounded-card border-hard px-3 py-2.5 ${bar.length ? 'gap-[5px]' : 'gap-1'} ${frame}`}
    >
      <div className="flex justify-between gap-2">
        <span className="flex min-w-0 flex-wrap gap-x-1.5">
          {stateLabels(task).map(({ text, marca }) => (
            <span key={text} className={`font-bold ${marca ? STATE_TEXT[marca] : 'text-ink-dim'}`}>
              {text}
            </span>
          ))}
        </span>
        {top && <span className="shrink-0 text-ink-dim">{top}</span>}
      </div>
      <span className={`wrap-break-word font-medium ${delivered ? 'text-ink-soft' : ''}`}>
        {title ?? task.titulo}
      </span>
      {owner && <span className="wrap-break-word text-small text-ink-dim">{owner}</span>}
      <WaitTree waits={waits} />
      <WorkdayBar segments={bar} />
    </article>
  );
}
