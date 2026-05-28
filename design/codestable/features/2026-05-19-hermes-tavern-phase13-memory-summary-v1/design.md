# Hermes Tavern Phase 13 — Memory / Summary v1

## Scope

Add mock-first, session-scoped memory primitives to Hermes Tavern without changing Hermes core entrypoints and without making live provider calls.

## Goals

- Persist explicit memory facts per active RP session.
- Persist a manual or deterministic session summary per active RP session.
- Inject saved memory into the existing prompt compiler as `PromptModule`s.
- Provide `/rp memory` commands for mobile/gateway debugging.
- Keep behavior deterministic, local, and inspectable.

## Non-goals

- No semantic/vector memory retrieval.
- No live LLM summarization.
- No cross-session character memory merge.
- No external network or provider calls.
- No changes to `run_agent.py`, `cli.py`, or `gateway/run.py`.

## Files

- `plugins/hermes_tavern/memory.py`
  - `TavernMemoryFact`
  - `TavernMemoryContext`
  - `build_memory_modules(...)`
  - `summarize_recent_messages(...)`
- `plugins/hermes_tavern/db.py`
  - `session_memory_facts`
  - `session_summaries`
  - session memory CRUD helpers
- `plugins/hermes_tavern/runtime.py`
  - `/rp memory add <fact>`
  - `/rp memory list`
  - `/rp memory summary [set <text>|summarize [limit]]`
  - `/rp memory debug`
  - prompt injection via `_session_memory_modules(...)`
- `tests/plugins/test_hermes_tavern_memory.py`

## Data model

### `session_memory_facts`

Explicit, user-provided facts bound to one active session.

Fields:

- `id`
- `session_id`
- `content`
- `importance` — clamped to 1..5
- `source` — default `manual`
- `created_at`

### `session_summaries`

One summary row per session.

Fields:

- `session_id`
- `summary`
- `updated_at`

## Prompt injection

Memory is converted into prompt modules before lorebook modules:

- `memory:summary`
- `memory:facts`

Both are system modules with negative insertion order so they appear early and remain visible in `/rp debug prompt`.

## Mock-first summarization

`/rp memory summary summarize [limit]` does deterministic transcript compaction only:

```text
Recent session turns:
- user: ...
- assistant: ...
```

This deliberately avoids semantic claims and provider calls. Future phases can add live-model summarization behind explicit live-provider gating.

## Acceptance criteria

- Memory tables migrate idempotently.
- Facts and summary round-trip through `TavernStore`.
- `/rp memory add/list/summary/debug` work only with active sessions.
- Saved memory appears in `/rp debug prompt` as memory modules.
- Deterministic summary uses recent local message rows only.
- py_compile passes.
- pytest is attempted if available; current active venv may block with `No module named pytest`.
