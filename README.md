# martin

Legal research SaaS for South African lawyers. Monorepo containing the Vue 3 frontend and FastAPI backend.

## Stack

### Frontend
- **Framework:** Vue 3 · TypeScript
- **Build:** Rsbuild · Module Federation
- **UI:** shadcn-vue · Tailwind CSS
- **State:** TanStack Store (auth) · TanStack Vue Query
- **Monorepo:** pnpm workspaces

### Backend
- **Framework:** FastAPI · Python 3.12
- **Database:** PostgreSQL (pgvector) · SQLAlchemy async · Alembic
- **Auth:** fastapi-users · JWT cookies · Google OAuth · Microsoft OAuth
- **AI:** Anthropic · OpenAI · Google Gemini · DeepSeek (per-user provider config)
- **Search:** pgvector cosine + tsvector keyword, RRF merge · Voyage AI embeddings
- **Storage:** Cloudflare R2 (PDF storage)

## Workspace Structure

```
martin-shell/
├── apps/
│   └── shell/              # Vue 3 Module Federation host app
├── packages/
│   ├── common/             # apiFetch, auth store, shared types
│   ├── components/         # shadcn-vue base components
│   ├── tsconfig/           # Shared TS config
│   └── eslint-config/      # Shared ESLint rules
└── backend/                # FastAPI backend
    ├── app/
    │   ├── auth/           # JWT + OAuth + email verification
    │   ├── cases/          # Case CRUD + AI chat endpoint
    │   ├── briefcases/     # Briefcase workspace + AI generation
    │   ├── search/         # Hybrid search (pgvector + tsvector)
    │   ├── ai_settings/    # Per-user AI provider config
    │   └── models/         # SQLAlchemy models
    └── tests/              # pytest test suite
```

## Frontend Pages

| Route | Description |
|-------|-------------|
| `/` | Home |
| `/search` | Split-screen case search with CaseDetail panel + AI chat |
| `/sign-in`, `/sign-up` | Auth pages |
| `/auth/callback/google` | OAuth callback |
| `/auth/forgot-password` | Password reset request |
| `/auth/verify` | Email verification |
| `/account` | Profile, security, AI provider settings, POPIA |
| `/briefcases` | Briefcase list |
| `/briefcases/:id` | Briefcase workspace (grounds, cases, AI generation, version history) |

## Backend API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register |
| POST | `/auth/login` | Login (sets cookies) |
| POST | `/auth/logout` | Logout |
| POST | `/auth/refresh` | Refresh access token |
| GET/PATCH | `/users/me/ai-settings/` | Per-user AI provider config |
| GET | `/search/` | Hybrid case search |
| GET | `/search/autocomplete` | Case name autocomplete |
| GET | `/cases/` | List cases |
| GET | `/cases/{id}` | Get case detail |
| POST | `/cases/{id}/chat` | AI chat about a case (auth required) |
| GET/POST | `/briefcases/` | List / create briefcases |
| GET/PATCH/DELETE | `/briefcases/{id}` | Briefcase CRUD |
| POST | `/briefcases/{id}/reasons/{rid}/generate` | AI generate argument for a ground |
| POST | `/briefcases/{id}/reasons/{rid}/cases/{eid}/generate` | AI generate case note |

## Getting Started

### Frontend

```bash
pnpm install
pnpm dev
```

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, SECRET_KEY, etc.
uvicorn app.main:app --reload
```

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

## Environment Variables (backend/.env)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | JWT signing secret |
| `RESEND_API_KEY` | Resend API key for transactional email |
| `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` | Google OAuth credentials |
| `MICROSOFT_OAUTH_CLIENT_ID` / `_SECRET` | Microsoft OAuth credentials |
| `VOYAGE_API_KEY` | Voyage AI API key for embeddings |
| `CLAUDE_API_KEY` | Fallback Anthropic key for AI generation |
| `R2_ENDPOINT_URL` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` / `R2_BUCKET_NAME` | Cloudflare R2 for PDF storage |
| `FRONTEND_URL` | CORS origin (e.g. `http://localhost:3000`) |

## Key Design Decisions

- **"Grounds" vs "reasons":** The UI uses "Grounds" (correct legal term). The DB and API use "reasons" everywhere — do not rename API fields.
- **Auth pattern:** `useAuthStore()` returns `Readonly<Ref<AuthState>>`. Use `auth.value.user` in `<script setup>`, `auth.user` in `<template>` (Vue auto-unwraps).
- **AI chat:** Stateless — the frontend maintains conversation history in memory and sends the full history with each request. No server-side persistence.
- **AI provider resolution:** `_resolve_ai()` checks the user's configured provider first, falls back to the global `CLAUDE_API_KEY` env var.
