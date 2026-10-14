import { LogOut } from 'lucide-react';
import { useState } from 'react';
import { signOut } from '../api';

/** "salir": closes the session on this computer, after one confirmation, because coming back
 * needs the QR again. Only in a browser: inside the Mini App each opening identifies the person
 * (MA-3). The administration door passes its own `action`. */
export function SignOut({
  onDone,
  action = signOut,
}: {
  onDone: () => void;
  action?: () => Promise<void>;
}) {
  const [step, setStep] = useState<'idle' | 'confirm' | 'busy' | 'failed'>('idle');

  async function confirm() {
    setStep('busy');
    try {
      await action();
      onDone();
    } catch {
      setStep('failed');
    }
  }

  const link = 'bg-transparent p-0 text-small text-ink-dim underline-offset-2 hover:text-ink hover:underline';
  if (step === 'idle') {
    return (
      <button type="button" className={`inline-flex items-center gap-1 ${link}`} onClick={() => setStep('confirm')}>
        <LogOut aria-hidden="true" size={12} strokeWidth={2} />
        salir
      </button>
    );
  }
  return (
    <div className="flex flex-col items-end gap-1 text-right text-small text-ink-dim">
      <span>
        {step === 'failed'
          ? 'No se pudo cerrar la sesión. Probá de nuevo en un rato.'
          : 'Para volver a entrar vas a tener que escanear el código otra vez.'}
      </span>
      <span className="flex gap-3">
        <button type="button" className={link} onClick={() => setStep('idle')} disabled={step === 'busy'}>
          no, seguir
        </button>
        <button type="button" className={`${link} text-ink`} onClick={confirm} disabled={step === 'busy'}>
          sí, salir
        </button>
      </span>
    </div>
  );
}
