export type ApiError = { status: number; detail: string }

export function isApiError(err: unknown): err is ApiError {
  return (
    typeof err === 'object' &&
    err !== null &&
    'status' in err &&
    'detail' in err
  )
}

const API_URL = import.meta.env.VITE_API_URL as string

let refreshPromise: Promise<boolean> | null = null

async function tryRefresh(): Promise<boolean> {
  if (refreshPromise) return refreshPromise
  refreshPromise = fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })
    .then((res) => res.ok)
    .catch(() => false)
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}

async function _apiFetch<T>(path: string, options: RequestInit, retry: boolean): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (res.status === 401 && !retry) {
    const refreshed = await tryRefresh()
    if (refreshed) {
      return _apiFetch(path, options, true)
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

export async function apiFetch<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  return _apiFetch(path, options, false)
}
