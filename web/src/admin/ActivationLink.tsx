import { useState } from 'react';
import { SessionClosedError } from '../api';
import type { Problem } from './api';
import { Errors } from './AreaEditor';
import { SMALL } from './controls';
import type { ActivationLink as Link, TeamApi } from './teamApi';
import { FIELD_HINT } from './typography';

type State =
  | { kind: 'idle' }
  | { kind: 'sending' }
  | { kind: 'shown'; link: Link; copied: boolean }
  | { kind: 'failed'; errors: Problem[] };

/** "> copiar el enlace de activación" (J7-5; ADR 0024): asks the server for a new link for someone
 * who has not connected Telegram yet (the previous unused one stops working), copies it and shows
 * it once, with how to send it. The server keeps only its fingerprint, so the link is never shown
 * again: another tap makes a new one. */
export function ActivationLink({
  api,
  membershipId,
  nombre,
  onClosed,
}: {
  api: TeamApi;
  membershipId: string;
  nombre: string;
  onClosed: () => void;
}) {
  const [state, setState] = useState<State>({ kind: 'idle' });

  async function issue() {
    setState({ kind: 'sending' });
    try {
      const result = await api.issueLink(membershipId);
      if (result.kind === 'rejected') {
        setState({ kind: 'failed', errors: result.errors });
        return;
      }
      let copied = false;
      try {
        if (navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(result.link.enlace);
          copied = true;
        }
      } catch {
        // Some browsers (and the Mini App) do not let a page copy: the link stays on screen.
      }
      setState({ kind: 'shown', link: result.link, copied });
    } catch (error) {
      if (error instanceof SessionClosedError) onClosed();
      else
        setState({
          kind: 'failed',
          errors: [
            { campo: 'red', motivo: 'sin_respuesta', texto: 'No se pudo armar el enlace: no llegó la respuesta. Probá de nuevo.' },
          ],
        });
    }
  }

  if (state.kind === 'shown') {
    return (
      <div
        role="status"
        aria-label={`Enlace de activación de ${nombre}`}
        className="flex min-w-0 flex-col gap-1 rounded-card border-hard border-line-soft px-2.5 py-2 text-small"
      >
        <span className="text-ink">{state.copied ? 'Enlace copiado.' : 'Copiá el enlace:'}</span>
        <code className="min-w-0 select-all break-all text-ink-soft">{state.link.enlace}</code>
        <span className={FIELD_HINT}>
          Mandáselo por donde se hablen; vence en {state.link.vence_en_dias} días.
        </span>
      </div>
    );
  }
  return (
    <span className="flex min-w-0 flex-col gap-1">
      <button
        type="button"
        className={SMALL}
        onClick={() => void issue()}
        disabled={state.kind === 'sending'}
      >
        {state.kind === 'sending' ? 'armando el enlace…' : '> copiar el enlace de activación'}
      </button>
      {state.kind === 'failed' && <Errors errors={state.errors} />}
    </span>
  );
}
