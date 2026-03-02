import { Store } from '@tanstack/store'
import { useStore } from '@tanstack/vue-store'

export type UserRole = 'member' | 'admin'

export interface User {
  id: string
  email: string
  is_verified: boolean
  role: UserRole
}

interface AuthState {
  user: User | null
  loading: boolean
}

export const authStore = new Store<AuthState>({
  user: null,
  loading: true,
})

export function setUser(user: User): void {
  authStore.setState(() => ({ user, loading: false }))
}

export function clearUser(): void {
  authStore.setState(() => ({ user: null, loading: false }))
}

export function setLoading(loading: boolean): void {
  authStore.setState((s) => ({ ...s, loading }))
}

export function useAuthStore() {
  return useStore(authStore)
}
