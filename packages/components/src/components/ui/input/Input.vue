<script setup lang="ts">
import { cn } from '../../../lib/utils.js'

const props = defineProps<{
  class?: string
  type?: string
  placeholder?: string
  disabled?: boolean
}>()

const model = defineModel<string>()
</script>

<template>
  <input
    v-model="model"
    :type="props.type ?? 'text'"
    :placeholder="props.placeholder"
    :disabled="props.disabled"
    :class="cn(
      'flex h-10 w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-fg placeholder:text-fg-muted focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )"
  />
</template>
