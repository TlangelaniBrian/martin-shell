<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { Bookmark } from 'lucide-vue-next'
import { useAuthStore, isApiError } from '@martin/common'
import type { Briefcase } from '@martin/common'
import { useBriefcases } from '../briefcases/useBriefcases.js'

const props = defineProps<{ caseId: number }>()

const auth = useAuthStore()
const { listBriefcases, addCaseToReason } = useBriefcases()

const open = ref(false)
const briefcases = ref<Briefcase[]>([])
const loading = ref(false)
const expanded = ref<string | null>(null)
const saving = ref<string | null>(null)
const feedback = ref<{ msg: string; ok: boolean } | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)

function onOutsideClick(e: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(e.target as Node)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onOutsideClick))
onUnmounted(() => document.removeEventListener('mousedown', onOutsideClick))

async function toggle(e: MouseEvent) {
  e.stopPropagation()
  const next = !open.value
  open.value = next
  if (next && auth.value.user) {
    loading.value = true
    feedback.value = null
    expanded.value = null
    try {
      const data = await listBriefcases()
      briefcases.value = data.briefcases
    } finally {
      loading.value = false
    }
  }
}

async function save(briefcaseId: string, reasonId: string) {
  saving.value = reasonId
  feedback.value = null
  try {
    await addCaseToReason(briefcaseId, reasonId, props.caseId)
    feedback.value = { msg: 'Saved!', ok: true }
    setTimeout(() => { open.value = false }, 800)
  } catch (err) {
    feedback.value = {
      msg: isApiError(err) && err.status === 409 ? 'Already in this ground' : 'Failed to save',
      ok: false,
    }
  } finally {
    saving.value = null
  }
}
</script>

<template>
  <div ref="containerRef" class="relative" @click.stop>
    <button
      @click="toggle"
      title="Save to briefcase"
      aria-label="Save to briefcase"
      class="flex items-center justify-center p-1.5 rounded border border-border text-fg-muted hover:border-primary hover:text-primary transition-colors"
    >
      <Bookmark :size="14" />
    </button>

    <div
      v-if="open"
      class="absolute right-0 top-8 z-20 w-64 rounded-lg border border-border bg-bg shadow-lg overflow-hidden"
    >
      <div v-if="!auth.user" class="p-3 space-y-1.5">
        <p class="text-xs text-fg-muted">Sign in to save cases</p>
        <RouterLink to="/sign-in" class="text-xs text-primary hover:underline">Sign in →</RouterLink>
      </div>

      <p v-else-if="loading" class="text-xs text-fg-muted px-3 py-4 text-center">Loading…</p>

      <div v-else-if="briefcases.length === 0" class="p-3 space-y-1.5">
        <p class="text-xs text-fg-muted">No briefcases yet.</p>
        <RouterLink to="/briefcases" class="text-xs text-primary hover:underline">Create one →</RouterLink>
      </div>

      <template v-else>
        <div class="px-3 py-2 border-b border-border">
          <p class="text-xs font-medium text-fg">Save to briefcase</p>
        </div>
        <div class="max-h-64 overflow-y-auto">
          <div v-for="bc in briefcases" :key="bc.id" class="border-b border-border last:border-0">
            <button
              @click="expanded = expanded === bc.id ? null : bc.id"
              class="w-full text-left px-3 py-2 hover:bg-bg-subtle transition-colors"
            >
              <p class="text-xs font-medium text-fg truncate">{{ bc.name }}</p>
              <p class="text-xs text-fg-muted">{{ bc.reasons.length }} {{ bc.reasons.length === 1 ? 'ground' : 'grounds' }}</p>
            </button>
            <div v-if="expanded === bc.id" class="bg-bg-subtle border-t border-border">
              <p v-if="bc.reasons.length === 0" class="text-xs text-fg-muted px-4 py-2">No grounds yet</p>
              <button
                v-for="r in bc.reasons"
                :key="r.id"
                @click="save(bc.id, r.id)"
                :disabled="saving === r.id"
                class="w-full text-left px-4 py-2 text-xs text-fg hover:bg-primary/10 hover:text-primary transition-colors disabled:opacity-50"
              >
                {{ saving === r.id ? 'Saving…' : r.title }}
              </button>
            </div>
          </div>
        </div>
        <div
          v-if="feedback"
          :class="['px-3 py-2 border-t border-border text-xs', feedback.ok ? 'text-green-600' : 'text-red-500']"
        >
          {{ feedback.msg }}
        </div>
      </template>
    </div>
  </div>
</template>
