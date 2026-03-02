// @vitest-environment jsdom
import { describe, it, expect, beforeEach } from 'vitest'

describe('authStore', () => {
  beforeEach(async () => {
    const mod = await import('../auth-store.js')
    mod.clearUser()
  })

  it('starts with no user (null)', async () => {
    const { authStore } = await import('../auth-store.js')
    expect(authStore.state.user).toBeNull()
  })

  it('setUser stores role correctly', async () => {
    const { setUser, authStore } = await import('../auth-store.js')
    setUser({ id: '1', email: 'admin@example.com', is_verified: true, role: 'admin' })
    expect(authStore.state.user?.role).toBe('admin')
  })

  it('setUser updates the user in store', async () => {
    const { setUser, authStore } = await import('../auth-store.js')
    setUser({ id: '1', email: 'test@example.com', is_verified: true, role: 'member' })
    expect(authStore.state.user?.email).toBe('test@example.com')
    expect(authStore.state.user?.id).toBe('1')
    expect(authStore.state.user?.is_verified).toBe(true)
    expect(authStore.state.user?.role).toBe('member')
  })

  it('clearUser resets user to null', async () => {
    const { setUser, clearUser, authStore } = await import('../auth-store.js')
    setUser({ id: '1', email: 'test@example.com', is_verified: true, role: 'member' })
    clearUser()
    expect(authStore.state.user).toBeNull()
  })
})
