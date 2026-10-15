import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { adminMe, options, OTHER_SPACE, SPACE } from '../test/adminFixtures';
import { AdminApp } from './AdminApp';
import { newKey } from './draft';
import { CONTROL, FIELD_HINT, FIELD_TITLE, FIELD_VALUE, PREVIEW_VALUE, TEXT_SIZE } from './typography';

type Reply = { status: number; body?: unknown } | 'network';
type Call = { key: string; body: unknown; headers?: HeadersInit };

const TASKS = `POST /app/admin/api/espacios/${SPACE}/tareas`;
const OPTIONS = `GET /app/admin/api/espacios/${SPACE}/opciones`;
// J2-17: before loading, Leda checks the spelling of the text fields. By default nothing to
// correct, so the tests that do not look at it load as before.
const SPELLING = `POST /app/admin/api/espacios/${SPACE}/ortografia`;
const NOTHING_TO_CORRECT = { status: 200, body: { corregidos: {}, sin_revisar: [] } };
// J2-21: before the spelling, what the load would refuse. By default it would load.
const REVIEW = `POST /app/admin/api/espacios/${SPACE}/tareas/revisar`;
const WOULD_LOAD = { status: 200, body: { errores: [] } };

/** A fake server: each route answers with its replies in order (the last one repeats). */
function serve(routes: Record<string, Reply | Reply[]>) {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      // JSON as sent, read back; anything else (the dictated audio, J2b) as it is.
      const sentBody = typeof init?.body === 'string' ? JSON.parse(init.body) : (init?.body ?? undefined);
      calls.push({ key, body: sentBody, headers: init?.headers });
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
    [SPELLING]: NOTHING_TO_CORRECT,
    [REVIEW]: WOULD_LOAD,
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
  // J2-19: choosing who does it ticks nothing; the person ticks the evidence.
  fireEvent.click(screen.getByRole('checkbox', { name: /una captura de pantalla/ }));
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

  it('choosing who does it ticks nothing: what the area asks for is only said next to it (J2-19)', async () => {
    await openForm();
    pick('Quién la hace', 'm-marcos');
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).not.toBeChecked();
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla · la pide el área/ })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: /un informe/ })).not.toBeChecked();
    // Nothing ticked: the form says the evidence is missing.
    expect(document.getElementById('lo-que-falta')).toHaveTextContent('evidencia');
    fireEvent.click(screen.getByRole('checkbox', { name: /un informe/ }));
    // Another person whose area knows it: what the person ticked stays, nothing new is ticked.
    pick('Quién la hace', 'm-marcos');
    expect(screen.getByRole('checkbox', { name: /un informe/ })).toBeChecked();
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).not.toBeChecked();
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
      // J2-19: nothing is ticked on its own, so the evidence is missing.
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
            { campo: 'espera', motivo: 'esta_cerrada', texto: 'La tarea que espera ya está cerrada: otra no puede quedar esperándola.' },
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

  // Decision 6 of the user (2026-10-14; migration 0070): a task never falls due after its
  // objective. Leda stops before loading and says why; the way out is a date up to that day.
  const LATE =
    'Esta tarea vence después que «Puesta en marcha de la línea 3» (30.10): el objetivo se demoraría. Para cargarla ahora, elegí una fecha hasta ese día.';

  it('stops a task that falls due after its objective: confirm is disabled and says why', async () => {
    const calls = await openForm({ [TASKS]: loaded() });
    fillTask();
    fireEvent.click(screen.getByRole('button', { name: 'mes siguiente' }));
    fireEvent.click(screen.getByRole('button', { name: 'lun 02.11' }));
    // Before any tap: next to confirm and on the date, in plain words with the objective's name.
    expect(within(preview().parentElement as HTMLElement).getAllByText(LATE).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: '> confirmar' })).toHaveAttribute('aria-disabled', 'true');
    expect(screen.queryByText(/se avisa, no se bloquea/)).toBeNull();
    confirm();
    // Nothing is sent; the tap takes the person to the date, which says it.
    expect(calls.some((c) => c.key === TASKS || c.key === REVIEW)).toBe(false);
    expect(document.getElementById('f-fecha-error')).toHaveTextContent(LATE);
    // A date up to the objective's day: the conflict goes, and it loads.
    fireEvent.click(screen.getByRole('button', { name: 'mes anterior' }));
    fireEvent.click(screen.getByRole('button', { name: 'vie 30.10' }));
    expect(screen.queryByText(LATE)).toBeNull();
    expect(screen.getByRole('button', { name: '> confirmar' })).not.toHaveAttribute('aria-disabled');
    confirm();
    await screen.findByRole('heading', { name: 'Tarea cargada.' });
    expect(calls.filter((c) => c.key === TASKS)).toHaveLength(1);
  });

  it('an objective without a date sets no limit, and changing the objective clears the stop', async () => {
    await openForm();
    fillTask();
    fireEvent.click(screen.getByRole('button', { name: 'mes siguiente' }));
    fireEvent.click(screen.getByRole('button', { name: 'lun 02.11' }));
    confirm();
    expect(document.getElementById('f-fecha-error')).toHaveTextContent(LATE);
    pick('Objetivo', 'o2');
    expect(screen.queryByText(LATE)).toBeNull();
    expect(document.getElementById('f-fecha-error')).toBeNull();
    expect(screen.getByRole('button', { name: '> confirmar' })).not.toHaveAttribute('aria-disabled');
  });

  it('the server refusing a late date lands on the date with the day it says', async () => {
    await openForm({
      [REVIEW]: {
        status: 422,
        body: {
          errores: [
            {
              campo: 'fecha',
              motivo: 'vence_despues_del_objetivo',
              texto: 'Esta tarea vence después que su objetivo: el objetivo se demoraría. Para cargarla ahora, elegí una fecha hasta la del objetivo.',
              hasta: '2026-10-14',
            },
          ],
        },
      },
    });
    fillTask();
    confirm();
    await screen.findByRole('alert');
    expect(screen.getByRole('group', { name: 'Fecha' })).toBeInTheDocument();
    expect(document.getElementById('f-fecha-error')).toHaveTextContent('Para cargarla ahora, elegí una fecha hasta la del objetivo.');
  });

  it('a retry after a network failure keeps the data and the key', async () => {
    keys('22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333');
    const calls = await openForm({ [TASKS]: ['network', loaded()] });
    fillTask();
    confirm();
    // While it is sending, what is shown is what goes: the form is locked.
    // J2-17: first Leda checks the spelling ("revisando…"), then it loads; locked all along.
    expect(screen.getByLabelText('Título')).toBeDisabled();
    expect(screen.getByRole('button', { name: 'revisando…' })).toBeDisabled();
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
    // J2-17: the load starts once the spelling check answered.
    const button = await screen.findByRole('button', { name: 'cargando…' });
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
    // ADR 0024: never a link; the administration's sign-in (with Telegram) takes the page.
    expect(await screen.findByText(/Entrá con Telegram|Esta dirección no sirve/)).toBeInTheDocument();
    expect(screen.queryByText(/enlace nuevo/)).toBeNull();
    expect(screen.queryByRole('form')).toBeNull();
  });

  it('makes a valid key where randomUUID is missing (plain HTTP)', () => {
    vi.stubGlobal('crypto', { getRandomValues: (a: Uint8Array) => a.fill(171) });
    expect(newKey()).toBe('ab'.repeat(16));
  });

  it('without a session there is no form', async () => {
    serve({ 'GET /app/admin/api/yo': { status: 401, body: { error: 'sin_sesion' } } });
    render(<AdminApp />);
    expect(await screen.findByText(/Entrá con Telegram|Esta dirección no sirve/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Cerrar sesión' })).toBeNull();
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
    evidencia: ['captura'],
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

/** A fake MediaRecorder (J2b): it records in webm/opus and, stopped, gives one piece of audio. */
class FakeRecorder {
  static last: FakeRecorder | null = null;
  static isTypeSupported = (type: string) => type === 'audio/webm;codecs=opus';
  state: 'inactive' | 'recording' = 'inactive';
  mimeType: string;
  ondataavailable: ((event: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: (() => void) | null = null;
  start = vi.fn(() => {
    this.state = 'recording';
  });
  stop = vi.fn(() => {
    if (this.state === 'inactive') return;
    this.state = 'inactive';
    this.ondataavailable?.({ data: new Blob(['audio dictado'], { type: this.mimeType }) });
    this.onstop?.();
  });
  constructor(_stream: MediaStream, options?: { mimeType?: string }) {
    this.mimeType = options?.mimeType ?? '';
    FakeRecorder.last = this;
  }
}

/** The microphone and the screen lock of the phone, faked on `navigator` (taken away after each
 * test by `forgetMicrophone`). */
function fakeMicrophone(allow: 'yes' | 'denied' = 'yes') {
  vi.stubGlobal('MediaRecorder', FakeRecorder);
  const track = { stop: vi.fn() };
  const getUserMedia = vi.fn(async () => {
    if (allow === 'denied') throw new DOMException('no', 'NotAllowedError');
    return { getTracks: () => [track] } as unknown as MediaStream;
  });
  const release = vi.fn(async () => {});
  const request = vi.fn(async () => ({ release, addEventListener: vi.fn() }));
  Object.defineProperty(navigator, 'mediaDevices', { value: { getUserMedia }, configurable: true });
  Object.defineProperty(navigator, 'wakeLock', { value: { request }, configurable: true });
  return { getUserMedia, track, request, release };
}

function forgetMicrophone() {
  for (const key of ['mediaDevices', 'wakeLock'] as const) {
    if (Object.getOwnPropertyDescriptor(navigator, key)) delete (navigator as unknown as Record<string, unknown>)[key];
  }
}

describe('Leda completes the load from the free box', () => {
  it('fills only the empty fields, marks each one, and ticks only the evidence Leda proposed', async () => {
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
      // J2-18: the evidence already ticked goes too, so Leda never proposes over it.
      evidencia: [],
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
    expect(screen.getByRole('checkbox', { name: /un informe/ })).not.toBeChecked();
    expect(
      within(screen.getByRole('group', { name: 'Fecha' })).getByRole('button', { name: 'vie 16.10' }),
    ).toHaveAttribute('aria-pressed', 'true');
    // The free text stays in its box, and the preview shows what was proposed.
    expect(screen.getByLabelText(BOX)).toHaveValue(STORY);
    expect(preview()).toHaveTextContent('Las 12 alarmas suenan en la sala de control.');
  });

  it('a date Leda fills after the objective stops the load the same way (decision 6)', async () => {
    const calls = await openForm({
      [HELP]: proposed({ ...FULL, propuesta: { ...FULL.propuesta, fecha: '2026-11-02' } }),
    });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByLabelText('Objetivo')).toHaveValue('o1'));
    pick('Quién la decidió', 'm-ismael');
    expect(screen.getAllByText(/Esta tarea vence después que «Puesta en marcha de la línea 3» \(30\.10\)/).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: '> confirmar' })).toHaveAttribute('aria-disabled', 'true');
    confirm();
    expect(calls.some((c) => c.key === TASKS || c.key === REVIEW)).toBe(false);
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

  it('the evidence changed while Leda was answering: the old answer fills nothing (R3-001)', async () => {
    const release = await holdTheAnswer();
    pick('Quién la hace', 'm-marcos');
    tell();
    askLeda();
    fireEvent.click(screen.getByRole('checkbox', { name: /un informe/ }));
    release(FULL);
    expect(await screen.findByText(STALE_ANSWER)).toBeInTheDocument();
    expect(screen.getByLabelText('Título')).toHaveValue('');
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).not.toBeChecked();
  });

  it('evidence ticked and unticked while Leda was answering is the same evidence: the answer fills', async () => {
    const release = await holdTheAnswer();
    pick('Quién la hace', 'm-marcos');
    tell();
    askLeda();
    fireEvent.click(screen.getByRole('checkbox', { name: /un informe/ }));
    fireEvent.click(screen.getByRole('checkbox', { name: /un informe/ }));
    release(FULL);
    await waitFor(() => expect(screen.getByLabelText('Título')).toHaveValue(FULL.propuesta.titulo));
    expect(screen.queryByText(STALE_ANSWER)).toBeNull();
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

// J2b: the browser records and the server turns the audio into text with Gemini.
const DICTATION = `POST /app/admin/api/espacios/${SPACE}/dictado`;

/** Holds the server's answers to one route until the test gives them, in order, to see what shows
 * meanwhile; the other routes answer as `serve` says. `held` counts the calls to that route. */
function hold(route: string) {
  const served = globalThis.fetch;
  const waiting: ((response: Response) => void)[] = [];
  const held = { count: 0, bodies: [] as unknown[] };
  vi.stubGlobal(
    'fetch',
    vi.fn((url: string, init?: RequestInit) => {
      if (`${init?.method ?? 'GET'} ${url}` !== route) return served(url, init);
      held.count += 1;
      held.bodies.push(typeof init?.body === 'string' ? JSON.parse(init.body) : init?.body);
      return new Promise<Response>((resolve) => {
        waiting.push(resolve);
      });
    }),
  );
  const answer = (status: number, body: unknown) =>
    act(async () => {
      waiting.shift()?.(new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }));
    });
  return { answer, held };
}

const holdDictation = () => hold(DICTATION).answer;

// J2-28: the microphone is an icon of constant width, named by its `aria-label`.
async function startDictating() {
  fireEvent.click(screen.getByRole('button', { name: 'dictar' }));
  return screen.findByRole('button', { name: 'dejar de dictar' });
}

/** J2-27: a Web Audio of mentira, whose analyser gives a voice at the level of `loud` (0 to 1). */
function fakeAudio(loud = 0.5) {
  const made: { resume: ReturnType<typeof vi.fn>; close: ReturnType<typeof vi.fn> }[] = [];
  class FakeAudioContext {
    state = 'suspended';
    resume = vi.fn(async () => {
      this.state = 'running';
    });
    close = vi.fn(async () => {
      this.state = 'closed';
    });
    constructor() {
      made.push(this);
    }
    createMediaStreamSource() {
      return { connect: vi.fn(), disconnect: vi.fn() };
    }
    createAnalyser() {
      return {
        fftSize: 2048,
        getByteTimeDomainData(samples: Uint8Array) {
          samples.forEach((_, i) => {
            samples[i] = 128 + Math.round((i % 2 ? 1 : -1) * loud * 127);
          });
        },
      };
    }
  }
  vi.stubGlobal('AudioContext', FakeAudioContext);
  return made;
}

describe('Dictating into the free box', () => {
  afterEach(() => forgetMicrophone());

  it('where the browser cannot record there is no microphone, and typing works', async () => {
    await openForm();
    expect(screen.queryByRole('button', { name: 'dictar' })).toBeNull();
    tell('lo escribo');
    expect(screen.getByLabelText(BOX)).toHaveValue('lo escribo');
  });

  it('records, shows it is recording, and the text Leda heard goes after what was written', async () => {
    const mic = fakeMicrophone();
    const calls = await openForm({ [DICTATION]: ok({ texto: 'colgar el estante del módem' }) });
    tell('hay que');
    const stop = await startDictating();
    expect(stop).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByText(/grabando · 0:00 de 2:00/)).toBeInTheDocument();
    expect(mic.request).toHaveBeenCalledWith('screen');
    fireEvent.click(stop);
    await waitFor(() => expect(screen.getByLabelText(BOX)).toHaveValue('hay que colgar el estante del módem'));
    const sent = calls.find((c) => c.key === DICTATION);
    expect(sent?.body).toBeInstanceOf(Blob);
    expect(sent?.headers).toEqual(expect.objectContaining({ 'Content-Type': 'audio/webm;codecs=opus' }));
    // The microphone and the screen go back as they were; the box is still the person's to edit.
    expect(mic.track.stop).toHaveBeenCalled();
    expect(mic.release).toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'dictar' })).toHaveAttribute('aria-pressed', 'false');
    expect(screen.getByLabelText(BOX)).toBeEnabled();
    expect(screen.queryByText(/grabando/)).toBeNull();
  });

  it('a dictation cut by the limit adds what was heard and says it was cut (J2-26)', async () => {
    fakeMicrophone();
    const cut = 'Pasé a texto sólo una parte: el dictado se cortó. Dictá lo que falta o escribilo acá.';
    await openForm({ [DICTATION]: ok({ texto: 'colgar el estante', aviso: cut }) });
    fireEvent.click(await startDictating());
    await waitFor(() => expect(screen.getByLabelText(BOX)).toHaveValue('colgar el estante'));
    expect(screen.getByText(cut)).toBeInTheDocument();
  });

  it('the microphone is an icon of the same width in both states, next to "completar" (J2-28)', async () => {
    fakeMicrophone();
    await openForm();
    const mic = screen.getByRole('button', { name: 'dictar' });
    const complete = screen.getByRole('button', { name: '> completar con Leda' });
    expect(mic).toHaveAttribute('title', 'dictar');
    expect(mic.textContent).toBe('');
    expect(mic.querySelector('svg')).not.toBeNull();
    expect(mic.className).toMatch(/\bw-11\b/);
    expect(mic.className).toMatch(/\bh-11\b/);
    expect(complete.className).toMatch(/\bh-11\b/);
    // On the same line: one row that does not wrap.
    expect(mic.parentElement).toBe(complete.parentElement);
    expect(mic.parentElement?.className).not.toMatch(/flex-wrap/);
    const stop = await startDictating();
    expect(stop).toHaveAttribute('title', 'dejar de dictar');
    expect(stop.textContent).toBe('');
    expect(stop.className).toBe(mic.className);
    // The recording line stays below the buttons.
    expect(stop.parentElement?.contains(screen.getByText(/grabando · 0:00 de 2:00/))).toBe(false);
  });

  it('the help under the box says it can be written or dictated (J2-28)', async () => {
    await openForm();
    expect(screen.getByLabelText(BOX)).toHaveAccessibleDescription(
      'Escribilo o dictalo como lo dirías; Leda completa lo que falta.',
    );
  });

  it('while recording, bars move with the voice, and go away when it stops (J2-27)', async () => {
    fakeMicrophone();
    const contexts = fakeAudio(0.6);
    await openForm({ [DICTATION]: ok({ texto: 'colgar el estante' }) });
    const stop = await startDictating();
    // Made and resumed in the tap itself (Safari on the iPhone only lets it play from a tap).
    expect(contexts).toHaveLength(1);
    expect(contexts[0].resume).toHaveBeenCalled();
    const bars = await screen.findByTestId('audio-bars');
    await waitFor(() => {
      const heights = [...bars.children].map((b) => (b as HTMLElement).style.height);
      expect(heights.some((h) => h !== '' && h !== '12%')).toBe(true);
    });
    fireEvent.click(stop);
    await waitFor(() => expect(screen.queryByTestId('audio-bars')).toBeNull());
    expect(contexts[0].close).toHaveBeenCalled();
  });

  it('without Web Audio it records all the same, with no bars (J2-27)', async () => {
    fakeMicrophone();
    await openForm();
    await startDictating();
    expect(screen.getByText(/grabando · 0:00 de 2:00/)).toBeInTheDocument();
    expect(screen.queryByTestId('audio-bars')).toBeNull();
  });

  it('after a sentence that ends, the dictated text starts a new line', async () => {
    fakeMicrophone();
    await openForm({ [DICTATION]: ok({ texto: 'Que lo haga Lucas.' }) });
    tell('Colgar el estante.');
    fireEvent.click(await startDictating());
    await waitFor(() => expect(screen.getByLabelText(BOX)).toHaveValue('Colgar el estante.\nQue lo haga Lucas.'));
  });

  it('while the audio turns into text, the button says so with its dots', async () => {
    fakeMicrophone();
    await openForm();
    const answer = holdDictation();
    fireEvent.click(await startDictating());
    const busy = await screen.findByRole('button', { name: 'pasando a texto…' });
    expect(busy).toBeDisabled();
    // J2-28: the icon keeps its width; the words with their dots go on the line below.
    expect(busy.textContent).toBe('');
    expect(busy.parentElement?.parentElement).toHaveTextContent('pasando a texto...');
    await answer(200, { texto: 'colgar el estante' });
    expect(screen.getByLabelText(BOX)).toHaveValue('colgar el estante');
    expect(screen.getByRole('button', { name: 'dictar' })).toBeEnabled();
  });

  it('without permission it says so plainly and the box stays', async () => {
    fakeMicrophone('denied');
    await openForm();
    tell('lo que ya escribí');
    fireEvent.click(screen.getByRole('button', { name: 'dictar' }));
    expect(await screen.findByText('No tengo permiso para el micrófono; escribilo acá.')).toBeInTheDocument();
    expect(screen.getByLabelText(BOX)).toHaveValue('lo que ya escribí');
    expect(screen.getByLabelText(BOX)).toBeEnabled();
    expect(screen.getByRole('button', { name: 'dictar' })).toBeEnabled();
  });

  it('when Leda could not turn it into text, it says so and what was written stays', async () => {
    fakeMicrophone();
    await openForm({ [DICTATION]: { status: 502, body: { error: 'sin_dictado', texto: 'x' } } });
    tell('lo que ya escribí');
    fireEvent.click(await startDictating());
    expect(
      await screen.findByText('No pude pasar el audio a texto ahora. Probá de nuevo en un rato o escribilo acá.'),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(BOX)).toHaveValue('lo que ya escribí');
  });

  it('when nothing could be understood, it says so in its words', async () => {
    fakeMicrophone();
    await openForm({
      [DICTATION]: { status: 422, body: { error: 'no_se_entendio', texto: 'No te entendí; probá de nuevo o escribilo acá.' } },
    });
    fireEvent.click(await startDictating());
    expect(await screen.findByText('No te entendí; probá de nuevo o escribilo acá.')).toBeInTheDocument();
    expect(screen.getByLabelText(BOX)).toHaveValue('');
  });

  it('a session that closed while dictating goes back to the entry', async () => {
    fakeMicrophone();
    await openForm({ [DICTATION]: { status: 401, body: { error: 'sin_sesion' } } });
    fireEvent.click(await startDictating());
    await waitFor(() => expect(screen.queryByRole('form', { name: 'Cargar tarea' })).toBeNull());
  });
});

// J2-17 and J2-23: on confirm, Leda corrects the spelling of what the person typed (and writes the
// team's names as they are in the data), never the wording, and the corrected text loads in the same
// confirm, unmarked (the user: "que lo corrija directamente sin resaltarlo").
describe('the spelling before loading', () => {
  const corrected = (fields: Record<string, { texto: string; cambios: { antes: string; despues: string }[] }>) => ({
    status: 200,
    body: { corregidos: fields, sin_revisar: [] },
  });
  const TITLE_FIX = {
    titulo: {
      texto: 'Configurar las alarmas del SCADA con CoreLabs',
      cambios: [
        { antes: 'configurar', despues: 'Configurar' },
        { antes: 'scada', despues: 'SCADA' },
        { antes: 'cirelabs', despues: 'CoreLabs' },
      ],
    },
  };

  function typeTitle(value: string) {
    fireEvent.change(screen.getByLabelText('Título'), { target: { value } });
  }

  /** Nothing in the page says or shows that Leda corrected the spelling (J2-23). */
  function expectNoSpellingMark() {
    expect(screen.queryByText(/Leda corrigió la ortografía/)).toBeNull();
    expect(screen.queryByText(/ortografía corregida/)).toBeNull();
    expect(document.querySelector('[data-corrected], [data-spelling]')).toBeNull();
  }

  it('one confirm loads the corrected text, and nothing marks the correction', async () => {
    const calls = await openForm({ [SPELLING]: corrected(TITLE_FIX), [TASKS]: loaded() });
    fillTask();
    typeTitle('configurar las alarmas del scada con cirelabs');
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    expect(calls.find((c) => c.key === SPELLING)?.body).toEqual({
      titulo: 'configurar las alarmas del scada con cirelabs',
      criterio: 'Las 12 alarmas suenan en la sala de control',
    });
    const sent = calls.filter((c) => c.key === TASKS);
    expect(sent).toHaveLength(1);
    expect((sent[0].body as { titulo: string }).titulo).toBe('Configurar las alarmas del SCADA con CoreLabs');
    // The task as it loaded, with the corrected words written as any other.
    expect(screen.getByText('Configurar las alarmas del SCADA con CoreLabs')).toBeInTheDocument();
    expectNoSpellingMark();
  });

  it('a load refused after the correction keeps the corrected text, and the next confirm loads it without checking it again', async () => {
    const refused = {
      status: 422,
      body: { errores: [{ campo: 'fecha', motivo: 'no_es_dia_habil', texto: 'Ese día no es hábil en este espacio.' }] },
    };
    const calls = await openForm({ [SPELLING]: corrected(TITLE_FIX), [TASKS]: [refused, loaded()] });
    fillTask();
    typeTitle('configurar las alarmas del scada con cirelabs');
    confirm();
    expect(await screen.findByText('Ese día no es hábil en este espacio.')).toBeInTheDocument();
    expect(screen.getByLabelText('Título')).toHaveValue('Configurar las alarmas del SCADA con CoreLabs');
    expectNoSpellingMark();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { titulo: string }).titulo);
    expect(sent).toEqual(['Configurar las alarmas del SCADA con CoreLabs', 'Configurar las alarmas del SCADA con CoreLabs']);
    expect(calls.filter((c) => c.key === SPELLING)).toHaveLength(1);
  });

  it('an edited text is checked again before loading', async () => {
    const refused = {
      status: 422,
      body: { errores: [{ campo: 'fecha', motivo: 'no_es_dia_habil', texto: 'Ese día no es hábil en este espacio.' }] },
    };
    const calls = await openForm({
      [SPELLING]: [corrected(TITLE_FIX), NOTHING_TO_CORRECT],
      [TASKS]: [refused, loaded()],
    });
    fillTask();
    typeTitle('configurar las alarmas del scada con cirelabs');
    confirm();
    expect(await screen.findByText('Ese día no es hábil en este espacio.')).toBeInTheDocument();
    typeTitle('Configurar las alarmas del SCADA');
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const checks = calls.filter((c) => c.key === SPELLING);
    expect(checks).toHaveLength(2);
    expect(checks[1].body).toEqual({ titulo: 'Configurar las alarmas del SCADA' });
  });

  it.each([
    ['the AI does not answer', { status: 200, body: { corregidos: {}, sin_revisar: ['titulo', 'criterio'], aviso: 'No pude revisar la ortografía ahora: quedó como lo escribiste.' } }],
    ['there is no answer at all', 'network' as const],
  ])('when %s nothing blocks: the task loads as written, and the person is told', async (_, reply) => {
    const calls = await openForm({ [SPELLING]: reply, [TASKS]: loaded() });
    fillTask();
    typeTitle('configurar las alarmas del scada');
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS);
    expect((sent[0].body as { titulo: string }).titulo).toBe('configurar las alarmas del scada');
    expect(screen.getByText('No pude revisar la ortografía ahora: quedó como lo escribiste.')).toBeInTheDocument();
  });

  it('a closed session while checking goes back to the door', async () => {
    const calls = await openForm({ [SPELLING]: { status: 401 } });
    fillTask();
    confirm();
    await waitFor(() => expect(screen.queryByRole('form', { name: 'Cargar tarea' })).toBeNull());
    expect(calls.some((c) => c.key === TASKS)).toBe(false);
  });
});

// --- J2-18: Leda completes everything it can --------------------------------------------------------
//
// Leda proposes who does it and the evidence that fits this task; the person reviews, corrects or
// keeps it. J2-19: only the evidence Leda proposed is ticked (and marked); what the area asks for is
// said next to it, never ticked on its own; and a text the spelling check could not check is checked
// again.

// J2-24 (the user: "la ortografía la idea es que la corrija en la vista previa, sin tener que apretar
// confirmar"; and then: the preview must not look wrong until the person leaves the field): after a
// pause in the typing, the preview shows the text corrected; the field takes it when she leaves it.
describe('the spelling while typing (J2-24)', () => {
  const TYPED = 'configurar las alarmas del scada con cirelabs';
  const FIXED = 'Configurar las alarmas del SCADA con CoreLabs';
  const fixTitle = {
    status: 200,
    body: { corregidos: { titulo: { texto: FIXED, cambios: [{ antes: 'scada', despues: 'SCADA' }] } }, sin_revisar: [] },
  };
  const title = () => screen.getByLabelText('Título');
  const typeTitle = (value: string) => fireEvent.change(title(), { target: { value } });
  const pause = (ms = 1500) =>
    act(async () => {
      await vi.advanceTimersByTimeAsync(ms);
    });
  const spellingCalls = (calls: Call[]) => calls.filter((c) => c.key === SPELLING);

  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('after a pause the preview shows the text corrected; the field takes it only when the person leaves it', async () => {
    const calls = await openForm({ [SPELLING]: fixTitle });
    title().focus();
    typeTitle(TYPED);
    await pause(1000);
    expect(spellingCalls(calls)).toHaveLength(0);
    await pause(500);
    await waitFor(() => expect(within(preview()).getByText(FIXED)).toBeInTheDocument());
    expect(spellingCalls(calls).map((c) => c.body)).toEqual([{ titulo: TYPED }]);
    // Never under her cursor.
    expect(title()).toHaveValue(TYPED);
    fireEvent.blur(title());
    expect(title()).toHaveValue(FIXED);
    expect(within(preview()).getByText(FIXED)).toBeInTheDocument();
    // Nothing marks it (J2-23), and a text already checked is not checked again.
    expect(screen.queryByText(/ortografía/)).toBeNull();
    await pause(3000);
    expect(spellingCalls(calls)).toHaveLength(1);
  });

  it('outside the field, the correction goes straight into it', async () => {
    await openForm({ [SPELLING]: fixTitle });
    typeTitle(TYPED);
    await pause();
    await waitFor(() => expect(title()).toHaveValue(FIXED));
  });

  it('an answer for a text the person kept typing reaches neither the preview nor the field', async () => {
    await openForm();
    const { answer, held } = hold(SPELLING);
    title().focus();
    typeTitle(TYPED);
    await pause();
    expect(held.count).toBe(1);
    typeTitle(`${TYPED} y el tablero`);
    await answer(200, fixTitle.body);
    expect(within(preview()).queryByText(FIXED)).toBeNull();
    expect(within(preview()).getByText(`${TYPED} y el tablero`)).toBeInTheDocument();
    fireEvent.blur(title());
    expect(title()).toHaveValue(`${TYPED} y el tablero`);
    // The next pause checks what she wrote last.
    await pause();
    expect(held.bodies).toEqual([{ titulo: TYPED }, { titulo: `${TYPED} y el tablero` }]);
  });

  it('when the check fails it says nothing, and confirm tries again', async () => {
    const calls = await openForm({
      [SPELLING]: [{ status: 503, body: { error: 'no_disponible' } }, NOTHING_TO_CORRECT],
      [TASKS]: loaded(),
    });
    fillTask();
    typeTitle(TYPED);
    await pause();
    await waitFor(() => expect(spellingCalls(calls).length).toBeGreaterThan(0));
    expect(screen.queryByText(/No pude revisar la ortografía/)).toBeNull();
    expect(title()).toHaveValue(TYPED);
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    expect(spellingCalls(calls).at(-1)?.body).toEqual(expect.objectContaining({ titulo: TYPED }));
  });

  it('confirm loads what the preview shows and does not check again what was already checked', async () => {
    const calls = await openForm({ [SPELLING]: fixTitle, [TASKS]: loaded() });
    fillTask();
    title().focus();
    typeTitle(TYPED);
    await pause();
    await waitFor(() => expect(within(preview()).getByText(FIXED)).toBeInTheDocument());
    const checks = spellingCalls(calls).length;
    // Still in the field: what loads is what the preview shows.
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    expect(spellingCalls(calls)).toHaveLength(checks);
    expect(calls.filter((c) => c.key === REVIEW)).toHaveLength(0);
    const sent = calls.filter((c) => c.key === TASKS);
    expect((sent[0].body as { titulo: string }).titulo).toBe(FIXED);
  });
});

// J2-28 (the user's phone test, 2026-10-13): a ticked evidence box was hard to tell from an empty
// one. No background in either state: the square's border, and a check mark only when ticked; the
// native checkbox stays underneath, for the keyboard, the screen reader and a tap on its words.
describe('the evidence boxes', () => {
  it('show a check mark only when ticked, with no background, and the words still tick them', async () => {
    await openForm();
    pick('Quién la hace', 'm-marcos');
    const box = screen.getByRole('checkbox', { name: /un informe/ });
    const row = box.closest('label') as HTMLElement;
    expect(box.className).toMatch(/\bsr-only\b/);
    expect(box.className).not.toMatch(/accent-/);
    const square = row.querySelector('[data-box]') as HTMLElement;
    expect(square.className).not.toMatch(/\bbg-(?!transparent)/);
    expect(square.className).toMatch(/peer-focus-visible:/);
    expect(square.querySelector('svg')).toBeNull();
    fireEvent.click(within(row).getByText(/un informe/));
    expect(box).toBeChecked();
    expect(square.querySelector('svg')).not.toBeNull();
    fireEvent.click(box);
    expect(box).not.toBeChecked();
    expect(square.querySelector('svg')).toBeNull();
  });
});

describe('Leda completes everything it can (J2-18)', () => {
  const WITH_EVIDENCE = { ...FULL, propuesta: { ...FULL.propuesta, evidencia: ['informe'] } };
  /** The "propuesto por Leda" mark of an evidence box, found from its words. */
  function evidenceMark(words: RegExp) {
    const row = screen.getByRole('checkbox', { name: words }).closest('label') as HTMLElement;
    return within(row).queryByText('· propuesto por Leda');
  }

  it('ticks only the evidence Leda proposes, not what the area asks, and marks it (J2-19)', async () => {
    const calls = await openForm({ [HELP]: proposed(WITH_EVIDENCE) });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByRole('checkbox', { name: /un informe/ })).toBeChecked());
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).not.toBeChecked();
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla · la pide el área/ })).toBeInTheDocument();
    expect(evidenceMark(/un informe/)).toBeInTheDocument();
    expect(evidenceMark(/una captura de pantalla/)).toBeNull();
    // What the form had goes with the question, so Leda never proposes over what was ticked.
    expect((calls.find((c) => c.key === HELP)?.body as { evidencia: string[] }).evidencia).toEqual([]);
    expect(within(preview()).getByText('un informe')).toBeInTheDocument();
  });

  it('with evidence the person already ticked, Leda\'s evidence never overwrites it', async () => {
    await openForm({ [HELP]: proposed({ propuesta: { titulo: 'Configurar las alarmas', evidencia: ['captura'] }, elegir: [], avisos: [] }) });
    pick('Quién la hace', 'm-marcos');
    fireEvent.click(screen.getByRole('checkbox', { name: /un informe/ }));
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByLabelText('Título')).toHaveValue('Configurar las alarmas'));
    expect(screen.getByRole('checkbox', { name: /un informe/ })).toBeChecked();
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).not.toBeChecked();
    expect(evidenceMark(/una captura de pantalla/)).toBeNull();
  });

  it('unticking the evidence Leda proposed is the person\'s choice: the mark goes', async () => {
    await openForm({ [HELP]: proposed(WITH_EVIDENCE) });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByRole('checkbox', { name: /un informe/ })).toBeChecked());
    fireEvent.click(screen.getByRole('checkbox', { name: /un informe/ }));
    expect(screen.getByRole('checkbox', { name: /un informe/ })).not.toBeChecked();
    expect(evidenceMark(/un informe/)).toBeNull();
  });

  it('another person: nothing new is ticked, and Leda\'s evidence stays if her area knows it', async () => {
    const both = options({
      politicas: [
        options().politicas[0],
        {
          area_id: 'a-infra',
          area: 'Infraestructura',
          evidencia_requerida: ['foto'],
          version: 1,
          tipos: {
            foto: { clases: ['imagen'], en_palabras: 'una foto' },
            informe: { clases: ['archivo'], en_palabras: 'un informe' },
          },
        },
      ],
    });
    await openForm({ [OPTIONS]: ok(both), [HELP]: proposed(WITH_EVIDENCE) });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByRole('checkbox', { name: /un informe/ })).toBeChecked());
    pick('Quién la hace', 'm-lucas');
    expect(screen.getByRole('checkbox', { name: /una foto/ })).not.toBeChecked();
    expect(screen.getByRole('checkbox', { name: /un informe/ })).toBeChecked();
    expect(evidenceMark(/un informe/)).toBeInTheDocument();
    expect(screen.queryByRole('checkbox', { name: /una captura de pantalla/ })).toBeNull();
  });

  it('never ticks an evidence the area does not know', async () => {
    await openForm({
      [HELP]: proposed({ ...FULL, propuesta: { ...FULL.propuesta, evidencia: ['inventada', 'captura'] } }),
    });
    tell();
    askLeda();
    await waitFor(() => expect(screen.getByLabelText('Quién la hace')).toHaveValue('m-marcos'));
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).toBeChecked();
    expect(screen.getByRole('checkbox', { name: /un informe/ })).not.toBeChecked();
    expect(screen.queryByRole('checkbox', { name: /inventada/ })).toBeNull();
    // J2-19: what is ticked is Leda's proposal, marked as hers.
    expect(evidenceMark(/una captura de pantalla/)).toBeInTheDocument();
  });

  it('a text the spelling check could not check is checked again on the next confirm', async () => {
    const unchecked = {
      status: 200,
      body: { corregidos: {}, sin_revisar: ['titulo', 'criterio'], aviso: 'No pude revisar la ortografía ahora: quedó como lo escribiste.' },
    };
    const refused = {
      status: 422,
      body: { errores: [{ campo: 'fecha', motivo: 'no_es_dia_habil', texto: 'Ese día no es hábil en este espacio.' }] },
    };
    const calls = await openForm({ [SPELLING]: [unchecked, NOTHING_TO_CORRECT], [TASKS]: [refused, loaded()] });
    fillTask();
    confirm();
    expect(await screen.findByText('Ese día no es hábil en este espacio.')).toBeInTheDocument();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const checks = calls.filter((c) => c.key === SPELLING);
    expect(checks).toHaveLength(2);
    expect(checks[1].body).toEqual(checks[0].body);
  });
});


// --- J2-20: starting over --------------------------------------------------------------------------

describe('starting over (J2-20)', () => {
  const START_OVER = '> empezar de nuevo';
  const ASK = '¿Borro todo lo que cargaste?';

  it('an empty form offers nothing to clear', async () => {
    await openForm();
    expect(screen.queryByRole('button', { name: START_OVER })).toBeNull();
  });

  it('asks first, and "no" keeps everything', async () => {
    await openForm();
    fillTask();
    tell();
    fireEvent.click(screen.getByRole('button', { name: START_OVER }));
    expect(screen.getByText(ASK)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '> no' }));
    expect(screen.queryByText(ASK)).toBeNull();
    expect(screen.getByLabelText('Título')).toHaveValue('Configurar alarmas del SCADA');
    expect(screen.getByLabelText(BOX)).toHaveValue(STORY);
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).toBeChecked();
  });

  it('"sí, borrar" clears every field, the box, Leda\'s marks, the problems and the preview', async () => {
    await openForm({ [HELP]: proposed(FULL) });
    tell();
    askLeda();
    await waitFor(() => expect(markOf('Criterio de aceptación')).toBeInTheDocument());
    confirm();
    expect(screen.getByRole('alert')).toHaveTextContent('quién la decidió');
    fireEvent.click(screen.getByRole('button', { name: START_OVER }));
    fireEvent.click(screen.getByRole('button', { name: '> sí, borrar' }));
    for (const label of ['Título', 'Descripción (opcional)', 'Criterio de aceptación', BOX]) {
      expect(screen.getByLabelText(label)).toHaveValue('');
    }
    expect(screen.getByLabelText('Objetivo')).toHaveValue('');
    expect(screen.getByLabelText('Quién la hace')).toHaveValue('');
    expect(screen.queryByText('· propuesto por Leda')).toBeNull();
    expect(screen.queryByRole('checkbox')).toBeNull();
    expect(screen.queryByRole('alert')).toBeNull();
    expect(within(preview()).getByText('(sin título)')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: START_OVER })).toBeNull();
  });

  it('a load after starting over goes with a new key', async () => {
    keys('44444444-4444-4444-8444-444444444444', '55555555-5555-4555-8555-555555555555');
    const calls = await openForm({ [TASKS]: ['network', loaded()] });
    fillTask();
    confirm();
    expect(await screen.findByText(/no llegó la respuesta/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: START_OVER }));
    fireEvent.click(screen.getByRole('button', { name: '> sí, borrar' }));
    fillTask();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { clave: string }).clave);
    expect(sent).toEqual(['44444444-4444-4444-8444-444444444444', '55555555-5555-4555-8555-555555555555']);
  });

  it('cannot be used while sending', async () => {
    const release = { go: (_: Response) => {} };
    await openForm();
    const real = globalThis.fetch;
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string, init?: RequestInit) =>
        url.endsWith('/tareas') ? new Promise<Response>((resolve) => (release.go = resolve)) : real(url, init),
      ),
    );
    fillTask();
    confirm();
    await waitFor(() => expect(screen.getByRole('button', { name: START_OVER })).toBeDisabled());
  });
});

// --- J2-21: what would be refused comes before the spelling ---------------------------------------
//
// The user's test (2026-10-13): Leda corrected "No se" to "No sé" and only on the second confirm the
// load refused that criterion. Now the form first asks what the load would refuse; the spelling runs
// only on what is going to load.

describe('the checks on confirm, in order (J2-21)', () => {
  const REFUSED = {
    status: 422,
    body: {
      errores: [
        {
          campo: 'criterio',
          motivo: 'sin_resultado',
          texto: 'No dice qué tiene que quedar hecho para darla por terminada.',
          propuesta: 'Las 12 alarmas del SCADA suenan en la sala de control.',
        },
      ],
    },
  };

  it('a criterion that is going to be refused is refused first, with Leda\'s proposal, and nothing is corrected', async () => {
    const calls = await openForm({ [REVIEW]: REFUSED });
    fillTask();
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), { target: { value: 'No se' } });
    confirm();
    expect(await screen.findByText('Las 12 alarmas del SCADA suenan en la sala de control.')).toBeInTheDocument();
    expect(screen.getByText('No dice qué tiene que quedar hecho para darla por terminada.')).toBeInTheDocument();
    expect(calls.some((c) => c.key === SPELLING)).toBe(false);
    expect(calls.some((c) => c.key === TASKS)).toBe(false);
    expect(screen.queryByText(/Leda corrigió la ortografía/)).toBeNull();
    // What was reviewed is what the form had, without loading anything.
    const reviewed = calls.find((c) => c.key === REVIEW)?.body as { criterio: string; titulo: string };
    expect(reviewed.criterio).toBe('No se');
    expect(reviewed.titulo).toBe('Configurar alarmas del SCADA');
  });

  it('using Leda\'s criterion and confirming goes on: review, spelling, load', async () => {
    const calls = await openForm({ [REVIEW]: [REFUSED, WOULD_LOAD], [TASKS]: loaded() });
    fillTask();
    fireEvent.change(screen.getByLabelText('Criterio de aceptación'), { target: { value: 'No se' } });
    confirm();
    fireEvent.click(await screen.findByRole('button', { name: '> usar este criterio' }));
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const order = calls.map((c) => c.key).filter((k) => [REVIEW, SPELLING, TASKS].includes(k));
    expect(order).toEqual([REVIEW, REVIEW, SPELLING, TASKS]);
  });

  it('what would load goes to the spelling before loading', async () => {
    const calls = await openForm({ [TASKS]: loaded() });
    fillTask();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const order = calls.map((c) => c.key).filter((k) => [REVIEW, SPELLING, TASKS].includes(k));
    expect(order).toEqual([REVIEW, SPELLING, TASKS]);
  });

  it('without an answer to the review nothing blocks: spelling and load as before', async () => {
    const calls = await openForm({ [REVIEW]: 'network', [TASKS]: loaded() });
    fillTask();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    expect(calls.filter((c) => c.key === SPELLING)).toHaveLength(1);
  });
});

// --- J2-30: what arrives late (the review of the whole J2, J2-29) -----------------------------------
//
// Answers that arrive after the form moved on: while it loads, after "sí, borrar", and the dictation
// that was still recording or turning into text when the person started over.

/** Holds every call to these routes until the test answers or fails it, by route and in order; the
 * other routes answer as `serve` says. */
function holdEvery(...routes: string[]) {
  const served = globalThis.fetch;
  type Held = { resolve: (response: Response) => void; reject: (error: unknown) => void; body: unknown };
  const pending: Record<string, Held[]> = {};
  vi.stubGlobal(
    'fetch',
    vi.fn((url: string, init?: RequestInit) => {
      const key = `${init?.method ?? 'GET'} ${url}`;
      if (!routes.includes(key)) return served(url, init);
      return new Promise<Response>((resolve, reject) => {
        const body = typeof init?.body === 'string' ? JSON.parse(init.body) : init?.body;
        (pending[key] ??= []).push({ resolve, reject, body });
      });
    }),
  );
  const calls = (route: string) => pending[route] ?? [];
  const answer = (route: string, i: number, status: number, body: unknown) =>
    act(async () => {
      calls(route)[i].resolve(
        new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }),
      );
    });
  const fail = (route: string, i: number) =>
    act(async () => {
      calls(route)[i].reject(new TypeError('Failed to fetch'));
    });
  return { calls, answer, fail };
}

describe('what arrives late (J2-30)', () => {
  const START_OVER = '> empezar de nuevo';
  const startOver = () => {
    fireEvent.click(screen.getByRole('button', { name: START_OVER }));
    fireEvent.click(screen.getByRole('button', { name: '> sí, borrar' }));
  };
  const title = () => screen.getByLabelText('Título');
  const pause = (ms = 1500) =>
    act(async () => {
      await vi.advanceTimersByTimeAsync(ms);
    });

  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
    forgetMicrophone();
  });

  it('a spelling answer that arrives while it loads changes nothing: a retry goes with the same key and data', async () => {
    keys('66666666-6666-4666-8666-666666666666', '77777777-7777-4777-8777-777777777777');
    await openForm();
    const held = holdEvery(SPELLING, TASKS);
    fillTask();
    // The pause checks the title and the criterion; their answers do not come yet.
    await pause();
    expect(held.calls(SPELLING)).toHaveLength(2);
    confirm();
    await waitFor(() => expect(held.calls(SPELLING)).toHaveLength(3));
    await held.answer(SPELLING, 2, 200, { corregidos: {}, sin_revisar: [] });
    await waitFor(() => expect(held.calls(TASKS)).toHaveLength(1));
    // While it loads, the pause check of the title answers with a correction.
    await held.answer(SPELLING, 0, 200, {
      corregidos: { titulo: { texto: 'Configurar Alarmas del SCADA', cambios: [] } },
      sin_revisar: [],
    });
    await held.fail(TASKS, 0);
    expect(await screen.findByText(/no llegó la respuesta/)).toBeInTheDocument();
    expect(title()).toHaveValue('Configurar alarmas del SCADA');
    confirm();
    await waitFor(() => expect(held.calls(TASKS)).toHaveLength(2));
    const [first, second] = held.calls(TASKS).map((c) => c.body as { clave: string; titulo: string });
    expect(second.clave).toBe('66666666-6666-4666-8666-666666666666');
    expect(second.clave).toBe(first.clave);
    expect(second.titulo).toBe(first.titulo);
  });

  // RDD warning of the J3-4 (R3-retry-spelling-key), the J2-30 rule: while the last send's outcome
  // is unknown, the spelling changes nothing, so a retry goes with the same data and the same key.
  it('after a send with no answer, the spelling changes nothing: the retry goes with the same data and key', async () => {
    keys('88888888-8888-4888-8888-888888888888', '99999999-9999-4999-8999-999999999999');
    const calls = await openForm({
      [SPELLING]: [
        { status: 503, body: { error: 'no_disponible' } },
        { status: 200, body: { corregidos: { titulo: { texto: 'Configurar Alarmas del SCADA', cambios: [] } }, sin_revisar: [] } },
      ],
      [TASKS]: ['network', loaded()],
    });
    fillTask();
    confirm();
    expect(await screen.findByText(/no llegó la respuesta/)).toBeInTheDocument();
    const checks = calls.filter((c) => c.key === SPELLING).length;
    await pause(3000);
    expect(calls.filter((c) => c.key === SPELLING)).toHaveLength(checks);
    expect(title()).toHaveValue('Configurar alarmas del SCADA');
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    expect(calls.filter((c) => c.key === SPELLING)).toHaveLength(checks);
    const [first, second] = calls.filter((c) => c.key === TASKS).map((c) => c.body as { clave: string; titulo: string });
    expect(second).toEqual(first);
  });

  it('a "completar con Leda" answer that arrives after "sí, borrar" fills nothing', async () => {
    await openForm();
    const held = holdEvery(HELP);
    tell();
    askLeda();
    await waitFor(() => expect(held.calls(HELP)).toHaveLength(1));
    startOver();
    // The same story again: only the start over tells the old answer apart.
    tell();
    await held.answer(HELP, 0, 200, FULL);
    expect(title()).toHaveValue('');
    expect(screen.getByLabelText('Criterio de aceptación')).toHaveValue('');
    expect(screen.queryByText('· propuesto por Leda')).toBeNull();
  });

  it('a spelling answer that arrives after "sí, borrar" reaches neither the field nor the preview', async () => {
    const TYPED = 'configurar las alarmas del scada';
    const FIXED = 'Configurar las alarmas del SCADA';
    await openForm();
    const held = holdEvery(SPELLING);
    fireEvent.change(title(), { target: { value: TYPED } });
    await pause();
    expect(held.calls(SPELLING)).toHaveLength(1);
    startOver();
    // The same text again: only the start over tells the old answer apart.
    fireEvent.change(title(), { target: { value: TYPED } });
    await held.answer(SPELLING, 0, 200, {
      corregidos: { titulo: { texto: FIXED, cambios: [] } },
      sin_revisar: [],
    });
    expect(title()).toHaveValue(TYPED);
    expect(within(preview()).queryByText(FIXED)).toBeNull();
  });

  it('"sí, borrar" while dictating stops the microphone and sends nothing', async () => {
    const mic = fakeMicrophone();
    const calls = await openForm({ [DICTATION]: ok({ texto: 'colgar el estante del módem' }) });
    tell('hay que');
    await startDictating();
    startOver();
    expect(mic.track.stop).toHaveBeenCalled();
    expect(mic.release).toHaveBeenCalled();
    expect(screen.queryByText(/grabando/)).toBeNull();
    expect(screen.getByRole('button', { name: 'dictar' })).toHaveAttribute('aria-pressed', 'false');
    await pause();
    expect(calls.filter((c) => c.key === DICTATION)).toHaveLength(0);
    expect(screen.getByLabelText(BOX)).toHaveValue('');
  });

  it('a dictation still turning into text when "sí, borrar" is tapped adds nothing', async () => {
    fakeMicrophone();
    await openForm();
    const held = holdEvery(DICTATION);
    tell('hay que');
    fireEvent.click(await startDictating());
    await waitFor(() => expect(held.calls(DICTATION)).toHaveLength(1));
    startOver();
    await held.answer(DICTATION, 0, 200, { texto: 'colgar el estante del módem' });
    expect(screen.getByLabelText(BOX)).toHaveValue('');
    expect(screen.getByRole('button', { name: 'dictar' })).toBeEnabled();
  });
});

// --- The J4 phone test (2026-10-14) -----------------------------------------------------------

describe('after loading a task', () => {
  it('says it in teal where confirm was, warns in the warning color, and offers it to wait on next', async () => {
    keys('33333333-3333-4333-8333-333333333333');
    const calls = await openForm({
      [OPTIONS]: [
        ok(options()),
        ok(
          options({
            tareas: [
              {
                id: 't-new',
                titulo: 'Configurar alarmas del SCADA',
                estado: 'asignada',
                fecha_objetivo: '2026-10-16',
                responsable: 'Marcos',
                objetivo: 'Mantenimiento anual',
              },
            ],
          }),
        ),
      ],
      [TASKS]: loaded([
        { campo: 'responsable', motivo: 'sin_conectar', texto: 'Esa persona todavía no tiene Leda conectada.' },
      ]),
    });
    fillTask();
    confirm();
    const done = await screen.findByText('Tarea cargada.');
    expect(done).toHaveClass('text-creado');
    // Below the preview, where the button was.
    const section = done.closest('section') as HTMLElement;
    const order = [...section.children];
    expect(order.indexOf(done)).toBeGreaterThan(0);
    expect(screen.getByText('Esa persona todavía no tiene Leda conectada.').closest('ul')).toHaveClass('text-falta');
    // The options are read again after the load.
    await waitFor(() => expect(calls.filter((c) => c.key === OPTIONS)).toHaveLength(2));
    fireEvent.click(screen.getByRole('button', { name: '> cargar otra' }));
    await screen.findByRole('form', { name: 'Cargar tarea' });
    expect(offered('Espera a (opcional)')).toContain('Configurar alarmas del SCADA · Marcos · Mantenimiento anual');
  });
});
