import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { canDictate, Dictation, DICTATION_LIMIT_MS, MIC_DENIED, MIC_FAILED } from './dictation';
import { SessionClosedError } from '../api';
import {
  DICTATION_FAILED,
  DICTATION_TIMEOUT_MS,
  DICTATION_TOO_LONG,
  DICTATION_UNHEARD,
  transcribe,
} from './api';

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

  it('an audio the browser gives with no type at all goes as audio/mp4, the iPhone\'s (J2-30)', async () => {
    // A recorder that names no type, and pieces with no type either.
    class Untyped extends FakeRecorder {
      constructor(stream: MediaStream, options?: { mimeType?: string }) {
        super(stream, options);
        this.mimeType = '';
      }
    }
    vi.stubGlobal('MediaRecorder', Untyped);
    FakeRecorder.supported = [];
    fakeMicrophone();
    const on = handlers();
    const dictation = new Dictation(on);
    await dictation.start();
    dictation.stop();
    FakeRecorder.supported = ['audio/webm;codecs=opus', 'audio/webm'];
    expect((on.onAudio.mock.calls[0][0] as Blob).type).toBe('audio/mp4');
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

// The transcribe client (`api.ts`, J2b), every way the answer can come back (review
// review-0f465303e17d9ce6: these branches had no test). Anything but a text reads as "could not",
// in plain words; only a closed session throws.
describe('transcribe', () => {
  const AUDIO = new Blob(['audio'], { type: 'audio/webm;codecs=opus' });
  const json = (status: number, body: unknown) =>
    new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

  function serve(answer: Response | Error | (() => Promise<Response>)) {
    const fetch = vi.fn(async (_url: string, init?: RequestInit) => {
      if (typeof answer === 'function') return answer();
      if (answer instanceof Error) throw answer;
      void init;
      return answer;
    });
    vi.stubGlobal('fetch', fetch);
    return fetch;
  }

  it('sends the audio as it is, with its type, and gives back the text', async () => {
    const fetch = serve(json(200, { texto: '  colgar el estante  ' }));
    expect(await transcribe('s 1', AUDIO)).toEqual({ kind: 'text', text: 'colgar el estante' });
    const [url, init] = fetch.mock.calls[0];
    expect(url).toBe('/app/admin/api/espacios/s%201/dictado');
    expect(init?.method).toBe('POST');
    expect(init?.body).toBe(AUDIO);
    expect(init?.headers).toEqual(expect.objectContaining({ 'Content-Type': 'audio/webm;codecs=opus' }));
  });

  it('an audio with no type goes as audio/mp4, never with an empty type (J2-30)', async () => {
    const fetch = serve(json(200, { texto: 'colgar el estante' }));
    await transcribe('s1', new Blob(['audio']));
    expect(fetch.mock.calls[0][1]?.headers).toEqual(expect.objectContaining({ 'Content-Type': 'audio/mp4' }));
  });

  it('a dictation cut by the limit gives the text and the notice that it was cut (J2-26)', async () => {
    serve(json(200, { texto: 'colgar el estante', aviso: 'Se cortó.' }));
    expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'text', text: 'colgar el estante', notice: 'Se cortó.' });
  });

  it('an empty text, or an answer that is not JSON, is that nothing was understood', async () => {
    serve(json(200, { texto: '   ' }));
    expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'failed', text: DICTATION_UNHEARD });
    serve(new Response('<html>', { status: 200 }));
    expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'failed', text: DICTATION_UNHEARD });
  });

  it("422 says the server's words, or its own when there are none", async () => {
    serve(json(422, { error: 'no_se_entendio', texto: 'No te entendí.' }));
    expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'failed', text: 'No te entendí.' });
    serve(json(422, { error: 'no_se_entendio' }));
    expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'failed', text: DICTATION_UNHEARD });
  });

  it('too long, a server failure or no network, each in plain words', async () => {
    serve(json(413, { error: 'demasiado_grande' }));
    expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'failed', text: DICTATION_TOO_LONG });
    for (const status of [502, 503, 500, 403, 415]) {
      serve(json(status, { error: 'x', texto: 'el texto del servidor no se muestra' }));
      expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'failed', text: DICTATION_FAILED });
    }
    serve(new TypeError('Failed to fetch'));
    expect(await transcribe('s1', AUDIO)).toEqual({ kind: 'failed', text: DICTATION_FAILED });
  });

  it('a closed session throws, to go back to the entry', async () => {
    serve(json(401, { error: 'sin_sesion' }));
    await expect(transcribe('s1', AUDIO)).rejects.toBeInstanceOf(SessionClosedError);
  });

  it('gives up after its own time, longer than the server waits for Gemini', async () => {
    vi.useFakeTimers();
    let signal: AbortSignal | undefined;
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url: string, init?: RequestInit) =>
          new Promise<Response>((_resolve, reject) => {
            signal = init?.signal ?? undefined;
            signal?.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')));
          }),
      ),
    );
    const answer = transcribe('s1', AUDIO);
    await vi.advanceTimersByTimeAsync(DICTATION_TIMEOUT_MS - 1);
    expect(signal?.aborted).toBe(false);
    await vi.advanceTimersByTimeAsync(1);
    expect(await answer).toEqual({ kind: 'failed', text: DICTATION_FAILED });
    expect(DICTATION_TIMEOUT_MS).toBeGreaterThan(35_000);
  });
});
