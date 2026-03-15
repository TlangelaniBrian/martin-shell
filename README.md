# martin-mfe

Micro-frontend shell workspace for the martin legal research platform.

## Overview

A pnpm monorepo that builds the Vue 3 + Module Federation frontend layer for martin. Shared packages provide the API client, auth state, TypeScript config, and UI components used across all MFE modules.

## Stack

- **Framework:** Vue 3 · TypeScript
- **Build:** Rsbuild · Module Federation
- **UI:** shadcn-vue
- **State:** TanStack Store
- **Monorepo:** pnpm workspaces

## Workspace Packages

| Package | Description | Status |
|---------|-------------|--------|
| `@martin/tsconfig` | Shared TypeScript config | ✅ Done |
| `@martin/eslint-config` | Shared ESLint rules | ✅ Done |
| `@martin/common` | Types, `apiFetch`, auth store | ✅ Done |
| `@martin/components` | shadcn-vue base components | ✅ Done |
| `apps/shell` | Rsbuild + Module Federation host | ⬜ In progress |

## Getting Started

```bash
pnpm install
pnpm dev
```

## Structure

```
martin-mfe/
└── martin-shell/
    ├── apps/
    │   └── shell/          # Module Federation host app
    └── packages/
        ├── common/         # Shared API client + auth store
        ├── components/     # Shared UI components
        ├── tsconfig/       # Shared TS config
        └── eslint-config/  # Shared ESLint config
```

## Related

- [martin](../martin) — The FastAPI backend this shell connects to
