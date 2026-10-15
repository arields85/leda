import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminApp } from './admin/AdminApp';
import { App } from './App';
import { transcribe } from './admin/api';
import { adminObjectives, teamObjectives } from './admin/objectiveApi';
import { adminMe, objectiveOptions, options, SPACE } from './test/adminFixtures';
import { me, view } from './test/fixtures';

// The objective form through each door (ADR 0023, decisions 1 and 5): the administration's, chosen
// at the top of the load area, and the team's, only for Dirección. The form itself is tested in
// `admin/ObjectiveForm.test.tsx`; here, that each door reads and writes its own addresses.

type Reply = { status: number; body?: unknown };
type Call = { key: string; body: unknown };

function serve(routes: Record<string, Reply>) {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      calls.push({ key, body: typeof init?.body === 'string' ? JSON.parse(init.body) : undefined });
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
const created = { status: 201, body: { objective_id: 'ob-1', repetida: false } };

function pick(label: string, value: string) {
  fireEvent.click(screen.getByLabelText(label));
  const option = within(screen.getByRole('listbox'))
    .getAllByRole('option')
    .find((o) => o.dataset.value === value);
  if (!option) throw new Error(`"${label}" does not offer "${value}"`);
  fireEvent.click(option);
}

function fill() {
  fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Planta 2027' } });
  pick('Referente', 'm-marcos');
  fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('the administration door', () => {
  const BASE = `/app/admin/api/espacios/${SPACE}/objetivos`;

  beforeEach(() => {
    window.history.replaceState(null, '', '/app/admin/');
  });

  it('chooses "objetivo" at the top and creates it in that space', async () => {
    vi.spyOn(crypto, 'randomUUID').mockReturnValueOnce('k1-0000-0000-0000-000000000000');
    const calls = serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [`GET /app/admin/api/espacios/${SPACE}/opciones`]: ok(options()),
      [`GET ${BASE}/opciones`]: ok(objectiveOptions()),
      [`POST ${BASE}`]: created,
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    const kinds = screen.getByRole('group', { name: 'Qué hacer' });
    expect(within(kinds).getByRole('button', { name: 'Tarea' })).toHaveAttribute('aria-pressed', 'true');
    // The objective's options are read only when it is chosen.
    expect(calls.some((c) => c.key === `GET ${BASE}/opciones`)).toBe(false);
    fireEvent.click(within(kinds).getByRole('button', { name: 'Objetivo' }));
    await screen.findByRole('form', { name: 'Crear objetivo' });
    expect(screen.queryByRole('form', { name: 'Cargar tarea' })).toBeNull();
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Crear objetivo');
    fill();
    expect(within(screen.getByRole('complementary', { name: 'Vista previa' })).getByText('Ariel')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    const post = calls.filter((c) => c.key === `POST ${BASE}`);
    expect(post).toHaveLength(1);
    expect(post[0].body).toEqual({
      titulo: 'Planta 2027',
      descripcion: '',
      tipo: 'estrategico',
      referente_id: 'm-marcos',
      fecha: '2026-10-16',
      clave: 'k1-0000-0000-0000-000000000000',
    });
    // "crear otro" reads the options again: the one just created can be a parent.
    const read = (key: string) => calls.filter((c) => c.key === key).length;
    fireEvent.click(screen.getByRole('button', { name: '> crear otro' }));
    await screen.findByRole('form', { name: 'Crear objetivo' });
    expect(read(`GET ${BASE}/opciones`)).toBe(2);
    expect(screen.getByLabelText('Nombre')).toHaveValue('');
    // Back to the task, the task form is there again, with its options read again (the new
    // objective is one a task can contribute to).
    const before = read(`GET /app/admin/api/espacios/${SPACE}/opciones`);
    fireEvent.click(within(kinds).getByRole('button', { name: 'Tarea' }));
    expect(await screen.findByRole('form', { name: 'Cargar tarea' })).toBeInTheDocument();
    expect(read(`GET /app/admin/api/espacios/${SPACE}/opciones`)).toBe(before + 1);
  });

  it("Leda's help and the spelling go to this space's administration addresses (J3-4)", async () => {
    const calls = serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [`GET /app/admin/api/espacios/${SPACE}/opciones`]: ok(options()),
      [`GET ${BASE}/opciones`]: ok(objectiveOptions()),
      [`POST ${BASE}/ayuda`]: ok({ propuesta: { titulo: 'Planta 2027' }, elegir: [], avisos: [] }),
      [`POST /app/admin/api/espacios/${SPACE}/ortografia`]: ok({ corregidos: {}, sin_revisar: [] }),
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    fireEvent.click(within(screen.getByRole('group', { name: 'Qué hacer' })).getByRole('button', { name: 'Objetivo' }));
    const form = await screen.findByRole('form', { name: 'Crear objetivo' });
    fireEvent.change(within(form).getByLabelText('Contame qué querés hacer y te ayudo'), {
      target: { value: 'la planta del 2027' },
    });
    fireEvent.click(within(form).getByRole('button', { name: '> completar con Leda' }));
    await waitFor(() => expect(within(form).getByLabelText('Nombre')).toHaveValue('Planta 2027'));
    expect(calls.filter((c) => c.key === `POST ${BASE}/ayuda`)).toHaveLength(1);
    // The task's help address is not the objective's.
    expect(calls.some((c) => c.key === `POST /app/admin/api/espacios/${SPACE}/ayuda`)).toBe(false);
    // The spelling, after a pause in the typing (J3-4b, as the task's J2-24).
    await waitFor(
      () =>
        expect(calls.find((c) => c.key === `POST /app/admin/api/espacios/${SPACE}/ortografia`)?.body).toEqual({
          titulo: 'Planta 2027',
          de: 'objetivo',
        }),
      { timeout: 3000 },
    );
  });

  it('switching between "tarea" and "objetivo" keeps what was typed in each', async () => {
    // RDD review-12308947b06404e4: the switch used to drop the other form's draft.
    const calls = serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [`GET /app/admin/api/espacios/${SPACE}/opciones`]: ok(options()),
      [`GET ${BASE}/opciones`]: ok(objectiveOptions()),
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    const kinds = screen.getByRole('group', { name: 'Qué hacer' });
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Configurar alarmas del SCADA' } });
    fireEvent.click(within(kinds).getByRole('button', { name: 'Objetivo' }));
    await screen.findByRole('form', { name: 'Crear objetivo' });
    expect(screen.queryByRole('form', { name: 'Cargar tarea' })).toBeNull();
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Planta 2027' } });
    fireEvent.click(within(kinds).getByRole('button', { name: 'Tarea' }));
    const task = await screen.findByRole('form', { name: 'Cargar tarea' });
    expect(within(task).getByLabelText('Título')).toHaveValue('Configurar alarmas del SCADA');
    expect(screen.queryByRole('form', { name: 'Crear objetivo' })).toBeNull();
    // Its options are read again, in the background, without losing the draft.
    await waitFor(() =>
      expect(calls.filter((c) => c.key === `GET /app/admin/api/espacios/${SPACE}/opciones`)).toHaveLength(2),
    );
    expect(within(task).getByLabelText('Título')).toHaveValue('Configurar alarmas del SCADA');
    fireEvent.click(within(kinds).getByRole('button', { name: 'Objetivo' }));
    const objective = await screen.findByRole('form', { name: 'Crear objetivo' });
    expect(within(objective).getByLabelText('Nombre')).toHaveValue('Planta 2027');
    // The objective's options were read once: the form stayed.
    expect(calls.filter((c) => c.key === `GET ${BASE}/opciones`)).toHaveLength(1);
  });
});

describe('the team door', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '/app/');
  });

  it('offers "> Nuevo objetivo" only to Dirección', async () => {
    serve({ 'GET /app/api/yo': ok(me()), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.queryByRole('button', { name: '> Nuevo objetivo' })).toBeNull();
  });

  it('Dirección creates an objective of her team through her own door', async () => {
    vi.spyOn(crypto, 'randomUUID').mockReturnValueOnce('k1-0000-0000-0000-000000000000');
    const calls = serve({
      'GET /app/api/yo': ok(me({ persona: 'Ismael', crea_objetivos: true })),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/objetivos/opciones': ok(objectiveOptions()),
      'POST /app/api/objetivos': created,
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '> Nuevo objetivo' }));
    await screen.findByRole('form', { name: 'Crear objetivo' });
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Nuevo objetivo');
    fill();
    expect(within(screen.getByRole('complementary', { name: 'Vista previa' })).getByText('Ismael')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(calls.filter((c) => c.key === 'POST /app/api/objetivos').map((c) => c.body)).toEqual([
      {
        titulo: 'Planta 2027',
        descripcion: '',
        tipo: 'estrategico',
        referente_id: 'm-marcos',
        fecha: '2026-10-16',
        clave: 'k1-0000-0000-0000-000000000000',
      },
    ]);
    expect(calls.some((c) => c.key.includes('/app/admin/'))).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: '> volver a las tareas' }));
    expect(await screen.findByText('Configurar alarmas del SCADA')).toBeInTheDocument();
  });

  it("Leda's help and the spelling go to the team's own addresses (J3-4)", async () => {
    const calls = serve({
      'GET /app/api/yo': ok(me({ persona: 'Ismael', crea_objetivos: true })),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/objetivos/opciones': ok(objectiveOptions()),
      'POST /app/api/objetivos/ayuda': ok({
        propuesta: { titulo: 'Planta 2027', referente_id: 'm-marcos', fecha: '2026-10-16' },
        elegir: [],
        avisos: [],
      }),
      'POST /app/api/ortografia': ok({ corregidos: {}, sin_revisar: [] }),
      'POST /app/api/objetivos': created,
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '> Nuevo objetivo' }));
    await screen.findByRole('form', { name: 'Crear objetivo' });
    fireEvent.change(screen.getByLabelText('Contame qué querés hacer y te ayudo'), {
      target: { value: 'la planta del 2027 la lleva marcos para el viernes' },
    });
    fireEvent.click(screen.getByRole('button', { name: '> completar con Leda' }));
    await waitFor(() => expect(screen.getByLabelText('Nombre')).toHaveValue('Planta 2027'));
    expect(calls.find((c) => c.key === 'POST /app/api/objetivos/ayuda')?.body).toEqual({
      texto: 'la planta del 2027 la lleva marcos para el viernes',
      titulo: '',
      descripcion: '',
      padre_id: '',
      tipo: '',
      referente_id: '',
      fecha: '',
    });
    fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(calls.find((c) => c.key === 'POST /app/api/ortografia')?.body).toEqual({
      titulo: 'Planta 2027',
      de: 'objetivo',
    });
    expect(calls.some((c) => c.key.includes('/app/admin/'))).toBe(false);
  });

  it('if the server says she is not Dirección, the page says so', async () => {
    serve({
      'GET /app/api/yo': ok(me({ crea_objetivos: true })),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/objetivos/opciones': {
        status: 403,
        body: { error: 'sin_autoridad', texto: 'Crear objetivos le corresponde a Dirección.' },
      },
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '> Nuevo objetivo' }));
    expect(await screen.findByText('Crear objetivos le corresponde a Dirección.')).toBeInTheDocument();
  });
});

// J3-4b: the dictation's instructions say what is being dictated; each objective door tells the
// server it is an objective, and the task's dictation says nothing (a task, as always).
describe('the dictation of an objective', () => {
  it('goes to each door with "de=objetivo", and the task\'s without it', async () => {
    const said = { texto: 'armar la planta nueva' };
    const calls = serve({
      [`POST /app/admin/api/espacios/${SPACE}/dictado?de=objetivo`]: ok(said),
      'POST /app/api/dictado?de=objetivo': ok(said),
      [`POST /app/admin/api/espacios/${SPACE}/dictado`]: ok(said),
    });
    const audio = new Blob(['audio'], { type: 'audio/webm' });
    expect(await adminObjectives(SPACE).assist!.transcribe(audio)).toEqual({ kind: 'text', text: said.texto });
    expect(await teamObjectives().assist!.transcribe(audio)).toEqual({ kind: 'text', text: said.texto });
    expect(await transcribe(SPACE, audio)).toEqual({ kind: 'text', text: said.texto });
    expect(calls.map((c) => c.key)).toEqual([
      `POST /app/admin/api/espacios/${SPACE}/dictado?de=objetivo`,
      'POST /app/api/dictado?de=objetivo',
      `POST /app/admin/api/espacios/${SPACE}/dictado`,
    ]);
  });
});
