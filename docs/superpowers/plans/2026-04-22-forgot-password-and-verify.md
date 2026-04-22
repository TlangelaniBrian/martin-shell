# Forgot Password + Email Verify Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a forgot-password page (sends reset link) and an email verification page (handles the token from the verification email), matching the existing Next.js implementations.

**Architecture:** Two new page components under `apps/shell/src/auth/`. Both are public-only routes. They call fastapi-users endpoints directly via `apiFetch`. `ForgotPasswordPage.vue` posts to `POST /auth/forgot-password`. `VerifyPage.vue` reads a `?token=` query param and posts to `POST /auth/verify`. Both show a styled confirmation state on success. Both use an `AuthCard` layout wrapper (created in this plan) to avoid repeating the card shell.

**Tech Stack:** Vue 3 Composition API, apiFetch from @martin/common, lucide-vue-next, Tailwind CSS v4 design tokens, vue-router

---

### Task 1: Create AuthCard layout component

**Files:**
- Create: `apps/shell/src/components/AuthCard.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/components/AuthCard.vue -->
<script setup lang="ts">
defineProps<{ class?: string }>()
</script>

<template>
  <main class="flex min-h-screen items-center justify-center bg-bg px-4">
    <div
      :class="['w-full max-w-sm rounded-xl border border-border bg-surface shadow-md p-8', $props.class ?? 'space-y-6']"
    >
      <slot />
    </div>
  </main>
</template>
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/components/AuthCard.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add AuthCard layout wrapper"
```

---

### Task 2: Add apiFetch for forgot-password to useAuth composable

**Files:**
- Modify: `apps/shell/src/auth/useAuth.ts`

The existing `useAuth.ts` only has `bootstrap`, `signIn`, `signUp`, `signOut`. Add `forgotPassword`.

- [ ] **Step 1: Add forgotPassword to useAuth.ts**

In `apps/shell/src/auth/useAuth.ts`, inside the `useAuth` function body, add before the `return` statement:

```typescript
async function forgotPassword(email: string): Promise<void> {
  // fastapi-users returns 202 regardless of whether the email exists (prevents enumeration)
  await fetch(`${import.meta.env.VITE_API_URL}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
}
```

Update the `return` statement to include `forgotPassword`:

```typescript
return { bootstrap, signIn, signUp, signOut, forgotPassword }
```

- [ ] **Step 2: Write test**

Add to `apps/shell/src/auth/__tests__/useAuth.test.ts`, inside the existing `describe('useAuth')` block:

```typescript
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
```

- [ ] **Step 3: Run tests**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell && pnpm test
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/auth/useAuth.ts apps/shell/src/auth/__tests__/useAuth.test.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add forgotPassword to useAuth"
```

---

### Task 3: Create ForgotPasswordPage.vue

**Files:**
- Create: `apps/shell/src/auth/ForgotPasswordPage.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/auth/ForgotPasswordPage.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Mail } from 'lucide-vue-next'
import AuthCard from '../components/AuthCard.vue'
import { useAuth } from './useAuth.js'

const { forgotPassword } = useAuth()

const email = ref('')
const sent = ref(false)
const error = ref<string | null>(null)
const loading = ref(false)

async function onSubmit() {
  error.value = null
  loading.value = true
  try {
    await forgotPassword(email.value)
    sent.value = true
  } catch {
    error.value = 'Something went wrong. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthCard v-if="sent" class="space-y-4 text-center">
    <Mail :size="36" class="text-primary mx-auto" />
    <h1 class="text-xl font-semibold text-fg">Check your email</h1>
    <p class="text-sm text-fg-muted">
      If an account with that address exists, we sent a password reset link to
      <span class="font-medium text-fg">{{ email }}</span>.
    </p>
    <RouterLink
      to="/sign-in"
      class="block text-sm text-primary hover:text-primary-hover transition-colors font-medium"
    >
      Back to sign in →
    </RouterLink>
  </AuthCard>

  <AuthCard v-else>
    <div class="space-y-1">
      <h1 class="text-2xl font-semibold text-fg">Reset password</h1>
      <p class="text-sm text-fg-muted">Enter your email and we'll send you a reset link.</p>
    </div>

    <form @submit.prevent="onSubmit" class="space-y-4">
      <div
        v-if="error"
        class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2"
      >
        {{ error }}
      </div>

      <div class="space-y-1.5">
        <label for="email" class="text-sm font-medium text-fg">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          placeholder="you@lawfirm.co.za"
          required
          maxlength="254"
          autocomplete="email"
          class="w-full px-3 py-2 rounded-md border border-border bg-bg text-fg placeholder:text-fg-muted focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm"
        />
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2.5 rounded-md bg-primary text-primary-fg font-medium text-sm hover:bg-primary-hover transition-colors disabled:opacity-60"
      >
        {{ loading ? 'Sending…' : 'Send reset link' }}
      </button>
    </form>

    <p class="text-sm text-center text-fg-muted">
      <RouterLink
        to="/sign-in"
        class="text-primary hover:text-primary-hover transition-colors font-medium"
      >
        ← Back to sign in
      </RouterLink>
    </p>
  </AuthCard>
</template>
```

- [ ] **Step 2: Register route in router.ts**

Add to the routes array (after `/sign-up`):

```typescript
{
  path: '/auth/forgot-password',
  component: () => import('./auth/ForgotPasswordPage.vue'),
},
```

Add `'/auth/forgot-password'` to the `PUBLIC_ONLY` array:

```typescript
const PUBLIC_ONLY = ['/sign-in', '/sign-up', '/auth/callback', '/auth/forgot-password']
```

- [ ] **Step 3: Add "Forgot password?" link to SignInPage.vue**

In `apps/shell/src/auth/SignInPage.vue`, find the password input section and add the link above it. Replace the password `<div>` block:

```vue
<div>
  <div class="flex items-center justify-between mb-1">
    <span class="text-sm font-medium text-fg">Password</span>
    <RouterLink to="/auth/forgot-password" class="text-xs text-primary hover:text-primary-hover transition-colors">
      Forgot password?
    </RouterLink>
  </div>
  <Input
    v-model="form.password"
    type="password"
    placeholder="Password"
    :disabled="submitting"
  />
</div>
```

Add `RouterLink` to the imports in `SignInPage.vue`:

```vue
<script setup lang="ts">
import { reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { useAuth } from "./useAuth.js";
import { isApiError } from "@martin/common";
import { Card, Input, Button } from "@martin/components";
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/auth/ForgotPasswordPage.vue apps/shell/src/router.ts apps/shell/src/auth/SignInPage.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add forgot-password page and link from sign-in"
```

---

### Task 4: Create VerifyPage.vue

**Files:**
- Create: `apps/shell/src/auth/VerifyPage.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/auth/VerifyPage.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Loader2, CheckCircle, XCircle } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
import AuthCard from '../components/AuthCard.vue'

type Status = 'loading' | 'success' | 'error'

const router = useRouter()
const route = useRoute()
const status = ref<Status>('loading')
let redirectTimer: ReturnType<typeof setTimeout> | null = null

onMounted(async () => {
  const token = route.query.token as string | undefined
  if (!token) {
    status.value = 'error'
    return
  }
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })
    if (res.ok) {
      status.value = 'success'
      redirectTimer = setTimeout(() => router.push('/sign-in'), 2500)
    } else {
      status.value = 'error'
    }
  } catch {
    status.value = 'error'
  }
})

onUnmounted(() => {
  if (redirectTimer) clearTimeout(redirectTimer)
})
</script>

<template>
  <AuthCard class="space-y-4 text-center">
    <template v-if="status === 'loading'">
      <Loader2 :size="32" class="animate-spin text-primary mx-auto" />
      <p class="text-sm text-fg-muted">Verifying your email…</p>
    </template>

    <template v-else-if="status === 'success'">
      <CheckCircle :size="32" class="text-green-500 mx-auto" />
      <h1 class="text-xl font-semibold text-fg">Email verified</h1>
      <p class="text-sm text-fg-muted">Redirecting you to sign in…</p>
    </template>

    <template v-else>
      <XCircle :size="32" class="text-red-500 mx-auto" />
      <h1 class="text-xl font-semibold text-fg">Verification failed</h1>
      <p class="text-sm text-fg-muted">The link may have expired or already been used.</p>
      <RouterLink
        to="/sign-in"
        class="block text-sm text-primary hover:text-primary-hover transition-colors font-medium"
      >
        Back to sign in →
      </RouterLink>
    </template>
  </AuthCard>
</template>
```

- [ ] **Step 2: Register route in router.ts**

Add to the routes array:

```typescript
{
  path: '/auth/verify',
  component: () => import('./auth/VerifyPage.vue'),
},
```

Add `'/auth/verify'` to `PUBLIC_ONLY`:

```typescript
const PUBLIC_ONLY = ['/sign-in', '/sign-up', '/auth/callback', '/auth/forgot-password', '/auth/verify']
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/auth/VerifyPage.vue apps/shell/src/router.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add email verify page"
```

---

### Task 5: Type-check

- [ ] **Step 1: Run type check**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell && pnpm type-check
```

Expected: no errors.
