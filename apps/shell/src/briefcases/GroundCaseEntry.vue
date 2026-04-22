<script setup lang="ts">
import { ref } from 'vue'
import { Sparkles, X } from 'lucide-vue-next'
import type { ReasonCase } from '@martin/common'
import { courtLabel } from '../search/courts.js'
import { useBriefcases } from './useBriefcases.js'
import VersionHistoryPopover from './VersionHistoryPopover.vue'

const props = defineProps<{ entry: ReasonCase; briefcaseId: string; reasonId: string }>()
const emit = defineEmits<{ update: [] }>()

const { updateReasonCase, removeReasonCase, generateCaseContent } = useBriefcases()

const content = ref(props.entry.content ?? '')
const savedContent = ref(content.value)
const saving = ref(false)
const removing = ref(false)
const generating = ref(false)
const confirmGenerate = ref(false)

async function onBlur() {
  if (content.value === savedContent.value) return
  saving.value = true
  try {
    await updateReasonCase(props.briefcaseId, props.reasonId, props.entry.id, { content: content.value })
    savedContent.value = content.value
  } finally {
    saving.value = false
  }
}

async function generate() {
  generating.value = true
  confirmGenerate.value = false
  try {
    const result = await generateCaseContent(props.briefcaseId, props.reasonId, props.entry.id)
    content.value = result.content
    savedContent.value = result.content
  } finally {
    generating.value = false
  }
}

async function remove() {
  removing.value = true
  try {
    await removeReasonCase(props.briefcaseId, props.reasonId, props.entry.id)
    emit('update')
  } finally {
    removing.value = false
  }
}
</script>

<template>
  <div class="rounded border border-border bg-bg p-3 space-y-2">
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <p class="text-sm font-medium text-fg leading-snug">
          {{ entry.case_name ?? `Case #${entry.case_id}` }}
        </p>
        <div class="flex flex-wrap items-center gap-2 mt-0.5">
          <span v-if="entry.court" class="text-xs font-medium px-1.5 py-0.5 rounded-full bg-primary/10 text-primary">
            {{ courtLabel(entry.court) }}
          </span>
          <span v-if="entry.date_decided" class="text-xs text-fg-muted">
            {{ new Date(entry.date_decided).getFullYear() }}
          </span>
          <span v-if="entry.citation" class="text-xs text-fg-muted">{{ entry.citation }}</span>
        </div>
      </div>

      <div class="flex items-center gap-1 shrink-0">
        <VersionHistoryPopover
          :briefcase-id="briefcaseId"
          parent-type="reason_case"
          :reason-id="reasonId"
          :entry-id="entry.id"
          @restored="$emit('update')"
        />
        <template v-if="confirmGenerate">
          <span class="text-xs text-fg-muted">Replace?</span>
          <button @click="generate" :disabled="generating" class="text-xs text-primary hover:underline disabled:opacity-50">Yes</button>
          <button @click="confirmGenerate = false" class="text-xs text-fg-muted hover:underline">No</button>
        </template>
        <button
          v-else
          @click="confirmGenerate = true"
          :disabled="generating"
          title="Generate relevance note"
          class="p-1 rounded text-fg-muted hover:text-primary hover:bg-bg-subtle transition-colors disabled:opacity-50"
          aria-label="Generate note"
        >
          <span v-if="generating" class="text-xs">…</span>
          <Sparkles v-else :size="13" />
        </button>
        <button
          @click="remove"
          :disabled="removing"
          title="Remove case"
          class="p-1 rounded text-fg-muted hover:text-red-500 hover:bg-bg-subtle transition-colors disabled:opacity-50"
          aria-label="Remove case"
        >
          <span v-if="removing" class="text-xs">…</span>
          <X v-else :size="13" />
        </button>
      </div>
    </div>

    <textarea
      v-model="content"
      @blur="onBlur"
      placeholder="Add a note about why this case is relevant…"
      rows="2"
      class="w-full text-sm px-2 py-1.5 rounded border border-border bg-bg-subtle text-fg placeholder:text-fg-muted focus:outline-none focus:ring-1 focus:ring-primary resize-none"
    />
    <p v-if="saving" class="text-xs text-fg-muted">Saving…</p>
  </div>
</template>
