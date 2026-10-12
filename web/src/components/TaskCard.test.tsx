import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { task } from '../test/fixtures';
import { TaskCard } from './TaskCard';

describe('TaskCard', () => {
  it('shows a late task with its working days of delay, in its color', () => {
    render(
      <TaskCard
        view="tus"
        task={task({
          marca: 'vencida',
          vencida: true,
          dias_de_atraso: 2,
          fecha_objetivo: '2026-10-22',
          quedan_dias_habiles: null,
        })}
      />,
    );
    expect(screen.getByText('[VENCIDA +2d]')).toHaveClass('text-vencida');
    expect(screen.getByText('22.10')).toBeInTheDocument();
  });

  it('shows [VENCIDA] alone when the delay cannot be counted', () => {
    render(<TaskCard view="tus" task={task({ marca: 'vencida', vencida: true, dias_de_atraso: null })} />);
    expect(screen.getByText('[VENCIDA]')).toBeInTheDocument();
  });

  it('never shows a delay or a block the server did not give (null fields)', () => {
    const { container } = render(
      <TaskCard
        view="tus"
        task={task({
          papel: 'espero',
          responsable: 'Ariel',
          estado: 'bloqueada',
          vencida: null,
          bloqueo_abierto: null,
          dias_de_atraso: null,
          esperas: null,
          fecha_objetivo: '2026-10-19',
          quedan_dias_habiles: null,
        })}
      />,
    );
    expect(container.textContent).not.toMatch(/VENCIDA|TRABADA|espera:/);
    expect(container.innerHTML).not.toMatch(/text-(vencida|trabada)/);
    expect(screen.getByText('[ABIERTA]')).toHaveClass('text-ink-dim');
    expect(screen.getByText('└─ de Ariel · la esperás')).toBeInTheDocument();
  });

  it('a task in progress shows the days left on top and its bar', () => {
    const { container } = render(
      <TaskCard
        view="tus"
        task={task({
          marca: 'en_curso',
          estado: 'en_curso',
          quedan_dias_habiles: 7,
          barra: [
            { fecha: '2026-10-23', momento: 'pasado' },
            { fecha: '2026-10-26', momento: 'hoy' },
            { fecha: '2026-10-27', momento: 'futuro' },
          ],
        })}
      />,
    );
    expect(screen.getByText('[EN CURSO]')).toHaveClass('text-en-curso');
    expect(screen.getByText('quedan 7 días')).toBeInTheDocument();
    expect(container.querySelectorAll('[data-moment]')).toHaveLength(3);
  });

  it('a delivered task is dashed and dimmer, without the shadow', () => {
    const { container } = render(
      <TaskCard view="tus" task={task({ marca: 'entregada', estado: 'en_revision' })} />,
    );
    const card = container.querySelector('article') as HTMLElement;
    expect(card).toHaveClass('border-dashed');
    expect(card).not.toHaveClass('shadow-hard');
    expect(screen.getByText('[ENTREGADA]')).toHaveClass('text-entregada');
    expect(screen.getByText('Configurar alarmas del SCADA')).toHaveClass('text-ink-soft');
  });

  it('a blocked task shows its chain of waits', () => {
    render(
      <TaskCard
        view="tus"
        task={task({
          marca: 'trabada',
          bloqueo_abierto: true,
          esperas: [{ que: 'servidor de la planta', quien: 'Ariel', esperas: [] }],
        })}
      />,
    );
    expect(screen.getByText('[TRABADA]')).toHaveClass('text-trabada');
    expect(screen.getByText('└─ espera: servidor de la planta (Ariel)')).toBeInTheDocument();
  });

  it('in the sector and team views every card says whose it is', () => {
    render(<TaskCard view="sector" task={task({ responsable: 'Lucas', papel: null })} />);
    expect(screen.getByText('└─ de Lucas')).toBeInTheDocument();
  });

  it("the person's own task does not repeat her name", () => {
    const { container } = render(<TaskCard view="tus" task={task()} />);
    expect(container.textContent).not.toContain('Marcos');
  });
});
