import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { TalkButton } from './TalkButton';

describe('TalkButton', () => {
  it('opens the chat with the team bot in Telegram', () => {
    render(<TalkButton href="https://t.me/LedaCoreWorkBot" />);
    const link = screen.getByRole('link', { name: '> consultar a leda' });
    expect(link).toHaveAttribute('href', 'https://t.me/LedaCoreWorkBot');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('is not shown when the space has no bot address', () => {
    const { container } = render(<TalkButton href={null} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('never links anywhere but Telegram', () => {
    const { container } = render(<TalkButton href="javascript:alert(1)" />);
    expect(container).toBeEmptyDOMElement();
  });
});
