import { fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AreaEditor } from './AreaEditor';
import { PersonEditor } from './PersonEditor';
import type { AreaPreview, PersonPreview, Team, TeamApi, TeamArea } from './teamApi';

// The key of a confirmation in the team's editors (J7-4 and J7-5): a confirm that got no answer may
// have done the change, so the key stays even after going back and reviewing again; the server then
// returns what was done, or refuses another change with that key, never does it twice. A confirm the
// server answered did nothing: the next review mints a new key.

const AREA: TeamArea = {
  id: 'a-auto',
  slug: 'automatizacion',
  nombre: 'Automatización',
  archivada: false,
  referente: { membership_id: 'm-marcos', nombre: 'Marcos', activo: true },
  autoaprobacion: false,
  personas: ['m-ismael', 'm-marcos'],
  tareas_abiertas: 0,
};

function team(): Team {
  const person = (id: string, nombre: string) => ({
    membership_id: id,
    nombre,
    activo: true,
    conectado: true,
    area_id: 'a-auto',
    area: 'Automatización',
    rol_id: 'r-int',
    rol: 'Integrante',
    autoridad_final: false,
    aprobador: { membership_id: 'm-ismael', nombre: 'Ismael', activo: true },
    referente_de: [],
  });
  return {
    espacio: { id: 'w-1', nombre: 'CoreWork' },
    areas: [AREA],
    personas: [
      { ...person('m-ismael', 'Ismael'), autoridad_final: true, aprobador: null },
      { ...person('m-marcos', 'Marcos'), referente_de: ['Automatización'] },
    ],
    roles: [
      { id: 'r-dir', slug: 'direccion', nombre: 'Dirección', autoridad_final: true, personas: 1 },
      { id: 'r-int', slug: 'integrante', nombre: 'Integrante', autoridad_final: false, personas: 1 },
    ],
    problemas: [],
    cambios: [],
    tipos_de_evidencia: [],
  };
}

const personPreview = (huella: string): PersonPreview => ({
  accion: 'alta',
  antes: null,
  despues: { nombre: 'Lucas Pérez', area: 'Automatización', rol: 'Integrante', quien_aprueba: 'Marcos' },
  aprobador: { membership_id: 'm-marcos', nombre: 'Marcos', por_omision: true },
  avisos: [],
  huella,
  problemas: [],
  problemas_nuevos: [],
});

const areaPreview = (huella: string): AreaPreview => ({
  accion: 'renombrar',
  antes: { nombre: 'Automatización' },
  despues: { nombre: 'Control' },
  huella,
  problemas: [],
  problemas_nuevos: [],
});

const CONFLICT = {
  kind: 'rejected' as const,
  errors: [{ campo: 'clave', motivo: 'usada_con_otros_datos', texto: 'Este envío ya hizo otro cambio.' }],
};
const NOT_SQUARE = {
  kind: 'rejected' as const,
  errors: [{ campo: 'equipo', motivo: 'no_cuadra', texto: 'Con este cambio el equipo no cuadraría: no se hizo.' }],
};

function fakeApi(overrides: Partial<TeamApi>): TeamApi {
  const never = () => Promise.reject(new Error('not in this test'));
  return {
    read: never,
    preview: never,
    confirm: never,
    previewPerson: never,
    confirmPerson: never,
    issueLink: never,
    ...overrides,
  };
}

afterEach(() => {
  vi.restoreAllMocks();
});

/** Reviews what the form holds and confirms it. */
async function reviewAndConfirm() {
  fireEvent.click(screen.getByRole('button', { name: '> revisar' }));
  const preview = within(await screen.findByRole('region', { name: 'Vista previa' }));
  fireEvent.click(preview.getByRole('button', { name: '> confirmar' }));
}

describe('the key of a person’s alta', () => {
  function open(api: TeamApi) {
    render(
      <PersonEditor api={api} team={team()} work={{ kind: 'alta' }} onDone={vi.fn()} onCancel={vi.fn()} onClosed={vi.fn()} />,
    );
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Lucas Pérez' } });
    fireEvent.change(screen.getByLabelText('Área'), { target: { value: 'a-auto' } });
  }

  it('a confirm with no answer keeps its key after going back and reviewing again', async () => {
    const previewPerson = vi
      .fn()
      .mockResolvedValue({ kind: 'preview', preview: personPreview('b'.repeat(64)) })
      .mockResolvedValueOnce({ kind: 'preview', preview: personPreview('a'.repeat(64)) });
    const confirmPerson = vi.fn().mockResolvedValue(CONFLICT).mockRejectedValueOnce(new TypeError('Failed to fetch'));
    open(fakeApi({ previewPerson, confirmPerson }));

    await reviewAndConfirm();
    expect(await screen.findByText('No se pudo confirmar: no llegó la respuesta. Probá de nuevo.')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '> volver' }));
    await reviewAndConfirm();
    expect(await screen.findByText('Este envío ya hizo otro cambio.')).toBeInTheDocument();

    expect(confirmPerson).toHaveBeenCalledTimes(2);
    expect(confirmPerson.mock.calls[1][1]).toBe(confirmPerson.mock.calls[0][1]);
    // The key stays while the server has not said the first one did nothing.
    await reviewAndConfirm();
    await vi.waitFor(() => expect(confirmPerson).toHaveBeenCalledTimes(3));
    expect(confirmPerson.mock.calls[2][1]).toBe(confirmPerson.mock.calls[0][1]);
  });

  it('a confirm the server answered did nothing: the next review mints a new key', async () => {
    const previewPerson = vi.fn().mockResolvedValue({ kind: 'preview', preview: personPreview('a'.repeat(64)) });
    const confirmPerson = vi.fn().mockResolvedValueOnce(NOT_SQUARE).mockResolvedValueOnce(NOT_SQUARE);
    open(fakeApi({ previewPerson, confirmPerson }));

    await reviewAndConfirm();
    expect(await screen.findByText('Con este cambio el equipo no cuadraría: no se hizo.')).toBeInTheDocument();
    await reviewAndConfirm();
    expect(await screen.findByText('Con este cambio el equipo no cuadraría: no se hizo.')).toBeInTheDocument();

    expect(confirmPerson).toHaveBeenCalledTimes(2);
    expect(confirmPerson.mock.calls[1][1]).not.toBe(confirmPerson.mock.calls[0][1]);
  });

  it('after no answer, a server answer that looked the key up lets the next review mint a new one', async () => {
    const previewPerson = vi.fn().mockResolvedValue({ kind: 'preview', preview: personPreview('a'.repeat(64)) });
    const confirmPerson = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockResolvedValueOnce(NOT_SQUARE)
      .mockResolvedValueOnce(NOT_SQUARE);
    open(fakeApi({ previewPerson, confirmPerson }));

    await reviewAndConfirm();
    fireEvent.click(await screen.findByRole('button', { name: '> probar de nuevo' }));
    expect(await screen.findByText('Con este cambio el equipo no cuadraría: no se hizo.')).toBeInTheDocument();
    await reviewAndConfirm();
    expect(await screen.findByText('Con este cambio el equipo no cuadraría: no se hizo.')).toBeInTheDocument();

    expect(confirmPerson).toHaveBeenCalledTimes(3);
    expect(confirmPerson.mock.calls[1][1]).toBe(confirmPerson.mock.calls[0][1]);
    expect(confirmPerson.mock.calls[2][1]).not.toBe(confirmPerson.mock.calls[0][1]);
  });
});

describe('the key of a change to an area', () => {
  function open(api: TeamApi) {
    render(
      <AreaEditor
        api={api}
        team={team()}
        work={{ kind: 'renombrar', area: AREA }}
        onDone={vi.fn()}
        onCancel={vi.fn()}
        onClosed={vi.fn()}
      />,
    );
    fireEvent.change(screen.getByLabelText('Nombre'), { target: { value: 'Control' } });
  }

  it('a confirm with no answer keeps its key after going back and reviewing again', async () => {
    const preview = vi
      .fn()
      .mockResolvedValueOnce({ kind: 'preview', preview: areaPreview('a'.repeat(64)) })
      .mockResolvedValueOnce({ kind: 'preview', preview: areaPreview('b'.repeat(64)) });
    const confirm = vi.fn().mockRejectedValueOnce(new TypeError('Failed to fetch')).mockResolvedValueOnce(CONFLICT);
    open(fakeApi({ preview, confirm }));

    await reviewAndConfirm();
    expect(await screen.findByText('No se pudo confirmar: no llegó la respuesta. Probá de nuevo.')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '> volver' }));
    await reviewAndConfirm();
    expect(await screen.findByText('Este envío ya hizo otro cambio.')).toBeInTheDocument();

    expect(confirm).toHaveBeenCalledTimes(2);
    expect(confirm.mock.calls[1][1]).toBe(confirm.mock.calls[0][1]);
  });

  it('a confirm the server answered did nothing: the next review mints a new key', async () => {
    const preview = vi.fn().mockResolvedValue({ kind: 'preview', preview: areaPreview('a'.repeat(64)) });
    const confirm = vi.fn().mockResolvedValueOnce(NOT_SQUARE).mockResolvedValueOnce(NOT_SQUARE);
    open(fakeApi({ preview, confirm }));

    await reviewAndConfirm();
    expect(await screen.findByText('Con este cambio el equipo no cuadraría: no se hizo.')).toBeInTheDocument();
    await reviewAndConfirm();
    expect(await screen.findByText('Con este cambio el equipo no cuadraría: no se hizo.')).toBeInTheDocument();

    expect(confirm).toHaveBeenCalledTimes(2);
    expect(confirm.mock.calls[1][1]).not.toBe(confirm.mock.calls[0][1]);
  });
});
