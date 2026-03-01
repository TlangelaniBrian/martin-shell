<script setup lang="ts">
import { cn } from '../../../lib/utils.js'
const props = defineProps<{ class?: string; variant?: 'default' | 'outline' }>()
</script>
<template>
  <span :class="cn(
    'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
    props.variant === 'outline'
      ? 'border-border text-fg'
      : 'border-transparent bg-primary text-primary-fg',
    props.class
  )"><slot /></span>
</template>
