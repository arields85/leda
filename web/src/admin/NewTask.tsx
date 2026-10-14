import { useEffect, useState } from 'react';
import { RequestError, SessionClosedError } from '../api';
import { Notice } from '../components/Notice';
import { fetchTeamOptions, NOT_LOADING, type Options, type TaskApi } from './api';
import { LoadForm } from './LoadForm';

type Load =
  | { kind: 'loading' }
  | { kind: 'ready'; data: Options }
  | { kind: 'refused' }
  | { kind: 'failed' };

/** The task form of the team's door (J4; ADR 0023, decision 3): Dirección and the area referentes,
 * with the same form and help as the administration's. Reads the options of the person's own load
 * (only the people she may load for) and shows the form; a closed session is the page's
 * (`onClosed`). The door's API must keep its identity between renders (`useMemo`). */
export function NewTask({ api, author, onClosed }: { api: TaskApi; author: string; onClosed: () => void }) {
  const [attempt, setAttempt] = useState(0);
  const [load, setLoad] = useState<Load>({ kind: 'loading' });

  useEffect(() => {
    const request = new AbortController();
    setLoad({ kind: 'loading' });
    fetchTeamOptions(request.signal)
      .then((data) => setLoad({ kind: 'ready', data }))
      .catch((error: unknown) => {
        if (request.signal.aborted) return;
        if (error instanceof SessionClosedError) onClosed();
        else if (error instanceof RequestError && error.status === 403) setLoad({ kind: 'refused' });
        else setLoad({ kind: 'failed' });
      });
    return () => request.abort();
    // `onClosed` is the page's; a new one is not a reason to read again.
  }, [attempt]);

  if (load.kind === 'loading') return <Notice title="Cargando…" />;
  if (load.kind === 'refused') return <Notice title={NOT_LOADING} />;
  if (load.kind === 'failed') {
    return (
      <Notice title="No se pudo abrir el formulario.">
        <p className="m-0">Probá de nuevo en un rato.</p>
        <button
          type="button"
          onClick={() => setAttempt((n) => n + 1)}
          className="w-fit rounded-card border-hard border-line bg-card px-3 py-2 text-small text-ink shadow-hard"
        >
          probar de nuevo
        </button>
      </Notice>
    );
  }
  return <LoadForm api={api} options={load.data} admin={author} onClosed={onClosed} stacked />;
}
