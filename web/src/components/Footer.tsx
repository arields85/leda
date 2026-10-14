import { MessageCircle } from 'lucide-react';
import { closeMiniApp } from '../telegram';
import { SignOut } from './SignOut';

// Only a Telegram address opens: the server builds it from the space's bot username.
const TELEGRAM = /^https:\/\/t\.me\/[A-Za-z][A-Za-z0-9_]{4,31}$/;

const SMALL = 'inline-flex items-center gap-1 bg-transparent p-0 text-small text-ink-dim no-underline underline-offset-2 hover:text-ink hover:underline';

/** "Volver al chat" (MA-3), small, bottom left: inside the Mini App it closes it, back to the chat
 * it came from; in a browser it opens the chat with the team bot. Without either, nothing. */
function BackToChat({ inMiniApp, chat }: { inMiniApp: boolean; chat: string | null }) {
  if (inMiniApp) {
    return (
      <button type="button" className={SMALL} onClick={() => closeMiniApp()}>
        <MessageCircle aria-hidden="true" size={12} strokeWidth={2} />
        Volver al chat
      </button>
    );
  }
  if (!chat || !TELEGRAM.test(chat)) return null;
  return (
    <a href={chat} target="_blank" rel="noopener noreferrer" className={SMALL}>
      <MessageCircle aria-hidden="true" size={12} strokeWidth={2} />
      Volver al chat
    </a>
  );
}

/** The bottom of the team's page (MA-3, the user's iPhone test): the big "> Nueva tarea", in the
 * primary style "> consultar a leda" had, only to whoever loads tasks; under it, "Volver al chat"
 * on the left and, only in a browser, "salir" on the right (inside the Mini App each opening
 * identifies the person again, so there is nothing to close). */
export function Footer({
  inMiniApp,
  chat,
  canLoad,
  onNewTask,
  onSignedOut,
}: {
  inMiniApp: boolean;
  chat: string | null;
  canLoad: boolean;
  onNewTask: () => void;
  onSignedOut: () => void;
}) {
  return (
    <footer className="flex shrink-0 flex-col gap-3 pb-[22px] pt-3">
      {canLoad && (
        <button
          type="button"
          onClick={onNewTask}
          className="flex h-12 w-full select-none items-center gap-2 rounded-card border-hard border-ink bg-card px-3.5 text-left text-button font-bold text-ink shadow-hard-ink"
        >
          &gt; Nueva tarea
        </button>
      )}
      <div className="flex items-start justify-between gap-3">
        <BackToChat inMiniApp={inMiniApp} chat={chat} />
        {!inMiniApp && <SignOut onDone={onSignedOut} />}
      </div>
    </footer>
  );
}
