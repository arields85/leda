import { fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminApp } from './admin/AdminApp';
import type { Team } from './admin/teamApi';
import { App } from './App';
import { adminMe, options, SPACE } from './test/adminFixtures';
import { me, view } from './test/fixtures';

// "Equipo" through each door (J7-3; ADR 0023, decisions 4 and 5): Dirección's own team, as one more
// tab of her views, and any space's from the administration, chosen at the top. The same view in
// both; each door reads its own address. Creating, renaming and archiving an area is in
// `teamAreas.test.tsx` (J7-4).

type Reply = { status: number; body?: unknown };

function serve(routes: Record<string, Reply>) {
  const calls: string[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      calls.push(key);
      const reply = routes[key];
      if (!reply) return new Response('{"error":"no_existe"}', { status: 404 });
      return new Response(reply.body === undefined ? null : JSON.stringify(reply.body), {
        status: reply.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }),
  );
  return calls;
}

const ok = (body: unknown) => ({ status: 200, body });

function team(overrides: Partial<Team> = {}): Team {
  const ismael = { membership_id: 'm-ismael', nombre: 'Ismael', activo: true };
  const marcos = { membership_id: 'm-marcos', nombre: 'Marcos', activo: true };
  return {
    espacio: { id: SPACE, nombre: 'CoreWork' },
    areas: [
      {
        id: 'a-auto',
        slug: 'automatizacion',
        nombre: 'Automatización',
        archivada: false,
        referente: marcos,
        autoaprobacion: false,
        personas: ['m-ismael', 'm-marcos', 'm-nahuel'],
        tareas_abiertas: 3,
      },
      {
        id: 'a-gestion',
        slug: 'gestion',
        nombre: 'Gestión',
        archivada: false,
        referente: null,
        autoaprobacion: true,
        personas: [],
        tareas_abiertas: 1,
      },
      {
        id: 'a-viejo',
        slug: 'viejo',
        nombre: 'Depósito',
        archivada: true,
        referente: null,
        autoaprobacion: false,
        personas: [],
        tareas_abiertas: 0,
      },
    ],
    personas: [
      {
        ...ismael,
        conectado: true,
        area_id: 'a-auto',
        area: 'Automatización',
        rol_id: 'r-dir',
        rol: 'Dirección',
        autoridad_final: true,
        aprobador: null,
        referente_de: [],
      },
      {
        ...marcos,
        conectado: true,
        area_id: 'a-auto',
        area: 'Automatización',
        rol_id: 'r-ref',
        rol: 'Referente',
        autoridad_final: false,
        aprobador: ismael,
        referente_de: ['Automatización'],
      },
      {
        membership_id: 'm-nahuel',
        nombre: 'Nahuel',
        activo: true,
        conectado: false,
        area_id: 'a-auto',
        area: 'Automatización',
        rol_id: 'r-int',
        rol: 'Integrante',
        autoridad_final: false,
        aprobador: marcos,
        referente_de: [],
      },
      {
        membership_id: 'm-lucas',
        nombre: 'Lucas',
        activo: false,
        conectado: true,
        area_id: 'a-auto',
        area: 'Automatización',
        rol_id: 'r-int',
        rol: 'Integrante',
        autoridad_final: false,
        aprobador: marcos,
        referente_de: [],
      },
    ],
    roles: [],
    problemas: [],
    cambios: [
      {
        id: 'c2',
        clase: 'cambio_de_rol',
        puerta: 'administracion',
        quien: 'Ariel',
        at: '2026-10-14T15:30:00Z',
        antes: { rol: 'Integrante' },
        despues: { rol: 'Referente' },
      },
      {
        id: 'c1',
        clase: 'area_creada',
        puerta: 'equipo',
        quien: 'Ismael',
        at: '2026-10-13T12:00:00Z',
        antes: null,
        despues: { nombre: 'Gestión' },
      },
    ],
    tipos_de_evidencia: [],
    ...overrides,
  };
}

/** What both doors show of the same team. */
function expectTheTeam() {
  const areas = within(screen.getByRole('region', { name: 'Áreas' }));
  const auto = areas.getByText('Automatización').closest('li') as HTMLElement;
  expect(within(auto).getByText('Referente: Marcos')).toBeInTheDocument();
  expect(within(auto).getByText('3 tareas abiertas')).toBeInTheDocument();
  const people = within(within(auto).getByRole('list', { name: 'Personas de Automatización' }));
  expect(people.getByText(/Nahuel/)).toHaveTextContent('Nahuel · «sin conectar»');
  expect(people.getByText(/Integrante · lo aprueba Marcos/)).toBeInTheDocument();
  expect(people.getByText(/Dirección · tiene la autoridad final/)).toBeInTheDocument();
  expect(people.getByText(/Referente · referente de Automatización · lo aprueba Ismael/)).toBeInTheDocument();
  // Only the people still in the team, under their area; who left goes apart.
  expect(people.queryByText(/Lucas/)).toBeNull();
  expect(within(screen.getByRole('region', { name: 'Ya no están en el equipo' })).getByText(/Lucas/)).toBeInTheDocument();
  const gestion = areas.getByText('Gestión').closest('li') as HTMLElement;
  expect(within(gestion).getByText('Sin referente: lo decide Dirección.')).toBeInTheDocument();
  expect(within(gestion).getByText('Su trabajo se aprueba en el área.')).toBeInTheDocument();
  // An archived area comes last, marked.
  const names = areas.getAllByRole('listitem').filter((li) => li.dataset.area).map((li) => li.dataset.area);
  expect(names).toEqual(['automatizacion', 'gestion', 'viejo']);
  expect(areas.getByText('Depósito').closest('li')).toHaveTextContent('Depósito · archivada');
  // The team's changes, newest first, with who and through which door.
  const changes = within(screen.getByRole('region', { name: 'Cambios del equipo' }));
  const items = changes.getAllByRole('listitem');
  expect(items[0]).toHaveTextContent('Cambio de rol');
  expect(items[0]).toHaveTextContent('Ariel (administración)');
  expect(items[0]).toHaveTextContent('rol: Integrante → Referente');
  expect(items[1]).toHaveTextContent('Área nueva');
  expect(items[1]).toHaveTextContent('nombre: Gestión');
  // Nothing to fix: no problems section. The areas change from here (J7-4) and people are given a
  // place (J7-5): an archived area offers nothing, and nobody is removed or edited yet.
  expect(screen.queryByRole('region', { name: 'Lo que no cuadra' })).toBeNull();
  expect(within(areas.getByText('Depósito').closest('li') as HTMLElement).queryByRole('button')).toBeNull();
  expect(screen.getByRole('button', { name: '> dar de alta' })).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /agregar|dar de baja|editar/i })).toBeNull();
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('the team door', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/app/');
  });

  const direccion = me({
    persona: 'Ismael',
    crea_objetivos: true,
    organiza_el_equipo: true,
    vistas: [
      { vista: 'tus', titulo: 'Mis tareas' },
      { vista: 'areas', titulo: 'Áreas' },
    ],
  });

  it('Dirección sees her team as one more tab, read from her own door', async () => {
    const calls = serve({
      'GET /app/api/yo': ok(direccion),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/equipo': ok(team()),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(calls).not.toContain('GET /app/api/equipo');
    fireEvent.click(screen.getByRole('tab', { name: 'Equipo' }));
    await screen.findByRole('region', { name: 'Áreas' });
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Equipo');
    expect(screen.getByRole('tab', { name: 'Equipo' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: 'Mis tareas' })).toHaveAttribute('aria-selected', 'false');
    expectTheTeam();
    expect(calls.some((c) => c.includes('/app/admin/'))).toBe(false);
    // Another tab goes back to the tasks.
    fireEvent.click(screen.getByRole('tab', { name: 'Mis tareas' }));
    expect(await screen.findByText('Configurar alarmas del SCADA')).toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Áreas' })).toBeNull();
  });

  it('is offered only to Dirección', async () => {
    serve({
      'GET /app/api/yo': ok(me({ vistas: [{ vista: 'tus', titulo: 'Mis tareas' }, { vista: 'sector', titulo: 'Mi área' }] })),
      'GET /app/api/tareas?vista=tus': ok(view()),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.queryByRole('tab', { name: 'Equipo' })).toBeNull();
  });

  it('says what does not add up, plainly', async () => {
    serve({
      'GET /app/api/yo': ok(direccion),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/equipo': ok(
        team({ problemas: [{ codigo: 'sin_aprobador', mensaje: 'Nadie aprueba el trabajo de Nahuel.' }] }),
      ),
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    fireEvent.click(screen.getByRole('tab', { name: 'Equipo' }));
    const problems = within(await screen.findByRole('region', { name: 'Lo que no cuadra' }));
    expect(problems.getByText('Nadie aprueba el trabajo de Nahuel.')).toHaveClass('text-falta');
  });

  it("the server's refusal shows in its own words", async () => {
    serve({
      'GET /app/api/yo': ok(direccion),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/equipo': {
        status: 403,
        body: { error: 'sin_autoridad', texto: 'Organizar el equipo le corresponde a Dirección.' },
      },
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    fireEvent.click(screen.getByRole('tab', { name: 'Equipo' }));
    expect(await screen.findByText('Organizar el equipo le corresponde a Dirección.')).toBeInTheDocument();
  });

  it('a closed session closes the page', async () => {
    serve({
      'GET /app/api/yo': ok(direccion),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/equipo': { status: 401, body: { error: 'sin_sesion' } },
    });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    fireEvent.click(screen.getByRole('tab', { name: 'Equipo' }));
    await screen.findByRole('heading', { level: 1, name: 'Leda' });
    expect(screen.queryByRole('tab', { name: 'Equipo' })).toBeNull();
  });
});

describe('the administration door', () => {
  const BASE = `/app/admin/api/espacios/${SPACE}/equipo`;

  beforeEach(() => {
    window.history.replaceState(null, '', '/app/admin/');
  });

  it('chooses "Equipo" at the top and sees that space\'s team', async () => {
    const calls = serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [`GET /app/admin/api/espacios/${SPACE}/opciones`]: ok(options()),
      [`GET ${BASE}`]: ok(team()),
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    expect(calls).not.toContain(`GET ${BASE}`);
    const kinds = screen.getByRole('group', { name: 'Qué hacer' });
    fireEvent.click(within(kinds).getByRole('button', { name: 'Equipo' }));
    await screen.findByRole('region', { name: 'Áreas' });
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Equipo');
    expect(screen.queryByRole('form', { name: 'Cargar tarea' })).toBeNull();
    expectTheTeam();
    // Back to the task, the form is there again.
    fireEvent.click(within(kinds).getByRole('button', { name: 'Tarea' }));
    expect(await screen.findByRole('form', { name: 'Cargar tarea' })).toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Áreas' })).toBeNull();
  });

  it('a space that is gone says so', async () => {
    serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [`GET /app/admin/api/espacios/${SPACE}/opciones`]: ok(options()),
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    fireEvent.click(within(screen.getByRole('group', { name: 'Qué hacer' })).getByRole('button', { name: 'Equipo' }));
    expect(await screen.findByText('Ese espacio ya no está disponible.')).toBeInTheDocument();
  });
});
