import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { adminMe, options, OTHER_SPACE, SPACE } from '../test/adminFixtures';
import { AdminApp } from './AdminApp';
import { newKey } from './draft';
import { CONTROL, FIELD_HINT, FIELD_TITLE, FIELD_VALUE, PREVIEW_VALUE, TEXT_SIZE } from './typography';

type Reply = { status: number; body?: unknown } | 'network';
type Call = { key: string; body: unknown };

const TASKS = `POST /app/admin/api/espacios/${SPACE}/tareas`;
const OPTIONS = `GET /app/admin/api/espacios/${SPACE}/opciones`;

/** A fake server: each route answers with its replies in order (the last one repeats). */
function serve(routes: Record<string, Reply | Reply[]>) {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      calls.push({ key, body: init?.body ? JSON.parse(String(init.body)) : undefined });
      const route = routes[key];
      const replies = Array.isArray(route) ? route : route ? [route] : [];
      const sent = calls.filter((c) => c.key === key).length;
      const reply = replies[Math.min(sent, replies.length) - 1];
      if (!reply) return new Response('{"error":"no_existe"}', { status: 404 });
      if (reply === 'network') throw new TypeError('Failed to fetch');
      return new Response(reply.body === undefined ? null : JSON.stringify(reply.body), {
        status: reply.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }),
  );
  return calls;
}

const ok = (body: unknown) => ({ status: 200, body });
const loaded = (avisos: unknown[] = []) => ({ status: 201, body: { task_id: 't-new', avisos, repetida: false } });

function keys(...values: string[]) {
  const spy = vi.spyOn(crypto, 'randomUUID');
  for (const v of values) spy.mockReturnValueOnce(v as `${string}-${string}-${string}-${string}-${string}`);
  return spy;
}

async function openForm(routes: Record<string, Reply | Reply[]> = {}) {
  const calls = serve({
    'GET /app/admin/api/yo': ok(adminMe()),
    [OPTIONS]: ok(options()),
    ...routes,
  });
  render(<AdminApp />);
  await screen.findByRole('form', { name: 'Cargar tarea' });
  return calls;
}

/** Picks the option with that value from a field's list, as a person does (J2-16: the lists are
 * the web's own, not the phone's): a tap on the list, a tap on the option. */
function pick(label: string | RegExp, value: string) {
  fireEvent.click(screen.getByLabelText(label));
  const option = within(screen.getByRole('listbox'))
    .getAllByRole('option')
    .find((o) => o.dataset.value === value);
  if (!option) throw new Error(`"${String(label)}" does not offer "${value}"`);
  fireEvent.click(option);
}

/** What a field's list offers: opened, read and closed again with Escape. */
function offered(label: string): string[] {
  fireEvent.click(screen.getByLabelText(label));
  const list = screen.getByRole('listbox');
  const names = within(list).getAllByRole('option').map((o) => o.textContent ?? '');
  fireEvent.keyDown(list, { key: 'Escape' });
  return names;
}

function fillTask() {
  pick('Objetivo', 'o1');
  fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Configurar alarmas del SCADA' } });
  pick('Quién la hace', 'm-marcos');
  fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
  fireEvent.change(screen.getByLabelText('Criterio de aceptación'), {
    target: { value: 'Las 12 alarmas suenan en la sala de control' },
  });
  pick('Quién la decidió', 'm-ismael');
}

const confirm = () => fireEvent.click(screen.getByRole('button', { name: /confirmar|probar de nuevo/ }));
const preview = () => screen.getByRole('complementary', { name: 'Vista previa' });

beforeEach(() => {
  window.history.replaceState(null, '', '/app/admin/');
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('AdminApp', () => {
  it('shows who is in and a form fed by the options', async () => {
    await openForm();
    expect(within(screen.getByRole('banner')).getByText('Ariel')).toBeInTheDocument();
    expect(screen.getByText('LEDA · ADMINISTRACIÓN · COREWORK')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Cargar tarea');
    // One space: no selector.
    expect(screen.queryByLabelText('espacio')).toBeNull();
    expect(offered('Objetivo')).toContain('Puesta en marcha de la línea 3 · hasta 30.10');
    expect(offered('Quién la hace')).toContain('Lucas · Infraestructura · sin conectar');
    pick('Quién la hace', 'm-lucas');
    expect(screen.getByText('· la revisa: Ismael')).toBeInTheDocument();
    expect(screen.getByText('[SIN CONECTAR]')).toBeInTheDocument();
    pick('Quién la hace', 'm-ismael');
    expect(screen.getByText('· la revisa: nadie')).toBeInTheDocument();
  });

  it('offers only the working days from today on', async () => {
    await openForm();
    const calendar = screen.getByRole('group', { name: 'Fecha' });
    const offered = within(calendar)
      .getAllByRole('button', { pressed: false })
      .map((b) => b.getAttribute('data-day'));
    expect(offered[0]).toBe('2026-10-12');
    expect(offered).toContain('2026-10-16');
    expect(offered).not.toContain('2026-10-17');
    expect(offered).not.toContain('2026-10-18');
    expect(within(calendar).queryByRole('button', { name: 'vie 09.10' })).toBeNull();
    fireEvent.click(within(calendar).getByRole('button', { name: 'mes siguiente' }));
    expect(within(calendar).queryByRole('button', { name: 'lun 23.11' })).toBeNull();
    expect(within(calendar).getByRole('button', { name: 'mar 24.11' })).toBeInTheDocument();
    expect(within(calendar).getByRole('button', { name: 'mes siguiente' })).toBeDisabled();
  });

  it('moves between working days with the arrows', async () => {
    await openForm();
    const friday = screen.getByRole('button', { name: 'vie 16.10' });
    friday.focus();
    fireEvent.keyDown(friday, { key: 'ArrowRight' });
    await waitFor(() => expect(screen.getByRole('button', { name: 'lun 19.10' })).toHaveFocus());
    fireEvent.keyDown(document.activeElement as Element, { key: 'ArrowUp' });
    await waitFor(() => expect(screen.getByRole('button', { name: 'lun 12.10' })).toHaveFocus());
  });

  it('pre-checks the evidence the area asks for', async () => {
    await openForm();
    pick('Quién la hace', 'm-marcos');
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).toBeChecked();
    expect(screen.getByRole('checkbox', { name: /un informe/ })).not.toBeChecked();
    pick('Quién la hace', 'm-lucas');
    expect(screen.queryByRole('checkbox')).toBeNull();
    expect(screen.getByText('El área no pide evidencia.')).toBeInTheDocument();
  });

  it('counts characters against the server limits', async () => {
    await openForm();
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'x'.repeat(205) } });
    expect(screen.getByText('205/200 · sobran 5')).toBeInTheDocument();
  });

  it('one screen: the live preview under "Vista previa", and confirm right below it', async () => {
    const calls = await openForm();
    expect(screen.queryByRole('button', { name: '> revisar' })).toBeNull();
    fillTask();
    const aside = preview();
    expect(within(aside).getByRole('heading', { name: 'Vista previa' })).toBeInTheDocument();
    const card = aside.querySelector('article[data-task]') as HTMLElement;
    expect(card).toHaveTextContent('Configurar alarmas del SCADA');
    expect(card).toHaveTextContent('16.10');
    expect(card).toHaveTextContent('└─ de Marcos');
    expect(aside).toHaveTextContent('Puesta en marcha de la línea 3');
    expect(aside).toHaveTextContent('una captura de pantalla');
    expect(aside).toHaveTextContent('La revisaIsmael');
    expect(aside).toHaveTextContent('La decidióIsmael');
    expect(aside).toHaveTextContent('La cargaAriel');
    const button = within(aside).getByRole('button', { name: '> confirmar' });
    // The confirm button comes after what it confirms.
    expect(card.compareDocumentPosition(button) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    // Writing never sends (Enter in a field submits the form): only confirm does.
    fireEvent.submit(screen.getByRole('form', { name: 'Cargar tarea' }));
    expect(calls.some((c) => c.key === TASKS)).toBe(false);
  });

  it('confirm with missing fields says what is missing next to it, focuses the first and sends nothing', async () => {
    const calls = await openForm();
    pick('Objetivo', 'o1');
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Configurar alarmas del SCADA' } });
    pick('Quién la hace', 'm-marcos');
    fireEvent.click(screen.getByRole('checkbox', { name: /una captura de pantalla/ }));
    fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
    confirm();
    const summary = within(preview()).getByRole('alert');
    expect(summary).toHaveTextContent('Falta completar: criterio de aceptación, evidencia, quién la decidió.');
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveFocus();
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveAttribute('aria-invalid', 'true');
    expect(document.getElementById('f-criterio-error')).toHaveTextContent('Falta el criterio de aceptación');
    expect(screen.getByLabelText('Quién la decidió')).toHaveAttribute('aria-describedby', 'f-decidio-error');
    expect(calls.some((c) => c.key === TASKS)).toBe(false);
    // Each name takes you to its field.
    fireEvent.click(within(summary).getByRole('button', { name: 'quién la decidió' }));
    expect(screen.getByLabelText('Quién la decidió')).toHaveFocus();
    fireEvent.click(within(summary).getByRole('button', { name: 'evidencia' }));
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).toHaveFocus();
    // Fixing a field takes it off the summary; with nothing missing, the summary goes away.
    pick('Quién la decidió', 'm-ismael');
    expect(summary).toHaveTextContent('Falta completar: criterio de aceptación, evidencia.');
    fireEvent.click(screen.getByRole('checkbox', { name: /una captura de pantalla/ }));
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), { target: { value: 'Suenan las 12' } });
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('an empty form lists every required field, the first one focused', async () => {
    await openForm();
    confirm();
    expect(screen.getByRole('alert')).toHaveTextContent(
      'Falta completar: objetivo, título, quién la hace, fecha, criterio de aceptación, quién la decidió.',
    );
    expect(screen.getByLabelText('Objetivo')).toHaveFocus();
  });

  it('a 422 from the server shows the same summary, with its own texts on the fields', async () => {
    const calls = await openForm({
      [TASKS]: {
        status: 422,
        body: {
          errores: [
            { campo: 'criterio', motivo: 'falta', texto: 'Falta el criterio de aceptación: qué tiene que pasar para darla por terminada.' },
            { campo: 'evidencia', motivo: 'falta', texto: 'Elegí la evidencia que se pide para darla por terminada.' },
            { campo: 'decidio', motivo: 'falta', texto: 'Elegí quién decidió la tarea.' },
          ],
        },
      },
    });
    const scroll = vi.spyOn(window, 'scrollTo');
    fillTask();
    confirm();
    const summary = await within(preview()).findByRole('alert');
    expect(summary).toHaveTextContent('Falta completar: criterio de aceptación, evidencia, quién la decidió.');
    await waitFor(() => expect(screen.getByLabelText('Criterio de aceptación')).toHaveFocus());
    expect(scroll).toHaveBeenCalled();
    expect(document.getElementById('f-decidio-error')).toHaveClass('text-falta');
    expect(document.getElementById('f-decidio-error')).toHaveTextContent('Elegí quién decidió la tarea.');
    expect(document.getElementById('f-evidencia-error')).toHaveTextContent('Elegí la evidencia que se pide');
    expect(calls.filter((c) => c.key === TASKS)).toHaveLength(1);
  });

  it('says what is still missing above confirm from the start, and the list shrinks as fields are filled', async () => {
    await openForm();
    const button = screen.getByRole('button', { name: '> confirmar' });
    const line = document.getElementById('lo-que-falta') as HTMLElement;
    expect(line).toHaveTextContent(
      'Falta completar: objetivo, título, quién la hace, fecha, criterio de aceptación, quién la decidió.',
    );
    expect(line).toHaveClass('text-falta');
    // The line comes right before the button it explains.
    expect(line.compareDocumentPosition(button) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    // Dimmed, but still tappable: never the HTML disabled attribute.
    expect(button).toHaveAttribute('aria-disabled', 'true');
    expect(button).toHaveAttribute('aria-describedby', 'lo-que-falta');
    expect(button).toBeEnabled();
    // Nothing is marked on the fields before confirm is tapped: the line is enough.
    expect(screen.getByLabelText('Título')).not.toHaveAttribute('aria-invalid');
    expect(screen.queryByRole('alert')).toBeNull();
    pick('Objetivo', 'o1');
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Configurar alarmas del SCADA' } });
    expect(line).toHaveTextContent('Falta completar: quién la hace, fecha, criterio de aceptación, quién la decidió.');
    fillTask();
    expect(document.getElementById('lo-que-falta')).toBeNull();
    expect(button).not.toHaveAttribute('aria-disabled');
    expect(button).not.toHaveAttribute('aria-describedby');
  });

  it('each tap on the dimmed confirm sends nothing and takes the person to the next missing field', async () => {
    // jsdom has no scrolling: an empty implementation, and both spies restored even on a failure.
    const scroll = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
    const focus = vi.spyOn(HTMLElement.prototype, 'focus');
    try {
      const calls = await openForm();
      pick('Objetivo', 'o1');
      fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Configurar alarmas del SCADA' } });
      pick('Quién la hace', 'm-marcos');
      fireEvent.click(screen.getByRole('checkbox', { name: /una captura de pantalla/ }));
      fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
      const criterio = screen.getByLabelText('Criterio de aceptación');
      const evidence = screen.getByRole('checkbox', { name: /una captura de pantalla/ });
      const decided = screen.getByLabelText('Quién la decidió');
      confirm();
      expect(criterio).toHaveFocus();
      // The field's message is there, in the warning color, and its border too.
      expect(document.getElementById('f-criterio-error')).toHaveClass('text-falta');
      expect(document.getElementById('f-criterio-error')).toHaveTextContent('Falta el criterio de aceptación');
      expect(document.getElementById('f-criterio-error')?.textContent).not.toContain('!');
      expect(document.querySelector('#f-criterio-error svg')).toHaveAttribute('aria-hidden', 'true');
      expect(document.getElementById('f-evidencia-error')).toHaveClass('text-falta');
      expect(criterio).toHaveClass('aria-[invalid=true]:border-falta');
      expect(within(preview()).getByRole('alert')).toHaveClass('text-falta');
      // Focusing never scrolls by itself, and the scroll is only vertical.
      expect(focus).toHaveBeenLastCalledWith({ preventScroll: true });
      expect(scroll).toHaveBeenCalled();
      for (const [arg] of scroll.mock.calls) {
        expect(arg).toEqual(expect.objectContaining({ top: expect.any(Number) }));
        expect(arg).not.toHaveProperty('left');
      }
      confirm();
      expect(evidence).toHaveFocus();
      confirm();
      expect(decided).toHaveFocus();
      // After the last one, back to the first.
      confirm();
      expect(criterio).toHaveFocus();
      // A field that gets filled drops out of the round: with the focus on the criterion, the
      // evidence (the next one) gets filled, so the next tap skips it and goes to the decider.
      fireEvent.click(evidence);
      confirm();
      expect(decided).toHaveFocus();
      // From the last one, back to the first that still lacks something: the criterion.
      confirm();
      expect(criterio).toHaveFocus();
      // Filled too: only the decider is left, and every tap goes there.
      fireEvent.change(criterio, { target: { value: 'Suenan las 12' } });
      confirm();
      expect(decided).toHaveFocus();
      confirm();
      expect(decided).toHaveFocus();
      expect(focus).toHaveBeenLastCalledWith({ preventScroll: true });
      expect(calls.some((c) => c.key === TASKS)).toBe(false);
    } finally {
      scroll.mockRestore();
      focus.mockRestore();
    }
  });

  it('the page can never pan sideways: the overflow safety net is in place', async () => {
    await openForm();
    // Vitest runs without CSS (`css: false`), so the stylesheet is read as a file, found from this
    // test file (`import.meta.dirname`) and not from the folder the tests run in. Not with a `URL`:
    // under jsdom it is jsdom's, which Node's `fs` does not take.
    // @ts-expect-error -- this browser project has no Node types; the tests run on Node.
    const { readFileSync } = await import('node:fs');
    // @ts-expect-error -- the same: `dirname` is Node's, not in the browser's `ImportMeta`.
    const here: string = import.meta.dirname;
    const css: string = readFileSync(`${here}/../index.css`, 'utf-8');
    // html and body clip what goes past the right edge (clip, not hidden, so nothing becomes a
    // scroll container and the sticky preview keeps working).
    expect(css).toMatch(/html,\s*body\s*\{[^}]*overflow-x:\s*clip/);
    expect(css).toMatch(/#root\s*\{[^}]*overflow-x:\s*clip/);
    const form = screen.getByRole('form', { name: 'Cargar tarea' });
    const layout = form.parentElement as HTMLElement;
    expect(layout.closest('.overflow-x-clip')).not.toBeNull();
    expect(layout).toHaveClass('max-w-full', 'min-w-0');
    expect(form).toHaveClass('max-w-full');
    expect(preview()).toHaveClass('max-w-full');
    // jsdom has no layout: whether the page still pans is only confirmed on the phone.
  });

  it('every control and the calendar are built to fit the width of a phone', async () => {
    await openForm();
    const form = screen.getByRole('form', { name: 'Cargar tarea' });
    const controls = form.querySelectorAll('[aria-haspopup="listbox"], input:not([type="checkbox"]), textarea');
    expect(controls.length).toBeGreaterThan(0);
    for (const control of controls) {
      expect(control).toHaveClass('w-full', 'min-w-0', 'max-w-full');
      // The size of the titles, never 16px: the zoom on focus is stopped on iOS by the viewport.
      expect(control).toHaveClass(...TEXT_SIZE.split(' '));
      expect(control.className).not.toContain('16px');
    }
    expect(screen.getByRole('group', { name: 'Fecha' })).toHaveClass('w-full', 'min-w-0', 'max-w-full');
    expect(form).toHaveClass('min-w-0');
    expect(preview()).toHaveClass('min-w-0');
    // jsdom has no layout: the real width is only confirmed on the phone.
  });

  it('every control has the same box and text, so a list looks like a text field (J2-10)', async () => {
    await openForm();
    const form = screen.getByRole('form', { name: 'Cargar tarea' });
    const controls = form.querySelectorAll('[aria-haspopup="listbox"], input:not([type="checkbox"]), textarea');
    for (const control of controls) expect(control).toHaveClass(...CONTROL.split(' '));
    // A list to choose from is the web's own (J2-16): the phone's menu cannot take the web's font
    // and size, so there is no native list left, in the form nor above it.
    expect(document.querySelectorAll('select')).toHaveLength(0);
    const lists = form.querySelectorAll('[aria-haspopup="listbox"]');
    expect(lists).toHaveLength(4);
    for (const list of lists) expect(list).toHaveClass('appearance-none');
    // The calendar's days are written in the same size as the controls.
    const day = screen.getByRole('button', { name: 'vie 16.10' });
    expect(day.parentElement).toHaveClass(...TEXT_SIZE.split(' '));
    expect(day).toHaveClass('text-ink-soft');
    // jsdom has no layout: whether they look the same size is only confirmed on the phone.
  });

  it('titles, values and help texts share one style in the form and in the preview (J2-10)', async () => {
    await openForm();
    const styled = (element: Element | null, style: string) => expect(element).toHaveClass(...style.split(' '));
    // An empty value in the preview is a dash in the same style as any value there.
    const empty = within(preview()).getByText('Objetivo').nextElementSibling;
    expect(empty).toHaveTextContent('—');
    styled(empty, PREVIEW_VALUE);
    styled(empty?.firstElementChild ?? null, PREVIEW_VALUE);
    fillTask();
    // The form: the title of a field, what the person types or chooses, and the help under it.
    styled(document.getElementById('f-criterio-label'), FIELD_TITLE);
    styled(screen.getByText('Contame qué querés hacer y te ayudo'), FIELD_TITLE);
    styled(screen.getByText('Evidencia que se pide'), FIELD_TITLE);
    styled(screen.getByLabelText('Criterio de aceptación'), FIELD_VALUE);
    styled(screen.getByLabelText('Quién la hace'), FIELD_VALUE);
    styled(screen.getByText('Qué tiene que pasar para darla por terminada.'), FIELD_HINT);
    // The preview's heading is one more field title (user, on the iPhone, 2026-10-13).
    const heading = within(preview()).getByRole('heading', { name: 'Vista previa' });
    styled(heading, FIELD_TITLE);
    expect(heading).not.toHaveClass('uppercase');
    expect(heading.className).not.toContain('tracking-');
    // The preview: each data name is a title, in sentence case, and its value looks like a help text.
    const name = within(preview()).getByText('Criterio de aceptación');
    expect(name.tagName).toBe('DT');
    styled(name, FIELD_TITLE);
    styled(name.nextElementSibling, PREVIEW_VALUE);
    expect(name.nextElementSibling).not.toHaveClass('text-ink-soft');
    expect(name.nextElementSibling).toHaveTextContent('Las 12 alarmas suenan en la sala de control');
    expect(PREVIEW_VALUE).toBe(FIELD_HINT);
    // One size for titles, values and help, in normal case; they differ only by color.
    for (const style of [FIELD_TITLE, FIELD_VALUE, FIELD_HINT, CONTROL]) {
      expect(style).toContain(TEXT_SIZE);
      expect(style).not.toContain('16px');
    }
    expect(FIELD_TITLE).not.toContain('uppercase');
    expect(FIELD_TITLE).toContain('text-ink');
    expect(FIELD_TITLE).not.toContain('font-bold');
  });

  it('no text on the load page is bigger than the form, but the page title (J2-10)', async () => {
    await openForm();
    fillTask();
    // Every element below the page title, the form and its preview included: none takes a size
    // above the body size nor the 16px the controls used to have.
    const main = document.querySelector('main') as HTMLElement;
    const big = /(^|s)(pointer-coarse:)?text-(button|day|count|title|[d+px])(s|$)/;
    const offenders = [...main.querySelectorAll('*')].filter((element) => big.test(element.getAttribute('class') ?? ''));
    expect(offenders.map((element) => element.outerHTML.slice(0, 80))).toEqual([]);
    for (const button of screen.getAllByRole('button', { name: /completar con Leda|confirmar/ })) {
      expect(button).toHaveClass(...TEXT_SIZE.split(' '));
    }
  });

  it('confirm sends the data with one key and shows the warnings', async () => {
    keys('11111111-1111-4111-8111-111111111111');
    const calls = await openForm({
      [TASKS]: loaded([
        { campo: 'responsable', motivo: 'sin_conectar', texto: 'Esa persona todavía no tiene Leda conectada: no va a recibir avisos ni seguimiento hasta que la conecte.' },
      ]),
    });
    fillTask();
    expect(screen.getByRole('button', { name: '> confirmar' })).not.toHaveAttribute('aria-disabled');
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    expect(screen.getByText(/no va a recibir avisos ni seguimiento hasta que la conecte/)).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS);
    expect(sent).toHaveLength(1);
    expect(sent[0].body).toEqual({
      objetivo_id: 'o1',
      titulo: 'Configurar alarmas del SCADA',
      descripcion: '',
      responsable_id: 'm-marcos',
      fecha: '2026-10-16',
      criterio: 'Las 12 alarmas suenan en la sala de control',
      evidencia: ['captura'],
      decidio_id: 'm-ismael',
      clave: '11111111-1111-4111-8111-111111111111',
    });
    fireEvent.click(screen.getByRole('button', { name: '> cargar otra' }));
    expect(screen.getByLabelText('Título')).toHaveValue('');
  });

  it('offers the open tasks to wait for, shows the wait and sends it', async () => {
    keys('22222222-2222-4222-8222-222222222222');
    const calls = await openForm({
      [OPTIONS]: ok(
        options({
          tareas: [
            {
              id: 't-estante',
              titulo: 'Colocar el estante',
              estado: 'asignada',
              fecha_objetivo: '2026-10-15',
              responsable: 'Lucas',
              objetivo: 'Mantenimiento anual',
            },
          ],
        }),
      ),
      [TASKS]: loaded(),
    });
    expect(screen.getByLabelText('Espera a (opcional)')).toHaveValue('');
    expect(offered('Espera a (opcional)')).toEqual([
      'no espera a ninguna',
      'Colocar el estante · Lucas · Mantenimiento anual',
    ]);
    fillTask();
    pick('Espera a (opcional)', 't-estante');
    const form = screen.getByRole('form', { name: 'Cargar tarea' });
    expect(within(form).getByText('No puede empezar hasta que esa esté terminada.')).toBeInTheDocument();
    expect(preview()).toHaveTextContent(
      'Espera aColocar el estante · Lucas',
    );
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS);
    expect(sent).toHaveLength(1);
    expect((sent[0].body as { espera_id?: string }).espera_id).toBe('t-estante');
  });

  it('without a wait the form sends what it sent before, and says when there is nothing to wait for', async () => {
    const calls = await openForm({ [TASKS]: loaded() });
    expect(screen.getByText('No hay tareas abiertas para esperar en este espacio.')).toBeInTheDocument();
    fillTask();
    expect(preview()).not.toHaveTextContent('espera a');
    confirm();
    await screen.findByText('Tarea cargada.');
    const sent = calls.filter((c) => c.key === TASKS);
    expect(sent[0].body).not.toHaveProperty('espera_id');
  });

  it('a rejected wait lands on its field', async () => {
    await openForm({
      [OPTIONS]: ok(
        options({
          tareas: [
            { id: 't-estante', titulo: 'Colocar el estante', estado: 'asignada', fecha_objetivo: null, responsable: 'Lucas', objetivo: 'Mantenimiento anual' },
          ],
        }),
      ),
      [TASKS]: {
        status: 422,
        body: {
          errores: [
            { campo: 'espera', motivo: 'esta_cerrada', texto: 'La tarea que espera ya está cerrada: no puede trabar a otra.' },
          ],
        },
      },
    });
    fillTask();
    pick('Espera a (opcional)', 't-estante');
    confirm();
    await screen.findByRole('alert');
    expect(screen.getByLabelText('Espera a (opcional)')).toHaveAttribute('aria-invalid', 'true');
    expect(document.getElementById('f-espera-error')).toHaveTextContent('ya está cerrada');
    pick('Espera a (opcional)', '');
    expect(document.getElementById('f-espera-error')).toBeNull();
  });

  it('warns when the date is after the objective, without blocking', async () => {
    await openForm();
    pick('Objetivo', 'o1');
    fireEvent.click(screen.getByRole('button', { name: 'mes siguiente' }));
    fireEvent.click(screen.getByRole('button', { name: 'lun 02.11' }));
    expect(screen.getAllByText(/Es posterior a la del objetivo \(30\.10\)/).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: '> confirmar' })).toBeEnabled();
  });

  it('a retry after a network failure keeps the data and the key', async () => {
    keys('22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333');
    const calls = await openForm({ [TASKS]: ['network', loaded()] });
    fillTask();
    confirm();
    // While it is sending, what is shown is what goes: the form is locked.
    expect(screen.getByLabelText('Título')).toBeDisabled();
    expect(screen.getByRole('button', { name: 'cargando…' })).toBeDisabled();
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo cargar');
    expect(screen.getByLabelText('Título')).toHaveValue('Configurar alarmas del SCADA');
    expect(screen.getByLabelText('Título')).toBeEnabled();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { clave: string }).clave);
    expect(sent).toEqual(['22222222-2222-4222-8222-222222222222', '22222222-2222-4222-8222-222222222222']);
  });

  it('while it loads, "cargando" has the same three fading dots as "completando", always (J2-15)', async () => {
    // The user, on the iPhone (J2-12): the dots of "completando…" also on "cargando…".
    await openForm();
    let answer: (r: Response) => void = () => {};
    const real = globalThis.fetch;
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string, init?: RequestInit) =>
        init?.method === 'POST' && url.endsWith('/tareas')
          ? new Promise<Response>((resolve) => (answer = resolve))
          : real(url, init),
      ),
    );
    fillTask();
    confirm();
    const button = screen.getByRole('button', { name: 'cargando…' });
    expect(button).toBeDisabled();
    const dots = Array.from(button.querySelectorAll('.animate-puntos'));
    expect(dots).toHaveLength(3);
    expect(dots.map((d) => d.textContent)).toEqual(['.', '.', '.']);
    expect(new Set(dots.map((d) => d.className)).size).toBe(3);
    expect(button.innerHTML).not.toMatch(/motion-reduce|motion-safe/);
    answer(new Response(JSON.stringify({ task_id: 't-new', avisos: [], repetida: false }), {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    }));
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
  });

  it('after a send with no answer, editing keeps the key so the server can tell', async () => {
    keys('44444444-4444-4444-8444-444444444444', '55555555-5555-4555-8555-555555555555');
    const conflict = {
      status: 422,
      body: {
        errores: [
          { campo: 'clave', motivo: 'usada_con_otros_datos', texto: 'Este envío ya cargó otra tarea. Recargá la página para cargar una nueva.' },
        ],
      },
    };
    const calls = await openForm({ [TASKS]: ['network', conflict, loaded()] });
    fillTask();
    confirm();
    await screen.findByRole('alert');
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Configurar las alarmas' } });
    confirm();
    // The first send may have loaded it: the server refused the same key with other data.
    expect(await screen.findByText(/Puede que ya se haya cargado: fijate en "El equipo"/)).toBeInTheDocument();
    expect(screen.queryByText(/Recargá la página/)).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'no está cargada: empezar de nuevo' }));
    expect(screen.queryByText(/Puede que ya se haya cargado/)).toBeNull();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { clave: string }).clave);
    expect(sent).toEqual([
      '44444444-4444-4444-8444-444444444444',
      '44444444-4444-4444-8444-444444444444',
      '55555555-5555-4555-8555-555555555555',
    ]);
  });

  it('after a rejection nothing was loaded, so editing renews the key', async () => {
    keys('66666666-6666-4666-8666-666666666666', '77777777-7777-4777-8777-777777777777');
    const rejected = {
      status: 422,
      body: { errores: [{ campo: 'criterio', motivo: 'falta', texto: 'Falta el criterio de aceptación.' }] },
    };
    const calls = await openForm({ [TASKS]: ['network', rejected, loaded()] });
    fillTask();
    confirm();
    await screen.findByRole('alert');
    confirm();
    await screen.findByText('No se cargó: hay que corregir lo marcado.');
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), { target: { value: 'Suenan las 12' } });
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { clave: string }).clave);
    expect(sent).toEqual([
      '66666666-6666-4666-8666-666666666666',
      '66666666-6666-4666-8666-666666666666',
      '77777777-7777-4777-8777-777777777777',
    ]);
  });

  // J2-9: a criterion that does not say how it is checked is refused by the server.
  const NO_CHECK = {
    status: 422,
    body: {
      errores: [{ campo: 'criterio', motivo: 'sin_comprobacion', texto: 'Contame cómo se sabe que está terminada.' }],
    },
  };

  it('a criterion that does not say how it is checked lands on its field, in the missing color', async () => {
    const calls = await openForm({ [TASKS]: NO_CHECK });
    const scroll = vi.spyOn(window, 'scrollTo');
    fillTask();
    confirm();
    await waitFor(() => expect(screen.getByLabelText('Criterio de aceptación')).toHaveFocus());
    expect(scroll).toHaveBeenCalled();
    const message = document.getElementById('f-criterio-error');
    expect(message).toHaveTextContent('Contame cómo se sabe que está terminada.');
    expect(message).toHaveClass('text-falta');
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveAttribute('aria-invalid', 'true');
    expect(within(preview()).getByRole('alert')).toHaveTextContent('Hay que corregir: criterio de aceptación.');
    expect(calls.filter((c) => c.key === TASKS)).toHaveLength(1);
    // Rewriting it clears the mark.
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), {
      target: { value: 'Las 12 alarmas suenan en la sala de control; se prueba disparando cada una' },
    });
    expect(document.getElementById('f-criterio-error')).toBeNull();
  });

  it('after a send with no answer, a refused criterion keeps the key: the server did not look it up', async () => {
    keys('88888888-8888-4888-8888-888888888888', '99999999-9999-4999-8999-999999999999');
    const calls = await openForm({ [TASKS]: ['network', NO_CHECK, loaded()] });
    fillTask();
    confirm();
    await screen.findByRole('alert');
    confirm();
    expect(await screen.findByText('Contame cómo se sabe que está terminada.')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), {
      target: { value: 'Las 12 alarmas suenan en la sala de control; se prueba disparando cada una' },
    });
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { clave: string }).clave);
    expect(sent).toEqual([
      '88888888-8888-4888-8888-888888888888',
      '88888888-8888-4888-8888-888888888888',
      '88888888-8888-4888-8888-888888888888',
    ]);
  });

  // J2-14: a criterion that says no result is refused with the one Leda proposes (the result and
  // the area's evidence), next to the field, ready to use with one tap.
  const NO_RESULT_TEXT = 'No dice qué tiene que quedar hecho para darla por terminada.';
  const PROPOSED_CRITERION =
    'Las alarmas del SCADA quedan configuradas. Se comprueba con lo que pide el área: una captura de pantalla.';
  const noResult = (propuesta?: string) => ({
    status: 422,
    body: {
      errores: [{ campo: 'criterio', motivo: 'sin_resultado', texto: NO_RESULT_TEXT, ...(propuesta ? { propuesta } : {}) }],
    },
  });
  const useProposal = () => screen.getByRole('button', { name: '> usar este criterio' });

  it('a criterion with no result comes back with the one Leda proposes, and one tap uses it', async () => {
    keys('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb');
    // First a send with no answer: it may have loaded the task, so the key stays until something
    // settles it, and this refusal does not (the server decides it before looking the key up).
    const calls = await openForm({ [TASKS]: ['network', noResult(PROPOSED_CRITERION), loaded()] });
    fillTask();
    confirm();
    await screen.findByRole('alert');
    confirm();
    await waitFor(() => expect(screen.getByLabelText('Criterio de aceptación')).toHaveFocus());
    expect(document.getElementById('f-criterio-error')).toHaveTextContent(NO_RESULT_TEXT);
    expect(screen.getByText(PROPOSED_CRITERION)).toBeInTheDocument();
    fireEvent.click(useProposal());
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveValue(PROPOSED_CRITERION);
    expect(document.getElementById('f-criterio-error')).toBeNull();
    expect(screen.queryByRole('button', { name: '> usar este criterio' })).toBeNull();
    expect(markOf('Criterio de aceptación')).toBeInTheDocument();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => c.body as { criterio: string; clave: string });
    expect(sent[2].criterio).toBe(PROPOSED_CRITERION);
    expect(sent.map((b) => b.clave)).toEqual([
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
    ]);
  });

  it('the person can write her own instead: the proposal goes with the notice', async () => {
    await openForm({ [TASKS]: noResult(PROPOSED_CRITERION) });
    fillTask();
    confirm();
    expect(await screen.findByText(PROPOSED_CRITERION)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), {
      target: { value: 'Las alarmas suenan en la sala de control' },
    });
    expect(screen.queryByText(PROPOSED_CRITERION)).toBeNull();
    expect(document.getElementById('f-criterio-error')).toBeNull();
    expect(markOf('Criterio de aceptación')).toBeNull();
  });

  it('without a proposal the notice still says what is missing, and there is nothing to tap', async () => {
    await openForm({ [TASKS]: noResult() });
    fillTask();
    confirm();
    expect(await screen.findByText(NO_RESULT_TEXT)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '> usar este criterio' })).toBeNull();
    expect(within(preview()).getByRole('alert')).toHaveTextContent('Hay que corregir: criterio de aceptación.');
  });

  it('a criterion Leda could not review loads with a warning that does not block', async () => {
    await openForm({
      [TASKS]: loaded([
        {
          campo: 'criterio',
          motivo: 'sin_revisar',
          texto: 'No pude revisar el criterio ahora: la tarea quedó cargada con el criterio como lo escribiste.',
        },
      ]),
    });
    fillTask();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    expect(screen.getByText(/No pude revisar el criterio ahora/)).toBeInTheDocument();
  });

  it('each rejection lands on its field, and the rest in the summary', async () => {
    await openForm({
      [TASKS]: {
        status: 422,
        body: {
          errores: [
            { campo: 'fecha', motivo: 'no_es_dia_habil', texto: 'Ese día no es hábil en este espacio.' },
            { campo: 'responsable', motivo: 'sin_quien_la_revise', texto: 'Nadie activo revisa el trabajo de esa persona: nadie podría aprobar la tarea.' },
            { campo: 'clave', motivo: 'mal_formada', texto: 'Este dato no es válido.' },
          ],
        },
      },
    });
    fillTask();
    confirm();
    const summary = await screen.findByRole('alert');
    expect(summary).toHaveTextContent('No se cargó: hay que corregir lo marcado.');
    expect(summary).toHaveTextContent('Hay que corregir: quién la hace, fecha.');
    expect(summary).toHaveTextContent('Este dato no es válido.');
    await waitFor(() => expect(screen.getByLabelText('Quién la hace')).toHaveFocus());
    expect(screen.getByLabelText('Quién la hace')).toHaveAttribute('aria-invalid', 'true');
    expect(document.getElementById('f-responsable-error')).toHaveTextContent('Nadie activo revisa');
    expect(document.getElementById('f-fecha-error')).toHaveTextContent('Ese día no es hábil');
    // Fixing a field clears its message.
    pick('Quién la hace', 'm-lucas');
    expect(document.getElementById('f-responsable-error')).toBeNull();
  });

  it('a closed session while confirming asks to come in with a new link', async () => {
    await openForm({ [TASKS]: { status: 401, body: { error: 'sin_sesion' } } });
    fillTask();
    confirm();
    expect(await screen.findByText('La sesión está cerrada.')).toBeInTheDocument();
    expect(screen.getByText(/entrá con un enlace nuevo/)).toBeInTheDocument();
    expect(screen.queryByRole('form')).toBeNull();
  });

  it('makes a valid key where randomUUID is missing (plain HTTP)', () => {
    vi.stubGlobal('crypto', { getRandomValues: (a: Uint8Array) => a.fill(171) });
    expect(newKey()).toBe('ab'.repeat(16));
  });

  it('without a session there is no form', async () => {
    serve({ 'GET /app/admin/api/yo': { status: 401, body: { error: 'sin_sesion' } } });
    render(<AdminApp />);
    expect(await screen.findByText('La sesión está cerrada.')).toBeInTheDocument();
    expect(screen.queryByText('salir')).toBeNull();
  });

  it('a space the server no longer finds re-reads the spaces once and never loops', async () => {
    const calls = serve({
      'GET /app/admin/api/yo': ok(adminMe()),
      [OPTIONS]: { status: 404, body: { error: 'espacio_no_existe' } },
    });
    render(<AdminApp />);
    expect(await screen.findByText('Ese espacio ya no está disponible.')).toBeInTheDocument();
    await new Promise((resolve) => setTimeout(resolve, 50));
    const count = (key: string) => calls.filter((c) => c.key === key).length;
    expect(count('GET /app/admin/api/yo')).toBe(2);
    expect(count(OPTIONS)).toBe(1);
    // Only the person asks again.
    fireEvent.click(screen.getByRole('button', { name: 'probar de nuevo' }));
    await waitFor(() => expect(count(OPTIONS)).toBe(2));
    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(count('GET /app/admin/api/yo')).toBe(4);
    expect(count(OPTIONS)).toBe(2);
  });

  it('a space that disappeared leaves the others to choose', async () => {
    const both = adminMe({
      espacios: [
        { id: SPACE, slug: 'corework', nombre: 'CoreWork' },
        { id: OTHER_SPACE, slug: 'north', nombre: 'North Lab' },
      ],
    });
    const onlyOther = adminMe({ espacios: [{ id: OTHER_SPACE, slug: 'north', nombre: 'North Lab' }] });
    serve({
      'GET /app/admin/api/yo': [ok(both), ok(onlyOther)],
      [OPTIONS]: { status: 404, body: { error: 'espacio_no_existe' } },
      [`GET /app/admin/api/espacios/${OTHER_SPACE}/opciones`]: ok(
        options({ espacio: { id: OTHER_SPACE, nombre: 'North Lab', zona_horaria: 'UTC' } }),
      ),
    });
    render(<AdminApp />);
    expect(await screen.findByText('Ese espacio ya no está disponible.')).toBeInTheDocument();
    expect(screen.getByText('Elegí otro espacio arriba.')).toBeInTheDocument();
    expect(offered('espacio')).toEqual(['elegí un espacio', 'North Lab']);
    pick('espacio', OTHER_SPACE);
    expect(await screen.findByRole('form', { name: 'Cargar tarea' })).toBeInTheDocument();
  });

  it('with more than one space, the form follows the chosen one', async () => {
    const calls = serve({
      'GET /app/admin/api/yo': ok(
        adminMe({
          espacios: [
            { id: SPACE, slug: 'corework', nombre: 'CoreWork' },
            { id: OTHER_SPACE, slug: 'north', nombre: 'North Lab' },
          ],
        }),
      ),
      [OPTIONS]: ok(options()),
      [`GET /app/admin/api/espacios/${OTHER_SPACE}/opciones`]: ok(
        options({
          espacio: { id: OTHER_SPACE, nombre: 'North Lab', zona_horaria: 'UTC' },
          objetivos: [{ id: 'n1', titulo: 'Laboratorio nuevo', tipo: 'operativo', estado: 'activo', fecha_objetivo: null }],
        }),
      ),
    });
    render(<AdminApp />);
    await screen.findByRole('form', { name: 'Cargar tarea' });
    pick('espacio', OTHER_SPACE);
    await waitFor(() => expect(calls.map((c) => c.key)).toContain(`GET /app/admin/api/espacios/${OTHER_SPACE}/opciones`));
    await waitFor(() => expect(offered('Objetivo')).toContain('Laboratorio nuevo'));
  });
});

// --- Leda's help from the free box (ADR 0023, point 4; portion J2) ------------------------------

const HELP = `POST /app/admin/api/espacios/${SPACE}/ayuda`;
const BOX = 'Contame qué querés hacer y te ayudo';
const STALE_ANSWER = 'Cambiaste lo escrito mientras Leda completaba; tocá completar de nuevo.';
const STORY =
  'hay que configurar las alarmas del scada que lo haga marcos para el viernes tienen que sonar las 12 en la sala de control';

const proposed = (body: unknown) => ({ status: 200, body });
const FULL = {
  propuesta: {
    objetivo_id: 'o1',
    titulo: 'Configurar las alarmas del SCADA',
    descripcion: 'Configurar las alarmas del SCADA. Tienen que sonar las 12 en la sala de control.',
    responsable_id: 'm-marcos',
    fecha: '2026-10-16',
    criterio: 'Las 12 alarmas suenan en la sala de control.',
  },
  elegir: [],
  avisos: [],
};

function tell(text = STORY) {
  fireEvent.change(screen.getByLabelText(BOX), { target: { value: text } });
}
const askLeda = () => fireEvent.click(screen.getByRole('button', { name: '> completar con Leda' }));
/** The "propuesto por Leda" mark of a field, found from its label. */
function markOf(label: string) {
  const row = screen.getByText(label, { selector: 'label' }).parentElement as HTMLElement;
  return within(row).queryByText('· propuesto por Leda');
}

class FakeRecognition {
  static last: FakeRecognition | null = null;
  lang = '';
  interimResults = true;
  continuous = true;
  onresult: ((e: unknown) => void) | null = null;
  onerror: ((e: { error: string }) => void) | null = null;
  onend: (() => void) | null = null;
  start = vi.fn();
  stop = vi.fn(() => this.onend?.());
  constructor() {
    FakeRecognition.last = this;
  }
}

describe('Leda completes the load from the free box', () => {
  it('fills only the empty fields, marks each one, and ticks the evidence of whoever does it', async () => {
    const calls = await openForm({ [HELP]: proposed(FULL) });
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Mi título' } });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByLabelText('Quién la hace')).toHaveValue('m-marcos'));
    expect(calls.find((c) => c.key === HELP)?.body).toEqual({
      texto: STORY,
      objetivo_id: '',
      titulo: 'Mi título',
      descripcion: '',
      responsable_id: '',
      fecha: '',
      espera_id: '',
      criterio: '',
    });
    // What the person typed stays, without a mark; the rest is proposed and marked.
    expect(screen.getByLabelText('Título')).toHaveValue('Mi título');
    expect(markOf('Título')).toBeNull();
    expect(screen.getByLabelText('Objetivo')).toHaveValue('o1');
    expect(screen.getByLabelText('Descripción (opcional)')).toHaveValue(FULL.propuesta.descripcion);
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveValue(FULL.propuesta.criterio);
    for (const label of ['Objetivo', 'Descripción (opcional)', 'Quién la hace', 'Fecha', 'Criterio de aceptación']) {
      expect(markOf(label)).toBeInTheDocument();
    }
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).toBeChecked();
    expect(
      within(screen.getByRole('group', { name: 'Fecha' })).getByRole('button', { name: 'vie 16.10' }),
    ).toHaveAttribute('aria-pressed', 'true');
    // The free text stays in its box, and the preview shows what was proposed.
    expect(screen.getByLabelText(BOX)).toHaveValue(STORY);
    expect(preview()).toHaveTextContent('Las 12 alarmas suenan en la sala de control.');
  });

  it('a field the person edits loses its mark', async () => {
    await openForm({ [HELP]: proposed(FULL) });
    tell();
    askLeda();
    await waitFor(() => expect(markOf('Criterio de aceptación')).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), { target: { value: 'Suenan las 12' } });
    expect(markOf('Criterio de aceptación')).toBeNull();
    expect(markOf('Descripción (opcional)')).toBeInTheDocument();
  });

  /** Holds Leda's answer until the test releases it, as a slow AI would. */
  async function holdTheAnswer() {
    await openForm();
    let answer: (r: Response) => void = () => {};
    const real = globalThis.fetch;
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string, init?: RequestInit) =>
        url.endsWith('/ayuda') ? new Promise<Response>((resolve) => (answer = resolve)) : real(url, init),
      ),
    );
    return (body: unknown) =>
      answer(new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } }));
  }

  it('a field changed while Leda was answering: the old answer fills nothing, and it says so quietly', async () => {
    // Review review-03b5c3a74d3719b7: the answer was made for what the form had when it was asked.
    const release = await holdTheAnswer();
    tell();
    askLeda();
    expect(screen.getByRole('button', { name: 'completando…' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), { target: { value: 'Lo mío' } });
    release(FULL);
    expect(await screen.findByText(STALE_ANSWER)).toBeInTheDocument();
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveValue('Lo mío');
    expect(screen.getByLabelText('Quién la hace')).toHaveValue('');
    expect(screen.getByLabelText('Título')).toHaveValue('');
    expect(markOf('Criterio de aceptación')).toBeNull();
    expect(markOf('Título')).toBeNull();
    expect(screen.getByRole('button', { name: '> completar con Leda' })).toBeEnabled();
  });

  it('the free text changed while Leda was answering: the old answer fills nothing', async () => {
    const release = await holdTheAnswer();
    tell();
    askLeda();
    tell(`${STORY} y que lo revise ismael`);
    release(FULL);
    expect(await screen.findByText(STALE_ANSWER)).toBeInTheDocument();
    expect(screen.getByLabelText('Título')).toHaveValue('');
    expect(screen.getByLabelText('Quién la hace')).toHaveValue('');
    expect(screen.getByLabelText(BOX)).toHaveValue(`${STORY} y que lo revise ismael`);
  });

  it('nothing changed while Leda was answering: the answer fills the empty fields', async () => {
    const release = await holdTheAnswer();
    tell();
    askLeda();
    release(FULL);
    await waitFor(() => expect(screen.getByLabelText('Quién la hace')).toHaveValue('m-marcos'));
    expect(screen.queryByText(STALE_ANSWER)).toBeNull();
  });

  it('a 422 says why Leda could not complete, and nothing changes', async () => {
    await openForm({
      [HELP]: {
        status: 422,
        body: {
          errores: [
            {
              campo: 'ayuda',
              motivo: 'nada_que_completar',
              texto: 'No queda nada para completar: el formulario ya tiene todo lo que Leda puede proponer.',
            },
          ],
        },
      },
    });
    tell();
    askLeda();
    expect(
      await screen.findByText('No queda nada para completar: el formulario ya tiene todo lo que Leda puede proponer.'),
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Título')).toHaveValue('');
    expect(screen.getByRole('button', { name: '> completar con Leda' })).toBeEnabled();
  });

  it('a 422 without its reasons is never silent: it reads as "could not complete"', async () => {
    await openForm({ [HELP]: { status: 422, body: {} } });
    tell();
    askLeda();
    expect(
      await screen.findByText(
        'Leda no pudo completar ahora. Lo que escribiste sigue acá: completalo vos o probá de nuevo en un rato.',
      ),
    ).toBeInTheDocument();
  });

  it('says what it could not propose, and shows the people to pick without choosing', async () => {
    await openForm({
      [HELP]: proposed({
        propuesta: { titulo: 'Configurar las alarmas del SCADA' },
        elegir: [
          { membership_id: 'm-marcos', nombre: 'Marcos', area: 'Automatización' },
          { membership_id: 'm-lucas', nombre: 'Lucas', area: 'Infraestructura' },
        ],
        avisos: [
          { campo: 'responsable', motivo: 'varios', texto: 'Encontré a más de una persona para el tano: elegí quién la hace.' },
          {
            campo: 'criterio',
            motivo: 'sin_proponer',
            texto: 'No pude proponer el criterio con lo que escribiste; contame cómo se comprueba.',
          },
          {
            campo: 'fecha',
            motivo: 'no_dicha',
            texto: 'No puse la fecha: no encontré en lo que escribiste qué día es; elegila en el calendario.',
          },
        ],
      }),
    });
    tell();
    askLeda();
    expect(
      await screen.findByText('No pude proponer el criterio con lo que escribiste; contame cómo se comprueba.'),
    ).toBeInTheDocument();
    expect(screen.getByText(/No puse la fecha/)).toBeInTheDocument();
    expect(screen.getByLabelText('Quién la hace')).toHaveValue('');
    const pickOne = screen.getByRole('group', { name: 'elegí quién la hace' });
    fireEvent.click(within(pickOne).getByRole('button', { name: 'Lucas · Infraestructura' }));
    expect(screen.getByLabelText('Quién la hace')).toHaveValue('m-lucas');
    // Her choice, not a proposal: no mark, and the choices go.
    expect(markOf('Quién la hace')).toBeNull();
    expect(screen.queryByRole('group', { name: 'elegí quién la hace' })).toBeNull();
  });

  it('a field Leda could not complete says why on that field, in the falta color, and the box lists it', async () => {
    // J2-13, the user's phone retest (2026-10-13): "el tano" is nobody in the team and the help
    // dropped who does it, but the screen said nothing where she was looking.
    const NOBODY = 'No encontré a «el tano» en el equipo; elegí quién la hace.';
    await openForm({
      [HELP]: proposed({
        propuesta: { titulo: 'Cambiar el UPS de la sala de servidores' },
        elegir: [],
        avisos: [
          { campo: 'responsable', motivo: 'no_encontrado', texto: NOBODY },
          { campo: 'criterio', motivo: 'sin_como', texto: 'Contame cómo se sabe que está terminada.' },
        ],
      }),
    });
    tell('hay que cambiar el ups de la sala de servidores que lo vea el tano antes del jueves se corta todo');
    askLeda();
    await waitFor(() => expect(screen.getByLabelText('Título')).toHaveValue('Cambiar el UPS de la sala de servidores'));
    const onField = document.getElementById('f-responsable-error') as HTMLElement;
    expect(onField).toHaveTextContent(NOBODY);
    expect(onField).toHaveClass('text-falta');
    expect(onField.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
    expect(screen.getByLabelText('Quién la hace')).toHaveAttribute('aria-describedby', 'f-responsable-error');
    expect(document.getElementById('f-criterio-error')).toHaveTextContent('Contame cómo se sabe que está terminada.');
    // Near the box, what it could not complete, in the order of the form.
    const listed = screen.getByText('No pude completar: quién la hace, criterio de aceptación.');
    expect(listed.closest('p')).toHaveClass('text-falta');
    // Each message goes when the person fills its field.
    pick('Quién la hace', 'm-marcos');
    expect(document.getElementById('f-responsable-error')).toBeNull();
    expect(document.getElementById('f-criterio-error')).toHaveTextContent('Contame cómo se sabe que está terminada.');
  });

  it('the box names only the fields still missing: filling one takes it out of the summary too', async () => {
    // Review review-97374544422a6d97: the summary came from the frozen answer, so a field the
    // person had already filled was still named there after its own notice went.
    const OTHER = 'Lo demás lo completé con lo que escribiste.';
    await openForm({
      [HELP]: proposed({
        propuesta: { titulo: 'Cambiar el UPS de la sala de servidores' },
        elegir: [],
        avisos: [
          { campo: 'responsable', motivo: 'no_encontrado', texto: 'No encontré a «el tano» en el equipo; elegí quién la hace.' },
          { campo: 'criterio', motivo: 'sin_como', texto: 'Contame cómo se sabe que está terminada.' },
          { campo: 'general', motivo: 'nota', texto: OTHER },
        ],
      }),
    });
    tell('hay que cambiar el ups de la sala de servidores que lo vea el tano antes del jueves se corta todo');
    askLeda();
    expect(
      await screen.findByText('No pude completar: quién la hace, criterio de aceptación.'),
    ).toBeInTheDocument();
    expect(screen.getByText(OTHER)).toBeInTheDocument();
    pick('Quién la hace', 'm-marcos');
    expect(screen.queryByText(/No pude completar: quién la hace/)).toBeNull();
    expect(screen.getByText('No pude completar: criterio de aceptación.')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), {
      target: { value: 'El UPS nuevo sostiene la sala 10 minutos con la red cortada.' },
    });
    expect(screen.queryByText(/No pude completar/)).toBeNull();
    // A note that belongs to no field stays until she asks again.
    expect(screen.getByText(OTHER)).toBeInTheDocument();
  });

  it('while Leda completes, the three dots fade in and out one after another, always', async () => {
    // The user (2026-10-13): "quiero que se animen siempre", also with reduced motion; so only the
    // opacity changes, with no movement, scaling or bouncing.
    const release = await holdTheAnswer();
    tell();
    askLeda();
    const button = screen.getByRole('button', { name: 'completando…' });
    const dots = Array.from(button.querySelectorAll('.animate-puntos'));
    expect(dots).toHaveLength(3);
    expect(dots.map((d) => d.textContent)).toEqual(['.', '.', '.']);
    expect(new Set(dots.map((d) => d.className)).size).toBe(3);
    expect(button.innerHTML).not.toMatch(/motion-reduce|motion-safe/);
    // @ts-expect-error -- this browser project has no Node types; the tests run on Node.
    const { readFileSync } = await import('node:fs');
    // @ts-expect-error -- the same: `dirname` is Node's, not in the browser's `ImportMeta`.
    const here: string = import.meta.dirname;
    const css: string = readFileSync(`${here}/../index.css`, 'utf-8');
    expect(css).toMatch(/--animate-puntos:\s*puntos\s[^;]*infinite/);
    const keyframes = css.match(/@keyframes puntos\s*\{([\s\S]*?\})\s*\}/)?.[1] ?? '';
    expect(keyframes).toMatch(/opacity/);
    expect(keyframes).not.toMatch(/transform|scale|translate|rotate|top|left|margin/);
    release(FULL);
    await waitFor(() => expect(screen.getByRole('button', { name: '> completar con Leda' })).toBeEnabled());
  });

  it('when Leda cannot answer it says so plainly and nothing changes', async () => {
    await openForm({ [HELP]: { status: 503, body: { error: 'sin_ayuda', texto: 'x' } } });
    fireEvent.change(screen.getByLabelText('Título'), { target: { value: 'Mi título' } });
    tell();
    askLeda();
    expect(
      await screen.findByText(
        'Leda no pudo completar ahora. Lo que escribiste sigue acá: completalo vos o probá de nuevo en un rato.',
      ),
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Título')).toHaveValue('Mi título');
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveValue('');
    expect(screen.getByLabelText(BOX)).toHaveValue(STORY);
    expect(screen.getByRole('button', { name: '> completar con Leda' })).toBeEnabled();
  });

  it('with the box empty it asks to tell first, without calling Leda', async () => {
    const calls = await openForm({ [HELP]: proposed(FULL) });
    askLeda();
    expect(screen.getByText('Contame primero qué querés hacer; con eso Leda completa lo que pueda.')).toBeInTheDocument();
    expect(calls.some((c) => c.key === HELP)).toBe(false);
  });

  it('never fills a field with what the options do not offer', async () => {
    await openForm({
      [HELP]: proposed({
        propuesta: { responsable_id: 'm-de-otro-lado', objetivo_id: 'o-cerrado', fecha: '2026-10-17', titulo: 'Configurar' },
        elegir: [],
        avisos: [],
      }),
    });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByLabelText('Título')).toHaveValue('Configurar'));
    expect(screen.getByLabelText('Quién la hace')).toHaveValue('');
    expect(screen.getByLabelText('Objetivo')).toHaveValue('');
    expect(markOf('Fecha')).toBeNull();
  });

  it('confirm after the proposals loads once, with what the preview shows', async () => {
    keys('33333333-3333-4333-8333-333333333333');
    const calls = await openForm({ [HELP]: proposed(FULL), [TASKS]: loaded() });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByLabelText('Quién la hace')).toHaveValue('m-marcos'));
    pick('Quién la decidió', 'm-ismael');
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS);
    expect(sent).toHaveLength(1);
    expect(sent[0].body).toEqual({
      ...FULL.propuesta,
      evidencia: ['captura'],
      decidio_id: 'm-ismael',
      clave: '33333333-3333-4333-8333-333333333333',
    });
    // "cargar otra" starts over, the box too.
    fireEvent.click(screen.getByRole('button', { name: '> cargar otra' }));
    expect(screen.getByLabelText(BOX)).toHaveValue('');
  });
});

describe('Dictating into the free box', () => {
  it('without speech recognition there is no microphone, and typing works', async () => {
    await openForm();
    expect(screen.queryByRole('button', { name: '> dictar' })).toBeNull();
    tell('lo escribo');
    expect(screen.getByLabelText(BOX)).toHaveValue('lo escribo');
  });

  it('where the browser recognizes speech, what is heard goes into the box', async () => {
    vi.stubGlobal('webkitSpeechRecognition', FakeRecognition);
    await openForm();
    tell('hay que');
    fireEvent.click(screen.getByRole('button', { name: '> dictar' }));
    const r = FakeRecognition.last as FakeRecognition;
    expect(r.start).toHaveBeenCalledTimes(1);
    expect(r.lang).toBe('es-AR');
    expect(screen.getByRole('button', { name: '> dejar de dictar' })).toHaveAttribute('aria-pressed', 'true');
    act(() => r.onresult?.({ resultIndex: 0, results: [[{ transcript: 'colgar el estante' }]] }));
    expect(screen.getByLabelText(BOX)).toHaveValue('hay que colgar el estante');
    fireEvent.click(screen.getByRole('button', { name: '> dejar de dictar' }));
    expect(r.stop).toHaveBeenCalled();
    expect(screen.getByRole('button', { name: '> dictar' })).toHaveAttribute('aria-pressed', 'false');
  });

  it('without permission it says so plainly and the box stays', async () => {
    vi.stubGlobal('SpeechRecognition', FakeRecognition);
    await openForm();
    tell('lo que ya escribí');
    fireEvent.click(screen.getByRole('button', { name: '> dictar' }));
    const r = FakeRecognition.last as FakeRecognition;
    act(() => {
      r.onerror?.({ error: 'not-allowed' });
      r.onend?.();
    });
    expect(screen.getByText('No tengo permiso para el micrófono; escribilo acá.')).toBeInTheDocument();
    expect(screen.getByLabelText(BOX)).toHaveValue('lo que ya escribí');
    expect(screen.getByLabelText(BOX)).toBeEnabled();
  });
});
