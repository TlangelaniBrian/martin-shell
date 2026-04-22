<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { Send, Loader2, AlertCircle } from 'lucide-vue-next'
import { useCaseChat } from './useCaseChat.js'

const props = defineProps<{ caseId: number }>()

const { messages, loading, error, send } = useCaseChat(props.caseId)
const input = ref('')
const threadRef = ref<HTMLElement | null>(null)

async function handleSend() {
  const msg = input.value.trim()
  if (!msg || loading.value) return
  input.value = ''
  await send(msg)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

watch(messages, async () => {
  await nextTick()
  threadRef.value?.scrollTo({ top: threadRef.value.scrollHeight, behavior: 'smooth' })
}, { deep: true })
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Message thread -->
    <div ref="threadRef" class="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-0">
      <p v-if="messages.length === 0" class="text-sm text-fg-muted leading-relaxed">
        Ask AI to summarise this case, identify relevant precedents, or help build an argument around it.
      </p>

      <template v-for="(msg, i) in messages" :key="i">
        <div
          :class="[
            'max-w-[85%] rounded-lg px-3 py-2 text-sm leading-relaxed',
            msg.role === 'user'
              ? 'ml-auto bg-primary text-white'
              : 'bg-bg-subtle text-fg border border-border'
          ]"
        >
          {{ msg.content }}
        </div>
      </template>

      <!-- Loading bubble -->
      <div v-if="loading" class="flex items-center gap-1.5 text-fg-muted">
        <Loader2 :size="14" class="animate-spin" />
        <span class="text-xs">Thinking…</span>
      </div>
    </div>

    <!-- Error bar -->
    <div v-if="error" class="flex items-center gap-1.5 px-4 py-2 bg-red-50 border-t border-red-200 text-red-600 text-xs">
      <AlertCircle :size="13" />
      {{ error }}
    </div>

    <!-- Input row -->
    <div class="flex items-end gap-2 px-4 py-3 border-t border-border">
      <textarea
        v-model="input"
        rows="1"
        placeholder="Ask about this case…"
        class="flex-1 resize-none rounded-md border border-border bg-bg px-3 py-2 text-sm text-fg placeholder:text-fg-muted focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
        style="max-height: 120px; overflow-y: auto;"
        @keydown="handleKeydown"
      />
      <button
        :disabled="!input.trim() || loading"
        class="flex items-center justify-center w-9 h-9 rounded-md bg-primary text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary-hover transition"
        @click="handleSend"
      >
        <Send :size="15" />
      </button>
    </div>
  </div>
</template>
