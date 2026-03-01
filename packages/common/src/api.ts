export type ApiError = { status: number; detail: string }

const API_URL = import.meta.env.VITE_API_URL as string

let isRefreshing = false

async function tryRefresh(): Promise<boolean> {
  if (isRefreshing) return false
  isRefreshing = true
  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    })
    return res.ok
  } catch {
    return false
  } finally {
    isRefreshing = false
  }
}

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {},
  _retry = false,
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (res.status === 401 && !_retry) {
    const refreshed = await tryRefresh()
    if (refreshed) {
      return apiFetch(path, options, true)
    }
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('session:expired'))
    }
    throw { status: 401, detail: 'Session expired' } satisfies ApiError
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw { status: res.status, detail: error.detail } satisfies ApiError
  }

  return res.json() as Promise<T>
}
