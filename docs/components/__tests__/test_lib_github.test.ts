import { describe, it, expect } from 'vitest';
import { DocHarvestGithubData } from '@/lib/github';

describe('lib github alias', () => {
  it('should resolve', () => {
    expect(typeof DocHarvestGithubData).toBe('undefined'); // type-only import, but module should load
  });
});
