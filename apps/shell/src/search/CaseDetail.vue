<script setup lang="ts">
import { ref } from 'vue'
import { FileText, ExternalLink, Sparkles, Building2, Calendar, ChevronDown } from 'lucide-vue-next'
import type { CaseData } from '@martin/common'
import { courtLabel } from './courts.js'
import SaveToBriefcaseButton from './SaveToBriefcaseButton.vue'
import CaseChatPanel from './CaseChatPanel.vue'

defineProps<{ case_: CaseData }>()
const chatOpen = ref(false)
</script>

<template>
  <div class="h-full flex flex-col overflow-hidden">
    <!-- Case metadata (scrollable) -->
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

    <!-- AI Analysis section -->
    <div class="border-t border-border bg-bg-subtle">
      <!-- Toggle header -->
      <button
        class="w-full px-6 py-3 flex items-center justify-between border-b border-border hover:bg-bg transition"
        @click="chatOpen = !chatOpen"
      >
        <span class="flex items-center gap-1.5 text-xs font-medium text-fg">
          <Sparkles :size="13" class="text-primary" />
          AI Analysis
        </span>
        <ChevronDown
          :size="14"
          class="text-fg-muted transition-transform duration-200"
          :class="{ 'rotate-180': chatOpen }"
        />
      </button>

      <!-- Chat panel — fixed height when open -->
      <div v-if="chatOpen" class="h-72">
        <CaseChatPanel :case-id="case_.id" />
      </div>
    </div>
  </div>
</template>
