import { shortDate } from '../format';
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
  padre_id: 'es parte de',
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

/** The user's decision 5 (2026-10-14; migration 0070): an objective never falls due after the one
 * it hangs from, when that one has a date (the pack's first objectives have none). The parent it
 * would fall due after, if any. */
export function lateForParent(draft: ObjectiveDraft, options: ObjectiveOptions): ParentObjective | undefined {
  const parent = parentOf(options, draft.padre_id);
  return parent?.fecha_objetivo && draft.fecha && draft.fecha > parent.fecha_objetivo ? parent : undefined;
}

/** What Leda says when it stops such an objective: the parent by its name and its day (J3-7: in
 * the words of the form, "es parte de"). */
export function dueAfterParentText(parent: ParentObjective): string {
  const day = parent.fecha_objetivo ? ` (${shortDate(parent.fecha_objetivo)})` : '';
  return `Este objetivo vence después que «${parent.titulo}»${day}: es parte de ese objetivo, que se demoraría.`;
}

/** A level's name with its indefinite article ("un objetivo general", "una etapa"), by the first
 * word of the pack's name: one that ends in "a" takes "una" (J3-7). */
export function withArticle(level: string): string {
  const first = level.trim().split(/\s+/)[0] ?? '';
  return `${/a$/i.test(first) ? 'una' : 'un'} ${level}`;
}

/** The empty choice of "Es parte de" (J3-7): it is part of nothing, so it is the biggest level. */
export function noParentLabel(levels: ObjectiveOptions['niveles']): string {
  return `de ninguno (es ${withArticle(levels.estrategico)})`;
}

/** One plain line about the chosen type, with the pack's names of the levels (J3-7, the user did
 * not understand the form): the biggest, what the work is for; an important step of it; something
 * concrete one area does. */
export function typeMeaning(tipo: string, levels: ObjectiveOptions['niveles']): string | null {
  const name = (level: string) => level.charAt(0).toUpperCase() + level.slice(1);
  if (tipo === 'estrategico') return `${name(levels.estrategico)}: lo más grande, para qué es todo el trabajo.`;
  if (tipo === 'hito') return `${name(levels.hito)}: un paso importante de ${withArticle(levels.estrategico)}.`;
  if (tipo === 'operativo') return `${name(levels.operativo)}: algo concreto que hace un área.`;
  return null;
}

/** The refusal of a child due after its parent (`fecha`, `vence_despues_del_padre`). */
export const LATE_FOR_PARENT = 'vence_despues_del_padre';

/** Where "cargarlo aparte" takes it: next to its parent, hanging from the parent's own parent
 * (when it is one it can hang from), or from none when the parent is a root. */
export function apartFrom(options: ObjectiveOptions, parent: ParentObjective): string {
  return parent.padre_id && parentOf(options, parent.padre_id) ? parent.padre_id : '';
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
  const late = lateForParent(draft, options);
  if (late) problems.push({ campo: 'fecha', motivo: LATE_FOR_PARENT, texto: dueAfterParentText(late) });
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
