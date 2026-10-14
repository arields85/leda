import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { options } from '../test/adminFixtures';
import { EMPTY_DRAFT } from './draft';
import { TaskPreview, withCorrections } from './TaskPreview';

// J2-19 (the user's phone test, 2026-10-13): in the preview, the words Leda corrected are in the
// color of "propuesto por Leda", inside the text; the note line stays as it was.

describe('the corrected words in the preview', () => {
  it('marks each corrected word in Leda\'s color, inside the text, and keeps the note', () => {
    const { container } = render(
      <TaskPreview
        draft={{ ...EMPTY_DRAFT, descripcion: 'Plantar el árbol y cambiar la batería del árbol viejo' }}
        options={options()}
        admin="Ariel"
        spelled={{
          descripcion: [
            { antes: 'arvol', despues: 'árbol' },
            { antes: 'bateria', despues: 'batería' },
          ],
        }}
      />,
    );
    const marked = [...container.querySelectorAll('[data-corrected]')];
    // Only the corrected ones, in order: the second "árbol" was written well and is not marked.
    expect(marked.map((m) => m.textContent)).toEqual(['árbol', 'batería']);
    for (const m of marked) expect(m).toHaveClass('text-propuesto');
    expect(screen.getByText(/Plantar el/)).toHaveTextContent('Plantar el árbol y cambiar la batería del árbol viejo');
    expect(container).toHaveTextContent('Leda corrigió la ortografía (arvol → árbol, bateria → batería).');
  });

  it('marks the corrected words of the title too, in the card', () => {
    const { container } = render(
      <TaskPreview
        draft={{ ...EMPTY_DRAFT, titulo: 'Integrar la paila 3 a CoreLabs' }}
        options={options()}
        admin="Ariel"
        spelled={{ titulo: [{ antes: 'cirelabs', despues: 'CoreLabs' }] }}
      />,
    );
    const card = container.querySelector('[data-task]')!;
    expect(card).toHaveTextContent('Integrar la paila 3 a CoreLabs');
    const marked = [...card.querySelectorAll('[data-corrected]')];
    expect(marked.map((m) => m.textContent)).toEqual(['CoreLabs']);
    expect(marked[0]).toHaveClass('text-propuesto');
  });

  it('without changes the text is plain', () => {
    expect(withCorrections('El tablero queda revisado.', undefined)).toBe('El tablero queda revisado.');
    expect(withCorrections('El tablero queda revisado.', [])).toBe('El tablero queda revisado.');
  });
});
