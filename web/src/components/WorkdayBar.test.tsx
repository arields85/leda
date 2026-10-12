import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { Segment } from '../api';
import { WorkdayBar } from './WorkdayBar';

const days = (moments: Segment['momento'][]): Segment[] =>
  moments.map((momento, i) => ({ fecha: `2026-10-${String(19 + i).padStart(2, '0')}`, momento }));

describe('WorkdayBar', () => {
  it('paints past days green, today white and the rest gray, one per working day', () => {
    const { container } = render(
      <WorkdayBar segments={days(['pasado', 'pasado', 'hoy', 'futuro', 'futuro'])} />,
    );
    const segments = [...container.querySelectorAll<HTMLElement>('[data-moment]')];
    expect(segments.map((s) => s.dataset.moment)).toEqual([
      'pasado',
      'pasado',
      'hoy',
      'futuro',
      'futuro',
    ]);
    expect(segments[0]).toHaveClass('bg-en-curso');
    expect(segments[2]).toHaveClass('bg-ink');
    expect(segments[4]).toHaveClass('bg-track');
  });

  it('labels the start date, "hoy" under the white segment and the due date under the last', () => {
    render(<WorkdayBar segments={days(['pasado', 'hoy', 'futuro', 'futuro'])} />);
    expect(screen.getByText('19.10').style.gridColumn).toBe('1');
    expect(screen.getByText('hoy').style.gridColumn).toBe('2');
    expect(screen.getByText('22.10').style.gridColumn).toBe('4');
  });

  it('does not stack a date under "hoy" on the last day', () => {
    render(<WorkdayBar segments={days(['pasado', 'hoy'])} />);
    expect(screen.getByText('19.10')).toBeInTheDocument();
    expect(screen.queryByText('20.10')).toBeNull();
    expect(screen.getByText('hoy').style.gridColumn).toBe('2');
  });

  it('draws nothing without segments', () => {
    const { container } = render(<WorkdayBar segments={[]} />);
    expect(container.innerHTML).toBe('');
  });
});
