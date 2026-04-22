<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronDown, ChevronRight, ArrowUp, ArrowDown, Trash2, Sparkles, Plus } from 'lucide-vue-next'
import type { Reason } from '@martin/common'
import { useBriefcases } from './useBriefcases.js'
import GroundCaseEntry from './GroundCaseEntry.vue'
import VersionHistoryPopover from './VersionHistoryPopover.vue'

const props = defineProps<{
  reason: Reason
  briefcaseId: string
  totalReasons: number
}>()

const emit = defineEmits<{
  update: []
  addCase: [reasonId: string]
  reorder: [reasonId: string, direction: 'up' | 'down']
}>()

const { updateReason, deleteReason, generateReasonArgument } = useBriefcases()

const collapsed = ref(false)
const editingTitle = ref(false)
const title = ref(props.reason.title)
const content = ref(props.reason.content ?? '')
const savedContent = ref(content.value)
const saving = ref(false)
const deleting = ref(false)
const generating = ref(false)
const confirmDelete = ref(false)
const confirmGenerate = ref(false)

const canGenerate = computed(() => props.reason.cases.length > 0)

async function onTitleBlur() {
  editingTitle.value = false
  const trimmed = title.value.trim()
  if (!trimmed || trimmed === props.reason.title) return
  await updateReason(props.briefcaseId, props.reason.id, { title: trimmed })
  emit('update')
}

async function onContentBlur() {
  if (content.value === savedContent.value) return
  saving.value = true
  try {
    await updateReason(props.briefcaseId, props.reason.id, { content: content.value })
    savedContent.value = content.value
  } finally {
    saving.value = false
  }
}

async function generate() {
  generating.value = true
  confirmGenerate.value = false
  try {
    const result = await generateReasonArgument(props.briefcaseId, props.reason.id)
    content.value = result.content
    savedContent.value = result.content
  } finally {
    generating.value = false
  }
}

async function doDelete() {
  deleting.value = true
  confirmDelete.value = false
  try {
    await deleteReason(props.briefcaseId, props.reason.id)
    emit('update')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="rounded-lg border border-border bg-bg-subtle overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-3 border-b border-border">
      <button @click="collapsed = !collapsed" class="text-fg-muted hover:text-fg transition-colors" :aria-label="collapsed ? 'Expand' : 'Collapse'">
        <ChevronRight v-if="collapsed" :size="15" />
        <ChevronDown v-else :size="15" />
      </button>

      <div class="flex-1 min-w-0">
        <input
          v-if="editingTitle"
          v-model="title"
          autofocus
          @blur="onTitleBlur"
          @keydown.enter="onTitleBlur"
          class="text-sm font-medium text-fg bg-transparent border-b border-primary focus:outline-none w-full"
        />
        <h3
          v-else
          @click="editingTitle = true"
          class="text-sm font-medium text-fg cursor-pointer hover:text-primary transition-colors truncate"
          title="Click to rename"
        >
          {{ reason.title }}
        </h3>
      </div>

      <div class="flex items-center gap-1 shrink-0">
        <button
          @click="$emit('reorder', reason.id, 'up')"
          :disabled="reason.order === 0"
          class="p-1 rounded text-fg-muted hover:text-fg hover:bg-bg disabled:opacity-30 transition-colors"
          title="Move up"
          aria-label="Move ground up"
        ><ArrowUp :size="14" /></button>
        <button
          @click="$emit('reorder', reason.id, 'down')"
          :disabled="reason.order === totalReasons - 1"
          class="p-1 rounded text-fg-muted hover:text-fg hover:bg-bg disabled:opacity-30 transition-colors"
          title="Move down"
          aria-label="Move ground down"
        ><ArrowDown :size="14" /></button>

        <template v-if="confirmDelete">
          <span class="text-xs text-fg-muted">Delete?</span>
          <button @click="doDelete" :disabled="deleting" class="text-xs text-red-500 hover:underline disabled:opacity-50 px-1">
            {{ deleting ? '…' : 'Yes' }}
          </button>
          <button @click="confirmDelete = false" class="text-xs text-fg-muted hover:underline px-1">No</button>
        </template>
        <button
          v-else
          @click="confirmDelete = true"
          class="p-1 rounded text-fg-muted hover:text-red-500 hover:bg-bg transition-colors"
          title="Delete ground"
          aria-label="Delete ground"
        ><Trash2 :size="14" /></button>
      </div>
    </div>

    <div v-if="!collapsed" class="p-4 space-y-3">
      <div v-if="reason.cases.length > 0" class="space-y-2">
        <GroundCaseEntry
          v-for="entry in reason.cases"
          :key="entry.id"
          :entry="entry"
          :briefcase-id="briefcaseId"
          :reason-id="reason.id"
          @update="$emit('update')"
        />
      </div>
      <p v-else class="text-xs text-fg-muted">No cases added yet.</p>

      <button
        @click="$emit('addCase', reason.id)"
        class="flex items-center gap-1 text-xs font-medium text-primary hover:opacity-80 transition-opacity"
      >
        <Plus :size="13" /> Add case
      </button>

      <div class="pt-3 border-t border-border space-y-1.5">
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium tracking-wide uppercase text-fg-muted">Argument</p>
          <div class="flex items-center gap-2">
            <template v-if="confirmGenerate">
              <span class="text-xs text-fg-muted">Replace?</span>
              <button @click="generate" :disabled="generating" class="text-xs text-primary hover:underline disabled:opacity-50">Yes</button>
              <button @click="confirmGenerate = false" class="text-xs text-fg-muted hover:underline">No</button>
            </template>
            <button
              v-else
              @click="confirmGenerate = true"
              :disabled="generating || !canGenerate"
              :title="canGenerate ? 'Generate argument from cases' : 'Add at least one case first'"
              class="flex items-center gap-1 text-xs text-fg-muted hover:text-primary transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Sparkles :size="12" />
              {{ generating ? 'Generating…' : 'Generate' }}
            </button>
            <VersionHistoryPopover
              :briefcase-id="briefcaseId"
              parent-type="reason"
              :reason-id="reason.id"
              @restored="$emit('update')"
            />
          </div>
        </div>
        <textarea
          v-model="content"
          @blur="onContentBlur"
          placeholder="Write your synthesised argument here, or generate one from the cases above…"
          rows="4"
          class="w-full text-sm px-3 py-2 rounded border border-border bg-bg text-fg placeholder:text-fg-muted focus:outline-none focus:ring-1 focus:ring-primary resize-none"
        />
        <p v-if="saving" class="text-xs text-fg-muted">Saving…</p>
      </div>
    </div>
  </div>
</template>
