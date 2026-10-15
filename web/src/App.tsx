import { RotateCw } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import {
  fetchMe,
  fetchTaskDetail,
  fetchView,
  SessionClosedError,
  type Me,
  type TaskDetail as Detail,
  type ViewData,
  type ViewId,
} from './api';
import { SignIn } from './components/SignIn';
import { rememberedSpace, rememberSpace, spaceOfPath } from './door';
import { bindBackButton, telegramWebApp } from './telegram';
import { teamTasks } from './admin/api';
import { NewObjective } from './admin/NewObjective';
import { NewTask } from './admin/NewTask';
import { teamObjectives } from './admin/objectiveApi';
import { FinishedList } from './components/FinishedList';
import { Footer } from './components/Footer';
import { PassTask } from './components/PassTask';
import { RequestedList } from './components/RequestedList';
import { Header } from './components/Header';
import { Notice } from './components/Notice';
import { StatePanel } from './components/StatePanel';
import { TaskCard } from './components/TaskCard';
import { TaskDetail } from './components/TaskDetail';
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
  pedidas: 'No pediste nada a otra área ni a Dirección.',
};

/** Where a button of Leda's chat leads (ADR 0024, decision 2): `?vista=`, `?tarea=<id>` (that
 * task's page) or `?nueva=tarea|objetivo` (the form), read once when the page opens. */
function deepLink(search: string = window.location.search): { task: string | null; create: string | null } {
  const params = new URLSearchParams(search);
  return { task: params.get('tarea'), create: params.get('nueva') };
}

/** The team's space for the QR: the one in the address, or the last one this browser entered. */
function spaceForSignIn(): string | null {
  return spaceOfPath(window.location.pathname) ?? rememberedSpace();
}

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

/** Without a session: enter with Telegram (ADR 0024, decisions 4 and 5), never asking for a
 * link. */
function SessionClosed({ onIn }: { onIn: () => void }) {
  return <SignIn door="equipo" space={spaceForSignIn()} onIn={onIn} />;
}

export function App() {
  const [attempt, setAttempt] = useState(0);
  const [me, setMe] = useState<Load<Me>>({ kind: 'loading' });
  const [view, setView] = useState<ViewId | null>(null);
  const [tasks, setTasks] = useState<Load<ViewData>>({ kind: 'loading' });
  // Dirección creating an objective (ADR 0023, decision 1), or Dirección or a referente loading a
  // task (decision 3; J4): the form takes the page's place.
  const [creating, setCreating] = useState<'tarea' | 'objetivo' | null>(null);
  const objectives = useMemo(teamObjectives, []);
  const tasksApi = useMemo(teamTasks, []);
  // The chat's button that opened the page, followed once (ADR 0024, decision 2).
  const link = useRef(deepLink());
  const [opening, setOpening] = useState(false);
  // A task that could not be opened says so (review R3-open-task-silent-failure).
  const [unopened, setUnopened] = useState(false);
  // The detail of a task, as a view of the app (MA-3): it takes the list's place until "> volver".
  const [detail, setDetail] = useState<Detail | null>(null);

  useEffect(() => {
    const request = new AbortController();
    setMe({ kind: 'loading' });
    fetchMe(request.signal)
      .then((data) => {
        setMe({ kind: 'ready', data });
        rememberSpace(data.espacio_slug);
        setView((current) => pickView(data, current ?? viewInAddress()));
        const { create, task } = link.current;
        link.current = { create: null, task: null };
        if (create === 'tarea' && data.carga_tareas) setCreating('tarea');
        else if (create === 'objetivo' && data.crea_objetivos) setCreating('objetivo');
        if (task) void openTask(task);
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

  // Telegram's "Atrás" closes the form or the task's detail the page is showing (ADR 0024,
  // decision 10; MA-3): the same as their "> volver", never closing the Mini App.
  useEffect(
    () => bindBackButton(telegramWebApp(), creating !== null || detail !== null, () => {
      setDetail(null);
      setCreating(null);
    }),
    [creating, detail],
  );

  /** A task's detail inside the app (MA-3): the server says what this person may see of it. */
  async function openTask(taskId: string) {
    setOpening(true);
    setUnopened(false);
    try {
      const found = await fetchTaskDetail(taskId);
      if (found) setDetail(found);
      else setUnopened(true);
    } catch (error) {
      if (error instanceof SessionClosedError) setMe({ kind: 'closed' });
      else setUnopened(true);
    } finally {
      setOpening(false);
    }
  }

  function choose(next: ViewId) {
    setDetail(null);
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
  const title = creating
    ? creating === 'tarea'
      ? 'Nueva tarea'
      : 'Nuevo objetivo'
    : detail
      ? 'Tarea'
      : (ready?.titulo ?? person?.vistas.find((v) => v.vista === view)?.titulo ?? 'Leda');

  const enter = retry;
  // What stays fixed at the top of the list, under the header (MA-3: only the cards scroll): the
  // tabs, the counters and the week.
  let fixed = null;
  let body;
  if (me.kind === 'closed' || tasks.kind === 'closed') {
    body = <SessionClosed onIn={enter} />;
  } else if (me.kind === 'failed') {
    body = <Failed onRetry={retry} />;
  } else if (person === null || view === null) {
    body = me.kind === 'loading' ? <Notice title="Cargando…" /> : <SessionClosed onIn={enter} />;
  } else if (detail && !creating) {
    body = <TaskDetail detail={detail} onBack={() => setDetail(null)} />;
  } else if (creating) {
    body = (
      <>
        <div>
          <button
            type="button"
            onClick={() => {
              setCreating(null);
              // What was loaded shows in the views.
              if (creating === 'tarea') retry();
            }}
            className="rounded-card border-hard border-line-soft bg-transparent px-2.5 py-1 text-small text-ink-dim"
          >
            &gt; volver a las tareas
          </button>
        </div>
        {creating === 'tarea' ? (
          <NewTask api={tasksApi} author={person.persona} onClosed={() => setMe({ kind: 'closed' })} />
        ) : (
          <NewObjective
            api={objectives}
            author={person.persona}
            onClosed={() => setMe({ kind: 'closed' })}
            stacked
          />
        )}
      </>
    );
  } else {
    fixed = (
      <>
        <ViewSwitch views={person.vistas} current={view} onChange={choose} />
        {ready && ready.vista !== 'pedidas' && (
          <>
            <StatePanel panel={ready.panel} notStarted={ready.sin_empezar} />
            {/* On a small phone the week gives way first: the rule stays, only the cards scroll. */}
            <div className="min-h-0 shrink">
              <WeekStrip days={ready.semana} tasks={ready.tareas} />
            </div>
          </>
        )}
      </>
    );
    body = (
      <>
        {tasks.kind === 'loading' && <Notice title="Cargando…" />}
        {opening && <Notice title="Abriendo la tarea…" />}
        {unopened && (
          <Notice title="No se pudo abrir esa tarea.">
            <p className="m-0">Puede que ya no la veas, o que no haya conexión. Probá de nuevo en un rato.</p>
          </Notice>
        )}
        {tasks.kind === 'failed' && <Failed onRetry={retry} />}
        {ready && ready.vista === 'pedidas' && (
          ready.pedidas && ready.pedidas.length > 0 ? (
            <RequestedList items={ready.pedidas} onChanged={retry} onClosed={() => setMe({ kind: 'closed' })} />
          ) : (
            <p className="m-0 pt-1 text-body text-ink-soft">{EMPTY.pedidas}</p>
          )
        )}
        {ready && ready.vista !== 'pedidas' && (
          <>
            {ready.tareas.length === 0 ? (
              <p className="m-0 pt-1 text-body text-ink-soft">{EMPTY[ready.vista] ?? EMPTY.tus}</p>
            ) : (
              <div className="flex flex-col gap-[11px] pt-0.5 text-body">
                {ready.tareas.map((task) => (
                  <div key={task.id} className="flex min-w-0 flex-col gap-[11px]">
                    <TaskCard task={task} view={ready.vista} onOpen={(id) => void openTask(id)} />
                    {ready.vista === 'sector' && ready.pasar_a && (
                      <PassTask task={task} teammates={ready.pasar_a} onClosed={() => setMe({ kind: 'closed' })} />
                    )}
                  </div>
                ))}
              </div>
            )}
            <FinishedList items={ready.terminadas ?? []} view={ready.vista} />
          </>
        )}
      </>
    );
  }

  const open = person !== null && me.kind === 'ready' && tasks.kind !== 'closed';
  // One screen, no page scroll (MA-3): the header, the tabs, the counters and the week fixed at
  // the top, "> Nueva tarea" and "> Nuevo objetivo" fixed at the bottom, and only the middle (the
  // cards, or the detail or the form) scrolls. Its height leaves out the safe areas the root
  // already keeps clear (the status bar and Telegram's floating "Cerrar" and "…"). The whole width,
  // also on a computer (MA-4).
  return (
    <div className="flex h-[calc(100dvh-var(--tg-safe-top,0px)-var(--tg-safe-bottom,0px))] w-full min-w-0 flex-col overflow-hidden px-5">
      <div data-testid="fixed-top" className="flex min-w-0 shrink-0 flex-col gap-3.5">
        <Header
          space={person?.espacio ?? ''}
          title={open ? title : 'Leda'}
          person={open ? person?.persona : undefined}
          area={open ? person?.area : undefined}
        />
        {fixed}
      </div>
      <main
        data-testid="scroll"
        className="-mx-5 flex min-h-0 min-w-0 flex-1 flex-col gap-3.5 overflow-y-auto overscroll-contain px-5 pb-1 pt-3.5"
      >
        {body}
      </main>
      {open && (
        <Footer
          canLoad={Boolean(person?.carga_tareas) && creating === null}
          canCreateObjective={Boolean(person?.crea_objetivos) && creating === null}
          onNewTask={() => {
            setDetail(null);
            setCreating('tarea');
          }}
          onNewObjective={() => {
            setDetail(null);
            setCreating('objetivo');
          }}
        />
      )}
    </div>
  );
}
