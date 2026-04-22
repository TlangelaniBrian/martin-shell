import { ref, onMounted } from 'vue'
import { apiFetch } from '@martin/common'
import type { AISettingsRead, AISettingsUpdate, AIProvider } from '@martin/common'

const KEY_MAP: Record<AIProvider, keyof AISettingsUpdate> = {
  anthropic: 'anthropic_api_key',
  openai:    'openai_api_key',
  google:    'google_api_key',
  deepseek:  'deepseek_api_key',
}

const CONFIGURED_MAP: Record<AIProvider, keyof AISettingsRead> = {
  anthropic: 'anthropic_configured',
  openai:    'openai_configured',
  google:    'google_configured',
  deepseek:  'deepseek_configured',
}

export function useAISettings() {
  const settings = ref<AISettingsRead | null>(null)
  const loading = ref(true)
  const saving = ref(false)
  const saved = ref(false)
  const error = ref<string | null>(null)
  let savedTimer: ReturnType<typeof setTimeout> | null = null

  onMounted(async () => {
    try {
      settings.value = await apiFetch<AISettingsRead>('/ai-settings/')
    } catch {
      // silently ignore — user just won't see configured state
    } finally {
      loading.value = false
    }
  })

  async function saveSettings(provider: AIProvider, apiKey: string, modelOverride: string): Promise<void> {
    saving.value = true
    error.value = null
    saved.value = false
    try {
      const body: AISettingsUpdate = { provider }
      if (apiKey) (body as Record<string, string>)[KEY_MAP[provider]] = apiKey
      if (modelOverride) body.model = modelOverride
      settings.value = await apiFetch<AISettingsRead>('/ai-settings/', {
        method: 'PATCH',
        body: JSON.stringify(body),
      })
      if (savedTimer) clearTimeout(savedTimer)
      saved.value = true
      savedTimer = setTimeout(() => { saved.value = false }, 3000)
    } catch {
      error.value = 'Failed to save AI settings.'
    } finally {
      saving.value = false
    }
  }

  function isConfigured(provider: AIProvider): boolean {
    if (!settings.value) return false
    return settings.value[CONFIGURED_MAP[provider]] as boolean
  }

  return { settings, loading, saving, saved, error, saveSettings, isConfigured }
}
