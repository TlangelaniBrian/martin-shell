<script setup lang="ts">
import { cn } from '../../../lib/utils.js'
const props = defineProps<{ class?: string }>()
</script>
<template>
  <p :class="cn('text-sm text-fg-muted', props.class)"><slot /></p>
</template>
