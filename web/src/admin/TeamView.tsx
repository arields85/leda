import { useEffect, useState } from 'react';
import { SessionClosedError } from '../api';
import { Notice } from '../components/Notice';
import { ActivationLink } from './ActivationLink';
import { AreaEditor, type AreaWork } from './AreaEditor';
import { CREATED, SMALL } from './controls';
import { PersonEditor, type PersonWork } from './PersonEditor';
import type { Team, TeamApi, TeamArea, TeamChange, TeamPerson, TeamRead } from './teamApi';

type Load = { kind: 'loading' } | { kind: 'read'; read: TeamRead } | { kind: 'failed' };

const HEADING = 'm-0 text-mini font-bold tracking-wide text-ink-dim';

/** How each piece of a change is named; an id is not shown. */
const CHANGE_KEYS: Record<string, string> = { quien_aprueba: 'quién aprueba', area: 'área' };

/** What each kind of change is called (`cambio_del_equipo.clase`). */
const CHANGES: Record<string, string> = {
  alta: 'Alta',
  baja: 'Baja',
  reactivacion: 'Volvió al equipo',
  cambio_de_area: 'Cambio de área',
  cambio_de_rol: 'Cambio de rol',
  cambio_de_aprobador: 'Cambio de quién aprueba',
  nombrar_referente: 'Nuevo referente',
  pase_de_autoridad_final: 'Pase de la autoridad final',
  area_creada: 'Área nueva',
  area_renombrada: 'Área renombrada',
  area_archivada: 'Área archivada',
};

function openTasks(n: number): string {
  if (n === 0) return 'Sin tareas abiertas.';
  return n === 1 ? '1 tarea abierta' : `${n} tareas abiertas`;
}

/** "14.10 15:30", in this browser's clock. */
function when(at: string): string {
  const date = new Date(at);
  if (Number.isNaN(date.getTime())) return '';
  const two = (n: number) => String(n).padStart(2, '0');
  return `${two(date.getDate())}.${two(date.getMonth() + 1)} ${two(date.getHours())}:${two(date.getMinutes())}`;
}

function value(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—';
  if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') return String(v);
  return JSON.stringify(v);
}

/** One person under her area: her role, who approves her work and whether she connected Leda; to
 * someone «sin conectar», her activation link (J7-5). */
function PersonLine({ person, link }: { person: TeamPerson; link: (person: TeamPerson) => React.ReactNode }) {
  const details = [
    person.rol,
    person.autoridad_final ? 'tiene la autoridad final' : null,
    person.referente_de.length > 0 ? `referente de ${person.referente_de.join(', ')}` : null,
    person.aprobador
      ? `lo aprueba ${person.aprobador.nombre}${person.aprobador.activo ? '' : ' (ya no está)'}`
      : null,
  ].filter(Boolean);
  return (
    <li data-person={person.membership_id} className="flex min-w-0 flex-col gap-0.5">
      <span className="wrap-break-word text-ink">
        {person.nombre}
        {!person.conectado && <span className="text-ink-dim"> · «sin conectar»</span>}
      </span>
      <span className="wrap-break-word text-small text-ink-dim">└─ {details.join(' · ')}</span>
      {!person.conectado && link(person)}
    </li>
  );
}

function AreaCard({
  area,
  people,
  onWork,
  editor,
  link,
}: {
  area: TeamArea;
  people: Map<string, TeamPerson>;
  onWork: (work: AreaWork) => void;
  editor: React.ReactNode;
  link: (person: TeamPerson) => React.ReactNode;
}) {
  const members = area.personas.map((id) => people.get(id)).filter((p): p is TeamPerson => Boolean(p));
  const referente = area.referente
    ? `Referente: ${area.referente.nombre}${area.referente.activo ? '' : ' (ya no está)'}`
    : 'Sin referente: lo decide Dirección.';
  return (
    <li
      data-area={area.slug}
      className={`flex min-w-0 flex-col gap-2 rounded-card border-hard px-3 py-2.5 ${
        area.archivada ? 'border-dashed border-line-dashed' : 'border-line bg-card shadow-hard'
      }`}
    >
      <span className={`min-w-0 text-body font-bold ${area.archivada ? 'text-ink-dim' : 'text-ink'}`}>
        {area.nombre}
        {area.archivada && <span className="font-normal"> · archivada</span>}
      </span>
      <span className="flex min-w-0 flex-col gap-0.5 text-small text-ink-soft">
        <span>{referente}</span>
        {area.autoaprobacion && <span>Su trabajo se aprueba en el área.</span>}
        <span className="text-ink-dim">{openTasks(area.tareas_abiertas)}</span>
      </span>
      {members.length > 0 ? (
        <ul aria-label={`Personas de ${area.nombre}`} className="m-0 flex list-none flex-col gap-1.5 p-0 text-body">
          {members.map((person) => (
            <PersonLine key={person.membership_id} person={person} link={link} />
          ))}
        </ul>
      ) : (
        <span className="text-small text-ink-dim">Nadie en esta área.</span>
      )}
      {/* An archived area stays as it is (J7-4): it is never renamed nor deleted. */}
      {!area.archivada && !editor && (
        <span className="flex flex-wrap gap-2">
          <button type="button" className={SMALL} onClick={() => onWork({ kind: 'renombrar', area })}>
            &gt; renombrar
          </button>
          <button type="button" className={SMALL} onClick={() => onWork({ kind: 'archivar', area })}>
            &gt; archivar
          </button>
        </span>
      )}
      {editor}
    </li>
  );
}

function ChangeLine({ change }: { change: TeamChange }) {
  const keys = Array.from(
    new Set([...Object.keys(change.antes ?? {}), ...Object.keys(change.despues ?? {})]),
  ).filter((key) => !key.endsWith('_id'));
  return (
    <li data-change={change.id} className="flex min-w-0 flex-col gap-0.5 border-b border-line-soft pb-1.5">
      <span className="flex min-w-0 justify-between gap-2">
        <span className="wrap-break-word text-ink">{CHANGES[change.clase] ?? change.clase}</span>
        <span className="shrink-0 text-small text-ink-dim">{when(change.at)}</span>
      </span>
      <span className="wrap-break-word text-small text-ink-dim">
        {change.quien}
        {change.puerta === 'administracion' ? ' (administración)' : ''}
      </span>
      {keys.map((key) => (
        <span key={key} className="wrap-break-word text-small text-ink-soft">
          {CHANGE_KEYS[key] ?? key}: {change.antes ? `${value(change.antes[key])} → ` : ''}
          {change.despues ? value(change.despues[key]) : '—'}
        </span>
      ))}
    </li>
  );
}

function TeamBody({
  team,
  api,
  onChanged,
  onClosed,
}: {
  team: Team;
  api: TeamApi;
  onChanged: () => void;
  onClosed: () => void;
}) {
  const people = new Map(team.personas.map((p) => [p.membership_id, p]));
  const gone = team.personas.filter((p) => !p.activo);
  const [work, setWork] = useState<AreaWork | null>(null);
  const [personWork, setPersonWork] = useState<PersonWork | null>(null);
  const [done, setDone] = useState<string | null>(null);
  // Who was just given a place, for her link right there (J7-5).
  const [joined, setJoined] = useState<{ membershipId: string; nombre: string } | null>(null);

  // One change at a time: opening one editor closes the other.
  function open(next: AreaWork) {
    setDone(null);
    setJoined(null);
    setPersonWork(null);
    setWork(next);
  }

  function openPerson(next: PersonWork) {
    setDone(null);
    setJoined(null);
    setWork(null);
    setPersonWork(next);
  }

  const link = (person: TeamPerson) =>
    person.activo && person.membership_id !== joined?.membershipId ? (
      <ActivationLink api={api} membershipId={person.membership_id} nombre={person.nombre} onClosed={onClosed} />
    ) : null;

  const personEditor = personWork && (
    <PersonEditor
      key={personWork.kind === 'alta' ? 'alta' : `reactivar-${personWork.person.membership_id}`}
      api={api}
      team={team}
      work={personWork}
      onCancel={() => setPersonWork(null)}
      onClosed={onClosed}
      onDone={(message, membershipId, nombre) => {
        setPersonWork(null);
        setDone(message);
        setJoined(personWork.kind === 'alta' ? { membershipId, nombre } : null);
        onChanged();
      }}
    />
  );

  // One change at a time; the editor sits where the change happens.
  const editor = work && (
    <AreaEditor
      key={work.kind === 'crear' ? 'crear' : `${work.kind}-${work.area.id}`}
      api={api}
      team={team}
      work={work}
      onCancel={() => setWork(null)}
      onClosed={onClosed}
      onDone={(message) => {
        setWork(null);
        setDone(message);
        onChanged();
      }}
    />
  );
  return (
    <>
      {team.problemas.length > 0 && (
        <section aria-label="Lo que no cuadra" className="flex flex-col gap-1.5 text-body">
          <h2 className={HEADING}>LO QUE NO CUADRA</h2>
          <ul className="m-0 flex list-none flex-col gap-1 p-0">
            {team.problemas.map((problem, i) => (
              <li key={`${problem.codigo}-${i}`} data-problem={problem.codigo} className="wrap-break-word text-falta">
                {problem.mensaje}
              </li>
            ))}
          </ul>
        </section>
      )}
      <section aria-label="Áreas" className="flex flex-col gap-[11px]">
        <h2 className={HEADING}>ÁREAS</h2>
        {done && (
          <p role="status" className={`m-0 text-body font-bold ${CREATED}`}>
            {done}
          </p>
        )}
        {joined && (
          <ActivationLink api={api} membershipId={joined.membershipId} nombre={joined.nombre} onClosed={onClosed} />
        )}
        {work?.kind === 'crear' ? (
          editor
        ) : personWork?.kind === 'alta' ? (
          personEditor
        ) : (
          <span className="flex flex-wrap gap-2">
            <button type="button" className={SMALL} onClick={() => open({ kind: 'crear' })}>
              &gt; crear área
            </button>
            <button type="button" className={SMALL} onClick={() => openPerson({ kind: 'alta' })}>
              &gt; dar de alta
            </button>
          </span>
        )}
        {team.areas.length === 0 ? (
          <p className="m-0 text-body text-ink-soft">Este equipo todavía no tiene áreas.</p>
        ) : (
          <ul className="m-0 flex list-none flex-col gap-[11px] p-0">
            {team.areas.map((area) => (
              <AreaCard
                key={area.id}
                area={area}
                people={people}
                onWork={open}
                editor={work && work.kind !== 'crear' && work.area.id === area.id ? editor : null}
                link={link}
              />
            ))}
          </ul>
        )}
      </section>
      {gone.length > 0 && (
        <section aria-label="Ya no están en el equipo" className="flex flex-col gap-1.5 text-body">
          <h2 className={HEADING}>YA NO ESTÁN EN EL EQUIPO</h2>
          <ul className="m-0 flex list-none flex-col gap-1 p-0">
            {gone.map((person) => (
              <li key={person.membership_id} data-person={person.membership_id} className="flex min-w-0 flex-col gap-1.5 text-ink-dim">
                <span>
                  {person.nombre} · {person.area}
                </span>
                {personWork?.kind === 'reactivar' && personWork.person.membership_id === person.membership_id ? (
                  personEditor
                ) : (
                  <button type="button" className={SMALL} onClick={() => openPerson({ kind: 'reactivar', person })}>
                    &gt; volver a sumar
                  </button>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
      <section aria-label="Cambios del equipo" className="flex flex-col gap-1.5 text-body">
        <h2 className={HEADING}>CAMBIOS DEL EQUIPO</h2>
        {team.cambios.length === 0 ? (
          <p className="m-0 text-small text-ink-dim">Todavía no hubo cambios en el equipo.</p>
        ) : (
          <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
            {team.cambios.map((change) => (
              <ChangeLine key={change.id} change={change} />
            ))}
          </ul>
        )}
      </section>
    </>
  );
}

/** "Equipo" (J7-3): the areas with their referente and their people (role, who approves each one,
 * «sin conectar»), what does not add up, who left, and the team's changes, newest first. The same
 * view through both doors (like `NewObjective`): Dirección's own team, or any space's from the
 * administration. The areas are created, renamed and archived from here (J7-4), and people are
 * given a place, or brought back, with their activation link (J7-5), each with its preview first;
 * the other changes to the team come in the next portions. */
export function TeamView({ api, onClosed }: { api: TeamApi; onClosed: () => void }) {
  const [attempt, setAttempt] = useState(0);
  const [load, setLoad] = useState<Load>({ kind: 'loading' });

  useEffect(() => {
    const request = new AbortController();
    // Reading again after a change keeps the team on screen until the new one arrives.
    setLoad((current) => (current.kind === 'read' && current.read.kind === 'team' ? current : { kind: 'loading' }));
    api
      .read(request.signal)
      .then((read) => setLoad({ kind: 'read', read }))
      .catch((error: unknown) => {
        if (request.signal.aborted) return;
        if (error instanceof SessionClosedError) onClosed();
        else setLoad({ kind: 'failed' });
      });
    return () => request.abort();
    // `onClosed` is a callback of the page: reading again follows only the door and "probar de nuevo".
  }, [api, attempt]);

  if (load.kind === 'loading') return <Notice title="Cargando…" />;
  if (load.kind === 'failed') {
    return (
      <Notice title="No se pudo cargar el equipo.">
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
  const { read } = load;
  if (read.kind === 'denied') return <Notice title={read.texto} />;
  if (read.kind === 'gone') return <Notice title="Ese espacio ya no está disponible." />;
  return (
    <div data-testid="team" className="flex min-w-0 flex-col gap-4">
      <TeamBody
        team={read.team}
        api={api}
        onChanged={() => setAttempt((n) => n + 1)}
        onClosed={onClosed}
      />
    </div>
  );
}
