import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { objectiveOptions } from '../test/adminFixtures';
import { HELP_FAILED, type HelpResult, type Spelling } from './api';
import type {
  CreateResult,
  ObjectiveApi,
  ObjectiveAssist,
  ObjectiveHelpInput,
  ObjectiveInput,
  ObjectiveProposal,
} from './objectiveApi';
import { ObjectiveForm } from './ObjectiveForm';

// Leda's help on the objective form (J3-4; ADR 0023, point 4): the same box as the task's ("Contame
// qué querés hacer y te ayudo"), with the door's own help, spelling and dictation injected. Leda
// fills only what is still empty and never what the person wrote or chose; what she proposes is
// marked until the person changes it; an answer for a form that changed or was cleared fills
// nothing.

type Answer = HelpResult<ObjectiveProposal>;

/** A door with Leda's help: each ask waits until the test answers it (`answer`); the spelling
 * corrects with `fixes` (by the text it got). */
function assisted(fixes: Record<string, string> = {}) {
  const asked: ObjectiveHelpInput[] = [];
  const spelled: Record<string, string>[] = [];
  const sent: ObjectiveInput[] = [];
  let pending: ((answer: Answer) => void) | null = null;
  const assist: ObjectiveAssist = {
    help: vi.fn((input: ObjectiveHelpInput) => {
      asked.push(input);
      return new Promise<Answer>((resolve) => {
        pending = resolve;
      });
    }),
    spell: vi.fn(async (texts: Partial<Record<'titulo' | 'descripcion', string>>): Promise<Spelling> => {
      spelled.push(texts as Record<string, string>);
      const corrected: Spelling['corrected'] = {};
      for (const [field, text] of Object.entries(texts)) {
        if (text && fixes[text]) corrected[field as 'titulo'] = { text: fixes[text] };
      }
      return { corrected, unchecked: [] };
    }),
    transcribe: vi.fn(async () => ({ kind: 'text' as const, text: 'dictado' })),
  };
  const api: ObjectiveApi = {
    options: vi.fn(async () => objectiveOptions()),
    create: vi.fn(async (input: ObjectiveInput): Promise<CreateResult> => {
      sent.push(input);
      return { kind: 'created', objectiveId: 'ob-1', repeated: false };
    }),
    assist,
  };
  async function answer(reply: Answer) {
    await act(async () => {
      pending?.(reply);
    });
  }
  return { api, asked, spelled, sent, answer };
}

const proposed = (proposal: ObjectiveProposal, extra: Partial<Extract<Answer, { kind: 'proposed' }>> = {}): Answer => ({
  kind: 'proposed',
  proposal,
  choices: [],
  notes: [],
  ...extra,
});

function open(api: ObjectiveApi) {
  render(<ObjectiveForm api={api} options={objectiveOptions()} author="Ariel" onClosed={vi.fn()} />);
}

function tell(text: string) {
  fireEvent.change(screen.getByLabelText('Contame qué querés hacer y te ayudo'), { target: { value: text } });
}

const ask = () => fireEvent.click(screen.getByRole('button', { name: '> completar con Leda' }));

/** The field block of a control, to look at its mark and its messages. */
const block = (label: string) => screen.getByLabelText(label).closest('[data-field]') as HTMLElement;
const markedByLeda = (label: string) => within(block(label)).queryByText('· propuesto por Leda') !== null;

function pick(label: string, value: string) {
  fireEvent.click(screen.getByLabelText(label));
  const option = within(screen.getByRole('listbox'))
    .getAllByRole('option')
    .find((o) => o.dataset.value === value);
  if (!option) throw new Error(`"${label}" does not offer "${value}"`);
  fireEvent.click(option);
}

const typeShown = () => document.getElementById('o-tipo')?.textContent;

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Leda's help on the objective form", () => {
  it('shows the box first in the form when the door has it, and none without it', () => {
    const { api } = assisted();
    const { unmount } = render(<ObjectiveForm api={api} options={objectiveOptions()} author="Ariel" onClosed={vi.fn()} />);
    const form = screen.getByRole('form', { name: 'Crear objetivo' });
    const fields = form.querySelectorAll('[data-field]');
    expect(within(fields[0] as HTMLElement).getByLabelText('Contame qué querés hacer y te ayudo')).toBeInTheDocument();
    unmount();
    const { assist: _, ...byHand } = api;
    open(byHand);
    expect(screen.queryByLabelText('Contame qué querés hacer y te ayudo')).toBeNull();
  });

  it('fills only what is still empty, marked as Leda\'s until the person changes it', async () => {
    const { api, asked, answer } = assisted();
    open(api);
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Tablero nuevo' } });
    tell('hay q poner el tablero nuevo en la linea 3 lo lleva lucas para el viernes');
    ask();
    expect(screen.getByRole('button', { name: 'completando…' })).toBeDisabled();
    // What the form has goes with the ask; the type only if the person chose it.
    expect(asked[0]).toEqual({
      texto: 'hay q poner el tablero nuevo en la linea 3 lo lleva lucas para el viernes',
      titulo: 'Tablero nuevo',
      descripcion: '',
      padre_id: '',
      tipo: '',
      referente_id: '',
      fecha: '',
    });
    await answer(
      proposed({
        titulo: 'Poner el tablero nuevo',
        descripcion: 'Poner el tablero nuevo en la línea 3.',
        padre_id: 'o-plan',
        tipo: 'hito',
        referente_id: 'm-lucas',
        fecha: '2026-10-16',
      }),
    );
    // What the person wrote stays hers.
    expect(screen.getByLabelText('Nombre')).toHaveValue('Tablero nuevo');
    expect(markedByLeda('Nombre')).toBe(false);
    expect(screen.getByLabelText('Descripción (opcional)')).toHaveValue('Poner el tablero nuevo en la línea 3.');
    expect(screen.getByLabelText('Es parte de')).toHaveTextContent('Modernizar la planta');
    expect(typeShown()).toContain('hito');
    expect(screen.getByLabelText('Referente')).toHaveTextContent('Lucas');
    for (const label of ['Descripción (opcional)', 'Es parte de', 'Tipo', 'Referente', 'Fecha']) {
      expect(markedByLeda(label)).toBe(true);
    }
    // Edited, the mark goes.
    fireEvent.change(screen.getByLabelText('Descripción (opcional)'), { target: { value: 'Otra cosa.' } });
    expect(markedByLeda('Descripción (opcional)')).toBe(false);
    expect(markedByLeda('Referente')).toBe(true);
  });

  it('a type that does not fit where it hangs is never taken: the one that fits is', async () => {
    const { api, answer } = assisted();
    open(api);
    tell('dentro de la linea 3 andando, capacitar a los operarios');
    ask();
    await answer(proposed({ padre_id: 'o-hito', tipo: 'hito' }));
    expect(screen.getByLabelText('Es parte de')).toHaveTextContent('Línea 3 andando');
    expect(typeShown()).toBe('objetivo operativo');
  });

  it('never changes what the person chose herself, also "de ninguno" and the type', async () => {
    const { api, asked, answer } = assisted();
    open(api);
    pick('Es parte de', 'o-plan');
    pick('Tipo', 'hito');
    pick('Es parte de', '');
    tell('un plan para el año que viene');
    ask();
    expect(asked[0].padre_id).toBe('');
    await answer(proposed({ padre_id: 'o-plan', tipo: 'operativo', titulo: 'Plan del año' }));
    expect(screen.getByLabelText('Es parte de')).toHaveTextContent('de ninguno');
    expect(typeShown()).toBe('plan anual');
    expect(screen.getByLabelText('Nombre')).toHaveValue('Plan del año');
    // A type the person picked goes with the ask, and stays.
    pick('Es parte de', 'o-plan');
    pick('Tipo', 'hito');
    tell('otro plan');
    ask();
    expect(asked[1].tipo).toBe('hito');
    await answer(proposed({ tipo: 'operativo' }));
    expect(typeShown()).toContain('hito');
  });

  it('says on its field what Leda could not complete, and offers the referentes to choose', async () => {
    const { api, answer } = assisted();
    open(api);
    tell('lo lleva el ruso');
    ask();
    await answer(
      proposed(
        {},
        {
          choices: [
            { membership_id: 'm-lucas', nombre: 'Lucas', area: 'Infraestructura, Redes' },
            { membership_id: 'm-marcos', nombre: 'Marcos', area: 'Automatización' },
          ],
          notes: [
            { campo: 'referente', motivo: 'varios', texto: 'Encontré a más de un referente para el ruso: elegí el referente.' },
            { campo: 'titulo', motivo: 'sin_proponer', texto: 'No pude proponer el nombre con lo que escribiste; contame qué se quiere lograr.' },
          ],
        },
      ),
    );
    expect(within(block('Referente')).getByText(/más de un referente/)).toBeInTheDocument();
    expect(within(block('Nombre')).getByText(/No pude proponer el nombre/)).toBeInTheDocument();
    expect(screen.getByText('No pude completar: nombre, referente.')).toBeInTheDocument();
    const choose = screen.getByRole('group', { name: 'elegí el referente' });
    fireEvent.click(within(choose).getByRole('button', { name: 'Lucas · Infraestructura, Redes' }));
    expect(screen.getByLabelText('Referente')).toHaveTextContent('Lucas');
    // Her choice, not Leda's: unmarked, and the notice on that field goes.
    expect(markedByLeda('Referente')).toBe(false);
    expect(within(block('Referente')).queryByText(/más de un referente/)).toBeNull();
    expect(screen.queryByRole('group', { name: 'elegí el referente' })).toBeNull();
  });

  it('an answer for a form that changed, or that was cleared, fills nothing', async () => {
    const { api, answer } = assisted();
    open(api);
    tell('poner el tablero nuevo');
    ask();
    tell('poner el tablero nuevo, lo lleva lucas');
    await answer(proposed({ titulo: 'Poner el tablero nuevo' }));
    expect(screen.getByLabelText('Nombre')).toHaveValue('');
    expect(screen.getByText('Cambiaste lo escrito mientras Leda completaba; tocá completar de nuevo.')).toBeInTheDocument();
    ask();
    fireEvent.click(screen.getByRole('button', { name: '> empezar de nuevo' }));
    fireEvent.click(screen.getByRole('button', { name: '> sí, borrar' }));
    await answer(proposed({ titulo: 'Poner el tablero nuevo' }));
    expect(screen.getByLabelText('Nombre')).toHaveValue('');
    expect(screen.getByLabelText('Contame qué querés hacer y te ayudo')).toHaveValue('');
  });

  it('when Leda could not complete, it says so in plain words and the form stays', async () => {
    const { api, answer } = assisted();
    open(api);
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Planta 2027' } });
    tell('la planta del año que viene');
    ask();
    await answer({ kind: 'failed', text: HELP_FAILED });
    expect(screen.getByText(HELP_FAILED)).toBeInTheDocument();
    expect(screen.getByLabelText('Nombre')).toHaveValue('Planta 2027');
  });

  it('corrects the spelling while typing and before creating, unmarked', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    try {
      const { api, spelled, sent } = assisted({
        'tablero nuebo': 'tablero nuevo',
        'cambiar el tablero viejo x el nuebo': 'cambiar el tablero viejo x el nuevo',
      });
      open(api);
      const name = screen.getByLabelText('Nombre');
      fireEvent.change(name, { target: { value: 'tablero nuebo' } });
      await pause();
      await waitFor(() => expect(name).toHaveValue('tablero nuevo'));
      expect(spelled[0]).toEqual({ titulo: 'tablero nuebo' });
      expect(markedByLeda('Nombre')).toBe(false);
      pick('Referente', 'm-lucas');
      fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
      fireEvent.change(screen.getByLabelText('Descripción (opcional)'), {
        target: { value: 'cambiar el tablero viejo x el nuebo' },
      });
      fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
      await screen.findByRole('heading', { name: 'Objetivo creado.' });
      // Only what was not checked yet, as it was.
      expect(spelled[1]).toEqual({ descripcion: 'cambiar el tablero viejo x el nuebo' });
      expect(sent[0].titulo).toBe('tablero nuevo');
      expect(sent[0].descripcion).toBe('cambiar el tablero viejo x el nuevo');
    } finally {
      vi.useRealTimers();
    }
  });
});

const pause = (ms = 1500) =>
  act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });

/** The spelling of a door that waits until the test answers each check (`answer`, by its order). */
function heldSpelling(api: ObjectiveApi) {
  const asked: Record<string, string>[] = [];
  const pending: ((spelling: Spelling) => void)[] = [];
  api.assist!.spell = vi.fn(
    (texts: Partial<Record<'titulo' | 'descripcion', string>>) =>
      new Promise<Spelling>((resolve) => {
        asked.push(texts as Record<string, string>);
        pending.push(resolve);
      }),
  );
  async function answer(i: number, corrected: Record<string, string> = {}) {
    const fixes: Spelling['corrected'] = {};
    for (const [field, text] of Object.entries(corrected)) fixes[field as 'titulo'] = { text };
    await act(async () => {
      pending[i]({ corrected: fixes, unchecked: [] });
    });
  }
  return { asked, answer };
}

// J3-4b, as the task's (J2-24, the user: "la ortografía la idea es que la corrija en la vista
// previa, sin tener que apretar confirmar"): after a pause in the typing, the preview shows the
// text corrected; the field takes it when the person leaves it, never under her cursor. The same
// rules as the task's (J2-30): an answer for a text that changed, for a form that was cleared or
// that arrives while it sends changes nothing, and never the idempotency key.
describe('the spelling of the objective while typing', () => {
  const TYPED = 'modernisar el tablero de la linea';
  const FIXED = 'modernizar el tablero de la línea';
  const name = () => screen.getByLabelText('Nombre');
  const preview = () => screen.getByRole('complementary', { name: 'Vista previa' });
  const fill = () => {
    pick('Referente', 'm-lucas');
    fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
  };
  const confirm = () => fireEvent.click(screen.getByRole('button', { name: /confirmar|probar de nuevo/ }));

  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('after a pause the preview shows the name corrected; the field takes it only when the person leaves it', async () => {
    const { api, spelled } = assisted({ [TYPED]: FIXED });
    open(api);
    name().focus();
    fireEvent.change(name(), { target: { value: TYPED } });
    await pause(1000);
    expect(spelled).toHaveLength(0);
    await pause(500);
    await waitFor(() => expect(within(preview()).getByText(FIXED)).toBeInTheDocument());
    expect(spelled).toEqual([{ titulo: TYPED }]);
    // Never under her cursor.
    expect(name()).toHaveValue(TYPED);
    fireEvent.blur(name());
    expect(name()).toHaveValue(FIXED);
    expect(markedByLeda('Nombre')).toBe(false);
    // A text already checked is not checked again.
    await pause(3000);
    expect(spelled).toHaveLength(1);
  });

  it('an answer for a text the person kept typing reaches neither the preview nor the field', async () => {
    const { api } = assisted();
    const { asked, answer } = heldSpelling(api);
    open(api);
    name().focus();
    fireEvent.change(name(), { target: { value: TYPED } });
    await pause();
    expect(asked).toEqual([{ titulo: TYPED }]);
    fireEvent.change(name(), { target: { value: `${TYPED} 3` } });
    await answer(0, { titulo: FIXED });
    expect(within(preview()).queryByText(FIXED)).toBeNull();
    fireEvent.blur(name());
    expect(name()).toHaveValue(`${TYPED} 3`);
  });

  it('confirm creates what the preview shows and does not check again what was checked', async () => {
    const { api, spelled, sent } = assisted({ [TYPED]: FIXED });
    open(api);
    fill();
    name().focus();
    fireEvent.change(name(), { target: { value: TYPED } });
    await pause();
    await waitFor(() => expect(within(preview()).getByText(FIXED)).toBeInTheDocument());
    // Still in the field: what is created is what the preview shows.
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(spelled).toHaveLength(1);
    expect(sent[0].titulo).toBe(FIXED);
  });

  it('an answer that arrives while it sends changes neither what goes nor the key', async () => {
    const { api, sent } = assisted();
    const { answer } = heldSpelling(api);
    let fail: ((error: Error) => void) | null = null;
    api.create = vi.fn(
      (input: ObjectiveInput) =>
        new Promise<CreateResult>((_resolve, reject) => {
          sent.push(input);
          fail = reject;
        }),
    );
    open(api);
    fill();
    fireEvent.change(name(), { target: { value: TYPED } });
    await pause();
    // The check of the pause is on its way; confirm checks the name on its own.
    confirm();
    await answer(1);
    await waitFor(() => expect(sent).toHaveLength(1));
    // The pause's answer arrives while it sends: nothing changes.
    await answer(0, { titulo: FIXED });
    await act(async () => {
      fail?.(new Error('sin red'));
    });
    await screen.findByText(/No se pudo crear/);
    expect(name()).toHaveValue(TYPED);
    expect(within(preview()).queryByText(FIXED)).toBeNull();
    api.create = vi.fn(async (input: ObjectiveInput): Promise<CreateResult> => {
      sent.push(input);
      return { kind: 'created', objectiveId: 'ob-1', repeated: false };
    });
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    // The retry goes with the same data and the same key.
    expect(sent[1]).toEqual(sent[0]);
  });

  // RDD warning of the J3-4 (R3-retry-spelling-key), the J2-30 rule: while the last send's outcome
  // is unknown, the spelling changes nothing, so a retry goes with the same data and the same key.
  it('after a send with no answer, the spelling changes nothing: the retry goes with the same data and key', async () => {
    const { api, sent } = assisted();
    let checks = 0;
    api.assist!.spell = vi.fn(async (texts: Partial<Record<'titulo' | 'descripcion', string>>): Promise<Spelling> => {
      checks += 1;
      // The first check (on confirm) could not be done; any later one would correct the name.
      if (checks === 1) return { corrected: {}, unchecked: ['titulo'], notice: 'No pude revisar la ortografía ahora.' };
      return { corrected: texts.titulo ? { titulo: { text: FIXED } } : {}, unchecked: [] };
    });
    let attempts = 0;
    api.create = vi.fn(async (input: ObjectiveInput): Promise<CreateResult> => {
      sent.push(input);
      attempts += 1;
      if (attempts === 1) throw new Error('sin red');
      return { kind: 'created', objectiveId: 'ob-1', repeated: false };
    });
    open(api);
    fill();
    fireEvent.change(name(), { target: { value: TYPED } });
    confirm();
    await screen.findByText(/No se pudo crear/);
    await pause(3000);
    expect(checks).toBe(1);
    expect(name()).toHaveValue(TYPED);
    confirm();
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    expect(checks).toBe(1);
    expect(sent[1]).toEqual(sent[0]);
  });

  it('an answer asked for before a start over changes nothing', async () => {
    const { api } = assisted();
    const { answer } = heldSpelling(api);
    open(api);
    fireEvent.change(name(), { target: { value: TYPED } });
    await pause();
    fireEvent.click(screen.getByRole('button', { name: '> empezar de nuevo' }));
    fireEvent.click(screen.getByRole('button', { name: '> sí, borrar' }));
    fireEvent.change(name(), { target: { value: TYPED } });
    await answer(0, { titulo: FIXED });
    expect(name()).toHaveValue(TYPED);
    expect(within(preview()).queryByText(FIXED)).toBeNull();
  });
});
