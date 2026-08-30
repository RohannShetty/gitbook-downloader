import { describe, it, expect } from 'vitest';

describe('infra smoke', () => {
  it('happy-dom + jest-dom matcher', () => {
    const el = document.createElement('div');
    el.textContent = 'hello world';
    expect(el).toHaveTextContent('hello world');
  });

  it('navigator.clipboard mock is wired', async () => {
    await navigator.clipboard.writeText('abc');
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('abc');
  });
});
