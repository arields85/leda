import { useEffect, useRef, useState } from 'react';
import { insideTelegram, REOPEN_TEXT } from '../telegram';
import { Notice } from './Notice';

// Entering from a computer, or from a phone's browser outside Telegram (ADR 0024, decisions 4 and
// 5; MA1c and MA5): the page asks the door for a sign-in request and shows a QR with
// `t.me/<bot>?start=compu_<code>`. Scanned with the phone's camera, Telegram opens the chat with
// Leda and its "Entrar en la compu" button; the page asks every few seconds and, once approved,
// it is in. On a phone's browser the QR cannot be scanned by the same phone: "Entrar con Telegram"
// opens the same chat. No user, password or code to type.

export type Door = 'equipo' | 'administracion';

/** How often the page asks whether the request was approved. */
export const POLL_MS = 2500;

interface Request {
  pedido_id: string;
  enlace: string;
  qr: string[];
}

type State =
  | { kind: 'asking' }
  | { kind: 'shown'; request: Request }
  | { kind: 'expired' }
  | { kind: 'unavailable' }
  | { kind: 'failed' };

function base(door: Door): string {
  return door === 'equipo' ? '/app/api/entrar/qr' : '/app/admin/api/entrar/qr';
}

/** Whether this is a phone or a tablet, where the QR cannot be scanned by the same device. */
export function onAPhone(nav: Pick<Navigator, 'userAgent'> = navigator): boolean {
  return /Android|iPhone|iPad|iPod|Mobile/i.test(nav.userAgent);
}

/** The QR as an SVG, dark on light with its quiet zone, from the server's matrix. */
export function QrCode({ rows, label }: { rows: string[]; label: string }) {
  const size = rows.length + 8;
  const path = rows
    .flatMap((row, y) => [...row].map((cell, x) => (cell === '1' ? `M${x + 4},${y + 4}h1v1h-1z` : '')))
    .join('');
  return (
    <svg
      role="img"
      aria-label={label}
      viewBox={`0 0 ${size} ${size}`}
      shapeRendering="crispEdges"
      className="h-auto w-full max-w-[16rem] rounded-card"
    >
      <rect width={size} height={size} fill="#FFFFFF" />
      <path d={path} fill="#000000" />
    </svg>
  );
}

/** The sign-in page of a door. `space`: the team's space (from the address or the last one this
 * browser entered); without it the team door can only say where to open Leda. */
export function SignIn({ door, space, onIn, phone = onAPhone() }: {
  door: Door;
  space: string | null;
  onIn: () => void;
  phone?: boolean;
}) {
  const [state, setState] = useState<State>({ kind: 'asking' });
  const [attempt, setAttempt] = useState(0);
  const onInNow = useRef(onIn);
  onInNow.current = onIn;

  // Inside Telegram there is no QR to scan: the session comes from opening the Mini App again
  // (review R4-spent-signature-lost-response: the signature was used but its answer was lost).
  // Decided once, by Telegram's platform too: opened without signed data, it is still Telegram.
  const [inTelegram] = useState(() => insideTelegram());

  useEffect(() => {
    if (inTelegram || (door === 'equipo' && !space)) return;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    setState({ kind: 'asking' });

    async function ask(id: string) {
      if (stopped) return;
      try {
        const response = await fetch(`${base(door)}/${encodeURIComponent(id)}`, {
          credentials: 'same-origin',
          headers: { Accept: 'application/json' },
        });
        const body = (await response.json().catch(() => ({}))) as { estado?: string };
        if (stopped) return;
        if (body.estado === 'adentro') {
          onInNow.current();
          return;
        }
        if (body.estado === 'vencido' || response.status === 404) {
          setState({ kind: 'expired' });
          return;
        }
      } catch {
        // A blip: ask again.
      }
      timer = setTimeout(() => void ask(id), POLL_MS);
    }

    (async () => {
      try {
        const response = await fetch(base(door), {
          method: 'POST',
          credentials: 'same-origin',
          headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
          body: JSON.stringify(door === 'equipo' ? { espacio: space } : {}),
        });
        if (stopped) return;
        if (response.status === 404) {
          setState({ kind: 'unavailable' });
          return;
        }
        if (!response.ok) {
          setState({ kind: 'failed' });
          return;
        }
        const request = (await response.json()) as Request;
        if (stopped) return;
        setState({ kind: 'shown', request });
        timer = setTimeout(() => void ask(request.pedido_id), POLL_MS);
      } catch {
        if (!stopped) setState({ kind: 'failed' });
      }
    })();
    return () => {
      stopped = true;
      if (timer) clearTimeout(timer);
    };
  }, [door, space, attempt, inTelegram]);

  const again = (
    <button
      type="button"
      onClick={() => setAttempt((n) => n + 1)}
      className="w-fit rounded-card border-hard border-line bg-card px-3 py-2 text-small text-ink shadow-hard"
    >
      &gt; otro código
    </button>
  );
  const what = door === 'equipo' ? 'tus tareas' : 'la administración';

  if (inTelegram) {
    return (
      <Notice title="No se pudo abrir la sesión.">
        {/* What to do, in plain words (MA-5): Telegram's «Cerrar» and the bot's menu button. */}
        <p className="m-0">{REOPEN_TEXT[door]}</p>
      </Notice>
    );
  }
  if (door === 'equipo' && !space) {
    return (
      <Notice title="Entrá desde Telegram.">
        <p className="m-0">Abrí el chat de Leda de tu equipo y tocá «Mi espacio».</p>
      </Notice>
    );
  }
  if (state.kind === 'asking') return <Notice title="Cargando…" />;
  if (state.kind === 'unavailable') {
    return (
      <Notice title="Esta dirección no sirve para entrar.">
        <p className="m-0">Pedile a Leda por Telegram la dirección para la compu.</p>
      </Notice>
    );
  }
  if (state.kind === 'failed') {
    return (
      <Notice title="No se pudo preparar la entrada.">
        <p className="m-0">Probá de nuevo en un rato.</p>
        {again}
      </Notice>
    );
  }
  if (state.kind === 'expired') {
    return (
      <Notice title="El código venció.">
        <p className="m-0">Cada código sirve unos minutos y una sola vez.</p>
        {again}
      </Notice>
    );
  }
  const { request } = state;
  return (
    <section aria-label="Entrar con Telegram" className="flex flex-col gap-3 pt-6 text-body text-ink-soft">
      <p className="m-0 text-button font-bold text-ink">Entrá con Telegram.</p>
      {phone ? (
        <>
          <p className="m-0">Tocá el botón: se abre el chat de Leda en Telegram, y ahí «Entrar en la compu».</p>
          <a
            href={request.enlace}
            className="w-fit rounded-card border-hard border-line bg-card px-3 py-2 text-small font-bold text-ink no-underline shadow-hard"
          >
            Entrar con Telegram
          </a>
        </>
      ) : (
        <>
          <p className="m-0">
            Escaneá el código con la cámara del celular. Se abre el chat de Leda en Telegram: tocá «Entrar en la
            compu» y acá entra solo a {what}.
          </p>
          <QrCode rows={request.qr} label="Código para entrar con Telegram" />
        </>
      )}
      <p className="m-0 text-small text-ink-dim">El código vence en unos minutos y sirve una sola vez.</p>
    </section>
  );
}
