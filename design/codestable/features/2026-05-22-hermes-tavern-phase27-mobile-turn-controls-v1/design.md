---
feature: 2026-05-22-hermes-tavern-phase27-mobile-turn-controls-v1
summary: Polish Hermes Tavern retry, undo, and edit-last command output for mobile chat surfaces.
tags: [hermes-tavern, mobile, turn-controls, runtime]
---

# Hermes Tavern Phase 27: Mobile Turn Controls Polish v1

## Goal

Turn-control commands return compact, self-contained mobile messages that name
the action, preserve generated assistant text, and provide the next command a
user is likely to need.

## Scope

- `/rp retry`
- `/rp undo`
- `/rp edit last <text>`
- `/rp help` verification for `/rp retry`

## Design

The runtime keeps all existing turn-control behavior intact. Retry still
regenerates from the previous user message and replaces the last assistant
message while preserving swipe metadata. Undo still delegates to
`delete_last_user_assistant_turn`. Edit still updates the last user message,
removes the following assistant message, and regenerates through the existing
pipeline.

Only successful output formatting changes:

- Retry returns `Hermes Tavern retry:`, the generated reply, and
  `retry again: /rp retry`.
- Undo returns the removed message count in a sentence and
  `undo again: /rp undo`.
- Edit returns `Hermes Tavern edit:`, the regenerated reply, and
  `edit again: /rp edit last <text>`.

Error messages remain short and direct so messaging-platform clients do not
bury the useful instruction in long diagnostic text.

## Non-Goals

- No database schema or CRUD changes.
- No generation pipeline changes.
- No raw JSON output.
- No network calls.
