# Account Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/account` page with four sections: Profile (email + verified badge), Security (password reset trigger), AI Provider (configure which LLM provider powers argument generation), and Data & Privacy (POPIA notice).

**Architecture:** Single `AccountPage.vue` protected by the router guard. Calls `GET /ai-settings/` on mount, `PATCH /ai-settings/` on save, and `POST /auth/forgot-password` for password reset. AI settings types added to `@martin/common`. A `useAISettings` composable handles the API calls so the page stays thin. `Section.vue` is a tiny layout wrapper reused four times.

**Tech Stack:** Vue 3 Composition API, apiFetch from @martin/common, lucide-vue-next (Eye/EyeOff/CheckCircle), Tailwind CSS v4, vue-router

---

### Task 1: Add AI settings types to @martin/common

**Files:**
- Create: `packages/common/src/types/ai-settings.ts`
- Modify: `packages/common/src/index.ts`

- [ ] **Step 1: Create ai-settings.ts**

```typescript
// packages/common/src/types/ai-settings.ts
export type AIProvider = 'anthropic' | 'openai' | 'google' | 'deepseek'

export interface AISettingsRead {
  provider: AIProvider
  model: string | null
  anthropic_configured: boolean
  openai_configured: boolean
  google_configured: boolean
  deepseek_configured: boolean
}

export interface AISettingsUpdate {
  provider?: AIProvider
  model?: string
  anthropic_api_key?: string
  openai_api_key?: string
  google_api_key?: string
  deepseek_api_key?: string
}

export const PROVIDER_META: Record<AIProvider, { label: string; keyField: keyof AISettingsUpdate; configuredField: keyof AISettingsRead }> = {
  anthropic: { label: 'Anthropic (Claude)', keyField: 'anthropic_api_key', configuredField: 'anthropic_configured' },
  openai:    { label: 'OpenAI (GPT)',        keyField: 'openai_api_key',    configuredField: 'openai_configured' },
  google:    { label: 'Google (Gemini)',     keyField: 'google_api_key',    configuredField: 'google_configured' },
  deepseek:  { label: 'DeepSeek',           keyField: 'deepseek_api_key',  configuredField: 'deepseek_configured' },
}
```

- [ ] **Step 2: Export from index.ts**

Add to `packages/common/src/index.ts`:

```typescript
export * from './types/ai-settings.js'
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add packages/common/src/types/ai-settings.ts packages/common/src/index.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add AI settings types to @martin/common"
```

---

### Task 2: Create useAISettings composable

**Files:**
- Create: `apps/shell/src/account/useAISettings.ts`

- [ ] **Step 1: Create the file**

```typescript
// apps/shell/src/account/useAISettings.ts
import { ref, onMounted } from 'vue'
import { apiFetch } from '@martin/common'
import type { AISettingsRead, AISettingsUpdate, AIProvider } from '@martin/common'

export function useAISettings() {
  const settings = ref<AISettingsRead | null>(null)
  const loading = ref(true)
  const saving = ref(false)
  const saved = ref(false)
  const error = ref<string | null>(null)
  let savedTimer: ReturnType<typeof setTimeout> | null = null

  onMounted(async () => {
    try {
      settings.value = await apiFetch<AISettingsRead>('/ai-settings/')
    } catch {
      // silently ignore — user just won't see configured state
    } finally {
      loading.value = false
    }
  })

  async function saveSettings(provider: AIProvider, apiKey: string, modelOverride: string): Promise<void> {
    saving.value = true
    error.value = null
    saved.value = false
    try {
      const body: AISettingsUpdate = { provider }
      if (apiKey) body[import_meta_provider_key(provider)] = apiKey
      if (modelOverride) body.model = modelOverride
      settings.value = await apiFetch<AISettingsRead>('/ai-settings/', {
        method: 'PATCH',
        body: JSON.stringify(body),
      })
      if (savedTimer) clearTimeout(savedTimer)
      saved.value = true
      savedTimer = setTimeout(() => { saved.value = false }, 3000)
    } catch {
      error.value = 'Failed to save AI settings.'
    } finally {
      saving.value = false
    }
  }

  function isConfigured(provider: AIProvider): boolean {
    if (!settings.value) return false
    const fieldMap: Record<AIProvider, keyof AISettingsRead> = {
      anthropic: 'anthropic_configured',
      openai: 'openai_configured',
      google: 'google_configured',
      deepseek: 'deepseek_configured',
    }
    return settings.value[fieldMap[provider]] as boolean
  }

  return { settings, loading, saving, saved, error, saveSettings, isConfigured }
}

function import_meta_provider_key(provider: AIProvider): keyof AISettingsUpdate {
  const map: Record<AIProvider, keyof AISettingsUpdate> = {
    anthropic: 'anthropic_api_key',
    openai: 'openai_api_key',
    google: 'google_api_key',
    deepseek: 'deepseek_api_key',
  }
  return map[provider]
}
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/account/useAISettings.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add useAISettings composable"
```

---

### Task 3: Create Section.vue layout helper

**Files:**
- Create: `apps/shell/src/components/Section.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/components/Section.vue -->
<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="rounded-lg border border-border bg-surface p-6 space-y-4">
    <h2 class="text-base font-semibold text-fg">{{ title }}</h2>
    <slot />
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/components/Section.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add Section layout component"
```

---

### Task 4: Create AccountPage.vue

**Files:**
- Create: `apps/shell/src/account/AccountPage.vue`
- Modify: `apps/shell/src/router.ts`

- [ ] **Step 1: Create AccountPage.vue**

```vue
<!-- apps/shell/src/account/AccountPage.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { Eye, EyeOff, CheckCircle } from 'lucide-vue-next'
import { useAuthStore } from '@martin/common'
import type { AIProvider } from '@martin/common'
import { PROVIDER_META } from '@martin/common'
import Section from '../components/Section.vue'
import { useAISettings } from './useAISettings.js'

const auth = useAuthStore()
const { settings, saving, saved, error: aiError, saveSettings, isConfigured } = useAISettings()

// AI settings form state
const provider = ref<AIProvider>('anthropic')
const apiKey = ref('')
const showKey = ref(false)
const modelOverride = ref('')

// Sync provider/model from loaded settings
import { watch } from 'vue'
watch(settings, (val) => {
  if (val) {
    provider.value = val.provider
    modelOverride.value = val.model ?? ''
  }
}, { immediate: true })

async function onAISave(e: Event) {
  e.preventDefault()
  await saveSettings(provider.value, apiKey.value, modelOverride.value)
  if (!aiError.value) apiKey.value = ''
}

// Password reset
const resetSent = ref(false)
const resetError = ref<string | null>(null)
const resetting = ref(false)

async function sendResetLink() {
  if (!auth.user?.email) return
  resetting.value = true
  resetError.value = null
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: auth.user.email }),
    })
    if (res.ok || res.status === 202) {
      resetSent.value = true
    } else {
      resetError.value = 'Failed to send reset email.'
    }
  } catch {
    resetError.value = 'Failed to send reset email.'
  } finally {
    resetting.value = false
  }
}

const PROVIDERS = Object.entries(PROVIDER_META).map(([value, meta]) => ({
  value: value as AIProvider,
  label: meta.label,
}))
</script>

<template>
  <main class="max-w-2xl mx-auto px-6 py-10 space-y-6">
    <h1 class="text-2xl font-semibold text-fg">Account</h1>

    <!-- Profile -->
    <Section title="Profile">
      <div class="space-y-1">
        <p class="text-xs font-medium text-fg-muted uppercase tracking-wide">Email</p>
        <div class="flex items-center gap-2">
          <p class="text-sm text-fg">{{ auth.user?.email }}</p>
          <span v-if="auth.user?.is_verified" class="flex items-center gap-1 text-xs text-green-600">
            <CheckCircle :size="13" />
            Verified
          </span>
        </div>
      </div>
    </Section>

    <!-- Security -->
    <Section title="Security">
      <p class="text-sm text-fg-muted">Change your password by requesting a reset link.</p>
      <p v-if="resetSent" class="text-sm text-green-600">Reset link sent — check your email.</p>
      <template v-else>
        <p v-if="resetError" class="text-sm text-red-500">{{ resetError }}</p>
        <button
          @click="sendResetLink"
          :disabled="resetting"
          class="px-4 py-2 rounded-md border border-border text-sm text-fg hover:bg-bg-subtle transition-colors disabled:opacity-60"
        >
          {{ resetting ? 'Sending…' : 'Send password reset link' }}
        </button>
      </template>
    </Section>

    <!-- AI Provider -->
    <Section title="AI Provider">
      <p class="text-sm text-fg-muted">
        Configure which AI provider powers argument generation in your briefcases.
        Your API key is stored securely and never shared.
      </p>
      <form @submit.prevent="onAISave" class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-fg">Provider</label>
          <select
            v-model="provider"
            @change="apiKey = ''"
            class="w-full px-3 py-2 rounded-md border border-border bg-bg text-fg text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option v-for="p in PROVIDERS" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-fg">
            API Key
            <span v-if="isConfigured(provider)" class="text-xs font-normal text-green-600 ml-1">
              (configured — leave blank to keep existing)
            </span>
          </label>
          <div class="relative">
            <input
              v-model="apiKey"
              :type="showKey ? 'text' : 'password'"
              :placeholder="isConfigured(provider) ? '••••••••••••••••' : 'Enter your API key'"
              class="w-full px-3 py-2 pr-10 rounded-md border border-border bg-bg text-fg placeholder:text-fg-muted text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="button"
              @click="showKey = !showKey"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-fg-muted hover:text-fg transition-colors"
              :aria-label="showKey ? 'Hide key' : 'Show key'"
            >
              <EyeOff v-if="showKey" :size="15" />
              <Eye v-else :size="15" />
            </button>
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-fg">
            Model override
            <span class="text-xs font-normal text-fg-muted">(optional)</span>
          </label>
          <input
            v-model="modelOverride"
            type="text"
            placeholder="e.g. claude-sonnet-4-5 (leave blank for default)"
            class="w-full px-3 py-2 rounded-md border border-border bg-bg text-fg placeholder:text-fg-muted text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <p v-if="aiError" class="text-sm text-red-500">{{ aiError }}</p>
        <p v-if="saved" class="text-sm text-green-600">Settings saved.</p>

        <button
          type="submit"
          :disabled="saving"
          class="px-4 py-2 rounded-md bg-primary text-primary-fg text-sm font-medium hover:bg-primary-hover transition-colors disabled:opacity-60"
        >
          {{ saving ? 'Saving…' : 'Save AI settings' }}
        </button>
      </form>
    </Section>

    <!-- Data & Privacy -->
    <Section title="Data & Privacy">
      <p class="text-sm text-fg-muted leading-relaxed">
        In accordance with POPIA, your search history is retained for up to 90 days and then
        automatically deleted. You can request full deletion of your account and all associated
        data at any time.
      </p>
      <button
        disabled
        title="Contact support to delete your account"
        class="px-4 py-2 rounded-md border border-red-200 text-sm text-red-500 hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Delete my account
      </button>
      <p class="text-xs text-fg-muted">
        To delete your account now, email
        <a href="mailto:support@martinlegal.co.za" class="text-primary hover:underline">
          support@martinlegal.co.za
        </a>
      </p>
    </Section>
  </main>
</template>
```

- [ ] **Step 2: Register route in router.ts**

Add to the routes array (this is a protected route — no changes to `PUBLIC_ONLY`):

```typescript
{
  path: '/account',
  component: () => import('./account/AccountPage.vue'),
},
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/account/AccountPage.vue apps/shell/src/router.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add account page with AI settings and POPIA section"
```

---

### Task 5: Type-check

- [ ] **Step 1: Run type check**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell && pnpm type-check
```

Expected: no errors.
