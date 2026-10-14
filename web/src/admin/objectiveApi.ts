// Creating an objective from the web (ADR 0023, decisions 1 and 5 and point 11; migrations 0068
// and 0069). Two doors with the same shape: the administration's, in any space
// (`/app/admin/api/espacios/{id}/objetivos`), and the team's, only for Dirección
// (`/app/api/objetivos`). The form takes an `ObjectiveApi`, so the same form serves both doors.
// Field names mirror the server's JSON, which is in Spanish like the rest of Leda's data.
import { RequestError } from '../api';
import {
  askLedaAt,
  call,
  checkSpellingAt,
  type DictationResult,
  type HelpResult,
  type Options,
  type Problem,
  type Spelling,
  transcribeAt,
} from './api';

/** The objective levels of the core (mechanics §1), as the server names them. */
export type ObjectiveType = 'estrategico' | 'hito' | 'operativo';

/** An open objective a new one may hang from, with the types it admits under it, its date and
 * what it hangs from itself (migration 0070: the form stops a child that would fall due after it,
 * and "cargarlo aparte" moves the child to hang from the parent's own parent). */
export interface ParentObjective {
  id: string;
  titulo: string;
  tipo: ObjectiveType;
  estado: string;
  fecha_objetivo: string | null;
  padre_id: string | null;
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

/** What the form sends to ask Leda to complete it (J3-4): what the person told in the free box and
 * what the form already has. `tipo` goes only when the person chose it herself (otherwise '':
 * Leda proposes the one that fits where it hangs). */
export interface ObjectiveHelpInput {
  texto: string;
  titulo: string;
  descripcion: string;
  padre_id: string;
  tipo: string;
  referente_id: string;
  fecha: string;
}

/** What Leda proposes for an objective, with the form's field names. */
export type ObjectiveProposal = Partial<{
  titulo: string;
  descripcion: string;
  padre_id: string;
  tipo: string;
  referente_id: string;
  fecha: string;
}>;

/** Leda's help through a door (J3-4): completing the form, its spelling and its dictation, each at
 * that door's own address. */
export interface ObjectiveAssist {
  help(input: ObjectiveHelpInput): Promise<HelpResult<ObjectiveProposal>>;
  spell(texts: Partial<Record<'titulo' | 'descripcion', string>>): Promise<Spelling>;
  transcribe(audio: Blob): Promise<DictationResult>;
}

export interface ObjectiveApi {
  options(signal?: AbortSignal): Promise<ObjectiveOptions>;
  create(input: ObjectiveInput): Promise<CreateResult>;
  /** Leda's help; a door without it shows the form by hand only. */
  assist?: ObjectiveAssist;
}

/** The server's words when the person is not Dirección (src/leda/web_app.py,
 * TEXTO_SIN_AUTORIDAD). */
export const NO_AUTHORITY = 'Crear objetivos le corresponde a Dirección.';

/** Leda's help at one door: completing at `${base}/ayuda`, the spelling and the dictation at the
 * door's own addresses. */
export function objectiveAssist(base: string, spelling: string, dictation: string): ObjectiveAssist {
  return {
    help: (input) => askLedaAt<ObjectiveProposal>(`${base}/ayuda`, input),
    spell: (texts) => checkSpellingAt(spelling, texts, 'objetivo'),
    transcribe: (audio) => transcribeAt(dictation, audio),
  };
}

/** The API of one door, from its base path. */
export function objectiveApi(base: string, assist?: ObjectiveAssist): ObjectiveApi {
  return {
    assist,
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
  const space = `/app/admin/api/espacios/${encodeURIComponent(spaceId)}`;
  const base = `${space}/objetivos`;
  return objectiveApi(base, objectiveAssist(base, `${space}/ortografia`, `${space}/dictado`));
}

/** The team's door: the space is the session's, never the request's. */
export function teamObjectives(): ObjectiveApi {
  const base = '/app/api/objetivos';
  return objectiveApi(base, objectiveAssist(base, '/app/api/ortografia', '/app/api/dictado'));
}
