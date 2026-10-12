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

/** Closes this administration session on the server; the server also clears its cookie. */
export async function adminSignOut(): Promise<void> {
  const response = await fetch(`${ADMIN}/salir`, { method: 'POST', credentials: 'same-origin' });
  if (!response.ok && response.status !== 401) throw new RequestError(response.status);
}
