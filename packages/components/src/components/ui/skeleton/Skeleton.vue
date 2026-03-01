<script setup lang="ts">
import { cn } from '../../../lib/utils.js'
const props = defineProps<{ class?: string }>()
</script>
<template>
  <div :class="cn('animate-pulse rounded-md bg-border', props.class)" />
</template>
