import { describe, it, expect } from 'vitest';

describe('Test infrastructure', () => {
  it('should have vitest configured correctly', () => {
    expect(true).toBe(true);
  });

  it('should have navigator.clipboard mocked', () => {
    expect(navigator.clipboard).toBeDefined();
    expect(navigator.clipboard.writeText).toBeDefined();
    expect(navigator.clipboard.readText).toBeDefined();
  });
});
