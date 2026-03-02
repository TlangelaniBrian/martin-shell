import { pluginModuleFederation } from '@module-federation/rsbuild-plugin'
import { defineConfig } from '@rsbuild/core'
import { pluginVue } from '@rsbuild/plugin-vue'

export default defineConfig({
  html: { title: 'Martin', template: './index.html' },
  source: { entry: { index: './src/main.ts' } },
  dev: { lazyCompilation: false },
  plugins: [
    pluginVue(),
    pluginModuleFederation({
      name: 'martin_shell',
      remotes: {
        martin_workspace: `martin_workspace@${process.env.WORKSPACE_URL ?? 'http://localhost:3001'}/mf-manifest.json`,
      },
      dts: false,
      shared: {
        vue: { singleton: true, eager: true },
        'vue-router': { singleton: true, eager: true },
      },
    }),
  ],
})
