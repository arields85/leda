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
  pick('Es parte de', 'o-plan');
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
    // J3-7: what each type is, in plain words with the pack's names.
    expect(screen.getByText('Plan anual: lo más grande, para qué es todo el trabajo.')).toBeInTheDocument();
    expect(offered('Es parte de')).toEqual([
      'de ninguno (es un plan anual)',
      'Modernizar la planta · plan anual · hasta 18.12',
      'Línea 3 andando · hito',
    ]);
    // Under a strategic one: a milestone or an operational one, the operational one chosen.
    pick('Es parte de', 'o-plan');
    expect(typeIsAsked()).toBe(true);
    expect(typeShown()).toBe('objetivo operativo');
    expect(offered('Tipo')).toEqual(['hito', 'objetivo operativo']);
    expect(screen.getByText('Objetivo operativo: algo concreto que hace un área.')).toBeInTheDocument();
    pick('Tipo', 'hito');
    expect(typeShown()).toBe('hito');
    expect(screen.getByText('Hito: un paso importante de un plan anual.')).toBeInTheDocument();
    // Under a milestone: operational, without asking.
    pick('Es parte de', 'o-hito');
    expect(typeIsAsked()).toBe(false);
    expect(typeShown()).toBe('objetivo operativo');
    expect(screen.getByText('Debajo de «Línea 3 andando» es objetivo operativo.')).toBeInTheDocument();
    pick('Es parte de', '');
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

// Decision 5 of the user (2026-10-14; migration 0070): an objective never falls due after the one
// it hangs from, when that one has a date. Leda stops before confirming and offers the ways out:
// another date, or "> cargarlo aparte" (to hang from the parent's own parent, or from none).
describe('an objective that falls due after its parent', () => {
  /** Options where "Modernizar la planta" (strategic, a root) is due on Friday 23.10 and, if
   * given, "Línea 3 andando" (a milestone under it) on `milestone`. */
  function dated(milestone: string | null = null, plan = '2026-10-23') {
    const options = objectiveOptions();
    return {
      ...options,
      padres: [
        { ...options.padres[0], fecha_objetivo: plan, padre_id: null },
        { ...options.padres[1], fecha_objetivo: milestone, padre_id: 'o-plan' },
      ],
    };
  }

  function openWith(api: ObjectiveApi, options = dated()) {
    render(<ObjectiveForm api={api} options={options} author="Ariel" onClosed={vi.fn()} />);
  }

  const STOP_PLAN =
    'Este objetivo vence después que «Modernizar la planta» (23.10): es parte de ese objetivo, que se demoraría.';
  const stop = () => screen.queryByRole('group', { name: 'Vence después que el objetivo del que es parte' });

  function fillLate(parent = 'o-plan') {
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Habilitar el laboratorio' } });
    pick('Es parte de', parent);
    pick('Referente', 'm-lucas');
    fireEvent.click(screen.getByRole('button', { name: 'mar 27.10' }));
  }

  it('stops before confirming and says why, with the parent by its name and day', () => {
    const { api } = door(created);
    openWith(api);
    fillLate();
    expect(stop()).toHaveTextContent(STOP_PLAN);
    expect(within(stop()!).getByRole('button', { name: '> cargarlo aparte' })).toBeInTheDocument();
    expect(preview()).toHaveTextContent('Vence después que «Modernizar la planta» (23.10).');
    expect(screen.getByRole('button', { name: '> confirmar' })).toHaveAttribute('aria-disabled', 'true');
    expect(document.getElementById('lo-que-falta-objetivo')).toHaveTextContent('Hay que corregir: fecha.');
    confirm();
    expect(api.create).not.toHaveBeenCalled();
    expect(document.getElementById('o-fecha-error')).toHaveTextContent(STOP_PLAN);
  });

  it('exit 1: another date up to the parent\'s day, and it is created where it was', async () => {
    keys('k1-0000-0000-0000-000000000000');
    const { api, sent } = door(created);
    openWith(api);
    fillLate();
    fireEvent.click(screen.getByRole('button', { name: 'vie 23.10' }));
    expect(stop()).toBeNull();
    expect(document.getElementById('o-fecha-error')).toBeNull();
    expect(screen.getByRole('button', { name: '> confirmar' })).not.toHaveAttribute('aria-disabled');
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(sent).toEqual([
      {
        titulo: 'Habilitar el laboratorio',
        descripcion: '',
        padre_id: 'o-plan',
        tipo: 'operativo',
        referente_id: 'm-lucas',
        fecha: '2026-10-23',
        clave: 'k1-0000-0000-0000-000000000000',
      },
    ]);
  });

  it('exit 2: "cargarlo aparte" from a root hangs it from none, as a strategic one', async () => {
    const { api, sent } = door(created);
    openWith(api);
    fillLate();
    pick('Tipo', 'hito');
    confirm();
    fireEvent.click(within(stop()!).getByRole('button', { name: '> cargarlo aparte' }));
    expect(screen.getByLabelText('Es parte de')).toHaveValue('');
    expect(typeShown()).toBe('plan anual');
    expect(stop()).toBeNull();
    expect(document.getElementById('o-fecha-error')).toBeNull();
    expect(preview()).toHaveTextContent('ninguno');
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(sent[0]).toMatchObject({ tipo: 'estrategico', fecha: '2026-10-27' });
    expect(sent[0]).not.toHaveProperty('padre_id');
  });

  it('exit 2 from a milestone goes next to it, and the type is offered again for the new place', async () => {
    const { api, sent } = door(created);
    openWith(api, dated('2026-10-21', '2026-12-18'));
    fillLate('o-hito');
    expect(stop()).toHaveTextContent('Este objetivo vence después que «Línea 3 andando» (21.10)');
    expect(typeIsAsked()).toBe(false);
    fireEvent.click(within(stop()!).getByRole('button', { name: '> cargarlo aparte' }));
    // Now under the strategic one: a milestone or an operational one, the operational one chosen.
    expect(screen.getByLabelText('Es parte de')).toHaveValue('o-plan');
    expect(typeIsAsked()).toBe(true);
    expect(typeShown()).toBe('objetivo operativo');
    expect(stop()).toBeNull();
    pick('Tipo', 'hito');
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(sent[0]).toMatchObject({ padre_id: 'o-plan', tipo: 'hito', fecha: '2026-10-27' });
  });

  it('when the parent\'s parent is also earlier, it stops again there, never a dead end', () => {
    openWith(door(created).api, dated('2026-10-21', '2026-10-23'));
    fillLate('o-hito');
    fireEvent.click(within(stop()!).getByRole('button', { name: '> cargarlo aparte' }));
    expect(screen.getByLabelText('Es parte de')).toHaveValue('o-plan');
    expect(stop()).toHaveTextContent(STOP_PLAN);
    fireEvent.click(within(stop()!).getByRole('button', { name: '> cargarlo aparte' }));
    expect(screen.getByLabelText('Es parte de')).toHaveValue('');
    expect(stop()).toBeNull();
  });

  it('a parent without a date sets no limit', () => {
    openWith(door(created).api, dated(null, '2026-12-18'));
    fillLate('o-hito');
    expect(stop()).toBeNull();
    expect(screen.getByRole('button', { name: '> confirmar' })).not.toHaveAttribute('aria-disabled');
  });

  it('the server refusing it, with options read earlier, lands on the date', async () => {
    const { api } = door({
      kind: 'rejected',
      errors: [
        {
          campo: 'fecha',
          motivo: 'vence_despues_del_padre',
          texto: 'Este objetivo vence después que el objetivo del que es parte, que se demoraría. Elegí una fecha hasta la de ese objetivo o cargalo aparte.',
          hasta: '2026-10-20',
        },
      ],
    });
    openWith(api, dated(null, '2026-12-18'));
    fillLate('o-hito');
    confirm();
    await screen.findByRole('alert');
    expect(document.getElementById('o-fecha-error')).toHaveTextContent('Elegí una fecha hasta la de ese objetivo');
  });
});
