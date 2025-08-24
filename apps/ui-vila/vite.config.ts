import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/hydra-agency/' : '/',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        demo: resolve(__dirname, 'demo/index.html'),
        equipe: resolve(__dirname, 'equipe/index.html'),
        contato: resolve(__dirname, 'contato/index.html'),
        debug: resolve(__dirname, 'debug/index.html'),
      },
    },
  },
}));
