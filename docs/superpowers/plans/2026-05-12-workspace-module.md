# Workspace Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold `martin-workspace-module` — a standalone Module Federation remote (port 3001) that exposes `WorkspaceApp`, providing a PDF viewer + notes panel for cases and briefcases.

**Architecture:** Standalone pnpm Vue 3 app in `/Users/BrianMkhabela/Projects/op/martin-workspace-module`. Uses `createMemoryHistory()` router that syncs with the shell's URL. Exposes one MF entry (`./WorkspaceApp`) consumed by `martin-shell`'s catch-all `/workspace/*` route.

**Tech Stack:** Vue 3, TypeScript, Rsbuild, `@module-federation/rsbuild-plugin`, Tailwind CSS v4, TanStack Vue Query, vue-router, `@martin/common` (file: dep), `@martin/components` (file: dep)

---

## File Map

| File | Purpose |
|------|---------|
| `package.json` | pnpm project, file: deps for @martin/common & @martin/components |
| `rsbuild.config.ts` | MF remote config — exposes WorkspaceApp on port 3001 |
| `tsconfig.json` | TypeScript config matching shell's conventions |
| `index.html` | Standalone dev entry point |
| `.env` / `.env.example` | `VITE_API_URL=http://localhost:8000` |
| `src/main.ts` | Standalone dev bootstrap — creates app + router |
| `src/WorkspaceApp.vue` | MF-exposed root — mounts memory router, syncs shell URL |
| `src/router.ts` | `createMemoryHistory()` router with 2 routes |
| `src/css/globals.css` | Design tokens (copy of shell globals) |
| `src/case/useCaseWorkspace.ts` | Fetches `/cases/:id`, returns `CaseDetail` |
| `src/case/CaseWorkspacePage.vue` | 60/40 split: PDF iframe + in-memory notes panel |
| `src/briefcase/useBriefcaseWorkspace.ts` | Fetches `/briefcases/:id`, returns `Briefcase` |
| `src/briefcase/BriefcaseWorkspacePage.vue` | 25/75 split: case sidebar + PDF iframe + notes |

---

## Task 1: Project scaffold — package.json, tsconfig, rsbuild config

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `rsbuild.config.ts`
- Create: `.env`
- Create: `.env.example`
- Create: `index.html`

- [ ] **Step 1: Create `package.json`**

```json
{
  "name": "martin-workspace-module",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "rsbuild dev",
    "build": "rsbuild build",
    "preview": "rsbuild preview",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "@martin/common": "file:../martin-shell/packages/common",
    "@martin/components": "file:../martin-shell/packages/components",
    "@tanstack/vue-query": "^5.0.0",
    "lucide-vue-next": "^0.400.0",
    "tailwindcss": "^4.0.0",
    "vue": "^3.5.0",
    "vue-router": "^4.0.0"
  },
  "devDependencies": {
    "@module-federation/rsbuild-plugin": "^0.9.0",
    "@rsbuild/core": "^1.0.0",
    "@rsbuild/plugin-vue": "^1.0.0",
    "@tailwindcss/postcss": "^4.0.0",
    "typescript": "^5.0.0",
    "vue-tsc": "^2.0.0"
  }
}
```

- [ ] **Step 2: Create `tsconfig.json`**

```json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    "incremental": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "useDefineForClassFields": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ESNext",
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "jsxImportSource": "vue",
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*", "env.d.ts"]
}
```

- [ ] **Step 3: Create `rsbuild.config.ts`**

```typescript
import { pluginModuleFederation } from '@module-federation/rsbuild-plugin'
import { defineConfig } from '@rsbuild/core'
import { pluginVue } from '@rsbuild/plugin-vue'

export default defineConfig({
  html: { title: 'Martin Workspace', template: './index.html' },
  source: { entry: { index: './src/main.ts' }, envPrefix: ['PUBLIC_', 'VITE_'] },
  server: { port: 3001 },
  dev: { lazyCompilation: false },
  plugins: [
    pluginVue(),
    pluginModuleFederation({
      name: 'martin_workspace',
      exposes: {
        './WorkspaceApp': './src/WorkspaceApp.vue',
      },
      dts: false,
      shared: {
        vue: { singleton: true, eager: true },
        'vue-router': { singleton: true, eager: true },
      },
    }),
  ],
})
```

- [ ] **Step 4: Create `index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Martin Workspace</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 5: Create `.env` and `.env.example`**

Both files identical:
```
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 6: Create `env.d.ts`**

```typescript
/// <reference types="@rsbuild/core/types" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

- [ ] **Step 7: Install dependencies**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
pnpm install
```

Expected: `node_modules/` created, `@martin/common` and `@martin/components` symlinked from `../martin-shell/packages/`.

- [ ] **Step 8: Commit**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
git add package.json tsconfig.json rsbuild.config.ts index.html .env .env.example env.d.ts
git commit -m "chore: scaffold project — package.json, tsconfig, rsbuild MF remote config"
```

---

## Task 2: Global CSS and router

**Files:**
- Create: `src/css/globals.css`
- Create: `src/router.ts`

- [ ] **Step 1: Create `src/css/globals.css`**

```css
@import "tailwindcss";

/* ── Design tokens ─────────────────────────────────────── */
:root {
  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system,
    BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial;

  --neutral-0:   #ffffff;
  --neutral-50:  #f9fafb;
  --neutral-100: #f3f4f6;
  --neutral-200: #e5e7eb;
  --neutral-300: #d1d5db;
  --neutral-400: #9ca3af;
  --neutral-500: #6b7280;
  --neutral-600: #4b5563;
  --neutral-700: #374151;
  --neutral-800: #111827;
  --neutral-900: #0b1220;

  --accent-300: #93c5fd;
  --accent-400: #60a5fa;
  --accent-500: #3b82f6;
  --accent-600: #2563eb;
  --accent-700: #1d4ed8;

  --bg:                var(--neutral-0);
  --bg-subtle:         var(--neutral-50);
  --surface:           var(--neutral-0);
  --surface-raised:    var(--neutral-0);
  --border:            var(--neutral-200);
  --divider:           var(--neutral-300);
  --fg:                var(--neutral-800);
  --fg-muted:          var(--neutral-500);
  --primary:           var(--accent-600);
  --primary-hover:     var(--accent-700);
  --primary-fg:        #ffffff;
  --ring:              var(--accent-500);

  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 18px;

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md: 0 8px 24px rgba(0,0,0,0.10);
}

.dark {
  --bg:             #0b1220;
  --bg-subtle:      #0f172a;
  --surface:        #111827;
  --surface-raised: #162034;
  --border:         #243244;
  --divider:        #1f2a3a;
  --fg:             #f5f7fa;
  --fg-muted:       #b8bdc6;
  --primary:        var(--accent-400);
  --primary-hover:  var(--accent-300);
  --primary-fg:     #0b1220;
}

@theme inline {
  --font-sans: var(--font-sans);
  --color-bg:             var(--bg);
  --color-bg-subtle:      var(--bg-subtle);
  --color-surface:        var(--surface);
  --color-surface-raised: var(--surface-raised);
  --color-border:         var(--border);
  --color-divider:        var(--divider);
  --color-fg:             var(--fg);
  --color-fg-muted:       var(--fg-muted);
  --color-primary:        var(--primary);
  --color-primary-hover:  var(--primary-hover);
  --color-primary-fg:     var(--primary-fg);
  --radius-sm: var(--radius-sm);
  --radius-md: var(--radius-md);
  --radius-lg: var(--radius-lg);
  --shadow-sm: var(--shadow-sm);
  --shadow-md: var(--shadow-md);
}

html {
  font-family: var(--font-sans);
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}

body {
  background: var(--bg);
  color: var(--fg);
  margin: 0;
}

:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.35);
  border-radius: 10px;
}
```

- [ ] **Step 2: Create `src/router.ts`**

```typescript
import { createRouter, createMemoryHistory } from 'vue-router'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    {
      path: '/workspace/cases/:id',
      component: () => import('./case/CaseWorkspacePage.vue'),
    },
    {
      path: '/workspace/briefcases/:id',
      component: () => import('./briefcase/BriefcaseWorkspacePage.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('./case/CaseWorkspacePage.vue'),
    },
  ],
})

export default router
```

- [ ] **Step 3: Commit**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
git add src/css/globals.css src/router.ts
git commit -m "feat: add global CSS tokens and memory router"
```

---

## Task 3: WorkspaceApp root component and standalone dev entry

**Files:**
- Create: `src/WorkspaceApp.vue`
- Create: `src/main.ts`

- [ ] **Step 1: Create `src/WorkspaceApp.vue`**

This is the MF-exposed entry. It mounts its own router and watches the shell's `useRoute().path` to keep them in sync. When running standalone (no shell), there's no outer route to watch, so it falls back to the current memory location.

```vue
<script setup lang="ts">
import { watch, onMounted } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { VueQueryPlugin } from '@tanstack/vue-query'
import router from './router.js'
import './css/globals.css'

// When loaded as an MF remote, vue-router is a shared singleton — the shell's
// router is the same instance. We watch the shell's current route and push
// matching path changes into our memory router so the correct page renders.
let shellRoute: ReturnType<typeof useRoute> | null = null
try {
  shellRoute = useRoute()
} catch {
  // No outer router context (standalone dev) — memory router handles navigation
}

const memoryRouter = router

function syncPath(path: string) {
  if (path.startsWith('/workspace/')) {
    memoryRouter.push(path).catch(() => {})
  }
}

if (shellRoute) {
  onMounted(() => syncPath(shellRoute!.path))
  watch(() => shellRoute!.path, syncPath)
}
</script>

<template>
  <RouterView :router="router" />
</template>
```

- [ ] **Step 2: Create `src/main.ts`** (standalone dev bootstrap only)

```typescript
import { createApp } from 'vue'
import { VueQueryPlugin } from '@tanstack/vue-query'
import { createRouter, createWebHistory } from 'vue-router'
import WorkspaceApp from './WorkspaceApp.vue'

// Standalone dev: use a real web history router so the URL bar works normally.
// This router is only used when running `pnpm dev` directly (not as MF remote).
const devRouter = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/:pathMatch(.*)*', component: WorkspaceApp }],
})

const app = createApp(WorkspaceApp)
app.use(devRouter)
app.use(VueQueryPlugin)
app.mount('#app')
```

- [ ] **Step 3: Verify the dev server starts**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
pnpm dev
```

Expected: Rsbuild starts on http://localhost:3001 with no TypeScript errors. Browser shows a blank page (no pages implemented yet) — this is correct.

- [ ] **Step 4: Commit**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
git add src/WorkspaceApp.vue src/main.ts
git commit -m "feat: add WorkspaceApp MF entry and standalone dev bootstrap"
```

---

## Task 4: Case workspace — composable and page

**Files:**
- Create: `src/case/useCaseWorkspace.ts`
- Create: `src/case/CaseWorkspacePage.vue`

The `CaseDetail` type from `@martin/common` (`src/types/search.ts`) has these fields:
```typescript
interface CaseData {
  id: number
  case_name: string
  court: string
  date_decided: string | null
  citation: string | null
  summary: string | null
  pdf_url: string | null
  saflii_url: string
}
```

The backend's `GET /cases/:id` returns a superset of `CaseData` (adds `full_text`, `pdf_storage_key`) — use `CaseData` as the response type since it's what `@martin/common` exports.

- [ ] **Step 1: Create `src/case/useCaseWorkspace.ts`**

```typescript
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from '@martin/common'
import type { CaseData } from '@martin/common'
import type { Ref } from 'vue'

export function useCaseWorkspace(id: Ref<string>) {
  return useQuery({
    queryKey: ['case', id],
    queryFn: () => apiFetch<CaseData>(`/cases/${id.value}`),
    enabled: () => !!id.value,
  })
}
```

- [ ] **Step 2: Create `src/case/CaseWorkspacePage.vue`**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCaseWorkspace } from './useCaseWorkspace.js'

const route = useRoute()
const id = computed(() => route.params.id as string)
const { data: caseData, isPending, isError } = useCaseWorkspace(id)

const notes = ref('')
</script>

<template>
  <div class="workspace-root">
    <div v-if="isPending" class="workspace-loading">
      <div class="spinner" />
    </div>

    <div v-else-if="isError" class="workspace-error">
      <p>Failed to load case. Please try again.</p>
    </div>

    <template v-else-if="caseData">
      <header class="workspace-header">
        <div class="workspace-header-meta">
          <h1 class="workspace-title">{{ caseData.case_name }}</h1>
          <div class="workspace-meta">
            <span>{{ caseData.court }}</span>
            <span v-if="caseData.date_decided">· {{ caseData.date_decided }}</span>
            <span v-if="caseData.citation">· {{ caseData.citation }}</span>
          </div>
        </div>
        <a
          v-if="caseData.saflii_url"
          :href="caseData.saflii_url"
          target="_blank"
          rel="noopener noreferrer"
          class="saflii-link"
        >
          View on SAFLII ↗
        </a>
      </header>

      <div class="workspace-body">
        <!-- PDF viewer -->
        <div class="pdf-pane">
          <iframe
            v-if="caseData.pdf_url"
            :src="caseData.pdf_url"
            class="pdf-frame"
            title="Case PDF"
          />
          <div v-else class="pdf-unavailable">
            <p>No PDF available for this case.</p>
            <a
              v-if="caseData.saflii_url"
              :href="caseData.saflii_url"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on SAFLII ↗
            </a>
          </div>
        </div>

        <!-- Notes panel -->
        <div class="notes-pane">
          <div class="notes-header">Notes</div>
          <textarea
            v-model="notes"
            class="notes-textarea"
            placeholder="Write notes about this case…"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.workspace-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg);
  color: var(--fg);
}

.workspace-loading,
.workspace-error {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.workspace-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}

.workspace-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem;
  color: var(--fg);
}

.workspace-meta {
  font-size: 0.8125rem;
  color: var(--fg-muted);
  display: flex;
  gap: 0.25rem;
}

.saflii-link {
  font-size: 0.8125rem;
  color: var(--primary);
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}
.saflii-link:hover { text-decoration: underline; }

.workspace-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.pdf-pane {
  flex: 0 0 60%;
  border-right: 1px solid var(--border);
  overflow: hidden;
  display: flex;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-unavailable {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  flex: 1;
  color: var(--fg-muted);
  font-size: 0.875rem;
}

.notes-pane {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notes-header {
  padding: 0.75rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--fg-muted);
  border-bottom: 1px solid var(--border);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}

.notes-textarea {
  flex: 1;
  width: 100%;
  padding: 1rem;
  border: none;
  outline: none;
  resize: none;
  font-family: var(--font-sans);
  font-size: 0.9375rem;
  line-height: 1.6;
  background: var(--bg-subtle);
  color: var(--fg);
  box-sizing: border-box;
}

.notes-textarea::placeholder { color: var(--fg-muted); }
</style>
```

- [ ] **Step 3: Verify type-check passes**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
pnpm type-check
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
git add src/case/useCaseWorkspace.ts src/case/CaseWorkspacePage.vue
git commit -m "feat: add CaseWorkspacePage with PDF viewer and notes panel"
```

---

## Task 5: Briefcase workspace — composable and page

**Files:**
- Create: `src/briefcase/useBriefcaseWorkspace.ts`
- Create: `src/briefcase/BriefcaseWorkspacePage.vue`

The `Briefcase` type from `@martin/common` (`src/types/briefcase.ts`):
```typescript
interface Briefcase {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
  reasons: Reason[]  // reasons have .cases: ReasonCase[]
}

interface ReasonCase {
  id: string
  case_id: number
  content: string | null
  order: number
  created_at: string
  case_name: string | null
  court: string | null
  citation: string | null
  date_decided: string | null
}
```

Note: `ReasonCase` does not include `pdf_url`. After selecting a case from the sidebar, a second fetch to `/cases/:case_id` is needed to get the PDF URL.

- [ ] **Step 1: Create `src/briefcase/useBriefcaseWorkspace.ts`**

```typescript
import { useQuery } from '@tanstack/vue-query'
import { apiFetch } from '@martin/common'
import type { Briefcase, CaseData } from '@martin/common'
import type { Ref } from 'vue'

export function useBriefcaseWorkspace(id: Ref<string>) {
  return useQuery({
    queryKey: ['briefcase', id],
    queryFn: () => apiFetch<Briefcase>(`/briefcases/${id.value}`),
    enabled: () => !!id.value,
  })
}

export function useBriefcaseCase(caseId: Ref<number | null>) {
  return useQuery({
    queryKey: ['case', caseId],
    queryFn: () => apiFetch<CaseData>(`/cases/${caseId.value}`),
    enabled: () => caseId.value !== null,
  })
}
```

- [ ] **Step 2: Create `src/briefcase/BriefcaseWorkspacePage.vue`**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { ReasonCase } from '@martin/common'
import { useBriefcaseWorkspace, useBriefcaseCase } from './useBriefcaseWorkspace.js'

const route = useRoute()
const briefcaseId = computed(() => route.params.id as string)
const { data: briefcase, isPending, isError } = useBriefcaseWorkspace(briefcaseId)

// Flatten all cases across all reasons, deduplicated by case_id
const allCases = computed<ReasonCase[]>(() => {
  if (!briefcase.value) return []
  const seen = new Set<number>()
  const result: ReasonCase[] = []
  for (const reason of briefcase.value.reasons) {
    for (const c of reason.cases) {
      if (!seen.has(c.case_id)) {
        seen.add(c.case_id)
        result.push(c)
      }
    }
  }
  return result
})

const selectedCaseId = ref<number | null>(null)
const selectedCaseIdRef = computed(() => selectedCaseId.value)
const { data: selectedCase, isPending: caseLoading } = useBriefcaseCase(selectedCaseIdRef)

const notes = ref('')

function selectCase(c: ReasonCase) {
  selectedCaseId.value = c.case_id
  notes.value = c.content ?? ''
}
</script>

<template>
  <div class="workspace-root">
    <div v-if="isPending" class="workspace-loading">
      <div class="spinner" />
    </div>

    <div v-else-if="isError" class="workspace-error">
      <p>Failed to load briefcase. Please try again.</p>
    </div>

    <template v-else-if="briefcase">
      <header class="workspace-header">
        <h1 class="workspace-title">{{ briefcase.name }}</h1>
        <p v-if="briefcase.description" class="workspace-description">
          {{ briefcase.description }}
        </p>
      </header>

      <div class="workspace-body">
        <!-- Case list sidebar -->
        <aside class="sidebar">
          <div class="sidebar-heading">Cases ({{ allCases.length }})</div>
          <ul class="case-list">
            <li
              v-for="c in allCases"
              :key="c.case_id"
              class="case-item"
              :class="{ 'case-item--active': selectedCaseId === c.case_id }"
              @click="selectCase(c)"
            >
              <div class="case-item-name">{{ c.case_name ?? `Case #${c.case_id}` }}</div>
              <div class="case-item-meta">
                <span v-if="c.court">{{ c.court }}</span>
                <span v-if="c.date_decided">· {{ c.date_decided }}</span>
              </div>
            </li>
          </ul>
          <div v-if="allCases.length === 0" class="sidebar-empty">
            No cases in this briefcase yet.
          </div>
        </aside>

        <!-- PDF + notes -->
        <div class="main-pane">
          <div v-if="!selectedCaseId" class="select-prompt">
            <p>Select a case from the sidebar to view its document.</p>
          </div>

          <template v-else>
            <div v-if="caseLoading" class="workspace-loading">
              <div class="spinner" />
            </div>

            <template v-else-if="selectedCase">
              <div class="pdf-pane">
                <iframe
                  v-if="selectedCase.pdf_url"
                  :src="selectedCase.pdf_url"
                  class="pdf-frame"
                  :title="selectedCase.case_name"
                />
                <div v-else class="pdf-unavailable">
                  <p>No PDF available for this case.</p>
                  <a
                    v-if="selectedCase.saflii_url"
                    :href="selectedCase.saflii_url"
                    target="_blank"
                    rel="noopener noreferrer"
                  >View on SAFLII ↗</a>
                </div>
              </div>

              <div class="notes-pane">
                <div class="notes-header">Notes</div>
                <textarea
                  v-model="notes"
                  class="notes-textarea"
                  placeholder="Write notes about this case…"
                />
              </div>
            </template>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.workspace-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg);
  color: var(--fg);
}

.workspace-loading,
.workspace-error,
.select-prompt {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--fg-muted);
  font-size: 0.875rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.workspace-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}

.workspace-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: var(--fg);
}

.workspace-description {
  font-size: 0.8125rem;
  color: var(--fg-muted);
  margin: 0.25rem 0 0;
}

.workspace-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  flex: 0 0 25%;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-heading {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--fg-muted);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.case-list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
}

.case-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.15s;
}
.case-item:hover { background: var(--bg-subtle); }
.case-item--active { background: var(--bg-subtle); border-left: 3px solid var(--primary); }

.case-item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--fg);
  margin-bottom: 0.2rem;
  line-height: 1.3;
}

.case-item-meta {
  font-size: 0.75rem;
  color: var(--fg-muted);
}

.sidebar-empty {
  padding: 1.5rem 1rem;
  font-size: 0.875rem;
  color: var(--fg-muted);
  text-align: center;
}

/* Main pane */
.main-pane {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.pdf-pane {
  flex: 0 0 60%;
  border-right: 1px solid var(--border);
  overflow: hidden;
  display: flex;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-unavailable {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  flex: 1;
  color: var(--fg-muted);
  font-size: 0.875rem;
}

.notes-pane {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
}

.notes-header {
  padding: 0.75rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--fg-muted);
  border-bottom: 1px solid var(--border);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}

.notes-textarea {
  flex: 1;
  width: 100%;
  padding: 1rem;
  border: none;
  outline: none;
  resize: none;
  font-family: var(--font-sans);
  font-size: 0.9375rem;
  line-height: 1.6;
  background: var(--bg-subtle);
  color: var(--fg);
  box-sizing: border-box;
}
.notes-textarea::placeholder { color: var(--fg-muted); }
</style>
```

- [ ] **Step 3: Verify type-check passes**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
pnpm type-check
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
git add src/briefcase/useBriefcaseWorkspace.ts src/briefcase/BriefcaseWorkspacePage.vue
git commit -m "feat: add BriefcaseWorkspacePage with sidebar, PDF viewer, and notes"
```

---

## Task 6: Wire WorkspaceApp with VueQueryPlugin and verify MF integration

The `WorkspaceApp.vue` needs `VueQueryPlugin` installed on the app instance it mounts. When loaded as an MF remote it doesn't call `createApp` — so VueQueryPlugin must be provided via the component itself using `app.use` on the Vue app instance that hosts it. The cleanest pattern is to use `provide`/`inject` via a wrapper, but since the shell already calls `app.use(VueQueryPlugin)`, the shared singleton means TanStack Query's context is already available. No change needed to `WorkspaceApp.vue` — this task verifies the integration works end-to-end.

**Files:**
- Modify: `src/WorkspaceApp.vue` — add VueQueryPlugin provision for standalone mode

- [ ] **Step 1: Update `src/WorkspaceApp.vue` to provide VueQueryPlugin when running standalone**

Replace the full file contents:

```vue
<script setup lang="ts">
import { watch, onMounted, getCurrentInstance } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { VueQueryPlugin } from '@tanstack/vue-query'
import router from './router.js'
import './css/globals.css'

// In standalone dev mode the app is created in main.ts and VueQueryPlugin is
// registered there. When loaded as an MF remote the shell already registers it
// on the shared Vue app. Either way, queries work without extra setup here.

let shellRoute: ReturnType<typeof useRoute> | null = null
try {
  shellRoute = useRoute()
} catch {
  // No outer router context — standalone dev, memory router handles navigation
}

function syncPath(path: string) {
  if (path.startsWith('/workspace/')) {
    router.push(path).catch(() => {})
  }
}

if (shellRoute) {
  onMounted(() => syncPath(shellRoute!.path))
  watch(() => shellRoute!.path, syncPath)
}
</script>

<template>
  <RouterView :router="router" />
</template>
```

- [ ] **Step 2: Start both servers and test integration**

Terminal 1 (workspace remote):
```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
pnpm dev
```

Terminal 2 (shell):
```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell
pnpm dev
```

Navigate to `http://localhost:3000/workspace/cases/1` (replace `1` with a real case ID from your DB).

Expected:
- No `ERR_CONNECTION_REFUSED` for `localhost:3001/mf-manifest.json` in console
- `CaseWorkspacePage` renders — either the PDF or the "No PDF available" message
- No Vue warnings about missing router context

- [ ] **Step 3: Commit**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-workspace-module
git add src/WorkspaceApp.vue
git commit -m "fix: ensure WorkspaceApp route sync works in both standalone and MF contexts"
```

---

## Task 7: Add navigation links in the shell to the workspace

**Files:**
- Modify: `/Users/BrianMkhabela/Projects/op/martin-shell/apps/shell/src/search/CaseDetail.vue`

The shell's `CaseDetail.vue` shows a case — add a "Open in Workspace" button that navigates to `/workspace/cases/:id`.

- [ ] **Step 1: Read the current CaseDetail.vue**

```bash
cat /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell/src/search/CaseDetail.vue
```

- [ ] **Step 2: Add "Open in Workspace" RouterLink**

Find the section in `CaseDetail.vue` where the case header/actions are rendered. Add a `RouterLink` alongside the existing action buttons:

```vue
<RouterLink
  :to="`/workspace/cases/${caseData.id}`"
  class="open-workspace-btn"
>
  Open in Workspace
</RouterLink>
```

Add the style:
```css
.open-workspace-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  color: var(--fg);
  text-decoration: none;
  transition: background 0.15s;
}
.open-workspace-btn:hover { background: var(--bg-subtle); }
```

- [ ] **Step 3: Verify shell type-check**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell/apps/shell
pnpm type-check
```

Expected: No errors.

- [ ] **Step 4: Commit to martin-shell**

```bash
cd /Users/BrianMkhabela/Projects/op/martin-shell
git add apps/shell/src/search/CaseDetail.vue
git commit -m "feat: add Open in Workspace link to CaseDetail"
```

---

## Self-Review Notes

**Spec coverage check:**
- ✅ Standalone pnpm repo at correct path
- ✅ `file:` deps for `@martin/common` and `@martin/components`
- ✅ MF remote named `martin_workspace`, exposes `./WorkspaceApp`, port 3001
- ✅ Shared `vue` and `vue-router` singletons matching shell config
- ✅ `createMemoryHistory()` router syncing with shell URL
- ✅ `/workspace/cases/:id` → `CaseWorkspacePage` (PDF iframe + notes)
- ✅ `/workspace/briefcases/:id` → `BriefcaseWorkspacePage` (sidebar + PDF + notes)
- ✅ Same design tokens as shell
- ✅ No new backend endpoints
- ✅ Standalone dev mode works independently

**Type consistency check:**
- `useCaseWorkspace` returns `useQuery` with `CaseData` — used as `data` in `CaseWorkspacePage` ✅
- `useBriefcaseWorkspace` returns `Briefcase`, `useBriefcaseCase` returns `CaseData` — both used correctly in `BriefcaseWorkspacePage` ✅
- `selectedCaseIdRef` is `Ref<number | null>` matching `useBriefcaseCase` parameter type ✅
