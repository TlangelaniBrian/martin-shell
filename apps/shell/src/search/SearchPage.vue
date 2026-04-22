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

  <div v-else class="flex h-screen overflow-hidden bg-bg">
    <!-- Left panel -->
    <div class="w-full md:w-2/5 flex flex-col border-r border-border overflow-hidden">
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

      <!-- Results -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="isFetching">
          <div v-for="i in 8" :key="i" class="p-4 border-b border-border">
            <div class="h-4 bg-border rounded animate-pulse mb-2 w-3/4" />
            <div class="h-3 bg-border rounded animate-pulse w-1/3" />
          </div>
        </div>

        <div v-else-if="isError" class="p-4">
          <p class="text-sm text-red-500">Search failed. Please try again.</p>
        </div>

        <div v-else-if="results.length === 0" class="flex flex-col items-center justify-center gap-3 py-16 px-6 text-center">
          <p class="text-sm font-medium text-fg">No cases found</p>
          <p class="text-xs text-fg-muted">Try different search terms or adjust your filters</p>
        </div>

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

      <!-- Pagination -->
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

    <!-- Right panel -->
    <div class="hidden md:flex flex-1 flex-col overflow-hidden">
      <CaseDetail v-if="selectedCase" :case_="selectedCase" />
      <div v-else class="flex-1 flex flex-col items-center justify-center gap-2 text-center px-8">
        <p class="text-sm font-medium text-fg-muted">Select a case to view details</p>
        <p class="text-xs text-fg-muted">Click any result on the left</p>
      </div>
    </div>
  </div>
</template>
