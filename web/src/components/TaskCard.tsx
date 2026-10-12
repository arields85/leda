import type { Task, ViewId } from '../api';
import { daysLeft, shortDate, STATE_TEXT, stateLabel } from '../format';
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

/** Top right: the working days left on a task in progress, the due date on the others. */
function corner(task: Task): string | null {
  if (task.marca === 'en_curso' && task.quedan_dias_habiles !== null) {
    return daysLeft(task.quedan_dias_habiles);
  }
  return task.fecha_objetivo ? shortDate(task.fecha_objetivo) : null;
}

/** A task: its state in brackets (in color only for the four states), its date, its title,
 * and, when there is one, the chain of waits or the bar of working days. */
export function TaskCard({ task, view }: { task: Task; view: ViewId }) {
  const delivered = task.marca === 'entregada';
  const frame = delivered
    ? 'border-dashed border-line-dashed'
    : 'border-line bg-card shadow-hard';
  const labelColor = task.marca ? STATE_TEXT[task.marca] : 'text-ink-dim';
  const owner = ownerLine(task, view);
  const top = corner(task);
  const waits = task.marca === 'trabada' && task.esperas ? task.esperas : [];
  const bar = task.barra ?? [];
  return (
    <article
      data-task={task.id}
      className={`flex min-w-0 flex-col rounded-card border-hard px-3 py-2.5 ${bar.length ? 'gap-[5px]' : 'gap-1'} ${frame}`}
    >
      <div className="flex justify-between gap-2">
        <span className={`font-bold ${labelColor}`}>{stateLabel(task)}</span>
        {top && <span className="shrink-0 text-ink-dim">{top}</span>}
      </div>
      <span className={`wrap-break-word font-medium ${delivered ? 'text-ink-soft' : ''}`}>
        {task.titulo}
      </span>
      {owner && <span className="wrap-break-word text-small text-ink-dim">{owner}</span>}
      <WaitTree waits={waits} />
      <WorkdayBar segments={bar} />
    </article>
  );
}
