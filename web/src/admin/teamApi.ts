// Seeing the team from the web (J7-3; ADR 0023, decisions 4 and 5; migration 0082). Two doors with
// the same shape: the administration's, in any space (`/app/admin/api/espacios/{id}/equipo`), and
// the team's, only for Dirección (`/app/api/equipo`). The view takes a `TeamApi`, so the same view
// serves both doors. Field names mirror the server's JSON, which is in Spanish like the rest of
// Leda's data. Nothing here changes the team yet.
import { RequestError } from '../api';
import { call } from './api';

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

export interface Team {
  espacio: { id: string; nombre: string };
  areas: TeamArea[];
  personas: TeamPerson[];
  roles: TeamRole[];
  problemas: TeamProblem[];
  cambios: TeamChange[];
}

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
