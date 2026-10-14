import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminApp } from './admin/AdminApp';
import { App } from './App';
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
    const kinds = screen.getByRole('group', { name: 'Qué cargar' });
    expect(within(kinds).getByRole('button', { name: 'tarea' })).toHaveAttribute('aria-pressed', 'true');
    // The objective's options are read only when it is chosen.
    expect(calls.some((c) => c.key === `GET ${BASE}/opciones`)).toBe(false);
    fireEvent.click(within(kinds).getByRole('button', { name: 'objetivo' }));
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
    fireEvent.click(within(kinds).getByRole('button', { name: 'tarea' }));
    expect(await screen.findByRole('form', { name: 'Cargar tarea' })).toBeInTheDocument();
    expect(read(`GET /app/admin/api/espacios/${SPACE}/opciones`)).toBe(before + 1);
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
    const kinds = screen.getByRole('group', { name: 'Qué cargar' });
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Configurar alarmas del SCADA' } });
    fireEvent.click(within(kinds).getByRole('button', { name: 'objetivo' }));
    await screen.findByRole('form', { name: 'Crear objetivo' });
    expect(screen.queryByRole('form', { name: 'Cargar tarea' })).toBeNull();
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Planta 2027' } });
    fireEvent.click(within(kinds).getByRole('button', { name: 'tarea' }));
    const task = await screen.findByRole('form', { name: 'Cargar tarea' });
    expect(within(task).getByLabelText('Título')).toHaveValue('Configurar alarmas del SCADA');
    expect(screen.queryByRole('form', { name: 'Crear objetivo' })).toBeNull();
    // Its options are read again, in the background, without losing the draft.
    await waitFor(() =>
      expect(calls.filter((c) => c.key === `GET /app/admin/api/espacios/${SPACE}/opciones`)).toHaveLength(2),
    );
    expect(within(task).getByLabelText('Título')).toHaveValue('Configurar alarmas del SCADA');
    fireEvent.click(within(kinds).getByRole('button', { name: 'objetivo' }));
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

  it('offers "nuevo objetivo" only to Dirección', async () => {
    serve({ 'GET /app/api/yo': ok(me()), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await screen.findByText('Configurar alarmas del SCADA');
    expect(screen.queryByRole('button', { name: '> nuevo objetivo' })).toBeNull();
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
    fireEvent.click(await screen.findByRole('button', { name: '> nuevo objetivo' }));
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
    fireEvent.click(await screen.findByRole('button', { name: '> nuevo objetivo' }));
    expect(await screen.findByText('Crear objetivos le corresponde a Dirección.')).toBeInTheDocument();
  });
});
