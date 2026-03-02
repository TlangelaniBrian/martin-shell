<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const WorkspaceApp = defineAsyncComponent(() =>
  // @ts-ignore — MF remote, resolved at runtime
  import('martin_workspace/WorkspaceApp')
)
</script>

<template>
  <WorkspaceApp />
</template>
