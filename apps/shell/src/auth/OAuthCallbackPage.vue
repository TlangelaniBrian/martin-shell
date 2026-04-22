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
