// Import the configuration helper that understands both Vite and Vitest options.
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  // Configure the automated frontend test environment.
  test: {
    // Provide browser-like document and window objects inside Node
    environment: 'jsdom',
    // Load custom DOM assertions before each test suite
    setupFiles: './src/setupTests.ts',
  }
});

