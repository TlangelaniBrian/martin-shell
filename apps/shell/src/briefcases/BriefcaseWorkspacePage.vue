<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { Plus } from 'lucide-vue-next'
import type { Briefcase } from '@martin/common'
import { isApiError } from '@martin/common'
import { useBriefcases } from './useBriefcases.js'
import GroundSection from './GroundSection.vue'
import AddCaseModal from './AddCaseModal.vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const { getBriefcase, updateBriefcase, createReason, reorderReasons } = useBriefcases()

const briefcase = ref<Briefcase | null>(null)
const loading = ref(true)
const editingName = ref(false)
const name = ref('')
const description = ref('')
const addingGround = ref(false)
const addingToReasonId = ref<string | null>(null)

async function load() {
  try {
    const data = await getBriefcase(id)
    briefcase.value = data
    name.value = data.name
    description.value = data.description ?? ''
  } catch (err) {
    if (isApiError(err) && err.status === 404) router.push('/briefcases')
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function onNameBlur() {
  editingName.value = false
  if (!briefcase.value) return
  const trimmed = name.value.trim()
  if (!trimmed || trimmed === briefcase.value.name) return
  briefcase.value = await updateBriefcase(id, { name: trimmed })
}

async function onDescBlur() {
  if (!briefcase.value) return
  const trimmed = description.value.trim()
  if (trimmed === (briefcase.value.description ?? '')) return
  briefcase.value = await updateBriefcase(id, { description: trimmed })
}

async function addGround() {
  addingGround.value = true
  try {
    await createReason(id, 'New ground')
    await load()
  } finally {
    addingGround.value = false
  }
}

async function handleReorder(movedId: string, direction: 'up' | 'down') {
  if (!briefcase.value) return
  const ids = briefcase.value.reasons.map((r) => r.id)
  const idx = ids.indexOf(movedId)
  if (direction === 'up' && idx === 0) return
  if (direction === 'down' && idx === ids.length - 1) return
  const newIds = [...ids]
  const swap = direction === 'up' ? idx - 1 : idx + 1;
  [newIds[idx], newIds[swap]] = [newIds[swap], newIds[idx]]
  await reorderReasons(id, newIds)
  await load()
}
</script>

<template>
  <main class="max-w-3xl mx-auto px-6 py-10 space-y-8">
    <div class="flex items-center gap-2 text-xs text-fg-muted">
      <RouterLink to="/briefcases" class="hover:text-fg transition-colors">Briefcases</RouterLink>
      <span>/</span>
      <span class="text-fg truncate">{{ briefcase?.name }}</span>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="h-6 w-6 animate-spin rounded-full border-4 border-border border-t-primary" />
    </div>

    <template v-else-if="briefcase">
      <div class="space-y-2">
        <input
          v-if="editingName"
          v-model="name"
          autofocus
          @blur="onNameBlur"
          @keydown.enter="onNameBlur"
          class="text-2xl font-semibold text-fg bg-transparent border-b border-primary focus:outline-none w-full"
        />
        <h1
          v-else
          @click="editingName = true"
          class="text-2xl font-semibold text-fg cursor-pointer hover:text-primary transition-colors"
          title="Click to edit"
        >
          {{ briefcase.name }}
        </h1>
        <textarea
          v-model="description"
          @blur="onDescBlur"
          placeholder="Add a description…"
          rows="2"
          class="w-full text-sm text-fg-muted bg-transparent placeholder:text-fg-muted/50 focus:outline-none resize-none"
        />
      </div>

      <div v-if="briefcase.reasons.length === 0" class="flex flex-col items-center gap-2 py-10 text-center">
        <p class="text-sm font-medium text-fg">No grounds yet</p>
        <p class="text-sm text-fg-muted">Add a ground (e.g. a legal argument or cause of action), then attach supporting cases.</p>
      </div>

      <div v-else class="space-y-4">
        <GroundSection
          v-for="reason in briefcase.reasons"
          :key="reason.id"
          :reason="reason"
          :briefcase-id="id"
          :total-reasons="briefcase.reasons.length"
          @update="load"
          @add-case="(rid) => addingToReasonId = rid"
          @reorder="handleReorder"
        />
      </div>

      <button
        @click="addGround"
        :disabled="addingGround"
        class="flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-md border border-border text-fg-muted hover:border-primary hover:text-primary transition-colors disabled:opacity-50"
      >
        <Plus :size="15" />
        {{ addingGround ? 'Adding…' : 'Add ground' }}
      </button>
    </template>

    <AddCaseModal
      :open="addingToReasonId !== null"
      :briefcase-id="id"
      :reason-id="addingToReasonId ?? ''"
      @close="addingToReasonId = null"
      @added="load"
    />
  </main>
</template>
