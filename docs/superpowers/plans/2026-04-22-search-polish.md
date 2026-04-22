# Search Page Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing SearchPage to match the polished Next.js version: split-screen layout (result list left, case detail right), pagination, court code → human name mapping, lucide icons throughout, a save-to-briefcase bookmark button, and an AI analysis placeholder panel in the detail view.

**Architecture:** `SearchPage.vue` is refactored into a split-screen layout using a `selectedCaseId` ref. Clicking a card sets the selected ID; the right panel shows `CaseDetail.vue`. A `courts.ts` util holds the court name map. `SaveToBriefcaseButton.vue` is a self-contained dropdown that lists briefcases/grounds and calls `addCaseToReason`. Pagination is client-side via `page` ref + TanStack Query.

**Tech Stack:** Vue 3 Composition API, TanStack Vue Query (already in use), lucide-vue-next, apiFetch + useBriefcases, Tailwind CSS v4

---

### Task 1: Create courts.ts utility

**Files:**
- Create: `apps/shell/src/search/courts.ts`

- [ ] **Step 1: Create the file**

```typescript
// apps/shell/src/search/courts.ts
export const COURT_NAMES: Record<string, string> = {
  ZACC:     'Constitutional Court',
  ZASCA:    'Supreme Court of Appeal',
  ZAGPJHC:  'Gauteng HC (Johannesburg)',
  ZAGPPHC:  'Gauteng HC (Pretoria)',
  ZAWCHC:   'Western Cape HC',
  ZAKZDHC:  'KwaZulu-Natal HC (Durban)',
  ZAKZPHC:  'KwaZulu-Natal HC (Pietermaritzburg)',
  ZAECGHC:  'Eastern Cape HC (Grahamstown)',
  ZACT:     'Competition Tribunal',
  ZACAC:    'Competition Appeal Court',
}

export const COURTS = Object.keys(COURT_NAMES)

export function courtLabel(code: string): string {
  return COURT_NAMES[code] ?? code
}
```

- [ ] **Step 2: Remove the inline `courtLabel` from SearchPage.vue**

In `apps/shell/src/search/SearchPage.vue`, delete the existing `courtLabel` function and replace the `SA_COURTS` array. This will be done in Task 4 when SearchPage is fully rewritten.

- [ ] **Step 3: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/search/courts.ts
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add courts utility with SA court name mapping"
```

---

### Task 2: Create SaveToBriefcaseButton.vue

**Files:**
- Create: `apps/shell/src/search/SaveToBriefcaseButton.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/search/SaveToBriefcaseButton.vue -->
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
  if (next && auth.user) {
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
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/search/SaveToBriefcaseButton.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add SaveToBriefcaseButton component"
```

---

### Task 3: Create CaseDetail.vue

**Files:**
- Create: `apps/shell/src/search/CaseDetail.vue`

- [ ] **Step 1: Create the file**

```vue
<!-- apps/shell/src/search/CaseDetail.vue -->
<script setup lang="ts">
import { FileText, ExternalLink, Sparkles, Building2, Calendar } from 'lucide-vue-next'
import type { CaseData } from '@martin/common'
import { courtLabel } from './courts.js'
import SaveToBriefcaseButton from './SaveToBriefcaseButton.vue'

defineProps<{ case_: CaseData }>()
</script>

<template>
  <div class="h-full flex flex-col overflow-hidden">
    <div class="flex-1 overflow-y-auto p-6">
      <h2 class="text-xl font-semibold text-fg leading-snug mb-3">{{ case_.case_name }}</h2>

      <div class="flex items-start justify-between gap-2 mb-3">
        <div class="flex flex-wrap gap-2">
          <span class="flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full bg-primary/10 text-primary">
            <Building2 :size="11" />
            {{ courtLabel(case_.court) }}
          </span>
          <span v-if="case_.date_decided" class="flex items-center gap-1 text-xs text-fg-muted py-1">
            <Calendar :size="11" />
            {{ new Date(case_.date_decided).toLocaleDateString('en-ZA', { year: 'numeric', month: 'long', day: 'numeric' }) }}
          </span>
        </div>
        <SaveToBriefcaseButton :case-id="case_.id" />
      </div>

      <p v-if="case_.citation" class="text-sm text-fg-muted mb-4">{{ case_.citation }}</p>

      <div v-if="case_.summary" class="mb-6">
        <p class="text-xs font-medium tracking-wide uppercase text-fg-muted mb-2">Summary</p>
        <p class="text-sm text-fg leading-relaxed whitespace-pre-line">{{ case_.summary }}</p>
      </div>

      <div class="flex gap-4">
        <a
          v-if="case_.pdf_url"
          :href="case_.pdf_url"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary-hover transition-colors"
        >
          <FileText :size="15" />
          Download PDF
        </a>
        <a
          :href="case_.saflii_url"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary-hover transition-colors"
        >
          <ExternalLink :size="15" />
          View on SAFLII
        </a>
      </div>
    </div>

    <!-- AI Analysis panel -->
    <div class="border-t border-border bg-bg-subtle">
      <div class="px-6 py-3 flex items-center border-b border-border">
        <span class="flex items-center gap-1.5 text-xs font-medium text-fg">
          <Sparkles :size="13" class="text-primary" />
          AI Analysis
        </span>
      </div>
      <div class="px-6 py-5 space-y-3">
        <p class="text-sm text-fg-muted leading-relaxed">
          Ask AI to summarise this case, identify relevant precedents, or help build an argument around it.
        </p>
        <button
          disabled
          title="AI chat coming soon"
          class="px-4 py-2 rounded-md text-sm font-medium bg-primary/10 text-primary border border-primary/20 opacity-60 cursor-not-allowed"
        >
          Ask about this case
        </button>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/search/CaseDetail.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: add CaseDetail component with AI placeholder panel"
```

---

### Task 4: Rewrite SearchPage.vue

**Files:**
- Modify: `apps/shell/src/search/SearchPage.vue`

- [ ] **Step 1: Replace SearchPage.vue entirely**

```vue
<!-- apps/shell/src/search/SearchPage.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { Search, Building2, Calendar, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import { apiFetch } from '@martin/common'
import type { SearchResponse, CaseData, SearchParams } from '@martin/common'
import { COURTS, courtLabel } from './courts.js'
import CaseDetail from './CaseDetail.vue'
import SaveToBriefcaseButton from './SaveToBriefcaseButton.vue'

const PAGE_SIZE = 20

// Search state
const query = ref('')
const court = ref('')
const yearFrom = ref('')
const yearTo = ref('')
const judge = ref('')
const party = ref('')
const page = ref(1)
const submitted = ref(false)
const selectedId = ref<number | null>(null)

const searchParams = computed<SearchParams>(() => ({
  q: query.value.trim() || undefined,
  court: court.value || undefined,
  year_from: yearFrom.value || undefined,
  year_to: yearTo.value || undefined,
  judge: judge.value.trim() || undefined,
  party: party.value.trim() || undefined,
  page: String(page.value),
}))

const enabled = computed(() => submitted.value && !!query.value.trim())

const { data, isFetching, isError } = useQuery({
  queryKey: ['search', searchParams],
  queryFn: () => {
    const params = new URLSearchParams()
    const p = searchParams.value
    if (p.q)         params.set('q', p.q)
    if (p.court)     params.set('court', p.court)
    if (p.year_from) params.set('year_from', p.year_from)
    if (p.year_to)   params.set('year_to', p.year_to)
    if (p.judge)     params.set('judge', p.judge)
    if (p.party)     params.set('party', p.party)
    if (p.page)      params.set('page', p.page)
    return apiFetch<SearchResponse>(`/search/?${params.toString()}`)
  },
  enabled,
  staleTime: 1000 * 60 * 5,
})

const results = computed<CaseData[]>(() => data.value?.results ?? [])
const total = computed(() => data.value?.total ?? 0)
const totalPages = computed(() => Math.ceil(total.value / PAGE_SIZE))
const selectedCase = computed(() => results.value.find((c) => c.id === selectedId.value) ?? null)
const hasFilters = computed(() => !!(court.value || yearFrom.value || yearTo.value || judge.value || party.value))

function handleSearch() {
  page.value = 1
  selectedId.value = null
  submitted.value = true
}

function clearFilters() {
  court.value = ''
  yearFrom.value = ''
  yearTo.value = ''
  judge.value = ''
  party.value = ''
  page.value = 1
}

function prevPage() { if (page.value > 1) { page.value--; selectedId.value = null } }
function nextPage() { if (page.value < totalPages.value) { page.value++; selectedId.value = null } }
</script>

<template>
  <!-- Initial / empty query state -->
  <div v-if="!submitted" class="flex flex-col items-center justify-center min-h-screen px-4 gap-8 bg-bg">
    <div class="text-center">
      <h1 class="text-3xl font-semibold tracking-tight text-fg mb-2">Martin</h1>
      <p class="text-fg-muted text-base">Search South African commercial law cases</p>
    </div>
    <form @submit.prevent="handleSearch" class="w-full max-w-2xl flex gap-2">
      <input
        v-model="query"
        type="text"
        placeholder="Search cases, citations, parties…"
        maxlength="200"
        class="flex-1 px-4 py-3 text-base bg-surface border border-border rounded-md text-fg placeholder:text-fg-muted focus:outline-none"
      />
      <button type="submit" aria-label="Search" class="px-4 py-3 bg-primary text-primary-fg font-medium rounded-md hover:bg-primary-hover transition-colors flex items-center justify-center">
        <Search :size="18" />
      </button>
    </form>
  </div>

  <!-- Split-screen search results -->
  <div v-else class="flex h-screen overflow-hidden bg-bg">
    <!-- Left panel -->
    <div class="w-full md:w-2/5 flex flex-col border-r border-border overflow-hidden">
      <!-- Search bar -->
      <div class="p-4 border-b border-border">
        <form @submit.prevent="handleSearch" class="flex gap-2">
          <input
            v-model="query"
            type="text"
            placeholder="Search cases, citations, parties…"
            maxlength="200"
            class="flex-1 px-4 py-2 text-sm bg-surface border border-border rounded-md text-fg placeholder:text-fg-muted focus:outline-none"
          />
          <button type="submit" aria-label="Search" class="px-3 py-2 bg-primary text-primary-fg rounded-md hover:bg-primary-hover transition-colors flex items-center justify-center">
            <Search :size="16" />
          </button>
        </form>
      </div>

      <!-- Filters -->
      <div class="px-4 py-3 border-b border-border bg-bg-subtle space-y-2">
        <div class="flex flex-wrap gap-3">
          <div class="space-y-1 min-w-[130px]">
            <label class="text-xs font-medium text-fg-muted">Court</label>
            <select v-model="court" class="w-full px-2.5 py-1.5 text-sm bg-surface border border-border rounded-md text-fg focus:outline-none focus:ring-1 focus:ring-primary">
              <option value="">All courts</option>
              <option v-for="c in COURTS" :key="c" :value="c">{{ courtLabel(c) }} ({{ c }})</option>
            </select>
          </div>
          <div class="space-y-1 w-[90px]">
            <label class="text-xs font-medium text-fg-muted">From year</label>
            <input v-model="yearFrom" type="number" placeholder="1994" min="1900" max="2100" class="w-full px-2.5 py-1.5 text-sm bg-surface border border-border rounded-md text-fg focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
          <div class="space-y-1 w-[90px]">
            <label class="text-xs font-medium text-fg-muted">To year</label>
            <input v-model="yearTo" type="number" placeholder="2025" min="1900" max="2100" class="w-full px-2.5 py-1.5 text-sm bg-surface border border-border rounded-md text-fg focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
          <div class="space-y-1 min-w-[110px]">
            <label class="text-xs font-medium text-fg-muted">Judge</label>
            <input v-model="judge" placeholder="e.g. Moseneke" maxlength="100" class="w-full px-2.5 py-1.5 text-sm bg-surface border border-border rounded-md text-fg focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
          <div class="space-y-1 min-w-[110px]">
            <label class="text-xs font-medium text-fg-muted">Party</label>
            <input v-model="party" placeholder="e.g. Woolworths" maxlength="100" class="w-full px-2.5 py-1.5 text-sm bg-surface border border-border rounded-md text-fg focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button @click="handleSearch" class="px-3 py-1.5 text-xs font-medium bg-primary text-primary-fg rounded-md hover:bg-primary-hover transition-colors">
            Apply filters
          </button>
          <button v-if="hasFilters" @click="clearFilters" class="flex items-center gap-1 px-2.5 py-1.5 text-xs text-fg-muted hover:text-fg rounded-md hover:bg-bg transition-colors">
            <X :size="12" /> Clear
          </button>
        </div>
      </div>

      <!-- Results list -->
      <div class="flex-1 overflow-y-auto">
        <!-- Loading skeletons -->
        <div v-if="isFetching" class="space-y-0">
          <div v-for="i in 8" :key="i" class="p-4 border-b border-border">
            <div class="h-4 bg-border rounded animate-pulse mb-2 w-3/4" />
            <div class="h-3 bg-border rounded animate-pulse w-1/3" />
          </div>
        </div>

        <!-- Error -->
        <div v-else-if="isError" class="p-4">
          <p class="text-sm text-red-500">Search failed. Please try again.</p>
        </div>

        <!-- Empty -->
        <div v-else-if="results.length === 0" class="flex flex-col items-center justify-center gap-3 py-16 px-6 text-center">
          <p class="text-sm font-medium text-fg">No cases found</p>
          <p class="text-xs text-fg-muted">Try different search terms or adjust your filters</p>
        </div>

        <!-- Case cards -->
        <button
          v-else
          v-for="c in results"
          :key="c.id"
          @click="selectedId = c.id"
          :class="[
            'w-full text-left p-4 border-b border-border transition-colors hover:bg-bg-subtle',
            selectedId === c.id ? 'bg-bg-subtle border-l-2 border-l-primary' : ''
          ]"
        >
          <div class="flex items-start justify-between gap-2 mb-1.5">
            <p class="text-sm font-medium text-fg leading-snug">{{ c.case_name }}</p>
            <SaveToBriefcaseButton :case-id="c.id" />
          </div>
          <div class="flex flex-wrap items-center gap-2 mb-1.5">
            <span class="flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">
              <Building2 :size="11" />
              {{ courtLabel(c.court) }}
            </span>
            <span v-if="c.date_decided" class="flex items-center gap-1 text-xs text-fg-muted">
              <Calendar :size="11" />
              {{ new Date(c.date_decided).getFullYear() }}
            </span>
            <span v-if="c.citation" class="text-xs text-fg-muted">{{ c.citation }}</span>
          </div>
          <p v-if="c.summary" class="text-xs text-fg-muted leading-relaxed line-clamp-2">
            {{ c.summary.replace(/<[^>]+>/g, '').trim() }}
          </p>
        </button>
      </div>

      <!-- Pagination footer -->
      <div class="p-3 border-t border-border flex items-center justify-between text-xs text-fg-muted">
        <span>{{ total }} result{{ total !== 1 ? 's' : '' }}</span>
        <div v-if="totalPages > 1" class="flex items-center gap-1">
          <button
            @click="prevPage"
            :disabled="page <= 1"
            class="flex items-center gap-0.5 px-2 py-1 rounded hover:bg-bg-subtle transition-colors disabled:opacity-30"
          >
            <ChevronLeft :size="13" /> Prev
          </button>
          <span class="px-2">{{ page }} / {{ totalPages }}</span>
          <button
            @click="nextPage"
            :disabled="page >= totalPages"
            class="flex items-center gap-0.5 px-2 py-1 rounded hover:bg-bg-subtle transition-colors disabled:opacity-30"
          >
            Next <ChevronRight :size="13" />
          </button>
        </div>
      </div>
    </div>

    <!-- Right panel: case detail -->
    <div class="hidden md:flex flex-1 flex-col overflow-hidden">
      <CaseDetail v-if="selectedCase" :case_="selectedCase" />
      <div v-else class="flex-1 flex flex-col items-center justify-center gap-2 text-center px-8">
        <p class="text-sm font-medium text-fg-muted">Select a case to view details</p>
        <p class="text-xs text-fg-muted">Click any result on the left</p>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/BrianMkhabela/Projects/op/martin-shell add apps/shell/src/search/SearchPage.vue
git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "feat: rewrite SearchPage with split-screen, pagination, filters, and icons"
```

---

### Task 5: Type-check

- [ ] **Step 1: Run type check**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell && pnpm type-check
```

Expected: no errors.

- [ ] **Step 2: Delete the stray ranking.py file**

```bash
rm /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell/src/search/ranking.py
git -C /Users/BrianMkhabela/Projects/op/martin-shell add -A && git -C /Users/BrianMkhabela/Projects/op/martin-shell commit -m "chore: remove stray ranking.py from frontend"
```
