<script setup lang="ts">
import { ref } from 'vue'
import { Clock, X } from 'lucide-vue-next'
import type { ContentVersion } from '@martin/common'
import { useBriefcases } from './useBriefcases.js'

const props = defineProps<{
  briefcaseId: string
  parentType: 'reason' | 'reason_case'
  reasonId: string
  entryId?: string
}>()

const emit = defineEmits<{ restored: [] }>()

const { listReasonVersions, listReasonCaseVersions, restoreVersion } = useBriefcases()

const open = ref(false)
const versions = ref<ContentVersion[]>([])
const loading = ref(false)
const restoring = ref<string | null>(null)

async function toggle() {
  if (open.value) { open.value = false; return }
  open.value = true
  loading.value = true
  try {
    versions.value = props.parentType === 'reason'
      ? await listReasonVersions(props.briefcaseId, props.reasonId)
      : await listReasonCaseVersions(props.briefcaseId, props.reasonId, props.entryId!)
  } finally {
    loading.value = false
  }
}

async function restore(versionId: string) {
  restoring.value = versionId
  try {
    await restoreVersion(props.briefcaseId, versionId)
    open.value = false
    emit('restored')
  } finally {
    restoring.value = null
  }
}
</script>

<template>
  <div class="relative">
    <button
      @click="toggle"
      title="Version history"
      aria-label="Version history"
      class="p-1 rounded text-fg-muted hover:text-fg hover:bg-bg-subtle transition-colors"
    >
      <Clock :size="13" />
    </button>

    <div
      v-if="open"
      class="absolute right-0 top-7 z-10 w-72 rounded-lg border border-border bg-bg shadow-lg"
    >
      <div class="flex items-center justify-between px-3 py-2 border-b border-border">
        <span class="text-xs font-medium text-fg">Version history</span>
        <button @click="open = false" class="p-0.5 rounded text-fg-muted hover:text-fg" aria-label="Close">
          <X :size="13" />
        </button>
      </div>

      <p v-if="loading" class="text-xs text-fg-muted px-3 py-4 text-center">Loading…</p>
      <p v-else-if="versions.length === 0" class="text-xs text-fg-muted px-3 py-4 text-center">No versions saved yet.</p>
      <ul v-else class="max-h-64 overflow-y-auto divide-y divide-border">
        <li v-for="v in versions" :key="v.id" class="px-3 py-2 flex items-start gap-2">
          <div class="flex-1 min-w-0">
            <p class="text-xs text-fg">{{ v.content.slice(0, 60) }}{{ v.content.length > 60 ? '…' : '' }}</p>
            <p class="text-xs text-fg-muted mt-0.5">
              v{{ v.version }} · {{ new Date(v.created_at).toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) }}
            </p>
          </div>
          <button
            @click="restore(v.id)"
            :disabled="restoring === v.id"
            class="shrink-0 text-xs text-primary hover:opacity-80 disabled:opacity-50"
          >
            {{ restoring === v.id ? '…' : 'Restore' }}
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>
