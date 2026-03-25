<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from '@martin/common'
import type { SearchParams, SearchResponse, CaseData } from '@martin/common'
import { Input } from '@martin/components'
import { Button } from '@martin/components'
import { Badge } from '@martin/components'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@martin/components'

// ── Search state ──────────────────────────────────────────────────────────
const query = ref('')
const court  = ref('')
const yearFrom = ref('')
const yearTo   = ref('')
const judge    = ref('')
const page     = ref(1)
const submitted = ref(false)

const SA_COURTS = [
  'Constitutional Court of South Africa',
  'Supreme Court of Appeal',
  'Gauteng Division, Pretoria',
  'Gauteng Division, Johannesburg',
  'Western Cape High Court, Cape Town',
  'KwaZulu-Natal Division, Durban',
  'KwaZulu-Natal Division, Pietermaritzburg',
  'Eastern Cape Division, Grahamstown',
  'Northern Cape Division',
  'Free State Division',
  'Limpopo Division',
  'Mpumalanga Division',
]

// ── Search params ─────────────────────────────────────────────────────────
const searchParams = computed<SearchParams>(() => ({
  q:        query.value.trim() || undefined,
  court:    court.value || undefined,
  year_from: yearFrom.value || undefined,
  year_to:   yearTo.value || undefined,
  judge:    judge.value.trim() || undefined,
  page:     String(page.value),
}))

// ── TanStack Query ────────────────────────────────────────────────────────
const enabled = computed(() => submitted.value && !!query.value.trim())

const { data, isFetching, isError, error } = useQuery({
  queryKey: ['search', searchParams],
  queryFn: () => {
    const params = new URLSearchParams()
    const p = searchParams.value
    if (p.q)         params.set('q', p.q)
    if (p.court)     params.set('court', p.court)
    if (p.year_from) params.set('year_from', p.year_from)
    if (p.year_to)   params.set('year_to', p.year_to)
    if (p.judge)     params.set('judge', p.judge)
    if (p.page)      params.set('page', p.page)
    return apiFetch<SearchResponse>(`/search?${params.toString()}`)
  },
  enabled,
  staleTime: 1000 * 60 * 5,
})

const results  = computed<CaseData[]>(() => data.value?.results ?? [])
const total    = computed(() => data.value?.total ?? 0)
const hasMore  = computed(() => results.value.length < total.value)

// ── Actions ───────────────────────────────────────────────────────────────
function handleSearch() {
  page.value = 1
  submitted.value = true
}

function loadMore() {
  page.value += 1
}

function clearFilters() {
  court.value = ''
  yearFrom.value = ''
  yearTo.value = ''
  judge.value = ''
  page.value = 1
}

function courtLabel(court: string): string {
  if (court.includes('Constitutional')) return 'ConCourt'
  if (court.includes('Supreme Court of Appeal')) return 'SCA'
  if (court.includes('Gauteng')) return 'GP'
  if (court.includes('Western Cape')) return 'WC'
  if (court.includes('KwaZulu')) return 'KZN'
  return court.split(',')[0].trim()
}
</script>

<template>
  <div class="mx-auto max-w-4xl px-4 py-8 space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-semibold text-fg">Case Law Search</h1>
      <p class="text-sm text-fg-muted mt-1">Search South African case law from SAFLII</p>
    </div>

    <!-- Search bar -->
    <form class="flex gap-2" @submit.prevent="handleSearch">
      <Input
        v-model="query"
        placeholder="Search cases, citations, legal principles…"
        class="flex-1"
        autofocus
      />
      <Button type="submit" :disabled="!query.trim() || isFetching">
        {{ isFetching ? 'Searching…' : 'Search' }}
      </Button>
    </form>

    <!-- Filters -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="col-span-2 sm:col-span-2">
        <label class="text-xs text-fg-muted mb-1 block">Court</label>
        <select
          v-model="court"
          class="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-fg focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All courts</option>
          <option v-for="c in SA_COURTS" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
      <div>
        <label class="text-xs text-fg-muted mb-1 block">Year from</label>
        <Input v-model="yearFrom" placeholder="e.g. 2010" type="number" min="1994" max="2026" />
      </div>
      <div>
        <label class="text-xs text-fg-muted mb-1 block">Year to</label>
        <Input v-model="yearTo" placeholder="e.g. 2024" type="number" min="1994" max="2026" />
      </div>
      <div class="col-span-2 flex items-end gap-2">
        <div class="flex-1">
          <label class="text-xs text-fg-muted mb-1 block">Judge</label>
          <Input v-model="judge" placeholder="e.g. Wallis JA" />
        </div>
        <Button variant="ghost" size="sm" class="mb-0.5" @click="clearFilters">
          Clear filters
        </Button>
      </div>
    </div>

    <!-- Error -->
    <div
      v-if="isError"
      class="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      Search failed: {{ (error as Error)?.message ?? 'Unknown error' }}
    </div>

    <!-- Results summary -->
    <div v-if="submitted && !isFetching && results.length > 0" class="text-sm text-fg-muted">
      {{ total.toLocaleString() }} result{{ total !== 1 ? 's' : '' }} for
      <span class="font-medium text-fg">"{{ searchParams.q }}"</span>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="submitted && !isFetching && results.length === 0 && !isError"
      class="flex flex-col items-center justify-center py-16 text-center"
    >
      <p class="text-fg-muted">No cases found for <strong>{{ searchParams.q }}</strong></p>
      <p class="text-sm text-fg-muted mt-1">Try different search terms or remove filters.</p>
    </div>

    <!-- Initial state -->
    <div
      v-else-if="!submitted"
      class="flex flex-col items-center justify-center py-16 text-center gap-2"
    >
      <p class="text-fg-muted">Search SAFLII case law</p>
      <p class="text-sm text-fg-muted">
        Try: "Grootboom housing rights", "[2002] ZACC 15", "Wallis JA dismissal"
      </p>
    </div>

    <!-- Results list -->
    <div v-if="results.length > 0" class="space-y-3">
      <Card
        v-for="c in results"
        :key="c.id"
        class="transition-shadow hover:shadow-md cursor-pointer"
        @click="c.saflii_url && window.open(c.saflii_url, '_blank')"
      >
        <CardHeader class="pb-2">
          <div class="flex items-start justify-between gap-3">
            <CardTitle class="text-base leading-snug">{{ c.case_name }}</CardTitle>
            <Badge variant="outline" class="shrink-0 text-xs">
              {{ courtLabel(c.court) }}
            </Badge>
          </div>
          <CardDescription class="flex flex-wrap gap-2 mt-1">
            <span v-if="c.citation" class="font-mono text-xs">{{ c.citation }}</span>
            <span v-if="c.date_decided" class="text-xs">
              {{ new Date(c.date_decided).getFullYear() }}
            </span>
            <span class="text-xs text-fg-muted truncate max-w-xs">{{ c.court }}</span>
          </CardDescription>
        </CardHeader>
        <CardContent v-if="c.summary" class="pt-0">
          <p class="text-sm text-fg-muted line-clamp-3">{{ c.summary }}</p>
        </CardContent>
      </Card>
    </div>

    <!-- Load more -->
    <div v-if="hasMore" class="flex justify-center pt-2">
      <Button variant="outline" :disabled="isFetching" @click="loadMore">
        {{ isFetching ? 'Loading…' : 'Load more results' }}
      </Button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isFetching && results.length === 0" class="space-y-3">
      <div
        v-for="i in 5"
        :key="i"
        class="h-28 rounded-lg border border-border bg-muted animate-pulse"
      />
    </div>
  </div>
</template>
