import { fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { Switch } from '../components/Switch';
import { OFF, PRIMARY, SECONDARY } from './controls';
import { CLEAR_STORY, HelpBox, type HelpState } from './HelpBox';

// The three fixes of the user's phone test of the J3: the clear button of the free box, the
// disabled and enabled looks of the buttons, and the "Tarea / Objetivo" tabs.

function Box({ initial, onStory }: { initial: string; onStory?: (text: string) => void }) {
  const [story, setStory] = useState(initial);
  const help: HelpState = { kind: 'idle' };
  return (
    <HelpBox
      transcribe={vi.fn()}
      onClosed={vi.fn()}
      story={story}
      onStory={(text) => {
        onStory?.(text);
        setStory(text);
      }}
      help={help}
      notes={[]}
      onAsk={vi.fn()}
      onChoose={vi.fn()}
    />
  );
}

describe('the clear button of the free box', () => {
  it('empties only the free box, with its own name', () => {
    const onStory = vi.fn();
    render(<Box initial="que Lucas cuelgue el módem" onStory={onStory} />);
    const clear = screen.getByRole('button', { name: CLEAR_STORY });
    expect(clear).toHaveAttribute('title', 'Borrar el texto');
    fireEvent.click(clear);
    expect(onStory).toHaveBeenCalledWith('');
    expect(screen.getByLabelText('Contame qué querés hacer y te ayudo')).toHaveValue('');
    // Nothing left to clear: it reads as off.
    expect(clear).toBeDisabled();
  });

  it('has the size and look of the microphone button', () => {
    render(<Box initial="algo" />);
    expect(screen.getByRole('button', { name: CLEAR_STORY })).toHaveClass('h-11', 'w-11');
  });
});

describe('the looks of a button that can act and one that cannot', () => {
  it('a disabled button reads as off: dimmed text and border, no shadow', () => {
    render(
      <button type="button" className={PRIMARY} aria-disabled>
        &gt; confirmar
      </button>,
    );
    const button = screen.getByRole('button', { name: '> confirmar' });
    expect(button).toHaveAttribute('aria-disabled', 'true');
    for (const look of ['aria-disabled:text-ink-dim', 'aria-disabled:border-line-soft', 'aria-disabled:shadow-none',
      'disabled:text-ink-dim', 'disabled:shadow-none']) {
      expect(OFF.split(' ')).toContain(look);
      expect(button).toHaveClass(look);
    }
    // Never a fade that keeps the bright border and shadow, never a color.
    expect(PRIMARY).not.toMatch(/opacity|vencida|yellow/);
  });

  it('an active secondary button reads as active', () => {
    expect(SECONDARY.split(' ')).toEqual(expect.arrayContaining(['text-ink', 'border-line-strong']));
    expect(SECONDARY.split(' ')).not.toContain('text-ink-soft');
  });
});

describe('the tabs', () => {
  it('mark the selected one and dim the other, like the team views', () => {
    const onChange = vi.fn();
    render(
      <Switch
        label="Qué cargar"
        items={[
          { value: 'tarea', label: 'Tarea' },
          { value: 'objetivo', label: 'Objetivo' },
        ]}
        current="tarea"
        onChange={onChange}
      />,
    );
    const group = screen.getByRole('group', { name: 'Qué cargar' });
    const task = screen.getByRole('button', { name: 'Tarea' });
    const objective = screen.getByRole('button', { name: 'Objetivo' });
    expect(group).toContainElement(task);
    expect(task).toHaveAttribute('aria-pressed', 'true');
    expect(task).toHaveClass('border-line', 'text-ink');
    expect(objective).toHaveClass('border-line-soft', 'text-ink-dim');
    fireEvent.click(objective);
    expect(onChange).toHaveBeenCalledWith('objetivo');
  });
});
