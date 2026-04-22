<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { BookOpen, Plus } from 'lucide-vue-next'
import type { Briefcase } from '@martin/common'
import { useBriefcases } from './useBriefcases.js'

const { listBriefcases, createBriefcase, deleteBriefcase } = useBriefcases()

const briefcases = ref<Briefcase[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await listBriefcases()
    briefcases.value = res.briefcases
  } finally {
    loading.value = false
  }
})

const newName = ref('')
const newDesc = ref('')
const creating = ref(false)
const createError = ref<string | null>(null)

async function onCreate() {
  if (!newName.value.trim()) return
  creating.value = true
  createError.value = null
  try {
    const created = await createBriefcase(newName.value.trim(), newDesc.value.trim() || undefined)
    briefcases.value.unshift(created)
    newName.value = ''
    newDesc.value = ''
  } catch {
    createError.value = 'Failed to create briefcase.'
  } finally {
    creating.value = false
  }
}

const confirmingDelete = ref<string | null>(null)
const deleting = ref<string | null>(null)

async function doDelete(id: string) {
  deleting.value = id
  try {
    await deleteBriefcase(id)
    briefcases.value = briefcases.value.filter((b) => b.id !== id)
  } finally {
    deleting.value = null
    confirmingDelete.value = null
  }
}

function groundCount(b: Briefcase) { return b.reasons.length }
function caseCount(b: Briefcase) { return b.reasons.reduce((sum, r) => sum + r.cases.length, 0) }
</script>

<template>
  <main class="max-w-3xl mx-auto px-6 py-10 space-y-8">
    <h1 class="text-2xl font-semibold text-fg">Your Briefcases</h1>

    <form @submit.prevent="onCreate" class="rounded-lg border border-border bg-bg-subtle p-5 space-y-3">
      <h2 class="font-medium text-fg">New briefcase</h2>
      <input
        v-model="newName"
        type="text"
        placeholder="Matter name (e.g. Smith v ABC Corp)"
        required
        class="w-full text-sm px-3 py-2 rounded-md border border-border bg-bg text-fg placeholder:text-fg-muted focus:outline-none focus:ring-1 focus:ring-primary"
      />
      <input
        v-model="newDesc"
        type="text"
        placeholder="Description (optional)"
        class="w-full text-sm px-3 py-2 rounded-md border border-border bg-bg text-fg placeholder:text-fg-muted focus:outline-none focus:ring-1 focus:ring-primary"
      />
      <p v-if="createError" class="text-xs text-red-500">{{ createError }}</p>
      <button
        type="submit"
        :disabled="creating || !newName.trim()"
        class="flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-md bg-primary text-primary-fg disabled:opacity-50 hover:bg-primary-hover transition-colors"
      >
        <Plus :size="15" />
        {{ creating ? 'Creating…' : 'Create briefcase' }}
      </button>
    </form>

    <p v-if="loading" class="text-sm text-fg-muted">Loading…</p>

    <div v-else-if="briefcases.length === 0" class="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <BookOpen :size="36" class="text-fg-muted/50" />
      <p class="text-sm font-medium text-fg">No briefcases yet</p>
      <p class="text-sm text-fg-muted max-w-xs">
        Create a briefcase for each matter you're working on, then add grounds and supporting cases.
      </p>
    </div>

    <div v-else class="grid gap-4">
      <div
        v-for="b in briefcases"
        :key="b.id"
        class="relative rounded-lg border border-border bg-bg-subtle p-5 hover:border-primary/40 transition-colors"
      >
        <RouterLink :to="`/briefcases/${b.id}`" class="block">
          <h3 class="font-medium text-fg leading-snug mb-1">{{ b.name }}</h3>
          <p v-if="b.description" class="text-sm text-fg-muted line-clamp-2 mb-3">{{ b.description }}</p>
          <div class="flex items-center gap-3 text-xs text-fg-muted">
            <span>{{ groundCount(b) }} {{ groundCount(b) === 1 ? 'ground' : 'grounds' }}</span>
            <span>·</span>
            <span>{{ caseCount(b) }} {{ caseCount(b) === 1 ? 'case' : 'cases' }}</span>
            <span>·</span>
            <span>Updated {{ new Date(b.updated_at).toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', year: 'numeric' }) }}</span>
          </div>
        </RouterLink>

        <div class="absolute top-4 right-4 flex items-center gap-2">
          <button v-if="confirmingDelete === b.id" @click="confirmingDelete = null" class="text-xs text-fg-muted hover:text-fg">Cancel</button>
          <button
            @click="confirmingDelete === b.id ? doDelete(b.id) : (confirmingDelete = b.id)"
            :disabled="deleting === b.id"
            class="text-xs text-fg-muted hover:text-red-500 transition-colors"
          >
            {{ deleting === b.id ? 'Deleting…' : confirmingDelete === b.id ? 'Confirm?' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>
