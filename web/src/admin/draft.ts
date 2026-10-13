import type { Task } from '../api';
import type { Member, Options, Policy, Problem, Proposal, TaskInput, WaitableTask } from './api';

/** What the administrator is writing, before the idempotency key is added. `espera_id` is ''
 * while it waits for no task. */
export type Draft = Omit<TaskInput, 'clave' | 'espera_id'> & { espera_id: string };

export type Field = keyof Draft;

export const EMPTY_DRAFT: Draft = {
  objetivo_id: '',
  titulo: '',
  descripcion: '',
  responsable_id: '',
  fecha: '',
  criterio: '',
  evidencia: [],
  decidio_id: '',
  espera_id: '',
};

/** The server's limits, in characters of the trimmed text (migration 0062). */
export const LIMITS = { titulo: 200, descripcion: 800, criterio: 500 } as const;

/** The server names each problem with these `campo` values; the rest go to the summary. */
export const PROBLEM_FIELD: Record<string, Field> = {
  objetivo: 'objetivo_id',
  titulo: 'titulo',
  descripcion: 'descripcion',
  responsable: 'responsable_id',
  fecha: 'fecha',
  criterio: 'criterio',
  evidencia: 'evidencia',
  decidio: 'decidio_id',
  espera: 'espera_id',
};

/** The fields in the order the form shows them: the first one with a problem gets the focus. */
export const FIELD_ORDER: Field[] = [
  'objetivo_id',
  'titulo',
  'descripcion',
  'responsable_id',
  'fecha',
  'espera_id',
  'criterio',
  'evidencia',
  'decidio_id',
];

/** How each field is named to the person, the same words as its label. */
export const FIELD_NAME: Record<Field, string> = {
  objetivo_id: 'objetivo',
  titulo: 'título',
  descripcion: 'descripción',
  responsable_id: 'quién la hace',
  fecha: 'fecha',
  espera_id: 'espera a',
  criterio: 'criterio de aceptación',
  evidencia: 'evidencia',
  decidio_id: 'quién la decidió',
};

/** The element of each field in the form (a control, the calendar or the evidence group). */
export const FIELD_ID: Record<Field, string> = {
  objetivo_id: 'f-objetivo',
  titulo: 'f-titulo',
  descripcion: 'f-descripcion',
  responsable_id: 'f-responsable',
  fecha: 'f-fecha',
  espera_id: 'f-espera',
  criterio: 'f-criterio',
  evidencia: 'f-evidencia',
  decidio_id: 'f-decidio',
};

// The server's own words for what the form can tell before sending (src/leda/web_app.py,
// TEXTOS_DE_LA_CARGA), so a problem reads the same whoever found it.
const MISSING_TEXT = {
  objetivo: 'Elegí el objetivo al que contribuye la tarea.',
  titulo: 'Falta el título.',
  responsable: 'Elegí quién la va a hacer.',
  fecha: 'Elegí la fecha.',
  criterio: 'Falta el criterio de aceptación: qué tiene que pasar para darla por terminada.',
  evidencia: 'Elegí la evidencia que se pide para darla por terminada.',
  decidio: 'Elegí quién decidió la tarea.',
} as const;
const TOO_LONG_TEXT = {
  titulo: 'El título es demasiado largo: hasta 200 caracteres.',
  descripcion: 'La descripción es demasiado larga: hasta 800 caracteres.',
  criterio: 'El criterio es demasiado largo: hasta 500 caracteres.',
} as const;

/** What the form can already tell is missing or too long, before sending: the same `campo` and
 * `motivo` the server would answer. The server stays the judge of everything else (a day that
 * is not a working day, nobody to review, an area without an evidence policy). */
export function checkDraft(draft: Draft, options: Options): Problem[] {
  const problems: Problem[] = [];
  const missing = (campo: keyof typeof MISSING_TEXT) =>
    problems.push({ campo, motivo: 'falta', texto: MISSING_TEXT[campo] });
  const tooLong = (campo: keyof typeof TOO_LONG_TEXT) =>
    problems.push({ campo, motivo: 'demasiado_largo', texto: TOO_LONG_TEXT[campo] });

  if (!draft.objetivo_id) missing('objetivo');
  if (length(draft.titulo) === 0) missing('titulo');
  else if (length(draft.titulo) > LIMITS.titulo) tooLong('titulo');
  if (length(draft.descripcion) > LIMITS.descripcion) tooLong('descripcion');
  if (!draft.responsable_id) missing('responsable');
  if (!draft.fecha) missing('fecha');
  if (length(draft.criterio) === 0) missing('criterio');
  else if (length(draft.criterio) > LIMITS.criterio) tooLong('criterio');
  const policy = policyOf(options, memberOf(options, draft.responsable_id));
  if (policy && policy.evidencia_requerida.length > 0 && draft.evidencia.length === 0) missing('evidencia');
  if (!draft.decidio_id) missing('decidio');
  return problems;
}

/** What the form sends: the draft and its key, without `espera_id` when it waits for none, so a
 * load without a wait is the same request as before migration 0067. */
export function toInput(draft: Draft, clave: string): TaskInput {
  const { espera_id, ...rest } = draft;
  return espera_id ? { ...rest, espera_id, clave } : { ...rest, clave };
}

/** The tasks a new one may wait for, as the server offers them. */
export function waitableTasks(options: Options): WaitableTask[] {
  return options.tareas ?? [];
}

export function waitOf(options: Options, id: string): WaitableTask | undefined {
  return id ? waitableTasks(options).find((t) => t.id === id) : undefined;
}

/** How a task to wait for is named in the form: title, who does it and its objective. */
export function waitLabel(task: WaitableTask): string {
  return [task.titulo, task.responsable, task.objetivo].filter(Boolean).join(' · ');
}

/** A new idempotency key for one attempt. `crypto.randomUUID` exists only on HTTPS or
 * localhost; elsewhere (a phone on the local network over plain HTTP) 32 random hex digits,
 * which the server also accepts. */
export function newKey(): string {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

/** Characters as the server counts them (code points of the trimmed text). */
export function length(text: string): number {
  return Array.from(text.trim()).length;
}

export function memberOf(options: Options, id: string): Member | undefined {
  return options.integrantes.find((m) => m.membership_id === id);
}

export function policyOf(options: Options, member: Member | undefined): Policy | undefined {
  return member ? options.politicas.find((p) => p.area_id === member.area_id) : undefined;
}

/** The evidence an area knows: the kinds it asks for first, then the other kinds it accepts. */
export function evidenceKinds(policy: Policy | undefined): string[] {
  if (!policy) return [];
  const extra = Object.keys(policy.tipos).filter((k) => !policy.evidencia_requerida.includes(k));
  return [...policy.evidencia_requerida, ...extra.sort()];
}

/** How a kind of evidence is said in everyday words, from the area's policy. */
export function evidenceWords(policy: Policy | undefined, kind: string): string {
  return policy?.tipos[kind]?.en_palabras ?? kind.replace(/_/g, ' ');
}

/** What Leda proposed that the options really offer: a person, a task to wait for, an objective
 * and a working day from the lists, and the texts within the form's limits. The server already
 * checked it; the form never fills a field with something it could not offer by hand. */
export function validProposal(proposal: Proposal, options: Options): Proposal {
  const valid: Proposal = {};
  const text = (value: unknown, limit: number) =>
    typeof value === 'string' && length(value) > 0 && length(value) <= limit ? value.trim() : undefined;
  const titulo = text(proposal.titulo, LIMITS.titulo);
  const descripcion = text(proposal.descripcion, LIMITS.descripcion);
  const criterio = text(proposal.criterio, LIMITS.criterio);
  if (titulo) valid.titulo = titulo;
  if (descripcion) valid.descripcion = descripcion;
  if (criterio) valid.criterio = criterio;
  if (proposal.responsable_id && memberOf(options, proposal.responsable_id)) valid.responsable_id = proposal.responsable_id;
  if (proposal.espera_id && waitOf(options, proposal.espera_id)) valid.espera_id = proposal.espera_id;
  if (proposal.objetivo_id && options.objetivos.some((o) => o.id === proposal.objetivo_id)) {
    valid.objetivo_id = proposal.objetivo_id;
  }
  if (proposal.fecha && options.calendario.dias_habiles.includes(proposal.fecha)) valid.fecha = proposal.fecha;
  return valid;
}

/** The task as the team cards will show it, for the preview. */
export function previewTask(draft: Draft, member: Member | undefined): Task {
  return {
    id: 'vista-previa',
    titulo: draft.titulo.trim() || '(sin título)',
    estado: 'asignada',
    marca: null,
    marcas: [],
    fecha_objetivo: draft.fecha || null,
    prevision: null,
    asignada_el: null,
    responsable: member?.nombre ?? null,
    area: member?.area ?? null,
    papel: null,
    vencida: false,
    bloqueo_abierto: false,
    dias_de_atraso: null,
    ve_la_pagina: false,
    quedan_dias_habiles: null,
    barra: null,
    esperas: null,
  };
}
