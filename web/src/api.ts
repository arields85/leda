// The platform's internal API (src/leda/web_app.py). Field names mirror the server's JSON,
// which is in Spanish like the rest of Leda's data.

export type Marca = 'vencida' | 'trabada' | 'en_curso' | 'entregada';
// "Mis pedidos" is a tab of its own (J4 phone test); the names come from the server (`VISTAS`).
// "Áreas" (`areas`, MA-6) is Dirección's: one card per area, then that area's tasks.
export type ViewId = 'tus' | 'sector' | 'equipo' | 'areas' | 'pedidas';

export interface ViewRef {
  vista: ViewId;
  titulo: string;
}

export interface Me {
  persona: string;
  // The person's area, under the name at the top right (MA-4).
  area?: string | null;
  espacio: string;
  // The space's slug, to enter again with the QR from this computer (ADR 0024).
  espacio_slug?: string | null;
  vistas: ViewRef[];
  // The Telegram chat with the team bot, when the space declares it (the page no longer shows it:
  // MA-4 took "Volver al chat" away).
  chat_con_leda: string | null;
  // Whether this person creates the team's objectives (Dirección, ADR 0023, decision 1): only then
  // the page offers "> Nuevo objetivo". The server refuses anyone else anyway.
  crea_objetivos?: boolean;
  // Whether this person loads tasks (Dirección and the area referentes, ADR 0023, decision 3; J4):
  // only then the page offers "> Nueva tarea". The server refuses anyone else anyway.
  carga_tareas?: boolean;
  // Whether this person sees "Equipo" (Dirección, ADR 0023, decision 4; J7-3). The server refuses
  // anyone else anyway.
  organiza_el_equipo?: boolean;
}

export interface Wait {
  que: string | null;
  quien: string | null;
  esperas: Wait[];
}

export interface Segment {
  fecha: string;
  momento: 'pasado' | 'hoy' | 'futuro';
}

export interface Task {
  id: string;
  titulo: string;
  estado: string;
  // The first mark gives the card its frame; the card shows them all (blocked and late can
  // come together).
  marca: Marca | null;
  marcas: Marca[];
  fecha_objetivo: string | null;
  // The day the person gave, later than the due date: a delay already talked about.
  prevision: string | null;
  asignada_el: string | null;
  responsable: string | null;
  area: string | null;
  papel: 'mia' | 'espero' | 'me_esperan' | null;
  // The server decides both: a waited task is late here only once the delay was talked about,
  // like in the group report. Never guess them.
  vencida: boolean | null;
  bloqueo_abierto: boolean | null;
  dias_de_atraso: number | null;
  ve_la_pagina: boolean;
  quedan_dias_habiles: number | null;
  barra: Segment[] | null;
  esperas: Wait[] | null;
  // Only in "Mis tareas": who asked for the task, when it was someone else (MA debt).
  pidio?: string | null;
}

/** A task finished in the last 30 days, with who did it. */
export interface Finished {
  id: string;
  titulo: string;
  responsable: string | null;
  area: string | null;
  terminada_el: string | null;
}

/** What the person asked from another area or from Dirección (J4, D14 and D1b): open, or finished
 * in the last 30 days; finished, she may ask for changes ("> pedir cambios"). */
export interface Requested {
  id: string;
  titulo: string;
  estado: string;
  responsable: string | null;
  area: string | null;
  fecha_objetivo: string | null;
  terminada_el: string | null;
  puede_pedir_cambios: boolean;
}

/** Someone of the referente's own area, to pass a task of the sector to (J4, D14 steps 2 and 3). */
export interface Teammate {
  membership_id: string;
  nombre: string;
  area: string;
}

export interface Day {
  fecha: string;
  dia: string;
  hoy: boolean;
  habil: boolean;
  vence_algo: boolean;
}

export interface ViewData {
  vista: ViewId;
  titulo: string;
  hoy: string;
  semana_iso: number;
  panel: Record<Marca, number>;
  activas: number;
  semana: Day[];
  tareas: Task[];
  terminadas: Finished[];
  // Only in "Mis pedidos" (J4): what the person asked from another area or from Dirección.
  pedidas?: Requested[];
  // Only in "Tu sector" (J4): to whom the referente may pass a task of the sector.
  pasar_a?: Teammate[];
  // Assigned and not started yet (MA-3): the counter "Sin empezar", apart from the four colours.
  sin_empezar?: number;
  // Only in a referente's "Mi área" (MA-3): the referente's area (or areas). Not shown since
  // the area went top right (MA-4).
  area_del_equipo?: string | null;
  // Only in one area of "Áreas" (MA-6): which area it is.
  area?: AreaRef;
}

/** An area of the space, with its referente (MA-6). */
export interface AreaRef {
  id: string;
  nombre: string;
  referente: string | null;
}

/** One card of "Áreas": the area and the counters of its list, counted by the server with the
 * same rules as the tiles (MA-6). */
export interface AreaCard extends AreaRef {
  panel: Record<Marca, number>;
  sin_empezar: number;
  activas: number;
}

/** "Áreas" before choosing one: a card per area of the space, in a stable order. */
export interface AreasOverview {
  vista: 'areas';
  titulo: string;
  areas: AreaCard[];
}

/** A task related to the one in the detail (it waits for it, or it waits for this one). Of one
 * the person may not see, only that it exists (`ve: false`). */
export interface RelatedTask {
  ve: boolean;
  titulo?: string;
  estado?: string;
  responsable?: string | null;
}

/** A piece of evidence in the detail, as the server's task page shows it. */
export interface DetailEvidence {
  clase: string;
  texto: string | null;
  enlace: string | null;
  nombre: string | null;
  imagen: boolean;
  archivo: string | null;
  quien: string | null;
  cuando: string | null;
  retirada: boolean;
  motivo_del_retiro: string | null;
}

/** The detail of a task inside the app (MA-3), under the rule of who sees what: the server
 * returns it only to someone who may see the task. States in plain words. */
export interface TaskDetail {
  titulo: string;
  estado: string;
  objetivo: string | null;
  area: string | null;
  responsable: string | null;
  revisa: string | null;
  pidio: string | null;
  vence: string | null;
  prevision: string | null;
  criterio: string | null;
  pide: { que: string; cubierto: boolean }[];
  evidencia: DetailEvidence[];
  espera_a: RelatedTask[];
  la_esperan: RelatedTask[];
}

/** The session is gone (cut, expired cookie, or the person left the team). */
export class SessionClosedError extends Error {
  constructor() {
    super('session closed');
  }
}

/** Any other failure: the page shows a plain message, never the details. */
export class RequestError extends Error {
  constructor(readonly status: number) {
    super(`request failed (${status})`);
  }
}

async function getJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
      signal,
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new RequestError(0);
  }
  if (response.status === 401) throw new SessionClosedError();
  if (!response.ok) throw new RequestError(response.status);
  return (await response.json()) as T;
}

export function fetchMe(signal?: AbortSignal): Promise<Me> {
  return getJson<Me>('/app/api/yo', signal);
}

export function fetchView(view: ViewId, signal?: AbortSignal, area?: string | null): Promise<ViewData> {
  const inArea = area ? `&area=${encodeURIComponent(area)}` : '';
  return getJson<ViewData>(`/app/api/tareas?vista=${encodeURIComponent(view)}${inArea}`, signal);
}

/** "Áreas" before choosing one (MA-6). */
export function fetchAreas(signal?: AbortSignal): Promise<AreasOverview> {
  return getJson<AreasOverview>('/app/api/tareas?vista=areas', signal);
}

/** One problem the server found with a pass or a reopening, in plain words. */
export interface ActionProblem {
  campo: string;
  motivo: string;
  texto: string;
}

export type ActionResult = { kind: 'done' } | { kind: 'rejected'; errors: ActionProblem[] };

async function postJson(url: string, body: unknown): Promise<ActionResult> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch {
    throw new RequestError(0);
  }
  if (response.status === 401) throw new SessionClosedError();
  if (response.ok) return { kind: 'done' };
  if (response.status === 422 || response.status === 403) {
    try {
      const data = (await response.json()) as { errores?: ActionProblem[]; error?: string; texto?: string };
      if (Array.isArray(data.errores) && data.errores.length > 0) return { kind: 'rejected', errors: data.errores };
      if (typeof data.texto === 'string') {
        return { kind: 'rejected', errors: [{ campo: 'sesion', motivo: data.error ?? 'sin_autoridad', texto: data.texto }] };
      }
    } catch {
      // Below: a failure without its reasons is never shown as silence.
    }
  }
  throw new RequestError(response.status);
}

/** The referente passes a task of the sector to someone of the area (J4): it waits until that
 * person takes it by chat. */
export function passTask(taskId: string, to: string): Promise<ActionResult> {
  return postJson(`/app/api/tareas/${encodeURIComponent(taskId)}/pase`, { a_membership_id: to });
}

/** Whoever asked for a finished task reopens it, with what has to change (J4, D14 step 5). */
export function reopenTask(taskId: string, reason: string): Promise<ActionResult> {
  return postJson(`/app/api/tareas/${encodeURIComponent(taskId)}/reabrir`, { motivo: reason });
}

/** The detail of a task inside the app (MA-3): `null` when the person may not see it. */
export async function fetchTaskDetail(taskId: string): Promise<TaskDetail | null> {
  let response: Response;
  try {
    response = await fetch(`/app/api/tareas/${encodeURIComponent(taskId)}/detalle`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    });
  } catch {
    throw new RequestError(0);
  }
  if (response.status === 401) throw new SessionClosedError();
  if (response.status === 403 || response.status === 404) return null;
  if (!response.ok) throw new RequestError(response.status);
  return (await response.json()) as TaskDetail;
}

/** Closes this session on the server; the server also clears the cookie. */
export async function signOut(): Promise<void> {
  const response = await fetch('/app/salir', { method: 'POST', credentials: 'same-origin' });
  // 401: the session was already closed, which is what the person wanted.
  if (!response.ok && response.status !== 401) throw new RequestError(response.status);
}
