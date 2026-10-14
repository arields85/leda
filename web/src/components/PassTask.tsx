import { useState } from 'react';
import { type ActionProblem, passTask, SessionClosedError, type Task, type Teammate } from '../api';
import { PRIMARY, SECONDARY, WARN } from '../admin/controls';
import { Dropdown } from '../admin/Dropdown';

/** The states in which a task can change hands (the pase's own rule, `herramientas`). */
const PASSABLE = ['asignada', 'en_curso', 'bloqueada'];

const SEND_FAILED = 'No se pudo mandar ahora; probá de nuevo.';

/** "> pasarla" under a task of the referente's sector (J4, D14 steps 2 and 3): to someone of her
 * area, who takes it by chat (Leda asks her). The task stays with whoever has it until then. */
export function PassTask({
  task,
  teammates,
  onClosed,
}: {
  task: Task;
  teammates: Teammate[];
  onClosed: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [to, setTo] = useState('');
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState<string | null>(null);
  const [problems, setProblems] = useState<ActionProblem[]>([]);
  const options = teammates.filter((t) => t.nombre !== task.responsable);
  if (!PASSABLE.includes(task.estado) || options.length === 0) return null;
  const id = `pase-${task.id}`;

  async function send() {
    if (sending) return;
    if (!to) {
      setProblems([{ campo: 'a', motivo: 'falta', texto: 'Elegí a quién se la pasás.' }]);
      return;
    }
    setSending(true);
    try {
      const result = await passTask(task.id, to);
      if (result.kind === 'done') {
        setDone(options.find((t) => t.membership_id === to)?.nombre ?? '');
        setOpen(false);
      } else setProblems(result.errors);
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else setProblems([{ campo: 'envio', motivo: 'sin_respuesta', texto: SEND_FAILED }]);
    } finally {
      setSending(false);
    }
  }

  if (done !== null) {
    return (
      <p role="status" className="m-0 -mt-1.5 text-small text-ink-soft">
        Listo: le pregunto a {done} si la toma. Hasta que diga que sí, la sigue teniendo {task.responsable}.
      </p>
    );
  }
  if (!open) {
    return (
      <button type="button" className={`${SECONDARY} -mt-1.5 w-fit`} onClick={() => setOpen(true)}>
        &gt; pasarla
      </button>
    );
  }
  return (
    <div className="-mt-1.5 flex min-w-0 flex-col gap-2">
      <span id={`${id}-label`} className="text-small text-ink-soft">
        A quién se la pasás
      </span>
      <Dropdown
        id={id}
        labelledBy={`${id}-label`}
        value={to}
        onChange={(value) => {
          setTo(value);
          setProblems([]);
        }}
        options={[
          { value: '', label: 'elegí a una persona' },
          ...options.map((t) => ({ value: t.membership_id, label: `${t.nombre} · ${t.area}` })),
        ]}
      />
      {problems.map((p) => (
        <p key={`${p.campo}-${p.motivo}`} role="alert" className={`m-0 text-small font-bold ${WARN}`}>
          {p.texto}
        </p>
      ))}
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          className={PRIMARY}
          onClick={send}
          disabled={sending}
          aria-disabled={!to && !sending ? true : undefined}
        >
          {sending ? 'mandando…' : '> confirmar'}
        </button>
        <button type="button" className={SECONDARY} onClick={() => setOpen(false)} disabled={sending}>
          &gt; no
        </button>
      </div>
    </div>
  );
}
