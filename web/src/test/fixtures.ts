import type { Finished, Me, Task, ViewData } from '../api';

export function task(overrides: Partial<Task> = {}): Task {
  return {
    id: 't1',
    titulo: 'Configurar alarmas del SCADA',
    estado: 'asignada',
    marca: null,
    marcas: [],
    fecha_objetivo: '2026-10-30',
    prevision: null,
    asignada_el: '2026-10-19',
    responsable: 'Marcos',
    area: 'Automatización',
    papel: 'mia',
    vencida: false,
    bloqueo_abierto: false,
    dias_de_atraso: null,
    ve_la_pagina: true,
    quedan_dias_habiles: 4,
    barra: null,
    esperas: null,
    ...overrides,
  };
}

export function finished(overrides: Partial<Finished> = {}): Finished {
  return {
    id: 'f1',
    titulo: 'Relevar tableros de la línea 2',
    responsable: 'Marcos',
    area: 'Automatización',
    terminada_el: '2026-10-20',
    ...overrides,
  };
}

export function view(overrides: Partial<ViewData> = {}): ViewData {
  return {
    vista: 'tus',
    titulo: 'Tus tareas',
    hoy: '2026-10-26',
    semana_iso: 44,
    panel: { vencida: 1, trabada: 0, en_curso: 2, entregada: 0 },
    activas: 3,
    semana: [
      { fecha: '2026-10-26', dia: 'lun', hoy: true, habil: true, vence_algo: false },
      { fecha: '2026-10-27', dia: 'mar', hoy: false, habil: true, vence_algo: false },
      { fecha: '2026-10-28', dia: 'mié', hoy: false, habil: true, vence_algo: false },
      { fecha: '2026-10-29', dia: 'jue', hoy: false, habil: true, vence_algo: false },
      { fecha: '2026-10-30', dia: 'vie', hoy: false, habil: true, vence_algo: true },
    ],
    tareas: [task()],
    terminadas: [],
    ...overrides,
  };
}

export function me(overrides: Partial<Me> = {}): Me {
  return {
    persona: 'Marcos',
    espacio: 'CoreWork',
    vistas: [{ vista: 'tus', titulo: 'Tus tareas' }],
    chat_con_leda: null,
    ...overrides,
  };
}
