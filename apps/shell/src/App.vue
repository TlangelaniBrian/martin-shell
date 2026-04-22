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
