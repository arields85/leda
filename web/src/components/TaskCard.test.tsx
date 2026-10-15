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
          marcas: ['vencida'],
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
    render(
      <TaskCard
        view="tus"
        task={task({ marca: 'vencida', marcas: ['vencida'], vencida: true, dias_de_atraso: null })}
      />,
    );
    expect(screen.getByText('[VENCIDA]')).toBeInTheDocument();
  });

  it('a blocked and late task shows both marks, each in its color', () => {
    render(
      <TaskCard
        view="tus"
        task={task({
          papel: 'espero',
          responsable: 'Ariel',
          estado: 'bloqueada',
          marca: 'trabada',
          marcas: ['trabada', 'vencida'],
          vencida: true,
          bloqueo_abierto: true,
          dias_de_atraso: 3,
          fecha_objetivo: '2026-10-19',
          quedan_dias_habiles: null,
          esperas: [{ que: 'falta el cable', quien: 'Lucas', esperas: [] }],
        })}
      />,
    );
    expect(screen.getByText('[ESPERANDO]')).toHaveClass('text-trabada');
    expect(screen.getByText('[VENCIDA +3d]')).toHaveClass('text-vencida');
    expect(screen.getByText('└─ espera: falta el cable (Lucas)')).toBeInTheDocument();
  });

  it('a waited task the server does not mark late shows only its state and its date', () => {
    const { container } = render(
      <TaskCard
        view="tus"
        task={task({
          papel: 'espero',
          responsable: 'Ariel',
          estado: 'asignada',
          vencida: false,
          bloqueo_abierto: false,
          dias_de_atraso: null,
          esperas: null,
          fecha_objetivo: '2026-10-19',
          quedan_dias_habiles: null,
        })}
      />,
    );
    expect(container.textContent).not.toMatch(/VENCIDA|ESPERANDO|TRABADA|espera:|prevé/);
    expect(container.innerHTML).not.toMatch(/text-(vencida|trabada)/);
    expect(screen.getByText('[SIN EMPEZAR]')).toHaveClass('text-ink-dim');
    expect(screen.getByText('19.10')).toBeInTheDocument();
    expect(screen.getByText('└─ de Ariel · la esperás')).toBeInTheDocument();
  });

  it('shows the day the person gave when a delay was already talked about', () => {
    render(
      <TaskCard
        view="tus"
        task={task({
          papel: 'espero',
          responsable: 'Ariel',
          marca: 'vencida',
          marcas: ['vencida'],
          vencida: true,
          dias_de_atraso: 3,
          fecha_objetivo: '2026-10-19',
          prevision: '2026-10-28',
          quedan_dias_habiles: null,
        })}
      />,
    );
    expect(screen.getByText('19.10 · prevé 28.10')).toBeInTheDocument();
  });

  it('a task in progress shows the days left on top and its bar', () => {
    const { container } = render(
      <TaskCard
        view="tus"
        task={task({
          marca: 'en_curso',
          marcas: ['en_curso'],
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
      <TaskCard
        view="tus"
        task={task({ marca: 'entregada', marcas: ['entregada'], estado: 'en_revision' })}
      />,
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
          marcas: ['trabada'],
          bloqueo_abierto: true,
          esperas: [{ que: 'servidor de la planta', quien: 'Ariel', esperas: [] }],
        })}
      />,
    );
    expect(screen.getByText('[ESPERANDO]')).toHaveClass('text-trabada');
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

  it('an own task someone else asked for says who, under the title (MA debt)', () => {
    render(
      <TaskCard
        view="tus"
        task={task({ titulo: 'Aprobar la compra del módem', responsable: 'Ismael', pidio: 'Marcos Tarquini' })}
      />,
    );
    const line = screen.getByText('└─ te la pidió Marcos Tarquini');
    expect(line).toHaveClass('text-small', 'text-ink-dim');
    const title = screen.getByText('Aprobar la compra del módem');
    expect(title.compareDocumentPosition(line) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it('no line when nobody else asked for it, nor outside "Mis tareas"', () => {
    const { container, rerender } = render(<TaskCard view="tus" task={task({ pidio: null })} />);
    expect(container.textContent).not.toContain('te la pidió');
    // A waited task is someone else's: who asked for it is not the person's business here.
    rerender(<TaskCard view="tus" task={task({ papel: 'espero', responsable: 'Lucas', pidio: 'Ariel' })} />);
    expect(container.textContent).not.toContain('te la pidió');
    rerender(<TaskCard view="sector" task={task({ responsable: 'Lucas', papel: null, pidio: 'Ariel' })} />);
    expect(container.textContent).not.toContain('te la pidió');
  });
});
