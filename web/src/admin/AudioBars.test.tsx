import { act, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AudioBars, BARS, EVERY_MS, EVERY_MS_STILL, LOWEST } from './AudioBars';
import { Dictation, VoiceLevel } from './dictation';

// J2-27: while it records, bars that move with the voice. Web Audio, the microphone, the recorder
// and the animation frames are fakes here; never the real ones.

/** A fake analyser: the voice at `loud` (0 to 1), as samples around the middle (128). */
function fakeAudio(loud = { now: 0.5 }) {
  const made: FakeAudioContext[] = [];
  const sources: { connect: ReturnType<typeof vi.fn>; disconnect: ReturnType<typeof vi.fn> }[] = [];
  class FakeAudioContext {
    state = 'suspended';
    resume = vi.fn(async () => {
      this.state = 'running';
    });
    close = vi.fn(async () => {
      this.state = 'closed';
    });
    constructor() {
      made.push(this);
    }
    createMediaStreamSource() {
      const source = { connect: vi.fn(), disconnect: vi.fn() };
      sources.push(source);
      return source;
    }
    createAnalyser() {
      return {
        fftSize: 2048,
        getByteTimeDomainData(samples: Uint8Array) {
          samples.forEach((_, i) => {
            samples[i] = 128 + Math.round((i % 2 ? 1 : -1) * loud.now * 127);
          });
        },
      };
    }
  }
  vi.stubGlobal('AudioContext', FakeAudioContext);
  return { made, sources, loud };
}

class FakeRecorder {
  state: 'inactive' | 'recording' = 'inactive';
  mimeType = 'audio/webm';
  ondataavailable: ((event: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: (() => void) | null = null;
  start = vi.fn(() => {
    this.state = 'recording';
  });
  stop = vi.fn(() => {
    this.state = 'inactive';
    this.ondataavailable?.({ data: new Blob(['audio'], { type: this.mimeType }) });
    this.onstop?.();
  });
}

function fakeMicrophone() {
  vi.stubGlobal('MediaRecorder', FakeRecorder);
  const track = { stop: vi.fn() };
  let give: ((stream: MediaStream) => void) | null = null;
  const getUserMedia = vi.fn(
    () =>
      new Promise<MediaStream>((resolve) => {
        give = resolve;
      }),
  );
  Object.defineProperty(navigator, 'mediaDevices', { value: { getUserMedia }, configurable: true });
  return { allow: () => give?.({ getTracks: () => [track] } as unknown as MediaStream), track };
}

function handlers() {
  return { onRecording: vi.fn(), onTick: vi.fn(), onAudio: vi.fn(), onProblem: vi.fn() };
}

/** Animation frames run by hand, with the time the test says. */
function fakeFrames() {
  let queue: { id: number; run: (now: number) => void }[] = [];
  let next = 1;
  const cancel = vi.fn((id: number) => {
    queue = queue.filter((f) => f.id !== id);
  });
  vi.stubGlobal('requestAnimationFrame', (run: (now: number) => void) => {
    queue.push({ id: next, run });
    return next++;
  });
  vi.stubGlobal('cancelAnimationFrame', cancel);
  return {
    cancel,
    pending: () => queue.length,
    at(now: number) {
      const due = queue;
      queue = [];
      act(() => due.forEach((f) => f.run(now)));
    },
  };
}

function heights(): string[] {
  return [...screen.getByTestId('audio-bars').children].map((b) => (b as HTMLElement).style.height);
}

function reducedMotion(still: boolean) {
  vi.stubGlobal('matchMedia', (query: string) => ({ matches: still && query.includes('reduce') }));
}

beforeEach(() => reducedMotion(false));

afterEach(() => {
  vi.unstubAllGlobals();
  if (Object.getOwnPropertyDescriptor(navigator, 'mediaDevices')) {
    delete (navigator as unknown as Record<string, unknown>).mediaDevices;
  }
});

describe('VoiceLevel', () => {
  it('reads how loud the voice is, from silence to full', () => {
    const audio = fakeAudio({ now: 0 });
    const voice = new VoiceLevel();
    voice.attach({} as MediaStream);
    expect(voice.available).toBe(true);
    expect(voice.read()).toBe(0);
    audio.loud.now = 0.2;
    expect(voice.read()).toBeCloseTo(0.6, 1);
    audio.loud.now = 1;
    expect(voice.read()).toBe(1);
    voice.close();
    expect(voice.read()).toBeNull();
    expect(audio.made[0].close).toHaveBeenCalled();
    expect(audio.sources[0].disconnect).toHaveBeenCalled();
  });

  it('without Web Audio there is no level, and nothing breaks', () => {
    const voice = new VoiceLevel();
    voice.attach({} as MediaStream);
    expect(voice.available).toBe(false);
    expect(voice.read()).toBeNull();
    voice.close();
  });

  it('uses the old Safari name where it is the only one', () => {
    const { made } = fakeAudio();
    const Context = (window as unknown as { AudioContext: unknown }).AudioContext;
    vi.stubGlobal('AudioContext', undefined);
    vi.stubGlobal('webkitAudioContext', Context);
    new VoiceLevel().attach({} as MediaStream);
    expect(made).toHaveLength(1);
  });
});

describe('Dictation and the voice level', () => {
  it('makes and resumes Web Audio in the tap, before the microphone answers, and closes it when it stops', async () => {
    const audio = fakeAudio();
    const mic = fakeMicrophone();
    const dictation = new Dictation(handlers());
    const started = dictation.start();
    // Still inside the tap: nothing awaited yet (Safari on the iPhone).
    expect(audio.made).toHaveLength(1);
    expect(audio.made[0].resume).toHaveBeenCalled();
    expect(dictation.level()).toBeNull();
    mic.allow();
    await started;
    expect(dictation.hasLevel()).toBe(true);
    expect(dictation.level()).toBeGreaterThan(0);
    dictation.stop();
    expect(audio.made[0].close).toHaveBeenCalled();
    expect(dictation.level()).toBeNull();
  });

  it('a microphone that is not allowed lets Web Audio go too', async () => {
    const audio = fakeAudio();
    Object.defineProperty(navigator, 'mediaDevices', {
      value: { getUserMedia: vi.fn(async () => Promise.reject(new DOMException('no', 'NotAllowedError'))) },
      configurable: true,
    });
    vi.stubGlobal('MediaRecorder', FakeRecorder);
    await new Dictation(handlers()).start();
    expect(audio.made[0].close).toHaveBeenCalled();
  });

  it('without Web Audio it records all the same, with no level', async () => {
    const mic = fakeMicrophone();
    const on = handlers();
    const dictation = new Dictation(on);
    const started = dictation.start();
    mic.allow();
    await started;
    expect(on.onRecording).toHaveBeenCalled();
    expect(dictation.hasLevel()).toBe(false);
    expect(dictation.level()).toBeNull();
    dictation.stop();
    expect(on.onAudio).toHaveBeenCalledTimes(1);
  });
});

describe('AudioBars', () => {
  it('shows a row of bars, low in silence, and each new level comes in from the right', () => {
    const frames = fakeFrames();
    let level = 0;
    render(<AudioBars read={() => level} />);
    expect(heights()).toHaveLength(BARS);
    expect(new Set(heights())).toEqual(new Set([`${LOWEST}%`]));
    frames.at(0);
    level = 0.8;
    frames.at(EVERY_MS - 1);
    expect(heights().at(-1)).toBe(`${LOWEST}%`);
    frames.at(EVERY_MS);
    expect(heights().at(-1)).toBe('80%');
    level = 0.5;
    frames.at(2 * EVERY_MS);
    // The earlier one moved one place to the left.
    expect(heights().slice(-2)).toEqual(['80%', '50%']);
  });

  it('stops its loop when it goes away (the recording stopped)', () => {
    const frames = fakeFrames();
    const { unmount } = render(<AudioBars read={() => 0.3} />);
    frames.at(0);
    expect(frames.pending()).toBe(1);
    unmount();
    expect(frames.cancel).toHaveBeenCalled();
    expect(frames.pending()).toBe(0);
  });

  it('with reduced motion it moves slowly', () => {
    reducedMotion(true);
    const frames = fakeFrames();
    render(<AudioBars read={() => 0.6} />);
    frames.at(0);
    expect(heights().at(-1)).toBe('60%');
    frames.at(EVERY_MS * 2);
    expect(heights().at(-2)).toBe(`${LOWEST}%`);
    frames.at(EVERY_MS_STILL);
    expect(heights().slice(-2)).toEqual(['60%', '60%']);
  });

  it('without a level (null) the row stays as it was', () => {
    const frames = fakeFrames();
    render(<AudioBars read={() => null} />);
    frames.at(0);
    frames.at(EVERY_MS * 3);
    expect(new Set(heights())).toEqual(new Set([`${LOWEST}%`]));
  });
});
