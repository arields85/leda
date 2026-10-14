import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { Spelling } from './api';
import { SPELL_PAUSE_MS, useSpellWhilePaused } from './spellWhilePaused';

type Draft = { titulo: string };

function deferred() {
  let resolve!: (s: Spelling) => void;
  const promise = new Promise<Spelling>((r) => {
    resolve = r;
  });
  return { promise, resolve };
}

describe('the spelling while typing', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('an older check that answers late never lets the same text be checked twice (R3-001)', async () => {
    const answers = [deferred(), deferred(), deferred()];
    const check = vi.fn(() => answers[check.mock.calls.length - 1].promise);
    const round = { current: 0 };
    const latest = { current: { titulo: 'hola' } as Draft };
    const { result, rerender } = renderHook(
      ({ draft, editing }: { draft: Draft; editing: boolean }) => {
        latest.current = draft;
        return useSpellWhilePaused<'titulo', Draft>({
          fields: ['titulo'],
          draft,
          latest,
          round,
          open: () => true,
          editing,
          check,
          onClosed: vi.fn(),
          elementId: (f) => `f-${f}`,
          onTake: vi.fn(),
        });
      },
      { initialProps: { draft: { titulo: 'hola' }, editing: true } },
    );
    await act(async () => vi.advanceTimersByTime(SPELL_PAUSE_MS));
    expect(check).toHaveBeenCalledTimes(1);

    // The person starts over and types the same text again: a new check, while the first one is
    // still on its way.
    act(() => {
      round.current += 1;
      result.current.reset();
    });
    rerender({ draft: { titulo: '' }, editing: true });
    rerender({ draft: { titulo: 'hola' }, editing: true });
    await act(async () => vi.advanceTimersByTime(SPELL_PAUSE_MS));
    expect(check).toHaveBeenCalledTimes(2);

    // The first one answers late (for a round that is gone): it changes nothing, and the second one
    // is still on its way, so a new pause does not ask again.
    await act(async () => answers[0].resolve({ corrected: {}, unchecked: [] }));
    rerender({ draft: { titulo: 'hola' }, editing: false });
    rerender({ draft: { titulo: 'hola' }, editing: true });
    await act(async () => vi.advanceTimersByTime(SPELL_PAUSE_MS));
    expect(check).toHaveBeenCalledTimes(2);
  });
});
