import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { canDictate, Dictation, DICTATION_LIMIT_MS, MIC_DENIED, MIC_FAILED } from './dictation';

/** A fake MediaRecorder: `start` records, `stop` gives one chunk and then says it stopped. */
class FakeRecorder {
  static last: FakeRecorder | null = null;
  static supported = ['audio/webm;codecs=opus', 'audio/webm'];
  static isTypeSupported = (type: string) => FakeRecorder.supported.includes(type);
  state: 'inactive' | 'recording' = 'inactive';
  mimeType: string;
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
  constructor(
    public stream: MediaStream,
    options?: { mimeType?: string },
  ) {
    this.mimeType = options?.mimeType ?? 'audio/mp4';
    FakeRecorder.last = this;
  }
}

function fakeMicrophone(allow: 'yes' | 'denied' | 'missing' = 'yes') {
  const track = { stop: vi.fn() };
  const getUserMedia = vi.fn(async () => {
    if (allow === 'denied') throw new DOMException('no', 'NotAllowedError');
    if (allow === 'missing') throw new DOMException('no', 'NotFoundError');
    return { getTracks: () => [track] } as unknown as MediaStream;
  });
  Object.defineProperty(navigator, 'mediaDevices', { value: { getUserMedia }, configurable: true });
  return { getUserMedia, track };
}

function fakeWakeLock() {
  const locks: { release: ReturnType<typeof vi.fn>; released: boolean }[] = [];
  const request = vi.fn(async () => {
    const lock = {
      released: false,
      release: vi.fn(async () => {
        lock.released = true;
      }),
      addEventListener: vi.fn(),
    };
    locks.push(lock);
    return lock;
  });
  Object.defineProperty(navigator, 'wakeLock', { value: { request }, configurable: true });
  return { request, locks };
}

function forgetBrowserFakes() {
  for (const key of ['mediaDevices', 'wakeLock'] as const) {
    if (Object.getOwnPropertyDescriptor(navigator, key)) delete (navigator as unknown as Record<string, unknown>)[key];
  }
}

function setVisibility(state: 'visible' | 'hidden') {
  Object.defineProperty(document, 'visibilityState', { value: state, configurable: true });
  document.dispatchEvent(new Event('visibilitychange'));
}

function handlers() {
  return { onRecording: vi.fn(), onTick: vi.fn(), onAudio: vi.fn(), onProblem: vi.fn() };
}

beforeEach(() => {
  FakeRecorder.last = null;
  vi.stubGlobal('MediaRecorder', FakeRecorder);
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  forgetBrowserFakes();
  setVisibility('visible');
});

describe('canDictate', () => {
  it('needs both the microphone and a recorder', () => {
    expect(canDictate()).toBe(false);
    fakeMicrophone();
    expect(canDictate()).toBe(true);
    vi.unstubAllGlobals();
    expect(canDictate()).toBe(false);
  });
});

describe('Dictation', () => {
  it('records in the format the device gives, keeps the screen on, and hands over the audio', async () => {
    const mic = fakeMicrophone();
    const wake = fakeWakeLock();
    const on = handlers();
    const dictation = new Dictation(on);
    await dictation.start();
    expect(mic.getUserMedia).toHaveBeenCalledWith({ audio: true });
    const recorder = FakeRecorder.last as FakeRecorder;
    expect(recorder.mimeType).toBe('audio/webm;codecs=opus');
    expect(recorder.start).toHaveBeenCalled();
    expect(on.onRecording).toHaveBeenCalledTimes(1);
    await vi.waitFor(() => expect(wake.request).toHaveBeenCalledWith('screen'));
    dictation.stop();
    expect(on.onAudio).toHaveBeenCalledTimes(1);
    const audio = on.onAudio.mock.calls[0][0] as Blob;
    expect(audio.type).toBe('audio/webm;codecs=opus');
    expect(audio.size).toBeGreaterThan(0);
    // The microphone and the screen go back as they were.
    expect(mic.track.stop).toHaveBeenCalled();
    expect(wake.locks[0].release).toHaveBeenCalled();
  });

  it('where the device names no format of its own, it uses the one the recorder picks (iPhone)', async () => {
    FakeRecorder.supported = [];
    fakeMicrophone();
    const on = handlers();
    const dictation = new Dictation(on);
    await dictation.start();
    dictation.stop();
    expect((on.onAudio.mock.calls[0][0] as Blob).type).toBe('audio/mp4');
    FakeRecorder.supported = ['audio/webm;codecs=opus', 'audio/webm'];
  });

  it('stops by itself at two minutes and counts the time while it records', async () => {
    vi.useFakeTimers();
    fakeMicrophone();
    const on = handlers();
    const dictation = new Dictation(on);
    await dictation.start();
    vi.advanceTimersByTime(12_000);
    expect(on.onTick).toHaveBeenLastCalledWith(12_000);
    expect(on.onAudio).not.toHaveBeenCalled();
    vi.advanceTimersByTime(DICTATION_LIMIT_MS - 12_000);
    expect(DICTATION_LIMIT_MS).toBe(120_000);
    expect(FakeRecorder.last?.stop).toHaveBeenCalled();
    expect(on.onAudio).toHaveBeenCalledTimes(1);
    // Nothing more after it stopped.
    const ticks = on.onTick.mock.calls.length;
    vi.advanceTimersByTime(10_000);
    expect(on.onTick).toHaveBeenCalledTimes(ticks);
  });

  it('lets the screen lock go while the page is hidden and keeps it on again when it comes back', async () => {
    fakeMicrophone();
    const wake = fakeWakeLock();
    const dictation = new Dictation(handlers());
    await dictation.start();
    await vi.waitFor(() => expect(wake.request).toHaveBeenCalledTimes(1));
    setVisibility('hidden');
    expect(wake.locks[0].release).toHaveBeenCalled();
    setVisibility('visible');
    await vi.waitFor(() => expect(wake.request).toHaveBeenCalledTimes(2));
    dictation.stop();
    expect(wake.locks[1].release).toHaveBeenCalled();
    // After it stopped, coming back does not keep the screen on.
    setVisibility('hidden');
    setVisibility('visible');
    await Promise.resolve();
    expect(wake.request).toHaveBeenCalledTimes(2);
  });

  it('records also where the screen cannot be kept on', async () => {
    fakeMicrophone();
    Object.defineProperty(navigator, 'wakeLock', {
      value: { request: vi.fn(async () => Promise.reject(new DOMException('no', 'NotAllowedError'))) },
      configurable: true,
    });
    const on = handlers();
    const dictation = new Dictation(on);
    await dictation.start();
    dictation.stop();
    expect(on.onAudio).toHaveBeenCalledTimes(1);
    expect(on.onProblem).not.toHaveBeenCalled();
  });

  it('without permission it says so plainly, and records nothing', async () => {
    fakeMicrophone('denied');
    const on = handlers();
    await new Dictation(on).start();
    expect(on.onProblem).toHaveBeenCalledWith(MIC_DENIED);
    expect(on.onRecording).not.toHaveBeenCalled();
    expect(FakeRecorder.last).toBeNull();
  });

  it('without a microphone it says it could not hear', async () => {
    fakeMicrophone('missing');
    const on = handlers();
    await new Dictation(on).start();
    expect(on.onProblem).toHaveBeenCalledWith(MIC_FAILED);
  });

  it('cancelled (the form goes away), it hands over nothing and lets the microphone go', async () => {
    const mic = fakeMicrophone();
    const wake = fakeWakeLock();
    const on = handlers();
    const dictation = new Dictation(on);
    await dictation.start();
    await vi.waitFor(() => expect(wake.request).toHaveBeenCalled());
    dictation.cancel();
    expect(on.onAudio).not.toHaveBeenCalled();
    expect(mic.track.stop).toHaveBeenCalled();
    expect(wake.locks[0].release).toHaveBeenCalled();
  });

  it('a recorder that fails says it could not hear and hands over nothing', async () => {
    fakeMicrophone();
    const on = handlers();
    const dictation = new Dictation(on);
    await dictation.start();
    const recorder = FakeRecorder.last as FakeRecorder;
    recorder.onerror?.();
    expect(on.onProblem).toHaveBeenCalledWith(MIC_FAILED);
    expect(on.onAudio).not.toHaveBeenCalled();
  });
});
