import pluginVue from 'eslint-plugin-vue'
import base from './base.js'

export default [
  ...base,
  ...pluginVue.configs['flat/recommended'],
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/component-api-style': ['error', ['script-setup']],
    },
  },
]
