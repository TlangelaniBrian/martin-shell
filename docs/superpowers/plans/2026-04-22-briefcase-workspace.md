# Briefcase Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full briefcase workspace — a list page, a workspace page per briefcase, with argument grounds, per-ground cases, AI argument generation, version history, and a case-search modal.

**Architecture:** Two routes: `/briefcases` (list) and `/briefcases/:id` (workspace). A `useBriefcases` composable handles all API calls. `@martin/common` already has all the types (`Briefcase`, `Reason`, `ReasonCase`, `ContentVersion`, `GenerateResponse`). Components are split by responsibility: `GroundSection.vue` (one argument ground), `GroundCaseEntry.vue` (one case within a ground), `VersionHistoryPopover.vue`, `AddCaseModal.vue`. UI labels say "ground/grounds" — DB/API stays "reason".

**Tech Stack:** Vue 3 Composition API, TanStack Vue Query for data fetching, apiFetch from @martin/common, lucide-vue-next, Tailwind CSS v4

---

### Task 1: Create useBriefcases composable

**Files:**
- Create: `apps/shell/src/briefcases/useBriefcases.ts`

- [ ] **Step 1: Create the file**

```typescript
// apps/shell/src/briefcases/useBriefcases.ts
import { apiFetch } from '@martin/common'
import type { Briefcase, Reason, ReasonCase, ContentVersion, GenerateResponse } from '@martin/common'

export function useBriefcases() {
  function listBriefcases(): Promise<{ briefcases: Briefcase[]; total: number }> {
    return apiFetch('/briefcases/')
  }

  function getBriefcase(id: string): Promise<Briefcase> {
    return apiFetch(`/briefcases/${id}`)
  }

  function createBriefcase(name: string, description?: string): Promise<Briefcase> {
    return apiFetch('/briefcases/', {
      method: 'POST',
      body: JSON.stringify({ name, description: description ?? null }),
    })
  }

  function updateBriefcase(id: string, data: { name?: string; description?: string }): Promise<Briefcase> {
    return apiFetch(`/briefcases/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
  }

  function deleteBriefcase(id: string): Promise<void> {
    return apiFetch(`/briefcases/${id}`, { method: 'DELETE' })
  }

  function createReason(briefcaseId: string, title: string): Promise<Reason> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons`, {
      method: 'POST',
      body: JSON.stringify({ title, description: null }),
    })
  }

  function updateReason(briefcaseId: string, reasonId: string, data: { title?: string; content?: string }): Promise<Reason> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  function deleteReason(briefcaseId: string, reasonId: string): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}`, { method: 'DELETE' })
  }

  function reorderReasons(briefcaseId: string, reasonIds: string[]): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/reorder`, {
      method: 'PATCH',
      body: JSON.stringify({ reason_ids: reasonIds }),
    })
  }

  function addCaseToReason(briefcaseId: string, reasonId: string, caseId: number): Promise<ReasonCase> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases`, {
      method: 'POST',
      body: JSON.stringify({ case_id: caseId, content: null }),
    })
  }

  function updateReasonCase(briefcaseId: string, reasonId: string, entryId: string, data: { content?: string }): Promise<ReasonCase> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  function removeReasonCase(briefcaseId: string, reasonId: string, entryId: string): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}`, { method: 'DELETE' })
  }

  function listReasonVersions(briefcaseId: string, reasonId: string): Promise<ContentVersion[]> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/versions`)
  }

  function listReasonCaseVersions(briefcaseId: string, reasonId: string, entryId: string): Promise<ContentVersion[]> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}/versions`)
  }

  function restoreVersion(briefcaseId: string, versionId: string): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/versions/${versionId}/restore`, { method: 'POST' })
  }

  function generateCaseContent(briefcaseId: string, reasonId: string, entryId: string): Promise<GenerateResponse> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}/generate`, { method: 'POST' })
  }

  function generateReasonArgument(briefcaseId: string, reasonId: string): Promise<GenerateResponse> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/generate`, { method: 'POST' })
  }

  return {
    listBriefcases, getBriefcase, createBriefcase, updateBriefcase, deleteBriefcase,
    createReason, updateReason, deleteReason, reorderReasons,
    addCaseToReason, updateReasonCase, removeReasonCase,
    listReasonVersions, listReasonCaseVersions, restoreVersion,
    generateCaseContent, generateReasonArgument,
  }
}
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/briefcases/useBriefcases.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add useBriefcases composable"
```

---

### Task 2: Create VersionHistoryPopover.vue

**Files:**
- Create: `apps/shell/src/briefcases/VersionHistoryPopover.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/briefcases/VersionHistoryPopover.vue -->
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
        <button @click="open = false" class="p-0.5 rounded text-fg-muted hover:text-fg">
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
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/briefcases/VersionHistoryPopover.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add VersionHistoryPopover component"
```

---

### Task 3: Create AddCaseModal.vue

**Files:**
- Create: `apps/shell/src/briefcases/AddCaseModal.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/briefcases/AddCaseModal.vue -->
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
          <button @click="$emit('close')" class="p-1 rounded text-fg-muted hover:text-fg hover:bg-bg-subtle">
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
```

Note: this imports `courtLabel` from `../search/courts.js` — that file is created in the Search Polish plan. If running this plan first, create a stub:

```typescript
// apps/shell/src/search/courts.ts (stub — full version in search-polish plan)
export function courtLabel(code: string): string { return code }
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/briefcases/AddCaseModal.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add AddCaseModal component"
```

---

### Task 4: Create GroundCaseEntry.vue

**Files:**
- Create: `apps/shell/src/briefcases/GroundCaseEntry.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/briefcases/GroundCaseEntry.vue -->
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
        >
          <span v-if="generating" class="text-xs">…</span>
          <Sparkles v-else :size="13" />
        </button>
        <button
          @click="remove"
          :disabled="removing"
          title="Remove case"
          class="p-1 rounded text-fg-muted hover:text-red-500 hover:bg-bg-subtle transition-colors disabled:opacity-50"
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
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/briefcases/GroundCaseEntry.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add GroundCaseEntry component"
```

---

### Task 5: Create GroundSection.vue

**Files:**
- Create: `apps/shell/src/briefcases/GroundSection.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/briefcases/GroundSection.vue -->
<script setup lang="ts">
import { ref } from 'vue'
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

const emit = defineEmits<{ update: []; addCase: [reasonId: string]; reorder: [reasonId: string, direction: 'up' | 'down'] }>()

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

const canGenerate = $computed(() => props.reason.cases.length > 0)
</script>

<template>
  <div class="rounded-lg border border-border bg-bg-subtle overflow-hidden">
    <!-- Header -->
    <div class="flex items-center gap-2 px-4 py-3 border-b border-border">
      <button @click="collapsed = !collapsed" class="text-fg-muted hover:text-fg transition-colors">
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
        ><ArrowUp :size="14" /></button>
        <button
          @click="$emit('reorder', reason.id, 'down')"
          :disabled="reason.order === totalReasons - 1"
          class="p-1 rounded text-fg-muted hover:text-fg hover:bg-bg disabled:opacity-30 transition-colors"
          title="Move down"
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
        ><Trash2 :size="14" /></button>
      </div>
    </div>

    <!-- Body -->
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

      <!-- Argument -->
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
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/briefcases/GroundSection.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add GroundSection component"
```

---

### Task 6: Create BriefcasesPage.vue (list)

**Files:**
- Create: `apps/shell/src/briefcases/BriefcasesPage.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/briefcases/BriefcasesPage.vue -->
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

// New briefcase form
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

// Delete
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

    <!-- New briefcase form -->
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

    <!-- Loading -->
    <p v-if="loading" class="text-sm text-fg-muted">Loading…</p>

    <!-- Empty state -->
    <div v-else-if="briefcases.length === 0" class="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <BookOpen :size="36" class="text-fg-muted/50" />
      <p class="text-sm font-medium text-fg">No briefcases yet</p>
      <p class="text-sm text-fg-muted max-w-xs">
        Create a briefcase for each matter you're working on, then add grounds and supporting cases.
      </p>
    </div>

    <!-- List -->
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
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/briefcases/BriefcasesPage.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add BriefcasesPage list view"
```

---

### Task 7: Create BriefcaseWorkspacePage.vue

**Files:**
- Create: `apps/shell/src/briefcases/BriefcaseWorkspacePage.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/briefcases/BriefcaseWorkspacePage.vue -->
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

const {
  getBriefcase, updateBriefcase, createReason, reorderReasons,
} = useBriefcases()

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
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-xs text-fg-muted">
      <RouterLink to="/briefcases" class="hover:text-fg transition-colors">Briefcases</RouterLink>
      <span>/</span>
      <span class="text-fg truncate">{{ briefcase?.name }}</span>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="h-6 w-6 animate-spin rounded-full border-4 border-border border-t-primary" />
    </div>

    <template v-else-if="briefcase">
      <!-- Title + description -->
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

      <!-- Empty state -->
      <div v-if="briefcase.reasons.length === 0" class="flex flex-col items-center gap-2 py-10 text-center">
        <p class="text-sm font-medium text-fg">No grounds yet</p>
        <p class="text-sm text-fg-muted">Add a ground (e.g. a legal argument or cause of action), then attach supporting cases.</p>
      </div>

      <!-- Grounds list -->
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

      <!-- Add ground button -->
      <button
        @click="addGround"
        :disabled="addingGround"
        class="flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-md border border-border text-fg-muted hover:border-primary hover:text-primary transition-colors disabled:opacity-50"
      >
        <Plus :size="15" />
        {{ addingGround ? 'Adding…' : 'Add ground' }}
      </button>
    </template>

    <!-- Add case modal -->
    <AddCaseModal
      :open="addingToReasonId !== null"
      :briefcase-id="id"
      :reason-id="addingToReasonId ?? ''"
      @close="addingToReasonId = null"
      @added="load"
    />
  </main>
</template>
```

- [ ] **Step 2: Register routes in router.ts**

Add to the routes array:

```typescript
{
  path: '/briefcases',
  component: () => import('./briefcases/BriefcasesPage.vue'),
},
{
  path: '/briefcases/:id',
  component: () => import('./briefcases/BriefcaseWorkspacePage.vue'),
},
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/briefcases/ apps/shell/src/router.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add briefcase workspace pages and routes"
```

---

### Task 8: Type-check

- [ ] **Step 1: Run type check**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell && pnpm type-check
```

Expected: no errors.
