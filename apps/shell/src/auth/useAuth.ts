import { apiFetch, isApiError, clearUser, setUser, setLoading } from '@martin/common'
import type { User } from '@martin/common'
import { useRouter } from 'vue-router'

const LOGIN_URL = '/auth/login'
const ME_URL = '/users/me'
const LOGOUT_URL = '/auth/logout'

export function useAuth() {
    const router = useRouter()

    async function bootstrap(): Promise<void> {
        setLoading(true)
        try {
            const user = await apiFetch<User>(ME_URL)
            setUser(user)
        } catch (err) {
            if (isApiError(err) && (err.status === 401 || err.status === 403)) {
                clearUser()
            } else {
                clearUser()
                throw err
            }
        }
    }

    async function signIn(email: string, password: string): Promise<void> {
        const body = new URLSearchParams({ username: email, password })
        await apiFetch(LOGIN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body.toString(),
        })
        const user = await apiFetch<User>(ME_URL)
        setUser(user)
        await router.push('/')
    }

    async function signUp(
        email: string,
        password: string,
    ): Promise<{ requiresVerification: true }> {
        await apiFetch(
            '/auth/register',
            { method: 'POST', body: JSON.stringify({ email, password }) },
        )
        return { requiresVerification: true }
    }

    async function signOut(): Promise<void> {
        try {
            await apiFetch(LOGOUT_URL, { method: 'POST' })
        } finally {
            clearUser()
            await router.push('/sign-in')
        }
    }

    async function forgotPassword(email: string): Promise<void> {
        // fastapi-users returns 202 regardless of whether the email exists (prevents enumeration)
        await fetch(`${import.meta.env.VITE_API_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        })
    }

    return { bootstrap, signIn, signUp, signOut, forgotPassword }
}
