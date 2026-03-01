// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('apiFetch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.resetModules()
  })

  it('calls the correct URL with credentials: include', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ data: 'ok' }),
    })
    const { apiFetch } = await import('../api.js')
    await apiFetch('/test')
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/test',
      expect.objectContaining({ credentials: 'include' })
    )
  })

  it('retries once on 401 after successful refresh', async () => {
    mockFetch
      .mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, status: 200 }) // refresh
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ data: 'retried' }) })
    const { apiFetch } = await import('../api.js')
    const result = await apiFetch('/protected')
    expect(result).toEqual({ data: 'retried' })
    expect(mockFetch).toHaveBeenCalledTimes(3)
  })

  it('dispatches session:expired CustomEvent when refresh fails', async () => {
    const dispatchSpy = vi.spyOn(window, 'dispatchEvent')
    mockFetch
      .mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: false, status: 401 }) // refresh also fails
    const { apiFetch } = await import('../api.js')
    await expect(apiFetch('/protected')).rejects.toMatchObject({ status: 401 })
    expect(dispatchSpy).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'session:expired' })
    )
  })

  it('throws ApiError with status and detail on non-401 error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Not found' }),
    })
    const { apiFetch } = await import('../api.js')
    await expect(apiFetch('/missing')).rejects.toMatchObject({
      status: 404,
      detail: 'Not found',
    })
  })
})
