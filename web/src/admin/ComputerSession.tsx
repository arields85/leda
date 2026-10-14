import { useEffect, useId, useState } from 'react';
import { RequestError, SessionClosedError } from '../api';
import { call } from './api';
import { Dropdown } from './Dropdown';
import { WARN } from './controls';

// How long a computer that entered with the QR stays remembered in a space (ADR 0024, decision 5):
// 1, 7, 30 or 90 days, or with no expiry (the default for everyone). Chosen by the administration
// for each space; it is still cut by leaving the team, "perdí el celular", the administration or
// signing out on that computer.

export const DURATIONS: { value: string; label: string }[] = [
  { value: '', label: 'sin vencimiento' },
  { value: '1', label: '1 día' },
  { value: '7', label: '7 días' },
  { value: '30', label: '30 días' },
  { value: '90', label: '90 días' },
];

function url(spaceId: string): string {
  return `/app/admin/api/espacios/${encodeURIComponent(spaceId)}/sesion-en-la-compu`;
}

export async function readComputerSession(spaceId: string, signal?: AbortSignal): Promise<number | null> {
  const response = await call(url(spaceId), { signal });
  if (response.status === 401) throw new SessionClosedError();
  if (!response.ok) throw new RequestError(response.status);
  return ((await response.json()) as { dias: number | null }).dias;
}

export async function saveComputerSession(spaceId: string, days: number | null): Promise<number | null> {
  const response = await call(url(spaceId), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dias: days }),
  });
  if (response.status === 401) throw new SessionClosedError();
  if (!response.ok) throw new RequestError(response.status);
  return ((await response.json()) as { dias: number | null }).dias;
}

/** The setting of one space, with what it means. A change is saved at once. */
export function ComputerSession({ spaceId, onClosed }: { spaceId: string; onClosed: () => void }) {
  const id = useId();
  const [days, setDays] = useState<string | null>(null);
  const [state, setState] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle');

  useEffect(() => {
    const request = new AbortController();
    setDays(null);
    setState('idle');
    readComputerSession(spaceId, request.signal)
      .then((value) => setDays(value === null ? '' : String(value)))
      .catch((error: unknown) => {
        if (request.signal.aborted) return;
        if (error instanceof SessionClosedError) onClosed();
        else setState('failed');
      });
    return () => request.abort();
    // `onClosed` is the page's; a new one is not a reason to read again.
  }, [spaceId]);

  async function choose(value: string) {
    setDays(value);
    setState('saving');
    try {
      const saved = await saveComputerSession(spaceId, value === '' ? null : Number(value));
      setDays(saved === null ? '' : String(saved));
      setState('saved');
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else setState('failed');
    }
  }

  return (
    <div className="flex w-full min-w-0 max-w-[24rem] flex-col gap-1.5 text-meta text-ink-dim">
      <label id={`${id}-label`} htmlFor={id} className="uppercase tracking-[0.04em]">
        una computadora queda recordada
      </label>
      {days === null && state !== 'failed' ? (
        <p className="m-0 text-body">Cargando…</p>
      ) : (
        <Dropdown
          id={id}
          labelledBy={`${id}-label`}
          value={days ?? ''}
          onChange={(value) => void choose(value)}
          options={DURATIONS}
        />
      )}
      <p role="status" className={`m-0 text-small ${state === 'failed' ? WARN : ''}`}>
        {state === 'saving'
          ? 'Guardando…'
          : state === 'saved'
            ? 'Guardado.'
            : state === 'failed'
              ? 'No se pudo guardar ahora; probá de nuevo.'
              : 'Después, esa computadora vuelve a escanear el código.'}
      </p>
    </div>
  );
}
