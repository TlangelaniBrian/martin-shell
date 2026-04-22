<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { Loader2, CheckCircle, XCircle } from 'lucide-vue-next'
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
