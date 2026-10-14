import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StatePanel } from './StatePanel';

const STATE_COLOR = /text-(vencida|trabada|en-curso|entregada)/;

describe('StatePanel', () => {
  it('colors a state only when it has something, and keeps zeros gray', () => {
    render(<StatePanel panel={{ vencida: 2, trabada: 0, en_curso: 1, entregada: 0 }} />);

    expect(screen.getByText('VENCIDAS')).toHaveClass('text-vencida');
    expect(screen.getByText('2')).toHaveClass('text-vencida');
    expect(screen.getByText('EN CURSO')).toHaveClass('text-en-curso');
    expect(screen.getByText('1')).toHaveClass('text-en-curso');

    for (const label of ['ESPERANDO', 'ENTREGADAS', 'SIN EMPEZAR']) {
      const cell = screen.getByText(label).parentElement as HTMLElement;
      expect(screen.getByText(label)).toHaveClass('text-ink-dim');
      expect(cell.innerHTML).not.toMatch(STATE_COLOR);
    }
  });

  it('a calm week has no color at all', () => {
    const { container } = render(
      <StatePanel panel={{ vencida: 0, trabada: 0, en_curso: 0, entregada: 0 }} />,
    );
    expect(container.innerHTML).not.toMatch(STATE_COLOR);
  });
});
