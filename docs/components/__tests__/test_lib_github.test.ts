import { describe, it, expect } from 'vitest';
import * as githubModule from '@/lib/github';

describe('lib github alias', () => {
  it('should resolve', () => {
    expect(githubModule).toBeDefined();
  });
});
