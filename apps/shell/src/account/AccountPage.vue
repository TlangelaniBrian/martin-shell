<script setup lang="ts">
import { ref, watch } from 'vue'
import { Eye, EyeOff, CheckCircle } from 'lucide-vue-next'
import { useAuthStore, authStore, PROVIDER_META } from '@martin/common'
import type { AIProvider } from '@martin/common'
import Section from '../components/Section.vue'
import { useAISettings } from './useAISettings.js'

const auth = useAuthStore()
const { settings, saving, saved, error: aiError, saveSettings, isConfigured } = useAISettings()

const provider = ref<AIProvider>('anthropic')
const apiKey = ref('')
const showKey = ref(false)
const modelOverride = ref('')

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

const resetSent = ref(false)
const resetError = ref<string | null>(null)
const resetting = ref(false)

async function sendResetLink() {
  const userEmail = authStore.state.user?.email
  if (!userEmail) return
  resetting.value = true
  resetError.value = null
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: userEmail }),
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
