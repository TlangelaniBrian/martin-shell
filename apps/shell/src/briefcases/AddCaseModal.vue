<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'
import { apiFetch, isApiError } from '@martin/common'
import type { CaseData, SearchResponse } from '@martin/common'
import { useBriefcases } from './useBriefcases.js'
import { courtLabel } from '../search/courts.js'

const props = defineProps<{
  open: boolean
  briefcaseId: string
  reasonId: string
}>()

const emit = defineEmits<{ close: []; added: [] }>()

const { addCaseToReason } = useBriefcases()

const query = ref('')
const results = ref<CaseData[]>([])
const loading = ref(false)
const adding = ref<number | null>(null)
const error = ref<string | null>(null)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(query, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!val.trim()) { results.value = []; return }
  debounceTimer = setTimeout(async () => {
    loading.value = true
    try {
      const data = await apiFetch<SearchResponse>(`/search/?q=${encodeURIComponent(val.trim())}`)
      results.value = data.results
    } finally {
      loading.value = false
    }
  }, 300)
})

watch(() => props.open, (val) => {
  if (val) { query.value = ''; results.value = []; error.value = null }
})

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

async function addCase(caseId: number) {
  adding.value = caseId
  error.value = null
  try {
    await addCaseToReason(props.briefcaseId, props.reasonId, caseId)
    emit('added')
    emit('close')
  } catch (err) {
    error.value = isApiError(err) && err.status === 409
      ? 'This case is already in this ground.'
      : 'Failed to add case.'
  } finally {
    adding.value = null
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="$emit('close')"
    >
      <div class="bg-bg rounded-xl border border-border shadow-xl w-full max-w-lg mx-4 overflow-hidden">
        <div class="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 class="text-sm font-medium text-fg">Add case to ground</h2>
          <button @click="$emit('close')" class="p-1 rounded text-fg-muted hover:text-fg hover:bg-bg-subtle" aria-label="Close">
            <X :size="16" />
          </button>
        </div>

        <div class="p-4 border-b border-border">
          <input
            v-model="query"
            type="text"
            placeholder="Search cases by name, citation, or parties…"
            class="w-full text-sm px-3 py-2 rounded-md border border-border bg-bg-subtle text-fg placeholder:text-fg-muted focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div class="max-h-80 overflow-y-auto">
          <p v-if="loading" class="text-sm text-fg-muted px-4 py-6 text-center">Searching…</p>
          <p v-else-if="!query.trim()" class="text-sm text-fg-muted px-4 py-6 text-center">Type to search for cases</p>
          <p v-else-if="results.length === 0" class="text-sm text-fg-muted px-4 py-6 text-center">No results found</p>
          <ul v-else class="divide-y divide-border">
            <li v-for="r in results" :key="r.id">
              <button
                @click="addCase(r.id)"
                :disabled="adding === r.id"
                class="w-full text-left px-4 py-3 hover:bg-bg-subtle transition-colors disabled:opacity-50"
              >
                <p class="text-sm font-medium text-fg">{{ r.case_name }}</p>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="text-xs font-medium px-1.5 py-0.5 rounded-full bg-primary/10 text-primary">
                    {{ courtLabel(r.court) }}
                  </span>
                  <span v-if="r.date_decided" class="text-xs text-fg-muted">
                    {{ new Date(r.date_decided).getFullYear() }}
                  </span>
                  <span v-if="r.citation" class="text-xs text-fg-muted">{{ r.citation }}</span>
                </div>
              </button>
            </li>
          </ul>
        </div>

        <div v-if="error" class="px-4 py-2 border-t border-border">
          <p class="text-xs text-red-500">{{ error }}</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>
