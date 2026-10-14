import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { options } from '../test/adminFixtures';
import { EMPTY_DRAFT } from './draft';
import { TaskPreview } from './TaskPreview';

// J2-23 (the user, 2026-10-13: "que lo corrija directamente sin resaltarlo"): Leda corrects single
// words, never what the person says, so the preview shows the texts as they will load, unmarked.

describe('the texts in the preview', () => {
  it('shows the title, the description and the criterion as plain text, with no spelling mark', () => {
    const { container } = render(
      <TaskPreview
        draft={{
          ...EMPTY_DRAFT,
          titulo: 'Integrar la paila 3 a CoreLabs',
          descripcion: 'Plantar el árbol y cambiar la batería del árbol viejo',
          criterio: 'La paila 3 se ve en CoreLabs',
        }}
        options={options()}
        admin="Ariel"
      />,
    );
    expect(container.querySelector('[data-task]')).toHaveTextContent('Integrar la paila 3 a CoreLabs');
    expect(container).toHaveTextContent('Plantar el árbol y cambiar la batería del árbol viejo');
    expect(container).toHaveTextContent('La paila 3 se ve en CoreLabs');
    expect(container.querySelector('[data-corrected], [data-spelling]')).toBeNull();
    expect(container).not.toHaveTextContent('Leda corrigió la ortografía');
  });
});
