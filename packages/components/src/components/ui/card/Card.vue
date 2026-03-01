<script setup lang="ts">
import { cn } from '../../../lib/utils.js'
const props = defineProps<{ class?: string }>()
</script>
<template>
  <div :class="cn('rounded-lg border border-border bg-bg-subtle text-fg shadow-sm', props.class)">
    <slot />
  </div>
</template>
