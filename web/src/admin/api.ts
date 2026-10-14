// The administration door's API (src/leda/web_app.py, ADR 0022, decisions 6, 9 and 10). Field
// names mirror the server's JSON, which is in Spanish like the rest of Leda's data.
import { RequestError, SessionClosedError } from '../api';

export interface Space {
  id: string;
  slug: string;
  nombre: string;
}

export interface AdminMe {
  administrador: string;
  espacios: Space[];
}

export interface Objective {
  id: string;
  titulo: string;
  tipo: string;
  estado: string;
  fecha_objetivo: string | null;
}

export interface Member {
  membership_id: string;
  nombre: string;
  area_id: string;
  area: string;
  autoridad_final: boolean;
  conectado: boolean;
  // Who would review this person's work; null when nobody active does (the server rejects it).
  revisa: { membership_id: string; nombre: string } | null;
}

/** A task a new one may wait for (ADR 0023, decision 2; migration 0067): committed and open. */
export interface WaitableTask {
  id: string;
  titulo: string;
  estado: string;
  fecha_objetivo: string | null;
  responsable: string | null;
  objetivo: string;
}

export interface EvidenceKind {
  clases: string[];
  en_palabras: string;
}

export interface Policy {
  area_id: string;
  area: string;
  evidencia_requerida: string[];
  version: number;
  tipos: Record<string, EvidenceKind>;
}

export interface Options {
  espacio: { id: string; nombre: string; zona_horaria: string };
  hoy: string;
  objetivos: Objective[];
  // The tasks a new one may wait for. The server always sends them since migration 0067; a reply
  // without them offers none.
  tareas?: WaitableTask[];
  integrantes: Member[];
  politicas: Policy[];
  calendario: {
    dias: string[];
    hasta: string;
    feriados: { fecha: string; nombre: string }[];
    // The working days the form may offer, from today on, as the server decides them.
    dias_habiles: string[];
  };
}

/** One problem the server found, already in plain words (`texto`). */
export interface Problem {
  campo: string;
  motivo: string;
  texto: string;
}

/** What the form sends: the server's names, with the idempotency key of this attempt. */
export interface TaskInput {
  objetivo_id: string;
  titulo: string;
  descripcion: string;
  responsable_id: string;
  fecha: string;
  criterio: string;
  evidencia: string[];
  decidio_id: string;
  // The task this one waits for (always blocking); left out when it waits for none.
  espera_id?: string;
  clave: string;
}

export type LoadResult =
  | { kind: 'loaded'; taskId: string; warnings: Problem[]; repeated: boolean }
  | { kind: 'rejected'; errors: Problem[] };

const ADMIN = '/app/admin';

async function call(url: string, init: RequestInit = {}): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(url, {
      credentials: 'same-origin',
      ...init,
      headers: { Accept: 'application/json', ...(init.headers ?? {}) },
    });
  } catch (error) {
    if (init.signal?.aborted) throw error;
    throw new RequestError(0);
  }
  if (response.status === 401) throw new SessionClosedError();
  return response;
}

async function getJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await call(url, { signal });
  if (!response.ok) throw new RequestError(response.status);
  return (await response.json()) as T;
}

export function fetchAdminMe(signal?: AbortSignal): Promise<AdminMe> {
  return getJson<AdminMe>(`${ADMIN}/api/yo`, signal);
}

export function fetchOptions(spaceId: string, signal?: AbortSignal): Promise<Options> {
  return getJson<Options>(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/opciones`, signal);
}

/** Loads a committed task (decision 9). 201 loads it; 200 means this key already loaded it (a
 * retry); 422 lists what to fix. Anything else throws, so the form keeps the data for a retry. */
export async function loadTask(spaceId: string, input: TaskInput): Promise<LoadResult> {
  const response = await call(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/tareas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (response.status === 201 || response.status === 200) {
    const body = (await response.json()) as { task_id: string; avisos?: Problem[]; repetida?: boolean };
    return {
      kind: 'loaded',
      taskId: body.task_id,
      warnings: body.avisos ?? [],
      repeated: Boolean(body.repetida),
    };
  }
  if (response.status === 422) {
    const body = (await response.json()) as { errores?: Problem[] };
    return { kind: 'rejected', errors: body.errores ?? [] };
  }
  throw new RequestError(response.status);
}

/** What the load would refuse (J2-21), asked before the spelling so a criterion that is going to be
 * refused is never corrected first: `ok` if it would load, `rejected` with the same problems the
 * load would answer, `unknown` if there was no answer (it never blocks: the load judges again). A
 * closed session throws. Nothing is loaded and the key is never used. */
export type ReviewResult = { kind: 'ok' } | { kind: 'rejected'; errors: Problem[] } | { kind: 'unknown' };

export async function reviewTask(spaceId: string, input: TaskInput): Promise<ReviewResult> {
  let response: Response;
  try {
    response = await call(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/tareas/revisar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
  } catch (error) {
    if (error instanceof SessionClosedError) throw error;
    return { kind: 'unknown' };
  }
  if (response.status === 200) return { kind: 'ok' };
  if (response.status === 422) {
    try {
      const body = (await response.json()) as { errores?: Problem[] };
      return { kind: 'rejected', errors: body.errores ?? [] };
    } catch {
      return { kind: 'unknown' };
    }
  }
  return { kind: 'unknown' };
}

/** What the form sends to ask Leda to complete it (ADR 0023, point 4; portion J2): what the
 * person told in the free box and what the form already has. Leda proposes only what is empty. */
export interface HelpInput {
  texto: string;
  objetivo_id: string;
  titulo: string;
  descripcion: string;
  responsable_id: string;
  fecha: string;
  espera_id: string;
  criterio: string;
  // The evidence already ticked (J2-18): what the person chose is hers, so Leda proposes none.
  evidencia: string[];
}

/** What Leda proposes, with the form's field names. `evidencia` (J2-18) is what Leda adds on top
 * of the minimum the area of whoever does it asks for. */
export type Proposal = Partial<
  Pick<HelpInput, 'objetivo_id' | 'titulo' | 'descripcion' | 'responsable_id' | 'fecha' | 'espera_id' | 'criterio'>
> & { evidencia?: string[] };

/** A person to choose from when the name the person used fits more than one: Leda never picks. */
export interface Candidate {
  membership_id: string;
  nombre: string;
  area: string;
}

export type HelpResult =
  | { kind: 'proposed'; proposal: Proposal; choices: Candidate[]; notes: Problem[] }
  | { kind: 'rejected'; errors: Problem[] }
  | { kind: 'failed'; text: string };

/** The plain words when Leda could not complete (the server says the same, with an incident). */
export const HELP_FAILED =
  'Leda no pudo completar ahora. Lo que escribiste sigue acá: completalo vos o probá de nuevo en un rato.';

/** Asks Leda to complete the empty fields. 200 proposes, 422 says why not, 503 means the AI did
 * not answer; anything else (no network, a server failure) also reads as "could not complete". */
export async function askLeda(spaceId: string, input: HelpInput): Promise<HelpResult> {
  let response: Response;
  try {
    response = await call(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/ayuda`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
  } catch (error) {
    if (error instanceof SessionClosedError) throw error;
    return { kind: 'failed', text: HELP_FAILED };
  }
  if (response.status === 200) {
    const body = (await response.json()) as { propuesta?: Proposal; elegir?: Candidate[]; avisos?: Problem[] };
    return { kind: 'proposed', proposal: body.propuesta ?? {}, choices: body.elegir ?? [], notes: body.avisos ?? [] };
  }
  if (response.status === 422) {
    const body = (await response.json()) as { errores?: Problem[] };
    // A rejection always says why; one without its reasons is never shown as silence.
    const errors = Array.isArray(body?.errores) ? body.errores : [];
    return errors.length > 0 ? { kind: 'rejected', errors } : { kind: 'failed', text: HELP_FAILED };
  }
  return { kind: 'failed', text: HELP_FAILED };
}

/** The form's free-text fields, the ones whose spelling Leda checks before loading (J2-17). */
export type TextField = 'titulo' | 'descripcion' | 'criterio';

/** What the spelling check said: the corrected texts (only the ones that changed; J2-23: they load
 * as corrected, unmarked), the fields it could not check, and, if any, the plain words to say so. */
export interface Spelling {
  corrected: Partial<Record<TextField, { text: string }>>;
  unchecked: TextField[];
  notice?: string;
}

/** The plain words when Leda could not check the spelling (the server says the same, with an
 * incident). Nothing blocks: the text stays as written. */
export const SPELLING_FAILED = 'No pude revisar la ortografía ahora: quedó como lo escribiste.';

/** Asks Leda to correct the spelling of the texts the person wrote (J2-17), before loading.
 * Never blocks the load: anything but an answer (no network, a server failure) reads as "could not
 * check", with the text as written; only a closed session throws. */
export async function checkSpelling(
  spaceId: string,
  texts: Partial<Record<TextField, string>>,
): Promise<Spelling> {
  const asked = Object.keys(texts) as TextField[];
  const failed: Spelling = { corrected: {}, unchecked: asked, notice: SPELLING_FAILED };
  let response: Response;
  try {
    response = await call(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/ortografia`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(texts),
    });
  } catch (error) {
    if (error instanceof SessionClosedError) throw error;
    return failed;
  }
  if (response.status !== 200) return failed;
  const body = (await response.json()) as {
    corregidos?: Record<string, { texto?: unknown }>;
    sin_revisar?: unknown;
    aviso?: unknown;
  };
  const corrected: Spelling['corrected'] = {};
  for (const field of asked) {
    const fix = body?.corregidos?.[field];
    if (fix && typeof fix.texto === 'string' && fix.texto.trim()) corrected[field] = { text: fix.texto };
  }
  const unchecked = Array.isArray(body?.sin_revisar)
    ? asked.filter((f) => (body.sin_revisar as unknown[]).includes(f))
    : [];
  return {
    corrected,
    unchecked,
    notice: unchecked.length > 0 ? (typeof body.aviso === 'string' ? body.aviso : SPELLING_FAILED) : undefined,
  };
}

/** The plain words when the dictated audio could not be turned into text (J2b; the server says the
 * same, with an incident). What was written stays. */
export const DICTATION_FAILED = 'No pude pasar el audio a texto ahora. Probá de nuevo en un rato o escribilo acá.';
/** Gemini answered, but understood nothing (the server's own words win when it sends them). */
export const DICTATION_UNHEARD = 'No te entendí; probá de nuevo o escribilo acá.';
export const DICTATION_TOO_LONG = 'El audio es demasiado largo para pasarlo a texto; probá con uno más corto o escribilo acá.';
/** How long the form waits for the text: more than the server waits for Gemini (35 s in all,
 * `dictado.PLAZO_TOTAL_S`), so a stuck call ends on the server first. */
export const DICTATION_TIMEOUT_MS = 45_000;

/** The text, and the server's notice when Gemini cut it at its output limit (J2-26: the text is
 * only a part, and the person can dictate the rest). */
export type DictationResult = { kind: 'text'; text: string; notice?: string } | { kind: 'failed'; text: string };

/** Sends the recorded audio as it is, with its own type, and returns what was said as text (J2b).
 * Anything but a text (no network, the time running out, a server failure) reads as "could not",
 * in plain words; only a closed session throws. */
export async function transcribe(spaceId: string, audio: Blob): Promise<DictationResult> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DICTATION_TIMEOUT_MS);
  try {
    let response: Response;
    try {
      response = await call(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/dictado`, {
        method: 'POST',
        headers: { 'Content-Type': audio.type },
        body: audio,
        signal: controller.signal,
      });
    } catch (error) {
      if (error instanceof SessionClosedError) throw error;
      return { kind: 'failed', text: DICTATION_FAILED };
    }
    if (response.status === 413) return { kind: 'failed', text: DICTATION_TOO_LONG };
    let body: { texto?: unknown; aviso?: unknown } | null = null;
    try {
      body = (await response.json()) as { texto?: unknown; aviso?: unknown };
    } catch {
      body = null;
    }
    const said = typeof body?.texto === 'string' ? body.texto.trim() : '';
    const notice = typeof body?.aviso === 'string' && body.aviso.trim() ? body.aviso.trim() : undefined;
    if (response.status === 200) {
      if (!said) return { kind: 'failed', text: DICTATION_UNHEARD };
      return notice ? { kind: 'text', text: said, notice } : { kind: 'text', text: said };
    }
    if (response.status === 422) return { kind: 'failed', text: said || DICTATION_UNHEARD };
    return { kind: 'failed', text: DICTATION_FAILED };
  } finally {
    clearTimeout(timer);
  }
}

/** Closes this administration session on the server; the server also clears its cookie. */
export async function adminSignOut(): Promise<void> {
  const response = await fetch(`${ADMIN}/salir`, { method: 'POST', credentials: 'same-origin' });
  if (!response.ok && response.status !== 401) throw new RequestError(response.status);
}
