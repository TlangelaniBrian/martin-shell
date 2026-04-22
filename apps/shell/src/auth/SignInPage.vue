<script setup lang="ts">
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuth } from './useAuth.js'
import { isApiError } from '@martin/common'

const { signIn } = useAuth()
const form = reactive({ email: '', password: '' })
const error = ref<string | null>(null)
const submitting = ref(false)
const showPassword = ref(false)

async function onSubmit() {
  error.value = null
  submitting.value = true
  try {
    await signIn(form.email, form.password)
  } catch (err: unknown) {
    error.value = isApiError(err) ? err.detail : 'Login failed. Check your credentials.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-root">
    <!-- Left brand panel -->
    <div class="brand-panel">
      <div class="brand-noise" />
      <div class="brand-grid" />
      <div class="brand-glow" />

      <div class="brand-content">
        <div class="brand-wordmark">
          <span class="wordmark-m">M</span><span class="wordmark-artin">artin</span>
        </div>
        <p class="brand-tagline">Legal intelligence,<br />distilled.</p>

        <div class="brand-feature-list">
          <div class="brand-feature">
            <span class="feature-dot" />
            <span>Case research at depth</span>
          </div>
          <div class="brand-feature">
            <span class="feature-dot" />
            <span>AI-powered analysis</span>
          </div>
          <div class="brand-feature">
            <span class="feature-dot" />
            <span>Secure briefcase workspace</span>
          </div>
        </div>
      </div>

      <div class="brand-footer">
        <span>Trusted by legal professionals</span>
      </div>
    </div>

    <!-- Right form panel -->
    <div class="form-panel">
      <div class="form-inner">
        <div class="form-header">
          <h1 class="form-title">Welcome back</h1>
          <p class="form-subtitle">Sign in to your workspace</p>
        </div>

        <form @submit.prevent="onSubmit" class="form-body" novalidate>
          <div class="field-group">
            <label class="field-label" for="email">Email address</label>
            <div class="field-wrap">
              <input
                id="email"
                v-model="form.email"
                type="email"
                class="field-input"
                placeholder="you@example.com"
                autocomplete="email"
                :disabled="submitting"
                required
              />
              <span class="field-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <rect x="2" y="4" width="20" height="16" rx="3"/>
                  <path d="m2 7 10 6 10-6"/>
                </svg>
              </span>
            </div>
          </div>

          <div class="field-group">
            <div class="field-label-row">
              <label class="field-label" for="password">Password</label>
              <RouterLink to="/auth/forgot-password" class="forgot-link">Forgot password?</RouterLink>
            </div>
            <div class="field-wrap">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="field-input"
                placeholder="••••••••••"
                autocomplete="current-password"
                :disabled="submitting"
                required
              />
              <button
                type="button"
                class="field-icon field-icon--btn"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
              >
                <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="form-error" role="alert">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ error }}
          </div>

          <button type="submit" class="submit-btn" :disabled="submitting">
            <span v-if="!submitting">Sign in</span>
            <span v-else class="submit-loading">
              <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
              Signing in…
            </span>
          </button>
        </form>

        <p class="form-switch">
          No account yet?
          <RouterLink to="/sign-up" class="switch-link">Create one</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Layout ── */
.auth-root {
  display: flex;
  min-height: 100vh;
  background: #06080f;
  font-family: 'DM Sans', sans-serif;
}

/* ── Brand panel ── */
.brand-panel {
  position: relative;
  width: 44%;
  min-height: 100vh;
  background: #06080f;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 3rem;

  animation: panelReveal 0.9s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes panelReveal {
  from { opacity: 0; transform: translateX(-20px); }
  to   { opacity: 1; transform: translateX(0); }
}

.brand-noise {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 200px 200px;
  pointer-events: none;
  z-index: 1;
}

.brand-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(196, 163, 98, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(196, 163, 98, 0.05) 1px, transparent 1px);
  background-size: 52px 52px;
  z-index: 1;
}

.brand-glow {
  position: absolute;
  bottom: -10%;
  left: -20%;
  width: 70%;
  height: 60%;
  background: radial-gradient(ellipse at center, rgba(196, 163, 98, 0.12) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
}

.brand-content {
  position: relative;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand-wordmark {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 4rem;
  font-weight: 500;
  line-height: 1;
  letter-spacing: -0.02em;
  margin-bottom: 2rem;

  animation: fadeUp 0.8s 0.2s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.wordmark-m {
  color: #c4a362;
}
.wordmark-artin {
  color: #e8e2d5;
}

.brand-tagline {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 2rem;
  font-weight: 400;
  line-height: 1.25;
  color: #8a8070;
  margin-bottom: 3rem;

  animation: fadeUp 0.8s 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.brand-feature-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;

  animation: fadeUp 0.8s 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.brand-feature {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  font-weight: 400;
  color: #6b6357;
  letter-spacing: 0.02em;
}

.feature-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #c4a362;
  flex-shrink: 0;
}

.brand-footer {
  position: relative;
  z-index: 2;
  font-size: 0.75rem;
  color: #3d3830;
  letter-spacing: 0.08em;
  text-transform: uppercase;

  animation: fadeUp 0.8s 0.65s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* ── Form panel ── */
.form-panel {
  flex: 1;
  background: #0d1117;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  position: relative;

  animation: panelReveal 0.9s 0.1s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.form-panel::before {
  content: '';
  position: absolute;
  inset-y: 0;
  left: 0;
  width: 1px;
  background: linear-gradient(to bottom, transparent, rgba(196, 163, 98, 0.2) 30%, rgba(196, 163, 98, 0.2) 70%, transparent);
}

.form-inner {
  width: 100%;
  max-width: 400px;

  animation: fadeUp 0.8s 0.3s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.form-header {
  margin-bottom: 2.5rem;
}

.form-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 2.25rem;
  font-weight: 500;
  color: #e8e2d5;
  letter-spacing: -0.02em;
  margin: 0 0 0.375rem;
  line-height: 1.1;
}

.form-subtitle {
  font-size: 0.875rem;
  color: #4a5568;
  font-weight: 400;
  margin: 0;
  letter-spacing: 0.01em;
}

/* ── Fields ── */
.form-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: #6b7280;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.forgot-link {
  font-size: 0.78rem;
  color: #c4a362;
  text-decoration: none;
  letter-spacing: 0.01em;
  transition: color 0.2s;
}
.forgot-link:hover { color: #d4b472; }

.field-wrap {
  position: relative;
}

.field-input {
  width: 100%;
  background: #0a0e16;
  border: 1px solid #1e2533;
  border-radius: 8px;
  color: #e8e2d5;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9375rem;
  font-weight: 400;
  padding: 0.75rem 2.75rem 0.75rem 0.9375rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  box-sizing: border-box;
  letter-spacing: 0.01em;
}

.field-input::placeholder {
  color: #2e3a4e;
  font-weight: 400;
}

.field-input:focus {
  border-color: rgba(196, 163, 98, 0.5);
  box-shadow: 0 0 0 3px rgba(196, 163, 98, 0.08);
  background: #0c1018;
}

.field-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.field-icon {
  position: absolute;
  right: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  color: #2e3a4e;
  display: flex;
  pointer-events: none;
}

.field-icon--btn {
  pointer-events: all;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: #3a4a5e;
  transition: color 0.2s;
}
.field-icon--btn:hover { color: #c4a362; }

/* ── Error ── */
.form-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  padding: 0.625rem 0.875rem;
  font-size: 0.8125rem;
  color: #fc8181;
  letter-spacing: 0.01em;
  animation: shake 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

@keyframes shake {
  10%, 90% { transform: translateX(-1px); }
  20%, 80% { transform: translateX(2px); }
  30%, 50%, 70% { transform: translateX(-3px); }
  40%, 60% { transform: translateX(3px); }
}

/* ── Submit ── */
.submit-btn {
  width: 100%;
  padding: 0.875rem;
  margin-top: 0.25rem;
  background: #c4a362;
  border: none;
  border-radius: 8px;
  color: #06080f;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, transparent 60%);
  pointer-events: none;
}

.submit-btn:hover:not(:disabled) {
  background: #d4b472;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(196, 163, 98, 0.25);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spin {
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Switch ── */
.form-switch {
  margin-top: 1.75rem;
  text-align: center;
  font-size: 0.8375rem;
  color: #3a4a5e;
  letter-spacing: 0.01em;
}

.switch-link {
  color: #c4a362;
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.25rem;
  transition: color 0.2s;
}
.switch-link:hover { color: #d4b472; }

/* ── Animations ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .auth-root { flex-direction: column; }
  .brand-panel {
    width: 100%;
    min-height: auto;
    padding: 2.5rem 2rem 2rem;
  }
  .brand-content { justify-content: flex-start; }
  .brand-tagline { font-size: 1.5rem; }
  .brand-feature-list { display: none; }
  .form-panel { padding: 2.5rem 1.5rem; }
  .form-panel::before { display: none; }
}
</style>
