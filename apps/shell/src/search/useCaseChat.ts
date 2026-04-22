import { ref } from 'vue'
import { apiFetch, isApiError } from '@martin/common'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export function useCaseChat(caseId: number) {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function send(message: string): Promise<void> {
    error.value = null
    messages.value.push({ role: 'user', content: message })
    loading.value = true

    const history = messages.value.slice(0, -1)

    try {
      const { reply } = await apiFetch<{ reply: string }>(`/cases/${caseId}/chat`, {
        method: 'POST',
        body: JSON.stringify({ message, history }),
      })
      messages.value.push({ role: 'assistant', content: reply })
    } catch (err) {
      error.value = isApiError(err) ? err.detail : 'Something went wrong'
    } finally {
      loading.value = false
    }
  }

  return { messages, loading, error, send }
}
