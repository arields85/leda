import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { RequestError, SessionClosedError } from '../api';
import { objectiveOptions } from '../test/adminFixtures';
import type { CreateResult, ObjectiveApi, ObjectiveInput } from './objectiveApi';
import { ObjectiveForm } from './ObjectiveForm';

type Reply = CreateResult | 'network' | 'closed';

/** A door that answers each creation with its replies in order (the last one repeats). */
function door(...replies: Reply[]) {
  const sent: ObjectiveInput[] = [];
  const api: ObjectiveApi = {
    options: vi.fn(async () => objectiveOptions()),
    create: vi.fn(async (input: ObjectiveInput) => {
      sent.push(input);
      const reply = replies[Math.min(sent.length, replies.length) - 1];
      if (reply === 'network') throw new RequestError(0);
      if (reply === 'closed') throw new SessionClosedError();
      return reply;
    }),
  };
  return { api, sent };
}

const created: CreateResult = { kind: 'created', objectiveId: 'ob-1', repeated: false };

function keys(...values: string[]) {
  const spy = vi.spyOn(crypto, 'randomUUID');
  for (const v of values) spy.mockReturnValueOnce(v as `${string}-${string}-${string}-${string}-${string}`);
  return spy;
}

function open(api: ObjectiveApi, onClosed = vi.fn()) {
  render(<ObjectiveForm api={api} options={objectiveOptions()} author="Ariel" onClosed={onClosed} />);
  return onClosed;
}

/** Picks the option with that value from a field's list, as a person does. */
function pick(label: string, value: string) {
  fireEvent.click(screen.getByLabelText(label));
  const option = within(screen.getByRole('listbox'))
    .getAllByRole('option')
    .find((o) => o.dataset.value === value);
  if (!option) throw new Error(`"${label}" does not offer "${value}"`);
  fireEvent.click(option);
}

function offered(label: string): string[] {
  fireEvent.click(screen.getByLabelText(label));
  const list = screen.getByRole('listbox');
  const names = within(list).getAllByRole('option').map((o) => o.textContent ?? '');
  fireEvent.keyDown(list, { key: 'Escape' });
  return names;
}

/** The type as the form shows it: the chosen one of its list, or the only one, said. */
const typeShown = () => document.getElementById('o-tipo')?.textContent;
const typeIsAsked = () => document.getElementById('o-tipo')?.tagName === 'BUTTON';

function fill() {
  fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Tablero nuevo de la línea 3' } });
  pick('De qué cuelga', 'o-plan');
  pick('Referente', 'm-lucas');
  fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
}

const confirm = () => fireEvent.click(screen.getByRole('button', { name: /confirmar|probar de nuevo/ }));
const preview = () => screen.getByRole('complementary', { name: 'Vista previa' });

afterEach(() => {
  vi.restoreAllMocks();
});

describe('ObjectiveForm', () => {
  it('chooses the type by what it hangs from, with the pack names', () => {
    open(door(created).api);
    // No parent: strategic, without asking.
    expect(typeIsAsked()).toBe(false);
    expect(typeShown()).toBe('plan anual');
    expect(screen.getByText('Sin un objetivo arriba, es plan anual.')).toBeInTheDocument();
    expect(offered('De qué cuelga')).toEqual([
      'de ninguno',
      'Modernizar la planta · plan anual · hasta 18.12',
      'Línea 3 andando · hito',
    ]);
    // Under a strategic one: a milestone or an operational one, the operational one chosen.
    pick('De qué cuelga', 'o-plan');
    expect(typeIsAsked()).toBe(true);
    expect(typeShown()).toBe('objetivo operativo');
    expect(offered('Tipo')).toEqual(['hito', 'objetivo operativo']);
    pick('Tipo', 'hito');
    expect(typeShown()).toBe('hito');
    // Under a milestone: operational, without asking.
    pick('De qué cuelga', 'o-hito');
    expect(typeIsAsked()).toBe(false);
    expect(typeShown()).toBe('objetivo operativo');
    expect(screen.getByText('Debajo de «Línea 3 andando» es objetivo operativo.')).toBeInTheDocument();
    pick('De qué cuelga', '');
    expect(typeShown()).toBe('plan anual');
  });

  it('offers only the area referentes, with their areas', () => {
    open(door(created).api);
    expect(offered('Referente')).toEqual([
      'elegí a una persona',
      'Marcos · Automatización',
      'Lucas · Infraestructura, Redes',
    ]);
  });

  it('says what is missing from the start, and a tap on confirm sends nothing', () => {
    const { api } = door(created);
    open(api);
    const summary = document.getElementById('lo-que-falta-objetivo')!;
    expect(summary).toHaveTextContent('Falta completar: nombre, referente, fecha.');
    expect(screen.getByRole('button', { name: '> confirmar' })).toHaveAttribute('aria-disabled', 'true');
    confirm();
    expect(api.create).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('No se creó: hay que corregir lo marcado.');
    expect(document.getElementById('o-titulo-error')).toHaveTextContent('Falta el nombre del objetivo.');
    expect(document.getElementById('o-referente-error')).toHaveTextContent('Elegí quién es el referente.');
    expect(document.getElementById('o-fecha-error')).toHaveTextContent('Elegí la fecha.');
    // Filling a field takes its message away.
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Algo' } });
    expect(document.getElementById('o-titulo-error')).toBeNull();
  });

  it('counts the name and the description as the server does', () => {
    open(door(created).api);
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'x'.repeat(201) } });
    expect(screen.getByText('201/200 · sobran 1')).toBeInTheDocument();
    expect(document.getElementById('lo-que-falta-objetivo')).toHaveTextContent('Hay que corregir: nombre.');
    fireEvent.change(screen.getByLabelText('Descripción (opcional)'), { target: { value: '  breve  ' } });
    expect(screen.getByText('5/800')).toBeInTheDocument();
  });

  it('sends exactly what the preview shows, with one key', async () => {
    keys('k1');
    const { api, sent } = door(created);
    open(api);
    fill();
    fireEvent.change(screen.getByLabelText('Descripción (opcional)'), { target: { value: 'Con el PLC nuevo' } });
    const shown = within(preview());
    expect(shown.getByText('Tablero nuevo de la línea 3')).toBeInTheDocument();
    expect(shown.getByText('objetivo operativo')).toBeInTheDocument();
    expect(shown.getByText('Modernizar la planta · plan anual')).toBeInTheDocument();
    expect(shown.getByText('Lucas · Infraestructura, Redes')).toBeInTheDocument();
    expect(shown.getByText('vie 16.10')).toBeInTheDocument();
    expect(shown.getByText('Con el PLC nuevo')).toBeInTheDocument();
    expect(shown.getByText('Ariel')).toBeInTheDocument();
    confirm();
    expect(await screen.findByRole('heading', { name: 'Objetivo creado.' })).toBeInTheDocument();
    expect(sent).toEqual([
      {
        titulo: 'Tablero nuevo de la línea 3',
        descripcion: 'Con el PLC nuevo',
        padre_id: 'o-plan',
        tipo: 'operativo',
        referente_id: 'm-lucas',
        fecha: '2026-10-16',
        clave: 'k1',
      },
    ]);
  });

  it('without a parent it sends none', async () => {
    keys('k1');
    const { api, sent } = door(created);
    open(api);
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Planta 2027' } });
    pick('Referente', 'm-marcos');
    fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(sent[0]).not.toHaveProperty('padre_id');
    expect(sent[0].tipo).toBe('estrategico');
  });

  it('shows "cargando…" and locks the form while it sends', async () => {
    let answer: (r: CreateResult) => void = () => {};
    const { api } = door(created);
    api.create = vi.fn(() => new Promise<CreateResult>((resolve) => (answer = resolve)));
    open(api);
    fill();
    confirm();
    expect(screen.getByRole('button', { name: 'cargando…' })).toBeDisabled();
    expect(screen.getByLabelText('Nombre')).toBeDisabled();
    answer(created);
    expect(await screen.findByRole('heading', { name: 'Objetivo creado.' })).toBeInTheDocument();
  });

  it('after an answer that never came, a retry goes with the same key, even with other data', async () => {
    keys('k1', 'k2');
    const { api, sent } = door('network', created);
    open(api);
    fill();
    confirm();
    expect(await screen.findByText(/No se pudo crear: no llegó la respuesta/)).toBeInTheDocument();
    expect(screen.getByLabelText('Nombre')).toHaveValue('Tablero nuevo de la línea 3');
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Tablero nuevo de la línea 3 (bis)' } });
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(sent.map((s) => s.clave)).toEqual(['k1', 'k1']);
  });

  it('a refusal creates nothing: the next attempt with other data takes a new key', async () => {
    keys('k1', 'k2');
    const refused: CreateResult = {
      kind: 'rejected',
      errors: [
        {
          campo: 'referente',
          motivo: 'no_es_referente_de_un_area',
          texto: 'El referente tiene que ser el referente de un área del equipo.',
        },
        { campo: 'fecha', motivo: 'no_es_dia_habil', texto: 'Ese día no es hábil en este espacio.' },
      ],
    };
    const { api, sent } = door(refused, created);
    open(api);
    fill();
    confirm();
    // The server's words, each in its field.
    expect(await screen.findByText('El referente tiene que ser el referente de un área del equipo.')).toBeInTheDocument();
    expect(document.getElementById('o-referente-error')).toHaveTextContent(
      'El referente tiene que ser el referente de un área del equipo.',
    );
    expect(document.getElementById('o-fecha-error')).toHaveTextContent('Ese día no es hábil en este espacio.');
    expect(document.getElementById('lo-que-falta-objetivo')).toHaveTextContent('Hay que corregir: referente, fecha.');
    pick('Referente', 'm-marcos');
    fireEvent.click(screen.getByRole('button', { name: 'lun 19.10' }));
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(sent.map((s) => s.clave)).toEqual(['k1', 'k2']);
  });

  it('only Dirección creates: the refusal is said, not lost', async () => {
    const { api } = door({
      kind: 'rejected',
      errors: [{ campo: 'sesion', motivo: 'sin_autoridad', texto: 'Crear objetivos le corresponde a Dirección.' }],
    });
    open(api);
    fill();
    confirm();
    expect(await screen.findByText('Crear objetivos le corresponde a Dirección.')).toBeInTheDocument();
  });

  it('a closed session goes to the page', async () => {
    const { api } = door('closed');
    const onClosed = open(api);
    fill();
    confirm();
    await waitFor(() => expect(onClosed).toHaveBeenCalled());
  });

  it('starts over after asking, back to the first state', () => {
    open(door(created).api);
    expect(screen.queryByRole('button', { name: '> empezar de nuevo' })).toBeNull();
    fill();
    fireEvent.click(screen.getByRole('button', { name: '> empezar de nuevo' }));
    fireEvent.click(screen.getByRole('button', { name: '> no' }));
    expect(screen.getByLabelText('Nombre')).toHaveValue('Tablero nuevo de la línea 3');
    fireEvent.click(screen.getByRole('button', { name: '> empezar de nuevo' }));
    fireEvent.click(screen.getByRole('button', { name: '> sí, borrar' }));
    expect(screen.getByLabelText('Nombre')).toHaveValue('');
    expect(typeShown()).toBe('plan anual');
    expect(screen.getByLabelText('Referente')).toHaveTextContent('elegí a una persona');
    expect(screen.queryByRole('button', { name: '> empezar de nuevo' })).toBeNull();
  });

  it('after creating, "crear otro" opens an empty form with a new key', async () => {
    keys('k1', 'k2');
    const { api, sent } = door(created);
    open(api);
    fill();
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    fireEvent.click(screen.getByRole('button', { name: '> crear otro' }));
    expect(screen.getByLabelText('Nombre')).toHaveValue('');
    fill();
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(sent.map((s) => s.clave)).toEqual(['k1', 'k2']);
  });
});
