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
  <div v-if="auth.loading" class="app-loading">
    <div class="app-loading-spinner" />
  </div>
  <template v-else>
    <AppNav v-if="showNav" />
    <RouterView />
  </template>
</template>

<style>
.app-loading {
  display: flex;
  height: 100vh;
  align-items: center;
  justify-content: center;
  background: #06080f;
}
.app-loading-spinner {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 2px solid #1e2533;
  border-top-color: #c4a362;
  animation: app-spin 0.7s linear infinite;
}
@keyframes app-spin {
  to { transform: rotate(360deg); }
}
</style>
