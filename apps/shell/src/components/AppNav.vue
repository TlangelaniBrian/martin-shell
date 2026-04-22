<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Search, BookOpen, ChevronDown, User } from 'lucide-vue-next'
import { useAuthStore } from '@martin/common'
import { useAuth } from '../auth/useAuth.js'

const auth = useAuthStore()
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

const initials = computed(() => auth.value.user?.email?.[0]?.toUpperCase() ?? null)
</script>

<template>
  <nav class="sticky top-0 z-50 border-b border-border bg-surface/80 backdrop-blur-md">
    <div class="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
      <RouterLink to="/" class="text-lg font-semibold tracking-tight text-fg">
        Martin
      </RouterLink>

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

      <div class="flex items-center gap-2">
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
