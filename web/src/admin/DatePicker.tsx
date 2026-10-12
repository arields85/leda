import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from 'react';
import { shortDate, weekdayOf } from '../format';

const MONTHS = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
];
const WEEK = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];

/** "2026-10-16" + 3 → "2026-10-19", as calendar dates (no time zone involved). */
export function addDays(iso: string, days: number): string {
  const [year, month, day] = iso.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day + days)).toISOString().slice(0, 10);
}

/** "2026-10-16" → "vie 16.10": how a day is read out and shown. */
export function dayLabel(iso: string): string {
  return `${weekdayOf(iso).toLowerCase()} ${shortDate(iso)}`;
}

function monthOf(iso: string): string {
  return iso.slice(0, 7);
}

function nextMonth(month: string, step: number): string {
  const [year, m] = month.split('-').map(Number);
  return new Date(Date.UTC(year, m - 1 + step, 1)).toISOString().slice(0, 7);
}

/** The cells of a month, Monday first: null for the blanks before the 1st. */
function cells(month: string): (string | null)[] {
  const [year, m] = month.split('-').map(Number);
  const first = new Date(Date.UTC(year, m - 1, 1));
  const length = new Date(Date.UTC(year, m, 0)).getUTCDate();
  const blanks = (first.getUTCDay() + 6) % 7;
  const days = Array.from({ length }, (_, i) => `${month}-${String(i + 1).padStart(2, '0')}`);
  return [...Array<null>(blanks).fill(null), ...days];
}

interface DatePickerProps {
  /** The working days the server offers, sorted: nothing else can be chosen. */
  days: string[];
  value: string;
  onChange: (day: string) => void;
  labelledBy: string;
  describedBy?: string;
}

/** A compact month calendar in the Terminal look that only lets you pick the space's working
 * days from today on (decision 9). Keyboard: Tab reaches the month, the arrows move between the
 * days that can be chosen, Enter or Space picks one. */
export function DatePicker({ days, value, onChange, labelledBy, describedBy }: DatePickerProps) {
  const allowed = useMemo(() => new Set(days), [days]);
  const first = days[0] ?? null;
  const last = days[days.length - 1] ?? null;
  const [month, setMonth] = useState(() => monthOf(value || first || new Date().toISOString()));
  const [focusDay, setFocusDay] = useState<string | null>(null);
  const grid = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (value) setMonth(monthOf(value));
  }, [value]);

  useEffect(() => {
    if (!focusDay) return;
    grid.current?.querySelector<HTMLButtonElement>(`[data-day="${focusDay}"]`)?.focus();
  }, [focusDay, month]);

  if (!first || !last) {
    return <p className="m-0 text-small text-ink-dim">No hay días hábiles para elegir.</p>;
  }

  const shown = cells(month);
  const inMonth = days.filter((d) => monthOf(d) === month);
  const tabbable = value && monthOf(value) === month && allowed.has(value) ? value : inMonth[0];
  const canBack = month > monthOf(first);
  const canForward = month < monthOf(last);

  function moveTo(day: string | undefined) {
    if (!day) return;
    setMonth(monthOf(day));
    setFocusDay(day);
  }

  function onKey(event: KeyboardEvent<HTMLButtonElement>, day: string) {
    const index = days.indexOf(day);
    let target: string | undefined;
    if (event.key === 'ArrowRight') target = days[index + 1];
    else if (event.key === 'ArrowLeft') target = days[index - 1];
    else if (event.key === 'ArrowDown') target = days.find((d) => d >= addDays(day, 7));
    else if (event.key === 'ArrowUp') target = [...days].reverse().find((d) => d <= addDays(day, -7));
    else return;
    event.preventDefault();
    moveTo(target);
  }

  const [year, m] = month.split('-').map(Number);
  const arrow =
    'grid h-7 w-7 place-items-center rounded-card border-hard border-line-soft bg-transparent text-ink-soft disabled:opacity-30';
  return (
    <div
      role="group"
      aria-labelledby={labelledBy}
      aria-describedby={describedBy}
      className="flex w-full max-w-[19rem] flex-col gap-2 rounded-card border-hard border-line bg-card p-2.5 shadow-hard"
    >
      <div className="flex items-center justify-between gap-2 text-small">
        <button
          type="button"
          className={arrow}
          aria-label="mes anterior"
          disabled={!canBack}
          onClick={() => {
            setFocusDay(null);
            setMonth(nextMonth(month, -1));
          }}
        >
          <ChevronLeft aria-hidden="true" size={14} strokeWidth={2} />
        </button>
        <span aria-live="polite" className="font-bold text-ink">
          {MONTHS[m - 1]} {year}
        </span>
        <button
          type="button"
          className={arrow}
          aria-label="mes siguiente"
          disabled={!canForward}
          onClick={() => {
            setFocusDay(null);
            setMonth(nextMonth(month, 1));
          }}
        >
          <ChevronRight aria-hidden="true" size={14} strokeWidth={2} />
        </button>
      </div>
      <div ref={grid} className="grid grid-cols-7 gap-1 text-center text-small">
        {WEEK.map((d, i) => (
          <span key={i} aria-hidden="true" className="text-mini text-ink-dim">
            {d}
          </span>
        ))}
        {shown.map((day, i) => {
          if (day === null) return <span key={`b${i}`} aria-hidden="true" />;
          const open = allowed.has(day);
          const selected = day === value;
          const number = Number(day.slice(8));
          if (!open) {
            return (
              <span key={day} aria-hidden="true" className="py-1 text-line-strong">
                {number}
              </span>
            );
          }
          return (
            <button
              key={day}
              type="button"
              data-day={day}
              tabIndex={day === tabbable ? 0 : -1}
              aria-pressed={selected}
              aria-label={dayLabel(day)}
              onClick={() => onChange(day)}
              onKeyDown={(event) => onKey(event, day)}
              className={`rounded-card border-hard py-1 ${selected ? 'border-ink bg-ink font-bold text-page' : 'border-line-soft bg-transparent text-ink hover:border-line-strong'}`}
            >
              {number}
            </button>
          );
        })}
      </div>
    </div>
  );
}
