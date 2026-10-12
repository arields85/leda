import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { task, view } from '../test/fixtures';
import { WeekStrip } from './WeekStrip';

describe('WeekStrip', () => {
  it('marks today white and counts what is due on each day', () => {
    const tareas = [task({ id: 'a' }), task({ id: 'b' })];
    const { container } = render(<WeekStrip days={view().semana} tasks={tareas} />);
    const today = container.querySelector('[data-today]') as HTMLElement;
    expect(today).toHaveClass('bg-ink');
    expect(today).toHaveTextContent('HOY');
    const friday = screen.getByText('2 VENCE').closest('li') as HTMLElement;
    expect(friday).toHaveClass('border-line-strong');
    expect(container.innerHTML).not.toMatch(/text-(vencida|trabada|en-curso|entregada)/);
  });

  it('marks a holiday', () => {
    const semana = view().semana.map((d) =>
      d.fecha === '2026-10-28' ? { ...d, habil: false } : d,
    );
    render(<WeekStrip days={semana} tasks={[]} />);
    expect(screen.getByText('FERIADO')).toBeInTheDocument();
  });
});
