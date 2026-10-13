import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});

// jsdom has no layout and does not implement window.scrollTo: a quiet stub that tests can spy on.
window.scrollTo = (() => {}) as typeof window.scrollTo;
