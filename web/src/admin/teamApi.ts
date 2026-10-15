// Seeing the team from the web (J7-3; ADR 0023, decisions 4 and 5; migration 0082). Two doors with
// the same shape: the administration's, in any space (`/app/admin/api/espacios/{id}/equipo`), and
// the team's, only for Dirección (`/app/api/equipo`). The view takes a `TeamApi`, so the same view
// serves both doors. Field names mirror the server's JSON, which is in Spanish like the rest of
// Leda's data. The areas change from here too (J7-4; migration 0083): a preview first, then the
// confirmation with the preview's fingerprint and a key of its own.
import { RequestError } from '../api';
import { call, type Problem } from './api';

/** A person named from an area or another person: the referente, the approver. */
export interface TeamRef {
  membership_id: string;
  nombre: string;
  activo: boolean;
}

export interface TeamArea {
  id: string;
  slug: string;
  nombre: string;
  // An area is never deleted, it is archived (J7-1): it comes last, marked.
  archivada: boolean;
  referente: TeamRef | null;
  // The area declared that its work approves itself (mechanics §7).
  autoaprobacion: boolean;
  // The active people of the area, by `membership_id`.
  personas: string[];
  tareas_abiertas: number;
}

export interface TeamPerson {
  membership_id: string;
  nombre: string;
  // No longer in the team: listed apart, never in an area.
  activo: boolean;
  // Whether this person already activated Leda in Telegram; «sin conectar» when not.
  conectado: boolean;
  area_id: string;
  area: string;
  rol_id: string;
  rol: string;
  autoridad_final: boolean;
  aprobador: TeamRef | null;
  referente_de: string[];
}

export interface TeamRole {
  id: string;
  slug: string;
  nombre: string;
  autoridad_final: boolean;
  personas: number;
}

/** What does not add up in the team (`problemas_del_equipo`), in everyday words. */
export interface TeamProblem {
  codigo: string;
  mensaje: string;
}

/** One change of the team, with its before and after (`cambio_del_equipo`). */
export interface TeamChange {
  id: string;
  clase: string;
  puerta: 'equipo' | 'administracion';
  quien: string;
  at: string;
  antes: Record<string, unknown> | null;
  despues: Record<string, unknown> | null;
}

/** An evidence type of the space, to choose what a new area's tasks require. */
export interface EvidenceKind {
  tipo: string;
  en_palabras: string;
}

export interface Team {
  espacio: { id: string; nombre: string };
  areas: TeamArea[];
  personas: TeamPerson[];
  roles: TeamRole[];
  problemas: TeamProblem[];
  cambios: TeamChange[];
  tipos_de_evidencia: EvidenceKind[];
}

/** Who approves a new area's work (mechanics §7): its referente, the area itself (declared on
 * purpose) or, with no referente, Dirección decides. */
export type Approval = 'referente' | 'autoaprobacion' | 'direccion';

/** One change to an area, as the server reads it. */
export type AreaChange =
  | {
      accion: 'crear';
      nombre: string;
      aprobacion: Approval | null;
      referente_id: string | null;
      evidencia: string[];
      sin_evidencia: boolean;
    }
  | { accion: 'renombrar'; area_id: string; nombre: string }
  | { accion: 'archivar'; area_id: string };

/** What a change would do, in words, with its fingerprint and the problems it would leave. */
export interface AreaPreview {
  accion: AreaChange['accion'];
  antes: Record<string, unknown> | null;
  despues: Record<string, unknown> | null;
  huella: string;
  problemas: TeamProblem[];
  problemas_nuevos: TeamProblem[];
}

export type PreviewResult = { kind: 'preview'; preview: AreaPreview } | { kind: 'rejected'; errors: Problem[] };
export type ChangeResult =
  | { kind: 'done'; areaId: string; repeated: boolean }
  | { kind: 'rejected'; errors: Problem[] };

export type TeamRead =
  | { kind: 'team'; team: Team }
  | { kind: 'denied'; texto: string }
  | { kind: 'gone' };

/** The server's words when the person is not Dirección (src/leda/web_equipo.py,
 * TEXTO_SIN_AUTORIDAD). */
export const NO_AUTHORITY = 'Organizar el equipo le corresponde a Dirección.';

export interface TeamApi {
  /** 200, the team; 403, who may not see it, with the server's words; 404, the space is gone. A
   * closed session throws `SessionClosedError`; anything else, `RequestError`. */
  read(signal?: AbortSignal): Promise<TeamRead>;
  /** 200, what the change would do; 422 or 403, what does not allow it, in the server's words.
   * Writes nothing. */
  preview(change: AreaChange): Promise<PreviewResult>;
  /** 201 does it; 200 means this key already did it (a retry); 422 or 403, what does not allow it.
   * Anything else throws, so the view keeps the key for a retry. */
  confirm(change: AreaChange, clave: string, huella: string): Promise<ChangeResult>;
}

async function refusal(response: Response): Promise<Problem[]> {
  if (response.status === 403) {
    let texto = NO_AUTHORITY;
    try {
      const body = (await response.json()) as { texto?: unknown };
      if (typeof body?.texto === 'string' && body.texto.trim()) texto = body.texto;
    } catch {
      // The plain words above.
    }
    return [{ campo: 'sesion', motivo: 'sin_autoridad', texto }];
  }
  const body = (await response.json()) as { errores?: Problem[] };
  return body.errores ?? [];
}

function post(url: string, body: unknown): Promise<Response> {
  return call(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

export function teamApi(base: string): TeamApi {
  return {
    async read(signal) {
      const response = await call(base, { signal });
      if (response.ok) return { kind: 'team', team: (await response.json()) as Team };
      if (response.status === 403) {
        let texto = NO_AUTHORITY;
        try {
          const body = (await response.json()) as { texto?: unknown };
          if (typeof body?.texto === 'string' && body.texto.trim()) texto = body.texto;
        } catch {
          // The plain words above.
        }
        return { kind: 'denied', texto };
      }
      if (response.status === 404) return { kind: 'gone' };
      throw new RequestError(response.status);
    },
    async preview(change) {
      const response = await post(`${base}/areas/revisar`, change);
      if (response.ok) return { kind: 'preview', preview: (await response.json()) as AreaPreview };
      if (response.status === 422 || response.status === 403) {
        return { kind: 'rejected', errors: await refusal(response) };
      }
      throw new RequestError(response.status);
    },
    async confirm(change, clave, huella) {
      const response = await post(`${base}/areas`, { ...change, clave, huella });
      if (response.status === 201 || response.status === 200) {
        const body = (await response.json()) as { area_id: string; repetida?: boolean };
        return { kind: 'done', areaId: body.area_id, repeated: Boolean(body.repetida) };
      }
      if (response.status === 422 || response.status === 403) {
        return { kind: 'rejected', errors: await refusal(response) };
      }
      throw new RequestError(response.status);
    },
  };
}

/** The administration's door, in one space. */
export function adminTeam(spaceId: string): TeamApi {
  return teamApi(`/app/admin/api/espacios/${encodeURIComponent(spaceId)}/equipo`);
}

/** The team's door: the space is the session's, never the request's. */
export function ownTeam(): TeamApi {
  return teamApi('/app/api/equipo');
}
