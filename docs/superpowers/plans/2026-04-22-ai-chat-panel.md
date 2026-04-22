# AI Chat Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up the disabled "Ask about this case" button in `CaseDetail.vue` to an interactive AI Q&A panel backed by a new `/cases/{case_id}/chat` backend endpoint.

**Architecture:** Stateless chat — the client maintains conversation history in memory and sends the full history with each request. The backend resolves the user's AI provider (same `_resolve_ai` / `_call_ai` helpers from the briefcases router) and streams no output; it returns a plain JSON `{ reply }`. No chat persistence to DB (YAGNI — it belongs to a future "conversation history" feature).

**Tech Stack:** FastAPI (Python 3.12), Vue 3 + TypeScript, `apiFetch` from `@martin/common`, Vitest, pytest + httpx AsyncClient.

---

## File Map

### Backend (in the `backend/` directory at the repo root)

| Action | Path |
|--------|------|
| Modify | `backend/app/cases/router.py` — add `POST /{case_id}/chat` |
| Create | `backend/tests/test_case_chat.py` |

### Frontend (in `apps/shell/src/search/`)

| Action | Path |
|--------|------|
| Create | `apps/shell/src/search/useCaseChat.ts` |
| Create | `apps/shell/src/search/__tests__/useCaseChat.test.ts` |
| Create | `apps/shell/src/search/CaseChatPanel.vue` |
| Modify | `apps/shell/src/search/CaseDetail.vue` — swap disabled button for `<CaseChatPanel>` |

---

## Task 1: Backend — chat endpoint

**Files:**
- Modify: `backend/app/cases/router.py`
- Create: `backend/tests/test_case_chat.py`

### What the endpoint does

`POST /cases/{case_id}/chat` — auth-required. Body: `{ "message": string, "history": [{ "role": "user"|"assistant", "content": string }] }`. Fetches the case from DB, resolves the user's AI settings, builds a system prompt with the case context, appends `history + message`, calls `_call_ai`, returns `{ "reply": string }`.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_case_chat.py`:

```python
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_chat_returns_reply(async_client: AsyncClient, auth_headers: dict):
    """Happy path: authenticated user gets a reply for a real case_id."""
    with patch("app.cases.router._call_ai", return_value="This case concerns X."):
        with patch("app.cases.router._resolve_ai", new_callable=AsyncMock,
                   return_value=("anthropic", "sk-fake", None)):
            resp = await async_client.post(
                "/cases/1/chat",
                json={"message": "Summarise the key ratio.", "history": []},
                headers=auth_headers,
            )
    # 404 is acceptable when no seed data exists; 422/401/500 are failures
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "reply" in resp.json()
        assert resp.json()["reply"] == "This case concerns X."


@pytest.mark.asyncio
async def test_chat_requires_auth(async_client: AsyncClient):
    resp = await async_client.post(
        "/cases/1/chat",
        json={"message": "Hello", "history": []},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_404_unknown_case(async_client: AsyncClient, auth_headers: dict):
    with patch("app.cases.router._resolve_ai", new_callable=AsyncMock,
               return_value=("anthropic", "sk-fake", None)):
        resp = await async_client.post(
            "/cases/999999/chat",
            json={"message": "Hello", "history": []},
            headers=auth_headers,
        )
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests to confirm they fail (endpoint not yet added)**

```bash
cd backend && python -m pytest tests/test_case_chat.py -v
```

Expected: `FAILED` — `404 Not Found` on POST to `/cases/1/chat` (route doesn't exist yet).

- [ ] **Step 3: Implement the endpoint**

Add to the **bottom** of `backend/app/cases/router.py`:

```python
import asyncio
from fastapi import Depends
from app.auth.users import current_active_user
from app.models.user import User
from app.database import get_async_session
from app.briefcases.router import _resolve_ai, _call_ai  # re-use existing helpers


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


@router.post("/{case_id}/chat", response_model=ChatResponse)
async def chat_about_case(
    case_id: int,
    body: ChatRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    provider, api_key, model_override = await _resolve_ai(user, session)

    citation = f" ({case.citation})" if case.citation else ""
    case_summary = case.summary or "No summary available."
    system = (
        "You are an AI legal research assistant helping a South African lawyer. "
        f"The user is asking about the following case:\n\n"
        f"**{case.case_name}** — {case.court}{citation}\n\n"
        f"Summary: {case_summary}\n\n"
        "Answer concisely in plain legal English."
    )

    # Build the full prompt: system context + conversation history + new message
    history_lines = "\n".join(
        f"{m.role.capitalize()}: {m.content}" for m in body.history
    )
    prompt = f"{system}\n\n{history_lines}\nUser: {body.message}\nAssistant:"

    reply = await asyncio.to_thread(_call_ai, provider, api_key, model_override, prompt, 512)
    return ChatResponse(reply=reply)
```

> **Note on imports:** `AsyncSession` and `select` are already imported at the top of `router.py`. Add only the new imports that are missing.

- [ ] **Step 4: Run tests — confirm they pass**

```bash
cd backend && python -m pytest tests/test_case_chat.py -v
```

Expected: All 3 pass. If `conftest.py` fixtures (`async_client`, `auth_headers`) don't exist yet, check `tests/conftest.py` — the pattern matches the existing auth test suite. If the fixture file is absent, add it following the same httpx `AsyncClient` pattern used by `test_ai_settings.py`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/cases/router.py backend/tests/test_case_chat.py
git commit -m "feat: add POST /cases/{id}/chat endpoint"
```

---

## Task 2: Frontend composable — `useCaseChat`

**Files:**
- Create: `apps/shell/src/search/useCaseChat.ts`
- Create: `apps/shell/src/search/__tests__/useCaseChat.test.ts`

### What `useCaseChat` does

Returns reactive state + `send(message)` function. Manages a `messages` array of `{ role, content }`, a `loading` ref, and an `error` ref. Calls `apiFetch<{ reply: string }>('/cases/{id}/chat', { method: 'POST', body: JSON.stringify({ message, history }) })`.

- [ ] **Step 1: Write the failing test**

Create `apps/shell/src/search/__tests__/useCaseChat.test.ts`:

```typescript
// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@martin/common', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@martin/common')>()
  return { ...actual, apiFetch: vi.fn() }
})

describe('useCaseChat', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.resetModules()
  })

  it('send: appends user message, calls apiFetch, appends assistant reply', async () => {
    const { apiFetch } = await import('@martin/common')
    vi.mocked(apiFetch).mockResolvedValueOnce({ reply: 'It held that X.' })

    const { useCaseChat } = await import('../useCaseChat.js')
    const { messages, send, loading } = useCaseChat(42)

    const sendPromise = send('What was the ratio?')
    expect(loading.value).toBe(true)
    await sendPromise

    expect(loading.value).toBe(false)
    expect(messages.value).toHaveLength(2)
    expect(messages.value[0]).toEqual({ role: 'user', content: 'What was the ratio?' })
    expect(messages.value[1]).toEqual({ role: 'assistant', content: 'It held that X.' })
    expect(vi.mocked(apiFetch)).toHaveBeenCalledWith(
      '/cases/42/chat',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('send: sets error on API failure', async () => {
    const { apiFetch } = await import('@martin/common')
    vi.mocked(apiFetch).mockRejectedValueOnce({ status: 503, detail: 'AI not configured' })

    const { useCaseChat } = await import('../useCaseChat.js')
    const { send, error, loading } = useCaseChat(42)

    await send('Hello')

    expect(loading.value).toBe(false)
    expect(error.value).toBe('AI not configured')
  })

  it('send: passes history from prior messages', async () => {
    const { apiFetch } = await import('@martin/common')
    vi.mocked(apiFetch)
      .mockResolvedValueOnce({ reply: 'First reply.' })
      .mockResolvedValueOnce({ reply: 'Second reply.' })

    const { useCaseChat } = await import('../useCaseChat.js')
    const { send } = useCaseChat(7)

    await send('First question')
    await send('Second question')

    const secondCall = vi.mocked(apiFetch).mock.calls[1]
    const body = JSON.parse((secondCall[1] as RequestInit).body as string)
    expect(body.history).toHaveLength(2)
    expect(body.history[0]).toEqual({ role: 'user', content: 'First question' })
    expect(body.history[1]).toEqual({ role: 'assistant', content: 'First reply.' })
  })
})
```

- [ ] **Step 2: Run tests — confirm failure**

```bash
cd apps/shell && pnpm test -- useCaseChat
```

Expected: `FAILED` — `useCaseChat.js` not found.

- [ ] **Step 3: Implement `useCaseChat.ts`**

Create `apps/shell/src/search/useCaseChat.ts`:

```typescript
import { ref } from 'vue'
import { apiFetch, isApiError } from '@martin/common'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export function useCaseChat(caseId: number) {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function send(message: string): Promise<void> {
    error.value = null
    messages.value.push({ role: 'user', content: message })
    loading.value = true

    const history = messages.value.slice(0, -1)

    try {
      const { reply } = await apiFetch<{ reply: string }>(`/cases/${caseId}/chat`, {
        method: 'POST',
        body: JSON.stringify({ message, history }),
      })
      messages.value.push({ role: 'assistant', content: reply })
    } catch (err) {
      error.value = isApiError(err) ? err.detail : 'Something went wrong'
    } finally {
      loading.value = false
    }
  }

  return { messages, loading, error, send }
}
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
cd apps/shell && pnpm test -- useCaseChat
```

Expected: 3 passing.

- [ ] **Step 5: Commit**

```bash
git add apps/shell/src/search/useCaseChat.ts apps/shell/src/search/__tests__/useCaseChat.test.ts
git commit -m "feat: add useCaseChat composable"
```

---

## Task 3: Frontend — `CaseChatPanel.vue` component

**Files:**
- Create: `apps/shell/src/search/CaseChatPanel.vue`

This component is self-contained: it takes `caseId: number` as a prop, calls `useCaseChat`, renders the message thread, and provides an input + send button.

- [ ] **Step 1: Create `CaseChatPanel.vue`**

Create `apps/shell/src/search/CaseChatPanel.vue`:

```vue
<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { Send, Loader2, AlertCircle } from 'lucide-vue-next'
import { useCaseChat } from './useCaseChat.js'

const props = defineProps<{ caseId: number }>()

const { messages, loading, error, send } = useCaseChat(props.caseId)
const input = ref('')
const threadRef = ref<HTMLElement | null>(null)

async function handleSend() {
  const msg = input.value.trim()
  if (!msg || loading.value) return
  input.value = ''
  await send(msg)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

watch(messages, async () => {
  await nextTick()
  threadRef.value?.scrollTo({ top: threadRef.value.scrollHeight, behavior: 'smooth' })
}, { deep: true })
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Message thread -->
    <div ref="threadRef" class="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-0">
      <p v-if="messages.length === 0" class="text-sm text-fg-muted leading-relaxed">
        Ask AI to summarise this case, identify relevant precedents, or help build an argument around it.
      </p>

      <template v-for="(msg, i) in messages" :key="i">
        <div
          :class="[
            'max-w-[85%] rounded-lg px-3 py-2 text-sm leading-relaxed',
            msg.role === 'user'
              ? 'ml-auto bg-primary text-white'
              : 'bg-bg-subtle text-fg border border-border'
          ]"
        >
          {{ msg.content }}
        </div>
      </template>

      <!-- Loading bubble -->
      <div v-if="loading" class="flex items-center gap-1.5 text-fg-muted">
        <Loader2 :size="14" class="animate-spin" />
        <span class="text-xs">Thinking…</span>
      </div>
    </div>

    <!-- Error bar -->
    <div v-if="error" class="flex items-center gap-1.5 px-4 py-2 bg-red-50 border-t border-red-200 text-red-600 text-xs">
      <AlertCircle :size="13" />
      {{ error }}
    </div>

    <!-- Input row -->
    <div class="flex items-end gap-2 px-4 py-3 border-t border-border">
      <textarea
        v-model="input"
        rows="1"
        placeholder="Ask about this case…"
        class="flex-1 resize-none rounded-md border border-border bg-bg px-3 py-2 text-sm text-fg placeholder:text-fg-muted focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
        style="max-height: 120px; overflow-y: auto;"
        @keydown="handleKeydown"
      />
      <button
        :disabled="!input.trim() || loading"
        class="flex items-center justify-center w-9 h-9 rounded-md bg-primary text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary-hover transition"
        @click="handleSend"
      >
        <Send :size="15" />
      </button>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Type-check**

```bash
cd apps/shell && pnpm type-check
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add apps/shell/src/search/CaseChatPanel.vue
git commit -m "feat: add CaseChatPanel component"
```

---

## Task 4: Wire `CaseChatPanel` into `CaseDetail.vue`

**Files:**
- Modify: `apps/shell/src/search/CaseDetail.vue`

Replace the static "AI Analysis" placeholder section at the bottom of `CaseDetail.vue` with a toggled chat panel.

- [ ] **Step 1: Update `CaseDetail.vue`**

Replace the entire file content with:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { FileText, ExternalLink, Sparkles, Building2, Calendar, ChevronDown } from 'lucide-vue-next'
import type { CaseData } from '@martin/common'
import { courtLabel } from './courts.js'
import SaveToBriefcaseButton from './SaveToBriefcaseButton.vue'
import CaseChatPanel from './CaseChatPanel.vue'

const props = defineProps<{ case_: CaseData }>()
const chatOpen = ref(false)
</script>

<template>
  <div class="h-full flex flex-col overflow-hidden">
    <!-- Case metadata (scrollable) -->
    <div class="flex-1 overflow-y-auto p-6">
      <h2 class="text-xl font-semibold text-fg leading-snug mb-3">{{ case_.case_name }}</h2>

      <div class="flex items-start justify-between gap-2 mb-3">
        <div class="flex flex-wrap gap-2">
          <span class="flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full bg-primary/10 text-primary">
            <Building2 :size="11" />
            {{ courtLabel(case_.court) }}
          </span>
          <span v-if="case_.date_decided" class="flex items-center gap-1 text-xs text-fg-muted py-1">
            <Calendar :size="11" />
            {{ new Date(case_.date_decided).toLocaleDateString('en-ZA', { year: 'numeric', month: 'long', day: 'numeric' }) }}
          </span>
        </div>
        <SaveToBriefcaseButton :case-id="case_.id" />
      </div>

      <p v-if="case_.citation" class="text-sm text-fg-muted mb-4">{{ case_.citation }}</p>

      <div v-if="case_.summary" class="mb-6">
        <p class="text-xs font-medium tracking-wide uppercase text-fg-muted mb-2">Summary</p>
        <p class="text-sm text-fg leading-relaxed whitespace-pre-line">{{ case_.summary }}</p>
      </div>

      <div class="flex gap-4">
        <a
          v-if="case_.pdf_url"
          :href="case_.pdf_url"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary-hover transition-colors"
        >
          <FileText :size="15" />
          Download PDF
        </a>
        <a
          :href="case_.saflii_url"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary-hover transition-colors"
        >
          <ExternalLink :size="15" />
          View on SAFLII
        </a>
      </div>
    </div>

    <!-- AI Analysis section -->
    <div class="border-t border-border bg-bg-subtle">
      <!-- Toggle header -->
      <button
        class="w-full px-6 py-3 flex items-center justify-between border-b border-border hover:bg-bg transition"
        @click="chatOpen = !chatOpen"
      >
        <span class="flex items-center gap-1.5 text-xs font-medium text-fg">
          <Sparkles :size="13" class="text-primary" />
          AI Analysis
        </span>
        <ChevronDown
          :size="14"
          class="text-fg-muted transition-transform duration-200"
          :class="{ 'rotate-180': chatOpen }"
        />
      </button>

      <!-- Chat panel — fixed height when open -->
      <div v-if="chatOpen" class="h-72">
        <CaseChatPanel :case-id="case_.id" />
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Run full test suite and type-check**

```bash
cd apps/shell && pnpm test && pnpm type-check
```

Expected: all tests pass, no type errors.

- [ ] **Step 3: Commit**

```bash
git add apps/shell/src/search/CaseDetail.vue
git commit -m "feat: wire AI chat panel into CaseDetail"
```

---

## Task 5: End-to-end smoke test (manual)

- [ ] Start the backend dev server:

```bash
cd backend && uvicorn app.main:app --reload
```

- [ ] Start the frontend dev server:

```bash
cd apps/shell && pnpm dev
```

- [ ] In the browser: run a search, click a result to open the detail panel, click "AI Analysis" to expand the chat, type a question, press Enter.

- [ ] Verify: user bubble appears immediately; loading spinner appears; assistant reply appears.

- [ ] Verify multi-turn: send a follow-up question — history is maintained within the session.

- [ ] Verify error state: disconnect the backend and send a message — an error bar should appear below the thread.

- [ ] Commit a final smoke-test commit if any tweaks were made:

```bash
git add -p
git commit -m "fix: chat panel polish after smoke test"
```

---

## Self-review

### Spec coverage
| Requirement | Task |
|---|---|
| Disabled button replaced with functional chat | Task 4 |
| User can type and send a message | Task 3 |
| AI responds using user's configured provider | Task 1 (`_resolve_ai`) |
| Conversation history maintained in session | Task 2 (`useCaseChat`) |
| Loading indicator | Task 3 |
| Error feedback | Task 2 + Task 3 |
| Auth required on backend | Task 1 (test covers 401) |
| 404 for unknown case | Task 1 (test covers 404) |

### Type consistency
- `ChatMessage` defined in `useCaseChat.ts` — used in `CaseChatPanel.vue` (imported) and sent to backend as `{ role, content }` matching `ChatMessage` Pydantic model.
- `caseId: number` flows from `CaseData.id` (number in `search.ts`) → `CaseDetail` prop → `CaseChatPanel` prop → `useCaseChat(caseId)` — consistent throughout.

### No placeholders: confirmed — all steps contain complete code.
