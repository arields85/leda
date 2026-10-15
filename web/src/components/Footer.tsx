const BIG = 'flex h-12 min-w-0 flex-1 basis-0 select-none items-center gap-2 rounded-card border-hard border-ink bg-card px-3 text-left whitespace-nowrap text-button font-bold text-ink shadow-hard-ink';

/** The bottom of the team's page (MA-3 and MA-4, the user's tests on the iPhone and the computer):
 * "> Nueva tarea", to whoever loads tasks, and next to it "> Nuevo objetivo", only to Dirección,
 * both in the primary style and side by side. Nothing else: no "Volver al chat" (the computer's
 * "Cerrar sesión" lives in the header, under the name, MA-7). */
export function Footer({
  canLoad,
  canCreateObjective,
  onNewTask,
  onNewObjective,
}: {
  canLoad: boolean;
  canCreateObjective: boolean;
  onNewTask: () => void;
  onNewObjective: () => void;
}) {
  if (!canLoad && !canCreateObjective) return <div aria-hidden="true" className="shrink-0 pb-[22px]" />;
  return (
    <footer className="flex shrink-0 gap-2.5 pb-[22px] pt-3">
      {canLoad && (
        <button type="button" onClick={onNewTask} className={BIG}>
          &gt; Nueva tarea
        </button>
      )}
      {canCreateObjective && (
        <button type="button" onClick={onNewObjective} className={BIG}>
          &gt; Nuevo objetivo
        </button>
      )}
    </footer>
  );
}
