import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
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
    expect(screen.getByLabelText('De qué cuelga')).toHaveTextContent('Modernizar la planta');
    expect(typeShown()).toContain('hito');
    expect(screen.getByLabelText('Referente')).toHaveTextContent('Lucas');
    for (const label of ['Descripción (opcional)', 'De qué cuelga', 'Tipo', 'Referente', 'Fecha']) {
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
    expect(screen.getByLabelText('De qué cuelga')).toHaveTextContent('Línea 3 andando');
    expect(typeShown()).toBe('objetivo operativo');
  });

  it('never changes what the person chose herself, also "de ninguno" and the type', async () => {
    const { api, asked, answer } = assisted();
    open(api);
    pick('De qué cuelga', 'o-plan');
    pick('Tipo', 'hito');
    pick('De qué cuelga', '');
    tell('un plan para el año que viene');
    ask();
    expect(asked[0].padre_id).toBe('');
    await answer(proposed({ padre_id: 'o-plan', tipo: 'operativo', titulo: 'Plan del año' }));
    expect(screen.getByLabelText('De qué cuelga')).toHaveTextContent('de ninguno');
    expect(typeShown()).toBe('plan anual');
    expect(screen.getByLabelText('Nombre')).toHaveValue('Plan del año');
    // A type the person picked goes with the ask, and stays.
    pick('De qué cuelga', 'o-plan');
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

  it('corrects the spelling when leaving a text and before creating, unmarked', async () => {
    const { api, spelled, sent } = assisted({
      'tablero nuebo': 'tablero nuevo',
      'cambiar el tablero viejo x el nuebo': 'cambiar el tablero viejo x el nuevo',
    });
    open(api);
    const name = screen.getByLabelText('Nombre');
    fireEvent.change(name, { target: { value: 'tablero nuebo' } });
    fireEvent.blur(name);
    await waitFor(() => expect(name).toHaveValue('tablero nuevo'));
    expect(spelled[0]).toEqual({ titulo: 'tablero nuebo' });
    expect(markedByLeda('Nombre')).toBe(false);
    fireEvent.change(screen.getByLabelText('Descripción (opcional)'), {
      target: { value: 'cambiar el tablero viejo x el nuebo' },
    });
    pick('Referente', 'm-lucas');
    fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
    fireEvent.click(screen.getByRole('button', { name: '> confirmar' }));
    await screen.findByRole('heading', { name: 'Objetivo creado.' });
    // Only what was not checked yet, as it was.
    expect(spelled[1]).toEqual({ descripcion: 'cambiar el tablero viejo x el nuebo' });
    expect(sent[0].titulo).toBe('tablero nuevo');
    expect(sent[0].descripcion).toBe('cambiar el tablero viejo x el nuevo');
  });
});
