import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminApp } from './admin/AdminApp';
import type { Team } from './admin/teamApi';
import { App } from './App';
import { adminMe, options, SPACE } from './test/adminFixtures';
import { me, view } from './test/fixtures';

// The areas from the "Equipo" view (J7-4; ADR 0023, decision 4; migration 0083): create, rename and
// archive, each first as a preview ("> revisar") and then confirmed with the preview's fingerprint
// and a key of its own. The same in both doors, each at its own address.

type Reply = { status: number; body?: unknown };
type Route = Reply | ((body: unknown) => Reply);
type Call = { key: string; body: unknown };

function serve(routes: Record<string, Route>) {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      const body = typeof init?.body === 'string' ? JSON.parse(init.body) : undefined;
      calls.push({ key, body });
      const route = routes[key];
      const reply = typeof route === 'function' ? route(body) : route;
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
const HUELLA = 'a'.repeat(64);

function team(overrides: Partial<Team> = {}): Team {
  const ismael = { membership_id: 'm-ismael', nombre: 'Ismael', activo: true };
  const person = (id: string, nombre: string, area_id: string, area: string) => ({
    membership_id: id,
    nombre,
    activo: true,
    conectado: true,
    area_id,
    area,
    rol_id: 'r-int',
    rol: 'Integrante',
    autoridad_final: false,
    aprobador: ismael,
    referente_de: [],
  });
  return {
    espacio: { id: SPACE, nombre: 'CoreWork' },
    areas: [
      {
        id: 'a-auto',
        slug: 'automatizacion',
        nombre: 'Automatización',
        archivada: false,
        referente: null,
        autoaprobacion: false,
        personas: ['m-ismael', 'm-marcos'],
        tareas_abiertas: 3,
      },
      {
        id: 'a-gestion',
        slug: 'gestion',
        nombre: 'Gestión',
        archivada: false,
        referente: null,
        autoaprobacion: false,
        personas: [],
        tareas_abiertas: 0,
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
      { ...person('m-ismael', 'Ismael', 'a-auto', 'Automatización'), autoridad_final: true, aprobador: null },
      person('m-marcos', 'Marcos', 'a-auto', 'Automatización'),
    ],
    roles: [],
    problemas: [],
    cambios: [],
    tipos_de_evidencia: [
      { tipo: 'captura', en_palabras: 'una captura de pantalla' },
      { tipo: 'explicacion', en_palabras: 'una explicación' },
    ],
    ...overrides,
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

const direccion = me({
  persona: 'Ismael',
  crea_objetivos: true,
  organiza_el_equipo: true,
  vistas: [{ vista: 'tus', titulo: 'Mis tareas' }],
});

async function openTheTeam(routes: Record<string, Route>) {
  const calls = serve({
    'GET /app/api/yo': ok(direccion),
    'GET /app/api/tareas?vista=tus': ok(view()),
    'GET /app/api/equipo': ok(team()),
    ...routes,
  });
  render(<App />);
  await screen.findByText('Configurar alarmas del SCADA');
  fireEvent.click(screen.getByRole('tab', { name: 'Equipo' }));
  await screen.findByRole('region', { name: 'Áreas' });
  return calls;
}

function card(nombre: string): HTMLElement {
  return within(screen.getByRole('region', { name: 'Áreas' })).getByText(nombre).closest('li') as HTMLElement;
}

describe('creating an area', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/app/');
  });

  it('previews it, then confirms it with the fingerprint and reads the team again', async () => {
    const calls = await openTheTeam({
      'POST /app/api/equipo/areas/revisar': ok({
        accion: 'crear',
        antes: null,
        despues: {
          nombre: 'Compras',
          referente: 'Marcos',
          quien_aprueba: 'su referente',
          evidencia: 'una explicación',
        },
        huella: HUELLA,
        problemas: [],
        problemas_nuevos: [],
      }),
      'POST /app/api/equipo/areas': { status: 201, body: { area_id: 'a-nueva', repetida: false } },
    });
    fireEvent.click(screen.getByRole('button', { name: '> crear área' }));
    const editor = within(screen.getByRole('region', { name: 'Crear un área' }));
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Compras' } });
    fireEvent.click(editor.getByRole('radio', { name: 'Su referente' }));
    fireEvent.change(editor.getByLabelText('Referente'), { target: { value: 'm-marcos' } });
    fireEvent.click(editor.getByRole('checkbox', { name: 'una explicación' }));
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));

    const preview = within(await screen.findByRole('region', { name: 'Vista previa' }));
    expect(preview.getByText('Quién aprueba')).toBeInTheDocument();
    expect(preview.getByText('su referente')).toBeInTheDocument();
    expect(preview.getByText('una explicación')).toBeInTheDocument();
    const revisar = calls.find((c) => c.key === 'POST /app/api/equipo/areas/revisar');
    expect(revisar?.body).toEqual({
      accion: 'crear',
      nombre: 'Compras',
      aprobacion: 'referente',
      referente_id: 'm-marcos',
      evidencia: ['explicacion'],
      sin_evidencia: false,
    });

    fireEvent.click(preview.getByRole('button', { name: '> confirmar' }));
    expect(await screen.findByText('Área creada.')).toBeInTheDocument();
    const confirmar = calls.find((c) => c.key === 'POST /app/api/equipo/areas');
    const body = confirmar?.body as Record<string, unknown>;
    expect(body).toMatchObject({ accion: 'crear', nombre: 'Compras', huella: HUELLA });
    expect(typeof body.clave).toBe('string');
    expect((body.clave as string).length).toBeGreaterThanOrEqual(16);
    await waitFor(() => expect(calls.filter((c) => c.key === 'GET /app/api/equipo')).toHaveLength(2));
  });

  it('«No pide evidencia» is chosen on purpose and leaves no type ticked', async () => {
    const calls = await openTheTeam({
      'POST /app/api/equipo/areas/revisar': {
        status: 422,
        body: { errores: [{ campo: 'nombre', motivo: 'ya_existe', texto: 'Ya hay un área con ese nombre.' }] },
      },
    });
    fireEvent.click(screen.getByRole('button', { name: '> crear área' }));
    const editor = within(screen.getByRole('region', { name: 'Crear un área' }));
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Gestión' } });
    fireEvent.click(editor.getByRole('radio', { name: 'Lo decide Dirección' }));
    fireEvent.click(editor.getByRole('checkbox', { name: 'una captura de pantalla' }));
    fireEvent.click(editor.getByRole('checkbox', { name: 'No pide evidencia' }));
    expect(editor.getByRole('checkbox', { name: 'una captura de pantalla' })).not.toBeChecked();
    // The referente is chosen only with "Su referente".
    expect(editor.queryByLabelText('Referente')).toBeNull();
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    expect(await screen.findByText('Ya hay un área con ese nombre.')).toBeInTheDocument();
    expect(calls.find((c) => c.key === 'POST /app/api/equipo/areas/revisar')?.body).toMatchObject({
      aprobacion: 'direccion',
      referente_id: null,
      evidencia: [],
      sin_evidencia: true,
    });
    // Still editing: nothing to confirm.
    expect(screen.queryByRole('button', { name: '> confirmar' })).toBeNull();
    fireEvent.click(editor.getByRole('checkbox', { name: 'una explicación' }));
    expect(editor.getByRole('checkbox', { name: 'No pide evidencia' })).not.toBeChecked();
  });

  it('when the team changed since the preview, says so and goes back to editing', async () => {
    await openTheTeam({
      'POST /app/api/equipo/areas/revisar': ok({
        accion: 'crear',
        antes: null,
        despues: { nombre: 'Compras', referente: null, quien_aprueba: 'Dirección', evidencia: 'no pide evidencia' },
        huella: HUELLA,
        problemas: [],
        problemas_nuevos: [],
      }),
      'POST /app/api/equipo/areas': {
        status: 422,
        body: {
          errores: [
            {
              campo: 'huella',
              motivo: 'el_equipo_cambio',
              texto: 'El equipo cambió desde la vista previa: revisala de nuevo.',
            },
          ],
        },
      },
    });
    fireEvent.click(screen.getByRole('button', { name: '> crear área' }));
    const editor = within(screen.getByRole('region', { name: 'Crear un área' }));
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Compras' } });
    fireEvent.click(editor.getByRole('radio', { name: 'Lo decide Dirección' }));
    fireEvent.click(editor.getByRole('checkbox', { name: 'No pide evidencia' }));
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    fireEvent.click(await screen.findByRole('button', { name: '> confirmar' }));
    expect(await screen.findByText('El equipo cambió desde la vista previa: revisala de nuevo.')).toBeInTheDocument();
    expect(screen.getByLabelText('Nombre')).toHaveValue('Compras');
  });
});

describe('renaming and archiving', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/app/');
  });

  it('renames: the preview shows the name before and after', async () => {
    const calls = await openTheTeam({
      'POST /app/api/equipo/areas/revisar': ok({
        accion: 'renombrar',
        antes: { nombre: 'Gestión' },
        despues: { nombre: 'Administración' },
        huella: HUELLA,
        problemas: [],
        problemas_nuevos: [],
      }),
      'POST /app/api/equipo/areas': { status: 201, body: { area_id: 'a-gestion', repetida: false } },
    });
    fireEvent.click(within(card('Gestión')).getByRole('button', { name: '> renombrar' }));
    const editor = within(screen.getByRole('region', { name: 'Renombrar Gestión' }));
    expect(editor.getByLabelText('Nombre')).toHaveValue('Gestión');
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Administración' } });
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    const preview = within(await screen.findByRole('region', { name: 'Vista previa' }));
    expect(preview.getByText('Gestión → Administración')).toBeInTheDocument();
    fireEvent.click(preview.getByRole('button', { name: '> confirmar' }));
    expect(await screen.findByText('Área renombrada.')).toBeInTheDocument();
    expect(calls.find((c) => c.key === 'POST /app/api/equipo/areas')?.body).toMatchObject({
      accion: 'renombrar',
      area_id: 'a-gestion',
      nombre: 'Administración',
      huella: HUELLA,
    });
  });

  it('archiving an area with people shows why it cannot', async () => {
    const calls = await openTheTeam({
      'POST /app/api/equipo/areas/revisar': {
        status: 422,
        body: {
          errores: [
            {
              campo: 'area',
              motivo: 'tiene_personas',
              texto: 'No se puede archivar: tiene 2 personas. Pasalas a otra área antes.',
            },
          ],
        },
      },
    });
    fireEvent.click(within(card('Automatización')).getByRole('button', { name: '> archivar' }));
    expect(
      await screen.findByText('No se puede archivar: tiene 2 personas. Pasalas a otra área antes.'),
    ).toBeInTheDocument();
    expect(calls.find((c) => c.key === 'POST /app/api/equipo/areas/revisar')?.body).toEqual({
      accion: 'archivar',
      area_id: 'a-auto',
    });
    expect(screen.queryByRole('button', { name: '> confirmar' })).toBeNull();
  });

  it('archives an empty area after its preview', async () => {
    const calls = await openTheTeam({
      'POST /app/api/equipo/areas/revisar': ok({
        accion: 'archivar',
        antes: { nombre: 'Gestión', estado: 'vigente' },
        despues: { nombre: 'Gestión', estado: 'archivada' },
        huella: HUELLA,
        problemas: [],
        problemas_nuevos: [],
      }),
      'POST /app/api/equipo/areas': { status: 201, body: { area_id: 'a-gestion', repetida: false } },
    });
    fireEvent.click(within(card('Gestión')).getByRole('button', { name: '> archivar' }));
    const preview = within(await screen.findByRole('region', { name: 'Vista previa' }));
    expect(preview.getByText('vigente → archivada')).toBeInTheDocument();
    fireEvent.click(preview.getByRole('button', { name: '> confirmar' }));
    expect(await screen.findByText('Área archivada.')).toBeInTheDocument();
    expect(calls.find((c) => c.key === 'POST /app/api/equipo/areas')?.body).toMatchObject({
      accion: 'archivar',
      area_id: 'a-gestion',
      huella: HUELLA,
    });
  });

  it('an archived area offers nothing to change', async () => {
    await openTheTeam({});
    expect(within(card('Depósito')).queryByRole('button')).toBeNull();
  });
});

describe('the administration door', () => {
  const BASE = `/app/admin/api/espacios/${SPACE}/equipo`;

  beforeEach(() => {
    window.history.replaceState(null, '', '/app/admin/');
  });

  it('creates an area in the chosen space, at its own address', async () => {
    const calls = serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [`GET /app/admin/api/espacios/${SPACE}/opciones`]: ok(options()),
      [`GET ${BASE}`]: ok(team()),
      [`POST ${BASE}/areas/revisar`]: ok({
        accion: 'crear',
        antes: null,
        despues: { nombre: 'Compras', referente: null, quien_aprueba: 'el área misma', evidencia: 'una explicación' },
        huella: HUELLA,
        problemas: [],
        problemas_nuevos: [],
      }),
      [`POST ${BASE}/areas`]: { status: 201, body: { area_id: 'a-nueva', repetida: false } },
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    fireEvent.click(within(screen.getByRole('group', { name: 'Qué hacer' })).getByRole('button', { name: 'Equipo' }));
    await screen.findByRole('region', { name: 'Áreas' });
    fireEvent.click(screen.getByRole('button', { name: '> crear área' }));
    const editor = within(screen.getByRole('region', { name: 'Crear un área' }));
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Compras' } });
    fireEvent.click(editor.getByRole('radio', { name: 'El área misma' }));
    fireEvent.click(editor.getByRole('checkbox', { name: 'una explicación' }));
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    fireEvent.click(await screen.findByRole('button', { name: '> confirmar' }));
    expect(await screen.findByText('Área creada.')).toBeInTheDocument();
    expect(calls.some((c) => c.key === `POST ${BASE}/areas` && (c.body as { aprobacion?: string }).aprobacion === 'autoaprobacion')).toBe(true);
    expect(calls.some((c) => c.key.startsWith('POST /app/api/'))).toBe(false);
  });
});
