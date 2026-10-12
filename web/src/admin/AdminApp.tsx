import { useEffect, useState } from 'react';
import { RequestError, SessionClosedError } from '../api';
import { Header } from '../components/Header';
import { Notice } from '../components/Notice';
import { SignOut } from '../components/SignOut';
import { adminSignOut, fetchAdminMe, fetchOptions, type AdminMe, type Options } from './api';
import { LoadForm } from './LoadForm';

type Load<T> =
  | { kind: 'loading' }
  | { kind: 'ready'; data: T }
  | { kind: 'closed' }
  | { kind: 'failed' };

function failure(error: unknown): { kind: 'closed' } | { kind: 'failed' } {
  return error instanceof SessionClosedError ? { kind: 'closed' } : { kind: 'failed' };
}

function SessionClosed({ byPerson = false }: { byPerson?: boolean }) {
  return (
    <Notice title={byPerson ? 'Cerraste la sesión.' : 'La sesión está cerrada.'}>
      <p className="m-0">Para volver a entrar a la administración, entrá con un enlace nuevo.</p>
    </Notice>
  );
}

function Failed({ onRetry }: { onRetry: () => void }) {
  return (
    <Notice title="No se pudo cargar la página.">
      <p className="m-0">Probá de nuevo en un rato.</p>
      <button
        type="button"
        onClick={onRetry}
        className="w-fit rounded-card border-hard border-line bg-card px-3 py-2 text-small text-ink shadow-hard"
      >
        probar de nuevo
      </button>
    </Notice>
  );
}

/** The administration door (ADR 0022, decisions 6 and 10): who is in, which space, and the form
 * that loads a task. Wide on a desktop; it stacks on a phone. */
export function AdminApp() {
  const [attempt, setAttempt] = useState(0);
  const [me, setMe] = useState<Load<AdminMe>>({ kind: 'loading' });
  const [spaceId, setSpaceId] = useState<string | null>(null);
  const [options, setOptions] = useState<Load<Options>>({ kind: 'loading' });
  const [closed, setClosed] = useState(false);
  const [signedOut, setSignedOut] = useState(false);

  useEffect(() => {
    const request = new AbortController();
    setMe({ kind: 'loading' });
    fetchAdminMe(request.signal)
      .then((data) => {
        setMe({ kind: 'ready', data });
        setSpaceId((current) =>
          data.espacios.some((s) => s.id === current) ? current : (data.espacios[0]?.id ?? null),
        );
      })
      .catch((error: unknown) => {
        if (!request.signal.aborted) setMe(failure(error));
      });
    return () => request.abort();
  }, [attempt]);

  useEffect(() => {
    if (spaceId === null) return;
    const request = new AbortController();
    setOptions({ kind: 'loading' });
    fetchOptions(spaceId, request.signal)
      .then((data) => setOptions({ kind: 'ready', data }))
      .catch((error: unknown) => {
        if (request.signal.aborted) return;
        // 404: the space is gone; read the spaces again.
        if (error instanceof RequestError && error.status === 404) setAttempt((n) => n + 1);
        else setOptions(failure(error));
      });
    return () => request.abort();
  }, [spaceId, attempt]);

  const retry = () => setAttempt((n) => n + 1);
  const admin = me.kind === 'ready' ? me.data : null;
  const open = !signedOut && !closed && admin !== null && options.kind !== 'closed';

  let body;
  if (signedOut) body = <SessionClosed byPerson />;
  else if (closed || me.kind === 'closed' || options.kind === 'closed') body = <SessionClosed />;
  else if (me.kind === 'failed') body = <Failed onRetry={retry} />;
  else if (admin === null) body = <Notice title="Cargando…" />;
  else if (admin.espacios.length === 0) body = <Notice title="Todavía no hay espacios." />;
  else {
    body = (
      <>
        {admin.espacios.length > 1 && (
          <label className="flex max-w-[24rem] flex-col gap-1.5 text-meta text-ink-dim">
            <span className="uppercase tracking-[0.04em]">espacio</span>
            <select
              className="w-full rounded-card border-hard border-line bg-card px-3 py-2 text-body text-ink outline-none focus:border-ink"
              value={spaceId ?? ''}
              onChange={(e) => setSpaceId(e.target.value)}
            >
              {admin.espacios.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.nombre}
                </option>
              ))}
            </select>
          </label>
        )}
        {options.kind === 'loading' && <Notice title="Cargando…" />}
        {options.kind === 'failed' && <Failed onRetry={retry} />}
        {options.kind === 'ready' && spaceId && (
          <LoadForm
            key={spaceId}
            spaceId={spaceId}
            options={options.data}
            admin={admin.administrador}
            onClosed={() => setClosed(true)}
          />
        )}
      </>
    );
  }

  const spaceName =
    admin?.espacios.length === 1 ? admin.espacios[0].nombre : options.kind === 'ready' ? options.data.espacio.nombre : '';
  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-[72rem] flex-col px-5">
      <Header
        space={open && spaceName ? `administración · ${spaceName}` : 'administración'}
        title={open ? 'Cargar tarea' : 'Leda'}
        person={open ? admin?.administrador : undefined}
      />
      <main className="flex flex-col gap-4 pt-4">{body}</main>
      {open && (
        <footer className="mt-auto flex justify-end pb-[22px] pt-6">
          <SignOut action={adminSignOut} onDone={() => setSignedOut(true)} />
        </footer>
      )}
    </div>
  );
}
