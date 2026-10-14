// Dictating into the free box (portion J2b): the browser records what the person says and the
// server turns it into text with Gemini (`transcribe` in `api.ts`). It replaced the browser's
// speech recognition, which stopped on the iPhone when the screen locked (J2-5); while it records,
// the screen is kept on where the browser allows it. Typing always works; the microphone is an
// extra, never the only way.
//
// J2-27 (the user, after the phone test, 2026-10-13): while it records, a row of bars moves with
// the voice, like the messaging apps (`AudioBars.tsx`). The level comes from the same microphone,
// through Web Audio (`VoiceLevel`); without it there are no bars and the recording is the same.

/** Two minutes at most: then it stops by itself and hands over what it recorded. */
export const DICTATION_LIMIT_MS = 2 * 60 * 1000;

export const MIC_DENIED = 'No tengo permiso para el micrófono; escribilo acá.';
export const MIC_FAILED = 'No te pude escuchar; probá de nuevo o escribilo acá.';

// The formats to ask for, in order, when the device offers them; otherwise the one the recorder
// picks (the iPhone records mp4/aac). The audio goes with the type it really has.
const FORMATS = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'];

interface ScreenLock {
  release(): Promise<void>;
  addEventListener?(type: 'release', listener: () => void): void;
}

interface WithWakeLock {
  wakeLock?: { request(type: 'screen'): Promise<ScreenLock> };
}

type AudioContextClass = new () => AudioContext;

/** The browser's Web Audio, also the old Safari name; undefined where there is none. */
function audioContextClass(): AudioContextClass | undefined {
  if (typeof window === 'undefined') return undefined;
  const w = window as unknown as { AudioContext?: AudioContextClass; webkitAudioContext?: AudioContextClass };
  return w.AudioContext ?? w.webkitAudioContext;
}

/** How loud the voice is now, from the microphone's own stream (J2-27): an analyser over the
 * stream, read when asked. It must be made in the tap itself: Safari on the iPhone lets Web Audio
 * run only from a tap, so it is made, and resumed, before waiting for the microphone. Anything
 * that fails leaves it without a level (no bars), never without the recording. */
export class VoiceLevel {
  private context: AudioContext | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private analyser: AnalyserNode | null = null;
  private samples: Uint8Array<ArrayBuffer> | null = null;

  constructor() {
    const Context = audioContextClass();
    if (!Context) return;
    try {
      this.context = new Context();
      void Promise.resolve(this.context.resume?.()).catch(() => {});
    } catch {
      this.context = null;
    }
  }

  /** Listens to the stream; without Web Audio, or if it fails, there is no level. */
  attach(stream: MediaStream): void {
    if (!this.context) return;
    try {
      this.source = this.context.createMediaStreamSource(stream);
      this.analyser = this.context.createAnalyser();
      this.analyser.fftSize = 256;
      this.source.connect(this.analyser);
      this.samples = new Uint8Array(this.analyser.fftSize);
    } catch {
      this.close();
    }
  }

  /** Whether there is a level to read. */
  get available(): boolean {
    return this.analyser !== null;
  }

  /** The voice now, from 0 (silence) to 1, or null without a level. */
  read(): number | null {
    if (!this.analyser || !this.samples) return null;
    this.analyser.getByteTimeDomainData(this.samples);
    let sum = 0;
    for (const sample of this.samples) {
      const centered = (sample - 128) / 128;
      sum += centered * centered;
    }
    // A voice is far from the full scale: three times its loudness fills the bar.
    return Math.min(1, Math.sqrt(sum / this.samples.length) * 3);
  }

  /** Lets the microphone's stream go and closes Web Audio. */
  close(): void {
    try {
      this.source?.disconnect();
    } catch {
      // Already gone.
    }
    const context = this.context;
    this.context = null;
    this.source = null;
    this.analyser = null;
    this.samples = null;
    if (context) void Promise.resolve(context.close?.()).catch(() => {});
  }
}

/** Whether this browser can record: a microphone to ask for and a recorder. */
export function canDictate(): boolean {
  return (
    typeof window !== 'undefined' &&
    typeof (window as { MediaRecorder?: unknown }).MediaRecorder === 'function' &&
    typeof navigator.mediaDevices?.getUserMedia === 'function'
  );
}

function preferredFormat(): string | undefined {
  const check = MediaRecorder.isTypeSupported;
  if (typeof check !== 'function') return undefined;
  return FORMATS.find((format) => check.call(MediaRecorder, format));
}

function denied(error: unknown): boolean {
  const name = (error as { name?: unknown } | null)?.name;
  return name === 'NotAllowedError' || name === 'SecurityError' || name === 'PermissionDeniedError';
}

export interface DictationHandlers {
  /** The microphone is on and it is recording. */
  onRecording(): void;
  /** How long it has been recording, once a second. */
  onTick(elapsedMs: number): void;
  /** It stopped (the person, or the two minutes) with what it recorded. */
  onAudio(audio: Blob): void;
  /** It could not record, in plain words. */
  onProblem(text: string): void;
}

type State = 'idle' | 'starting' | 'recording' | 'stopping' | 'done';

/** One dictation: asks for the microphone, records, keeps the screen on while it records (and
 * again when the page comes back), and stops by itself at two minutes. Used once. */
export class Dictation {
  private state: State = 'idle';
  private stream: MediaStream | null = null;
  private recorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private lock: ScreenLock | null = null;
  private limit: ReturnType<typeof setTimeout> | null = null;
  private ticker: ReturnType<typeof setInterval> | null = null;
  private discard = false;
  private voice: VoiceLevel | null = null;

  constructor(private readonly on: DictationHandlers) {}

  /** Whether the voice's level can be read while it records (J2-27). */
  hasLevel(): boolean {
    return this.voice?.available ?? false;
  }

  /** The voice now, from 0 to 1, or null when there is no level or it is not recording. */
  level(): number | null {
    return this.state === 'recording' ? (this.voice?.read() ?? null) : null;
  }

  async start(): Promise<void> {
    if (this.state !== 'idle') return;
    this.state = 'starting';
    // Before anything is awaited: still inside the tap (Safari on the iPhone, J2-27).
    this.voice = new VoiceLevel();
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (error) {
      this.state = 'done';
      this.voice?.close();
      this.voice = null;
      if (!this.discard) this.on.onProblem(denied(error) ? MIC_DENIED : MIC_FAILED);
      return;
    }
    this.stream = stream;
    // Stopped or cancelled while the browser asked for permission.
    if (this.state !== 'starting') {
      this.finish();
      return;
    }
    try {
      const format = preferredFormat();
      const recorder = format ? new MediaRecorder(stream, { mimeType: format }) : new MediaRecorder(stream);
      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) this.chunks.push(event.data);
      };
      recorder.onstop = () => this.finish();
      recorder.onerror = () => this.fail();
      this.recorder = recorder;
      // A piece every second, so what was said is kept even if the recorder ends on its own.
      recorder.start(1000);
      this.voice?.attach(stream);
    } catch {
      this.fail();
      return;
    }
    this.state = 'recording';
    const startedAt = Date.now();
    this.limit = setTimeout(() => this.stop(), DICTATION_LIMIT_MS);
    this.ticker = setInterval(() => this.on.onTick(Math.min(Date.now() - startedAt, DICTATION_LIMIT_MS)), 1000);
    document.addEventListener('visibilitychange', this.onVisibility);
    this.on.onRecording();
    void this.keepScreenOn();
  }

  /** Stops and hands over what it recorded. */
  stop(): void {
    if (this.state === 'starting') {
      this.state = 'stopping';
      return;
    }
    if (this.state !== 'recording') return;
    this.state = 'stopping';
    this.clearTimers();
    const recorder = this.recorder;
    if (recorder && recorder.state !== 'inactive') {
      try {
        recorder.stop();
        return;
      } catch {
        // It ended on its own: what it gave is all there is.
      }
    }
    this.finish();
  }

  /** Stops and hands over nothing (the form went away). */
  cancel(): void {
    this.discard = true;
    if (this.state === 'done') return;
    this.stop();
    if (this.state === 'stopping' && !this.recorder) this.finish();
  }

  private fail(): void {
    this.discard = true;
    const first = this.state !== 'done';
    this.finish();
    if (first) this.on.onProblem(MIC_FAILED);
  }

  /** Lets the microphone and the screen go, and hands over the audio unless it was discarded. */
  private finish(): void {
    if (this.state === 'done' && !this.stream && !this.recorder) return;
    this.state = 'done';
    this.clearTimers();
    document.removeEventListener('visibilitychange', this.onVisibility);
    this.releaseScreen();
    this.voice?.close();
    this.voice = null;
    for (const track of this.stream?.getTracks() ?? []) track.stop();
    this.stream = null;
    const recorder = this.recorder;
    this.recorder = null;
    if (recorder) {
      recorder.ondataavailable = null;
      recorder.onstop = null;
      recorder.onerror = null;
    }
    if (this.discard || !recorder) return;
    const audio = new Blob(this.chunks, { type: recorder.mimeType || this.chunks[0]?.type || '' });
    this.chunks = [];
    if (audio.size === 0) this.on.onProblem(MIC_FAILED);
    else this.on.onAudio(audio);
  }

  private clearTimers(): void {
    if (this.limit !== null) clearTimeout(this.limit);
    if (this.ticker !== null) clearInterval(this.ticker);
    this.limit = null;
    this.ticker = null;
  }

  private readonly onVisibility = () => {
    if (document.visibilityState === 'visible') void this.keepScreenOn();
    else this.releaseScreen();
  };

  /** Keeps the screen on while it records, where the browser allows it. Where it does not, the
   * recording goes on all the same (the person may have to keep the screen on herself). */
  private async keepScreenOn(): Promise<void> {
    const wakeLock = (navigator as WithWakeLock).wakeLock;
    if (!wakeLock || this.state !== 'recording' || this.lock) return;
    try {
      const lock = await wakeLock.request('screen');
      if (this.state !== 'recording' || this.lock) {
        void lock.release().catch(() => {});
        return;
      }
      this.lock = lock;
      // The browser lets it go by itself when the page is hidden.
      lock.addEventListener?.('release', () => {
        if (this.lock === lock) this.lock = null;
      });
    } catch {
      // Not allowed now (a hidden page, low battery): it records anyway.
    }
  }

  private releaseScreen(): void {
    const lock = this.lock;
    this.lock = null;
    if (lock) void Promise.resolve(lock.release()).catch(() => {});
  }
}
