import { describe, it, expect } from 'vitest';
import { FAQ_ITEMS } from '@/data/showcaseData';

describe('relative alias resolution', () => {
  it('relative data import works', () => {
    expect(FAQ_ITEMS).toBeDefined();
    expect(FAQ_ITEMS.length).toBeGreaterThan(0);
  });
});
