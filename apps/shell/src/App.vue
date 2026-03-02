<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";
import { RouterView, useRouter } from "vue-router";
import { useAuthStore, clearUser } from "@martin/common";
import { useAuth } from "./auth/useAuth.js";

const router = useRouter();
const auth = useAuthStore();
const { bootstrap } = useAuth();

function onSessionExpired() {
  clearUser();
  router.push("/sign-in");
}

onMounted(async () => {
  window.addEventListener("session:expired", onSessionExpired);
  await bootstrap();
});

onUnmounted(() => {
  window.removeEventListener("session:expired", onSessionExpired);
});
</script>

<template>
  <div
    v-if="auth.loading"
    class="flex h-screen items-center justify-center"
  >
    <div class="h-8 w-8 animate-spin rounded-full border-4 border-border border-t-primary" />
  </div>
  <RouterView v-else />
</template>
