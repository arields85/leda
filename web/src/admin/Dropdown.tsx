import { ChevronDown } from 'lucide-react';
import { useEffect, useRef, useState, type FocusEvent, type KeyboardEvent } from 'react';
import { CONTROL, TEXT_SIZE } from './typography';

export interface DropdownOption {
  value: string;
  label: string;
}

interface DropdownProps {
  /** The id of the button: the field's `<label htmlFor>` points at it, and a problem with the
   * field takes the focus to it. */
  id: string;
  /** The id of the field's label, which names the button and the list. */
  labelledBy: string;
  value: string;
  /** Every option, the empty one ("elegí…") included when the field offers it. */
  options: DropdownOption[];
  /** Called only when the person picks another value, like a native list. */
  onChange: (value: string) => void;
  describedBy?: string;
  /** The field has a problem: the frame takes the attention color. */
  invalid?: boolean;
}

// The box of every control (`typography.ts`) with room for its arrow, without the phone's own look,
// and the attention border while it is wrong.
const BUTTON = `${CONTROL} appearance-none pr-9 text-left aria-[invalid=true]:border-falta`;
// Under the button and as wide as it, so it never pushes the page sideways on a phone.
const LIST = `absolute top-full right-0 left-0 z-20 mt-1 flex max-h-64 flex-col gap-0.5 overflow-y-auto rounded-card border-hard border-line bg-card p-1 shadow-hard outline-none ${TEXT_SIZE}`;

function initial(text: string): string {
  return text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().charAt(0);
}

/** A list to choose from in the web's own font, size and look, like the calendar (J2-16): on an
 * iPhone a native `<select>` opens the system's menu, which cannot be styled. A button that says
 * what is chosen and opens a listbox under it (the button + listbox pattern): a tap or the arrows
 * open it, the arrows, Home, End and a first letter move, Enter, Space or a tap pick, Escape or a
 * tap outside close it, and the focus goes back to the button. Inside a disabled fieldset the
 * button is disabled too, as a native list would be. */
export function Dropdown({ id, labelledBy, value, options, onChange, describedBy, invalid }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const root = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const list = useRef<HTMLUListElement>(null);
  const listId = `${id}-lista`;
  const optionId = (index: number) => `${id}-opcion-${index}`;
  const chosen = Math.max(0, options.findIndex((o) => o.value === value));
  const current = options.find((o) => o.value === value);

  useEffect(() => {
    if (open) list.current?.focus({ preventScroll: true });
  }, [open]);

  useEffect(() => {
    // The option the arrows reached stays in sight in a long list (jsdom has no `scrollIntoView`).
    if (open) document.getElementById(`${id}-opcion-${active}`)?.scrollIntoView?.({ block: 'nearest' });
  }, [open, active, id]);

  useEffect(() => {
    if (!open) return;
    function outside(event: Event) {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener('pointerdown', outside);
    return () => document.removeEventListener('pointerdown', outside);
  }, [open]);

  function show(index: number) {
    setActive(index);
    setOpen(true);
  }

  function close() {
    setOpen(false);
    button.current?.focus({ preventScroll: true });
  }

  function pick(index: number) {
    const option = options[index];
    if (option && option.value !== value) onChange(option.value);
    close();
  }

  function onButtonKey(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
    event.preventDefault();
    show(chosen);
  }

  function onListKey(event: KeyboardEvent<HTMLUListElement>) {
    const last = options.length - 1;
    let next: number | null = null;
    if (event.key === 'ArrowDown') next = Math.min(last, active + 1);
    else if (event.key === 'ArrowUp') next = Math.max(0, active - 1);
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = last;
    else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      pick(active);
      return;
    } else if (event.key === 'Escape') {
      event.preventDefault();
      close();
      return;
    } else if (event.key === 'Tab') {
      setOpen(false);
      return;
    } else if (event.key.length === 1 && /\p{L}|\p{N}/u.test(event.key)) {
      const letter = initial(event.key);
      const after = [...options.slice(active + 1), ...options.slice(0, active + 1)];
      const found = after.find((o) => initial(o.label) === letter);
      if (found) next = options.indexOf(found);
    }
    if (next === null) return;
    event.preventDefault();
    setActive(next);
  }

  /** The focus left the list for something outside it (not a tap, which `outside` sees). A
   * blur to nowhere is a tap: on iOS a tapped button takes no focus, and closing here would let
   * the button's own click open the list again. */
  function onListBlur(event: FocusEvent<HTMLUListElement>) {
    const next = event.relatedTarget as Node | null;
    if (next && !root.current?.contains(next)) setOpen(false);
  }

  return (
    <div ref={root} className="relative min-w-0 max-w-full">
      <button
        ref={button}
        id={id}
        type="button"
        value={value}
        className={BUTTON}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        aria-labelledby={`${labelledBy} ${id}`}
        aria-describedby={describedBy}
        aria-invalid={invalid ? true : undefined}
        onClick={(event) => {
          // A disabled fieldset (the form while it sends) leaves it closed, also where a click
          // still arrives.
          if (event.currentTarget.matches(':disabled')) return;
          if (open) setOpen(false);
          else show(chosen);
        }}
        onKeyDown={onButtonKey}
      >
        <span className="block min-w-0 wrap-break-word">{current?.label ?? ''}</span>
        <ChevronDown
          aria-hidden="true"
          size={16}
          strokeWidth={2}
          className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-ink-dim"
        />
      </button>
      {open && (
        <ul
          ref={list}
          id={listId}
          role="listbox"
          tabIndex={-1}
          aria-labelledby={labelledBy}
          aria-activedescendant={optionId(active)}
          className={LIST}
          onKeyDown={onListKey}
          onBlur={onListBlur}
        >
          {options.map((option, index) => {
            const selected = option.value === value;
            return (
              <li
                key={option.value}
                id={optionId(index)}
                role="option"
                aria-selected={selected}
                data-value={option.value}
                className={`min-w-0 cursor-pointer rounded-card px-2 py-1.5 wrap-break-word ${index === active ? 'bg-line-soft' : ''} ${selected ? 'font-bold text-ink' : 'text-ink-soft'}`}
                onMouseMove={() => setActive(index)}
                onClick={() => pick(index)}
              >
                {option.label}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
