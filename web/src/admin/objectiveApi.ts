// Creating an objective from the web (ADR 0023, decisions 1 and 5 and point 11; migrations 0068
// and 0069). Two doors with the same shape: the administration's, in any space
// (`/app/admin/api/espacios/{id}/objetivos`), and the team's, only for Dirección
// (`/app/api/objetivos`). The form takes an `ObjectiveApi`, so the same form serves both doors.
// Field names mirror the server's JSON, which is in Spanish like the rest of Leda's data.
import { RequestError } from '../api';
import { call, type Options, type Problem } from './api';

/** The objective levels of the core (mechanics §1), as the server names them. */
export type ObjectiveType = 'estrategico' | 'hito' | 'operativo';

/** An open objective a new one may hang from, with the types it admits under it. */
export interface ParentObjective {
  id: string;
  titulo: string;
  tipo: ObjectiveType;
  estado: string;
  fecha_objetivo: string | null;
  tipos: ObjectiveType[];
}

/** An active area referente (the user's decision, 2026-10-14: an objective's referente is always
 * one), with the areas she is the referente of. */
export interface AreaReferent {
  membership_id: string;
  nombre: string;
  areas: string[];
}

export interface ObjectiveOptions {
  espacio: { id: string; nombre: string; zona_horaria?: string };
  hoy: string;
  // How the space's pack names each level ("plan anual", "campaña"…), over the core's names.
  niveles: Record<ObjectiveType, string>;
  // The types an objective without a parent may have: only the strategic one.
  sin_padre: ObjectiveType[];
  padres: ParentObjective[];
  referentes: AreaReferent[];
  calendario: Options['calendario'];
}

/** What the form sends: the server's names, with the idempotency key of this attempt.
 * `padre_id` is left out when it hangs from none. */
export interface ObjectiveInput {
  titulo: string;
  descripcion: string;
  padre_id?: string;
  tipo: string;
  referente_id: string;
  fecha: string;
  clave: string;
}

export type CreateResult =
  | { kind: 'created'; objectiveId: string; repeated: boolean }
  | { kind: 'rejected'; errors: Problem[] };

export interface ObjectiveApi {
  options(signal?: AbortSignal): Promise<ObjectiveOptions>;
  create(input: ObjectiveInput): Promise<CreateResult>;
}

/** The server's words when the person is not Dirección (src/leda/web_app.py,
 * TEXTO_SIN_AUTORIDAD). */
export const NO_AUTHORITY = 'Crear objetivos le corresponde a Dirección.';

/** The API of one door, from its base path. */
export function objectiveApi(base: string): ObjectiveApi {
  return {
    async options(signal) {
      const response = await call(`${base}/opciones`, { signal });
      if (!response.ok) throw new RequestError(response.status);
      return (await response.json()) as ObjectiveOptions;
    },
    /** 201 creates it; 200 means this key already created it (a retry); 422 lists what to fix;
     * 403, that only Dirección creates objectives. Anything else throws, so the form keeps the data
     * for a retry with the same key. */
    async create(input) {
      const response = await call(base, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });
      if (response.status === 201 || response.status === 200) {
        const body = (await response.json()) as { objective_id: string; repetida?: boolean };
        return { kind: 'created', objectiveId: body.objective_id, repeated: Boolean(body.repetida) };
      }
      if (response.status === 422) {
        const body = (await response.json()) as { errores?: Problem[] };
        return { kind: 'rejected', errors: body.errores ?? [] };
      }
      if (response.status === 403) {
        let texto = NO_AUTHORITY;
        try {
          const body = (await response.json()) as { texto?: unknown };
          if (typeof body?.texto === 'string' && body.texto.trim()) texto = body.texto;
        } catch {
          // The plain words above.
        }
        return { kind: 'rejected', errors: [{ campo: 'sesion', motivo: 'sin_autoridad', texto }] };
      }
      throw new RequestError(response.status);
    },
  };
}

/** The administration's door, in one space. */
export function adminObjectives(spaceId: string): ObjectiveApi {
  return objectiveApi(`/app/admin/api/espacios/${encodeURIComponent(spaceId)}/objetivos`);
}

/** The team's door: the space is the session's, never the request's. */
export function teamObjectives(): ObjectiveApi {
  return objectiveApi('/app/api/objetivos');
}
