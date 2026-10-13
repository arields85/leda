import { fireEvent, render, screen, within } from '@testing-library/react';
import { useState } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { Dropdown, type DropdownOption } from './Dropdown';
import { CONTROL, TEXT_SIZE } from './typography';

const OPTIONS: DropdownOption[] = [
  { value: '', label: 'elegí a una persona' },
  { value: 'm-lucas', label: 'Lucas · Infraestructura · sin conectar' },
  { value: 'm-marcos', label: 'Marcos · Automatización' },
  { value: 'm-ismael', label: 'Ismael · Automatización' },
];

/** A field like the load form's: its label, the list, and something else to tap. */
function Field({ onChange = () => {}, start = '' }: { onChange?: (value: string) => void; start?: string }) {
  const [value, setValue] = useState(start);
  return (
    <div>
      <label id="f-quien-label" htmlFor="f-quien">
        Quién la hace
      </label>
      <Dropdown
        id="f-quien"
        labelledBy="f-quien-label"
        value={value}
        options={OPTIONS}
        onChange={(next) => {
          setValue(next);
          onChange(next);
        }}
        describedBy="f-quien-error"
      />
      <p id="f-quien-error">Elegí quién la hace.</p>
      <button type="button">afuera</button>
    </div>
  );
}

const button = () => screen.getByLabelText('Quién la hace', { selector: 'button' });
const list = () => screen.getByRole('listbox');
const active = () => document.getElementById(list().getAttribute('aria-activedescendant') ?? '');

describe('Dropdown', () => {
  it('is a button that says what is chosen, labelled by the field, with the form text and box', () => {
    render(<Field start="m-marcos" />);
    const b = button();
    expect(b).toHaveAttribute('aria-haspopup', 'listbox');
    expect(b).toHaveAttribute('aria-expanded', 'false');
    expect(b).toHaveAttribute('aria-describedby', 'f-quien-error');
    expect(b).toHaveValue('m-marcos');
    expect(b).toHaveTextContent('Marcos · Automatización');
    expect(b).toHaveClass(...CONTROL.split(' '), ...TEXT_SIZE.split(' '), 'appearance-none');
    // Closed, nothing of the list is there.
    expect(screen.queryByRole('listbox')).toBeNull();
  });

  it('opens on a tap, shows every option with the chosen one marked, and picks with a tap', () => {
    const onChange = vi.fn();
    render(<Field onChange={onChange} />);
    fireEvent.click(button());
    expect(button()).toHaveAttribute('aria-expanded', 'true');
    expect(list()).toHaveAttribute('aria-labelledby', 'f-quien-label');
    expect(list()).toHaveFocus();
    const options = within(list()).getAllByRole('option');
    expect(options.map((o) => o.textContent)).toEqual(OPTIONS.map((o) => o.label));
    expect(options[0]).toHaveAttribute('aria-selected', 'true');
    expect(options[1]).toHaveAttribute('aria-selected', 'false');
    // A long option wraps instead of pushing the page sideways on a phone.
    expect(options[1]).toHaveClass('wrap-break-word');
    expect(list()).toHaveClass('left-0', 'right-0');
    fireEvent.click(options[2]);
    expect(onChange).toHaveBeenCalledWith('m-marcos');
    expect(screen.queryByRole('listbox')).toBeNull();
    expect(button()).toHaveValue('m-marcos');
    expect(button()).toHaveFocus();
  });

  it('picking what was already chosen changes nothing, like a native list', () => {
    const onChange = vi.fn();
    render(<Field onChange={onChange} start="m-lucas" />);
    fireEvent.click(button());
    fireEvent.click(within(list()).getByRole('option', { name: 'Lucas · Infraestructura · sin conectar' }));
    expect(onChange).not.toHaveBeenCalled();
    expect(screen.queryByRole('listbox')).toBeNull();
  });

  it('works with the keyboard: arrows open and move, Enter and Space pick, Home and End jump', () => {
    const onChange = vi.fn();
    render(<Field onChange={onChange} start="m-lucas" />);
    fireEvent.keyDown(button(), { key: 'ArrowDown' });
    // It opens on the chosen one.
    expect(active()).toHaveTextContent('Lucas');
    fireEvent.keyDown(list(), { key: 'ArrowDown' });
    expect(active()).toHaveTextContent('Marcos');
    fireEvent.keyDown(list(), { key: 'ArrowUp' });
    fireEvent.keyDown(list(), { key: 'ArrowUp' });
    fireEvent.keyDown(list(), { key: 'ArrowUp' });
    expect(active()).toHaveTextContent('elegí a una persona');
    fireEvent.keyDown(list(), { key: 'End' });
    expect(active()).toHaveTextContent('Ismael');
    fireEvent.keyDown(list(), { key: 'Enter' });
    expect(onChange).toHaveBeenLastCalledWith('m-ismael');
    expect(screen.queryByRole('listbox')).toBeNull();
    expect(button()).toHaveFocus();
    fireEvent.keyDown(button(), { key: 'ArrowUp' });
    fireEvent.keyDown(list(), { key: 'Home' });
    fireEvent.keyDown(list(), { key: ' ' });
    expect(onChange).toHaveBeenLastCalledWith('');
  });

  it('a letter goes to the next option that starts with it', () => {
    render(<Field />);
    fireEvent.click(button());
    fireEvent.keyDown(list(), { key: 'm' });
    expect(active()).toHaveTextContent('Marcos');
    fireEvent.keyDown(list(), { key: 'i' });
    expect(active()).toHaveTextContent('Ismael');
  });

  it('Escape closes it without changing anything and gives the focus back to the button', () => {
    const onChange = vi.fn();
    render(<Field onChange={onChange} start="m-lucas" />);
    fireEvent.click(button());
    fireEvent.keyDown(list(), { key: 'ArrowDown' });
    fireEvent.keyDown(list(), { key: 'Escape' });
    expect(screen.queryByRole('listbox')).toBeNull();
    expect(button()).toHaveAttribute('aria-expanded', 'false');
    expect(button()).toHaveFocus();
    expect(button()).toHaveValue('m-lucas');
    expect(onChange).not.toHaveBeenCalled();
  });

  it('a tap outside closes it without changing anything; a second tap on the button too', () => {
    const onChange = vi.fn();
    render(<Field onChange={onChange} />);
    fireEvent.click(button());
    // A tap inside the list does not close it.
    fireEvent.pointerDown(list());
    expect(list()).toBeInTheDocument();
    fireEvent.pointerDown(screen.getByRole('button', { name: 'afuera' }));
    expect(screen.queryByRole('listbox')).toBeNull();
    fireEvent.click(button());
    fireEvent.click(button());
    expect(screen.queryByRole('listbox')).toBeNull();
    expect(onChange).not.toHaveBeenCalled();
  });

  it('marks a problem on its frame and cannot be opened while disabled', () => {
    render(
      <fieldset disabled>
        <label id="l" htmlFor="d">
          Objetivo
        </label>
        <Dropdown id="d" labelledBy="l" value="" options={OPTIONS} onChange={() => {}} invalid />
      </fieldset>,
    );
    const b = screen.getByLabelText('Objetivo', { selector: 'button' });
    expect(b).toHaveAttribute('aria-invalid', 'true');
    expect(b).toBeDisabled();
    fireEvent.click(b);
    expect(screen.queryByRole('listbox')).toBeNull();
  });
});
