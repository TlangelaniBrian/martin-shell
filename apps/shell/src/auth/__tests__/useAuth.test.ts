// @vitest-environment jsdom
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { clearUser, authStore } from '@martin/common'

// Mock apiFetch and router
vi.mock('@martin/common', async (importOriginal) => {
    const actual = await importOriginal<typeof import('@martin/common')>()
    return {
        ...actual,
        apiFetch: vi.fn(),
    }
})

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
    useRouter: () => ({ push: mockPush }),
}))

describe('useAuth', () => {
    beforeEach(() => {
        clearUser()
        mockPush.mockReset()
        vi.resetAllMocks()
    })

    it('bootstrap: sets user when /users/me succeeds', async () => {
        const { apiFetch } = await import('@martin/common')
        vi.mocked(apiFetch).mockResolvedValueOnce({
            id: '1', email: 'a@b.com', is_verified: true, role: 'member',
        })
        const { useAuth } = await import('../useAuth.js')
        const { bootstrap } = useAuth()
        await bootstrap()
        expect(authStore.state.user?.email).toBe('a@b.com')
    })

    it('bootstrap: clears user when /users/me fails', async () => {
        const { apiFetch } = await import('@martin/common')
        vi.mocked(apiFetch).mockRejectedValueOnce({ status: 401, detail: 'Unauthorized' })
        const { useAuth } = await import('../useAuth.js')
        const { bootstrap } = useAuth()
        await bootstrap()
        expect(authStore.state.user).toBeNull()
        expect(authStore.state.loading).toBe(false)
    })

    it('signIn: sets user and redirects on success', async () => {
        const { apiFetch } = await import('@martin/common')
        // login returns nothing useful (204), then /users/me returns user
        vi.mocked(apiFetch)
            .mockResolvedValueOnce(undefined) // POST /auth/login
            .mockResolvedValueOnce({ id: '2', email: 'x@y.com', is_verified: true, role: 'member' }) // GET /users/me
        const { useAuth } = await import('../useAuth.js')
        const { signIn } = useAuth()
        await signIn('x@y.com', 'pass')
        expect(authStore.state.user?.email).toBe('x@y.com')
        expect(mockPush).toHaveBeenCalledWith('/')
    })

    it('signOut: clears user and redirects to /sign-in', async () => {
        const { apiFetch, setUser } = await import('@martin/common')
        setUser({ id: '1', email: 'a@b.com', is_verified: true, role: 'member' })
        vi.mocked(apiFetch).mockResolvedValueOnce(undefined)
        const { useAuth } = await import('../useAuth.js')
        const { signOut } = useAuth()
        await signOut()
        expect(authStore.state.user).toBeNull()
        expect(mockPush).toHaveBeenCalledWith('/sign-in')
    })

    it('forgotPassword: calls /auth/forgot-password with email', async () => {
        const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
            new Response(null, { status: 202 })
        )
        const { useAuth } = await import('../useAuth.js')
        const { forgotPassword } = useAuth()
        await forgotPassword('a@b.com')
        expect(fetchSpy).toHaveBeenCalledWith(
            expect.stringContaining('/auth/forgot-password'),
            expect.objectContaining({ method: 'POST' })
        )
        fetchSpy.mockRestore()
    })
})
