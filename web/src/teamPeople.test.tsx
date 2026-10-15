import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminApp } from './admin/AdminApp';
import type { Team } from './admin/teamApi';
import { App } from './App';
import { adminMe, options, SPACE } from './test/adminFixtures';
import { me, view } from './test/fixtures';

// Giving a person a place in the team from the "Equipo" view (J7-5; ADR 0023, decision 4;
// migration 0084): name, area, role and who approves her work (by default the area's referente),
// a preview first and then the confirmation; and the activation link of whoever is «sin conectar»,
// copied and shown once. The same in both doors, each at its own address.

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
const LINK = 'https://t.me/leda_corework_bot?start=abcdefghijklmnopqrstuvwxyz012345';

function clipboard(works: boolean) {
  const writeText = works ? vi.fn().mockResolvedValue(undefined) : vi.fn().mockRejectedValue(new Error('no'));
  Object.defineProperty(navigator, 'clipboard', { value: { writeText }, configurable: true });
  return writeText;
}

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
        referente: { membership_id: 'm-marcos', nombre: 'Marcos', activo: true },
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
        autoaprobacion: false,
        personas: [],
        tareas_abiertas: 0,
      },
    ],
    personas: [
      { ...person('m-ismael', 'Ismael', 'a-auto', 'Automatización'), autoridad_final: true, aprobador: null },
      { ...person('m-marcos', 'Marcos', 'a-auto', 'Automatización'), referente_de: ['Automatización'] },
      { ...person('m-nahuel', 'Nahuel', 'a-auto', 'Automatización'), conectado: false },
      { ...person('m-ana', 'Ana', 'a-gestion', 'Gestión'), activo: false },
    ],
    roles: [
      { id: 'r-dir', slug: 'direccion', nombre: 'Dirección', autoridad_final: true, personas: 1 },
      { id: 'r-ref', slug: 'referente', nombre: 'Referente', autoridad_final: false, personas: 1 },
      { id: 'r-int', slug: 'integrante', nombre: 'Integrante', autoridad_final: false, personas: 2 },
    ],
    problemas: [],
    cambios: [],
    tipos_de_evidencia: [],
    ...overrides,
  };
}

const PREVIEW = {
  accion: 'alta',
  antes: null,
  despues: { nombre: 'Lucas Pérez', area: 'Automatización', rol: 'Integrante', quien_aprueba: 'Marcos' },
  aprobador: { membership_id: 'm-marcos', nombre: 'Marcos', por_omision: true },
  avisos: [],
  huella: HUELLA,
  problemas: [],
  problemas_nuevos: [],
};

const ISSUED = {
  membership_id: 'm-lucas',
  nombre: 'Lucas Pérez',
  enlace: LINK,
  expira_en: '2026-10-29T12:00:00+00:00',
  vence_en_dias: 14,
};

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

describe('giving a person a place', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/app/');
  });

  it('shows who approves by default, previews, confirms and offers the link right there', async () => {
    const writeText = clipboard(true);
    const calls = await openTheTeam({
      'POST /app/api/equipo/personas/revisar': ok(PREVIEW),
      'POST /app/api/equipo/personas': { status: 201, body: { membership_id: 'm-lucas', repetida: false } },
      'POST /app/api/equipo/personas/enlace': ok(ISSUED),
    });
    fireEvent.click(screen.getByRole('button', { name: '> dar de alta' }));
    const editor = within(screen.getByRole('region', { name: 'Dar de alta a una persona' }));
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Lucas Pérez' } });
    // The role most of the team has comes chosen; Dirección's is never offered.
    expect(editor.getByLabelText('Rol')).toHaveValue('r-int');
    expect(within(editor.getByLabelText('Rol')).queryByRole('option', { name: 'Dirección' })).toBeNull();
    fireEvent.change(editor.getByLabelText('Área'), { target: { value: 'a-auto' } });
    expect(within(editor.getByLabelText('Quién aprueba su trabajo')).getByRole('option', { name: 'Marcos (por omisión)' })).toBeInTheDocument();
    // Without a referente, Dirección.
    fireEvent.change(editor.getByLabelText('Área'), { target: { value: 'a-gestion' } });
    expect(within(editor.getByLabelText('Quién aprueba su trabajo')).getByRole('option', { name: 'Ismael (por omisión)' })).toBeInTheDocument();
    fireEvent.change(editor.getByLabelText('Área'), { target: { value: 'a-auto' } });
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));

    const preview = within(await screen.findByRole('region', { name: 'Vista previa' }));
    expect(preview.getByText('Marcos (por omisión)')).toBeInTheDocument();
    expect(calls.find((c) => c.key === 'POST /app/api/equipo/personas/revisar')?.body).toEqual({
      accion: 'alta',
      nombre: 'Lucas Pérez',
      area_id: 'a-auto',
      rol_id: 'r-int',
      aprobador_id: null,
    });
    fireEvent.click(preview.getByRole('button', { name: '> confirmar' }));
    expect(
      await screen.findByText('Lucas Pérez quedó en el equipo, «sin conectar» hasta que abra su enlace.'),
    ).toBeInTheDocument();
    const body = calls.find((c) => c.key === 'POST /app/api/equipo/personas')?.body as Record<string, unknown>;
    expect(body).toMatchObject({ accion: 'alta', nombre: 'Lucas Pérez', huella: HUELLA });
    expect((body.clave as string).length).toBeGreaterThanOrEqual(16);
    await waitFor(() => expect(calls.filter((c) => c.key === 'GET /app/api/equipo')).toHaveLength(2));

    const areas = within(screen.getByRole('region', { name: 'Áreas' }));
    fireEvent.click(areas.getAllByRole('button', { name: '> copiar el enlace de activación' })[0]);
    const shown = within(await screen.findByRole('status', { name: 'Enlace de activación de Lucas Pérez' }));
    expect(shown.getByText(LINK)).toBeInTheDocument();
    expect(shown.getByText('Enlace copiado.')).toBeInTheDocument();
    expect(shown.getByText('Mandáselo por donde se hablen; vence en 14 días.')).toBeInTheDocument();
    expect(writeText).toHaveBeenCalledWith(LINK);
    expect(calls.find((c) => c.key === 'POST /app/api/equipo/personas/enlace')?.body).toEqual({
      membership_id: 'm-lucas',
    });
  });

  it('a warning that does not stop it is said in the preview', async () => {
    await openTheTeam({
      'POST /app/api/equipo/personas/revisar': ok({
        ...PREVIEW,
        avisos: [{ codigo: 'mismo_nombre', mensaje: 'Ya hay alguien en el equipo que se llama Marcos.' }],
      }),
    });
    fireEvent.click(screen.getByRole('button', { name: '> dar de alta' }));
    const editor = within(screen.getByRole('region', { name: 'Dar de alta a una persona' }));
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Marcos' } });
    fireEvent.change(editor.getByLabelText('Área'), { target: { value: 'a-auto' } });
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    expect(await screen.findByText('Ya hay alguien en el equipo que se llama Marcos.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '> confirmar' })).toBeInTheDocument();
  });

  it('what the server rejects is said with its words, still editing', async () => {
    await openTheTeam({
      'POST /app/api/equipo/personas/revisar': {
        status: 422,
        body: { errores: [{ campo: 'area', motivo: 'falta', texto: 'Elegí el área.' }] },
      },
    });
    fireEvent.click(screen.getByRole('button', { name: '> dar de alta' }));
    const editor = within(screen.getByRole('region', { name: 'Dar de alta a una persona' }));
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    expect(await screen.findByText('Elegí el área.')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '> confirmar' })).toBeNull();
  });
});

describe('the activation link', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/app/');
  });

  it('a person «sin conectar» has it; when the page cannot copy, the link stays on screen', async () => {
    clipboard(false);
    await openTheTeam({
      'POST /app/api/equipo/personas/enlace': ok({ ...ISSUED, membership_id: 'm-nahuel', nombre: 'Nahuel' }),
    });
    const nahuel = screen.getByText('Nahuel').closest('li') as HTMLElement;
    const marcos = screen.getByText('Marcos', { selector: 'span' }).closest('li') as HTMLElement;
    expect(within(marcos).queryByRole('button', { name: '> copiar el enlace de activación' })).toBeNull();
    fireEvent.click(within(nahuel).getByRole('button', { name: '> copiar el enlace de activación' }));
    const shown = within(await screen.findByRole('status', { name: 'Enlace de activación de Nahuel' }));
    expect(shown.getByText('Copiá el enlace:')).toBeInTheDocument();
    expect(shown.getByText(LINK)).toBeInTheDocument();
  });

  it('says why it cannot be made', async () => {
    await openTheTeam({
      'POST /app/api/equipo/personas/enlace': {
        status: 422,
        body: {
          errores: [
            {
              campo: 'bot',
              motivo: 'sin_usuario',
              texto: 'Todavía no se puede armar el enlace: falta configurar el bot del equipo.',
            },
          ],
        },
      },
    });
    const nahuel = screen.getByText('Nahuel').closest('li') as HTMLElement;
    fireEvent.click(within(nahuel).getByRole('button', { name: '> copiar el enlace de activación' }));
    expect(
      await screen.findByText('Todavía no se puede armar el enlace: falta configurar el bot del equipo.'),
    ).toBeInTheDocument();
  });
});

describe('bringing someone back', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/app/');
  });

  it('from who left, with her membership', async () => {
    const calls = await openTheTeam({
      'POST /app/api/equipo/personas/revisar': ok({
        ...PREVIEW,
        accion: 'reactivar',
        antes: { nombre: 'Ana', area: 'Gestión', rol: 'Integrante', quien_aprueba: 'Ismael', estado: 'fuera del equipo' },
        despues: { nombre: 'Ana', area: 'Gestión', rol: 'Integrante', quien_aprueba: 'Ismael', estado: 'en el equipo' },
      }),
      'POST /app/api/equipo/personas': { status: 201, body: { membership_id: 'm-ana', repetida: false } },
    });
    const gone = within(screen.getByRole('region', { name: 'Ya no están en el equipo' }));
    fireEvent.click(gone.getByRole('button', { name: '> volver a sumar' }));
    const editor = within(screen.getByRole('region', { name: 'Volver a sumar a Ana' }));
    expect(editor.queryByLabelText('Nombre')).toBeNull();
    expect(editor.getByLabelText('Área')).toHaveValue('a-gestion');
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    const preview = within(await screen.findByRole('region', { name: 'Vista previa' }));
    expect(preview.getByText('fuera del equipo → en el equipo')).toBeInTheDocument();
    expect(calls.find((c) => c.key === 'POST /app/api/equipo/personas/revisar')?.body).toEqual({
      accion: 'reactivar',
      membership_id: 'm-ana',
      area_id: 'a-gestion',
      rol_id: 'r-int',
      aprobador_id: null,
    });
    fireEvent.click(preview.getByRole('button', { name: '> confirmar' }));
    expect(await screen.findByText('Ana volvió al equipo.')).toBeInTheDocument();
  });
});

describe('the administration door', () => {
  const BASE = `/app/admin/api/espacios/${SPACE}/equipo`;

  beforeEach(() => {
    window.history.replaceState(null, '', '/app/admin/');
  });

  it('gives a person a place and makes her link at its own address', async () => {
    clipboard(true);
    const calls = serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [`GET /app/admin/api/espacios/${SPACE}/opciones`]: ok(options()),
      [`GET ${BASE}`]: ok(team()),
      [`POST ${BASE}/personas/revisar`]: ok(PREVIEW),
      [`POST ${BASE}/personas`]: { status: 201, body: { membership_id: 'm-lucas', repetida: false } },
      [`POST ${BASE}/personas/enlace`]: ok(ISSUED),
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    fireEvent.click(within(screen.getByRole('group', { name: 'Qué hacer' })).getByRole('button', { name: 'Equipo' }));
    await screen.findByRole('region', { name: 'Áreas' });
    fireEvent.click(screen.getByRole('button', { name: '> dar de alta' }));
    const editor = within(screen.getByRole('region', { name: 'Dar de alta a una persona' }));
    fireEvent.change(editor.getByLabelText('Nombre'), { target: { value: 'Lucas Pérez' } });
    fireEvent.change(editor.getByLabelText('Área'), { target: { value: 'a-auto' } });
    fireEvent.click(editor.getByRole('button', { name: '> revisar' }));
    fireEvent.click(await screen.findByRole('button', { name: '> confirmar' }));
    await screen.findByText('Lucas Pérez quedó en el equipo, «sin conectar» hasta que abra su enlace.');
    const areas = within(screen.getByRole('region', { name: 'Áreas' }));
    fireEvent.click(areas.getAllByRole('button', { name: '> copiar el enlace de activación' })[0]);
    await screen.findByRole('status', { name: 'Enlace de activación de Lucas Pérez' });
    expect(calls.some((c) => c.key === `POST ${BASE}/personas/enlace`)).toBe(true);
    expect(calls.some((c) => c.key.startsWith('POST /app/api/'))).toBe(false);
  });
});
