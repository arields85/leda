import type { Task } from '../api';
import type { Member, Options, Policy, TaskInput, WaitableTask } from './api';

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
