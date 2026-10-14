import { act, fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { DictationResult } from './api';
import { CLEAR_STORY, HelpBox, type HelpState } from './HelpBox';

// "Borrar el texto" while a dictation is starting or turning into text (review of the J4a,
// warnings R3-clear-during-starting and R3-clear-race-untested): the box stays empty, the
// microphone is let go, and nothing that arrives late from the dictation that was cleared reaches
// the box or its notes.

class FakeRecorder {
  static last: FakeRecorder | null = null;
  static isTypeSupported = () => false;
  state: 'inactive' | 'recording' = 'inactive';
  mimeType = 'audio/mp4';
  ondataavailable: ((event: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: (() => void) | null = null;
  start = vi.fn(() => {
    this.state = 'recording';
  });
  stop = vi.fn(() => {
    if (this.state === 'inactive') return;
    this.state = 'inactive';
    this.ondataavailable?.({ data: new Blob(['audio'], { type: this.mimeType }) });
    this.onstop?.();
  });
  constructor(public stream: MediaStream) {
    FakeRecorder.last = this;
  }
}

/** A microphone whose permission answers only when the test says so. */
function slowMicrophone() {
  const track = { stop: vi.fn() };
  let allow: () => void = () => {};
  const getUserMedia = vi.fn(
    () =>
      new Promise<MediaStream>((resolve) => {
        allow = () => resolve({ getTracks: () => [track] } as unknown as MediaStream);
      }),
  );
  Object.defineProperty(navigator, 'mediaDevices', { value: { getUserMedia }, configurable: true });
  return { track, allow: () => allow() };
}

function Box({ transcribe }: { transcribe: (audio: Blob) => Promise<DictationResult> }) {
  const [story, setStory] = useState('lo que había');
  const help: HelpState = { kind: 'idle' };
  return (
    <HelpBox
      transcribe={transcribe}
      onClosed={vi.fn()}
      story={story}
      onStory={setStory}
      help={help}
      notes={[]}
      onAsk={vi.fn()}
      onChoose={vi.fn()}
    />
  );
}

const box = () => screen.getByLabelText('Contame qué querés hacer y te ayudo');

beforeEach(() => {
  FakeRecorder.last = null;
  vi.stubGlobal('MediaRecorder', FakeRecorder);
});

afterEach(() => {
  vi.unstubAllGlobals();
  if (Object.getOwnPropertyDescriptor(navigator, 'mediaDevices')) {
    delete (navigator as unknown as Record<string, unknown>).mediaDevices;
  }
});

describe('clearing the free box while a dictation is on its way', () => {
  it('while the browser asks for the microphone: nothing records, and the microphone is let go', async () => {
    const mic = slowMicrophone();
    render(<Box transcribe={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'dictar' }));
    fireEvent.click(screen.getByRole('button', { name: CLEAR_STORY }));
    expect(box()).toHaveValue('');
    expect(screen.getByRole('button', { name: 'dictar' })).toBeEnabled();
    await act(async () => mic.allow());
    // The permission came late: no recording starts and the microphone goes back at once.
    expect(FakeRecorder.last).toBeNull();
    expect(mic.track.stop).toHaveBeenCalled();
    expect(screen.queryByText(/grabando/)).toBeNull();
    expect(screen.getByRole('status').textContent?.trim()).toBe('');
    expect(box()).toHaveValue('');
  });

  it('while it turns into text: what arrives later fills nothing', async () => {
    const mic = slowMicrophone();
    let answer: (result: DictationResult) => void = () => {};
    const transcribe = vi.fn(
      () =>
        new Promise<DictationResult>((resolve) => {
          answer = resolve;
        }),
    );
    render(<Box transcribe={transcribe} />);
    fireEvent.click(screen.getByRole('button', { name: 'dictar' }));
    await act(async () => mic.allow());
    fireEvent.click(screen.getByRole('button', { name: 'dejar de dictar' }));
    expect(transcribe).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: CLEAR_STORY }));
    expect(box()).toHaveValue('');
    await act(async () => answer({ kind: 'text', text: 'que Lucas cuelgue el módem' }));
    expect(box()).toHaveValue('');
    expect(screen.getByRole('button', { name: 'dictar' })).toBeEnabled();
    expect(screen.getByRole('status').textContent?.trim()).toBe('');
  });
});
