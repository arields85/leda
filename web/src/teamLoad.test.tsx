import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';
import type { Options } from './admin/api';
import { choosesReviewer, EMPTY_DRAFT, requestNote, reviewerName, toInput } from './admin/draft';
import { options } from './test/adminFixtures';
import { me, view } from './test/fixtures';

// The task load through the team's door (J4; ADR 0023, decision 3): Dirección and the area
// referentes, with the same form, the people each one may load for, who reviews (Dirección
// chooses, D3) and what a request to another area means (D14). Also what the requester sees and
// how she asks for changes, and how a referente passes a task of the sector.

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

/** Martín, the referente of Infraestructura: his own task, Lucas of his area, Marcos (the referente
 * of Automatización: a request to that area) and Ismael (a request to Dirección). */
function teamOptions(overrides: Partial<Options> = {}): Options {
  const base = options();
  return {
    ...base,
    integrantes: [
      { membership_id: 'm-ismael', nombre: 'Ismael', area_id: 'a-dir', area: 'Dirección', autoridad_final: true,
        conectado: true, revisa: { membership_id: 'm-martin', nombre: 'Martín' }, como: 'pedido_a_direccion' },
      { membership_id: 'm-lucas', nombre: 'Lucas', area_id: 'a-infra', area: 'Infraestructura', autoridad_final: false,
        conectado: true, revisa: { membership_id: 'm-martin', nombre: 'Martín' }, como: 'su_area' },
      { membership_id: 'm-marcos', nombre: 'Marcos', area_id: 'a-auto', area: 'Automatización', autoridad_final: false,
        conectado: true, revisa: { membership_id: 'm-marcos', nombre: 'Marcos' }, como: 'pedido_a_otra_area' },
    ],
    areas: [
      { id: 'a-auto', nombre: 'Automatización', referente: { membership_id: 'm-marcos', nombre: 'Marcos' } },
      { id: 'a-dir', nombre: 'Dirección', referente: { membership_id: 'm-ismael', nombre: 'Ismael' } },
      { id: 'a-infra', nombre: 'Infraestructura', referente: { membership_id: 'm-martin', nombre: 'Martín' } },
    ],
    revisores: [
      { membership_id: 'm-ismael', nombre: 'Ismael', autoridad_final: true, areas: ['Dirección'] },
      { membership_id: 'm-marcos', nombre: 'Marcos', autoridad_final: false, areas: ['Automatización'] },
      { membership_id: 'm-martin', nombre: 'Martín', autoridad_final: false, areas: ['Infraestructura'] },
    ],
    yo: { membership_id: 'm-martin', nombre: 'Martín', autoridad_final: false, elige_quien_revisa: false },
    ...overrides,
  };
}

function pick(label: string, value: string) {
  fireEvent.click(screen.getByLabelText(label));
  const option = within(screen.getByRole('listbox'))
    .getAllByRole('option')
    .find((o) => o.dataset.value === value);
  if (!option) throw new Error(`"${label}" does not offer "${value}"`);
  fireEvent.click(option);
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('the team door load form', () => {
  it('a referente loads a request to another area, without declaring who decided it', async () => {
    const calls = serve({
      'GET /app/api/yo': ok(me({ persona: 'Martín', carga_tareas: true })),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/carga/opciones': ok(teamOptions()),
      'POST /app/api/tareas/revisar': ok({ errores: [] }),
      'POST /app/api/ortografia': ok({ corregidos: {}, sin_revisar: [] }),
      'POST /app/api/tareas': { status: 201, body: { task_id: 't-1', avisos: [], repetida: false } },
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '> nueva tarea' }));
    await screen.findByRole('form', { name: 'Cargar tarea' });
    expect(screen.queryByLabelText('Quién la decidió')).toBeNull();
    // A referente does not choose who reviews it.
    expect(screen.queryByLabelText('Quién la revisa')).toBeNull();
    pick('Objetivo', 'o1');
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Colgar el módem en la pared' } });
    pick('Quién la hace', 'm-marcos');
    expect(screen.getAllByText('Es un pedido a Automatización: Marcos decide quién la hace y la revisa.')).toHaveLength(2);
    fireEvent.click(screen.getByRole('checkbox', { name: /una captura de pantalla/ }));
    fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), { target: { value: 'El módem queda colgado' } });
    const preview = screen.getByRole('complementary', { name: 'Vista previa' });
    expect(within(preview).getByText('La pide')).toBeInTheDocument();
    // The preview says what it is too, with the form's same words (J4 phone test).
    expect(
      within(preview).getByText('Es un pedido a Automatización: Marcos decide quién la hace y la revisa.'),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
    await screen.findByText('Tarea cargada.');
    // The options are read again in the background (J4 phone test: "espera a" offers it next).
    await waitFor(() => expect(calls.filter((c) => c.key === 'GET /app/api/carga/opciones')).toHaveLength(2));
    expect(screen.getByText('Tarea cargada.')).toBeInTheDocument();
    const load = calls.find((c) => c.key === 'POST /app/api/tareas');
    expect(load?.body).toMatchObject({ responsable_id: 'm-marcos', objetivo_id: 'o1', decidio_id: '' });
    expect(load?.body).not.toHaveProperty('revisa_id');
    expect(calls.some((c) => c.key.includes('/admin/'))).toBe(false);
  });

  it('a member does not see "> nueva tarea"', async () => {
    serve({ 'GET /app/api/yo': ok(me({ carga_tareas: false })), 'GET /app/api/tareas?vista=tus': ok(view()) });
    render(<App />);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    expect(screen.queryByRole('button', { name: '> nueva tarea' })).toBeNull();
  });

  it('Dirección chooses who reviews, never who does it', async () => {
    serve({
      'GET /app/api/yo': ok(me({ persona: 'Ismael', carga_tareas: true })),
      'GET /app/api/tareas?vista=tus': ok(view()),
      'GET /app/api/carga/opciones': ok(teamOptions({
        yo: { membership_id: 'm-ismael', nombre: 'Ismael', autoridad_final: true, elige_quien_revisa: true },
      })),
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '> nueva tarea' }));
    await screen.findByRole('form', { name: 'Cargar tarea' });
    pick('Quién la hace', 'm-marcos');
    fireEvent.click(screen.getByLabelText('Quién la revisa'));
    const offered = within(screen.getByRole('listbox')).getAllByRole('option').map((o) => o.dataset.value);
    expect(offered).toEqual(['', 'm-ismael', 'm-martin']);
  });
});

describe('the draft through the team door', () => {
  it('says what a request means and who reviews it', () => {
    const team = teamOptions();
    const marcos = team.integrantes[2];
    expect(requestNote(team, team.integrantes[0])).toBe('Es un pedido a Dirección: la da por cumplida quien la pide, Martín.');
    expect(requestNote(team, team.integrantes[1])).toBeNull();
    expect(reviewerName({ ...EMPTY_DRAFT, responsable_id: marcos.membership_id }, team)).toBe('Marcos');
    expect(reviewerName({ ...EMPTY_DRAFT, responsable_id: 'm-lucas', revisa_id: 'm-ismael' }, team)).toBe('Ismael');
    expect(choosesReviewer(team)).toBe(false);
    expect(choosesReviewer(options())).toBe(false);
    expect(choosesReviewer({ ...options(), revisores: team.revisores })).toBe(true);
    expect(toInput({ ...EMPTY_DRAFT, revisa_id: 'm-ismael' }, 'k')).toMatchObject({ revisa_id: 'm-ismael' });
    expect(toInput(EMPTY_DRAFT, 'k')).not.toHaveProperty('revisa_id');
  });
});

// "Lo que pedí" is a tab of its own (J4 phone test): the page opens on it from the address.
const REQUESTER_TABS = [
  { vista: 'tus' as const, titulo: 'Mis tareas' },
  { vista: 'pedidas' as const, titulo: 'Lo que pedí' },
];

describe('what the requester sees', () => {
  beforeEach(() => window.history.replaceState(null, '', '/app/?vista=pedidas'));
  afterEach(() => window.history.replaceState(null, '', '/app/'));

  it('lists what she asked and asks for changes on a finished one', async () => {
    const calls = serve({
      'GET /app/api/yo': ok(me({ persona: 'Martín', vistas: REQUESTER_TABS })),
      'GET /app/api/tareas?vista=pedidas': ok(view({
        vista: 'pedidas',
        titulo: 'Lo que pedí',
        pedidas: [
          { id: 't-modem', titulo: 'Colgar el módem en la pared', estado: 'terminada', responsable: 'Nahuel',
            area: 'Automatización', fecha_objetivo: '2026-10-16', terminada_el: '2026-10-22', puede_pedir_cambios: true },
          { id: 't-rack', titulo: 'Medir el rack', estado: 'en_curso', responsable: 'Marcos',
            area: 'Automatización', fecha_objetivo: '2026-10-30', terminada_el: null, puede_pedir_cambios: false },
        ],
      })),
      'POST /app/api/tareas/t-modem/reabrir': { status: 200, body: { task_id: 't-modem', responsable_membership_id: 'm-marcos' } },
    });
    render(<App />);
    const list = await screen.findByRole('region', { name: 'Lo que pediste' });
    expect(within(list).getByText('[TERMINADA]')).toBeInTheDocument();
    expect(within(list).getByText('[EN CURSO]')).toBeInTheDocument();
    expect(within(list).getAllByRole('button', { name: '> pedir cambios' })).toHaveLength(1);
    fireEvent.click(within(list).getByRole('button', { name: '> pedir cambios' }));
    fireEvent.change(within(list).getByLabelText('Qué hay que cambiar'), { target: { value: 'Quedó torcido' } });
    fireEvent.click(within(list).getByRole('button', { name: '> confirmar' }));
    await waitFor(() =>
      expect(calls.find((c) => c.key === 'POST /app/api/tareas/t-modem/reabrir')?.body).toEqual({ motivo: 'Quedó torcido' }),
    );
    // The view is read again.
    await waitFor(() => expect(calls.filter((c) => c.key === 'GET /app/api/tareas?vista=pedidas')).toHaveLength(2));
  });

  it('says why when the server refuses', async () => {
    serve({
      'GET /app/api/yo': ok(me({ vistas: REQUESTER_TABS })),
      'GET /app/api/tareas?vista=pedidas': ok(view({
        vista: 'pedidas',
        pedidas: [{ id: 't-modem', titulo: 'Colgar el módem', estado: 'terminada', responsable: 'Nahuel',
          area: 'Automatización', fecha_objetivo: null, terminada_el: '2026-10-22', puede_pedir_cambios: true }],
      })),
      'POST /app/api/tareas/t-modem/reabrir': {
        status: 422, body: { errores: [{ campo: 'motivo', motivo: 'falta', texto: 'Contá qué hay que cambiar.' }] },
      },
    });
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '> pedir cambios' }));
    fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Contá qué hay que cambiar.');
  });
});

describe('passing a task of the sector', () => {
  it('the referente passes it to someone of the area, who takes it by chat', async () => {
    const sector = view({
      vista: 'sector',
      titulo: 'Tu sector',
      pasar_a: [{ membership_id: 'm-nahuel', nombre: 'Nahuel', area: 'Automatización' }],
    });
    const task = sector.tareas[0];
    const calls = serve({
      'GET /app/api/yo': ok(me({ vistas: [{ vista: 'sector', titulo: 'Tu sector' }] })),
      'GET /app/api/tareas?vista=sector': ok(sector),
      [`POST /app/api/tareas/${task.id}/pase`]: ok({ pase_id: 'p-1', estado: 'esperando_que_la_tome' }),
    });
    render(<App />);
    const pass = (await screen.findAllByRole('button', { name: '> pasarla' }))[0];
    fireEvent.click(pass);
    pick('A quién se la pasás', 'm-nahuel');
    fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
    expect(await screen.findByText(/le pregunto a Nahuel si la toma/)).toBeInTheDocument();
    expect(calls.find((c) => c.key === `POST /app/api/tareas/${task.id}/pase`)?.body).toEqual({ a_membership_id: 'm-nahuel' });
  });
});
