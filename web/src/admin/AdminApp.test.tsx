import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { adminMe, options, OTHER_SPACE, SPACE } from '../test/adminFixtures';
import { AdminApp } from './AdminApp';
import { newKey } from './draft';

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

function pick(label: string | RegExp, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

function fillTask() {
  pick('objetivo', 'o1');
  fireEvent.change(screen.getByLabelText('título'), { target: { value: 'Configurar alarmas del SCADA' } });
  pick('quién la hace', 'm-marcos');
  fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
  fireEvent.change(screen.getByLabelText('criterio de aceptación'), {
    target: { value: 'Las 12 alarmas suenan en la sala de control' },
  });
  pick('quién la decidió', 'm-ismael');
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
    const objective = screen.getByLabelText('objetivo');
    expect(within(objective).getByRole('option', { name: 'Puesta en marcha de la línea 3 · hasta 30.10' })).toBeInTheDocument();
    const responsible = screen.getByLabelText('quién la hace');
    expect(within(responsible).getByRole('option', { name: 'Lucas · Infraestructura · sin conectar' })).toBeInTheDocument();
    pick('quién la hace', 'm-lucas');
    expect(screen.getByText('· la revisa: Ismael')).toBeInTheDocument();
    expect(screen.getByText('[SIN CONECTAR]')).toBeInTheDocument();
    pick('quién la hace', 'm-ismael');
    expect(screen.getByText('· la revisa: nadie')).toBeInTheDocument();
  });

  it('offers only the working days from today on', async () => {
    await openForm();
    const calendar = screen.getByRole('group', { name: 'fecha' });
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
    pick('quién la hace', 'm-marcos');
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).toBeChecked();
    expect(screen.getByRole('checkbox', { name: /un informe/ })).not.toBeChecked();
    pick('quién la hace', 'm-lucas');
    expect(screen.queryByRole('checkbox')).toBeNull();
    expect(screen.getByText('El área no pide evidencia.')).toBeInTheDocument();
  });

  it('counts characters against the server limits', async () => {
    await openForm();
    fireEvent.change(screen.getByLabelText('título'), { target: { value: 'x'.repeat(205) } });
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
    expect(aside).toHaveTextContent('la revisaIsmael');
    expect(aside).toHaveTextContent('la decidióIsmael');
    expect(aside).toHaveTextContent('la cargaAriel');
    const button = within(aside).getByRole('button', { name: '> confirmar' });
    // The confirm button comes after what it confirms.
    expect(card.compareDocumentPosition(button) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    // Writing never sends (Enter in a field submits the form): only confirm does.
    fireEvent.submit(screen.getByRole('form', { name: 'Cargar tarea' }));
    expect(calls.some((c) => c.key === TASKS)).toBe(false);
  });

  it('confirm with missing fields says what is missing next to it, focuses the first and sends nothing', async () => {
    const calls = await openForm();
    pick('objetivo', 'o1');
    fireEvent.change(screen.getByLabelText('título'), { target: { value: 'Configurar alarmas del SCADA' } });
    pick('quién la hace', 'm-marcos');
    fireEvent.click(screen.getByRole('checkbox', { name: /una captura de pantalla/ }));
    fireEvent.click(screen.getByRole('button', { name: 'vie 16.10' }));
    confirm();
    const summary = within(preview()).getByRole('alert');
    expect(summary).toHaveTextContent('Falta completar: criterio de aceptación, evidencia, quién la decidió.');
    expect(screen.getByLabelText('criterio de aceptación')).toHaveFocus();
    expect(screen.getByLabelText('criterio de aceptación')).toHaveAttribute('aria-invalid', 'true');
    expect(document.getElementById('f-criterio-error')).toHaveTextContent('Falta el criterio de aceptación');
    expect(screen.getByLabelText('quién la decidió')).toHaveAttribute('aria-describedby', 'f-decidio-error');
    expect(calls.some((c) => c.key === TASKS)).toBe(false);
    // Each name takes you to its field.
    fireEvent.click(within(summary).getByRole('button', { name: 'quién la decidió' }));
    expect(screen.getByLabelText('quién la decidió')).toHaveFocus();
    fireEvent.click(within(summary).getByRole('button', { name: 'evidencia' }));
    expect(screen.getByRole('checkbox', { name: /una captura de pantalla/ })).toHaveFocus();
    // Fixing a field takes it off the summary; with nothing missing, the summary goes away.
    pick('quién la decidió', 'm-ismael');
    expect(summary).toHaveTextContent('Falta completar: criterio de aceptación, evidencia.');
    fireEvent.click(screen.getByRole('checkbox', { name: /una captura de pantalla/ }));
    fireEvent.change(screen.getByLabelText('criterio de aceptación'), { target: { value: 'Suenan las 12' } });
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('an empty form lists every required field, the first one focused', async () => {
    await openForm();
    confirm();
    expect(screen.getByRole('alert')).toHaveTextContent(
      'Falta completar: objetivo, título, quién la hace, fecha, criterio de aceptación, quién la decidió.',
    );
    expect(screen.getByLabelText('objetivo')).toHaveFocus();
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
    fillTask();
    confirm();
    const summary = await within(preview()).findByRole('alert');
    expect(summary).toHaveTextContent('Falta completar: criterio de aceptación, evidencia, quién la decidió.');
    await waitFor(() => expect(screen.getByLabelText('criterio de aceptación')).toHaveFocus());
    expect(document.getElementById('f-decidio-error')).toHaveTextContent('Elegí quién decidió la tarea.');
    expect(document.getElementById('f-evidencia-error')).toHaveTextContent('Elegí la evidencia que se pide');
    expect(calls.filter((c) => c.key === TASKS)).toHaveLength(1);
  });

  it('every control and the calendar are built to fit the width of a phone', async () => {
    await openForm();
    const form = screen.getByRole('form', { name: 'Cargar tarea' });
    const controls = form.querySelectorAll('select, input:not([type="checkbox"]), textarea');
    expect(controls.length).toBeGreaterThan(0);
    for (const control of controls) {
      expect(control).toHaveClass('w-full', 'min-w-0', 'max-w-full');
      // 16px on a touch screen, so the phone does not zoom in when the field is touched.
      expect(control).toHaveClass('pointer-coarse:text-[16px]');
    }
    expect(screen.getByRole('group', { name: 'fecha' })).toHaveClass('w-full', 'min-w-0', 'max-w-full');
    expect(form).toHaveClass('min-w-0');
    expect(preview()).toHaveClass('min-w-0');
    // jsdom has no layout: the real width is only confirmed on the phone.
  });

  it('confirm sends the data with one key and shows the warnings', async () => {
    keys('11111111-1111-4111-8111-111111111111');
    const calls = await openForm({
      [TASKS]: loaded([
        { campo: 'responsable', motivo: 'sin_conectar', texto: 'Esa persona todavía no tiene Leda conectada: no va a recibir avisos ni seguimiento hasta que la conecte.' },
      ]),
    });
    fillTask();
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
    expect(screen.getByLabelText('título')).toHaveValue('');
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
    const wait = screen.getByLabelText('espera a (opcional)');
    expect(wait).toHaveValue('');
    expect(
      within(wait).getByRole('option', { name: 'Colocar el estante · Lucas · Mantenimiento anual' }),
    ).toBeInTheDocument();
    fillTask();
    pick('espera a (opcional)', 't-estante');
    const form = screen.getByRole('form', { name: 'Cargar tarea' });
    expect(within(form).getByText('No puede empezar hasta que esa esté terminada.')).toBeInTheDocument();
    expect(preview()).toHaveTextContent(
      'espera aColocar el estante · Lucas',
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
    pick('espera a (opcional)', 't-estante');
    confirm();
    await screen.findByRole('alert');
    expect(screen.getByLabelText('espera a (opcional)')).toHaveAttribute('aria-invalid', 'true');
    expect(document.getElementById('f-espera-error')).toHaveTextContent('ya está cerrada');
    pick('espera a (opcional)', '');
    expect(document.getElementById('f-espera-error')).toBeNull();
  });

  it('warns when the date is after the objective, without blocking', async () => {
    await openForm();
    pick('objetivo', 'o1');
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
    expect(screen.getByLabelText('título')).toBeDisabled();
    expect(screen.getByRole('button', { name: 'cargando…' })).toBeDisabled();
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo cargar');
    expect(screen.getByLabelText('título')).toHaveValue('Configurar alarmas del SCADA');
    expect(screen.getByLabelText('título')).toBeEnabled();
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { clave: string }).clave);
    expect(sent).toEqual(['22222222-2222-4222-8222-222222222222', '22222222-2222-4222-8222-222222222222']);
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
    fireEvent.change(screen.getByLabelText('título'), { target: { value: 'Configurar las alarmas' } });
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
    fireEvent.change(screen.getByLabelText('criterio de aceptación'), { target: { value: 'Suenan las 12' } });
    confirm();
    expect(await screen.findByText('Tarea cargada.')).toBeInTheDocument();
    const sent = calls.filter((c) => c.key === TASKS).map((c) => (c.body as { clave: string }).clave);
    expect(sent).toEqual([
      '66666666-6666-4666-8666-666666666666',
      '66666666-6666-4666-8666-666666666666',
      '77777777-7777-4777-8777-777777777777',
    ]);
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
    await waitFor(() => expect(screen.getByLabelText('quién la hace')).toHaveFocus());
    expect(screen.getByLabelText('quién la hace')).toHaveAttribute('aria-invalid', 'true');
    expect(document.getElementById('f-responsable-error')).toHaveTextContent('Nadie activo revisa');
    expect(document.getElementById('f-fecha-error')).toHaveTextContent('Ese día no es hábil');
    // Fixing a field clears its message.
    pick('quién la hace', 'm-lucas');
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
    const selector = screen.getByLabelText('espacio');
    expect(within(selector).queryByRole('option', { name: 'CoreWork' })).toBeNull();
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
    expect(await screen.findByRole('option', { name: 'Laboratorio nuevo' })).toBeInTheDocument();
    expect(calls.map((c) => c.key)).toContain(`GET /app/admin/api/espacios/${OTHER_SPACE}/opciones`);
  });
});
