<script setup lang="ts">
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuth } from './useAuth.js'
import { isApiError } from '@martin/common'
import { Card, Input, Button } from '@martin/components'

const { signIn } = useAuth()
const form = reactive({ email: '', password: '' })
const error = ref<string | null>(null)
const submitting = ref(false)

async function onSubmit() {
  error.value = null
  submitting.value = true
  try {
    await signIn(form.email, form.password)
  } catch (err: unknown) {
    error.value = isApiError(err) ? err.detail : 'Login failed'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex h-screen items-center justify-center">
    <Card class="w-96 p-6">
      <h2 class="mb-4 text-lg font-semibold">Sign in</h2>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <div>
          <Input
            v-model="form.email"
            type="email"
            placeholder="Email"
            :disabled="submitting"
          />
        </div>
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
        <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
        <Button type="submit" :disabled="submitting" class="w-full">
          {{ submitting ? 'Signing in...' : 'Sign in' }}
        </Button>
      </form>
    </Card>
  </div>
</template>
