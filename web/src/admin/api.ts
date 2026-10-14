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
  // Through the team's door (J4), who would review a task this person loads for this member.
  revisa: { membership_id: string; nombre: string } | null;
  // Through the team's door (J4; migration 0071, `como_carga`): how the person who loads loads for
  // this member. `pedido_a_otra_area` and `pedido_a_direccion` are requests: the other area's
  // referente decides who does it (D14), and Dirección's is given as done by who asked (D1b).
  como?: 'propia' | 'direccion' | 'su_area' | 'pedido_a_otra_area' | 'pedido_a_direccion';
}

/** An area with its active referente (migration 0071): who decides there (D10) and to whom what
 * belongs to that area is asked (D14). */
export interface Area {
  id: string;
  nombre: string;
  referente: { membership_id: string; nombre: string } | null;
}

/** Who may be chosen to review a task (D3): Dirección and the active area referentes. */
export interface Reviewer {
  membership_id: string;
  nombre: string;
  autoridad_final: boolean;
  areas: string[];
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
  // Since migration 0071; a reply without them offers no reviewer choice.
  areas?: Area[];
  revisores?: Reviewer[];
  // Only through the team's door (J4): who loads, and whether she chooses who reviews (Dirección).
  yo?: { membership_id: string; nombre: string; autoridad_final: boolean; elige_quien_revisa: boolean };
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
  // The day it may fall due on at most, with a date after its objective or its parent (migration
  // 0070, `vence_despues_del_objetivo` and `vence_despues_del_padre`).
  hasta?: string;
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
  // Who reviews it, when chosen (D3; migration 0071); left out for the one that corresponds.
  revisa_id?: string;
  clave: string;
}

export type LoadResult =
  | { kind: 'loaded'; taskId: string; warnings: Problem[]; repeated: boolean }
  | { kind: 'rejected'; errors: Problem[] };

const ADMIN = '/app/admin';

/** A request with the session's cookie: a closed session (401) throws `SessionClosedError`, no
 * network throws `RequestError(0)`; any other answer is returned as it came. */
export async function call(url: string, init: RequestInit = {}): Promise<Response> {
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

/** The options of the team's door (J4): only Dirección and the area referentes; a 403 throws a
 * `RequestError(403)`. */
export function fetchTeamOptions(signal?: AbortSignal): Promise<Options> {
  return getJson<Options>('/app/api/carga/opciones', signal);
}

/** Loads a committed task (decision 9). 201 loads it; 200 means this key already loaded it (a
 * retry); 422 lists what to fix. Anything else throws, so the form keeps the data for a retry. */
export function loadTask(spaceId: string, input: TaskInput): Promise<LoadResult> {
  return loadTaskAt(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/tareas`, input);
}

/** The same load at any door's address (the team's, J4). A 403 (not Dirección nor a referente)
 * reads as a rejection with the server's words. */
export async function loadTaskAt(url: string, input: TaskInput): Promise<LoadResult> {
  const response = await call(url, {
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
  if (response.status === 403) {
    let texto = NOT_LOADING;
    try {
      const body = (await response.json()) as { texto?: unknown };
      if (typeof body?.texto === 'string' && body.texto.trim()) texto = body.texto;
    } catch {
      // The plain words above.
    }
    return { kind: 'rejected', errors: [{ campo: 'sesion', motivo: 'sin_autoridad', texto }] };
  }
  throw new RequestError(response.status);
}

/** The server's words when the person may not load tasks (src/leda/web_app.py,
 * TEXTO_SIN_AUTORIDAD_PARA_CARGAR). */
export const NOT_LOADING = 'Cargar tareas le corresponde a Dirección y a los referentes de área.';

/** What the load would refuse (J2-21), asked before the spelling so a criterion that is going to be
 * refused is never corrected first: `ok` if it would load, `rejected` with the same problems the
 * load would answer, `unknown` if there was no answer (it never blocks: the load judges again). A
 * closed session throws. Nothing is loaded and the key is never used. */
export type ReviewResult = { kind: 'ok' } | { kind: 'rejected'; errors: Problem[] } | { kind: 'unknown' };

export function reviewTask(spaceId: string, input: TaskInput): Promise<ReviewResult> {
  return reviewTaskAt(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/tareas/revisar`, input);
}

export async function reviewTaskAt(url: string, input: TaskInput): Promise<ReviewResult> {
  let response: Response;
  try {
    response = await call(url, {
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

export type HelpResult<P = Proposal> =
  | { kind: 'proposed'; proposal: P; choices: Candidate[]; notes: Problem[] }
  | { kind: 'rejected'; errors: Problem[] }
  | { kind: 'failed'; text: string };

/** The plain words when Leda could not complete (the server says the same, with an incident). */
export const HELP_FAILED =
  'Leda no pudo completar ahora. Lo que escribiste sigue acá: completalo vos o probá de nuevo en un rato.';

/** Asks Leda to complete the empty fields. 200 proposes, 422 says why not, 503 means the AI did
 * not answer; anything else (no network, a server failure) also reads as "could not complete". */
export function askLeda(spaceId: string, input: HelpInput): Promise<HelpResult> {
  return askLedaAt<Proposal>(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/ayuda`, input);
}

/** The same request to any door's help address (the task's or the objective's, J3-4). */
export async function askLedaAt<P>(url: string, input: object): Promise<HelpResult<P>> {
  let response: Response;
  try {
    response = await call(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
  } catch (error) {
    if (error instanceof SessionClosedError) throw error;
    return { kind: 'failed', text: HELP_FAILED };
  }
  if (response.status === 200) {
    const body = (await response.json()) as { propuesta?: P; elegir?: Candidate[]; avisos?: Problem[] };
    return { kind: 'proposed', proposal: body.propuesta ?? ({} as P), choices: body.elegir ?? [], notes: body.avisos ?? [] };
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
export function checkSpelling(spaceId: string, texts: Partial<Record<TextField, string>>): Promise<Spelling> {
  return checkSpellingAt(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/ortografia`, texts);
}

/** The same check at any door's spelling address; `of` tells the server whose texts they are (an
 * objective's, J3-4; a task's when left out). */
export async function checkSpellingAt(
  url: string,
  texts: Partial<Record<TextField, string>>,
  of?: 'objetivo',
): Promise<Spelling> {
  const asked = Object.keys(texts) as TextField[];
  const failed: Spelling = { corrected: {}, unchecked: asked, notice: SPELLING_FAILED };
  let response: Response;
  try {
    response = await call(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(of ? { ...texts, de: of } : texts),
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
export function transcribe(spaceId: string, audio: Blob): Promise<DictationResult> {
  return transcribeAt(`${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}/dictado`, audio);
}

/** The same dictation at any door's address (the team's, J3-4). `of`: what is being dictated, so
 * the server's instructions say it (J3-4b); without it, a task. */
export async function transcribeAt(url: string, audio: Blob, of?: 'objetivo'): Promise<DictationResult> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DICTATION_TIMEOUT_MS);
  try {
    let response: Response;
    try {
      response = await call(of ? `${url}?de=${of}` : url, {
        method: 'POST',
        // J2-30: never an empty type (the server refuses it); without one, the iPhone's.
        headers: { 'Content-Type': audio.type || 'audio/mp4' },
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

/** A door's task load (J4): loading, what it would refuse, Leda's help, the spelling and the
 * dictation, each at that door's own address. The form takes one, so it serves both doors. */
export interface TaskApi {
  load(input: TaskInput): Promise<LoadResult>;
  review(input: TaskInput): Promise<ReviewResult>;
  help(input: HelpInput): Promise<HelpResult>;
  spell(texts: Partial<Record<TextField, string>>): Promise<Spelling>;
  transcribe(audio: Blob): Promise<DictationResult>;
}

/** The administration's door, in one space. */
export function adminTasks(spaceId: string): TaskApi {
  const space = `${ADMIN}/api/espacios/${encodeURIComponent(spaceId)}`;
  return {
    load: (input) => loadTaskAt(`${space}/tareas`, input),
    review: (input) => reviewTaskAt(`${space}/tareas/revisar`, input),
    help: (input) => askLedaAt<Proposal>(`${space}/ayuda`, input),
    spell: (texts) => checkSpellingAt(`${space}/ortografia`, texts),
    transcribe: (audio) => transcribeAt(`${space}/dictado`, audio),
  };
}

/** The team's door (J4): the space is the session's, never the request's. */
export function teamTasks(): TaskApi {
  return {
    load: (input) => loadTaskAt('/app/api/tareas', input),
    review: (input) => reviewTaskAt('/app/api/tareas/revisar', input),
    help: (input) => askLedaAt<Proposal>('/app/api/ayuda', input),
    spell: (texts) => checkSpellingAt('/app/api/ortografia', texts),
    transcribe: (audio) => transcribeAt('/app/api/dictado', audio),
  };
}

/** Closes this administration session on the server; the server also clears its cookie. */
export async function adminSignOut(): Promise<void> {
  const response = await fetch(`${ADMIN}/salir`, { method: 'POST', credentials: 'same-origin' });
  if (!response.ok && response.status !== 401) throw new RequestError(response.status);
}
