---
feature: 2026-05-22-hermes-tavern-phase22-author-note-v1
summary: Add session-scoped Author's Note / Scene Note prompt control for Hermes Tavern.
tags: [hermes-tavern, author-note, scene-note, prompt, sqlite, runtime]
---

# Hermes Tavern Phase 22: Author's Note / Scene Note v1

## Goal

Add a narrow SillyTavern-style Author's Note / Scene Note feature: a user can set a short session-scoped directive that is injected into the prompt as `note:author` and flows through the existing macro expansion path.

## Scope

- Guarded SQLite migration on `sessions`:
  - `note_text`
  - `note_position`
  - `note_frequency`
  - `note_every_n`
- Store helpers:
  - `set_session_note`
  - `clear_session_note`
  - `set_session_note_position`
  - `set_session_note_frequency`
- Runtime commands:
  - `/rp note set <text>`
  - `/rp note clear`
  - `/rp note inspect`
  - `/rp note position [before_char|after_history|before_user]`
  - `/rp note frequency [always|every_n [n]]`
- Prompt integration through `TavernRuntime._session_prompt_modules()`.
- Mobile-safe inspect/status output and no raw JSON dumps.

## Non-Goals

- Multiple notes per session.
- Global/default notes.
- UI widgets, Telegram inline buttons, or rich platform-specific controls.
- New macro semantics or execution-capable templating.
- Live provider/network behavior changes.

## Design

The note is stored directly on the active `sessions` row because it is strictly session-local state, like content mode and active asset bindings. During prompt assembly, `_session_note_modules()` emits one `PromptModule` when the note is active:

```text
name: note:author
role: system
position: before_char | after_history | before_user
content: session.note_text
```

`PromptCompiler.compile()` already expands all prompt module content with the Phase 20 one-pass allowlist macro engine, so note text may safely use macros such as `{{char}}`, `{{user}}`, `{{session_title}}`, and `{{content_mode}}` without a second expansion mechanism.

## Frequency Semantics

- `always`: inject on every compiled turn.
- `every_n [n]`: inject only when the next user turn index is divisible by `n`.
- `n` is clamped to `2..20`; omitted `n` defaults to `3`.

This keeps the feature deterministic and testable without provider calls.

## Acceptance

- Existing DBs migrate with the new session note columns.
- `/rp note set/clear/inspect/position/frequency` work only against the active session and return phone-readable errors when no session is active.
- `/rp note inspect` is compact and never prints raw JSON.
- `/rp debug prompt` shows `note:author` and macro-expanded note text when active.
- Active generation receives the note module via the existing renderer/adapter path.
- `every_n` behavior is deterministic and covered by tests.
