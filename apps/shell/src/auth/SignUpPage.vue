<script setup lang="ts">
import { reactive, ref } from "vue";
import { useAuth } from "./useAuth.js";
import { Card } from "@martin/components";
import { Input } from "@martin/components";
import { Button } from "@martin/components";

const { signUp } = useAuth();
const form = reactive({ email: "", password: "" });
const error = ref<string | null>(null);
const submitted = ref(false);
const submitting = ref(false);

async function onSubmit() {
  error.value = null;
  submitting.value = true;
  try {
    await signUp(form.email, form.password);
    submitted.value = true;
  } catch (err: any) {
    error.value = err?.detail ?? "Registration failed";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="flex h-screen items-center justify-center">
    <Card class="w-96 p-6">
      <h2 class="mb-4 text-lg font-semibold">Sign up</h2>
      <template v-if="submitted">
        <p class="text-sm">Thanks! Check your email to verify your account.</p>
      </template>
      <template v-else>
        <form @submit.prevent="onSubmit" class="space-y-4">
          <div>
            <Input
              v-model="form.email"
              type="email"
              placeholder="Email"
              :disabled="submitting"
            />
          </div>
          <div>
            <Input
              v-model="form.password"
              type="password"
              placeholder="Password"
              :disabled="submitting"
            />
          </div>
          <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
          <Button type="submit" :disabled="submitting" class="w-full">
            {{ submitting ? 'Signing up...' : 'Sign up' }}
          </Button>
        </form>
      </template>
    </Card>
  </div>
</template>
