import { pluginModuleFederation } from '@module-federation/rsbuild-plugin'
import { defineConfig, loadEnv } from '@rsbuild/core'
import { pluginVue } from '@rsbuild/plugin-vue'

const { parsed } = loadEnv({ prefixes: ['VITE_', 'PUBLIC_'] })

export default defineConfig({
  html: { title: 'Martin', template: './index.html' },
  source: {
    entry: { index: './src/main.ts' },
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(parsed.VITE_API_URL ?? ''),
    },
  },
  dev: { lazyCompilation: false },
  server: {
    proxy: {
      '/auth': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/users': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/cases': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/search': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/briefcases': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/health': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  plugins: [
    pluginVue(),
    pluginModuleFederation({
      name: 'martin_shell',
      remotes: {
        martin_workspace: `martin_workspace@${process.env.WORKSPACE_URL ?? 'http://localhost:3001'}/mf-manifest.json`,
      },
      dts: false,
      shared: {
        vue: { singleton: true, eager: true, requiredVersion: '^3.5.0' },
        'vue-router': { singleton: true, eager: true, requiredVersion: '^4.0.0' },
        '@tanstack/vue-query': { singleton: true, eager: true, requiredVersion: '^5.0.0' },
      },
    }),
  ],
})
