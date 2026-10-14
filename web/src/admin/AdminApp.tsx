import { useEffect, useMemo, useState } from 'react';
import { RequestError, SessionClosedError } from '../api';
import { Header } from '../components/Header';
import { Notice } from '../components/Notice';
import { SignOut } from '../components/SignOut';
import { adminSignOut, fetchAdminMe, fetchOptions, type AdminMe, type Options } from './api';
import { Dropdown } from './Dropdown';
import { LoadForm } from './LoadForm';
import { NewObjective } from './NewObjective';
import { adminObjectives } from './objectiveApi';

type Load<T> =
  | { kind: 'loading' }
  | { kind: 'ready'; data: T }
  | { kind: 'closed' }
  | { kind: 'failed' };

// The options of a space can also be gone: the server no longer finds that space.
type OptionsLoad = Load<Options> | { kind: 'gone' };

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

function RetryButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-fit rounded-card border-hard border-line bg-card px-3 py-2 text-small text-ink shadow-hard"
    >
      probar de nuevo
    </button>
  );
}

function Failed({ onRetry }: { onRetry: () => void }) {
  return (
    <Notice title="No se pudo cargar la página.">
      <p className="m-0">Probá de nuevo en un rato.</p>
      <RetryButton onClick={onRetry} />
    </Notice>
  );
}

/** What the administrator loads: a task (ADR 0022) or an objective (ADR 0023, decision 5). */
type Kind = 'tarea' | 'objetivo';

const KINDS: { kind: Kind; label: string }[] = [
  { kind: 'tarea', label: 'tarea' },
  { kind: 'objetivo', label: 'objetivo' },
];

/** The choice at the top of the load area: a task or an objective. Gray, like everything that is
 * not a state (the same look as the team's view switch). */
function KindSwitch({ current, onChange }: { current: Kind; onChange: (kind: Kind) => void }) {
  return (
    <div role="group" aria-label="Qué cargar" className="flex flex-wrap gap-1.5 text-small">
      {KINDS.map(({ kind, label }) => {
        const selected = kind === current;
        return (
          <button
            key={kind}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(kind)}
            className={`rounded-card border-hard px-2.5 py-1 ${selected ? 'border-line bg-card text-ink' : 'border-line-soft bg-transparent text-ink-dim'}`}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}

/** The administration door (ADR 0022, decisions 6 and 10): who is in, which space, and the form
 * that loads a task or, chosen at the top, the one that creates an objective (ADR 0023, decision
 * 5). Wide on a desktop; it stacks on a phone. */
export function AdminApp() {
  const [attempt, setAttempt] = useState(0);
  const [me, setMe] = useState<Load<AdminMe>>({ kind: 'loading' });
  const [spaceId, setSpaceId] = useState<string | null>(null);
  const [options, setOptions] = useState<OptionsLoad>({ kind: 'loading' });
  const [closed, setClosed] = useState(false);
  const [signedOut, setSignedOut] = useState(false);
  const [kind, setKind] = useState<Kind>('tarea');
  // Back to the task after the objective form, the task's options are read again: an objective
  // just created is one a task can contribute to.
  const [reread, setReread] = useState(0);
  const objectives = useMemo(() => (spaceId ? adminObjectives(spaceId) : null), [spaceId]);

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
      .catch(async (error: unknown) => {
        if (request.signal.aborted) return;
        if (!(error instanceof RequestError && error.status === 404)) {
          setOptions(failure(error));
          return;
        }
        // 404: the space is gone. Read the spaces once more, so the selector stops offering it,
        // and say so; never fetch again on its own (only "probar de nuevo" does).
        try {
          const fresh = await fetchAdminMe(request.signal);
          if (request.signal.aborted) return;
          setMe({ kind: 'ready', data: fresh });
          if (!fresh.espacios.some((s) => s.id === spaceId)) setSpaceId(null);
          setOptions({ kind: 'gone' });
        } catch (again: unknown) {
          if (!request.signal.aborted) setOptions(failure(again));
        }
      });
    return () => request.abort();
  }, [spaceId, attempt, reread]);

  function chooseKind(next: Kind) {
    if (next === kind) return;
    if (next === 'tarea') setReread((n) => n + 1);
    setKind(next);
  }

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
        {(admin.espacios.length > 1 || spaceId === null) && (
          <div className="flex w-full min-w-0 max-w-[24rem] flex-col gap-1.5 text-meta text-ink-dim">
            <label id="f-espacio-label" htmlFor="f-espacio" className="uppercase tracking-[0.04em]">
              espacio
            </label>
            <Dropdown
              id="f-espacio"
              labelledBy="f-espacio-label"
              value={spaceId ?? ''}
              onChange={(value) => setSpaceId(value || null)}
              options={[
                ...(spaceId === null ? [{ value: '', label: 'elegí un espacio' }] : []),
                ...admin.espacios.map((s) => ({ value: s.id, label: s.nombre })),
              ]}
            />
          </div>
        )}
        {spaceId && options.kind !== 'gone' && <KindSwitch current={kind} onChange={chooseKind} />}
        {kind === 'objetivo' && objectives && options.kind !== 'gone' && (
          <NewObjective
            key={spaceId}
            api={objectives}
            author={admin.administrador}
            onClosed={() => setClosed(true)}
          />
        )}
        {kind === 'tarea' && options.kind === 'loading' && <Notice title="Cargando…" />}
        {kind === 'tarea' && options.kind === 'failed' && <Failed onRetry={retry} />}
        {options.kind === 'gone' && (
          <Notice title="Ese espacio ya no está disponible.">
            <p className="m-0">
              {spaceId === null && admin.espacios.length > 0
                ? 'Elegí otro espacio arriba.'
                : 'Probá de nuevo en un rato.'}
            </p>
            {spaceId !== null && <RetryButton onClick={retry} />}
          </Notice>
        )}
        {kind === 'tarea' && options.kind === 'ready' && spaceId && (
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
    <div className="mx-auto flex min-h-dvh w-full min-w-0 overflow-x-clip max-w-[72rem] flex-col px-5">
      <Header
        space={open && spaceName ? `administración · ${spaceName}` : 'administración'}
        title={open ? (kind === 'objetivo' ? 'Crear objetivo' : 'Cargar tarea') : 'Leda'}
        person={open ? admin?.administrador : undefined}
      />
      <main className="flex min-w-0 flex-col gap-4 pt-4">{body}</main>
      {open && (
        <footer className="mt-auto flex justify-end pb-[22px] pt-6">
          <SignOut action={adminSignOut} onDone={() => setSignedOut(true)} />
        </footer>
      )}
    </div>
  );
}
