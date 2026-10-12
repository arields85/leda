// The platform's internal API (src/leda/web_app.py). Field names mirror the server's JSON,
// which is in Spanish like the rest of Leda's data.

export type Marca = 'vencida' | 'trabada' | 'en_curso' | 'entregada';
export type ViewId = 'tus' | 'sector' | 'equipo';

export interface ViewRef {
  vista: ViewId;
  titulo: string;
}

export interface Me {
  persona: string;
  espacio: string;
  vistas: ViewRef[];
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
  marca: Marca | null;
  fecha_objetivo: string | null;
  asignada_el: string | null;
  responsable: string | null;
  area: string | null;
  papel: 'mia' | 'espero' | 'me_esperan' | null;
  // Null means this person is not shown the delay or the block: never guess it.
  vencida: boolean | null;
  bloqueo_abierto: boolean | null;
  dias_de_atraso: number | null;
  ve_la_pagina: boolean;
  quedan_dias_habiles: number | null;
  barra: Segment[] | null;
  esperas: Wait[] | null;
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

export function fetchView(view: ViewId, signal?: AbortSignal): Promise<ViewData> {
  return getJson<ViewData>(`/app/api/tareas?vista=${encodeURIComponent(view)}`, signal);
}

/** Closes this session on the server; the server also clears the cookie. */
export async function signOut(): Promise<void> {
  const response = await fetch('/app/salir', { method: 'POST', credentials: 'same-origin' });
  // 401: the session was already closed, which is what the person wanted.
  if (!response.ok && response.status !== 401) throw new RequestError(response.status);
}
