# CI/CD Pipeline Design — 2026-03-02

## Approach

Option A: **GitHub Actions for CI + Vercel GitHub Integration for deployment.**

- GitHub Actions runs type-check, lint, and build on every push and PR — fast feedback before Vercel starts.
- Vercel's native GitHub integration handles all deployments: production on `main`, preview deploys on PR branches.

## GitHub Actions CI Workflow

**File:** `.github/workflows/ci.yml`

**Triggers:** push to `main`, pull requests targeting `main`

**Job:** `ci` on `ubuntu-latest`

Steps:
1. Checkout repo
2. Setup pnpm 10.26.2 + Node 20 with pnpm store cache
3. `pnpm install --frozen-lockfile`
4. `pnpm type-check` — `vue-tsc --noEmit` across all packages
5. `pnpm lint` — ESLint across all packages
6. `pnpm build` — `rsbuild build` for the shell app with stub env vars

Env vars used in CI build (stubs only — not real values):
- `VITE_API_URL=https://api.example.com`
- `WORKSPACE_URL=https://workspace.example.com`

## Vercel Project

**Project name:** `martin-shell`
**Repo:** `TlangelaniBrian/martin-shell`
**GitHub integration:** native (Vercel app installed on repo)

| Setting | Value |
|---|---|
| Framework preset | Other |
| Root directory | `.` |
| Install command | `pnpm install --frozen-lockfile` |
| Build command | `pnpm --filter @martin/shell build` |
| Output directory | `apps/shell/dist` |

**Deployment targets:**
- `main` branch → production
- PR branches → preview (URL posted as PR comment)

**Environment variables** (set in Vercel dashboard):

| Variable | Environments |
|---|---|
| `VITE_API_URL` | Production, Preview |
| `WORKSPACE_URL` | Production, Preview |

Values are set via Vercel dashboard once backends are deployed. Placeholder values suffice until then.

## What is NOT in scope

- Deployment of the FastAPI backend (separate repo)
- Deployment of the `martin_workspace` MFE remote (separate repo)
- E2E / integration tests (no test suite exists yet)
