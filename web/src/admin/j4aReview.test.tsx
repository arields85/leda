import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { RequestError } from '../api';
import { adminMe, options, SPACE } from '../test/adminFixtures';
import { AdminApp } from './AdminApp';
import { loadTask, loadTaskAt, NOT_LOADING } from './api';
import { EMPTY_DRAFT } from './draft';
import { noParentLabel, withArticle } from './objectiveDraft';

// The review of the J4a (warnings R3-admin-403-reworded, R3-stale-decider and
// R3-article-heuristic).

function answer(status: number, body?: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => new Response(body === undefined ? null : JSON.stringify(body), { status })),
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('a 403 when loading a task', () => {
  it("is the server's refusal only when it says the person may not load", async () => {
    answer(403, { error: 'sin_autoridad', texto: NOT_LOADING });
    await expect(loadTaskAt('/app/api/tareas', { ...EMPTY_DRAFT, clave: 'k' })).resolves.toEqual({
      kind: 'rejected',
      errors: [{ campo: 'sesion', motivo: 'sin_autoridad', texto: NOT_LOADING }],
    });
  });

  it('any other 403 (another site, at the administration door) is a failure, never "only Dirección loads"', async () => {
    answer(403, { error: 'origen_no_verificado' });
    await expect(loadTask(SPACE, { ...EMPTY_DRAFT, clave: 'k' })).rejects.toEqual(new RequestError(403));
    answer(403);
    await expect(loadTaskAt('/app/api/tareas', { ...EMPTY_DRAFT, clave: 'k' })).rejects.toEqual(new RequestError(403));
  });
});

describe('who decided, when who does it changes', () => {
  const OPTIONS = `GET /app/admin/api/espacios/${SPACE}/opciones`;

  beforeEach(() => {
    window.history.replaceState(null, '', '/app/admin/');
    const withAreas = options({
      areas: [
        { id: 'a-dir', nombre: 'Dirección', referente: { membership_id: 'm-ismael', nombre: 'Ismael' } },
        { id: 'a-auto', nombre: 'Automatización', referente: { membership_id: 'm-marcos', nombre: 'Marcos' } },
        { id: 'a-infra', nombre: 'Infraestructura', referente: { membership_id: 'm-lucas', nombre: 'Lucas' } },
      ],
    });
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const key = `${init?.method ?? 'GET'} ${url}`;
        const body = key === 'GET /app/admin/api/yo' ? adminMe() : key === OPTIONS ? withAreas : null;
        return body
          ? new Response(JSON.stringify(body), { status: 200 })
          : new Response('{"error":"no_existe"}', { status: 404 });
      }),
    );
  });

  function pick(label: string, value: string) {
    fireEvent.click(screen.getByLabelText(label));
    const option = within(screen.getByRole('listbox'))
      .getAllByRole('option')
      .find((o) => o.dataset.value === value);
    if (!option) throw new Error(`"${label}" does not offer "${value}"`);
    fireEvent.click(option);
  }

  /** What the preview says under "La decidió": what would be sent. */
  const decided = () =>
    within(screen.getByRole('complementary', { name: 'Vista previa' })).getByText('La decidió').nextElementSibling
      ?.textContent;

  it('a decider who may not decide for the new person is cleared; one who still may, stays', async () => {
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    pick('Quién la hace', 'm-marcos');
    pick('Quién la decidió', 'm-marcos');
    expect(decided()).toBe('Marcos');
    // Lucas is in Infraestructura: Marcos is not its referente (D10), so he no longer decided.
    pick('Quién la hace', 'm-lucas');
    expect(decided()).toBe('—');
    pick('Quién la decidió', 'm-ismael');
    // Dirección may decide for anyone: it stays.
    pick('Quién la hace', 'm-marcos');
    expect(decided()).toBe('Ismael');
  });
});

describe('the article of a level name', () => {
  it.each([
    ['objetivo general', 'un objetivo general'],
    ['etapa', 'una etapa'],
    ['campaña', 'una campaña'],
    ['intervención', 'una intervención'],
    ['orden de trabajo', 'una orden de trabajo'],
    ['plan anual', 'un plan anual'],
    ['programa', 'un programa'],
    ['sistema', 'un sistema'],
    ['hito', 'un hito'],
    ['paso', 'un paso'],
    ['unidad de negocio', 'una unidad de negocio'],
  ])('%s → %s', (level, said) => {
    expect(withArticle(level)).toBe(said);
  });

  it('the empty choice of "Es parte de" uses it', () => {
    expect(noParentLabel({ estrategico: 'programa', hito: 'etapa', operativo: 'objetivo de área' })).toBe(
      'de ninguno (es un programa)',
    );
  });
});

// The review of the J4b (warning R3-proposal-decider-untested): when Leda proposes who does it,
// the decider already chosen follows the same rule as a hand-picked change.
describe('who decided, when Leda proposes who does it', () => {
  const OPTIONS = `GET /app/admin/api/espacios/${SPACE}/opciones`;
  const HELP = `POST /app/admin/api/espacios/${SPACE}/ayuda`;

  function serve(responsible: string) {
    const withAreas = options({
      areas: [
        { id: 'a-dir', nombre: 'Dirección', referente: { membership_id: 'm-ismael', nombre: 'Ismael' } },
        { id: 'a-auto', nombre: 'Automatización', referente: { membership_id: 'm-marcos', nombre: 'Marcos' } },
        { id: 'a-infra', nombre: 'Infraestructura', referente: { membership_id: 'm-lucas', nombre: 'Lucas' } },
      ],
    });
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, init?: RequestInit) => {
        const key = `${init?.method ?? 'GET'} ${url}`;
        const body =
          key === 'GET /app/admin/api/yo'
            ? adminMe()
            : key === OPTIONS
              ? withAreas
              : key === HELP
                ? { propuesta: { responsable_id: responsible }, elegir: [], avisos: [] }
                : null;
        return body
          ? new Response(JSON.stringify(body), { status: 200 })
          : new Response('{"error":"no_existe"}', { status: 404 });
      }),
    );
  }

  function pick(label: string, value: string) {
    fireEvent.click(screen.getByLabelText(label));
    const option = within(screen.getByRole('listbox'))
      .getAllByRole('option')
      .find((o) => o.dataset.value === value);
    if (!option) throw new Error(`"${label}" does not offer "${value}"`);
    fireEvent.click(option);
  }

  const decided = () =>
    within(screen.getByRole('complementary', { name: 'Vista previa' })).getByText('La decidió').nextElementSibling
      ?.textContent;

  async function proposeAfterDeciding(responsible: string) {
    window.history.replaceState(null, '', '/app/admin/');
    serve(responsible);
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    pick('Quién la decidió', 'm-marcos');
    expect(decided()).toBe('Marcos');
    fireEvent.change(screen.getByLabelText('Contame qué querés hacer y te ayudo'), {
      target: { value: 'hay que colgar el módem' },
    });
    fireEvent.click(screen.getByRole('button', { name: '> completar con Leda' }));
  }

  it('a decider who may not decide for the proposed person is cleared', async () => {
    await proposeAfterDeciding('m-lucas');
    await waitFor(() => expect(decided()).toBe('—'));
  });

  it('a decider who may decide for the proposed person stays', async () => {
    await proposeAfterDeciding('m-marcos');
    await screen.findByText('· propuesto por Leda');
    expect(decided()).toBe('Marcos');
  });
});
