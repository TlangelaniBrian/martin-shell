export type AIProvider = 'anthropic' | 'openai' | 'google' | 'deepseek'

export interface AISettingsRead {
  provider: AIProvider
  model: string | null
  anthropic_configured: boolean
  openai_configured: boolean
  google_configured: boolean
  deepseek_configured: boolean
}

export interface AISettingsUpdate {
  provider?: AIProvider
  model?: string
  anthropic_api_key?: string
  openai_api_key?: string
  google_api_key?: string
  deepseek_api_key?: string
}

export const PROVIDER_META: Record<AIProvider, { label: string; keyField: keyof AISettingsUpdate; configuredField: keyof AISettingsRead }> = {
  anthropic: { label: 'Anthropic (Claude)', keyField: 'anthropic_api_key', configuredField: 'anthropic_configured' },
  openai:    { label: 'OpenAI (GPT)',        keyField: 'openai_api_key',    configuredField: 'openai_configured' },
  google:    { label: 'Google (Gemini)',     keyField: 'google_api_key',    configuredField: 'google_configured' },
  deepseek:  { label: 'DeepSeek',           keyField: 'deepseek_api_key',  configuredField: 'deepseek_configured' },
}
