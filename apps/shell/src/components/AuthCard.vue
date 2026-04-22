<script setup lang="ts">
defineProps<{ class?: string }>()
</script>

<template>
  <main class="flex min-h-screen items-center justify-center bg-bg px-4">
    <div
      :class="['w-full max-w-sm rounded-xl border border-border bg-surface shadow-md p-8', $props.class ?? 'space-y-6']"
    >
      <slot />
    </div>
  </main>
</template>
