<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="rounded-lg border border-border bg-surface p-6 space-y-4">
    <h2 class="text-base font-semibold text-fg">{{ title }}</h2>
    <slot />
  </div>
</template>
