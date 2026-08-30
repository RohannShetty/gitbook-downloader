import { defineConfig } from 'vitest/config';
import { resolve } from 'path';
import react from '@vitejs/plugin-react';

// Note: Using Next.js path aliases
// @/* → ./*
// @/components/* → ./components/*
// @/data/* → ./data/*
// @/lib/* → ./lib/*

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./test/setup.ts'],
    include: ['**/*.test.{ts,tsx}'],
    exclude: ['node_modules/**', '.next/**', 'dist/**', 'out/**'],
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary', 'html'],
      exclude: [
        'node_modules/**',
        'test/**',
        '**/*.d.ts',
        '**/*.config.*',
        '**/*.test.*',
      ],
    },
  },
  resolve: {
    alias: [
      { find: '@/', replacement: resolve(__dirname, '.').split('\\').join('/') + '/' },
    ],
  },
});
