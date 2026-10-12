import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { WaitTree } from './WaitTree';

describe('WaitTree', () => {
  it('indents each wait under the one it waits for', () => {
    const { container } = render(
      <WaitTree
        waits={[
          {
            que: 'servidor de la planta',
            quien: 'Ariel',
            esperas: [
              {
                que: 'switch nuevo',
                quien: 'Lucas',
                esperas: [{ que: 'la compra', quien: null, esperas: [] }],
              },
            ],
          },
          { que: 'falta una pieza', quien: 'Ismael', esperas: [] },
        ]}
      />,
    );
    const lines = [...container.querySelectorAll<HTMLElement>('li')];
    expect(lines.map((l) => [l.dataset.level, l.textContent])).toEqual([
      ['0', '└─ espera: servidor de la planta (Ariel)'],
      ['1', '└─ espera: switch nuevo (Lucas)'],
      ['2', '└─ espera: la compra'],
      ['0', '└─ espera: falta una pieza (Ismael)'],
    ]);
    expect(lines.map((l) => l.style.paddingLeft)).toEqual(['0ch', '3ch', '6ch', '0ch']);
  });
});
