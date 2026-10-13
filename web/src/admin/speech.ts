// Dictating into the free box (portion J2): only where the browser recognizes speech. Typing
// always works; the microphone is an extra, never the only way.

export interface SpeechResultEvent {
  resultIndex: number;
  results: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal?: boolean }>;
}

export interface Recognizer {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start(): void;
  stop(): void;
  onresult: ((event: SpeechResultEvent) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
}

export type RecognizerClass = new () => Recognizer;

/** The browser's speech recognition, or undefined where there is none (then no microphone). */
export function speechRecognition(): RecognizerClass | undefined {
  if (typeof window === 'undefined') return undefined;
  const w = window as unknown as { SpeechRecognition?: RecognizerClass; webkitSpeechRecognition?: RecognizerClass };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition;
}

/** What was heard in one result event, joined. */
export function heard(event: SpeechResultEvent): string {
  const parts: string[] = [];
  for (let i = event.resultIndex; i < event.results.length; i++) {
    const text = event.results[i]?.[0]?.transcript?.trim();
    if (text) parts.push(text);
  }
  return parts.join(' ');
}

export const MIC_DENIED = 'No tengo permiso para el micrófono; escribilo acá.';
export const MIC_FAILED = 'No te pude escuchar; probá de nuevo o escribilo acá.';

/** The plain words for a recognition error; null for one that needs none (the person stopped). */
export function micProblem(error: string): string | null {
  if (error === 'aborted') return null;
  return error === 'not-allowed' || error === 'service-not-allowed' ? MIC_DENIED : MIC_FAILED;
}
