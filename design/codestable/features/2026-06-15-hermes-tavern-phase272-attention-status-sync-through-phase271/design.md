---
doc_type: feature-design
status: approved
feature: "2026-06-15-hermes-tavern-phase272-attention-status-sync-through-phase271"
date: "2026-06-15"
created: "2026-06-15"
updated: "2026-06-15"
implementation_ready: true
owner: codestable-cron
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 272: Attention Status Sync Through Phase 271

## Read-Only Architect Precheck

Controller-selected slice extends the accepted Phase 271 attention-status sync to cover
accepted Phase 271 and keep the artifact in lockstep with the focused test guard.

- Source branch has current accepted status through Phase 271.
- This executor slice is docs/test/status-only.

## Scope

- Update `design/codestable/attention.md` one current-status bullet only.
- Update `tests/test_hermes_tavern_codestable_status.py` to guard the same terminal state.
- Track no runtime, source, provider, plugin, safety, or policy behavior.

## Exact S1 Contract

- `design/codestable/attention.md` terminal status remains:
  - date `2026-06-15`
  - one current-status bullet
  - accepted range `1-271`
  - preserve `Phase 121-167`
- Append exactly:
  - `Phase 271 attention status sync through Phase 270`
- Keep final suffix exactly:
  - `Phase 269 attention status sync through Phase 268, Phase 270 attention status sync through Phase 269, and Phase 271 attention status sync through Phase 270.`

## Test Contract

- In `tests/test_hermes_tavern_codestable_status.py` set:
  - `CURRENT_STATUS_PREFIX`: `Current status (2026-06-15): All phases 1-271 accepted`
  - `STALE_STATUS_PREFIX`: `Current status (2026-06-15): All phases 1-270 accepted`
  - `STALE_PHASE_MARKER`: `1-270`
  - `STALE_PHASE_MARKER_EN_DASH`: `1–270`
- Required labels include `Phase 271 attention status sync through Phase 270`.
- `phase_range` assertion uses `range(168, 272)`.
- Aggregate literal `range(168, 272)` present.
- Direct stale literal `range(168, 271)` is rejected via split-string construction.
- Keep exactly one `CURRENT_STATUS_PREFIX` assignment.
- Keep explicit/static file scan assertions (no glob/rglob/iterdir/os.walk discovery).

## Non-Goals

- No service lifecycle commands.
- No edits outside allowed files for this slice.
