// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@martin/common', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@martin/common')>()
  return { ...actual, apiFetch: vi.fn() }
})

describe('useCaseChat', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.resetModules()
  })

  it('send: appends user message, calls apiFetch, appends assistant reply', async () => {
    const { apiFetch } = await import('@martin/common')
    vi.mocked(apiFetch).mockResolvedValueOnce({ reply: 'It held that X.' })

    const { useCaseChat } = await import('../useCaseChat.js')
    const { messages, send, loading } = useCaseChat(42)

    const sendPromise = send('What was the ratio?')
    expect(loading.value).toBe(true)
    await sendPromise

    expect(loading.value).toBe(false)
    expect(messages.value).toHaveLength(2)
    expect(messages.value[0]).toEqual({ role: 'user', content: 'What was the ratio?' })
    expect(messages.value[1]).toEqual({ role: 'assistant', content: 'It held that X.' })
    expect(vi.mocked(apiFetch)).toHaveBeenCalledWith(
      '/cases/42/chat',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('send: sets error on API failure', async () => {
    const { apiFetch } = await import('@martin/common')
    vi.mocked(apiFetch).mockRejectedValueOnce({ status: 503, detail: 'AI not configured' })

    const { useCaseChat } = await import('../useCaseChat.js')
    const { send, error, loading } = useCaseChat(42)

    await send('Hello')

    expect(loading.value).toBe(false)
    expect(error.value).toBe('AI not configured')
  })

  it('send: passes history from prior messages', async () => {
    const { apiFetch } = await import('@martin/common')
    vi.mocked(apiFetch)
      .mockResolvedValueOnce({ reply: 'First reply.' })
      .mockResolvedValueOnce({ reply: 'Second reply.' })

    const { useCaseChat } = await import('../useCaseChat.js')
    const { send } = useCaseChat(7)

    await send('First question')
    await send('Second question')

    const secondCall = vi.mocked(apiFetch).mock.calls[1]
    const body = JSON.parse((secondCall[1] as RequestInit).body as string)
    expect(body.history).toHaveLength(2)
    expect(body.history[0]).toEqual({ role: 'user', content: 'First question' })
    expect(body.history[1]).toEqual({ role: 'assistant', content: 'First reply.' })
  })
})
