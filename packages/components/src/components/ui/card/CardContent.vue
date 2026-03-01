<script setup lang="ts">
import { cn } from '../../../lib/utils.js'
const props = defineProps<{ class?: string }>()
</script>
<template>
  <div :class="cn('p-6 pt-0', props.class)"><slot /></div>
</template>
