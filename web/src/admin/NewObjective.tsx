import { useEffect, useState } from 'react';
import { RequestError, SessionClosedError } from '../api';
import { Notice } from '../components/Notice';
import { NO_AUTHORITY, type ObjectiveApi, type ObjectiveOptions } from './objectiveApi';
import { ObjectiveForm } from './ObjectiveForm';

type Load =
  | { kind: 'loading' }
  | { kind: 'ready'; data: ObjectiveOptions }
  | { kind: 'refused' }
  | { kind: 'failed' };

/** Reads what the objective form offers, through the door it was given, and shows the form. Its
 * own messages while it reads or when it could not; a closed session is the page's
 * (`onClosed`). The door's API must keep its identity between renders (`useMemo`). */
export function NewObjective({
  api,
  author,
  onClosed,
  stacked,
}: {
  api: ObjectiveApi;
  author: string;
  onClosed: () => void;
  stacked?: boolean;
}) {
  const [attempt, setAttempt] = useState(0);
  const [load, setLoad] = useState<Load>({ kind: 'loading' });

  useEffect(() => {
    const request = new AbortController();
    setLoad({ kind: 'loading' });
    api
      .options(request.signal)
      .then((data) => setLoad({ kind: 'ready', data }))
      .catch((error: unknown) => {
        if (request.signal.aborted) return;
        if (error instanceof SessionClosedError) onClosed();
        else if (error instanceof RequestError && error.status === 403) setLoad({ kind: 'refused' });
        else setLoad({ kind: 'failed' });
      });
    return () => request.abort();
    // `onClosed` is the page's; a new one is not a reason to read again.
  }, [api, attempt]);

  if (load.kind === 'loading') return <Notice title="Cargando…" />;
  if (load.kind === 'refused') return <Notice title={NO_AUTHORITY} />;
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
  return (
    <ObjectiveForm
      api={api}
      options={load.data}
      author={author}
      onClosed={onClosed}
      stacked={stacked}
      onAnother={() => setAttempt((n) => n + 1)}
    />
  );
}
