import type { AdminMe, Options } from '../admin/api';
import type { ObjectiveOptions } from '../admin/objectiveApi';
import { addDays } from '../admin/DatePicker';

export const SPACE = '8f1d2c3b-0000-4000-8000-000000000001';
export const OTHER_SPACE = '8f1d2c3b-0000-4000-8000-000000000002';

export function adminMe(overrides: Partial<AdminMe> = {}): AdminMe {
  return {
    administrador: 'Ariel',
    espacios: [{ id: SPACE, slug: 'corework', nombre: 'CoreWork' }],
    ...overrides,
  };
}

/** Monday 12.10.2026 to Friday 27.11, weekdays only, without the holiday of Monday 23.11. */
function workingDays(): string[] {
  const days: string[] = [];
  for (let day = '2026-10-12'; day <= '2026-11-27'; day = addDays(day, 1)) {
    const weekday = new Date(`${day}T00:00:00Z`).getUTCDay();
    if (weekday !== 0 && weekday !== 6 && day !== '2026-11-23') days.push(day);
  }
  return days;
}

export function options(overrides: Partial<Options> = {}): Options {
  return {
    espacio: { id: SPACE, nombre: 'CoreWork', zona_horaria: 'America/Argentina/Buenos_Aires' },
    hoy: '2026-10-12',
    objetivos: [
      {
        id: 'o1',
        titulo: 'Puesta en marcha de la línea 3',
        tipo: 'operativo',
        estado: 'activo',
        fecha_objetivo: '2026-10-30',
      },
      { id: 'o2', titulo: 'Mantenimiento anual', tipo: 'operativo', estado: 'activo', fecha_objetivo: null },
    ],
    integrantes: [
      {
        membership_id: 'm-ismael',
        nombre: 'Ismael',
        area_id: 'a-dir',
        area: 'Dirección',
        autoridad_final: true,
        conectado: true,
        revisa: null,
      },
      {
        membership_id: 'm-lucas',
        nombre: 'Lucas',
        area_id: 'a-infra',
        area: 'Infraestructura',
        autoridad_final: false,
        conectado: false,
        revisa: { membership_id: 'm-ismael', nombre: 'Ismael' },
      },
      {
        membership_id: 'm-marcos',
        nombre: 'Marcos',
        area_id: 'a-auto',
        area: 'Automatización',
        autoridad_final: false,
        conectado: true,
        revisa: { membership_id: 'm-ismael', nombre: 'Ismael' },
      },
    ],
    politicas: [
      {
        area_id: 'a-auto',
        area: 'Automatización',
        evidencia_requerida: ['captura'],
        version: 1,
        tipos: {
          captura: { clases: ['imagen'], en_palabras: 'una captura de pantalla' },
          informe: { clases: ['archivo'], en_palabras: 'un informe' },
        },
      },
      { area_id: 'a-infra', area: 'Infraestructura', evidencia_requerida: [], version: 1, tipos: {} },
    ],
    calendario: {
      dias: ['lunes', 'martes', 'miercoles', 'jueves', 'viernes'],
      hasta: '2026-11-27',
      feriados: [{ fecha: '2026-11-23', nombre: 'Día de la Soberanía' }],
      dias_habiles: workingDays(),
    },
    ...overrides,
  };
}

/** What the objective form offers in CoreWork (migrations 0068 and 0069): a strategic objective and
 * a milestone to hang from, two area referentes and the pack's own name for the top level. */
export function objectiveOptions(overrides: Partial<ObjectiveOptions> = {}): ObjectiveOptions {
  return {
    espacio: { id: SPACE, nombre: 'CoreWork' },
    hoy: '2026-10-12',
    niveles: { estrategico: 'plan anual', hito: 'hito', operativo: 'objetivo operativo' },
    sin_padre: ['estrategico'],
    padres: [
      {
        id: 'o-plan',
        titulo: 'Modernizar la planta',
        tipo: 'estrategico',
        estado: 'activo',
        fecha_objetivo: '2026-12-18',
        tipos: ['hito', 'operativo'],
      },
      {
        id: 'o-hito',
        titulo: 'Línea 3 andando',
        tipo: 'hito',
        estado: 'activo',
        fecha_objetivo: null,
        tipos: ['operativo'],
      },
    ],
    referentes: [
      { membership_id: 'm-marcos', nombre: 'Marcos', areas: ['Automatización'] },
      { membership_id: 'm-lucas', nombre: 'Lucas', areas: ['Infraestructura', 'Redes'] },
    ],
    calendario: options().calendario,
    ...overrides,
  };
}
