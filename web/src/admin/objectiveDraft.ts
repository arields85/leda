import type { Problem } from './api';
import { length } from './draft';
import type { AreaReferent, ObjectiveInput, ObjectiveOptions, ObjectiveType, ParentObjective } from './objectiveApi';

/** What the person is writing, before the idempotency key is added. `padre_id` is '' while it
 * hangs from none; `tipo` is '' only when nothing can be offered. */
export interface ObjectiveDraft {
  titulo: string;
  padre_id: string;
  tipo: ObjectiveType | '';
  referente_id: string;
  fecha: string;
  descripcion: string;
}

export type ObjectiveField = keyof ObjectiveDraft;

/** The server's limits, in characters of the trimmed text (migration 0068). */
export const OBJECTIVE_LIMITS = { titulo: 200, descripcion: 800 } as const;

/** The server names each problem with these `campo` values; the rest go to the summary. */
export const OBJECTIVE_PROBLEM_FIELD: Record<string, ObjectiveField> = {
  titulo: 'titulo',
  padre: 'padre_id',
  tipo: 'tipo',
  referente: 'referente_id',
  fecha: 'fecha',
  descripcion: 'descripcion',
};

/** The fields in the order the form shows them: the first one with a problem gets the focus. */
export const OBJECTIVE_FIELD_ORDER: ObjectiveField[] = ['titulo', 'padre_id', 'tipo', 'referente_id', 'fecha', 'descripcion'];

/** How each field is named to the person, the same words as its label. */
export const OBJECTIVE_FIELD_NAME: Record<ObjectiveField, string> = {
  titulo: 'nombre',
  padre_id: 'de qué cuelga',
  tipo: 'tipo',
  referente_id: 'referente',
  fecha: 'fecha',
  descripcion: 'descripción',
};

/** The element of each field in the form. Their own ids, never the task form's. */
export const OBJECTIVE_FIELD_ID: Record<ObjectiveField, string> = {
  titulo: 'o-titulo',
  padre_id: 'o-padre',
  tipo: 'o-tipo',
  referente_id: 'o-referente',
  fecha: 'o-fecha',
  descripcion: 'o-descripcion',
};

// The server's own words for what the form can tell before sending (src/leda/web_app.py,
// TEXTOS_DEL_OBJETIVO), so a problem reads the same whoever found it.
const MISSING_TEXT = {
  titulo: 'Falta el nombre del objetivo.',
  tipo: 'Elegí el tipo de objetivo.',
  referente: 'Elegí quién es el referente.',
  fecha: 'Elegí la fecha.',
} as const;
const TOO_LONG_TEXT = {
  titulo: 'El nombre es demasiado largo: hasta 200 caracteres.',
  descripcion: 'La descripción es demasiado larga: hasta 800 caracteres.',
} as const;

export function parentOf(options: ObjectiveOptions, id: string): ParentObjective | undefined {
  return id ? options.padres.find((p) => p.id === id) : undefined;
}

export function referentOf(options: ObjectiveOptions, id: string): AreaReferent | undefined {
  return id ? options.referentes.find((r) => r.membership_id === id) : undefined;
}

/** The types an objective may have where it hangs (point 11): without a parent, only the
 * strategic one; under a strategic one, a milestone or an operational one; under a milestone, an
 * operational one. As the server offers them. */
export function typesFor(options: ObjectiveOptions, parentId: string): ObjectiveType[] {
  if (!parentId) return options.sin_padre;
  return parentOf(options, parentId)?.tipos ?? [];
}

/** The type chosen for the person when the parent changes: the only one when there is one (no
 * question), the operational one when it can be a milestone or an operational one. */
export function defaultType(types: ObjectiveType[]): ObjectiveType | '' {
  return types.includes('operativo') ? 'operativo' : (types[0] ?? '');
}

export function emptyObjective(options: ObjectiveOptions): ObjectiveDraft {
  return {
    titulo: '',
    padre_id: '',
    tipo: defaultType(typesFor(options, '')),
    referente_id: '',
    fecha: '',
    descripcion: '',
  };
}

/** What the form can already tell is missing or too long, before sending: the same `campo` and
 * `motivo` the server would answer. The server stays the judge of everything else (a day that is
 * not a working day, a referente who stopped being one, a parent that closed). */
export function checkObjective(draft: ObjectiveDraft, options: ObjectiveOptions): Problem[] {
  const problems: Problem[] = [];
  const missing = (campo: keyof typeof MISSING_TEXT) =>
    problems.push({ campo, motivo: 'falta', texto: MISSING_TEXT[campo] });
  const tooLong = (campo: keyof typeof TOO_LONG_TEXT) =>
    problems.push({ campo, motivo: 'demasiado_largo', texto: TOO_LONG_TEXT[campo] });

  if (length(draft.titulo) === 0) missing('titulo');
  else if (length(draft.titulo) > OBJECTIVE_LIMITS.titulo) tooLong('titulo');
  if (!draft.tipo || !typesFor(options, draft.padre_id).includes(draft.tipo)) missing('tipo');
  if (!draft.referente_id) missing('referente');
  if (!draft.fecha) missing('fecha');
  if (length(draft.descripcion) > OBJECTIVE_LIMITS.descripcion) tooLong('descripcion');
  return problems;
}

/** What the form sends: the draft and its key, without `padre_id` when it hangs from none. */
export function toObjectiveInput(draft: ObjectiveDraft, clave: string): ObjectiveInput {
  const { padre_id, ...rest } = draft;
  return padre_id ? { ...rest, padre_id, clave } : { ...rest, clave };
}

/** How a possible parent is named in the list: its name, its level and, if it has one, its date. */
export function parentLabel(parent: ParentObjective, levels: ObjectiveOptions['niveles'], date?: string): string {
  return [parent.titulo, levels[parent.tipo], date ? `hasta ${date}` : ''].filter(Boolean).join(' · ');
}
