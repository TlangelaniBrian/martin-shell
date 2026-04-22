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
