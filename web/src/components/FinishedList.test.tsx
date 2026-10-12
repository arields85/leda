import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { finished } from '../test/fixtures';
import { FinishedList } from './FinishedList';

describe('FinishedList', () => {
  it('lists what was finished in the last 30 days, apart, in gray', () => {
    render(
      <FinishedList
        view="equipo"
        items={[
          finished(),
          finished({ id: 'f2', titulo: 'Probar el PLC', responsable: 'Lucas', terminada_el: '2026-10-02' }),
        ]}
      />,
    );
    const section = screen.getByRole('region', { name: 'Terminadas en los últimos 30 días' });
    expect(section).toBeInTheDocument();
    expect(screen.getByText('Probar el PLC')).toBeInTheDocument();
    expect(screen.getByText('└─ de Lucas')).toBeInTheDocument();
    expect(screen.getByText('02.10')).toBeInTheDocument();
    expect(section.innerHTML).not.toMatch(/text-(vencida|trabada|en-curso|entregada)/);
  });

  it('in "Tus tareas" it does not repeat the person\'s own name', () => {
    const { container } = render(<FinishedList view="tus" items={[finished()]} />);
    expect(container.textContent).not.toContain('Marcos');
    expect(screen.getAllByText('[TERMINADA]')).toHaveLength(1);
  });

  it('shows nothing when nothing was finished', () => {
    const { container } = render(<FinishedList view="tus" items={[]} />);
    expect(container).toBeEmptyDOMElement();
  });
});
