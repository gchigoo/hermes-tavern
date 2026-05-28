# Hermes Tavern Phase 14 — Turn Controls v1

## Goal

Add turn-level editing to active sessions: view history, undo a turn, retry the
last assistant reply, and edit the last user message with regeneration.

## Scope

- `plugins/hermes_tavern/db.py` — four new / modified store helpers
- `plugins/hermes_tavern/runtime.py` — four new commands + `_run_generation_pipeline` helper
- `tests/plugins/test_hermes_tavern_turn_controls.py` — focused test suite

## Store helpers (`TavernStore`)

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_recent_messages` | existing, modified | Returns latest window in chronological order and includes `id` field in each row |
| `delete_message` | `(message_id) -> bool` | Delete a single message id for retry/edit bookkeeping |
| `delete_last_assistant_message` | `(session_id) -> str \| None` | Delete most-recent assistant msg; return its id or None |
| `delete_assistant_after_last_user_message` | `(session_id) -> str \| None` | Delete only the assistant reply immediately following the latest user msg; preserves greetings/other assistant-only rows |
| `delete_last_user_assistant_turn` | `(session_id) -> int` | Delete last user + optional following assistant; return count (0/1/2) |
| `update_last_user_message` | `(session_id, new_content) -> str \| None` | Update content of most-recent user msg; return its id or None |

All helpers are deterministic, session-scoped, and no-op cleanly when nothing to act on.

## Runtime commands

| Command | Behaviour |
|---------|-----------|
| `/rp history [limit]` | List recent messages with `[short_id] role: preview`. Default limit 10, max 50. |
| `/rp retry` | Only when the latest rows are `user -> assistant`: remove that assistant reply; regenerate from that user message via existing pipeline; append new reply. Greetings are not treated as retryable user-turn replies. |
| `/rp undo` | Remove last user + assistant pair. No regeneration. |
| `/rp edit last <text>` | Update last user message, delete its following assistant reply if present, regenerate, append new reply. |

## Generation pipeline extraction

`_run_generation_pipeline(session, user_text, history)` factors out the compile →
route → render → generate flow shared by `handle_active_message_sync`, `_retry`,
and `_edit`. Does **not** write to the store — callers decide what to persist.

## Constraints

- Mock-first by default via existing fake adapter path; any real provider use remains behind the existing session-level Hermes mode + live-confirm gate.
- Safe/adult-fiction gating preserved via existing `_session_preset_modules`.
- No new dependencies introduced.
