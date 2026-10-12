import { describe, expect, it } from 'vitest';
import { activeCount, daysLeft, stateLabels, weekLine } from './format';
import { task } from './test/fixtures';

describe('format', () => {
  it('writes the header line like the design', () => {
    expect(weekLine(44, '2026-10-26')).toBe('SEM 44 · LUN 26.10');
    expect(weekLine(43, '2026-10-22')).toBe('SEM 43 · JUE 22.10');
  });

  it('counts in plain Spanish', () => {
    expect(activeCount(1)).toBe('1 activa');
    expect(activeCount(4)).toBe('4 activas');
    expect(daysLeft(7)).toBe('quedan 7 días');
    expect(daysLeft(1)).toBe('queda 1 día');
    expect(daysLeft(0)).toBe('vence hoy');
  });

  it('labels every mark the server gave, blocked first', () => {
    expect(stateLabels(task({ marcas: ['trabada', 'vencida'], dias_de_atraso: 2 }))).toEqual([
      { text: '[TRABADA]', marca: 'trabada' },
      { text: '[VENCIDA +2d]', marca: 'vencida' },
    ]);
    expect(stateLabels(task({ marcas: [], estado: 'asignada' }))).toEqual([
      { text: '[ASIGNADA]', marca: null },
    ]);
  });
});
