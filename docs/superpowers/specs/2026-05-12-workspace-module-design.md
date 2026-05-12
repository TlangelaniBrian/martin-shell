# Workspace Module — Design Spec

**Date:** 2026-05-12
**Status:** Approved

---

## Overview

A new Module Federation remote app (`martin_workspace`) that lives in its own repo at `/Users/BrianMkhabela/Projects/op/martin-workspace-module`. It exposes a single `WorkspaceApp` component on port 3001, which the shell loads at the catch-all route `/workspace/:pathMatch(.*)* `.

The workspace is a document workspace: it opens case PDFs alongside an annotation/notes panel. It is reachable from two entry points:

- `/workspace/cases/:id` — a single case PDF + notes
- `/workspace/briefcases/:id` — a briefcase's case list sidebar + PDF + notes

---

## Repository

- **Location:** `/Users/BrianMkhabela/Projects/op/martin-workspace-module`
- **Type:** Standalone pnpm project (not a monorepo)
- **Shared packages:** `@martin/common` and `@martin/components` installed as `file:` path dependencies pointing at `../martin-shell/packages/common` and `../martin-shell/packages/components`

---

## Module Federation Config

- **Remote name:** `martin_workspace`
- **Exposed entry:** `./WorkspaceApp` → `src/WorkspaceApp.vue`
- **Port:** 3001
- **Shared singletons:** `vue` (singleton, eager), `vue-router` (singleton, eager) — mirrors shell config exactly
- **Build tool:** Rsbuild + `@module-federation/rsbuild-plugin`

---

## Stack

| Concern | Choice |
|---------|--------|
| Framework | Vue 3 + TypeScript |
| Build | Rsbuild |
| Styling | Tailwind CSS v4 (same globals/tokens as shell) |
| Data fetching | TanStack Vue Query + `@martin/common` `apiFetch` |
| Routing | `vue-router` with `createMemoryHistory()` |
| Auth | Shared cookie session — no extra login needed |

---

## Internal Routing

The workspace uses `createMemoryHistory()` so the shell owns the real URL bar. `WorkspaceApp.vue` watches `useRoute().path` from the shared router singleton and pushes matching path changes into the internal memory router.

| Route | Component |
|-------|-----------|
| `/workspace/cases/:id` | `CaseWorkspacePage.vue` |
| `/workspace/briefcases/:id` | `BriefcaseWorkspacePage.vue` |

---

## Pages & Components

### CaseWorkspacePage
- Fetches `/cases/:id` via `useCaseWorkspace.ts`
- Layout: PDF viewer (left, ~60%) + notes panel (right, ~40%)
- PDF rendered via `<iframe :src="pdfUrl">` (R2 URL from case detail response)
- Notes: in-memory state (no persistence for standalone case view in this iteration)

### BriefcaseWorkspacePage
- Fetches `/briefcases/:id` via `useBriefcaseWorkspace.ts`
- Layout: sidebar case list (left, ~25%) + PDF viewer + notes (right, ~75%)
- Selecting a case from the sidebar updates the PDF panel
- Notes: existing briefcase grounds/reasons API for persistence

---

## File Structure

```
martin-workspace-module/
├── src/
│   ├── WorkspaceApp.vue
│   ├── main.ts                        # Standalone dev entry
│   ├── router.ts
│   ├── css/
│   │   └── globals.css
│   ├── case/
│   │   ├── CaseWorkspacePage.vue
│   │   └── useCaseWorkspace.ts
│   └── briefcase/
│       ├── BriefcaseWorkspacePage.vue
│       └── useBriefcaseWorkspace.ts
├── index.html
├── package.json
├── rsbuild.config.ts
├── tsconfig.json
├── .env
└── .env.example
```

---

## Data Flow

1. User navigates to `/workspace/cases/123` in the shell
2. Shell's catch-all route renders `workspace-host.vue`, which lazy-loads `martin_workspace/WorkspaceApp` from port 3001
3. `WorkspaceApp` syncs the path into its memory router → renders `CaseWorkspacePage`
4. `useCaseWorkspace` calls `apiFetch('/cases/123')` — auth cookies already present from shell login
5. Response includes PDF URL (R2) → rendered in `<iframe>`

---

## Backend

No new endpoints required. Uses existing:
- `GET /cases/:id` — case detail + PDF URL
- `GET /briefcases/:id` — briefcase with cases list

---

## Local Development

Running `pnpm dev` inside `martin-workspace-module` starts a standalone app on port 3001 that can be developed independently of the shell. The shell must also be running for the federated integration to work.
