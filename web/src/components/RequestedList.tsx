import { useState } from 'react';
import { type ActionProblem, reopenTask, type Requested, SessionClosedError } from '../api';
import { INPUT, PRIMARY, SECONDARY, WARN } from '../admin/controls';
import { shortDate } from '../format';

const TITLE = 'Lo que pediste';

/** How each state reads in the list, the same words as the cards. */
const STATE: Record<string, string> = {
  asignada: 'asignada',
  en_curso: 'en curso',
  bloqueada: 'trabada',
  en_revision: 'entregada',
  terminada: 'terminada',
};

const REASON_LIMIT = 500;
const SEND_FAILED = 'No se pudo mandar ahora. Lo que escribiste sigue acá; probá de nuevo.';

/** "> pedir cambios" on a finished request (J4, D14 step 5): what has to change, and it goes back
 * to the area's referente, who decides who takes it again. */
function AskChanges({ item, onDone, onClosed }: { item: Requested; onDone: () => void; onClosed: () => void }) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState('');
  const [sending, setSending] = useState(false);
  const [problems, setProblems] = useState<ActionProblem[]>([]);
  const field = `cambios-${item.id}`;

  async function send() {
    if (sending) return;
    setSending(true);
    try {
      const result = await reopenTask(item.id, reason);
      if (result.kind === 'done') onDone();
      else setProblems(result.errors);
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else setProblems([{ campo: 'envio', motivo: 'sin_respuesta', texto: SEND_FAILED }]);
    } finally {
      setSending(false);
    }
  }

  if (!open) {
    return (
      <button type="button" className={`${SECONDARY} w-fit`} onClick={() => setOpen(true)}>
        &gt; pedir cambios
      </button>
    );
  }
  return (
    <div className="flex min-w-0 flex-col gap-2">
      <label htmlFor={field} className="text-small text-ink-soft">
        Qué hay que cambiar
      </label>
      <textarea
        id={field}
        className={`${INPUT} min-h-20 resize-y`}
        value={reason}
        maxLength={REASON_LIMIT}
        onChange={(e) => {
          setReason(e.target.value);
          setProblems([]);
        }}
        disabled={sending}
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
          aria-disabled={!reason.trim() && !sending ? true : undefined}
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

/** What the person asked from another area or from Dirección (J4), apart from her own tasks: its
 * state and who has it; finished, "> pedir cambios". Gray, like every state without color. */
export function RequestedList({
  items,
  onChanged,
  onClosed,
}: {
  items: Requested[];
  onChanged: () => void;
  onClosed: () => void;
}) {
  if (items.length === 0) return null;
  return (
    <section aria-label={TITLE} className="flex flex-col gap-[11px] pt-2 text-body">
      <h2 className="m-0 text-mini font-bold tracking-wide text-ink-dim">{TITLE.toUpperCase()}</h2>
      {items.map((item) => (
        <article
          key={item.id}
          data-requested={item.id}
          className="flex min-w-0 flex-col gap-1.5 rounded-card border-hard border-line-soft px-3 py-2.5"
        >
          <div className="flex justify-between gap-2">
            <span className="font-bold text-ink-dim">[{(STATE[item.estado] ?? item.estado).toUpperCase()}]</span>
            {(item.terminada_el ?? item.fecha_objetivo) && (
              <span className="shrink-0 text-ink-dim">{shortDate((item.terminada_el ?? item.fecha_objetivo)!)}</span>
            )}
          </div>
          <span className="wrap-break-word font-medium text-ink-soft">{item.titulo}</span>
          {item.responsable && (
            <span className="wrap-break-word text-small text-ink-dim">
              └─ {item.responsable}
              {item.area ? ` · ${item.area}` : ''}
            </span>
          )}
          {item.puede_pedir_cambios && <AskChanges item={item} onDone={onChanged} onClosed={onClosed} />}
        </article>
      ))}
    </section>
  );
}
