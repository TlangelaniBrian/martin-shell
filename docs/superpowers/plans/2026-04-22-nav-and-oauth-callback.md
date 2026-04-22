# Nav Component + Google OAuth Callback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a persistent navigation bar to the shell and a Google OAuth callback route so users who sign in with Google land correctly.

**Architecture:** `AppNav.vue` sits in `App.vue` above `<RouterView>`. It reads auth state from TanStack Store (`useAuthStore`), shows Sign in / Sign up for guests and an avatar dropdown for authenticated users. The Google callback route (`/auth/callback/google`) is a tiny page that fires `auth:changed`-equivalent logic (bootstrap + redirect). `lucide-vue-next` is already installed in `apps/shell/package.json`.

**Tech Stack:** Vue 3 Composition API, TanStack Store, vue-router, lucide-vue-next, Tailwind CSS v4 design tokens

---

### Task 1: Verify lucide-vue-next is available

**Files:**
- Read: `apps/shell/package.json`

- [ ] **Step 1: Confirm the package is listed**

```bash
grep lucide-vue-next /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell/package.json
```

Expected output: `"lucide-vue-next": "^0.400.0"`

- [ ] **Step 2: Install deps if not already installed**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell && pnpm install
```

Expected: exits 0, no errors about missing packages.

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add -A && git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "chore: ensure deps installed"
```

---

### Task 2: Create AppNav component

**Files:**
- Create: `apps/shell/src/components/AppNav.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/components/AppNav.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { Search, BookOpen, ChevronDown, User } from 'lucide-vue-next'
import { useAuthStore } from '@martin/common'
import { useAuth } from '../auth/useAuth.js'

const auth = useAuthStore()
const router = useRouter()
const { signOut } = useAuth()

const dropdownOpen = ref(false)
const dropdownRef = ref<HTMLDivElement | null>(null)

function handleOutsideClick(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    dropdownOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onUnmounted(() => document.removeEventListener('mousedown', handleOutsideClick))

const initials = $computed(() => auth.user?.email?.[0]?.toUpperCase() ?? null)
</script>

<template>
  <nav class="sticky top-0 z-50 border-b border-border bg-surface/80 backdrop-blur-md">
    <div class="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
      <!-- Logo -->
      <RouterLink to="/" class="text-lg font-semibold tracking-tight text-fg">
        Martin
      </RouterLink>

      <!-- Nav links -->
      <div class="flex items-center gap-5">
        <RouterLink
          to="/search"
          class="flex items-center gap-1.5 text-sm text-fg-muted hover:text-fg transition-colors"
        >
          <Search :size="15" />
          Search
        </RouterLink>
        <RouterLink
          to="/briefcases"
          class="flex items-center gap-1.5 text-sm text-fg-muted hover:text-fg transition-colors"
        >
          <BookOpen :size="15" />
          Briefcases
        </RouterLink>
      </div>

      <!-- Auth slot -->
      <div class="flex items-center gap-2">
        <!-- Authenticated: avatar dropdown -->
        <div v-if="auth.user" ref="dropdownRef" class="relative">
          <button
            @click="dropdownOpen = !dropdownOpen"
            class="flex items-center gap-1 h-8 pl-1 pr-2 rounded-full bg-primary text-primary-fg text-sm font-medium"
            aria-label="User menu"
          >
            <span class="flex h-7 w-7 items-center justify-center rounded-full">
              <template v-if="initials">{{ initials }}</template>
              <User v-else :size="14" />
            </span>
            <ChevronDown
              :size="13"
              :class="['transition-transform', dropdownOpen ? 'rotate-180' : '']"
            />
          </button>

          <div
            v-if="dropdownOpen"
            class="absolute right-0 mt-2 w-44 rounded-lg border border-border bg-surface shadow-md overflow-hidden"
          >
            <div class="px-4 py-2.5 border-b border-border">
              <p class="text-xs text-fg-muted truncate">{{ auth.user.email }}</p>
            </div>
            <RouterLink
              to="/account"
              @click="dropdownOpen = false"
              class="block px-4 py-2 text-sm text-fg hover:bg-bg-subtle transition-colors"
            >
              Account
            </RouterLink>
            <button
              @click="signOut"
              class="w-full text-left px-4 py-2 text-sm text-fg hover:bg-bg-subtle transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>

        <!-- Guest: sign in / sign up -->
        <template v-else>
          <RouterLink
            to="/sign-in"
            class="text-sm px-3 py-1.5 rounded-md border border-border text-fg hover:bg-bg-subtle transition-colors"
          >
            Sign in
          </RouterLink>
          <RouterLink
            to="/sign-up"
            class="text-sm px-3 py-1.5 rounded-md bg-primary text-primary-fg hover:bg-primary-hover transition-colors"
          >
            Sign up
          </RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>
```

- [ ] **Step 2: Wire into App.vue — add Nav above RouterView, hide on auth pages**

Replace the entire `App.vue` template section:

```vue
<!-- apps/shell/src/App.vue -->
<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { useAuthStore, clearUser } from '@martin/common'
import { useAuth } from './auth/useAuth.js'
import AppNav from './components/AppNav.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { bootstrap } = useAuth()

const AUTH_ROUTES = ['/sign-in', '/sign-up', '/auth/']
const showNav = computed(() =>
  !AUTH_ROUTES.some((p) => route.path.startsWith(p))
)

function onSessionExpired() {
  clearUser()
  router.push('/sign-in')
}

onMounted(async () => {
  window.addEventListener('session:expired', onSessionExpired)
  await bootstrap()
})

onUnmounted(() => {
  window.removeEventListener('session:expired', onSessionExpired)
})
</script>

<template>
  <div v-if="auth.loading" class="flex h-screen items-center justify-center">
    <div class="h-8 w-8 animate-spin rounded-full border-4 border-border border-t-primary" />
  </div>
  <template v-else>
    <AppNav v-if="showNav" />
    <RouterView />
  </template>
</template>
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/components/AppNav.vue apps/shell/src/App.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add AppNav with auth-aware dropdown and route-based visibility"
```

---

### Task 3: Add Google OAuth callback page

**Files:**
- Create: `apps/shell/src/auth/OAuthCallbackPage.vue`
- Modify: `apps/shell/src/router.ts`

- [ ] **Step 1: Create the callback page**

```vue
<!-- apps/shell/src/auth/OAuthCallbackPage.vue -->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loader2 } from 'lucide-vue-next'
import { useAuth } from './useAuth.js'

const router = useRouter()
const { bootstrap } = useAuth()

onMounted(async () => {
  // fastapi-users has already set cookies before redirecting here.
  // Bootstrap re-fetches /users/me to populate the auth store.
  await bootstrap()
  router.replace('/search')
})
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center gap-3 bg-bg">
    <Loader2 :size="28" class="animate-spin text-fg-muted" />
    <p class="text-sm text-fg-muted">Signing you in…</p>
  </div>
</template>
```

- [ ] **Step 2: Register the route in router.ts**

Add after the `/sign-up` route:

```typescript
// In apps/shell/src/router.ts, inside the routes array:
{
  path: '/auth/callback/google',
  component: () => import('./auth/OAuthCallbackPage.vue'),
},
```

Also add `'/auth/callback'` to the `PUBLIC_ONLY` array so authenticated users aren't redirected away if they somehow hit it again:

```typescript
const PUBLIC_ONLY = ['/sign-in', '/sign-up']
// change to:
const PUBLIC_ONLY = ['/sign-in', '/sign-up', '/auth/callback']
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/auth/OAuthCallbackPage.vue apps/shell/src/router.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add Google OAuth callback route"
```

---

### Task 4: Type-check

- [ ] **Step 1: Run type check**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell && pnpm type-check
```

Expected: no errors.

- [ ] **Step 2: Fix any type errors before continuing**
