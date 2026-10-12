import { RotateCw } from 'lucide-react';
import { useEffect, useState } from 'react';
import {
  fetchMe,
  fetchView,
  SessionClosedError,
  type Me,
  type ViewData,
  type ViewId,
} from './api';
import { FinishedList } from './components/FinishedList';
import { Header } from './components/Header';
import { Notice } from './components/Notice';
import { SignOut } from './components/SignOut';
import { StatePanel } from './components/StatePanel';
import { TalkButton } from './components/TalkButton';
import { TaskCard } from './components/TaskCard';
import { ViewSwitch } from './components/ViewSwitch';
import { WeekStrip } from './components/WeekStrip';

type Load<T> =
  | { kind: 'loading' }
  | { kind: 'ready'; data: T }
  | { kind: 'closed' }
  | { kind: 'failed' };

const EMPTY: Record<ViewId, string> = {
  tus: 'No tenés tareas abiertas.',
  sector: 'No hay tareas abiertas en tu sector.',
  equipo: 'No hay tareas abiertas en el equipo.',
};

function failure(error: unknown): { kind: 'closed' } | { kind: 'failed' } {
  return error instanceof SessionClosedError ? { kind: 'closed' } : { kind: 'failed' };
}

/** The view in the address (`/app/?vista=sector`), if this person has it; else the first. */
function pickView(me: Me, wanted: string | null): ViewId | null {
  const allowed = me.vistas.map((v) => v.vista);
  return allowed.find((v) => v === wanted) ?? allowed[0] ?? null;
}

function viewInAddress(): string | null {
  return new URLSearchParams(window.location.search).get('vista');
}

function Retry({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex w-fit items-center gap-2 rounded-card border-hard border-line bg-card px-3 py-2 text-small text-ink shadow-hard"
    >
      <RotateCw aria-hidden="true" size={12} strokeWidth={2} />
      probar de nuevo
    </button>
  );
}

function Failed({ onRetry }: { onRetry: () => void }) {
  return (
    <Notice title="No se pudo cargar la página.">
      <p className="m-0">Probá de nuevo en un rato.</p>
      <Retry onClick={onRetry} />
    </Notice>
  );
}

function SessionClosed({ byPerson = false }: { byPerson?: boolean }) {
  return (
    <Notice title={byPerson ? 'Cerraste la sesión.' : 'La sesión está cerrada.'}>
      <p className="m-0">Para volver a ver tus tareas, pedile a Leda un enlace nuevo por Telegram.</p>
    </Notice>
  );
}

export function App() {
  const [attempt, setAttempt] = useState(0);
  const [me, setMe] = useState<Load<Me>>({ kind: 'loading' });
  const [view, setView] = useState<ViewId | null>(null);
  const [tasks, setTasks] = useState<Load<ViewData>>({ kind: 'loading' });
  const [signedOut, setSignedOut] = useState(false);

  useEffect(() => {
    const request = new AbortController();
    setMe({ kind: 'loading' });
    fetchMe(request.signal)
      .then((data) => {
        setMe({ kind: 'ready', data });
        setView((current) => pickView(data, current ?? viewInAddress()));
      })
      .catch((error: unknown) => {
        if (!request.signal.aborted) setMe(failure(error));
      });
    return () => request.abort();
  }, [attempt]);

  useEffect(() => {
    if (view === null) return;
    const request = new AbortController();
    setTasks({ kind: 'loading' });
    fetchView(view, request.signal)
      .then((data) => setTasks({ kind: 'ready', data }))
      .catch((error: unknown) => {
        if (!request.signal.aborted) setTasks(failure(error));
      });
    return () => request.abort();
  }, [view, attempt]);

  function choose(next: ViewId) {
    setView(next);
    try {
      window.history.replaceState(null, '', `?vista=${next}`);
    } catch {
      // The address is a convenience; the view already changed.
    }
  }

  const retry = () => setAttempt((n) => n + 1);
  const person = me.kind === 'ready' ? me.data : null;
  const ready = tasks.kind === 'ready' ? tasks.data : null;
  const title =
    ready?.titulo ?? person?.vistas.find((v) => v.vista === view)?.titulo ?? 'Leda';

  let body;
  if (signedOut) {
    body = <SessionClosed byPerson />;
  } else if (me.kind === 'closed' || tasks.kind === 'closed') {
    body = <SessionClosed />;
  } else if (me.kind === 'failed') {
    body = <Failed onRetry={retry} />;
  } else if (person === null || view === null) {
    body = me.kind === 'loading' ? <Notice title="Cargando…" /> : <SessionClosed />;
  } else {
    body = (
      <>
        <ViewSwitch views={person.vistas} current={view} onChange={choose} />
        {tasks.kind === 'loading' && <Notice title="Cargando…" />}
        {tasks.kind === 'failed' && <Failed onRetry={retry} />}
        {ready && (
          <>
            <StatePanel panel={ready.panel} />
            <WeekStrip days={ready.semana} tasks={ready.tareas} />
            {ready.tareas.length === 0 ? (
              <p className="m-0 pt-1 text-body text-ink-soft">{EMPTY[ready.vista] ?? EMPTY.tus}</p>
            ) : (
              <div className="flex flex-col gap-[11px] pt-0.5 text-body">
                {ready.tareas.map((task) => (
                  <TaskCard key={task.id} task={task} view={ready.vista} />
                ))}
              </div>
            )}
            <FinishedList items={ready.terminadas ?? []} view={ready.vista} />
          </>
        )}
      </>
    );
  }

  const open = !signedOut && person !== null && me.kind === 'ready' && tasks.kind !== 'closed';
  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-[32rem] flex-col px-5">
      <Header
        space={person?.espacio ?? ''}
        title={signedOut || !open ? 'Leda' : title}
        person={open ? person?.persona : undefined}
        active={open ? ready?.activas : undefined}
        today={open ? ready?.hoy : undefined}
        isoWeek={open ? ready?.semana_iso : undefined}
      />
      <main className="flex flex-col gap-3.5 pt-3.5">{body}</main>
      {open && (
        <footer className="mt-auto flex flex-col gap-3 pb-[22px] pt-5">
          <TalkButton href={person?.chat_con_leda ?? null} />
          <div className="flex justify-end">
            <SignOut onDone={() => setSignedOut(true)} />
          </div>
        </footer>
      )}
    </div>
  );
}
